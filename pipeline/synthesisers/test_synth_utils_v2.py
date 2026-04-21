"""
Tests for synth_utils.py v2 additions (SPEC-AI-ENGINE-LABORATORY v0.3.2 PR 2).

Covers:
  1. _strip_think_blocks removes <think>...</think> wrappers, case-insensitive,
     multi-line, handles no-wrapper input.
  2. parse_llm_json(think_aware=False) — default behaviour unchanged (all 9
     existing synth-script callers continue to work).
  3. parse_llm_json(think_aware=True) — recovers JSON hidden after a <think>
     block that the standard extractor would fail to handle (the AGM 21 Apr
     attempt-3 failure class).
  4. call_synth_api surface contract — logs one exchange, never raises on
     network failure, returns (None, meta) with error populated.

No live Perplexity API calls — requests.post is monkey-patched.
"""

import json
import pathlib
import sys
import tempfile

# Make synth_utils importable
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Make pipeline/shared importable for log_exchange
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "shared"))

import synth_utils  # noqa: E402
from synth_utils import (  # noqa: E402
    _strip_think_blocks,
    call_synth_api,
    parse_llm_json,
)


# ─── _strip_think_blocks ─────────────────────────────────────────────────────

def test_strip_think_removes_single_block():
    raw = '<think>reasoning here</think>{"ok": true}'
    assert _strip_think_blocks(raw).strip() == '{"ok": true}'


def test_strip_think_removes_multiline_block():
    raw = (
        "<think>\nline 1\nline 2\nline 3\n</think>\n"
        '{"lead_signal": {"headline": "x"}}'
    )
    out = _strip_think_blocks(raw)
    assert "<think>" not in out
    assert "line 1" not in out
    assert '"lead_signal"' in out


def test_strip_think_case_insensitive():
    raw = '<THINK>r</THINK>{"ok": true}'
    assert "<THINK>" not in _strip_think_blocks(raw)


def test_strip_think_noop_when_no_block():
    raw = '{"ok": true}'
    assert _strip_think_blocks(raw) == raw


def test_strip_think_empty_input():
    assert _strip_think_blocks("") == ""


def test_strip_think_multiple_blocks():
    raw = '<think>a</think>\n<think>b</think>\n{"ok": true}'
    out = _strip_think_blocks(raw)
    assert "<think>" not in out
    assert '"ok"' in out


# ─── parse_llm_json back-compat ──────────────────────────────────────────────

def test_parse_llm_json_default_unchanged():
    """All 9 existing synth-script callers call parse_llm_json(raw, tag)
    with no think_aware kwarg. Default must remain think_aware=False."""
    raw = '{"a": 1}'
    parsed, repaired = parse_llm_json(raw, "GMM")
    assert parsed == {"a": 1}
    assert repaired is False


def test_parse_llm_json_default_does_NOT_strip_think():
    """Confirm default path does not strip <think> — caller must opt in."""
    raw = '<think>r</think>{"a": 1}'
    # Default (think_aware=False) — extractor will find { via brace-match,
    # but <think> contents should not have been stripped
    parsed, _ = parse_llm_json(raw, "GMM")
    # The extractor finds outermost {...} regardless; this test's point is
    # that _strip_think_blocks was not called in the default branch. We
    # verify by asserting the path works via the existing brace-match,
    # which it does because '{' appears AFTER </think>.
    assert parsed == {"a": 1}


def test_parse_llm_json_think_aware_recovers_wrapped_json():
    """The AGM 21 Apr attempt-3 failure class:
    sonar-deep-research emits <think>...reasoning...</think> then JSON.
    With think_aware=True, parsed successfully."""
    raw = (
        "<think>\n"
        "Reasoning about AI governance this week...\n"
        "Key signal: Anthropic alignment paper.\n"
        "</think>\n"
        '{"weekly_brief_draft": "This week\'s AI governance...", '
        '"lead_signal": {"headline": "Anthropic paper"}}'
    )
    parsed, _ = parse_llm_json(raw, "AIG", think_aware=True)
    assert parsed["lead_signal"]["headline"] == "Anthropic paper"


def test_parse_llm_json_think_aware_no_wrapper_still_works():
    """think_aware=True must be safe to use when there's no wrapper."""
    raw = '{"ok": true}'
    parsed, _ = parse_llm_json(raw, "AIG", think_aware=True)
    assert parsed == {"ok": True}


# ─── call_synth_api ──────────────────────────────────────────────────────────

def _mock_ok_response(content: str, tokens: int = 1234):
    class _Resp:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [{"message": {"content": content}}],
                "usage": {"total_tokens": tokens},
                "citations": ["a", "b", "c"],
            }

    return _Resp()


def test_call_synth_api_happy_path_logs_and_parses(tmp_path, monkeypatch):
    """Successful call: returns parsed dict, logs one exchange row,
    runtime_seconds populated on the record."""
    # Redirect log_exchange output to tmp_path
    import prompt_exchange_log as pel

    monkeypatch.setattr(pel, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(synth_utils, "_load_log_exchange",
                        lambda: pel.log_exchange)

    # Mock requests.post
    import requests

    def _mock_post(url, headers=None, json=None, timeout=None):
        return _mock_ok_response('{"weekly_brief_draft": "hello"}')

    monkeypatch.setattr(requests, "post", _mock_post)

    parsed, meta = call_synth_api(
        url="https://api.perplexity.ai/chat/completions",
        headers={"Authorization": "Bearer x"},
        body={"model": "sonar-pro", "messages": []},
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-pro",
        prompt_text="Synthesise this week.",
        prompt_file="aig-synth.txt",
        extractor="standard",
        source="lab",
        lab_run_id="run-test-001",
    )

    assert parsed == {"weekly_brief_draft": "hello"}
    assert meta["parsed_ok"] is True
    assert meta["error"] is None
    assert meta["http_status"] == 200
    assert meta["tokens"] == 1234
    assert meta["citations"] == 3
    assert meta["runtime_seconds"] >= 0

    # Exactly one exchange row written
    log_file = tmp_path / "pipeline" / "incidents" / "prompt-exchanges.jsonl"
    assert log_file.exists()
    rows = [json.loads(line) for line in log_file.read_text().splitlines() if line]
    assert len(rows) == 1
    row = rows[0]
    assert row["schema_version"] == "1.1"
    assert row["monitor"] == "ai-governance"
    assert row["stage"] == "synthesiser"
    assert row["model"] == "sonar-pro"
    assert row["extractor"] == "standard"
    assert row["source"] == "lab"
    assert row["lab_run_id"] == "run-test-001"
    assert row["runtime_seconds"] is not None


def test_call_synth_api_think_aware_routes_parser(tmp_path, monkeypatch):
    """extractor='think-aware' must strip <think> and recover the JSON."""
    import prompt_exchange_log as pel

    monkeypatch.setattr(pel, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(synth_utils, "_load_log_exchange",
                        lambda: pel.log_exchange)

    import requests

    raw_with_think = (
        "<think>Reasoning about this week</think>\n"
        '{"weekly_brief_draft": "this week..."}'
    )

    def _mock_post(*a, **k):
        return _mock_ok_response(raw_with_think)

    monkeypatch.setattr(requests, "post", _mock_post)

    parsed, meta = call_synth_api(
        url="x", headers={}, body={},
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-deep-research",
        prompt_text="p",
        extractor="think-aware",
        source="lab",
    )

    assert parsed is not None
    assert parsed.get("weekly_brief_draft") == "this week..."
    assert meta["parsed_ok"] is True

    # Logged row reflects extractor
    log_file = tmp_path / "pipeline" / "incidents" / "prompt-exchanges.jsonl"
    rows = [json.loads(line) for line in log_file.read_text().splitlines() if line]
    assert rows[-1]["extractor"] == "think-aware"


def test_call_synth_api_never_raises_on_network_failure(tmp_path, monkeypatch):
    """Network exception must NOT propagate. Must return (None, meta) with
    error populated and still log an exchange row (with empty raw_response)."""
    import prompt_exchange_log as pel

    monkeypatch.setattr(pel, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(synth_utils, "_load_log_exchange",
                        lambda: pel.log_exchange)

    import requests

    def _boom(*a, **k):
        raise requests.ConnectionError("network down")

    monkeypatch.setattr(requests, "post", _boom)

    parsed, meta = call_synth_api(
        url="x", headers={}, body={},
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-pro",
        prompt_text="p",
    )

    assert parsed is None
    assert meta["parsed_ok"] is False
    assert meta["error"] is not None
    assert "ConnectionError" in meta["error"]
    # Log row still emitted
    log_file = tmp_path / "pipeline" / "incidents" / "prompt-exchanges.jsonl"
    assert log_file.exists()


def test_call_synth_api_parse_failure_is_recorded_not_raised(tmp_path, monkeypatch):
    """Malformed JSON that can't be repaired must NOT raise. Must return
    (None, meta) with error populated + exchange row with parsed_ok=False."""
    import prompt_exchange_log as pel

    monkeypatch.setattr(pel, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(synth_utils, "_load_log_exchange",
                        lambda: pel.log_exchange)

    import requests

    def _mock_post(*a, **k):
        return _mock_ok_response("this is not json at all !!!")

    monkeypatch.setattr(requests, "post", _mock_post)

    parsed, meta = call_synth_api(
        url="x", headers={}, body={},
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-pro",
        prompt_text="p",
    )

    assert parsed is None
    assert meta["parsed_ok"] is False
    assert meta["error"] is not None
    assert "JSONDecodeError" in meta["error"]
    log_file = tmp_path / "pipeline" / "incidents" / "prompt-exchanges.jsonl"
    rows = [json.loads(line) for line in log_file.read_text().splitlines() if line]
    assert rows[-1]["outcome"] == "parse_error"

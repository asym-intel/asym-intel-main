#!/usr/bin/env python3
"""Tests for tools/no_direct_provider_calls.py (Sprint CS, BRIEF CS-2)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import no_direct_provider_calls as gate

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(tmp_path: Path, rel: str, body: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def test_clean_file_no_violations(tmp_path):
    _write(tmp_path, "pipeline/monitors/test_clean/clean.py",
           "def f():\n    return 1\n")
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 1


@pytest.mark.parametrize("snippet,expected_labels", [
    ('url = "https://api.perplexity.ai/chat/completions"\n', {"api.perplexity.ai"}),
    ('url = "http://api.anthropic.com/v1/messages"\n',       {"api.anthropic.com"}),
    ('import anthropic\n',                                    {"import anthropic"}),
    # `from anthropic import …` legitimately matches two patterns (the specific
    # `from anthropic import` and the broader `from anthropic`); the gate is
    # belt-and-braces so we accept both.
    ('from anthropic import Anthropic\n',                     {"from anthropic import", "from anthropic"}),
    ('from anthropic.types import Message\n',                 {"from anthropic"}),
    ('requests.post("https://x/perplexity-proxy", json={})\n', {"requests->perplexity"}),
    # A `requests.get` to the anthropic host matches both the host pattern
    # and the requests→anthropic pattern; both are correct.
    ('requests.get("https://api.anthropic.com/v1/messages")\n', {"api.anthropic.com", "requests->anthropic"}),
    ('API_KEY = os.environ["PPLX_API_KEY"]\n',                {"PPLX_API_KEY"}),
    ('API_KEY = os.environ["ANTHROPIC_API_KEY"]\n',           {"ANTHROPIC_API_KEY"}),
])
def test_each_pattern_triggers_violation(tmp_path, snippet, expected_labels):
    _write(tmp_path, "pipeline/monitors/p/file.py", snippet)
    violations, scanned = gate.scan(tmp_path)
    assert scanned == 1
    assert len(violations) == len(expected_labels), f"got {violations!r}"
    got_labels = {v.split(": ", 2)[2].split(" — ")[0] for v in violations}
    assert got_labels == expected_labels
    for v in violations:
        assert "pipeline/monitors/p/file.py:1:" in v


def test_allow_list_engine_path_is_exempt(tmp_path):
    body = (
        'import anthropic\n'
        'from anthropic import Anthropic\n'
        'url = "https://api.perplexity.ai/x"\n'
        'url2 = "https://api.anthropic.com/x"\n'
        'k = os.environ["PPLX_API_KEY"]\n'
        'k2 = os.environ["ANTHROPIC_API_KEY"]\n'
        'requests.post("https://api.perplexity.ai/x")\n'
        'requests.get("https://api.anthropic.com/x")\n'
    )
    # pipeline/engine/** is allow-listed AND the scanner only descends into
    # pipeline/monitors and pipeline/synthesisers — both protections apply.
    _write(tmp_path, "pipeline/engine/anthropic_client.py", body)
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


def test_allow_list_tools_path_is_exempt(tmp_path):
    # tools/** is allow-listed; even if a future file under
    # pipeline/monitors symlinks or someone places a tool path inside the
    # scan tree, it must be exempt. The simpler test: a tools/ file is never
    # scanned because tools/ is not a scan root.
    _write(tmp_path, "tools/some_ops_script.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


def test_multifile_violations_summary(tmp_path):
    _write(tmp_path, "pipeline/monitors/a/x.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    _write(tmp_path, "pipeline/synthesisers/b/y.py",
           'url = "https://api.perplexity.ai/x"\n')
    violations, scanned = gate.scan(tmp_path)
    assert scanned == 2
    assert len(violations) == 2
    paths = {v.split(": ", 1)[1].split(":", 1)[0] for v in violations}
    assert paths == {
        "pipeline/monitors/a/x.py",
        "pipeline/synthesisers/b/y.py",
    }


def test_standalone_invocation_exits_1_on_violations(tmp_path, monkeypatch):
    _write(tmp_path, "pipeline/monitors/m/bad.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    rc = gate.main()
    assert rc == 1


def test_standalone_invocation_exits_0_when_clean(tmp_path, monkeypatch):
    _write(tmp_path, "pipeline/monitors/m/ok.py", "x = 1\n")
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    rc = gate.main()
    assert rc == 0


def test_invocation_via_subprocess():
    """Confirm the tool is runnable as `python3 tools/no_direct_provider_calls.py`."""
    script = REPO_ROOT / "tools" / "no_direct_provider_calls.py"
    res = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    # On current main, violations exist (chatter/reasoner/collector/synthesiser
    # scripts call Perplexity directly). After CS-3 / engine migration, this
    # should flip to 0. Either way, exit code must be 0 or 1, never 2.
    assert res.returncode in (0, 1), (
        f"unexpected exit {res.returncode}; stderr: {res.stderr!r}"
    )
    assert "no_direct_provider_calls.py — checking" in res.stdout


@pytest.mark.xfail(
    reason="CS-3 normalisation pending — flips to pass after CS-3 merges",
    strict=False,
)
def test_live_state_main_is_clean():
    """Live-state assertion: after CS-3 lands, main has zero direct provider calls.

    Flips from xfail to pass once CS-3 migrates per-monitor scripts to the
    engine clients. Today this fails (≥8 violations expected per the BRIEF;
    in practice ~100 across the monitor + synthesiser tree — see PR body).
    """
    violations, _scanned = gate.scan(REPO_ROOT)
    assert violations == [], (
        f"{len(violations)} direct-provider-call violations remain on main"
    )

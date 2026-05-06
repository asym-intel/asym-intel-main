#!/usr/bin/env python3
"""Tests for tools/no_direct_provider_calls.py (Sprint CS-min, BRIEF CS-2).

The gate scans pipeline/engine/** ONLY. Pre-engine files and the
consolidated chatter dispatcher are intentionally out of scope; their
status (legacy / lab / fallback / dead / open architectural question) is
deferred to a later audit.
"""

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


# ── Pattern detection (run files inside the engine scope) ──────────────────


def test_clean_engine_file_no_violations(tmp_path):
    _write(tmp_path, "pipeline/engine/clean_module.py",
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
def test_each_pattern_triggers_violation_inside_engine(tmp_path, snippet, expected_labels):
    _write(tmp_path, "pipeline/engine/x.py", snippet)
    violations, scanned = gate.scan(tmp_path)
    assert scanned == 1
    assert len(violations) == len(expected_labels), f"got {violations!r}"
    got_labels = {v.split(": ", 2)[2].split(" — ")[0] for v in violations}
    assert got_labels == expected_labels
    for v in violations:
        assert "pipeline/engine/x.py:1:" in v


# ── Scope: only pipeline/engine/** is scanned ───────────────────────────


def test_unified_chatter_is_out_of_scope(tmp_path):
    """pipeline/chatter/unified-chatter.py is NOT scanned in CS-min.

    Audit found it currently calls Perplexity directly rather than routing
    through the engine. Whether chatter SHOULD route through the engine is
    an open architectural question deferred to a follow-up audit (see
    ops/HOUSEKEEPING-INBOX.md). Forcing a CS-min answer would expand scope.
    """
    body = (
        'API_KEY = os.environ["PPLX_API_KEY"]\n'
        'requests.post("https://api.perplexity.ai/chat/completions")\n'
    )
    _write(tmp_path, "pipeline/chatter/unified-chatter.py", body)
    _write(tmp_path, "pipeline/chatter/agm-chatter.py", body)
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


def test_pipeline_monitors_are_out_of_scope(tmp_path):
    """Pre-engine monitor scripts (weekly-research.py, <abbr>-reasoner.py,
    collect.py, etc.) are NOT scanned. Their status — legacy entry point,
    lab tooling, scheduled fallback, or dead — is deferred to a later audit
    (see ops/HOUSEKEEPING-INBOX.md)."""
    body = (
        'import anthropic\n'
        'k = os.environ["PPLX_API_KEY"]\n'
        'requests.post("https://api.perplexity.ai/chat/completions")\n'
    )
    _write(tmp_path, "pipeline/monitors/financial-integrity/weekly-research.py", body)
    _write(tmp_path, "pipeline/monitors/financial-integrity/fim-reasoner.py", body)
    _write(tmp_path, "pipeline/monitors/financial-integrity/collect.py", body)
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


def test_pipeline_synthesisers_are_out_of_scope(tmp_path):
    """Per-monitor synthesisers and the cross-monitor synthesiser are NOT
    scanned. Same deferred-audit reasoning as pipeline/monitors/**."""
    body = 'k = os.environ["PPLX_API_KEY"]\n'
    _write(tmp_path, "pipeline/synthesisers/erm/environmental-risks-synthesiser.py", body)
    _write(tmp_path, "pipeline/synthesisers/cross-monitor/cross-monitor-synthesiser.py", body)
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


def test_tools_directory_is_out_of_scope(tmp_path):
    """tools/ is not in the scan list. Ops scripts may legitimately need
    direct provider access for diagnostics."""
    _write(tmp_path, "tools/some_ops_script.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    violations, scanned = gate.scan(tmp_path)
    assert violations == []
    assert scanned == 0


# ── Multi-file behaviour and exit codes ────────────────────────────────────


def test_multifile_violations_summary(tmp_path):
    """Multiple dirty engine files contribute to the same violation report."""
    _write(tmp_path, "pipeline/engine/a.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    _write(tmp_path, "pipeline/engine/sub/b.py",
           'url = "https://api.perplexity.ai/x"\n')
    violations, scanned = gate.scan(tmp_path)
    assert scanned == 2
    assert len(violations) == 2
    paths = {v.split(": ", 1)[1].split(":", 1)[0] for v in violations}
    assert paths == {
        "pipeline/engine/a.py",
        "pipeline/engine/sub/b.py",
    }


def test_standalone_invocation_exits_1_on_violations(tmp_path, monkeypatch):
    _write(tmp_path, "pipeline/engine/bad.py",
           'k = os.environ["PPLX_API_KEY"]\n')
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    rc = gate.main()
    assert rc == 1


def test_standalone_invocation_exits_0_when_clean(tmp_path, monkeypatch):
    _write(tmp_path, "pipeline/engine/ok.py", "x = 1\n")
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    rc = gate.main()
    assert rc == 0


def test_standalone_invocation_exits_0_when_scope_is_empty(tmp_path, monkeypatch):
    """If the scope paths don't exist (e.g., on asym-intel-main where engine
    code is sparse-checked-out at workflow runtime, not committed), the gate
    reports 0 files scanned and exits 0. This is the expected steady state
    on main."""
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
    assert res.returncode in (0, 1), (
        f"unexpected exit {res.returncode}; stderr: {res.stderr!r}"
    )
    assert "no_direct_provider_calls.py — scanning" in res.stdout


def test_live_state_main_is_clean():
    """Live-state assertion: in-scope paths on main have zero violations.

    On asym-intel-main this is naturally true because the engine is
    sparse-checked-out at workflow runtime and `pipeline/engine/` is not
    committed to main. The single named file pipeline/chatter/unified-chatter.py
    routes through the engine clients via the standard import path.

    If this test ever fails, either (a) engine code has been accidentally
    committed to main without engine-style routing, or (b) unified-chatter.py
    has regressed.
    """
    violations, _scanned = gate.scan(REPO_ROOT)
    assert violations == [], (
        f"{len(violations)} direct-provider-call violations in scoped paths"
    )

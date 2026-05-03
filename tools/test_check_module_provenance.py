"""
Tests for tools/check_module_provenance.py — module-level null-signal
provenance auditor (CLI counterpart of publisher's write-time gate).

Cases (per North-Star module-quality-gate spec):

  1. populated module passes
  2. empty module with explicit absence provenance passes
  3. empty module without provenance fails
  4. non-module top-level keys are ignored

Plus: scanner round-trip — JSON output, exit codes, and discovery against a
fake repo root with multiple monitors.

No network, no real publish path. Pure in-memory + tmp_path fixtures.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_module_provenance import (  # noqa: E402
    audit_path,
    audit_report,
    discover_reports,
    main,
)


# ── Case 1: populated module passes ────────────────────────────────────────

def test_populated_module_passes():
    """A module with real content does not appear in the unprovenanced list."""
    report = {
        "module_0": {
            "title": "Lead Signal",
            "body": "Substantive content describing this week's lead.",
        },
        "module_2": {
            "models": [
                {"name": "GPT-X", "lab": "OpenAI", "tier": 1},
            ],
        },
    }
    assert audit_report(report) == []


# ── Case 2: empty module with explicit absence provenance passes ───────────

def test_empty_module_with_provenance_passes():
    """The contract: null_signal=True + empty_reason satisfies the gate."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "strategic_deals": [],
            "null_signal": True,
            "empty_reason": "no_material_content",
            "fallback_message": "No material developments observed this cycle.",
        },
    }
    assert audit_report(report) == []


def test_empty_module_with_unknown_reason_passes():
    """`empty_reason: 'unknown'` is the engine's explicit-unknown sentinel
    and MUST satisfy the gate — silence is the failure mode, not unknown."""
    report = {
        "module_6": {
            "title": "AI in Science",
            "threshold_events": [],
            "null_signal": True,
            "empty_reason": "unknown",
            "fallback_message": "Pipeline could not determine cause; flagged for review.",
        },
    }
    assert audit_report(report) == []


# ── Case 3: empty module without provenance fails ──────────────────────────

def test_empty_module_without_provenance_fails():
    """The data-quality break we are gating against: bare empty module shell."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "strategic_deals": [],
            "energy_wall": [],
        },
    }
    assert audit_report(report) == ["module_3"]


def test_empty_module_with_partial_provenance_fails():
    """null_signal alone (no empty_reason) is not enough — both are required."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "null_signal": True,
        },
    }
    assert audit_report(report) == ["module_3"]


def test_empty_module_with_only_title_fails():
    """A module with nothing but a title is structurally empty and unannotated."""
    report = {
        "module_8": {"title": "Military AI Watch"},
    }
    assert audit_report(report) == ["module_8"]


def test_multiple_empty_modules_all_reported():
    """Every offender is named, in deterministic order."""
    report = {
        "module_0": {"title": "Lead", "body": "Real content."},
        "module_1": {"mainstream": [], "underweighted": []},
        "module_3": {"title": "M&A", "funding_rounds": []},
        "module_5": {"title": "China", "items": [{}]},
    }
    bad = audit_report(report)
    assert set(bad) == {"module_1", "module_3", "module_5"}


# ── Case 4: non-module top-level keys are ignored ──────────────────────────

def test_non_module_keys_ignored():
    """Non-module top-level fields (meta, source_url, key_judgments, etc.)
    are out of scope for the gate even when empty or sparse."""
    report = {
        "meta": {"issue": 13, "week_label": "W/E 2 May 2026"},
        "source_url": "https://example.com",
        "key_judgments": [],
        "delta_strip": {},
        "weekly_brief": "",
        "country_grid": [],
        "module_0": {"title": "Lead", "body": "Real content."},
    }
    assert audit_report(report) == []


def test_module_key_with_non_dict_value_ignored():
    """A `module_*` key whose value is not a dict (e.g. a list) is not a
    module-shape object and the gate must not crash on it."""
    report = {
        "module_2": [{"name": "Model A"}],  # legacy flat-array form
        "module_0": {"title": "Lead", "body": "Real."},
    }
    assert audit_report(report) == []


# ── Scanner integration: file I/O, exit codes, JSON output ────────────────

def _write_report(path: pathlib.Path, payload: dict) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_audit_path_handles_missing_file(tmp_path):
    rec = audit_path(tmp_path / "does-not-exist.json")
    assert rec["ok"] is False
    assert rec["error"] == "file_not_found"


def test_audit_path_handles_malformed_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{ not json", encoding="utf-8")
    rec = audit_path(p)
    assert rec["ok"] is False
    assert rec["error"].startswith("json_parse_error")


def test_audit_path_returns_clean_record_for_clean_report(tmp_path):
    p = _write_report(
        tmp_path / "clean.json",
        {"module_0": {"title": "Lead", "body": "Real content."}},
    )
    rec = audit_path(p)
    assert rec["ok"] is True
    assert rec["empty_unprovenanced"] == []
    assert rec["error"] == ""


def test_audit_path_returns_failures_for_bad_report(tmp_path):
    p = _write_report(
        tmp_path / "docs/monitors/test-monitor/data/report-latest.json",
        {
            "module_0": {"title": "Lead", "body": "Real."},
            "module_3": {"title": "Empty", "items": []},
        },
    )
    rec = audit_path(p)
    assert rec["ok"] is False
    assert rec["empty_unprovenanced"] == ["module_3"]
    assert rec["slug"] == "test-monitor"


def test_discover_reports_finds_all_monitor_reports(tmp_path):
    # Two passing monitors, one failing monitor.
    _write_report(
        tmp_path / "docs/monitors/alpha/data/report-latest.json",
        {"module_0": {"title": "A", "body": "Real."}},
    )
    _write_report(
        tmp_path / "docs/monitors/beta/data/report-latest.json",
        {"module_0": {"title": "B", "body": "Real."}},
    )
    _write_report(
        tmp_path / "docs/monitors/gamma/data/report-latest.json",
        {"module_3": {"title": "Empty", "items": []}},
    )
    paths = discover_reports(tmp_path)
    assert len(paths) == 3
    slugs = {p.parts[-3] for p in paths}
    assert slugs == {"alpha", "beta", "gamma"}


def test_main_exits_1_on_failures_via_report_flag(tmp_path, capsys):
    p = _write_report(
        tmp_path / "report-latest.json",
        {"module_3": {"title": "Empty", "items": []}},
    )
    rc = main(["--report", str(p)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "module_3" in out


def test_main_exits_0_on_clean_report(tmp_path, capsys):
    p = _write_report(
        tmp_path / "report-latest.json",
        {"module_0": {"title": "Lead", "body": "Real content."}},
    )
    rc = main(["--report", str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PASS" in out


def test_main_emits_json_when_requested(tmp_path, capsys):
    p = _write_report(
        tmp_path / "report-latest.json",
        {
            "module_0": {"title": "Lead", "body": "Real."},
            "module_3": {"title": "Empty", "items": []},
        },
    )
    rc = main(["--report", str(p), "--json"])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["audited"] == 1
    assert payload["fail_count"] == 1
    assert payload["error_count"] == 0
    assert payload["results"][0]["empty_unprovenanced"] == ["module_3"]


def test_main_exits_2_on_parse_error(tmp_path, capsys):
    p = tmp_path / "broken.json"
    p.write_text("not-json", encoding="utf-8")
    rc = main(["--report", str(p)])
    assert rc == 2


def test_cli_smoke_via_subprocess(tmp_path):
    """End-to-end: invoke the script via Python so we know argparse + the
    script's __main__ block are wired correctly."""
    p = _write_report(
        tmp_path / "report-latest.json",
        {"module_3": {"title": "Empty", "items": []}},
    )
    result = subprocess.run(
        [sys.executable, str(HERE / "check_module_provenance.py"),
         "--report", str(p), "--json"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["fail_count"] == 1


# ── Standalone runner (matches the in-repo convention) ─────────────────────

if __name__ == "__main__":
    import inspect
    import traceback

    tests = [
        (name, obj) for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0

    class _CapsysShim:
        """Minimal stand-in for pytest's capsys when running as a script."""

        def __init__(self):
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            self._buf_out = None
            self._buf_err = None

        def __enter__(self):
            import io
            self._buf_out = io.StringIO()
            self._buf_err = io.StringIO()
            sys.stdout = self._buf_out
            sys.stderr = self._buf_err
            return self

        def __exit__(self, *exc):
            sys.stdout = self._stdout
            sys.stderr = self._stderr

        def readouterr(self):
            class _R:
                pass
            r = _R()
            r.out = self._buf_out.getvalue()
            r.err = self._buf_err.getvalue()
            return r

    import tempfile

    for name, fn in tests:
        try:
            sig = inspect.signature(fn)
            params = sig.parameters
            kwargs = {}
            tmp_ctx = None
            cap_ctx = None
            if "tmp_path" in params:
                tmp_ctx = tempfile.TemporaryDirectory()
                kwargs["tmp_path"] = pathlib.Path(tmp_ctx.__enter__())
            if "capsys" in params:
                cap_ctx = _CapsysShim()
                cap_ctx.__enter__()
                kwargs["capsys"] = cap_ctx
            try:
                fn(**kwargs)
                print(f"PASS  {name}")
                passed += 1
            finally:
                if cap_ctx is not None:
                    cap_ctx.__exit__(None, None, None)
                if tmp_ctx is not None:
                    tmp_ctx.__exit__(None, None, None)
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            failed += 1
        except Exception:
            print(f"ERROR {name}:")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)

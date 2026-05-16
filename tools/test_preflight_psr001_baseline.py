#!/usr/bin/env python3
"""
tools/test_preflight_psr001_baseline.py — unit tests for PSR-001 baseline-aware reshape.

Covers the four acceptance cases from W6b / AD-2026-05-13-CI-GATE-CALIBRATION-DOCTRINE:

  Case A: Baseline drift + PR adds no keys     → WARN per-slug, exit OK (no new FAIL)
  Case B: Baseline clean + PR adds 1 unrouted  → FAIL PSR-001:contract-coverage:new
  Case C: Baseline drift + PR removes 1 unrouted (PR-IS-CURE) → OK, no WARN
  Case D: Baseline-fetch failure (mock subprocess) → BOOTSTRAP-WARN, fallback absolute behaviour

Usage:
    python3 tools/test_preflight_psr001_baseline.py
    python3 -m pytest tools/test_preflight_psr001_baseline.py -v
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

THIS_DIR = Path(__file__).resolve().parent
# Support running from repo root or from tools/
# Allow override via env var for local testing
_env_override = os.environ.get("PREFLIGHT_PATH_OVERRIDE")
if _env_override and Path(_env_override).exists():
    PREFLIGHT_PATH = Path(_env_override)
elif (THIS_DIR / "preflight.py").exists():
    PREFLIGHT_PATH = THIS_DIR / "preflight.py"
elif (THIS_DIR.parent / "tools" / "preflight.py").exists():
    PREFLIGHT_PATH = THIS_DIR.parent / "tools" / "preflight.py"
else:
    raise FileNotFoundError("Cannot locate tools/preflight.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_preflight(repo_root: Path):
    """Load preflight.py with REPO_ROOT overridden to a temp fixture root."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("preflight_under_test", PREFLIGHT_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Override REPO_ROOT before exec so all path lookups hit the fixture
    mod.__dict__["REPO_ROOT"] = repo_root  # will be overwritten by module init
    spec.loader.exec_module(mod)
    # Patch after load
    mod.REPO_ROOT = repo_root
    return mod


def _make_contract_md(routes_by_slug: dict[str, list[str]]) -> str:
    """Build a minimal persistent-state-routing.md from a dict of {slug: [key, ...]}."""
    abbr_map = {
        "macro-monitor": "GMM",
        "ai-governance": "AGM",
        "environmental-risks": "ERM",
        "fimi-cognitive-warfare": "FCW",
        "democratic-integrity": "WDM",
        "conflict-escalation": "SCEM",
        "european-strategic-autonomy": "ESA",
    }
    lines = ["# persistent-state-routing.md (fixture)\n"]
    for slug, keys in routes_by_slug.items():
        abbr = abbr_map.get(slug, slug.upper()[:3])
        lines.append(f"### {abbr} — {slug}\n")
        lines.append("```yaml\n")
        lines.append("routes:\n")
        for k in keys:
            lines.append(f"  {k}: Section\n")
        lines.append("```\n")
    return "".join(lines)


def _make_ps_json(keys: list[str]) -> str:
    """Build a minimal persistent-state.json with the given top-level keys."""
    return json.dumps({k: {} for k in keys})


def _setup_fixture(
    tmp: Path,
    slug: str,
    abbr: str,
    head_keys: list[str],
    contract_keys: list[str],
) -> None:
    """Populate fixture tree for one monitor slug."""
    ps_dir = tmp / "static" / "monitors" / slug / "data"
    ps_dir.mkdir(parents=True, exist_ok=True)
    (ps_dir / "persistent-state.json").write_text(_make_ps_json(head_keys))

    contract_dir = tmp / "docs" / "monitors"
    contract_dir.mkdir(parents=True, exist_ok=True)
    contract_path = contract_dir / "persistent-state-routing.md"
    contract_path.write_text(_make_contract_md({slug: contract_keys}))


# ---------------------------------------------------------------------------
# A fake subprocess.run that returns a CompletedProcess-like object
# ---------------------------------------------------------------------------

def _fake_sp_success(baseline_ps_json: str, baseline_contract_text: str):
    """Factory: returns a fake sp.run that returns the given baseline content."""

    def _run(cmd, capture_output=True, text=True, cwd=None, **kw):
        result = MagicMock()
        result.returncode = 0
        cmd_str = " ".join(cmd)
        if "persistent-state.json" in cmd_str:
            result.stdout = baseline_ps_json
        elif "persistent-state-routing.md" in cmd_str:
            result.stdout = baseline_contract_text
        else:
            result.stdout = ""
            result.returncode = 1
        return result

    return _run


def _fake_sp_failure():
    """Factory: returns a fake sp.run that always fails (simulates baseline-fetch failure)."""

    def _run(cmd, capture_output=True, text=True, cwd=None, **kw):
        result = MagicMock()
        result.returncode = 128
        result.stdout = ""
        result.stderr = "fatal: not a git repository"
        return result

    return _run


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestPSR001BaselineAwareReshape(unittest.TestCase):
    """Four acceptance tests per W6b BRIEF."""

    # ── Case A: Baseline drift + PR adds no new keys → WARN, exit OK ──────

    def test_case_a_baseline_drift_no_new_keys_emits_warn_not_fail(self):
        """
        Baseline has 2 unrouted keys; PR HEAD has the same 2 unrouted keys.
        Expected: PSR-001:contract-coverage:pre-existing WARN (per slug);
                  PSR-001:contract-coverage:baseline-aware OK;
                  NO PSR-001:contract-coverage:new FAIL.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            slug = "macro-monitor"
            abbr = "GMM"
            # Contract routes only 3 keys; persistent-state has 5
            head_keys = ["module_1", "module_2", "module_3", "module_4", "module_7"]
            contract_keys = ["module_1", "module_2", "module_3"]

            _setup_fixture(tmp, slug, abbr, head_keys, contract_keys)
            pfmod = _load_preflight(tmp)

            baseline_ps = _make_ps_json(head_keys)  # same drift on baseline
            baseline_contract = _make_contract_md({slug: contract_keys})

            # Patch subprocess.run globally — the function uses the stdlib import
            with patch("subprocess.run", side_effect=_fake_sp_success(baseline_ps, baseline_contract)):
                r = pfmod.Results()
                pfmod.check_persistent_state_routing(r)

            fail_ids = [c for c, _ in r.failed]
            warn_ids = [c for c, _ in r.warnings]
            ok_ids = [c for c, _ in r.passed]

            # No new-key failures
            self.assertNotIn("PSR-001:contract-coverage:new", fail_ids,
                             f"Expected no new-key FAIL but got: {r.failed}")
            # Pre-existing warn present
            self.assertTrue(
                any("pre-existing" in c for c in warn_ids),
                f"Expected PSR-001:contract-coverage:pre-existing WARN but got warns: {warn_ids}",
            )
            # Baseline-aware OK present
            self.assertTrue(
                any("baseline-aware" in c for c in ok_ids),
                f"Expected PSR-001:contract-coverage:baseline-aware OK but got oks: {ok_ids}",
            )
            # Overall: no FAIL means exit 0
            self.assertEqual(len(r.failed), 0,
                             f"Expected 0 failures but got: {r.failed}")

    # ── Case B: Baseline clean + PR adds 1 unrouted key → FAIL ────────────

    def test_case_b_new_unrouted_key_on_pr_emits_fatal(self):
        """
        Baseline has 3 routed keys; PR HEAD adds a 4th that is not in the contract.
        Expected: PSR-001:contract-coverage:new FAIL.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            slug = "macro-monitor"
            abbr = "GMM"
            baseline_keys = ["module_1", "module_2", "module_3"]
            head_keys = ["module_1", "module_2", "module_3", "module_NEW"]
            contract_keys = ["module_1", "module_2", "module_3"]

            _setup_fixture(tmp, slug, abbr, head_keys, contract_keys)
            pfmod = _load_preflight(tmp)

            baseline_ps = _make_ps_json(baseline_keys)
            baseline_contract = _make_contract_md({slug: contract_keys})

            with patch("subprocess.run", side_effect=_fake_sp_success(baseline_ps, baseline_contract)):
                r = pfmod.Results()
                pfmod.check_persistent_state_routing(r)

            fail_ids = [c for c, _ in r.failed]
            self.assertIn("PSR-001:contract-coverage:new", fail_ids,
                          f"Expected PSR-001:contract-coverage:new FAIL but got: {r.failed}")
            # Confirm the new key is named in the detail
            new_fail_detail = next(d for c, d in r.failed if c == "PSR-001:contract-coverage:new")
            self.assertIn("module_NEW", new_fail_detail)

    # ── Case C: Baseline drift + PR cures 1 key (PR-IS-THE-CURE) → OK ─────

    def test_case_c_pr_is_the_cure_no_warn_no_fail(self):
        """
        Baseline has 2 unrouted keys (module_4, module_7).
        PR HEAD adds module_4 to the contract (only module_7 remains unrouted).
        The 1 remaining unrouted key is still pre-existing on baseline → WARN not FAIL.
        The newly-cured key must not cause a FAIL.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            slug = "macro-monitor"
            abbr = "GMM"
            # HEAD: persistent-state still has module_4 and module_7
            head_keys = ["module_1", "module_2", "module_4", "module_7"]
            # HEAD contract: module_4 is NOW routed (PR added it), module_7 still missing
            head_contract_keys = ["module_1", "module_2", "module_4"]

            _setup_fixture(tmp, slug, abbr, head_keys, head_contract_keys)
            pfmod = _load_preflight(tmp)

            # Baseline: neither module_4 nor module_7 was routed
            baseline_ps = _make_ps_json(head_keys)
            baseline_contract = _make_contract_md({slug: ["module_1", "module_2"]})

            with patch("subprocess.run", side_effect=_fake_sp_success(baseline_ps, baseline_contract)):
                r = pfmod.Results()
                pfmod.check_persistent_state_routing(r)

            fail_ids = [c for c, _ in r.failed]
            warn_ids = [c for c, _ in r.warnings]

            # No new-key failures (module_7 is pre-existing, not new)
            self.assertNotIn("PSR-001:contract-coverage:new", fail_ids,
                             f"PR-IS-THE-CURE should not emit new-key FAIL. Got: {r.failed}")
            self.assertEqual(len(r.failed), 0,
                             f"Expected 0 failures but got: {r.failed}")
            # module_7 pre-existing warn expected
            self.assertTrue(
                any("pre-existing" in c for c in warn_ids),
                f"Expected pre-existing WARN for module_7 but got: {warn_ids}",
            )

    # ── Case D: Baseline-fetch failure → BOOTSTRAP-WARN, absolute fallback ─

    def test_case_d_baseline_fetch_failure_falls_back_to_absolute(self):
        """
        subprocess.run always fails (simulating no git remote / detached HEAD).
        Expected: PSR-001:baseline-fetch BOOTSTRAP-WARN emitted;
                  falls back to absolute mode (same as pre-reshape behaviour).
        In absolute mode, unrouted keys → PSR-001:contract-coverage FAIL.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            slug = "macro-monitor"
            abbr = "GMM"
            head_keys = ["module_1", "module_2", "module_DRIFT"]
            contract_keys = ["module_1", "module_2"]

            _setup_fixture(tmp, slug, abbr, head_keys, contract_keys)
            pfmod = _load_preflight(tmp)

            with patch("subprocess.run", side_effect=_fake_sp_failure()):
                r = pfmod.Results()
                pfmod.check_persistent_state_routing(r)

            warn_ids = [c for c, _ in r.warnings]
            fail_ids = [c for c, _ in r.failed]

            # BOOTSTRAP-WARN emitted
            self.assertTrue(
                any("baseline-fetch" in c for c in warn_ids),
                f"Expected PSR-001:baseline-fetch BOOTSTRAP-WARN but got: {warn_ids}",
            )
            # Absolute-mode FAIL for the unrouted key
            self.assertTrue(
                any("contract-coverage" in c for c in fail_ids),
                f"Expected PSR-001:contract-coverage FAIL in absolute fallback but got: {r.failed}",
            )
            # The original aggregate check id (not the new baseline-aware ids)
            # PSR-001:contract-coverage should be present
            self.assertIn("PSR-001:contract-coverage", fail_ids,
                          f"Expected PSR-001:contract-coverage in fallback failures. Got: {fail_ids}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)

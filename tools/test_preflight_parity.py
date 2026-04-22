#!/usr/bin/env python3
"""
test_preflight_parity.py — unit tests for tools/preflight_parity.py.

Exercised branches
------------------
A. Manifest parsing — all 5 category tables parse correctly          → unit test
B. PARITY-001 clean   (byte-identical pair, md5 match)                → OK exit 0
C. PARITY-001 drift   (byte-identical pair, md5 differs)              → FAIL exit 1
D. PARITY-002 canonical-missing (byte-identical row, live-only)       → FAIL exit 1
E. PARITY-002 live-missing      (byte-identical row, canonical-only)  → FAIL exit 1
F. canonical-only row — both sides exempt regardless                  → OK
G. pre-canonical row — both sides exempt regardless                   → OK
H. known-drift row — md5 mismatch allow-listed                        → OK (logged)
I. known-drift row — missing side still fails PARITY-002              → FAIL
J. Regression demo — simulates reverting Class E back-port (d968fdf),
   expects PARITY-001 to fire on WDM + ERM synth-prompt               → FAIL with named files
K. JSON output shape                                                   → machine-parseable
L. Sentinel detection — missing both sentinels                        → exit 2
M. Manifest missing                                                    → exit 2

Usage:
    python3 tools/test_preflight_parity.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

THIS_DIR = Path(__file__).resolve().parent
PREFLIGHT = THIS_DIR / "preflight_parity.py"


# --------------------------------------------------------------------------- #
# Fixture builder
# --------------------------------------------------------------------------- #


def _mk_fake_repo(root: Path, side: str) -> None:
    """Build the minimum directory structure + sentinel file for one side.

    We use --self-test in most fixture runs (both sides = same root), so
    both sentinels go into the fixture. Production deployment has exactly
    one sentinel per checkout.
    """
    (root / "ops").mkdir(parents=True, exist_ok=True)
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "pipeline").mkdir(parents=True, exist_ok=True)

    # Sentinels (always both, since fixtures conflate internal + main)
    (root / "ops" / "ENGINE-RULES.md").write_text("# ENGINE-RULES (fixture)\n")
    (root / "tools" / "preflight.py").write_text("# preflight.py (fixture)\n")


_MANIFEST_TEMPLATE = dedent("""\
    # Canonical Artefacts Manifest (fixture)

    ## Byte-identical pairs

    | Monitor | Slot | Canonical (internal) | Live (main) |
    |---|---|---|---|
    {byte_rows}

    ## Canonical-only rows

    | Monitor | Slot | Canonical (internal) |
    |---|---|---|
    {canon_only_rows}

    ## Pre-canonical rows (FIM)

    | Abbr | Slot | Canonical path | Live path |
    |---|---|---|---|
    {pre_canon_rows}

    ## Known-drift rows

    | Monitor | Slot | Canonical | Live | Cause | Expiry |
    |---|---|---|---|---|---|
    {drift_rows}

    ## Manifest self-reference

    | Artefact | Canonical (internal) | Live (main) | Category |
    |---|---|---|---|
    {self_ref}
""")


def _write_manifest(root: Path, *, byte_rows=None, canon_only_rows=None,
                    pre_canon_rows=None, drift_rows=None, self_ref_row=True):
    def fmt(rows):
        return "\n".join(f"| {' | '.join(r)} |" for r in (rows or [])) or "| | | | |"

    self_ref = (
        "| This manifest | `ops/CANONICAL-ARTEFACTS.md` | `pipeline/CANONICAL-ARTEFACTS.md` | byte-identical |"
        if self_ref_row else "| | | | |"
    )
    text = _MANIFEST_TEMPLATE.format(
        byte_rows=fmt(byte_rows),
        canon_only_rows=fmt(canon_only_rows),
        pre_canon_rows=fmt(pre_canon_rows),
        drift_rows=fmt(drift_rows),
        self_ref=self_ref,
    )
    mp = root / "ops" / "CANONICAL-ARTEFACTS.md"
    mp.write_text(text)
    # Lift to main-side in fixture mode
    (root / "pipeline" / "CANONICAL-ARTEFACTS.md").write_text(text)


def _run(root: Path, *, json_out: bool = False, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(PREFLIGHT), "--self-test", "--repo-root", str(root)]
    if json_out:
        cmd.append("--json")
    if extra:
        cmd.extend(extra)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


class TestManifestParsing(unittest.TestCase):
    """Branch A — manifest parsing, with every category populated."""

    def test_all_categories_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            # matching content for byte-identical row
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.txt").write_text("hello\n")
            (root / "pipeline" / "live" / "mon").mkdir(parents=True)
            (root / "pipeline" / "live" / "mon" / "a.txt").write_text("hello\n")
            (root / "pipeline" / "mon" / "canon-only.md").write_text("canon-only\n")
            (root / "pipeline" / "live" / "mon" / "pre.txt").write_text("live-only\n")
            (root / "pipeline" / "mon" / "drift.json").write_text("{\"v\":1}\n")
            (root / "pipeline" / "live" / "mon" / "drift.json").write_text("{\"v\":2}\n")

            _write_manifest(root,
                byte_rows=[("FIX", "a", "`pipeline/mon/a.txt`", "`pipeline/live/mon/a.txt`")],
                canon_only_rows=[("FIX", "canon-only", "`pipeline/mon/canon-only.md`")],
                pre_canon_rows=[("FIX", "pre", "`pipeline/mon/pre.txt`", "`pipeline/live/mon/pre.txt`")],
                drift_rows=[("FIX", "drift", "`pipeline/mon/drift.json`", "`pipeline/live/mon/drift.json`", "test cause", "test expiry")],
            )
            result = _run(root, json_out=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            # 5 rows: 1 byte + 1 canon-only + 1 pre-canon + 1 known-drift + 1 self-ref
            self.assertEqual(data["rows_total"], 5)


class TestByteIdentical(unittest.TestCase):
    """Branches B, C — PARITY-001 clean + drift."""

    def test_clean_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.txt").write_text("identical\n")
            (root / "pipeline" / "live" / "mon").mkdir(parents=True)
            (root / "pipeline" / "live" / "mon" / "a.txt").write_text("identical\n")
            _write_manifest(root, byte_rows=[("X", "y", "`pipeline/mon/a.txt`", "`pipeline/live/mon/a.txt`")])
            r = _run(root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("all checks passed", r.stdout)

    def test_md5_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.txt").write_text("canonical content\n")
            (root / "pipeline" / "live" / "mon").mkdir(parents=True)
            (root / "pipeline" / "live" / "mon" / "a.txt").write_text("DIVERGED content\n")
            _write_manifest(root, byte_rows=[("X", "y", "`pipeline/mon/a.txt`", "`pipeline/live/mon/a.txt`")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            parity_001_fails = [c for c in data["checks"]
                                if c["check"] == "PARITY-001" and not c["passed"]]
            self.assertEqual(len(parity_001_fails), 1)
            f = parity_001_fails[0]
            self.assertIn("md5 mismatch", f["message"])
            self.assertNotEqual(f["canonical_md5"], f["live_md5"])


class TestPairExistence(unittest.TestCase):
    """Branches D, E — PARITY-002 one-sided drift."""

    def test_canonical_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "live" / "mon").mkdir(parents=True)
            (root / "pipeline" / "live" / "mon" / "a.txt").write_text("live-only\n")
            _write_manifest(root, byte_rows=[("X", "y", "`pipeline/mon/a.txt`", "`pipeline/live/mon/a.txt`")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            fails = [c for c in data["checks"] if not c["passed"]]
            self.assertEqual(len(fails), 1)
            self.assertEqual(fails[0]["check"], "PARITY-002")
            self.assertIn("canonical missing", fails[0]["message"])

    def test_live_missing(self):
        """Exact shape of the Class E gap this preflight is built to catch."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.txt").write_text("canonical only\n")
            _write_manifest(root, byte_rows=[("X", "y", "`pipeline/mon/a.txt`", "`pipeline/live/mon/a.txt`")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            fails = [c for c in data["checks"] if not c["passed"]]
            self.assertEqual(len(fails), 1)
            self.assertEqual(fails[0]["check"], "PARITY-002")
            self.assertIn("live missing", fails[0]["message"])


class TestExemptCategories(unittest.TestCase):
    """Branches F, G — canonical-only and pre-canonical rows are exempt."""

    def test_canonical_only_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            # NOTE: we intentionally do NOT create any file for the canon-only row
            _write_manifest(root, canon_only_rows=[("X", "y", "`pipeline/mon/ghost.md`")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertEqual(data["rows_exempt"], 1)

    def test_pre_canonical_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            _write_manifest(root, pre_canon_rows=[("FIM", "synth", "`pipeline/mon/fim.txt`", "`pipeline/live/fim.txt`")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertEqual(data["rows_exempt"], 1)


class TestKnownDrift(unittest.TestCase):
    """Branches H, I — known-drift allow-list + existence still enforced."""

    def test_known_drift_md5_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.json").write_text("{\"v\":1}\n")
            (root / "pipeline" / "live" / "mon").mkdir(parents=True)
            (root / "pipeline" / "live" / "mon" / "a.json").write_text("{\"v\":2}\n")
            _write_manifest(root, drift_rows=[("X", "y", "`pipeline/mon/a.json`", "`pipeline/live/mon/a.json`", "cause", "milestone")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            # Filter to the drift-category row only (self-reference row also
            # generates a PARITY-001 check of its own)
            drift_checks = [c for c in data["checks"]
                            if c["check"] == "PARITY-001"
                            and c["category"] == "known-drift"]
            self.assertEqual(len(drift_checks), 1)
            self.assertTrue(drift_checks[0]["passed"])
            self.assertIn("allow-listed", drift_checks[0]["message"])

    def test_known_drift_missing_side_still_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            (root / "pipeline" / "mon").mkdir(parents=True)
            (root / "pipeline" / "mon" / "a.json").write_text("{\"v\":1}\n")
            # live side missing
            _write_manifest(root, drift_rows=[("X", "y", "`pipeline/mon/a.json`", "`pipeline/live/mon/a.json`", "cause", "milestone")])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            fails = [c for c in data["checks"] if not c["passed"]]
            self.assertEqual(len(fails), 1)
            self.assertEqual(fails[0]["check"], "PARITY-002")


class TestRegressionDemo(unittest.TestCase):
    """Branch J — scope success criterion 3.

    Simulates the exact Class E gap: canonical side is at pre-d968fdf
    content, live side is at post-PR #98 content. PARITY-001 must fire
    on WDM + ERM synthesiser-prompt and name the affected files.
    """

    def test_d968fdf_revert_scenario(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            # Build the two file slots the Class E back-port touched
            wdm_c = root / "pipeline" / "monitors" / "democratic-integrity"
            wdm_l = root / "pipeline" / "synthesisers" / "wdm"
            erm_c = root / "pipeline" / "monitors" / "environmental-risks"
            erm_l = root / "pipeline" / "synthesisers" / "erm"
            for d in (wdm_c, wdm_l, erm_c, erm_l):
                d.mkdir(parents=True)

            # Canonical side = pre-back-port content (stale)
            (wdm_c / "synthesiser-prompt.txt").write_text("WDM v1 (pre Class E)\n")
            (erm_c / "synthesiser-prompt.txt").write_text("ERM v1 (pre Class E)\n")
            # Live side = post-PR #98 content (with ert_classification + electoral_environment + weaponisation_events etc)
            (wdm_l / "democratic-integrity-synthesiser-api-prompt.txt").write_text("WDM v2 (post Class E: ert_classification added)\n")
            (erm_l / "environmental-risks-synthesiser-api-prompt.txt").write_text("ERM v2 (post Class E: weaponisation_events added)\n")

            _write_manifest(root, byte_rows=[
                ("WDM", "synth-prompt",
                 "`pipeline/monitors/democratic-integrity/synthesiser-prompt.txt`",
                 "`pipeline/synthesisers/wdm/democratic-integrity-synthesiser-api-prompt.txt`"),
                ("ERM", "synth-prompt",
                 "`pipeline/monitors/environmental-risks/synthesiser-prompt.txt`",
                 "`pipeline/synthesisers/erm/environmental-risks-synthesiser-api-prompt.txt`"),
            ])
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 1, "PARITY-001 MUST fire when canonical is stale")
            data = json.loads(r.stdout)
            fails = [c for c in data["checks"] if c["check"] == "PARITY-001" and not c["passed"]]
            self.assertEqual(len(fails), 2, "both WDM and ERM synth-prompt rows must fail")
            monitors = {f["monitor"] for f in fails}
            self.assertEqual(monitors, {"WDM", "ERM"})
            # File names must appear in the failure message (so a human sees what to back-port)
            for f in fails:
                self.assertIn("synthesiser-prompt.txt", f["message"])
                self.assertIn("synthesiser-api-prompt.txt", f["message"])


class TestOutputShape(unittest.TestCase):
    """Branch K — JSON output is machine-parseable with the expected keys."""

    def test_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            _write_manifest(root)  # empty
            r = _run(root, json_out=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            for key in ("rows_total", "rows_checked", "rows_exempt", "failures", "checks"):
                self.assertIn(key, data)


class TestErrorPaths(unittest.TestCase):
    """Branches L, M — sentinel missing, manifest missing."""

    def test_missing_sentinels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # No sentinel files created
            r = _run(root, json_out=False)
            self.assertEqual(r.returncode, 2)
            self.assertIn("Neither sentinel found", r.stderr)

    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _mk_fake_repo(root, "self")
            # No manifest written
            r = _run(root, json_out=False)
            self.assertEqual(r.returncode, 2)
            self.assertIn("manifest not found", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

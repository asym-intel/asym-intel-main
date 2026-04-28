"""Unit tests for ops/update-pipeline-status.py Phase B cascade-file augmentation.

Added by Sprint AZ BRIEF-2 v2 §2. Tests build_phase_b_station_status() against
synthetic monitor directories in a tmpdir.

This is the first test file for the producer — earlier versions had no test
infra. Per BRIEF-2 v2 §2: "if no test infra exists yet, add minimal
tests/test_update_pipeline_status.py alongside PR-A — additive only".

Run:
    pytest tests/test_update_pipeline_status.py -v

(Or with stdlib unittest:)
    python -m unittest tests.test_update_pipeline_status
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Allow `import ops.update_pipeline_status` from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Module path: ops/update-pipeline-status.py — hyphenated filename, so import
# via importlib instead of `from ops import update_pipeline_status`.
import importlib.util

_module_path = REPO_ROOT / "ops" / "update-pipeline-status.py"
_spec = importlib.util.spec_from_file_location("update_pipeline_status", _module_path)
ups = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ups)


def _write_cascade_file(repo_root, monitor_slug, subdir, filename, payload):
    """Helper: write a synthetic cascade-output JSON file under tmpdir."""
    target_dir = Path(repo_root) / "pipeline" / "monitors" / monitor_slug / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return target


class TestBuildPhaseBStationStatus(unittest.TestCase):
    """Cascade-file-derived station status — BRIEF-2 v2 §2."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = self._tmpdir.name

    def tearDown(self):
        self._tmpdir.cleanup()

    # --- File missing ⇒ "never" ---

    def test_missing_file_returns_never_for_all_stages(self):
        for stage in ["interpret", "review", "compose", "apply", "curate"]:
            with self.subTest(stage=stage):
                result = ups.build_phase_b_station_status(
                    "macro-monitor", stage, repo_root=self.repo_root
                )
                self.assertEqual(
                    result,
                    {"last_run": None, "last_conclusion": "never", "last_success": None},
                    f"Missing {stage}-latest.json should yield 'never'",
                )

    # --- File present, no error ⇒ "success" with timestamp ---

    def test_interpret_present_no_error(self):
        _write_cascade_file(
            self.repo_root, "macro-monitor", "synthesised", "interpret-latest.json",
            {"_meta": {"synthesised_at": "2026-04-28T08:31:34Z",
                       "cycle_disposition": "material_change",
                       "schema_version": "gmm-interpret-v1.0"}},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "interpret", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertEqual(result["last_run"], "2026-04-28T08:31:34Z")
        self.assertEqual(result["last_success"], "2026-04-28T08:31:34Z")

    def test_review_present_error_false(self):
        _write_cascade_file(
            self.repo_root, "macro-monitor", "synthesised", "review-latest.json",
            {"_meta": {"reviewed_at": "2026-04-28T08:32:11Z",
                       "reviewer_error": False,
                       "schema_version": "gmm-review-v1.0"}},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "review", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertEqual(result["last_run"], "2026-04-28T08:32:11Z")
        self.assertEqual(result["last_success"], "2026-04-28T08:32:11Z")

    def test_compose_present_error_false(self):
        _write_cascade_file(
            self.repo_root, "macro-monitor", "synthesised", "compose-latest.json",
            {"_meta": {"composed_at": "2026-04-28T08:32:50Z",
                       "composer_error": False,
                       "cycle_disposition": "material_change"}},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "compose", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertEqual(result["last_run"], "2026-04-28T08:32:50Z")

    def test_apply_present_error_false(self):
        _write_cascade_file(
            self.repo_root, "macro-monitor", "applied", "apply-latest.json",
            {"_meta": {"applied_at": "2026-04-28T08:33:41Z",
                       "applier_error": False,
                       "cycle_disposition": "material_change",
                       "applier_flags": []}},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "apply", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertEqual(result["last_run"], "2026-04-28T08:33:41Z")

    def test_curate_present_no_error_field(self):
        # Curate stage has no explicit error field — presence ⇒ success
        _write_cascade_file(
            self.repo_root, "macro-monitor", "curator", "drift-register-latest.json",
            {"_meta": {"computed_at": "2026-04-28T08:34:05Z",
                       "cycle_id": "gmm-2026-04-28",
                       "schema_version": "aim-curator-drift-v1.0"}},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "curate", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertEqual(result["last_run"], "2026-04-28T08:34:05Z")

    # --- File present, error True ⇒ "failure" with last_success=None ---

    def test_review_error_true_yields_failure(self):
        _write_cascade_file(
            self.repo_root, "democratic-integrity", "synthesised", "review-latest.json",
            {"_meta": {"reviewed_at": "2026-04-27T00:02:26Z",
                       "reviewer_error": True,
                       "reviewer_error_reason": "schema mismatch"}},
        )
        result = ups.build_phase_b_station_status(
            "democratic-integrity", "review", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "failure")
        self.assertEqual(result["last_run"], "2026-04-27T00:02:26Z")
        self.assertIsNone(
            result["last_success"],
            "last_success must be None on failure (no recent successful landing)",
        )

    def test_apply_error_true_yields_failure(self):
        _write_cascade_file(
            self.repo_root, "democratic-integrity", "applied", "apply-latest.json",
            {"_meta": {"applied_at": "2026-04-27T00:03:30Z",
                       "applier_error": True,
                       "applier_error_reason": "patch rejected"}},
        )
        result = ups.build_phase_b_station_status(
            "democratic-integrity", "apply", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "failure")
        self.assertIsNone(result["last_success"])

    # --- Edge cases ---

    def test_compose_null_timestamp_still_success(self):
        # Real-world case: compose-latest.json with composed_at=null but
        # composer_error=false. File landed, upstream stage left timestamp unset.
        _write_cascade_file(
            self.repo_root, "democratic-integrity", "synthesised", "compose-latest.json",
            {"_meta": {"composed_at": None,
                       "composer_error": False}},
        )
        result = ups.build_phase_b_station_status(
            "democratic-integrity", "compose", repo_root=self.repo_root
        )
        self.assertEqual(result["last_conclusion"], "success")
        self.assertIsNone(result["last_run"])
        self.assertIsNone(
            result["last_success"],
            "If timestamp is null, last_success is also None even on success",
        )

    def test_string_null_timestamp_normalised_to_none(self):
        # Some monitors emit the literal string "null" for unset timestamps
        _write_cascade_file(
            self.repo_root, "democratic-integrity", "synthesised", "interpret-latest.json",
            {"_meta": {"synthesised_at": "null",
                       "cycle_disposition": "null_cycle"}},
        )
        result = ups.build_phase_b_station_status(
            "democratic-integrity", "interpret", repo_root=self.repo_root
        )
        self.assertIsNone(result["last_run"])
        self.assertEqual(result["last_conclusion"], "success")

    def test_malformed_json_treated_as_missing(self):
        target_dir = Path(self.repo_root) / "pipeline" / "monitors" / "macro-monitor" / "applied"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "apply-latest.json").write_text("{ this is not valid json")
        result = ups.build_phase_b_station_status(
            "macro-monitor", "apply", repo_root=self.repo_root
        )
        self.assertEqual(
            result,
            {"last_run": None, "last_conclusion": "never", "last_success": None},
            "Malformed JSON should be treated as missing, not crash",
        )

    def test_empty_meta_present_success(self):
        # File with no _meta at all — degenerate but possible during a partial write
        _write_cascade_file(
            self.repo_root, "macro-monitor", "applied", "apply-latest.json", {},
        )
        result = ups.build_phase_b_station_status(
            "macro-monitor", "apply", repo_root=self.repo_root
        )
        # No _meta means no error field present — success per spec
        self.assertEqual(result["last_conclusion"], "success")
        self.assertIsNone(result["last_run"])

    # --- Schema mappings sanity ---

    def test_phase_b_cascade_files_complete(self):
        """All 5 Phase B canon stages must have a cascade-file mapping."""
        for stage in ["interpret", "review", "compose", "apply", "curate"]:
            self.assertIn(stage, ups.PHASE_B_CASCADE_FILES)
            self.assertIn(stage, ups.PHASE_B_TIMESTAMP_FIELD)
            self.assertIn(stage, ups.PHASE_B_ERROR_FIELD)

    def test_curate_filename_is_drift_register_latest(self):
        """Document the deviation from BRIEF-2 v2 §2 (says curate-latest.json)."""
        self.assertEqual(
            ups.PHASE_B_CASCADE_FILES["curate"],
            ("curator", "drift-register-latest.json"),
            "Real on-disk filename is drift-register-latest.json, not curate-latest.json",
        )


class TestReadCascadeFile(unittest.TestCase):
    """Lower-level test of the file reader helper."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = self._tmpdir.name

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_read_existing_file(self):
        target = _write_cascade_file(
            self.repo_root, "macro-monitor", "applied", "apply-latest.json",
            {"_meta": {"applied_at": "2026-04-28T08:33:41Z"}, "data": "x"},
        )
        self.assertTrue(target.exists())
        data = ups._read_cascade_file(
            "macro-monitor", "applied", "apply-latest.json", repo_root=self.repo_root
        )
        self.assertIsNotNone(data)
        self.assertEqual(data["_meta"]["applied_at"], "2026-04-28T08:33:41Z")

    def test_read_missing_file_returns_none(self):
        data = ups._read_cascade_file(
            "macro-monitor", "applied", "apply-latest.json", repo_root=self.repo_root
        )
        self.assertIsNone(data)


if __name__ == "__main__":
    unittest.main()

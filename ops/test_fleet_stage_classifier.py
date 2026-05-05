#!/usr/bin/env python3
"""Tests for ops/fleet_stage_classifier.py.

Run:
    python3 ops/test_fleet_stage_classifier.py
or:
    pytest ops/test_fleet_stage_classifier.py -v

Strategy:
- Build minimal in-memory artefacts for each stage in a tmp tree, point the
  classifier at it via REPO_ROOT monkeypatching, and assert the
  earliest_blocking_stage / blocker_reason / recommended_next_action for
  each shape we care about: clean, applier-failed, review-held-with-stale-
  upstream, publisher-pending, non-canonical-FIM.
- Also asserts overall green/amber/red mapping matches the spec in the
  module docstring.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory


# Import the classifier module as a sibling.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_stage_classifier as fsc  # noqa: E402


NOW = datetime(2026, 5, 5, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def _stage_paths(root: Path, slug: str) -> dict[str, Path]:
    base = root / "pipeline" / "monitors" / slug
    return {
        "interpret": base / "synthesised" / "interpret-latest.json",
        "review":    base / "synthesised" / "review-latest.json",
        "compose":   base / "synthesised" / "compose-latest.json",
        "apply":     base / "applied" / "apply-latest.json",
        "report":    root / "static" / "monitors" / slug / "data" / "report-latest.json",
    }


def _green_fixture(root: Path, slug: str, *, week_ending="2026-05-09",
                   week_label="W/E 9 May 2026") -> None:
    """Write a clean, green-state set of artefacts for `slug`."""
    p = _stage_paths(root, slug)
    t_int = _iso(NOW - timedelta(hours=4))
    t_rev = _iso(NOW - timedelta(hours=3))
    t_cmp = _iso(NOW - timedelta(hours=2))
    t_app = _iso(NOW - timedelta(hours=1))
    t_pub = _iso(NOW - timedelta(minutes=30))

    _write(p["interpret"], {
        "_meta": {"synthesised_at": t_int, "week_ending": week_ending,
                  "cycle_disposition": "normal_cycle"},
    })
    _write(p["review"], {
        "_meta": {"reviewed_at": t_rev, "reviewed_from_file": "interpret-latest.json"},
        "verdict": "publish",
        "verdict_reason": "all checks PASS",
    })
    _write(p["compose"], {
        "_meta": {"composed_at": t_cmp, "composed_from_file": "interpret-latest.json"},
    })
    _write(p["apply"], {
        "_meta": {"applied_at": t_app, "applier_error": False},
        "week_ending": week_ending,
        "inputs": {
            "interpret": {"content_sha1": fsc._file_sha1(p["interpret"])},
            "review":    {"content_sha1": fsc._file_sha1(p["review"])},
            "compose":   {"content_sha1": fsc._file_sha1(p["compose"])},
        },
        "patches_applied": [{}, {}, {}],
        "patches_apply_failed": [],
        "publication": {"ready_to_publish": True, "hold_reason": None},
    })
    _write(p["report"], {
        "meta": {"published": t_pub, "week_label": week_label, "issue": 1},
    })


# ─── Tests ────────────────────────────────────────────────────────────────


class FleetStageClassifierTests(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = fsc.REPO_ROOT
        fsc.REPO_ROOT = self.root

    def tearDown(self):
        fsc.REPO_ROOT = self._orig_root
        self.tmp.cleanup()

    # ----- Green state -----

    def test_clean_state_is_green(self):
        _green_fixture(self.root, "macro-monitor")
        result = fsc.classify_monitor("GMM", "macro-monitor", now=NOW)
        self.assertEqual(result["status"], "green")
        self.assertIsNone(result["earliest_blocking_stage"])
        self.assertIsNone(result["blocker_reason"])
        self.assertIsNone(result["recommended_next_action"])

    # ----- Applier patch failure (red) -----

    def test_applier_patch_failed_is_red_with_target_in_reason(self):
        _green_fixture(self.root, "ai-governance")
        # Inject a patch-apply failure into apply-latest.
        p = _stage_paths(self.root, "ai-governance")
        apply = json.loads(p["apply"].read_text())
        apply["publication"] = {
            "ready_to_publish": False,
            "hold_reason": "patch_apply_failed",
        }
        apply["patches_apply_failed"] = [{
            "patch_id": "_unstamped_0",
            "target_kb_path": "module_2.models[OpenAI/GPT-5.5]",
            "applier_rejection_reason": "target_missing:module_2",
        }]
        _write(p["apply"], apply)

        result = fsc.classify_monitor("AIM", "ai-governance", now=NOW)
        self.assertEqual(result["status"], "red")
        self.assertEqual(result["earliest_blocking_stage"], "apply")
        self.assertIn("target_missing:module_2", result["blocker_reason"])
        self.assertIn("module_2.models", result["blocker_reason"])
        self.assertIn("aim-interpreter.yml", result["recommended_next_action"])

    # ----- Review verdict hold-for-review with stale-vs-upstream (red) -----

    def test_review_held_with_stale_upstream_recommends_reviewer_rerun(self):
        _green_fixture(self.root, "conflict-escalation")
        p = _stage_paths(self.root, "conflict-escalation")
        # Move review back so it's older than interpret (stale-vs-upstream).
        review = json.loads(p["review"].read_text())
        review["verdict"] = "hold-for-review"
        review["verdict_reason"] = "hard-invariant FAIL: ['R1', 'R2', 'R8']"
        review["_meta"]["reviewed_at"] = _iso(NOW - timedelta(hours=8))
        _write(p["review"], review)
        # And bump interpret to be fresher than review.
        interp = json.loads(p["interpret"].read_text())
        interp["_meta"]["synthesised_at"] = _iso(NOW - timedelta(hours=2))
        _write(p["interpret"], interp)

        result = fsc.classify_monitor("SCEM", "conflict-escalation", now=NOW)
        self.assertEqual(result["status"], "red")
        self.assertEqual(result["earliest_blocking_stage"], "review")
        # Recommendation should be to rerun reviewer (stale-vs-upstream wins
        # over "fix interpret" when interpret is already fresh).
        self.assertIn("scem-reviewer.yml", result["recommended_next_action"])
        self.assertIn("force=true", result["recommended_next_action"])

    # ----- Publisher-pending (amber) -----

    def test_publisher_pending_is_amber(self):
        _green_fixture(self.root, "democratic-integrity",
                       week_ending="2026-05-09",
                       week_label="W/E 2 May 2026")  # report-latest from prior cycle
        result = fsc.classify_monitor("WDM", "democratic-integrity", now=NOW)
        self.assertEqual(result["status"], "amber")
        self.assertEqual(result["earliest_blocking_stage"], "published")
        self.assertIn("publisher pending", result["blocker_reason"])
        self.assertIn("democratic-integrity-publisher.yml",
                      result["recommended_next_action"])

    # ----- Apply stale-vs-upstream (amber) -----

    def test_apply_stale_vs_upstream_is_amber(self):
        _green_fixture(self.root, "macro-monitor")
        p = _stage_paths(self.root, "macro-monitor")
        # Mutate compose-latest content; that bumps its sha1 but the apply
        # block still records the old sha. Result: apply.stale_vs_upstream=true
        # via the compose stage.
        compose = json.loads(p["compose"].read_text())
        compose["_meta"]["composed_at"] = _iso(NOW - timedelta(minutes=30))
        compose["_meta"]["padding_to_change_sha"] = "x"
        _write(p["compose"], compose)
        result = fsc.classify_monitor("GMM", "macro-monitor", now=NOW)
        self.assertEqual(result["status"], "amber")
        self.assertEqual(result["earliest_blocking_stage"], "apply")
        self.assertIn("compose", result["stages"]["apply"]["stale_inputs"])
        self.assertIn("force=true", result["recommended_next_action"])

    # ----- Missing artefact on canonical track (red) -----

    def test_missing_interpret_on_canonical_is_red(self):
        # No fixtures written.
        result = fsc.classify_monitor("WDM", "democratic-integrity", now=NOW)
        self.assertEqual(result["status"], "red")
        self.assertEqual(result["earliest_blocking_stage"], "interpret")
        self.assertIn("missing", result["blocker_reason"])
        self.assertIn("wdm-interpreter.yml",
                      result["recommended_next_action"])

    # ----- FIM non-canonical track is amber not red -----

    def test_fim_missing_artefacts_is_amber(self):
        result = fsc.classify_monitor("FIM", "financial-integrity", now=NOW)
        self.assertEqual(result["status"], "amber")
        # Earliest blocker is whichever stage is missing first; we don't
        # over-assert on exact stage, only on the FIM amber demotion rule.

    # ----- Engine roll-up: any red => red -----

    def test_engine_status_rollup(self):
        # Set up: WDM green, GMM red, others missing (red on canonical).
        _green_fixture(self.root, "democratic-integrity")
        _green_fixture(self.root, "macro-monitor")
        # Break GMM.
        p = _stage_paths(self.root, "macro-monitor")
        apply = json.loads(p["apply"].read_text())
        apply["publication"]["ready_to_publish"] = False
        apply["publication"]["hold_reason"] = "patch_apply_failed"
        apply["patches_apply_failed"] = [{
            "target_kb_path": "x", "applier_rejection_reason": "target_missing:x",
        }]
        _write(p["apply"], apply)

        report = fsc.classify_fleet(now=NOW)
        self.assertEqual(report["engine"]["status"], "red")
        self.assertGreaterEqual(report["engine"]["red"], 1)
        # Schema version locked at 1.0 for this initial release.
        self.assertEqual(report["schema_version"], "1.0")
        # All 8 monitors covered.
        slugs = {m["slug"] for m in report["monitors"]}
        self.assertEqual(slugs, {"WDM", "GMM", "ESA", "FCW", "AIM", "ERM", "SCEM", "FIM"})

    # ----- Markdown render is non-empty and contains the table header -----

    def test_render_markdown_contains_table_header(self):
        _green_fixture(self.root, "macro-monitor")
        report = fsc.classify_fleet(now=NOW)
        md = fsc.render_markdown(report)
        self.assertIn("| Monitor | Status |", md)
        self.assertIn("Engine:", md)


if __name__ == "__main__":
    unittest.main()

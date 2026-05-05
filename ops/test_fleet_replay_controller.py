#!/usr/bin/env python3
"""Tests for ops/fleet_replay_controller.py.

Run:
    python3 ops/test_fleet_replay_controller.py
or:
    pytest ops/test_fleet_replay_controller.py -v

Strategy:
- We feed hand-built classifier records (mirroring the shape of
  fleet_stage_classifier.classify_monitor) into build_plan_for_monitor /
  build_fleet_plan and assert on the resulting plan.
- We never live-dispatch: dispatch_plan accepts a `runner` parameter and
  the `--execute` CLI path is exercised with a fake runner via
  build_plan_for_monitor + dispatch_plan.
- Coverage: SCEM forced reviewer/composer/applier flow, AIM target_missing
  blocked (no dispatch), WDM publisher-pending requires --allow-publish,
  FIM publisher always parked, force validation contract.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock


sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_replay_controller as frc  # noqa: E402


# ─── Helpers ──────────────────────────────────────────────────────────────


def _record(
    abbr: str, monitor_dir: str, *, status: str = "amber",
    earliest: str | None = None, blocker_reason: str | None = None,
    recommended: str | None = None,
) -> dict:
    """Build a classifier-shaped monitor record."""
    return {
        "slug": abbr,
        "monitor_dir": monitor_dir,
        "stages": {},
        "earliest_blocking_stage": earliest,
        "blocker_reason": blocker_reason,
        "recommended_next_action": recommended,
        "status": status,
    }


# ─── Tests ────────────────────────────────────────────────────────────────


class WorkflowMappingTests(unittest.TestCase):
    """Workflow filenames must come from the central WORKFLOW_FILES map."""

    def test_scem_publisher_uses_slug_filename(self):
        # SCEM's publisher is conflict-escalation-publisher.yml, NOT
        # scem-publisher.yml — guards against the obvious naming mistake.
        self.assertEqual(
            frc._workflow_for("SCEM", "publish"),
            "conflict-escalation-publisher.yml",
        )

    def test_aim_phase_b_uses_agm_prefix(self):
        # AIM Phase-B workflows use the legacy `agm-` prefix on disk.
        self.assertEqual(frc._workflow_for("AIM", "review"), "agm-reviewer.yml")
        self.assertEqual(frc._workflow_for("AIM", "apply"), "agm-applier.yml")

    def test_gmm_publisher_uses_macro_monitor_slug(self):
        self.assertEqual(
            frc._workflow_for("GMM", "publish"),
            "macro-monitor-publisher.yml",
        )

    def test_wdm_stage_workflows(self):
        self.assertEqual(frc._workflow_for("WDM", "interpret"), "wdm-interpreter.yml")
        self.assertEqual(frc._workflow_for("WDM", "review"), "wdm-reviewer.yml")
        self.assertEqual(frc._workflow_for("WDM", "compose"), "wdm-composer.yml")
        self.assertEqual(frc._workflow_for("WDM", "apply"), "wdm-applier.yml")


class GreenStateTests(unittest.TestCase):

    def test_green_monitor_is_noop(self):
        rec = _record("GMM", "macro-monitor", status="green",
                      earliest=None, blocker_reason=None, recommended=None)
        plan = frc.build_plan_for_monitor(rec)
        self.assertEqual(plan["safety_status"], "noop")
        self.assertIsNone(plan["workflow_file"])
        self.assertIsNone(plan["dispatch_command"])


class ForceValidationTests(unittest.TestCase):

    def test_force_reason_too_short_fails_validation(self):
        errs = frc._validate_force_audit(
            force_reason="too short", force_ad="AD-2026-04-24l",
            force_operator="@ops-oncall",
        )
        self.assertTrue(any("force_reason must be" in e for e in errs))

    def test_missing_force_ad_fails(self):
        errs = frc._validate_force_audit(
            force_reason="A" * 30, force_ad=None,
            force_operator="@ops-oncall",
        )
        self.assertTrue(any("force_ad" in e for e in errs))

    def test_complete_force_audit_passes(self):
        errs = frc._validate_force_audit(
            force_reason="AD-2026-04-24l reviewer rerun after stale upstream",
            force_ad="AD-2026-04-24l",
            force_operator="@ops-oncall",
        )
        self.assertEqual(errs, [])


class SCEMForcedReviewerTests(unittest.TestCase):
    """SCEM stale-vs-upstream review — the canonical force chain shape."""

    def _scem_review_force_record(self) -> dict:
        return _record(
            "SCEM", "conflict-escalation", status="red",
            earliest="review",
            blocker_reason="review stale vs upstream",
            recommended=(
                "dispatch scem-reviewer.yml with force=true "
                "(review stale vs interpret) (prior verdict was 'hold-for-review' — "
                "may clear on rerun)"
            ),
        )

    def test_dry_run_default_surfaces_force_audit_template(self):
        rec = self._scem_review_force_record()
        plan = frc.build_plan_for_monitor(rec)
        # Even without execute, dry-run plan must surface the force_audit
        # block so the operator sees what to fill in.
        self.assertEqual(plan["workflow_file"], "scem-reviewer.yml")
        self.assertEqual(plan["safety_status"], "dry_run")
        self.assertIsNotNone(plan["force_audit"])
        self.assertEqual(plan["workflow_inputs"]["force"], "true")
        # Validation errors are present because no force fields supplied.
        self.assertTrue(plan["validation_errors"])

    def test_execute_without_force_audit_blocks_on_validation(self):
        rec = self._scem_review_force_record()
        plan = frc.build_plan_for_monitor(
            rec, execute=True, target_monitor="SCEM", target_stage="review",
        )
        self.assertEqual(plan["safety_status"], "blocked_validation")
        self.assertTrue(plan["validation_errors"])

    def test_execute_with_full_force_audit_is_ready_to_dispatch(self):
        rec = self._scem_review_force_record()
        plan = frc.build_plan_for_monitor(
            rec, execute=True, target_monitor="SCEM", target_stage="review",
            force_reason=(
                "AD-2026-04-24l reviewer same-day rerun after forced applier"
            ),
            force_ad="AD-2026-04-24l",
            force_operator="@ops-oncall",
        )
        self.assertEqual(plan["safety_status"], "ready_to_dispatch")
        self.assertEqual(plan["force_audit"]["force_ad"], "AD-2026-04-24l")
        # Dispatch command must include the force inputs verbatim.
        self.assertIn("scem-reviewer.yml", plan["dispatch_command"])
        self.assertIn("force=true", plan["dispatch_command"])
        self.assertIn("force_ad=AD-2026-04-24l", plan["dispatch_command"])

    def test_targeting_other_monitor_keeps_plan_in_dry_run(self):
        rec = self._scem_review_force_record()
        plan = frc.build_plan_for_monitor(
            rec, execute=True, target_monitor="WDM", target_stage="review",
            force_reason="A" * 30, force_ad="AD-X", force_operator="@x",
        )
        # SCEM should not be dispatched when target is WDM.
        self.assertEqual(plan["safety_status"], "dry_run")


class AIMTargetMissingTests(unittest.TestCase):
    """AIM patch_apply_failed: target_missing — classifier recommends fixing
    interpret-side facts, NOT applier rerun. Controller must NOT dispatch."""

    def test_target_missing_is_blocked_needs_human(self):
        rec = _record(
            "AIM", "ai-governance", status="red", earliest="apply",
            blocker_reason=(
                "patch_apply_failed: target_missing:module_2 at "
                "module_2.models[OpenAI/GPT-5.5]"
            ),
            recommended=(
                "investigate patches_apply_failed — fix interpret-side "
                "claim, then dispatch aim-interpreter.yml; downstream "
                "chain reruns automatically"
            ),
        )
        plan = frc.build_plan_for_monitor(
            rec, execute=True, target_monitor="AIM", target_stage="apply",
            force_reason="A" * 30, force_ad="AD-X", force_operator="@x",
        )
        # Recommendation does NOT name aim-applier.yml -> blocked-needs-human.
        self.assertEqual(plan["safety_status"], "blocked_needs_human")
        self.assertIsNone(plan["workflow_inputs"].get("force"))
        # No dispatch command should be issued for this stage.
        self.assertIsNone(plan["dispatch_command"])


class WDMPublisherPendingTests(unittest.TestCase):

    def _wdm_pub_pending_record(self) -> dict:
        return _record(
            "WDM", "democratic-integrity", status="amber",
            earliest="published",
            blocker_reason=(
                "publisher pending: report-latest shows 'W/E 2 May 2026' "
                "but apply-latest is ready for week_ending='2026-05-09'"
            ),
            recommended=(
                "dispatch democratic-integrity-publisher.yml — apply is "
                "ready, publisher has not yet propagated to report-latest"
            ),
        )

    def test_publisher_pending_dry_run_resolves_correct_workflow(self):
        plan = frc.build_plan_for_monitor(self._wdm_pub_pending_record())
        self.assertEqual(plan["controller_stage"], "publish")
        self.assertEqual(
            plan["workflow_file"], "democratic-integrity-publisher.yml"
        )
        self.assertEqual(plan["safety_status"], "dry_run")

    def test_publisher_execute_without_allow_publish_is_blocked(self):
        plan = frc.build_plan_for_monitor(
            self._wdm_pub_pending_record(),
            execute=True, target_monitor="WDM", target_stage="publish",
            allow_publish=False,
        )
        self.assertEqual(plan["safety_status"], "blocked_publish_gate")
        self.assertIn("--allow-publish", plan["publish_blocked_reason"])

    def test_publisher_execute_with_allow_publish_is_ready(self):
        plan = frc.build_plan_for_monitor(
            self._wdm_pub_pending_record(),
            execute=True, target_monitor="WDM", target_stage="publish",
            allow_publish=True,
        )
        self.assertEqual(plan["safety_status"], "ready_to_dispatch")
        self.assertEqual(
            plan["workflow_file"], "democratic-integrity-publisher.yml"
        )
        # Publisher dispatch carries no force audit by design.
        self.assertEqual(plan["workflow_inputs"], {})


class FIMParkedTests(unittest.TestCase):

    def test_fim_publisher_is_always_parked(self):
        rec = _record(
            "FIM", "financial-integrity", status="amber",
            earliest="published",
            blocker_reason="report-latest missing",
            recommended=(
                "dispatch financial-integrity-publisher.yml "
                "(report-latest missing)"
            ),
        )
        plan = frc.build_plan_for_monitor(
            rec, execute=True, target_monitor="FIM", target_stage="publish",
            allow_publish=True,  # even with allow-publish, FIM is parked
        )
        self.assertEqual(plan["safety_status"], "blocked_parked")
        self.assertIn("parked", plan["publish_blocked_reason"])


class DispatchTests(unittest.TestCase):

    def test_dispatch_only_runs_for_ready_plans(self):
        plan = {"safety_status": "blocked_validation"}
        result = frc.dispatch_plan(plan, runner=lambda *a, **kw: None)
        self.assertFalse(result["dispatched"])
        self.assertIn("not ready", result["reason"])

    def test_dispatch_invokes_runner_with_argv_no_shell(self):
        plan = {
            "safety_status": "ready_to_dispatch",
            "workflow_file": "scem-reviewer.yml",
            "workflow_inputs": {
                "force": "true",
                "force_reason": "AD-2026-04-24l reviewer rerun",
                "force_ad": "AD-2026-04-24l",
                "force_operator": "@ops-oncall",
            },
        }
        fake = MagicMock()
        fake.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = frc.dispatch_plan(plan, runner=fake)
        self.assertTrue(result["dispatched"])
        # First positional arg must be argv list, NOT a shell string.
        argv = fake.call_args.args[0]
        self.assertEqual(argv[0], "gh")
        self.assertEqual(argv[:4], ["gh", "workflow", "run", "scem-reviewer.yml"])
        self.assertIn("force=true", argv)
        self.assertIn("force_reason=AD-2026-04-24l reviewer rerun", argv)


class FleetPlanTests(unittest.TestCase):

    def test_fleet_plan_aggregates_safety_counts(self):
        classifier_report = {
            "engine": {"status": "red"},
            "monitors": [
                _record("GMM", "macro-monitor", status="green"),
                _record(
                    "WDM", "democratic-integrity", status="amber",
                    earliest="published",
                    blocker_reason="publisher pending: x",
                    recommended="dispatch democratic-integrity-publisher.yml",
                ),
                _record(
                    "FIM", "financial-integrity", status="amber",
                    earliest="published",
                    blocker_reason="report-latest missing",
                    recommended="dispatch financial-integrity-publisher.yml",
                ),
            ],
        }
        report = frc.build_fleet_plan(classifier_report)
        # GMM noop, WDM dry_run, FIM blocked_parked.
        self.assertEqual(report["safety_counts"].get("noop"), 1)
        self.assertEqual(report["safety_counts"].get("dry_run"), 1)
        self.assertEqual(report["safety_counts"].get("blocked_parked"), 1)
        self.assertEqual(report["engine_classifier_status"], "red")

    def test_render_markdown_contains_table_and_safety(self):
        classifier_report = {
            "engine": {"status": "amber"},
            "monitors": [
                _record(
                    "WDM", "democratic-integrity", status="amber",
                    earliest="published",
                    blocker_reason="publisher pending: x",
                    recommended="dispatch democratic-integrity-publisher.yml",
                ),
            ],
        }
        report = frc.build_fleet_plan(classifier_report)
        md = frc.render_markdown(report)
        self.assertIn("| Monitor | Stage |", md)
        self.assertIn("Safety:", md)
        self.assertIn("democratic-integrity-publisher.yml", md)


class CLIArgValidationTests(unittest.TestCase):

    def test_execute_without_monitor_fails(self):
        rc = frc.main(["--execute"])
        self.assertEqual(rc, 2)

    def test_execute_without_stage_fails(self):
        rc = frc.main(["--execute", "--monitor", "SCEM"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()

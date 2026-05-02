#!/usr/bin/env python3
"""
test_dependabot_skip_invariant.py — guards the bot-PR CI noise fix.

Why this test exists
--------------------
Dependabot PRs cannot read the cross-repo PAT (COMPUTER_SHIM_INTERNAL_READ),
so any parity workflow that calls into asym-intel-internal will fail with a
noisy red check on every dependency bump PR (#110, #113, etc).

The fix on `canonical-parity.yml` (the future-required `parity` context)
keeps the check-run name reporting success on dependabot PRs by short-
circuiting work *inside* the job via a `Scope check` step, NOT by skipping
the job. A job-level `if:` skip would erase the `parity` context entirely —
so when branch protection promotes `parity` to required, dependabot PRs
would block on a "missing required check" instead.

This invariant pins that distinction: workflows whose top-level job
publishes a check-run name in REQUIRED_OR_FUTURE_REQUIRED must NOT carry
a top-level job-level `if:`. They must use a step-level scope guard.

Advisory workflows (PARITY-003 etc.) are exempt — a job-level skip is fine
because the context is not in `branches/main/protection.required_status_checks`.

Run:  python3 tools/test_dependabot_skip_invariant.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

# Workflows whose top-level job publishes a check-run name that is either
# already in branches/main/protection.required_status_checks OR is on the
# documented promotion path. Adding a job-level `if:` to any of these would
# erase the check name from the run, breaking required-context resolution.
#
# Format: workflow filename -> set of job ids whose top level must stay un-skipped.
REQUIRED_OR_FUTURE_REQUIRED: dict[str, set[str]] = {
    "canonical-parity.yml": {"parity"},
}


def _load_workflow(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


class DependabotSkipInvariant(unittest.TestCase):
    def test_required_parity_jobs_have_no_top_level_if(self) -> None:
        """Required / future-required parity jobs must NOT carry a job-level `if:`.

        A top-level skip erases the check-run name. Use a step-level Scope
        check guard inside the job instead.
        """
        for filename, job_ids in REQUIRED_OR_FUTURE_REQUIRED.items():
            wf_path = WORKFLOWS_DIR / filename
            self.assertTrue(
                wf_path.exists(),
                f"workflow {filename} listed in REQUIRED_OR_FUTURE_REQUIRED is missing",
            )
            wf = _load_workflow(wf_path)
            jobs = wf.get("jobs", {}) or {}
            for job_id in job_ids:
                self.assertIn(
                    job_id,
                    jobs,
                    f"{filename}: expected job id `{job_id}` (publishes a "
                    f"required / future-required check name)",
                )
                job = jobs[job_id] or {}
                self.assertNotIn(
                    "if",
                    job,
                    f"{filename}: job `{job_id}` has a top-level `if:` — this "
                    f"erases the check-run name on skipped runs and would "
                    f"break required-context resolution. Use a step-level "
                    f"Scope check (see canonical-parity.yml) instead.",
                )

    def test_canonical_parity_has_step_level_scope_guard(self) -> None:
        """canonical-parity.yml must short-circuit on dependabot via a step.

        The fix keeps the `parity` check-run name reporting success on
        dependabot PRs by gating subsequent steps with
        `if: steps.scope.outputs.in_scope == 'true'`. Without a Scope step
        the dependabot fix has been reverted and bot PRs will go red again.
        """
        wf_path = WORKFLOWS_DIR / "canonical-parity.yml"
        wf = _load_workflow(wf_path)
        steps = (wf.get("jobs", {}).get("parity", {}) or {}).get("steps", []) or []
        self.assertTrue(steps, "canonical-parity.yml: parity job has no steps")

        # The first step should be the Scope check producing in_scope output.
        first = steps[0]
        self.assertEqual(
            first.get("id"),
            "scope",
            "canonical-parity.yml: first step of `parity` must be the Scope "
            "check (id: scope) so subsequent steps can gate on its output",
        )
        run_block = first.get("run", "") or ""
        self.assertIn(
            "dependabot[bot]",
            run_block,
            "canonical-parity.yml: Scope check must inspect dependabot actor "
            "or PR user to short-circuit bot PRs",
        )
        self.assertIn(
            "in_scope",
            run_block,
            "canonical-parity.yml: Scope check must emit `in_scope` output",
        )

        # At least one subsequent step must consume the scope output.
        gated = [
            s for s in steps[1:]
            if "steps.scope.outputs.in_scope" in (s.get("if") or "")
        ]
        self.assertTrue(
            gated,
            "canonical-parity.yml: no step gates on "
            "`steps.scope.outputs.in_scope` — Scope check is dead code",
        )


def main() -> int:
    suite = unittest.TestLoader().loadTestsFromTestCase(DependabotSkipInvariant)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

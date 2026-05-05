#!/usr/bin/env python3
"""
ops/fleet_replay_controller.py

Governed replay/reissue controller for fleet stage reruns. Consumes the
read-only output of `ops/fleet_stage_classifier.py` and converts each
monitor's earliest blocking stage into a *concrete, audited* replay plan
(workflow file + inputs + force-audit metadata + safety status). It is
dry-run by default and only emits a `gh workflow run` dispatch when the
operator passes explicit, scoped flags.

Design constraints (Phase B canon, AD-2026-04-24l force contract):

  1. Dry-run by default. Dispatch requires `--execute` AND a monitor scope
     (`--monitor SCEM`) AND a stage scope (`--stage review`).
  2. Stage ordering: interpret -> review -> compose -> apply -> publish.
     The earliest legal next stage is selected from the classifier; we do
     NOT blindly rerun all stages.
  3. Force gating: reviewer/composer/applier same-day/stale recovery
     requires `--force-reason` (>= 20 chars), `--force-ad`, `--force-operator`.
     Validation runs *before* dispatch; the audit block is rendered into
     JSON/Markdown output.
  4. Publisher gating: never publish unless `--allow-publish` is passed
     alongside `--execute`. FIM publish is *always* blocked (parked).
  5. Workflow filenames come from the central `WORKFLOW_FILES` map in
     `ops/update-pipeline-status.py` so the publisher slug map (e.g.
     conflict-escalation-publisher.yml, NOT scem-publisher.yml) and the
     AIM/AGM Phase-B prefix difference (agm-applier.yml, NOT aim-applier.yml)
     are honoured.
  6. Output: monitor, current earliest blocker, recommended action,
     proposed workflow file, workflow inputs, force audit (if any),
     publish blocked reason (if any), and `safety_status` ∈
     {dry_run, ready_to_dispatch, blocked}.

The controller does NOT bypass classifier gates. If the classifier says
green (no blocker), the controller emits no plan. If the classifier
recommends "fix interpret-side facts", the controller does not auto-rerun
the upstream stage on a guess — it surfaces the human action and marks
the monitor blocked-needs-human.

Usage:
    # Default dry-run plan, all monitors, JSON to stdout:
    python3 ops/fleet_replay_controller.py

    # Markdown plan:
    python3 ops/fleet_replay_controller.py --md

    # Dispatch a single monitor/stage with full force audit:
    python3 ops/fleet_replay_controller.py \
        --execute --monitor SCEM --stage review \
        --force-reason "AD-2026-04-24l reviewer same-day rerun after \
            forced applier — see SCEM Issue 10" \
        --force-ad AD-2026-04-24l \
        --force-operator @ops-oncall

    # Dispatch SCEM publisher (publisher gating):
    python3 ops/fleet_replay_controller.py \
        --execute --monitor SCEM --stage publish --allow-publish
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Repo root (this file lives at ops/).
REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Dependencies ─────────────────────────────────────────────────────────


sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_stage_classifier as fsc  # noqa: E402


def _load_workflow_files() -> dict[tuple[str, str], str]:
    """Load `WORKFLOW_FILES` from ops/update-pipeline-status.py.

    Single source of truth — keeps publisher slug map (e.g. SCEM ->
    conflict-escalation-publisher.yml) and AIM/AGM Phase-B prefix in sync
    with the workflow-run classifier without copying the table.

    The source filename has dashes, so we load it via importlib.spec.
    """
    src = Path(__file__).resolve().parent / "update-pipeline-status.py"
    spec = importlib.util.spec_from_file_location("_ups", src)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load WORKFLOW_FILES source at {src}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.WORKFLOW_FILES)


# Eager-load so callers can patch this module-level dict in tests.
WORKFLOW_FILES: dict[tuple[str, str], str] = _load_workflow_files()


# Stages we own in the replay controller. Note `publish` is the controller's
# external label; the central WORKFLOW_FILES key is `publisher` and the
# classifier emits `published` for the artefact stage.
CONTROLLER_STAGES: tuple[str, ...] = ("interpret", "review", "compose", "apply", "publish")


# Stages that require a force audit when invoked by the controller. These
# are the same-day/stale guards proven through the SCEM force chain
# (reviewer -> composer -> applier).
FORCE_REQUIRED_STAGES: frozenset[str] = frozenset({"review", "compose", "apply"})


# Monitors that are parked from publish (no published surface yet, or no
# canonical track). Aligned with classifier NON_CANONICAL set.
PUBLISH_PARKED: frozenset[str] = frozenset({"FIM"})


# Force-reason length contract — matches reviewer/composer/applier thin
# workflows (`Required with force. 20-500 chars.`).
FORCE_REASON_MIN = 20
FORCE_REASON_MAX = 500


# ─── Plan derivation ──────────────────────────────────────────────────────


def _classifier_stage_to_controller_stage(earliest: str | None) -> str | None:
    """Map classifier earliest_blocking_stage to controller stage label."""
    if earliest is None:
        return None
    if earliest == "published":
        return "publish"
    if earliest in CONTROLLER_STAGES:
        return earliest
    return None


def _workflow_for(abbr: str, controller_stage: str) -> str | None:
    """Resolve the workflow filename for (monitor, stage).

    Uses the central `WORKFLOW_FILES` map. The map keys publisher under
    the literal string "publisher", but the controller exposes "publish"
    externally — translate here.
    """
    map_key = "publisher" if controller_stage == "publish" else controller_stage
    return WORKFLOW_FILES.get((abbr, map_key))


def _recommended_action_calls_for_stage(
    recommended: str | None, controller_stage: str | None
) -> bool:
    """Return True if the classifier's recommendation actually points at
    the controller's `controller_stage`. If not, the recommendation is
    something like "fix interpret-side facts" which the controller cannot
    execute and must surface as blocked-needs-human.
    """
    if not recommended or controller_stage is None:
        return False
    rec = recommended.lower()
    # Classifier wording: "dispatch <name>-<stage>.yml".
    if not rec.startswith("dispatch "):
        return False
    suffix_map = {
        "interpret": "-interpreter.yml",
        "review":    "-reviewer.yml",
        "compose":   "-composer.yml",
        "apply":     "-applier.yml",
        "publish":   "-publisher.yml",
    }
    suffix = suffix_map.get(controller_stage)
    return bool(suffix and suffix in rec)


def _force_audit_block(
    *, force_reason: str | None, force_ad: str | None,
    force_operator: str | None,
) -> dict[str, Any]:
    return {
        "force": True,
        "force_reason": force_reason,
        "force_ad": force_ad,
        "force_operator": force_operator,
    }


def _validate_force_audit(
    *, force_reason: str | None, force_ad: str | None,
    force_operator: str | None,
) -> list[str]:
    """Return list of validation errors (empty list = ok)."""
    errs: list[str] = []
    if not force_reason or not force_reason.strip():
        errs.append("force_reason is required")
    elif not (FORCE_REASON_MIN <= len(force_reason.strip()) <= FORCE_REASON_MAX):
        errs.append(
            f"force_reason must be {FORCE_REASON_MIN}-{FORCE_REASON_MAX} chars "
            f"(got {len(force_reason.strip())})"
        )
    if not force_ad or not force_ad.strip():
        errs.append("force_ad is required (e.g. AD-2026-04-24l)")
    if not force_operator or not force_operator.strip():
        errs.append("force_operator is required (e.g. @ops-oncall)")
    return errs


def build_plan_for_monitor(
    monitor_record: dict[str, Any],
    *,
    execute: bool = False,
    target_monitor: str | None = None,
    target_stage: str | None = None,
    allow_publish: bool = False,
    force_reason: str | None = None,
    force_ad: str | None = None,
    force_operator: str | None = None,
) -> dict[str, Any]:
    """Translate one classifier monitor record into a replay plan entry.

    The record shape is what `fleet_stage_classifier.classify_monitor`
    returns: keys include `slug` (the abbr), `earliest_blocking_stage`,
    `blocker_reason`, `recommended_next_action`, `status`.
    """
    abbr = monitor_record["slug"]
    earliest = monitor_record.get("earliest_blocking_stage")
    controller_stage = _classifier_stage_to_controller_stage(earliest)

    plan: dict[str, Any] = {
        "monitor": abbr,
        "monitor_dir": monitor_record.get("monitor_dir"),
        "classifier_status": monitor_record.get("status"),
        "earliest_blocking_stage": earliest,
        "blocker_reason": monitor_record.get("blocker_reason"),
        "controller_stage": controller_stage,
        "recommended_next_action": monitor_record.get("recommended_next_action"),
        "workflow_file": None,
        "workflow_inputs": {},
        "force_audit": None,
        "publish_blocked_reason": None,
        "validation_errors": [],
        "dispatch_command": None,
        "safety_status": "dry_run",
    }

    # Green / no-op.
    if controller_stage is None:
        plan["safety_status"] = "noop"
        return plan

    # Recommendation does not point at a stage the controller can dispatch
    # (e.g. "fix interpret-side facts then dispatch interpreter"). Surface
    # blocked-needs-human and *do not* substitute our own action.
    rec = monitor_record.get("recommended_next_action")
    if not _recommended_action_calls_for_stage(rec, controller_stage):
        plan["safety_status"] = "blocked_needs_human"
        plan["validation_errors"].append(
            f"classifier recommendation does not target {controller_stage} "
            f"workflow — needs human action: {rec!r}"
        )
        return plan

    workflow = _workflow_for(abbr, controller_stage)
    if workflow is None:
        plan["safety_status"] = "blocked_no_workflow"
        plan["validation_errors"].append(
            f"no workflow filename mapped for ({abbr}, {controller_stage})"
        )
        return plan
    plan["workflow_file"] = workflow

    # Publisher gate: parked monitors are never dispatched, full stop.
    if controller_stage == "publish" and abbr in PUBLISH_PARKED:
        plan["safety_status"] = "blocked_parked"
        plan["publish_blocked_reason"] = (
            f"{abbr} is parked from publish (no published surface yet)"
        )
        return plan

    # Determine if force is required for THIS dispatch. The classifier
    # writes "force=true" into the recommendation when it derived
    # stale-vs-upstream or apply-held; we mirror the same rule here so the
    # JSON force_audit reflects what the dispatcher would actually pass.
    needs_force = (
        controller_stage in FORCE_REQUIRED_STAGES
        and "force=true" in (rec or "").lower()
    )

    inputs: dict[str, Any] = {}
    if needs_force:
        # Validate the audit block whether or not we are executing — so
        # dry-run JSON shows the operator what they'd need to provide.
        errs = _validate_force_audit(
            force_reason=force_reason, force_ad=force_ad,
            force_operator=force_operator,
        )
        plan["validation_errors"].extend(errs)
        plan["force_audit"] = _force_audit_block(
            force_reason=force_reason, force_ad=force_ad,
            force_operator=force_operator,
        )
        inputs["force"] = "true"
        # Workflow string-typed inputs — the thin callers accept empty
        # strings on non-force runs, but force runs require non-empty.
        inputs["force_reason"] = force_reason or ""
        inputs["force_ad"] = force_ad or ""
        inputs["force_operator"] = force_operator or ""

    plan["workflow_inputs"] = inputs

    # Build the audit-visible dispatch command (always, even on dry-run).
    plan["dispatch_command"] = _build_dispatch_command(
        workflow=workflow, inputs=inputs,
    )

    # Decide final safety_status.
    targets_match = (
        execute
        and (target_monitor is None or target_monitor == abbr)
        and (target_stage is None or target_stage == controller_stage)
    )

    if not targets_match:
        plan["safety_status"] = "dry_run"
        return plan

    # We are executing for this monitor/stage. Apply remaining gates.
    if controller_stage == "publish" and not allow_publish:
        plan["safety_status"] = "blocked_publish_gate"
        plan["publish_blocked_reason"] = (
            "publish dispatch requires --allow-publish flag"
        )
        return plan

    if plan["validation_errors"]:
        plan["safety_status"] = "blocked_validation"
        return plan

    plan["safety_status"] = "ready_to_dispatch"
    return plan


def _build_dispatch_command(*, workflow: str, inputs: dict[str, Any]) -> str:
    """Build a `gh workflow run` command string for audit/preview.

    NOTE: this is the *string* the controller would dispatch — it is
    rendered into JSON/Markdown for operator review. The actual subprocess
    invocation in `dispatch_plan()` builds an argv list, not a shell
    string, to avoid quoting hazards.
    """
    parts = ["gh", "workflow", "run", workflow]
    for k, v in inputs.items():
        parts.extend(["-f", f"{k}={v}"])
    return " ".join(shlex.quote(p) for p in parts)


def _dispatch_argv(*, workflow: str, inputs: dict[str, Any]) -> list[str]:
    argv = ["gh", "workflow", "run", workflow]
    for k, v in inputs.items():
        argv.extend(["-f", f"{k}={v}"])
    return argv


# ─── Fleet-level plan + dispatcher ────────────────────────────────────────


def build_fleet_plan(
    classifier_report: dict[str, Any],
    *,
    execute: bool = False,
    target_monitor: str | None = None,
    target_stage: str | None = None,
    allow_publish: bool = False,
    force_reason: str | None = None,
    force_ad: str | None = None,
    force_operator: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    plans = [
        build_plan_for_monitor(
            m,
            execute=execute,
            target_monitor=target_monitor,
            target_stage=target_stage,
            allow_publish=allow_publish,
            force_reason=force_reason,
            force_ad=force_ad,
            force_operator=force_operator,
        )
        for m in classifier_report.get("monitors", [])
    ]
    counts: dict[str, int] = {}
    for p in plans:
        counts[p["safety_status"]] = counts.get(p["safety_status"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "execute": execute,
        "target_monitor": target_monitor,
        "target_stage": target_stage,
        "allow_publish": allow_publish,
        "engine_classifier_status": (
            (classifier_report.get("engine") or {}).get("status")
        ),
        "safety_counts": counts,
        "plans": plans,
    }


def dispatch_plan(plan: dict[str, Any], *, runner=subprocess.run) -> dict[str, Any]:
    """Dispatch a single plan entry via `gh workflow run`.

    Caller must have already verified `plan["safety_status"] ==
    "ready_to_dispatch"` — this is enforced again here as a defensive
    last-mile check. `runner` is injectable for tests so we never shell
    out under pytest.
    """
    if plan.get("safety_status") != "ready_to_dispatch":
        return {
            "dispatched": False,
            "reason": f"plan not ready: {plan.get('safety_status')}",
        }
    argv = _dispatch_argv(
        workflow=plan["workflow_file"],
        inputs=plan["workflow_inputs"],
    )
    proc = runner(argv, capture_output=True, text=True, check=False)
    return {
        "dispatched": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "argv": argv,
    }


# ─── Renderers ────────────────────────────────────────────────────────────


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Fleet replay plan — {report['generated_at']}\n")
    flags = []
    flags.append(f"execute={report['execute']}")
    if report["target_monitor"]:
        flags.append(f"target_monitor={report['target_monitor']}")
    if report["target_stage"]:
        flags.append(f"target_stage={report['target_stage']}")
    if report["allow_publish"]:
        flags.append("allow_publish=true")
    lines.append(f"**Flags:** {', '.join(flags)}  ")
    lines.append(
        f"**Classifier engine:** `{report.get('engine_classifier_status') or '—'}`  \n"
    )
    if report["safety_counts"]:
        bits = ", ".join(f"{k}={v}" for k, v in sorted(report["safety_counts"].items()))
        lines.append(f"**Safety:** {bits}\n")
    lines.append("| Monitor | Stage | Status | Workflow | Dispatch command | Notes |")
    lines.append("|---|---|---|---|---|---|")
    for p in report["plans"]:
        notes_bits: list[str] = []
        if p.get("blocker_reason"):
            notes_bits.append(p["blocker_reason"])
        if p.get("publish_blocked_reason"):
            notes_bits.append(p["publish_blocked_reason"])
        if p.get("validation_errors"):
            notes_bits.append("; ".join(p["validation_errors"]))
        if p.get("force_audit"):
            fa = p["force_audit"]
            notes_bits.append(
                f"force_audit: ad={fa.get('force_ad')}, op={fa.get('force_operator')}"
            )
        notes = " · ".join(notes_bits).replace("|", "\\|") or "—"
        cmd = (p.get("dispatch_command") or "—").replace("|", "\\|")
        lines.append(
            f"| {p['monitor']} | {p.get('controller_stage') or '—'} | "
            f"`{p['safety_status']}` | "
            f"{p.get('workflow_file') or '—'} | `{cmd}` | {notes} |"
        )
    return "\n".join(lines) + "\n"


# ─── CLI ──────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Governed replay/reissue controller for fleet stage reruns."
    )
    p.add_argument("--md", action="store_true",
                   help="emit markdown plan instead of JSON")
    p.add_argument("--out", type=str, default=None,
                   help="write output to this path instead of stdout")
    p.add_argument("--execute", action="store_true",
                   help="actually dispatch the matching plan entry "
                        "(requires --monitor and --stage)")
    p.add_argument("--monitor", type=str, default=None,
                   help="restrict execution to this monitor abbreviation")
    p.add_argument("--stage", type=str, default=None,
                   choices=list(CONTROLLER_STAGES),
                   help="restrict execution to this controller stage")
    p.add_argument("--allow-publish", action="store_true",
                   help="required to dispatch a publish stage")
    p.add_argument("--force-reason", type=str, default=None,
                   help=f"force audit reason ({FORCE_REASON_MIN}-"
                        f"{FORCE_REASON_MAX} chars)")
    p.add_argument("--force-ad", type=str, default=None,
                   help="force audit AD reference (e.g. AD-2026-04-24l)")
    p.add_argument("--force-operator", type=str, default=None,
                   help="force audit operator handle")
    args = p.parse_args(argv)

    if args.execute and (not args.monitor or not args.stage):
        print(
            "--execute requires both --monitor and --stage to scope dispatch",
            file=sys.stderr,
        )
        return 2

    classifier_report = fsc.classify_fleet()
    plan_report = build_fleet_plan(
        classifier_report,
        execute=args.execute,
        target_monitor=(args.monitor.upper() if args.monitor else None),
        target_stage=args.stage,
        allow_publish=args.allow_publish,
        force_reason=args.force_reason,
        force_ad=args.force_ad,
        force_operator=args.force_operator,
    )

    # Dispatch loop — only ready_to_dispatch entries fire, and the targeting
    # gates already restricted that set above.
    if args.execute:
        for p_entry in plan_report["plans"]:
            if p_entry["safety_status"] == "ready_to_dispatch":
                p_entry["dispatch_result"] = dispatch_plan(p_entry)

    out = (
        render_markdown(plan_report)
        if args.md
        else json.dumps(plan_report, indent=2, sort_keys=False) + "\n"
    )
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out} ({len(out)} bytes)", file=sys.stderr)
    else:
        sys.stdout.write(out)

    # Exit non-zero if execute was requested and any targeted dispatch
    # failed — supports CI orchestration.
    if args.execute:
        for p_entry in plan_report["plans"]:
            res = p_entry.get("dispatch_result") or {}
            if (
                p_entry["safety_status"] == "ready_to_dispatch"
                and res.get("dispatched") is False
            ):
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

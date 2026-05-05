#!/usr/bin/env python3
"""
ops/fleet_stage_classifier.py

Per-monitor *artefact-level* fleet status classifier. Complements
`ops/update-pipeline-status.py:_classify_monitor`, which classifies based on
GitHub Actions workflow-run history. This module classifies based on the
artefacts each stage actually wrote to disk (interpret-latest.json,
review-latest.json, compose-latest.json, apply-latest.json,
report-latest.json), so it can pinpoint the *earliest blocking stage* and
the next legal recovery action without manual archaeology.

Stage order (per Phase B canon, PIPELINE-CANONICAL v1.2):
    interpret -> review -> compose -> apply -> published

For each monitor, we determine:

  * present[stage]                 — artefact exists on disk
  * timestamp[stage]               — stage completion timestamp from _meta
  * sha[stage]                     — content_sha1 of the artefact (sha1 of file bytes)
  * stale_vs_upstream[stage]       — downstream stage older than upstream stage
  * blocked[stage]                 — explicit hold/error/missing on this stage
  * earliest_blocking_stage        — first stage in order that is blocked
                                     or stale-vs-upstream
  * blocker_reason                 — short string describing why
  * recommended_next_action        — the next legal recovery action

The classifier does NOT mutate state. It is read-only over artefacts. Output
is a JSON-serialisable dict suitable for either standalone consumption or
embedding into a future `fleet_blockers` block of pipeline-status.json.

Usage:
    python3 ops/fleet_stage_classifier.py            # writes JSON to stdout
    python3 ops/fleet_stage_classifier.py --md       # markdown summary table
    python3 ops/fleet_stage_classifier.py --out PATH # write JSON to file

Architectural notes:
- Stays decoupled from update-pipeline-status.py to avoid coupling artefact
  inspection (this) with workflow-run telemetry (that). Either can be wired
  into the public pipeline-status.json roll-up later via a `fleet_blockers`
  key without changing the existing classifier contract.
- Treats the classifier as a *recommender*, not a controller. Recovery
  actions are surfaced as strings ("dispatch agm-applier with force=true");
  no workflow is dispatched here.
- FIM is on a non-canonical track until financial-integrity ships, so the
  published-stage lookup tolerates a missing report-latest.json (downgrades
  to amber instead of red).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


# Repo root resolution: this script lives at ops/, so root is parent.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Monitor abbreviation -> filesystem slug. Mirrors MONITORS in
# ops/update-pipeline-status.py but keyed by the artefact-side slug we need
# here. ADVENNT is intentionally absent: it is a cross-repo *consumer* of
# monitor outputs, not a producer of interpret/review/compose/apply
# artefacts in this repo.
MONITORS: list[tuple[str, str]] = [
    ("WDM",  "democratic-integrity"),
    ("GMM",  "macro-monitor"),
    ("ESA",  "european-strategic-autonomy"),
    ("FCW",  "fimi-cognitive-warfare"),
    ("AIM",  "ai-governance"),
    ("ERM",  "environmental-risks"),
    ("SCEM", "conflict-escalation"),
    ("FIM",  "financial-integrity"),
]

# Non-canonical track: missing artefacts/published surface downgrade red->amber.
NON_CANONICAL = {"FIM"}

# Stage order for blocker selection.
STAGES: tuple[str, ...] = ("interpret", "review", "compose", "apply", "published")

# How old a stage timestamp can be before it is considered stale-vs-clock.
# Aligned with ops/update-pipeline-status.py STALE_AMBER_DAYS for parity with
# the workflow-run classifier.
STALE_AMBER_DAYS = 9
STALE_RED_DAYS = 21


# ─── Helpers ──────────────────────────────────────────────────────────────


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _file_sha1(path: Path) -> str | None:
    """Return sha1 of the file bytes, or None if absent. Matches the
    `content_sha1` field that the applier records under inputs.{stage}."""
    if not path.exists():
        return None
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# ─── Per-stage probes ─────────────────────────────────────────────────────


def _probe_interpret(slug: str) -> dict[str, Any]:
    path = REPO_ROOT / "pipeline" / "monitors" / slug / "synthesised" / "interpret-latest.json"
    data = _read_json(path)
    sha = _file_sha1(path)
    if data is None:
        return {
            "present": False, "timestamp": None, "sha": None,
            "week_ending": None, "blocked": True,
            "blocker_reason": "interpret-latest missing",
        }
    meta = data.get("_meta") or {}
    return {
        "present": True,
        "timestamp": meta.get("synthesised_at") or meta.get("generated_at"),
        "sha": sha,
        "week_ending": meta.get("week_ending"),
        "cycle_disposition": meta.get("cycle_disposition"),
        "null_signal_week": meta.get("null_signal_week"),
        "blocked": False,
        "blocker_reason": None,
    }


def _probe_review(slug: str, interpret: dict) -> dict[str, Any]:
    path = REPO_ROOT / "pipeline" / "monitors" / slug / "synthesised" / "review-latest.json"
    data = _read_json(path)
    sha = _file_sha1(path)
    if data is None:
        return {
            "present": False, "timestamp": None, "sha": None,
            "verdict": None, "stale_vs_upstream": None, "blocked": True,
            "blocker_reason": "review-latest missing",
        }
    meta = data.get("_meta") or {}
    reviewed_at = meta.get("reviewed_at")
    rev_dt = _parse_iso(reviewed_at)
    int_dt = _parse_iso(interpret.get("timestamp"))
    stale = bool(int_dt and rev_dt and rev_dt < int_dt)
    verdict = data.get("verdict")
    reviewer_error = bool(meta.get("reviewer_error"))
    blocked = False
    blocker_reason = None
    if reviewer_error:
        blocked = True
        blocker_reason = f"reviewer_error: {meta.get('reviewer_error_reason') or 'unspecified'}"
    elif verdict in {"hold-for-review", "reject"}:
        blocked = True
        blocker_reason = f"review_verdict:{verdict} — {data.get('verdict_reason') or 'unspecified'}"
    return {
        "present": True,
        "timestamp": reviewed_at,
        "sha": sha,
        "verdict": verdict,
        "verdict_reason": data.get("verdict_reason"),
        "stale_vs_upstream": stale,
        "blocked": blocked,
        "blocker_reason": blocker_reason,
    }


def _probe_compose(slug: str, review: dict) -> dict[str, Any]:
    path = REPO_ROOT / "pipeline" / "monitors" / slug / "synthesised" / "compose-latest.json"
    data = _read_json(path)
    sha = _file_sha1(path)
    if data is None:
        return {
            "present": False, "timestamp": None, "sha": None,
            "stale_vs_upstream": None, "blocked": True,
            "blocker_reason": "compose-latest missing",
        }
    meta = data.get("_meta") or {}
    composed_at = meta.get("composed_at")
    cmp_dt = _parse_iso(composed_at)
    rev_dt = _parse_iso(review.get("timestamp"))
    stale = bool(rev_dt and cmp_dt and cmp_dt < rev_dt)
    composer_error = bool(meta.get("composer_error"))
    blocked = False
    reason = None
    if composer_error:
        blocked = True
        reason = f"composer_error: {meta.get('composer_error_reason') or 'unspecified'}"
    return {
        "present": True,
        "timestamp": composed_at,
        "sha": sha,
        "cycle_disposition": meta.get("cycle_disposition"),
        "stale_vs_upstream": stale,
        "blocked": blocked,
        "blocker_reason": reason,
    }


def _probe_apply(slug: str, latest_shas: dict[str, str | None]) -> dict[str, Any]:
    path = REPO_ROOT / "pipeline" / "monitors" / slug / "applied" / "apply-latest.json"
    data = _read_json(path)
    if data is None:
        return {
            "present": False, "timestamp": None, "ready_to_publish": False,
            "stale_vs_upstream": None, "blocked": True,
            "blocker_reason": "apply-latest missing",
        }
    meta = data.get("_meta") or {}
    applied_at = meta.get("applied_at")
    inputs = data.get("inputs") or {}
    # Compare each input's recorded content_sha1 against the live latest sha.
    stale_inputs = []
    for stage in ("interpret", "review", "compose"):
        block = inputs.get(stage) or {}
        recorded = block.get("content_sha1")
        live = latest_shas.get(stage)
        if recorded and live and recorded != live:
            stale_inputs.append(stage)
    stale = bool(stale_inputs)
    publication = data.get("publication") or {}
    ready = bool(publication.get("ready_to_publish"))
    hold_reason = publication.get("hold_reason")
    apply_failed = data.get("patches_apply_failed") or []
    applier_error = bool(meta.get("applier_error"))
    blocked = False
    reason = None
    if applier_error:
        blocked = True
        reason = f"applier_error: {meta.get('applier_error_reason') or 'unspecified'}"
    elif apply_failed:
        # Surface the first failed patch detail to short-circuit triage.
        # Schema (per applier output): target_kb_path + applier_rejection_reason.
        first = apply_failed[0]
        target = (
            first.get("target_kb_path")
            or first.get("target")
            or first.get("patch_id")
            or "unknown"
        )
        why = (
            first.get("applier_rejection_reason")
            or first.get("reason")
            or "patch_apply_failed"
        )
        n = len(apply_failed)
        suffix = f" (+{n - 1} more)" if n > 1 else ""
        blocked = True
        reason = f"patch_apply_failed: {why} at {target}{suffix}"
    elif not ready and hold_reason:
        blocked = True
        reason = f"apply_held: {hold_reason}"
    elif not ready:
        blocked = True
        reason = "apply_held: ready_to_publish=False (no hold_reason)"
    return {
        "present": True,
        "timestamp": applied_at,
        "ready_to_publish": ready,
        "hold_reason": hold_reason,
        "patches_applied": len(data.get("patches_applied") or []),
        "patches_apply_failed": len(apply_failed),
        "force_reissue": meta.get("force_reissue"),
        "stale_vs_upstream": stale,
        "stale_inputs": stale_inputs,
        "week_ending": data.get("week_ending"),
        "blocked": blocked,
        "blocker_reason": reason,
    }


def _probe_published(slug: str, abbr: str, apply_block: dict) -> dict[str, Any]:
    path = REPO_ROOT / "static" / "monitors" / slug / "data" / "report-latest.json"
    data = _read_json(path)
    if data is None:
        # FIM is non-canonical track — published surface may legitimately
        # be absent. Caller will demote red->amber.
        return {
            "present": False, "timestamp": None, "issue_date": None,
            "stale_vs_upstream": None, "blocked": True,
            "blocker_reason": "report-latest missing",
        }
    meta = data.get("meta") or {}
    published_at = meta.get("published")
    week_label = meta.get("week_label")
    issue = meta.get("issue")

    # Stale-vs-upstream: if publication was held by the applier but a stale
    # report still exists, the published surface is divergent from the
    # current cycle. Approximate this by comparing apply.week_ending to the
    # week_label parsed from "W/E DD MONTH YYYY".
    stale = None
    apply_week = apply_block.get("week_ending")
    if apply_week and week_label:
        # week_label format: "W/E 5 May 2026" -> normalise to date string.
        try:
            parsed = datetime.strptime(week_label, "W/E %d %B %Y").date().isoformat()
            stale = parsed != apply_week
        except ValueError:
            stale = None

    blocked = False
    reason = None
    if stale is True:
        # report-latest carries an older week_label than apply-latest's
        # week_ending — publisher has not yet propagated the current cycle.
        # If apply is ready_to_publish, this is a publisher-pending state
        # (amber). If apply is held, the published surface is divergent
        # from the held cycle and the block surfaces here as well.
        blocked = True
        if apply_block.get("ready_to_publish"):
            reason = (
                f"publisher pending: report-latest shows {week_label!r} but "
                f"apply-latest is ready for week_ending={apply_week!r}"
            )
        else:
            reason = (
                f"report-latest stale and apply held: report shows {week_label!r}, "
                f"apply week_ending={apply_week!r}, hold_reason={apply_block.get('hold_reason')!r}"
            )

    return {
        "present": True,
        "timestamp": published_at,
        "issue_date": week_label,
        "issue_number": issue,
        "stale_vs_upstream": stale,
        "blocked": blocked,
        "blocker_reason": reason,
    }


# ─── Recovery action recommender ──────────────────────────────────────────


def _recommend_action(abbr: str, slug: str, earliest: str | None,
                      stages: dict[str, dict]) -> str | None:
    """Translate the earliest blocking stage into a concrete recovery action.

    Returns a short imperative string. The string names the GitHub Actions
    workflow file (e.g. agm-interpreter.yml) and any required inputs. The
    caller does NOT dispatch — this is advisory.
    """
    if earliest is None:
        return None

    abbr_lc = abbr.lower()

    if earliest == "interpret":
        wf = f"{abbr_lc}-interpreter.yml"
        return f"dispatch {wf} (interpret-latest missing or invalid)"

    if earliest == "review":
        rs = stages["review"]
        wf = f"{abbr_lc}-reviewer.yml"
        # Stale-vs-upstream takes precedence over verdict: a fresh interpret
        # may resolve a hard-invariant FAIL that lived on the older interpret.
        if rs.get("stale_vs_upstream"):
            v = rs.get("verdict")
            tail = f" (prior verdict was {v!r} — may clear on rerun)" if v in {"hold-for-review", "reject"} else ""
            return f"dispatch {wf} with force=true (review stale vs interpret){tail}"
        if rs.get("verdict") in {"hold-for-review", "reject"}:
            return (
                f"hard-invariant block — fix interpret-side facts then dispatch "
                f"{abbr_lc}-interpreter.yml; reviewer will rerun on its workflow_run trigger"
            )
        if not rs.get("present"):
            return f"dispatch {wf} (review-latest missing)"
        return f"dispatch {wf} (reviewer_error or unknown block)"

    if earliest == "compose":
        cs = stages["compose"]
        wf = f"{abbr_lc}-composer.yml"
        if cs.get("stale_vs_upstream"):
            return f"dispatch {wf} with force=true (compose stale vs review)"
        if not cs.get("present"):
            return f"dispatch {wf} (compose-latest missing)"
        return f"dispatch {wf} (composer_error)"

    if earliest == "apply":
        ap = stages["apply"]
        wf = f"{abbr_lc}-applier.yml"
        reason = ap.get("blocker_reason") or ""
        if ap.get("stale_vs_upstream"):
            return (
                f"dispatch {wf} with force=true, force_reason, force_ad, force_operator "
                f"(applier stale vs upstream: {ap.get('stale_inputs')})"
            )
        if "patch_apply_failed" in reason:
            return (
                f"investigate patches_apply_failed — fix interpret-side claim, then "
                f"dispatch {abbr_lc}-interpreter.yml; downstream chain reruns automatically"
            )
        if "review_verdict:hold-for-review" in reason or "review_verdict:reject" in reason:
            return (
                f"reviewer held — fix interpret-side facts, then dispatch "
                f"{abbr_lc}-interpreter.yml"
            )
        return f"dispatch {wf} with force=true (apply held: {reason})"

    if earliest == "published":
        ps = stages["published"]
        reason = (ps.get("blocker_reason") or "").lower()
        if "publisher pending" in reason:
            return (
                f"dispatch {slug}-publisher.yml — apply is ready, publisher has "
                f"not yet propagated to report-latest"
            )
        if not ps.get("present"):
            if abbr in NON_CANONICAL:
                return f"non-canonical track — no action until {abbr} canonical sprint"
            return f"dispatch {slug}-publisher.yml (report-latest missing)"
        return (
            f"dispatch {slug}-publisher.yml after upstream apply is unblocked "
            f"(published surface stale)"
        )

    return None


# ─── Per-monitor classifier ───────────────────────────────────────────────


def classify_monitor(abbr: str, slug: str, *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    interpret = _probe_interpret(slug)
    review = _probe_review(slug, interpret)
    compose = _probe_compose(slug, review)
    latest_shas = {
        "interpret": interpret.get("sha"),
        "review": review.get("sha"),
        "compose": compose.get("sha"),
    }
    apply_b = _probe_apply(slug, latest_shas)
    published = _probe_published(slug, slug, apply_b)

    stages = {
        "interpret": interpret,
        "review": review,
        "compose": compose,
        "apply": apply_b,
        "published": published,
    }

    # Earliest blocking stage: first stage in order that is blocked OR
    # stale-vs-upstream.
    earliest: str | None = None
    blocker_reason: str | None = None
    for stage in STAGES:
        s = stages[stage]
        if s.get("blocked"):
            earliest = stage
            blocker_reason = s.get("blocker_reason")
            break
        if s.get("stale_vs_upstream"):
            earliest = stage
            blocker_reason = f"{stage} stale vs upstream"
            break
    # Clock-staleness fallback: if nothing else is blocking but the
    # published timestamp is older than STALE_AMBER_DAYS, surface that as
    # an amber blocker on `published`.
    if earliest is None:
        pub_dt = _parse_iso(published.get("timestamp"))
        if pub_dt and now - pub_dt > timedelta(days=STALE_AMBER_DAYS):
            age_days = (now - pub_dt).days
            earliest = "published"
            blocker_reason = f"published surface clock-stale ({age_days}d > {STALE_AMBER_DAYS}d amber threshold)"

    overall = _overall_status(abbr, earliest, stages, now=now)

    return {
        "slug": abbr,
        "monitor_dir": slug,
        "stages": stages,
        "reader_issue_date": published.get("issue_date"),
        "earliest_blocking_stage": earliest,
        "blocker_reason": blocker_reason,
        "recommended_next_action": _recommend_action(abbr, slug, earliest, stages),
        "status": overall,
    }


def _overall_status(abbr: str, earliest: str | None,
                    stages: dict[str, dict], *, now: datetime) -> str:
    """Roll up to green/amber/red.

    green  — no blocker.
    amber  — publisher-pending (apply ready, report-latest not yet refreshed),
             stale-vs-upstream that's recoverable by a same-day rerun, or
             non-canonical-track gaps (FIM).
    red    — hard error: applier patch failure, reviewer hold/reject, or any
             missing canonical-track artefact.
    """
    if earliest is None:
        return "green"
    if abbr in NON_CANONICAL:
        return "amber"
    s = stages[earliest]
    reason = (s.get("blocker_reason") or "").lower()

    # Publisher-pending is amber: apply ran successfully but the publisher
    # workflow has not yet propagated to report-latest. This is a normal
    # interleaving during the publish window, not a hard failure.
    if earliest == "published" and "publisher pending" in reason:
        return "amber"

    # Hard blockers => red.
    hard_signals = (
        "patch_apply_failed",
        "review_verdict:hold-for-review",
        "review_verdict:reject",
        "applier_error",
        "reviewer_error",
        "composer_error",
        "missing",
    )
    if s.get("blocked") and any(sig in reason for sig in hard_signals):
        return "red"
    # Other blocked or stale-vs-upstream => amber.
    return "amber"


# ─── Fleet-level entry points ─────────────────────────────────────────────


def classify_fleet(*, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    monitors = [classify_monitor(abbr, slug, now=now) for abbr, slug in MONITORS]
    counts = {"red": 0, "amber": 0, "green": 0}
    for m in monitors:
        counts[m["status"]] = counts.get(m["status"], 0) + 1
    if counts["red"]:
        engine = "red"
    elif counts["amber"]:
        engine = "amber"
    else:
        engine = "green"
    return {
        "schema_version": "1.0",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": {"status": engine, **counts},
        "monitors": monitors,
    }


def render_markdown(report: dict) -> str:
    lines = []
    lines.append(f"# Fleet stage classifier — {report['generated_at']}\n")
    eng = report["engine"]
    lines.append(
        f"**Engine:** `{eng['status']}`  "
        f"(red={eng['red']}, amber={eng['amber']}, green={eng['green']})\n"
    )
    lines.append("| Monitor | Status | Earliest blocker | Reason | Next action | Reader issue |")
    lines.append("|---|---|---|---|---|---|")
    for m in report["monitors"]:
        blocker = m["earliest_blocking_stage"] or "—"
        reason = (m["blocker_reason"] or "—").replace("|", "\\|")
        action = (m["recommended_next_action"] or "—").replace("|", "\\|")
        lines.append(
            f"| {m['slug']} | {m['status']} | {blocker} | {reason} | {action} | "
            f"{m.get('reader_issue_date') or '—'} |"
        )
    return "\n".join(lines) + "\n"


# ─── CLI ──────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--md", action="store_true",
                   help="emit markdown summary instead of JSON")
    p.add_argument("--out", type=str, default=None,
                   help="write output to this path instead of stdout")
    p.add_argument("--monitor", type=str, default=None,
                   help="restrict to a single monitor abbreviation")
    args = p.parse_args(argv)

    if args.monitor:
        slug = dict(MONITORS).get(args.monitor.upper())
        if not slug:
            print(f"unknown monitor: {args.monitor}", file=sys.stderr)
            return 2
        report = {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "monitors": [classify_monitor(args.monitor.upper(), slug)],
        }
    else:
        report = classify_fleet()

    if args.md:
        out = render_markdown(report)
    else:
        out = json.dumps(report, indent=2, sort_keys=False) + "\n"

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out} ({len(out)} bytes)", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

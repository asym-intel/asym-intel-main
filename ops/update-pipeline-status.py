#!/usr/bin/env python3
"""
Update pipeline-status.json (internal full-fidelity + public simplified) and
internal pipeline-dashboard.html from GitHub Actions API.

Runs as a GitHub Action in asym-intel-main. Reads its own workflow runs,
generates fresh status JSON in two surfaces:

  * INTERNAL  — full-fidelity per-station status for operators / Computer.
                Committed to asym-intel-internal:ops/pipeline-status.json.
  * PUBLIC    — simplified per-monitor green/amber/red roll-up + engine
                roll-up + `_trigger_health` block. Schema v4.0. Written to
                asym-intel-main:static/ops/pipeline-status.json so the
                public dashboard can fetch it at runtime.

Also injects the full-fidelity status into the internal dashboard template
and commits to asym-intel-internal:ops/pipeline-dashboard.html.

Environment variables required:
  GITHUB_TOKEN  — default token (reads own repo's workflow runs)
  GH_TOKEN      — PAT with write access to asym-intel-internal

Sprint AZ BRIEF #1 (AD-2026-04-28-AZ): split internal full-fidelity from
public simplified surface; add derive_public_rollup() helper; rename Phase B
stations from legacy -er suffixes to canon names per PIPELINE-CANONICAL v1.2.

Sprint BH BH.2 (AD-2026-04-30-BJ): wire pipeline-triggers.yml into producer
as the trigger-fire comparator; emit `_trigger_health` block; bump public
schema v3.0 -> v4.0.

Sprint BU BU.4 (AD-2026-05-02-BU): register Advennt as 9th monitor; add
cross-repo workflow-run reads (repo field on MONITORS entry); add producer-poll
failure-alert emission for cross-repo monitors; bump public schema v4.0 -> v4.1.
"""

import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Incident logging — graceful fallback if unavailable
try:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
    from incident_log import log_incident
except Exception:
    def log_incident(**kw): pass

# Trigger-fire comparator (Sprint BH BH.2): read manifest, enumerate expected
# fires, diff against actual GA run history. Helper module is co-located in
# ops/ so it imports as a sibling. Graceful degradation: if PyYAML or the
# helper is unavailable, _trigger_health degrades to manifest_loaded=false
# and consumers can still parse the block.
try:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _pipeline_triggers_loader import (
        load_manifest, iter_expected_fires, manifest_sha,
    )
    _TRIGGER_LOADER_AVAILABLE = True
except ImportError as _exc:
    print(f"  WARNING: _pipeline_triggers_loader unavailable: {_exc}",
          file=sys.stderr)
    _TRIGGER_LOADER_AVAILABLE = False

# ─── Configuration ──────────────────────────────────────────────

MAIN_REPO = "asym-intel/asym-intel-main"
INTERNAL_REPO = "asym-intel/asym-intel-internal"

# Repo-relative path where the public simplified status is written. Hugo serves
# static/ as site root, so this path becomes https://asym-intel.info/ops/pipeline-status.json
# Resolved relative to the script's parent-of-parent (repo root).
PUBLIC_STATUS_PATH = "static/ops/pipeline-status.json"

MONITORS = {
    "WDM": {"accent": "#61a5d2", "day": "Mon", "cron_time": "Mon 06:00 UTC"},
    "GMM": {"accent": "#22a0aa", "day": "Tue", "cron_time": "Tue 08:00 UTC"},
    "ESA": {"accent": "#5b8db0", "day": "Wed", "cron_time": "Wed 19:00 UTC"},
    "FCW": {"accent": "#38bdf8", "day": "Thu", "cron_time": "Thu 09:00 UTC"},
    "AIM": {"accent": "#3a7d5a", "day": "Fri", "cron_time": "Fri 09:00 UTC"},
    "ERM": {"accent": "#4caf7d", "day": "Sat", "cron_time": "Sat 05:00 UTC"},
    "SCEM": {"accent": "#dc2626", "day": "Sun", "cron_time": "Sun 18:00 UTC"},
    "FIM":  {"accent": "#e6a817", "day": "Tue", "cron_time": "Tue 16:00 UTC"},
    # Sprint BU BU.4: Advennt registered as 9th monitor (cross-repo).
    # `repo` field tells the producer which repo to read workflow runs from.
    # `slug` is the Advennt-side workflow filename prefix (differs from commons pattern).
    "ADVENNT": {
        "accent": "#f5a524",
        "day":    "Wed",
        "cron_time": "Wed 09:00 UTC",
        "repo":   "asym-intel/advennt",  # cross-repo read — BU.4
        "slug":   "advennt",
    },
}

# Day-of-week index for schedule matching (Mon=0 .. Sun=6)
DAY_INDEX = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

# Canon station names per PIPELINE-CANONICAL v1.2:
#   Phase A: collector, chatter, weekly-research, reasoner (legacy retained)
#   Phase B: interpret, review, compose, apply, curate
#   Legacy: synthesiser (retained for backwards-read on monitors not yet migrated)
# The workflow YAML filenames on disk still use the historical -er suffixes
# (e.g. agm-interpreter.yml). We map canon → filename here.
PHASE_B_FILE_SUFFIX = {
    "interpret": "interpreter",
    "review":    "reviewer",
    "compose":   "composer",
    "apply":     "applier",
    "curate":    "curator",
}

# Map (monitor_abbr, stage) -> workflow filename in asym-intel-main
WORKFLOW_FILES = {}
# Publisher slug map — workflow filename uses full monitor slug, not abbr
_PUBLISHER_SLUG = {
    "WDM": "democratic-integrity",
    "GMM": "macro-monitor",
    "ESA": "european-strategic-autonomy",
    "FCW": "fimi-cognitive-warfare",
    "AIM": "ai-governance",
    "ERM": "environmental-risks",
    "SCEM": "conflict-escalation",
    "FIM":    "financial-integrity",
    "ADVENNT": "advennt",  # BU.4 — publisher.yml in asym-intel/advennt
}

for abbr, ga_abbr in [("WDM","wdm"), ("GMM","gmm"), ("ESA","esa"), ("FCW","fcw"),
                       ("AIM","agm"), ("ERM","erm"), ("SCEM","scem"), ("FIM","fim")]:
    # Phase A + legacy
    for stage in [
        "collector", "weekly-research", "reasoner",
        "synthesiser",  # legacy — retained for backwards-read on monitors not yet migrated
    ]:
        WORKFLOW_FILES[(abbr, stage)] = f"{ga_abbr}-{stage}.yml"
    # Phase B — canon stage names map to legacy -er filenames on disk
    for canon_stage, file_suffix in PHASE_B_FILE_SUFFIX.items():
        WORKFLOW_FILES[(abbr, canon_stage)] = f"{ga_abbr}-{file_suffix}.yml"
    # Chatter is now unified — one workflow for all monitors (13 Apr 2026)
    WORKFLOW_FILES[(abbr, "chatter")] = "unified-chatter.yml"
    # Publisher: tracked as a GA workflow (fixes published:never lie — BUG-002)
    slug = _PUBLISHER_SLUG.get(abbr, ga_abbr)
    WORKFLOW_FILES[(abbr, "publisher")] = f"{slug}-publisher.yml"

# Sprint BU BU.4: Advennt workflow-file mapping (cross-repo).
# Advennt workflows live in asym-intel/advennt with different filename conventions
# from the commons monitors. Mapped explicitly — do NOT use the commons loop above.
# All Phase A workflows are in the advennt repo:
WORKFLOW_FILES[("ADVENNT", "weekly-research")] = "advennt-weekly-research.yml"
WORKFLOW_FILES[("ADVENNT", "collector")]        = "collector.yml"
WORKFLOW_FILES[("ADVENNT", "chatter")]          = "chatter.yml"
WORKFLOW_FILES[("ADVENNT", "reasoner")]         = "advennt-reasoner.yml"
# Phase B (Advennt uses advennt-* prefix for Phase B workflows):
WORKFLOW_FILES[("ADVENNT", "interpret")]        = "advennt-interpreter.yml"
WORKFLOW_FILES[("ADVENNT", "review")]           = "advennt-reviewer.yml"
WORKFLOW_FILES[("ADVENNT", "compose")]          = "advennt-composer.yml"
WORKFLOW_FILES[("ADVENNT", "apply")]            = "advennt-applier.yml"
WORKFLOW_FILES[("ADVENNT", "curate")]           = "advennt-curator.yml"
# Publisher:
WORKFLOW_FILES[("ADVENNT", "publisher")]        = "publisher.yml"

# Published/dashboard detection: commit message patterns per monitor
PUBLISH_PATTERNS = {
    "WDM": ["data(wdm)", "democratic-integrity", "content(wdm)"],
    "GMM": ["data(gmm)", "macro-monitor", "content(gmm)"],
    "ESA": ["data(esa)", "european-strategic-autonomy", "content(esa)"],
    "FCW": ["data(fcw)", "fimi-cognitive-warfare", "content(fcw)"],
    "AIM": ["data(agm)", "data(aim)", "ai-governance", "content(agm)"],
    "ERM": ["data(erm)", "environmental-risks", "content(erm)"],
    "SCEM": ["data(scem)", "conflict-escalation", "content(scem)"],
    "FIM":     ["data(fim)", "financial-integrity", "content(fim)"],
    "ADVENNT": ["data(advennt)", "advennt", "content(advennt)"],  # BU.4
}

# ─── GitHub API helpers ─────────────────────────────────────────

def gh_api(endpoint, token=None):
    """Call GitHub API via gh CLI."""
    cmd = ["gh", "api", endpoint]
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"  WARNING: gh api {endpoint} failed: {result.stderr[:200]}", file=sys.stderr)
        return None
    return result.stdout


def get_workflow_runs(workflow_file, count=5, repo=None):
    """Get recent runs for a specific workflow file.

    Sprint BU BU.4: added optional `repo` parameter for cross-repo reads.
    When `repo` is supplied (e.g. "asym-intel/advennt"), uses that repo;
    otherwise defaults to MAIN_REPO for backwards compatibility.
    Reads use GH_TOKEN (PAT, org-scoped) so cross-repo reads succeed without
    any workflow permission change.
    """
    target_repo = repo or MAIN_REPO
    raw = gh_api(f"/repos/{target_repo}/actions/workflows/{workflow_file}/runs?per_page={count}")
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data.get("workflow_runs", [])
    except json.JSONDecodeError:
        return []


def get_recent_commits(count=100):
    """Get recent commits from main repo."""
    raw = gh_api(f"/repos/{MAIN_REPO}/commits?per_page={count}")
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


# ─── Status generation ──────────────────────────────────────────

def build_station_status(workflow_file, repo=None):
    """Build status for a single pipeline station from its workflow runs.

    Sprint BU BU.4: added optional `repo` parameter forwarded to
    get_workflow_runs() for cross-repo monitors (e.g. ADVENNT).
    """
    runs = get_workflow_runs(workflow_file, repo=repo)
    if not runs:
        return {"last_run": None, "last_conclusion": "never", "last_success": None}

    latest = runs[0]
    last_success = None
    for r in runs:
        if r.get("conclusion") == "success":
            last_success = r["created_at"]
            break

    return {
        "last_run": latest["created_at"],
        "last_conclusion": latest.get("conclusion") or "running",
        "last_success": last_success,
    }


def find_publish_commit(commits, patterns):
    """Find the most recent publish commit for a monitor.

    DEPRECATED: publisher stages now read from GA workflow runs via
    build_station_status(). This function is retained only for the commit
    message enrichment path (_find_publish_message). Do not use for
    published.last_conclusion — that now comes from GA API.
    """
    return _find_publish_message_as_station(commits, patterns)


def _find_publish_message(commits, patterns):
    """Extract the most recent publisher commit message subject (for display only).

    Returns a trimmed string, or None if not found in the provided commit list.
    Does NOT determine published/never status — GA workflow runs own that.
    """
    for c in commits:
        msg = c.get("commit", {}).get("message", "").lower()
        subject = c.get("commit", {}).get("message", "").split("\n")[0]
        if any(p.lower() in msg for p in patterns):
            is_publish = any(kw in msg for kw in ["issue", "report", "weekly", "publish"])
            is_meta = any(kw in msg for kw in ["seo:", "fix methodology", "nav ", "rename"])
            if is_publish and not is_meta:
                return subject[:80]
    return None


# --- Phase B cascade-file station status (BRIEF-2 v2 §2) ---
#
# Phase B station status is derived from cascade-output artefacts under
# pipeline/monitors/{slug}/{synthesised,applied,curator}/...-latest.json,
# NOT from GitHub Actions workflow runs.
#
# Why: workflow-run lens captures "did the GA job exit 0". Cascade-file
# lens captures "did the artefact land cleanly per its own _meta". These
# differ on the failure class axis A is designed to catch (content-level
# applier divergence, e.g. GMM 2026-04-14 BUG-LOG: applier output diverged
# from published narrative even though every GA workflow exited 0).
#
# Field mapping per stage (verified from live samples 2026-04-28):
#   interpret -> synthesised/interpret-latest.json
#                _meta.synthesised_at, _meta.cycle_disposition (presence => success)
#   review    -> synthesised/review-latest.json
#                _meta.reviewed_at, _meta.reviewer_error (false => success)
#   compose   -> synthesised/compose-latest.json
#                _meta.composed_at, _meta.composer_error (false => success)
#   apply     -> applied/apply-latest.json
#                _meta.applied_at, _meta.applier_error (false => success)
#   curate    -> curator/drift-register-latest.json
#                _meta.computed_at, no explicit error field (presence => success)
#
# Note: BRIEF-2 v2 §2 names the curate file as 'curate-latest.json'; the
# actual on-disk filename is 'drift-register-latest.json'. Documenting the
# deviation in the PR body per BRIEF-2 v2 §0 deviation-declaration policy.

PHASE_B_CASCADE_FILES = {
    "interpret": ("synthesised", "interpret-latest.json"),
    "review":    ("synthesised", "review-latest.json"),
    "compose":   ("synthesised", "compose-latest.json"),
    "apply":     ("applied",     "apply-latest.json"),
    "curate":    ("curator",     "drift-register-latest.json"),
}

PHASE_B_TIMESTAMP_FIELD = {
    "interpret": "synthesised_at",
    "review":    "reviewed_at",
    "compose":   "composed_at",
    "apply":     "applied_at",
    "curate":    "computed_at",
}

# Stage-specific error field. None means 'no explicit error field — file
# presence with a non-null cycle_id/timestamp is the success signal'.
PHASE_B_ERROR_FIELD = {
    "interpret": None,           # success = file present + cycle_disposition set
    "review":    "reviewer_error",
    "compose":   "composer_error",
    "apply":     "applier_error",
    "curate":    None,           # success = file present + computed_at set
}


def _read_cascade_file(monitor_slug, subdir, filename, repo_root=None):
    """Read a cascade-output JSON file from the local checkout.

    Producer runs from `asym-intel-main` GitHub Actions and has filesystem
    access to `pipeline/monitors/{slug}/...` in the same checkout. Returns
    the parsed JSON dict, or None if the file is missing or unreadable.

    repo_root override is for unit tests — defaults to cwd which is the
    repo root inside GA.
    """
    import os
    root = repo_root if repo_root is not None else os.getcwd()
    path = os.path.join(
        root, "pipeline", "monitors", monitor_slug, subdir, filename
    )
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def build_phase_b_station_status(monitor_slug, stage, repo_root=None,
                                  discovery_misses=None):
    """Build station status for a Phase B stage from its cascade-output file.

    Returns dict with last_run / last_conclusion / last_success — same
    shape as build_station_status() so the consumer (operator surface) sees
    a uniform schema across Phase A + Phase B stations.

    Conclusion semantics (Sprint AZ Tier 2 A-1, post-AD-2026-04-29-BC):
      - File missing                                  -> 'never'
      - File present, timestamp field null/missing    -> 'never'
        (the upstream stage didn't actually emit; treating this as 'success'
        was the source of the contradictory `null timestamp + success` state
        that caused all monitors to render red on the compose column)
      - File present, error field True                -> 'failure'
      - File present, error field False/None,
        timestamp present                             -> 'success'

    discovery_misses (optional list): when supplied, each (slug, stage, reason)
    miss is appended for the caller to surface in _meta.station_discovery_misses.
    """
    subdir, filename = PHASE_B_CASCADE_FILES[stage]
    data = _read_cascade_file(monitor_slug, subdir, filename, repo_root=repo_root)

    if data is None:
        if discovery_misses is not None:
            discovery_misses.append({
                "monitor": monitor_slug,
                "stage": stage,
                "file": f"pipeline/monitors/{monitor_slug}/{subdir}/{filename}",
                "reason": "file_missing",
            })
        return {"last_run": None, "last_conclusion": "never", "last_success": None}

    meta = data.get("_meta") or data.get("meta") or {}
    ts_field = PHASE_B_TIMESTAMP_FIELD[stage]
    err_field = PHASE_B_ERROR_FIELD[stage]

    timestamp = meta.get(ts_field)
    if isinstance(timestamp, str) and timestamp.strip().lower() in ("", "null"):
        timestamp = None

    # A-1 fix: a null/missing timestamp means the stage didn't actually run
    # cleanly even if the artefact file landed. Classify as 'never' so the
    # operator surface doesn't show the contradictory `null + success` pair.
    if timestamp is None:
        if discovery_misses is not None:
            discovery_misses.append({
                "monitor": monitor_slug,
                "stage": stage,
                "file": f"pipeline/monitors/{monitor_slug}/{subdir}/{filename}",
                "reason": "timestamp_null",
            })
        return {"last_run": None, "last_conclusion": "never", "last_success": None}

    if err_field is None:
        # No explicit error field for this stage — presence + timestamp = success
        conclusion = "success"
    else:
        err_val = meta.get(err_field)
        if err_val is True:
            conclusion = "failure"
        else:
            # False, None, or missing — treat as success (file landed with timestamp)
            conclusion = "success"

    last_success = timestamp if conclusion == "success" else None

    return {
        "last_run": timestamp,
        "last_conclusion": conclusion,
        "last_success": last_success,
    }


def _find_publish_message_as_station(commits, patterns):
    """Legacy full-station builder — kept for any callers expecting a station dict."""
    for c in commits:
        msg = c.get("commit", {}).get("message", "").lower()
        if any(p.lower() in msg for p in patterns):
            is_publish = any(kw in msg for kw in ["issue", "report", "weekly", "publish", "pipeline"])
            is_meta = any(kw in msg for kw in ["seo:", "fix methodology", "nav ", "rename"])
            if is_publish and not is_meta:
                return {
                    "last_run": c["commit"]["author"]["date"],
                    "last_conclusion": "success",
                    "last_success": c["commit"]["author"]["date"],
                    "message": c["commit"]["message"].split("\n")[0][:60],
                }
    return None


# ─── Verification + incidents (internal-only) ──────────────────
#
# Sprint AZ Tier 2 B-1+B-2 re-instatement.
#
# These were stripped by PR #145 (DR baseliner, public-surface scrub) when the
# epistemic dashboard panels were removed from the public surface. PR-A (Phase
# B station derivation) on the same producer file was supposed to re-add them
# as internal-only equivalents but didn't — leaving the operator surface with
# no source for the verif/incidents panels. Re-adding here, surfaced under
# `_verification` and `_incidents` top-level keys (underscore-prefixed so they
# stay out of derive_public_rollup() which iterates per-monitor entries only).

def extract_verification_data():
    """Extract per-monitor verification summary from report-latest.json.

    Reads each monitor's `static/monitors/<slug>/data/report-latest.json` and
    returns a dict keyed by monitor slug:

        {
          "democratic-integrity": {
            "total": <weekly_brief_sources length>,
            "verified": <count with non-empty url>,
            "failed": 0,
            "date_mismatch": 0,
            "kj_with_sources": <key_judgments count with source_urls>,
            "kj_total": <key_judgments length>,
            "run_date": <first 10 chars of meta.published>,
            "issue": <meta.issue>
          },
          ...
        }

    Internal-only — written under `_verification` in pipeline-status.json so
    the operator surface (ops.asym-intel.info) can render the Verification panel.
    Distinguished by the front-end from `null` (producer not writing block) vs
    empty dict (no monitors with reports yet).
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    slug_map = {
        "WDM": "democratic-integrity", "GMM": "macro-monitor",
        "ESA": "european-strategic-autonomy", "FCW": "fimi-cognitive-warfare",
        "AIM": "ai-governance", "ERM": "environmental-risks",
        "SCEM": "conflict-escalation", "FIM": "financial-integrity",
    }
    verif = {}

    for abbr, slug in slug_map.items():
        report_path = repo_root / f"static/monitors/{slug}/data/report-latest.json"
        if not report_path.exists():
            continue
        try:
            with open(report_path) as f:
                report = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        kjs = report.get("key_judgments", []) or []
        wbs = report.get("weekly_brief_sources", []) or []
        meta = report.get("meta", {}) or {}

        total_sources = len(wbs)
        verified = sum(1 for s in wbs if isinstance(s, dict) and s.get("url"))
        kj_with_sources = sum(
            1 for kj in kjs if isinstance(kj, dict) and kj.get("source_urls"))

        verif[slug] = {
            "total": total_sources,
            "verified": verified,
            "failed": 0,
            "date_mismatch": 0,
            "kj_with_sources": kj_with_sources,
            "kj_total": len(kjs),
            "run_date": meta.get("published", "")[:10] if meta.get("published") else None,
            "issue": meta.get("issue"),
        }

    print(f"  Extracted verification data for {len(verif)} monitor(s)")
    return verif


def extract_incidents():
    """Read pipeline/incidents/incidents.jsonl and return a list of dicts.

    Internal-only — written under `_incidents` in pipeline-status.json. The
    operator surface renders this in the Incidents panel. Returns an empty
    list if the JSONL file is missing or unreadable; returns the parsed list
    (possibly empty) when the file is present but has no entries.

    Note: the front-end distinguishes a missing `_incidents` key (producer
    not writing block — panel renders "data unavailable") from an empty
    array (panel renders "no open incidents"). We always return a list here
    so the key is always present after this producer runs; missing-key state
    only occurs against a stale pre-Tier-2 pipeline-status.json.
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    incidents_path = repo_root / "pipeline" / "incidents" / "incidents.jsonl"

    if not incidents_path.exists():
        print("  No incidents.jsonl found")
        return []

    incidents = []
    try:
        text = incidents_path.read_text()
    except OSError:
        return []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            inc = json.loads(line)
        except json.JSONDecodeError:
            continue
        incidents.append({
            "ts": inc.get("ts", ""),
            "monitor": inc.get("monitor", ""),
            "stage": inc.get("stage", ""),
            "type": inc.get("type", inc.get("incident_type", "")),
            "severity": inc.get("severity", "info"),
            "detail": inc.get("detail", ""),
            "errors": inc.get("errors", []),
            "resolution": inc.get("resolution", ""),
            "resolved": inc.get("resolved", False),
        })

    print(f"  Loaded {len(incidents)} incident(s) from incidents.jsonl")
    return incidents


# ─── Trigger-fire comparator (Sprint BH BH.2) ───────────────────
#
# Reads asym-intel-internal:ops/pipeline-triggers.yml via the helper, enumerates
# every expected fire in a sliding window, queries GA for actual runs of each
# named workflow, and emits the `_trigger_health` block consumed by the ops
# admin pipeline monitor + downstream FE-readiness gate Check F.
#
# Authority: AD-2026-04-30-BH §BH.2 (BH.2 BRIEF). Schema v4.0.

# Match tolerance: actual.started_at must be within
#   [expected_at - TOL_EARLY, expected_at + TOL_LATE_<source_kind>] inclusive
# to count as a hit. "Early" = actual fired BEFORE expected; "late" = actual
# fired AFTER expected. AD-2026-04-30-BJ §fix-forward 2 corrected this window
# orientation: PR #153 had the arithmetic inverted (TOL_LATE was applied to
# the lower bound), so any actual that fired AFTER the expected timestamp by
# more than TOL_EARLY (2min) was marked as missed. That bug was masked by
# CI passing with a synthetic fixture and only surfaced on live producer fires
# where GA scheduled-cron arrival was 30-90min after expected.
#
# Tolerance splits per source_kind:
#   * cf_dispatcher   → +5min: Cloudflare Worker scheduled() dispatch is
#                        observed to fire within <60s of the cron tick. 5min
#                        gives head-room for clock skew + producer queue.
#   * github_native   → +60min: GA scheduled-cron has documented and observed
#                        p95 latency of 30-90 minutes during peak hours.
# TOL_EARLY (pre-expected) is 2min for both source_kinds — early-fire is rare
# and small for both dispatchers.
TRIGGER_TOLERANCE_LATE_CF = timedelta(minutes=5)
TRIGGER_TOLERANCE_LATE_GH_NATIVE = timedelta(minutes=60)
TRIGGER_TOLERANCE_EARLY = timedelta(minutes=2)

# Widest late tolerance — used by the run-fetch window only (we cast a wider
# net than any individual source_kind's tolerance, then narrow per-fire in
# _match_expected_to_actual()).
_TRIGGER_TOLERANCE_LATE_MAX = max(
    TRIGGER_TOLERANCE_LATE_CF, TRIGGER_TOLERANCE_LATE_GH_NATIVE
)


def _tolerance_late_for(source_kind):
    """Return the per-source_kind late-tolerance timedelta. Unknown source_kind
    falls back to the wider value (fail-open: prefer reporting on-time over
    spurious-missed during schema drift)."""
    if source_kind == "cf_dispatcher":
        return TRIGGER_TOLERANCE_LATE_CF
    if source_kind == "github_native":
        return TRIGGER_TOLERANCE_LATE_GH_NATIVE
    return _TRIGGER_TOLERANCE_LATE_MAX

# Internal schema version for the _trigger_health block itself. Independent
# of derive_public_rollup() schema_version (which is the outer surface
# version). This nests inside that surface.
TRIGGER_HEALTH_SCHEMA = "1.0"


def _trigger_window_actual_runs(workflow_file, repo, window_start, window_end,
                                 per_page=50):
    """Fetch recent runs for `workflow_file` in `repo`, filtered to runs whose
    started_at falls in [window_start - TOL_LATE, window_end + TOL_LATE].

    Returns a list of normalised dicts. Reuses gh_api() (auto-paginates a
    single page; per_page=50 is sufficient for any 7-day window since the
    densest workflow fires 3×/day = 21 expected fires).
    """
    endpoint = f"/repos/{repo}/actions/workflows/{workflow_file}/runs?per_page={per_page}"
    raw = gh_api(endpoint)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out = []
    for r in data.get("workflow_runs") or []:
        # Prefer run_started_at (when the runner picked up the job) since
        # that's closer to "fire time" than created_at (queue time). Fall
        # back to created_at if run_started_at is missing.
        started_raw = r.get("run_started_at") or r.get("created_at")
        if not started_raw:
            continue
        try:
            started = datetime.fromisoformat(
                started_raw.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            continue
        if started < window_start - _TRIGGER_TOLERANCE_LATE_MAX:
            # GA returns runs newest-first; once past the window, stop walking.
            break
        if started > window_end + _TRIGGER_TOLERANCE_LATE_MAX:
            continue
        out.append({
            "workflow": workflow_file,
            "repo": repo,
            "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_started_dt": started,  # internal use; stripped before serialising
            "conclusion": r.get("conclusion") or r.get("status") or "unknown",
            "event": r.get("event"),
            "run_number": r.get("run_number"),
            "html_url": r.get("html_url"),
        })
    return out


def _match_expected_to_actual(expected, actual_runs):
    """Return the first actual_run within tolerance of `expected`, or None.

    Tolerance is per-source_kind (cf_dispatcher: +5min, github_native: +60min)
    to reflect observed dispatch-latency profiles. See module-level constants.
    """
    try:
        expected_dt = datetime.fromisoformat(
            expected["expected_at"].replace("Z", "+00:00")
        )
    except (ValueError, TypeError, KeyError):
        return None
    tol_late = _tolerance_late_for(expected.get("source_kind"))
    # Window: [expected - TOL_EARLY, expected + TOL_LATE]. "Late" extends
    # the upper bound (actual fired AFTER expected); "early" the lower.
    lo = expected_dt - TRIGGER_TOLERANCE_EARLY
    hi = expected_dt + tol_late
    for run in actual_runs:
        if lo <= run["_started_dt"] <= hi:
            return run
    return None


def compute_trigger_health(window_days=7, now=None):
    """Compute the `_trigger_health` block by diffing manifest expected fires
    against actual GitHub Actions run history.

    Returns a dict with keys:
      schema_version, window_days, computed_at, tolerance,
      manifest_loaded, manifest_version,
      expected_fires, actual_fires, missed_fires, last_fire_was_on_time.

    On loader unavailability or manifest fetch failure, returns a degraded
    shape with `manifest_loaded: false` and empty arrays so consumers can
    still parse the block (degrade-gracefully principle — same as the
    log_incident fallback at module load).
    """
    now = now or datetime.now(timezone.utc)
    window_end = now
    window_start = now - timedelta(days=window_days)

    base = {
        "schema_version": TRIGGER_HEALTH_SCHEMA,
        "window_days": window_days,
        "computed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tolerance": {
            "late_minutes_cf_dispatcher": int(
                TRIGGER_TOLERANCE_LATE_CF.total_seconds() // 60
            ),
            "late_minutes_github_native": int(
                TRIGGER_TOLERANCE_LATE_GH_NATIVE.total_seconds() // 60
            ),
            "early_minutes": int(TRIGGER_TOLERANCE_EARLY.total_seconds() // 60),
        },
        "manifest_loaded": False,
        "manifest_version": None,
        "manifest_sha": None,
        "expected_fires": [],
        "actual_fires": [],
        "missed_fires": [],
        "last_fire_was_on_time": None,
    }

    if not _TRIGGER_LOADER_AVAILABLE:
        return base

    manifest = load_manifest()
    if not manifest:
        return base

    base["manifest_loaded"] = True
    base["manifest_version"] = manifest.get("manifest_version")
    # Git blob SHA of the manifest at read time. Captured by the loader from
    # the GH contents-API envelope; drives manifest-drift detection on the
    # consumer side (the in-YAML `manifest_version` field is bumped by
    # intent; the blob SHA changes on every byte-level edit). Per BH.2
    # BRIEF: emit `manifest_sha` alongside `manifest_version`.
    base["manifest_sha"] = manifest_sha()

    expected = iter_expected_fires(manifest, window_start, window_end)
    base["expected_fires"] = expected
    if not expected:
        return base

    # Fetch actual runs for every distinct (repo, workflow) in expected.
    by_wf = {}
    for fire in expected:
        key = (fire["repo"], fire["workflow"])
        by_wf.setdefault(key, []).append(fire)

    all_actual = []
    for (repo, wf), _ in by_wf.items():
        all_actual.extend(
            _trigger_window_actual_runs(wf, repo, window_start, window_end)
        )

    # Match each expected to an actual within tolerance.
    missed = []
    for fire in expected:
        actual_for_wf = [
            r for r in all_actual
            if r["repo"] == fire["repo"] and r["workflow"] == fire["workflow"]
        ]
        match = _match_expected_to_actual(fire, actual_for_wf)
        if match is None:
            missed.append({
                "trigger_id": fire["trigger_id"],
                "source_kind": fire["source_kind"],
                "workflow": fire["workflow"],
                "repo": fire["repo"],
                "cron": fire["cron"],
                "expected_at": fire["expected_at"],
                "monitor": fire.get("monitor"),
            })

    base["missed_fires"] = missed

    # Strip internal _started_dt before serialising.
    base["actual_fires"] = [
        {k: v for k, v in r.items() if not k.startswith("_")}
        for r in all_actual
    ]

    # last_fire_was_on_time: most recent expected fire in the past — was it
    # matched? None if no expected fires are yet past `now`.
    past_expected = [
        f for f in expected
        if datetime.fromisoformat(f["expected_at"].replace("Z", "+00:00")) <= now
    ]
    if past_expected:
        most_recent = max(past_expected, key=lambda f: f["expected_at"])
        actual_for_wf = [
            r for r in all_actual
            if r["repo"] == most_recent["repo"]
            and r["workflow"] == most_recent["workflow"]
        ]
        base["last_fire_was_on_time"] = (
            _match_expected_to_actual(most_recent, actual_for_wf) is not None
        )
    else:
        base["last_fire_was_on_time"] = None

    return base


def _list_open_pipeline_failure_issues():
    """Return list of open issues that may be producer-poll failure alerts.

    Returns [] on API failure (degrade gracefully — same as other gh_api callers).

    Historically this filtered server-side by `labels=pipeline-failure`, but
    issues #173/#174 surfaced that the open-path's `gh api --field labels[]=...`
    invocation does not always reliably attach the label (varies with gh CLI
    version; the field is sent as a string rather than a JSON array unless
    `-F`/`--input` is used). Result: label-less issues invisible to the
    auto-close path.

    The body-marker check in _parse_producer_issue_body() is the authoritative
    provenance signal — only issues whose body contains the producer-poll
    marker can ever be auto-closed. So it is safe to drop the server-side
    label filter and let the marker check be the gate; we just have to fetch
    a wider net of open issues. We cap at 100 and walk newest-first which is
    sufficient for the producer-poll volume (≤ a few open at any time).
    """
    raw = gh_api(
        f"/repos/{MAIN_REPO}/issues?state=open&per_page=100"
    )
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    # The /issues endpoint returns PRs too; strip them so callers don't have
    # to. PRs always carry a `pull_request` key.
    return [i for i in data if isinstance(i, dict) and "pull_request" not in i]


# Marker line written into auto-created cross-repo failure issues. Used by
# _resolve_cross_repo_failure_alerts() to scope auto-close to issues this
# function created — never touches manually-filed issues that happen to share
# the `pipeline-failure` label. The phrase appears verbatim in the body
# template emitted by _emit_cross_repo_failure_alerts().
_PRODUCER_POLL_BODY_MARKER = "producer poll (BU.4 cross-repo alert path)"


def _parse_producer_issue_body(body):
    """Extract (monitor_abbr, station) from a producer-poll issue body.

    The body template starts with:
        **Monitor:** ABBR (org/repo)
        **Station:** stationname
        ...
        **Detected by:** producer poll (BU.4 cross-repo alert path)

    Returns (abbr, station) or (None, None) if the body isn't a producer-poll
    body or the fields can't be parsed. Strict parser by design — the auto-close
    path must not act on issues whose provenance it can't confirm.
    """
    if not body or _PRODUCER_POLL_BODY_MARKER not in body:
        return None, None
    abbr = None
    station = None
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("**Monitor:**"):
            # "**Monitor:** ABBR (org/repo)"
            rest = line[len("**Monitor:**"):].strip()
            abbr_token = rest.split()[0] if rest else ""
            if abbr_token:
                abbr = abbr_token
        elif line.startswith("**Station:**"):
            rest = line[len("**Station:**"):].strip()
            if rest:
                station = rest.split()[0]
        if abbr and station:
            break
    return abbr, station


def _emit_cross_repo_failure_alerts(status):
    """Emit GitHub Issue alerts for cross-repo monitor failures.

    Sprint BU BU.4: pipeline-failure-alert.yml uses workflow_run triggers which
    are scoped to the same repo (GitHub Actions constraint). For cross-repo
    monitors (those with a `repo` field in MONITORS), the listener cannot fire.
    This function compensates: runs after the producer has fetched all run data,
    checks for recent failures in cross-repo monitors, and creates GitHub Issues
    in asym-intel-main matching the existing pipeline-failure-alert.yml format.

    Uses GH_TOKEN (PAT, org-scoped) — same credential used for internal-repo writes.
    Deduplicates by issue title (same as the listener workflow).

    This is the canonical approach for cross-repo consumers per
    ops/PIPELINE-OBSERVABILITY-DOCTRINE.md (BU.4).
    """
    now_utc = datetime.now(timezone.utc)
    alert_window_hours = 6  # alert on failures in the last 6h

    # Fetch open alerts once, not per-station, to avoid 9×14 GET amplification.
    existing = _list_open_pipeline_failure_issues()
    existing_titles = {i.get("title") for i in existing if isinstance(i, dict)}

    for abbr, meta in MONITORS.items():
        monitor_repo = meta.get("repo")
        if not monitor_repo:
            continue  # commons monitors covered by pipeline-failure-alert.yml

        # Scan all stations for recent failures
        monitor_status = status.get(abbr, {})
        monitor_stations = monitor_status.get("stations", {}) if isinstance(monitor_status, dict) else {}

        for station, station_data in monitor_stations.items():
            if not isinstance(station_data, dict):
                continue
            if station_data.get("last_conclusion") != "failure":
                continue
            last_run_str = station_data.get("last_run")
            if not last_run_str:
                continue

            # Parse the timestamp
            try:
                last_run_dt = datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            age_hours = (now_utc - last_run_dt).total_seconds() / 3600
            if age_hours > alert_window_hours:
                continue  # outside alert window

            # Find the workflow filename for this station
            wf_file = WORKFLOW_FILES.get((abbr, station), "unknown")
            issue_title = f"🔴 Pipeline failure: {abbr} {station} ({wf_file})"

            if issue_title in existing_titles:
                print(f"  ⚠️  {abbr} {station}: alert already open, skipping", file=sys.stderr)
                continue

            # Create the issue
            issue_body = (
                f"**Monitor:** {abbr} ({monitor_repo})\n"
                f"**Station:** {station}\n"
                f"**Workflow:** {wf_file}\n"
                f"**Last run:** {last_run_str}\n"
                f"**Detected by:** {_PRODUCER_POLL_BODY_MARKER}\n"
                f"\n"
                f"This issue was auto-created by `update-pipeline-status.py` "
                f"(cross-repo failure-alert path, Sprint BU BU.4).\n"
                f"The standard `pipeline-failure-alert.yml` workflow_run trigger "
                f"cannot reach `{monitor_repo}` — this producer-poll path is the "
                f"canonical mechanism for cross-repo monitors.\n"
                f"\nClose when resolved."
            )
            # Build the request body as explicit JSON and pipe via --input.
            # Earlier code used `--field labels[]=pipeline-failure`, which sent
            # `labels` as a string field on some gh versions and produced the
            # label-less issues #173/#174 (visible via `gh issue view --json labels`).
            # The auto-close path then could not find them because it filters
            # open issues by the `pipeline-failure` label. JSON-on-stdin is the
            # gh-documented array form and is version-stable.
            payload = json.dumps({
                "title": issue_title,
                "body": issue_body,
                "labels": ["pipeline-failure"],
            })
            create_raw = subprocess.run(
                [
                    "gh", "api",
                    f"/repos/{MAIN_REPO}/issues",
                    "--method", "POST",
                    "--input", "-",
                ],
                input=payload,
                capture_output=True, text=True,
            )
            if create_raw.returncode == 0:
                print(f"  🔴 {abbr} {station}: created failure alert issue", file=sys.stderr)
                existing_titles.add(issue_title)
            else:
                print(f"  ⚠️  {abbr} {station}: failed to create issue: {create_raw.stderr[:200]}", file=sys.stderr)


def _resolve_cross_repo_failure_alerts(status, *, issues=None, now=None):
    """Auto-close producer-poll failure issues whose station has since recovered.

    Closes the lifecycle gap behind asym-intel-main#173/#174: when a cross-repo
    publisher (e.g. ADVENNT) fails on one run and the producer opens a failure
    issue, then the next publisher run succeeds, the next producer run sees a
    `success` last_conclusion but had no path to clear the existing issue —
    so the red alert persisted forever and required manual close.

    Scope (deliberately narrow to avoid masking active failures or touching
    issues this script didn't create):

      * Issue must have the `pipeline-failure` label (already filtered by caller).
      * Issue body must contain the producer-poll marker line; manually-filed
        issues with the same label are left alone.
      * Body must parse to (monitor_abbr, station) and that monitor must be a
        cross-repo monitor in MONITORS (has a `repo` field).
      * Current `status[abbr]["stations"][station]["last_conclusion"]` must be
        `success` — never close on `running`/`never`/`failure`/missing.
      * Current `last_run` must be ≥ the issue's `created_at`. This guards
        against closing on a stale cached success that predates the failure.

    `issues` and `now` are injected for testability; defaults pull live data.
    Returns the list of closed issue numbers (for logging/test assertions).
    """
    now_utc = now or datetime.now(timezone.utc)
    if issues is None:
        issues = _list_open_pipeline_failure_issues()

    cross_repo_abbrs = {abbr for abbr, m in MONITORS.items() if m.get("repo")}
    closed = []

    for issue in issues:
        if not isinstance(issue, dict):
            continue
        number = issue.get("number")
        if not number:
            continue
        body = issue.get("body") or ""
        abbr, station = _parse_producer_issue_body(body)
        if not abbr or not station:
            continue  # not a producer-poll issue we own
        if abbr not in cross_repo_abbrs:
            continue  # commons monitor — owned by pipeline-failure-alert.yml lifecycle
        station_data = (
            status.get(abbr, {}).get("stations", {}).get(station)
            if isinstance(status.get(abbr), dict) else None
        )
        if not isinstance(station_data, dict):
            continue
        if station_data.get("last_conclusion") != "success":
            continue
        last_run_str = station_data.get("last_run")
        if not last_run_str:
            continue
        try:
            last_run_dt = datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        created_at_str = issue.get("created_at")
        if not created_at_str:
            continue
        try:
            created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if last_run_dt < created_dt:
            # Cached success predates the failure that triggered this issue —
            # not yet evidence of recovery.
            continue

        # Post recovery comment, then close. Comment first so the audit trail
        # survives even if the close call fails.
        comment_body = (
            f"✅ Auto-resolved by `update-pipeline-status.py`: "
            f"{abbr} {station} returned to success at {last_run_str} "
            f"(checked at {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}).\n"
            f"\nClosing as recovered. Re-opens automatically if a future run fails."
        )
        comment_res = subprocess.run(
            [
                "gh", "api",
                f"/repos/{MAIN_REPO}/issues/{number}/comments",
                "--method", "POST",
                "--field", f"body={comment_body}",
            ],
            capture_output=True, text=True,
        )
        if comment_res.returncode != 0:
            print(
                f"  ⚠️  #{number}: recovery comment failed: {comment_res.stderr[:200]}",
                file=sys.stderr,
            )
            # Don't close if we couldn't even comment — fail loud, not silent.
            continue

        close_res = subprocess.run(
            [
                "gh", "api",
                f"/repos/{MAIN_REPO}/issues/{number}",
                "--method", "PATCH",
                "--field", "state=closed",
                "--field", "state_reason=completed",
            ],
            capture_output=True, text=True,
        )
        if close_res.returncode == 0:
            print(f"  ✅ #{number}: auto-closed ({abbr} {station} recovered)", file=sys.stderr)
            closed.append(number)
        else:
            print(
                f"  ⚠️  #{number}: close failed: {close_res.stderr[:200]}",
                file=sys.stderr,
            )

    return closed


def generate_status():
    """Generate full pipeline-status.json from GitHub Actions API."""
    print("Fetching workflow runs for all 9 monitors × 14 stations...")
    commits = get_recent_commits(100)

    # Sprint AZ Tier 2 A-1: collect Phase B station-discovery misses (file
    # missing or timestamp null) for surfacing in _meta.station_discovery_misses.
    discovery_misses = []

    status = {}
    for abbr, meta in MONITORS.items():
        stations = {}

        # Phase A + legacy stages
        # Sprint BU BU.4: pass monitor_repo for cross-repo monitors (e.g. ADVENNT).
        monitor_repo = meta.get("repo")  # None for commons monitors (uses MAIN_REPO default)
        for stage in [
            "collector", "chatter", "weekly-research", "reasoner",
            "synthesiser",
        ]:
            wf_file = WORKFLOW_FILES.get((abbr, stage))
            if wf_file:
                stations[stage] = build_station_status(wf_file, repo=monitor_repo)
                symbol = {"success": "✅", "failure": "❌", "running": "🔄", "never": "⬜"}.get(
                    stations[stage]["last_conclusion"], "❓")
                print(f"  {symbol} {abbr} {stage}: {stations[stage]['last_conclusion']}")
            else:
                stations[stage] = {"last_run": None, "last_conclusion": "never", "last_success": None}

        # Phase B canon stages: interpret, review, compose, apply, curate.
        # Per BRIEF-2 v2 §2, Phase B stations are derived from cascade-output
        # *-latest.json artefacts (content-level signal) for commons monitors.
        # Sprint BU BU.4: for cross-repo monitors (ADVENNT), Phase B cascade
        # files are in the external repo — the producer cannot directly read them
        # via filesystem. For cross-repo monitors, fall back to GA workflow-run
        # signal (same as Phase A). This is a deliberate accuracy/scope trade-off:
        # cascade-file signal for ADVENNT requires a separate checkout step; using
        # GA run signal gives job-level visibility which is sufficient for the
        # observability surface at BU.4. Document in PIPELINE-OBSERVABILITY-DOCTRINE.
        monitor_slug = _PUBLISHER_SLUG.get(abbr, abbr.lower())
        for stage in ["interpret", "review", "compose", "apply", "curate"]:
            if monitor_repo:
                # Cross-repo monitor: use GA workflow-run signal (no filesystem access)
                wf_file = WORKFLOW_FILES.get((abbr, stage))
                if wf_file:
                    stations[stage] = build_station_status(wf_file, repo=monitor_repo)
                    signal_type = "ga-run"
                else:
                    stations[stage] = {"last_run": None, "last_conclusion": "never", "last_success": None}
                    signal_type = "no-wf-mapping"
            else:
                stations[stage] = build_phase_b_station_status(
                    monitor_slug, stage, discovery_misses=discovery_misses)
                signal_type = "cascade"
            symbol = {"success": "✅", "failure": "❌", "running": "🔄", "never": "⬜"}.get(
                stations[stage]["last_conclusion"], "❓")
            print(f"  {symbol} {abbr} {stage}: {stations[stage]['last_conclusion']} ({signal_type})")

        # Published — read from GA workflow runs (same as other stages)
        # BUG-002 fix: publisher workflows are tracked in GA; commit-scan
        # was limited to 100 commits and missed older publishes.
        # Sprint BU BU.4: pass monitor_repo for cross-repo publisher reads.
        pub_wf = WORKFLOW_FILES.get((abbr, "publisher"))
        if pub_wf:
            pub_station = build_station_status(pub_wf, repo=monitor_repo)
            # Enrich with commit message if available (commons monitors only —
            # cross-repo commit scan not implemented at BU.4)
            if not monitor_repo:
                commit_msg = _find_publish_message(commits, PUBLISH_PATTERNS.get(abbr, []))
                if commit_msg:
                    pub_station["message"] = commit_msg
            stations["published"] = pub_station
        else:
            stations["published"] = {"last_run": None, "last_conclusion": "never", "last_success": None}

        # Dashboard mirrors published
        stations["dashboard"] = stations["published"].copy()

        status[abbr] = {
            "accent": meta["accent"],
            "day": meta["day"],
            "cron_time": meta["cron_time"],
            "stations": stations,
        }

    # Sprint BU BU.4: cross-repo failure detection.
    # For cross-repo monitors (e.g. ADVENNT), the pipeline-failure-alert.yml
    # workflow_run trigger cannot listen to their repos (GH Actions constraint).
    # The producer compensates: after fetching all run data, check cross-repo
    # monitors for recent failures and emit a GitHub Issue alert matching the
    # existing pipeline-failure-alert.yml format (labels: pipeline-failure).
    _emit_cross_repo_failure_alerts(status)

    # Lifecycle close for cross-repo alerts: same producer-poll path that opens
    # alerts must also close them when the station has recovered. Without this,
    # a one-shot publisher failure (e.g. ADVENNT 2026-05-02 #173/#174) leaves a
    # red issue open even after subsequent successful runs, requiring manual
    # close. Strict guards in _resolve_cross_repo_failure_alerts ensure we only
    # close issues this script created and only when the current run is success.
    _resolve_cross_repo_failure_alerts(status)

    # Add metadata
    status["_meta"] = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "update-pipeline-status.yml",
        "station_discovery_misses": discovery_misses,
    }

    # Sprint AZ Tier 2 B-1+B-2: re-add verification + incidents as internal-only
    # top-level keys (`_verification`, `_incidents`). These are written into the
    # internal full-fidelity file (asym-intel-internal:ops/pipeline-status.json)
    # only — derive_public_rollup() does NOT propagate underscore-prefixed keys,
    # so the public roll-up at static/ops/pipeline-status.json stays clean per
    # BRIEF #1. The L7 scanner only walks static/, so the methodology vocab in
    # incident detail strings is out-of-scope by construction.
    status["_verification"] = extract_verification_data()
    status["_incidents"] = extract_incidents()

    # Sprint BH BH.2: trigger-fire comparator. Reads asym-intel-internal
    # manifest, diffs expected vs actual GA fires in a 7-day window. Lands
    # as a peer top-level key (not a sub-key of _meta) so consumers can read
    # it without parsing _meta. Degrades gracefully on loader/manifest failure.
    status["_trigger_health"] = compute_trigger_health(window_days=7)

    return status


# ─── Public roll-up derivation (Sprint AZ BRIEF #1) ─────────────

# Stations included in the per-monitor roll-up. All canonical pipeline stages
# plus publisher. We deliberately exclude legacy "synthesiser" and "dashboard"
# (mirror) to avoid double-counting.
ROLLUP_STATIONS = (
    "collector", "chatter", "weekly-research",
    "interpret", "review", "compose", "apply", "curate",
    "published",
)

# Cadence windows (in days) before a successful station is considered stale-amber.
# Mon-Sun publish cadence + a generous grace; FIM Tuesday-only. 9 days covers
# any normal weekly + cron-skip + maintenance window without flapping amber.
STALE_AMBER_DAYS = 9
# Max tolerated lag for a "ran successfully recently" lookback. Beyond this,
# absent any successful run, monitor is red.
STALE_RED_DAYS = 21


def _parse_iso(ts):
    """Parse ISO timestamp ('...Z' or with offset). Return aware datetime or None."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _classify_station(station, now=None):
    """Classify a single station's state for roll-up purposes.

    Returns one of: 'green', 'amber', 'red', 'never', 'running', 'unknown'.

    Rules:
      - last_conclusion == 'failure'                                 -> red
      - last_conclusion == 'never' and last_success is None          -> never
      - last_conclusion == 'running' or 'in_progress' or 'queued'    -> running
                                       (treated as green for roll-up)
      - last_success within STALE_AMBER_DAYS                         -> green
      - last_success within STALE_RED_DAYS but past STALE_AMBER_DAYS -> amber
      - older or missing                                             -> red
    """
    now = now or datetime.now(timezone.utc)
    if not station:
        return "never"
    conc = station.get("last_conclusion")
    if conc == "failure":
        return "red"
    if conc == "never" and not station.get("last_success"):
        return "never"
    if conc in ("running", "in_progress", "queued"):
        return "running"
    last_success_dt = _parse_iso(station.get("last_success"))
    if last_success_dt is None:
        return "red"
    age = now - last_success_dt
    if age <= timedelta(days=STALE_AMBER_DAYS):
        return "green"
    if age <= timedelta(days=STALE_RED_DAYS):
        return "amber"
    return "red"


def _classify_monitor(monitor_status, *, monitor_slug=None, now=None):
    """Classify a monitor's overall roll-up colour.

    green  — every roll-up station is green (or running/never on a non-canonical track).
    amber  — at least one station is past STALE_AMBER_DAYS but none are red,
             OR a station is in 'never' state on a non-canonical monitor (e.g. FIM).
    red    — at least one station is red (failure or beyond STALE_RED_DAYS).
    """
    now = now or datetime.now(timezone.utc)
    stations = (monitor_status or {}).get("stations", {})

    # FIM is on a non-canonical track until financial-integrity ships — its
    # 'never' states should surface as amber, not red.
    is_canonical_track = monitor_slug != "FIM"

    has_red = False
    has_amber = False
    for stage in ROLLUP_STATIONS:
        station = stations.get(stage)
        cls = _classify_station(station, now=now)
        if cls == "red":
            has_red = True
        elif cls == "amber":
            has_amber = True
        elif cls == "never":
            if is_canonical_track:
                # Canonical monitor with a never-run station is a real gap — red.
                has_red = True
            else:
                has_amber = True
        # green / running / unknown contribute nothing
    if has_red:
        return "red"
    if has_amber:
        return "amber"
    return "green"


def _classify_engine(monitor_rollups):
    """Engine-level roll-up: red if any monitor red; amber if any amber; else green."""
    statuses = {m["status"] for m in monitor_rollups}
    if "red" in statuses:
        return "red"
    if "amber" in statuses:
        return "amber"
    return "green"


def _last_updated(monitor_status):
    """Most recent last_run across roll-up stations, or None."""
    stations = (monitor_status or {}).get("stations", {})
    candidates = []
    for stage in ROLLUP_STATIONS:
        st = stations.get(stage) or {}
        if st.get("last_run"):
            candidates.append(st["last_run"])
    if not candidates:
        return None
    return max(candidates)


def derive_public_rollup(internal_status):
    """Map full-fidelity internal status → simplified public schema v4.0.

    Input shape: the dict returned by generate_status() — monitor abbr -> dict
    with `accent`, `day`, `cron_time`, `stations` (all stations); plus `_meta`,
    `_verification`, `_incidents`, and (Sprint BH BH.2) `_trigger_health`.

    Output shape (schema v4.1):
        {
          "schema_version": "4.1",
          "generated_at": "...Z",
          "engine": {"status": "green|amber|red", "last_updated": "...Z"},
          "monitors": [
            {"slug": "WDM", "status": "...", "last_updated": "...Z|null"},
            ...
          ],
          "_trigger_health": {...}  # Sprint BH BH.2 — propagated from internal.
        }

    Schema v3.0 -> v4.0 (Sprint BH BH.2): introduces `_trigger_health`. No
    breaking change to the existing v3.0 keys; v4.0 is a strict superset.
    Consumers reading v3.0 keys continue to work.

    Schema v4.0 -> v4.1 (Sprint BU BU.4): adds ADVENNT as 9th monitor in the
    `monitors[]` list. Additive — consumers reading v4.0 shape continue to work;
    they will see a new entry with slug "ADVENNT". Consumers explicitly checking
    monitor count or hard-coding 8 monitors will need updating.

    The roll-up logic is the ONLY place these rules are encoded. The public
    HTML reads this JSON; it does not re-derive status. `_meta`,
    `_verification`, and `_incidents` remain internal-only by construction
    (they are not added to this returned dict). `_trigger_health` is
    deliberately propagated to the public surface per BH.2 BRIEF Architect
    rec — operator-facing missed-fire visibility belongs on ops.asym-intel.info.
    """
    now = datetime.now(timezone.utc)
    monitor_rollups = []
    for abbr in MONITORS.keys():
        ms = internal_status.get(abbr) or {}
        status = _classify_monitor(ms, monitor_slug=abbr, now=now)
        monitor_rollups.append({
            "slug": abbr,
            "status": status,
            "last_updated": _last_updated(ms),
        })

    engine_status = _classify_engine(monitor_rollups)
    # Engine last_updated is the max of monitor last_updateds (or now if all null)
    monitor_lus = [m["last_updated"] for m in monitor_rollups if m["last_updated"]]
    engine_last_updated = max(monitor_lus) if monitor_lus else now.strftime("%Y-%m-%dT%H:%M:%SZ")

    out = {
        "schema_version": "4.1",  # BU.4: bumped from 4.0 (ADVENNT as 9th monitor)
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": {
            "status": engine_status,
            "last_updated": engine_last_updated,
        },
        "monitors": monitor_rollups,
    }
    # Sprint BH BH.2: propagate trigger-fire comparator block to public.
    # This is the only `_`-prefixed key kept on the public surface — _meta,
    # _verification, _incidents stay internal by construction.
    trigger_health = internal_status.get("_trigger_health")
    if trigger_health is not None:
        out["_trigger_health"] = trigger_health
    return out


# ─── Dashboard generation ───────────────────────────────────────


def generate_dashboard(status):
    """Inject status JSON into INTERNAL dashboard HTML template.

    Output is committed to asym-intel-internal:ops/pipeline-dashboard.html.
    Methodology terms are allowed here (internal surface). The PUBLIC dashboard
    at static/ops/pipeline.html reads the simplified JSON via fetch().
    """
    template_path = Path(__file__).parent / "pipeline-dashboard-template.html"
    if not template_path.exists():
        print(f"  WARNING: Template not found at {template_path}", file=sys.stderr)
        return None

    template = template_path.read_text()

    # Remove _meta before injecting (not needed in frontend)
    frontend_status = {k: v for k, v in status.items() if not k.startswith("_")}
    json_str = json.dumps(frontend_status)


    # Replace placeholders
    html = template.replace("__PIPELINE_DATA__", json_str)

    # Update the "last updated" timestamp if present
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = html.replace("{{UPDATED}}", now_str)

    return html


# ─── Commit to internal repo ───────────────────────────────────

def commit_to_internal(filepath, content, message):
    """Commit a file to asym-intel-internal using GH_TOKEN PAT."""
    import base64

    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        print(f"  WARNING: GH_TOKEN not set, skipping commit of {filepath}", file=sys.stderr)
        return False

    # Get current SHA
    raw = gh_api(f"/repos/{INTERNAL_REPO}/contents/{filepath}", token=gh_token)
    sha = None
    if raw:
        try:
            sha = json.loads(raw).get("sha")
        except json.JSONDecodeError:
            pass

    # Encode content
    encoded = base64.b64encode(content.encode()).decode()

    # Build API call
    data = {"message": message, "content": encoded, "branch": "main"}
    if sha:
        data["sha"] = sha

    cmd = [
        "gh", "api", "--method", "PUT",
        f"/repos/{INTERNAL_REPO}/contents/{filepath}",
        "-f", f"message={message}",
        "-f", f"content={encoded}",
        "-f", "branch=main",
    ]
    if sha:
        cmd.extend(["-f", f"sha={sha}"])

    env = os.environ.copy()
    env["GH_TOKEN"] = gh_token

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"  ERROR committing {filepath}: {result.stderr[:200]}", file=sys.stderr)
        return False

    print(f"  Committed {filepath}")
    return True


# ─── No-show detection ──────────────────────────────────────────

def detect_no_shows(status):
    """Detect monitors whose pipeline stages didn't fire when expected.

    Each monitor has a designated publish day. On that day the collector
    should run by ~07:00 UTC and the cascade should complete within a few
    hours. If this script runs on or after the expected day and the last_run
    for a stage is older than the start of that day, the stage is a no-show.

    FIM is special: runs on Tuesdays but on a later cron (16:00 UTC).
    For FIM we only flag no-show if checking after 18:00 UTC on Tuesday.

    Logs one incident per missing stage via log_incident().
    Returns the number of no-shows found.
    """
    now = datetime.now(timezone.utc)
    today_dow = now.weekday()  # Mon=0 .. Sun=6
    no_show_count = 0

    # Stages that should fire on publish day (in order). Phase B uses canon names.
    expected_stages = [
        "collector", "weekly-research", "reasoner",
        "interpret", "review", "compose", "apply", "curate",
    ]
    # Note: "synthesiser" deliberately excluded from expected stages — legacy.
    # Monitors emit either synthesiser OR the 5-stage cascade; expect the new chain.

    for abbr, meta in MONITORS.items():
        expected_dow = DAY_INDEX.get(meta["day"])
        if expected_dow is None:
            continue

        # Only check on the monitor's publish day (or the day after, to catch
        # late-night runs). We check today and yesterday.
        yesterday_dow = (today_dow - 1) % 7
        if expected_dow not in (today_dow, yesterday_dow):
            continue

        # Determine the start of the expected run day
        if expected_dow == today_dow:
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            day_start = (now - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        # FIM special case: later cron, only flag after 18:00 UTC on Tue
        if abbr == "FIM" and expected_dow == today_dow and now.hour < 18:
            continue

        # Grace period: don't flag until at least 2 hours after the cron_time
        # Parse hour from cron_time string like "Tue 08:00 UTC"
        try:
            cron_hour = int(meta["cron_time"].split()[1].split(":")[0])
        except (IndexError, ValueError):
            cron_hour = 7  # default fallback
        grace_cutoff = day_start.replace(hour=min(cron_hour + 2, 23))
        if expected_dow == today_dow and now < grace_cutoff:
            continue  # Too early to declare a no-show

        stations = status.get(abbr, {}).get("stations", {})

        for stage in expected_stages:
            station = stations.get(stage, {})
            last_run = station.get("last_run")

            if last_run:
                # Parse ISO timestamp and check if it's from the expected day
                try:
                    run_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                    if run_dt >= day_start:
                        continue  # Ran on time — no issue
                except (ValueError, TypeError):
                    pass  # Can't parse — treat as no-show

            # No-show detected
            no_show_count += 1
            slug_map = {
                "WDM": "democratic-integrity", "GMM": "macro-monitor",
                "ESA": "european-strategic-autonomy", "FCW": "fimi-cognitive-warfare",
                "AIM": "ai-governance", "ERM": "environmental-risks",
                "SCEM": "conflict-escalation", "FIM": "financial-integrity",
            }
            log_incident(
                monitor=slug_map.get(abbr, abbr.lower()),
                stage="watchdog",
                incident_type="no_show",
                severity="error",
                detail=(
                    f"{abbr} {stage} did not fire on expected day "
                    f"({meta['day']}). Last run: {last_run or 'never'}"
                ),
                repo_root=pathlib.Path(__file__).resolve().parent.parent,
            )
            print(f"  🚫 NO-SHOW: {abbr} {stage} — expected {meta['cron_time']}, last run: {last_run or 'never'}")

    if no_show_count == 0:
        print("  ✅ No no-shows detected")
    else:
        print(f"  ⚠ {no_show_count} no-show(s) detected and logged")

    return no_show_count


# ─── Main ───────────────────────────────────────────────────────

def main():
    print(f"\n  Pipeline Status Update — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")

    # Generate full-fidelity status (internal)
    status = generate_status()

    # Write internal full-fidelity locally (for CI artifacts and internal commit)
    status_json = json.dumps(status, indent=2)
    Path("pipeline-status.json").write_text(status_json)
    print(f"\n  Generated internal pipeline-status.json ({len(status_json)} bytes)")

    # Derive public roll-up (Sprint AZ BRIEF #1)
    public_rollup = derive_public_rollup(status)
    public_json = json.dumps(public_rollup, indent=2)
    # Resolve repo root (script lives in <repo>/ops/, so parent.parent is repo root)
    repo_root = Path(__file__).resolve().parent.parent
    public_path = repo_root / PUBLIC_STATUS_PATH
    public_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_text(public_json)
    print(f"  Generated public {PUBLIC_STATUS_PATH} ({len(public_json)} bytes, schema v{public_rollup['schema_version']})")
    print(f"    engine={public_rollup['engine']['status']}; "
          f"monitors={[(m['slug'], m['status']) for m in public_rollup['monitors']]}")

    # Generate internal dashboard
    html = generate_dashboard(status)
    if html:
        Path("pipeline-dashboard.html").write_text(html)
        print(f"  Generated internal pipeline-dashboard.html ({len(html)} bytes)")

    # Detect no-shows and log incidents
    detect_no_shows(status)

    # Commit to internal repo
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_to_internal("ops/pipeline-status.json", status_json,
                       f"ops: auto-update pipeline-status.json ({now})")
    if html:
        commit_to_internal("ops/pipeline-dashboard.html", html,
                           f"ops: auto-update pipeline-dashboard.html ({now})")

    # Public file (static/ops/pipeline-status.json) is NOT committed via PAT —
    # it's a local file write in the same repo this script runs in. The GA
    # workflow update-pipeline-status.yml is responsible for committing the
    # workspace change back to asym-intel-main:main on each run.

    print("\n  Done.")


if __name__ == "__main__":
    main()
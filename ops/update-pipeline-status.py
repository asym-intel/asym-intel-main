#!/usr/bin/env python3
"""
Update pipeline-status.json (internal full-fidelity + public simplified) and
internal pipeline-dashboard.html from GitHub Actions API.

Runs as a GitHub Action in asym-intel-main. Reads its own workflow runs,
generates fresh status JSON in two surfaces:

  * INTERNAL  — full-fidelity per-station status for operators / Computer.
                Committed to asym-intel-internal:ops/pipeline-status.json.
  * PUBLIC    — simplified per-monitor green/amber/red roll-up + engine
                roll-up. Schema v3.0. Written to
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
    "FIM": "financial-integrity",
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

# Published/dashboard detection: commit message patterns per monitor
PUBLISH_PATTERNS = {
    "WDM": ["data(wdm)", "democratic-integrity", "content(wdm)"],
    "GMM": ["data(gmm)", "macro-monitor", "content(gmm)"],
    "ESA": ["data(esa)", "european-strategic-autonomy", "content(esa)"],
    "FCW": ["data(fcw)", "fimi-cognitive-warfare", "content(fcw)"],
    "AIM": ["data(agm)", "data(aim)", "ai-governance", "content(agm)"],
    "ERM": ["data(erm)", "environmental-risks", "content(erm)"],
    "SCEM": ["data(scem)", "conflict-escalation", "content(scem)"],
    "FIM":  ["data(fim)", "financial-integrity", "content(fim)"],
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


def get_workflow_runs(workflow_file, count=5):
    """Get recent runs for a specific workflow file."""
    raw = gh_api(f"/repos/{MAIN_REPO}/actions/workflows/{workflow_file}/runs?per_page={count}")
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

def build_station_status(workflow_file):
    """Build status for a single pipeline station from its workflow runs."""
    runs = get_workflow_runs(workflow_file)
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


def generate_status():
    """Generate full pipeline-status.json from GitHub Actions API."""
    print("Fetching workflow runs for all 8 monitors × 14 stations...")
    commits = get_recent_commits(100)

    status = {}
    for abbr, meta in MONITORS.items():
        stations = {}

        # Phase A + legacy stages
        for stage in [
            "collector", "chatter", "weekly-research", "reasoner",
            "synthesiser",
        ]:
            wf_file = WORKFLOW_FILES.get((abbr, stage))
            if wf_file:
                stations[stage] = build_station_status(wf_file)
                symbol = {"success": "✅", "failure": "❌", "running": "🔄", "never": "⬜"}.get(
                    stations[stage]["last_conclusion"], "❓")
                print(f"  {symbol} {abbr} {stage}: {stations[stage]['last_conclusion']}")
            else:
                stations[stage] = {"last_run": None, "last_conclusion": "never", "last_success": None}

        # Phase B canon stages: interpret, review, compose, apply, curate
        for stage in ["interpret", "review", "compose", "apply", "curate"]:
            wf_file = WORKFLOW_FILES.get((abbr, stage))
            if wf_file:
                stations[stage] = build_station_status(wf_file)
                symbol = {"success": "✅", "failure": "❌", "running": "🔄", "never": "⬜"}.get(
                    stations[stage]["last_conclusion"], "❓")
                print(f"  {symbol} {abbr} {stage}: {stations[stage]['last_conclusion']}")
            else:
                stations[stage] = {"last_run": None, "last_conclusion": "never", "last_success": None}

        # Published — read from GA workflow runs (same as other stages)
        # BUG-002 fix: publisher workflows are tracked in GA; commit-scan
        # was limited to 100 commits and missed older publishes.
        pub_wf = WORKFLOW_FILES.get((abbr, "publisher"))
        if pub_wf:
            pub_station = build_station_status(pub_wf)
            # Enrich with commit message if available
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

    # Add metadata
    status["_meta"] = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "update-pipeline-status.yml",
    }

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
    """Map full-fidelity internal status → simplified public schema v3.0.

    Input shape: the dict returned by generate_status() — monitor abbr -> dict
    with `accent`, `day`, `cron_time`, `stations` (all stations); plus `_meta`.

    Output shape (schema v3.0):
        {
          "schema_version": "3.0",
          "generated_at": "...Z",
          "engine": {"status": "green|amber|red", "last_updated": "...Z"},
          "monitors": [
            {"slug": "WDM", "status": "...", "last_updated": "...Z|null"},
            ...
          ]
        }

    The roll-up logic is the ONLY place these rules are encoded. The public
    HTML reads this JSON; it does not re-derive status.
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

    return {
        "schema_version": "3.0",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": {
            "status": engine_status,
            "last_updated": engine_last_updated,
        },
        "monitors": monitor_rollups,
    }


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

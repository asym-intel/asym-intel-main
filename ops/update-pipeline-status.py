#!/usr/bin/env python3
"""
Update pipeline-status.json and pipeline-dashboard.html from GitHub Actions API.

Runs as a GitHub Action in asym-intel-main. Reads its own workflow runs,
generates fresh status JSON, injects it into the dashboard template,
and commits both to asym-intel-internal via the GH_TOKEN PAT.

Environment variables required:
  GITHUB_TOKEN  — default token (reads own repo's workflow runs)
  GH_TOKEN      — PAT with write access to asym-intel-internal
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
    for stage in [
        "collector", "weekly-research", "reasoner",
        "interpreter", "reviewer", "composer", "applier", "curator",
        "synthesiser",  # legacy — retained for backwards-read on monitors not yet migrated off
    ]:
        WORKFLOW_FILES[(abbr, stage)] = f"{ga_abbr}-{stage}.yml"
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
    print("Fetching workflow runs for all 8 monitors × 5 stages...")
    commits = get_recent_commits(100)

    status = {}
    for abbr, meta in MONITORS.items():
        stations = {}

        # GA pipeline stages
        for stage in [
            "collector", "chatter", "weekly-research", "reasoner",
            "interpreter", "reviewer", "composer", "applier", "curator",
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


# ─── Dashboard generation ───────────────────────────────────────

def extract_verification_data():
    """Extract verification summary from each monitor's report-latest.json.

    Reads local repo files (this runs inside a checkout). Returns a dict
    keyed by monitor slug with verification summary for the Epistemic tab.
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

        kjs = report.get("key_judgments", [])
        wbs = report.get("weekly_brief_sources", [])
        meta = report.get("meta", {})

        total_sources = len(wbs)
        verified = sum(1 for s in wbs if isinstance(s, dict) and s.get("url"))
        kj_with_sources = sum(1 for kj in kjs if isinstance(kj, dict) and kj.get("source_urls"))

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
    """Read incidents.jsonl and return as a list of dicts for the dashboard."""
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    incidents_path = repo_root / "pipeline" / "incidents" / "incidents.jsonl"

    if not incidents_path.exists():
        print("  No incidents.jsonl found")
        return []

    incidents = []
    for line in incidents_path.read_text().strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            inc = json.loads(line)
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
        except json.JSONDecodeError:
            continue

    print(f"  Loaded {len(incidents)} incident(s) from incidents.jsonl")
    return incidents


def generate_dashboard(status):
    """Inject status JSON, verification data, and incidents into dashboard HTML template."""
    template_path = Path(__file__).parent / "pipeline-dashboard-template.html"
    if not template_path.exists():
        print(f"  WARNING: Template not found at {template_path}", file=sys.stderr)
        return None

    template = template_path.read_text()

    # Remove _meta before injecting (not needed in frontend)
    frontend_status = {k: v for k, v in status.items() if not k.startswith("_")}
    json_str = json.dumps(frontend_status)

    # Extract epistemic data
    verif_data = extract_verification_data()
    incidents_data = extract_incidents()

    # Replace placeholders
    html = template.replace("__PIPELINE_DATA__", json_str)
    html = html.replace("__VERIF_DATA__", json.dumps(verif_data) if verif_data else "null")
    html = html.replace("__INCIDENTS_DATA__", json.dumps(incidents_data))

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
    should run by ~07:00 UTC and the cascade (research → reasoner →
    synthesiser) should complete within a few hours. If this script runs
    on or after the expected day and the last_run for a stage is older
    than the start of that day, the stage is a no-show.

    FIM is special: runs on Tuesdays but on a later cron (16:00 UTC).
    For FIM we only flag no-show if checking after 18:00 UTC on Tuesday.

    Logs one incident per missing stage via log_incident().
    Returns the number of no-shows found.
    """
    now = datetime.now(timezone.utc)
    today_dow = now.weekday()  # Mon=0 .. Sun=6
    no_show_count = 0

    # Stages that should fire on publish day (in order)
    expected_stages = [
        "collector", "weekly-research", "reasoner",
        "interpreter", "reviewer", "composer", "applier", "curator",
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

    # Generate status
    status = generate_status()

    # Write locally (for CI artifacts)
    status_json = json.dumps(status, indent=2)
    Path("pipeline-status.json").write_text(status_json)
    print(f"\n  Generated pipeline-status.json ({len(status_json)} bytes)")

    # Generate dashboard
    html = generate_dashboard(status)
    if html:
        Path("pipeline-dashboard.html").write_text(html)
        print(f"  Generated pipeline-dashboard.html ({len(html)} bytes)")

    # Detect no-shows and log incidents
    detect_no_shows(status)

    # Commit to internal repo
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_to_internal("ops/pipeline-status.json", status_json,
                       f"ops: auto-update pipeline-status.json ({now})")
    if html:
        commit_to_internal("ops/pipeline-dashboard.html", html,
                           f"ops: auto-update pipeline-dashboard.html ({now})")

    print("\n  Done.")


if __name__ == "__main__":
    main()

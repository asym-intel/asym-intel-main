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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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
}

# Map (monitor_abbr, stage) -> workflow filename in asym-intel-main
WORKFLOW_FILES = {}
for abbr, ga_abbr in [("WDM","wdm"), ("GMM","gmm"), ("ESA","esa"), ("FCW","fcw"),
                       ("AIM","agm"), ("ERM","erm"), ("SCEM","scem")]:
    for stage in ["collector", "weekly-research", "reasoner", "synthesiser"]:
        WORKFLOW_FILES[(abbr, stage)] = f"{ga_abbr}-{stage}.yml"
    # Chatter is now unified — one workflow for all monitors (13 Apr 2026)
    WORKFLOW_FILES[(abbr, "chatter")] = "unified-chatter.yml"

# Published/dashboard detection: commit message patterns per monitor
PUBLISH_PATTERNS = {
    "WDM": ["data(wdm)", "democratic-integrity", "content(wdm)"],
    "GMM": ["data(gmm)", "macro-monitor", "content(gmm)"],
    "ESA": ["data(esa)", "european-strategic-autonomy", "content(esa)"],
    "FCW": ["data(fcw)", "fimi-cognitive-warfare", "content(fcw)"],
    "AIM": ["data(agm)", "data(aim)", "ai-governance", "content(agm)"],
    "ERM": ["data(erm)", "environmental-risks", "content(erm)"],
    "SCEM": ["data(scem)", "conflict-escalation", "content(scem)"],
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
    """Find the most recent publish commit for a monitor."""
    for c in commits:
        msg = c.get("commit", {}).get("message", "").lower()
        # Must be a data/content commit, not just an SEO or metadata fix
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
    print("Fetching workflow runs for all 7 monitors × 5 stages...")
    commits = get_recent_commits(100)

    status = {}
    for abbr, meta in MONITORS.items():
        stations = {}

        # GA pipeline stages
        for stage in ["collector", "chatter", "weekly-research", "reasoner", "synthesiser"]:
            wf_file = WORKFLOW_FILES.get((abbr, stage))
            if wf_file:
                stations[stage] = build_station_status(wf_file)
                symbol = {"success": "✅", "failure": "❌", "running": "🔄", "never": "⬜"}.get(
                    stations[stage]["last_conclusion"], "❓")
                print(f"  {symbol} {abbr} {stage}: {stations[stage]['last_conclusion']}")
            else:
                stations[stage] = {"last_run": None, "last_conclusion": "never", "last_success": None}

        # Published (from commits — Computer crons don't show in GA runs)
        pub = find_publish_commit(commits, PUBLISH_PATTERNS.get(abbr, []))
        stations["published"] = pub or {"last_run": None, "last_conclusion": "never", "last_success": None}

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

def generate_dashboard(status):
    """Inject status JSON into dashboard HTML template."""
    template_path = Path(__file__).parent / "pipeline-dashboard-template.html"
    if not template_path.exists():
        print(f"  WARNING: Template not found at {template_path}", file=sys.stderr)
        return None

    template = template_path.read_text()

    # Remove _meta before injecting (not needed in frontend)
    frontend_status = {k: v for k, v in status.items() if not k.startswith("_")}
    json_str = json.dumps(frontend_status)

    # Replace placeholder
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

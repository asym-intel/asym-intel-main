#!/usr/bin/env python3
"""
FCW Publisher — Mechanical report publisher for the FIMI & Cognitive Warfare Monitor.

Reads synthesiser output + persistent state, assembles the weekly report JSON,
updates persistent state and archive, generates the Hugo brief markdown.

Zero LLM — pure Python transformation. Runs in GitHub Actions.

Inputs:
  pipeline/monitors/fimi-cognitive-warfare/synthesised/synthesis-latest.json
  static/monitors/fimi-cognitive-warfare/data/report-latest.json  (previous)
  static/monitors/fimi-cognitive-warfare/data/persistent-state.json
  static/monitors/fimi-cognitive-warfare/data/archive.json

Outputs:
  static/monitors/fimi-cognitive-warfare/data/report-YYYY-MM-DD.json
  static/monitors/fimi-cognitive-warfare/data/report-latest.json
  static/monitors/fimi-cognitive-warfare/data/persistent-state.json  (updated)
  static/monitors/fimi-cognitive-warfare/data/archive.json  (appended)
  content/monitors/fimi-cognitive-warfare/YYYY-MM-DD-weekly-brief.md
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "."))

SYNTHESIS_PATH = REPO_ROOT / "pipeline/monitors/fimi-cognitive-warfare/synthesised/synthesis-latest.json"
PREV_REPORT_PATH = REPO_ROOT / "static/monitors/fimi-cognitive-warfare/data/report-latest.json"
PERSISTENT_PATH = REPO_ROOT / "static/monitors/fimi-cognitive-warfare/data/persistent-state.json"
ARCHIVE_PATH = REPO_ROOT / "static/monitors/fimi-cognitive-warfare/data/archive.json"

DATA_DIR = REPO_ROOT / "static/monitors/fimi-cognitive-warfare/data"
DOCS_DATA_DIR = REPO_ROOT / "docs/monitors/fimi-cognitive-warfare/data"
BRIEF_DIR = REPO_ROOT / "content/monitors/fimi-cognitive-warfare"

MONITOR_SLUG = "fimi-cognitive-warfare"
MONITOR_TITLE = "FIMI & Cognitive Warfare Monitor"
PUBLISH_TIME = "T09:00:00Z"
SITE_URL = "https://asym-intel.info"

# Adjacent monitors for cross-monitor flag verification
ADJACENT_MONITORS = [
    "democratic-integrity",
    "conflict-escalation",
    "european-strategic-autonomy",
    "macro-monitor",
    "ai-governance",
    "environmental-risks",
]


# ── Helpers ────────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict | list:
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, data, indent=2):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    print(f"  ✓ wrote {path}")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print(f"  ✓ wrote {path}")


# ── Staleness check ───────────────────────────────────────────────────────

def check_synthesis_freshness(synthesis: dict, max_age_days: int = 8) -> bool:
    """Return True if synthesis is fresh enough to publish."""
    generated_at = synthesis.get("_meta", {}).get("generated_at", "")
    if not generated_at:
        return False
    gen_dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    age = datetime.now(timezone.utc) - gen_dt
    if age.days > max_age_days:
        print(f"  ⚠ synthesis is {age.days} days old (max {max_age_days}) — STALE, skipping publish")
        return False
    return True


# ── Build report ──────────────────────────────────────────────────────────

def build_meta(prev_report: dict, synthesis: dict, publish_date: str) -> dict:
    """Build the meta block, incrementing issue number."""
    prev_meta = prev_report.get("meta", {})
    prev_issue = prev_meta.get("issue", 0)
    week_ending = synthesis.get("_meta", {}).get("week_ending", publish_date)

    return {
        "issue": prev_issue + 1,
        "volume": prev_meta.get("volume", 1),
        "week_label": f"W/E {datetime.strptime(week_ending, '%Y-%m-%d').strftime('%-d %B %Y')}",
        "published": f"{publish_date}{PUBLISH_TIME}",
        "slug": publish_date,
        "publish_time_utc": PUBLISH_TIME,
        "editor": "fcw-publisher-bot",
        "schema_version": "2.0",
    }


def build_signal(synthesis: dict) -> dict:
    """Map synthesis lead_signal → report signal."""
    ls = synthesis.get("lead_signal", {})
    return {
        "headline": ls.get("headline", ""),
        "actor": ls.get("actor", "N/A"),
        "confidence": ls.get("confidence", "N/A"),
        "f_flags": ls.get("mf_flags", []),
        "note": ls.get("note", ""),
    }


def build_campaigns(persistent: dict, synthesis: dict) -> list:
    """
    Build campaign list from persistent state, applying delta_strip changes.
    Campaigns come from persistent-state.json, NOT from synthesis.campaigns
    (which may be empty on quiet weeks).
    """
    # Flatten all active campaigns from persistent state
    active = persistent.get("active_campaigns", {})
    campaigns = []
    for actor_key, actor_campaigns in active.items():
        if isinstance(actor_campaigns, list):
            campaigns.extend(actor_campaigns)
        elif isinstance(actor_campaigns, dict):
            # Some actors may have a single campaign as dict
            campaigns.append(actor_campaigns)

    # Apply delta_strip changes
    delta = synthesis.get("delta_strip", {})

    # Add new campaigns
    for new_camp in delta.get("new_campaigns", []):
        campaigns.append(new_camp)

    # Apply status changes
    for change in delta.get("status_changes", []):
        cid = change.get("campaign_id", "")
        for camp in campaigns:
            if camp.get("id") == cid or camp.get("campaign_id") == cid:
                if "new_status" in change:
                    camp["status"] = change["new_status"]
                if "new_trajectory" in change:
                    camp["trajectory"] = change["new_trajectory"]
                break

    return campaigns


def build_actor_tracker(synthesis: dict, prev_report: dict) -> list:
    """
    Use synthesis actor_tracker if available.
    Map field names to report schema.
    """
    synth_actors = synthesis.get("actor_tracker", [])
    if synth_actors:
        result = []
        for a in synth_actors:
            result.append({
                "actor": a.get("actor", ""),
                "status": a.get("status", a.get("posture", "")),
                "doctrine": a.get("doctrine_note", a.get("doctrine", "")),
                "source_url": a.get("source_url", ""),
                "headline": a.get("headline", a.get("summary", "")[:120]),
            })
        return result
    # Fallback: carry forward from previous report
    return prev_report.get("actor_tracker", [])


def build_platform_responses(persistent: dict, prev_report: dict) -> list:
    """Platform responses from persistent state tracker."""
    tracker = persistent.get("platform_enforcement_tracker", [])
    if tracker:
        return tracker
    return prev_report.get("platform_responses", [])


def build_attribution_log(synthesis: dict, prev_report: dict) -> list:
    """Merge synthesis attribution log with previous."""
    synth_log = synthesis.get("attribution_log", [])
    prev_log = prev_report.get("attribution_log", [])

    if synth_log:
        # Merge: add any new entries not already in prev
        existing_ids = {e.get("id") for e in prev_log}
        merged = list(prev_log)
        for entry in synth_log:
            if entry.get("id") not in existing_ids:
                merged.append(entry)
        return merged
    return prev_log


def build_cognitive_warfare(synthesis: dict, prev_report: dict) -> list:
    """
    Cognitive warfare section: carry forward existing entries +
    promote any new structural key_judgments from synthesis.

    A key_judgment becomes a CW entry if it:
    - Has confidence Confirmed or High
    - Contains structural/doctrinal significance (not routine status)
    - Isn't already covered by an existing CW entry
    """
    existing = list(prev_report.get("cognitive_warfare", []))
    existing_headlines = {e.get("headline", "").lower() for e in existing}

    # Check intelligence_highlights first (synthesiser's curated highlights)
    highlights = synthesis.get("intelligence_highlights", [])
    for hl in highlights:
        headline = hl.get("headline", hl.get("title", ""))
        if headline.lower() not in existing_headlines:
            next_id = f"CW-{len(existing) + 1:03d}"
            existing.append({
                "id": next_id,
                "classification": "COGNITIVE WARFARE",
                "headline": headline,
                "detail": hl.get("detail", hl.get("summary", "")),
                "significance": hl.get("significance", ""),
                "source_url": hl.get("source_url", ""),
            })
            print(f"    + new CW entry: {next_id} — {headline[:60]}")

    # Also check key_judgments for structural findings
    for kj in synthesis.get("key_judgments", []):
        # Only promote Confirmed/High confidence structural judgments
        if kj.get("confidence") not in ("Confirmed", "High"):
            continue
        text = kj.get("text", "")
        # Skip routine "no signal" judgments
        if any(skip in text.lower() for skip in ["no new", "no signal", "unchanged", "no operations"]):
            continue
        if text[:50].lower() not in existing_headlines:
            next_id = f"CW-{len(existing) + 1:03d}"
            existing.append({
                "id": next_id,
                "classification": "COGNITIVE WARFARE",
                "headline": text[:120],
                "detail": text,
                "significance": kj.get("basis", ""),
                "source_url": "",
            })
            print(f"    + new CW entry from key judgment: {next_id}")

    return existing


def load_adjacent_reports() -> dict:
    """
    Load report-latest.json from all adjacent monitors.
    Returns {slug: report_dict} for monitors that have data.
    """
    reports = {}
    for slug in ADJACENT_MONITORS:
        path = REPO_ROOT / f"static/monitors/{slug}/data/report-latest.json"
        if path.exists():
            try:
                reports[slug] = load_json(path)
                print(f"    loaded {slug} (Issue {reports[slug].get('meta', {}).get('issue', '?')})")
            except (json.JSONDecodeError, KeyError):
                print(f"    ⚠ {slug}: failed to parse")
        else:
            print(f"    ⚠ {slug}: no report-latest.json")
    return reports


def verify_flag_against_adjacent(flag: dict, adjacent_reports: dict) -> str:
    """
    Check if a cross-monitor flag's referenced monitor has a current report.
    Each monitor has different schema — we verify the report exists and is
    recent, not that specific fields match (that would require per-monitor logic).
    Returns updated status string.
    """
    slug = flag.get("monitor_slug", "")
    if slug not in adjacent_reports:
        return flag.get("status", "Active")  # can't verify, keep current

    adj = adjacent_reports[slug]
    adj_meta = adj.get("meta", {})

    # If adjacent report has a meta block with an issue number, it's live
    if adj_meta.get("issue"):
        current_status = flag.get("status", "Active")
        # Strip any previous verification notes, keep the core status
        if "—" in current_status:
            core = current_status.split("—")[0].strip()
        else:
            core = current_status
        return f"{core} — verified (adjacent Issue {adj_meta['issue']})"

    return flag.get("status", "Active")


def build_cross_monitor_flags(synthesis: dict, prev_report: dict, publish_date: str) -> dict:
    """
    Verify existing flags against adjacent monitor data.
    Promote synthesis cross_monitor_candidates to new flags.
    Track version history.
    """
    prev_cmf = prev_report.get("cross_monitor_flags", {})
    prev_flags = list(prev_cmf.get("flags", []))
    prev_history = list(prev_cmf.get("version_history", []))
    candidates = synthesis.get("cross_monitor_candidates", {})

    print("  Verifying cross-monitor flags against adjacent reports...")
    adjacent = load_adjacent_reports()

    changes_this_issue = []

    # Verify existing flags
    for flag in prev_flags:
        old_status = flag.get("status", "")
        new_status = verify_flag_against_adjacent(flag, adjacent)
        if new_status != old_status:
            flag["status"] = new_status
            changes_this_issue.append(f"{flag.get('id')}: {old_status} → {new_status}")
        flag["updated"] = publish_date

    # Promote new candidates from synthesis
    existing_slugs = {f.get("monitor_slug") for f in prev_flags}
    for slug_key, candidate in candidates.items():
        if candidate is None:
            continue
        # candidate can be a dict with flag data or a string note
        if isinstance(candidate, dict):
            monitor_slug = candidate.get("monitor_slug", slug_key)
            if monitor_slug not in existing_slugs:
                next_id = f"CMF-{len(prev_flags) + 1:03d}"
                new_flag = {
                    "id": next_id,
                    "monitor": candidate.get("monitor", monitor_slug),
                    "monitor_slug": monitor_slug,
                    "headline": candidate.get("headline", ""),
                    "linkage": candidate.get("linkage", ""),
                    "classification": candidate.get("classification", "Structural"),
                    "status": "Active — NEW",
                    "first_flagged": publish_date,
                    "updated": publish_date,
                    "source_url": candidate.get("source_url", ""),
                }
                prev_flags.append(new_flag)
                changes_this_issue.append(f"{next_id}: NEW — {new_flag['headline'][:60]}")
                print(f"    + new flag: {next_id} — {new_flag['headline'][:60]}")

    # Build version history entry
    if changes_this_issue:
        prev_history.append({
            "date": publish_date,
            "change": "; ".join(changes_this_issue),
            "reason": "Publisher auto-verification against adjacent monitor data",
        })
    else:
        prev_history.append({
            "date": publish_date,
            "change": "No changes — all flags verified against adjacent monitor data",
            "reason": "Routine verification",
        })

    return {
        "updated": f"{publish_date}{PUBLISH_TIME}",
        "flags": prev_flags,
        "version_history": prev_history,
    }


def build_last_run_status(synthesis: dict, success: bool = True, issues: list = None) -> dict:
    """Build _meta.last_run_status for next run's one-step memory."""
    inputs = synthesis.get("_meta", {}).get("inputs_used", {})
    return {
        "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "success": success,
        "publisher": "fcw-publisher-bot",
        "pipeline_inputs": {
            "daily_latest": bool(inputs.get("daily_latest")),
            "weekly_latest": bool(inputs.get("weekly_latest")),
            "reasoner_latest": bool(inputs.get("reasoner_latest")),
            "synthesis_latest": True,
        },
        "synthesis_status": synthesis.get("_meta", {}).get("status", "unknown"),
        "issues": issues or [],
        "deferred": [],
    }


# ── Delta strip for archive ──────────────────────────────────────────────

def build_archive_delta_strip(synthesis: dict) -> list:
    """Build a concise delta strip for the archive entry."""
    delta = synthesis.get("delta_strip", {})
    strips = []
    rank = 1

    for camp in delta.get("new_campaigns", []):
        strips.append({
            "rank": rank,
            "title": camp.get("operation_name", camp.get("summary", "New campaign")[:80]),
            "module_tag": camp.get("actor", "UNKNOWN"),
            "delta_type": "New Campaign",
            "one_line": camp.get("summary", "")[:200],
        })
        rank += 1

    for change in delta.get("status_changes", []):
        strips.append({
            "rank": rank,
            "title": f"{change.get('campaign_id', '')} status change",
            "module_tag": change.get("actor", ""),
            "delta_type": "Status Change",
            "one_line": f"{change.get('old_status', '')} → {change.get('new_status', '')}",
        })
        rank += 1

    for action in delta.get("platform_actions", []):
        strips.append({
            "rank": rank,
            "title": action.get("headline", action.get("summary", "Platform action")[:80]),
            "module_tag": action.get("platform", ""),
            "delta_type": "Platform Action",
            "one_line": action.get("summary", "")[:200],
        })
        rank += 1

    # If quiet week with no deltas, add a quiet-week note
    if not strips:
        strips.append({
            "rank": 1,
            "title": "No material FIMI developments",
            "module_tag": "ALL",
            "delta_type": "Quiet Week",
            "one_line": synthesis.get("lead_signal", {}).get("headline", "No signal this week."),
        })

    return strips


# ── Hugo brief ────────────────────────────────────────────────────────────

def build_hugo_brief(meta: dict, synthesis: dict, publish_date: str) -> str:
    """Generate Hugo markdown brief from synthesis weekly_brief_draft."""
    brief_body = synthesis.get("weekly_brief_draft", "No brief available.")
    signal_headline = synthesis.get("lead_signal", {}).get("headline", "")

    frontmatter = f"""---
title: "{MONITOR_TITLE} — {meta['week_label']}"
date: {meta['published']}
summary: "{signal_headline[:200]}"
draft: false
monitor: "{MONITOR_SLUG}"
---"""

    dashboard_link = f"[live dashboard]({SITE_URL}/monitors/{MONITOR_SLUG}/dashboard.html)"
    data_link = f"[JSON data feed]({SITE_URL}/monitors/{MONITOR_SLUG}/data/report-latest.json)"

    body = f"""{frontmatter}

{brief_body}

---

The {dashboard_link} and {data_link} have been updated to Issue {meta['issue']} ({meta['week_label']}).

*Published by FCW Publisher Bot.*
"""
    return body


# ── Persistent state update ──────────────────────────────────────────────

def update_persistent_state(persistent: dict, synthesis: dict, meta: dict) -> dict:
    """Apply delta_strip to persistent state and update metadata."""
    persistent["_meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    persistent["_meta"]["last_issue"] = meta["issue"]

    delta = synthesis.get("delta_strip", {})

    # Add new campaigns to the appropriate actor bucket
    for new_camp in delta.get("new_campaigns", []):
        actor = new_camp.get("actor", "UNATTRIBUTED").upper()
        if actor not in persistent.get("active_campaigns", {}):
            persistent["active_campaigns"][actor] = []
        bucket = persistent["active_campaigns"][actor]
        if isinstance(bucket, list):
            bucket.append(new_camp)

    # Apply status changes
    for change in delta.get("status_changes", []):
        cid = change.get("campaign_id", "")
        for actor_key, camps in persistent.get("active_campaigns", {}).items():
            if isinstance(camps, list):
                for camp in camps:
                    if camp.get("id") == cid or camp.get("campaign_id") == cid:
                        if "new_status" in change:
                            camp["status"] = change["new_status"]

    return persistent


# ── Schema validation ────────────────────────────────────────────────────

def validate_report(report: dict) -> list[str]:
    """Validate the assembled report. Returns list of errors (empty = valid)."""
    errors = []

    required_keys = ["meta", "signal", "campaigns", "actor_tracker",
                     "platform_responses", "attribution_log",
                     "cross_monitor_flags", "source_url"]

    for key in required_keys:
        if key not in report:
            errors.append(f"Missing top-level key: {key}")

    meta = report.get("meta", {})
    if not meta.get("issue"):
        errors.append("meta.issue is missing or zero")
    if not meta.get("week_label"):
        errors.append("meta.week_label is empty")
    if meta.get("schema_version") != "2.0":
        errors.append(f"schema_version is '{meta.get('schema_version')}', expected '2.0'")

    signal = report.get("signal", {})
    if not signal.get("headline"):
        errors.append("signal.headline is empty")

    if not report.get("actor_tracker"):
        errors.append("actor_tracker is empty")

    return errors


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("FCW Publisher — Mechanical Report Publisher")
    print("=" * 50)

    # Load inputs
    print("\n[1/6] Loading inputs...")
    if not SYNTHESIS_PATH.exists():
        print(f"  ✗ synthesis-latest.json not found at {SYNTHESIS_PATH}")
        sys.exit(1)

    synthesis = load_json(SYNTHESIS_PATH)
    prev_report = load_json(PREV_REPORT_PATH) if PREV_REPORT_PATH.exists() else {}
    persistent = load_json(PERSISTENT_PATH) if PERSISTENT_PATH.exists() else {}
    archive = load_json(ARCHIVE_PATH) if ARCHIVE_PATH.exists() else []

    print(f"  synthesis: {synthesis.get('_meta', {}).get('status', 'unknown')} "
          f"(week ending {synthesis.get('_meta', {}).get('week_ending', '?')})")
    print(f"  previous report: Issue {prev_report.get('meta', {}).get('issue', '?')}")

    # Freshness check
    print("\n[2/6] Checking synthesis freshness...")
    if not check_synthesis_freshness(synthesis):
        print("  ✗ ABORTING — synthesis too stale to publish")
        sys.exit(1)
    print("  ✓ synthesis is fresh")

    # Determine publish date
    publish_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build report
    print("\n[3/6] Assembling report...")
    meta = build_meta(prev_report, synthesis, publish_date)
    print(f"  Issue {meta['issue']}, {meta['week_label']}")

    report = {
        "meta": meta,
        "signal": build_signal(synthesis),
        "campaigns": build_campaigns(persistent, synthesis),
        "actor_tracker": build_actor_tracker(synthesis, prev_report),
        "platform_responses": build_platform_responses(persistent, prev_report),
        "attribution_log": build_attribution_log(synthesis, prev_report),
        "cognitive_warfare": build_cognitive_warfare(synthesis, prev_report),
        "cross_monitor_flags": build_cross_monitor_flags(synthesis, prev_report, publish_date),
        "source_url": f"{SITE_URL}/monitors/{MONITOR_SLUG}/{publish_date}-weekly-brief/",
        "_meta": {
            "last_run_status": build_last_run_status(synthesis),
        },
    }

    # Validate
    print("\n[4/6] Validating schema...")
    errors = validate_report(report)
    if errors:
        print("  ⚠ Validation warnings:")
        for e in errors:
            print(f"    - {e}")
        # Don't abort on warnings — log them in last_run_status
        report["_meta"]["last_run_status"]["issues"] = errors
    else:
        print("  ✓ schema valid")

    # Update persistent state
    print("\n[5/6] Updating persistent state + archive...")
    persistent = update_persistent_state(persistent, synthesis, meta)

    archive_entry = {
        "issue": meta["issue"],
        "volume": meta["volume"],
        "week_label": meta["week_label"],
        "published": publish_date,
        "slug": publish_date,
        "signal": report["signal"]["headline"],
        "source_url": report["source_url"],
        "delta_strip": build_archive_delta_strip(synthesis),
    }
    archive.append(archive_entry)

    # Generate Hugo brief
    hugo_brief = build_hugo_brief(meta, synthesis, publish_date)

    # Write outputs
    print("\n[6/6] Writing outputs...")
    dated_report_path = DATA_DIR / f"report-{publish_date}.json"
    write_json(dated_report_path, report)
    write_json(DATA_DIR / "report-latest.json", report)
    write_json(PERSISTENT_PATH, persistent)
    write_json(ARCHIVE_PATH, archive)
    write_text(BRIEF_DIR / f"{publish_date}-weekly-brief.md", hugo_brief)

    # Mirror to docs/
    write_json(DOCS_DATA_DIR / f"report-{publish_date}.json", report)
    write_json(DOCS_DATA_DIR / "report-latest.json", report)

    print(f"\n{'=' * 50}")
    print(f"FCW Issue {meta['issue']} ({meta['week_label']}) published.")
    print(f"  Report: {dated_report_path}")
    print(f"  Brief:  {BRIEF_DIR / f'{publish_date}-weekly-brief.md'}")
    if errors:
        print(f"  ⚠ {len(errors)} validation warning(s) — check _meta.last_run_status")


if __name__ == "__main__":
    main()

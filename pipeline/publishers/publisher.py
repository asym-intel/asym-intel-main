#!/usr/bin/env python3
"""
Generic Monitor Publisher — Mechanical report publisher for any Asymmetric Intelligence monitor.

Config-driven: reads a per-monitor JSON config that specifies slug, paths, field mappings,
and publish schedule. The core logic is identical across all 7 monitors.

Usage:
  REPO_ROOT=. MONITOR_SLUG=fimi-cognitive-warfare python3 publisher.py
  REPO_ROOT=. MONITOR_SLUG=macro-monitor python3 publisher.py

Inputs (per monitor):
  pipeline/monitors/{slug}/synthesised/synthesis-latest.json
  static/monitors/{slug}/data/report-latest.json  (previous)
  static/monitors/{slug}/data/persistent-state.json
  static/monitors/{slug}/data/archive.json

Outputs:
  static/monitors/{slug}/data/report-YYYY-MM-DD.json
  static/monitors/{slug}/data/report-latest.json
  static/monitors/{slug}/data/persistent-state.json  (updated)
  static/monitors/{slug}/data/archive.json  (appended)
  content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md
  docs/monitors/{slug}/data/ mirrors
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "."))
MONITOR_SLUG = os.environ.get("MONITOR_SLUG", "")
SITE_URL = "https://asym-intel.info"

# All monitors except the current one, for cross-monitor verification
ALL_MONITORS = [
    "democratic-integrity",
    "macro-monitor",
    "european-strategic-autonomy",
    "fimi-cognitive-warfare",
    "ai-governance",
    "environmental-risks",
    "conflict-escalation",
]

MONITOR_CONFIGS = {
    "fimi-cognitive-warfare": {
        "title": "FIMI & Cognitive Warfare Monitor",
        "abbr": "FCW",
        "publish_time": "T09:00:00Z",
        "signal_key": "lead_signal",       # synthesis field for headline signal
        "has_campaigns": True,             # uses persistent-state campaign registry
        "has_actor_tracker": True,
        "has_cognitive_warfare": True,
        "has_platform_responses": True,
        # synthesis field → report field mappings (beyond standard ones)
        "field_map": {
            "lead_signal": "signal",
        },
    },
    "democratic-integrity": {
        "title": "World Democracy Monitor",
        "abbr": "WDM",
        "publish_time": "T06:00:00Z",
        "signal_key": None,                # signal comes from report, not synthesis
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {
            "country_heatmap": "heatmap",
            "backsliding_alerts": "intelligence_items",
        },
    },
    "macro-monitor": {
        "title": "Global Macro Monitor",
        "abbr": "GMM",
        "publish_time": "T08:00:00Z",
        "signal_key": None,
        "signal_builder": "gmm",
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {
            "stress_regime_preliminary": "stress_regime",
        },
    },
    "european-strategic-autonomy": {
        "title": "European Strategic Autonomy Monitor",
        "abbr": "ESA",
        "publish_time": "T19:00:00Z",
        "signal_key": None,
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {},
    },
    "ai-governance": {
        "title": "Artificial Intelligence Monitor",
        "abbr": "AIM",
        "publish_time": "T09:00:00Z",
        "signal_key": None,
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {
            "governance_snapshot": "module_0",
            "capability_tier_tracker": "module_1",
            "regulatory_framework_tracker": "module_2",
            "ai_fimi_layer": "module_3",
        },
    },
    "environmental-risks": {
        "title": "Global Environmental Risks Monitor",
        "abbr": "ERM",
        "publish_time": "T05:00:00Z",
        "signal_key": None,
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {
            "planetary_status_snapshot": "m00_the_signal",
            "planetary_boundary_tracker": "m02_planetary_boundaries",
            "climate_security_nexus": "m03_threat_multiplier",
        },
    },
    "conflict-escalation": {
        "title": "Strategic Conflict & Escalation Monitor",
        "abbr": "SCEM",
        "publish_time": "T18:00:00Z",
        "signal_key": "lead_signal",
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {},
    },
}


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
    meta = synthesis.get("_meta", {})
    generated_at = meta.get("generated_at", "")
    week_ending = meta.get("week_ending", "")

    # Try generated_at first, fall back to week_ending
    ref_date = None
    if generated_at:
        ref_date = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    elif week_ending:
        try:
            ref_date = datetime.strptime(week_ending, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    if ref_date is None:
        print("  ⚠ synthesis has no generated_at or week_ending — cannot assess freshness, skipping")
        return False

    age = datetime.now(timezone.utc) - ref_date
    if age.days > max_age_days:
        print(f"  ⚠ synthesis is {age.days} days old (max {max_age_days}) — STALE, skipping publish")
        return False
    print(f"  ✓ synthesis age: {age.days} day(s)")
    return True


def check_synthesis_valid(synthesis: dict) -> bool:
    """Check synthesis isn't a stub / raw fallback."""
    keys = set(synthesis.keys()) - {"_meta"}
    if not keys:
        print("  ⚠ synthesis has no content keys (only _meta) — STUB, skipping publish")
        return False
    if keys == {"_raw_fallback"}:
        print("  ⚠ synthesis is raw fallback only — skipping publish")
        return False
    return True


# ── Meta ──────────────────────────────────────────────────────────────────

def build_meta(prev_report: dict, synthesis: dict, publish_date: str, config: dict) -> dict:
    prev_meta = prev_report.get("meta", {})
    prev_issue = prev_meta.get("issue", 0)
    # Use publish date for the week label (not forward-looking week_ending from synthesis)
    week_date = publish_date

    try:
        week_label = f"W/E {datetime.strptime(week_date, '%Y-%m-%d').strftime('%-d %B %Y')}"
    except ValueError:
        week_label = f"W/E {week_date}"

    return {
        "issue": prev_issue + 1,
        "volume": prev_meta.get("volume", 1),
        "week_label": week_label,
        "published": f"{publish_date}{config['publish_time']}",
        "slug": publish_date,
        "publish_time_utc": config["publish_time"],
        "editor": f"{config['abbr'].lower()}-publisher-bot",
        "schema_version": "2.0",
    }


# ── Signal ────────────────────────────────────────────────────────────────

def build_signal(synthesis: dict, prev_report: dict, config: dict) -> dict | None:
    """Build signal from synthesis lead_signal, or carry forward."""
    signal_key = config.get("signal_key")

    # GMM: signal is a composite of lead_signal + stress_regime_preliminary
    if config.get("signal_builder") == "gmm":
        return build_gmm_signal(synthesis, prev_report)

    if signal_key and signal_key in synthesis:
        ls = synthesis[signal_key]
        return {
            "headline": ls.get("headline", ""),
            "actor": ls.get("actor", ls.get("region", "N/A")),
            "confidence": ls.get("confidence", "N/A"),
            "f_flags": ls.get("mf_flags", ls.get("f_flags", [])),
            "note": ls.get("note", ""),
        }
    # Carry forward from previous report
    return prev_report.get("signal", prev_report.get("lead_signal"))


def build_gmm_signal(synthesis: dict, prev_report: dict) -> dict:
    """GMM signal: built from lead_signal + stress_regime_preliminary.
    Dashboard reads: headline, system_stress_label, system_stress_direction,
    system_average_score, regime, regime_conviction, regime_shift_probabilities, source_url.
    """
    ls = synthesis.get("lead_signal", {})
    srp = synthesis.get("stress_regime_preliminary", {})
    prev_signal = prev_report.get("signal", {})

    # Regime label: synthesis regime field, or derive from regional consensus
    regime = srp.get("regime", "")
    if not regime:
        # Derive from regional statuses — take the highest stress level
        levels = {"Green": 0, "Amber": 1, "Red": 2, "Crisis": 3, "Critical": 3}
        max_level = 0
        for region in ["global", "us", "eu", "china", "em_basket"]:
            val = srp.get(region, "")
            max_level = max(max_level, levels.get(val, 0))
        regime = [k for k, v in levels.items() if v == max_level][0] if max_level > 0 else "Green"

    # System average: synthesis value or compute from regions
    system_avg = srp.get("system_average")
    if system_avg is None:
        score_map = {"Green": 0, "Amber": -0.33, "Red": -0.66, "Crisis": -1.0, "Critical": -1.0}
        region_scores = []
        for region in ["global", "us", "eu", "china", "em_basket"]:
            val = srp.get(region, "")
            if val in score_map:
                region_scores.append(score_map[val])
        system_avg = round(sum(region_scores) / max(len(region_scores), 1), 3) if region_scores else None

    # Stress label: map regime to display label
    label_map = {"Green": "GREEN — No systemic stress", "Amber": "AMBER — Elevated stress",
                 "Red": "RED — Systemic stress", "Crisis": "CRISIS — Active crisis",
                 "Critical": "CRITICAL — Pre-crisis"}
    stress_label = label_map.get(regime, regime.upper() if regime else prev_signal.get("system_stress_label", ""))

    # Direction: from regime_delta
    delta = srp.get("regime_delta", "Stable")
    direction_map = {"Stable": "Stable", "Downgrade": "Deteriorating", "Upgrade": "Improving"}
    stress_dir = direction_map.get(delta, delta)

    # Conviction: synthesis value or derive
    conviction = srp.get("conviction", "")
    if not conviction:
        # Count non-Green regions as corroborating
        n = sum(1 for r in ["global", "us", "eu", "china", "em_basket"] if srp.get(r, "Green") != "Green")
        conviction = {0: "LOW", 1: "LOW", 2: "MEDIUM", 3: "MEDIUM", 4: "HIGH", 5: "VERY HIGH"}.get(n, "LOW")

    signal = {
        "headline": ls.get("headline", prev_signal.get("headline", "")),
        "system_stress_label": stress_label,
        "system_stress_direction": stress_dir,
        "system_average_score": system_avg,
        "regime": regime.upper(),
        "regime_conviction": conviction,
        "regime_shift_probabilities": prev_signal.get("regime_shift_probabilities", {}),
        "source_url": ls.get("source_url", ls.get("regime_relevance", "")),
    }

    # Carry forward regime_shift_probabilities from executive_briefing if available
    eb = prev_report.get("executive_briefing", {})
    if eb.get("regime_shift_probabilities") and not signal["regime_shift_probabilities"]:
        signal["regime_shift_probabilities"] = eb["regime_shift_probabilities"]

    return signal


# ── Campaigns (FCW-specific but handled generically) ─────────────────────

def build_campaigns(persistent: dict, synthesis: dict) -> list:
    active = persistent.get("active_campaigns", {})
    campaigns = []
    for actor_key, actor_campaigns in active.items():
        if isinstance(actor_campaigns, list):
            campaigns.extend(actor_campaigns)
        elif isinstance(actor_campaigns, dict):
            campaigns.append(actor_campaigns)

    delta = synthesis.get("delta_strip", {})
    for new_camp in delta.get("new_campaigns", []):
        campaigns.append(new_camp)
    for change in delta.get("status_changes", []):
        cid = change.get("campaign_id", "")
        for camp in campaigns:
            if camp.get("id") == cid or camp.get("campaign_id") == cid:
                if "new_status" in change:
                    camp["status"] = change["new_status"]
                break

    return campaigns


# ── Actor tracker ─────────────────────────────────────────────────────────

def build_actor_tracker(synthesis: dict, prev_report: dict) -> list:
    synth_actors = synthesis.get("actor_tracker", [])
    if synth_actors:
        return [{
            "actor": a.get("actor", ""),
            "status": a.get("status", a.get("posture", "")),
            "doctrine": a.get("doctrine_note", a.get("doctrine", "")),
            "source_url": a.get("source_url", ""),
            "headline": a.get("headline", a.get("summary", "")[:120]),
        } for a in synth_actors]
    return prev_report.get("actor_tracker", [])


# ── Cross-monitor flags ──────────────────────────────────────────────────

def load_adjacent_reports(current_slug: str) -> dict:
    reports = {}
    for slug in ALL_MONITORS:
        if slug == current_slug:
            continue
        path = REPO_ROOT / f"static/monitors/{slug}/data/report-latest.json"
        if path.exists():
            try:
                reports[slug] = load_json(path)
            except (json.JSONDecodeError, KeyError):
                pass
    print(f"    loaded {len(reports)} adjacent monitor reports")
    return reports


def normalise_prev_flags(prev_cmf) -> tuple[list, list]:
    """Handle three shapes of cross_monitor_flags from previous reports:
    - dict with {flags: [], version_history: []}  (FCW, GMM, AIM)
    - flat list of flag dicts                      (WDM)
    - None / missing                               (ERM)
    Returns (flags_list, version_history_list).
    """
    if prev_cmf is None:
        return [], []
    if isinstance(prev_cmf, list):
        normalised = []
        for f in prev_cmf:
            normalised.append({
                "id": f.get("id", f.get("flag_id", "")),
                "monitor": f.get("monitor", f.get("source_monitor", "")),
                "monitor_slug": f.get("monitor_slug", ""),
                "headline": f.get("headline", f.get("title", "")),
                "linkage": f.get("linkage", f.get("body", "")),
                "classification": f.get("classification", f.get("type", "Structural")),
                "status": f.get("status", "Active"),
                "first_flagged": f.get("first_flagged", ""),
                "updated": f.get("updated", ""),
                "source_url": f.get("source_url", ""),
            })
        return normalised, []
    if isinstance(prev_cmf, dict):
        return list(prev_cmf.get("flags", [])), list(prev_cmf.get("version_history", []))
    return [], []


def normalise_candidates(candidates) -> list:
    """Handle two shapes of cross_monitor_candidates from synthesis:
    - dict keyed by slug abbreviation  (FCW: {wdm: {...}, scem: {...}})
    - list of candidate dicts           (WDM, GMM, AIM, ERM)
    Returns a flat list of candidate dicts.
    """
    if candidates is None:
        return []
    if isinstance(candidates, list):
        return [c for c in candidates if isinstance(c, dict)]
    if isinstance(candidates, dict):
        result = []
        for key, val in candidates.items():
            if isinstance(val, dict):
                val.setdefault("monitor_slug", key)
                result.append(val)
        return result
    return []


def build_cross_monitor_flags(synthesis: dict, prev_report: dict, publish_date: str, current_slug: str) -> dict:
    prev_cmf = prev_report.get("cross_monitor_flags")
    prev_flags, prev_history = normalise_prev_flags(prev_cmf)
    candidates = normalise_candidates(synthesis.get("cross_monitor_candidates"))

    adjacent = load_adjacent_reports(current_slug)
    changes = []

    # Verify existing flags
    for flag in prev_flags:
        slug = flag.get("monitor_slug", "")
        old_status = flag.get("status", "")
        if slug in adjacent:
            adj_meta = adjacent[slug].get("meta", {})
            if adj_meta.get("issue"):
                core = old_status.split("—")[0].strip() if "—" in old_status else old_status
                new_status = f"{core} — verified (adjacent Issue {adj_meta['issue']})"
                if new_status != old_status:
                    flag["status"] = new_status
                    changes.append(f"{flag.get('id')}: verified")
        flag["updated"] = publish_date

    # Promote new candidates
    existing_ids = {f.get("id") for f in prev_flags}
    existing_slugs = {f.get("monitor_slug") for f in prev_flags}
    existing_headlines = {f.get("headline", "").lower() for f in prev_flags}

    for candidate in candidates:
        monitor_slug = candidate.get("monitor_slug", candidate.get("target_monitor", ""))
        headline = candidate.get("headline", candidate.get("signal", ""))

        # Skip if already tracked (by slug AND headline match)
        if monitor_slug in existing_slugs and headline.lower() in existing_headlines:
            continue

        next_id = f"CMF-{len(prev_flags) + 1:03d}"
        prev_flags.append({
            "id": next_id,
            "monitor": candidate.get("monitor", monitor_slug),
            "monitor_slug": monitor_slug,
            "headline": headline,
            "linkage": candidate.get("linkage", candidate.get("type", "")),
            "classification": candidate.get("classification", candidate.get("type", "Structural")),
            "status": "Active — NEW",
            "first_flagged": publish_date,
            "updated": publish_date,
            "source_url": candidate.get("source_url", ""),
        })
        changes.append(f"{next_id}: NEW")

    prev_history.append({
        "date": publish_date,
        "change": "; ".join(changes) if changes else "No changes — routine verification",
        "reason": "Publisher auto-verification",
    })

    config = MONITOR_CONFIGS.get(MONITOR_SLUG, {})
    return {
        "updated": f"{publish_date}{config.get('publish_time', 'T09:00:00Z')}",
        "flags": prev_flags,
        "version_history": prev_history,
    }


# ── Cognitive warfare (FCW-specific) ─────────────────────────────────────

def build_cognitive_warfare(synthesis: dict, prev_report: dict) -> list:
    existing = list(prev_report.get("cognitive_warfare", []))
    existing_headlines = {e.get("headline", "").lower() for e in existing}

    for hl in synthesis.get("intelligence_highlights", []):
        headline = hl.get("headline", hl.get("title", ""))
        if headline.lower() not in existing_headlines:
            next_id = f"CW-{len(existing) + 1:03d}"
            existing.append({
                "id": next_id, "classification": "COGNITIVE WARFARE",
                "headline": headline, "detail": hl.get("detail", hl.get("summary", "")),
                "significance": hl.get("significance", ""), "source_url": hl.get("source_url", ""),
            })

    for kj in synthesis.get("key_judgments", []):
        if kj.get("confidence") not in ("Confirmed", "High"):
            continue
        text = kj.get("text", "")
        if any(skip in text.lower() for skip in ["no new", "no signal", "unchanged", "no operations"]):
            continue
        if text[:50].lower() not in existing_headlines:
            next_id = f"CW-{len(existing) + 1:03d}"
            existing.append({
                "id": next_id, "classification": "COGNITIVE WARFARE",
                "headline": text[:120], "detail": text,
                "significance": kj.get("basis", ""), "source_url": "",
            })

    return existing


# ── Merge synthesis into report ──────────────────────────────────────────

def merge_synthesis_into_report(synthesis: dict, prev_report: dict, config: dict) -> dict:
    """
    Core merge logic: start with previous report as base, overlay
    synthesis fields using the monitor's field_map.

    Fields the publisher explicitly builds (meta, signal, cross_monitor_flags,
    source_url, _meta) are handled separately — not merged here.
    """
    # Fields handled explicitly by the publisher
    EXPLICIT_FIELDS = {"meta", "signal", "lead_signal", "cross_monitor_flags",
                       "source_url", "_meta", "campaigns", "actor_tracker",
                       "platform_responses", "cognitive_warfare", "attribution_log"}

    # Start with previous report (deep copy)
    report = json.loads(json.dumps(prev_report))

    field_map = config.get("field_map", {})
    skip_keys = {"_meta", "weekly_brief_draft", "cross_monitor_candidates",
                 "synthesis_quality_notes", "delta_strip", "_raw_fallback"}

    # Overlay synthesis fields
    for synth_key, synth_value in synthesis.items():
        if synth_key in skip_keys:
            continue

        # Map synthesis key to report key
        report_key = field_map.get(synth_key, synth_key)

        # Don't override fields the publisher handles explicitly
        if report_key in EXPLICIT_FIELDS:
            continue

        # Overlay: synthesis value replaces previous report value
        if synth_value:  # only overlay non-empty values
            report[report_key] = synth_value

    # Map weekly_brief_draft → weekly_brief in report JSON
    brief = synthesis.get("weekly_brief_draft")
    if brief:
        report["weekly_brief"] = brief

    # Strip _preliminary suffix from confidence fields in key_judgments
    for kj in report.get("key_judgments", []):
        if isinstance(kj, dict) and "confidence_preliminary" in kj:
            kj["confidence"] = kj.pop("confidence_preliminary")

    return report


# ── Persistent state ─────────────────────────────────────────────────────

def update_persistent_state(persistent: dict, synthesis: dict, meta: dict, config: dict) -> dict:
    persistent.setdefault("_meta", {})
    persistent["_meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    persistent["_meta"]["last_issue"] = meta["issue"]

    if config.get("has_campaigns"):
        delta = synthesis.get("delta_strip", {})
        for new_camp in delta.get("new_campaigns", []):
            actor = new_camp.get("actor", "UNATTRIBUTED").upper()
            persistent.setdefault("active_campaigns", {}).setdefault(actor, [])
            bucket = persistent["active_campaigns"][actor]
            if isinstance(bucket, list):
                bucket.append(new_camp)
        for change in delta.get("status_changes", []):
            cid = change.get("campaign_id", "")
            for actor_key, camps in persistent.get("active_campaigns", {}).items():
                if isinstance(camps, list):
                    for camp in camps:
                        if camp.get("id") == cid or camp.get("campaign_id") == cid:
                            if "new_status" in change:
                                camp["status"] = change["new_status"]

    return persistent


# ── Archive ──────────────────────────────────────────────────────────────

def build_archive_entry(meta: dict, signal: dict | None, synthesis: dict) -> dict:
    delta = synthesis.get("delta_strip", {})
    strips = []
    rank = 1

    for camp in delta.get("new_campaigns", []):
        strips.append({"rank": rank, "title": camp.get("operation_name", camp.get("summary", ""))[:80],
                        "module_tag": camp.get("actor", ""), "delta_type": "New Campaign",
                        "one_line": camp.get("summary", "")[:200]})
        rank += 1

    for change in delta.get("status_changes", []):
        strips.append({"rank": rank, "title": f"{change.get('campaign_id', '')} status change",
                        "module_tag": change.get("actor", ""), "delta_type": "Status Change",
                        "one_line": f"{change.get('old_status', '')} → {change.get('new_status', '')}"})
        rank += 1

    if not strips:
        headline = ""
        if signal:
            headline = signal.get("headline", "")
        if not headline:
            headline = (synthesis.get("key_judgments", [{}])[0].get("judgment", "") or synthesis.get("key_judgments", [{}])[0].get("text", "No signal this week."))[:200] if synthesis.get("key_judgments") else "No signal this week."
        strips.append({"rank": 1, "title": "No material developments", "module_tag": "ALL",
                        "delta_type": "Quiet Week", "one_line": headline})

    return {
        "issue": meta["issue"], "volume": meta["volume"],
        "week_label": meta["week_label"], "published": meta["slug"],
        "slug": meta["slug"],
        "signal": signal.get("headline", "") if signal else "",
        "source_url": f"{SITE_URL}/monitors/{MONITOR_SLUG}/{meta['slug']}-weekly-brief/",
        "delta_strip": strips,
    }


# ── Hugo brief ────────────────────────────────────────────────────────────

def build_hugo_brief(meta: dict, synthesis: dict, config: dict) -> str:
    brief_body = synthesis.get("weekly_brief_draft", "No brief available this week.")
    signal_headline = ""
    signal_key = config.get("signal_key")
    if signal_key and signal_key in synthesis:
        signal_headline = synthesis[signal_key].get("headline", "")
    if not signal_headline and synthesis.get("key_judgments"):
        signal_headline = (synthesis["key_judgments"][0].get("judgment", "") or synthesis["key_judgments"][0].get("text", ""))[:200]

    # Escape quotes in summary
    summary = signal_headline.replace('"', '\\"')[:200]

    return f"""---
title: "{config['title']} — {meta['week_label']}"
date: {meta['published']}
summary: "{summary}"
draft: false
monitor: "{MONITOR_SLUG}"
---

{brief_body}

---

The [live dashboard]({SITE_URL}/monitors/{MONITOR_SLUG}/dashboard.html) and [JSON data feed]({SITE_URL}/monitors/{MONITOR_SLUG}/data/report-latest.json) have been updated to Issue {meta['issue']} ({meta['week_label']}).

*Published by {config['abbr']} Publisher Bot.*
"""


# ── Last run status ──────────────────────────────────────────────────────

def build_last_run_status(synthesis: dict, config: dict, issues: list = None) -> dict:
    inputs = synthesis.get("_meta", {}).get("inputs_used", {})
    return {
        "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "success": True,
        "publisher": f"{config['abbr'].lower()}-publisher-bot",
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


# ── Schema validation ────────────────────────────────────────────────────

def validate_report(report: dict) -> list[str]:
    errors = []
    meta = report.get("meta", {})
    if not meta.get("issue"):
        errors.append("meta.issue is missing or zero")
    if not meta.get("week_label"):
        errors.append("meta.week_label is empty")
    if meta.get("schema_version") != "2.0":
        errors.append(f"schema_version is '{meta.get('schema_version')}', expected '2.0'")
    if not report.get("source_url"):
        errors.append("source_url is empty")
    return errors


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    if not MONITOR_SLUG:
        print("ERROR: MONITOR_SLUG environment variable not set")
        sys.exit(1)

    config = MONITOR_CONFIGS.get(MONITOR_SLUG)
    if not config:
        print(f"ERROR: No config for monitor '{MONITOR_SLUG}'")
        sys.exit(1)

    print(f"{config['title']} — Publisher")
    print("=" * 50)

    # Paths
    synthesis_path = REPO_ROOT / f"pipeline/monitors/{MONITOR_SLUG}/synthesised/synthesis-latest.json"
    prev_report_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/report-latest.json"
    persistent_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/persistent-state.json"
    archive_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/archive.json"
    data_dir = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data"
    docs_data_dir = REPO_ROOT / f"docs/monitors/{MONITOR_SLUG}/data"
    brief_dir = REPO_ROOT / f"content/monitors/{MONITOR_SLUG}"

    # Load inputs
    print("\n[1/6] Loading inputs...")
    if not synthesis_path.exists():
        print(f"  ✗ synthesis-latest.json not found at {synthesis_path}")
        sys.exit(1)

    synthesis = load_json(synthesis_path)
    prev_report = load_json(prev_report_path) if prev_report_path.exists() else {}
    persistent = load_json(persistent_path) if persistent_path.exists() else {}
    archive = load_json(archive_path) if archive_path.exists() else []

    synth_meta = synthesis.get('_meta', {})
    print(f"  synthesis: {synth_meta.get('status', 'loaded')} "
          f"(week ending {synth_meta.get('week_ending', '?')}, "
          f"generated {synth_meta.get('generated_at', 'N/A')})")
    print(f"  content keys: {sorted(set(synthesis.keys()) - {'_meta'})}")
    if prev_report:
        print(f"  previous report: Issue {prev_report.get('meta', {}).get('issue', '?')}")
    else:
        print(f"  previous report: none (first issue)")

    # Freshness + validity checks
    print("\n[2/6] Checking synthesis...")
    if not check_synthesis_freshness(synthesis):
        sys.exit(1)
    if not check_synthesis_valid(synthesis):
        sys.exit(1)
    print("  ✓ synthesis is fresh and valid")

    publish_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build report
    print("\n[3/6] Assembling report...")
    meta = build_meta(prev_report, synthesis, publish_date, config)
    print(f"  Issue {meta['issue']}, {meta['week_label']}")

    # Start with merged base (synthesis overlaid on previous report)
    report = merge_synthesis_into_report(synthesis, prev_report, config)

    # Override explicit fields
    report["meta"] = meta
    signal = build_signal(synthesis, prev_report, config)
    if signal:
        report_signal_key = config["field_map"].get(config.get("signal_key", ""), "signal")
        report[report_signal_key] = signal

    if config["has_campaigns"]:
        report["campaigns"] = build_campaigns(persistent, synthesis)
    if config["has_actor_tracker"]:
        report["actor_tracker"] = build_actor_tracker(synthesis, prev_report)
    if config["has_platform_responses"]:
        report["platform_responses"] = persistent.get("platform_enforcement_tracker",
                                                       prev_report.get("platform_responses", []))
    if config["has_cognitive_warfare"]:
        report["cognitive_warfare"] = build_cognitive_warfare(synthesis, prev_report)

    # Attribution log: merge
    synth_log = synthesis.get("attribution_log", [])
    prev_log = prev_report.get("attribution_log", [])
    if synth_log or prev_log:
        existing_ids = {e.get("id") for e in prev_log}
        merged_log = list(prev_log)
        for entry in synth_log:
            if entry.get("id") not in existing_ids:
                merged_log.append(entry)
        report["attribution_log"] = merged_log

    # Cross-monitor flags
    report["cross_monitor_flags"] = build_cross_monitor_flags(
        synthesis, prev_report, publish_date, MONITOR_SLUG)

    report["source_url"] = f"{SITE_URL}/monitors/{MONITOR_SLUG}/{publish_date}-weekly-brief/"
    report["_meta"] = {"last_run_status": build_last_run_status(synthesis, config)}

    # Validate
    print("\n[4/6] Validating schema...")
    errors = validate_report(report)
    if errors:
        print("  ⚠ Validation warnings:")
        for e in errors:
            print(f"    - {e}")
        report["_meta"]["last_run_status"]["issues"] = errors
    else:
        print("  ✓ schema valid")

    # Update persistent state
    print("\n[5/6] Updating persistent state + archive...")
    persistent = update_persistent_state(persistent, synthesis, meta, config)
    archive.append(build_archive_entry(meta, signal, synthesis))

    # Hugo brief
    hugo_brief = build_hugo_brief(meta, synthesis, config)

    # Write outputs
    print("\n[6/6] Writing outputs...")
    dated_report_path = data_dir / f"report-{publish_date}.json"
    write_json(dated_report_path, report)
    write_json(data_dir / "report-latest.json", report)
    if persistent:
        write_json(persistent_path, persistent)
    write_json(archive_path, archive)
    write_text(brief_dir / f"{publish_date}-weekly-brief.md", hugo_brief)
    write_json(docs_data_dir / f"report-{publish_date}.json", report)
    write_json(docs_data_dir / "report-latest.json", report)

    print(f"\n{'=' * 50}")
    print(f"{config['abbr']} Issue {meta['issue']} ({meta['week_label']}) published.")
    if errors:
        print(f"  ⚠ {len(errors)} validation warning(s)")


if __name__ == "__main__":
    main()

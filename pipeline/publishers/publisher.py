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

# ── Pipeline incident logging (engine-level) ──────────────────────────────────
try:
    sys.path.insert(0, str(Path(os.environ.get("REPO_ROOT", ".")) / "pipeline"))
    from incident_log import log_incident
except ImportError:
    def log_incident(**kw): pass  # graceful fallback

# ── Lineage envelope writer (Sprint Narrow & Fence Item 3) ───────────────────
try:
    from shared.lineage import mint_ulid, content_sha256, build_envelope, write_lineage_envelope
    _LINEAGE_AVAILABLE = True
except ImportError:
    _LINEAGE_AVAILABLE = False
    def mint_ulid(): import time, random; return f"NOULID{int(time.time()*1000):013d}{random.randint(0,9999):04d}"[:26]
    def content_sha256(obj): return "sha256:" + "0" * 64
    def build_envelope(**kw): return {}
    def write_lineage_envelope(*a, **kw): pass


# All monitors except the current one, for cross-monitor verification
ALL_MONITORS = [
    "democratic-integrity",
    "macro-monitor",
    "european-strategic-autonomy",
    "fimi-cognitive-warfare",
    "ai-governance",
    "environmental-risks",
    "conflict-escalation",
    "financial-integrity",
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
        "signal_key": "lead_signal",
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {
            "lead_signal": "signal",
        },
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
        "field_map": {},  # v2.0 synthesis outputs module_0–module_15 directly
    },
    "environmental-risks": {
        "title": "Global Environmental Risks Monitor",
        "abbr": "ERM",
        "publish_time": "T05:00:00Z",
        "signal_key": None,                # lead_signal lives inside planetary_status_snapshot
        "has_campaigns": False,
        "has_actor_tracker": False,
        "has_cognitive_warfare": False,
        "has_platform_responses": False,
        "field_map": {},                    # v2.2: pass-through synthesis field names directly
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
    "financial-integrity": {
        "title": "Financial Integrity Monitor",
        "abbr": "FIM",
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
        log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="publisher_skip",
                     severity="warning", detail="Synthesis has no generated_at or week_ending")
        print("  ⚠ synthesis has no generated_at or week_ending — cannot assess freshness, skipping")
        return False

    age = datetime.now(timezone.utc) - ref_date
    if age.days > max_age_days:
        log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="publisher_skip",
                     severity="warning", detail=f"Synthesis is {age.days} days old (max {max_age_days}) — STALE")
        print(f"  ⚠ synthesis is {age.days} days old (max {max_age_days}) — STALE, skipping publish")
        return False
    print(f"  ✓ synthesis age: {age.days} day(s)")
    return True


def check_synthesis_valid(synthesis: dict) -> bool:
    """Check synthesis isn't a stub / raw fallback."""
    keys = set(synthesis.keys()) - {"_meta"}
    if not keys:
        log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="publisher_skip",
                     severity="error", detail="Synthesis is a stub (only _meta, no content)")
        print("  ⚠ synthesis has no content keys (only _meta) — STUB, skipping publish")
        return False
    if keys == {"_raw_fallback"}:
        log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="quality_failure",
                     severity="error", detail="Synthesis is raw fallback only (LLM output unparseable)")
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
    """Build signal from synthesis, or carry forward.

    Checks both legacy key (lead_signal) and normalised key (signal)
    so monitors work regardless of which schema version their
    synthesiser outputs.  Class fix for stale carry-forward bug.
    """
    signal_key = config.get("signal_key")

    # GMM: signal is a composite of lead_signal + stress_regime_preliminary
    if config.get("signal_builder") == "gmm":
        return build_gmm_signal(synthesis, prev_report)

    # Try configured key first, then normalised "signal", then legacy "lead_signal"
    ls = None
    for candidate in [signal_key, "signal", "lead_signal"]:
        if candidate and candidate in synthesis:
            ls = synthesis[candidate]
            break

    if ls and isinstance(ls, dict):
        return {
            "headline": ls.get("headline", ""),
            "actor": ls.get("actor", ls.get("region", "N/A")),
            "confidence": ls.get("confidence", "N/A"),
            "f_flags": ls.get("mf_flags", ls.get("f_flags", [])),
            "note": ls.get("note", ""),
            "source_url": ls.get("source_url", ""),
        }
    # Carry forward from previous report
    return prev_report.get("signal", prev_report.get("lead_signal"))


def build_gmm_regime_audit(reasoner: dict, synthesis: dict) -> dict | None:
    """Build a regime_audit block for GMM (BUG-2026-04-17-004).

    Publisher historically renames synth.stress_regime_preliminary -> stress_regime
    and discards the reasoner's regime_assessment_review.recommended_regime entirely.
    That hides divergence between the two stations (reasoner uses a 3-indicator
    corroboration test; synth uses a 2-domain rule; they can disagree on the
    same week's data).

    This helper preserves both calls in the published report so readers can see:
      - what the reasoner recommended (conservative/structural)
      - what the synth published (canonical/tactical)
      - whether they agree
      - why divergence is allowed (methodology note)

    Methodology decision (Option B, 2026-04-17): synth remains canonical for
    published stress_regime; reasoner's call is preserved in audit form pending
    methodology unification (SCOPE-2026-04-17-005).

    Returns None if reasoner data is absent (no audit possible).
    """
    if not reasoner or not isinstance(reasoner, dict):
        return None

    reasoner_review = reasoner.get("regime_assessment_review", {}) or {}
    synth_srp = synthesis.get("stress_regime_preliminary", {}) or {}

    reasoner_regime = reasoner_review.get("recommended_regime") or reasoner_review.get("current_regime")
    reasoner_conviction = reasoner_review.get("recommended_conviction") or reasoner_review.get("current_conviction")
    reasoner_change_warranted = reasoner_review.get("regime_change_warranted")

    synth_regime = synth_srp.get("regime")
    synth_conviction = synth_srp.get("conviction")

    if not reasoner_regime and not synth_regime:
        return None

    divergence = bool(
        reasoner_regime and synth_regime
        and reasoner_regime.strip().upper() != synth_regime.strip().upper()
    )

    audit = {
        "reasoner_recommended": {
            "regime": reasoner_regime,
            "conviction": reasoner_conviction,
            "regime_change_warranted": reasoner_change_warranted,
            "sa_indicator_support": reasoner_review.get("sa_indicator_support"),
            "ts_noise_flag": reasoner_review.get("ts_noise_flag"),
        },
        "synth_preliminary": {
            "regime": synth_regime,
            "conviction": synth_conviction,
            "system_average": synth_srp.get("system_average"),
            "regime_delta": synth_srp.get("regime_delta"),
            "regime_change_evidence": synth_srp.get("regime_change_evidence"),
        },
        "divergence": divergence,
        "canonical_source": "synthesiser",
        "methodology_note": (
            "Published stress_regime is the synthesiser's stress_regime_preliminary "
            "(2-domain corroboration rule). The reasoner's recommended_regime uses "
            "a stricter 3-indicator SA corroboration test and is preserved here for "
            "audit. Divergence indicates a tactical shock the synth has priced in "
            "ahead of reasoner's structural confirmation. Methodology unification "
            "under SCOPE-2026-04-17-005."
        ),
    }
    return audit


def build_gmm_signal(synthesis: dict, prev_report: dict) -> dict:
    """GMM signal: built from lead_signal + stress_regime_preliminary.
    Dashboard reads: headline, system_stress_label, system_stress_direction,
    system_average_score, regime, regime_conviction, regime_shift_probabilities, source_url.
    """
    ls = synthesis.get("signal", synthesis.get("lead_signal", {}))
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


# ── Weekly brief sources (Source Surfacing Principle, ENGINE-RULES §14) ─────

def build_weekly_brief_sources(synthesis: dict, prev_report: dict) -> list:
    """
    Collect verified source URLs from all structured finding arrays to attach
    to the weekly_brief narrative. Publisher-side JOIN — no synthesiser change needed.
    Implements Source Surfacing Principle (ENGINE-RULES Section 14).
    """
    sources = []
    seen_urls = set()

    def add_source(url, label=None, tier=None):
        if not url or url in seen_urls:
            return
        if not url.startswith(("http://", "https://")):
            return
        seen_urls.add(url)
        sources.append({"url": url, "label": label, "tier": tier})

    # Pull from synthesis first (freshest data)
    for field in [
        "defence_developments", "hybrid_threat_incidents", "institutional_developments",
        "domain_developments", "findings", "items", "threat_incidents",
        "weekly_findings", "domain_updates", "developments",
        "standing_tracker_updates", "jurisdiction_risk_movements",
    ]:
        items = synthesis.get(field, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    add_source(
                        item.get("source_url"),
                        label=None,
                        tier=item.get("source_tier"),
                    )

    # Lead signal source
    for sig_key in ["lead_signal", "signal"]:
        sig = synthesis.get(sig_key, {})
        if isinstance(sig, dict):
            add_source(sig.get("source_url"), tier=sig.get("source_tier"))

    # Also pull from domain_tracker if present
    for d in synthesis.get("domain_tracker", {}).values() if isinstance(synthesis.get("domain_tracker"), dict) else synthesis.get("domain_tracker", []) if isinstance(synthesis.get("domain_tracker"), list) else []:
        if isinstance(d, dict):
            add_source(d.get("source_url"), tier=d.get("source_tier"))

    # Fallback: prev_report structured fields
    if not sources:
        for field in ["defence_developments", "hybrid_threats", "institutional_developments"]:
            for item in prev_report.get(field, []):
                if isinstance(item, dict):
                    add_source(item.get("source_url"), tier=item.get("source_tier"))

    return sources[:12]  # cap at 12 — renderer caps display at 8


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
    skip_keys = {"_meta", "weekly_brief_draft",
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

    # ── Shape guards ────────────────────────────────────────────────────
    # AIM module_2 must be {models: [...]} not a flat array.
    # Protects against synthesis regressions where module_2 outputs a
    # regulatory-framework list instead of the expected models dict.
    m2 = report.get("module_2")
    if isinstance(m2, list):
        print(f"  ⚠ WARN: module_2 is a list ({len(m2)} items), not {{models: [...]}}. "
              "Preserving previous report module_2.")
        report["module_2"] = prev_report.get("module_2", {"models": []})

    # Map weekly_brief_draft → weekly_brief in report JSON
    brief = synthesis.get("weekly_brief_draft")
    if brief:
        report["weekly_brief"] = brief

    # Strip _preliminary suffix from confidence fields in key_judgments
    for kj in report.get("key_judgments", []):
        if isinstance(kj, dict) and "confidence_preliminary" in kj:
            kj["confidence"] = kj.pop("confidence_preliminary")

    # ── Confidence auto-downgrade (Housekeeping check 21) ────────────
    # "Confirmed" requires a verifiable source. Without one, the LLM is
    # asserting certainty it cannot back — downgrade to "High".
    # Target: "High" not "Assessed" — preserves the signal that strong
    # evidence exists while correcting the over-claim.
    # (Approved: confidence-calibration-v1.md, Q3 decision, 16 Apr 2026)
    downgraded = []
    for kj in report.get("key_judgments", []):
        if not isinstance(kj, dict):
            continue
        conf = kj.get("confidence", "")
        if conf == "Confirmed":
            has_source = bool(kj.get("source_url"))
            has_evidence = bool(kj.get("supporting_evidence") or kj.get("basis"))
            if not has_source:
                kj["confidence"] = "High"
                kj["confidence_downgrade_reason"] = "auto: Confirmed without source_url → High"
                label = kj.get("id", kj.get("judgment", "?")[:40])
                downgraded.append(label)
    if downgraded:
        print(f"  ⚠ Confidence auto-downgrade: {len(downgraded)} key_judgment(s) "
              f"Confirmed→High (no source_url): {', '.join(downgraded)}")

    # Signal-level: strip _preliminary and auto-downgrade
    sig = report.get("signal", {})
    if isinstance(sig, dict):
        if "confidence_preliminary" in sig:
            sig["confidence"] = sig.pop("confidence_preliminary")
        if sig.get("confidence") == "Confirmed" and not sig.get("source_url"):
            sig["confidence"] = "High"
            sig["confidence_downgrade_reason"] = "auto: Confirmed without source_url → High"
            print("  ⚠ Signal confidence Confirmed→High (no source_url)")

    return report


# ── Persistent state ─────────────────────────────────────────────────────

# Per-monitor extraction config:
#   synthesis_key  → which field in synthesis-latest.json to read
#   persistent_key → which field in persistent-state.json to write
#   mode           → "replace" | "merge_list" | "merge_dict"
#   match_key      → (merge_list only) key to match existing items for update
#
# Notes:
# - "replace": overwrites persistent field with synthesis value
# - "merge_list": updates existing items by match_key, appends new ones
# - "merge_dict": shallow-merges synthesis dict into persistent dict
# - Items with version_history get automatic history entries on change
# - _meta is always updated (handled outside this config)
# - FCW campaigns are handled by dedicated logic (has_campaigns flag)

PERSISTENT_STATE_EXTRACTORS = {
    "democratic-integrity": [
        {"synthesis_key": "country_heatmap", "persistent_key": "heatmap_countries",
         "mode": "custom", "handler": "wdm_heatmap"},
        {"synthesis_key": "mimicry_chain_update", "persistent_key": "mimicry_chains",
         "mode": "custom", "handler": "wdm_mimicry"},
        {"synthesis_key": "institutional_integrity_flags", "persistent_key": "institutional_integrity_active_flags",
         "mode": "merge_list", "match_key": "country"},
    ],
    "macro-monitor": [
        {"synthesis_key": "asset_outlook", "persistent_key": "asset_class_baseline",
         "mode": "custom", "handler": "gmm_asset_baseline"},
        {"synthesis_key": "stress_regime_preliminary", "persistent_key": "conviction_history",
         "mode": "custom", "handler": "gmm_conviction"},
        {"synthesis_key": "tariff_tracker", "persistent_key": "tariff_escalation_protocol",
         "mode": "custom", "handler": "gmm_tariff"},
    ],
    "european-strategic-autonomy": [
        {"synthesis_key": "domain_tracker", "persistent_key": "kpi_state",
         "mode": "custom", "handler": "esa_kpi_state"},
        {"synthesis_key": "election_threat_assessment", "persistent_key": "active_elections",
         "mode": "merge_list", "match_key": "country"},
        {"synthesis_key": "lagrange_point_scores", "persistent_key": "lagrange_scoring_2026",
         "mode": "custom", "handler": "esa_lagrange"},
        {"synthesis_key": "hybrid_threats", "persistent_key": "timeline_events",
         "mode": "custom", "handler": "esa_timeline"},
    ],
    "fimi-cognitive-warfare": [
        {"synthesis_key": "actor_tracker", "persistent_key": "actor_profiles",
         "mode": "custom", "handler": "fcw_actor_profiles"},
        {"synthesis_key": "platform_responses", "persistent_key": "platform_enforcement_tracker",
         "mode": "merge_list", "match_key": "id"},
    ],
    "ai-governance": [
        {"synthesis_key": "module_7", "persistent_key": "module_7_risk_vectors",
         "mode": "custom", "handler": "aim_risk_vectors"},
        {"synthesis_key": "module_9", "persistent_key": "module_9_eu_ai_act_tracker",
         "mode": "custom", "handler": "aim_eu_ai_act"},
        {"synthesis_key": "module_14", "persistent_key": "module_14_concentration_index",
         "mode": "custom", "handler": "aim_concentration"},
        {"synthesis_key": "module_15", "persistent_key": "module_15_aisi_pipeline",
         "mode": "custom", "handler": "aim_aisi"},
        {"synthesis_key": "lab_posture_scorecard", "persistent_key": "ongoing_lab_postures",
         "mode": "merge_list", "match_key": "lab"},
    ],
    "environmental-risks": [
        {"synthesis_key": "planetary_boundary_tracker", "persistent_key": "planetary_boundary_status",
         "mode": "merge_list", "match_key": "boundary"},
        {"synthesis_key": "tipping_point_tracker", "persistent_key": "tipping_system_flags",
         "mode": "custom", "handler": "erm_tipping"},
        {"synthesis_key": "attribution_gap_cases", "persistent_key": "active_attribution_gap_cases",
         "mode": "merge_list", "match_key": "case"},
        {"synthesis_key": "reverse_cascade_check", "persistent_key": "regional_cascade_chains",
         "mode": "custom", "handler": "erm_cascade"},
        {"synthesis_key": "icj_tracker", "persistent_key": "standing_trackers",
         "mode": "custom", "handler": "erm_standing_trackers"},
        {"synthesis_key": "loss_damage_tracker", "persistent_key": "standing_trackers",
         "mode": "custom", "handler": "erm_loss_damage"},
    ],
    "conflict-escalation": [
        {"synthesis_key": "conflict_roster", "persistent_key": "conflict_baselines",
         "mode": "custom", "handler": "scem_baselines"},
        {"synthesis_key": "f_flag_matrix", "persistent_key": "f_flag_history",
         "mode": "custom", "handler": "scem_f_flags"},
        {"synthesis_key": "conflict_roster", "persistent_key": "roster_status",
         "mode": "merge_list", "match_key": "conflict"},
        {"synthesis_key": "roster_watch", "persistent_key": "roster_watch",
         "mode": "replace"},
    ],
    "financial-integrity": [
        {"synthesis_key": "jurisdiction_risk_tracker", "persistent_key": "jurisdiction_baselines",
         "mode": "merge_list", "match_key": "jurisdiction"},
        {"synthesis_key": "tooling_outputs", "persistent_key": "scheme_inventory",
         "mode": "custom", "handler": "fim_scheme_inventory"},
        {"synthesis_key": "tooling_outputs", "persistent_key": "enforcement_gap_log",
         "mode": "custom", "handler": "fim_enforcement_gaps"},
        {"synthesis_key": "tooling_outputs", "persistent_key": "regulatory_horizon",
         "mode": "custom", "handler": "fim_regulatory_horizon"},
        {"synthesis_key": "tooling_outputs", "persistent_key": "ctf_cpf_flags",
         "mode": "custom", "handler": "fim_ctf_cpf"},
        {"synthesis_key": "standing_tracker_synthesis", "persistent_key": "standing_trackers",
         "mode": "merge_list", "match_key": "tracker"},
        {"synthesis_key": "cross_monitor_candidates", "persistent_key": "cross_monitor_flags",
         "mode": "replace"},
    ],
}


# Normalisation maps for fuzzy matching of synthesis ↔ persistent field values.
# Synthesis LLMs produce varying abbreviations; persistent-state uses canonical names.
BOUNDARY_ALIASES = {
    "climate": "Climate Change", "climate change": "Climate Change",
    "biodiversity": "Biosphere Integrity", "biosphere integrity": "Biosphere Integrity",
    "biosphere": "Biosphere Integrity",
    "land system": "Land System Change", "land system change": "Land System Change",
    "land-system change": "Land System Change", "land use": "Land System Change",
    "freshwater": "Freshwater Change", "freshwater change": "Freshwater Change",
    "biogeochemical": "Biogeochemical Flows", "biogeochemical flows": "Biogeochemical Flows",
    "nitrogen": "Biogeochemical Flows", "phosphorus": "Biogeochemical Flows",
    "novel entities": "Novel Entities", "chemical pollution": "Novel Entities",
    "ocean acidification": "Ocean Acidification",
    "atmospheric aerosols": "Atmospheric Aerosol Loading",
    "atmospheric aerosol loading": "Atmospheric Aerosol Loading",
    "aerosol": "Atmospheric Aerosol Loading",
    "stratospheric ozone": "Stratospheric Ozone", "ozone": "Stratospheric Ozone",
}

# Tipping system aliases
TIPPING_ALIASES = {
    "amoc": "AMOC / Atlantic Circulation", "amoc / atlantic circulation": "AMOC / Atlantic Circulation",
    "atlantic overturning": "AMOC / Atlantic Circulation",
    "amazon": "Amazon Dieback", "amazon dieback": "Amazon Dieback",
    "amazon rainforest": "Amazon Dieback",
    "coral": "Coral Reef Collapse", "coral reef collapse": "Coral Reef Collapse",
    "coral reefs": "Coral Reef Collapse",
    "permafrost": "Permafrost Methane Release", "permafrost methane release": "Permafrost Methane Release",
    "arctic permafrost": "Permafrost Methane Release",
    "greenland": "Greenland Ice Sheet", "greenland ice sheet": "Greenland Ice Sheet",
    "west antarctic": "West Antarctic Ice Sheet / Thwaites",
    "west antarctic ice sheet": "West Antarctic Ice Sheet / Thwaites",
    "west antarctic ice sheet / thwaites": "West Antarctic Ice Sheet / Thwaites",
    "wais": "West Antarctic Ice Sheet / Thwaites", "thwaites": "West Antarctic Ice Sheet / Thwaites",
    "arctic sea ice": "Arctic Sea Ice",
}

# Attribution gap case aliases
ATTRIBUTION_GAP_ALIASES = {
    "novel entities": "Novel Entities \u2014 Synthetic Chemicals",
    "novel entities \u2014 synthetic chemicals": "Novel Entities \u2014 Synthetic Chemicals",
    "deep-sea mining": "Deep-Sea Mining \u2014 ISA Governance Void",
    "deep-sea mining \u2014 isa governance void": "Deep-Sea Mining \u2014 ISA Governance Void",
    "aerosol loading": "Atmospheric Aerosol Loading \u2014 Shipping Fuel Transition",
    "atmospheric aerosol loading": "Atmospheric Aerosol Loading \u2014 Shipping Fuel Transition",
    "atmospheric aerosol loading \u2014 shipping fuel transition": "Atmospheric Aerosol Loading \u2014 Shipping Fuel Transition",
    "coral reef bleaching": "Coral Reef Bleaching \u2014 No International Liability Framework",
    "coral reef bleaching \u2014 no international liability framework": "Coral Reef Bleaching \u2014 No International Liability Framework",
    "coral bleaching": "Coral Reef Bleaching \u2014 No International Liability Framework",
}

# Which persistent-state keys use which alias map
ALIAS_MAPS = {
    "boundary": BOUNDARY_ALIASES,
    "system": TIPPING_ALIASES,
    "case": ATTRIBUTION_GAP_ALIASES,
}


def _normalise_match_value(value: str, match_key: str) -> str:
    """Normalise a match value using alias maps if available."""
    alias_map = ALIAS_MAPS.get(match_key)
    if alias_map:
        canonical = alias_map.get(value.lower().strip())
        if canonical:
            return canonical
    return value


def _merge_list(persistent_list: list, synthesis_list: list, match_key: str, publish_date: str) -> list:
    """Update existing items by match_key, append new ones. Tracks version_history."""
    existing_map = {}
    for i, item in enumerate(persistent_list):
        k = item.get(match_key, "")
        if k:
            existing_map[_normalise_match_value(k, match_key)] = i

    updated = 0
    appended = 0
    for synth_item in synthesis_list:
        if not isinstance(synth_item, dict):
            continue
        raw_key = synth_item.get(match_key, "")
        if not raw_key:
            continue
        key_val = _normalise_match_value(raw_key, match_key)
        # Write canonical name back to synthesis item
        if key_val != raw_key:
            synth_item[match_key] = key_val

        if key_val in existing_map:
            idx = existing_map[key_val]
            old = persistent_list[idx]
            # Detect meaningful changes (ignore version_history, last_updated)
            old_compare = {k: v for k, v in old.items() if k not in ("version_history", "last_updated")}
            new_compare = {k: v for k, v in synth_item.items() if k not in ("version_history", "last_updated")}
            if old_compare != new_compare:
                # Preserve version_history, append change record
                history = list(old.get("version_history", []))
                # Build a concise change summary
                changes = []
                for field in synth_item:
                    if field in ("version_history", "last_updated", match_key):
                        continue
                    if synth_item.get(field) != old.get(field):
                        changes.append(field)
                if changes:
                    history.append({
                        "date": publish_date,
                        "fields_changed": changes,
                        "source": "publisher-auto",
                    })
                merged = dict(old)
                merged.update(synth_item)
                merged["version_history"] = history
                merged["last_updated"] = publish_date
                persistent_list[idx] = merged
                updated += 1
        else:
            # New item
            synth_item.setdefault("last_updated", publish_date)
            synth_item.setdefault("version_history", [{"date": publish_date, "source": "publisher-auto", "note": "first entry"}])
            persistent_list.append(synth_item)
            existing_map[key_val] = len(persistent_list) - 1
            appended += 1

    if updated or appended:
        print(f"    merge_list: {updated} updated, {appended} appended")
    return persistent_list


# ── Custom handlers ──────────────────────────────────────────────────────
# Each handler receives (persistent, synthesis_value, publish_date) and
# updates persistent in-place.

def _handle_wdm_heatmap(persistent: dict, synth_val, publish_date: str):
    """WDM: synthesis country_heatmap is a list of country statuses.
    Persistent heatmap_countries is {rapid_decay: [], recovery: [], watchlist: []}."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    buckets = {"rapid_decay": [], "recovery": [], "watchlist": []}
    for c in synth_val:
        status = (c.get("health_status") or c.get("health_delta") or "").lower()
        country = c.get("country_name") or c.get("country", "")
        entry = {"country": country, "severity_score": c.get("severity_score"),
                 "last_updated": publish_date}
        if "decay" in status or "decline" in status:
            buckets["rapid_decay"].append(entry)
        elif "recovery" in status or "improv" in status:
            buckets["recovery"].append(entry)
        else:
            buckets["watchlist"].append(entry)
    # Merge with existing (don't lose countries not in this week's synthesis)
    existing = persistent.get("heatmap_countries", {})
    for bucket_name, new_entries in buckets.items():
        old = existing.get(bucket_name, [])
        old_countries = {e.get("country", "") for e in old if isinstance(e, dict)}
        for entry in new_entries:
            if entry["country"] not in old_countries:
                old.append(entry)
            else:
                # Update existing
                for i, o in enumerate(old):
                    if o.get("country") == entry["country"]:
                        old[i].update(entry)
                        break
        existing[bucket_name] = old
    persistent["heatmap_countries"] = existing
    print(f"    wdm_heatmap: updated {sum(len(v) for v in buckets.values())} countries")


def _handle_wdm_mimicry(persistent: dict, synth_val, publish_date: str):
    """WDM: mimicry_chain_update has {active_chains, new_mimicry_detected, note}."""
    if not isinstance(synth_val, dict):
        return
    if synth_val.get("new_mimicry_detected") and synth_val.get("active_chains"):
        existing = persistent.get("mimicry_chains", [])
        existing_ids = {c.get("chain_id") for c in existing}
        for chain in synth_val["active_chains"]:
            if isinstance(chain, dict) and chain.get("chain_id") not in existing_ids:
                chain.setdefault("first_documented", publish_date)
                existing.append(chain)
        persistent["mimicry_chains"] = existing
        print(f"    wdm_mimicry: {len(existing)} chains total")


def _handle_gmm_asset_baseline(persistent: dict, synth_val, publish_date: str):
    """GMM: synthesis asset_outlook → persistent asset_class_baseline.
    Updates current scores but preserves baseline anchors."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    existing = persistent.get("asset_class_baseline", [])
    existing_map = {e.get("asset_class", ""): i for i, e in enumerate(existing)}
    updated = 0
    for outlook in synth_val:
        ac = outlook.get("asset_class", "")
        if not ac:
            continue
        if ac in existing_map:
            idx = existing_map[ac]
            old = existing[idx]
            new_score = outlook.get("score", outlook.get("current_score"))
            new_flag = outlook.get("outlook_label", outlook.get("current_flag", ""))
            new_dir = outlook.get("conviction", outlook.get("current_direction", ""))
            if new_score is not None and new_score != old.get("current_score"):
                history = list(old.get("version_history", []))
                history.append({"date": publish_date, "old_score": old.get("current_score"),
                                "new_score": new_score, "source": "publisher-auto"})
                old["current_score"] = new_score
                old["current_flag"] = new_flag
                old["current_direction"] = new_dir
                old["version_history"] = history
                updated += 1
        else:
            existing.append({
                "asset_class": ac, "current_score": outlook.get("score"),
                "current_flag": outlook.get("outlook_label", ""),
                "current_direction": outlook.get("conviction", ""),
                "baseline_score": outlook.get("score"), "baseline_date": publish_date,
                "version_history": [{"date": publish_date, "source": "publisher-auto", "note": "first entry"}],
            })
            updated += 1
    persistent["asset_class_baseline"] = existing
    if updated:
        print(f"    gmm_asset_baseline: {updated} asset classes updated")


def _handle_gmm_conviction(persistent: dict, synth_val, publish_date: str):
    """GMM: stress_regime_preliminary → append to conviction_history."""
    if not isinstance(synth_val, dict):
        return
    history = persistent.get("conviction_history", [])
    # Don't duplicate for same date
    if history and history[-1].get("date") == publish_date:
        return
    entry = {
        "date": publish_date,
        "system_average": synth_val.get("system_average"),
        "conviction": synth_val.get("conviction", ""),
        "regime": synth_val.get("regime", ""),
        "regime_conviction": synth_val.get("conviction", ""),
        "rationale": synth_val.get("rationale", synth_val.get("regime_delta", "")),
    }
    history.append(entry)
    # Keep last 52 weeks
    persistent["conviction_history"] = history[-52:]
    print(f"    gmm_conviction: appended (total {len(persistent['conviction_history'])} entries)")


def _handle_gmm_tariff(persistent: dict, synth_val, publish_date: str):
    """GMM: tariff_tracker list → update tariff_escalation_protocol."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    protocol = persistent.get("tariff_escalation_protocol", {})
    if not protocol.get("active"):
        return  # Don't activate protocol from synthesis alone
    # Count active retaliators from tariff_tracker
    retaliators = set()
    wto = []
    for t in synth_val:
        if t.get("status", "").lower() in ("active", "in force", "announced"):
            target = t.get("target", "")
            if target:
                retaliators.add(target)
        if "wto" in t.get("measure", "").lower():
            wto.append(t.get("measure", "")[:80])
    if retaliators:
        protocol["active_retaliators"] = sorted(retaliators)
    if wto:
        protocol["wto_filings"] = wto
    persistent["tariff_escalation_protocol"] = protocol
    print(f"    gmm_tariff: {len(retaliators)} retaliators, {len(wto)} WTO filings")


def _handle_esa_kpi_state(persistent: dict, synth_val, publish_date: str):
    """ESA: domain_tracker list → update kpi_state dict."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    kpi = persistent.get("kpi_state", {})
    for domain in synth_val:
        # Map domain fields to KPI fields where applicable
        dep_risk = domain.get("dependency_risk", "")
        dep_actor = domain.get("dependency_actor", "")
        if dep_risk and dep_actor:
            # Track as a hybrid metric
            pass  # kpi_state fields are manually curated — only update counts
    # Update hybrid_attacks from domain_tracker if available
    hybrid_count = sum(1 for d in synth_val if "hybrid" in d.get("domain", "").lower())
    if hybrid_count:
        kpi["hybrid_attacks_recent"] = hybrid_count
    persistent["kpi_state"] = kpi


def _handle_esa_lagrange(persistent: dict, synth_val, publish_date: str):
    """ESA: lagrange_point_scores → update lagrange_scoring_2026.pillar_directions."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    scoring = persistent.get("lagrange_scoring_2026", {})
    directions = scoring.get("pillar_directions", {})
    for score in synth_val:
        vector = score.get("vector", "")
        progress = score.get("progress_preliminary", score.get("progress", ""))
        if vector and progress:
            directions[vector] = {"progress": progress, "last_updated": publish_date,
                                  "key_metric": score.get("key_metric", ""),
                                  "blocker": score.get("blocker", "")}
    scoring["pillar_directions"] = directions
    persistent["lagrange_scoring_2026"] = scoring
    print(f"    esa_lagrange: {len(directions)} pillar directions updated")


def _handle_esa_timeline(persistent: dict, synth_val, publish_date: str):
    """ESA: hybrid_threats → append to timeline_events."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    events = persistent.get("timeline_events", [])
    existing_headlines = {e.get("event", "").lower() for e in events}
    added = 0
    for threat in synth_val:
        headline = threat.get("headline", "")
        if headline.lower() not in existing_headlines:
            events.append({"date": publish_date, "event": headline,
                           "module": threat.get("threat_type", "hybrid")})
            existing_headlines.add(headline.lower())
            added += 1
    persistent["timeline_events"] = events
    if added:
        print(f"    esa_timeline: {added} events appended (total {len(events)})")


def _handle_fcw_actor_profiles(persistent: dict, synth_val, publish_date: str):
    """FCW: actor_tracker list → update actor_profiles dict."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    profiles = persistent.get("actor_profiles", {})
    updated = 0
    for actor in synth_val:
        key = (actor.get("actor", "") or "").upper()
        if not key:
            continue
        existing = profiles.get(key, {})
        # Update posture/status fields
        new_posture = actor.get("posture", actor.get("status", ""))
        if new_posture and new_posture != existing.get("posture"):
            existing["posture"] = new_posture
            existing["last_updated"] = publish_date
            updated += 1
        doctrine = actor.get("doctrine_note", actor.get("doctrine", ""))
        if doctrine:
            existing["doctrine_note"] = doctrine
        if actor.get("capability_change"):
            existing["capability_change"] = actor["capability_change"]
        profiles[key] = existing
    persistent["actor_profiles"] = profiles
    if updated:
        print(f"    fcw_actor_profiles: {updated} actors updated")


def _handle_aim_risk_vectors(persistent: dict, synth_val, publish_date: str):
    """AIM: module_7 has {vectors: [...]} → update module_7_risk_vectors."""
    vectors = synth_val.get("vectors", []) if isinstance(synth_val, dict) else []
    if not vectors:
        return
    existing = persistent.get("module_7_risk_vectors", [])
    _merge_list(existing, vectors, "vector", publish_date)
    persistent["module_7_risk_vectors"] = existing


def _handle_aim_eu_ai_act(persistent: dict, synth_val, publish_date: str):
    """AIM: module_9 → update module_9_eu_ai_act_tracker."""
    if not isinstance(synth_val, dict):
        return
    tracker = persistent.get("module_9_eu_ai_act_tracker", {})
    # Update law/standards highlights
    for field in ["law_highlights", "standards_highlights", "litigation_highlights", "digest_note"]:
        if synth_val.get(field):
            tracker[field] = synth_val[field]
    # Update standards_vacuum if synthesis mentions it
    if synth_val.get("standards_highlights"):
        tracker["last_updated"] = publish_date
    # Recalculate days to deadline if date is set
    deadline = tracker.get("general_application_date", "")
    if deadline:
        try:
            d = datetime.strptime(deadline, "%Y-%m-%d")
            days_left = (d - datetime.strptime(publish_date, "%Y-%m-%d")).days
            tracker["current_days_to_deadline"] = max(days_left, 0)
        except ValueError:
            pass
    persistent["module_9_eu_ai_act_tracker"] = tracker
    print(f"    aim_eu_ai_act: tracker updated")


def _handle_aim_concentration(persistent: dict, synth_val, publish_date: str):
    """AIM: module_14 has {concentration_index: {...}} → update module_14_concentration_index."""
    if not isinstance(synth_val, dict):
        return
    ci = synth_val.get("concentration_index", {})
    if not ci:
        return
    existing = persistent.get("module_14_concentration_index", {})
    if isinstance(ci, dict):
        existing["domains"] = ci.get("domains", existing.get("domains", {}))
        existing["last_updated"] = publish_date
    persistent["module_14_concentration_index"] = existing
    print(f"    aim_concentration: index updated")


def _handle_aim_aisi(persistent: dict, synth_val, publish_date: str):
    """AIM: module_15 → update module_15_aisi_pipeline."""
    if not isinstance(synth_val, dict):
        return
    tracker = persistent.get("module_15_aisi_pipeline", {})
    for field in ["lab_movements", "government_ai_bodies", "revolving_door"]:
        if synth_val.get(field):
            tracker[field] = synth_val[field]
            tracker["last_updated"] = publish_date
    persistent["module_15_aisi_pipeline"] = tracker
    print(f"    aim_aisi: pipeline updated")


def _handle_erm_tipping(persistent: dict, synth_val, publish_date: str):
    """ERM: tipping_point_tracker → update tipping_system_flags.
    Synthesis uses 'tipping_element' as key; persistent uses 'system'."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    # Rename tipping_element → system for merge
    normalised = []
    for item in synth_val:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        # Map tipping_element to system
        te = entry.pop("tipping_element", "")
        if te and not entry.get("system"):
            entry["system"] = te
        normalised.append(entry)
    existing = persistent.get("tipping_system_flags", [])
    _merge_list(existing, normalised, "system", publish_date)
    persistent["tipping_system_flags"] = existing


def _handle_erm_cascade(persistent: dict, synth_val, publish_date: str):
    """ERM: reverse_cascade_check → update regional_cascade_chains."""
    if not isinstance(synth_val, dict) or not synth_val.get("checked"):
        return
    if not synth_val.get("accelerates_boundary"):
        return  # No cascade detected this week
    chains = persistent.get("regional_cascade_chains", [])
    existing_regions = {c.get("region", "").lower() for c in chains}
    region = synth_val.get("affected_boundary", synth_val.get("geopolitical_event", ""))
    if region and region.lower() not in existing_regions:
        chains.append({
            "region": region,
            "chain": synth_val.get("cascade_description", ""),
            "status": "active",
            "current_stage": synth_val.get("geopolitical_event", ""),
            "reverse_cascade": True,
            "first_recorded": publish_date,
            "version_history": [{"date": publish_date, "source": "publisher-auto", "note": "detected"}],
        })
        persistent["regional_cascade_chains"] = chains
        print(f"    erm_cascade: new chain added ({region})")


def _handle_erm_standing_trackers(persistent: dict, synth_val, publish_date: str):
    """ERM: icj_tracker → update standing_trackers.icj_climate_advisory."""
    if not isinstance(synth_val, dict):
        return
    trackers = persistent.get("standing_trackers", {})
    existing = trackers.get("icj_climate_advisory", {})
    for field in ["status", "last_development", "last_development_date", "next_milestone", "significance"]:
        if synth_val.get(field):
            existing[field] = synth_val[field]
    existing["last_updated"] = publish_date
    trackers["icj_climate_advisory"] = existing
    persistent["standing_trackers"] = trackers
    print(f"    erm_standing_trackers: ICJ advisory updated")


def _handle_erm_loss_damage(persistent: dict, synth_val, publish_date: str):
    """ERM: loss_damage_tracker → update standing_trackers.loss_damage_finance."""
    if not isinstance(synth_val, dict):
        return
    trackers = persistent.get("standing_trackers", {})
    existing = trackers.get("loss_damage_finance", {})
    for field in ["mechanism_status", "committed_usd", "disbursed_usd",
                  "disbursement_ratio", "compliance_cycle", "key_development"]:
        if synth_val.get(field):
            existing[field] = synth_val[field]
    existing["last_updated"] = publish_date
    trackers["loss_damage_finance"] = existing
    persistent["standing_trackers"] = trackers
    print(f"    erm_standing_trackers: loss & damage updated")


def _handle_scem_baselines(persistent: dict, synth_val, publish_date: str):
    """SCEM: conflict_roster → update conflict_baselines."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    existing = persistent.get("conflict_baselines", [])
    existing_map = {e.get("conflict", e.get("theatre_id", "")): i for i, e in enumerate(existing)}
    updated = 0
    for conflict in synth_val:
        theatre_id = conflict.get("theatre_id", conflict.get("theatre_name", ""))
        if not theatre_id:
            continue
        status = conflict.get("status", conflict.get("overall_band", ""))
        if theatre_id in existing_map:
            idx = existing_map[theatre_id]
            old = existing[idx]
            if status and status != old.get("baseline_status"):
                old["baseline_status"] = status
                old["week_count"] = old.get("week_count", 0) + 1
                history = list(old.get("version_history", []))
                history.append({"date": publish_date, "status": status, "source": "publisher-auto"})
                old["version_history"] = history
                updated += 1
            else:
                old["week_count"] = old.get("week_count", 0) + 1
        else:
            existing.append({
                "conflict": theatre_id, "theatre": conflict.get("theatre_name", theatre_id),
                "baseline_status": status, "week_count": 1,
                "baseline_locks_at_week": 4, "first_observed": publish_date,
                "version_history": [{"date": publish_date, "source": "publisher-auto", "note": "first entry"}],
            })
            updated += 1
    persistent["conflict_baselines"] = existing
    if updated:
        print(f"    scem_baselines: {updated} conflicts updated")


def _handle_scem_f_flags(persistent: dict, synth_val, publish_date: str):
    """SCEM: f_flag_matrix → append new F-flags to f_flag_history."""
    if not isinstance(synth_val, list) or not synth_val:
        return
    history = persistent.get("f_flag_history", [])
    existing_keys = {(f.get("flag", ""), f.get("conflict", "")) for f in history}
    added = 0
    for entry in synth_val:
        theatre = entry.get("theatre_id", "")
        for flag in entry.get("f_flags_detected", []):
            flag_name = flag if isinstance(flag, str) else flag.get("flag", "")
            if (flag_name, theatre) not in existing_keys:
                history.append({
                    "flag": flag_name, "conflict": theatre,
                    "indicator": "", "detail": "",
                    "applied": publish_date, "status": "active",
                    "version_history": [{"date": publish_date, "source": "publisher-auto"}],
                })
                existing_keys.add((flag_name, theatre))
                added += 1
    persistent["f_flag_history"] = history
    if added:
        print(f"    scem_f_flags: {added} new flags added (total {len(history)})")


# ── FIM custom handlers ───────────────────────────────────────────────────

def _handle_fim_scheme_inventory(persistent: dict, synth_val, publish_date: str):
    """FIM: tooling_outputs → update scheme_inventory from active_scheme_inventory."""
    if not isinstance(synth_val, dict):
        return
    schemes = synth_val.get("active_scheme_inventory", [])
    if not schemes:
        return
    existing = persistent.get("scheme_inventory", [])
    existing_map = {e.get("scheme_name", ""): i for i, e in enumerate(existing)}
    updated = 0
    for scheme in schemes:
        name = scheme.get("scheme_name", "")
        if not name:
            continue
        if name in existing_map:
            idx = existing_map[name]
            existing[idx].update(scheme)
            existing[idx]["last_updated"] = publish_date
        else:
            scheme["first_observed"] = publish_date
            scheme["last_updated"] = publish_date
            existing.append(scheme)
        updated += 1
    persistent["scheme_inventory"] = existing
    if updated:
        print(f"    fim_scheme_inventory: {updated} schemes updated (total {len(existing)})")


def _handle_fim_enforcement_gaps(persistent: dict, synth_val, publish_date: str):
    """FIM: tooling_outputs → append enforcement_gap_signals to log."""
    if not isinstance(synth_val, dict):
        return
    gaps = synth_val.get("enforcement_gap_signals", [])
    if not gaps:
        return
    log = persistent.get("enforcement_gap_log", [])
    existing_keys = {(g.get("jurisdiction", ""), g.get("gap_description", "")[:50]) for g in log}
    added = 0
    for gap in gaps:
        key = (gap.get("jurisdiction", ""), gap.get("gap_description", "")[:50])
        if key not in existing_keys:
            gap["first_flagged"] = publish_date
            gap["status"] = "active"
            log.append(gap)
            existing_keys.add(key)
            added += 1
    persistent["enforcement_gap_log"] = log
    if added:
        print(f"    fim_enforcement_gaps: {added} new gaps (total {len(log)})")


def _handle_fim_regulatory_horizon(persistent: dict, synth_val, publish_date: str):
    """FIM: tooling_outputs → update regulatory_horizon."""
    if not isinstance(synth_val, dict):
        return
    horizon = synth_val.get("regulatory_horizon", [])
    if not horizon:
        return
    persistent["regulatory_horizon"] = horizon
    print(f"    fim_regulatory_horizon: {len(horizon)} items replaced")


def _handle_fim_ctf_cpf(persistent: dict, synth_val, publish_date: str):
    """FIM: tooling_outputs → append CTF/CPF flags."""
    if not isinstance(synth_val, dict):
        return
    flags = synth_val.get("ctf_cpf_flags", [])
    if not flags:
        return
    existing = persistent.get("ctf_cpf_flags", [])
    existing_keys = {(f.get("pillar", ""), f.get("jurisdiction", ""), f.get("signal", "")[:50]) for f in existing}
    added = 0
    for flag in flags:
        key = (flag.get("pillar", ""), flag.get("jurisdiction", ""), flag.get("signal", "")[:50])
        if key not in existing_keys:
            flag["first_flagged"] = publish_date
            flag["status"] = "active"
            existing.append(flag)
            existing_keys.add(key)
            added += 1
    persistent["ctf_cpf_flags"] = existing
    if added:
        print(f"    fim_ctf_cpf: {added} new CTF/CPF flags (total {len(existing)})")


# Handler registry
CUSTOM_HANDLERS = {
    "wdm_heatmap": _handle_wdm_heatmap,
    "wdm_mimicry": _handle_wdm_mimicry,
    "gmm_asset_baseline": _handle_gmm_asset_baseline,
    "gmm_conviction": _handle_gmm_conviction,
    "gmm_tariff": _handle_gmm_tariff,
    "esa_kpi_state": _handle_esa_kpi_state,
    "esa_lagrange": _handle_esa_lagrange,
    "esa_timeline": _handle_esa_timeline,
    "fcw_actor_profiles": _handle_fcw_actor_profiles,
    "aim_risk_vectors": _handle_aim_risk_vectors,
    "aim_eu_ai_act": _handle_aim_eu_ai_act,
    "aim_concentration": _handle_aim_concentration,
    "aim_aisi": _handle_aim_aisi,
    "erm_tipping": _handle_erm_tipping,
    "erm_cascade": _handle_erm_cascade,
    "erm_standing_trackers": _handle_erm_standing_trackers,
    "erm_loss_damage": _handle_erm_loss_damage,
    "scem_baselines": _handle_scem_baselines,
    "scem_f_flags": _handle_scem_f_flags,
    "fim_scheme_inventory": _handle_fim_scheme_inventory,
    "fim_enforcement_gaps": _handle_fim_enforcement_gaps,
    "fim_regulatory_horizon": _handle_fim_regulatory_horizon,
    "fim_ctf_cpf": _handle_fim_ctf_cpf,
}


def update_persistent_state(persistent: dict, synthesis: dict, meta: dict, config: dict) -> dict:
    publish_date = meta.get("slug", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    persistent.setdefault("_meta", {})
    persistent["_meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    persistent["_meta"]["last_issue"] = meta["issue"]

    # FCW campaign handling (preserved from original)
    if config.get("has_campaigns"):
        delta = synthesis.get("delta_strip", {})
        if isinstance(delta, dict):
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

    # Per-monitor extraction
    extractors = PERSISTENT_STATE_EXTRACTORS.get(MONITOR_SLUG, [])
    if extractors:
        print(f"  Extracting persistent state ({len(extractors)} extractors)...")
    for ext in extractors:
        synth_key = ext["synthesis_key"]
        persist_key = ext["persistent_key"]
        mode = ext["mode"]
        synth_val = synthesis.get(synth_key)

        if synth_val is None:
            continue  # Field not in this week's synthesis

        if mode == "replace":
            persistent[persist_key] = synth_val
            print(f"    {persist_key}: replaced")

        elif mode == "merge_list":
            match_key = ext.get("match_key", "id")
            existing = persistent.get(persist_key, [])
            if isinstance(existing, list) and isinstance(synth_val, list):
                _merge_list(existing, synth_val, match_key, publish_date)
                persistent[persist_key] = existing

        elif mode == "merge_dict":
            existing = persistent.get(persist_key, {})
            if isinstance(existing, dict) and isinstance(synth_val, dict):
                existing.update(synth_val)
                persistent[persist_key] = existing
                print(f"    {persist_key}: merged")

        elif mode == "custom":
            handler_name = ext.get("handler", "")
            handler = CUSTOM_HANDLERS.get(handler_name)
            if handler:
                handler(persistent, synth_val, publish_date)
            else:
                print(f"    ⚠ unknown handler: {handler_name}")

    return persistent


# ── Archive ──────────────────────────────────────────────────────────────

def build_archive_entry(meta: dict, signal: dict | None, synthesis: dict) -> dict:
    delta = synthesis.get("delta_strip", {})
    strips = []
    rank = 1

    # Handle both shapes: list (AIM, GMM, WDM, ESA, ERM) or dict (FCW, SCEM)
    if isinstance(delta, list):
        # Pre-built ranked list — pass through directly
        strips = delta[:5]  # Top 5
    elif isinstance(delta, dict):
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

def build_hugo_brief(meta: dict, synthesis: dict, config: dict, brief_sources: list | None = None) -> str:
    brief_body = synthesis.get("weekly_brief_draft", "No brief available this week.")
    signal_headline = ""
    signal_key = config.get("signal_key")
    if signal_key and signal_key in synthesis:
        signal_headline = synthesis[signal_key].get("headline", "")
    if not signal_headline and synthesis.get("key_judgments"):
        signal_headline = (synthesis["key_judgments"][0].get("judgment", "") or synthesis["key_judgments"][0].get("text", ""))[:200]

    # Escape quotes in summary
    summary = signal_headline.replace('"', '\\"')[:200]

    # Build brief_sources YAML list for Hugo front-matter
    sources_yaml = ""
    if brief_sources:
        items = []
        for s in brief_sources[:12]:
            if isinstance(s, dict):
                url = s.get("url", "")
                label = s.get("label", "")
                tier = s.get("tier", "")
                if url:
                    item = f'  - url: "{url}"'
                    if label:
                        item += f'\n    label: "{label}"'
                    if tier:
                        item += f'\n    tier: "{tier}"'
                    items.append(item)
            elif isinstance(s, str) and s.startswith("http"):
                items.append(f'  - url: "{s}"')
        if items:
            sources_yaml = "\nbrief_sources:\n" + "\n".join(items)

    return f"""---
title: "{config['title']} — {meta['week_label']}"
date: {meta['published']}
summary: "{summary}"
draft: false
monitor: "{MONITOR_SLUG}"{sources_yaml}
---

{brief_body}
"""


# ── AI-readable markdown ─────────────────────────────────────────────

def build_report_markdown(report: dict, config: dict) -> str:
    """Generate a clean AI-readable markdown version of the report.
    This is served at /monitors/{slug}/data/report-latest.md and linked
    via <link rel="alternate" type="text/markdown"> for AI search discovery."""
    meta = report.get("meta", {})
    signal = report.get("signal", {})
    kj_list = report.get("key_judgments", [])

    lines = []
    lines.append(f"# {config['title']} — Issue {meta.get('issue', '?')}")
    lines.append(f"")
    lines.append(f"**{meta.get('week_label', '')}** | Published {meta.get('published', '')}")
    lines.append(f"")
    lines.append(f"Publisher: Asymmetric Intelligence — <https://asym-intel.info>")
    lines.append(f"")
    lines.append(f"License: CC BY 4.0")
    lines.append(f"")
    lines.append(f"Schema version: {meta.get('schema_version', '2.0')}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Signal
    if isinstance(signal, dict) and signal.get("headline"):
        lines.append(f"## Lead Signal")
        lines.append(f"")
        lines.append(f"**{signal['headline']}**")
        lines.append(f"")
        if signal.get("confidence"):
            lines.append(f"Confidence: {signal['confidence']}")
        if signal.get("actor"):
            lines.append(f"Actor: {signal['actor']}")
        if signal.get("system_stress_label"):
            lines.append(f"System stress: {signal['system_stress_label']}")
            lines.append(f"Direction: {signal.get('system_stress_direction', '')}")
        if signal.get("source_url"):
            lines.append(f"Source: {signal['source_url']}")
        lines.append(f"")

    # Key judgments
    if kj_list:
        lines.append(f"## Key Judgments")
        lines.append(f"")
        for i, kj in enumerate(kj_list, 1):
            if not isinstance(kj, dict):
                continue
            text = kj.get("judgment", kj.get("text", ""))
            conf = kj.get("confidence", kj.get("confidence_preliminary", ""))
            lines.append(f"{i}. **{text}**")
            if conf:
                lines.append(f"   - Confidence: {conf}")
            if kj.get("trajectory"):
                lines.append(f"   - Trajectory: {kj['trajectory']}")
            if kj.get("source_url"):
                lines.append(f"   - Source: {kj['source_url']}")
            lines.append(f"")

    # Weekly brief
    brief = report.get("weekly_brief", "")
    if brief:
        lines.append(f"## Weekly Brief")
        lines.append(f"")
        lines.append(brief)
        lines.append(f"")

    # Cross-monitor flags
    cmf = report.get("cross_monitor_flags", {})
    flags = cmf.get("flags", []) if isinstance(cmf, dict) else cmf if isinstance(cmf, list) else []
    if flags:
        lines.append(f"## Cross-Monitor Flags")
        lines.append(f"")
        for flag in flags:
            if not isinstance(flag, dict):
                continue
            lines.append(f"- **{flag.get('headline', '')}** ({flag.get('monitor', '')}) — {flag.get('status', '')}")
        lines.append(f"")

    # Data links
    slug = MONITOR_SLUG
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Data")
    lines.append(f"")
    lines.append(f"- Full report JSON: <{SITE_URL}/monitors/{slug}/data/report-latest.json>")
    lines.append(f"- Living Knowledge: <{SITE_URL}/monitors/{slug}/data/persistent-state.json>")
    lines.append(f"- Archive: <{SITE_URL}/monitors/{slug}/data/archive.json>")
    lines.append(f"- Dashboard: <{SITE_URL}/monitors/{slug}/dashboard.html>")
    lines.append(f"- Methodology: <{SITE_URL}/monitors/{slug}/methodology.html>")
    lines.append(f"")

    return "\n".join(lines)


# ── Last run status ──────────────────────────────────────────────────────


def sanitise_for_public(report: dict) -> dict:
    """Return a deep copy of report with internal fields stripped (ENGINE-RULES §16).

    Removes:
      - _meta (pipeline telemetry — not reader output)
      - _meta.correction subfields except correction.reason (kept as public note)
      - cross_monitor_candidates (internal routing table)
      - _challenge (adversarial challenger verdict — observer-only internal audit trail
        per SCOPE-2026-04-17-003 and CHALLENGER-KNOWHOW §5; attached to
        persistent-state.json by the challenger runner and MUST NOT leak to the public
        report)
      - Any key ending in _preliminary (internal staging label — value already published
        under the canonical key by publisher normalisation; where not yet normalised,
        the _preliminary value is the best available and should be published without
        the internal suffix)
    """
    import copy, re
    r = copy.deepcopy(report)

    # Strip _meta entirely (pipeline telemetry belongs in pipeline-status.json, not reports)
    r.pop("_meta", None)

    # Strip cross_monitor_candidates (internal routing — not published output)
    r.pop("cross_monitor_candidates", None)

    # Strip _challenge (adversarial challenger verdict — observer-only audit trail;
    # publisher reads persistent-state.json to assemble the next report, so without
    # this strip the challenger block would leak into report-latest.json. See
    # ops/CHALLENGER-KNOWHOW.md §5.)
    r.pop("_challenge", None)

    def strip_preliminary_keys(obj):
        """Recursively rename keys ending in _preliminary → canonical name."""
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                canonical = re.sub(r"_preliminary$", "", k)
                new[canonical] = strip_preliminary_keys(v)
            return new
        elif isinstance(obj, list):
            return [strip_preliminary_keys(i) for i in obj]
        return obj

    r = strip_preliminary_keys(r)
    return r

def build_last_run_status(synthesis: dict, config: dict, issues: list = None,
                          reasoner_present: bool | None = None) -> dict:
    inputs = synthesis.get("_meta", {}).get("inputs_used", {})
    # reasoner_present: caller passes real file-existence when known (accurate).
    # Fallback to synth._meta.inputs_used which many synthesisers do not populate
    # (therefore under-reports reasoner availability — see BUG-2026-04-17-004 work).
    reasoner_flag = reasoner_present if reasoner_present is not None else bool(inputs.get("reasoner_latest"))
    return {
        "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "success": True,
        "publisher": f"{config['abbr'].lower()}-publisher-bot",
        "pipeline_inputs": {
            "daily_latest": bool(inputs.get("daily_latest")),
            "weekly_latest": bool(inputs.get("weekly_latest")),
            "reasoner_latest": reasoner_flag,
            "synthesis_latest": True,
        },
        "synthesis_status": synthesis.get("_meta", {}).get("status", "unknown"),
        "issues": issues or [],
        "deferred": [],
    }


# ── Schema validation ────────────────────────────────────────────────────

def validate_report(report: dict, prev_report: dict | None = None) -> list[str]:
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

    # ── Roster continuity check (SCEM and any future roster monitors) ────
    new_roster = report.get("conflict_roster", [])
    if prev_report and new_roster:
        prev_roster = prev_report.get("conflict_roster", [])
        if prev_roster:
            drop = len(prev_roster) - len(new_roster)
            retirements = report.get("roster_watch", {}).get("approaching_retirement", [])
            if drop > 1 and len(retirements) < drop:
                errors.append(
                    f"ROSTER DROP: conflict_roster shrank by {drop} "
                    f"(from {len(prev_roster)} to {len(new_roster)}) "
                    f"with only {len(retirements)} retirement(s). "
                    f"Blocking publish — synthesiser may have dropped conflicts."
                )
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

    # ── Lineage: mint run_id for this publish cycle ───────────────────────────
    # One ULID per end-to-end cycle (AD 2026-04-18 Q3). Publisher is the first
    # wrapped stage; upstream stages will inherit this run_id when they are wrapped.
    run_id = mint_ulid()
    print(f"  run_id: {run_id}")

    # Paths
    synthesised_dir = REPO_ROOT / f"pipeline/monitors/{MONITOR_SLUG}/synthesised"
    synthesis_path = synthesised_dir / "synthesis-latest.json"
    # Sprint 3 Step 1 — dual-file paths (AGM only, at present). When both
    # interpret-latest.json and compose-latest.json exist, they are merged
    # into a synthesis-shape dict and used in preference to the legacy
    # single-file path. If either is missing, the legacy path is used and
    # the pipeline behaves exactly as before. This keeps the 6 un-migrated
    # monitors (WDM/GMM/FCW/ESA/ERM/SCEM) on the old path until Step 4
    # propagation. See AD 2026-04-23 Sprint 3 Step 1.
    interpret_path = synthesised_dir / "interpret-latest.json"
    compose_path = synthesised_dir / "compose-latest.json"
    reasoner_path = REPO_ROOT / f"pipeline/monitors/{MONITOR_SLUG}/reasoner/reasoner-latest.json"
    prev_report_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/report-latest.json"
    persistent_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/persistent-state.json"
    archive_path = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data/archive.json"
    data_dir = REPO_ROOT / f"static/monitors/{MONITOR_SLUG}/data"
    docs_data_dir = REPO_ROOT / f"docs/monitors/{MONITOR_SLUG}/data"
    brief_dir = REPO_ROOT / f"content/monitors/{MONITOR_SLUG}"

    # Load inputs
    print("\n[1/6] Loading inputs...")

    # Sprint 3 Step 1 — dual-file detection + merge (Interpreter + Composer)
    # Merge rule: interpret payload is the base (all modules + _meta);
    # compose payload overlays weekly_brief_draft only. Top-level _meta is
    # taken from interpret (freshness checks key off _meta.week_ending and
    # _meta.generated_at). Compose _meta is preserved under
    # _meta.compose_meta for downstream lineage if needed.
    _dual_file_mode = interpret_path.exists() and compose_path.exists()
    if _dual_file_mode:
        print(f"  dual-file mode (Sprint 3 Step 1): interpret + compose present")
        _interpret = load_json(interpret_path)
        _compose = load_json(compose_path)
        synthesis = dict(_interpret)  # shallow copy — we overlay one key
        _compose_brief = _compose.get("weekly_brief_draft")
        if _compose_brief is not None:
            synthesis["weekly_brief_draft"] = _compose_brief
        # Preserve compose _meta for lineage; keep interpret _meta authoritative.
        _interp_meta = dict(synthesis.get("_meta", {}))
        _compose_meta = _compose.get("_meta") or {}
        if _compose_meta:
            _interp_meta["compose_meta"] = _compose_meta
            synthesis["_meta"] = _interp_meta
    else:
        if not synthesis_path.exists():
            log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="input_missing",
                         severity="error", detail=f"synthesis-latest.json not found at {synthesis_path} (and dual-file pair not present)")
            print(f"  ✗ synthesis-latest.json not found at {synthesis_path}")
            sys.exit(1)
        synthesis = load_json(synthesis_path)
    # Hash synthesis at load time — before any mutation — for input_hashes
    _synthesis_hash = content_sha256(synthesis)
    reasoner_latest = load_json(reasoner_path) if reasoner_path.exists() else {}
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

    # ── R4: Publisher source gate (ENGINE-RULES Section 13) ──────────────────
    try:
        import sys as _pub_sys
        _pub_sys.path.insert(0, str(REPO_ROOT / "pipeline" / "tools"))
        from verify_sources import check_lead_signal_gate
        if signal and isinstance(signal, dict):
            _gate_block, _gate_result = check_lead_signal_gate(
                signal,
                monitor_slug=MONITOR_SLUG,
                log_incident_fn=log_incident,
            )
            if _gate_block:
                print(f"🚫 R4 PUBLISHER GATE: Lead signal source unreachable — BLOCKING PUBLISH")
                print(f"   URL: {signal.get('source_url', 'none')}")
                print(f"   HTTP: {_gate_result.get('http_status')}")
                print(f"   This prevents publishing hallucinated or fabricated lead signals.")
                print(f"   Fix: correct the lead signal source_url in the synthesis output.")
                log_incident(
                    monitor=MONITOR_SLUG, stage="publisher",
                    incident_type="source_gate_block", severity="critical",
                    detail=f"R4 gate blocked publish. Signal: {signal.get('headline','')[:80]}",
                )
                sys.exit(1)
            else:
                print(f"   R4 gate: lead source {'verified' if _gate_result.get('reachable') else 'unverified (warning only)'}")
    except ImportError:
        print("  ⚠ verify_sources not available — R4 gate skipped")
    except Exception as _r4e:
        print(f"  ⚠ R4 gate error (non-fatal): {_r4e}")

    # ── R4-ext: Check all key judgment source_urls (warn-only) ─────────────
    try:
        from verify_sources import check_key_judgment_sources
        _kj_results, _kj_summary = check_key_judgment_sources(
            report, monitor_slug=MONITOR_SLUG, log_incident_fn=log_incident,
        )
        if _kj_summary["total_urls"] > 0:
            print(f"   R4-ext: {_kj_summary['verified']}/{_kj_summary['total_urls']} "
                  f"key judgment source(s) verified "
                  f"({_kj_summary['unreachable']} unreachable)")
        elif _kj_summary["skipped_no_urls"] > 0:
            print(f"   R4-ext: {_kj_summary['skipped_no_urls']} key judgment(s) "
                  f"have no source_urls yet (field populates after next weekly run)")
    except ImportError:
        pass  # verify_sources already warned above
    except Exception as _r4ext_e:
        print(f"  ⚠ R4-ext error (non-fatal): {_r4ext_e}")

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

    # GMM-only: regime audit trail (BUG-2026-04-17-004)
    # Preserves reasoner's recommended_regime alongside synth's preliminary call so
    # divergence between the two methodologies is visible to readers. Synth remains
    # canonical; reasoner is preserved in audit form. See build_gmm_regime_audit docstring.
    if config.get("signal_builder") == "gmm":
        audit = build_gmm_regime_audit(reasoner_latest, synthesis)
        if audit:
            report["regime_audit"] = audit
            if audit.get("divergence"):
                log_incident(
                    monitor=MONITOR_SLUG, stage="publisher",
                    incident_type="regime_divergence", severity="info",
                    detail=(
                        f"Reasoner recommends {audit['reasoner_recommended'].get('regime')}/"
                        f"{audit['reasoner_recommended'].get('conviction')}; "
                        f"synth published {audit['synth_preliminary'].get('regime')}/"
                        f"{audit['synth_preliminary'].get('conviction')}. "
                        f"Audit block included in report."
                    ),
                )
                print(
                    f"  ⚠ regime divergence: reasoner={audit['reasoner_recommended'].get('regime')} "
                    f"synth={audit['synth_preliminary'].get('regime')} — audit block attached"
                )
            else:
                print(f"  ✓ regime agreement: reasoner+synth={audit['synth_preliminary'].get('regime')}")
        else:
            print("  ⚠ regime_audit skipped — reasoner input not available")

    report["source_url"] = f"{SITE_URL}/monitors/{MONITOR_SLUG}/{publish_date}-weekly-brief/"
    report["weekly_brief_sources"] = build_weekly_brief_sources(synthesis, prev_report)
    report["_meta"] = {"last_run_status": build_last_run_status(
        synthesis, config, reasoner_present=bool(reasoner_latest)
    )}

    # Normalise: all monitors use "signal" — remove legacy "lead_signal" if carried forward
    report.pop("lead_signal", None)

    # Validate
    print("\n[4/6] Validating schema...")
    errors = validate_report(report, prev_report)
    blocking = [e for e in errors if e.startswith("ROSTER DROP")]
    warnings = [e for e in errors if e not in blocking]
    if blocking:
        log_incident(monitor=MONITOR_SLUG, stage="publisher", incident_type="schema_violation",
                     severity="critical", detail=f"Blocking validation: {len(blocking)} error(s)",
                     errors=blocking)
        print("  ✗ BLOCKING validation errors:")
        for e in blocking:
            print(f"    - {e}")
        sys.exit(1)
    if warnings:
        print("  ⚠ Validation warnings:")
        for e in warnings:
            print(f"    - {e}")
        report["_meta"]["last_run_status"]["issues"] = warnings
    else:
        print("  ✓ schema valid")

    # Update persistent state
    print("\n[5/6] Updating persistent state + archive...")
    # Snapshot persistent-state before overwrite (insurance against data loss)
    if persistent and persistent_path.exists():
        snapshot_path = data_dir / f"persistent-state-{publish_date}.json"
        write_json(snapshot_path, persistent)
    persistent = update_persistent_state(persistent, synthesis, meta, config)
    archive.append(build_archive_entry(meta, signal, synthesis))

    # Hugo brief
    hugo_brief = build_hugo_brief(meta, synthesis, config, brief_sources=report.get("weekly_brief_sources", []))

    # AI-readable markdown (served at /monitors/{slug}/data/report-latest.md)
    report_md = build_report_markdown(report, config)

    # Write outputs
    print("\n[6/6] Writing outputs...")
    # Sanitise before any public write (ENGINE-RULES §16 — strip _meta, _preliminary, internal fields)
    public_report = sanitise_for_public(report)
    dated_report_path = data_dir / f"report-{publish_date}.json"
    write_json(dated_report_path, public_report)
    write_json(data_dir / "report-latest.json", public_report)
    if persistent:
        write_json(persistent_path, persistent)
    write_json(archive_path, archive)
    write_text(brief_dir / f"{publish_date}-weekly-brief.md", hugo_brief)
    write_text(data_dir / "report-latest.md", report_md)
    write_json(docs_data_dir / f"report-{publish_date}.json", public_report)
    write_json(docs_data_dir / "report-latest.json", public_report)
    write_text(docs_data_dir / "report-latest.md", report_md)

    # ── Lineage: write publisher envelope to asym-intel-internal ───────────────
    # Internal-only. Never written to public paths (ENGINE-RULES §15/§16).
    # Non-blocking: failure is logged but does not abort publish.
    print("\n[lineage] Writing provenance envelope...")
    _synth_meta = synthesis.get("_meta", {})
    _schema_ver = _synth_meta.get("schema_version", "2.0")
    # Strip leading 'gmm-synthesis-v' prefix if present — envelope wants bare semver
    if isinstance(_schema_ver, str) and _schema_ver.startswith("gmm-synthesis-v"):
        _schema_ver = _schema_ver[len("gmm-synthesis-v"):]
    _produced_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _git_sha = os.environ.get("GITHUB_SHA")  # set by GA; None in local runs
    if _git_sha:
        _git_sha = _git_sha[:40]
    envelope = build_envelope(
        run_id=run_id,
        tenant="asym-intel",
        stage="publisher",
        product=MONITOR_SLUG,
        schema_version=_schema_ver,
        produced_at=_produced_at,
        # Upstream stages not yet wrapped — no upstream run_ids to reference.
        # input_artifact_ids will be populated when synthesiser is wrapped (Item 3 follow-on).
        input_artifact_ids=[],
        input_hashes={"synthesis": _synthesis_hash},
        output_obj=public_report,
        status="published",
        git_sha=_git_sha,
    )
    write_lineage_envelope(
        envelope,
        tenant="asym-intel",
        product=MONITOR_SLUG,
        date_str=publish_date,
    )

    print(f"\n{'=' * 50}")
    print(f"{config['abbr']} Issue {meta['issue']} ({meta['week_label']}) published.")
    if errors:
        print(f"  ⚠ {len(errors)} validation warning(s)")


if __name__ == "__main__":
    main()

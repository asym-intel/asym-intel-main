#!/usr/bin/env python3
"""
FCW Reasoner — Attribution Chain Analysis
GitHub Actions script. Runs Wednesday 20:00 UTC.

Loads:
  - persistent-state.json (active campaign registry + attribution log)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector candidates)

Feeds all three as context to sonar-deep-research for attribution chain
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/fimi-cognitive-warfare/reasoner/reasoner-latest.json
  pipeline/monitors/fimi-cognitive-warfare/reasoner/reasoner-YYYY-MM-DD.json

The FCW Analyst reads this at Step 0E before applying methodology.

sonar-deep-research is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
"""

import os
import json
import datetime
import pathlib
import requests
import sys

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-deep-research"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/fimi-cognitive-warfare/reasoner")
OUT_LATEST = OUT_DIR / "reasoner-latest.json"
OUT_DATED  = OUT_DIR / f"reasoner-{TODAY_STR}.json"

# ── Guard ──────────────────────────────────────────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: Reasoner already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

# ── Load input documents ───────────────────────────────────────────────────────

def load_json_file(path, label):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"WARNING: {label} not found at {path} — skipping")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"WARNING: Could not parse {label}: {e}")
        return None

persistent  = load_json_file(
    "static/monitors/fimi-cognitive-warfare/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/fimi-cognitive-warfare/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/fimi-cognitive-warfare/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for attribution reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: active campaigns + attribution log (last 8 weeks)
active_campaigns = persistent.get("campaigns", [])
attribution_log  = persistent.get("attribution_log", [])[-20:]  # last 20 entries

# From weekly research: new campaign candidates + actor tracker
weekly_campaigns = weekly.get("campaigns", []) if weekly else []
weekly_actors    = weekly.get("actor_tracker", []) if weekly else []
weekly_attr_log  = weekly.get("attribution_log", []) if weekly else []

# From daily Collector: Tier 0 candidate findings
daily_findings   = daily.get("findings", []) if daily else []
daily_below      = daily.get("below_threshold", []) if daily else []

print(f"Loaded: {len(active_campaigns)} active campaigns, "
      f"{len(attribution_log)} attribution log entries")
print(f"Weekly research: {len(weekly_campaigns)} campaign candidates, "
      f"{len(weekly_actors)} actor entries")
print(f"Daily Collector: {len(daily_findings)} candidates, "
      f"{len(daily_below)} below threshold")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "active_campaigns": active_campaigns,
    "attribution_log_recent": attribution_log,
    "weekly_new_campaigns": weekly_campaigns,
    "weekly_actor_tracker": weekly_actors,
    "weekly_attribution_log": weekly_attr_log,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: active campaigns > attribution log > weekly > daily
    context_json = json.dumps({
        "active_campaigns": active_campaigns[:15],
        "attribution_log_recent": attribution_log[-10:],
        "weekly_new_campaigns": weekly_campaigns[:10],
        "weekly_actor_tracker": weekly_actors,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]

prompt = f"""You are an expert FIMI attribution analyst performing deep reasoning over
structured intelligence data from the Global FIMI & Cognitive Warfare Monitor.

You have been provided with:
1. Active campaign registry (from persistent-state.json)
2. Recent attribution log entries
3. New campaign candidates from this week's research
4. Daily Collector pre-verified candidates
5. Current actor posture data

Your task is to reason deeply over this structured data and return analytical
conclusions as JSON. You are NOT searching the web — reason only over the
data provided below.

ANALYTICAL TASKS:

A. ATTRIBUTION CONFIDENCE REVIEW
For each active campaign AND each new candidate, assess whether the accumulated
evidence supports upgrading or downgrading confidence_preliminary:
- Review all attribution_log entries related to the campaign
- Check for corroboration across multiple source tiers
- Check for contradictory evidence
- Apply FCW evidentiary thresholds:
  Confirmed = Tier 1 platform disclosure + independent government attribution
  High      = Tier 1 platform disclosure + Tier 2/3 corroboration
  Assessed  = Tier 2/3 sources, credible, not platform-confirmed
  Possible  = Single Tier 3/4 source

B. CAMPAIGN LINKAGE DETECTION
Identify whether any new candidates (weekly or daily) show patterns
consistent with existing registered campaigns:
- Same actor + same TTP fingerprint
- Same infrastructure or targeting pattern
- Same narrative across different platforms
- Mark as "continuation" or "possible_linkage" if strong match

C. ACTOR POSTURE CHANGE DETECTION
Based on the combined data, identify:
- Any actor showing increased operational tempo this week
- Any actor showing doctrine evolution (new TTPs or targeting)
- Any actor with notable absence (expected activity not seen)

D. CROSS-MONITOR ESCALATION FLAGS
Identify findings that should be flagged to adjacent monitors:
- WDM: FIMI targeting electoral processes in monitored countries
- SCEM: FIMI operations alongside conflict escalation (hybrid warfare)
- ESA: FIMI targeting European integration or EU institutions
- AGM: AI capabilities newly observed in FIMI operations

E. CONTESTED FINDINGS
Flag any finding where the evidence is contradictory or where two sources
support different attribution conclusions. These need human review.

STRUCTURED DATA:
{context_json}

Return ONLY valid JSON — no markdown, no prose, no code fences:

{{
  "_meta": {{
    "schema_version": "reasoner-v1.0",
    "monitor_slug": "fimi-cognitive-warfare",
    "job_type": "attribution-chain-reasoning",
    "generated_at": "{datetime.datetime.utcnow().isoformat()}Z",
    "data_date": "{TODAY_STR}",
    "campaigns_reviewed": <integer>,
    "candidates_reviewed": <integer>
  }},
  "attribution_reviews": [
    {{
      "campaign_id_or_candidate": "<id or dedupe_key>",
      "current_confidence": "<existing confidence level>",
      "recommended_confidence": "<Confirmed|High|Assessed|Possible — or UNCHANGED>",
      "recommendation": "<upgrade|downgrade|unchanged>",
      "reasoning": "<2-3 sentences explaining the evidence basis for this recommendation>",
      "key_evidence": ["<evidence item 1>", "<evidence item 2>"],
      "contradictory_evidence": "<any evidence pointing the other way, or null>",
      "needs_human_review": <true|false>
    }}
  ],
  "linkage_detections": [
    {{
      "candidate_id": "<daily or weekly candidate id/dedupe_key>",
      "matches_campaign": "<existing campaign id or null>",
      "match_type": "<continuation|possible_linkage|new_campaign>",
      "match_basis": "<TTPs|infrastructure|narrative|actor|null>",
      "confidence": "<High|Medium|Low>",
      "reasoning": "<why these appear linked>"
    }}
  ],
  "actor_posture_changes": [
    {{
      "actor": "<RU|CN|IR|Gulf|US|IL>",
      "change_type": "<increased_tempo|decreased_tempo|new_ttp|new_targeting|notable_absence>",
      "observation": "<what was observed>",
      "significance": "<why this matters analytically>",
      "confidence": "<High|Medium|Low>"
    }}
  ],
  "cross_monitor_escalation_flags": [
    {{
      "target_monitor": "<wdm|scem|esa|agm>",
      "flag_type": "<electoral_fimi|hybrid_warfare|eu_targeting|ai_fimi>",
      "summary": "<what should be flagged and why>",
      "source_campaign_or_finding": "<campaign id or candidate dedupe_key>",
      "urgency": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "contested_findings": [
    {{
      "finding_id": "<campaign or candidate id>",
      "contradiction": "<what is contradictory>",
      "source_a": "<one view + source>",
      "source_b": "<conflicting view + source>",
      "recommended_action": "<hold|escalate|downgrade>"
    }}
  ],
  "analyst_briefing": "<200-300 word summary for the FCW Analyst. Cover: key attribution changes recommended, important linkages detected, actor posture changes, cross-monitor flags. Written in cold analytical register.>"
}}"""

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for attribution chain reasoning...")
print(f"Context size: {len(context_json)} chars")

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    },
    json={
        "model":       MODEL,
        "messages":    [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    },
    timeout=300,
)
response.raise_for_status()

api_response = response.json()
raw_content  = api_response["choices"][0]["message"]["content"]

print(f"Response received. Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

# ── Parse ──────────────────────────────────────────────────────────────────────

clean = raw_content.strip()
if clean.startswith("```"):
    clean = clean.split("```", 2)[-1]
    clean = clean.rsplit("```", 1)[0].strip()
    if clean.startswith("json"):
        clean = clean[4:].strip()

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    sys.exit(1)

# ── Validate ───────────────────────────────────────────────────────────────────

errors = []
meta = data.get("_meta", {})
if meta.get("schema_version") != "reasoner-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'reasoner-v1.0'")
if not data.get("analyst_briefing"):
    errors.append("analyst_briefing missing")

if errors:
    print(f"VALIDATION FAILED: {errors}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    sys.exit(1)

# ── Write ──────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output, encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

reviews   = data.get("attribution_reviews", [])
linkages  = data.get("linkage_detections", [])
flags     = data.get("cross_monitor_escalation_flags", [])
contested = data.get("contested_findings", [])
posture   = data.get("actor_posture_changes", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Attribution reviews: {len(reviews)} "
      f"({sum(1 for r in reviews if r.get('recommendation') != 'unchanged')} changes recommended)")
print(f"   Linkages detected: {len(linkages)}")
print(f"   Actor posture changes: {len(posture)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

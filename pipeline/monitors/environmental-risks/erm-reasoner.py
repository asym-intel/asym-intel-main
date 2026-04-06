#!/usr/bin/env python3
"""
ERM Reasoner — Earth System Reasoning
GitHub Actions script. Runs Friday 18:00 UTC.

Loads:
  - static/monitors/environmental-risks/data/persistent-state.json
      (planetary boundary registry, tipping system state, cascade watch list)
  - pipeline/monitors/environmental-risks/weekly/weekly-latest.json
      (weekly_developments, tipping_point_tracker, planetary_boundary_tracker)
  - pipeline/monitors/environmental-risks/daily/daily-latest.json
      (findings array)

Feeds all three as context to sonar-deep-research for Earth system reasoning.
Outputs structured analytical recommendations to:
  pipeline/monitors/environmental-risks/reasoner/reasoner-latest.json
  pipeline/monitors/environmental-risks/reasoner/reasoner-YYYY-MM-DD.json

The ERM Analyst reads this at Step 0E before applying methodology.

sonar-deep-research is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
"""

import os
import json
import datetime
import pathlib
import requests
import sys
import re

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-deep-research"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/environmental-risks/reasoner")
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

persistent = load_json_file(
    "static/monitors/environmental-risks/data/persistent-state.json",
    "persistent-state"
)
weekly     = load_json_file(
    "pipeline/monitors/environmental-risks/weekly/weekly-latest.json",
    "weekly research"
)
daily      = load_json_file(
    "pipeline/monitors/environmental-risks/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for Earth system reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: planetary boundary registry, tipping system state, cascade watch list
boundary_registry   = persistent.get("planetary_boundary_registry", {})
tipping_state       = persistent.get("tipping_system_state", {})
cascade_watch_list  = persistent.get("cascade_watch_list", [])

# From weekly research: developments, trackers
weekly_developments        = weekly.get("weekly_developments", []) if weekly else []
weekly_tipping_tracker     = weekly.get("tipping_point_tracker", {}) if weekly else {}
weekly_boundary_tracker    = weekly.get("planetary_boundary_tracker", {}) if weekly else {}
weekly_extreme_events      = weekly.get("extreme_events_log", []) if weekly else []
weekly_climate_security    = weekly.get("climate_security_nexus", {}) if weekly else {}

# From daily Collector: findings array
daily_findings = daily.get("findings", []) if daily else []

print(f"Loaded: {len(boundary_registry)} boundary registry entries, "
      f"{len(tipping_state)} tipping system states, "
      f"{len(cascade_watch_list)} cascade watch items")
print(f"Weekly research: {len(weekly_developments)} developments, "
      f"{len(weekly_tipping_tracker)} tipping trackers, "
      f"{len(weekly_boundary_tracker)} boundary trackers")
print(f"Daily Collector: {len(daily_findings)} findings")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "boundary_registry": boundary_registry,
    "tipping_system_state": tipping_state,
    "cascade_watch_list": cascade_watch_list,
    "weekly_developments": weekly_developments,
    "weekly_tipping_point_tracker": weekly_tipping_tracker,
    "weekly_planetary_boundary_tracker": weekly_boundary_tracker,
    "weekly_extreme_events_log": weekly_extreme_events,
    "weekly_climate_security_nexus": weekly_climate_security,
    "daily_collector_findings": daily_findings
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: tipping state > boundary registry > cascade watch > weekly > daily
    context_json = json.dumps({
        "boundary_registry": boundary_registry,
        "tipping_system_state": tipping_state,
        "cascade_watch_list": cascade_watch_list[:10],
        "weekly_developments": weekly_developments[:15],
        "weekly_tipping_point_tracker": weekly_tipping_tracker,
        "weekly_planetary_boundary_tracker": weekly_boundary_tracker,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]

prompt = f"""You are an expert Earth system analyst performing deep reasoning over
structured intelligence data from the Environmental Risks Monitor.

You have been provided with:
1. Planetary boundary registry (from persistent-state.json)
2. Tipping system state (current tracked trajectory per element)
3. Cascade watch list (active environmental-geopolitical cascades under monitoring)
4. Weekly research developments, tipping point tracker, planetary boundary tracker
5. Daily Collector findings

Your task is to reason deeply over this structured data and return analytical
conclusions as JSON. You are NOT searching the web — reason only over the
data provided below.

ANALYTICAL TASKS:

A. PLANETARY BOUNDARY STATUS REVIEW
For each tracked planetary boundary in the registry, review the accumulated
weekly evidence and recommend a status upgrade, downgrade, or hold:
- Review all weekly_planetary_boundary_tracker and weekly_developments entries
  relevant to the boundary
- Apply the scientific source threshold:
    High confidence  = PIK / Stockholm Resilience Centre / Copernicus / IPCC source
    Assessed         = Tier 2 scientific press (Nature, Science, Carbon Brief)
    Media alone      = Assessed at most — never Confirmed without Tier 1 source
- Flag if any boundary shows a trajectory acceleration requiring analyst attention

B. TIPPING POINT TRAJECTORY ASSESSMENT
For each of the five tracked tipping elements (AMOC, ice_sheets, permafrost,
Amazon, coral), assess whether this week's signals represent:
- trajectory_acceleration: signals are stronger / faster than the prior baseline
- trajectory_continuation: signals continue existing trajectory without acceleration
- trajectory_deceleration: signals indicate a slowing or partial reversal
- no_signal: no qualifying signals this week
Apply scientific source threshold (Tier 1 required for acceleration call;
Tier 2/3 alone = Assessed continuation at most).

C. CASCADE RISK PATTERN DETECTION
Review the cascade_watch_list against new weekly_developments and
daily_collector_findings. Identify whether new findings show patterns of
environmental-geopolitical cascade:
  climate stress → resource conflict → displacement → political instability
- If a cascade pattern matches an existing watch item: recommend status update
- If a new pattern emerges not on the watch list: flag as new_cascade_candidate
- Flag if a cross-monitor signal is warranted to an adjacent monitor

D. CROSS-MONITOR ESCALATION FLAGS
Identify findings that should be flagged to adjacent monitors:
- scem: climate-conflict nexus, displacement as conflict driver,
        resource conflict (water/food stress → political violence)
- gmm:  commodity disruption from climate events, stranded asset risks,
        physical risk repricing with macro implications
- wdm:  climate governance failure as democratic stress, climate FIMI
        targeting national elections or referenda
- fcw:  climate FIMI operations — disinformation about attribution events,
        greenwashing campaigns with political dimensions

E. CONTESTED FINDINGS
Flag any finding where the evidence is contradictory or where two sources
support different trajectory or attribution conclusions. These need human review.
Examples: conflicting AMOC slowdown rates from different institutions;
disputed attribution confidence for an extreme event; NDC compliance claims
contradicted by independent assessments.

STRUCTURED DATA:
{context_json}

Return ONLY valid JSON — no markdown, no prose, no code fences:

{{
  "_meta": {{
    "schema_version": "reasoner-v1.0",
    "monitor_slug": "environmental-risks",
    "job_type": "earth-system-reasoning",
    "generated_at": "{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
    "data_date": "{TODAY_STR}",
    "boundaries_reviewed": <integer>,
    "tipping_elements_reviewed": <integer>
  }},
  "boundary_status_reviews": [
    {{
      "boundary": "<climate_change|biosphere_integrity|land_system_change|freshwater_use|biogeochemical_flows|novel_entities|aerosol_loading|stratospheric_ozone|ocean_acidification>",
      "current_status": "<existing status from registry>",
      "recommended_status": "<safe|increasing_risk|high_risk|beyond_boundary — or UNCHANGED>",
      "recommendation": "<upgrade|downgrade|unchanged>",
      "reasoning": "<2-3 sentences explaining the evidence basis for this recommendation>",
      "key_evidence": ["<evidence item 1>", "<evidence item 2>"],
      "source_confidence": "<High|Assessed — per scientific source threshold>",
      "contradictory_evidence": "<any evidence pointing the other way, or null>",
      "needs_human_review": <true|false>
    }}
  ],
  "tipping_trajectory_assessments": [
    {{
      "tipping_element": "<AMOC|ice_sheets|permafrost|Amazon|coral>",
      "current_trajectory": "<existing trajectory from persistent-state>",
      "assessed_trajectory": "<trajectory_acceleration|trajectory_continuation|trajectory_deceleration|no_signal>",
      "trajectory_change": "<accelerated|unchanged|decelerated|no_signal>",
      "reasoning": "<2-3 sentences explaining the evidence basis for this assessment>",
      "key_signals_this_week": ["<signal 1>", "<signal 2>"],
      "source_confidence": "<High|Assessed — per scientific source threshold>",
      "needs_human_review": <true|false>
    }}
  ],
  "cascade_pattern_detections": [
    {{
      "cascade_id_or_candidate": "<watch list id or 'new_candidate'>",
      "cascade_type": "<water_stress|food_insecurity|resource_conflict|mass_displacement|infrastructure_failure>",
      "pattern_status": "<continuation|escalation|de-escalation|new_cascade_candidate>",
      "climate_driver": "<brief description of the climate stressor>",
      "geopolitical_consequence": "<brief description of downstream geopolitical effect>",
      "cross_monitor_signal_warranted": "<scem|gmm|wdm|null>",
      "confidence": "<High|Medium|Low>",
      "reasoning": "<why this pattern is assessed as stated>"
    }}
  ],
  "cross_monitor_escalation_flags": [
    {{
      "target_monitor": "<scem|gmm|wdm|fcw>",
      "flag_type": "<climate_conflict_nexus|displacement_driver|commodity_disruption|stranded_asset|governance_failure|climate_fimi>",
      "summary": "<what should be flagged and why>",
      "source_finding": "<weekly_developments entry title or daily finding id>",
      "urgency": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "contested_findings": [
    {{
      "finding_id": "<development title or finding id>",
      "contradiction": "<what is contradictory>",
      "source_a": "<one view + source>",
      "source_b": "<conflicting view + source>",
      "recommended_action": "<hold|escalate|downgrade>"
    }}
  ],
  "analyst_briefing": "<200-300 word summary for the ERM Analyst. Cover: key boundary status changes recommended, tipping trajectory assessments, cascade patterns detected, cross-monitor escalation flags. Written in cold analytical register.>"
}}"""

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for Earth system reasoning...")
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

# Robust JSON extraction — strip fences, find outermost { }
clean = raw_content.strip()
if clean.startswith("```"):
    # Remove opening fence line
    clean = re.sub(r'^```(?:json)?[ \t]*\n?', '', clean)
    # Remove closing fence
    clean = re.sub(r'\n?```[ \t]*$', '', clean).strip()
# Find outermost JSON object (handles any leading/trailing text)
brace_start = clean.find('{')
brace_end   = clean.rfind('}')
if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
    clean = clean[brace_start:brace_end+1]

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

boundary_reviews  = data.get("boundary_status_reviews", [])
tipping_assessments = data.get("tipping_trajectory_assessments", [])
cascade_detections  = data.get("cascade_pattern_detections", [])
flags             = data.get("cross_monitor_escalation_flags", [])
contested         = data.get("contested_findings", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Boundary status reviews: {len(boundary_reviews)} "
      f"({sum(1 for r in boundary_reviews if r.get('recommendation') != 'unchanged')} changes recommended)")
print(f"   Tipping trajectory assessments: {len(tipping_assessments)} "
      f"({sum(1 for t in tipping_assessments if t.get('trajectory_change') not in ('unchanged', 'no_signal'))} non-trivial)")
print(f"   Cascade patterns detected: {len(cascade_detections)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

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

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/environmental-risks/erm-reasoner-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

_raw_prompt = PROMPT_FILE.read_text(encoding="utf-8")
prompt = _raw_prompt.replace('{context_json}', context_json)
print(f"Prompt loaded ({len(_raw_prompt)} chars)")

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

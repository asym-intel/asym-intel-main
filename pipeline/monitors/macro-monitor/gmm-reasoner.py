#!/usr/bin/env python3
"""
GMM Reasoner — Attribution Chain Analysis
GitHub Actions script. Runs Wednesday 20:00 UTC.

Loads:
  - persistent-state.json (active campaign registry + attribution log)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector candidates)

Feeds all three as context to sonar-deep-research for attribution chain
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/macro-monitor/reasoner/reasoner-latest.json
  pipeline/monitors/macro-monitor/reasoner/reasoner-YYYY-MM-DD.json

The GMM Analyst reads this at Step 0E before applying methodology.

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
OUT_DIR   = pathlib.Path("pipeline/monitors/macro-monitor/reasoner")
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
    "static/monitors/macro-monitor/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/macro-monitor/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/macro-monitor/daily/daily-latest.json",
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

# ── Load reasoning prompt ──────────────────────────────────────────────────────

import datetime as _dt

PROMPT_FILE = pathlib.Path("pipeline/monitors/macro-monitor/gmm-reasoner-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

_raw_prompt = PROMPT_FILE.read_text(encoding="utf-8")
# Inject runtime values
prompt = _raw_prompt.replace('{context_json}', context_json)
prompt = prompt.replace('{generated_at}', _dt.datetime.now(_dt.timezone.utc).isoformat())
prompt = prompt.replace('{data_date}', TODAY_STR)
print(f"Prompt loaded ({len(_raw_prompt)} chars)")

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

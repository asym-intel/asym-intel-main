#!/usr/bin/env python3
"""
SCEM Reasoner — Conflict Trajectory & Escalation Pattern Analysis
GitHub Actions script. Runs Saturday 08:00 UTC.

Loads:
  - persistent-state.json (conflict baselines, roster status, F-flag history,
    roster watch, cross-monitor flags, I1-I6 indicators per conflict)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector findings)

Feeds all three as context to sonar-pro for conflict trajectory
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/conflict-escalation/reasoner/reasoner-latest.json
  pipeline/monitors/conflict-escalation/reasoner/reasoner-YYYY-MM-DD.json

The SCEM Synthesiser reads this at Step 0E before applying methodology.

sonar-pro is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
"""

import os
import json
import datetime
import datetime as _dt
import pathlib
import requests
import sys
import re

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-pro"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/conflict-escalation/reasoner")
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
    "static/monitors/conflict-escalation/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/conflict-escalation/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/conflict-escalation/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for conflict trajectory reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: conflict baselines, roster, F-flags, cross-monitor flags
conflict_baselines   = persistent.get("conflict_baselines", [])
roster_status        = persistent.get("roster_status", [])
f_flag_history       = persistent.get("f_flag_history", [])
roster_watch         = persistent.get("roster_watch", {})
cross_monitor_flags  = persistent.get("cross_monitor_flags", {})
calibration_log      = persistent.get("calibration_log", [])
i5_calibration       = persistent.get("i5_calibration_2026", {})
source_hierarchy     = persistent.get("source_hierarchy_2026", {})

# From weekly research: lead signal, conflict updates, theatre status, displacement
weekly_lead_signal      = weekly.get("lead_signal", {}) if weekly else {}
weekly_conflict_updates = weekly.get("conflict_updates", []) if weekly else []
weekly_theatre_status   = weekly.get("theatre_status", []) if weekly else []
weekly_displacement     = weekly.get("displacement_watch", {}) if weekly else {}
weekly_cross_signals    = weekly.get("cross_monitor_signals", {}) if weekly else {}

# From daily Collector: latest conflict findings
daily_findings          = daily.get("findings", []) if daily else []
daily_below             = daily.get("below_threshold", []) if daily else []
daily_theatre_summary   = daily.get("theatre_summary", {}) if daily else {}

print(f"Loaded: {len(conflict_baselines)} conflict baselines, "
      f"{len(roster_status)} roster entries")
print(f"Weekly research: {len(weekly_conflict_updates)} conflict updates, "
      f"{len(weekly_theatre_status)} theatre statuses")
print(f"Daily Collector: {len(daily_findings)} findings, "
      f"{len(daily_below)} below threshold")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "conflict_baselines": conflict_baselines,
    "roster_status": roster_status,
    "f_flag_history": f_flag_history,
    "roster_watch": roster_watch,
    "cross_monitor_flags": cross_monitor_flags,
    "i5_calibration": i5_calibration,
    "calibration_log": calibration_log,
    "weekly_lead_signal": weekly_lead_signal,
    "weekly_conflict_updates": weekly_conflict_updates,
    "weekly_theatre_status": weekly_theatre_status,
    "weekly_displacement_watch": weekly_displacement,
    "weekly_cross_monitor_signals": weekly_cross_signals,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below,
    "daily_theatre_summary": daily_theatre_summary
}, indent=2)

# Truncate if too large (sonar-pro has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: baselines + roster > weekly > daily
    context_json = json.dumps({
        "conflict_baselines": conflict_baselines,
        "roster_status": roster_status,
        "f_flag_history": f_flag_history[-10:],
        "roster_watch": roster_watch,
        "weekly_lead_signal": weekly_lead_signal,
        "weekly_conflict_updates": weekly_conflict_updates[:5],
        "weekly_theatre_status": weekly_theatre_status,
        "daily_collector_findings": daily_findings[:5]
    }, indent=2)[:MAX_CONTEXT]


# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/scem-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — reasoning without identity context")

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/conflict-escalation/scem-reasoner-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

_raw_prompt = PROMPT_FILE.read_text(encoding="utf-8")
# Inject identity card before pipeline data if available
if identity_content:
    prompt = _raw_prompt.replace('{context_json}',
        "## IDENTITY CARD (analytical quality standard)\n\n" + identity_content[:6000] +
        "\n\n---\n\n## PIPELINE DATA\n\n" + context_json)
else:
    prompt = _raw_prompt.replace('{context_json}', context_json)
prompt = prompt.replace('{generated_at}', _dt.datetime.now(_dt.timezone.utc).isoformat())
prompt = prompt.replace('{data_date}', TODAY_STR)
print(f"Prompt loaded ({len(_raw_prompt)} chars)")

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for conflict trajectory reasoning...")
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

trajectory_reviews  = data.get("trajectory_reviews", [])
deviation_alerts    = data.get("deviation_alerts", [])
baseline_reviews    = data.get("baseline_reviews", [])
cross_flags         = data.get("cross_monitor_flags", [])
roster_changes      = data.get("roster_change_recommendations", [])
f_flag_reviews      = data.get("f_flag_reviews", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Trajectory reviews: {len(trajectory_reviews)}")
print(f"   Deviation alerts: {len(deviation_alerts)}")
print(f"   Baseline reviews: {len(baseline_reviews)}")
print(f"   Cross-monitor flags: {len(cross_flags)}")
print(f"   Roster change recommendations: {len(roster_changes)}")
print(f"   F-flag reviews: {len(f_flag_reviews)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

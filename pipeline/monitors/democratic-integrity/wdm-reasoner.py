#!/usr/bin/env python3
"""
WDM Reasoner — Deterioration Pattern Analysis
GitHub Actions script. Runs Sunday 20:00 UTC.

Loads:
  - persistent-state.json (active country registry + mimicry chains + integrity flags)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector candidates)

Feeds all three as context to sonar-deep-research for deterioration pattern
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/democratic-integrity/reasoner/reasoner-latest.json
  pipeline/monitors/democratic-integrity/reasoner/reasoner-YYYY-MM-DD.json

The WDM Analyst reads this at Step 0E before applying methodology.

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
OUT_DIR   = pathlib.Path("pipeline/monitors/democratic-integrity/reasoner")
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
    "static/monitors/democratic-integrity/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/democratic-integrity/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/democratic-integrity/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for deterioration pattern reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: active country heatmap, mimicry chains, integrity flags
heatmap_rapid   = persistent.get("rapid_decay", [])
heatmap_watchlist = persistent.get("watchlist", [])
heatmap_recovery = persistent.get("recovery", [])
mimicry_chains  = persistent.get("mimicry_chains", [])
integrity_flags = persistent.get("institutional_integrity_flags", [])

# From weekly research: erosion developments, electoral watch, autocratic export
weekly_developments = weekly.get("erosion_developments", []) if weekly else []
weekly_electoral    = weekly.get("electoral_watch", []) if weekly else []
weekly_export       = weekly.get("autocratic_export", []) if weekly else []
weekly_actors       = weekly.get("actor_tracker", []) if weekly else []

# From daily Collector: Tier 0 candidate findings
daily_findings = daily.get("findings", []) if daily else []
daily_below    = daily.get("below_threshold", []) if daily else []

print(f"Loaded: {len(heatmap_rapid)} rapid decay, {len(heatmap_watchlist)} watchlist, "
      f"{len(heatmap_recovery)} recovery countries")
print(f"Mimicry chains: {len(mimicry_chains)} | Integrity flags: {len(integrity_flags)}")
print(f"Weekly developments: {len(weekly_developments)} | Electoral: {len(weekly_electoral)}")
print(f"Daily Collector: {len(daily_findings)} candidates, {len(daily_below)} below threshold")

# ── Build the reasoning prompt ─────────────────────────────────────────────────

context_json = json.dumps({
    "heatmap_rapid_decay": heatmap_rapid,
    "heatmap_watchlist": heatmap_watchlist,
    "heatmap_recovery": heatmap_recovery,
    "mimicry_chains": mimicry_chains,
    "institutional_integrity_flags": integrity_flags[-20:],  # last 20
    "weekly_erosion_developments": weekly_developments,
    "weekly_electoral_watch": weekly_electoral,
    "weekly_autocratic_export": weekly_export,
    "weekly_actor_tracker": weekly_actors,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: rapid decay > watchlist > recovery > mimicry > weekly > daily
    context_json = json.dumps({
        "heatmap_rapid_decay": heatmap_rapid[:15],
        "heatmap_watchlist": heatmap_watchlist[:10],
        "mimicry_chains": mimicry_chains[:8],
        "institutional_integrity_flags": integrity_flags[-10:],
        "weekly_erosion_developments": weekly_developments[:10],
        "weekly_electoral_watch": weekly_electoral[:5],
        "daily_collector_findings": daily_findings[:8]
    }, indent=2)[:MAX_CONTEXT]

# ── Load reasoning prompt from repo (repo-first pattern) ─────────────────────
import subprocess
import base64
_PROMPT_PATH = "docs/crons/reasoner-prompts/wdm-reasoner-prompt.md"
_pr = subprocess.run(
    ['gh', 'api',
     '/repos/asym-intel/asym-intel-main/contents/' + _PROMPT_PATH,
     '--jq', '.content'],
    capture_output=True, text=True
)
if _pr.returncode != 0 or not _pr.stdout.strip():
    print('ERROR: Could not fetch prompt from ' + _PROMPT_PATH)
    sys.exit(1)
_raw_prompt = base64.b64decode(_pr.stdout.strip()).decode('utf-8')
# Inject context_json into prompt (replaces {context_json} placeholder in .md)
prompt = _raw_prompt.replace('{context_json}', context_json)
print('Prompt loaded from repo (' + str(len(_raw_prompt)) + ' chars)')

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for deterioration pattern reasoning...")
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
    clean = re.sub(r'^```(?:json)?[ \t]*\n?', '', clean)
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

# ── Validate ──────────────────────────────────────────────────────────────────

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

reviews   = data.get("severity_reviews", [])
mimicry   = data.get("mimicry_chain_detections", [])
watchlist = data.get("watchlist_threshold_assessments", [])
flags     = data.get("cross_monitor_escalation_flags", [])
contested = data.get("contested_findings", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Severity reviews: {len(reviews)} "
      f"({sum(1 for r in reviews if r.get('recommendation') != 'unchanged')} changes recommended)")
print(f"   Mimicry chain detections: {len(mimicry)}")
print(f"   Watchlist threshold assessments: {len(watchlist)} "
      f"({sum(1 for w in watchlist if w.get('threshold_crossed')) } crossed)")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

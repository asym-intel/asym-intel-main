#!/usr/bin/env python3
"""
AGM Reasoner — Capability & Governance Reasoning
GitHub Actions script. Runs Thursday 20:00 UTC.

Loads:
  - static/monitors/ai-governance/data/persistent-state.json
      (capability registry, regulatory milestones, risk vectors)
  - pipeline/monitors/ai-governance/weekly/weekly-latest.json
      (weekly_developments, capability_tier_tracker, regulatory_framework_tracker)
  - pipeline/monitors/ai-governance/daily/daily-latest.json
      (findings array)

Feeds all three as context to sonar-deep-research for capability and governance
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/ai-governance/reasoner/reasoner-latest.json
  pipeline/monitors/ai-governance/reasoner/reasoner-YYYY-MM-DD.json

The AGM Analyst reads this at Step 0E before applying methodology.

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
OUT_DIR   = pathlib.Path("pipeline/monitors/ai-governance/reasoner")
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
    "static/monitors/ai-governance/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/ai-governance/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/ai-governance/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for capability-governance reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: capability registry, regulatory milestones, risk vectors
capability_registry    = persistent.get("capability_registry", [])
regulatory_milestones  = persistent.get("regulatory_milestones", [])
risk_vectors           = persistent.get("risk_vectors", [])

# From weekly research: developments, capability tracker, regulatory tracker
weekly_developments     = weekly.get("weekly_developments", []) if weekly else []
weekly_cap_tracker      = weekly.get("capability_tier_tracker", {}) if weekly else {}
weekly_reg_tracker      = weekly.get("regulatory_framework_tracker", {}) if weekly else {}
weekly_ai_fimi          = weekly.get("ai_fimi_layer", {}) if weekly else {}

# From daily Collector: findings array
daily_findings   = daily.get("findings", []) if daily else []

print(f"Loaded: {len(capability_registry)} capability registry entries, "
      f"{len(regulatory_milestones)} regulatory milestones, "
      f"{len(risk_vectors)} risk vectors")
print(f"Weekly research: {len(weekly_developments)} developments, "
      f"{len(weekly_cap_tracker)} labs in capability tracker, "
      f"{len(weekly_reg_tracker)} frameworks in regulatory tracker")
print(f"Daily Collector: {len(daily_findings)} findings")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "capability_registry": capability_registry,
    "regulatory_milestones": regulatory_milestones,
    "risk_vectors": risk_vectors,
    "weekly_developments": weekly_developments,
    "weekly_capability_tier_tracker": weekly_cap_tracker,
    "weekly_regulatory_framework_tracker": weekly_reg_tracker,
    "weekly_ai_fimi_layer": weekly_ai_fimi,
    "daily_collector_findings": daily_findings,
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: capability registry > regulatory milestones > risk vectors > weekly > daily
    context_json = json.dumps({
        "capability_registry": capability_registry[:15],
        "regulatory_milestones": regulatory_milestones[-10:],
        "risk_vectors": risk_vectors[:10],
        "weekly_developments": weekly_developments[:15],
        "weekly_capability_tier_tracker": weekly_cap_tracker,
        "weekly_regulatory_framework_tracker": weekly_reg_tracker,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]

# ── Load reasoning prompt from repo (repo-first pattern) ─────────────────────
import subprocess
import base64
_PROMPT_PATH = "docs/crons/reasoner-prompts/agm-reasoner-prompt.md"
_pr = subprocess.run(
    ['gh', 'api',
     '/repos/asym-intel/asym-intel-internal/contents/' + _PROMPT_PATH,
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

print(f"Calling {MODEL} for capability-governance reasoning...")
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
if meta.get("monitor_slug") != "ai-governance":
    errors.append(f"monitor_slug '{meta.get('monitor_slug')}' — expected 'ai-governance'")
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

tier_reviews    = data.get("capability_tier_reviews", [])
milestone_upd   = data.get("regulatory_milestone_updates", [])
risk_detections = data.get("risk_pattern_detections", [])
flags           = data.get("cross_monitor_escalation_flags", [])
contested       = data.get("contested_findings", [])
posture         = data.get("lab_posture_changes", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Capability tier reviews: {len(tier_reviews)} "
      f"({sum(1 for r in tier_reviews if r.get('recommendation') != 'hold')} changes recommended)")
print(f"   Regulatory milestone updates: {len(milestone_upd)}")
print(f"   Risk pattern detections: {len(risk_detections)}")
print(f"   Lab posture changes: {len(posture)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

#!/usr/bin/env python3
"""
FCW Weekly Research — GitHub Actions script
Calls Perplexity sonar-deep-research API with the FCW weekly research prompt,
validates schema, and writes output to pipeline/monitors/fimi-cognitive-warfare/weekly/

Runs: Wednesday 18:00 UTC (15 hours before Thursday FCW Analyst at 09:00 UTC)

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (GitHub repository secret)
"""

import os
import json
import datetime
import pathlib
import requests
import sys

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY     = os.environ["PPLX_API_KEY"]
MODEL       = "sonar-pro"             # sonar-pro: live web search with deeper synthesis
TODAY       = datetime.date.today()
TODAY_STR   = TODAY.isoformat()

# Week ending = next Saturday (or today if Saturday)
days_to_sat = (5 - TODAY.weekday()) % 7
WEEK_ENDING = (TODAY + datetime.timedelta(days=days_to_sat)).isoformat()

OUT_DIR     = pathlib.Path("pipeline/monitors/fimi-cognitive-warfare/weekly")
OUT_LATEST  = OUT_DIR / "weekly-latest.json"
OUT_DATED   = OUT_DIR / f"weekly-{TODAY_STR}.json"

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Weekly research already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt ───────────────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/fimi-cognitive-warfare/fcw-weekly-research-api-prompt.txt"
)
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")

# Inject current week_ending date into prompt context
prompt += f"\n\nCurrent date: {TODAY_STR}. Week ending (Saturday): {WEEK_ENDING}."

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling Perplexity API ({MODEL}) for week ending {WEEK_ENDING}...")
print("Note: sonar-pro may take 10-30 seconds...")

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
    timeout=120,
)
response.raise_for_status()

api_response = response.json()
raw_content  = api_response["choices"][0]["message"]["content"]
citations    = api_response.get("citations", [])

print(f"API response received. Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

# ── Parse JSON output ──────────────────────────────────────────────────────────

# Robust JSON extraction
import re as _re
clean = raw_content.strip()
fence_match = _re.search(r'''```(?:json)?\s*(\{.*?\})\s*```''', clean, _re.DOTALL)
if fence_match:
    clean = fence_match.group(1).strip()
elif clean.startswith("```"):
    clean = _re.sub(r'^```(?:json)?\s*', '', clean)
    clean = _re.sub(r'\s*```$', '', clean).strip()
if not clean.startswith('{'):
    brace = clean.find('{')
    if brace != -1: clean = clean[brace:]
if not clean.endswith('}'):
    brace = clean.rfind('}')
    if brace != -1: clean = clean[:brace+1]

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    sys.exit(1)

# ── Validate schema ───────────────────────────────────────────────────────────

REQUIRED_META = ["schema_version", "monitor_slug", "job_type", "week_ending", "status"]
REQUIRED_LEAD = ["headline", "actor", "confidence_preliminary", "source_url"]

errors   = []
warnings = []

meta = data.get("_meta", {})
for field in REQUIRED_META:
    if field not in meta:
        errors.append(f"_meta.{field} missing")

if meta.get("schema_version") != "weekly-research-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'weekly-research-v1.0'")

lead = data.get("lead_signal", {})
for field in REQUIRED_LEAD:
    if not lead.get(field):
        if field == "source_url":
            warnings.append(f"lead_signal.source_url missing — model did not return a primary URL")
        else:
            errors.append(f"lead_signal.{field} missing or empty")

if not data.get("campaigns"):
    print("INFO: campaigns array is empty — no new campaigns this week (valid)")

if not data.get("actor_tracker"):
    warnings.append("actor_tracker array is empty — actor posture data expected weekly")

if not data.get("weekly_brief_narrative"):
    errors.append("weekly_brief_narrative missing — required for Hugo brief")
elif len(data["weekly_brief_narrative"]) < 200:
    warnings.append(f"weekly_brief_narrative is very short ({len(data['weekly_brief_narrative'])} chars) — expected 400-600 words")

# Validate campaign traceback for High/Confirmed
for i, campaign in enumerate(data.get("campaigns", [])):
    conf = campaign.get("attribution_confidence_preliminary", "")
    if conf in ("Confirmed", "High"):
        sources = campaign.get("research_traceback", {}).get("sources_cited", [])
        if len(sources) < 2:
            errors.append(
                f"campaigns[{i}] ({campaign.get('operation_name','?')}) is {conf} "
                f"but has {len(sources)} source(s) — need 2+"
            )

if errors:
    print(f"SCHEMA VALIDATION FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  ✗ {e}")
    if warnings:
        for w in warnings:
            print(f"  ⚠ {w}")
    # Print structure summary to help diagnose
    print(f"\nStructure received: {list(data.keys())}")
    print(f"_meta keys: {list(data.get('_meta',{}).keys())}")
    print(f"lead_signal keys: {list(data.get('lead_signal',{}).keys())}")
    print(f"campaigns count: {len(data.get('campaigns',[]))}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    debug_path = OUT_DIR / f"debug-{TODAY_STR}.json"
    debug_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Debug output written to {debug_path}")
    sys.exit(1)

for w in warnings:
    print(f"  ⚠ {w}")

# ── Ensure meta fields are correct ───────────────────────────────────────────

data["_meta"]["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
data["_meta"]["week_ending"]  = WEEK_ENDING
data["_meta"]["monitor_slug"] = "fimi-cognitive-warfare"

# ── Write output ──────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_json = json.dumps(data, indent=2, ensure_ascii=False)

OUT_DATED.write_text(output_json, encoding="utf-8")
OUT_LATEST.write_text(output_json, encoding="utf-8")

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_LATEST}")
print(f"   Lead: [{lead.get('confidence_preliminary')}] {lead.get('headline','')[:70]}")
print(f"   Campaigns: {len(data.get('campaigns', []))}")
print(f"   Actor entries: {len(data.get('actor_tracker', []))}")
print(f"   Platform responses: {len(data.get('platform_responses', []))}")
print(f"   Brief narrative: {len(data.get('weekly_brief_narrative',''))} chars")

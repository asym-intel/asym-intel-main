#!/usr/bin/env python3
"""
AGM Weekly Research — GitHub Actions script
Calls Perplexity sonar-deep-research API with the AGM weekly research prompt,
validates schema, and writes output to pipeline/monitors/ai-governance/weekly/

Runs: Thursday 18:00 UTC (synthesiser fires Thursday 22:00 UTC,
      AGM Analyst fires Friday 09:00 UTC)

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (GitHub repository secret)
"""

import os
import json
import datetime
import pathlib
import requests
import sys
import subprocess
import base64

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY     = os.environ["PPLX_API_KEY"]
MODEL       = "sonar-pro"             # sonar-pro: live web search with deeper synthesis
TODAY       = datetime.date.today()
TODAY_STR   = TODAY.isoformat()

# Week ending = next Thursday (AGM analyst fires Fri 09:00 UTC, synthesiser Thu 22:00)
days_to_thu = (3 - TODAY.weekday()) % 7
WEEK_ENDING = (TODAY + datetime.timedelta(days=days_to_thu)).isoformat()

OUT_DIR     = pathlib.Path("pipeline/monitors/ai-governance/weekly")
OUT_LATEST  = OUT_DIR / "weekly-latest.json"
OUT_DATED   = OUT_DIR / f"weekly-{TODAY_STR}.json"

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Weekly research already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt ───────────────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/ai-governance/agm-weekly-research-api-prompt.txt"
)
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")

# Inject current week_ending date into prompt context
prompt += f"\n\nCurrent date: {TODAY_STR}. Week ending (Thursday): {WEEK_ENDING}."


# ── Inject annual calibration from internal repo ──────────────────────────────

_calib_path = "methodology/ai-governance-euaiact-2026.md"
_calib_result = subprocess.run(
    ['gh', 'api',
     f'/repos/asym-intel/asym-intel-internal/contents/{_calib_path}',
     '--jq', '.content'],
    capture_output=True, text=True
)
if _calib_result.returncode == 0 and _calib_result.stdout.strip():
    try:
        _calib_raw = base64.b64decode(
            _calib_result.stdout.strip().replace('\n', '')
        ).decode('utf-8')
        _sec_start = _calib_raw.find('\n## 2.')
        if _sec_start == -1:
            _sec_start = _calib_raw.find('\n## 2 ')
        if _sec_start > -1:
            _inject = _calib_raw[_sec_start:_sec_start + 5000]
            prompt += (
                "\n\nANNUAL CALIBRATION 2026 — apply these rules:\n"
                + _inject
            )
            print(f"Calibration injected: {_calib_path} ({len(_inject)} chars)")
        else:
            print(f"Calibration loaded but no section markers: {_calib_path}")
    except Exception as _ce:
        print(f"Calibration injection skipped: {_ce}")
else:
    print(f"No calibration file for {_calib_path} — proceeding without")

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
REQUIRED_LEAD = ["headline", "indicator", "confidence_preliminary", "source_url"]

errors   = []
warnings = []

meta = data.get("_meta", {})
for field in REQUIRED_META:
    if field not in meta:
        errors.append(f"_meta.{field} missing")

if meta.get("schema_version") != "weekly-research-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'weekly-research-v1.0'")

if meta.get("monitor_slug") != "ai-governance":
    warnings.append(f"monitor_slug '{meta.get('monitor_slug')}' — expected 'ai-governance' (will be corrected)")

lead = data.get("lead_signal", {})
for field in REQUIRED_LEAD:
    if not lead.get(field):
        if field == "source_url":
            warnings.append("lead_signal.source_url missing — model did not return a primary URL")
        else:
            errors.append(f"lead_signal.{field} missing or empty")

# AGM-specific: weekly_developments array
if not data.get("weekly_developments"):
    errors.append("weekly_developments array missing or empty — required for AGM analyst")
else:
    for i, dev in enumerate(data.get("weekly_developments", [])):
        if not dev.get("source_url"):
            warnings.append(f"weekly_developments[{i}] missing source_url")
        if not dev.get("indicator"):
            warnings.append(f"weekly_developments[{i}] missing indicator tag")

# AGM-specific: capability_tier_tracker
if not data.get("capability_tier_tracker"):
    errors.append("capability_tier_tracker missing — required for AGM analyst (Step 0S)")

# AGM-specific: regulatory_framework_tracker
if not data.get("regulatory_framework_tracker"):
    errors.append("regulatory_framework_tracker missing — required for AGM analyst (Step 0S)")

# AGM-specific: weekly_brief_narrative
if not data.get("weekly_brief_narrative"):
    errors.append("weekly_brief_narrative missing — required for Hugo brief")
elif len(data["weekly_brief_narrative"]) < 200:
    warnings.append(
        f"weekly_brief_narrative is very short ({len(data['weekly_brief_narrative'])} chars) "
        f"— expected 400-600 words"
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
    print(f"weekly_developments count: {len(data.get('weekly_developments',[]))}")
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
data["_meta"]["monitor_slug"] = "ai-governance"

# ── Write output ──────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_json = json.dumps(data, indent=2, ensure_ascii=False)

OUT_DATED.write_text(output_json, encoding="utf-8")
OUT_LATEST.write_text(output_json, encoding="utf-8")

# ── Print summary ─────────────────────────────────────────────────────────────

developments    = data.get("weekly_developments", [])
cap_tracker     = data.get("capability_tier_tracker", {})
reg_tracker     = data.get("regulatory_framework_tracker", {})
brief_narrative = data.get("weekly_brief_narrative", "")

cap_labs_covered = [lab for lab, v in cap_tracker.items() if isinstance(v, dict) and v.get("lead_system")]
reg_frameworks_covered = [fw for fw, v in reg_tracker.items() if isinstance(v, dict) and v.get("current_milestone") or v.get("current_status")]

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_LATEST}")
print(f"   Lead: [{lead.get('confidence_preliminary')}] {lead.get('headline','')[:70]}")
print(f"   Developments: {len(developments)}")
print(f"   Capability labs covered: {len(cap_labs_covered)} ({', '.join(cap_labs_covered)})")
print(f"   Regulatory frameworks covered: {len(reg_frameworks_covered)} ({', '.join(reg_frameworks_covered)})")
print(f"   Brief narrative: {len(brief_narrative)} chars")

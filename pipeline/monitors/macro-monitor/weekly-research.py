#!/usr/bin/env python3
"""
GMM Weekly Research — GitHub Actions script
Calls Perplexity sonar-deep-research API with the GMM weekly research prompt,
validates schema, and writes output to pipeline/monitors/macro-monitor/weekly/

Runs: Wednesday 18:00 UTC (15 hours before Thursday GMM Analyst at 09:00 UTC)

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (GitHub repository secret)
"""

import os
import json
import datetime
import pathlib
import requests
import subprocess
import base64
import sys

# ── Exchange logger (record every API call — success or failure) ──────────────
try:
    _repo_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_repo_root / "pipeline" / "shared"))
    from prompt_exchange_log import log_exchange
except ImportError:
    def log_exchange(**kw): pass  # graceful fallback

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY     = os.environ["PPLX_API_KEY"]
MODEL       = "sonar-pro"             # sonar-pro: live web search with deeper synthesis
TODAY       = datetime.date.today()
TODAY_STR   = TODAY.isoformat()

# Week ending = next Saturday (or today if Saturday)
days_to_sat = (5 - TODAY.weekday()) % 7
WEEK_ENDING = (TODAY + datetime.timedelta(days=days_to_sat)).isoformat()

OUT_DIR     = pathlib.Path("pipeline/monitors/macro-monitor/weekly")
OUT_LATEST  = OUT_DIR / "weekly-latest.json"
OUT_DATED   = OUT_DIR / f"weekly-{TODAY_STR}.json"

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Weekly research already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt ───────────────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/macro-monitor/gmm-weekly-research-api-prompt.txt"
)
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")
print(f"Prompt loaded ({len(prompt)} chars)")

# Inject current week_ending date into prompt context
prompt += f"\n\nCurrent date: {TODAY_STR}. Week ending (Saturday): {WEEK_ENDING}."


# ── Inject annual calibration from internal repo ──────────────────────────────

_calib_year = datetime.date.today().year
_calib_path = f"methodology/macro-monitor-imf-{_calib_year}.md"
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
                "\n\nANNUAL CALIBRATION "
                + str(_calib_year)
                + " — apply these rules:\n"
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
        "search_recency_filter": "month",  # weekly research — broader window than daily
        "return_citations": True,
    },
    timeout=120,
)
response.raise_for_status()

api_response = response.json()
raw_content  = api_response["choices"][0]["message"]["content"]
citations    = api_response.get("citations", [])
_tokens      = api_response.get("usage", {}).get("total_tokens")

print(f"API response received. Tokens: {_tokens if _tokens is not None else 'unknown'}")

# ── Log exchange (before any parsing — captures success AND failure) ──────────
log_exchange(
    monitor="macro-monitor", stage="weekly-research", model=MODEL,
    prompt_text=prompt, prompt_file=str(PROMPT_FILE),
    raw_response=raw_content, parsed_ok=False,
    tokens=_tokens if isinstance(_tokens, int) else None,
    citations=len(citations),
)

# ── Parse JSON output ──────────────────────────────────────────────────────────

# Robust JSON extraction
import re as _re

# ── Pipeline incident logging (engine-level) ──────────────────────────────────
try:
    _il_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_il_root / "pipeline"))
    from incident_log import log_incident
except ImportError:
    def log_incident(**kw): pass  # graceful fallback

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
    log_incident(monitor="macro-monitor", stage="weekly-research", incident_type="json_parse_error",
                 detail=f"Failed to parse JSON: {e}",
                 raw_snippet=raw_content[:500] if raw_content else "")
    print(f"ERROR: Failed to parse JSON: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    sys.exit(1)


# ── R1+R2: Source verification (ENGINE-RULES Section 13) ─────────────────────
try:
    _vr_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    import sys as _sys
    _sys.path.insert(0, str(_vr_root / "pipeline" / "tools"))
    from verify_sources import verify_item_sources, log_verification_summary, emit_verification_record
    
    # Collect all items with source_url across all finding arrays
    _all_items = []
    for _field in ["findings", "lead_signal", "domain_developments", "hybrid_threat_incidents",
                   "institutional_developments", "items", "domain_updates", "developments",
                   "threat_incidents", "weekly_findings", "standing_tracker_updates"]:
        _val = data.get(_field)
        if isinstance(_val, list):
            _all_items.extend(_val)
        elif isinstance(_val, dict) and _val.get("source_url"):
            _all_items.append(_val)
    
    if _all_items:
        _all_items, _vstats = verify_item_sources(
            _all_items,
            monitor_slug=data.get("_meta", {}).get("monitor_slug", "unknown"),
            stage="weekly-research",
            log_incident_fn=log_incident,
        )
        log_verification_summary(_vstats, "weekly-research",
                                 data.get("_meta", {}).get("monitor_slug", "unknown"))
        # Embed verification record for epistemic dashboard
        data["_verification"] = emit_verification_record(
            _all_items, _vstats,
            monitor_slug=data.get("_meta", {}).get("monitor_slug", "unknown"),
            stage="weekly-research",
            run_date=TODAY_STR,
        )
        print(f"   Source verification: {_vstats['verified']}/{_vstats['total']} verified")
except ImportError:
    print("  ⚠ verify_sources not available — skipping R1/R2 checks")
except Exception as _ve:
    print(f"  ⚠ Source verification error (non-fatal): {_ve}")

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

if not data.get("top_developments"):
    print("INFO: campaigns array is empty — no new campaigns this week (valid)")

if not data.get("asset_class_summary"):
    warnings.append("asset_class_summary is empty — actor posture data expected weekly")

if not data.get("weekly_brief_narrative"):
    errors.append("weekly_brief_narrative missing — required for Hugo brief")
elif len(data["weekly_brief_narrative"]) < 200:
    warnings.append(f"weekly_brief_narrative is very short ({len(data['weekly_brief_narrative'])} chars) — expected 400-600 words")

# Validate campaign traceback for High/Confirmed
# GMM: validate top_developments have source_urls
for i, dev in enumerate(data.get("top_developments", [])):
    if not dev.get("source_url"):
        warnings.append(f"top_developments[{i}] missing source_url")

if errors:
    log_incident(monitor="macro-monitor", stage="weekly-research", incident_type="schema_violation",
                 severity="error", detail=f"Schema validation failed: {len(errors)} error(s)",
                 errors=errors, warnings=warnings)
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
data["_meta"]["monitor_slug"] = "macro-monitor"

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

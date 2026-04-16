#!/usr/bin/env python3
"""
FIM Weekly Research — GitHub Actions script
Calls Perplexity sonar-pro API with the FIM weekly research prompt,
validates schema, and writes output to pipeline/monitors/financial-integrity/weekly/

Runs: Wednesday 15:00 UTC (scheduled by cron dispatcher)

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (GitHub repository secret)
"""

import os
import json
import datetime
import pathlib
import requests
import sys
import re

# ── Pipeline incident logging (engine-level) ──────────────────────────────────
try:
    _il_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_il_root / "pipeline"))
    from incident_log import log_incident
except ImportError:
    def log_incident(**kw): pass  # graceful fallback


# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY     = os.environ["PPLX_API_KEY"]
MODEL       = "sonar-pro"             # sonar-pro: live web search with deeper synthesis
TODAY       = datetime.date.today()
TODAY_STR   = TODAY.isoformat()

# Week ending = next Saturday (or today if Saturday)
days_to_sat = (5 - TODAY.weekday()) % 7
WEEK_ENDING = (TODAY + datetime.timedelta(days=days_to_sat)).isoformat()

OUT_DIR     = pathlib.Path("pipeline/monitors/financial-integrity/weekly")
OUT_LATEST  = OUT_DIR / "weekly-latest.json"
OUT_DATED   = OUT_DIR / f"weekly-{TODAY_STR}.json"

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Weekly research already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt ───────────────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/financial-integrity/fim-weekly-research-api-prompt.txt"
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
        "search_recency_filter": "month",  # weekly research — broader window than daily
        "return_citations": True,
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
clean = raw_content.strip()
fence_match = re.search(r'''```(?:json)?\s*(\{.*?\})\s*```''', clean, re.DOTALL)
if fence_match:
    clean = fence_match.group(1).strip()
elif clean.startswith("```"):
    clean = re.sub(r'^```(?:json)?\s*', '', clean)
    clean = re.sub(r'\s*```$', '', clean).strip()
if not clean.startswith('{'):
    brace = clean.find('{')
    if brace != -1: clean = clean[brace:]
if not clean.endswith('}'):
    brace = clean.rfind('}')
    if brace != -1: clean = clean[:brace+1]

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    log_incident(monitor="financial-integrity", stage="weekly-research", incident_type="json_parse_error",
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
REQUIRED_LEAD = ["headline", "confidence_preliminary", "domain", "pillar"]

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
            warnings.append("lead_signal.source_url missing — model did not return a primary URL")
        else:
            errors.append(f"lead_signal.{field} missing or empty")

# Validate domain_updates
domain_updates = data.get("domain_updates", [])
if not domain_updates:
    errors.append("domain_updates is empty — minimum coverage requires D1-D5 findings")
else:
    domains_found = set()
    for i, du in enumerate(domain_updates):
        d = du.get("domain", "")
        domains_found.add(d)
        if not du.get("title"):
            warnings.append(f"domain_updates[{i}] missing title")
        if not du.get("source_url"):
            warnings.append(f"domain_updates[{i}] missing source_url")
    missing_domains = {"D1", "D2", "D3", "D4", "D5"} - domains_found
    if missing_domains:
        warnings.append(f"Domains with no findings: {', '.join(sorted(missing_domains))}")

# Validate standing trackers
trackers = data.get("standing_tracker_updates", [])
if not trackers:
    errors.append("standing_tracker_updates is empty — all 5 trackers must be updated")
elif len(trackers) < 5:
    warnings.append(f"Only {len(trackers)} standing trackers updated — expected 5")

# Validate narrative
if not data.get("weekly_brief_narrative"):
    errors.append("weekly_brief_narrative missing — required for Hugo brief")
elif len(data["weekly_brief_narrative"]) < 200:
    warnings.append(f"weekly_brief_narrative is very short ({len(data['weekly_brief_narrative'])} chars) — expected 400-600 words")

# Validate jurisdiction risk movements
if not data.get("jurisdiction_risk_movements"):
    warnings.append("jurisdiction_risk_movements is empty — expected at least one")

# Validate research coverage
coverage = data.get("research_coverage", {})
if not coverage:
    warnings.append("research_coverage section missing")

if errors:
    log_incident(monitor="financial-integrity", stage="weekly-research", incident_type="schema_violation",
                 severity="error", detail=f"Schema validation failed: {len(errors)} error(s)",
                 errors=errors, warnings=warnings)
    print(f"SCHEMA VALIDATION FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  ✗ {e}")
    if warnings:
        for w in warnings:
            print(f"  ⚠ {w}")
    print(f"\nStructure received: {list(data.keys())}")
    print(f"_meta keys: {list(data.get('_meta',{}).keys())}")
    print(f"lead_signal keys: {list(data.get('lead_signal',{}).keys())}")
    print(f"domain_updates count: {len(domain_updates)}")
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
data["_meta"]["monitor_slug"] = "financial-integrity"

# ── Write output ──────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_json = json.dumps(data, indent=2, ensure_ascii=False)

OUT_DATED.write_text(output_json, encoding="utf-8")
OUT_LATEST.write_text(output_json, encoding="utf-8")

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_LATEST}")
print(f"   Lead: [{lead.get('confidence_preliminary')}] {lead.get('headline','')[:70]}")
print(f"   Domain updates: {len(domain_updates)}")
print(f"   Standing trackers: {len(trackers)}")
print(f"   Jurisdiction movements: {len(data.get('jurisdiction_risk_movements', []))}")
print(f"   Cross-monitor signals: {bool(data.get('cross_monitor_signals'))}")
print(f"   Brief narrative: {len(data.get('weekly_brief_narrative',''))} chars")

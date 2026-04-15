#!/usr/bin/env python3
"""
FIM Collector — GitHub Actions script
Calls Perplexity API with the FIM Collector prompt,
validates Tier 0 schema, and writes output to pipeline/.

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (set as GitHub repository secret)
"""

import os
import json
import datetime
import pathlib
import requests
import sys

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar"                    # fast daily search
TODAY     = datetime.date.today()
TODAY_STR = TODAY.isoformat()
DOW       = TODAY.weekday()            # 0=Mon, 6=Sun
OUT_DIR   = pathlib.Path("pipeline/monitors/financial-integrity/daily")
OUT_DAILY = OUT_DIR / "daily-latest.json"
OUT_DATED = OUT_DIR / f"verified-{TODAY_STR}.json"

# ── Tier C+D rotation schedule ────────────────────────────────────────────────
# Tier C: EU/FATF, Cayman/BVI, Panama/Cyprus, Jersey/Guernsey/IoM
# Tier D: Central Asia, Kenya/East Africa, DRC/Great Lakes, Nigeria/West Africa, Myanmar

TIER_CD_ROTATION = {
    0: "Tier C: EU (AMLA, 6AMLD), FATF (grey list, plenary). Tier D: Central Asia (Kazakhstan, Uzbekistan, Kyrgyzstan — Russian sanctions rerouting).",
    1: "Tier C: Cayman Islands (fund structures, BO registry), British Virgin Islands (corporate opacity). Tier D: Kenya / East Africa (TBML, mobile money, Al-Shabaab financing).",
    2: "Tier C: Panama (Colon FTZ, TBML, corporate vehicles), Cyprus (golden passport legacy, Russian structures). Tier D: DRC / Great Lakes (conflict minerals, extractive corruption).",
    3: "Tier C: Jersey, Guernsey, Isle of Man (trust structures, UK interface). Tier D: Nigeria / West Africa (fraud networks, oil corruption, Boko Haram/ISWAP financing).",
    4: "Tier C: EU (AMLA, 6AMLD), FATF (grey list, plenary). Tier D: Myanmar (sanctions evasion, jade trade, military junta financing, meth-trade laundering).",
    5: "Tier C: Cayman Islands, British Virgin Islands. Tier D: Central Asia (Kazakhstan, Uzbekistan, Kyrgyzstan).",
    6: "Tier C: Panama, Cyprus. Tier D: Kenya / East Africa (TBML, mobile money integrity).",
}

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Collector already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt from repo ─────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/financial-integrity/fim-collector-api-prompt.txt"
)
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")

# Inject today's Tier C+D rotation
tier_cd_today = TIER_CD_ROTATION.get(DOW, "Tier C: EU, FATF. Tier D: Central Asia.")
prompt = prompt.replace("{tier_cd_today}", tier_cd_today)

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling Perplexity API ({MODEL}) for FIM Collector ({TODAY_STR})...")
print(f"Tier C+D rotation today ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][DOW]}): {tier_cd_today[:80]}...")

MAX_RETRIES = 3
raw_content = None
citations = []

for attempt in range(1, MAX_RETRIES + 1):
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":    MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            timeout=120,
        )
        response.raise_for_status()
        api_response  = response.json()
        raw_content   = api_response["choices"][0]["message"]["content"]
        citations     = api_response.get("citations", [])
        print(f"API response received (attempt {attempt}). Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

        # Check for empty or non-JSON response
        if not raw_content or not raw_content.strip():
            print(f"WARNING: Empty response on attempt {attempt}")
            raw_content = None
            continue
        if raw_content.strip()[0] not in ('{', '[', '`'):
            print(f"WARNING: Response doesn't look like JSON (attempt {attempt}): {raw_content[:100]}")
            raw_content = None
            continue
        break  # success

    except (requests.RequestException, KeyError) as e:
        print(f"WARNING: API call failed on attempt {attempt}/{MAX_RETRIES}: {e}")
        if attempt < MAX_RETRIES:
            import time; time.sleep(attempt * 10)
        continue

if raw_content is None:
    print("ERROR: All API attempts failed or returned empty/invalid response.")
    sys.exit(1)

# ── Parse JSON output ──────────────────────────────────────────────────────────

# Strip markdown code fences if model wrapped the JSON despite instructions
clean = raw_content.strip()
if clean.startswith("```"):
    # split on first fence: ["", "json\n{...}\n", ""] — take index 1, not -1
    parts = clean.split("```")
    inner = parts[1] if len(parts) > 1 else clean
    inner = inner.strip()
    if inner.startswith("json"):
        inner = inner[4:].strip()
    clean = inner.rsplit("```", 1)[0].strip()  # remove any trailing fence

# Fallback: extract outermost { } in case of surrounding prose
if not clean.startswith('{'):
    brace = clean.find('{')
    if brace != -1:
        clean = clean[brace:]
if not clean.endswith('}'):
    brace = clean.rfind('}')
    if brace != -1:
        clean = clean[:brace + 1]

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON output: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    print(f"Raw output saved for debugging.")
    sys.exit(1)

# ── Validate Tier 0 schema ────────────────────────────────────────────────────

REQUIRED_META = [
    "schema_version", "monitor_slug", "job_type", "generated_at",
    "data_date", "finding_count", "status"
]
REQUIRED_FINDING = [
    "finding_id", "dedupe_key", "title", "summary", "source_url",
    "source_tier", "confidence_preliminary", "confidence_basis",
    "research_traceback", "campaign_status_candidate",
    "episodic_flag", "needs_weekly_review",
    "jurisdiction", "domain", "pillar"
]

errors   = []
warnings = []

meta = data.get("_meta", {})
for field in REQUIRED_META:
    if field not in meta:
        errors.append(f"_meta.{field} missing")

if meta.get("schema_version") != "tier0-v1.0":
    errors.append(f"schema_version is '{meta.get('schema_version')}' — expected 'tier0-v1.0'")

if meta.get("monitor_slug") != "financial-integrity":
    errors.append(f"monitor_slug is '{meta.get('monitor_slug')}' — expected 'financial-integrity'")

# Validate data_date matches today
if meta.get("data_date") != TODAY_STR:
    warnings.append(f"data_date is '{meta.get('data_date')}' — expected '{TODAY_STR}'")
    data["_meta"]["data_date"] = TODAY_STR  # auto-correct

findings = data.get("findings", [])
for i, finding in enumerate(findings):
    for field in REQUIRED_FINDING:
        if field not in finding:
            errors.append(f"findings[{i}].{field} missing (id: {finding.get('finding_id', '?')})")

    # Validate domain field
    valid_domains = {"D1", "D2", "D3", "D4", "D5"}
    if finding.get("domain") and finding["domain"] not in valid_domains:
        warnings.append(f"findings[{i}] has domain '{finding['domain']}' — expected one of {valid_domains}")

    # Validate pillar field
    valid_pillars = {"AML", "CTF", "CPF", "multiple"}
    if finding.get("pillar") and finding["pillar"] not in valid_pillars:
        warnings.append(f"findings[{i}] has pillar '{finding['pillar']}' — expected one of {valid_pillars}")

    # High/Confirmed with only 1 source: auto-downgrade to Assessed
    conf = finding.get("confidence_preliminary", "")
    if conf in ("High", "Confirmed"):
        sources = finding.get("research_traceback", {}).get("sources_cited", [])
        if len(sources) < 2:
            old_conf = conf
            finding["confidence_preliminary"] = "Assessed"
            finding["confidence_basis"] = (
                f"[AUTO-DOWNGRADED from {old_conf}: single source at Tier 0 — "
                f"Analyst cron to verify] " + finding.get("confidence_basis", "")
            )
            warnings.append(
                f"findings[{i}] ({finding.get('finding_id', '?')}) auto-downgraded "
                f"{old_conf} → Assessed (1 source; 2+ needed for {old_conf})"
            )

    # episodic_flag=true must have episodic_reason
    if finding.get("episodic_flag") and not finding.get("episodic_reason"):
        warnings.append(
            f"findings[{i}] ({finding.get('finding_id', '?')}) has "
            f"episodic_flag=true but no episodic_reason"
        )

if errors:
    print(f"SCHEMA VALIDATION FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  ✗ {e}")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    sys.exit(1)

if warnings:
    print(f"Warnings ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠ {w}")

# ── Inject citations from API response into source URLs if not already present ─

for finding in findings:
    if not finding.get("source_url") and citations:
        finding["source_url"] = citations[0]

# ── Ensure _meta counts match actual arrays ───────────────────────────────────

data["_meta"]["finding_count"]        = len(findings)
data["_meta"]["net_new_count"]        = sum(1 for f in findings if f.get("campaign_status_candidate") == "net_new")
data["_meta"]["continuation_count"]   = sum(1 for f in findings if f.get("campaign_status_candidate") == "continuation")
data["_meta"]["below_threshold_count"] = len(data.get("below_threshold", []))

# ── Write output files ─────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)

output_json = json.dumps(data, indent=2, ensure_ascii=False)

OUT_DATED.write_text(output_json, encoding="utf-8")
OUT_DAILY.write_text(output_json, encoding="utf-8")

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_DAILY}")
print(f"   Findings: {data['_meta']['finding_count']} "
      f"({data['_meta']['net_new_count']} net new, "
      f"{data['_meta']['continuation_count']} continuations, "
      f"{data['_meta']['below_threshold_count']} below threshold)")

# Print jurisdiction coverage summary
for finding in findings[:5]:
    j = finding.get("jurisdiction", "?")
    d = finding.get("domain", "?")
    p = finding.get("pillar", "?")
    t = finding.get("title", "")[:60]
    print(f"   [{j}/{d}/{p}] {t}")

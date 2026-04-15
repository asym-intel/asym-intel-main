#!/usr/bin/env python3
"""
ESA Collector — GitHub Actions script
Calls Perplexity API with the ESA Collector prompt,
validates Tier 0 schema, and writes output to pipeline/.

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (set as GitHub repository secret)
  GITHUB_TOKEN  — automatically injected by GitHub Actions
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

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar"                    # fast daily search; upgrade to sonar-pro for depth
TODAY     = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/european-strategic-autonomy/daily")
OUT_DAILY = OUT_DIR / "daily-latest.json"
OUT_DATED = OUT_DIR / f"verified-{TODAY}.json"

# ── Guard: skip if today's file already exists ────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Collector already ran today. Exiting.")
    sys.exit(0)

# ── Load prompt from repo ─────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(
    "pipeline/monitors/european-strategic-autonomy/esa-collector-api-prompt.txt"
)
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")


# ── Inject annual calibration from internal repo ──────────────────────────────

_calib_year = datetime.date.today().year
_calib_path = f"methodology/european-strategic-autonomy-eeas-{_calib_year}.md"
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

print(f"Calling Perplexity API ({MODEL}) for {TODAY}...")

# ── API call with retry ────────────────────────────────────────────────────────

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
    # Write raw output for debugging
    debug_path = OUT_DIR / f"debug-{TODAY}.txt"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    debug_path.write_text(raw_content, encoding="utf-8")
    print(f"Raw output saved to {debug_path} for debugging.")
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
    "episodic_flag", "needs_weekly_review"
]

errors   = []
warnings = []

meta = data.get("_meta", {})
for field in REQUIRED_META:
    if field not in meta:
        errors.append(f"_meta.{field} missing")

if meta.get("schema_version") != "tier0-v1.0":
    errors.append(f"schema_version is '{meta.get('schema_version')}' — expected 'tier0-v1.0'")

if meta.get("monitor_slug") != "european-strategic-autonomy":
    errors.append(f"monitor_slug is '{meta.get('monitor_slug')}' — expected 'european-strategic-autonomy'")

# Validate data_date matches today
if meta.get("data_date") != TODAY:
    warnings.append(f"data_date is '{meta.get('data_date')}' — expected '{TODAY}'")
    data["_meta"]["data_date"] = TODAY  # auto-correct

findings = data.get("findings", [])
for i, finding in enumerate(findings):
    for field in REQUIRED_FINDING:
        if field not in finding:
            errors.append(f"findings[{i}].{field} missing (id: {finding.get('finding_id', '?')})")

    # High/Confirmed with only 1 source: auto-downgrade to Assessed (Tier 0 tolerance)
    # Daily collector captures signal; Analyst cron applies publication-grade rigour.
    conf = finding.get("confidence_preliminary", "")
    if conf in ("High", "Confirmed"):
        sources = finding.get("research_traceback", {}).get("sources_cited", [])
        if len(sources) < 2:
            old_conf = conf
            finding["confidence_preliminary"] = "Assessed"
            finding["confidence_basis"] = (
                f"[AUTO-DOWNGRADED from {old_conf}: single source at Tier 0 — "                f"Analyst cron to verify] " + finding.get("confidence_basis", "")
            )
            warnings.append(
                f"findings[{i}] ({finding.get('finding_id', '?')}) auto-downgraded "                f"{old_conf} → Assessed (1 source; 2+ needed for {old_conf})"            )

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
    # Write raw + parsed for debugging
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY}.json").write_text(
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
        finding["source_url"] = citations[0]  # fallback to first citation

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

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

Feeds all three as context to sonar-pro for capability and governance
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/ai-governance/reasoner/reasoner-latest.json
  pipeline/monitors/ai-governance/reasoner/reasoner-YYYY-MM-DD.json

The AGM Analyst reads this at Step 0E before applying methodology.

sonar-pro is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
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

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-pro"
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

# Truncate if too large (sonar-pro has context limits)
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


# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/agm-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — reasoning without identity context")

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/ai-governance/agm-reasoner-api-prompt.txt")
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
print(f"Prompt loaded ({len(_raw_prompt)} chars)")

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for capability-governance reasoning...")
print(f"Context size: {len(context_json)} chars")

# ── API call with retry ────────────────────────────────────────────────────────

MAX_RETRIES = 3
raw_content = None

for attempt in range(1, MAX_RETRIES + 1):
    try:
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
        print(f"Response received (attempt {attempt}). Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

        if not raw_content or not raw_content.strip():
            print(f"WARNING: Empty response on attempt {attempt}")
            raw_content = None
            continue
        if raw_content.strip()[0] not in ('{', '[', '`'):
            print(f"WARNING: Response doesn't look like JSON (attempt {attempt}): {raw_content[:100]}")
            raw_content = None
            continue
        break

    except (requests.RequestException, KeyError) as e:
        print(f"WARNING: API call failed on attempt {attempt}/{MAX_RETRIES}: {e}")
        if attempt < MAX_RETRIES:
            import time; time.sleep(attempt * 10)
        continue

if raw_content is None:
    print("ERROR: All API attempts failed or returned empty/invalid response.")
    sys.exit(1)

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
    log_incident(monitor="ai-governance", stage="reasoner", incident_type="json_parse_error",
                 detail=f"Failed to parse JSON: {e}",
                 raw_snippet=raw_content[:500] if raw_content else "")
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
    log_incident(monitor="ai-governance", stage="reasoner", incident_type="schema_violation",
                 severity="error", detail=f"Validation failed: {len(errors)} error(s)",
                 errors=errors)
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

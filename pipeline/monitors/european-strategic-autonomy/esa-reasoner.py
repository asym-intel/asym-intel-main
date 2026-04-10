#!/usr/bin/env python3
"""
ESA Reasoner — Domain Autonomy & Hybrid Threat Analysis
GitHub Actions script. Runs Tuesday 20:00 UTC.

Loads:
  - static/monitors/european-strategic-autonomy/data/persistent-state.json
      (active domain scores + hybrid threat registry)
  - pipeline/monitors/european-strategic-autonomy/weekly/weekly-latest.json
      (domain_developments + hybrid_threat_incidents from this week's deep research)
  - pipeline/monitors/european-strategic-autonomy/daily/daily-latest.json
      (most recent Collector findings array)

Feeds all three as context to sonar-pro for domain autonomy
reasoning and hybrid threat pattern analysis. Outputs structured analytical
recommendations to:
  pipeline/monitors/european-strategic-autonomy/reasoner/reasoner-latest.json
  pipeline/monitors/european-strategic-autonomy/reasoner/reasoner-YYYY-MM-DD.json

The ESA Analyst reads this at Step 0E before applying methodology.

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

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-pro"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/european-strategic-autonomy/reasoner")
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

persistent = load_json_file(
    "static/monitors/european-strategic-autonomy/data/persistent-state.json",
    "persistent-state"
)
weekly     = load_json_file(
    "pipeline/monitors/european-strategic-autonomy/weekly/weekly-latest.json",
    "weekly research"
)
daily      = load_json_file(
    "pipeline/monitors/european-strategic-autonomy/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for domain autonomy reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: active domain scores + hybrid threat registry
active_domain_scores   = persistent.get("domain_scores", {})
hybrid_threat_registry = persistent.get("hybrid_threat_registry", [])[-20:]  # last 20 entries
actor_posture_log      = persistent.get("actor_posture_log", [])[-10:]

# From weekly research: domain_developments + hybrid_threat_incidents
weekly_domain_devs    = weekly.get("domain_developments", []) if weekly else []
weekly_hybrid_threats = weekly.get("hybrid_threat_incidents", []) if weekly else []
weekly_us_eu          = weekly.get("us_eu_tracker", {}) if weekly else {}

# From daily Collector: findings array
daily_findings = daily.get("findings", []) if daily else []

print(f"Loaded: {len(active_domain_scores)} domain scores, "
      f"{len(hybrid_threat_registry)} threat registry entries")
print(f"Weekly research: {len(weekly_domain_devs)} domain developments, "
      f"{len(weekly_hybrid_threats)} hybrid threat incidents")
print(f"Daily Collector: {len(daily_findings)} findings")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "active_domain_scores":    active_domain_scores,
    "hybrid_threat_registry":  hybrid_threat_registry,
    "actor_posture_log":       actor_posture_log,
    "weekly_domain_developments": weekly_domain_devs,
    "weekly_hybrid_threat_incidents": weekly_hybrid_threats,
    "weekly_us_eu_tracker":    weekly_us_eu,
    "daily_collector_findings": daily_findings,
}, indent=2)

# Truncate if too large (sonar-pro has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: domain scores > threat registry > weekly > daily
    context_json = json.dumps({
        "active_domain_scores":    active_domain_scores,
        "hybrid_threat_registry":  hybrid_threat_registry[-10:],
        "weekly_domain_developments": weekly_domain_devs[:15],
        "weekly_hybrid_threat_incidents": weekly_hybrid_threats[:10],
        "weekly_us_eu_tracker":    weekly_us_eu,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]


# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/esa-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — reasoning without identity context")

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/european-strategic-autonomy/esa-reasoner-api-prompt.txt")
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

print(f"Calling {MODEL} for domain autonomy reasoning...")
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
if meta.get("monitor_slug") != "european-strategic-autonomy":
    errors.append(f"monitor_slug '{meta.get('monitor_slug')}' — expected 'european-strategic-autonomy'")
if not data.get("domain_score_reviews"):
    errors.append("domain_score_reviews missing — required for analyst methodology")
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

score_reviews = data.get("domain_score_reviews", [])
threat_pats   = data.get("threat_pattern_detections", [])
flags         = data.get("cross_monitor_escalation_flags", [])
contested     = data.get("contested_findings", [])
posture       = data.get("actor_posture_changes", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Domain score reviews: {len(score_reviews)} "
      f"({sum(1 for r in score_reviews if r.get('recommendation') != 'hold')} changes recommended)")
print(f"   Threat pattern detections: {len(threat_pats)} "
      f"({sum(1 for t in threat_pats if t.get('match_type') == 'net_new')} net new)")
print(f"   Actor posture changes: {len(posture)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

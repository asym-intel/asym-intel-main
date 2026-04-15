#!/usr/bin/env python3
"""
FIM Reasoner — Financial Integrity Architecture & Risk Analysis
GitHub Actions script. Runs Saturday 09:00 UTC.

Loads:
  - persistent-state.json (jurisdiction baselines, scheme inventory,
    enforcement gap history, regulatory horizon, CTF/CPF flags)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector findings)

Feeds all three as context to sonar-deep-research for financial integrity
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/financial-integrity/reasoner/reasoner-latest.json
  pipeline/monitors/financial-integrity/reasoner/reasoner-YYYY-MM-DD.json

The FIM Synthesiser reads this at Step 0E before applying methodology.

sonar-pro is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.

Environment variables required:
  PPLX_API_KEY  — Perplexity API key (GitHub repository secret)
  GH_TOKEN      — GitHub PAT for internal repo access (identity card)
"""

import os
import json
import datetime
import datetime as _dt
import pathlib
import requests
import sys
import re

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-pro"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/financial-integrity/reasoner")
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
    "static/monitors/financial-integrity/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/financial-integrity/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/financial-integrity/daily/daily-latest.json",
    "daily Collector"
)

# FIM can run without persistent-state on first cycle — weekly research is minimum
if not weekly and not daily:
    print("ERROR: Neither weekly research nor daily Collector data available. Cannot reason.")
    sys.exit(1)

if not persistent:
    print("NOTE: persistent-state.json not found — first cycle. Reasoning with weekly + daily only.")

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: jurisdiction baselines, scheme inventory, enforcement gaps
jurisdiction_baselines = persistent.get("jurisdiction_baselines", []) if persistent else []
scheme_inventory       = persistent.get("scheme_inventory", []) if persistent else []
enforcement_gap_log    = persistent.get("enforcement_gap_log", []) if persistent else []
regulatory_horizon     = persistent.get("regulatory_horizon", []) if persistent else []
ctf_cpf_flags          = persistent.get("ctf_cpf_flags", []) if persistent else []
cross_monitor_flags    = persistent.get("cross_monitor_flags", {}) if persistent else {}

# From weekly research: lead signal, domain updates, standing trackers, jurisdiction movements
weekly_lead_signal     = weekly.get("lead_signal", {}) if weekly else {}
weekly_domain_updates  = weekly.get("domain_updates", []) if weekly else []
weekly_trackers        = weekly.get("standing_tracker_updates", []) if weekly else []
weekly_jurisdiction    = weekly.get("jurisdiction_risk_movements", []) if weekly else []
weekly_cross_signals   = weekly.get("cross_monitor_signals", {}) if weekly else {}
weekly_tooling         = weekly.get("tooling_signals", {}) if weekly else {}

# From daily Collector: latest jurisdiction-level findings
daily_findings         = daily.get("findings", []) if daily else []
daily_below            = daily.get("below_threshold", []) if daily else []

print(f"Loaded: {len(jurisdiction_baselines)} jurisdiction baselines, "
      f"{len(scheme_inventory)} scheme inventory entries")
print(f"Weekly research: {len(weekly_domain_updates)} domain updates, "
      f"{len(weekly_trackers)} trackers, {len(weekly_jurisdiction)} jurisdiction movements")
print(f"Daily Collector: {len(daily_findings)} findings, "
      f"{len(daily_below)} below threshold")

# ── Build the reasoning context ──────────────────────────────────────────────

context_json = json.dumps({
    "jurisdiction_baselines": jurisdiction_baselines,
    "scheme_inventory": scheme_inventory,
    "enforcement_gap_log": enforcement_gap_log,
    "regulatory_horizon": regulatory_horizon,
    "ctf_cpf_flags": ctf_cpf_flags,
    "cross_monitor_flags": cross_monitor_flags,
    "weekly_lead_signal": weekly_lead_signal,
    "weekly_domain_updates": weekly_domain_updates,
    "weekly_standing_trackers": weekly_trackers,
    "weekly_jurisdiction_movements": weekly_jurisdiction,
    "weekly_cross_monitor_signals": weekly_cross_signals,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below
}, indent=2)

# Truncate if too large (sonar-pro has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: baselines + weekly > daily
    context_json = json.dumps({
        "jurisdiction_baselines": jurisdiction_baselines,
        "scheme_inventory": scheme_inventory,
        "enforcement_gap_log": enforcement_gap_log[-10:],
        "regulatory_horizon": regulatory_horizon,
        "ctf_cpf_flags": ctf_cpf_flags,
        "weekly_lead_signal": weekly_lead_signal,
        "weekly_domain_updates": weekly_domain_updates[:8],
        "weekly_standing_trackers": weekly_trackers,
        "weekly_jurisdiction_movements": weekly_jurisdiction[:10],
        "daily_collector_findings": daily_findings[:5]
    }, indent=2)[:MAX_CONTEXT]


# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/fim-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — reasoning without identity context")

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/financial-integrity/fim-reasoner-api-prompt.txt")
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
prompt = prompt.replace('{generated_at}', _dt.datetime.now(_dt.timezone.utc).isoformat())
prompt = prompt.replace('{data_date}', TODAY_STR)
print(f"Prompt loaded ({len(_raw_prompt)} chars)")

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for financial integrity reasoning...")
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
warnings = []
meta = data.get("_meta", {})
if meta.get("schema_version") != "reasoner-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'reasoner-v1.0'")
if not data.get("analyst_briefing"):
    errors.append("analyst_briefing missing")

# Validate domain assessments
domain_assessments = data.get("domain_assessments", [])
if not domain_assessments:
    errors.append("domain_assessments is empty — all 5 domains must be assessed")
elif len(domain_assessments) < 5:
    warnings.append(f"Only {len(domain_assessments)} domain assessments — expected 5")

# Validate jurisdiction risk assessments
jra = data.get("jurisdiction_risk_assessments", [])
if not jra:
    warnings.append("jurisdiction_risk_assessments is empty")

# Validate standing tracker synthesis
sts = data.get("standing_tracker_synthesis", [])
if not sts:
    errors.append("standing_tracker_synthesis is empty — all 5 trackers must be synthesised")
elif len(sts) < 5:
    warnings.append(f"Only {len(sts)} tracker syntheses — expected 5")

# Validate tooling outputs
tooling = data.get("tooling_outputs", {})
if not tooling:
    warnings.append("tooling_outputs section missing — needed for compliance tooling layer")

if errors:
    print(f"VALIDATION FAILED: {errors}")
    for w in warnings:
        print(f"  ⚠ {w}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    sys.exit(1)

for w in warnings:
    print(f"  ⚠ {w}")

# ── Write ──────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output, encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

domain_assessments  = data.get("domain_assessments", [])
jurisdiction_risks  = data.get("jurisdiction_risk_assessments", [])
tracker_synthesis   = data.get("standing_tracker_synthesis", [])
severity_reviews    = data.get("severity_reviews", [])
cross_flags         = data.get("cross_monitor_flags", [])
filter_reviews      = data.get("filter_review", [])
tooling_out         = data.get("tooling_outputs", {})

print(f"✅ Written: {OUT_DATED}")
print(f"   Domain assessments: {len(domain_assessments)}")
print(f"   Jurisdiction risk assessments: {len(jurisdiction_risks)}")
print(f"   Tracker syntheses: {len(tracker_synthesis)}")
print(f"   Severity reviews: {len(severity_reviews)}")
print(f"   Cross-monitor flags: {len(cross_flags)}")
print(f"   Filter reviews: {len(filter_reviews)}")
print(f"   Tooling outputs: {list(tooling_out.keys())}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

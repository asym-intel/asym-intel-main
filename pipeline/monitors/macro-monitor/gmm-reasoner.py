#!/usr/bin/env python3
"""
GMM Reasoner — Macro Regime & Stress Pattern Analysis
GitHub Actions script. Runs Monday 18:00 UTC.

Loads:
  - persistent-state.json (conviction history, asset class baselines,
    tactical alerts, blind spot overrides, tariff escalation protocol)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector findings)

Feeds all three as context to sonar-pro for macro regime
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/macro-monitor/reasoner/reasoner-latest.json
  pipeline/monitors/macro-monitor/reasoner/reasoner-YYYY-MM-DD.json

The GMM Synthesiser reads this at Step 0E before applying methodology.

sonar-pro is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
"""

import os
import json
import datetime
import datetime as _dt
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
OUT_DIR   = pathlib.Path("pipeline/monitors/macro-monitor/reasoner")
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
    "static/monitors/macro-monitor/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/macro-monitor/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/macro-monitor/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for macro regime reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: conviction history, asset baselines, structural indicators
conviction_history    = persistent.get("conviction_history", [])
asset_class_baseline  = persistent.get("asset_class_baseline", [])
tactical_alerts       = persistent.get("active_tactical_alerts", [])
blind_spot_overrides  = persistent.get("blind_spot_overrides", [])
tariff_protocol       = persistent.get("tariff_escalation_protocol", {})
oil_shock_driver      = persistent.get("oil_supply_shock_driver", {})
calibration_log       = persistent.get("calibration_log", [])
us_decoupling         = persistent.get("us_decoupling_index", {})
ai_capex_watch        = persistent.get("ai_capex_watch", {})

# From weekly research: lead signal, regime assessment, asset class summary
weekly_lead_signal    = weekly.get("lead_signal", {}) if weekly else {}
weekly_developments   = weekly.get("top_developments", []) if weekly else []
weekly_tariff         = weekly.get("tariff_escalation", {}) if weekly else {}
weekly_asset_summary  = weekly.get("asset_class_summary", {}) if weekly else {}
weekly_regime         = weekly.get("regime_assessment", {}) if weekly else {}
weekly_cross_signals  = weekly.get("cross_monitor_signals", {}) if weekly else {}

# From daily Collector: latest indicator findings
daily_findings        = daily.get("findings", []) if daily else []
daily_below           = daily.get("below_threshold", []) if daily else []
daily_tariff_status   = daily.get("tariff_escalation_status", {}) if daily else {}

print(f"Loaded: {len(conviction_history)} conviction history entries, "
      f"{len(asset_class_baseline)} asset class baselines")
print(f"Weekly research: {len(weekly_developments)} top developments, "
      f"regime={weekly_regime.get('current_regime', 'N/A')}")
print(f"Daily Collector: {len(daily_findings)} findings, "
      f"{len(daily_below)} below threshold")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "conviction_history": conviction_history,
    "asset_class_baseline": asset_class_baseline,
    "active_tactical_alerts": tactical_alerts,
    "blind_spot_overrides": blind_spot_overrides,
    "tariff_escalation_protocol": tariff_protocol,
    "oil_supply_shock_driver": oil_shock_driver,
    "us_decoupling_index": us_decoupling,
    "ai_capex_watch": ai_capex_watch,
    "calibration_log": calibration_log,
    "weekly_lead_signal": weekly_lead_signal,
    "weekly_top_developments": weekly_developments,
    "weekly_tariff_escalation": weekly_tariff,
    "weekly_asset_class_summary": weekly_asset_summary,
    "weekly_regime_assessment": weekly_regime,
    "weekly_cross_monitor_signals": weekly_cross_signals,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below,
    "daily_tariff_status": daily_tariff_status
}, indent=2)

# Truncate if too large (sonar-pro has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: conviction + baselines > weekly > daily
    context_json = json.dumps({
        "conviction_history": conviction_history[-5:],
        "asset_class_baseline": asset_class_baseline,
        "active_tactical_alerts": tactical_alerts,
        "blind_spot_overrides": blind_spot_overrides,
        "tariff_escalation_protocol": tariff_protocol,
        "weekly_lead_signal": weekly_lead_signal,
        "weekly_top_developments": weekly_developments[:3],
        "weekly_regime_assessment": weekly_regime,
        "daily_collector_findings": daily_findings[:5]
    }, indent=2)[:MAX_CONTEXT]


# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/gmm-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — reasoning without identity context")

# ── Load reasoning prompt ──────────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/macro-monitor/gmm-reasoner-api-prompt.txt")
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

print(f"Calling {MODEL} for macro regime reasoning...")
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
    log_incident(monitor="macro-monitor", stage="reasoner", incident_type="json_parse_error",
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
if not data.get("analyst_briefing"):
    errors.append("analyst_briefing missing")

if errors:
    log_incident(monitor="macro-monitor", stage="reasoner", incident_type="schema_violation",
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

regime_reviews     = data.get("regime_assessment_review", {})
asset_reviews      = data.get("asset_class_reviews", [])
indicator_reviews  = data.get("indicator_pattern_analysis", [])
tail_risk_reviews  = data.get("tail_risk_assessment", [])
cross_flags        = data.get("cross_monitor_flags", [])
blind_spot_checks  = data.get("blind_spot_audit", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Asset class reviews: {len(asset_reviews)}")
print(f"   Indicator pattern analyses: {len(indicator_reviews)}")
print(f"   Tail risks assessed: {len(tail_risk_reviews)}")
print(f"   Cross-monitor flags: {len(cross_flags)}")
print(f"   Blind spot checks: {len(blind_spot_checks)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

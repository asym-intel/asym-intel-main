#!/usr/bin/env python3
"""
FIMI & Cognitive Warfare Monitor Synthesiser
Monitor slug : fimi-cognitive-warfare
Model       : sonar-deep-research (no web search — reasons over supplied docs)
Output      : pipeline/monitors/fimi-cognitive-warfare/synthesised/synthesis-latest.json
"""

import os
import json
import datetime
import pathlib
import requests
import sys
import re

# Shared repair utilities
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from synth_utils import parse_llm_json

# ── Pipeline incident logging (engine-level) ──────────────────────────────────
try:
    _il_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_il_root / "pipeline"))
    from incident_log import log_incident
except ImportError:
    def log_incident(**kw): pass  # graceful fallback

# ── Token Intensity Monitor ──────────────────────────────────────────────────
try:
    sys.path.insert(0, str(pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))))
    from pipeline.shared.Token_Intensity_Monitor import monitor_metabolic_load as _tim_monitor
    _TIM_AVAILABLE = True
except ImportError:
    _TIM_AVAILABLE = False
    def _tim_monitor(*a, **kw): return {}  # graceful fallback


# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL   = os.environ.get("SYNTH_MODEL") or "sonar-deep-research"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/fimi-cognitive-warfare/synthesised")
OUT_LATEST = OUT_DIR / "synthesis-latest.json"
OUT_DATED  = OUT_DIR / f"synthesis-{TODAY_STR}.json"
PROMPT_PATH = pathlib.Path(__file__).with_name("fcw-synthesiser-api-prompt.txt")

# ── Guard ──────────────────────────────────────────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: Synthesiser already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

# ── Load prompt template ───────────────────────────────────────────────────────

if not PROMPT_PATH.exists():
    print(f"ERROR: Prompt not found at {PROMPT_PATH}. Cannot continue.")
    sys.exit(1)

PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")

# ── Load identity card (analytical quality standard) ──────────────────────────

IDENTITY_FILE = pathlib.Path("docs/identity/fcw-identity.md")
identity_content = ""
if IDENTITY_FILE.exists():
    identity_content = IDENTITY_FILE.read_text(encoding="utf-8")
    print(f"Identity card loaded ({len(identity_content)} chars)")
else:
    print("NOTE: Identity card not available — synthesising without identity context")

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

daily    = load_json_file(
    "pipeline/monitors/fimi-cognitive-warfare/daily/daily-latest.json",
    "daily Collector"
)
weekly   = load_json_file(
    "pipeline/monitors/fimi-cognitive-warfare/weekly/weekly-latest.json",
    "weekly research"
)
reasoner = load_json_file(
    "pipeline/monitors/fimi-cognitive-warfare/reasoner/reasoner-latest.json",
    "reasoner"
)

# At least weekly research is required — Analyst cannot synthesise without it
if not weekly:
    print("ERROR: weekly-latest.json is required for synthesis. Cannot continue.")
    print("       Trigger the weekly-research workflow first, or run manually.")
    sys.exit(1)

daily_count    = len(daily.get("findings", [])) if daily else 0
weekly_count   = len(weekly.get("campaigns", [])) if weekly else 0
reasoner_count = len(reasoner.get("attribution_reviews", [])) if reasoner else 0

print(f"Loaded inputs:")
print(f"  daily-latest:    {daily_count} findings")
print(f"  weekly-latest:   {weekly_count} campaigns")
print(f"  reasoner-latest: {reasoner_count} attribution reviews")

if not daily:
    print("NOTE: daily-latest.json absent — synthesising from weekly + reasoner only.")
if not reasoner:
    print("NOTE: reasoner-latest.json absent — synthesising from weekly + daily only.")

# Guard: empty weekly-research — synthesise from daily + reasoner with null_signal hint
# This prevents hard-fail on quiet weeks where weekly-research returned 0 campaigns.
# The synthesiser prompt supports null_signal_week=true — synthesiser should fire that path.
_empty_weekly = (weekly_count == 0)
if _empty_weekly:
    print("NOTE: weekly-latest.json has 0 campaigns — quiet week or weekly-research returned no data.")
    print("      Synthesising from daily + reasoner only. Null-signal week is expected output.")
    if not daily and not reasoner:
        print("ERROR: No input data available (daily, weekly, and reasoner are all empty/absent). Cannot synthesise.")
        sys.exit(1)

# ── Build context JSON ─────────────────────────────────────────────────────────

context = {
    "daily_collector":   daily   or {"note": "Not available for this synthesis run"},
    "weekly_research":   weekly,
    "reasoner_analysis": reasoner or {"note": "Not available for this synthesis run"},
}

context_json = json.dumps(context, indent=2)

# Truncate if too large — prioritise weekly > reasoner > daily
MAX_CONTEXT = 45000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    context = {
        "daily_collector": {
            "findings": (daily.get("findings", []) if daily else [])[:8],
            "_meta": (daily or {}).get("_meta", {}),
        },
        "weekly_research": weekly,
        "reasoner_analysis": {
            "attribution_reviews":           (reasoner.get("attribution_reviews", [])    if reasoner else [])[:10],
            "linkage_detections":            (reasoner.get("linkage_detections", [])     if reasoner else []),
            "actor_posture_changes":         (reasoner.get("actor_posture_changes", [])  if reasoner else []),
            "cross_monitor_escalation_flags":(reasoner.get("cross_monitor_escalation_flags", []) if reasoner else []),
            "contested_findings":            (reasoner.get("contested_findings", [])     if reasoner else []),
            "analyst_briefing":              (reasoner.get("analyst_briefing", "")       if reasoner else ""),
        } if reasoner else {"note": "Not available"},
    }
    context_json = json.dumps(context, indent=2)[:MAX_CONTEXT]

# ── Build prompt ───────────────────────────────────────────────────────────────

# Inject identity card before pipeline data if available
if identity_content:
    prompt = PROMPT_TEMPLATE.replace("{PIPELINE_JSON}", 
        "## IDENTITY CARD (analytical quality standard)\n\n" + identity_content[:6000] + 
        "\n\n---\n\n## PIPELINE DATA\n\n" + context_json)
else:
    prompt = PROMPT_TEMPLATE.replace("{PIPELINE_JSON}", context_json)

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for weekly synthesis...")
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
        "max_tokens":  32768,
        "temperature": 0.1,
    },
    timeout=300,
)
response.raise_for_status()

api_response = response.json()
raw_content  = api_response["choices"][0]["message"]["content"]

print(f"Response received. Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

# ── Parse ──────────────────────────────────────────────────────────────────────

try:
    data, was_repaired = parse_llm_json(raw_content, "FCW")
    if was_repaired:
        print("[FCW] JSON repaired successfully")
        log_incident(monitor="unknown", stage="synthesiser", incident_type="json_repaired",
                     severity="info", detail="JSON required repair before parsing")
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON after all repair attempts: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    sys.exit(1)

# ── Validate ───────────────────────────────────────────────────────────────────

errors = []
warnings = []
meta = data.get("_meta", {})

# Hard failures — must have these to publish
# On quiet weeks (_empty_weekly), key_judgments / lead_signal / weekly_brief_draft
# may be absent if the model fires the null-signal path — demote to warnings.
if not data.get("lead_signal", {}).get("headline"):
    if _empty_weekly:
        warnings.append("lead_signal.headline missing — quiet week, null-signal path accepted")
    else:
        errors.append("lead_signal.headline missing")
if not data.get("key_judgments"):
    if _empty_weekly:
        warnings.append("key_judgments empty — quiet week, null-signal path accepted")
    else:
        errors.append("key_judgments empty or missing")
if not data.get("weekly_brief_draft"):
    if _empty_weekly:
        warnings.append("weekly_brief_draft missing — quiet week, null-signal path accepted")
    else:
        errors.append("weekly_brief_draft missing")

# Soft warnings — acceptable on quiet weeks
if meta.get("schema_version") not in ("synthesis-v1.0", "fcw-synthesis-v1.0"):
    warnings.append(f"schema_version '{meta.get('schema_version')}' unexpected — continuing")
if not data.get("campaigns"):
    warnings.append("campaigns empty — quiet week or model did not populate")
if not data.get("actor_tracker"):
    warnings.append("actor_tracker empty — quiet week or model did not populate")

for w in warnings:
    print(f"VALIDATION WARNING: {w}")

# Always write debug file for inspection
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Debug file written: debug-{TODAY_STR}.json")

if errors:
    print(f"VALIDATION FAILED (hard errors): {errors}")
    sys.exit(1)

# ── Token Intensity Monitor hook ─────────────────────────────────────────────

if _TIM_AVAILABLE:
    _usage = api_response.get("usage", {})
    _usage["citations"] = 0       # synthesisers don't do web search
    _usage["unique_domains"] = 0
    try:
        _tim_result = _tim_monitor(
            "fimi-cognitive-warfare",
            _usage,
            "pipeline/monitors/fimi-cognitive-warfare/ops/ops-metrics.json",
        )
        print(f"TIM: intensity={_tim_result.get('analytical_intensity')}, cascade={_tim_result.get('cascade_state')}, alerts={_tim_result.get('alerts', [])}")
    except Exception as _tim_e:
        print(f"TIM hook failed (non-blocking): {_tim_e}")


# ── Write ──────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output,  encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

campaigns   = data.get("campaigns", [])
actors      = data.get("actor_tracker", [])
judgments   = data.get("key_judgments", [])
highlights  = data.get("intelligence_highlights", [])
contested   = data.get("delta_strip", {}).get("contested_findings_for_analyst", [])
brief_len   = len(data.get("weekly_brief_draft", ""))

print(f"✅ Written: {OUT_DATED}")
print(f"   Lead signal:            {data.get('lead_signal', {}).get('confidence', '?')}")
print(f"   Key judgments:          {len(judgments)}")
print(f"   Campaigns synthesised:  {len(campaigns)}")
print(f"   Actor tracker entries:  {len(actors)}")
print(f"   Intelligence highlights:{len(highlights)}")
print(f"   Contested for Analyst:  {len(contested)}")
print(f"   Weekly brief draft:     {brief_len} chars")

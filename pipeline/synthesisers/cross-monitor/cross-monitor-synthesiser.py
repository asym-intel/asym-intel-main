#!/usr/bin/env python3
"""
Cross-Monitor Synthesiser
Pipeline stage : cross-monitor (site-wide synthesis)
Model          : sonar-deep-research (no web search — reasons over monitor reports)
Output         : pipeline/cross-monitor/synthesis-YYYY-MM-DD.json
                 pipeline/cross-monitor/synthesis-latest.json
Runs           : Sunday 18:30 UTC (30 min after SCEM publisher at 18:00)
Signal product : This output is the raw material for signal.gi
"""

import json, os, sys, re, datetime, pathlib
import requests
import time

# Shared repair utilities — sibling of synthesisers/
# synth_utils.py lives at pipeline/synthesisers/synth_utils.py, which is this
# file's grandparent dir (parent.parent). Earlier parents[2] was wrong — that
# resolved to pipeline/, one level too high.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from synth_utils import parse_llm_json

# ── Pipeline incident logging ─────────────────────────────────────────────────
try:
    _il_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_il_root / "pipeline"))
    from incident_log import log_incident
except ImportError:
    def log_incident(**kw): pass  # graceful fallback

# ── Token Intensity Monitor ───────────────────────────────────────────────────
try:
    sys.path.insert(0, str(pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))))
    from pipeline.shared.Token_Intensity_Monitor import monitor_metabolic_load as _tim_monitor
    _TIM_AVAILABLE = True
except ImportError:
    _TIM_AVAILABLE = False
    def _tim_monitor(*a, **kw): return {}  # graceful fallback


REPO_ROOT  = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
SYNTH_DIR  = REPO_ROOT / "pipeline" / "cross-monitor"
PROMPT_FILE     = pathlib.Path(__file__).with_name("cross-monitor-synthesiser-api-prompt.txt")
RESPONSE_SCHEMA = pathlib.Path(__file__).with_name("cross-monitor-response-schema.json")

TODAY_STR = datetime.date.today().isoformat()
OUT_DATED = SYNTH_DIR / f"synthesis-{TODAY_STR}.json"

API_KEY = os.environ["PPLX_API_KEY"]
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL   = os.environ.get("SYNTH_MODEL") or "sonar-deep-research"

# ── Dedup guard ───────────────────────────────────────────────────────────────
if OUT_DATED.exists():
    print(f"[XM] GUARD: cross-monitor synthesiser already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

# ── Monitor report map (abbr → data path) ────────────────────────────────────
MONITORS = {
    "wdm":  "democratic-integrity",
    "gmm":  "macro-monitor",
    "esa":  "european-strategic-autonomy",
    "fcw":  "fimi-cognitive-warfare",
    "aim":  "ai-governance",
    "erm":  "environmental-risks",
    "scem": "conflict-escalation",
}

def load_json(path, tag="XM"):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"[{tag}] WARNING: {p} not found — skipping")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[{tag}] WARNING: Could not parse {p}: {e}")
        return {}

def load_text(path):
    p = pathlib.Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""

# ── Load all 7 monitor reports ────────────────────────────────────────────────
monitor_reports = {}
monitors_loaded = []
monitors_missing = []

for abbr, slug in MONITORS.items():
    report_path = REPO_ROOT / "docs" / "monitors" / slug / "data" / "report-latest.json"
    report = load_json(report_path, "XM")
    if report:
        monitor_reports[abbr] = report
        monitors_loaded.append(abbr)
        week = report.get("meta", {}).get("week_label", "?")
        print(f"[XM] Loaded {abbr.upper()} report: {week}")
    else:
        monitors_missing.append(abbr)
        print(f"[XM] WARNING: {abbr.upper()} report not available")

if len(monitors_loaded) < 4:
    msg = f"Insufficient monitor data: only {len(monitors_loaded)}/7 reports available ({monitors_loaded}). Cannot produce meaningful cross-domain synthesis."
    print(f"[XM] ABORT: {msg}")
    log_incident(
        monitor="cross-monitor",
        stage="synthesiser",
        incident_type="input_missing",
        severity="error",
        detail=msg,
    )
    # Write a null-signal stub so the publisher can still create an archive entry
    SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    stub = {
        "_meta": {
            "schema_version": "cross-monitor-synthesis-v1.0",
            "research_model": MODEL,
            "synthesised_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "week_ending": TODAY_STR,
            "monitors_read": list(MONITORS.keys()),
            "monitors_with_signal": monitors_loaded,
            "null_signal_week": True,
            "null_signal_reason": msg,
        },
        "week_label": "Insufficient data — synthesis skipped",
        "composite_score": {
            "score": 0.0,
            "direction": "Mixed",
            "conviction": "Low",
            "component_scores": {k: 0.0 for k in MONITORS},
            "score_rationale": msg,
        },
        "dominant_pattern": {
            "narrative": msg,
            "monitors_involved": monitors_loaded,
            "confidence": "Possible",
        },
        "cross_domain_connections": [],
        "amplification_flags": [],
        "quiet_domain_assessment": [
            {"monitor": m, "assessment": "Significant absence", "note": "Report not available at synthesis time."}
            for m in monitors_missing
        ],
        "weekly_brief_draft": msg,
    }
    OUT_DATED.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    (SYNTH_DIR / "synthesis-latest.json").write_text(json.dumps(stub, indent=2), encoding="utf-8")
    sys.exit(0)

prompt_text = load_text(PROMPT_FILE)
if not prompt_text:
    sys.exit(f"[XM] ERROR: prompt file not found at {PROMPT_FILE}")

# ── Build context message ─────────────────────────────────────────────────────
# Provide a structured summary of each monitor report
# Keep each report to its most synthesis-relevant fields to manage context
def extract_synthesis_fields(abbr, report):
    """Extract the fields most useful for cross-domain synthesis."""
    meta = report.get("meta", {})
    signal = report.get("signal", {})
    key_judgments = report.get("key_judgments", [])
    cross_flags = report.get("cross_monitor_flags", [])
    weekly_brief = report.get("weekly_brief", {})

    extracted = {
        "monitor": abbr.upper(),
        "week_label": meta.get("week_label", "?"),
        "schema_version": meta.get("schema_version", "?"),
        "issue": meta.get("issue", "?"),
        "signal": signal,
        "key_judgments": key_judgments[:5] if isinstance(key_judgments, list) else key_judgments,
        "cross_monitor_flags": cross_flags[:6] if isinstance(cross_flags, list) else cross_flags,
        "weekly_brief_summary": weekly_brief if isinstance(weekly_brief, dict) else str(weekly_brief)[:500],
    }

    # Include monitor-specific high-value fields
    if abbr == "gmm":
        extracted["stress_regime"] = report.get("stress_regime", {})
        extracted["tail_risks"] = report.get("tail_risks", [])[:3]
    elif abbr == "wdm":
        extracted["global_health_snapshot"] = report.get("global_health_snapshot", {})
    elif abbr == "esa":
        extracted["autonomy_scorecard"] = report.get("autonomy_scorecard", {})
        extracted["lagrange_point_scores"] = report.get("lagrange_point_scores", {})
    elif abbr == "fcw":
        # FCW key campaigns
        pass
    elif abbr == "scem":
        extracted["global_escalation_snapshot"] = report.get("global_escalation_snapshot", {})
    elif abbr == "erm":
        pass
    elif abbr == "aim":
        pass

    return extracted

system_msg = (
    "You are the Cross-Monitor Synthesiser for Asymmetric Intelligence at asym-intel.info. "
    "Reason over the provided monitor reports only — do not search the web. "
    "Identify structural cross-domain connections and produce the composite synthesis JSON. "
    "Respond with a single valid JSON object matching the schema in the prompt. "
    "No markdown fences. No explanatory text outside the JSON object."
)

parts = ["## SYNTHESIS PROMPT\n\n" + prompt_text]

# Append each monitor report as a clearly labelled section
for abbr in ["wdm", "gmm", "esa", "fcw", "aim", "erm", "scem"]:
    if abbr in monitor_reports:
        extracted = extract_synthesis_fields(abbr, monitor_reports[abbr])
        label = f"## {abbr.upper()} — {extracted['week_label']} (Issue {extracted['issue']})"
        parts.append(label + "\n\n" + json.dumps(extracted, indent=2)[:8000])
    else:
        parts.append(f"## {abbr.upper()} — NOT AVAILABLE THIS WEEK")

MAX_CONTEXT = 128000
user_msg = "\n\n---\n\n".join(parts)
if len(user_msg) > MAX_CONTEXT:
    print(f"[XM] Context truncated: {len(user_msg)} → {MAX_CONTEXT} chars")
    user_msg = user_msg[:MAX_CONTEXT]

print(f"[XM] Context size: {len(user_msg)} chars | Monitors: {monitors_loaded}")

# ── Load response schema ──────────────────────────────────────────────────────
response_schema = load_json(RESPONSE_SCHEMA, "XM")
request_body = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg},
    ],
    "max_tokens": 16384,
    "temperature": 0.1,
}
if response_schema:
    request_body["response_format"] = {
        "type": "json_schema",
        "json_schema": {"schema": response_schema},
    }
    print("[XM] Using structured output (response_format)")

# ── API call ──────────────────────────────────────────────────────────────────
print(f"[XM] Calling {MODEL} …")
resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json=request_body,
    timeout=300,
)
if resp.status_code == 429:
    print("[XM] 429 rate limit — waiting 60s")
    time.sleep(60)
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=request_body,
        timeout=300,
    )
resp.raise_for_status()
raw = resp.json()["choices"][0]["message"]["content"].strip()

# ── Parse + repair ────────────────────────────────────────────────────────────
try:
    synthesis, was_repaired = parse_llm_json(raw, "XM")
    if was_repaired:
        print("[XM] JSON repaired successfully")
        log_incident(
            monitor="cross-monitor",
            stage="synthesiser",
            incident_type="json_repaired",
            severity="info",
            detail="JSON required repair before parsing",
        )
except json.JSONDecodeError as e:
    print(f"[XM] JSON parse error: {e}. Writing fallback stub.")
    log_incident(
        monitor="cross-monitor",
        stage="synthesiser",
        incident_type="json_parse_error",
        severity="error",
        detail=f"JSON parse error: {e}. Fallback stub written.",
        raw_snippet=raw[:500] if raw else "",
    )
    synthesis = {
        "_meta": {
            "schema_version": "cross-monitor-synthesis-v1.0",
            "research_model": MODEL,
            "synthesised_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "week_ending": TODAY_STR,
            "monitors_read": list(MONITORS.keys()),
            "monitors_with_signal": monitors_loaded,
            "null_signal_week": True,
            "null_signal_reason": f"JSON parse error: {e}",
        },
        "week_label": "Parse error — synthesis incomplete",
        "composite_score": {
            "score": 0.0,
            "direction": "Mixed",
            "conviction": "Low",
            "component_scores": {k: 0.0 for k in MONITORS},
            "score_rationale": "Synthesis failed due to JSON parse error.",
        },
        "dominant_pattern": {
            "narrative": "Synthesis could not be completed this week due to a processing error.",
            "monitors_involved": [],
            "confidence": "Possible",
        },
        "cross_domain_connections": [],
        "amplification_flags": [],
        "quiet_domain_assessment": [],
        "weekly_brief_draft": "Cross-monitor synthesis could not be completed this week due to a processing error.",
        "_raw_fallback": raw,
    }

# ── Stamp metadata ────────────────────────────────────────────────────────────
if "_meta" in synthesis:
    synthesis["_meta"].setdefault(
        "synthesised_at",
        datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    synthesis["_meta"]["research_model"] = MODEL
    synthesis["_meta"]["monitors_read"] = list(MONITORS.keys())
    synthesis["_meta"]["monitors_with_signal"] = monitors_loaded

# ── Token Intensity Monitor hook ──────────────────────────────────────────────
if _TIM_AVAILABLE:
    _api_json = resp.json()
    _usage = _api_json.get("usage", {})
    _usage["citations"] = 0       # synthesiser does not search the web
    _usage["unique_domains"] = 0
    try:
        _tim_result = _tim_monitor(
            "cross-monitor",
            _usage,
            "pipeline/cross-monitor/ops-metrics.json",
        )
        print(f"[XM] TIM: intensity={_tim_result.get('analytical_intensity')}, "
              f"cascade={_tim_result.get('cascade_state')}, "
              f"alerts={_tim_result.get('alerts', [])}")
    except Exception as _tim_e:
        print(f"[XM] TIM hook failed (non-blocking): {_tim_e}")

# ── Write output ──────────────────────────────────────────────────────────────
SYNTH_DIR.mkdir(parents=True, exist_ok=True)

# Debug copy (full LLM response metadata)
debug = {"synthesis": synthesis, "monitors_loaded": monitors_loaded, "monitors_missing": monitors_missing}
(SYNTH_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(debug, indent=2), encoding="utf-8")

out = json.dumps(synthesis, indent=2, ensure_ascii=False)
OUT_DATED.write_text(out, encoding="utf-8")
(SYNTH_DIR / "synthesis-latest.json").write_text(out, encoding="utf-8")

null_flag = synthesis.get("_meta", {}).get("null_signal_week", False)
week_label = synthesis.get("week_label", "?")
score = synthesis.get("composite_score", {}).get("score", "?")
direction = synthesis.get("composite_score", {}).get("direction", "?")
connections = len(synthesis.get("cross_domain_connections", []))

print(f"[XM] Written → {OUT_DATED}")
print(f"[XM] Week: {week_label}")
print(f"[XM] Composite score: {score} ({direction})")
print(f"[XM] Cross-domain connections: {connections}")
print(f"[XM] null_signal_week = {null_flag}")

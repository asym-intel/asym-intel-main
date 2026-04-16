#!/usr/bin/env python3
"""
World Democracy Monitor Synthesiser
Monitor slug : democratic-integrity
Model       : sonar-pro (no web search — reasons over supplied docs)
Output      : pipeline/monitors/democratic-integrity/synthesised/synthesis-latest.json
"""

import json, os, sys, re, datetime, pathlib
import requests
import time

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


REPO_ROOT   = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
MONITOR_DIR = REPO_ROOT / "pipeline" / "monitors" / "democratic-integrity"
SYNTH_DIR   = MONITOR_DIR / "synthesised"
PROMPT_FILE    = pathlib.Path(__file__).with_name("democratic-integrity-synthesiser-api-prompt.txt")
RESPONSE_SCHEMA = pathlib.Path(__file__).with_name("wdm-response-schema.json")
METHODOLOGY = REPO_ROOT / "docs" / "methodology" / "democratic-integrity-full.md"
IDENTITY    = REPO_ROOT / "docs" / "identity" / "wdm-identity.md"
ADDENDUM    = REPO_ROOT / "docs" / "methodology" / "democratic-integrity-addendum.md"

TODAY_STR = datetime.date.today().isoformat()
OUT_DATED = SYNTH_DIR / f"synthesis-{TODAY_STR}.json"

API_KEY = os.environ["PPLX_API_KEY"]
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL   = os.environ.get("SYNTH_MODEL") or "sonar-pro"

if OUT_DATED.exists():
    print(f"[WDM] GUARD: synthesiser already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

def load_json(path):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"[WDM] WARNING: {p} not found — skipping")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[WDM] WARNING: Could not parse {p}: {e}")
        return {}

def load_text(path):
    p = pathlib.Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""

daily_latest      = load_json(MONITOR_DIR / "daily"  / "daily-latest.json")
weekly_latest     = load_json(MONITOR_DIR / "weekly" / "weekly-latest.json")
reasoner_latest   = load_json(MONITOR_DIR / "reasoner" / "reasoner-latest.json")
prompt_text       = load_text(PROMPT_FILE)
methodology       = load_text(METHODOLOGY)
identity          = load_text(IDENTITY)
addendum          = load_text(ADDENDUM)

if not prompt_text:
    sys.exit(f"[WDM] ERROR: prompt file not found at {PROMPT_FILE}")

system_msg = (
    "You are a systematic intelligence synthesiser for the World Democracy Monitor "
    "at asym-intel.info. "
    "Reason over the provided documents only — do not search the web. "
    "Respond with a single valid JSON object matching the schema in the prompt. "
    "No markdown fences. No explanatory text outside the JSON object."
)

parts = [
    "## SYNTHESIS PROMPT\n\n" + prompt_text,
    "## IDENTITY CARD (analytical quality standard)\n\n" + identity[:6000],
    "## METHODOLOGY\n\n" + methodology[:8000],
]
if addendum:
    parts.append("## METHODOLOGY ADDENDUM\n\n" + addendum[:4000])
# ── Analytical continuity: reasoner before raw news ──────────────────────
if reasoner_latest:
    parts.append("## REASONER ANALYSIS (reasoner-latest.json)\n\n"
                 + json.dumps(reasoner_latest, indent=2)[:16000])

# ── Raw collector data ────────────────────────────────────────────────────
parts.append("## DAILY COLLECTOR (daily-latest.json)\n\n"
             + json.dumps(daily_latest, indent=2)[:12000])
if weekly_latest:
    parts.append("## WEEKLY RESEARCH (weekly-latest.json)\n\n"
                 + json.dumps(weekly_latest, indent=2)[:12000])

MAX_CONTEXT = 120000
user_msg = "\n\n---\n\n".join(parts)
if len(user_msg) > MAX_CONTEXT:
    print(f"[WDM] Context truncated: {len(user_msg)} → {MAX_CONTEXT} chars")
    user_msg = user_msg[:MAX_CONTEXT]

# ── Load response schema for structured output ───────────────────────────────
response_schema = load_json(RESPONSE_SCHEMA)
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
    print("[WDM] Using structured output (response_format)")

print(f"[WDM] Calling {MODEL} …")
resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json=request_body,
    timeout=300,
)
if resp.status_code == 429:
    print(f"[WDM] 429 rate limit — waiting 60s")
    time.sleep(60)
    resp = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=request_body,
        timeout=300)
resp.raise_for_status()
raw = resp.json()["choices"][0]["message"]["content"].strip()

try:
    synthesis, was_repaired = parse_llm_json(raw, "WDM")
    if was_repaired:
        print("[WDM] JSON repaired successfully")
        log_incident(monitor="democratic-integrity", stage="synthesiser", incident_type="json_repaired",
                     severity="info", detail="JSON required repair before parsing")
except json.JSONDecodeError as e:
    print(f"[WDM] JSON parse error: {e}. Writing fallback stub.")
    log_incident(monitor="democratic-integrity", stage="synthesiser", incident_type="json_parse_error",
                 severity="error", detail=f"JSON parse error: {e}. Fallback stub written.",
                 raw_snippet=raw[:500] if raw else "")
    synthesis = {
        "_meta": {
            "schema_version": "democratic-integrity-synthesis-v1.0",
            "research_model": MODEL,
            "monitor_slug": "democratic-integrity",
            "synthesised_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "null_signal_week": True,
            "null_signal_reason": f"JSON parse error: {e}",
        },
        "_raw_fallback": raw,
    }

if "_meta" in synthesis:
    synthesis["_meta"].setdefault(
        "synthesised_at",
        datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    synthesis["_meta"]["research_model"] = MODEL

# ── Token Intensity Monitor hook ─────────────────────────────────────────────

if _TIM_AVAILABLE:
    _api_json = resp.json()
    _usage = _api_json.get("usage", {})
    _usage["citations"] = 0       # synthesisers don't do web search
    _usage["unique_domains"] = 0
    try:
        _tim_result = _tim_monitor(
            "democratic-integrity",
            _usage,
            "pipeline/monitors/democratic-integrity/ops/ops-metrics.json",
        )
        print(f"TIM: intensity={_tim_result.get('analytical_intensity')}, cascade={_tim_result.get('cascade_state')}, alerts={_tim_result.get('alerts', [])}")
    except Exception as _tim_e:
        print(f"TIM hook failed (non-blocking): {_tim_e}")


SYNTH_DIR.mkdir(parents=True, exist_ok=True)
(SYNTH_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(synthesis, indent=2), encoding="utf-8")
out = json.dumps(synthesis, indent=2, ensure_ascii=False)
OUT_DATED.write_text(out, encoding="utf-8")
(SYNTH_DIR / "synthesis-latest.json").write_text(out, encoding="utf-8")

null_flag = synthesis.get("_meta", {}).get("null_signal_week", False)
print(f"[WDM] Written → {OUT_DATED}")
print(f"[WDM] null_signal_week = {null_flag}")

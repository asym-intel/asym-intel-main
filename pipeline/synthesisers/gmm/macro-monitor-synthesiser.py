#!/usr/bin/env python3
"""
Global Macro Monitor Synthesiser
Monitor slug : macro-monitor
Model       : sonar-deep-research (no web search — reasons over supplied docs)
Output      : pipeline/monitors/macro-monitor/synthesised/synthesis-latest.json
"""

import json, os, sys, re, datetime, pathlib
import requests
import time

# Shared repair utilities
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from synth_utils import parse_llm_json

REPO_ROOT   = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
MONITOR_DIR = REPO_ROOT / "pipeline" / "monitors" / "macro-monitor"
SYNTH_DIR   = MONITOR_DIR / "synthesised"
PROMPT_FILE = pathlib.Path(__file__).with_name("macro-monitor-synthesiser-api-prompt.txt")
METHODOLOGY = REPO_ROOT / "docs" / "methodology" / "macro-monitor-full.md"
ADDENDUM    = REPO_ROOT / "docs" / "methodology" / "macro-monitor-addendum.md"

TODAY_STR = datetime.date.today().isoformat()
OUT_DATED = SYNTH_DIR / f"synthesis-{TODAY_STR}.json"

API_KEY = os.environ["PPLX_API_KEY"]
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL   = os.environ.get("SYNTH_MODEL", "sonar-deep-research")

if OUT_DATED.exists():
    print(f"[GMM] GUARD: synthesiser already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

def load_json(path):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"[GMM] WARNING: {p} not found — skipping")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[GMM] WARNING: Could not parse {p}: {e}")
        return {}

def load_text(path):
    p = pathlib.Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""

daily_latest  = load_json(MONITOR_DIR / "daily"  / "daily-latest.json")
weekly_latest = load_json(MONITOR_DIR / "weekly" / "weekly-latest.json")
prompt_text   = load_text(PROMPT_FILE)
methodology   = load_text(METHODOLOGY)
addendum      = load_text(ADDENDUM)

if not prompt_text:
    sys.exit(f"[GMM] ERROR: prompt file not found at {PROMPT_FILE}")

system_msg = (
    "You are a systematic intelligence synthesiser for the Global Macro Monitor "
    "at asym-intel.info. "
    "Reason over the provided documents only — do not search the web. "
    "Respond with a single valid JSON object matching the schema in the prompt. "
    "No markdown fences. No explanatory text outside the JSON object."
)

parts = [
    "## SYNTHESIS PROMPT\n\n" + prompt_text,
    "## METHODOLOGY\n\n" + methodology[:8000],
]
if addendum:
    parts.append("## METHODOLOGY ADDENDUM\n\n" + addendum[:4000])
parts.append("## DAILY COLLECTOR (daily-latest.json)\n\n"
             + json.dumps(daily_latest, indent=2)[:8000])
if weekly_latest:
    parts.append("## WEEKLY RESEARCH (weekly-latest.json)\n\n"
                 + json.dumps(weekly_latest, indent=2)[:8000])

MAX_CONTEXT = 40000
user_msg = "\n\n---\n\n".join(parts)
if len(user_msg) > MAX_CONTEXT:
    print(f"[GMM] Context truncated: {len(user_msg)} → {MAX_CONTEXT} chars")
    user_msg = user_msg[:MAX_CONTEXT]

print(f"[GMM] Calling {MODEL} …")
resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        "max_tokens": 8192,
        "temperature": 0.1,
    },
    timeout=180,
)
if resp.status_code == 429:
    print(f"[GMM] 429 rate limit — waiting 60s")
    time.sleep(60)
    resp = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "system", "content": system_msg},
              {"role": "user", "content": user_msg}], "max_tokens": 8192, "temperature": 0.1},
        timeout=180)
resp.raise_for_status()
raw = resp.json()["choices"][0]["message"]["content"].strip()

try:
    synthesis, was_repaired = parse_llm_json(raw, "GMM")
    if was_repaired:
        print("[GMM] JSON repaired successfully")
except json.JSONDecodeError as e:
    print(f"[GMM] JSON parse error: {e}. Writing fallback stub.")
    synthesis = {
        "_meta": {
            "schema_version": "macro-monitor-synthesis-v1.0",
            "research_model": MODEL,
            "monitor_slug": "macro-monitor",
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

SYNTH_DIR.mkdir(parents=True, exist_ok=True)
(SYNTH_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(synthesis, indent=2), encoding="utf-8")
out = json.dumps(synthesis, indent=2, ensure_ascii=False)
OUT_DATED.write_text(out, encoding="utf-8")
(SYNTH_DIR / "synthesis-latest.json").write_text(out, encoding="utf-8")

null_flag = synthesis.get("_meta", {}).get("null_signal_week", False)
print(f"[GMM] Written → {OUT_DATED}")
print(f"[GMM] null_signal_week = {null_flag}")

#!/usr/bin/env python3
"""
GMM Weekly Research — TEST SCRIPT
Calls sonar-pro with a focused GMM prompt.
Writes output to pipeline/monitors/macro-monitor/weekly/weekly-test-YYYY-MM-DD.json
"""
import os, json, requests, datetime, re, pathlib, sys

API_KEY   = os.environ["PPLX_API_KEY"]
TODAY     = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/macro-monitor/weekly")
OUT_FILE  = OUT_DIR / f"weekly-test-{TODAY}.json"

if OUT_FILE.exists():
    print(f"GUARD: {OUT_FILE} already exists. Exiting.")
    sys.exit(0)

prompt = """You are a global macro financial analyst conducting deep research on the week ending April 4, 2026.

The dominant macro event this week is the Trump administration's April 2, 2026 "Liberation Day" tariff package — the largest US tariff escalation since the 1930s. Effective US tariff rates have risen sharply with tariff disputes now active against EU, China, Canada, Mexico simultaneously.

Search these sources: Federal Reserve statements, ECB press releases, USTR announcements, IMF/World Bank, Peterson Institute PIIE tariff tracker, BIS, WTO, Bloomberg/Reuters/FT financial news, central bank meeting minutes, earnings guidance from major corporates.

Return ONLY valid JSON — no markdown, no code fences, no explanation outside the JSON.

{
  "_meta": {
    "schema_version": "weekly-research-v1.0",
    "monitor_slug": "macro-monitor",
    "job_type": "weekly-deep-research",
    "generated_at": "ISO8601",
    "week_ending": "2026-04-04",
    "status": "complete"
  },
  "lead_signal": {
    "headline": "one sentence — single most important macro development this week",
    "actor": "US|EU|China|Global|Central Banks",
    "confidence_preliminary": "Confirmed|High|Assessed|Possible",
    "confidence_basis": "explain why this confidence level",
    "source_url": "direct URL to primary source",
    "mf_flags": []
  },
  "top_developments": [
    {
      "title": "short descriptive title",
      "summary": "2-3 sentences: what happened and why it matters for macro",
      "signal_type": "SA|CC|TS",
      "signal_type_basis": "why SA/CC/TS",
      "asset_classes_affected": ["Bonds","Tech","Energy","Metals","EM Equities","Crypto","Consumer Staples","Real Estate"],
      "source_url": "direct URL",
      "source_name": "publication name",
      "source_tier": 1
    }
  ],
  "tariff_escalation": {
    "current_rung": 3,
    "rung_basis": "explanation of current escalation level",
    "effective_rate_approx_pct": 22,
    "active_retaliators": ["CN","EU","CA","MX"],
    "decoupling_direction": "Accelerating|Stable|De-escalating"
  },
  "asset_class_summary": {
    "bonds": "current signal and direction",
    "tech": "current signal and direction",
    "energy": "current signal and direction",
    "metals": "current signal and direction",
    "em_equities": "current signal and direction",
    "crypto": "current signal and direction"
  },
  "weekly_brief_narrative": "300-400 word analytical narrative covering: dominant macro regime, tariff war impact, asset class implications, what to watch next week. Cold analytical register.",
  "research_coverage": {
    "sources_searched": ["list all sources checked"],
    "sources_with_findings": ["sources that returned relevant material"],
    "coverage_gaps": ["any areas with thin coverage"]
  }
}"""

print(f"Calling sonar-pro for GMM weekly test ({TODAY})...")
r = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"model": "sonar-pro", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
    timeout=120
)
r.raise_for_status()

api_resp  = r.json()
raw       = api_resp["choices"][0]["message"]["content"]
citations = api_resp.get("citations", [])
tokens    = api_resp.get("usage", {}).get("total_tokens", "?")
print(f"Response received. Tokens: {tokens} | Citations: {len(citations)}")

# Strip fences
clean = raw.strip()
if clean.startswith("```"):
    clean = re.sub(r'^```(?:json)?\s*', '', clean)
    clean = re.sub(r'\s*```$', '', clean).strip()
brace = clean.find('{'); rbrace = clean.rfind('}')
if brace != -1 and rbrace != -1:
    clean = clean[brace:rbrace+1]

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    print(f"ERROR: JSON parse failed: {e}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY}.txt").write_text(raw)
    sys.exit(1)

# Inject citations
data["_meta"]["citations"] = citations
data["_meta"]["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"✅ Written: {OUT_FILE}")

lead = data.get("lead_signal", {})
devs = data.get("top_developments", [])
tariff = data.get("tariff_escalation", {})
brief = data.get("weekly_brief_narrative", "")
print(f"\nLEAD: [{lead.get('confidence_preliminary')}] {lead.get('headline','')[:90]}")
print(f"Tariff rung: {tariff.get('current_rung')} — {tariff.get('rung_basis','')[:70]}")
print(f"Decoupling: {tariff.get('decoupling_direction')}")
print(f"Developments: {len(devs)}")
for d in devs[:4]:
    print(f"  [{d.get('signal_type')}] {d.get('title','')[:65]}")
    print(f"     {d.get('summary','')[:90]}")
print(f"\nBrief: {len(brief)} chars")
print(brief[:400])

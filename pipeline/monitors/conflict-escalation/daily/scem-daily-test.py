#!/usr/bin/env python3
"""
SCEM Daily Collector — TEST SCRIPT
Tests sonar on active conflict signal collection.
Writes to pipeline/monitors/conflict-escalation/daily/daily-test-YYYY-MM-DD.json
"""
import os, json, requests, datetime, re, pathlib, sys

API_KEY  = os.environ["PPLX_API_KEY"]
TODAY    = datetime.date.today().isoformat()
OUT_DIR  = pathlib.Path("pipeline/monitors/conflict-escalation/daily")
OUT_FILE = OUT_DIR / f"daily-test-{TODAY}.json"

if OUT_FILE.exists():
    print(f"GUARD: {OUT_FILE} already exists. Exiting.")
    sys.exit(0)

prompt = """You are a conflict escalation analyst. Research today's most significant conflict escalation or de-escalation developments across these active theatres: Russia-Ukraine War, Gaza/Israel-Hamas, Sudan Civil War, Myanmar Civil War, DRC Eastern Conflict, Iran regional tensions.

Search: ACLED, UCDP, ISW (Institute for the Study of War), UN OCHA, ICG Crisis Watch, Reuters, AP, BBC, Al Jazeera, Bellingcat. Focus on developments from the past 48 hours only.

Return ONLY valid JSON — no markdown, no code fences.

{
  "_meta": {
    "schema_version": "tier0-v1.0",
    "monitor_slug": "conflict-escalation",
    "data_date": "2026-04-02",
    "status": "complete",
    "finding_count": 0
  },
  "findings": [
    {
      "finding_id": "scem-2026-04-02-001",
      "dedupe_key": "theatre-indicator-descriptor",
      "title": "short title",
      "summary": "2-3 sentences: what happened, which indicator affected (I1-I6), direction",
      "theatre": "Russia-Ukraine|Gaza|Sudan|Myanmar|DRC|Iran",
      "indicator": "I1|I2|I3|I4|I5|I6",
      "indicator_direction": "escalating|de-escalating|stable",
      "confidence_preliminary": "Confirmed|High|Assessed|Possible",
      "source_url": "direct URL",
      "source_name": "publication name",
      "source_tier": 1,
      "episodic_flag": false,
      "campaign_status_candidate": "net_new|continuation",
      "research_traceback": {
        "sources_cited": [{"source_name": "name", "source_url": "url", "tier": 1, "excerpt": "quote"}],
        "search_queries_run": ["exact queries"]
      }
    }
  ],
  "below_threshold": [],
  "theatre_summary": {
    "russia_ukraine": "one sentence current status",
    "gaza": "one sentence current status",
    "sudan": "one sentence current status",
    "myanmar": "one sentence current status",
    "drc": "one sentence current status"
  }
}"""

print(f"Calling sonar for SCEM daily test ({TODAY})...")
r = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
    timeout=60
)
r.raise_for_status()

api_resp  = r.json()
raw       = api_resp["choices"][0]["message"]["content"]
citations = api_resp.get("citations", [])
tokens    = api_resp.get("usage", {}).get("total_tokens", "?")
print(f"Response received. Tokens: {tokens} | Citations: {len(citations)}")

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
    print(f"ERROR: {e}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY}.txt").write_text(raw)
    sys.exit(1)

data["_meta"]["citations"] = citations
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"✅ Written: {OUT_FILE}")

findings = data.get("findings", [])
print(f"\nFINDINGS ({len(findings)}):")
for f in findings[:5]:
    print(f"  [{f.get('confidence_preliminary')}] [{f.get('theatre')}] [{f.get('indicator')}↑↓] {f.get('title','')[:65]}")
    print(f"     {f.get('summary','')[:90]}")
    print(f"     Source: {f.get('source_url','')[:60]}")

theatres = data.get('theatre_summary', {})
print(f"\nTHEATRE SUMMARY:")
for t, s in theatres.items():
    print(f"  {t}: {str(s)[:80]}")

print(f"\nCitations:")
for c in citations[:5]:
    print(f"  {c[:80]}")

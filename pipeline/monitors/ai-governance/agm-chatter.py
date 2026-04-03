#!/usr/bin/env python3
"""
AGM Chatter — Daily Signal
Calls Perplexity sonar for top 10 raw FIMI signal items.
Writes to static/monitors/ai-governance/data/chatter-latest.json (public)
       and static/monitors/ai-governance/data/chatter-YYYY-MM-DD.json
"""
import os, json, requests, datetime, re, pathlib, sys, base64, subprocess

API_KEY   = os.environ["PPLX_API_KEY"]
TODAY     = datetime.date.today().isoformat()
SLUG      = "ai-governance"
OUT_DIR   = pathlib.Path(f"static/monitors/{SLUG}/data")
OUT_DATED = OUT_DIR / f"chatter-{TODAY}.json"
OUT_LATEST = OUT_DIR / "chatter-latest.json"

# Guard: skip if today's file already exists
if OUT_DATED.exists():
    print(f"GUARD: chatter-{TODAY}.json already exists. Exiting.")
    sys.exit(0)

# Load prompt
PROMPT_FILE = pathlib.Path(f"pipeline/monitors/{SLUG}/agm-chatter-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt not found at {PROMPT_FILE}")
    sys.exit(1)
prompt = PROMPT_FILE.read_text(encoding="utf-8")

# Call Perplexity API
print(f"Calling sonar for AGM Chatter ({TODAY})...")
response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
    timeout=60,
)
response.raise_for_status()

api_resp  = response.json()
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
    (OUT_DIR / f"chatter-debug-{TODAY}.txt").write_text(raw)
    sys.exit(1)

# Validate
items = data.get("items", [])
if not items:
    print("WARNING: No items returned — model may have returned empty response")

# Fix meta
data["_meta"]["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
data["_meta"]["data_date"]    = TODAY
data["_meta"]["item_count"]   = len(items)
data["_meta"]["citations"]    = citations

# Ensure item_ids are set
for i, item in enumerate(items):
    if not item.get("item_id"):
        item["item_id"] = f"agm-chatter-{TODAY}-{i+1:03d}"

# Write
OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output, encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_LATEST}")
print(f"   Items: {len(items)}")
for item in items[:5]:
    print(f"   [{item.get('source_tier','?')}] {item.get('title','')[:70]}")

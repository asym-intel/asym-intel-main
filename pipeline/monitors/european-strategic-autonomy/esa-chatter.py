#!/usr/bin/env python3
"""
ESA Chatter — Daily Signal
Calls Perplexity sonar for top 10 raw ESA signal items.
Writes to static/monitors/european-strategic-autonomy/data/chatter-latest.json (public)
       and static/monitors/european-strategic-autonomy/data/chatter-YYYY-MM-DD.json

Deduplication: loads previous 7 days of chatter URLs and injects as
exclusion list into the prompt. Post-filters items older than 48h.
"""
import os, json, requests, datetime, re, pathlib, sys

API_KEY   = os.environ["PPLX_API_KEY"]
TODAY     = datetime.date.today()
TODAY_STR = TODAY.isoformat()
CUTOFF    = (TODAY - datetime.timedelta(days=2)).isoformat()
SLUG      = "european-strategic-autonomy"
ABBR      = "esa"
OUT_DIR   = pathlib.Path(f"static/monitors/{SLUG}/data")
OUT_DATED = OUT_DIR / f"chatter-{TODAY_STR}.json"
OUT_LATEST = OUT_DIR / "chatter-latest.json"

# Guard: skip if today's file already exists
if OUT_DATED.exists():
    print(f"GUARD: chatter-{TODAY_STR}.json already exists. Exiting.")
    sys.exit(0)

# ── Load previous chatter URLs for deduplication ──────────────────────────────

def load_previous_urls(days=7):
    """Collect all source_url values from the last N days of chatter files."""
    urls = set()
    for d in range(1, days + 1):
        date_str = (TODAY - datetime.timedelta(days=d)).isoformat()
        for prefix in ["static", "docs"]:
            path = pathlib.Path(f"{prefix}/monitors/{SLUG}/data/chatter-{date_str}.json")
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    for item in data.get("items", []):
                        url = item.get("source_url", "")
                        if url:
                            urls.add(url)
                except (json.JSONDecodeError, KeyError):
                    pass
                break  # found in static or docs, no need to check both
    return urls

previous_urls = load_previous_urls()
print(f"Dedup: loaded {len(previous_urls)} previously covered URLs from last 7 days")

# Format exclusion list for prompt injection
if previous_urls:
    exclude_block = "\n".join(f"- {u}" for u in sorted(previous_urls))
else:
    exclude_block = "(none — first run or no recent history)"

# ── Load and prepare prompt ───────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path(f"pipeline/monitors/{SLUG}/{ABBR}-chatter-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")
prompt = prompt.replace("{today_date}", TODAY_STR)
prompt = prompt.replace("{cutoff_date}", CUTOFF)
prompt = prompt.replace("{exclude_urls}", exclude_block)

# ── Call Perplexity API ───────────────────────────────────────────────────────

print(f"Calling sonar for {ABBR.upper()} Chatter ({TODAY_STR})...")
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

# ── Parse JSON ────────────────────────────────────────────────────────────────

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
    (OUT_DIR / f"chatter-debug-{TODAY_STR}.txt").write_text(raw)
    sys.exit(1)

# ── Filter: dedup + recency ───────────────────────────────────────────────────

items = data.get("items", [])
original_count = len(items)
filtered = []

for item in items:
    url = item.get("source_url", "")
    pub_date = item.get("published_date", "")

    # Skip if URL was in previous chatter
    if url and url in previous_urls:
        print(f"  DEDUP: skipping previously covered: {url[:80]}")
        continue

    # Skip if published_date is older than 48h cutoff
    if pub_date and pub_date < CUTOFF:
        print(f"  STALE: skipping ({pub_date} < {CUTOFF}): {item.get('title','')[:60]}")
        continue

    filtered.append(item)

if len(filtered) < original_count:
    print(f"Filtered: {original_count} → {len(filtered)} items "
          f"({original_count - len(filtered)} removed)")

data["items"] = filtered

# ── Fix meta ──────────────────────────────────────────────────────────────────

data.setdefault("_meta", {})
data["_meta"]["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
data["_meta"]["data_date"]    = TODAY_STR
data["_meta"]["item_count"]   = len(filtered)
data["_meta"]["citations"]    = citations

# Ensure item_ids are set
for i, item in enumerate(filtered):
    if not item.get("item_id"):
        item["item_id"] = f"{ABBR}-chatter-{TODAY_STR}-{i+1:03d}"

# ── Write ─────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output, encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

print(f"✅ Written: {OUT_DATED}")
print(f"✅ Written: {OUT_LATEST}")
print(f"   Items: {len(filtered)}")
for item in filtered[:5]:
    print(f"   [{item.get('source_tier','?')}] {item.get('title','')[:70]}")

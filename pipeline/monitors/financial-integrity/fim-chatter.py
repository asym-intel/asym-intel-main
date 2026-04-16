#!/usr/bin/env python3
"""
FIM Chatter — Standalone fallback (emergency single-monitor re-run only)
Normal operation uses unified-chatter.py for all monitors.

Environment variables required:
  PPLX_API_KEY  — Perplexity API key
"""

import os, json, requests, datetime, pathlib, sys, re

# ── Exchange logger (record every API call — success or failure) ──────────────
try:
    _repo_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(_repo_root / "pipeline" / "shared"))
    from prompt_exchange_log import log_exchange
except ImportError:
    def log_exchange(**kw): pass  # graceful fallback

API_KEY   = os.environ["PPLX_API_KEY"]
NOW       = datetime.datetime.now(datetime.timezone.utc)
TODAY     = datetime.date.today()
TODAY_STR = TODAY.isoformat()
CUTOFF    = (TODAY - datetime.timedelta(days=2)).isoformat()
SLUG      = "financial-integrity"
ABBR      = "fim"

OUT_DIR    = pathlib.Path(f"static/monitors/{SLUG}/data")
OUT_DATED  = OUT_DIR / f"chatter-{TODAY_STR}.json"
OUT_LATEST = OUT_DIR / "chatter-latest.json"

# ── Guard ─────────────────────────────────────────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: {OUT_DATED} already exists. Exiting.")
    sys.exit(0)

# ── Load previous URLs for dedup ──────────────────────────────────────────────

previous_urls = set()
for d in range(1, 8):
    date_str = (TODAY - datetime.timedelta(days=d)).isoformat()
    for prefix in ["static", "docs"]:
        path = pathlib.Path(f"{prefix}/monitors/{SLUG}/data/chatter-{date_str}.json")
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for item in data.get("items", []):
                    url = item.get("source_url", "")
                    if url:
                        previous_urls.add(url)
            except (json.JSONDecodeError, KeyError):
                pass
            break

exclude_block = "\n".join(f"- {u}" for u in sorted(previous_urls)) if previous_urls else "(none)"
print(f"Dedup: {len(previous_urls)} previously covered URLs")

# ── Load and prepare prompt ──────────────────────────────────────────────────

PROMPT_FILE = pathlib.Path("pipeline/monitors/financial-integrity/fim-chatter-api-prompt.txt")
if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")
prompt = prompt.replace("{today_date}", TODAY_STR)
prompt = prompt.replace("{cutoff_date}", CUTOFF)
prompt = prompt.replace("{exclude_urls}", exclude_block)

# ── Call Perplexity API ──────────────────────────────────────────────────────

print(f"Calling sonar for FIM Chatter ({TODAY_STR})...")
response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
    timeout=120,
)
response.raise_for_status()

api_resp  = response.json()
raw       = api_resp["choices"][0]["message"]["content"]
citations = api_resp.get("citations", [])
tokens = api_resp.get('usage', {}).get('total_tokens', '?')
print(f"Response received. Tokens: {tokens}")

# ── Log exchange (before any parsing — captures success AND failure) ──────────
log_exchange(
    monitor=SLUG, stage="chatter", model="sonar",
    prompt_text=prompt, prompt_file=str(PROMPT_FILE),
    raw_response=raw, parsed_ok=False,
    tokens=tokens if isinstance(tokens, int) else None,
    citations=len(citations),
)

# ── Parse JSON ───────────────────────────────────────────────────────────────

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

# ── Filter and write ─────────────────────────────────────────────────────────

items = data.get("items", [])
filtered = []
for item in items:
    url = item.get("source_url", "")
    pub_date = item.get("published_date", "")
    if url and url in previous_urls:
        continue
    if pub_date and pub_date < CUTOFF:
        continue
    filtered.append(item)

for i, item in enumerate(filtered):
    if not item.get("item_id"):
        item["item_id"] = f"{ABBR}-chatter-{TODAY_STR}-{i+1:03d}"

output_obj = {
    "_meta": {
        "schema_version": "chatter-v1.0",
        "monitor_slug": SLUG,
        "generated_at": NOW.isoformat().replace("+00:00", "Z"),
        "data_date": TODAY_STR,
        "item_count": len(filtered),
        "citations": citations,
        "source": "standalone-chatter",
        "coverage_note": f"Top signals for {ABBR.upper()} — standalone fallback run"
    },
    "items": filtered
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_json = json.dumps(output_obj, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output_json, encoding="utf-8")
OUT_LATEST.write_text(output_json, encoding="utf-8")

print(f"✅ FIM Chatter: {len(filtered)} items → {OUT_DATED}")
for item in filtered[:5]:
    print(f"   [{item.get('source_tier', '?')}] {item.get('title', '')[:70]}")

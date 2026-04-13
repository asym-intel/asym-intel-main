#!/usr/bin/env python3
"""
Unified Chatter — Daily Signal (all 7 monitors)
One Perplexity sonar call surfaces up to 5 items per domain across all 7 monitors.
Splits output into per-monitor chatter-latest.json files.

Replaces 7 individual {abbr}-chatter.py scripts (11 Apr 2026).
"""
import os, json, requests, datetime, re, pathlib, sys

API_KEY   = os.environ["PPLX_API_KEY"]
NOW       = datetime.datetime.now(datetime.timezone.utc)
TODAY     = datetime.date.today()
TODAY_STR = TODAY.isoformat()
CUTOFF    = (TODAY - datetime.timedelta(days=2)).isoformat()

MONITORS = [
    {"abbr": "wdm",  "slug": "democratic-integrity"},
    {"abbr": "gmm",  "slug": "macro-monitor"},
    {"abbr": "esa",  "slug": "european-strategic-autonomy"},
    {"abbr": "fcw",  "slug": "fimi-cognitive-warfare"},
    {"abbr": "agm",  "slug": "ai-governance"},
    {"abbr": "erm",  "slug": "environmental-risks"},
    {"abbr": "scem", "slug": "conflict-escalation"},
]

PROMPT_FILE = pathlib.Path("pipeline/chatter/unified-chatter-api-prompt.txt")

# ── Guard: skip if all monitors already have today's file ─────────────────────

all_exist = True
for m in MONITORS:
    dated = pathlib.Path(f"static/monitors/{m['slug']}/data/chatter-{TODAY_STR}.json")
    if not dated.exists():
        all_exist = False
        break

if all_exist:
    print(f"GUARD: All 7 chatter-{TODAY_STR}.json files already exist. Exiting.")
    sys.exit(0)

# ── Load previous chatter URLs for deduplication ──────────────────────────────

def load_previous_urls(days=7):
    """Collect all source_url values from the last N days of chatter files across all monitors."""
    urls = set()
    for m in MONITORS:
        slug = m["slug"]
        for d in range(1, days + 1):
            date_str = (TODAY - datetime.timedelta(days=d)).isoformat()
            for prefix in ["static", "docs"]:
                path = pathlib.Path(f"{prefix}/monitors/{slug}/data/chatter-{date_str}.json")
                if path.exists():
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                        for item in data.get("items", []):
                            url = item.get("source_url", "")
                            if url:
                                urls.add(url)
                    except (json.JSONDecodeError, KeyError):
                        pass
                    break
    return urls

previous_urls = load_previous_urls()
print(f"Dedup: loaded {len(previous_urls)} previously covered URLs from last 7 days (all monitors)")

if previous_urls:
    exclude_block = "\n".join(f"- {u}" for u in sorted(previous_urls))
else:
    exclude_block = "(none — first run or no recent history)"

# ── Load and prepare prompt ───────────────────────────────────────────────────

if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt not found at {PROMPT_FILE}")
    sys.exit(1)

prompt = PROMPT_FILE.read_text(encoding="utf-8")
prompt = prompt.replace("{today_date}", TODAY_STR)
prompt = prompt.replace("{cutoff_date}", CUTOFF)
prompt = prompt.replace("{exclude_urls}", exclude_block)

# ── Call Perplexity API ───────────────────────────────────────────────────────

print(f"Calling sonar for Unified Chatter ({TODAY_STR})...")
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
    debug_dir = pathlib.Path("pipeline/chatter")
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"chatter-debug-{TODAY_STR}.txt").write_text(raw)
    sys.exit(1)

# ── Extract monitors dict ────────────────────────────────────────────────────
# Accept either {"monitors": {...}} or flat {slug: {items: [...]}} format

monitors_data = data.get("monitors", data)
if not isinstance(monitors_data, dict):
    print(f"ERROR: Expected dict at top-level or under 'monitors', got {type(monitors_data).__name__}")
    sys.exit(1)

# ── Split into per-monitor files ──────────────────────────────────────────────

total_items = 0
for m in MONITORS:
    slug = m["slug"]
    abbr = m["abbr"]
    out_dir = pathlib.Path(f"static/monitors/{slug}/data")
    out_dated = out_dir / f"chatter-{TODAY_STR}.json"
    out_latest = out_dir / "chatter-latest.json"

    # Extract this monitor's items
    monitor_block = monitors_data.get(slug, {})
    items = monitor_block.get("items", []) if isinstance(monitor_block, dict) else []

    # Filter: dedup + recency
    original_count = len(items)
    filtered = []
    for item in items:
        url = item.get("source_url", "")
        pub_date = item.get("published_date", "")

        if url and url in previous_urls:
            print(f"  [{abbr.upper()}] DEDUP: skipping {url[:80]}")
            continue

        if pub_date and pub_date < CUTOFF:
            print(f"  [{abbr.upper()}] STALE: skipping ({pub_date} < {CUTOFF})")
            continue

        filtered.append(item)

    if len(filtered) < original_count:
        print(f"  [{abbr.upper()}] Filtered: {original_count} → {len(filtered)} items")

    # Ensure item_ids
    for i, item in enumerate(filtered):
        if not item.get("item_id"):
            item["item_id"] = f"{abbr}-chatter-{TODAY_STR}-{i+1:03d}"

    # Build per-monitor output (same format downstream consumers expect)
    output_obj = {
        "_meta": {
            "schema_version": "chatter-v1.0",
            "monitor_slug": slug,
            "generated_at": NOW.isoformat().replace("+00:00", "Z"),
            "data_date": TODAY_STR,
            "item_count": len(filtered),
            "citations": citations,
            "source": "unified-chatter",
            "coverage_note": f"Top signals for {abbr.upper()} — from unified daily scan"
        },
        "items": filtered
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    output_json = json.dumps(output_obj, indent=2, ensure_ascii=False)
    out_dated.write_text(output_json, encoding="utf-8")
    out_latest.write_text(output_json, encoding="utf-8")

    total_items += len(filtered)
    print(f"✅ {abbr.upper()}: {len(filtered)} items → {out_dated}")
    for item in filtered[:3]:
        print(f"   [{item.get('source_tier','?')}] {item.get('title','')[:70]}")

print(f"\n✅ Unified Chatter complete: {total_items} items across 7 monitors")

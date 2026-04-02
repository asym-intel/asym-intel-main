#!/usr/bin/env python3
"""
WDM Reasoner — Deterioration Pattern Analysis
GitHub Actions script. Runs Sunday 20:00 UTC.

Loads:
  - persistent-state.json (active country registry + mimicry chains + integrity flags)
  - pipeline/weekly/weekly-latest.json (this week's deep research)
  - pipeline/daily/daily-latest.json (most recent Collector candidates)

Feeds all three as context to sonar-deep-research for deterioration pattern
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/democratic-integrity/reasoner/reasoner-latest.json
  pipeline/monitors/democratic-integrity/reasoner/reasoner-YYYY-MM-DD.json

The WDM Analyst reads this at Step 0E before applying methodology.

sonar-deep-research is correct here: it reasons over documents YOU provide.
It does NOT search the web. The structured JSON is the document.
"""

import os
import json
import datetime
import pathlib
import requests
import sys
import re

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY   = os.environ["PPLX_API_KEY"]
MODEL     = "sonar-deep-research"
TODAY_STR = datetime.date.today().isoformat()
OUT_DIR   = pathlib.Path("pipeline/monitors/democratic-integrity/reasoner")
OUT_LATEST = OUT_DIR / "reasoner-latest.json"
OUT_DATED  = OUT_DIR / f"reasoner-{TODAY_STR}.json"

# ── Guard ──────────────────────────────────────────────────────────────────────

if OUT_DATED.exists():
    print(f"GUARD: Reasoner already ran today ({TODAY_STR}). Exiting.")
    sys.exit(0)

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

persistent  = load_json_file(
    "static/monitors/democratic-integrity/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/democratic-integrity/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/democratic-integrity/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for deterioration pattern reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: active country heatmap, mimicry chains, integrity flags
heatmap_rapid   = persistent.get("rapid_decay", [])
heatmap_watchlist = persistent.get("watchlist", [])
heatmap_recovery = persistent.get("recovery", [])
mimicry_chains  = persistent.get("mimicry_chains", [])
integrity_flags = persistent.get("institutional_integrity_flags", [])

# From weekly research: erosion developments, electoral watch, autocratic export
weekly_developments = weekly.get("erosion_developments", []) if weekly else []
weekly_electoral    = weekly.get("electoral_watch", []) if weekly else []
weekly_export       = weekly.get("autocratic_export", []) if weekly else []
weekly_actors       = weekly.get("actor_tracker", []) if weekly else []

# From daily Collector: Tier 0 candidate findings
daily_findings = daily.get("findings", []) if daily else []
daily_below    = daily.get("below_threshold", []) if daily else []

print(f"Loaded: {len(heatmap_rapid)} rapid decay, {len(heatmap_watchlist)} watchlist, "
      f"{len(heatmap_recovery)} recovery countries")
print(f"Mimicry chains: {len(mimicry_chains)} | Integrity flags: {len(integrity_flags)}")
print(f"Weekly developments: {len(weekly_developments)} | Electoral: {len(weekly_electoral)}")
print(f"Daily Collector: {len(daily_findings)} candidates, {len(daily_below)} below threshold")

# ── Build the reasoning prompt ─────────────────────────────────────────────────

context_json = json.dumps({
    "heatmap_rapid_decay": heatmap_rapid,
    "heatmap_watchlist": heatmap_watchlist,
    "heatmap_recovery": heatmap_recovery,
    "mimicry_chains": mimicry_chains,
    "institutional_integrity_flags": integrity_flags[-20:],  # last 20
    "weekly_erosion_developments": weekly_developments,
    "weekly_electoral_watch": weekly_electoral,
    "weekly_autocratic_export": weekly_export,
    "weekly_actor_tracker": weekly_actors,
    "daily_collector_findings": daily_findings,
    "daily_below_threshold": daily_below
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: rapid decay > watchlist > recovery > mimicry > weekly > daily
    context_json = json.dumps({
        "heatmap_rapid_decay": heatmap_rapid[:15],
        "heatmap_watchlist": heatmap_watchlist[:10],
        "mimicry_chains": mimicry_chains[:8],
        "institutional_integrity_flags": integrity_flags[-10:],
        "weekly_erosion_developments": weekly_developments[:10],
        "weekly_electoral_watch": weekly_electoral[:5],
        "daily_collector_findings": daily_findings[:8]
    }, indent=2)[:MAX_CONTEXT]

prompt = f"""You are an expert democratic erosion analyst performing deep reasoning over
structured intelligence data from the World Democracy Monitor (WDM).

You have been provided with:
1. Active country heatmap (rapid decay, watchlist, recovery)
2. Mimicry chains (documented spread of authoritarian legislative templates)
3. Institutional integrity flags
4. This week's erosion developments from deep research
5. Electoral watch items
6. Daily Collector pre-verified candidate findings

Your task is to reason deeply over this structured data and return analytical
conclusions as JSON. You are NOT searching the web — reason only over the
data provided below.

ANALYTICAL TASKS:

A. SEVERITY CONFIDENCE REVIEW
For each rapid decay AND watchlist country, assess whether the accumulated
evidence supports upgrading or downgrading the severity score or status:
- Review all developments, flags, and daily findings for this country
- Check for corroboration across multiple source tiers
- Apply WDM severity formula: Score = A + B + C + (2.5 - D)
  A = LDI Trajectory (0–2.5), B = Institutional Breadth (0–2.5),
  C = Repression Severity (0–2.5), D = Resilience INVERTED (0–2.5)
- Recommend score change only if substantiated by at least 2 sources
- Mark as "unchanged" if no new evidence warrants a change

B. MIMICRY CHAIN LINKAGE DETECTION
Identify whether any new developments (weekly or daily) show patterns
consistent with existing mimicry chains or initiate new ones:
- Same legislative template across countries (foreign agent law, NGO restrictions, etc.)
- Advisory or technical support from an established autocratic exporter
- Venice Commission or OSCE unfavourable opinion on identical or near-identical provisions
- Mark as "continuation" if it extends an existing chain, "new_chain" if novel pattern

C. WATCHLIST THRESHOLD ASSESSMENT
For watchlist countries: assess whether any have crossed the promotion threshold:
  → Rapid Decay: score > 5.0 on two consecutive assessments AND 2+ pillars under attack
  → If threshold crossed: recommend promotion with specific triggering evidence
For rapid decay countries: assess whether any show recovery indicators:
  → Recovery: net positive trajectory maintained for 2+ consecutive weeks
  → Specific institutional improvements (not just rhetoric)

D. CROSS-MONITOR ESCALATION FLAGS
Identify findings that should be flagged to adjacent monitors:
- SCEM: Democratic erosion creating state fragility, enabling coups, or accompanying conflict
- FCW: FIMI operations targeting electoral processes or democratic institutions
- ESA: EU/candidate country democratic norm violations with EU institutional consequences
- AGM: AI tools deployed for state surveillance, censorship, or election manipulation

E. CONTESTED FINDINGS
Flag any country or event where the evidence is contradictory or where two
sources support different assessments of trajectory. These need human review.

STRUCTURED DATA:
{context_json}

Return ONLY valid JSON — no markdown, no prose, no code fences:

{{
  "_meta": {{
    "schema_version": "reasoner-v1.0",
    "monitor_slug": "democratic-integrity",
    "job_type": "deterioration-pattern-reasoning",
    "generated_at": "{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
    "data_date": "{TODAY_STR}",
    "countries_reviewed": <integer>,
    "candidates_reviewed": <integer>
  }},
  "severity_reviews": [
    {{
      "country": "<country name>",
      "current_severity": <current score>,
      "recommended_severity": <recommended score or UNCHANGED>,
      "current_status": "<rapid_decay|watchlist|recovery>",
      "recommended_status": "<rapid_decay|watchlist|recovery|UNCHANGED>",
      "recommendation": "<upgrade|downgrade|promote_to_rapid_decay|promote_to_watchlist|recovery|unchanged>",
      "reasoning": "<2-3 sentences explaining the evidence basis>",
      "key_evidence": ["<evidence item 1>", "<evidence item 2>"],
      "contradictory_evidence": "<any evidence pointing the other way, or null>",
      "needs_human_review": <true|false>
    }}
  ],
  "mimicry_chain_detections": [
    {{
      "development_id_or_country": "<from weekly/daily data>",
      "chain_type": "<continuation|new_chain>",
      "template_source": "<Hungary|Russia|China|Turkey|null>",
      "target_country": "<country>",
      "matches_existing_chain": "<existing chain name or null>",
      "match_basis": "<legislation|advisory|infrastructure|narrative>",
      "confidence": "<High|Medium|Low>",
      "reasoning": "<why this appears to be mimicry>"
    }}
  ],
  "watchlist_threshold_assessments": [
    {{
      "country": "<watchlist country>",
      "threshold_crossed": <true|false>,
      "recommended_action": "<promote_to_rapid_decay|hold|monitor>",
      "triggering_evidence": "<specific development that crosses threshold, or null>",
      "consecutive_weeks_above_threshold": <integer or null>,
      "confidence": "<High|Medium|Low>"
    }}
  ],
  "cross_monitor_escalation_flags": [
    {{
      "target_monitor": "<scem|fcw|esa|agm>",
      "flag_type": "<state_fragility|electoral_fimi|eu_backsliding|ai_repression>",
      "country": "<country>",
      "summary": "<what should be flagged and why>",
      "source_development_or_country": "<development_id or country name>",
      "urgency": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "contested_findings": [
    {{
      "country": "<country>",
      "contradiction": "<what is contradictory>",
      "source_a": "<one view + source>",
      "source_b": "<conflicting view + source>",
      "recommended_action": "<hold|escalate|downgrade>"
    }}
  ],
  "analyst_briefing": "<200-300 word summary for the WDM Analyst. Cover: key severity changes recommended, important mimicry detections, watchlist threshold assessments, cross-monitor flags. Written in cold analytical register.>"
}}"""

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for deterioration pattern reasoning...")
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
        "temperature": 0.1,
    },
    timeout=300,
)
response.raise_for_status()

api_response = response.json()
raw_content  = api_response["choices"][0]["message"]["content"]

print(f"Response received. Tokens: {api_response.get('usage', {}).get('total_tokens', 'unknown')}")

# ── Parse ──────────────────────────────────────────────────────────────────────

# Robust JSON extraction — strip fences, find outermost { }
clean = raw_content.strip()
if clean.startswith("```"):
    clean = re.sub(r'^```(?:json)?[ \t]*\n?', '', clean)
    clean = re.sub(r'\n?```[ \t]*$', '', clean).strip()
# Find outermost JSON object (handles any leading/trailing text)
brace_start = clean.find('{')
brace_end   = clean.rfind('}')
if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
    clean = clean[brace_start:brace_end+1]

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON: {e}")
    print("Raw output (first 500 chars):", raw_content[:500])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.txt").write_text(raw_content, encoding="utf-8")
    sys.exit(1)

# ── Validate ──────────────────────────────────────────────────────────────────

errors = []
meta = data.get("_meta", {})
if meta.get("schema_version") != "reasoner-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'reasoner-v1.0'")
if not data.get("analyst_briefing"):
    errors.append("analyst_briefing missing")

if errors:
    print(f"VALIDATION FAILED: {errors}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"debug-{TODAY_STR}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    sys.exit(1)

# ── Write ──────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)
output = json.dumps(data, indent=2, ensure_ascii=False)
OUT_DATED.write_text(output, encoding="utf-8")
OUT_LATEST.write_text(output, encoding="utf-8")

reviews   = data.get("severity_reviews", [])
mimicry   = data.get("mimicry_chain_detections", [])
watchlist = data.get("watchlist_threshold_assessments", [])
flags     = data.get("cross_monitor_escalation_flags", [])
contested = data.get("contested_findings", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Severity reviews: {len(reviews)} "
      f"({sum(1 for r in reviews if r.get('recommendation') != 'unchanged')} changes recommended)")
print(f"   Mimicry chain detections: {len(mimicry)}")
print(f"   Watchlist threshold assessments: {len(watchlist)} "
      f"({sum(1 for w in watchlist if w.get('threshold_crossed')) } crossed)")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

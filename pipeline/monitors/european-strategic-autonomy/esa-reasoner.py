#!/usr/bin/env python3
"""
ESA Reasoner — Domain Autonomy & Hybrid Threat Analysis
GitHub Actions script. Runs Tuesday 20:00 UTC.

Loads:
  - static/monitors/european-strategic-autonomy/data/persistent-state.json
      (active domain scores + hybrid threat registry)
  - pipeline/monitors/european-strategic-autonomy/weekly/weekly-latest.json
      (domain_developments + hybrid_threat_incidents from this week's deep research)
  - pipeline/monitors/european-strategic-autonomy/daily/daily-latest.json
      (most recent Collector findings array)

Feeds all three as context to sonar-deep-research for domain autonomy
reasoning and hybrid threat pattern analysis. Outputs structured analytical
recommendations to:
  pipeline/monitors/european-strategic-autonomy/reasoner/reasoner-latest.json
  pipeline/monitors/european-strategic-autonomy/reasoner/reasoner-YYYY-MM-DD.json

The ESA Analyst reads this at Step 0E before applying methodology.

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
OUT_DIR   = pathlib.Path("pipeline/monitors/european-strategic-autonomy/reasoner")
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

persistent = load_json_file(
    "static/monitors/european-strategic-autonomy/data/persistent-state.json",
    "persistent-state"
)
weekly     = load_json_file(
    "pipeline/monitors/european-strategic-autonomy/weekly/weekly-latest.json",
    "weekly research"
)
daily      = load_json_file(
    "pipeline/monitors/european-strategic-autonomy/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for domain autonomy reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: active domain scores + hybrid threat registry
active_domain_scores   = persistent.get("domain_scores", {})
hybrid_threat_registry = persistent.get("hybrid_threat_registry", [])[-20:]  # last 20 entries
actor_posture_log      = persistent.get("actor_posture_log", [])[-10:]

# From weekly research: domain_developments + hybrid_threat_incidents
weekly_domain_devs    = weekly.get("domain_developments", []) if weekly else []
weekly_hybrid_threats = weekly.get("hybrid_threat_incidents", []) if weekly else []
weekly_us_eu          = weekly.get("us_eu_tracker", {}) if weekly else {}

# From daily Collector: findings array
daily_findings = daily.get("findings", []) if daily else []

print(f"Loaded: {len(active_domain_scores)} domain scores, "
      f"{len(hybrid_threat_registry)} threat registry entries")
print(f"Weekly research: {len(weekly_domain_devs)} domain developments, "
      f"{len(weekly_hybrid_threats)} hybrid threat incidents")
print(f"Daily Collector: {len(daily_findings)} findings")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "active_domain_scores":    active_domain_scores,
    "hybrid_threat_registry":  hybrid_threat_registry,
    "actor_posture_log":       actor_posture_log,
    "weekly_domain_developments": weekly_domain_devs,
    "weekly_hybrid_threat_incidents": weekly_hybrid_threats,
    "weekly_us_eu_tracker":    weekly_us_eu,
    "daily_collector_findings": daily_findings,
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: domain scores > threat registry > weekly > daily
    context_json = json.dumps({
        "active_domain_scores":    active_domain_scores,
        "hybrid_threat_registry":  hybrid_threat_registry[-10:],
        "weekly_domain_developments": weekly_domain_devs[:15],
        "weekly_hybrid_threat_incidents": weekly_hybrid_threats[:10],
        "weekly_us_eu_tracker":    weekly_us_eu,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]

prompt = f"""You are an expert European strategic autonomy analyst performing deep reasoning over
structured intelligence data from the European Strategic Autonomy Monitor.

You have been provided with:
1. Active domain autonomy scores (from persistent-state.json)
2. Hybrid threat registry — recent registered incidents
3. Actor posture log — prior actor assessments
4. New domain developments from this week's deep research
5. New hybrid threat incidents identified this week
6. US-EU tracker (weekly update)
7. Daily Collector pre-verified findings

Your task is to reason deeply over this structured data and return analytical
conclusions as JSON. You are NOT searching the web — reason only over the
data provided below.

ANALYTICAL TASKS:

A. DOMAIN AUTONOMY SCORE REVIEW
For each domain (defence / energy / tech / trade / diplomatic), review the
accumulated evidence from weekly developments and daily findings, then
recommend whether to upgrade, downgrade, or hold the current autonomy score:
- Score scale: 1 (fully dependent / highly vulnerable) to 5 (fully autonomous / resilient)
- Upgrade requires: sustained positive developments across 2+ sources in this domain
- Downgrade requires: confirmed setback, dependency increase, or structural reversal
- Hold: insufficient evidence to move; weekly noise should not move scores
- Provide specific evidence items supporting the recommendation
- Flag if the score movement is episodic (single-week signal) vs. structural

B. HYBRID THREAT PATTERN DETECTION
Review new hybrid threat incidents against the registered threat registry:
- Identify whether new incidents show patterns consistent with ongoing operations
  (same actor + TTP fingerprint, same target sector, same infrastructure)
- Mark as "continuation" if strong match with registered operation
- Mark as "net_new" if no prior registry match — flag for persistent-state addition
- Mark as "possible_linkage" if partial match requiring further evidence
- Note actor attribution confidence for each

C. ACTOR POSTURE CHANGE DETECTION
Based on combined weekly and daily data, identify posture changes for:
- Russia: hybrid operations tempo, FIMI activity, energy weaponisation
- China: technology dependency leverage, economic coercion, interference in EU
- US (adversarial/competitive framing): transatlantic pressure, trade leverage, NATO commitment signals
- Turkey: EU accession dynamics, NATO leverage, bilateral friction
- Gulf states: investment patterns, energy diplomacy, influence operations
Flag any actor showing: increased operational tempo, new TTPs or targeting, doctrine evolution,
or notable absence where activity was expected.

D. CROSS-MONITOR ESCALATION FLAGS
Identify findings that should be flagged to adjacent monitors:
- wdm (democratic-integrity): foreign interference in EU elections or member-state institutions
- scem (conflict-escalation): hybrid operations with direct conflict escalation nexus
- gmm (macro-monitor): economic coercion, sanctions enforcement, or commodity leverage with macro implications
- fcw (fimi-cognitive-warfare): FIMI campaigns targeting EU narrative space, institutions, or member-state media
- agm (ai-governance): AI capabilities in hybrid operations, tech dependency, dual-use AI

E. CONTESTED FINDINGS
Flag any finding where evidence is contradictory or where two sources support
different conclusions about actor attribution or domain score direction.
These require human review before the analyst applies final methodology.

STRUCTURED DATA:
{context_json}

Return ONLY valid JSON — no markdown, no prose, no code fences:

{{
  "_meta": {{
    "schema_version": "reasoner-v1.0",
    "monitor_slug": "european-strategic-autonomy",
    "job_type": "domain-autonomy-reasoning",
    "generated_at": "{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
    "data_date": "{TODAY_STR}",
    "domains_reviewed": 5,
    "threats_reviewed": <integer>
  }},
  "domain_score_reviews": [
    {{
      "domain": "<defence|energy|tech|trade|diplomatic>",
      "current_score": <integer 1-5>,
      "recommended_score": <integer 1-5 or same as current>,
      "recommendation": "<upgrade|downgrade|hold>",
      "reasoning": "<2-3 sentences explaining the evidence basis for this recommendation>",
      "key_evidence": ["<evidence item 1>", "<evidence item 2>"],
      "contradictory_evidence": "<any evidence pointing the other way, or null>",
      "episodic_flag": <true|false>,
      "needs_human_review": <true|false>
    }}
  ],
  "threat_pattern_detections": [
    {{
      "incident_id": "<new incident id from weekly/daily data>",
      "matches_registry_id": "<registered threat id or null>",
      "match_type": "<continuation|net_new|possible_linkage>",
      "match_basis": "<actor-ttp|infrastructure|targeting-pattern|narrative|null>",
      "confidence": "<High|Medium|Low>",
      "reasoning": "<why these appear linked or why this is net new>",
      "flag_for_registry": <true|false>
    }}
  ],
  "actor_posture_changes": [
    {{
      "actor": "<Russia|China|US|Turkey|Gulf>",
      "change_type": "<increased_tempo|decreased_tempo|new_ttp|new_targeting|doctrine_evolution|notable_absence>",
      "observation": "<what was observed in the data>",
      "significance": "<why this matters analytically for European strategic autonomy>",
      "confidence": "<High|Medium|Low>"
    }}
  ],
  "cross_monitor_escalation_flags": [
    {{
      "target_monitor": "<wdm|scem|gmm|fcw|agm>",
      "flag_type": "<electoral_interference|hybrid_conflict_nexus|economic_coercion|fimi_eu_targeting|ai_hybrid_ops>",
      "summary": "<what should be flagged and why>",
      "source_incident_or_finding": "<incident_id or domain development title>",
      "urgency": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "contested_findings": [
    {{
      "finding_id": "<incident id or domain development title>",
      "contradiction": "<what is contradictory>",
      "source_a": "<one view + source>",
      "source_b": "<conflicting view + source>",
      "recommended_action": "<hold|escalate|downgrade>"
    }}
  ],
  "analyst_briefing": "<200-300 word summary for the ESA Analyst. Cover: key domain score changes recommended and evidence basis, important hybrid threat pattern detections, actor posture changes of note, cross-monitor flags requiring action. Written in cold analytical register.>"
}}"""

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for domain autonomy reasoning...")
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
    # Remove opening fence line
    clean = re.sub(r'^```(?:json)?[ \t]*\n?', '', clean)
    # Remove closing fence
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

# ── Validate ───────────────────────────────────────────────────────────────────

errors = []
meta = data.get("_meta", {})
if meta.get("schema_version") != "reasoner-v1.0":
    errors.append(f"schema_version '{meta.get('schema_version')}' — expected 'reasoner-v1.0'")
if meta.get("monitor_slug") != "european-strategic-autonomy":
    errors.append(f"monitor_slug '{meta.get('monitor_slug')}' — expected 'european-strategic-autonomy'")
if not data.get("domain_score_reviews"):
    errors.append("domain_score_reviews missing — required for analyst methodology")
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

score_reviews = data.get("domain_score_reviews", [])
threat_pats   = data.get("threat_pattern_detections", [])
flags         = data.get("cross_monitor_escalation_flags", [])
contested     = data.get("contested_findings", [])
posture       = data.get("actor_posture_changes", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Domain score reviews: {len(score_reviews)} "
      f"({sum(1 for r in score_reviews if r.get('recommendation') != 'hold')} changes recommended)")
print(f"   Threat pattern detections: {len(threat_pats)} "
      f"({sum(1 for t in threat_pats if t.get('match_type') == 'net_new')} net new)")
print(f"   Actor posture changes: {len(posture)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

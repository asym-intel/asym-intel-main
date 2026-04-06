#!/usr/bin/env python3
"""
AGM Reasoner — Capability & Governance Reasoning
GitHub Actions script. Runs Thursday 20:00 UTC.

Loads:
  - static/monitors/ai-governance/data/persistent-state.json
      (capability registry, regulatory milestones, risk vectors)
  - pipeline/monitors/ai-governance/weekly/weekly-latest.json
      (weekly_developments, capability_tier_tracker, regulatory_framework_tracker)
  - pipeline/monitors/ai-governance/daily/daily-latest.json
      (findings array)

Feeds all three as context to sonar-deep-research for capability and governance
reasoning. Outputs structured analytical recommendations to:
  pipeline/monitors/ai-governance/reasoner/reasoner-latest.json
  pipeline/monitors/ai-governance/reasoner/reasoner-YYYY-MM-DD.json

The AGM Analyst reads this at Step 0E before applying methodology.

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
OUT_DIR   = pathlib.Path("pipeline/monitors/ai-governance/reasoner")
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
    "static/monitors/ai-governance/data/persistent-state.json",
    "persistent-state"
)
weekly      = load_json_file(
    "pipeline/monitors/ai-governance/weekly/weekly-latest.json",
    "weekly research"
)
daily       = load_json_file(
    "pipeline/monitors/ai-governance/daily/daily-latest.json",
    "daily Collector"
)

if not persistent:
    print("ERROR: persistent-state.json is required for capability-governance reasoning. Cannot continue.")
    sys.exit(1)

# ── Extract relevant sections ──────────────────────────────────────────────────

# From persistent-state: capability registry, regulatory milestones, risk vectors
capability_registry    = persistent.get("capability_registry", [])
regulatory_milestones  = persistent.get("regulatory_milestones", [])
risk_vectors           = persistent.get("risk_vectors", [])

# From weekly research: developments, capability tracker, regulatory tracker
weekly_developments     = weekly.get("weekly_developments", []) if weekly else []
weekly_cap_tracker      = weekly.get("capability_tier_tracker", {}) if weekly else {}
weekly_reg_tracker      = weekly.get("regulatory_framework_tracker", {}) if weekly else {}
weekly_ai_fimi          = weekly.get("ai_fimi_layer", {}) if weekly else {}

# From daily Collector: findings array
daily_findings   = daily.get("findings", []) if daily else []

print(f"Loaded: {len(capability_registry)} capability registry entries, "
      f"{len(regulatory_milestones)} regulatory milestones, "
      f"{len(risk_vectors)} risk vectors")
print(f"Weekly research: {len(weekly_developments)} developments, "
      f"{len(weekly_cap_tracker)} labs in capability tracker, "
      f"{len(weekly_reg_tracker)} frameworks in regulatory tracker")
print(f"Daily Collector: {len(daily_findings)} findings")

# ── Build the reasoning prompt ────────────────────────────────────────────────

context_json = json.dumps({
    "capability_registry": capability_registry,
    "regulatory_milestones": regulatory_milestones,
    "risk_vectors": risk_vectors,
    "weekly_developments": weekly_developments,
    "weekly_capability_tier_tracker": weekly_cap_tracker,
    "weekly_regulatory_framework_tracker": weekly_reg_tracker,
    "weekly_ai_fimi_layer": weekly_ai_fimi,
    "daily_collector_findings": daily_findings,
}, indent=2)

# Truncate if too large (sonar-deep-research has context limits)
MAX_CONTEXT = 40000
if len(context_json) > MAX_CONTEXT:
    print(f"Context truncated: {len(context_json)} → {MAX_CONTEXT} chars")
    # Prioritise: capability registry > regulatory milestones > risk vectors > weekly > daily
    context_json = json.dumps({
        "capability_registry": capability_registry[:15],
        "regulatory_milestones": regulatory_milestones[-10:],
        "risk_vectors": risk_vectors[:10],
        "weekly_developments": weekly_developments[:15],
        "weekly_capability_tier_tracker": weekly_cap_tracker,
        "weekly_regulatory_framework_tracker": weekly_reg_tracker,
        "daily_collector_findings": daily_findings[:10]
    }, indent=2)[:MAX_CONTEXT]

prompt = f"""You are an expert AI governance and capability analyst performing deep reasoning over
structured intelligence data from the AI Governance Monitor at asym-intel.info.

You have been provided with:
1. Capability registry (from persistent-state.json — tracked frontier labs and systems)
2. Regulatory milestones (from persistent-state.json — EU AI Act, US EO, UK, China timeline)
3. Risk vectors (from persistent-state.json — known safety and misuse risk patterns)
4. Weekly research findings (this week's developments, capability tracker, regulatory tracker)
5. Daily Collector findings (most recent pre-verified candidates)

Your task is to reason deeply over this structured data and return analytical
conclusions as JSON. You are NOT searching the web — reason only over the
data provided below.

ANALYTICAL TASKS:

A. CAPABILITY TIER REVIEW
For each tracked frontier lab or system in the capability registry, review this
week's evidence (weekly_capability_tier_tracker + weekly_developments) and recommend:
- tier_upgrade: evidence supports a meaningful capability advance — justify with specific findings
- tier_downgrade: evidence suggests retreat, capability gap, or safety limitation
- hold: insufficient new evidence to change tier
Apply conservative evidentiary threshold:
  Confirmed = 2+ independent sources corroborating the capability claim
  Assessed = single lab announcement or single source — label as lab-reported, not independently verified
Do NOT upgrade on single-lab benchmark announcements alone.

B. REGULATORY MILESTONE TRACKING
For each regulatory framework in regulatory_milestones, assess this week's evidence:
- milestone_crossed: a compliance deadline, enforcement action, or legislative step completed
- slippage: a previously expected milestone appears delayed or has been missed
- acceleration: a framework is moving faster than anticipated
- on_track: no material change
Flag which framework and jurisdiction is affected. Note durability: distinguish
executive orders (revocable) from legislation (durable).

C. RISK VECTOR PATTERN DETECTION
For each risk vector in persistent-state, assess whether this week's safety incidents,
misuse cases, or agentic failure reports show patterns consistent with that vector:
- match: new finding is consistent with a known risk vector — cite the specific finding
- escalation: pattern frequency or severity has increased this week
- no_match: no new corroborating evidence
New risk vectors not previously registered should be flagged as emerging_vector.

D. CROSS-MONITOR ESCALATION FLAGS
Identify findings that should be flagged to adjacent monitors. Target monitors:
- fcw (fimi-cognitive-warfare): AI-enabled FIMI operations with documented operational AI use
- scem (conflict-escalation): AI applications in active conflict theatres
- wdm (democratic-integrity): AI tools in electoral manipulation or democratic interference
- esa (european-strategic-autonomy): AI chip supply chain, tech sovereignty, EU AI dependency
- erm (environmental-risks): AI energy consumption, data centre environmental footprint

D. CROSS-MONITOR ESCALATION FLAGS
Only flag if evidence is direct and specific — do not flag speculative or theoretical risks.
Include urgency: HIGH for imminent or active events, MEDIUM for developing trends,
LOW for background signals.

E. CONTESTED FINDINGS
Flag any capability claim or governance development where:
- Lab announcement conflicts with independent benchmark assessment
- Two credible sources support different conclusions about the same development
- A regulatory claim cannot be verified against official sources
These require human review before the AGM Analyst applies methodology.

STRUCTURED DATA:
{context_json}

Return ONLY valid JSON — no markdown, no prose, no code fences:

{{
  "_meta": {{
    "schema_version": "reasoner-v1.0",
    "monitor_slug": "ai-governance",
    "job_type": "capability-governance-reasoning",
    "generated_at": "{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
    "data_date": "{TODAY_STR}",
    "labs_reviewed": <integer — count of labs reviewed in capability tier review>,
    "frameworks_reviewed": <integer — count of regulatory frameworks reviewed>
  }},
  "capability_tier_reviews": [
    {{
      "lab_or_system": "<Anthropic|OpenAI|Google_DeepMind|Meta|xAI|Chinese_labs|other>",
      "current_tier": "<existing tier or posture from registry>",
      "recommended_tier": "<upgraded|downgraded|hold — or specific tier label if applicable>",
      "recommendation": "<upgrade|downgrade|hold>",
      "reasoning": "<2-3 sentences explaining the evidence basis for this recommendation>",
      "key_evidence": ["<evidence item 1>", "<evidence item 2>"],
      "evidentiary_note": "<Confirmed|Assessed — note if single-lab benchmark de-weighting applied>",
      "contradictory_evidence": "<any evidence pointing the other way, or null>",
      "needs_human_review": <true|false>
    }}
  ],
  "regulatory_milestone_updates": [
    {{
      "framework": "<EU_AI_Act|US_EO|UK|China>",
      "jurisdiction": "<EU|US|UK|China>",
      "status": "<milestone_crossed|slippage|acceleration|on_track>",
      "milestone_description": "<what milestone is affected>",
      "evidence": "<what this week's data shows>",
      "durability_note": "<executive_order|legislation|regulatory_instrument — flag if revocable>",
      "source_reference": "<relevant finding id or development title from weekly data>"
    }}
  ],
  "risk_pattern_detections": [
    {{
      "risk_vector": "<risk vector id or label from persistent-state>",
      "detection_type": "<match|escalation|no_match|emerging_vector>",
      "observation": "<what was observed in this week's data>",
      "supporting_findings": ["<finding title or id>"],
      "significance": "<why this pattern matters analytically>",
      "confidence": "<High|Medium|Low>"
    }}
  ],
  "lab_posture_changes": [
    {{
      "lab": "<Anthropic|OpenAI|Google_DeepMind|Meta|xAI|Chinese_labs>",
      "change_type": "<increased_capability_tempo|decreased_capability_tempo|new_safety_stance|new_deployment_policy|notable_absence>",
      "observation": "<what was observed>",
      "significance": "<why this matters analytically>",
      "confidence": "<High|Medium|Low>"
    }}
  ],
  "cross_monitor_escalation_flags": [
    {{
      "target_monitor": "<fcw|scem|wdm|esa|erm>",
      "flag_type": "<ai_fimi_operational|ai_in_conflict|electoral_ai|tech_sovereignty|ai_energy_footprint>",
      "summary": "<what should be flagged and why — specific, not speculative>",
      "source_finding": "<development title or daily finding id>",
      "urgency": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "contested_findings": [
    {{
      "finding_id": "<development title or candidate id>",
      "contradiction": "<what is contradictory>",
      "source_a": "<one view + source>",
      "source_b": "<conflicting view + source>",
      "recommended_action": "<hold|escalate|downgrade>"
    }}
  ],
  "analyst_briefing": "<200-300 word summary for the AGM Analyst. Cover: key capability tier changes recommended and their evidentiary basis, regulatory milestone developments, notable risk vector patterns, cross-monitor escalation flags, and any contested findings requiring human review. Written in cold analytical register.>"
}}"""

# ── Call Perplexity API ────────────────────────────────────────────────────────

print(f"Calling {MODEL} for capability-governance reasoning...")
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
if meta.get("monitor_slug") != "ai-governance":
    errors.append(f"monitor_slug '{meta.get('monitor_slug')}' — expected 'ai-governance'")
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

tier_reviews    = data.get("capability_tier_reviews", [])
milestone_upd   = data.get("regulatory_milestone_updates", [])
risk_detections = data.get("risk_pattern_detections", [])
flags           = data.get("cross_monitor_escalation_flags", [])
contested       = data.get("contested_findings", [])
posture         = data.get("lab_posture_changes", [])

print(f"✅ Written: {OUT_DATED}")
print(f"   Capability tier reviews: {len(tier_reviews)} "
      f"({sum(1 for r in tier_reviews if r.get('recommendation') != 'hold')} changes recommended)")
print(f"   Regulatory milestone updates: {len(milestone_upd)}")
print(f"   Risk pattern detections: {len(risk_detections)}")
print(f"   Lab posture changes: {len(posture)}")
print(f"   Cross-monitor flags: {len(flags)}")
print(f"   Contested findings: {len(contested)}")
print(f"   Briefing: {len(data.get('analyst_briefing',''))} chars")

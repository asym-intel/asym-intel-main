# SYNTHESISER-SPEC.md

## Platform-First Fix Rule

**Before fixing any bug, gap, or prompt issue — always ask:**

> "Is this specific to one monitor/file, or is it likely present across multiple monitors, workflows, scripts, or pages?"

If the answer is "likely platform-wide" or "I'm not sure":
1. **Audit first** — check all affected monitors/files before touching anything
2. **Fix the spec** — update ANALYST-CRON-SPEC.md or SYNTHESISER-SPEC.md to reflect the correct behaviour
3. **Apply platform-wide** — fix all affected files in one pass, not one at a time as they surface

**Never:**
- Fix one monitor's prompt and leave the same gap in the other 6
- Patch a workflow file without checking if the same pattern exists in all 14 workflow files
- Update a Python script for one monitor without checking the equivalent scripts for all 7

**The cost of reactive patching is high:** each gap found in one monitor that later turns out to affect all 7 means 6 additional session tool calls, 6 additional commits, and 6 additional opportunities for inconsistency. One properly scoped fix costs less than two reactive ones.

**When a gap IS monitor-specific** (e.g. SCEM deviation calculation, WDM living knowledge fields) — document why it's specific before fixing, so future sessions don't audit unnecessarily.


## Canonical Specification — Synthesiser Prompts
## Asymmetric Intelligence | asym-intel.info
### Version: 1.0 | Date: 2026-04-07
### Governs: All 7 monitor Synthesiser prompts (Layer 1C)

---

## Purpose

This document is the single source of truth for every Synthesiser prompt across
all seven monitors. When a gap is found in any Synthesiser prompt:

1. Fix this spec first.
2. Then make every monitor synthesiser conform to it.

One spec update → one conformance pass across all monitors.
Do not patch individual synthesiser prompts in isolation.

**Companion spec:** `ANALYST-CRON-SPEC.md` — governs Analyst cron prompts.

**Governing architecture:** `COLLECTOR-ANALYST-ARCHITECTURE.md` (Version 2.2).

---

## 1. Role

### 1.1 What the Synthesiser IS

The Synthesiser is a **GitHub Actions workflow** (Layer 1C), not a Computer cron.
It runs on a schedule before the Analyst cron for the same monitor.

The Synthesiser is a **reasoning engine over provided documents**.
It is **not a research agent** — it does not search the web.
It reads pipeline JSON files and methodology content embedded in the API call,
then produces a structured synthesis JSON for the Analyst to use as a primary draft.

All Synthesiser outputs are **advisory** and **preliminary**. The Analyst owns
final methodology, state, and publication.

### 1.2 Model

All Synthesisers use **`sonar-deep-research`**.

`sonar-deep-research` reasons over provided documents. It does **not** perform
live web search. The synthesiser Python script must explicitly load pipeline JSON
files and methodology content and embed them in the API request body before calling
the model.

### 1.3 What the Synthesiser Reads

Inputs must be explicitly loaded and embedded by the synthesiser Python script:

1. **Primary:** `pipeline/monitors/{slug}/daily/daily-latest.json` — Collector output
2. **Secondary:** `pipeline/monitors/{slug}/weekly/weekly-latest.json` (if present)
3. **Tertiary:** `pipeline/monitors/{slug}/reasoner/reasoner-latest.json` (if present — legacy)
4. **Methodology:** Relevant excerpts from `docs/methodology/{slug}-full.md`

The Synthesiser script reads these from the repo using `gh api` and injects their
content into the `sonar-deep-research` API request.

**GH_TOKEN (Gap 1):** The workflow that runs the synthesiser script must include
`GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in its `env` block, because the script
uses `subprocess` calls to `gh api` to read these files.

### 1.4 What the Synthesiser Writes

Writes **one file only**:
- `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`

The GitHub Actions workflow commits this file after the script completes.

The Synthesiser does **not** write to:
- `static/monitors/{slug}/data/` (Analyst-only paths)
- `content/monitors/{slug}/` (Analyst-only paths)
- `pipeline/monitors/{slug}/daily/` or `weekly/` (Collector/Weekly Research only)
- `archive.json` or `persistent-state.json` (Analyst-only)

### 1.5 Schedule

Synthesisers run weekly, before the Analyst cron for the same monitor.
Target: same day as Collector, +2 hours minimum (allow Collector to complete).

| Monitor | Synthesiser UTC | Analyst UTC | Gap |
|---------|----------------|-------------|-----|
| WDM | Sun 21:00 | Mon 06:00 | +9h |
| GMM | Mon 20:00 | Tue 08:00 | +12h |
| ESA | Tue 21:00 | Wed 19:00 | +22h |
| FCW | Wed 10:00 | Thu 09:00 | +23h |
| AGM | Thu 10:00 | Fri 09:00 | +23h |
| ERM | Fri 08:00 | Sat 05:00 | +21h |
| SCEM | Sat 10:00 | Sun 18:00 | +8h |

Start new synthesisers with `workflow_dispatch` only.
Enable scheduled trigger only after manual validation of the first 2+ runs.

### 1.6 Workflow and File Locations

```
Workflow:   .github/workflows/{slug}-synthesiser.yml
Script:     pipeline/monitors/{slug}/{slug}-synthesiser.py
Prompt:     pipeline/monitors/{slug}/{slug}-synthesiser-api-prompt.txt
Output:     pipeline/monitors/{slug}/synthesised/synthesis-latest.json
```

---

## 2. Required Output Fields (Universal)

Every Synthesiser must produce all of the following fields.
Monitor-specific additional fields are specified in Section 3.

### 2.1 `_meta` object

```json
"_meta": {
  "schema_version": "{monitor}-synthesis-v1.0",
  "research_model": "sonar-deep-research",
  "monitor_slug": "{slug}",
  "job_type": "synthesiser",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "data_date": "YYYY-MM-DD",
  "week_ending": "YYYY-MM-DD",
  "null_signal_week": false,
  "null_signal_reason": null,
  "finding_count": 0,
  "status": "complete"
}
```

Field notes:
- `schema_version` — `"{monitor}-synthesis-v1.0"` (e.g. `"gmm-synthesis-v1.0"`)
- `null_signal_week` — `true` only when all monitor-specific indicators are
  stable/green and no regime delta; Analyst may override
- `null_signal_reason` — required string when `null_signal_week: true`; null otherwise
- `finding_count` — count of distinct findings from daily-latest.json that informed synthesis
- `status` — `"complete"` | `"partial"` | `"null_signal"`

### 2.2 `lead_signal` object

```json
"lead_signal": {
  "headline": "string — max 120 chars, specific factual statement (not a regime label)",
  "domain": "string — monitor-specific domain or indicator name",
  "confidence_preliminary": "Confirmed | High | Assessed | Possible",
  "source_url": "string — primary source URL"
}
```

**Rule:** `headline` must be a specific factual statement, not a status label.
- Correct: `"Liberation Day tariff package activates 10-percentage-point baseline surcharge on all US imports"`
- Wrong: `"Macro stress elevated"` or `"Escalation risk high"`

Maximum 120 characters.

The Analyst confirms or refines this lead_signal. If the Analyst disagrees,
they correct it with a note. The Analyst does not independently derive a new
lead_signal unless this field is null.

### 2.3 `key_judgments` array (3–5 items)

```json
"key_judgments": [
  {
    "id": "kj-001",
    "judgment": "string — specific, decision-useful analytical statement",
    "confidence_preliminary": "High | Assessed | Possible",
    "supporting_evidence": "string — specific data point from pipeline input",
    "trajectory": "string — direction of development"
  }
]
```

- Minimum 3, maximum 5 judgments
- All confidence values are `_preliminary` — Analyst finalises
- Never omit `_preliminary` suffix on confidence labels in synthesiser output
- `supporting_evidence` must reference specific content from the provided documents

### 2.4 `cross_monitor_candidates` array

```json
"cross_monitor_candidates": [
  {
    "target_monitor": "string — full slug (see Section 2.6)",
    "signal": "string — what the cross-monitor link is",
    "type": "string — category of cross-monitor relationship",
    "rationale": "string — why this link is analytically significant",
    "confidence_preliminary": "Low | Medium | High"
  }
]
```

The Analyst confirms, rejects, or expands these candidates when writing final
`cross_monitor_flags`. The Synthesiser produces **candidates only** — the Analyst
determines what becomes a published flag.

If no candidates this week, set to `[]` — do not omit the field.

### 2.5 `weekly_brief_draft` field

```json
"weekly_brief_draft": "string — 400–600 words, analytical narrative"
```

- 400–600 words (enforced — not a guideline)
- Opens with the monitor's key status indicator (stress regime, democratic health trend, etc.)
- Covers the main analytical developments in order of significance
- Analytical register (not journalistic, not hedged to uselessness)
- The Analyst edits this draft; does not rewrite from scratch without cause
- JSON string values must never contain apostrophes or contractions — use full words
  (e.g. `"does not"` not `"doesn't"`, `"this weeks"` not `"this week's"`)
  Apostrophes break JSON parsing.

### 2.6 Null Signal Week Handling

If `null_signal_week: true`:
- `null_signal_reason` must be a descriptive string explaining why
- `weekly_brief_draft` must still be present and explain the absence of signal
- Do not produce empty arrays without explanation — `cross_monitor_candidates: []` is
  acceptable only if accompanied by a `null_signal_reason`
- The Analyst may override a `null_signal_week` assessment if their methodology
  review finds a signal the Synthesiser missed

### 2.7 Cross-Monitor Slug Reference

All `target_monitor` values in `cross_monitor_candidates` must use these exact slugs:

```
fimi-cognitive-warfare        (FCW)
democratic-integrity          (WDM)
conflict-escalation           (SCEM)
european-strategic-autonomy   (ESA)
macro-monitor                 (GMM)
ai-governance                 (AGM)
environmental-risks           (ERM)
```

---

## 3. Monitor-Specific Required Fields

Each monitor's Synthesiser must produce these additional fields beyond the universal set.

### 3.1 GMM — Global Macro Monitor

**Slug:** `macro-monitor`

#### `stress_regime_preliminary`

```json
"stress_regime_preliminary": {
  "regime": "GREEN | AMBER | RED | CRITICAL | CRISIS",
  "conviction": "LOW | MEDIUM | HIGH | VERY HIGH",
  "system_average": 0.000,
  "global": "Green | Amber | Red | Crisis",
  "us": "Green | Amber | Red | Crisis",
  "eu": "Green | Amber | Red | Crisis",
  "china": "Green | Amber | Red | Crisis",
  "em_basket": "Green | Amber | Red | Crisis",
  "regime_delta": "Stable | Downgrade | Upgrade",
  "regime_change_evidence": "string or null"
}
```

Rules:
- Regime is conjunctive — requires evidence across at least two indicator domains
- `system_average` = arithmetic mean of indicator domain stress scores (Green=0, Amber=−0.33, Red=−0.66, Crisis=−1.0). Range: 0.0 to −1.0. CRITICAL threshold: below −0.50.
- `conviction`: 1 domain = LOW, 2–3 = MEDIUM, 4–5 = HIGH, 6 = VERY HIGH
- Regime change requires evidence in ≥2 domains

#### `indicator_domains` array (6 domains)

One entry per domain. All six must be present:

```json
{
  "domain": "growth_recession | inflation_central_bank | financial_stability | trade_tariff | currency_fx | sovereign_debt",
  "signal": "string — key development this week",
  "direction": "Deteriorating | Stable | Improving",
  "stress_level": "Green | Amber | Red",
  "key_data_point": "string — specific figure or event",
  "source": "string — IMF / BIS / WB / Fed / ECB / Other"
}
```

#### `central_bank_tracker` array

Per institution: `institution`, `posture` (Tightening / Neutral / Easing / Emergency), `last_action`, `next_meeting`, `forward_guidance`

#### `tariff_tracker` array

Per measure: `actor`, `target`, `measure`, `effective_date`, `status` (Announced / In force / Suspended / Retaliated), `macro_impact_assessment`

#### `tail_risks` array

Per risk: `id`, `risk`, `probability` (Low / Medium / High), `horizon` (Immediate / 30d / 90d / 6m), `trigger_condition`, `affected_domains`

### 3.2 WDM — World Democracy Monitor

**Slug:** `democratic-integrity`

#### `global_health_snapshot`

```json
{
  "overall_trend": "Improving | Stable | Declining | Accelerating decline",
  "countries_under_watch": 0,
  "new_alerts_this_week": 0,
  "lead_concern": "string"
}
```

#### `country_heatmap` array (preliminary)

Per country:
```json
{
  "country": "ISO 3166-1 alpha-3",
  "country_name": "string",
  "health_status": "Consolidated | Constrained | Backsliding | Crisis | Closed",
  "health_delta": "Improving | Stable | Declining",
  "vdem_ldi_preliminary": 0.0,
  "vdem_ldi_delta_12m": 0.0,
  "electoral_calendar": "string or null",
  "key_development": "string",
  "fimi_exposure": "None | Low | Medium | High",
  "resilience_indicators": ["string"]
}
```

Note: `vdem_ldi_preliminary` — use `score_preliminary` only; never assign final V-Dem scores.

#### `backsliding_alerts` array

Per alert: `country`, `alert_type`, `severity` (Watch / Alert / Critical), `development`, `vdem_dimension_affected`, `source`

#### `electoral_calendar_watch` array

Flag all elections within 90 days:
Per entry: `country`, `election_date`, `election_type`, `days_until`, `fimi_risk`, `integrity_concern`

#### Counts for Analyst reference

Include in `_meta` or top-level:
- `heatmap_counts`: `{"rapid_decay": N, "recovery": N, "watchlist": N}`
- `global_wdm_score_preliminary`: numeric (Analyst confirms final)
- `trajectory`: `"Improving | Stable | Declining"`

### 3.3 SCEM — Strategic Conflict & Escalation Monitor

**Slug:** `conflict-escalation`

#### `global_escalation_snapshot`

```json
{
  "active_theatres": 0,
  "new_escalations_this_week": 0,
  "de_escalations_this_week": 0,
  "highest_intensity_theatre": "string",
  "lead_signal": "string"
}
```

#### `theatre_tracker` array

Per theatre:
```json
{
  "theatre_id": "string — slug e.g. ukraine-russia",
  "theatre_name": "string",
  "intensity": "I1 | I2 | I3 | I4",
  "intensity_delta": "Escalating | Stable | De-escalating",
  "primary_actors": ["string"],
  "acled_event_count_7d": 0,
  "acled_fatality_count_7d": 0,
  "key_development": "string",
  "escalation_risk": "Low | Medium | High | Critical",
  "nuclear_threshold_concern": false,
  "hybrid_dimensions": ["FIMI | Cyber | Proxy | Economic | Sanctions"],
  "ceasefire_status": "None | Negotiating | In force | Collapsed",
  "source": "ACLED | ICG | SIPRI | Other"
}
```

Intensity scale: I1 = Green (armed vigilance), I2 = Amber (active hostilities),
I3 = Red (major offensive operations), I4 = Crisis (interstate war / mass atrocity risk).

#### `theatre_summary` per theatre (for Analyst deviation calculation)

The Synthesiser must provide per-indicator preliminary values to inform the Analyst's
deviation calculation. Per indicator, per theatre:

```json
{
  "theatre_id": "string",
  "indicator_id": "string — e.g. I1_rhetoric",
  "intensity_preliminary": "I1 | I2 | I3 | I4",
  "escalation_indicators": ["string — list of observed escalation signals"],
  "deviation_preliminary": "string — narrative description of deviation from baseline"
}
```

Note: The Analyst performs the formal `deviation = level − baseline` calculation
with numeric values (Section 2, Step 2 of ANALYST-CRON-SPEC). The Synthesiser
provides narrative context only — it does not set numeric `level`, `baseline`,
`deviation`, or `band` values.

#### `escalation_indicators` array

Per indicator: `theatre_id`, `indicator`, `type` (Kinetic / Political / Hybrid / Nuclear / Economic), `confidence_preliminary`, `threshold_crossed`

#### `hybrid_warfare_layer` array

Per dimension: `theatre_id`, `dimension` (FIMI / Cyber / Proxy / Economic coercion), `development`, `actor`, `fcw_link`

### 3.4 FCW — FIMI & Cognitive Warfare Monitor

**Slug:** `fimi-cognitive-warfare`

#### `campaign_roster_preliminary`

```json
{
  "active_count": 0,
  "emerging_count": 0,
  "dormant_count": 0,
  "campaigns": [
    {
      "campaign_id": "string",
      "campaign_name": "string",
      "status": "Active | Emerging | Dormant",
      "target_geography": "string",
      "primary_actor": "string",
      "platform_footprint": ["string"],
      "key_development": "string",
      "confidence_preliminary": "High | Assessed | Possible"
    }
  ]
}
```

#### `threat_level_preliminary`

```json
{
  "overall": "Low | Moderate | Elevated | Critical",
  "electoral": "Low | Moderate | Elevated | Critical",
  "information_environment": "Low | Moderate | Elevated | Critical"
}
```

### 3.5 ESA — European Strategic Autonomy Monitor

**Slug:** `european-strategic-autonomy`

#### `domain_tracker_preliminary`

```json
{
  "defence": {"score": 0.0, "direction": "Improving | Stable | Declining", "key_development": "string"},
  "energy": {"score": 0.0, "direction": "Improving | Stable | Declining", "key_development": "string"},
  "tech": {"score": 0.0, "direction": "Improving | Stable | Declining", "key_development": "string"},
  "trade": {"score": 0.0, "direction": "Improving | Stable | Declining", "key_development": "string"},
  "diplomatic": {"score": 0.0, "direction": "Improving | Stable | Declining", "key_development": "string"}
}
```

Scores are preliminary (0.0–10.0 scale). Analyst confirms final values.

### 3.6 AGM — AI Governance Monitor

**Slug:** `ai-governance`

#### `capability_tier_preliminary`

```json
[
  {
    "lab": "string — lab name",
    "tier": "Frontier | Advanced | Mainstream",
    "lead_model": "string",
    "key_development": "string",
    "governance_risk": "Low | Medium | High"
  }
]
```

#### `regulatory_milestone_status`

```json
[
  {
    "jurisdiction": "string",
    "milestone": "string",
    "status": "Proposed | Advancing | Enacted | Stalled | Withdrawn",
    "significance": "string",
    "week_update": "string"
  }
]
```

### 3.7 ERM — Environmental Risks Monitor

**Slug:** `environmental-risks`

#### `planetary_boundary_status_preliminary`

```json
[
  {
    "boundary": "string — boundary name",
    "status": "Safe | Increasing risk | High risk | Transgressed",
    "trajectory": "Improving | Stable | Deteriorating",
    "key_indicator": "string",
    "week_development": "string"
  }
]
```

#### `tipping_trajectory_preliminary`

```json
{
  "overall": "Stable | Elevated | High | Critical",
  "most_proximate_tipping_element": "string",
  "cascade_risk": "Low | Medium | High"
}
```

---

## 4. What Synthesisers Must NOT Do

### 4.1 No Live Web Search

`sonar-deep-research` reasons over provided documents only. It has no web access.
The synthesiser prompt must state explicitly: **"Do not search the web. Reason only
over provided documents."**

The synthesiser Python script is responsible for loading all necessary content
and embedding it in the API request body. If a document cannot be loaded, the
script must log the failure and proceed with available inputs — not attempt live search.

### 4.2 No Final Confidence Labels

All confidence, status, and regime labels in synthesiser output are **preliminary**.
Fields must use `_preliminary` suffix or be marked advisory.

Do not produce:
- `"confidence": "Confirmed"` → use `"confidence_preliminary": "Confirmed"`
- `"stress_regime": "RED"` → use `"stress_regime_preliminary": { "regime": "RED" }`
- `"health_status": "Crisis"` (without `_preliminary` annotation) → label as preliminary

The Analyst assigns all final labels.

### 4.3 No Writes to Static or Content Paths

The Synthesiser writes **only** to `pipeline/monitors/{slug}/synthesised/`.

Never write to:
- `static/monitors/{slug}/data/` — Analyst-only
- `content/monitors/{slug}/` — Analyst-only
- Any `archive.json`, `persistent-state.json` — Analyst-only
- `pipeline/monitors/{slug}/daily/` or `weekly/` — Collector/Weekly Research only

### 4.4 No Empty Arrays Without Null Signal Explanation

If a required array field has no entries this week, it must be `[]` (not omitted).

If the Synthesiser produces `cross_monitor_candidates: []`, this is only acceptable
when `null_signal_week: true` or when there are genuinely no cross-monitor signals.
An empty array without explanation triggers the "Build 2" placeholder in the UI.

If `weekly_brief_draft` cannot be produced because there is no signal, set
`null_signal_week: true` and explain in `null_signal_reason`. The Analyst will
handle null-signal weeks in their own methodology.

### 4.5 No Cross-Monitor Flag Setting

The Synthesiser produces `cross_monitor_candidates` — suggestions only.
It does not set `cross_monitor_flags`. That is the Analyst's responsibility.

### 4.6 No Persistent State Reads or Writes

The Synthesiser does not read or write `persistent-state.json`.
State continuity is the Analyst's domain.

---

## 5. Workflow Configuration Requirements

### 5.1 API Call Configuration (Gap 2 — search_recency_filter)

The Synthesiser uses `sonar-deep-research`, which does not perform web search.
However, any weekly-research workflows that feed the Synthesiser must include:

**Weekly-research workflows** (`sonar-pro`):
```json
"search_recency_filter": "month"
```

**Collector workflows** (`sonar`):
```json
"search_recency_filter": "week"
```

These must be present in every API call payload. Omitting them causes stale findings.

### 5.2 GH_TOKEN Requirement (Gap 1)

Every synthesiser workflow must include in its `env` block:

```yaml
env:
  PPLX_API_KEY: ${{ secrets.PPLX_API_KEY }}
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`GH_TOKEN` is required because the synthesiser Python script uses `subprocess`
calls to `gh api` to load pipeline files and methodology content.
Without `GH_TOKEN` in the workflow env, all `gh api` calls fail silently or with 401.

---

## 6. Conformance Checklist

Use this checklist to audit any Synthesiser prompt against this spec.
Answer YES or NO. Any NO is a gap requiring correction.

### Identity and Role

- [ ] Prompt identifies synthesiser as a reasoning engine over provided documents, not a research agent
- [ ] Prompt states: "Do not search the web. Reason only over provided documents."
- [ ] Prompt uses `sonar-deep-research` as the model
- [ ] Prompt output is described as advisory / preliminary
- [ ] Prompt does not claim to write to static/ or content/ paths

### `_meta` Object

- [ ] `schema_version` present (e.g. `"gmm-synthesis-v1.0"`)
- [ ] `monitor_slug` present and correct
- [ ] `job_type` = `"synthesiser"`
- [ ] `generated_at` present (ISO 8601)
- [ ] `data_date` or `week_ending` present
- [ ] `null_signal_week` present (boolean)
- [ ] `null_signal_reason` present (string or null)
- [ ] `finding_count` present (integer)
- [ ] `status` present

### Universal Required Fields

- [ ] `lead_signal` present with headline (max 120 chars, factual), domain, confidence_preliminary, source_url
- [ ] `lead_signal.headline` is a specific factual statement (not a status label)
- [ ] `key_judgments` array with 3–5 items, each with id, judgment, confidence_preliminary, supporting_evidence
- [ ] All `key_judgments` confidence values use `_preliminary` suffix
- [ ] `cross_monitor_candidates` array present (may be `[]` if genuinely none)
- [ ] `cross_monitor_candidates` uses exact slugs from Section 2.7
- [ ] `weekly_brief_draft` present as a string field
- [ ] `weekly_brief_draft` is 400–600 words
- [ ] `weekly_brief_draft` uses no apostrophes or contractions (JSON safety)

### Null Signal Handling

- [ ] When `null_signal_week: true`, `null_signal_reason` is populated
- [ ] When `null_signal_week: true`, `weekly_brief_draft` explains the absence of signal
- [ ] No required array is omitted — set to `[]` if empty

### What Synthesiser Does NOT Do

- [ ] Prompt does not instruct writing to `static/` or `content/` paths
- [ ] Prompt does not assign final confidence labels (no non-`_preliminary` confidence in final outputs)
- [ ] Prompt does not set `cross_monitor_flags` (candidates only)
- [ ] Prompt does not read or write `persistent-state.json`

### Monitor-Specific Fields

- [ ] **GMM:** `stress_regime_preliminary` with regime, conviction, system_average, regional breakdowns, regime_delta; all 6 `indicator_domains`; `central_bank_tracker`; `tariff_tracker`; `tail_risks`
- [ ] **WDM:** `global_health_snapshot`; `country_heatmap` with `vdem_ldi_preliminary`; `backsliding_alerts`; `electoral_calendar_watch` (all elections within 90 days); heatmap counts for Analyst reference
- [ ] **SCEM:** `global_escalation_snapshot`; `theatre_tracker` with ACLED counts; `theatre_summary` with `escalation_indicators` and `deviation_preliminary` narrative; `hybrid_warfare_layer`
- [ ] **FCW:** `campaign_roster_preliminary` with active/emerging/dormant counts; `threat_level_preliminary`
- [ ] **ESA:** `domain_tracker_preliminary` for all 5 domains (defence, energy, tech, trade, diplomatic)
- [ ] **AGM:** `capability_tier_preliminary` per lab; `regulatory_milestone_status` per jurisdiction
- [ ] **ERM:** `planetary_boundary_status_preliminary` per boundary; `tipping_trajectory_preliminary`

### Workflow Configuration (for workflow authors)

- [ ] `PPLX_API_KEY` in workflow env
- [ ] `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in workflow env (Gap 1)
- [ ] Script loads daily-latest.json, weekly-latest.json, and methodology content and embeds in API request
- [ ] Collector workflows feeding this synthesiser include `search_recency_filter: "week"` (Gap 2)
- [ ] Weekly-research workflows feeding this synthesiser include `search_recency_filter: "month"` (Gap 2)

---

## Appendix A — Known Gaps Fixed (Session 2026-04-07)

These gaps are addressed in this spec and in ANALYST-CRON-SPEC.md.

| Gap | Description | Spec Section |
|-----|-------------|-------------|
| Gap 1 | GH_TOKEN in workflow env | Sections 1.3, 5.2 |
| Gap 2 | search_recency_filter in collector/weekly-research API calls | Section 5.1 |
| Gap 3 | meta.pipeline_inputs in report-latest.json | ANALYST-CRON-SPEC Section 3.1 |
| Gap 4 | weekly_brief in JSON AND Hugo brief | ANALYST-CRON-SPEC Sections 3.1, 7 |
| Gap 5 | lead_signal from synthesiser — Analyst confirms/refines, does not independently derive | Sections 2.2; ANALYST-CRON-SPEC Step 0S |
| Gap 6 | Publish Guard 3 checks | ANALYST-CRON-SPEC Section 5 |
| Gap 7 | Two-Pass Commit Rule | ANALYST-CRON-SPEC Section 6 |
| Gap 8 | Hugo brief filename = frontmatter date (FE-019) | ANALYST-CRON-SPEC Section 7.1 |

---

## Appendix B — Synthesiser to Analyst Handoff Map

How each Synthesiser output field maps to the Analyst's final report field:

| Synthesiser field | Analyst field | Analyst action |
|-------------------|--------------|----------------|
| `lead_signal` | `lead_signal` | Confirm or refine; do not rewrite without cause |
| `key_judgments[].confidence_preliminary` | `key_judgments[].confidence` | Assign final value; remove `_preliminary` |
| `stress_regime_preliminary` | `stress_regime` | Confirm or override with methodology |
| `country_heatmap[].health_status` | `country_heatmap[].health_status` | Confirm; add `severity_sub` |
| `theatre_tracker[].intensity` | `theatre_tracker[].intensity` | Confirm; run deviation calc |
| `campaign_roster_preliminary` | `campaign_roster` | Confirm; assign final threat levels |
| `weekly_brief_draft` | `weekly_brief` | Edit; write to JSON and Hugo |
| `cross_monitor_candidates` | `cross_monitor_flags` | Confirm, reject, or add; write final flags |

---

*End of SYNTHESISER-SPEC.md — Version 1.0 | 2026-04-07*

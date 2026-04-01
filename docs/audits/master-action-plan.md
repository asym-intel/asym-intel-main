# Master Action Plan — All Monitors
*Consolidated from 7 domain audits | Produced: 2026-04-01*  
*Monitors covered: GMM · WDM · FCW · ESA · AGM · ERM · SCEM*

---

## 1. Rendering Bugs (fix immediately — data exists, page is broken)

These represent data being collected and silently dropped. Fix before any other work.

| Monitor | Bug | Effort |
|---|---|---|
| AGM | M07 Risk Vector Heat Grid — dashboard shows the header but content does not render (confirmed blank) | Low |
| AGM | M07 Risk Vectors — persistent.html renders literal `undefined` instead of the risk vector values | Low |
| AGM | M15 AISI Pipeline — persistent.html renders literal `undefined` | Low |
| AGM | M15 Ongoing Lab Postures — persistent.html renders literal `undefined` | Low |
| AGM | Delta Strip — dashboard shows count "5" but the five items are not listed; counter without content | Low |
| AGM | Digest page (digest.html) — not live at all; renders subscription form placeholder only; copy says "15 modules" but schema has 16 | Medium |
| SCEM | Report.html "Roster Watch" section — appears in sidebar navigation but renders empty content body; `roster_watch` data in JSON is not injected into the template | Low |
| SCEM | Report.html "Cross-Monitor" section — appears in sidebar navigation but renders empty content body; `cross_monitor_flags` data in JSON is not injected into the template | Low |
| SCEM | Dashboard Indicator Breakdown bar chart — shows indicator *level* (1–5), not *deviation*. A user looking at Russia-Ukraine I1=5 (deviation=0) and Sudan I6=5 (deviation=+1) sees identical full bars. The core concept of the monitor (deviation, not level) is not communicated | Low |
| SCEM | Global Escalation Index reads "LOW (0 RED, 0 AMBER)" while C10 (US-Iran) has three indicators meeting RED-band thresholds — suppressed by CONTESTED baseline status with no explanation to dashboard users | Low |
| SCEM | Schema version mismatch — report.html shows "Schema 2.0"; persistent.html shows "Schema 1.0" | Low |
| ESA | Lagrange Point radar chart renders only 5 dimensions (Energy, Defence, Technology, Finance, Materials); the Institutions spoke is missing despite being the 6th explicitly defined pillar — contradicts both the persistent scorecard and the About page | Low |
| AGM | M06 arXiv entry — renders as metadata stub only ("2026-03-30 arXiv cs.AI 1") with no title, abstract, or significance note | Low |
| WDM | `heatmap[*].source_url` — all 29 entries (15 rapid_decay + 5 recovery + 9 watchlist) have the key present but the value is always an empty string; every country classification is untraceable to a primary source; credibility issue for researchers and journalists | Low |
| WDM | `severity_sub` — specified in the cron schema but has never appeared in any heatmap entry across all 3 issues (0 of 29 entries carry electoral/civil_liberties/judicial sub-scores); renders nowhere; cron enforcement missing | Low |
| WDM | `heatmap.recovery[*].lead_signal` — absent from all 5 recovery entries despite being present on all 15 rapid_decay entries; structural asymmetry between heatmap tiers; analysts cannot see the leading indicator driving recovery classification | Low |
| WDM | `signal.silent_erosion` — specified in schema, never present in any issue (Issues 1–3); the monitor's highest-value analytical differentiator from wire-service summarisation is completely absent | Low |
| WDM | `signal.history` — specified in schema, never present in any issue; week-over-week diff context (escalations, new entries, exits) lives only as prose inside `weekly_brief` and is not structured or rendered anywhere | Low |

---

## 2. Critical Data Gaps (collected but never surfaced)

Fields populated in JSON but rendered on zero pages across all three page types.

| Monitor | Field/Section | Where it should appear | Effort |
|---|---|---|---|
| GMM | `regime_shift_probabilities` (4 values: stay_stagflation 60%, deflationary_bust 25%, inflationary_boom 10%, goldilocks 5%) — exists in both `signal` and `executive_briefing` blocks | Dashboard Signal section (4-bar chart); Report | Medium |
| GMM | `sentiment_overlay` (entire block) — 5 FOMC meetings with cut probabilities, AGREES/DISAGREES column, `prob_zero_cuts_2026` (22%), `matt_agreement_pct` (40%) | Dashboard (5-row table); Report Safe Haven section | Medium |
| GMM | `domain_indicators` object (all 6 domains, ~24 indicators) — entire schema v2.0 expansion including `indicator_type` (SA/CC/TS), `crisis_threshold`, `blind_spot_rule`, `update_this_week` per indicator | Report (expandable grid); Dashboard (TS indicators) | High |
| GMM | `executive_briefing.scenario_analysis` array (3 scenarios: Slow Burn 55%, De-escalation 20%, Fast Cascade 25%) | Dashboard (scenario cards); Report | Medium |
| GMM | `executive_briefing.real_m2` (5-deflator stack: nominal, vs_cpi, vs_pce, vs_core_pce, vs_ppi, vs_core_ppi) | Dashboard (waterfall bar chart); Report | Medium |
| GMM | `executive_briefing.hard_landing_risk.score` (0.38, Increasing) | Dashboard KPI card (4th tile) | Low |
| GMM | `update_this_week` field on all domain-level indicators (debt_dynamics, credit_stress, systemic_risk) — the most analytically dense field in the schema | Report (expandable accordion per indicator) | Low |
| GMM | `domain_indicators` Domains 4 (Real Economy: ISM PMI 52.4, Jobless Claims 205K, Cass Freight -7.2%, Earnings Revisions +12.5%) and Domain 5 (STLFSI, NFCI, IIF Global Debt, 0DTE Volume Ratio) — entirely invisible to users | Report | High |
| GMM | `cross_monitor_flags[].macro_indicators_affected` — the explicit linkage between cross-monitor signals and the GMM indicators they affect | Report (chip/tag list) | Low |
| GMM | `tail_risks[].note` — one-sentence explanation of trigger and horizon for each of 6 tail risks on the heatmap | Dashboard (tooltip on heatmap hover) | Low |
| FCW | `attribution_log[]` (entire section) — date, campaign_id, confidence, note, headline, summary, source_url | Dashboard; Persistent | Medium |
| FCW | `cognitive_warfare[]` (entire section) — id, classification, headline, detail, source_url | Dashboard; Persistent (structural CW patterns need to accumulate in living KB) | Medium |
| FCW | `platform_responses[]` (entire section) — platform, action_type, headline, actor, date, source_url | Dashboard (platform enforcement widget) | Medium |
| FCW | `cross_monitor_flags` (ESCALATED flags — CMF-001, CMF-002) | Dashboard (alert banner or card) | Low |
| FCW | `campaigns[6–11]` (7 of 12 campaigns: CN-001, CN-002, AI-NET-001, IR-001, GULF-UAE-001, US-001, IL-001) — entirely absent from dashboard view | Dashboard (secondary grid) | Low |
| FCW | `cross_monitor_flags.version_history` | Dashboard; Report; Persistent | Low |
| ESA | `institutional_developments[]` (all items including EU-China trade data, Slovenia government, Hungary election, €90B Ukraine loan) — 4 of 10 items per issue are invisible to dashboard users | Dashboard Top Items strip | Low |
| ESA | `cross_monitor_flags` — structurally present in schema and rendered in report/persistent, but contains zero data in two consecutive issues; either a collection gap or dead schema field | N/A (trigger criteria must be defined) | Low |
| AGM | M01 `intelligence.mainstream` and `intelligence.underweighted` (5 items each) | Dashboard | Medium |
| AGM | M03 `capital.energy_wall` filter — a key differentiator for the monitor, not surfaced on dashboard at all | Dashboard | Low |
| AGM | M04 `deployment_by_sector` (7 sectors with Accelerating/Stalling/Emerging status) | Dashboard (sector heat map) | Low |
| AGM | M06 `frontier_research.threshold_events` — among the most important AGM outputs | Dashboard | Low |
| AGM | M08 `dual_use` (procurement, doctrine, capability, IHL friction) | Dashboard | Medium |
| AGM | M10 `governance_gaps` (all 5 sub-sections: international soft law, corporate governance, product liability, algorithmic accountability) | Dashboard | Medium |
| AGM | M11 `accountability` (lab ethics commitments, accountability friction, AISI ethics pipeline) | Dashboard | Medium |
| AGM | M14 `power_concentration.concentration_index` | Dashboard | Low |
| AGM | `cross_monitor_flags` (cmf-001 through cmf-006) | Dashboard | Low |
| ERM | `m02.boundaries[].summary` — per-boundary analytical summary (e.g., "Current trajectory consistent with 2.7°C by 2100") | Dashboard (expandable row); Report | Low |
| ERM | `m03[].f1_trigger` — the specific physical trigger that activates each cascade chain | Report; Dashboard | Low |
| ERM | `m03[].tier_1_physical`, `tier_2_human`, `tier_3_political` — the three-layer cascade breakdown is the analytical core of the module; none of the three tiers are individually rendered anywhere | Report (3-column table per M03 item) | Low |
| ERM | `m03[].reverse_cascade_check` — confirmed reverse cascade (geopolitical operation → physical boundary transgression) absent from Report M03 section where it has highest analytical value | Report | Low |
| ERM | `persistent: tipping_systems.threshold_lower/upper_bound_pct` for Amazon dieback (25–30%) — data exists in persistent-state.json but never rendered | Persistent page (progress bar) | Low |
| SCEM | `roster_watch.approaching_retirement[]` — which conflicts are approaching retirement from the roster | Report; Persistent | Low |
| SCEM | `lead_signal.source_url` | Dashboard lead signal block | Low |
| SCEM | `conflict.source_url` (conflict-level) | Report; Dashboard | Low |
| SCEM | `indicators.I1–I6.baseline` | Dashboard bar chart (marker line) | Low |
| SCEM | `lead_development` (per conflict) | Persistent | Low |
| WDM | `weekly_brief` (6,369 chars) — present in JSON and rendered on report.html and persistent.html but entirely absent from dashboard.html; a 900–1,200 word narrative summary is invisible on the primary user-facing page | Dashboard | Low |
| WDM | 9 Category B sections absent from JSON in Issues 1–3: `electoral_watch`, `digital_civil`, `autocratic_export`, `state_capture`, `institutional_pulse`, `legislative_watch`, `research_360.friction_notes`, `networks`, `monthly_trend` — two-pass commit fix applied 1 April 2026; **known and being fixed**; expected from Issue 4 (w/e 6 April) onwards; stubs on report.html and persistent.html confirmed; verify rendering once data arrives | Dashboard; Report; Persistent | Low |

---

## 3. Schema Additions (new fields to add to cron prompts)

Ranked by value. New data the cron should collect that it currently doesn't.

| Monitor | Addition | Why it matters | Effort |
|---|---|---|---|
| GMM | `credit_spreads` object: `ig_oas`, `hy_oas`, `cdx_ig_5yr`, `cdx_hy_5yr`, `embi_spread` — each with current level, prior level, z-score vs 2yr, direction. Source: ICE BofA/FRED, Markit | Single most important missing data stream for a credit-stress monitor; grounds every qualitative credit_stress call in quantifiable data | Low |
| GMM | `prior_regime`, `regime_change_date`, `weeks_in_current_regime` in the `signal` block | When STAGFLATION transitions to DEFLATIONARY BUST, users need to know it is a new call; currently no explicit record of when regime last changed | Low |
| GMM | VIX term structure and Treasury liquidity as named numeric indicators in Domain 3 (listed in cron canonical mapping but dropped from current JSON): VIX front-month vs 3-month ratio, MOVE index, 10yr bid-ask spread | Most actionable short-horizon tactical signals in the monitor's remit | Medium |
| GMM | `custody_migration` (SA) and `gold_reserve_ratio` (SA) in Domain 1 — specified in cron canonical mapping but absent from `domain_1_debt_sovereign` array | Directly supports dollar weaponisation theme and Metals safe haven call; their absence weakens the analytical chain | Medium |
| GMM | `dollar_funding_fx_basis` and `margin_debt` as Domain 3 TS indicators — in cron canonical mapping but absent from JSON domain_3 array | FX swap basis is the cleanest real-time dollar stress signal in global markets; margin debt is a leading forced-selling indicator | Medium |
| GMM | Tariff impact quantification sub-fields: `effective_rate_pct`, `prior_effective_rate_pct`, `gdp_drag_est_low/high`, `retaliation_risk_score` on the trump_tariff_escalation indicator | Converts a narrative-only indicator into a quantified basis for the tariff call; feeds directly into asset class scoring | Medium |
| GMM | `source_quality_flags` (F1/F2/F3) on individual indicators — flags defined in cron schema but never applied in JSON | Epistemic discipline for highest-conviction calls; makes sourcing auditable by users | Low |
| GMM | Scenario-conditional asset class impacts sub-object on each `scenario_analysis` entry | Makes scenario analysis actionable for portfolio construction rather than purely descriptive | High |
| FCW | `narrative_ids[]` array on each campaign + top-level `narratives[]` registry (id, label, first_observed, last_observed, actor_spread, platform_spread) | Enables cross-campaign narrative tracking — the most analytically powerful capability FCW currently lacks; currently the fact that two campaigns deploy the same narrative is only visible through manual reading | High |
| FCW | `effectiveness` object per campaign: `reach_estimate`, `amplification_evidence`, `counter_response_triggered`, `narrative_penetration` | Converts FCW from a pure tracking monitor into an impact-assessment monitor; currently describes operations but not downstream effects | Medium |
| FCW | `start_date` field population + timeline Gantt fix — field added to schema but not yet populated; first data expected Apr 9 cron | `first_documented` ≠ `start_date`; Gantt must use canonical `start_date` once populated | Low |
| FCW | Fix `attribution_log[].instrument` population error — currently set to confidence string (e.g., "Assessed", "High") instead of operational technique (e.g., "impersonation website", "coordinated inauthentic accounts") | Wasted field; blocks MITRE ATT&CK-style cross-campaign technique analysis | Low |
| FCW | Fix `attribution_log[].actor` population error — currently stores campaign_id ("RU-004") instead of actor code ("RU") | Naming collision creates analytical ambiguity in the evidentiary record | Low |
| FCW | `threat_level` object: `level` (BASELINE/ELEVATED/HIGH/CRITICAL), `basis`, `trend`, `previous_level` — current dashboard banner appears hardcoded in template, not in JSON | Enables time-series tracking of threat level; currently cannot be tracked over time or used in cross-monitor aggregation | Low |
| FCW | `cognitive_warfare[]` in persistent data layer with `first_identified` date and `status` (ACTIVE_DOCTRINE/HISTORICAL/RESOLVED) | Structural CW patterns are persistent phenomena; currently ephemeral per-issue entries lost from living KB | Medium |
| FCW | `linked_campaigns[]` array on each campaign entry for explicit co-targeting relationships | RU-001/RU-004 co-targeting relationship buried in text; makes campaign clusters queryable and visualisable | Low |
| FCW | `platform_responses[].enforcement_completeness` (none/partial/complete), `assets_actioned`, `assets_estimated_remaining` | "88% of EU-flagged FIMI content remains on X" is currently a narrative string, not queryable data | Low |
| FCW | `event_horizon[]` array: `date`, `country`, `type`, `fimi_risk_level`, `linked_campaigns[]` | Forward-looking FIMI-risk calendar for upcoming elections; Hungary April 12 election has no structured event data | Low |
| ESA | `defence_spending[]` array per member state: `country`, `gdp_pct_actual`, `gdp_pct_target` (2%), `hague_target_pct` (5%), `absolute_eur_bn`, `yoy_change_pct`, `safe_allocation_eur_bn`, `source_url` | Single most investor-relevant quantitative output; data publicly available from NATO; monitor tracks defence autonomy with no numeric data on the most important indicator | Medium |
| ESA | `scorecard[]` array with structured pillar fields: `pillar`, `score`, `delta_from_last_issue`, `direction`, `key_driver_this_week`, `data_sources[]`, `methodology_note` | Current ~35% composite score is an unanchored point-in-time assertion; no week-on-week delta or sub-indicator transparency | Medium |
| ESA | `us_dependency[]` array: `domain`, `dependency_score`, `primary_dependency_mechanism`, `recent_development`, `source_url` | Monitor's stated scope includes US-Europe relationship but US dependency is entirely absent from JSON schema; most investor-relevant signal in current environment | Medium |
| ESA | `defence_programmes[]` persistent tracker: `programme_name`, `total_envelope_eur_bn`, `disbursed_to_date_eur_bn`, `pending_disbursements[]`, `next_milestone`, `blocking_actors` | ReArm Europe (€800B) and EDIP (€1.5B) tracked only as one-off items; no persistent programme-level progress tracking | Medium |
| ESA | `composite_index_history[]` for issue-by-issue trend of the ~35% autonomy index | At Issue 2 there is no baseline delta; two-point time series minimum needed for directional language | Low |
| ESA | `us_eu_bilateral_state{}` object: `trade_dispute_status`, `tariff_threat_level`, `nato_commitment_status`, `intelligence_sharing_status`, `data_protection_tension_level` | First-class concern in the monitor's stated scope; currently scattered prose only | Medium |
| AGM | `regulatory_calendar` structured array: `{event, jurisdiction, date, type: [deadline/vote/enforcement/review], status}` | EU AI Act countdown (122 days) and Omnibus 28 April deadline are hand-computed; structuring enables dashboard countdown widgets and automated staleness alerts | Low |
| AGM | Governance Health Composite Score (0–100 or traffic light) computed from M07 + M09 + M10 + M11 + M15 data | The AGM's analytical thesis made measurable; becomes the monitor's signature metric; most requested output by policy analysts and investors | Medium |
| AGM | Capability-Governance Lag Index: capability events scored by magnitude, governance responses scored by bindingness, rolling 12-week lag in weighted days | Transforms AGM from a narrative publication into a data product with a proprietary signal | High |
| AGM | `capability_profile` per tracked model: `{model_id, lab, tier, dimensions: {reasoning, coding, cyber, bio, agentic}, eval_source, date}` | Enables capability-governance lag computation; feeds dual-use risk flag in M08 | Medium |
| AGM | Jurisdiction Risk Matrix — extend Country Grid to structured object: `{jurisdiction, ai_law_status, enforcement_capacity, regulatory_velocity, strategic_posture, last_event, next_event}` | Enables sortable matrix, cross-issue trend tracking, direct input into governance health score | Medium |
| AGM | `lab_posture` scorecard per major lab: `{rsp_trigger_status, disclosure_record, audit_access, government_contracts, revolving_door_velocity, opsec_incidents}` | Aggregates M11 per-item ethics tracking into a persistent, comparable scorecard | Medium |
| AGM | Investment Flow structured object per M03 funding round: `{amount_USD, type, investors, sector, energy_wall: boolean}` | M03 is currently narrative; enables capital flow dashboard widget and energy wall filter as standalone chart | Low |
| AGM | `flag_type` field on every asymmetric flag: `{reframing / underweighting / structural_implication / cross_monitor}` | Enables filtering and issue-level analytics; investor audience wants structural_implication, safety researchers want reframing | Low |
| ERM | Planetary boundary numeric proximity score per boundary: `control_variable`, `current_value`, `unit`, `safe_boundary`, `zone_upper_limit`, `proximity_score`, `proximity_direction` | Status board currently shows Safe/Uncertain/Transgressed with no degree of transgression; CO₂ 424 ppm vs. 350 ppm boundary vs. 450 ppm zone ceiling is a trackable ratio | Medium |
| ERM | Tipping system proximity-to-threshold object (standardised across all 6 systems, extending Amazon's existing `threshold_lower/upper_bound_pct` to AMOC, Greenland, etc.) | Makes "how close are we?" answerable at a glance; enables dashboard gauge and automated escalation alerts | Medium |
| ERM | `m04_ytd_summary` block: `year`, `events_logged`, `events_with_f1_tag`, `regions_affected`, `cumulative_displaced_estimate`, `baseline_comparison` | Insurance/reinsurance audience needs YTD normalised loss data; no aggregation layer currently exists across M04 events | Low |
| ERM | M05 regulatory pipeline tracker: structured anticipated policy developments with `type: anticipated`, `current_status`, `anticipated_resolution`, `risk_rating`, `investor_impact` | Without this the monitor is purely reactive; misses lead time that is most valuable to investors | Medium |
| ERM | M08 supply chain concentration index per resource: `processing_hhi_estimate`, `top_supplier`, `top_supplier_share_pct`, `supply_disruption_scenario` | Enables machine-readable supply chain risk scoring; actors field is currently free text | Medium |
| ERM | `reverse_cascade` structured object in M03: `confirmed: bool`, `severity`, `mechanism`, `estimated_feedback_lag_weeks` | Enables automated detection of confirmed reverse cascades and cross-monitor escalation triggers | Low |
| ERM | M03 `cascade_stage` enumerated status: `{current, max, confirmed_transition[], projected_next_transition_weeks}` | Current stage is a text string; enumeration supports automated tracking and progression visualisation | Low |
| ERM | Cross-monitor flags `escalation_trigger` field: the condition under which a flag moves to higher severity, `escalation_threshold_met: bool` | `version_history` array exists but is empty; no machine-readable escalation condition | Low |
| SCEM | `escalation_velocity` field: `{direction: accelerating/steady/decelerating, week_over_week_delta, consecutive_escalating_weeks}` | Single highest-value SCEM schema addition; enables early warning before band thresholds are crossed; distinguishes new breakout from chronic plateau | Medium |
| SCEM | `esc_score` composite per conflict: `{raw, weighted, methodology_note}` with I3/I2 weighted higher for interstate conflicts | Enables conflict ranking by escalation severity rather than single-indicator maximum; improves Delta Strip logic | Medium |
| SCEM | `negotiation_status` per conflict: `{status: none/backchannel/formal_talks/ceasefire_holding/ceasefire_violated, mechanism, confidence, last_updated, note}` | For Gaza, DRC, Sudan, US-Iran, ceasefire/negotiation state is the primary variable determining whether deviation trajectory continues or reverses | Low |
| SCEM | `external_actors[]` per conflict: `{actor, role, indicator_affected, confidence}` | External actor involvement is analytically critical but captured only in free text; structuring enables cross-conflict pattern analysis (Iran as multi-theatre enabler) | Low |
| SCEM | `sources[]` structured array per conflict (replacing free-text T1/T2/T3 tier references) | Enables systematic confidence-scoring audit and editorial traceability | Low |
| SCEM | `conflict_phase` field: latent/low-intensity/active_conventional/active_wmd_risk/ceasefire/post-conflict | `trajectory` conflates direction with phase; phase determines which indicators are most diagnostically relevant | Low |
| SCEM | `conflict_linkages[]` array mapping within-SCEM conflict relationships (US-Iran/Israel-Lebanon/Gaza nexus) | Cross-conflict spillover is now the dominant analytical challenge; currently noted in free text only | Low |
| SCEM | PROVISIONAL band tier for CONTESTED-period RED-band deviations (≥+2) | Current architecture produces structural false negatives: C10 (US-Iran) has three RED-band indicators suppressed by CONTESTED status; index reads LOW during active war with Hormuz closed | Medium |
| SCEM | I7 — proxy/third-party warfare indicator: `state-sponsored external military support`, `proxy_ground_forces`, `mercenary/PMC_deployment` | Proxy warfare is now the dominant escalation vector across 4+ active conflicts (Myanmar, Korea, Sudan, DRC, US-Iran); currently absorbed into I2 notes | High |
| SCEM | `conflict_context` object (humanitarian/territorial) — already in cron prompt from Apr 5; no rendering scaffolding yet visible on any page | Provides territorial control data to ground I2 assessments; rendering must be built before data arrives | Medium |
| WDM | `wdm_stress_index` — aggregate 0–100 democratic deterioration composite across rapid_decay + watchlist severity scores, with `direction` (Deteriorating/Stable/Improving) and `delta` vs prior issue | Monitor-level headline metric; mirrors GMM’s regime score and SCEM’s GEI; makes WDM summary comparable across issues and to other monitors | Low |
| WDM | Severity score version history in persistent-state per country — issue-by-issue severity_score log analogous to GMM’s `conviction_history`; enables trend lines on persistent country cards | Without this, persistent.html is a snapshot, not a trend tracker; critical for longitudinal analysis | Low |
| WDM | `heatmap.recovery[*].lead_signal` + `heatmap.watchlist[*].lead_signal` — parity with rapid_decay; single cron prompt fix; render slots already exist in table layout | Analysts need the leading indicator for recovery and watchlist tiers as much as for decay; currently asymmetric | Low |
| WDM | `monthly_trend` block: `rapid_decay_count_now`, `rapid_decay_count_4w_ago`, `recovery_count_now`, `recovery_count_4w_ago`, `watchlist_count_now`, `watchlist_count_4w_ago`, `net_change_direction` — persistent stub exists; cron must accumulate and diff issue counts; available at Issue 5 (4-week threshold) | Most requested feature for analysts tracking aggregate democratic health over time; enables KPI delta row on dashboard and trend chart on persistent | Low |
| WDM | Mimicry chain velocity fields: `days_between_links` and `chain_velocity` (Accelerating / Stable / Slowing) per `regional_mimicry_chains[]` entry — also add `mechanism`, `spread_velocity`, `origin`, and `links[*].status` (enacted/pending/blocked/repealed) | Transforms mimicry chain from a list of facts into an analytical propagation model; `links[*].status` is especially critical (Bosnia-Herzegovina suspension is invisible in current data) | Low |
| WDM | `signal.silent_erosion` — required 300–600 word analytical paragraph per issue on a single buried procedural development; distinct from `signal.body` which summarises top stories | Monitor’s highest-value differentiator from wire-service summarisation; already specified in cron schema but never produced | Low |
| WDM | `signal.history` structured array: `[{country, previous_tier, current_tier, direction, reason}]` — "This Week’s Changes" diff table; render on report.html and persistent.html | Most immediately actionable summary for a busy analyst; currently buried as prose in `weekly_brief` | Low |

---

## 4. Dashboard/UI Improvements (rendering changes needed)

Visual and UX improvements beyond just surfacing existing data.

| Monitor | Improvement | Why it matters | Effort |
|---|---|---|---|
| GMM | Add `condition_for_reassessment` to dashboard Safe Haven card (already on report.html) | The specific trigger to rotate out is most useful on the quick-view page, not just the report | Low |
| GMM | Add `not_investment_advice` disclaimer to Safe Haven section | Compliance/legal context missing from all pages | Low |
| GMM | Real M2 five-deflator waterfall bar chart on dashboard: nominal → vs_CPI → vs_PCE → vs_Core_PCE → vs_PPI → vs_Core_PPI | This is the chart the cron explicitly designs the five-deflator schema for; currently exists as six numbers in a JSON object and is never visualised | Medium |
| GMM | Tail risk `note` tooltip on dashboard heatmap hover — heatmap currently shows label and position only; no explanation of trigger or horizon | Transforms heatmap from visual decoration into actionable intelligence layer | Low |
| GMM | Asset class delta vs. baseline on persistent.html — add delta from `baseline_score` to current score (e.g. Consumer Staples: -0.83 → -0.908, Δ -0.078) | Current chart shows absolute scores but not cumulative drift from inaugural scoring | Low |
| FCW | Surface all 12 campaigns on dashboard (not just top 5) — add secondary condensed grid below featured section | 7 of 12 campaigns are entirely invisible on the primary view; dashboard user has no idea CN-002, IR-001, or IL-001 exist | Low |
| FCW | Actor Threat Board: add `doctrine` label and `actor_tracker[].headline` (expandable or tooltip) | Board currently shows actor, campaign count, status dot, activity bar — no analytical content; one-line doctrine makes it meaningful rather than a count aggregation | Low |
| FCW | Campaign changelog visible on report.html — add "What changed this issue" line per campaign | `changelog` field populated but not rendered; report readers cannot identify new developments without re-reading full summary | Low |
| FCW | "Last intelligence" staleness indicator for campaigns with `last_activity` > 4 weeks old | Cannot distinguish live operations from stale carry-forwards; RU-003, CN-001, CN-002, IR-001 all at 2026-03-01 | Low |
| ESA | Add source links to Top Items dashboard strip (every item has `source_url` in JSON; template drops it) | Analysts need verifiability from the fastest view; single template change | Low |
| ESA | Add delta arrows to pillar scores on dashboard/persistent scorecard (▲/▼/–) | Weekly publication; directional signal is more informative than absolute score for returning users | Medium |
| ESA | Replace "~35%" composite gauge with labelled pillar breakdown bar chart (data exists in persistent JSON) | Single opaque number vs. seeing Tech:18 and Finance:22 as the weakest pillars; transforms gauge from decoration into insight | Medium |
| ESA | Add institutional developments module/card strip to dashboard | Four of ten items per issue invisible; even a minimal card strip analogous to existing Defence/Hybrid strips closes the gap | Low |
| ESA | Make Member State Tracker sortable/filterable by status (CRITICAL/HIGH/ELEVATED/STABLE/POSITIVE) | As tracker grows, users need to triage by severity; currently only 4 member states displayed | Medium |
| ESA | Add issue navigation/archive widget to dashboard (last 3–4 issues with date and lead signal title) | Dashboard shows only latest issue; no quick-access to recent issues for trend comparison | Low |
| AGM | Collapse "No items this issue" modules on report.html by default with "+expand" affordance | 16 modules in long scroll; empty sections create false impression of missed coverage and add cognitive friction | Low |
| AGM | Add module density indicator/count badge to sidebar nav (e.g., "02 Model Frontier · 3") | Users can scan sidebar to find density before scrolling; low effort, significant UX improvement for structured-briefing audience | Low |
| AGM | Country Grid — add Regulatory Velocity column (↑ Accelerating / → Stable / ↓ Retreating) | Makes geopolitical competition narrative scannable; data exists in M09 | Low |
| AGM | Persistent page — add issue-over-issue trend lines to Concentration Index (M14) | Current bar-width for current-state only; "Nvidia ~11x AMD" direction of travel matters more than point-in-time snapshot | Medium |
| AGM | Build the digest.html page — minimum viable: The Signal + delta_strip top 5 + M07 risk ratings + M14 concentration index + cross_monitor_flags count | Placeholder page for returning users who don't need the full report; 6 data fields already collected | Medium |
| ERM | Dashboard Lead Signal (M00) card — add source link (report has "Primary source →"; dashboard has none) | Most-visited entry point; analysts need to verify primary signal without navigating to report | Low |
| ERM | Delta strip format: add `why_it_matters` as second line in smaller italic below headline | Most time-pressed reading experience; omitting "why it matters" is significant loss of analytical value | Low |
| ERM | Cascade chain heatmap on dashboard — three columns (Physical / Human / Political) × active cascade chains, showing tier status and one-line indicator per cell | The cascade chain is the ERM's methodological signature and is entirely absent from the dashboard | Low |
| ERM | M02 boundary expandable row summary on dashboard — clicking a boundary row reveals the `summary` field analytical content | Transforms status board into analytical brief; data already in JSON | Low |
| ERM | M06 `dual_edge` badge (Positive / Negative) on each AI-climate item in report | GenCast (Positive) and data centre demand (Negative) look identical without it; dual-nature framing is invisible | Low |
| SCEM | Dashboard: add baseline marker line to I1–I6 bar chart (two-tone fill or marker showing baseline; filled portion above marker = deviation) | Most important visual fix; the core concept is not communicated at all currently | Low |
| SCEM | Dashboard: add contested-baseline disclaimer to Global Escalation Index ("Bands suppressed: baselines CONTESTED until W13. Current levels without baseline: C10 I3+2, I4+1, I6+2.") | Trust and analytical integrity issue; users conclude the conflict environment is calm during an active US-Iran war with Hormuz closed | Low |
| SCEM | Delta Strip: show count of deviating indicators per conflict alongside highest deviation (e.g., "3 indicators deviating (I3+2, I4+1, I6+2)") | Current display understates multi-indicator crises; C10 has three RED-band indicators, shown as a single "+2" | Low |
| SCEM | F-Flag tile expand/hover on dashboard — show all conflict-indicator instances per flag with count badge (e.g., "F4 × 5") | F4 is active on 5 conflict-indicator pairs; dashboard only shows "F4 Active / Russia" | Low |
| SCEM | Active Conflicts cards — add count of deviating indicators this week (e.g., "4 indicators above baseline") | Communicates analytical severity at the card level before user drills into Indicator Breakdown | Low |
| SCEM | Persistent page: render `approaching_retirement[]` section | Pure rendering gap; field exists in schema; any conflict nearing retirement criteria should have a visible watch note | Low |
| SCEM | Schema version display — unify "Schema 2.0" (report) and "Schema 1.0" (persistent) into a single consistent version string | Erodes confidence in data integrity; if genuinely different versions, needs explicit documentation | Low |
| WDM | Surface `weekly_brief` on dashboard.html — 900–1,200 word narrative currently collected, rendered on report and persistent, but invisible on dashboard; add as a collapsible or scrollable section below the heatmap | Most substantial analytical content in each issue is hidden from the primary view | Low |
| WDM | Add monthly trend delta KPI cards — second row beneath existing KPI strip showing `±N vs 4w ago` for rapid_decay, watchlist, and recovery counts; show "tracking since Issue 1" if fewer than 4 issues exist | Most actionable single-number summary for a democratic health monitor; current KPI section is a snapshot without context | Low |
| WDM | Add `severity_sub` breakdown (electoral / civil_liberties / judicial) to heatmap country cards — once severity_sub lands in JSON, render as a three-segment bar or three sub-score badges on each country card in the Most Severe section | Makes every composite severity score interpretable at a glance; rendering slots exist, just waiting for data | Low |
| WDM | Add Recovery Progress and Watchlist Threshold sections to dashboard — dashboard shows only rapid_decay top 5; recovery and watchlist not rendered anywhere on dashboard; add "Recovery Progress" (5 countries) and "Watchlist Threshold" (3–5 closest to crossing rapid_decay line) sections | Colour-coded KPI bar shows 5 recovery entries but no recovery detail is visible; dashboard gives false impression of completeness | Medium |
| WDM | Add `signal.silent_erosion` analytical block to dashboard — distinct visual treatment (grey background, "Structural Signal" label, longer typography) below Lead Signal card once field arrives in JSON | Monitor’s highest-value differentiator for researchers, policy analysts, and journalists | Low |
| WDM | Surface `cross_monitor_flags` on dashboard — 6 flags (cms-001 to cms-006) rendered on report.html but invisible on dashboard; add compact "Cross-Monitor Signals" strip (cms-ID, title, monitors_involved, status) | Downstream monitors (SCEM, FCW, ESA, AGM) consult WDM dashboard as a primary feed; currently must navigate to report to see these flags | Low |

---

## 5. Methodology Improvements

Analytical improvements — coverage gaps, indicator set changes, framing issues.

| Monitor | Improvement | Priority |
|---|---|---|
| GMM | Replace narrative scoring with explicit weighted scoring model — `scoring_weights` block per asset class showing which indicators feed the score, their weight, and current flag contribution. A -0.908 on Consumer Staples is analytically opaque without a transparent formula | Critical |
| GMM | Formalise regime definition and transition rules — explicit entry/exit criteria (e.g., "STAGFLATION confirmed when: Core PCE > 3% AND GDP growth < 1% for 2 consecutive quarters AND system_average_score < -0.4") to make probabilities auditable and enable backtesting | High |
| GMM | Crisis threshold visualisation — add `distance_to_threshold` metric per domain indicator (standard deviations or percentage points from crisis level); display as a fill bar on the indicator grid | High |
| GMM | Formalise and expand blind spot override library — named patterns beyond current Rule 1/2 (add Rule 3: "Labour Market Masking", Rule 4: "Dollar Basis Distortion"); each rule with activation trigger, affected indicators, direction of correction, deactivation condition | High |
| GMM | Define `matt_agreement_pct` calculation methodology — which flags feed the numerator, how "market pricing" is measured for each, what 40% vs 80% implies for positioning; rename to `framework_market_alignment_pct` for clarity | Medium |
| GMM | Tail risk direction scoring — derive `direction` (Increasing/Stable/Decreasing) from observable indicator changes week-on-week rather than free-form analyst discretion | Medium |
| GMM | Deprecate legacy `debt_dynamics`/`credit_stress`/`systemic_risk` arrays once `domain_indicators` is fully rendered — prevent divergence between legacy arrays and domain_indicators for the same indicator (trump_tariffs, oil_supply_shock, consumer_confidence appear in both) | Medium |
| FCW | Narrative persistence tracking as first-class methodology — document how narratives are identified, bounded, and retired; complement the `narratives[]` schema registry | Critical |
| FCW | Cross-platform coherence detection protocol — add `cross_platform_coherence` field (NOT_ASSESSED/POSSIBLE/LIKELY/CONFIRMED) to campaigns + detection note; currently cross-platform synchronisation is noted but not systematically flagged | High |
| FCW | Attribution confidence escalation/de-escalation trigger documentation — explicit criteria for when attribution moves between tiers (Possible → Assessed → High → Confirmed and reverse); formal escalation matrix specifying T1/T2 evidence requirements per actor | High |
| FCW | Status-unchanged carry-forward policy — define: (a) maximum issues a campaign can be carried forward on unchanged status before moving to MONITORING/DORMANT; (b) what triggers a status review; (c) ONGOING vs. status-unchanged carry-forward distinction | High |
| FCW | Election-proximate FIMI density scoring — a density score accounting for confirmed/assessed operations count, attribution confidence, days to election, platform reach estimate; makes Hungary 2026 comparable to Germany 2025, France 2027 | High |
| FCW | AI-FIMI convergence tracking as structured sub-domain — `ai_fimi_indicators[]` field on relevant campaigns (synthetic media, LLM-generated text at scale, automated amplification, AI-generated imagery); feeds structured data to AGM cross-monitor flag | Medium |
| FCW | Formalise meta-FIMI as a campaign type — `is_meta_fimi: bool` + `primary_campaign_id` reference; distinguish media outlets with motivated editorial stance from state-directed counter-intelligence | Medium |
| ESA | Publish Autonomy Scorecard methodology document — define scoring rubric (0–100 per pillar), weighting formula for composite, update trigger criteria. Current scores are analytically unusable without it. Single largest credibility gap. | Critical |
| ESA | Integrate ReArm Europe (€800B) as a dedicated analytical thread — persistent "ReArm Europe Tracker" covering all 5 pillars (fiscal space ~€650B, SAFE €150B, EU budget reallocation, EIB capital, mini-Omnibus dual-use flexibility); cumulative disbursed vs. committed per pillar | Critical |
| ESA | Integrate EDIP as dedicated industrial capacity tracking — persistent `edip_tracker{}` covering open calls, awarded grants by country and capability area, running "EDTIB capacity delta" vs. stated baseline (155mm shell production rate); first calls opened 31 March 2026 | High |
| ESA | Formalise US-EU dependency as an analytical pillar — structured coverage of (a) trade exposure and tariff threat, (b) military dependence and equipment share, (c) tech dependency (CLOUD Act, AWS/Azure/Google share), (d) financial dependency (USD reserve, SWIFT alternatives) | High |
| ESA | Expand NATO burden-sharing to per-country GDP tracking — Poland at 4%+, Italy/Spain/Belgium near floor; new 5% Hague target creates a new gap; single "+20%" KPI tile understates the country-level picture | High |
| ESA | Add EU-China dependency thread as integrated analytical section — critical minerals (97% Mg from China, RE suspension), tech supply chains, Huawei/ZTE phase-out; currently dispersed across KPI tiles and prose | Medium |
| ESA | Connect `hybrid_threats[]` items to autonomy scorecard — add optional `autonomy_impact` field: which pillar does each item affect and in which direction; enables hybrid section to drive scorecard updates | Low |
| ESA | Establish retroactive Issue 1 baseline scoring for trend analysis — explicitly mark Issue 2 scores as "changed" or "unchanged from baseline"; from Issue 3 onward, every change accompanied by a named driver event | Medium |
| AGM | China coverage structural gap — add `china_capability_watch` persistent tracker (weekly token volume, open-weight vs. proprietary mix, frontier model release cadence, BIS enforcement signals) alongside existing `ciyuan_watch`; China Watch has been empty two consecutive issues despite active China signals | Critical |
| AGM | Underweighted signal: Compute access asymmetry below hyperscaler layer — inference-only providers (Together AI, Fireworks, Groq), academic compute access (NSF NAIRR, UK AIRR), Global South compute gap | High |
| AGM | Underweighted signal: Standards bodies as power structures — ISO/IEC SC 42 working group composition, national body positions, draft standard timelines by jurisdiction; `standards_geopolitics` sub-module | High |
| AGM | Underweighted signal: AI in democratic and electoral processes — `electoral_ai_governance` tracker; FEC inaction, state preemption of disclosure laws, structural detection vacuum created by SIO dismantlement before November 2026 | High |
| AGM | Underweighted signal: Autonomous weapons doctrine-deployment gap — add `doctrine_deployment_gap` persistent M08 field: `{system_type, stated_policy, operational_timeline, human_in_loop_feasible: boolean, source}` | High |
| AGM | Underweighted signal: AI Safety institution capacity metrics — per-body staffing, budget, enforcement powers, decisions-per-month for UK AISI, US CAISI, EU AI Office; converts "vacuum" narrative into measurable deterioration curve | High |
| AGM | IHL friction analysis must be visually distinguished in report — methodology says "mandatory for capability and doctrine items"; currently present but not labelled as IHL analysis in rendered output | Medium |
| ERM | Heat-stress economic productivity loss — add as standalone M04 sub-field or separate module; ILO models: 2.4% of global working hours lost by 2030 (equivalent to 80M full-time jobs); highest-dollar-value physical climate risk channel for investors | Critical |
| ERM | Financial sector transition risk — stranded asset tracker in M05: USD 1–4 trillion in fossil fuel assets that become uneconomic under <2°C (Carbon Tracker / IEA unburnable carbon framework); quarterly update | High |
| ERM | AMOC weakening → regional cascade chains — add structured `downstream_cascade_refs` to tipping system objects linking AMOC to relevant M03/M04 entries (West African monsoon timing, European winter extremes, Atlantic hurricane intensification) | High |
| ERM | Water-energy-food nexus country-level exposure index — `m03_country_exposure_index` with WEF nexus scores (FAO AQUASTAT + FEWS NET + IRENA inputs) for countries like Egypt, Pakistan, Jordan, Ethiopia; most investable output the monitor could produce | High |
| ERM | Tipping system interaction effects — `tipping_system_interactions` block in M02 with documented interaction pairs and amplification factors; AMOC + Amazon dieback together have nonlinear compounding effects (Lenton et al. 2019, Armstrong McKay et al. 2022) | High |
| ERM | Attribution science lag — add `attribution_status: pending/confirmed_anthropogenic/confirmed_natural/mixed` and `attribution_study_url` to M04 items; World Weather Attribution publishes within 2–4 weeks of major events | Medium |
| ERM | Reverse cascade methodology formalisation — formal definition of confirmed vs. assessed vs. hypothetical reverse cascade; evidence threshold for each; analogous to FIMI Monitor attribution confidence levels | Medium |
| ERM | TNFD biodiversity financial risk tracking in M07 — TNFD now in force for early adopters; track adoption rates and disclosure-to-action gap; analogous to M05 CSRD coverage | Medium |
| ERM | Unify schema versions — report-latest.json is v2.0; persistent-state.json is v1.0; inconsistent field structures (threshold fields exist only in persistent-state) | Low |
| SCEM | Add I7 (proxy/third-party warfare) to indicator framework — sub-indicators: state-sponsored external military support, proxy ground forces, mercenary/PMC deployment; requires methodology documentation, historical re-scoring, cron prompt update | High |
| SCEM | Add I8/expanded I1 for cyber/information warfare — offensive cyber operations as early warning indicator and escalation mechanism; particularly relevant for Taiwan/Korea latent conflicts where cyber is primary active escalation vector | High |
| SCEM | Baseline locking at W13: add conflict phase reset protocol — if a conflict transitions from latent to active during observation window, baseline period should restart from transition date; C10's contested I3 baseline includes W1 Natanz-strike aftermath, which will anchor "normal" at historically unprecedented levels | High |
| SCEM | Formalise confidence tier source-tier anchoring — Confirmed = T1 primary source independently corroborated; Probable = T2 source or single T1; Possible = T3 or inference; publish in methodology note and apply consistently | High |
| SCEM | F6 (Data Denial) must be triggered for currently suppressed indicators — DPRK I6 is explicitly noted as "unmonitorable (no T1 access)" but scored at structural zero rather than F6; Sudan I2 and Gaza I6 have known data gaps; F6 = CLEAR is analytically wrong | High |
| SCEM | Add F8 — Indicator Suppression by Belligerent (distinct from F6 general access denial) — active information warfare against the monitoring function (IRGC jamming, Russian EW affecting satellite imagery interpretation) | Medium |
| SCEM | Cross-conflict spillover methodology — structured linkage map section; US-Iran/Israel-Lebanon/Gaza nexus demonstrates cross-conflict spillover is now the dominant analytical challenge | High |
| SCEM | Roster additions/retirements assessment — Ethiopia Northern Theatre approaching inclusion; Gaza/Israel-Hamas approaching retirement criteria if ceasefire holds (I4/I5 < +1 for 4+ weeks); Sahel Fracture approaching threshold | Medium |
| WDM | Add `signal.silent_erosion` to cron schema as a required 300–600 word field per issue — surfaces structural democratic deterioration that is real and measurable but not generating news coverage; distinct from `signal.body` which summarises top stories; the monitor’s highest-value differentiator | Critical |
| WDM | Severity sub-dimension anchoring — publish explicit 1–10 anchor descriptions for the three dimensions (Electoral: 1 = free/fair/competitive, 10 = no meaningful elections; Civil Liberties: 1 = full freedoms, 10 = totalitarian suppression; Judicial: 1 = fully independent, 10 = fully captured); without anchors the composite score is not reproducible across LLM runs | Critical |
| WDM | Recovery classification rigour — add `reversal_risk` field (Low/Medium/High) to recovery entries to distinguish genuine democratic consolidations (Bolivia, South Korea: Low) from coerced or transactional transitions (Venezuela severity 7: High); current Recovery tier creates false equivalence | High |
| WDM | Heatmap `entry_type` taxonomy formalisation — define Episode / Persistent / Transient with explicit decision tree; currently inferred from data (Iraq: Transient severity 6; Colombia: Persistent severity 4 appears inconsistent given terror threat trajectory); document in methodology | High |
| WDM | Watchlist threshold weighting — replace raw `threshold_crossed` count with tier-weighted escalation score: Tier 1 structural/hard-to-reverse changes (constitutional, judicial packing, electoral redistricting) weight 3; Tier 2 legislative/reversible (foreign agent laws, NGO restrictions) weight 2; Tier 3 episodic (press crackdowns, individual prosecutions) weight 1; aligns with V-Dem indicator weighting | High |
| WDM | Cross-monitor feed protocol formalisation — add `priority` (1–5), `linked_countries[]`, `action_required_by`, and `confidence` fields to `cross_monitor_flags` entries; without these, downstream monitors (SCEM, FCW, ESA, AGM) consume WDM signals as unstructured text | High |
| WDM | Regional coverage expansion — Sub-Saharan Africa gaps (Ethiopia, Mozambique, Sudan, Zimbabwe, Cameroon, Rwanda absent); Central Asia gaps (only Kazakhstan tracked; Tajikistan, Kyrgyzstan absent); MENA gaps (Turkey’s ongoing V-Dem electoral autocracy designation absent despite NATO membership); gaps create selection bias in mimicry chain analysis | High |
| WDM | Source diversity discipline — CIVICUS appears in ~40% of heatmap entry evidence (Issues 1–3); require per-entry source diversity: at minimum one V-Dem/Freedom House/IDEA source AND one current-week source (RSF, IPI, CIVICUS watchlist, Election Watch, HRW); flag single-source entries | Medium |
| WDM | Mimicry chain transmission vs correlation distinction — require documented transmission pathway (direct legislative copying / advisory / learning / IO-mediated) and a counterfactual test for each chain; current chains assert connections without evidencing the transmission mechanism | Medium |
| WDM | `research_360.friction_notes` prominence — when Category B lands in Issue 4, position friction notes early in methodology section (not buried at bottom of report.html) and link from heatmap entries where source conflict exists; these are the most analytically distinctive section for methodology credibility | Medium |

---

## 6. Cross-Monitor Patterns

Issues that appear in multiple monitors and should be fixed globally.

### 6.1 Bar charts show current level, not deviation from baseline
**Monitors:** SCEM (confirmed), ERM (planetary boundary chart shows binary Safe/Transgressed, not degree)  
The SCEM Indicator Breakdown bar chart shows indicator level (1–5) rather than deviation from baseline — users see identical full bars for Russia-Ukraine I1=5 (deviation=0) and Sudan I6=5 (deviation=+1). The ERM planetary boundary chart similarly treats all "Transgressed" boundaries as equal-height red bars regardless of how far beyond the boundary the system actually sits. In both cases, the visual communicates a qualitatively different (and less accurate) message than the underlying data supports.  
**Global fix:** Any bar chart where the analytical concept is deviation or distance from threshold must add a baseline/threshold marker and render the excess-above-baseline as a distinct fill colour. This is a template/CSS fix applicable wherever the pattern appears.

### 6.2 Entire sections absent from dashboard that are present on report/persistent
**Monitors:** WDM (`weekly_brief` 6,369 chars collected and rendered on report/persistent but absent from dashboard; recovery and watchlist sections also absent from dashboard), FCW (platform_responses, cognitive_warfare, attribution_log entirely absent from dashboard), ESA (institutional_developments entirely absent from dashboard), AGM (M01, M04, M08, M10, M11, M14 entirely absent from dashboard), ERM (M03 cascade chains entirely absent from dashboard), SCEM (roster_watch, cross_monitor_flags, lead_signal source_url absent from dashboard)  
Every monitor has at least one analytically important section that is collected, rendered on report.html, but completely invisible on the primary dashboard view. This is a systemic architectural pattern: the report is comprehensive but the dashboard is underpowered, causing dashboard-only users to receive a materially incomplete picture.  
**Global fix:** Define a "dashboard minimum" standard — every section that reaches a designated signal threshold must have at least a compact widget/card on the dashboard. Implement a review pass for each monitor to identify sections meeting this threshold that are currently absent.

### 6.3 `cross_monitor_flags` not rendered on dashboard
**Monitors:** GMM, WDM (6 flags cms-001 to cms-006 rendered on report.html but absent from dashboard and persistent), FCW (ESCALATED flags CMF-001/CMF-002 invisible on dashboard), ESA (section present but always empty), AGM (6 flags fully rendered on persistent only), ERM (rendered on report, absent from dashboard), SCEM (absent from dashboard)  
Across all monitors, cross_monitor_flags are either invisible on the dashboard or not populated at all. This is the primary mechanism for cross-monitor signal propagation and its invisibility at the dashboard level defeats its purpose.  
**Global fix:** Every dashboard must include a compact "Cross-Monitor Signals" widget showing count + status. ESCALATED/CRITICAL flags must trigger an alert banner. The widget should be a shared template component implemented once and used across all monitors.

### 6.4 `source_url` fields stripped from dashboard views
**Monitors:** GMM (source_url never linked on any page for individual indicators), WDM (all 29 heatmap entries have empty-string source_url — key present, value always absent; this is both a bug and a credibility issue), FCW (source_url absent from dashboard campaign cards), ESA (source URLs stripped from Top Items), ERM (m00.source_url absent from dashboard Lead Signal card), SCEM (lead_signal.source_url absent from dashboard)  
Nearly every monitor collects `source_url` at the indicator/item level but dashboard templates systematically strip it. Analysts using the dashboard as their primary view cannot verify sources without navigating to the full report. WDM’s case is the most severe: the field is present in the schema but no country entry has ever had a non-empty value across three issues, meaning the classification is untraceable at any page level.  
**Global fix:** Add a source link ("→ Source") to every dashboard card/item where `source_url` exists in the JSON. For WDM specifically, enforce non-empty `source_url` in cron schema validation before the rendering fix is relevant. One-line template change per card type once populated. Implement as a global UI standard.

### 6.5 `update_this_week` / changelog / `last_activity` staleness not displayed
**Monitors:** GMM (`update_this_week` collected for every domain indicator, rendered on zero pages), FCW (`campaigns[].changelog` not rendered in report), FCW (no staleness indicator for campaigns with old `last_activity` dates), ERM (multiple `last_updated` fields not rendered)  
The most analytically dense "what changed this week" content is systematically invisible across monitors. Weekly intelligence monitors that don't surface weekly changes reduce themselves to static snapshots.  
**Global fix:** Every item-level card on report.html must surface the "what changed" field (whatever it is named per monitor: `update_this_week`, `changelog`, `last_activity`). Dashboard items should show at minimum a staleness indicator when last update is > N weeks old.

### 6.6 `cross_monitor_flags.version_history` never rendered anywhere
**Monitors:** GMM, FCW, ERM (empty array field in JSON), SCEM (section empty in report template)  
The change history for cross-monitor flag escalations is completely invisible across all monitors. When a flag escalates from STRUCTURAL to ESCALATED, there is no record visible to users.  
**Global fix:** Populate `version_history` arrays when flag status changes. Render as a changelog in the persistent page's Cross-Monitor section for all monitors.

### 6.7 Schema version inconsistency between report JSON and persistent JSON
**Monitors:** SCEM (report says Schema 2.0, persistent says Schema 1.0), ERM (report-latest.json is v2.0, persistent-state.json is v1.0)  
Two monitors have report and persistent JSON at different schema versions with inconsistent field structures. This creates maintenance risk where a field added to v2.0 may not exist in persistent-state and vice versa.  
**Global fix:** Unify schema versions across all JSON files for each monitor. Run a compatibility audit before the next schema version increment.

### 6.8 `domain_indicators` / expanded indicator objects not rendered (GMM-specific but pattern-relevant)
**Monitor:** GMM, with the general pattern appearing in AGM (entire modules absent from dashboard)  
The GMM v2.0 `domain_indicators` object was added alongside the legacy domain arrays, creating redundant data. Indicators appear in both `systemic_risk` (legacy) and `domain_3_market_structure` (new) with potential for divergence. The same pattern applies wherever schema expansions create parallel data paths.  
**Global fix:** When a new schema structure replaces a legacy one, deprecate the legacy structure with a documented migration path. Do not maintain parallel arrays indefinitely.

---

## 7. Prioritised Sprint Plan

### Sprint 1 — Do Now (this session or next)
*Rendering bugs, low-effort high-value surfacing, schema fixes with no new collection required*

| Monitor(s) | Action | Type | Effort |
|---|---|---|---|
| AGM | Fix 3 `undefined` rendering bugs on persistent.html: M07 Risk Vectors, M15 AISI Pipeline, M15 Ongoing Lab Postures | Bug | Low |
| AGM | Fix Delta Strip on dashboard — render the 5 items, not just the count | Bug | Low |
| SCEM | Fix report.html Roster Watch section — inject `roster_watch` data into the report template | Bug | Low |
| SCEM | Fix report.html Cross-Monitor section — inject `cross_monitor_flags` data into the report template | Bug | Low |
| SCEM | Fix dashboard Indicator Breakdown bar chart — add baseline marker line and two-tone fill so deviation (not level) is visualised | Bug | Low |
| SCEM | Add contested-baseline disclaimer to Global Escalation Index | Bug | Low |
| SCEM | Fix schema version mismatch (report: 2.0, persistent: 1.0) | Bug | Low |
| ESA | Fix Lagrange Point radar — add Institutions spoke (6th dimension) | Bug | Low |
| AGM | Fix M06 arXiv entry — render title, significance note, not just metadata stub | Bug | Low |
| GMM | Promote `hard_landing_risk.score` to a 4th KPI card on dashboard — zero schema change | Rendering | Low |
| GMM | Add tail risk `note` as tooltip on heatmap hover | Rendering | Low |
| GMM | Add `condition_for_reassessment` to dashboard Safe Haven card | Rendering | Low |
| GMM | Add `macro_indicators_affected` chips on cross-monitor flags (report.html) | Rendering | Low |
| GMM | Add `not_investment_advice` disclaimer to Safe Haven section | Rendering | Low |
| GMM | Add `update_this_week` as expandable accordion per domain indicator on report.html | Rendering | Low |
| FCW | Fix `attribution_log[].instrument` population error (set to technique, not confidence) | Schema | Low |
| FCW | Fix `attribution_log[].actor` population error (set to actor code, not campaign_id) | Schema | Low |
| FCW | Add `threat_level` object to JSON schema and wire to dashboard banner | Schema | Low |
| FCW | Add ESCALATED cross_monitor_flags alert banner/card on dashboard | Rendering | Low |
| FCW | Surface all 12 campaigns on dashboard (secondary grid for campaigns 6–12) | Rendering | Low |
| FCW | Add campaign `platform` and `target` labels to dashboard campaign cards | Rendering | Low |
| FCW | Add campaign `changelog` "What changed this issue" line to report.html | Rendering | Low |
| FCW | Add last-intelligence staleness indicator for campaigns with `last_activity` > 4 weeks | Rendering | Low |
| FCW | Add `f_flags` badges to dashboard campaign cards | Rendering | Low |
| ESA | Surface `institutional_developments[]` in dashboard Top Items strip | Rendering | Low |
| ESA | Add source links to dashboard Top Items entries | Rendering | Low |
| ESA | Add issue navigation/archive widget to dashboard | Rendering | Low |
| ESA | Add institutional developments card strip to dashboard | Rendering | Low |
| ESA | `cross_monitor_flags` — define population trigger criteria and enforce, or explicitly retire the dead schema field | Schema | Low |
| AGM | Collapse "No items this issue" modules by default on report.html | Rendering | Low |
| AGM | Add module density count badge to sidebar nav | Rendering | Low |
| AGM | Country Grid — add Regulatory Velocity column | Rendering | Low |
| AGM | Add cross_monitor_flags widget to dashboard ("6 Active") | Rendering | Low |
| AGM | Add `regulatory_calendar` structured array to schema (largely data entry from existing M05/M09 content) | Schema | Low |
| AGM | Add `flag_type` field to asymmetric flags | Schema | Low |
| AGM | Add Investment Flow structured object to M03 | Schema | Low |
| ERM | Add M03 cascade tier breakdown to report.html — render tier_1_physical / tier_2_human / tier_3_political per M03 item | Rendering | Low |
| ERM | Add cascade chain heatmap to dashboard (3-column Physical/Human/Political grid) | Rendering | Low |
| ERM | Add `reverse_cascade_check` to report.html M03 section | Rendering | Low |
| ERM | Add source link to dashboard Lead Signal (M00) card | Rendering | Low |
| ERM | Add `why_it_matters` as second line in dashboard delta strip | Rendering | Low |
| ERM | Add `dual_edge` badge (Positive/Negative) to M06 items in report | Rendering | Low |
| ERM | Render `threshold_lower/upper_bound_pct` for Amazon dieback on persistent page | Rendering | Low |
| ERM | Add `reverse_cascade` structured field to M03 (replaces prose `reverse_cascade_check`) | Schema | Low |
| ERM | Add `cascade_stage` enumerated status to M03 | Schema | Low |
| ERM | Add `escalation_trigger` and `escalation_threshold_met` to cross_monitor_flags | Schema | Low |
| ERM | Add `m04_ytd_summary` block to schema | Schema | Low |
| SCEM | Add `negotiation_status` per conflict to schema | Schema | Low |
| SCEM | Add `external_actors[]` per conflict to schema | Schema | Low |
| SCEM | Add `sources[]` structured array per conflict | Schema | Low |
| SCEM | Add `conflict_phase` field per conflict | Schema | Low |
| SCEM | Add `conflict_linkages[]` array per conflict | Schema | Low |
| SCEM | Delta Strip — show count of deviating indicators alongside highest deviation | Rendering | Low |
| SCEM | F-Flag tiles — add count badge ("F4 × 5") and expand/hover for all instances | Rendering | Low |
| SCEM | Active Conflicts cards — add count of deviating indicators | Rendering | Low |
| SCEM | Dashboard lead signal — add `source_url` link | Rendering | Low |
| SCEM | Persistent page — render `approaching_retirement[]` section | Rendering | Low |
| SCEM | Populate `conflict_context` rendering scaffolding (data arriving Apr 5 cron) | Rendering | Medium |
| GMM | Add `prior_regime`, `regime_change_date`, `weeks_in_current_regime` to `signal` block | Schema | Low |
| GMM | Add `source_quality_flags` (F1/F2/F3) on individual indicators | Schema | Low |
| GMM | Add `credit_spreads` object to schema | Schema | Low |
| FCW | Populate `start_date` on campaigns and update persistent timeline Gantt to use it | Schema | Low |
| FCW | Add `linked_campaigns[]` field to campaigns | Schema | Low |
| FCW | Add `enforcement_completeness` fields to `platform_responses[]` | Schema | Low |
| FCW | Add `event_horizon[]` array for election calendar | Schema | Low |
| ALL | Add source link ("→ Source") to every dashboard card/item where `source_url` exists | Rendering | Low |
| ALL | Add compact Cross-Monitor Signals widget to every dashboard | Rendering | Low |
| WDM | Fix `heatmap[*].source_url` — enforce non-empty string in cron schema validation; populate with authoritative V-Dem/CIVICUS/Freedom House canonical URL per country, or restructure as `sources[]` array (1–3 per entry) | Bug | Low |
| WDM | Enforce `severity_sub` output from cron — add schema validation to require electoral/civil_liberties/judicial sub-scores per heatmap entry; retry or surface schema error if LLM omits; render in existing table slots | Bug | Low |
| WDM | Add `heatmap.recovery[*].lead_signal` and `heatmap.watchlist[*].lead_signal` — parity with rapid_decay; single cron prompt fix; renders immediately in existing table layout | Bug | Low |
| WDM | Add `signal.silent_erosion` to cron schema as required 300–600 word field — the monitor’s highest-value analytical differentiator; render on dashboard and report | Schema + Rendering | Low |

---

### Sprint 2 — Next 2 Sessions
*Medium-effort schema and rendering work; requires cron changes or template restructuring*

| Monitor(s) | Action | Type | Effort |
|---|---|---|---|
| GMM | Add `sentiment_overlay` Fed path table to dashboard and report — 5-row table: Meeting / Cut Probability / Our View / Note | Rendering | Medium |
| GMM | Add `regime_shift_probabilities` 4-bar chart to Signal section on dashboard and report | Rendering | Medium |
| GMM | Add `scenario_analysis` three-scenario panel to dashboard | Rendering | Medium |
| GMM | Add Real M2 five-deflator waterfall bar chart to dashboard | Rendering | Medium |
| GMM | Add VIX term structure and Treasury liquidity as Domain 3 named numeric indicators to cron | Schema | Medium |
| GMM | Add `custody_migration` and `gold_reserve_ratio` to Domain 1 cron collection | Schema | Medium |
| GMM | Add `dollar_funding_fx_basis` and `margin_debt` as Domain 3 TS indicators | Schema | Medium |
| GMM | Add tariff impact quantification sub-fields to trump_tariff_escalation indicator | Schema | Medium |
| GMM | Add delta vs. baseline column to persistent.html asset class chart | Rendering | Low |
| FCW | Add `narratives[]` registry to schema + `narrative_ids[]` to campaigns — foundation for cross-campaign narrative tracking | Schema | High |
| FCW | Add `effectiveness` object per campaign (reach, amplification, counter_response, narrative_penetration) | Schema | Medium |
| FCW | Migrate `cognitive_warfare[]` entries to persistent layer with `first_identified` and `status` | Schema | Medium |
| FCW | Add platform enforcement summary widget to dashboard (Platform / Action / Date / Status) | Rendering | Medium |
| FCW | Add Actor Threat Board doctrine label and current `actor_tracker[].headline` | Rendering | Low |
| FCW | Add Cognitive Warfare panel to dashboard (2–3 CW headlines) | Rendering | Medium |
| ESA | Add `defence_spending[]` array to schema per member state | Schema | Medium |
| ESA | Add `scorecard[]` array with structured pillar fields including `delta_from_last_issue` and `direction` | Schema | Medium |
| ESA | Add `us_dependency[]` array to schema | Schema | Medium |
| ESA | Add `defence_programmes[]` persistent tracker to schema | Schema | Medium |
| ESA | Add `composite_index_history[]` for issue-by-issue trend | Schema | Low |
| ESA | Add delta arrows (▲/▼/–) to pillar scores on dashboard scorecard | Rendering | Medium |
| ESA | Replace "~35%" gauge with labelled pillar breakdown bar chart | Rendering | Medium |
| ESA | Make Member State Tracker sortable/filterable by status | Rendering | Medium |
| AGM | Build the Governance Health Composite Score (schema + dashboard widget) | Schema | Medium |
| AGM | Activate Risk Vector Heat Grid — fix rendering and elevate to second dashboard element with delta arrows | Rendering | Low |
| AGM | Add M04 Sector Penetration Heat Map to dashboard (7-cell sector grid) | Rendering | Low |
| AGM | Add Jurisdiction Risk Matrix (structured Country Grid extension) | Schema | Medium |
| AGM | Add Lab Governance Posture Scorecard per major lab | Schema | Medium |
| AGM | Build digest.html — Signal + delta_strip + M07 risk ratings + M14 concentration index + cross_monitor_flags | Rendering | Medium |
| AGM | Persistent page — add time-series trend lines to Concentration Index (M14) | Rendering | Medium |
| ERM | Add planetary boundary numeric proximity score to schema + upgrade persistent boundary chart to variable bar heights | Schema | Medium |
| ERM | Standardise tipping system proximity-to-threshold fields across all 6 systems + add dashboard gauge | Schema | Medium |
| ERM | Add M05 regulatory pipeline tracker to schema | Schema | Medium |
| ERM | Add M08 supply chain concentration index per resource | Schema | Medium |
| ERM | Add `m02.boundaries[].summary` expandable row on dashboard | Rendering | Low |
| ERM | Unify report-latest.json (v2.0) and persistent-state.json (v1.0) schema versions | Methodology | Low |
| SCEM | Add `escalation_velocity` field to schema — requires prior-week state in cron | Schema | Medium |
| SCEM | Add `esc_score` composite per conflict | Schema | Medium |
| SCEM | Add PROVISIONAL band tier for CONTESTED-period RED-band deviations (≥+2) — schema change + dashboard index recalibration | Schema | Medium |
| SCEM | Add I7 proxy/third-party warfare indicator — methodology documentation + historical re-scoring | Methodology | High |
| SCEM | Add conflict phase reset protocol to baseline locking methodology (new-conflict transition case) | Methodology | Medium |
| SCEM | Formalise confidence tier source-tier anchoring in methodology document | Methodology | Medium |
| SCEM | Activate F6 flags for DPRK I6, Sudan I2, Gaza I6 (currently showing CLEAR when data denial is documented) | Methodology | Low |
| FCW | Document attribution confidence escalation/de-escalation matrix | Methodology | Medium |
| FCW | Define and implement status-unchanged carry-forward policy | Methodology | Medium |
| ESA | Publish Autonomy Scorecard methodology document (scoring rubric, weighting formula, update triggers) | Methodology | Medium |
| ALL | Implement `version_history` population when cross_monitor_flag status changes; render as changelog on persistent page | Rendering | Medium |
| WDM | Add `wdm_stress_index` aggregate (0–100 deterioration composite across rapid_decay + watchlist severity scores, with `direction` and `delta`) — schema addition + dashboard KPI tile | Schema + Rendering | Medium |
| WDM | Add severity score version history to persistent-state per country — issue-by-issue log analogous to GMM’s `conviction_history`; enables trend lines on persistent country cards | Schema | Medium |
| WDM | Surface `weekly_brief` on dashboard.html — collapsible or scrollable section below heatmap; 900–1,200 word narrative currently invisible on primary view | Rendering | Medium |
| WDM | Add monthly trend delta KPI row to dashboard — `±N vs 4w ago` for rapid_decay, watchlist, recovery counts; implement `monthly_trend` block in cron; render as second KPI strip and trend chart on persistent (available at Issue 5) | Schema + Rendering | Medium |

---

### Sprint 3 — Planned Work
*High-effort structural improvements; requires architectural changes, new data collection, or external research*

| Monitor(s) | Action | Type | Effort |
|---|---|---|---|
| GMM | Build domain_indicators expandable grid on report.html — 6 domain headers × ~4 indicators with flag badge, score bar, SA/CC/TS badge, reading, crisis threshold | Rendering | High |
| GMM | Render `domain_indicators` Domains 4 and 5 (Real Economy; Composite Indices) — completely invisible to users | Rendering | High |
| GMM | Implement explicit weighted scoring model with `scoring_weights` block per asset class | Methodology | High |
| GMM | Add scenario-conditional asset class impacts sub-object to `scenario_analysis` entries | Schema | High |
| GMM | Formalise regime definition and transition rules with explicit entry/exit criteria | Methodology | High |
| GMM | Expand and formalise blind spot override library (Rules 3, 4, etc.) | Methodology | High |
| GMM | Deprecate legacy domain arrays (`debt_dynamics`/`credit_stress`/`systemic_risk`) after domain_indicators is fully rendered | Schema | High |
| FCW | Build `narratives[]` registry rendering — cross-campaign narrative tracking view | Rendering | High |
| FCW | Implement election-proximate FIMI density scoring methodology | Methodology | High |
| FCW | Add AI-FIMI convergence as structured sub-domain with `ai_fimi_indicators[]` | Schema | Medium |
| FCW | Add `source_tier` classification to all source_url-bearing entries | Schema | Medium |
| ESA | Add `us_eu_bilateral_state{}` object to schema + surface as dashboard indicator | Schema | Medium |
| ESA | Add `edtib_capacity{}` tracker | Schema | Medium |
| ESA | Integrate EDIP as dedicated industrial capacity tracking thread | Methodology | High |
| ESA | Formalise US-EU dependency as analytical pillar (trade, military, tech, financial dimensions) | Methodology | High |
| ESA | Add EU-China dependency as integrated analytical thread | Methodology | Medium |
| AGM | Build Capability-Governance Lag Index (capability event scoring + governance response scoring + rolling 12-week lag chart) | Schema | High |
| AGM | Add `capability_profile` per tracked model with per-dimension scoring | Schema | Medium |
| AGM | Restructure China coverage into persistent `china_capability_watch` tracker | Methodology | Medium |
| AGM | Add `standards_geopolitics` sub-module for ISO/IEC SC 42 and JTC21 tracking | Methodology | High |
| AGM | Add `electoral_ai_governance` structured tracker | Methodology | High |
| AGM | Add `doctrine_deployment_gap` persistent M08 field for autonomous weapons | Methodology | High |
| AGM | Add `oversight_capacity_index` per safety body (staffing, budget, decisions, enforcement actions) | Methodology | Medium |
| AGM | Add Export Control Tracker as persistent structured module | Schema | Medium |
| AGM | Add Benchmark Contamination / Eval Integrity flag to M02 | Schema | Medium |
| ERM | Add heat-stress economic productivity loss as M04 sub-field or separate module | Methodology | High |
| ERM | Add stranded asset / financial sector transition risk tracker to M05 | Methodology | High |
| ERM | Add `downstream_cascade_refs` linking tipping systems to relevant M03/M04 entries | Schema | Medium |
| ERM | Build water-energy-food nexus country-level exposure index (`m03_country_exposure_index`) | Methodology | High |
| ERM | Add tipping system interaction effects block (`tipping_system_interactions` with documented amplification factors) | Methodology | High |
| ERM | Add geospatial precision fields to M03/M04 (bounding box or GeoJSON reference for asset-level risk mapping) | Schema | High |
| ERM | Add sovereign credit exposure sub-field to M03 cascade chains | Schema | Medium |
| ERM | Add TNFD biodiversity financial risk tracking to M07 | Methodology | Medium |
| ERM | Formalise reverse cascade assessment rubric (confirmed / assessed / hypothetical with evidence thresholds) | Methodology | Medium |
| SCEM | Add I8 / expanded I1 for cyber/information warfare indicator | Methodology | High |
| SCEM | Build cross-conflict linkage map — structured `conflict_linkages[]` rendering + "Linkage Map" section on dashboard/report | Rendering | High |
| ALL | Global scoring transparency initiative — every monitor that produces composite scores or ratings must publish a scoring rubric page with (a) what 0/50/100 means, (b) weighting formula, (c) update trigger criteria | Methodology | High |
| ALL | Sub-weekly hot_signal surfacing mechanism — RSS/webhook/persistent page update for Signal-threshold items that occur mid-week | Schema | High |
| WDM | Render `networks` section once Category B lands (Issue 4, verify Mon 6 April) — stub exists on persistent.html; verify all 9 Category B sections (electoral_watch, digital_civil, autocratic_export, state_capture, institutional_pulse, legislative_watch, research_360.friction_notes, networks, monthly_trend) render correctly; position `friction_notes` prominently in methodology section | Rendering | Medium |
| WDM | Regional coverage expansion — add Turkey, Ethiopia, Sudan, Zimbabwe at minimum; their absence creates selection bias in regional_mimicry_chains analysis (Ethiopia enacted a Russian-template CSO law in 2009, precursor to several African chain adoptions) | Methodology | High |

---

*End of Master Action Plan. Total items: ~210 distinct actions across 7 sections.*

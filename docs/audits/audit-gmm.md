# GMM Domain Audit
*Audit date: 1 April 2026 | Analyst: Domain Expert | Schema v2.0 | Issue 2 / Vol 1*

---

## Part 1: Collected But Not Surfaced

The table below maps every significant field in `report-latest.json` (and `persistent-state.json`) against what is actually rendered on each of the three live pages. "Rendered" means a user can read the value, chart, or text — not merely that the page loads data that drives invisible logic.

### Legend
- **✅ Yes** — field is rendered, readable by the user
- **⚠️ Partial** — some sub-fields rendered, others silently dropped
- **❌ No** — field is in the JSON but user cannot see it

---

### 1.1 `meta` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `issue`, `volume`, `week_label` | ✅ | ✅ | ✅ | ✅ |
| `published` | ✅ | ✅ | ✅ | ✅ |
| `schema_version` | ✅ | ❌ | ❌ | ✅ (footer) |
| `methodology_url` | ✅ (cron schema) | ❌ | ❌ | ❌ |
| `flag_definitions` (F1/F2/F3) | ✅ (cron schema) | ❌ | ❌ | ❌ |
| `editor` | ✅ | ❌ | ✅ | ❌ |

**Gap:** `flag_definitions` (F1/F2/F3 source-quality flags) are defined in the cron schema and referenced in the brief, but no page exposes a legend or applies the badges visually. Users see `update_this_week` text citing Bloomberg etc. but have no F-flag status visible.

---

### 1.2 `signal` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `system_stress_label` | ✅ | ✅ | ✅ | ❌ |
| `system_stress_direction` | ✅ | ✅ (KPI card) | ✅ | ❌ |
| `system_average_score` | ✅ | ✅ (KPI card) | ❌ | ✅ (conviction chart) |
| `delta_vs_prior` | ✅ | ✅ (KPI card Δ) | ❌ | ❌ |
| `regime` | ✅ | ✅ | ✅ | ✅ (conviction chart) |
| `regime_conviction` | ✅ | ✅ | ✅ | ✅ (conviction chart) |
| `headline` | ✅ | ✅ | ✅ | ❌ |
| `no_tactical_alerts` | ✅ | ❌ | ❌ | ✅ |
| `source_url` | ✅ | ❌ | ❌ | ❌ |
| `regime_shift_probabilities.stay_stagflation` | ✅ | ❌ | ❌ | ❌ |
| `regime_shift_probabilities.deflationary_bust` | ✅ | ❌ | ❌ | ❌ |
| `regime_shift_probabilities.inflationary_boom` | ✅ | ❌ | ❌ | ❌ |
| `regime_shift_probabilities.goldilocks` | ✅ | ❌ | ❌ | ❌ |

**Gap:** `regime_shift_probabilities` — four probabilities summing to 1.0 (stay_stagflation 60%, deflationary_bust 25%, inflationary_boom 10%, goldilocks 5%) — are collected every week but rendered **nowhere**. This is the most significant single omission: it is a four-way probability distribution that investors could use for regime hedging, yet it is completely invisible on all three pages.

---

### 1.3 `executive_briefing` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `system_stress_label` | ✅ (duplicate) | ✅ | ✅ | ❌ |
| `summary` | ✅ | ✅ | ✅ | ❌ |
| `one_number_to_watch` | ✅ | ✅ | ✅ | ❌ |
| `one_indicator_lying` | ✅ | ❌ | ✅ | ❌ |
| `base_case_label` | ✅ | ❌ | ✅ (inline) | ❌ |
| `base_case_probability` | ✅ | ❌ | ✅ (inline) | ❌ |
| `scenario_analysis[0] Base Case` | ✅ | ❌ | ❌ | ❌ |
| `scenario_analysis[1] De-escalation` | ✅ | ❌ | ❌ | ❌ |
| `scenario_analysis[2] Fast Cascade` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.nominal` | ✅ | ❌ | ⚠️ (in one_indicator_lying text only) | ❌ |
| `real_m2.vs_cpi` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.vs_pce` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.vs_core_pce` | ✅ | ❌ | ⚠️ (in one_indicator_lying text only) | ❌ |
| `real_m2.vs_ppi` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.vs_core_ppi` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.direction` | ✅ | ❌ | ❌ | ❌ |
| `real_m2.note` | ✅ | ❌ | ❌ | ❌ |
| `hard_landing_risk.score` | ✅ | ❌ | ❌ | ❌ |
| `hard_landing_risk.direction` | ✅ | ❌ | ❌ | ❌ |
| `hard_landing_risk.note` | ✅ | ❌ | ❌ | ❌ |
| `regime_shift_probabilities` (duplicate) | ✅ | ❌ | ❌ | ❌ |

**Gaps:**
- The full `scenario_analysis` array (three structured scenarios with names, probabilities, horizons, descriptions) is collected weekly but rendered on **no page**. The report.html only shows "Base case: Slow Burn (55%)" inline in the signal block — none of the De-escalation or Fast Cascade scenarios surface at all.
- The five-deflator Real M2 stack (`nominal`, `vs_cpi`, `vs_pce`, `vs_core_pce`, `vs_ppi`, `vs_core_ppi`) — which the cron explicitly calls a "waterfall chart" — is collected in full but rendered nowhere as a chart or table. The only exposure is a brief mention in `one_indicator_lying`.
- `hard_landing_risk.score` (0.38, Increasing) is collected weekly but invisible on all three pages. This is a single number that synthesizes all leading recession indicators into one probability — exactly the kind of KPI investors expect prominently.

---

### 1.4 `debt_dynamics`, `credit_stress`, `systemic_risk` domain arrays

These three arrays are the "legacy" domain structure that predates the `domain_indicators` object. They carry `indicator`, `flag`, `score`, `direction`, `reading`, `update_this_week`, `source_url`.

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `indicator` name | ✅ | ✅ (WARNING cards) | ✅ (section header) | ❌ |
| `flag` | ✅ | ✅ (WARNING cards) | ✅ | ❌ |
| `score` | ✅ | ❌ | ❌ | ❌ |
| `direction` | ✅ | ❌ | ❌ | ❌ |
| `reading` | ✅ | ✅ (WARNING cards) | ✅ | ❌ |
| `update_this_week` | ✅ | ❌ | ❌ | ❌ |
| `source_url` | ✅ | ❌ | ❌ | ❌ |

**Gaps:**
- `score` on domain-level indicators (debt_dynamics, credit_stress, systemic_risk) is never shown. The dashboard shows WARNING/ELEVATED/GREEN badges but not the underlying numeric score (e.g. -0.3 vs -1.0). Users cannot distinguish between an ELEVATED at -0.3 (mild) and approaching -1.0 (near-WARNING).
- `update_this_week` — the most analytically rich field in the entire schema; contains 2–5 sentences with source attribution, named figures, and quantified changes — is collected for every indicator but rendered on **no page**. Users see only the `reading` (a static snapshot). The fresh weekly intelligence is completely hidden.
- `source_url` for individual indicators is never linked anywhere, making it impossible for users to verify claims or drill down.
- The `current_driver` field on `oil_supply_shock` (the named geopolitical root cause) is not rendered on the report or dashboard — only visible on persistent.html's Oil Shock Driver section.

---

### 1.5 `domain_indicators` object (6 domains × ~4 indicators)

This is the expanded indicator layer added in schema v2.0. It adds `indicator_type` (SA/CC/TS), `crisis_threshold`, and `blind_spot_rule` fields.

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `indicator` name | ✅ | ❌ | ❌ | ❌ |
| `flag` | ✅ | ❌ | ❌ | ❌ |
| `score` | ✅ | ❌ | ❌ | ❌ |
| `direction` | ✅ | ❌ | ❌ | ❌ |
| `reading` | ✅ | ❌ | ❌ | ❌ |
| `indicator_type` (SA/CC/TS) | ✅ | ❌ | ❌ | ❌ |
| `crisis_threshold` | ✅ | ❌ | ❌ | ❌ |
| `update_this_week` | ✅ | ❌ | ❌ | ❌ |
| `blind_spot_rule` | ✅ | ❌ | ❌ | ❌ |
| `source_url` | ✅ | ❌ | ❌ | ❌ |

**Major gap:** The entire `domain_indicators` object — 6 domains, ~24 indicators with their types, crisis thresholds, blind spot rules, and weekly updates — is collected but **rendered on zero pages**. The report.html section headers for Debt Dynamics, Credit Stress, Systemic Risk, Amplifiers reference "Domain 1–6" but only pull from the legacy top-level arrays. Domain 4 (Real Economy: ISM PMI 52.4, Jobless Claims 205K, Cass Freight -7.2%, Earnings Revisions +12.5%) and Domain 5 (STLFSI, NFCI, IIF Global Debt, 0DTE Volume Ratio) are entirely invisible to users. Domain 6 (Dollar Weaponisation, AI Infrastructure Debt) is mentioned in report.html's "Systemic Amplifiers" section header but the actual domain_indicators entries for it are not rendered — only the legacy systemic_risk array items appear.

The `indicator_type` badges (SA = Strategic Anchor, CC = Cycle Coincident, TS = Tactical Signal) are a deliberate analytical filter helping investors distinguish slow-moving structural risks from fast-moving positioning signals. These badges are defined in the cron prompt's canonical mapping but rendered nowhere.

The `crisis_threshold` field — which contextualizes where each indicator sits relative to historically dangerous levels — is collected for all domain indicators but shown to users on no page.

---

### 1.6 `tail_risks` array (6 items)

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `label` | ✅ | ✅ (heatmap) | ❌ | ❌ |
| `likelihood` (x-axis) | ✅ | ✅ (heatmap positioning) | ❌ | ❌ |
| `impact` (y-axis) | ✅ | ✅ (heatmap positioning) | ❌ | ❌ |
| `direction` (↑/→/↓) | ✅ | ✅ (arrow prefix) | ❌ | ❌ |
| `note` | ✅ | ❌ | ❌ | ❌ |
| `id` | ✅ | ❌ | ❌ | ❌ |
| Near/Medium horizon (embedded in note) | ✅ | ❌ | ❌ | ❌ |

**Gap:** `note` — the one-sentence explanation of what triggers the tail risk and why it matters now, including the Near/Medium horizon label — is never rendered. The heatmap on the dashboard shows label and relative placement but gives users no explanation of why the item is positioned where it is. There is no clickable tooltip or expansion. The full `tail_risks` section is absent from report.html entirely.

---

### 1.7 `sentiment_overlay` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `fed_funds_futures[].meeting` | ✅ | ❌ | ❌ | ❌ |
| `fed_funds_futures[].cut_probability` | ✅ | ❌ | ❌ | ❌ |
| `fed_funds_futures[].our_view` (AGREES/DISAGREES) | ✅ | ❌ | ❌ | ❌ |
| `fed_funds_futures[].note` | ✅ | ❌ | ❌ | ❌ |
| `fed_funds_futures[].weeks_ahead` | ✅ | ❌ | ❌ | ❌ |
| `prob_zero_cuts_2026` | ✅ | ❌ | ❌ | ❌ |
| `matt_agreement_pct` | ✅ | ❌ | ❌ | ❌ |
| `source_url` | ✅ | ❌ | ❌ | ❌ |

**Major gap:** The entire `sentiment_overlay` block — five FOMC meetings with cut probabilities, our AGREES/DISAGREES view vs. market, and the `prob_zero_cuts_2026` (22%) and `matt_agreement_pct` (40%) summary stats — is collected weekly but rendered on **no page**. This is the Fed policy path visualisation that was a centrepiece of the Perplexity-era monitor. Currently the only Fed-related content users see is the `fed_policy_context` indicator in systemic_risk (a static narrative) and a partial reference in the report's Safe Haven section ("market now pricing zero cuts").

---

### 1.8 `safe_haven` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `asset` | ✅ | ❌ | ✅ | ❌ |
| `regime` | ✅ | ❌ | ✅ | ❌ |
| `horizon` | ✅ | ❌ | ✅ | ❌ |
| `rationale` | ✅ | ✅ (below asset table) | ✅ | ❌ |
| `condition_for_reassessment` | ✅ | ❌ | ✅ | ❌ |
| `not_investment_advice` | ✅ | ❌ | ❌ | ❌ |
| `source_url` | ✅ | ❌ | ❌ | ❌ |

**Gap:** The `not_investment_advice` disclaimer is embedded in the JSON but not displayed on any page. The disclaimer is important for compliance/legal context. The `condition_for_reassessment` (the specific regime trigger to rotate out of the safe haven) is surfaced on report.html but not the dashboard's Safe Haven section, where it would be most useful.

---

### 1.9 `cross_monitor_flags` block

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `flags[].title` | ✅ | ❌ | ✅ (section header) | ✅ |
| `flags[].body` | ✅ | ❌ | ✅ | ✅ |
| `flags[].status` (Active/Watch/NoSignal) | ✅ | ❌ | ❌ | ⚠️ |
| `flags[].type` (STRUCTURAL/ACTIVE/EMERGING) | ✅ | ❌ | ❌ | ❌ |
| `flags[].monitor` (source monitor name) | ✅ | ❌ | ❌ | ✅ |
| `flags[].macro_indicators_affected` | ✅ | ❌ | ❌ | ❌ |
| `flags[].first_flagged` date | ✅ | ❌ | ❌ | ❌ |
| `flags[].last_updated` date | ✅ | ❌ | ❌ | ❌ |
| `flags[].source_url` | ✅ | ❌ | ❌ | ❌ |
| `version_history` | ✅ | ❌ | ❌ | ❌ |
| NoSignal flags (cmf_005, cmf_007) | ✅ | ❌ | ❌ | ❌ |

**Gap:** `macro_indicators_affected` — the explicit linkage between a cross-monitor signal and the GMM indicators it affects — is never rendered. This is the primary mechanism for cross-monitor signal propagation and would help users understand why the AI Governance Monitor's cmf_001 is relevant to the Macro Monitor's `ai_infra_debt` indicator. The `type` taxonomy (STRUCTURAL / ACTIVE / EMERGING / NO_SIGNAL) and the `first_flagged` date (staleness indicator) are both invisible.

---

### 1.10 `persistent-state.json` specific fields

| Field | In persistent-state.json | Persistent page |
|---|---|---|
| `asset_class_baseline[].baseline_score` | ✅ | ❌ |
| `asset_class_baseline[].baseline_date` | ✅ | ❌ |
| `asset_class_baseline[].version_history[].change` | ✅ | ❌ |
| `asset_class_baseline[].version_history[].reason` | ✅ | ❌ |
| `oil_supply_shock_driver.resolution_criteria` | ✅ | ❌ |
| `blind_spot_overrides[].rule` name | ✅ | ⚠️ (implied) |
| `blind_spot_overrides[].indicator` | ✅ | ❌ |
| `blind_spot_overrides[].active_since` | ✅ | ❌ |
| `blind_spot_overrides[].warning` | ✅ | ❌ |
| `blind_spot_overrides[].version_history` | ✅ | ❌ |
| `conviction_history[].rationale` | ✅ | ❌ |
| `conviction_history[].conviction` | ✅ | ✅ (badge) |
| `conviction_history[].system_average` | ✅ | ✅ (chart) |

**Gaps:**
- `resolution_criteria` for the oil supply shock driver (the specific condition that would end the WARNING) is collected but not rendered on persistent.html.
- `baseline_score` and `baseline_date` for each asset class (the inaugural-issue anchor) are not shown, making it impossible for users to contextualise how far each asset class has moved from its starting point.
- The `conviction_history[].rationale` (the analyst's written explanation for each regime change) is collected but not shown in the conviction chart tooltip or anywhere on the page.

---

### Summary Gap Table

| Section | Fields Collected | Fields Rendered | Gap % |
|---|---|---|---|
| `meta` | 6 | 4 | 33% |
| `signal` | 10 | 6 | 40% |
| `executive_briefing` | 22 | 5 | 77% |
| `debt_dynamics` / `credit_stress` / `systemic_risk` domain arrays | 7 per indicator | 3 per indicator | 57% |
| `domain_indicators` (all 6 domains) | ~10 per indicator | 0 | **100% gap** |
| `tail_risks` | 6 per item | 4 (heatmap only, no note) | 33% |
| `sentiment_overlay` | 8 | 0 | **100% gap** |
| `safe_haven` | 7 | 4 | 43% |
| `cross_monitor_flags` | 11 per flag | 2–3 per flag | 73% |
| `persistent-state` fields | ~30 | 8 | 73% |

---

## Part 2: Recommended Improvements

### Schema/Data Additions (ranked by investor value)

**1. Credit Spreads Panel — IG, HY, CDX, EMBI (Weekly)**
*Value: Critical | Effort: Low*
The monitor tracks private credit gate events and VIX/CDX divergence narratively but collects no raw spread data. Add a `credit_spreads` object: `ig_oas`, `hy_oas`, `cdx_ig_5yr`, `cdx_hy_5yr`, `embi_spread`, each with current level, prior level, z-score vs. 2yr, and direction. Source: ICE BofA indices (FRED), Markit. This is the single most important missing data stream for a credit-stress monitor — it provides quantitative grounding for every qualitative call in the credit_stress domain.

**2. Hard Landing Risk Score as a KPI (Existing Field, New Prominence)**
*Value: Critical | Effort: Low (data exists, rendering absent)*
`hard_landing_risk.score` (currently 0.38, Increasing) is already collected but invisible. Promote it to a fourth KPI card alongside System Stress, Regime, and System Average Score. A 0–1 probability gauge with a directional arrow is the clearest single-number expression of the monitor's recession call. This requires zero schema change — only a rendering change.

**3. VIX Term Structure and Treasury Liquidity as Named Numeric Indicators**
*Value: High | Effort: Medium*
The cron prompt's canonical indicator mapping lists `vix_term_structure` and `treasury_market_liquidity` as TS (Tactical Signal) indicators in Domain 3, but the current `domain_3_market_structure` array does not include either — they are listed in the cron's canonical mapping as expected indicators but appear to have been dropped in the current JSON. Add them with quantified readings: VIX front-month vs. 3-month ratio (contango/backwardation), MOVE index, bid-ask spreads on 10yr Treasury. These are among the most actionable short-horizon signals in the monitor's remit.

**4. `custody_migration` and `gold_reserve_ratio` Indicators (Cron-Specified, Missing from JSON)**
*Value: High | Effort: Medium*
The cron prompt's canonical Domain 1 mapping includes `custody_migration` (SA) and `gold_reserve_ratio` (SA) as named indicators, but the current `domain_1_debt_sovereign` array contains only three entries (us_debt_deficit, japan_jgb_yields, em_sovereign_distress). These two indicators are directly relevant to the dollar weaponisation theme and the Metals safe haven call — their absence weakens the analytical chain from indicator to asset outlook.

**5. `dollar_funding_fx_basis` and `margin_debt` as Quantified TS Indicators**
*Value: High | Effort: Medium*
Both appear in the cron's canonical Domain 3 mapping as Tactical Signal indicators but are absent from the current JSON domain_3 array. FX swap basis (cross-currency dollar funding cost) is the cleanest real-time signal of dollar stress in global markets. Margin debt level and month-over-month change is a leading indicator of forced selling. Source: Fed H.8, NYSE margin stats.

**6. Tariff Impact Quantification Layer**
*Value: High | Effort: Medium*
The trump_tariff_escalation indicator is currently narrative-only. Add structured sub-fields: `effective_rate_pct` (26.2%), `prior_effective_rate_pct` (2.3%), `gdp_drag_est_low` and `gdp_drag_est_high` (e.g. -0.6% to -2.1% from IMF/BIS ranges), `retaliation_risk_score` (0–1). These would feed directly into the asset class scoring model and give investors a quantified basis for the tariff call.

**7. Regime History Tracking in `signal` block**
*Value: Medium | Effort: Low*
Add `prior_regime` and `regime_change_date` to the signal block. Currently the monitor tracks conviction_history in persistent-state but has no explicit record of when the regime label last changed. When STAGFLATION transitions to DEFLATIONARY BUST, users need to know that this is a new call, not a persistent one. Add `weeks_in_current_regime` as a counter derived from conviction_history.

**8. Scenario-Conditional Asset Class Impacts**
*Value: Medium | Effort: High*
Each `scenario_analysis` entry should include a `asset_impacts` sub-object showing the directional impact on each of the 8 asset classes if that scenario materialises. e.g. Fast Cascade → {bonds: "Bullish +Rally", metals: "Bullish", tech: "Bearish -25%", ...}. This would make the scenario analysis actionable for portfolio construction rather than purely descriptive.

**9. `source_quality_flags` (F1/F2/F3) on Individual Indicators**
*Value: Medium | Effort: Low*
The cron schema defines F1 (counter-narrative), F2 (attribution contested), F3 (single source) flags but they are never applied in the current JSON. Implement them selectively on the highest-conviction calls — e.g. the Brent $126/bbl peak should carry an F3 note, the NBER WP 34836 job-cut projection (502K) should carry F2 until corroborated. These flags are a meaningful epistemic discipline for an intelligence monitor.

---

### Dashboard Rendering Improvements (ranked)

**1. Regime Shift Probability Panel**
*Value: Critical | Effort: Medium*
Add a four-bar horizontal chart or pie/donut showing `regime_shift_probabilities`: Stay Stagflation 60%, Deflationary Bust 25%, Inflationary Boom 10%, Goldilocks 5%. This is the most actionable output of the analytical framework for an investor who needs to hedge or position across regimes. Place it adjacent to the Signal KPI cards. The data is already collected — this is purely a rendering gap.

**2. Sentiment Overlay / Fed Path Table**
*Value: Critical | Effort: Medium*
Render `sentiment_overlay.fed_funds_futures` as a five-row table: Meeting | Cut Probability | Our View | Analyst Note. Highlight DISAGREES rows in amber. Add `prob_zero_cuts_2026` (22%) and `matt_agreement_pct` (40%) as a two-stat callout. This was the most distinctive feature of the Perplexity-era monitor (the AGREES/DISAGREES column against CME FedWatch) and its complete absence from the current dashboard is the sharpest regression from v1 to v2.

**3. Hard Landing Risk KPI Card**
*Value: Critical | Effort: Low*
Promote `executive_briefing.hard_landing_risk.score` (0.38) to a fourth KPI card next to System Stress. Display as a percentage gauge (0–100%) with a direction badge (Increasing). Include the one-sentence note as a tooltip. Zero schema change required.

**4. Real M2 Waterfall / Five-Deflator Bar Chart**
*Value: High | Effort: Medium*
Render `executive_briefing.real_m2` as a horizontal waterfall bar: Nominal M2 (4.88%) → vs CPI (2.48%) → vs PCE (2.08%) → vs Core PCE (1.78%) → vs PPI (1.48%) → vs Core PPI (0.98%). Each bar represents the real purchasing power of M2 growth against a progressively tighter deflator. This is the chart the cron prompt explicitly designs the five-deflator schema for — a waterfall of progressive liquidity erosion. It currently exists only as six numbers in a JSON object.

**5. Tail Risk Note Tooltip**
*Value: High | Effort: Low*
The tail risk heatmap on the dashboard positions six items correctly but shows no explanation on hover. Adding the `note` field as a tooltip (or a click-to-expand panel below the heatmap) would transform the heatmap from a visual decoration into an actionable intelligence layer. Near/Medium horizon labels should also appear (currently embedded in the note text, should be parsed and displayed as a badge).

**6. Scenario Analysis Panel**
*Value: High | Effort: Medium*
Add a three-scenario panel to the dashboard (below or adjacent to the Signal section): Base Case (Slow Burn, 55%) | De-escalation (Policy Pivot, 20%) | Fast Cascade (Credit Contagion, 25%). Each card: scenario name, probability bar, horizon, 2-sentence description. This contextualises the system stress label for investors who need to understand the range of plausible outcomes — not just the current regime label.

**7. Domain Indicator Grid with SA/CC/TS Badges**
*Value: High | Effort: High*
The full `domain_indicators` object should be rendered as an expandable grid on report.html: 6 domain headers, each with ~4 indicators showing flag badge, score bar, indicator_type badge (SA/CC/TS), current reading, and crisis threshold. The TS indicators belong above the fold (weekly positioning); the SA indicators belong in a collapsible detail section (structural context). Currently users see only 3–4 indicators per domain from the legacy arrays, missing Domain 4 and 5 entirely.

**8. `update_this_week` as Expandable Intel Layer on Report**
*Value: High | Effort: Low*
The most intelligence-dense field in the schema — `update_this_week` — is never shown to users. Add a "What changed this week" expandable accordion for each domain indicator on report.html. This would surface the sourced, quantified weekly intelligence that the cron spends 80% of its analytical effort producing. Without it, the report reads as a static snapshot rather than a live intelligence feed.

**9. Cross-Monitor Flag Enhancements**
*Value: Medium | Effort: Low*
On the Cross-Monitor Flags section (report.html already renders flag titles and bodies), add: (a) `macro_indicators_affected` as a chip/tag list showing which GMM indicators each flag touches; (b) `type` badge (STRUCTURAL/ACTIVE/EMERGING); (c) `first_flagged` date to show staleness; (d) filter to hide NoSignal flags by default (currently cmf_005 and cmf_007 NoSignal entries dilute the signal density). The persistent.html Cross-Monitor section should show the `version_history` of flag changes as a changelog log.

**10. Asset Class Delta vs. Baseline (Persistent Page)**
*Value: Medium | Effort: Low*
On persistent.html, add a column to the asset class baseline chart legend showing delta from baseline_score to current_score (e.g. Consumer Staples: -0.83 → -0.908, Δ -0.078). The current chart shows absolute scores over time but does not surface the cumulative drift from the inaugural scoring run. Add `baseline_score` and `baseline_date` as hover labels on the chart's first data point.

---

### Methodology Improvements (ranked)

**1. Replace Narrative Scoring with Explicit Weighted Scoring Model**
*Value: Critical*
The current scoring methodology is described in the cron prompt but not systematically documented in the JSON or rendered for users. Every asset class score is produced by an LLM applying qualitative weights — there is no transparent formula users can audit. The monitor would benefit from a `scoring_weights` block per asset class documenting: which indicators feed the score, their weight, and the current flag contribution. Without this, a -0.908 on Consumer Staples is analytically opaque. Reference: the Perplexity-era monitor used explicit weighted tables that made the scoring reproducible.

**2. Crisis Threshold Visualisation — Distance-to-Threshold Metric**
*Value: High*
Every `domain_indicators` entry has a `crisis_threshold` field. Add a `distance_to_threshold` metric: how far (in standard deviations or percentage points) each indicator is from its crisis level. CMBS office delinquency at 12.34% vs. GFC peak 13% = 5.3% away. This converts the binary ELEVATED/WARNING flag into a continuous proximity metric, which is far more useful for monitoring deteriorating conditions. Display as a fill bar on the indicator grid (0% = at threshold, 100% = benign).

**3. Formal Regime Definition and Transition Rules**
*Value: High*
The regime (STAGFLATION/DEFLATIONARY BUST/INFLATIONARY BOOM/GOLDILOCKS) is set by analyst judgment, but no formal transition rules are documented in the schema. The cron prompt's `regime_shift_probabilities` implies the four regimes are fixed but their entry/exit criteria are not specified. Define formal regime entry/exit conditions (e.g. "STAGFLATION confirmed when: Core PCE > 3% AND GDP growth < 1% for 2 consecutive quarters AND system_average_score < -0.4"). Codifying this would: (a) make the probabilities auditable, (b) prevent inconsistent calls, and (c) allow backtesting against historical episodes.

**4. Blind Spot Override System — Formalise and Expand**
*Value: High*
The current blind spot overrides (Rule 1: Earnings Suppression, Rule 2: Nominal M2 Mirage) are excellent analytical discipline but are defined ad hoc. Formalise a library of named blind spot patterns — e.g. Rule 3: "Labour Market Masking" (AI displacement suppressing claims below structural unemployment), Rule 4: "Dollar Basis Distortion" (FX swap basis distorted by quarter-end window dressing). Each rule should have: activation trigger (quantified), affected indicators, direction of correction, and deactivation condition. The Perplexity-era monitor had similar "contrarian flags" — formalise them into a standing library.

**5. `matt_agreement_pct` Definition and Sourcing**
*Value: Medium*
`sentiment_overlay.matt_agreement_pct` (0.40) is referenced in the schema but its definition is unclear. Based on the cron prompt context, it appears to measure what percentage of the analyst's framework flags are being priced by the market. If this is accurate, it is a powerful mispricing metric — but it needs a clear definition, calculation methodology, and historical range to be useful. Document: (a) which flags feed the numerator, (b) how "market pricing" is measured for each, (c) what 40% vs 80% agreement implies for positioning. Name it something explicit in the schema (e.g. `framework_market_alignment_pct`) and surface it prominently.

**6. Tail Risk Direction Scoring — Quantify the Arrow**
*Value: Medium*
The `tail_risks[].direction` field (Increasing/Stable/Decreasing) is currently set by analyst judgment with no formal rule. Add a formal derivation: if the tail risk's core driver indicators deteriorated week-on-week (using the relevant domain_indicators), direction = Increasing; if stable or mixed, Stable; if relieved, Decreasing. This ties the direction arrow to observable indicator changes rather than free-form analyst discretion, making the heatmap more auditable.

**7. Introduce a "Corroboration Score" for HIGH-conviction Calls**
*Value: Medium*
For any indicator at WARNING with HIGH conviction, require the cron to populate a `corroboration_count` field: the number of independent named sources (T1 or T2) that confirm the reading. e.g., JGB Yields at WARNING: corroborated by BoJ statement, JPMorgan research, FT reporting, Bloomberg data = 4. This operationalises the source-quality hierarchy defined in the cron prompt (named-source 5-tier hierarchy) and gives users a basis for distinguishing well-sourced calls from single-source flags.

**8. Backward Compatibility Test for schema_version Upgrades**
*Value: Medium (operational)*
With schema v2.0, the `domain_indicators` object was added alongside the legacy `debt_dynamics`/`credit_stress`/`systemic_risk` arrays, creating redundant data. Several indicators appear in both (trump_tariffs, oil_supply_shock, consumer_confidence, fed_policy_context appear in both systemic_risk and domain_3_market_structure). This redundancy risks divergence — the legacy array and the domain_indicators entry could show different scores or readings for the same indicator if the cron updates one but not the other. Deprecate the legacy top-level domain arrays once the domain_indicators object is fully rendered, and add a schema migration note.

---

## Priority Summary

Top 5 actions ranked by investor value, with implementation effort:

| Rank | Action | Value | Effort | What to do |
|---|---|---|---|---|
| **1** | ~~Render `sentiment_overlay` (Fed path table with AGREES/DISAGREES)~~ ✅ 2026-04-01 | Critical | Medium | Add 5-row table to dashboard + report Safe Haven section. Data already collected weekly. This was the signature feature of the v1 Perplexity monitor and its absence is the clearest regression. |
| **2** | ~~Render `regime_shift_probabilities` as a four-way probability chart~~ ✅ 2026-04-01 (4-bar chart deferred Sprint 2; data rendered in signal block) | Critical | Medium | Add a 4-bar chart to the Signal section of both dashboard and report. Data already in both `signal` and `executive_briefing` blocks every issue. |
| **3** | ~~Promote `hard_landing_risk.score` to a KPI card~~ ✅ 2026-04-01 | Critical | Low | Add a fourth KPI tile to the dashboard's top strip. Requires only JavaScript change in dashboard.html to read the existing field. Highest-value/lowest-effort change available. |
| **4** | Render `domain_indicators` Domains 4 & 5 on report.html | High | High | Real Economy (ISM PMI, Jobless Claims, Cass Freight, Earnings) and Composite Indices (STLFSI, NFCI, IIF Debt, 0DTE) are invisible despite being collected. Add an expandable indicator grid with SA/CC/TS badges and crisis_threshold context bars. |
| **5** | Render `scenario_analysis` three-scenario panel + `update_this_week` accordion | High | Medium | The scenario analysis (Slow Burn 55%, Policy Pivot 20%, Credit Contagion 25%) and the weekly intelligence updates are the highest-analytical-density content in the schema and are never shown to users. Add scenario cards to dashboard and `update_this_week` expandables to report.html. |

**Bonus quick wins (each < 1 hour of JS/template work):**
- Tail risk `note` tooltip on heatmap hover
- `condition_for_reassessment` on dashboard Safe Haven card
- `macro_indicators_affected` chips on cross-monitor flags
- `not_investment_advice` disclaimer on Safe Haven section
- Real M2 waterfall bar chart (5 deflators already in JSON)

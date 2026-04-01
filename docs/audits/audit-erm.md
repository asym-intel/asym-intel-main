# ERM Domain Audit
*Auditor: Domain expert analyst, Environmental Risks Monitor*
*Date: 1 April 2026 | Schema v2.0 | Issue 1, Vol 1 (W/E 29 March 2026)*

---

## Part 1: Collected But Not Surfaced

Analysis covers three live pages: [Dashboard](https://asym-intel.info/monitors/environmental-risks/dashboard.html), [Report](https://asym-intel.info/monitors/environmental-risks/report.html), [Persistent/Living Knowledge](https://asym-intel.info/monitors/environmental-risks/persistent.html). JSON sources: `report-latest.json` (schema v2.0) and `persistent-state.json` (schema v1.0).

### Full Field Mapping

| Field / Sub-field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| **meta.issue / volume / week_label** | ✓ | ✓ (header) | ✓ (header) | — |
| **meta.published** | ✓ | ✓ | ✓ | — |
| **meta.schema_version** | ✓ | — | ✓ (shown as "Schema v2.0") | — |
| **meta.editor** | ✓ | — | — | — |
| **meta.slug / publish_time_utc** | ✓ | — | — | — |
| **m00.title / body / filter_tag / tier** | ✓ | ✓ (full body rendered) | ✓ (full body rendered) | — |
| **m00.source_url** | ✓ | — | ✓ ("Primary source →") | — |
| **m01[].rank** | ✓ | ✓ (delta strip numbering) | ✓ | — |
| **m01[].headline** | ✓ | ✓ (delta strip) | ✓ | — |
| **m01[].why_it_matters** | ✓ | — | ✓ | — |
| **m01[].module_tag** | ✓ | ✓ (delta strip badge) | ✓ (badge) | — |
| **m01[].tier** | ✓ | — | ✓ (implicit via filter tag) | — |
| **m01[].filter_tag** | ✓ | ✓ (delta strip badge) | ✓ (badge) | — |
| **m01[].cross_monitor** | ✓ | — | ✓ (badge on #1, #4) | — |
| **m01[].source_url** | ✓ | — | ✓ ("Source →") | — |
| **m02.boundaries[].boundary / status / trend / tier / headline** | ✓ | ✓ (full boundary table) | ✓ (full table) | ✓ (per-boundary cards) |
| **m02.boundaries[].summary** | ✓ | — | — | — |
| **m02.boundaries[].filter_tag** | ✓ | — | — | — |
| **m02.boundaries[].last_updated** | ✓ | — | — | ✓ (per card) |
| **m02.boundaries[].source_url** | ✓ | — | — | — |
| **m02.tipping_systems[].system / status** | ✓ | ✓ (flag cards) | ✓ (flag list) | ✓ (flag cards) |
| **m02.tipping_systems[].proxy_metric** | ✓ | ✓ (shown in tipping flag cards) | — | ✓ |
| **m02.tipping_systems[].filter_tag / tier** | ✓ | — | — | — |
| **m02.tipping_systems[].headline** | ✓ | — | — | — |
| **m02.tipping_systems[].summary** | ✓ | — | — | — |
| **m02.tipping_systems[].last_updated** | ✓ | ✓ (per tipping flag card) | — | ✓ |
| **m02.tipping_systems[].source_url** | ✓ | — | — | — |
| **m03[].region / cascade_chain / headline** | ✓ | — | ✓ | ✓ (persistent chain cards) |
| **m03[].f1_trigger** | ✓ | — | — | — |
| **m03[].tier_1_physical** | ✓ | — | — | — |
| **m03[].tier_2_human** | ✓ | — | — | — |
| **m03[].tier_3_political** | ✓ | — | — | — |
| **m03[].filter_tag** | ✓ | — | ✓ (badge) | — |
| **m03[].reverse_cascade_check** | ✓ | — | — | ✓ (shown in cascade chain cards) |
| **m03[].cross_monitor** | ✓ | — | ✓ (badge) | — |
| **m03[].source_url** | ✓ | — | ✓ ("Source →") | — |
| **m03[].last_updated** | ✓ | — | — | — |
| **m04[].event / region / headline** | ✓ | ✓ (delta strip item #4 maps here in context) | ✓ | — |
| **m04[].polycrisis_filter** | ✓ | — | ✓ (shown as body text) | — |
| **m04[].systemic_attribution** | ✓ | — | ✓ | — |
| **m04[].filter_tag / tier** | ✓ | — | ✓ (badge) | — |
| **m04[].source_url** | ✓ | — | ✓ | — |
| **m04[].last_updated** | ✓ | — | — | — |
| **m05.icj_tracker.status / last_development** | ✓ | — | ✓ | ✓ |
| **m05.icj_tracker.unchanged_since / last_updated** | ✓ | — | ✓ | ✓ |
| **m05.icj_tracker.source_url** | ✓ | — | ✓ ("ICJ Case 187 →") | ✓ |
| **m05.loss_damage_tracker.committed / disbursed / gap** | ✓ | ✓ (delta strip item #5) | ✓ | ✓ |
| **m05.loss_damage_tracker.filter_tag** | ✓ | — | — | — |
| **m05.loss_damage_tracker.unchanged_since / last_updated** | ✓ | — | ✓ | ✓ |
| **m05.items[].jurisdiction / headline / summary** | ✓ | — | ✓ | — |
| **m05.items[].filter_tag / tier** | ✓ | — | ✓ (badges) | — |
| **m05.items[].source_url / last_updated** | ✓ | — | ✓ | — |
| **m06[].headline / dual_edge / summary** | ✓ | — | ✓ | — |
| **m06[].filter_tag** | ✓ | — | — | — |
| **m06[].cross_monitor** | ✓ | — | ✓ (badge) | — |
| **m06[].tier** | ✓ | — | ✓ (module card badge) | — |
| **m06[].source_url / last_updated** | ✓ | — | ✓ | — |
| **m07[].headline / index / summary** | ✓ | — | ✓ | — |
| **m07[].filter_tag / tier** | ✓ | — | ✓ (badges) | — |
| **m07[].source_url / last_updated** | ✓ | — | ✓ | — |
| **m08[].resource / actors / headline / summary** | ✓ | — | ✓ | — |
| **m08[].filter_tag / cross_monitor / tier** | ✓ | — | ✓ (badges) | — |
| **m08[].source_url / last_updated** | ✓ | — | ✓ | — |
| **cross_monitor_flags[].target_monitor / linkage** | ✓ | — | ✓ | — |
| **cross_monitor_flags[].gerp_perspective** | ✓ | — | ✓ | — |
| **cross_monitor_flags[].significance / status** | ✓ | — | ✓ (badges) | — |
| **cross_monitor_flags[].version_history** | ✓ | — | — | — |
| **persistent: active_attribution_gap_cases[].attribution_progress** | ✓ (in UI only) | — | — | ✓ (progress bar) |
| **persistent: active_attribution_gap_cases[].type (attribution_gap / governance_void)** | — | — | — | ✓ (badge) |
| **persistent: tipping_systems.collapse_probability_range / ipcc_ar6_baseline** | ✓ | — | — | ✓ |
| **persistent: tipping_systems.slr_equivalent_metres** | ✓ (Thwaites only) | — | — | ✓ |
| **persistent: tipping_systems.threshold_lower/upper_bound_pct** | ✓ (Amazon only) | — | — | — |

### Summary of Significant Gaps

**Collected but not surfaced anywhere:**
- `meta.editor`, `meta.slug`, `meta.publish_time_utc` — operational metadata, low priority
- `m02.boundaries[].summary` — per-boundary analytical summary (e.g. "Current trajectory consistent with 2.7°C by 2100") is collected but **never rendered on any page**. This is substantive analytical content invisible to readers.
- `m02.boundaries[].filter_tag` — never rendered; some are null, but where set (e.g. Freshwater=F1, Novel Entities=F4) this is meaningful
- `m02.boundaries[].source_url` — never exposed to readers
- `m02.tipping_systems[].headline` — distinct from proxy_metric but never shown
- `m02.tipping_systems[].summary` — detailed collapse analysis (e.g. "Self-reinforcing feedback loop not yet confirmed but precursor conditions strengthening") never rendered
- `m02.tipping_systems[].filter_tag / tier` — never shown on any page
- `m03[].f1_trigger` — the specific physical trigger that activates the cascade is collected but not shown on any page
- `m03[].tier_1_physical / tier_2_human / tier_3_political` — the three-layer cascade breakdown is the core analytical methodology; **none of the three tiers are individually rendered anywhere**. Report shows only headline + cascade chain label.
- `m03[].last_updated` — not shown
- `m04[].last_updated` — not shown
- `m05.loss_damage_tracker.filter_tag` — not shown
- `m06[].filter_tag` — not shown (both items have null, but the field exists and is structurally unused)
- `m07[].last_updated` — not shown
- `m08[].last_updated` — not shown
- `cross_monitor_flags[].version_history` — the JSON has an empty array field; never populated or surfaced
- `persistent: tipping_systems.threshold_lower/upper_bound_pct` (Amazon) — the 25–30% dieback threshold data is in the JSON but **not rendered anywhere**, even on the persistent page
- `persistent: tipping_systems.proxy_value` as distinct from `proxy_metric` — partial rendering; the specific quantitative value is sometimes merged, sometimes lost

**Collected but surfaced on only one page (should appear in more places):**
- `m02.boundaries[].last_updated` — only on persistent page, not in report boundary table
- `m00.source_url` — only on report, not on dashboard (The Signal card has no source link)
- `m01[].why_it_matters` — only on report, not on dashboard delta strip (dashboard only shows headline)
- `m03[].reverse_cascade_check` — only on persistent page cascade chain cards; absent from report M03 section where it would have highest analytical value
- `m02.tipping_systems[].proxy_metric` — shown on dashboard tipping flag cards and persistent, but absent from report tipping system list

---

## Part 2: Recommended Improvements

### Schema / Data Additions (ranked)

**1. Planetary boundary numeric proximity score** *(High value · Medium effort)*

Current schema: `status` (Safe/Zone of Uncertainty/Transgressed) + `trend` (Worsening/Stable/Improving). Missing: a normalised 0–100 proximity score expressing how far beyond or before the boundary a system sits, calculated from the control variable against the boundary and the zone-of-uncertainty upper limit. Example: Climate Change CO₂ control variable is ~424 ppm against a boundary of ~350 ppm and a zone-of-uncertainty ceiling near 450 ppm. That gives a proximity score that can be tracked week-over-week and charted as a sparkline. Without this, the 9-boundary status chart on the persistent page is static — you can see "Transgressed" but not whether the system is 5% or 80% beyond the boundary.

Suggested fields to add to each `m02.boundaries[]` entry:
```json
{
  "control_variable": "Atmospheric CO₂ concentration",
  "current_value": 424,
  "unit": "ppm",
  "safe_boundary": 350,
  "zone_upper_limit": 450,
  "proximity_score": 74,
  "proximity_direction": "beyond"
}
```

**2. Tipping system proximity-to-threshold score** *(High value · Medium effort)*

Current schema: qualitative `status` level (Elevated/High/Critical) + proxy metric as a text string. The Amazon Dieback entry partially solves this with `threshold_lower_bound_pct: 25` and `threshold_upper_bound_pct: 30` in persistent-state.json, but this pattern is inconsistently applied — AMOC and Greenland have no equivalent threshold fields. A consistent `proximity_to_threshold` object across all tipping systems would enable:
- A radar/gauge visualisation of all six systems on the dashboard
- Machine-readable escalation triggers for automated alerts

Suggested standard sub-object for all `tipping_systems[]`:
```json
{
  "threshold": {
    "lower_bound": {"value": 25, "unit": "%", "label": "probable point of no return"},
    "upper_bound": {"value": 30, "unit": "%", "label": "confirmed point of no return"},
    "current_value": 19,
    "proximity_pct_to_lower": 76
  }
}
```

For AMOC: threshold defined as FovS anomaly persistence (e.g. 8+ consecutive anomaly weeks = High → Critical escalation trigger). For Greenland: mass loss rate vs. rate at which self-sustaining feedback is modelled to begin.

**3. M04 cumulative YTD extreme weather tracker** *(High value · Low effort to add to schema)*

Current M04 schema: individual event objects with no aggregation layer. An analyst or investor cannot answer "how does extreme weather activity YTD 2026 compare to 2022–2025?" from this data. Add a `m04_ytd_summary` block:
```json
{
  "m04_ytd_summary": {
    "year": 2026,
    "events_logged": 1,
    "events_with_f1_tag": 1,
    "events_with_cascade_pathway": 1,
    "regions_affected": ["Horn of Africa"],
    "cumulative_displaced_estimate": null,
    "baseline_comparison": "insufficient data — tracking from Issue 1"
  }
}
```
As issues accumulate, this becomes a running counter. The insurance and reinsurance audience needs YTD normalised loss data; this is the pathway to that.

**4. M05 regulatory pipeline tracker** *(High value · Medium effort)*

Current schema: `items[]` is a flat list of individual developments, plus two standing trackers (ICJ, Loss & Damage). Missing: a structured regulatory pipeline for anticipated policy developments — bills in legislative process, COP negotiations approaching deadlines, regulatory consultations. Each item should include:
```json
{
  "type": "anticipated",
  "jurisdiction": "United States",
  "instrument": "SEC Climate Disclosure Rule",
  "current_status": "stayed_by_litigation",
  "anticipated_resolution": "2026-Q3",
  "risk_rating": "F2",
  "investor_impact": "..."
}
```
Without this, the monitor is reactive to policy changes after they happen, missing the lead time that is most valuable to investors.

**5. M08 supply chain concentration index per resource** *(Medium-high value · Medium effort)*

Current schema: `actors` as a text string, `summary` as prose. Missing: a structured concentration object — Herfindahl-Hirschman Index equivalent or simple top-3-supplier market share fields. This enables machine-readable supply chain risk scoring:
```json
{
  "concentration": {
    "processing_hhi_estimate": 7200,
    "top_supplier": "China",
    "top_supplier_share_pct": 80,
    "supply_disruption_scenario": "Chinese export control → 12–18 month lead time to alternative supply"
  }
}
```

**6. Reverse cascade severity field in M03** *(Medium value · Low effort)*

`reverse_cascade_check` is currently a prose string. Add a structured field:
```json
{
  "reverse_cascade": {
    "confirmed": true,
    "severity": "High",
    "mechanism": "Armed conflict destroying irrigation infrastructure, preventing adaptation investment",
    "estimated_feedback_lag_weeks": 12
  }
}
```
This enables automated detection of confirmed reverse cascades and cross-monitor escalation triggers.

**7. M06 environmental cost per compute unit** *(Medium value · Medium effort)*

Current schema captures high-level demand projections (IEA data centre doubling). Missing: a per-model or per-deployment estimate of kWh/inference, litres-water/inference, and CO₂e/inference — the inputs that allow direct comparison between AI scaling trajectories and planetary boundary budgets. Without quantified per-unit costs, the AI-climate linkage remains rhetorical rather than analytical.

**8. Cross-monitor flags: escalation trigger fields** *(Medium value · Low effort)*

`cross_monitor_flags[].version_history` array exists in the JSON but is unpopulated (contains an empty outer array). More importantly, the flags have no machine-readable escalation trigger — the condition under which a Structural/Active flag would move to a higher severity. Add:
```json
{
  "escalation_trigger": "If FIMI Monitor confirms state attribution for climate denial campaign → flag moves to CRITICAL",
  "escalation_threshold_met": false
}
```

**9. M03 cascade_stage enumerated status** *(Medium value · Low effort)*

`current_stage` in persistent-state is a text string ("Tier 2–3 (human-to-political transition confirmed)"). This should be an enumerated field to support automated tracking and visualisation of cascade progression:
```json
{
  "cascade_stage": {
    "current": 2,
    "max": 3,
    "confirmed_transition": [1, 2],
    "projected_next_transition_weeks": 8
  }
}
```

**10. Schema version parity** *(Low value · Low effort)*

`report-latest.json` is schema v2.0; `persistent-state.json` is schema v1.0. They describe the same tipping systems and cascade chains but with inconsistent field structures (e.g. tipping system threshold fields exist only in persistent-state, not in report JSON). Unify schema versions and ensure the threshold/proximity fields added above exist in both files.

---

### Dashboard Rendering Improvements (ranked)

**1. M03 cascade chain — not rendered on dashboard at all** *(Critical gap)*

The threat multiplier cascade chain (physical→human→political) is the single most analytically distinctive element of the ERM framework. It is entirely absent from the dashboard. The delta strip item #4 (Sahel) shows the cascade chain label in a badge, but there is no visualisation of the three-tier cascade structure. Investors and policy analysts visiting the dashboard see boundary counts and tipping flags — they do not see the causal pathway from physical stress to geopolitical risk.

Recommendation: Add a "Cascade Chain Heatmap" section below the tipping flags on the dashboard. Three columns (Physical / Human / Political), three rows (one per active cascade chain). Each cell shows the tier status (active/confirmed/projected) and a one-line indicator. This is the key differentiator from a standard climate data feed — it should be prominent on the first page a reader sees.

**2. M02 tipping systems — no proximity-to-threshold visualisation**

The tipping flag cards on the dashboard show status (High/Critical/Elevated) and the prose proxy metric, but there is no gauge or bar chart showing distance-to-threshold. The Amazon entry is especially frustrating: the data exists in persistent-state.json (`threshold_lower_bound_pct: 25`, current: ~19%) but is never visualised. A simple progress bar — "19% deforested of 25–30% threshold" — would communicate urgency more effectively to a non-specialist reader than the status badge alone.

Recommendation: Add a proximity bar to each tipping flag card, rendered from the threshold fields once added to the schema (see Schema #2 above).

**3. M02 planetary boundary chart — status only, no proximity dimension**

The boundary status chart on the persistent page (and the boundary count KPI tile on the dashboard) conveys safe/uncertain/transgressed but not degree of transgression. All seven "Transgressed" boundaries are shown as equal-height red bars. Biogeochemical Flows at 2–3× safe limit and Climate Change at 424 ppm (vs 350 ppm boundary) represent very different risk magnitudes. A normalised proximity score (see Schema #1) would allow the chart to show varying bar heights within the "Transgressed" zone.

**4. M02 boundary summaries — substantive analysis invisible**

Each boundary object in the JSON has a `summary` field containing genuine analytical content (e.g. "Sahel groundwater depletion beyond seasonal variance constitutes the primary freshwater signal this week" for Freshwater; "Aragonite saturation thresholds being crossed in Arctic and Southern Ocean surface waters" for Ocean Acidification). This is never rendered anywhere. On the dashboard boundary table, clicking or expanding a row should reveal this summary. It transforms the table from a status board into an analytical brief.

**5. Dashboard source attribution gap**

The Lead Signal (M00) card on the dashboard has no source link. On the report page, "Primary source →" is shown. The dashboard is the most-visited entry point; analysts need to be able to verify the primary signal immediately without navigating to the report.

**6. Filter tags on executive insight delta strip — partial rendering**

The dashboard delta strip renders module tag and filter tag for each item, but not `why_it_matters` or `cross_monitor`. For the five headline items — the most time-pressed reading experience on the product — omitting "why it matters" is a significant loss of analytical value. Consider a two-line format: headline in normal weight, `why_it_matters` in smaller italic below, matching the report layout.

**7. M03 tier-1/2/3 breakdown absent from report**

On the report page, M03 renders headline, cascade chain label, filter tag, cross_monitor badge, and source link. The three-tier breakdown (tier_1_physical / tier_2_human / tier_3_political) is the analytical core of the module — each tier is a separately sourced assertion that the cascade has reached that level. None of the three tiers appear in the rendered report. A reader cannot assess the evidence basis for the cascade claim. This should be an expandable section or a three-column table within each M03 item.

**8. Reverse cascade indicator absent from report**

`reverse_cascade_check` appears only in the persistent page cascade chain cards. In the report M03 section — where it has the highest analytical value as a confirmed cross-module signal — it is absent. The reverse cascade (geopolitical operation → accelerating physical boundary transgression) is a distinguishing analytical claim that should be flagged visually in the report.

**9. M06 dual_edge field — not indicated in report**

`dual_edge` (Positive/Negative) classifies each AI-climate item but is never shown. The GenCast entry (Positive) and data centre demand entry (Negative) look identical in the rendered report. A simple badge — "positive edge" / "negative edge" — would help readers parse the dual-nature framing of the AI module.

**10. Persistent page: threshold proximity missing from Amazon dieback card**

Amazon Dieback in the persistent tipping systems section shows status (High), proxy metric, and update date, but does not render the `threshold_lower_bound_pct: 25` and `threshold_upper_bound_pct: 30` fields that exist in persistent-state.json. This is the closest thing to a hard numerical threshold in the dataset and is completely invisible.

---

### Methodology Improvements (ranked)

**1. Heat-stress economic productivity loss — missing module or M04 sub-field** *(Most underweighted signal for investors)*

The ERM tracks extreme weather events through a political cascade lens (F1 filter) but does not track heat-stress-induced labour productivity loss as a standalone metric. For investors, this is the highest-dollar-value physical climate risk channel: outdoor labour productivity in South/Southeast Asia and Sub-Saharan Africa is already measurably reduced by Wet Bulb Globe Temperature exceedances. ILO models project 2.4% of global working hours lost by 2030 (equivalent to 80 million full-time jobs). This is not an F1 cascade — it is a direct balance-sheet input. It belongs either as a standing M04 tracker or as a separate `m09_labour_productivity_heat_stress` module.

**2. Financial sector transition risk underweighted vs physical risk** *(Most underweighted for policy analysts)*

M05 Policy & Law currently tracks the ICJ case, Loss & Damage, and EU CSRD. Missing: a structured tracker for stranded asset risk — the mismatch between financial assets priced on a 2°C pathway and physical assets already priced in below that level. The Carbon Tracker / IEA unburnable carbon framework gives an investable number: approximately USD 1–4 trillion in fossil fuel assets that become uneconomic under <2°C scenarios. Policy analysts need this number to understand the political economy of climate inaction (who benefits from delay). This should be a standing tracker in M05, updated quarterly.

**3. AMOC weakening → regional cascade chains not operationalised**

The ERM correctly identifies AMOC weakening as the lead signal (M00) and a tipping system (M02) but does not connect it forward to specific M03 cascade chains. AMOC weakening has documented impacts on: (a) West African monsoon timing (Sahel cascade accelerant), (b) European winter temperature extremes, (c) North Atlantic hurricane intensification. These are modelled physical pathways, not speculative. The cross-reference from M02 tipping_systems[AMOC] → relevant M03/M04 entries does not exist in the schema as a structured link. Adding `downstream_cascade_refs: ["m03/Sahel", "m04/Atlantic_hurricane_season"]` to tipping system objects would make the causal chain machine-readable and visually traceable.

**4. Water-energy-food nexus modelling absent at country level**

The cascade chains in M03 are region-level (Sahel, South Asia, Arctic). Missing: country-level WEF nexus stress scores that would allow investors and policy analysts to rank national exposure. Countries like Egypt, Pakistan, Jordan, and Ethiopia are simultaneously exposed on all three nexus dimensions in ways that are not captured by the regional framing. A `m03_country_exposure_index` with WEF nexus scores (using FAO AQUASTAT + FEWS NET + IRENA renewable energy share as inputs) would be the most investable output the monitor could produce.

**5. Geospatial precision — M03 and M04 use regional framing, not coordinate-level**

All cascade chains and extreme weather events are described at the regional level (e.g. "Horn of Africa", "Sahel"). For investors with physical asset exposure (infrastructure, agriculture, real estate), the relevant unit is sub-national or project-level. The methodology should include a field for bounding box or polygon reference — either a GeoJSON reference or a link to a geospatial data layer (e.g. ACLED, FEWS NET IPC shapefiles) — to allow direct integration with asset-level risk mapping tools.

**6. Sovereign credit implications — underweighted for investors**

Environmental stress is increasingly a sovereign credit rating input (Moody's, S&P, and Fitch now incorporate physical climate risk into sovereign assessments). The ERM's cascade chains directly generate sovereign credit risk signals — Sahel water stress → food insecurity → political instability → governance deterioration → credit downgrade pathway. A `sovereign_credit_exposure` sub-field in M03 cascade chains (listing countries with IMF Article IV consultations referencing climate stress, or credit rating outlook changes attributable to physical risk) would directly address the investor use case.

**7. Tipping system interaction effects — not modelled**

The six tipping systems are tracked independently. Climate science literature (Lenton et al. 2019, Armstrong McKay et al. 2022) documents nonlinear interaction effects: AMOC weakening + Amazon dieback together have a larger forcing effect than the sum of their individual contributions. The methodology currently has no mechanism to flag when two co-occurring tipping signals constitute a compound risk greater than their individual parts. A `tipping_system_interactions` block in M02 — with documented interaction pairs and amplification factors — would be a meaningful methodological advance.

**8. M07 biosphere — no biodiversity financial risk metric**

M07 tracks ocean heat content, coral bleaching, and deep-sea mining governance. Missing: a financial risk framing of biodiversity loss. The TNFD (Taskforce on Nature-related Financial Disclosures) framework, now in force for early adopters, provides the methodology. Nature-related financial risk for investors includes supply chain exposure to ecosystem services (pollination, freshwater, soil fertility). The ERM should track TNFD adoption rates and the disclosure-to-action gap, analogous to what M05 does for CSRD.

**9. Attribution science lag — signal not updated when attribution studies publish**

Extreme weather events in M04 often lack definitive attribution at time of entry. The World Weather Attribution program typically publishes rapid attribution studies within 2–4 weeks of major events. The schema has no mechanism to mark an event as "attribution pending" and then update it when the study publishes. Adding `attribution_status: "pending" | "confirmed_anthropogenic" | "confirmed_natural" | "mixed"` and `attribution_study_url` to M04 items would allow the monitor to carry forward incomplete entries and resolve them — creating a more accurate long-term record.

**10. Reverse cascade methodology formalisation**

Reverse cascades (geopolitical operations → physical boundary transgression) are identified ad hoc in `reverse_cascade_check` fields and cross-monitor flags. The methodology lacks a formal definition of what constitutes a confirmed vs. assessed vs. hypothetical reverse cascade, and what evidence threshold is required for each. This creates inconsistency: the Arctic Russian resource extraction reverse cascade is "confirmed," the India-Pakistan nuclear posture reverse cascade is "assessed moderate." The distinction is analytically important but the criteria are not documented. A formal reverse cascade assessment rubric — analogous to the FIMI Monitor's attribution confidence levels — would strengthen the methodology's credibility with policy analysts.

---

## Priority Summary

Top 5 actions ranked by value delivered per unit of effort:

| Rank | Action | Description | Value | Effort |
|---|---|---|---|---|
| 1 | **Add M03 cascade tier breakdown to report rendering** | Render tier_1_physical / tier_2_human / tier_3_political as a three-column structured section within each M03 item on the report page. Data already exists in JSON. This is the single most underutilised analytical asset in the product. | Critical | Low |
| 2 | **Add tipping system proximity-to-threshold schema fields + dashboard gauge** | Standardise threshold fields across all six tipping systems (extending the Amazon pattern to AMOC, Greenland, etc.), then render as a progress bar on tipping flag cards. Makes the "how close are we?" question answerable at a glance. | High | Medium |
| 3 | **Cascade chain heatmap on dashboard** | Add a physical→human→political three-column grid to the dashboard showing all active cascade chains and their confirmed tier. Requires no new data — only rendering of existing M03 schema. The cascade chain is the ERM's methodological signature; it is invisible on the most-visited page. | High | Low |
| 4 | **M04 cumulative YTD tracker + M05 regulatory pipeline tracker** | Two schema additions that shift the monitor from reactive (what happened) to predictive (what is building). YTD extreme weather counter addresses insurance/reinsurance audience; regulatory pipeline addresses legal and compliance audience. These are the two highest-value forward-looking gaps. | High | Medium |
| 5 | **Planetary boundary proximity score (numeric) + persistent page chart upgrade** | Add normalised proximity scores (control variable vs. boundary vs. zone limit) to boundaries schema, upgrade the persistent page bar chart to show variable heights within the Transgressed zone. Transforms the 9-boundary status board from a binary flag into a risk quantification surface. | High | Medium |

---

*Audit conducted against: [ERM Dashboard](https://asym-intel.info/monitors/environmental-risks/dashboard.html) · [ERM Report](https://asym-intel.info/monitors/environmental-risks/report.html) · [ERM Living Knowledge](https://asym-intel.info/monitors/environmental-risks/persistent.html) · JSON sources: `report-latest.json` (schema v2.0), `persistent-state.json` (schema v1.0)*

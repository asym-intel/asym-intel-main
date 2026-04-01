# ESA Domain Audit
**Auditor:** Domain expert analyst, European Strategic Autonomy Monitor  
**Date:** 1 April 2026 — Issue 2  
**Monitor URL:** https://asym-intel.info/monitors/european-strategic-autonomy/  
**JSON schema version audited:** report-latest.json (as described; direct URL returned 404 — audit uses schema as documented and cross-referenced against rendered HTML output)

---

## Part 1: Collected But Not Surfaced

The table below maps each top-level JSON field against its presence and rendering fidelity across the three live pages. "Rendered" means the data is surfaced to a user in a readable, interactive, or visual form. "Partial" means the data appears but is incomplete, unlabelled, or buried.

| Field | In JSON | Rendered on Dashboard | Rendered on Report | Rendered on Persistent |
|---|---|---|---|---|
| `meta` (issue number, date, schema version) | Yes | Partial — issue/date shown in header; schema version not exposed | Yes — issue/date in header | Partial — "Schema v2.0" visible in subtitle; issue number present |
| `signal.title` | Yes | Yes — shown as lead signal headline in KPI strip | Yes — full lead signal card | Not present |
| `signal.body` | Yes | Yes — full body text rendered below fold | Yes — full text in lead signal card | Not present |
| `signal.source_url` | Yes | Yes — "Source →" link | Yes — "Source →" link | Not present |
| `defence_developments[].headline` | Yes | Yes — in Top Items strip, labelled "Defence" | Yes — section heading per item | Not present (only referenced in Timeline by date tag) |
| `defence_developments[].summary` | Yes | Yes — truncated inline in Top Items | Yes — full summary | Not present |
| `defence_developments[].source_url` | Yes | Not visible on dashboard (no source link in Top Items strip) | Yes — "Source →" per item | Not present |
| `hybrid_threats[].headline` | Yes | Yes — in Top Items strip, labelled "Hybrid" | Yes | Not present (Timeline entries reference events by date, not full items) |
| `hybrid_threats[].summary` | Yes | Yes — truncated inline | Yes — full summary | Not present |
| `hybrid_threats[].source_url` | Yes | Not visible on dashboard | Yes — "Source →" per item | Not present |
| `institutional_developments[].headline` | Yes | Not surfaced — institutional items do NOT appear in Top Items strip on dashboard | Yes — dedicated section | Not present |
| `institutional_developments[].summary` | Yes | Not surfaced | Yes — full summary | Not present |
| `institutional_developments[].source_url` | Yes | Not surfaced | Yes — "Source →" per item | Not present |
| `member_state_tracker[].country` | Yes | Yes — flag + ISO code + name | Yes — flag + ISO code in section | Yes — in Active Elections and State Capture sections |
| `member_state_tracker[].headline` | Yes | Yes — rendered as "change_from_last_week" sub-label | Yes — rendered as primary headline per entry | Partial — country name/status in State Capture, not full headline |
| `member_state_tracker[].status` | Yes | Yes — coloured badge (CRITICAL/HIGH/ELEVATED/STABLE) | Yes — coloured badge | Yes — severity field in Active Elections |
| `member_state_tracker[].change_from_last_week` | Yes | Yes — shown as secondary text under country name | Yes — appears below headline | Not present |
| `member_state_tracker[].source_url` | Yes | Yes — "Source →" per entry | Yes — "Source →" per entry | Partial — source links in Actor Campaigns; not in Member State entries |
| `cross_monitor_flags` | Yes | Not rendered — section absent from dashboard | Yes — section heading "Cross-Monitor" visible but shows "No cross-monitor flags" | Yes — dedicated section, currently empty |

### Key gaps identified:

1. **`institutional_developments[]` is completely absent from the dashboard.** The dashboard Top Items strip surfaces only Defence and Hybrid items. Institutional items (EU-China trade data, Slovenia government formation, Hungary election, €90B Ukraine loan) are invisible to dashboard-only users. This is the largest surfacing gap — 4 of 10 total report items are missing from the primary user touchpoint.

2. **Source URLs are stripped from dashboard Top Items.** Defence and Hybrid items appear in the Top Items strip without "Source →" links. This matters for an analyst audience that needs to verify primary sources from the quickest view.

3. **The Lead Signal does not appear on the Persistent page.** The lead signal (the most editorially important item each week) is not carried forward into the living knowledge base. A user reviewing the persistent state has no record of what the week's defining signal was.

4. **`cross_monitor_flags` is structurally present but never populated.** The field exists in the JSON schema and is rendered in both report and persistent views, but has contained no data in either of the two issues published. This is either a collection gap or a dead schema field.

5. **The Lagrange Point radar on the dashboard shows 5 dimensions (Energy, Defence, Technology, Finance, Materials)** — missing "Institutions" as a sixth spoke, even though the persistent scorecard lists all six and the about page explicitly names six: energy, defence, technology, finance, materials, and institutions. The radar has a rendering defect.

6. **KPI tile "NATO 2% Target: 32/32"** appears on the dashboard (visible in the JavaScript-rendered index page content) but is not present in the JSON schema's described top-level keys. It is unclear whether this is hardcoded in the template or computed from a field not listed in the schema documentation.

7. **Defence spending fields on the dashboard** (`EU Defence Total 2025: €392B`, `Defence Spending Change: +20%`, `SAFE Programme Total: €150B`) are rendered as KPI tiles — but these values live in the persistent JSON's `kpi_state` block, not in the weekly `report-latest.json`. There is no per-member-state breakdown visible anywhere in the rendered output, despite country-level data being implied by the member state tracker.

---

## Part 2: Recommended Improvements

### Schema/Data Additions (ranked)

**1. Per-member-state defence spending tracker (% GDP actual vs. 2% target vs. 5% Hague target)**  
Priority: Critical. The monitor tracks defence autonomy but has no structured numeric data on the single most important quantitative indicator. NATO's 2025 annual report confirms all 32 allies now exceed 2% GDP, and the Hague Summit (June 2025) set a new 5% target. This data is publicly available from NATO, IISS, and SIPRI on a regular update cycle. The schema should add a `defence_spending[]` array with fields: `country` (ISO), `gdp_pct_actual`, `gdp_pct_target` (2% or national pledge), `hague_target_pct` (5%), `absolute_eur_bn`, `yoy_change_pct`, `safe_allocation_eur_bn`, `source_url`. This directly serves both the strategic policy analyst and the European defence investor use cases. Sources: [NATO Defence Expenditure 2025 PDF](https://www.nato.int/content/dam/nato/webready/documents/finance/def-exp-2025-en.pdf), [Atlantic Council NATO Tracker](https://www.atlanticcouncil.org/commentary/trackers-and-data-visualizations/nato-defense-spending-tracker/).

**2. Per-pillar autonomy scores with structured numeric fields and direction-of-travel delta**  
Priority: High. The Autonomy Scorecard currently exists only in the persistent JSON as prose labels and raw integers (Energy: 52, Defence: 30, Tech: 18, Finance: 22, Materials: 25, Institutions: 35). There are no structured fields for: (a) the scoring methodology/rationale, (b) week-on-week delta, (c) confidence interval or data vintage, (d) sub-indicators that compose each pillar score. The schema should add a `scorecard[]` array with: `pillar`, `score` (0–100), `delta_from_last_issue`, `direction` (up/down/flat), `key_driver_this_week` (text), `data_sources[]`, `methodology_note`. The current ~35% composite "Lagrange Point" score is likewise unanchored — it needs a defined aggregation formula (weighted average of pillar scores) and a changelog. The Compossible series ([A Reckoning: European Strategy for an Unstable World](https://compossible.asym-intel.info/2026/03/10/a-reckoning-european-strategy-for-an-unstable-world/)) defines the six autonomy dimensions qualitatively but provides no quantitative baseline; the schema should close that gap.

**3. US-dependency index per domain**  
Priority: High. The monitor's analytical purpose explicitly includes the US-Europe relationship, but there is no structured field capturing US dependency. The persistent scorecard alludes to this ("US LNG at 60%", "US cloud 70%+") only in prose descriptions. Add a `us_dependency[]` array: `domain` (energy/tech/defence/finance/trade), `dependency_score` (0–100), `primary_dependency_mechanism` (LNG supply, cloud infrastructure, Article 5 guarantee, USD reserve share, tariff exposure), `recent_development`, `source_url`. This is the most investor-relevant signal in the current geopolitical environment and is entirely absent from the JSON schema.

**4. EDIP/ReArm Europe programme tracker as a structured field**  
Priority: High. The €800B ReArm Europe package ([DW](https://www.dw.com/en/eus-von-der-leyen-proposes-800-billion-defense-plan/a-71819582)) and EDIP's €1.5B work programme ([EC](https://defence-industry-space.ec.europa.eu/edip-commission-adopts-eu15-billion-work-programme-boost-european-and-ukrainian-defence-industry-2026-03-30_en)) are central to European defence autonomy but are currently captured only as one-off items in `defence_developments[]` — no persistent structural tracking. Add a `defence_programmes[]` array: `programme_name`, `total_envelope_eur_bn`, `disbursed_to_date_eur_bn`, `pending_disbursements[]` (country/amount/status), `next_milestone`, `blocking_actors`, `source_url`. SAFE is partially tracked in KPI tiles but not as a programmable field with disbursement progress.

**5. Aggregate autonomy index with historical time series (issue-by-issue)**  
Priority: Medium. At issue 2, there is no baseline delta — "~35%" is a point-in-time assertion with no trajectory. The schema should store a `composite_index_history[]` array (populated from issue 1 onward) enabling trend visualisation. Even a two-point time series would enable directional language ("improving", "deteriorating") with data backing.

**6. US-EU bilateral tension tracker as a persistent structured section**  
Priority: Medium. US influence campaigns (Alliance of Sovereign Nations, Section 301 investigations, Anti-GDPR campaign) are tracked in the persistent Actor Campaigns section — but EU-US institutional dynamics (tariff negotiations, NATO burden-sharing disputes, intelligence sharing status, GDPR/DSA enforcement pressure) are not captured as a structured bilateral state. Add a `us_eu_bilateral_state{}` object: `trade_dispute_status`, `tariff_threat_level`, `nato_commitment_status`, `intelligence_sharing_status`, `data_protection_tension_level`, `last_significant_event`, `source_url`. This is a first-class concern for the monitor's stated scope.

**7. EDTIB (European Defence Technological and Industrial Base) capacity tracker**  
Priority: Medium. Investment in European defence autonomy means little without tracking industrial capacity. Add `edtib_capacity{}`: `ammunition_production_kt_per_year`, `artillery_rounds_annual_target`, `drone_production_units`, `key_chokepoints[]`, `ukraine_integration_status`. EDIP's first calls (closing June 2026) provide a natural anchor point. Sources: [EDIP programme page](https://defence-industry-space.ec.europa.eu/eu-defence-industry/edip-forging-europes-defence_en).

**8. Cross-monitor flags: populate or retire**  
Priority: Low-Medium. The `cross_monitor_flags` field has been empty for two consecutive issues. Either define the trigger criteria clearly (e.g., "any item that is also tracked by the Russia Strategic Monitor or the China Strategic Monitor") and enforce population, or remove the section to avoid dead scaffolding that erodes reader trust.

---

### Dashboard Rendering Improvements (ranked)

**1. Surface institutional_developments[] in the Top Items strip**  
Priority: Critical / Effort: Low. The dashboard currently filters Top Items to only Defence and Hybrid categories. Institutional items (EU legislation, election outcomes, trade data) must appear in the strip. Either extend the strip or add a third module. Four of ten items this issue are invisible on the dashboard — a 40% surfacing failure rate for the primary user touchpoint.

**2. Add source links to Top Items entries**  
Priority: High / Effort: Low. Every Top Item already has a `source_url` in the JSON. The dashboard template drops this link. A one-line template change surfaces primary sources for all items without adding layout complexity. Analysts need verifiability from the fastest view.

**3. Fix the Lagrange Point radar: add the Institutions spoke**  
Priority: High / Effort: Low. The radar chart renders only 5 dimensions despite 6 being defined in the schema (Energy: 52, Defence: 30, Tech: 18, Finance: 22, Materials: 25, Institutions: 35). The Institutions spoke is missing. This is a direct contradiction between the persistent scorecard and the dashboard visualisation.

**4. Add week-on-week delta arrows to pillar scores**  
Priority: High / Effort: Medium. The scorecard currently shows static integers. For a weekly publication, the directional signal — is Europe's tech autonomy improving or deteriorating since last week? — is more informative than the absolute score. Delta arrows (▲/▼/–) with tooltip explanations would make the scorecard analytically actionable rather than decorative.

**5. Replace "~35%" composite score gauge with a labelled breakdown**  
Priority: Medium / Effort: Medium. The current 35% gauge is displayed as a dial with no contextual breakdown. A short horizontal bar chart showing each pillar score side-by-side (the data already exists in persistent JSON) would allow a user to immediately see where Europe is weakest (Tech: 18, Finance: 22) and strongest (Energy: 52). This transforms a single opaque number into genuine insight.

**6. Add an institutional developments section to the dashboard**  
Priority: Medium / Effort: Low-Medium. Even a minimal card strip (analogous to the existing Defence/Hybrid strip) for Institutional items would close the surfacing gap. The module exists in the report; it needs a corresponding dashboard tile.

**7. Surface US-EU bilateral tension as a named dashboard indicator**  
Priority: Medium / Effort: Medium. The current KPI tiles cover defence spending and threat landscape. There is no tile for transatlantic relationship status. Given the monitor's stated focus on the US-Europe relationship, add a "Transatlantic Tension Level" KPI tile (using a Low/Moderate/High/Critical rating) — pulling from the proposed `us_eu_bilateral_state{}` schema field once added.

**8. Make the Member State Tracker sortable and filterable by status**  
Priority: Low-Medium / Effort: Medium. Currently only 4 member states appear (HU, SI, CZ, FR). As the tracker grows, users need to filter by status (CRITICAL, HIGH, ELEVATED, STABLE, POSITIVE) or sort by severity. A simple JS filter control on the existing HTML table would suffice.

**9. Add issue navigation / archive access from the dashboard**  
Priority: Low / Effort: Low. The dashboard shows only the latest issue. There is an "ARCHIVE" nav item but no quick-access panel on the dashboard itself showing recent issues with date and lead signal title. A "Previous Issues" widget (last 3-4) would increase engagement and allow trend comparison.

---

### Methodology Improvements (ranked)

**1. Build a structured scoring methodology document for the Autonomy Scorecard**  
Priority: Critical. The six pillar scores (Energy: 52, Defence: 30, etc.) are currently unanchored — there is no published methodology explaining the scoring scale, data sources, aggregation logic, or update trigger. The monitor cites ECFR, IISS, and Chatham House methodologies in the About page, but no traceability to those frameworks is visible in the output. For a policy analyst or investor audience, scores without methodology documentation are analytically unusable. Required: a scoring rubric page defining (a) what 0/50/100 means per pillar, (b) the weighting formula for the 35% composite, (c) the cadence and trigger for score updates. This is the single largest credibility gap in the monitor.

**2. Integrate ReArm Europe/€800B package as a dedicated analytical thread**  
Priority: Critical. The ReArm Europe plan ([Statista chart](https://www.statista.com/chart/34051/eu-plan-to-boost-defense-spending/), [DW](https://www.dw.com/en/eus-von-der-leyen-proposes-800-billion-defense-plan/a-71819582)) is the defining structural development in European defence autonomy since 2022. Its five pillars (fiscal space/SGP exemption ~€650B, SAFE loans €150B, EU budget reallocation, EIB private capital mobilisation, mini-Omnibus dual-use flexibility) are tracked only partially and inconsistently: SAFE disbursements appear in KPI tiles, but the overall envelope, disbursement progress, and the fiscal space pillar (the largest component) are not tracked at all. Each issue should include a persistent "ReArm Europe Tracker" section showing cumulative disbursed vs. committed vs. total envelope per pillar.

**3. Integrate EDIP as a dedicated industrial capacity tracking thread**  
Priority: High. EDIP's €1.5B work programme was formally adopted 8 December 2025 and first calls opened 31 March 2026 ([EC EDIP page](https://defence-industry-space.ec.europa.eu/eu-defence-industry/edip-forging-europes-defence_en)). This is the primary mechanism for building EU defence industrial capacity independent of US suppliers. Current coverage: zero structured tracking. Recommended addition: a persistent `edip_tracker{}` covering open calls, submitted proposals, awarded grants (by country and capability area), and a running "EDTIB capacity delta" vs. a stated baseline (e.g., NATO target of 155mm shell production rate).

**4. Formalise US-EU dependency as an analytical pillar, not a side note**  
Priority: High. The monitor's stated scope includes "particular focus on the US-Europe relationship and NATO dynamics," yet US dependency is surfaced only as scattered prose in pillar descriptions (US LNG 60%, US cloud 70%+) and in Actor Campaigns (Alliance of Sovereign Nations, Section 301). A structured US-EU section should cover: (a) trade exposure (current tariff threat level, bilateral trade volumes, Section 301 investigation status), (b) military dependence (Article 5 credibility assessment, US equipment share in European force structures, intelligence sharing status post-DOGE USAID cuts), (c) tech dependency (CLOUD Act exposure, AWS/Azure/Google market share in EU critical infrastructure, GDPR enforcement dynamics), (d) financial dependency (USD reserve share, SWIFT alternatives progress). Sources for this already flow into the monitor — they need to be systematically routed to a persistent bilateral section rather than scattered across module items.

**5. Expand NATO burden-sharing coverage to per-country GDP tracking**  
Priority: High. NATO's 2025 annual report (March 26, cited in the Timeline) shows European allies +20% spending, and all 32 allies now exceed 2% GDP — a historic first. The new 5% Hague target creates a new gap to track. The monitor currently renders this as a single "+20%" KPI tile. For a policy/investor audience, the value is in the country-by-country picture: which states are accelerating (Poland at 4%+, Estonia at 3.4%), which are lagging (Italy, Spain, Belgium still near floor), and which have made credible pledges vs. political statements. Sources: [NATO defence expenditure PDF](https://www.nato.int/content/dam/nato/webready/documents/finance/def-exp-2025-en.pdf), [World Population Review NATO spending](https://worldpopulationreview.com/country-rankings/nato-spending-by-country).

**6. Add an EU-China dependency thread to the Institutional Developments coverage**  
Priority: Medium. The monitor currently covers EU-China trade in `institutional_developments[]` (Eurostat 2025 data: China imports €559.4B, +6.4% YoY, goods deficit ~€355-360B). But the strategic autonomy dimension of China dependency — critical minerals (97% Mg from China, RE suspension tracked on persistent page), tech supply chains, Huawei/ZTE phase-out, Chinese FDI concentration in Cyprus — is dispersed across KPI tiles and scorecard prose with no integrated analytical thread. The Critical Materials pillar score (25/100) is the lowest-confidence score in the scorecard because the underlying indicators are not tracked systematically week-by-week.

**7. Incorporate the Institutional Resilience pillar more rigorously**  
Priority: Medium. The Institutional Resilience score (35/100) is noted as "QMV blocked" — a single data point that barely justifies a pillar score. This pillar should track: QMV reform status, rule-of-law proceedings (Article 7 cases), democratic backsliding index (V-Dem, already partially tracked), EU budget negotiations and conditionality enforcement, and EP coalition dynamics. The State Capture section in persistent already has much of this data; it needs to be connected to the pillar score.

**8. Establish a baseline issue (Issue 1 retroactive scoring) for trend analysis**  
Priority: Medium. Issue 1 (30 March 2026) presumably set initial scores, but without a published delta the Issue 2 scores are absolute assertions, not trend readings. Even if scores did not change from Issue 1 to Issue 2, explicitly marking them "unchanged from baseline" signals methodology rigour. From Issue 3 onward, every pillar score change should be accompanied by a named driver event.

**9. Align the Russia hybrid threat coverage to autonomy impact, not just threat tracking**  
Priority: Low-Medium. The Hybrid Threats section currently functions like a Russia/Ukraine war tracker (gasoline export halt, ISW battlefield reporting, ceasefire proposals). While analytically useful, the autonomy relevance — how does each hybrid threat development affect European strategic autonomy specifically? — is not made explicit. Each `hybrid_threats[]` item should include an optional `autonomy_impact` field: which pillar does this affect, and in which direction? This would enable the hybrid section to drive scorecard updates rather than running in parallel without connection.

---

## Priority Summary

| Rank | Action | Value | Effort | Category |
|---|---|---|---|---|
| 1 | **Publish Autonomy Scorecard methodology document** — define scoring rubric (0–100 per pillar), weighting formula for composite, update trigger criteria | Foundational credibility for policy/investor audience; all other scores are analytically unusable without it | Low | Methodology |
| 2 | **Surface `institutional_developments[]` on the dashboard** — extend Top Items strip to include the Institutional category; currently 4 of 10 items per issue are invisible to dashboard users | Immediate fix to a 40% item surfacing failure; single template change | Low | Dashboard Rendering |
| 3 | **Add per-member-state defence spending tracker to schema** — `defence_spending[]` array with GDP%, absolute spend, SAFE allocation, vs. 2% and 5% targets | The single most investor-relevant quantitative output; data already publicly available from NATO | Medium | Schema/Data |
| 4 | **Add US-dependency index per domain to schema** — structured `us_dependency[]` with domain, score, mechanism, recent development | Directly addresses the monitor's stated analytical scope on US-Europe dynamics; completely absent from current schema | Medium | Schema/Data + Methodology |
| 5 | **Fix Lagrange Point radar: add Institutions spoke + add delta arrows to pillar scores** — both the missing sixth dimension and the week-on-week directional signal | Two-part rendering fix that corrects a visible defect and adds the monitor's most actionable weekly insight; Institutions (35) is missing from the primary visualisation | Low | Dashboard Rendering |

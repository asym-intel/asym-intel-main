# asym-intel.info — Visual Audit
# Date: 1 April 2026
# Scope: All charts, tables, graphs, and structured data displays across the site
# Excludes: The White Space knowledge graph (whitespace.asym-intel.info)

---

## Context

This audit was produced by reviewing all 8 dashboard pages, 4 report pages, and 2 persistent-state pages live. It cross-references the asym-intel-charts skill (which lists Sprint 2 pending charts) and is intended to inform sprint prioritisation.

---

## Cross-Site Structural Issues

1. **"Heatmap" label mismatch** — used on WDM, ERM, and SCEM but in each case renders as a plain text table with no colour gradient or matrix encoding. Either implement proper colour encoding or rename the sections.

2. **Report pages hold far richer data than dashboards visualise** — almost every module (risk indicators, cross-monitor flags, concentration indices, scenario probabilities, investment flows) exists as text cards only. Dashboards cherry-pick a few items to chart and leave the rest invisible.

3. **Dark mode inconsistency** — AGM dashboard is dark-mode only; all other 6 dashboards are light mode.

---

## Per-Monitor Findings

---

### Global Macro Monitor (GMM)

**Existing visualisations:**
- Asset Class Scores — horizontal bar chart (current vs prior score, 8 asset classes)
- Real M2 Deflator Waterfall — horizontal bars, nominal → real through 5 deflators ✅ best-executed on this page
- Tail Risk Heatmap — 3×3 matrix (Likelihood × Impact)
- Macro Scenarios — 3 probability cards (text only)
- Fed Funds Path — table (5 FOMC dates × market-implied cut probability)
- Score History — multi-series line chart (persistent page)
- System Average Score History — line chart (persistent page)
- Regime Timeline — dated node log (persistent page)

**Issues:**
- Prior-week bars in Asset Class chart are uniform grey — hard to distinguish from background. Should be 40% opacity version of the current bar colour.
- Score History and System Average charts have only 2 data points (straight lines). Will improve naturally. Add a regime band overlay (e.g. light red fill below -0.5 = "bearish territory") so early issues look meaningful.
- Tail Risk Heatmap MED and LOW rows are entirely empty. If genuinely no medium/low risks exist this week, say so explicitly ("All tail risks rated HIGH impact — reflects current stress regime"). Empty cells look like a bug.
- Macro Scenarios probabilities are text only (55% / 25% / 20%). A simple inline probability bar would make relative confidence instantly scannable — ~20 lines of CSS.
- Fed Funds Path table would be more legible as a bar chart (x = FOMC meeting date, y = probability of cut).
- Regime Conviction History on persistent page has no visual showing when the regime label changed. A colour-coded timeline strip (RISK-ON / STAGFLATION / CONTRACTION) per week would be the most compelling chart on the site over time.

**Not yet visualised (data exists):**
- Regime shift probabilities (`signal.regime_shift_probabilities`) → 4-bar horizontal *(listed in chart skill Sprint 2)*
- Horizon Matrix (`horizon_matrix`) → structured table *(Sprint 2 schema)*
- Factor Attribution (`factor_attribution`) → per-asset breakdown *(Sprint 2 schema)*
- Cross-Monitor Flags (7 flags) → text cards only, no status matrix

---

### World Democracy Monitor (WDM)

**Existing visualisations:**
- Global Democratic Health — stacked bar (3 categories: 15 Rapid Decay / 9 Watchlist / 5 Recovery)
- KPI summary cards (3×)
- Most Severe ranking cards (top 5 countries by score)
- Country Heatmap — filterable table with severity scores and trend arrows (report page)
- Mimicry Chains — sequential arrow-separated text flow (report + persistent pages)

**Issues:**
- **Geographic View map does not render** — the section is blank. This is the most critical bug on the site. WDM monitors 29 countries with severity scores for all of them.
- Global Democratic Health bar is too minimal — only 3 colour segments with count totals. Consider adding a country flag strip below showing which countries sit in each band.
- Country severity scores (e.g. Iran 10.0, US 5.5, Hungary 7.5) are not visualised. A ranked horizontal bar chart of all 29 countries coloured by category would be the WDM's equivalent of the GMM asset score chart.
- Mimicry Chains text flow (Russia → Georgia → Bosnia → El Salvador → Kazakhstan) is a compelling story that deserves a proper node-link flow diagram. This is a differentiating feature no other political site publishes.
- Monthly Trend section: placeholder pending 4 weeks of data accumulation.
- Multiple sections (Electoral Watch, Digital & Civil, Autocratic Export, State & Media Capture, Legislative Watch) not yet in schema — will appear after Build 2 cron prompt update.

**Not yet visualised (data exists):**
- All 29 country severity scores → ranked horizontal bar chart
- Integrity Flags (7 flags) → text cards only

---

### Strategic Conflict & Escalation Monitor (SCEM)

**Existing visualisations:**
- Global Escalation Index — segmented colour band (LOW/MODERATE/HIGH/CRITICAL) with position marker
- Friction Flag Status Board — 7 F-flags with CLEAR/ACTIVE status
- Active Conflicts list — 10 cards with trend arrows
- Indicator Breakdown — horizontal deviation bar chart (dropdown-selectable per conflict, interactive)
- Per-conflict Indicator Tables — structured tables with 5-dot progress bars (report page, ×10)

**Issues:**
- **Indicator Breakdown chart shows CONTESTED BASELINE watermark for all 10 conflicts** — correct (baselines lock at week 13) but looks broken. Move explanation above the chart; show current readings as absolute values until baselines establish rather than showing an empty deviation chart.
- Ten conflicts are tracked but there is no single visual comparing them side-by-side. A 10-row horizontal bar (each = conflict's highest indicator reading, coloured by escalation trend ↑/→/↓) would provide a global overview before drill-down.
- F-Flag Status Board is well executed. Consider adding a 4-week history strip (● active / ○ clear) next to each flag to show persistence vs. episodic triggers.
- All 10 conflict baselines are currently CONTESTED — this limits the Escalation Index analytical value. Note is present but could be more prominent.

**Not yet visualised (data exists):**
- Composite Escalation Score (`conflict_roster[*].esc_score`) → multi-conflict bar *(listed in chart skill Sprint 2, data arrives Sun 5 Apr)*
- Escalation Velocity (`conflict_roster[*].escalation_velocity`) → direction indicator *(Sprint 2)*
- Roster Watch (named individuals) → text only, no influence diagram

---

### European Strategic Autonomy (ESA)

**Existing visualisations:**
- Strategic Autonomy gauge — arc/donut at 35%
- KPI Indicators list — 16 metrics with values and trend arrows (3 sections)
- Member State Tracker — 4 status cards (HU/SI/CZ/FR)
- Lagrange Point Radar — radar/spider chart (6 dimensions: Energy/Defence/Technology/Finance/Materials/Institutions, scored 0–100)
- Companion horizontal bar chart — same 6 dimensions as bar chart alongside radar

**Issues:**
- Lagrange Point Radar polygon hugs the centre (all dimensions below 55/100) — hard to read individual values. Companion bar chart is clearer. Consider making bar the primary and adding a 50% target benchmark line to the radar.
- Member State Tracker shows only 4 of 27 EU states — selection criteria not explained. Consider a mini-table of all 27 with RAG status.
- 16 KPI metrics are text + numbers + arrows. Adding sparklines or traffic-light colour coding per metric would improve scannability.

**Not yet visualised (data exists):**
- Defence Spending by Member State (`defence_spending[]`) → horizontal bar *(listed in chart skill Sprint 2)*
- Cross-Monitor Flags (6 CMS entries) → prose only

---

### AI Governance Monitor (AGM)

**Existing visualisations:**
- KPI Summary cards (3×)
- EU AI Act Regulatory Pipeline — 7-layer status tracker with countdown
- Risk Vector cards (5×) — colour-coded text labels (HIGH/ELEVATED)
- Country Grid — structured table (7 countries)
- Model Frontier — tiered card grid (3 tiers)

**Issues / missing (data exists in report):**
- 5 risk dimensions (Governance Fragmentation, Cyber Escalation, Platform Power, Export Controls, Disinfo Velocity) are text cards only. A radar/spider chart on the dashboard would give the AGM a compelling visual centrepiece — data exists, just needs rendering.
- Concentration Index (5 power dimensions: Compute/Foundation Models/Infrastructure/Applications/Safety) shows Concentrating vs. Fragmenting as text only. A centre-anchored bar chart (bars extending left=concentrating, right=fragmenting) would make the power-concentration story visual and analytically distinctive.
- Investment flows tracked weekly ($12B OpenAI, etc.) — no cumulative investment chart. Worth starting now so trend data accumulates.
- EU AI Act timeline is described as a tracker but rendered as prose in the report. The dashboard has a visual version — could be improved with more prominent colour coding and a visual countdown bar.
- Sector penetration (7 sectors with acceleration/stalling labels) — no quadrant or heatmap.

**Not yet visualised (data exists):**
- Governance Health Score (`governance_health`) → composite dial *(listed in chart skill Sprint 2)*
- Personnel headcount trend (OpenAI ~4,500 → ~8,000) → no chart

---

### Environmental Risks Monitor (ERM)

**Existing visualisations:**
- KPI Summary cards (4×)
- Planetary Boundary Status — horizontal bar chart (9 boundaries, coloured by status: Transgressed/Uncertain/Safe) ✅ **best single chart on the site**
- Tipping System Flags — status card grid (6 systems with severity badges)
- Active Cascade Chains — 3-column text table (labelled "heatmap")
- Boundary Detail Table — 9-row structured table with narratives

**Issues:**
- Planetary Boundary chart is strong. One improvement: add a quantitative value or "distance from safe limit" number per boundary so readers understand *how far* into transgressed territory each one is, not just that it's transgressed.
- Cascade Chains labelled "heatmap" but is a plain text table. Add colour encoding by severity or rename it.
- Tipping Point Proximity: the 6 active tipping systems (AMOC, Thwaites, Amazon Dieback, Greenland Ice Sheet, Permafrost Methane, Coral Reef Collapse) have proximity scores but no visual. A horizontal gauge/progress bar per system would make the stakes visceral.

**Not yet visualised (data exists):**
- Tipping Point Proximity (`tipping_systems[*].proximity_score`) → gauge/progress bar *(listed in chart skill Sprint 2)*

---

### FIMI & Cognitive Warfare (FCW)

**Existing visualisations:**
- KPI Summary cards (3×)
- Actor Threat Board — table with inline activity bars (7 actors: RU/CN/IR/US/IL/GULF/UNATTR)
- Top Campaigns — ranked card list (5 operations)
- Additional Active Operations — card/tag grid (7 operations)
- Attribution Log — structured table (appears sparsely populated — possible rendering issue)
- Platform Enforcement — structured table (same issue)

**Issues:**
- Actor Threat Board activity bars are the only quantitative encoding. Adding a campaign count axis (0–10) would improve readability.
- Attribution Log and Platform Enforcement tables appear empty — check whether JS renderer is correctly binding to these sections.
- 12 active campaigns across 7 actors with start dates and status — no timeline visual. A horizontal campaign timeline (x = date, each campaign = coloured bar from start to present, coloured by actor) would make operational FIMI tempo visible. Analytically distinctive — no mainstream tracker publishes this.

**Not yet visualised (data exists):**
- Campaign timeline (12 active operations with dates) → horizontal timeline
- Platform enforcement counts → no trend chart

---

## Priority Ranking

| # | Change | Monitor | Complexity | Notes |
|---|--------|---------|------------|-------|
| 1 | Fix Geographic View map (blank) | WDM | Medium | Highest-impact bug on site |
| 2 | Tipping Point Proximity bars | ERM | Low | Already in Sprint 2 chart skill |
| 3 | Country severity ranked bar chart (all 29 countries) | WDM | Low | Data exists, just needs renderer |
| 4 | AI Governance Risk Radar (5 dimensions) | AGM | Low | Data exists in dashboard |
| 5 | Macro Scenario inline probability bars | GMM | Low | ~20 lines CSS |
| 6 | Fed Funds Path bar chart | GMM | Low | Replace table |
| 7 | Fix prior-week bar colour in Asset Class chart | GMM | Low | 40% opacity of current colour |
| 8 | SCEM 10-conflict comparison bar | SCEM | Medium | Pre-baseline: use absolute readings |
| 9 | ESA radar benchmark line + bar as primary | ESA | Low | |
| 10 | Mimicry Chain flow diagram | WDM | Medium | Compelling differentiator |
| 11 | FIMI Campaign Timeline | FCW | Medium | Analytically distinctive |
| 12 | AGM Concentration Index visual | AGM | Low | Centre-anchored bar chart |
| 13 | GMM Regime Conviction History timeline | GMM | Medium | Builds value over time |
| 14 | Rename "heatmap" sections to match actual content | WDM, ERM | Low | Label fix only |

---

## Cross-Reference: Items Already in Chart Skill Sprint 2

The following from the above list are already queued in the `asym-intel-charts` skill:

- GMM: Regime Shift Probability (4-bar horizontal) — `signal.regime_shift_probabilities`
- GMM: Horizon Matrix — `horizon_matrix` (Sprint 2 schema)
- GMM: Factor Attribution — `factor_attribution` (Sprint 2 schema)
- SCEM: Composite Escalation Score — `conflict_roster[*].esc_score` (data arrives Sun 5 Apr)
- SCEM: Escalation Velocity — `conflict_roster[*].escalation_velocity`
- ESA: Defence Spending by Member State — `defence_spending[]`
- ERM: Tipping Point Proximity — `tipping_systems[*].proximity_score`
- AGM: Governance Health Score — `governance_health`

These should not be re-scoped — they are already defined and awaiting data or implementation.

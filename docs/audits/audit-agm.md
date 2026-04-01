# AGM Domain Audit
*Conducted: 2026-04-01 | Auditor: Domain Expert (AGM founding analyst)*
*Live pages audited: [dashboard](https://asym-intel.info/monitors/ai-governance/dashboard.html) · [report](https://asym-intel.info/monitors/ai-governance/report.html) · [persistent](https://asym-intel.info/monitors/ai-governance/persistent.html) · [digest](https://asym-intel.info/monitors/ai-governance/digest.html)*

---

## Part 1: Collected But Not Surfaced

### Audit Methodology
The JSON direct-access path (`/data/agm-latest.json`) returns 404, so this audit derives the "collected" schema from: (a) the methodology page's authoritative 16-module specification, (b) the rendered report.html content (which is the closest proxy to the full JSON output), (c) the persistent.html living knowledge structure, and (d) the dashboard.html rendering. Where a field is specified in the methodology but absent from rendered output, it is flagged as a gap. Where a field renders a literal `undefined` in the live page, this is an explicit surfacing bug.

### Gap Table

| Field / Data Element | In JSON Schema (per methodology) | Rendered on Dashboard | Rendered on Report | Rendered on Digest | Notes |
|---|---|---|---|---|---|
| **M00 — signal.text** | ✅ Collected | ✅ Lead Signal block | ✅ Full text | ❌ Digest not live | Core signal, best surfaced element |
| **M01 — intelligence.mainstream** (5 items) | ✅ Collected | ❌ Not shown | ✅ Rendered (4+ items visible) | ❌ Digest not live | Dashboard shows no M01 content at all |
| **M01 — intelligence.underweighted** (5 items) | ✅ Collected | ❌ Not shown | ✅ Rendered | ❌ Digest not live | High-value asymmetric content invisible on dashboard |
| **M01 — asymmetric_flags per item** | ✅ Collected | ❌ Not shown | ✅ Inline per item | ❌ Digest not live | Flag labels surfaced, full framing text only in report |
| **M02 — model_tracker** (releases, benchmarks, architectures) | ✅ Collected | ✅ "Model Frontier" KPI in sidebar nav | ✅ Partial (Anthropic T1 visible, others truncated) | ❌ Digest not live | Dashboard shows nav link only, no model cards; report renders truncated entries |
| **M02 — benchmark_deltas** | ✅ Collected (per methodology: "benchmark updates") | ❌ Not shown anywhere | ⚠️ Listed but no delta comparison | ❌ | No issue-over-issue benchmark movement tracked visually |
| **M02 — architectural_innovations flag** | ✅ Collected | ❌ Not shown | ⚠️ Implied but not explicitly flagged | ❌ | Methodology specifies "Architectural innovations flagged separately" — not visible |
| **M03 — capital.funding_rounds** | ✅ Collected | ❌ Not shown | ✅ "$12B additional tranche" rendered | ❌ | Dashboard has no investment summary |
| **M03 — capital.strategic_deals** | ✅ Collected | ❌ Not shown | ✅ Section header present, content sparse | ❌ | |
| **M03 — capital.energy_wall** | ✅ Collected (Energy Wall filter) | ❌ Not shown | ✅ Section header only, no items this issue | ❌ | Energy Wall filter is a key differentiator — not surfaced on dashboard at all |
| **M04 — deployment_by_sector** (7 sectors with Accelerating/Stalling/Emerging status) | ✅ Collected | ❌ Not shown | ✅ "Sector Penetration" section present | ❌ | Dashboard shows no sector heat map; 7-sector status grid would be high value |
| **M05 — regulation.EU_watch** | ✅ Collected | ✅ EU AI Act pipeline rendered (7 layers + countdown) | ✅ European Watch section (empty this issue) | ❌ | Dashboard renders this well; report section shows "No items this issue" — gap between persistent tracker and per-issue EU watch |
| **M05 — regulation.China_watch** | ✅ Collected | ❌ Not shown (Country Grid has China row) | ✅ China Watch section (empty this issue) | ❌ | Ciyuan watch on persistent.html but per-issue China Watch is "No items this issue" despite active China signals in Country Grid |
| **M05 — standards_vacuum.status + trigger + deadline** | ✅ Collected | ✅ Alert badge shown | ✅ Covered via M09 standards section | ❌ | Alert badge is good; no countdown timer on dashboard |
| **M06 — frontier_research.threshold_events** | ✅ Collected | ❌ Not shown | ✅ Section header, sparse content | ❌ | Threshold events are among the most important AGM outputs — absent from dashboard |
| **M06 — frontier_research.programme_updates** | ✅ Collected | ❌ Not shown | ✅ Google DeepMind/EMBL-EBI entry visible | ❌ | |
| **M06 — frontier_research.arxiv** | ✅ Collected | ❌ Not shown | ✅ "2026-03-30 arXiv cs.AI 1" — extremely sparse render | ❌ | arXiv data collected, renders only as a metadata stub with no title, abstract, or significance note |
| **M06 — frontier_research.drill_down** | ✅ Collected (Science Drill-Down filter) | ❌ Not shown | ⚠️ Not clearly delineated | ❌ | Drill-down analysis not distinguishable from standard entries |
| **M07 — risk_vectors** (5 vectors: Governance Fragmentation, Cyber Escalation, Platform Power, Export Controls, Disinfo Velocity) | ✅ Collected | ✅ "Risk Vector Heat Grid" header present | ✅ "Risk Indicators" section rendered | ❌ | **Critical gap**: Dashboard shows header but content is EMPTY (not rendered). Persistent.html shows `undefined` for Risk Vectors. This is a hard rendering bug. |
| **M07 — risk_vector ratings** (HIGH/ELEVATED/VACUUM) | ✅ Collected | ❌ Rendering bug — `undefined` | ✅ Present in report | ❌ | The colour-coded rating system is the most scannable dashboard element — broken |
| **M08 — dual_use** (procurement, doctrine, capability, IHL friction) | ✅ Collected | ❌ Not shown | ✅ "Military AI" section rendered | ❌ | No dashboard visibility; IHL friction analysis collected but not highlighted |
| **M08 — IHL_friction_analysis** | ✅ Collected (mandatory per methodology) | ❌ Not shown | ⚠️ Present but not labelled as IHL analysis | ❌ | Methodology says "IHL friction analysis mandatory for capability and doctrine items" — not visually distinguished in report |
| **M09 — law_standards_litigation.law** | ✅ Collected | ❌ Not shown | ✅ Law section present | ❌ | |
| **M09 — law_standards_litigation.standards** | ✅ Collected | ⚠️ Standards Vacuum badge only | ✅ Standards section present | ❌ | |
| **M09 — law_standards_litigation.litigation** | ✅ Collected | ❌ Not shown | ✅ Litigation section present | ❌ | |
| **M09 — country_grid** (per-jurisdiction signal) | ✅ Collected | ✅ Country Grid table rendered | ✅ Implied via Law section | ❌ | Country Grid rendered on dashboard but not on report (no duplicate — by design) |
| **M09 — country_grid_watch** (persistent version) | ✅ Collected | ⚠️ Not a separate element | ⚠️ Not explicitly delineated | ❌ | The difference between weekly Country Grid and persistent country_grid_watch is not surfaced |
| **M10 — governance_gaps** (international soft law, corporate governance, product liability, algorithmic accountability, governance gaps sub-sections) | ✅ Collected | ❌ Not shown | ✅ All 5 sub-sections rendered | ❌ | 5 sub-sections collected, zero dashboard presence |
| **M11 — accountability** (lab ethics commitments, accountability friction, AISI ethics pipeline) | ✅ Collected | ❌ Not shown | ✅ "Ethics" section rendered | ❌ | Accountability friction analysis (mandatory per methodology) has no dashboard surface |
| **M12 — misuse_detection** (FIMI, synthetic media, narrative manipulation, state actor attribution, detection methods) | ✅ Collected | ❌ Not shown | ✅ "Info Ops" section with asymmetric flags rendered | ❌ | |
| **M12 — capability_watch** | ✅ Collected | ❌ Not shown | ✅ Section header present | ❌ | |
| **M13 — societal_impact** (labour, inequality, public trust, demographic impacts) | ✅ Collected | ❌ Not shown | ✅ "AI & Society" with structural trends + asymmetric flags | ❌ | |
| **M14 — power_concentration.concentration_index** | ✅ Collected | ❌ Not shown on dashboard | ✅ "Power Structures" with Concentration Index | ❌ | Persistent.html renders this well with bar widths; dashboard has no surface |
| **M14 — power_concentration.asymmetric_flags** | ✅ Collected | ❌ Not shown | ✅ 3 flags rendered | ❌ | |
| **M15 — personnel_movements.lab_movements** | ✅ Collected | ❌ Not shown | ✅ Lab Movements section rendered | ❌ | |
| **M15 — personnel_movements.government_ai_bodies** | ✅ Collected | ❌ Not shown | ✅ Government AI Bodies section (interim leadership flag) | ❌ | |
| **M15 — personnel_movements.revolving_door** | ✅ Collected | ❌ Not shown | ✅ Revolving Door section with 12-month summary | ❌ | |
| **M15 — AISI_pipeline** | ✅ Collected | ❌ Not shown | ✅ Referenced in report | ⚠️ Persistent shows `undefined` | **Rendering bug**: Persistent.html "AISI Pipeline (M15)" section renders `undefined` |
| **delta_strip** (top 5 items) | ✅ Collected | ✅ Header present, count shown (5) | ✅ Implied via M01 | ❌ | Dashboard shows "5" count but the actual delta items are not listed — counter without content |
| **cross_monitor_flags** (cmf-001 through cmf-006) | ✅ Collected | ⚠️ Not on dashboard | ✅ Cross-Monitor Signals section (cmf-001 shown) | ✅ Persistent renders all 6 flags fully | Only page rendering this well is persistent.html |
| **M05/M09 — regulatory_calendar** | ❌ Not in schema | ❌ | ❌ | ❌ | **Schema gap**: Countdown to Aug 2026 is hand-computed, not a structured calendar field |
| **Governance health composite score** | ❌ Not in schema | ❌ | ❌ | ❌ | **Schema gap** |
| **Capability-governance lag index** | ❌ Not in schema | ❌ | ❌ | ❌ | **Schema gap** |

### Summary of Rendering Bugs (Explicit)
1. **M07 Risk Vectors — dashboard**: Header exists, content does not render.
2. **M07 Risk Vectors — persistent.html**: Renders literal `undefined`.
3. **M15 AISI Pipeline — persistent.html**: Renders literal `undefined`.
4. **M15 Ongoing Lab Postures — persistent.html**: Renders literal `undefined`.
5. **Delta Strip — dashboard**: Count (5) shown but items not listed.
6. **M06 arXiv — report**: Renders as metadata stub only (date + category + count), no title or significance.
7. **Digest page**: Not live — subscription form placeholder only; renders "15 modules" in copy but schema has 16.

---

## Part 2: Recommended Improvements

### Schema/Data Additions (ranked by value)

**1. Governance Health Composite Score** *(Value: Critical | Effort: Medium)*
A single synthesised score (0–100 or traffic light) computed from: M07 risk vector average severity + M09 regulatory pipeline completion + M10 governance gap count + M11 accountability friction + M15 oversight body capacity. This is the single most requested output by policy analysts and investors — "is governance keeping pace with capability?" The score would surface on every page and become the AGM's signature metric. Sub-scores per dimension enable drill-down. Updated weekly.

**2. Capability-Governance Lag Index** *(Value: Critical | Effort: High)*
The structural claim the AGM makes repeatedly is that governance lags capability. Quantify it. Track: (a) capability advancement events in M02/M06 (scored by magnitude), (b) governance response events in M05/M09/M10 (scored by bindingness), (c) compute a rolling 12-week lag in weighted days. Render as a time-series chart. This is the monitor's analytical thesis made measurable — it transforms the AGM from a narrative publication into a data product with a proprietary signal.

**3. Regulatory Calendar with Countdown Timers** *(Value: High | Effort: Low)*
Structured `regulatory_calendar` array in the JSON: `{event, jurisdiction, date, type: [deadline|vote|enforcement|review], status}`. Currently the EU AI Act countdown (122 days) is computed ad hoc; the Omnibus 28 April deadline is only in the narrative. A calendar object enables: dashboard countdown widgets per event, automated staleness alerts, and forward-looking "next 30 days" module on the dashboard. The value is disproportionate to effort — it is largely data entry from already-collected M05/M09 content.

**4. Model Capability Score (per tracked model)** *(Value: High | Effort: Medium)*
M02 tracks model releases but does not aggregate a per-model capability rating across dimensions (reasoning, coding, cyberoffense, multimodal, agentic autonomy). Add a structured `capability_profile` per tracked model: `{model_id, lab, tier, dimensions: {reasoning, coding, cyber, bio, agentic}, eval_source, date}`. This enables: trend charts of capability acceleration, the capability-governance lag computation above, and the dual-use risk flag in M08. OpenAI Preparedness Scorecards and Anthropic RSP threshold triggers already provide tier-1 source data for this.

**5. Jurisdiction Risk Matrix** *(Value: High | Effort: Medium)*
Extend the Country Grid from a narrative column to a structured object: `{jurisdiction, ai_law_status, enforcement_capacity: [operational|transitional|none], regulatory_velocity: [accelerating|stable|retreating], strategic_posture: [leading|following|opting_out], last_event, next_event}`. The current Country Grid is a text summary — structuring it enables a sortable matrix view, cross-issue trend tracking, and direct input into the governance health score.

**6. Lab Governance Posture Scorecard** *(Value: High | Effort: Medium)*
A persistent `lab_posture` object per major lab (OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Mistral): `{lab, rsp_trigger_status, disclosure_record [compliance|partial|refused], audit_access [full|limited|none], government_contracts [type, scope], revolving_door_velocity, opsec_incidents}`. M11 currently tracks ethics/accountability per item — aggregating to a scorecard makes it persistent and comparable. The Anthropic opsec double failure this issue is exactly the event that should decrement a disclosure_record score.

**7. Investment Flow Structured Object** *(Value: Medium | Effort: Low)*
M03 funding rounds are narrative. Add `{round_id, entity, amount_USD, type: [equity|debt|sovereign_wealth|strategic], investors, valuation, sector: [foundation_model|infrastructure|application|safety], energy_wall: boolean}`. Enables: weekly capital flow dashboard widget, investor network analysis, energy wall filter as a standalone chart. The $852B OpenAI valuation at 60x revenue is the data point that needs a time-series context.

**8. Asymmetric Flag Taxonomy** *(Value: Medium | Effort: Low)*
Add a `flag_type` field to every asymmetric flag: `{reframing | underweighting | structural_implication | cross_monitor}`. Currently all flags are equal weight. Tagging by type enables: filtering (investors want structural_implication; safety researchers want reframing); issue-level analytics ("this issue has 8 structural flags vs. 3 last issue"); and digest personalisation.

**9. Export Control Tracker** *(Value: Medium | Effort: Medium)*
Currently tracked within M07 (Export Controls vector) as one of five risk vectors with a single rating. Export controls are now a primary geopolitical competition variable (Nvidia BIS rules, TSMC compliance, AMD-Meta bilateral deals). Deserves a persistent structured module: `{entity, restriction_type, jurisdiction, date_effective, enforcement_status, workaround_signals}`. The China token volume surpassing US (4.12T vs. 2.94T in February 2026) is partly an export control efficacy signal — it needs to connect to a structured tracker.

**10. Benchmark Contamination / Eval Integrity Flag** *(Value: Medium | Effort: Medium)*
M02 tracks benchmark updates but has no field for evaluation integrity concerns (benchmark saturation, contamination, gaming). Add `eval_integrity_flag: {concern_type, evidence_source, affected_benchmarks}` to M02 entries. This matters for both AI safety researchers (who know MMLU and HLE are saturating) and investors (who need to distinguish genuine vs. Goodhart capability claims).

---

### Dashboard/Digest Rendering Improvements (ranked)

**1. Fix the Three `undefined` Rendering Bugs** *(Value: Critical | Effort: Low)*
Persistent.html renders `undefined` for Risk Vectors (M07), AISI Pipeline (M15), and Ongoing Lab Postures. These are live data bugs that undermine the product's credibility. The fields exist in the JSON schema — the template is failing to access them. Fix before any aesthetic improvements.

**2. Activate the Delta Strip Content** *(Value: High | Effort: Low)*
Dashboard shows a "5" counter for Delta Items but lists nothing. The delta strip is the highest-attention item for weekly returning users — they want to see "what changed since last week" in five lines. The data is collected (top-5 items from M01 underweighted + M07/M09 changes). Render the items, not just the count.

**3. Sector Penetration Heat Map on Dashboard** *(Value: High | Effort: Low)*
M04's 7-sector status (Accelerating/Stalling/Emerging) is pure dashboard material — it is already a structured rating, not a narrative. Replace or supplement the current sparse Model Frontier sidebar link with a 7-cell sector grid showing colour-coded status. This is high-scannability content that the current dashboard lacks entirely.

**4. Risk Vector Heat Grid — Fix and Elevate** *(Value: High | Effort: Low)*
The dashboard has a "Risk Vector Heat Grid" header and the data exists in M07 (5 vectors × HIGH/ELEVATED/VACUUM ratings). The grid simply does not render. Once fixed, this should be the second element users see — after the EU AI Act pipeline — because it answers "how dangerous is the current environment?" in a 5-cell visual. Add delta arrows (↑/↓/→) vs. prior issue.

**5. Governance Health Score Widget** *(Value: High | Effort: Medium — depends on schema addition #1)*
Once the composite score exists in the schema, add a prominent widget at the top of the dashboard: score number, colour band, one-line rationale, delta vs. prior week. This becomes the AGM's masthead metric — what Bloomberg Terminal's risk indices are for finance. Policy analysts and investors will anchor on it.

**6. Report Page: Collapse Low-Signal Modules by Default** *(Value: High | Effort: Low)*
The report renders 16 modules sequentially in a long scroll. Modules that have "No items this issue" (EU Watch, China Watch in this issue; Energy Wall) should collapse by default with a "+expand" affordance. This removes cognitive friction for users scanning for active signal and makes the density of the report's strong issues (like Issue 2) more legible. Empty sections currently create a false impression that the monitor missed coverage.

**7. Module Density Indicator** *(Value: Medium | Effort: Low)*
Add a small item-count badge to each module in the sidebar nav (e.g., "02 Model Frontier · 3", "08 Military AI · 5"). Users can then scan the sidebar to find where the density is this issue before scrolling. Low effort, significant UX improvement for the target audience who reads the report as a structured briefing.

**8. Digest Page — Build It** *(Value: High | Effort: Medium)*
The digest.html is a placeholder. It describes what subscribers will receive ("The Signal, top 5 items, and key developments across all 15 modules" — note: copy says 15, schema has 16) but delivers nothing. For returning users who do not need the full report, a rendered digest on the page (not just email) is the most-used surface. Priority: The Signal + delta_strip top 5 + M07 risk ratings + M14 concentration index + cross_monitor_flags count. This is 6 data fields already collected and should render as a one-screen brief.

**9. Country Grid — Add Regulatory Velocity Column** *(Value: Medium | Effort: Low)*
The Country Grid table has two columns: Country and Signal. Add a third column: Trend (↑ Accelerating / → Stable / ↓ Retreating). The data exists in M09. The visual makes the geopolitical competition narrative scannable — users see immediately that EU is accelerating, UK is stalled, US is retreating on safety frameworks.

**10. Cross-Monitor Flags — Dashboard Widget** *(Value: Medium | Effort: Low)*
The 6 cross-monitor flags (cmf-001 through cmf-006) are fully rendered on persistent.html but invisible on the dashboard. Add a compact "Cross-Monitor Signals: 6 Active" widget on the dashboard with flag IDs and one-line summaries — it signals the AGM's cross-monitor intelligence value and drives traffic to persistent.html.

**11. Persistent Page — Time-Series Chart for Concentration Index** *(Value: Medium | Effort: Medium)*
The Concentration Index (M14) on persistent.html uses bar-width for current-state. Add issue-over-issue trend lines per domain (Compute/GPU, Foundation Models, AI Safety/Oversight). The "Nvidia ~11x AMD" ratio has a direction of travel that matters more than the point-in-time snapshot. Two issues is too few — but establishing the data structure now pays off by Issue 10.

---

### Methodology Improvements (ranked)

**1. China Coverage Structural Gap** *(Value: Critical)*
The most significant coverage gap in the current schema is the disconnect between China signals in the Country Grid (active, strong signals every issue) and the M05 China Watch per-issue section (empty two issues running). The root cause: China Watch is populated only when there are explicit regulatory/governance events, but the most important China signals are capability trajectory, token volume metrics, and export control bypass evidence — which land in M02, M07, and M03 respectively with no aggregation. *Fix*: Add a `china_capability_watch` persistent tracker alongside the `ciyuan_watch` already in persistent.html. Track: weekly token volume, open-weight vs. proprietary mix, frontier model release cadence, and BIS enforcement signals. The 4.12T vs. 2.94T token volume reversal (China now exceeding US) should have been a standalone signal-level event, not a Country Grid footnote.

**2. Underweighted Signal Category: Compute Access Asymmetry Below the Hyperscaler Layer** *(Value: High)*
The Concentration Index tracks Nvidia/AMD/Intel and Big 4 cloud. It does not track the mid-tier compute access layer: inference-only providers (Together AI, Fireworks, Groq), academic compute access (NSF NAIRR, UK AIRR), and the Global South compute gap. The geopolitical thesis of AI advantage depends not just on who owns the GPUs but on who can access inference at scale. This layer is systematically underweighted in all mainstream AI coverage — making it a core asymmetric signal the AGM should own.

**3. Underweighted Signal Category: Standards Bodies as Power Structures** *(Value: High)*
JTC21 delay gets coverage as a compliance problem. It is not tracked as what it actually is: a structural power contest between US (NIST-influenced) and EU (risk-based) approaches to AI standardisation, with ISO/IEC SC 42 as the global battleground. The ciyuan (词元) signal is precisely this pattern at the terminology layer — China is attempting to set the token-as-settlement-unit paradigm before global standards lock. AGM should add a `standards_geopolitics` sub-module tracking: ISO/IEC SC 42 working group composition, national body positions, and draft standard publication timelines by jurisdiction. This is invisible in mainstream coverage.

**4. Underweighted Signal Category: AI in Democratic and Electoral Processes** *(Value: High)*
The SIO dismantlement and 2026 US midterms deepfake risk is tracked in M12 and cross-monitor flag cmf-002. But the upstream governance failure — that no federal AI disclosure law for political advertising exists, that the FEC has not acted, and that state-level efforts are being preempted — is a systemic gap that deserves a dedicated `electoral_ai_governance` tracker. The structural detection vacuum created by SIO's removal is a one-time, irreversible event occurring in a narrow time window before November 2026. This deserves more than asymmetric flags in M12.

**5. Underweighted Signal Category: Autonomous Weapons — Doctrine vs. Deployment Gap** *(Value: High)*
M08 covers military AI well but currently treats procurement and doctrine as parallel tracks. The key asymmetric signal is the gap between stated doctrine (DoD 3000.09 human control requirement) and actual deployment (hypersonic engagement timelines that make human-in-the-loop physically impossible). This gap is the crux of the IHL friction analysis but is not tracked as a persistent, quantified metric. *Fix*: Add `doctrine_deployment_gap` as a persistent M08 field: `{system_type, stated_policy, operational_timeline, human_in_loop_feasible: boolean, source}`. The DoD rejection of Gillibrand's autonomous weapons guardrails is the most recent evidence — it should trigger a flag on this tracker, not just appear in a narrative item.

**6. Underweighted Signal Category: AI Safety Institution Capacity** *(Value: High)*
The three-way simultaneous leadership vacuum (UK AISI, US CAISI, EU AI Office) is flagged in M15 and cmf flags. What is not tracked is the structural capacity metric: staff count, budget, enforcement powers, and decisions-per-month for each body. The coordination vacuum at August 2026 is a thesis — but without capacity metrics it cannot be falsified or tracked. *Fix*: Add `oversight_capacity_index` to the persistent tracker: per-body staffing, budget, decisions issued, and enforcement actions pending. This converts the qualitative "vacuum" narrative into a measurable deterioration curve.

**7. Underweighted Signal Category: Foundation Model Concentration Below the Frontier** *(Value: Medium)*
The AGM tracks frontier labs (OpenAI, Anthropic, Google DeepMind, Meta, xAI, Mistral). The most underweighted dynamic is the consolidation at the second tier: Harvey AI and Legora in legal, Cohere in enterprise, Glean in enterprise search, Nvidia NIM microservices as a deployment layer. These are the actual lock-in dynamics for non-frontier deployments, which represent 95% of AI economic value. The application layer is described as "Fragmenting" in the Concentration Index but this is directionally wrong for vertical-specific deployments.

**8. Underweighted Signal Category: Regulatory Arbitrage Positioning** *(Value: Medium)*
Multiple labs are structurally positioning to exploit governance gaps: Anthropic's Gibraltar-adjacent structures, xAI's offshore compute positioning, OpenAI's shift to a PBC with government contractor culture. The M10/M11 governance modules track corporate governance commitments but do not track regulatory arbitrage positioning as a structural signal. A `regulatory_arbitrage_watch` field would track: entity, jurisdiction of incorporation vs. primary operations, tax/regulatory treatment differential, and government contracts by jurisdiction.

**9. Source Coverage Gap: SEC Filings and Investor Communications** *(Value: Medium)*
The methodology lists SEC filings (S-1, 13F, 8-K) as a monitored source. In practice, M03 covers funding rounds but does not systematically surface investor-grade signals from SEC filings: governance provisions in S-1s, related-party transaction disclosures, material risk factors (which often contain the clearest internal assessments of AI risk), or 13F position changes by AI-exposed institutional investors. For the investor audience, this is a high-value gap.

**10. Temporal Coverage Gap: Sub-Weekly Velocity for Acute Events** *(Value: Medium)*
The AGM is a weekly publication, which is appropriate for structural signals. But acute events (the Anthropic double opsec failure, the OpenAI $852B close, the Omnibus trilogue opening) are 2–5 days old by publication. For the target audience (policy analysts, investors), sub-weekly velocity matters for the highest-tier signals. *Recommendation*: Add a `hot_signal` field in the schema for items that meet the Signal threshold mid-week, surfaced via a lightweight alert mechanism (RSS/webhook/persistent page update) without waiting for Friday publication. This does not require changing the weekly cadence — just adding a surfacing layer for the most time-sensitive items.

---

## Priority Summary

| Rank | Action | Value | Effort | Rationale |
|---|---|---|---|---|
| **1** | **~~Fix three `undefined` rendering bugs~~ ✅ 2026-04-01 (M07, M15 AISI, M15 lab postures on persistent.html)** (M07 risk vectors, M15 AISI pipeline, M15 lab postures on persistent.html) | Critical | Low | Live product credibility bug. Data exists, template access is broken. Fix in hours, not days. |
| **2** | **~~Activate delta strip content on dashboard~~ ✅ 2026-04-01 (confirmed working — was rendering correctly already)** (render top-5 items, not just count) and **fix Risk Vector Heat Grid rendering** | High | Low | Two dashboard elements with headers and data but no content. Highest-return rendering fix after bug fixes. |
| **3** | **Add `regulatory_calendar` structured field** with countdown timers | High | Low | The August 2026 enforcement cliff, Omnibus 28 April deadline, and watermarking November activation are already being tracked narratively. Structuring them into a calendar object unlocks dashboard countdown widgets, forward-looking module, and automated staleness alerts with ~1 day of data entry work. |
| **4** | **Build the Governance Health Composite Score** (schema + dashboard widget) | Critical | Medium | The AGM's analytical thesis ("governance is not keeping pace with capability") needs a measurable, persistent expression. A composite score computed from existing M07/M09/M10/M11/M15 data becomes the monitor's signature metric and the primary value proposition for the investor and policy audience. |
| **5** | **Restructure China coverage** from per-issue section to persistent capability tracker | High | Medium | China Watch has been empty two consecutive issues despite China being the most active non-EU AI governance and capability story. The ciyuan signal, token volume reversal, and export control bypass patterns deserve a persistent structured tracker parallel to the EU AI Act pipeline. This is the single largest coverage gap relative to the audience's intelligence needs. |

---

*Audit Notes: JSON direct-access path (attempted `/data/agm-latest.json`, `/data/latest.json`, `/issues/002.json`) returns 404 — the JSON source is not publicly accessible. This audit derives the collected schema from the methodology specification, rendered output analysis, and comparison of what persistent.html describes vs. renders. If JSON access is available internally, a more precise field-level audit is possible. The `undefined` rendering bugs are the clearest evidence of fields that are in the schema but not accessible by the template.*

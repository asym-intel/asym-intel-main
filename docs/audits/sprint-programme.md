# Asymmetric Intelligence — Sprint Programme
**Platform:** asym-intel.info  
**Last updated:** 1 April 2026  
**Status:** Post-Infrastructure Sprint

---

## Executive Summary

The platform has completed three phases of structured work. Sprint 1 cleared the critical rendering bugs and institutional data gaps that were blocking publication. Sprint 2A delivered the visual/charting layer — maps, radar charts, comparison bars — across all seven monitors. Today's Infrastructure Sprint addressed the invisible but foundational layer: governance documentation, agent identity framework, SEO/sitemap correctness, and signal link UX consistency across all dashboards.

**Where we are now:** The platform is structurally sound. All seven monitors publish, all crons fire on schedule, and the governance/identity framework is in place for autonomous operation. The remaining work is a well-understood backlog organised by effort level.

**What's next:** Sprint 2B is data-gated — it waits on cron runs this week (SCEM Sun 5 Apr, WDM Mon 6 Apr, ESA Wed 8 Apr, FCW Thu 9 Apr). Sprint 3 is a single focused session of low-effort rendering bugs and quick schema additions — the longest list but the lowest individual effort per item. Sprints 4 and 5 are the schema expansion and architectural work that will unlock the platform's analytical depth.

**Immediate user actions required:**
- GSC domain property verification (enables sitemap submission and coverage data)
- Monitor first cron outputs this week against FE-019 (filename must match date field)

**Monitors:** GMM · FCW · ESA · AGM · SCEM · ERM · WDM

---

## COMPLETED SPRINTS (reference only)

### Sprint 1 ✅
Bugs, ESA institutional items, AGM undefined bugs, ERM/FCW/GMM rendering. PRs #18–#22.

### Sprint 2A ✅
Nine visual/chart items: WDM world map, GMM prior-week bars, ERM tipping bars, AGM radar + diverging bar, ESA benchmark bar, SCEM comparison bar.

### Infrastructure Sprint ✅ (1 April 2026)
Sitemap correctness, SEO fixes, agent identity framework, governance documents, signal link UX fixes across all monitors. Full item list below for audit trail.

**Infrastructure Sprint — completed items:**

| Area | Item |
|------|------|
| Governance | COMPUTER.md v1.9 — internal repo, notes-for-computer.md, MISSION/ROLES in Step 0 |
| Governance | All 7 cron prompts — identity block prepended (MISSION.md + analyst template + internal spec) |
| Governance | All 7 internal methodology specs — architecture block added (two-pass, publish guard, Step 0B) |
| Governance | docs/MISSION.md, docs/ROLES.md — platform governance documents |
| Governance | docs/prompts/platform-developer.md, docs/prompts/domain-analyst-template.md |
| Governance | AGENT-IDENTITIES.md — deep analyst identity cards (internal repo) |
| Governance | notes-for-computer.md — inter-agent communication channel |
| Governance | ESA internal spec — stray JS removed |
| Governance | Anti-pattern FE-019 — Hugo brief filename must match date field |
| SEO | asym-intel.info/sitemap.xml — xmlns:xhtml removed (GSC "could not be read" fix) |
| SEO | FCW brief renamed 2026-04-02 → 2026-04-01 (future-dated URL in sitemap) |
| SEO | compossible.asym-intel.info/sitemap.xml — xmlns:xhtml removed |
| SEO | compossible.asym-intel.info tag/category pages — noindex,follow added |
| SEO | Compossible hugo.toml — sitemap changefreq/priority defaults added |
| Content | content/mission.md — Mission & Principles published at /mission/ |
| Content | content/about.md — updated to link to /mission/ |
| Content | hugo.toml — Mission added to site nav |
| UX | base.css — .signal-block .source-link white text (all 7 monitors) |
| UX | WDM + FCW dashboard — "See lead signal ↓" scroll anchor in KPI card sub |
| UX | GMM dashboard — signal block link uses .signal-block .source-link class |
| UX | All 7 cron prompts — GMM/FCW/ESA/AGM explicit PUBLISH_DATE derivation rule (FE-019) |
| UX | robots.txt — confirmed correct |

---

## SPRINT 2B — Data-Dependent Items
**Goal:** Complete the visualisations that are built but waiting on cron data produced this week.

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| SCEM | Verify first publish output | Infrastructure | First cron: Sun 5 Apr 18:30 UTC (cron a67a9739) — confirm FE-019 compliance |
| WDM | Verify first publish output | Infrastructure | First cron: Mon 6 Apr 06:30 UTC (cron 10ddf5f0) — confirm FE-019 compliance |
| WDM | Category B sections render | Rendering | First appearance Mon 6 Apr — verify section markup renders on report.html |
| ESA | Defence spending bar chart | Rendering | Waiting on Wed 8 Apr cron — defence_spending array must be present in output |
| FCW | Campaign timeline Gantt | Rendering | Waiting on Thu 9 Apr cron — start_date field must be present in campaign objects |
| ALL | GSC sitemap submission | Infrastructure | User action: verify domain property in GSC first, then submit both sitemaps |

**Done when:** All five crons have fired and outputs confirmed valid; GSC domain property verified and sitemaps submitted; Category B sections visible on WDM report; ESA defence spending bar visible on ESA dashboard; FCW Gantt visible on FCW dashboard.

---

## PIPELINE OUTSOURCING REVIEW — Gate before each new pipeline

**Agreed 2 April 2026.** Before finalising the GitHub Actions pipeline for WDM, ESA, AGM, or ERM,
run the following review against the FCW/GMM/SCEM reference pattern:

> "Before we finalise the next Perplexity-linked monitors, check we have outsourced as much as is reasonable."

**Review questions (per monitor, per pipeline layer):**
1. Is there any step currently in the Computer Analyst cron that a sonar/sonar-pro Collector could do?
2. Does the weekly Research layer (sonar-pro) capture everything that currently requires Analyst judgement?
3. Is the Reasoner layer (sonar-deep-research) being used correctly — reasoning over structured data only, not web search?
4. After the first 2-3 live runs: is the Analyst adding genuine value over raw Collector output, or just reformatting?

**Reference:** FCW/GMM/SCEM pipelines. Pattern: sonar (daily) → sonar-pro (weekly) → sonar-deep-research (Reasoner) → Computer Analyst (methodology + publish).

**Trigger:** Run this review before opening the pipeline build session for each remaining monitor.

---

## SPRINT 3 — Rendering & Quick Schema (Next Session)
**Goal:** Clear all pending low-effort rendering bugs and quick schema additions across all monitors in a single focused session.

### AGM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| AGM | digest.html not live | Rendering | Page template exists but not linked from dashboard nav |
| AGM | M06 arXiv stub — render section | Rendering | Schema stub present; need HTML section in report.html |
| AGM | Risk vector heat grid | Rendering | Data likely present in schema; new HTML grid component needed |

### SCEM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| SCEM | Roster watch section on report.html | Rendering | Section defined in methodology; template section missing |
| SCEM | Cross-monitor flags section on report.html | Rendering | Same — template section missing |
| SCEM | Indicator deviation chart fix | Bug | Chart rendering error from Sprint 1 — regression or data shape issue |
| SCEM | GEI CONTESTED disclaimer | Rendering | Display disclaimer when GEI value is flagged CONTESTED |
| SCEM | Schema version mismatch | Bug | Internal spec version ≠ cron output version — align field names |

### ESA

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| ESA | Lagrange radar 6th spoke | Rendering | Radar chart has 5 spokes; 6th dimension defined in schema — add spoke |
| ESA | institutional_developments on dashboard | Rendering | Field present in schema; not surfaced on dashboard — add card |

### FCW

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| FCW | All 12 campaigns on dashboard | Rendering | Dashboard currently shows subset; loop over full campaigns array |
| FCW | attribution_log instrument field fix | Bug | Field name mismatch between schema and template |
| FCW | attribution_log actor field fix | Bug | Same — actor field not rendering |
| FCW | threat_level schema field | Schema | Field defined in spec; not in cron output — add to prompt, render in HTML |

### GMM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| GMM | hard_landing_risk KPI card | Rendering | Field in schema; KPI card not rendered on dashboard |
| GMM | Tail risk note tooltips | Rendering | tail_risk_note text exists; needs tooltip component on relevant cards |
| GMM | Scenario cards | Rendering | scenarios array in schema; no card component on dashboard |
| GMM | regime_shift_probabilities chart | Rendering | Data in schema; no chart rendered — bar or pie chart |
| GMM | sentiment_overlay table | Rendering | sentiment_overlay object in schema; no table on dashboard |
| GMM | Real M2 waterfall chart | Rendering | real_m2 data in schema; waterfall chart component needed |

### WDM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| WDM | source_url enforcement | Schema | Enforce source_url on every signal object in cron prompt |
| WDM | severity_sub field render | Rendering | Field in schema; not rendered on dashboard cards |
| WDM | silent_erosion section | Rendering | Section defined in methodology; not rendered on report.html |
| WDM | signal.history render | Rendering | history array in schema; no rendering — show delta or trend indicator |
| WDM | weekly_brief on dashboard | Rendering | weekly_brief field in schema; not surfaced on dashboard |

### ERM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| ERM | Cascade tier breakdown on report | Rendering | cascade_tiers array in schema; only summary shown — expand to full breakdown |
| ERM | reverse_cascade_check | Rendering | Methodology defines reverse cascade check; no HTML section |
| ERM | M03 three-layer rendering | Rendering | M03 has three-layer schema; only top layer rendered |

### ALL Monitors

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| ALL | Source links on every card with source_url | Rendering | Where source_url is present in schema, link should appear on card — systematic pass |
| ALL | Cross-monitor flags widget on all dashboards | Rendering | Widget designed in methodology; not implemented on any dashboard |

**Done when:** All items above are rendered correctly on their respective dashboards and reports; source links appear wherever source_url is populated; cross-monitor flags widget live on all 7 dashboards.

---

## SPRINT 4 — Schema Sprint (Medium Effort)
**Goal:** Add new data fields that don't exist yet — requires cron prompt updates and corresponding HTML renders. Group by monitor; do all prompt + HTML work together per monitor.

### GMM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| GMM | credit_spreads field | Schema | Add to cron prompt; render spread chart on dashboard |
| GMM | VIX term structure | Schema | Add term structure array to prompt; render curve chart |
| GMM | Tariff quantification | Schema | Structured tariff impact field; render as annotated figure |
| GMM | Scenario-conditional impacts | Schema | Extend scenarios object with conditional impact fields; render in scenario cards |

### FCW

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| FCW | Narratives registry | Schema | New top-level object tracking active narratives; render as table |
| FCW | effectiveness object per campaign | Schema | Add effectiveness scoring to each campaign; render as badge/score |
| FCW | campaign start_date (all campaigns) | Schema | Required for Gantt (Sprint 2B) — enforce in prompt |
| FCW | cognitive_warfare persistence field | Schema | Duration/persistence score per campaign; render on campaign card |

### ESA

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| ESA | defence_spending array (structured) | Schema | Structured spend-by-country array; used by Sprint 2B bar chart |
| ESA | scorecard structured fields | Schema | Replace narrative scorecard with machine-readable fields; render as grid |
| ESA | us_dependency field | Schema | Quantified US dependency score per actor; render on actor cards |
| ESA | defence_programmes tracker | Schema | Structured tracker object per programme; render as status table |

### AGM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| AGM | Governance health composite | Schema | Composite score across governance dimensions; render as summary KPI |
| AGM | Jurisdiction risk matrix | Schema | Structured matrix object; render as heat grid (companion to Sprint 3 risk vector grid) |
| AGM | Lab posture scorecard | Schema | Structured lab-by-lab posture fields; render as comparison table |
| AGM | capability_profile object | Schema | Structured capability object per actor; render on actor cards |

### ERM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| ERM | Planetary boundary proximity scores | Schema | Numeric proximity score per boundary; render as progress bars |
| ERM | Tipping system standardisation | Schema | Standardise tipping_system object across all M-series entries |
| ERM | M05 regulatory pipeline | Schema | Structured pipeline array; render as status table on M05 section |

### SCEM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| SCEM | escalation_velocity field | Schema | Rate-of-change metric for escalation score; render as trend indicator |
| SCEM | esc_score composite | Schema | Composite escalation score with sub-components; render as breakdown |
| SCEM | PROVISIONAL band tier | Schema | Flag output as PROVISIONAL when data is sparse; render disclaimer |
| SCEM | I7 proxy warfare indicator | Schema | New indicator in I-series; add to prompt and render in indicators table |

### WDM

| Monitor | Item | Type | Notes |
|---------|------|------|-------|
| WDM | wdm_stress_index | Schema | Platform-level composite stress index; render as headline KPI |
| WDM | severity score version history | Schema | Track version of severity scoring methodology; render as metadata |
| WDM | monthly_trend block | Schema | Month-over-month trend summary; render as trend section on report |
| WDM | mimicry_chain_velocity field | Schema | Rate metric for mimicry chain propagation; render on relevant signal cards |

**Done when:** All new fields are defined in cron prompts, appear in next cron output, and are rendered in HTML for their monitor. No prompt change is considered done until the field appears in a live cron output.

---

## SPRINT 5 — Structural & Architectural (High Effort)
**Goal:** Define and build the major architectural capabilities that require design sessions before implementation. Do not begin without a design session for each item.

*Items listed without full specification — each needs a design session to define scope, data model, and rendering approach before building.*

| Item | Area | Notes |
|------|------|-------|
| Cross-monitor synthesis layer | Architecture | Automated cross-monitor signal correlation and composite risk output |
| Compossible deep integration | Architecture | Surface asym-intel signals in Compossible content programmatically |
| Alert / threshold notification system | Architecture | User-configurable alerts when monitor scores cross thresholds |
| Historical archive and trend visualisation | Architecture | Store and query historical cron outputs; trend charts over time |
| Mobile-first audit and redesign | UX | All Sprint 2A visual enhancements not audited on mobile; systematic audit + fixes |
| Monitor comparison view | UX | Side-by-side or summary view across all 7 monitors |
| Search and signal discovery | UX | Cross-monitor search interface |
| API layer for programmatic access | Architecture | Public or authenticated API over monitor data |
| Analyst commentary layer | Content | Human-authored commentary integrated with cron outputs |
| Automated QA / validation pipeline | Infrastructure | Post-cron validation runs to catch schema drift and rendering failures |

---

## ONGOING / EVERGREEN

| Item | Type | Date / Trigger |
|------|------|----------------|
| GSC domain property verification | User action | Required before sitemap submission — do now |
| Sitemap submission (both properties) | SEO | After GSC verification |
| SCEM cron verify — FE-019 compliance | QA | Sun 5 Apr 18:30 UTC (cron a67a9739) |
| WDM cron verify — FE-019 compliance | QA | Mon 6 Apr 06:30 UTC (cron 10ddf5f0) |
| WDM Category B sections — first render verify | QA | Mon 6 Apr — check report.html after cron |
| ESA defence spending bar — verify after cron | QA | Wed 8 Apr |
| FCW campaign Gantt — verify after cron | QA | Thu 9 Apr (start_date data arrives) |
| Housekeeping cron — first run with 20-check validation | QA | Mon 8 Apr 08:00 UTC |
| Mobile audit — all Sprint 2A visual enhancements | UX | Before Sprint 5 structural work |

---

## Parking Lot

Items that are genuinely deferred pending design decisions. Do not schedule until a dedicated design session has produced a written spec.

| Item | Blocker |
|------|---------|
| Cross-monitor synthesis layer | Need to define the data model for cross-monitor correlation: what signals correlate, how composite risk is computed, what the output format is |
| Alert / threshold notification system | Delivery mechanism (email, webhook, in-app) and threshold configuration UX need to be designed |
| Historical archive and trend visualisation | Storage strategy for cron outputs (flat file vs. database) needs a decision; query interface design needed |
| API layer | Authentication model, rate limiting, endpoint design, versioning strategy |
| Analyst commentary layer | Editorial workflow, how commentary relates to cron output (overrides? annotations?), CMS requirements |
| Automated QA / validation pipeline | Define what "valid" means per monitor: schema completeness, field presence, value range checks — write the spec before building |
| Monitor comparison view | Layout design needed — which fields are comparable across monitors, what the summary surface looks like |

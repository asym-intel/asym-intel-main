# Asymmetric Intelligence — Platform Roadmap
**Last updated:** 2026-04-12 (Sprint 3 page-by-page audit + fixes)  
**Maintained by:** Computer sessions — update this file at every wrap.  
**Canonical location:** `docs/ROADMAP.md` (asym-intel-main)

---

> **Canonical planning documents:**
> - `docs/ux/ASYM-INTEL-SITE-REBUILD-SPEC-JOURNEY-FIRST.md` — **canonical Sprint 1+ design spec** (journey-first, user-facing, signed-off)
> - `asym-intel-internal/editorial-strategy.md` — audience strategy, epistemic hierarchy, tier architecture
> - `asym-intel-internal/development-plan.md` — master build sequence, phase gates, annual report calendar
> - `asym-intel-internal/docs/ga-advisory-agent-roles.md` — role architecture, GA automation roadmap, advisory agent catalogue
>
> **Implementation discipline (from journey-first spec):**
> **Computer builds HTML/CSS/JS directly** (updated 2026-04-12). Peter builds mockups only when the end state
> is genuinely unclear (e.g. new homepage layout, design-gated items). In all other cases Computer implements;
> Peter reviews committed output and corrects.

## How to read this file

- ✅ Done — shipped and live
- 🔄 In flight — data-gated or waiting on cron output this week
- 📋 Queued — ready to build, no blockers
- 🔒 Schema-gated — blocked until cron prompt updated and next output arrives
- 🎨 Design-gated — needs a design session before any build work begins
- 📅 Scheduled — fires automatically, no session needed

Items are ordered within each sprint by priority. Estimates are session time including staging, testing, and merge.

---

## COMPLETED

### Sprint 1 ✅
Rendering bugs across all monitors. ESA institutional items. AGM undefined bugs. ERM/FCW/GMM rendering fixes. PRs #18–#22.

### Sprint 2A ✅
Nine visual/chart items: WDM world map, GMM prior-week bars, ERM tipping bars, AGM radar + diverging bar, ESA benchmark bar, SCEM comparison bar.

### Infrastructure Sprint ✅ (1 April 2026)
Sitemap correctness, SEO fixes, agent identity framework, governance documents, signal link UX standardisation across all monitors. Full item list in `docs/audits/sprint-programme.md`.

### Sprint 3A ✅ (2 April 2026)
FCW 12 campaigns + Chatter page, GMM Fed Funds KPI + Sentiment Overlay, WDM weekly_brief on dashboard, SCEM roster_watch section.

### Sprint 3B ✅ (2 April 2026)
Cross-monitor flags widget on all 6 dashboards (GMM/ESA/AGM/ERM/WDM/FCW), AGM nav links (Digest/Methodology/Search), ERM reverse_cascade_check in cascade cells, ESA duplicate radar removed → links to persistent.html, ESA Lagrange radar enlarged +40% on persistent page, GMM score-history sidebar anchor fixed.

### Housekeeping / Platform ✅ (2 April 2026)
- All 9 crons migrated to slim repo pointers
- docs/crons/ registry created
- Staging divergence guard live (aec126c5)
- 7/7 annual calibration files created and wired
- FCW + GMM + SCEM GitHub Actions pipelines live (Collector/Weekly/Reasoner layers)
- anti-patterns.json v1.1 (FE-001 through FE-025)
- `AsymRenderer.sourceLabel(url)` — domain-aware source link labels in renderer.js
- Nav brand " Monitor" stripped from all 59 monitor HTML pages
- EGHTM → ESA rename across 21 files (both repos)
- ESA dashboard: Lagrange radar section removed; cross-monitor FE-022 scope bug fixed


### GA Automation Sprint ✅ (9 April 2026)
- Chatters fixed to daily (were weekly — cron expressions had day-of-week constraints)
- WDM reasoner reconciled (was documented as PAUSED, actually live)
- Pipeline-status.json + dashboard auto-update workflow (3x daily, zero credits)
- Preflight checks on every push (tools/preflight.py as CI)
- Pipeline failure alerts (auto-create GitHub issue on workflow failure)
- Staging divergence guard (replaces Computer cron — zero credits)
- Site inventory auto-regeneration (weekly, zero credits)
- Session Role Triggers in COMPUTER.md v3.25 (platform-dev, pipeline-ops, analyst-debug bootloaders)
- tools/preflight.py (9 check groups, 290 checks)
- notes-for-computer.md pruned (135KB → 5KB, archive preserved)


---

## CREDIT-SAVING PRIORITY

When planning session work, prioritise items that reduce recurring credit spend.
Target: Computer credits for manual sessions only — all automation on GA.

**Completed 9 April 2026:**
- ✅ Analyst crons → GA publisher migration (was ~700 credits/week)
- ✅ Boot context pre-caching (compile-boot-context.yml)
- ✅ Housekeeping cron paused (was ~400 credits/month)
- ✅ Push retry logic on all 14 collector/chatter workflows

The automated pipeline now runs end-to-end on GitHub Actions with zero Computer credits.
Only manual development sessions consume credits.

---

## IMMEDIATE — Schema Enrichment Sprint (April 2026)

**Sprint reorder decision** (11 April 2026): Schema enrichment moved BEFORE Site Rebuild.
Rationale: templates are built from data config — enrich data first so HTML is built to real fields from day one. Avoids double-handling when schema fields arrive after UI is built.

**New sprint order:**
1. Schema Enrichment (was Sprint 4) ← **NOW**
2. Site Rebuild Sprint 1 — Shared Foundations + Homepage (was Sprint 1)
3. Data-Gated Renders (Sprint 2B) + Sprint 3 Remainder
4. Structural & Architectural (Sprint 5)

**Schema Sprint v2 COMPLETE** (12 April 2026). All 7 synthesiser prompts expanded. All monitors at 85%+ coverage.
Coverage by monitor (lowest first — priority order for enrichment):
- ~~SCEM 60%~~ **SCEM 85% ✓** → ~~ESA 65%~~ **ESA ~95% ✓** → ~~ERM 67%~~ **ERM ~90% ✓** → ~~GMM 75%~~ **GMM ~90% ✓** → ~~FCW 85%~~ **FCW ~90% ✓** → ~~WDM 92%~~ **WDM ~95% ✓** → ~~AIM 95%~~ **AIM ~98% ✓**

**SCEM schema sprint complete** (12 April 2026):
- JSON enforcement preamble added to all 7 synthesiser prompts (class fix)
- Synthesiser re-run: 14/14 target sections produced as valid JSON
- Smart merge: 9 new sections added to report-latest, analyst-authored data preserved (10 conflicts)
- `file_paths` registry added to schema-registry.json for all 7 monitors
- Dashboard verified: all 10 sections rendering correctly
- Persistent-state v2 schema design PARKED — needs separate design session
- HTML renders rewired: all 3 SCEM pages (dashboard, report, persistent) use AsymSections shared library
- Hugo issues noted: (1) Missing sitemap template warning, (2) Node.js 20 deprecation in GA actions (checkout@v4, upload-artifact@v4, peaceiris/actions-hugo@v3) — need Node 24 migration before 2 June 2026

**ESA schema sprint complete** (12 April 2026):
- Synthesiser prompt v2.2: enriched domain_tracker with 6 ECFR autonomy domains as structured objects
- Publisher field_map updated: signal_key + 10 new field mappings
- Schema-registry: 9→19 fields registered
- Report-latest smart merge: 8→15 fields (7 new sections added)
- Renderer.js: 7 new ESA AsymSections functions
- Generic `renderRadarChart` added to shared library — reusable by any monitor
- Lagrange Scorecard: restored radar+bars layout, fixed label clipping (aspect-ratio 1:1 solution)
- All 3 pages rewired to AsymSections shared library
- 3 report sections (election_threats, defence_spending, defence_programmes) awaiting data from next synthesis run
- E2E pipeline triggered and verified green

**ERM schema sprint complete** (12 April 2026):
- Synthesiser prompt already at v2.0 quality — incorporates Copernicus 2025 + planetary boundaries addendum
- Publisher field_map: cleared legacy m0x mappings → pass-through synthesis field names directly
- `cross_monitor_candidates` removed from publisher skip_keys (class fix — benefits all monitors)
- Schema-registry: 17 active fields, 8 legacy m0x fields deprecated
- Renderer.js: 9 new ERM AsymSections functions (renderPolicyLawCompliance, renderICJTracker, renderLossDamageTracker, renderAttributionGapCases, renderReverseCascadeCheck, renderRegionalCoverage, renderExtremeEventsLog, renderClimateSecurityNexus, renderPlanetaryStatusSnapshot)
- All 3 pages rewired: dashboard (+11 sections), report (+12), persistent (+4)
- Field name fallbacks: pages handle both legacy (m00_the_signal, m02_planetary_boundaries, m03_threat_multiplier) and new names
- E2E pipeline triggered — collector complete, cascade in progress

**GMM schema sprint complete** (12 April 2026):
- Synthesiser prompt already at v1.0 quality — no changes needed
- Schema-registry: 19→21 fields (key_judgments, intelligence_highlights added)
- Renderer.js: 8 new GMM/cross-monitor AsymSections functions (renderKeyJudgments, renderIntelligenceHighlights, renderIndicatorGrid, renderRiskRadarMini, renderScenarioPaths, renderPolicyWatch, renderRegionalBreakdown, renderHistoricalContext)
- Dashboard: 8 new sections wired with sidebar nav
- Report: 6 new modules (key_judgments, intel_highlights, indicator_grid, risk_radar_mini, scenario_paths, policy_watch)
- E2E pipeline triggered and verified

**FCW schema sprint complete** (12 April 2026):
- Synthesiser prompt already at v1.0 quality — no changes needed
- Schema-registry: 10→12 fields (key_judgments, intelligence_highlights added; cognitive_warfare, platform_responses, weekly_brief made explicit)
- Dashboard: 3 new sections (key_judgments, intelligence_highlights, cognitive_warfare) with sidebar nav; esc→escHtml bug fixed
- Report: 2 new sections (key_judgments, intelligence_highlights) wired with AsymSections fallback
- Persistent.html: no changes needed
- Pipeline dispatched: fcw-synthesiser + fimi-cognitive-warfare-publisher

**WDM schema sprint complete** (12 April 2026):
- Synthesiser prompt already at v2 (288 lines) — comprehensive, no changes needed
- Reasoner prompt v1.0 confirmed WDM-specific — severity reviews, mimicry detection, watchlist thresholds, cross-monitor escalation
- V-Dem 2026 addendum (414 lines) confirmed integrated
- Publisher: field_map updated (`legislative_watch_entries` → `legislative_watch`), signal pass-through added for monitors with direct `signal` object in synthesis
- Schema-registry: 14→15 fields (+intelligence_highlights cross-monitor alias, key_judgments enriched with sub_fields)
- Dashboard: 5 new sections (key_judgments, electoral_calendar, mimicry_chains, legislative_watch, friction_notes) + sidebar nav; duplicate escHtml removed
- Report: key_judgments section added; v2 field name fallbacks for electoral_calendar_watch, mimicry_chain_update, legislative_watch_entries; mimicry chain render handles both v2 and legacy shapes
- Persistent.html: no changes needed
- Pipeline dispatched: wdm-synthesiser + democratic-integrity-publisher
- Current synthesis-latest.json is pre-v2 (only 8 of 13 target fields). Next synthesis run should produce all fields including institutional_integrity_flags, mimicry_chain_update, legislative_watch_entries, friction_notes

**AIM schema sprint complete** (12 April 2026):
- Synthesiser prompt already at v2.0 (500 lines) — comprehensive 16-module schema with all Sprint 4 fields. No changes needed
- Reasoner prompt v1.0 (148 lines) — AIM-specific capability governance reasoning (tier reviews, regulatory milestones, risk pattern detection, cross-monitor escalation, contested findings)
- EU AI Act addendum (220 lines) confirmed integrated in synthesiser
- Schema-registry: 24→27 fields (+country_grid, +country_grid_watch, +key_judgments; synthesis_gaps cleared)
- Dashboard: 4 new Sprint 4 sections (key_judgments, jurisdiction_risk_matrix, lab_posture_scorecard, governance_health_composite) + render functions + sidebar links
- Report: same 4 Sprint 4 sections with inline render logic + sidebar links
- Persistent.html: no changes needed
- Pipeline dispatched: agm-synthesiser
- All Sprint 4 data already present in report-latest.json — renders wired to existing data
- **ALL 7 SCHEMA SPRINTS COMPLETE** — SCEM ✓ ESA ✓ ERM ✓ GMM ✓ FCW ✓ WDM ✓ AIM ✓

**Schema sprint lesson (standing):** Each sprint must update THREE files: synthesiser prompt, report-latest.json, AND persistent-state.json. The publisher does not auto-extract persistent fields from synthesis. Context limits: 80K context, 20K weekly research, 16K max_tokens, 300s timeout. Smart merge strategy: only overwrite broken modules, preserve existing rich data.

---

## ✅ Site Rebuild Sprint 1 COMPLETE (2026-04-12)

Canonical spec: `docs/ux/ASYM-INTEL-SITE-REBUILD-SPEC-JOURNEY-FIRST.md`

**What shipped:**
- SL-01 to SL-09: Shared library foundations (triage strip, confidence badges, signal panel, cross-monitor flags, colour tokens, validators)
- HP-01 + HP-02: Homepage (monitor strip, three-zone layout, featured article, report-card grid, value statement)
- WDM dashboard: thin orchestrator pattern pilot (962 → 581 lines)
- BEM mismatch fixed in `.ov-glance-box` (all 7 overview pages)
- base.css: 2200 → 2833 lines total across all CSS centralisation sprints

## ✅ Site Rebuild Sprint 2 COMPLETE (2026-04-12)

**What shipped:**
- `AsymSections.renderTriageStrip` wired to all 6 remaining dashboards (GMM, ESA, FCW, AGM, ERM, SCEM)
- 12 commits (6 static/ + 6 docs/)
- renderTriageStrip needed zero changes — fully generic; config builders handle per-monitor field mapping
- GMM exception: kept `section-signal` (relabelled "Signal Detail") for rich extra fields per D9 efficiency decision
- All 7 monitors published fresh baseline 12 Apr 07:45 UTC

## 🔄 Site Rebuild Sprint 3: Homepage + Page-by-Page Monitor Check

**Status:** In progress (12 April 2026)

### Completed
- ✅ Homepage audit — screenshot + issue identification
- ✅ All 7 monitor pages audited (overview, dashboard, report) — class-level issues catalogued
- ✅ 404 check — cross-monitor.html was 404 on all 7 monitors (only 404s found site-wide)
- ✅ cross-monitor.html built and deployed to all 7 monitors (14 files, commit `328c8683`)
- ✅ AGM date format fix — was only monitor using raw ISO date (commit `1e231a02`)
- ✅ WDM report.html crash fixed — root cause: `mimicry_chain_update.active_chains` is integer, not array; also fixed flat-array heatmap binning + field name mismatches (commit `a4a38dd5`)
- ✅ renderer.js stubs — AsymRenderer.sourceLink/sourceLabel/flag stubs prevent TypeError class-wide (commit `683a638a`)
- ✅ Site subagent rule written to COMPUTER-core.md (commit `b5854eda`)

### Remaining known issues
- Homepage chatter widget shows only SCEM items (not aggregating across monitors)
- WDM CMF linkbacks show slugs instead of display names
- WDM heatmap Recovery tab shows (0) — data has no `health_status: "Recovery"` countries

---

## IN FLIGHT THIS WEEK (automated — no session needed)

| Item | Schedule | Notes |
|------|----------|---------|
| All 7 publisher workflows | Weekly per monitor | First full cycle: WDM Mon → SCEM Sun. Zero credits. |
| All 7 chatters | Daily 06:00-06:30 UTC | Fixed to daily (was weekly) |
| All 7 collectors | Daily 07:00-07:30 UTC | Staggered, push retry logic |
| Weekly research + reasoner + synthesiser | Per-monitor weekly cascade | Fires automatically |

---

## SPECIALIST SESSIONS — First Benchmark Runs (in order)

| Session | Priority | Goal | Prompt |
|---------|----------|------|--------|
| Platform Security Expert | ✅ Complete | docs/security/ created, 3 HIGH: branch protection, SRI hashes, integrity manifest | `docs/prompts/platform-security-expert.md` |
| SEO & Discoverability Expert | ✅ Complete | docs/SEO.md + AI search baseline · 0/3 benchmark queries cited · robots.txt fixed | `docs/prompts/seo-discoverability-expert.md` |
| Platform Experience Designer | 🟡 Run third | Peter's reader observations + knowhow dump + colour-registry.md (must precede all implementation) | `docs/prompts/platform-experience-designer.md` |
| Intelligence Surface Analyst | 🟢 After PED | Five-audience gap test, asymmetric signal audit, recovery parity audit | `docs/prompts/reader-experience-analyst.md` |

**Benchmark prompts:** ready-to-paste prompts for all four sessions are in HANDOFF.md next-session notes.

---


## SECURITY + SEO BACKLOG — From First Benchmark Sessions (3 April 2026)

### Security — requires Peter's action (cannot be done autonomously)

| Item | Severity | Owner | Notes |
|------|----------|-------|-------|
| Branch protection on main | 🔴 HIGH | Peter | Require CI to pass, include administrators — GitHub repo settings → Branches |
| HSTS max-age 31536000 | 🟡 MEDIUM | Peter | Cloudflare Transform Rule — currently 15552000 |
| X-Frame-Options + CSP + Referrer-Policy headers | 🟡 MEDIUM | Peter | Cloudflare Transform Rules — spec in platform-security-expert.md |

### Security — requires Platform Developer + Computer session

| Item | Severity | Est. | Notes |
|------|----------|------|-------|
| SRI hashes on all Chart.js CDN tags | ✅ Done | — | PR #29 merged 3 Apr · all 7 dashboards · SEC-010 resolved |
| integrity-manifest.json — first manifest live | ✅ Done | — | static/monitors/shared/integrity-manifest.json committed · draft workflow in docs/security/drafts/ · Peter approval needed to move to .github/workflows/ |
| GA workflow failure notifications | 🟡 MEDIUM | 30 min | All 14 Collector/Research/Reasoner workflows — add `if: failure()` step |

### SEO — requires Platform Developer session

| Item | Severity | Est. | Notes |
|------|----------|------|-------|
| JSON-LD structured data — full suite | 🔴 HIGH | 2 hrs | Dataset + NewsArticle + FAQPage + BreadcrumbList in layouts/partials/head.html + layouts/_default/single.html · Full spec: docs/seo/ai-search-audit-2026-Q2.md Section 5 |
| WDM meta description fix | ✅ Done | — | SEO-010 resolved · "democratic backsliding" + V-Dem + Freedom House added |
| Methodology page lastmod dates | ✅ Done | — | All 7 methodology pages corrected to actual launch dates |
| 4 utility pages missing lastmod | 🟡 MEDIUM | 15 min | /about/, /search/, /subscribe/, /tags/ |
| "Cite this" element on brief pages | 🟡 MEDIUM | 30 min | layouts/_default/single.html — citation block spec in docs/SEO.md |
| 7 monitor-specific OG images | 🟡 MEDIUM | Design-gated 🎨 | All monitors share fallback image — PED session first |

### SEO — requires Peter's decision

| Item | Notes |
|------|-------|
| Complete GSC property verification | https://search.google.com/search-console/ |
| Archive indexing policy for first 12 months | Recommend: index all, review at 12-month mark |
| Static dashboard pages in sitemap? | Supplemental sitemap needed — Peter to decide |
| GMM title "Macro Monitor" → "Global Macro Risk Monitor"? | Competitor domain global-macro-monitor.com appears in AI search |


## PED SPRINT 1 — ✅ Complete (2026-04-03 session)

| Item | Status | Notes |
|------|--------|-------|
| docs/ux/decisions.md — full population | ✅ Done | 8 principles, 4-monitor findings, 8 open questions for Peter |
| docs/ux/colour-registry.md — created | ✅ Done | Session 1 prerequisite — severity system, accents, 3 collision warnings |
| FCW signal panel contrast fix | ✅ Staged PR #31 | rgba(255,255,255,0.82) secondary text — awaiting Peter sign-off |
| SCEM nav gaps (Conflict Overview + Friction Flags) | ✅ Staged PR #31 | Awaiting Peter sign-off |
| GMM nav alignment (4 labels) | ✅ Staged PR #31 | Awaiting Peter sign-off |
| WDM live audit | ✅ Done | Findings in decisions.md — no implementation needed |
| Homepage redundant Read→ CTAs removed | ✅ Done | Commits 48e64d4, 9e9673a — live |

## PED SPRINT 2 — Queued

| Item | Priority | Est. | Notes |
|------|----------|------|-------|
| AGM + ERM dashboard audit | 🔴 HIGH | 30 min | Last 2 monitors not yet reviewed — complete colour-registry coverage |
| ESA mobile viewport test (#section-delta font) | 🟡 MEDIUM | 15 min | Peter observed small font — unconfirmed at desktop; needs 375px test |
| Signal panel contrast fix — GMM + SCEM | 🔴 HIGH | 30 min | Extend Principle 5 fix to GMM "One number to watch" + SCEM secondary text |
| SCEM F-flag matrix — integrated labels | 🟡 MEDIUM | 45 min | Show "F2 · False-flag risk" inline in tile, not just legend below |
| Severity badge font size floor | 🟡 MEDIUM | 15 min | Raise from 0.6rem to --text-xs across base.css |
| Peter decisions needed before sprint | ⚠️ BLOCKER | — | Q4 (confidence badges), Q6 (hero image), Q7 (chatter feed), Q8 (SCEM/critical collision) |

## SPRINT 3 REMAINDER

### Doable now — no blockers

| Monitor | Item | Est. | Notes |
|---------|------|------|-------|
| ALL | Migrate inline `Source →` to `AsymRenderer.sourceLabel()` | 45 min | Low priority — migrate as dashboards are touched |
| GMM | Tail risk note tooltips | 20 min | tail_risk_note text in schema; tooltip component |
| GMM | Scenario cards | 30 min | scenarios array in schema; card component on dashboard |
| AGM | M06 arXiv stub section | 20 min | Schema stub present; HTML section in report.html |
| AGM | Risk vector heat grid | 30 min | Data likely present; new grid component |

### Schema-gated — blocked until cron output updated

| Monitor | Item | Blocker |
|---------|------|---------|
| WDM | silent_erosion section | 🔒 Field not yet in cron output — parked for design session |
| WDM | signal.history trend indicator | ✅ Added to cron Step 4 — 6 Apr 2026 |
| WDM | severity_sub field render | ✅ Added to cron Step 4 — 6 Apr 2026 |
| SCEM | GEI CONTESTED disclaimer | 🔒 Parked for design session — band graduation threshold needs decision |
| SCEM | Indicator deviation chart fix | ✅ Deviation calculation added to SCEM cron Step 2 — 6 Apr 2026 |

---

## SPRINT 2B — Data-Gated Renders

Session work needed after crons confirm data is present this week.

| Monitor | Item | Est. | Trigger |
|---------|------|------|---------|
| WDM | Category B sections render verify | 🔄 20 min | Mon 6 Apr |
| ESA | Defence spending bar chart | 🔄 30 min | Wed 8 Apr |
| FCW | Campaign timeline Gantt | 🔄 45 min | Thu 9 Apr |

---

## SPRINT 4 (PROMOTED) — Schema Sprint — Detailed Item Backlog

Each item = cron prompt change + wait for next output + HTML render.  
Do all prompt + HTML work for one monitor per session.

### GMM — 1 session ~2–2.5 hrs
| Item | Notes |
|------|-------|
| credit_spreads field | Add to prompt; render spread chart on dashboard |
| VIX term structure | Add array to prompt; render curve chart |
| Tariff quantification | Structured tariff impact field; render as annotated figure |
| Scenario-conditional impacts | Extend scenarios object; render in scenario cards |

### FCW — 1 session ~2 hrs
| Item | Notes |
|------|-------|
| Narratives registry | New top-level object; render as table |
| effectiveness per campaign | Scoring badge on campaign card |
| campaign start_date enforcement | Required for Gantt (Sprint 2B) |
| cognitive_warfare persistence field | Duration score per campaign |

### ESA — 1 session ~2–2.5 hrs
| Item | Notes |
|------|-------|
| defence_spending array (structured) | Structured spend-by-country; Sprint 2B bar chart |
| scorecard structured fields | Replace narrative with machine-readable fields; grid render |
| us_dependency field | Quantified score per actor; actor cards |
| defence_programmes tracker | Structured tracker per programme; status table |

### AGM — 1 session ~2 hrs
| Item | Notes |
|------|-------|
| Governance health composite | Composite score; headline KPI |
| Jurisdiction risk matrix | Structured matrix; heat grid |
| Lab posture scorecard | Structured lab-by-lab fields; comparison table |
| capability_profile object | Structured capability per actor; actor cards |

### ERM — 1 session ~1.5 hrs
| Item | Notes |
|------|-------|
| Planetary boundary proximity scores | Numeric score per boundary; progress bars |
| Tipping system standardisation | Standardise tipping_system object |
| M05 regulatory pipeline | Structured pipeline array; status table |

### SCEM — 1 session ~2 hrs
| Item | Notes |
|------|-------|
| escalation_velocity field | Rate-of-change metric; trend indicator |
| esc_score composite | Sub-component breakdown |
| PROVISIONAL band tier | Flag sparse data; render disclaimer |
| I7 proxy warfare indicator | New I-series indicator |

### WDM — 1 session ~2 hrs
| Item | Notes |
|------|-------|
| wdm_stress_index | Platform-level composite; headline KPI |
| severity score version history | Track methodology version; metadata render |
| monthly_trend block | Month-over-month summary section |
| mimicry_chain_velocity field | Rate metric; signal card render |

**Sprint 4 total: ~14 hrs across 7 sessions**

---

## PIPELINE OUTSOURCING — WDM / ESA / AGM / ERM

Run outsourcing review (COMPUTER.md) before each build. FCW/GMM/SCEM already live.  
Sequential — each validates before next begins.

| Monitor | Est. | Trigger |
|---------|------|---------|
| WDM pipeline | ~2 hrs | After FCW Thu 9 Apr validates |
| ESA pipeline | ~2 hrs | After WDM validates |
| AGM pipeline | ~2 hrs | After ESA validates |
| ERM pipeline | ~2 hrs | After AGM validates |

**Pipeline total: ~8 hrs across 4 sessions**

---

## SPRINT 5 — Structural & Architectural

**Each item requires a design session before any build work.**  
Do not begin without a written spec produced in a design session.

| Item | Design | Build est. | Notes |
|------|--------|-----------|-------|
| Cross-monitor synthesis layer | 🎨 1 hr | 6–8 hrs | Automated signal correlation + composite risk output |
| Historical archive + trend charts | 🎨 1 hr | 4–6 hrs | Storage strategy decision needed first |
| Alert / threshold notification system | 🎨 1 hr | 4–5 hrs | Delivery mechanism + threshold config UX |
| Mobile-first audit + redesign | 🎨 0.5 hr | 3–4 hrs | All Sprint 2A visuals unaudited on mobile |
| Monitor comparison view | 🎨 1 hr | 3–4 hrs | Side-by-side summary across monitors |
| Search and signal discovery | 🎨 1 hr | 4–5 hrs | Cross-monitor search interface |
| API layer | 🎨 1 hr | 6–8 hrs | Auth model, rate limiting, endpoints, versioning |
| Compossible deep integration | 🎨 1 hr | 3–4 hrs | Surface asym-intel signals in Compossible |
| Analyst commentary layer | 🎨 1 hr | 4–5 hrs | Editorial workflow + CMS requirements |
| Automated QA / validation pipeline | 🎨 1 hr | 4–5 hrs | Define "valid" per monitor; write spec first |

**Sprint 5 total: ~10 hrs design + ~47–54 hrs build**

---

## ONGOING / EVERGREEN

| Item | Type | Status |
|------|------|--------|
| GSC domain property verification (asym-intel.info) | User action | ⏳ Pending |
| Sitemap submission (both properties) | SEO | ⏳ After GSC verification |
| Cloudflare: Bot Fight Mode + Page Shield | User action | ⏳ Pending |
| Fortiguard recategorisation (News and Media / Research) | User action | ⏳ Pending |
| Housekeeping cron — Monday 08:00 UTC | 📅 Automated | Runs weekly |
| Staging divergence guard — daily ~18:00 UTC | 📅 Automated | Runs daily |
| Annual calibration reminder — 28 March | 📅 Automated | Next: Mar 2027 |
| **Platform Security Expert** session | On-demand + quarterly | Prompt: `docs/prompts/platform-security-expert.md` |
| **SEO & Discoverability Expert** session | On-demand + monthly GSC audit | Prompt: `docs/prompts/seo-discoverability-expert.md` |
| **Platform Auditor** session | Quarterly (Q1/Q2/Q3/Q4) | Prompt: `docs/prompts/platform-auditor.md` |

---

## FIRST-RUN SETUP (create on first specialist session)

The following `docs/` subdirectories do not yet exist. Each specialist role creates
them on its first session. Do not create them speculatively — let the role create them
with the correct stub files.

| Directory | Created by | First session trigger |
|-----------|------------|----------------------|
| `docs/security/` | Platform Security Expert | First security audit session |
| `docs/seo/` | SEO & Discoverability Expert | First SEO audit session |
| `docs/audits/` | Platform Auditor | First Q1 calibration session |

---

## PARKING LOT

Genuinely deferred — needs a design session before scheduling.

| Item | Blocker |
|------|---------| 
| ~~Boot context pre-caching~~ | ✅ Done 9 Apr 2026 — compile-boot-context.yml live |
| Housekeeping cron decommission | Once GA workflows confirm working (failure alerts, staging guard, site-inventory, HANDOFF, pipeline-status), Housekeeping has almost nothing left. ~400 credits/month. |
| Structured state YAML | Replace notes-for-computer.md with ops/agent-state.yml (standing decisions, open actions, recent notes). Machine-parseable. Low urgency — pruning solved immediate problem. |
| GA orchestrator (42 workflows → 6) | Parameterised workflows accepting monitor slug. Right idea, stabilise current pipeline first. |
| COMPUTER.md slim (566 → ~350 lines) | Subagent section duplicates skill; efficiency table removed; consolidation pass needed. Target: reduce per-session Step 0 token cost by ~30%. |

| Item | Blocker |
|------|---------|
| Cross-monitor synthesis layer | Data model for correlation; composite risk output format |
| Alert / threshold notification system | Delivery mechanism (email, webhook, in-app); threshold UX |
| Historical archive + trend visualisation | Storage strategy (flat file vs. database); query interface |
| API layer | Auth model, rate limiting, endpoint design, versioning |
| Analyst commentary layer | Editorial workflow; how commentary relates to cron output |
| Automated QA / validation pipeline | What "valid" means per monitor — spec needed before building |
| Monitor comparison view | Which fields are comparable; layout design |
| Publisher persistent-state extraction | `update_persistent_state()` only handles campaigns (FCW). Needs extraction logic for risk vectors, lab postures, CMFs, concentration index, EU AI Act tracker, AISI pipeline per monitor. Without this, Living Knowledge pages go stale after every issue. Discovered during AIM schema sprint 10 Apr 2026. |
| eghtm-full.md filename rename | Low priority — content updated; filename still eghtm-full.md in internal repo |
| tools/generate-sprint1-batch.py | Retired 7 Apr 2026 — sonar-pro component generation produces near-identical variants with no visual feedback loop. Sprint 1 components built directly in-session instead. File can be deleted once Sprint 1 is complete. |
| ~~Analyst crons → GA migration~~ | ✅ Done 9 Apr 2026 — publisher.py + 7 GA workflows live, all schedules enabled |
| ~~HANDOFF.md full automation~~ | ✅ Done — generate-handoff.yml live, daily + Monday |
| Hugo brief existence check (GA) | After analyst cron publishes, verify .md file exists with correct FE-019 filename. |
| JSON schema deep validation (GA) | Beyond validate-blueprint.py: required fields per monitor, cross-reference dashboard expectations. |

---

## Maintenance notes

**To update this file:** Edit `docs/ROADMAP.md` directly on main at every wrap.  
Mark items ✅ when merged. Move to COMPLETED section. Add new items as they arise.  
Do not delete items — mark them ✅ or move to Parking Lot with a reason.

---

## Site Rebuild — Document Index

### Canonical (active)

| File | Role | Status |
|---|---|---|
| `docs/ux/ASYM-INTEL-SITE-REBUILD-SPEC-JOURNEY-FIRST.md` | **Master design spec** — journey-first, cross-monitor rules, scope boundaries, implementation discipline | Canonical |
| `docs/ux/colour-registry.md` | Severity tokens, monitor accents, collision rules | Canonical |
| `docs/ux/badge-spec.md` | Confidence badge CSS spec (signed off) | Canonical |
| `docs/ux/homepage-copy.md` | Value statement + routing cues (signed off) | Canonical |
| `docs/ux/section-naming-registry.md` | Canonical section names, Tier 1/2/3 classification, layout templates | Canonical |
| `docs/ux/visuals-handover-all-monitors.md` | Chart types, monitor colour assignments, visual requirements | Canonical |
| `docs/ux/decisions.md` | Design decision log with rationale | Living doc |

### Superseded (retained as reference)

| File | Superseded by | Retained for |
|---|---|---|
| `docs/ux/site-rebuild-spec.md` | Journey-first spec | Sprint IDs (SL-*, WDM-*, etc.) and time estimates |
| `docs/ux/site-rebuild-sprints.md` | Journey-first spec | Sprint sequencing reference |
| `docs/ux/homepage-ia-v4.md` | Journey-first spec §1 | Historical working note |
| `docs/ux/monitor-overview-brief.md` | Journey-first spec §2 | Historical working note |

### Exploratory (not implementation-ready)

| File | Notes |
|---|---|
| `docs/ux/mockups/homepage-map-prototype-v2-3.html` | Three-zone layout idea with visual tiles |
| `docs/ux/mockups/world-map-page-mockup-v2-2.html` | Dedicated /map/ page concept |

### LLM briefing

| File | Notes |
|---|---|
| `docs/prompts/sprint1-llm-briefing.md` | 230KB compiled briefing (specs + full code). Note: Section 2A references old site-rebuild-spec.md — use journey-first spec instead for design intent. |

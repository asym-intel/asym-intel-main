# Asymmetric Intelligence — Platform Roadmap
**Last updated:** 2026-04-03 (wrap) (wrap)  
**Maintained by:** Computer sessions — update this file at every wrap.  
**Canonical location:** `docs/ROADMAP.md` (asym-intel-main)

---

> **Canonical editorial and development planning documents:**
> - `asym-intel-internal/editorial-strategy.md` — audience strategy, epistemic hierarchy, tier architecture
> - `asym-intel-internal/development-plan.md` — master build sequence, phase gates, annual report calendar
> These supersede the sprint planning sections below for strategic direction.

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

---

## IMMEDIATE — Next Session (blockers, fix before content work)

| Item | Priority | Owner | Notes |
|------|----------|-------|-------|
| FCW dashboard.html diverged | ✅ Done | — | Legacy 140k replaced with modern 37k shared-library version on main (3 Apr) |
| FCW-DAILY-FEEDER-PROMPT-v4.md missing | ✅ Done | — | Both stub files corrected — GA architecture documented, no cron was broken |
| docs/monitors/_shared/ stale artefact | 🟡 HIGH | Platform Developer | Older CSS/JS than docs/monitors/shared/ — nothing references it. Verify and delete. |
| housekeeping-cron-prompt.md in docs/ only | 🟡 HIGH | Computer | Exists in docs/monitors/ but not static/monitors/ — source/output broken. Add to static/. |

---

## IN FLIGHT THIS WEEK (automated — no session needed)

| Item | Trigger | Action if OK |
|------|---------|--------------|
| GMM Collector first run | 📅 Fri 3 Apr 06:00 UTC | Check pipeline/monitors/macro-monitor/daily/ |
| SCEM verify cron (a67a9739) | 📅 Sun 5 Apr 18:30 UTC | Confirms FE-019 compliance on briefs |
| WDM verify cron (10ddf5f0) | 📅 Mon 6 Apr 06:30 UTC | Confirms FE-019 compliance on briefs |
| FCW full pipeline test | 📅 Thu 9 Apr 09:00 UTC | First full Collector→Weekly→Reasoner→Analyst pass |

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

## SPRINT 4 — Schema Sprint

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
| eghtm-full.md filename rename | Low priority — content updated; filename still eghtm-full.md in internal repo |

---

## Maintenance notes

**To update this file:** Edit `docs/ROADMAP.md` directly on main at every wrap.  
Mark items ✅ when merged. Move to COMPLETED section. Add new items as they arise.  
Do not delete items — mark them ✅ or move to Parking Lot with a reason.

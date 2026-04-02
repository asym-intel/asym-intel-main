# docs/SEO.md — Asymmetric Intelligence SEO Strategy & Findings
## Version 1.0 — First Session Baseline
## Session date: 2026-04-03 | Role: SEO & Discoverability Expert

---

## Platform SEO Purpose

asym-intel.info is a public OSINT intelligence commons. Its seven monitors publish
structured early-warning intelligence weekly — freely, with full methodology, for anyone who
needs it. SEO for this platform is not traffic optimisation. It is the mechanism by which
the right query — asked by a senior analyst, a policymaker, a journalist, or an engaged
citizen — finds the monitor that answers it, before that answer appears in the FT or an
annual index. If WDM is not findable when someone searches "democratic backsliding monitor,"
the public commons is not serving its public. That is the failure mode this role exists to
prevent.

---

## Five Reader Profiles and Search Intent Matrix

The platform's five reader profiles (from MISSION.md) have distinct search behaviours.
Every monitor landing page must serve at least three of the five types in its title, meta
description, H1, and first visible paragraph. This is the three-of-five test.

| Reader profile | Search behaviour | WDM example query | GMM example query | FCW example query |
|---|---|---|---|---|
| OSINT practitioner | Named-source, data-specific, methodological | `V-Dem liberal democracy index Hungary 2026` | `US credit spread systemic risk indicator 2026` | `EU EEAS attribution FIMI campaign tracker` |
| Lawyer / policy expert | Structural-trajectory, compliance-focused, citable | `Hungary rule of law Article 7 proceedings current status` | `US tariff economic impact sovereign debt 2026` | `EU FIMI regulation policy framework 2026` |
| Journalist | Pattern-seeking, event-triggered, verification-oriented | `Hungary democratic backsliding pattern evidence` | `global recession risk early warning indicators` | `Russian information operations disinformation evidence` |
| Activist citizen | Natural language, concern-driven, exploratory | `is democracy declining in Europe` | `will there be a financial crisis 2026` | `is Russia targeting European elections disinformation` |
| Politician / civil society | Positional, cherry-pick-resistant, citable in debate | `independent assessment Hungary democratic institutions` | `independent macro risk assessment 2026` | `state-sponsored disinformation independent analysis` |

### Per-Monitor Keyword Strategy (Standing Reference)

| Monitor | Primary keyword cluster | Secondary cluster | Long-tail opportunity |
|---|---|---|---|
| WDM | democratic backsliding, institutional erosion, democracy index | judicial independence, electoral integrity, authoritarian diffusion | `[country] democracy score 2026` |
| SCEM | conflict escalation, early warning, geopolitical risk | civilian displacement, ceasefire monitoring, escalation indicators | `[region] conflict risk assessment` |
| ESA | European strategic autonomy, EU defence, digital sovereignty | ReArm Europe, NATO European pillar, EU-US decoupling | `European defence industrial base progress` |
| GMM | macro financial risk, global recession risk, systemic stress | credit conditions, sovereign debt, tariff economic impact | `US tariff impact on [asset class/region]` |
| FCW | foreign information manipulation, FIMI, disinformation | cognitive warfare, election interference, state-sponsored | `[country] disinformation campaign evidence` |
| ERM | environmental risk, climate tipping points, planetary boundaries | food security, biodiversity loss, climate migration | `[region] climate risk structural assessment` |
| AGM | AI governance, AI regulation, AI safety | EU AI Act, frontier model risk, AI ethics accountability | `AI regulation tracker [jurisdiction] 2026` |

Update this table quarterly when GSC query data reveals actual search patterns.
First evidence-based revision scheduled Q1 2027.

---

## Current Baseline Findings (2026-Q2 First Session)

### Task 1 — Sitemap Audit

**Status: PASS with two MEDIUM issues**

- **All 7 monitor landing pages present** ✅
  - democratic-integrity, macro-monitor, fimi-cognitive-warfare, european-strategic-autonomy,
    ai-governance, environmental-risks, conflict-escalation — all confirmed in sitemap.
- **Published brief pages present** ✅
  - 10 brief/digest URLs present for the most recent two weeks across all active monitors.
  - Oldest briefs present: 2026-03-29 (ERM), 2026-03-30 (multiple monitors).
- **No future-dated lastmod entries** ✅ — All entries are on or before 2026-04-01.
- **MEDIUM: Methodology pages have spurious `lastmod: 2020-01-01`** ⚠️
  - All 7 methodology pages carry `<lastmod>2020-01-01T00:00:00+00:00</lastmod>`.
  - This date predates the platform. GSC will flag these as stale.
  - Impact: GSC may deprioritise methodology pages in crawl budget.
  - Fix: Hugo front-matter for methodology pages should carry a real `lastmod` date.
    Flag for Platform Developer to set `lastmod` in methodology page front-matter.
- **MEDIUM: 4 utility pages missing `lastmod` entirely** ⚠️
  - /about/, /search/, /subscribe/, /tags/ have no `<lastmod>` in sitemap.
  - GSC will treat these as undated, potentially reducing crawl priority.
- **LOW: Static dashboard pages not in sitemap**
  - dashboard.html, report.html, overview.html, persistent.html etc. are static HTML files
    served from docs/monitors/{slug}/ and are NOT Hugo-built pages.
  - Hugo's sitemap.xml only includes Hugo-rendered pages. Static pages are not indexed
    through the sitemap. Google may still discover them via internal links.
  - Decision needed (Peter): should static dashboard pages be submitted separately?
    If yes, a supplemental sitemap or manual submission to GSC is required.
- **41 total URLs in sitemap** — reasonable for this stage of the platform.
- **Sitemap URL in robots.txt**: `https://asym-intel.info/sitemap.xml` ✅ correct.
- **Repo and live sitemap match** ✅ — identical content.

### Task 2 — Meta Tag Audit (WDM, FCW, GMM)

#### World Democracy Monitor (WDM)

**Title:** `Democratic Integrity · Asymmetric Intelligence`
**Meta description:** `Weekly early-warning radar on democratic erosion, resilience, and
state capture — tracking the leading indicators that annual indices miss. Published every Tuesday.`
**OG title:** `Democratic Integrity · Asymmetric Intelligence`
**OG description:** (same as meta description) ✅
**OG image:** `https://asym-intel.info/images/og-fallback.png` (shared fallback — not monitor-specific) ⚠️
**Canonical:** `https://asym-intel.info/monitors/democratic-integrity/` ✅ correct self-reference
**Twitter card:** `summary_large_image` ✅

**Three-of-five reader profile test:**

| Profile | Served? | Assessment |
|---|---|---|
| OSINT practitioner | ⚠️ PARTIAL | "leading indicators" signals data rigour but no named sources (V-Dem, Freedom House) in title/desc |
| Lawyer / policy expert | ⚠️ PARTIAL | "state capture" is citable framing but "democratic erosion" is general; no Article 7 / rule of law signal |
| Journalist | ✅ YES | "early-warning radar," "leading indicators that annual indices miss" — pattern-seeking, event-triggered |
| Activist citizen | ✅ YES | "democratic erosion" is natural-language accessible; "resilience" is reassuring |
| Politician / civil society | ⚠️ PARTIAL | No "independent assessment" signal; no citable data source named |

**Result: 2 of 5 — FAILS the three-of-five test**

**Gap:** The title "Democratic Integrity" is the monitor's internal name, not a searchable query.
No user searches for "democratic integrity." The primary keyword "democratic backsliding" is
absent from title and meta description. No named data sources (V-Dem, Freedom House,
CIVICUS) appear in the meta description.

**Proposed replacement meta description (155 chars):**
`Weekly early-warning intelligence on democratic backsliding, institutional erosion, and state capture — tracking V-Dem and Freedom House signals before annual indices catch up.`

---

#### FIMI & Cognitive Warfare Monitor (FCW)

**Title:** `Global FIMI & Cognitive Warfare · Asymmetric Intelligence`
**Meta description:** `Weekly intelligence on foreign information manipulation, influence operations, and cognitive warfare targeting democratic societies. Published every Thursday.`
**OG image:** `https://asym-intel.info/images/og-fallback.png` (shared fallback) ⚠️
**Canonical:** `https://asym-intel.info/monitors/fimi-cognitive-warfare/` ✅ correct

**Three-of-five reader profile test:**

| Profile | Served? | Assessment |
|---|---|---|
| OSINT practitioner | ✅ YES | "FIMI" is the technical term practitioners use; "influence operations" is specific |
| Lawyer / policy expert | ✅ YES | EU FIMI regulation framing; "foreign information manipulation" maps to legal/policy vocabulary |
| Journalist | ✅ YES | "cognitive warfare targeting democratic societies" — pattern-seeking framing |
| Activist citizen | ⚠️ PARTIAL | "FIMI" is opaque to non-specialists; "influence operations" is accessible but "cognitive warfare" is jargon |
| Politician / civil society | ⚠️ PARTIAL | "foreign information manipulation" is citable but no independence/attribution signal |

**Result: 3 of 5 — PASSES the three-of-five test (marginally)**

**Gap:** Activist citizen is underserved. Consider adding a plain-language phrase.
"FIMI cognitive warfare tracker" (the primary benchmark query) is not searchable for
non-specialists. Title is strong for practitioners but opaque for general audience.

---

#### Global Macro Monitor (GMM)

**Title:** `Macro Monitor · Asymmetric Intelligence`
**Meta description:** `Weekly financial crisis early-warning system tracking debt, credit, market structure, real economy, and systemic risk. Published every Monday.`
**OG image:** `https://asym-intel.info/images/og-fallback.png` (shared fallback) ⚠️
**Canonical:** `https://asym-intel.info/monitors/macro-monitor/` ✅ correct

**Three-of-five reader profile test:**

| Profile | Served? | Assessment |
|---|---|---|
| OSINT practitioner | ✅ YES | "debt, credit, market structure, real economy, systemic risk" — data-specific |
| Lawyer / policy expert | ✅ YES | "financial crisis early-warning system" — citable, structural framing |
| Journalist | ✅ YES | "early-warning system" — pattern-seeking |
| Activist citizen | ⚠️ PARTIAL | "Macro Monitor" title is opaque; "financial crisis" is accessible but "systemic risk" is jargon |
| Politician / civil society | ⚠️ PARTIAL | No independent assessment signal; no named data sources |

**Result: 3 of 5 — PASSES the three-of-five test (marginally)**

**Gap:** Title "Macro Monitor" is the weakest of the three — it is generic and shares namespace
with an existing competitor site (global-macro-monitor.com) which appeared in AI search results
for the "global macro risk monitor" query. No named data sources in description.
The keyword "global recession risk" does not appear.

---

**Cross-monitor findings:**

- **MEDIUM-SEO-001: OG images are all the same fallback** — All monitor pages use
  `og-fallback.png`. Social shares show identical preview image for all 7 monitors.
  This is SEO-004 (Missing Open Graph Images). Flag for Platform Developer.
- **MEDIUM-SEO-002: No monitor-specific images** — Each monitor needs a 1200×630px
  monitor-specific OG image. Requires Platform Developer + PED (for visual design).
- **HIGH-SEO-010: WDM fails the three-of-five test** — Only 2 of 5 reader profiles served.
  "Democratic backsliding" (the primary keyword) is absent from all WDM metadata.

### Task 3 — Robots.txt Audit

**Current robots.txt (both repo and live):**
```
User-agent: *
Allow: /
Disallow: /admin/

Sitemap: https://asym-intel.info/sitemap.xml
```

**Findings:**

- **LOW: `/pipeline/` not disallowed** — Security Expert (Session 2) confirmed this as
  a LOW finding. /pipeline/ returns 404 (not served), so this is defence-in-depth only.
  Should be added as per the SEO spec and security-findings.md recommendation.
- **LOW: `/*.json` not disallowed** — Data files should not be indexed. Not currently
  served publicly (they are in the docs/monitors/ tree which GitHub Pages serves but
  data/ paths are not standard content), but the robots.txt spec requires this.
- **Monitor pages: correctly allowed** ✅ — `Allow: /` covers all monitor pages.
- **Sitemap URL: correct** ✅
- **`/admin/` disallowed** ✅ — fine, but this path doesn't exist on the live site.

**Required robots.txt update (spec for Platform Developer):**
```
User-agent: *
Allow: /
Allow: /monitors/
Disallow: /pipeline/
Disallow: /*.json

Sitemap: https://asym-intel.info/sitemap.xml
```

Note: Per security-findings.md MEDIUM-3 — when CSP headers are added via Cloudflare,
this robots.txt change has no CSP interaction. But any new external analytics added for
SEO tracking (e.g., Google Analytics) must be pre-approved through the Security Expert
before implementation.

### Task 4 — Dataset Markup Gap

**Status: HIGH — No structured data on any page.**

Confirmed via:
- `curl` on WDM, GMM monitor landing pages: zero matches for `schema.org`, `application/ld+json`,
  `Dataset`, `NewsArticle`, `BreadcrumbList`
- Inspection of `layouts/partials/head.html`: no JSON-LD blocks present
- Inspection of all dashboard HTML files: no `<script type="application/ld+json">` blocks

**Gaps identified:**

1. **No `Dataset` markup on monitor overview/dashboard pages** — HIGH
   The platform publishes structured JSON data files weekly. These are substantively datasets.
   Dataset markup makes them discoverable in Google Dataset Search, directly serving OSINT
   practitioners and academic researchers — the platform's primary audience.

2. **No `NewsArticle` markup on brief/digest pages** — HIGH
   Each weekly brief is a structured intelligence report. NewsArticle schema is the correct
   type and makes brief pages eligible for Google News features and AI overview citations.

3. **No `BreadcrumbList` markup on any page** — MEDIUM
   Every page should have breadcrumb schema (Home → Monitors → [Monitor Name]) to
   improve SERP display and help AI search engines understand the site hierarchy.

4. **No `FAQPage` schema on monitor landing pages** — MEDIUM
   Monitor landing pages answer predictable questions (What is WDM? What countries does it
   cover? How often does it publish?). FAQPage JSON-LD is a priority for AI search visibility.

5. **No `WebPage` schema on overview/dashboard pages** — LOW

**Full implementation spec:** See `docs/seo/ai-search-audit-2026-Q2.md` Section 5.

### Task 5 — AI Search Baseline

**See `docs/seo/ai-search-audit-2026-Q2.md` for full audit. Summary:**

All three benchmark queries return **zero citations of asym-intel.info**. The platform
is invisible in AI search as of 2026-Q2. Competitors appearing in results include:
- V-Dem, Freedom House, Carnegie Endowment (WDM query)
- EEAS, LinkedIn/OpenMinds Cognitive Defence Monitor (FCW query)
- Oxford Analytica Global Risk Monitor, global-macro-monitor.com (GMM query)

This is a HIGH finding (SEO-008: AI-Search Invisibility).

### Task 6 — Citability Audit

**WDM brief tested:** `https://asym-intel.info/monitors/democratic-integrity/2026-04-01-weekly-brief/`

- **HTTP status: 200** ✅ — URL is live and accessible
- **Canonical tag: present and self-referencing** ✅
  `<link rel="canonical" href="https://asym-intel.info/monitors/democratic-integrity/2026-04-01-weekly-brief/">`
- **In sitemap: YES** ✅ — included as `<loc>` entry with `lastmod: 2026-04-01T06:00:00+00:00`
- **Permalink stability: GOOD** — URL is date-stamped, human-readable, stable slug pattern
- **OG type: `article`** ✅ — correct for individual brief pages

**Gap: No "Cite this" element visible** — The brief page has no structured citation helper.
Per the Enhancement Addenda citability infrastructure requirement, each brief should have
a visible "Cite this" element with formatted citation. Spec for Platform Developer.

**No archive policy applied yet** — All existing briefs appear to be indexed (no `noindex`
found in any brief page). Platform is 3 issues old so archive policy is not yet material.
Review at 3-month mark per the archive indexing policy in the SEO prompt.

---

## Quarterly Checklist

Run every quarter. First run: 2026-Q2 (this session). Next scheduled: 2026-Q3 (July).

- [ ] Sitemap: all 7 monitors present, no future-dated entries, methodology page dates accurate
- [ ] Robots.txt: /pipeline/ disallowed, /*.json disallowed, monitors allowed, sitemap URL correct
- [ ] Meta tags: three-of-five test on all 7 monitor landing pages, no duplicate descriptions
- [ ] OG images: all monitors have monitor-specific images (not fallback)
- [ ] Canonical tags: all pages self-referencing, no inconsistencies
- [ ] Structured data: Dataset markup on all 7 overview pages; NewsArticle on all briefs
- [ ] AI search audit: run 7 primary keyword queries, document citation status
- [ ] GSC coverage: review indexed vs. crawled page counts (requires GSC access)
- [ ] Top queries: identify which research queries are finding the site
- [ ] Brief citability: "Cite this" element on all brief pages
- [ ] Archive policy: apply noindex to briefs older than 3 months (except Issue 1 per monitor)

---

## Implementation Backlog for Platform Developer

All items below require Platform Developer implementation (staging → PR → visual sign-off → merge).
This role does not modify HTML directly.

### P1 — Critical (block AI search visibility)

**P1-A: Add `Disallow: /pipeline/` and `Disallow: /*.json` to robots.txt**
- File: `docs/robots.txt`
- Current: `Disallow: /admin/`
- Required addition:
  ```
  Disallow: /pipeline/
  Disallow: /*.json
  ```
- Why: Security requirement (Session 2 LOW finding) + SEO spec compliance.

**P1-B: Add JSON-LD structured data to Hugo head.html partial**
- File: `layouts/partials/head.html`
- For monitor overview/landing pages: `Dataset` schema
- For individual brief/digest pages: `NewsArticle` schema
- For all pages: `BreadcrumbList` schema (Home → Monitors → [Monitor Name])
- Full JSON-LD spec in `docs/seo/ai-search-audit-2026-Q2.md` Section 5.
- Why: PRIMARY driver of AI search invisibility. NewsArticle and Dataset markup are
  citation-enabling for Google AI Overviews and Perplexity.

**P1-C: Fix WDM meta description — add primary keyword "democratic backsliding"**
- Page: `content/monitors/democratic-integrity/_index.md` (or equivalent Hugo content file)
- Current description: `Weekly early-warning radar on democratic erosion, resilience, and state capture — tracking the leading indicators that annual indices miss. Published every Tuesday.`
- Proposed (155 chars): `Weekly early-warning intelligence on democratic backsliding, institutional erosion, and state capture — tracking V-Dem and Freedom House signals before annual indices catch up.`
- Why: WDM fails the three-of-five test. "Democratic backsliding" is the primary search term.
  "V-Dem and Freedom House" gives OSINT practitioners and lawyers a named-source anchor.

### P2 — High priority (within 30 days)

**P2-A: Add FAQPage JSON-LD to monitor landing pages**
- Each monitor landing page: 3–5 FAQs answering the most common questions
- See `docs/seo/ai-search-audit-2026-Q2.md` for example JSON-LD
- Why: FAQPage schema is a primary mechanism for appearing in AI Overviews.

**P2-B: Add machine-readable timestamps to monitor pages**
- All monitor pages: `<time datetime="YYYY-MM-DDTHH:MM:SSZ" itemprop="dateModified">` element
- Required by Enhancement Addenda for AI search extraction
- Why: AI search engines use machine-readable timestamps to determine content freshness.

**P2-C: Fix methodology page `lastmod` dates (2020-01-01)**
- All 7 methodology pages in Hugo front-matter: set `lastmod` to actual date
- Why: GSC will flag all 7 methodology pages as stale (date predates the platform).

**P2-D: Add a "Cite this" element to brief pages**
- File: `layouts/_default/single.html` (or brief-specific layout)
- Element: visible citation block with formatted citation string and permalink
- Format: `Asymmetric Intelligence. "World Democracy Monitor — W/E 1 April 2026."
  asym-intel.info, 1 April 2026. https://asym-intel.info/monitors/democratic-integrity/2026-04-01-weekly-brief/`
- Why: Citability infrastructure requirement; enables lawyers, journalists, and politicians
  to cite briefs in their own work.

### P3 — Medium priority (within 90 days)

**P3-A: Monitor-specific OG images (1200×630px)**
- 7 monitor-specific images needed; each uses the monitor accent colour and name
- Requires PED (Platform Experience Designer) session for design before implementation
- Why: All monitors currently share og-fallback.png. Social shares are indistinguishable.

**P3-B: GMM meta description — add keyword "global recession risk"**
- Current title "Macro Monitor" competes with global-macro-monitor.com domain
- Proposed description addition: include "global recession risk" and "systemic stress indicators"

**P3-C: FCW meta description — add plain-language phrase for activist citizen profile**
- Current description is practitioner/policy-level. Add: "disinformation targeting elections"
  as an accessible signal.

---

## Open Questions Requiring Peter's Decision

1. **Static dashboard pages in sitemap** — Hugo's sitemap.xml only includes Hugo-rendered
   pages. The 7 dashboard.html, report.html, overview.html etc. files are static HTML
   (docs/monitors/{slug}/) and are not currently submitted to GSC via the sitemap.
   Question: Should a supplemental sitemap be created for static monitor pages?
   Impact: GSC may not discover or prioritise these pages without explicit submission.

2. **Archive indexing policy** — The platform is 3 issues old. Now is the time to decide:
   will old briefs be noindexed at 3 months, or indexed indefinitely?
   Recommendation: for a new platform, index all issues during the first 12 months to
   build authority. Apply the archive policy at the 12-month mark.

3. **GSC property setup completion** — DNS TXT record done (2 April per HANDOFF.md).
   Has Peter completed the GSC property verification in the GSC console?
   Without verification, no impression/click/query data is available.

4. **Keyword strategy for "Macro Monitor" title** — The monitor's title competes with
   global-macro-monitor.com. The platform's meta description is strong, but the short title
   "Macro Monitor" on its own is a weak anchor. Consider whether the title should be
   "Global Macro Risk Monitor" or whether "Global Macro Monitor" better serves search.
   This is a URL-structure-adjacent decision requiring Peter's approval.

5. **Google Dataset Search submission** — Once Dataset markup is implemented, submitting
   data files to Google Dataset Search is a manual step. Peter to confirm whether the
   published JSON data files (report-latest.json etc.) should be discoverable as datasets.

---

## Failure Mode Register (active)

| Code | Status | Description |
|------|--------|-------------|
| SEO-001 | OK — no duplicates found | Duplicate meta descriptions |
| SEO-002 | Not yet audited | Broken internal links (defer to next session) |
| SEO-003 | Not yet applicable | Archive over-indexing (platform too new) |
| SEO-004 | ACTIVE — all monitors | Missing monitor-specific OG images |
| SEO-005 | OK | Canonical tag inconsistency — all self-referencing |
| SEO-006 | OK | Outdated sitemap — all 7 monitors present |
| SEO-007 | OK | No future-dated sitemap entries |
| SEO-008 | ACTIVE — HIGH | AI search invisibility — not cited in any benchmark query |
| SEO-009 | OK — brief URLs are stable | Citability URL breakage |
| SEO-010 | ACTIVE — WDM | Single-profile metadata — WDM fails three-of-five test |

# docs/seo/gsc-monthly-audit.md
## Google Search Console — Monthly Audit Log
## Asymmetric Intelligence Platform

---

## About This File

This file is the persistent log of monthly Google Search Console audits for asym-intel.info.
Updated monthly by the SEO & Discoverability Expert role (or the GSC audit cron f78e0c2c).

**Audit schedule:** Monthly, with quarterly full reviews in Jan/Apr/Jul/Oct.  
**GSC property:** `asym-intel.info` (verified via DNS TXT record, completed 2 April 2026)  
**GSC cron:** f78e0c2c (background=false, 1 Jan/Apr/Jul/Oct 09:00 UTC)

**Note on access:** The DNS TXT record was confirmed done on 2 April 2026 per HANDOFF.md.
However, actual GSC data is not yet accessible — GSC property verification in the GSC
console must be completed by Peter. Until Peter completes the in-console verification
step, this file will carry [PENDING GSC ACCESS] in all data fields.

**To complete GSC setup (Peter action required):**
1. Go to https://search.google.com/search-console/
2. Add property for `asym-intel.info` (domain property type)
3. Confirm the DNS TXT record is verified (should show verified if added 2 April 2026)
4. Also add property for `compossible.asym-intel.info` (SEO prompt specifies both)
5. Submit sitemap: `https://asym-intel.info/sitemap.xml`

---

## Audit: 2026-04-03 (First Session Baseline)

**Auditor:** SEO & Discoverability Expert  
**GSC access:** NOT YET AVAILABLE — data fields are [PENDING GSC ACCESS]

### 1. Coverage

| Metric | Value | Notes |
|--------|-------|-------|
| Pages indexed | [PENDING GSC ACCESS] | - |
| Pages crawled but not indexed | [PENDING GSC ACCESS] | - |
| Pages excluded | [PENDING GSC ACCESS] | Check: are monitor pages accidentally excluded? |
| Sitemap submitted | [PENDING GSC ACCESS] | Once access confirmed |
| Sitemap accepted | [PENDING GSC ACCESS] | - |
| Sitemap errors | [PENDING GSC ACCESS] | Known possible issue: methodology page dates (2020-01-01) may flag |

**Expected findings when access is available:**
- Sitemap has 41 URLs — verify GSC shows all 41 as submitted
- Methodology pages with `2020-01-01` lastmod may appear in Coverage > Excluded >
  "Crawled — currently not indexed" if GSC treats the dates as stale
- Static dashboard pages (dashboard.html, report.html, etc.) will not appear via sitemap
  — they may appear in Coverage > Discovered — currently not indexed if found via crawl

### 2. Errors (4xx, 5xx, Redirect Chains)

| URL pattern | Status | Notes |
|-------------|--------|-------|
| [PENDING GSC ACCESS] | - | - |

**Known 200 OK URLs (confirmed via direct check):**
- `https://asym-intel.info/monitors/democratic-integrity/` — 200 ✅
- `https://asym-intel.info/monitors/democratic-integrity/2026-04-01-weekly-brief/` — 200 ✅
- `https://asym-intel.info/monitors/fimi-cognitive-warfare/` — 200 ✅
- `https://asym-intel.info/monitors/macro-monitor/` — 200 ✅

### 3. Top Queries

[PENDING GSC ACCESS]

**Expected query profile (assumption — no data yet):**
- Brand queries: "asym-intel," "asymmetric intelligence"
- Domain queries: none yet (platform too new, no external citations)
- Organic queries: "democratic backsliding," "FIMI," "macro risk" — if visible

First real query data expected 4–6 weeks after GSC property verification.
First evidence-based audience profile update: Q1 2027 (per MISSION.md).

### 4. CTR Analysis

[PENDING GSC ACCESS]

**Baseline note:** At platform launch, expect low CTR (< 1%) for most queries — platform
has no SERP presence yet. The first 6 months of GSC data will establish whether impressions
are generating clicks. If impressions > 100 but CTR < 1% for a monitor page, the meta
description needs rewriting.

### 5. Core Web Vitals

[PENDING GSC ACCESS]

**Manual observation (not GSC data):** Live site loads quickly on a clean browser session.
No Core Web Vitals failures observed during audit. Formal Lighthouse score not run this
session — add to next session.

### 6. Mobile Usability

[PENDING GSC ACCESS]

**Manual observation:** Site renders correctly on mobile viewport. No mobile usability
failures observed during audit.

---

## Audit: [NEXT MONTH — TBD]

*Populate when GSC access is confirmed and first data is available.*

| Field | Value |
|-------|-------|
| Date | [DATE] |
| Auditor | SEO & Discoverability Expert |
| GSC access | [CONFIRMED / PENDING] |
| Pages indexed | [VALUE] |
| Top query #1 | [QUERY] — [impressions] impressions, [CTR]% CTR |
| Top query #2 | [QUERY] — [impressions] impressions, [CTR]% CTR |
| Top query #3 | [QUERY] — [impressions] impressions, [CTR]% CTR |
| Errors found | [NONE / LIST] |
| Action taken | [NONE / FLAG FOR PLATFORM DEVELOPER] |

---

## Monthly Audit Checklist

Run every month once GSC access is confirmed:

- [ ] Coverage: pages indexed vs. crawled — any unexpected excluded pages?
- [ ] Errors: any new 4xx, 5xx, or redirect chain errors?
- [ ] Top queries: which research queries are finding the site?
- [ ] CTR: any monitor pages with high impressions but low CTR? (rewrite meta description)
- [ ] Core Web Vitals: any performance regressions?
- [ ] Mobile usability: any new mobile issues?
- [ ] Sitemap: confirm no new errors after any recent Hugo deploy
- [ ] New pages: any new monitor pages that should appear in coverage but don't?

For each finding: record URL, issue, recommended action.
Flag implementation tasks for Platform Developer in notes-for-computer.md.

---

## Standing Notes

- GSC cron f78e0c2c: runs 1 Jan/Apr/Jul/Oct 09:00 UTC (background=false). This cron is
  scheduled to run the full quarterly GSC audit. If GSC access is not established by
  1 July 2026, the cron will have no data to work with.
- DNS TXT verification: confirmed done 2 April 2026. Property verification in GSC console
  must be completed by Peter separately.
- compossible.asym-intel.info: the SEO prompt specifies both properties should be submitted.
  Add this as a second property in GSC once the primary is confirmed.
- First real data: expect 4–6 weeks after property verification for initial impression data.
- First query-driven audience insights: no earlier than Q3 2026.

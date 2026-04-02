# docs/seo/ai-search-audit-2026-Q2.md
## AI Search Baseline Audit — Q2 2026
## Asymmetric Intelligence Platform — First Session Benchmark

---

## 1. Date and Methodology

**Audit date:** 2026-04-03  
**Auditor:** SEO & Discoverability Expert (Session 3 — first-ever SEO session)  
**Methodology:**  
Three benchmark queries were run using search_web (Perplexity-backed) search to establish
the 2026-Q2 baseline. For each query: citation status of asym-intel.info was checked;
competing resources appearing in results were documented; and gap analysis was applied.

This is the first AI search audit. Subsequent quarterly audits should run against the same
three queries plus the four remaining monitor primary queries (ESA, AGM, ERM, SCEM) to
build a longitudinal citation record.

**AI search channels audited:** Perplexity (via search_web). Google AI Overviews and
ChatGPT Search not directly accessible in this session — noted as gap for future sessions.

---

## 2. Query Results

### Query 1: "democratic backsliding monitor"

**Citation status of asym-intel.info:** NOT CITED

**Sources appearing in results:**

| Source | Domain | Type | Notes |
|--------|--------|------|-------|
| Stanford Social Innovation Review | ssir.org | Academic/practitioner article | "How to Spot Democratic Backsliding" — links to V-Dem, Freedom House datasets |
| Carnegie Endowment for International Peace | carnegieendowment.org | Research paper | "Understanding and Responding to Global Democratic Backsliding" (2022) |
| Cambridge Core (PS: Political Science & Politics) | cambridge.org | Academic journal | "Measuring Democratic Backsliding" — cites V-Dem, Polity5, GSOD indices |
| Yale ISPS | isps.yale.edu | University blog | Research roundup, March 2025 |

**Key observations:**
- Zero AI-native monitoring platforms appear in results. Academic and institutional papers dominate.
- V-Dem, Freedom House, and Freedom in the World are named as the canonical data sources.
- asym-intel.info is absent despite WDM being the exact content type this query targets.
- The query "democratic backsliding monitor" is precisely what WDM is — a monitor of democratic backsliding. The absence is a structural SEO failure, not a content failure.

---

### Query 2: "FIMI cognitive warfare tracker"

**Citation status of asym-intel.info:** NOT CITED

**Sources appearing in results:**

| Source | Domain | Type | Notes |
|--------|--------|------|-------|
| LinkedIn / OpenMinds | linkedin.com | LinkedIn post | "Cognitive Defence Monitor" — a curated knowledge base of FIMI research, May 2025 |
| The Defence Horizon Journal | tdhj.org | Academic journal | "Disinformation In Cognitive Warfare, FIMI, Hybrid Threats" |
| LinkedIn / John Fuisz (Veriphix) | linkedin.com | LinkedIn post | Belief3 federated model for FIMI tracking, Feb 2026 |

**Key observations:**
- The exact term "FIMI cognitive warfare tracker" returns no authoritative institutional source.
  This is a gap in the market that FCW directly fills — but FCW is not appearing.
- OpenMinds' Cognitive Defence Monitor is the closest competitor — a knowledge base, not a
  real-time monitor. Different product, but same audience, same vocabulary.
- The EEAS (EU East StratCom Task Force) is conspicuously absent from results — the most
  prominent institutional FIMI tracking body. This suggests the query is too narrow for
  institutional sources, leaving a gap FCW should be filling.
- LinkedIn content appearing in AI search results for this query suggests the FIMI community
  is active there; a FCW presence or citation on LinkedIn could accelerate discovery.

---

### Query 3: "global macro risk monitor"

**Citation status of asym-intel.info:** NOT CITED

**Sources appearing in results:**

| Source | Domain | Type | Notes |
|--------|--------|------|-------|
| Oxford Analytica Global Risk Monitor | grm.oxan.com / globaledge.msu.edu | Proprietary platform | Commercial product; tracks "top ten global risks" — macro and geopolitical |
| Global Macro Monitor (blog) | global-macro-monitor.com | Independent blog | Weekly macro market commentary; "Week In Review — March 27" appeared with date 2026-03-29 |

**Key observations:**
- Two direct competitors for this query: Oxford Analytica's GRM (authoritative, paywalled,
  institutional) and global-macro-monitor.com (independent blog, free, ranks well).
- global-macro-monitor.com appeared with a 2026-03-29 article — very recent, same day as
  asym-intel.info's GMM brief. This is a head-to-head scenario: both publish weekly macro
  commentary; asym-intel.info did not appear.
- Oxford Analytica GRM is paywalled and institutional — not the same audience. But it
  owns the "global risk monitor" term.
- The GMM monitor title "Macro Monitor" (short) loses significantly to "global-macro-monitor.com"
  in domain authority and title match for this query. "Global Macro Risk Monitor" or
  "Global Macro Monitor" as the title would better match this query.

---

## 3. Citation Status Summary — 2026-Q2 Baseline

| Query | asym-intel.info cited? | Primary competitor(s) |
|-------|------------------------|----------------------|
| "democratic backsliding monitor" | NO | V-Dem, Freedom House, Carnegie, SSIR |
| "FIMI cognitive warfare tracker" | NO | OpenMinds Cognitive Defence Monitor, EEAS |
| "global macro risk monitor" | NO | Oxford Analytica GRM, global-macro-monitor.com |

**Overall status: 0 of 3 benchmark queries cite asym-intel.info**

This is a HIGH severity finding: SEO-008 (AI-Search Invisibility) is fully active.

---

## 4. Gap Analysis: Why Is the Platform Not Appearing?

### Root cause 1: No structured data (primary driver)

AI search engines (Perplexity, Google AI Overviews, ChatGPT Search) use structured data to
identify what a page is about, what type of content it is, and who produced it. The platform
has zero JSON-LD on any page. Without it:

- Google cannot classify monitor pages as `NewsArticle` or `Dataset`
- AI search cannot extract confidence levels, methodology, or data source references
- FAQPage schema (the primary mechanism for AI Overview inclusion) is absent
- Machine-readable timestamps are absent (AI search cannot verify freshness)

This is the most actionable fix and the highest-ROI intervention.

### Root cause 2: Primary keywords absent from metadata

- WDM meta description does not contain "democratic backsliding" — the primary search term
- GMM title "Macro Monitor" shares zero semantic overlap with "global macro risk monitor"
- FCW title "FIMI & Cognitive Warfare" is strong for practitioners but has no plain-language
  accessibility

### Root cause 3: Platform authority gap (new site, limited inbound links)

The platform has been live for a matter of weeks. AI search engines weight domain authority
heavily. The competitors appearing in results (Carnegie, Oxford Analytica, Cambridge Core)
have years of indexed content and thousands of inbound links. This authority gap will narrow
over time as the platform accumulates published briefs and inbound citations.

The structured data fix (Root cause 1) can partially compensate for authority deficit —
structured data signals content type and reliability directly, reducing the weight of
domain authority in AI citation decisions.

### Root cause 4: Dashboard pages not in sitemap

The primary interactive dashboard pages (dashboard.html, report.html, etc.) for all 7 monitors
are static HTML files. Hugo's auto-generated sitemap.xml does not include static HTML files.
Google may discover them via internal links but has no explicit crawl instruction via sitemap.

### Root cause 5: Methodology pages with stale dates

7 methodology pages carry `lastmod: 2020-01-01` — a date that predates the platform's
existence. GSC and AI search engines may treat these as stale and deprioritise them,
even though they contain the high-value "clean vocabulary" that AI search engines extract
for citations.

---

## 5. Dataset Markup Implementation Spec

### 5.1 For Monitor Overview/Landing Pages (`WebPage` + `Dataset`)

Implement in `layouts/partials/head.html`, conditional on page type.

```json
{
  "@context": "https://schema.org",
  "@type": ["WebPage", "Dataset"],
  "name": "World Democracy Monitor — Asymmetric Intelligence",
  "description": "Weekly early-warning intelligence on democratic backsliding, institutional erosion, and state capture, tracking V-Dem and Freedom House signals before annual indices catch up.",
  "url": "https://asym-intel.info/monitors/democratic-integrity/",
  "publisher": {
    "@type": "Organization",
    "name": "Asymmetric Intelligence",
    "url": "https://asym-intel.info"
  },
  "creator": {
    "@type": "Person",
    "name": "Peter Howitt"
  },
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json"
    }
  ],
  "temporalCoverage": "2026/..",
  "updateFrequency": "P7D",
  "keywords": [
    "democratic backsliding",
    "institutional erosion",
    "state capture",
    "democracy index",
    "V-Dem",
    "Freedom House",
    "OSINT"
  ],
  "inLanguage": "en",
  "dateModified": "2026-04-01"
}
```

Apply equivalent schema to all 7 monitors, substituting monitor-specific name,
description, keywords, and data URL.

### 5.2 For Individual Brief/Digest Pages (`NewsArticle`)

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "World Democracy Monitor — W/E 1 April 2026",
  "description": "Hungary enters the final 11 days with aggregate polling at 50.8% for Tisza — a potential end to 16 years of illiberal rule — while the US Supreme Court heard oral arguments testing whether the 14th Amendment citizenship clause can be reinterpreted by executive order alone.",
  "url": "https://asym-intel.info/monitors/democratic-integrity/2026-04-01-weekly-brief/",
  "datePublished": "2026-04-01T06:00:00Z",
  "dateModified": "2026-04-01T06:00:00Z",
  "author": {
    "@type": "Organization",
    "name": "Asymmetric Intelligence",
    "url": "https://asym-intel.info"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Asymmetric Intelligence",
    "url": "https://asym-intel.info",
    "logo": {
      "@type": "ImageObject",
      "url": "https://asym-intel.info/favicon-32x32.png"
    }
  },
  "isAccessibleForFree": true,
  "license": "https://creativecommons.org/licenses/by/4.0/"
}
```

Hugo template variables for `layouts/_default/single.html`:
- `headline` → `{{ .Title }}`
- `description` → `{{ .Description }}`
- `url` → `{{ .Permalink }}`
- `datePublished` → `{{ .Date.Format "2006-01-02T15:04:05Z" }}`
- `dateModified` → `{{ .Lastmod.Format "2006-01-02T15:04:05Z" }}`

### 5.3 FAQPage Schema for Monitor Landing Pages

Each monitor landing page should include 3–5 FAQs. Example for WDM:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does the World Democracy Monitor track?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The World Democracy Monitor tracks democratic backsliding, institutional erosion, and state capture across key countries. It uses V-Dem, Freedom House, and CIVICUS data as primary sources, publishing weekly early-warning intelligence before annual democracy indices register the deterioration."
      }
    },
    {
      "@type": "Question",
      "name": "How often does the World Democracy Monitor publish?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Weekly, every Monday at 06:00 UTC. Each issue covers the most significant structural developments in the preceding seven days."
      }
    },
    {
      "@type": "Question",
      "name": "Is the World Democracy Monitor free?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. All output is free, open, and permanently accessible. No paywalls, no paid tiers, ever. Content is published under CC BY 4.0."
      }
    },
    {
      "@type": "Question",
      "name": "What methodology does the World Democracy Monitor use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WDM applies a structured source hierarchy. Tier 1 sources (V-Dem, Freedom House, CIVICUS, official electoral data) determine findings. Tier 2–3 sources corroborate. Confidence levels are explicit. All methodology is published."
      }
    }
  ]
}
```

### 5.4 BreadcrumbList Schema (All Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://asym-intel.info/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Monitors",
      "item": "https://asym-intel.info/monitors/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "World Democracy Monitor",
      "item": "https://asym-intel.info/monitors/democratic-integrity/"
    }
  ]
}
```

---

## 6. Recommended Actions (Priority Order)

### Immediate (within 7 days)

1. **Implement JSON-LD structured data** (Dataset + NewsArticle + BreadcrumbList)
   — Platform Developer — `layouts/partials/head.html` and `layouts/_default/single.html`
   — This is the single highest-impact SEO action available.

2. **Fix WDM meta description** — add "democratic backsliding" + named sources
   — Platform Developer — content front-matter update only, no HTML change needed

3. **Add `Disallow: /pipeline/` and `Disallow: /*.json` to robots.txt**
   — Platform Developer — one-line change

### Within 30 days

4. **Add FAQPage JSON-LD to all 7 monitor landing pages**
5. **Add machine-readable timestamps to all monitor pages**
6. **Fix methodology page lastmod dates (2020-01-01 → actual dates)**

### Within 90 days

7. **Create monitor-specific OG images** — requires PED design session first
8. **Update GMM and FCW meta descriptions** for broader keyword coverage
9. **Submit static dashboard pages to GSC** if Peter confirms they should be indexed

---

## 7. Next Quarterly Audit (2026-Q3, July)

Run the same three benchmark queries plus:
- "European strategic autonomy monitor"
- "AI governance regulation tracker"
- "environmental risk early warning"
- "conflict escalation monitor"

Document whether structured data implementation has produced citation improvement.
Compare with this baseline.

---

*This is the 2026-Q2 baseline. All subsequent quarterly audits should reference this file
for longitudinal comparison. Next audit: 2026-Q3 (1 July 2026, GSC cron f78e0c2c runs
quarterly — but that cron checks GSC data, not AI search. AI search audit requires
a manual session or separate automation).*

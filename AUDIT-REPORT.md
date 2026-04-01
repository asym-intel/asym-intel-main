# Site Audit Report — asym-intel.info
**Date:** 2026-04-01 | **Audited:** Homepage, 7×overview, 7×dashboard, 4×report, 4×persistent
**Viewports:** Mobile 375×812 · Desktop 1440×900
**Validator:** 15/15 checks passing ✅

---

## CRITICAL (block next build session)

### C1 — WDM persistent.html JS error — data never loads
**Pages:** democratic-integrity/persistent.html (mobile + desktop)
**Issue:** `PAGE ERROR: Unexpected string` on load. Heatmap Countries and Mimicry Chains 
sections stuck at "Loading…" permanently. Root cause: syntax error in WDM persistent.html 
JavaScript — likely a template literal or JSON parse issue introduced by the visual 
enhancement subagent.
**Fix:** Fetch wdm persistent.html, locate the JS error, fix the syntax. Push to staging, 
verify data loads, merge to main.

---

## HIGH (fix before new features)

### H1 — Mobile horizontal overflow on 3 long monitor names
**Pages:** SCEM (+59px), ESA (+53px), FCW (+13px) — overview AND dashboard on mobile
**Issue:** Monitor name + hamburger + theme toggle don't fit in 375px nav bar. Causes 
horizontal scroll bleed. Same root cause on all pages for these 3 monitors.
**Fix:** In base.css, add to `.monitor-nav__brand span`:
  `overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: calc(100vw - 120px)`
This truncates the name gracefully. All 3 monitors fixed by one base.css change.
**Files:** `static/monitors/shared/css/base.css` → staging → main

### H2 — Dark mode toggle pushed off-screen on ESA and SCEM mobile
**Pages:** ESA and SCEM nav bar — toggle cut off at right edge on 375px
**Issue:** Same long-name problem as H1 — the toggle overflows the viewport.
**Fix:** Resolved by H1 fix — once the name truncates, the toggle has room. 
No separate fix needed if H1 is implemented correctly.

---

## MEDIUM (fix in upcoming sprint)

### M1 — FCW dark mode toggle clipped on report + persistent mobile
**Pages:** fcw-report-mobile, fcw-persistent-mobile
**Issue:** Toggle partially cut off at right viewport boundary.
**Fix:** Same as H1 — resolved by monitor name truncation.

### M2 — WDM persistent.html missing Category B sections
**Status:** Known outstanding task (WDM Build 2). HTML files prepared in workspace.
**Fix:** Push wdm-report-new.html and wdm-persistent-new.html to staging → verify → merge.
Note: Fix C1 FIRST before pushing Build 2 files to avoid overwriting the fix.

### M3 — AGM overview uses older template/layout
**Pages:** ai-governance/overview.html (both viewports)
**Issue:** Sidebar uses plain anchor rows instead of CTA button style used by all other 6 monitors.
**Fix:** Audit agm/overview.html against another monitor's overview.html and align the 
sidebar component. Staging → main.

---

## LOW (next cleanup round)

### L1 — Page <title> inconsistencies across 5 monitors
**Standard should be:** "{Monitor Full Name} — Overview · Asymmetric Intelligence"
**Current issues:**
- WDM: missing " · Asymmetric Intelligence" suffix
- FCW: missing " · Asymmetric Intelligence" suffix  
- ESA: missing " · Asymmetric Intelligence" suffix
- AGM: "AGM · Asymmetric Intelligence" (abbreviation, not full name)
- ERM: reversed word order
- SCEM: missing "Overview" and brand suffix
**Fix:** Edit each page's `<title>` tag. Low effort, high SEO/professionalism value.

### L2 — GMM mobile KPI card visually tight at right edge
**Pages:** gmm-dashboard-mobile
**Issue:** "STAGFLATION" KPI card crowded at 375px — not overflowing but feels clipped.
**Fix:** Reduce KPI card min-width slightly or adjust grid gap at mobile breakpoint in base.css.

### L3 — Validator: add <title> format check (prevent recurrence of L1)
**Fix:** Add Check 16 to validate-blueprint.py: each HTML page title must contain 
the monitor's full name and "Asymmetric Intelligence".

---

## CONFIRMED GOOD ✅

- Black network bar visible on ALL pages, mobile and desktop
- Brand name "Asymmetric Intelligence" visible in black bar on all pages
- Monitor nav sticky on scroll — all 7 monitors
- Data loading correctly on all dashboard pages — no JS errors on 6/7 monitors
- Charts rendering on all pages that use Chart.js
- GMM asset bar chart, FCW campaign Gantt, SCEM F-flag board all render on mobile
- Desktop sidebars present and labelled correctly on all pages
- No horizontal overflow on GMM, WDM, AGM, ERM
- Homepage clean on both viewports
- All 7 monitor overview pages loading correctly

---

## Fix Priority Order

1. **C1** — WDM persistent.html JS error (1 file, staging → main)
2. **H1** — Monitor name truncation on mobile (1 CSS rule in base.css, staging → main)
3. **M2** — WDM Build 2 Category B sections (after C1 is confirmed fixed)
4. **M3** — AGM overview template alignment (staging → main)
5. **L1** — Page title fixes across 5 monitors (staging → main, low risk)
6. **L2** — GMM KPI card mobile spacing (base.css, staging → main)
7. **L3** — Add title validator check

---

## What NOT to build next
No new features or visual enhancements until C1 and H1 are resolved.

# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap (~09:10 CEST)

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: PED Sprint 2 + ESA/AGM/ERM pipeline completion ---

First: surface Peter's open decisions before any implementation.
Check decisions.md Section 4 — Q4, Q6, Q7, Q8 still need answers.

VERIFY LIVE BEFORE STARTING:
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
Should show v1.3. If not: workflow_dispatch build.yml, then purge-all-files CF.

Priority queue:

1. ESA/AGM/ERM weekly-research + reasoner workflows
   Pattern in: .github/workflows/fcw-weekly-research.yml + fcw-reasoner.yml
   Need for: european-strategic-autonomy, ai-governance, environmental-risks
   Also update their analyst cron prompts with Steps 0C/0D/0E

2. Remaining Source → patterns (minor cleanup)
   FCW dashboard (1), WDM dashboard (1), SCEM dashboard (1) — bespoke inline styles
   Check: grep "Source →" in each file, fix manually

3. PED Sprint 2 (read docs/ux/decisions.md + docs/ux/colour-registry.md first)
   - AGM + ERM dashboard audit (last 2 unreviewed)
   - ESA mobile test — 375px #section-delta font
   - Signal panel contrast fix — GMM + SCEM (extend FCW Principle 5)
   - Severity badge font size — 0.6rem → --text-xs in base.css

4. GMM/ESA annual calibration files
   - macro-monitor-imf-2026.md (IMF WEO April 2026 data)
   - european-strategic-autonomy-ecfr-2026.md

DEPLOYMENT REMINDER:
After any shared JS/CSS change → verify live (Cache-Control: no-store) → if stale: workflow_dispatch + CF purge-all.
CF Zone ID: cc419b7519eba04ef0dc6a7b851930c7
```

## Previous session completed
- ✅ nav.js v1.3 — MONITOR_REGISTRY, 4 injection functions, shared module principle
- ✅ Deployment pipeline fixed — deploy-pages job, .nojekyll, force push
- ✅ renderer.js sourceLabel/sourceLink — 80+ domain map
- ✅ PR #32 — canonical 9-link nav across all 53 monitor pages
- ✅ Homepage 3-column layout — chatter right panel >1280px
- ✅ Chatter 7/7 — all monitors with 10 items, daily workflows running
- ✅ ESA/AGM/ERM daily collectors built
- ✅ Delta section headings canonical ("Top Items This Issue" across 6 monitors)
- ✅ ARCHITECTURE.md — deployment runbook + shared module principle documented

## Peter action required
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification

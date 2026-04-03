# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-03 session wrap (~09:10 CEST)

## Platform Status
- Site: ✅ Live at asym-intel.info
- Build: ✅ build.yml with proper deploy-pages job (fixed today)
- Staging: ✅ Clean (ahead_by: 0)
- CF Cache: ✅ Purged post-deploy

## Cron IDs (all verified)
| Monitor | Cron ID | Schedule |
|---|---|---|
| WDM | f7bd54e9 | Mon 06:00 UTC |
| GMM | c94c4134 | Tue 08:00 UTC |
| ESA | 0b39626e | Wed 19:00 UTC |
| FCW | b17522c3 | Thu 09:00 UTC |
| AGM | 5ac62731 | Fri 09:00 UTC |
| ERM | ce367026 | Sat 05:00 UTC |
| SCEM | 8cdb83c8 | Sun 18:00 UTC |
| Housekeeping | 7e058f57 | Mon 08:00 UTC |

## GitHub Actions Pipelines (not Computer crons)
**Collectors (daily 06:00/07:00 UTC):** FCW, GMM, SCEM, WDM ✅ | ESA, AGM, ERM ✅ (built today)
**Chatter (daily 06:00 UTC):** All 7 monitors ✅ — 10 items each, data committed today
**Weekly research + Reasoner:** FCW, GMM, SCEM ✅ | ESA, AGM, ERM ❌ not yet built

## Open — Needs next session
1. ESA/AGM/ERM weekly-research + reasoner workflows (only daily collector built)
2. Remaining ~4 unmatched Source → patterns (minor, no functional impact)
3. GMM/ESA calibration annual files (imf-2026, ecfr-2026)
4. Sprint 4 schema items (WDM/SCEM schema-gated renders)
5. PED Sprint 2 (AGM + ERM dashboard audit, ESA mobile font, signal panel contrast GMM/SCEM)

## Open — Peter action required
- ⚠️ Q4: confidence badge visual class (decisions.md)
- ⚠️ Q6: homepage hero image (decisions.md)
- ⚠️ Q7: homepage chatter feed spec (decisions.md)
- ⚠️ Q8: SCEM accent / --critical collision (decisions.md)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ GSC property verification (DNS TXT record)

## Chatter — all live
7/7 monitors: 10 items each, accessible at /monitors/{slug}/data/chatter-latest.json
Homepage chatter column: right panel >1280px, below feed ≤1100px

## Key files changed today
- `.github/workflows/build.yml` — added deploy-pages job, force push, .nojekyll
- `static/monitors/shared/js/nav.js` — v1.3, MONITOR_REGISTRY, 4 injection functions
- `static/monitors/shared/js/renderer.js` — sourceLabel + sourceLink, 80+ domains
- `docs/ARCHITECTURE.md` — shared module principle, deployment pipeline runbook
- `assets/css/main.css` — 3-col homepage, chatter breakpoints
- `layouts/index.html` — chatter column HTML + fetch JS
- All 53 monitor pages — canonical 9-link nav (PR #32)
- 9 dashboard/report files — sourceLink inline source labels
- All 7 chatter workflows + chatter.py + prompts for all monitors
- ESA/AGM/ERM collector pipelines (collect.py, workflow, prompt, pipeline stubs)

# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-03 efficiency sprint wrap (~11:30 CEST)

## Platform Status
- Site: ✅ Live at asym-intel.info
- Build: ✅ Passing
- Staging: ✅ Clean (ahead_by: 0, behind_by: 0)
- nav.js: ✅ v1.3 confirmed live

## Cron IDs (active — all verified)
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
| SCEM verify (one-shot) | a67a9739 | Sun 5 Apr 18:30 UTC |
| WDM verify (one-shot) | 10ddf5f0 | Mon 6 Apr 06:30 UTC |

## DELETED CRONS (do not recreate)
- aec126c5 — Staging guard (deleted 3 Apr). Wrap catches this.
- f78e0c2c — GSC quarterly audit (deleted 3 Apr). Recreate after GSC DNS TXT verified.

## This Session (efficiency sprint)
- ✅ Housekeeping slimmed — HTML structural checks removed (CI enforces them). ~50% fewer steps.
- ✅ Staging guard cron deleted — was running daily for near-zero value.
- ✅ GSC audit cron deleted — GSC unverified; pointless to audit.
- ✅ COMPUTER.md v3.4 — min session size rule, deleted cron table, version bump.
- ✅ docs/monitors/_shared/ deleted — stale pre-v1.3 artefact, nothing referenced it.
- ✅ CRON-001 fix applied to docs/monitors/ cron prompts (AGM/WDM/FCW/GMM).
- ✅ Staging reset clean.

## Open — Next Session
1. ESA/AGM/ERM weekly-research + reasoner workflows (pattern: fcw-weekly-research.yml + fcw-reasoner.yml)
2. Source → pattern cleanup (~3 items in FCW/WDM/SCEM dashboards — minor)
3. PED Sprint 2 — needs Q4/Q6/Q7/Q8 decisions first

## Peter Action Required
- ⚠️ Q4/Q6/Q7/Q8 in docs/ux/decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ GSC property verification — DNS TXT record → then recreate GSC audit cron

## GitHub Actions Pipelines
**Daily Collectors:** All 7 ✅
**Weekly research + Reasoner:** FCW/GMM/SCEM ✅ | ESA/AGM/ERM ❌ not yet built
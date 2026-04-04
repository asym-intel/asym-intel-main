# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-04 final wrap (~19:20 BST)

## Platform Status
- Site: ✅ asym-intel.info live, all dashboards rendering
- Build: ✅ Successful, staging clean (0/0)
- CF Cache: ✅ Zone ID cc419b7519eba04ef0dc6a7b851930c7

## Analyst Cron IDs (all weekly, unchanged)
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

## Synthesiser Status
| Monitor | Output | Notes |
|---|---|---|
| FCW | ✅ Validated v1.1 | |
| ESA | ✅ Full output | |
| ERM | ✅ Full output | |
| GMM | ⚠️ Apostrophe parse error | Prompt fix needed — see next session task 1 |
| WDM | ⚠️ Apostrophe parse error | Prompt fix needed |
| SCEM | ⚠️ Guard blocked | Retry tomorrow |
| AGM | ⚠️ Guard blocked | Retry tomorrow |

All 7 synthesiser workflows: workflow_dispatch only — enable schedules after all pass.

## GMM — Commercial Ring-Fence (4 Apr 2026)
GMM methodology and prompt IP moved to asym-intel-internal/gmm-prompts/.
Published reports and live dashboard remain public.
RULE: Never commit GMM IP to any public repo.
Commercial site architecture note in development-plan.md.

## Pipeline Schedule
- Chatter: rotating daily Mon–Sun 06:00 UTC ✅
- Collectors: rotating daily Mon–Sun 07:00 UTC ✅
- Weekly-research: PAUSED | Reasoner: PAUSED
- Synthesisers: all 7 built, workflow_dispatch only

## Canonical Documents (asym-intel-internal)
- COLLECTOR-ANALYST-ARCHITECTURE.md v2.2
- editorial-strategy.md v1.2
- development-plan.md v1.2 + GMM commercial section
- prompt-improvements.md
- fcw-slimmed-analyst-cron.md
- gmm-prompts/ (GMM IP — never public)

## Housekeeping
Trimmed to 5 steps (204 lines). Runs Monday 08:00 UTC as normal.

## Next Session — First Tasks
1. Fix apostrophe prompt rule in GMM/WDM/SCEM/AGM synthesiser prompts (v1.1)
2. Re-run all 4 after guard clears (after midnight UTC)
3. Once all 7 pass → enable scheduled triggers
4. Recreate FCW Analyst cron using fcw-slimmed-analyst-cron.md
5. Roll slimmed Analyst cron to remaining 6 monitors

## Open — Peter Action Required
- ⚠️ Q4/Q6/Q7/Q8 decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification
- ⚠️ Analytics provider decision: Plausible vs Fathom (before Tier 3)
- ⚠️ GMM commercial site: decide repo structure before building Tier 3 GMM content

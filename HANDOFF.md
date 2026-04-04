# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-04 final wrap (~16:20 BST)

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
| FCW | ✅ Validated v1.1 | Quiet-week, correct output |
| ESA | ✅ Full output | |
| ERM | ✅ Full output | |
| GMM | ⚠️ Apostrophe parse error | Prompt fix needed |
| WDM | ⚠️ Apostrophe parse error | Prompt fix needed |
| SCEM | ⚠️ Guard blocked | Retry tomorrow |
| AGM | ⚠️ Guard blocked | Retry tomorrow |

**Fix needed:** Add "no apostrophes/contractions in JSON values" to GMM/WDM/SCEM/AGM prompts.
**Workflows:** All 7 workflow_dispatch only — enable schedules after all pass manual test.

## Pipeline Schedule (GitHub Actions)
- Chatter: rotating daily Mon–Sun 06:00 UTC
- Collectors: rotating daily Mon–Sun 07:00 UTC
- Weekly-research: PAUSED (FCW/GMM/WDM/SCEM built, ESA/AGM/ERM not built)
- Reasoner: PAUSED (same)
- Synthesisers: All 7 built, workflow_dispatch only

## Canonical Documents (asym-intel-internal)
- `COLLECTOR-ANALYST-ARCHITECTURE.md` v2.2 — pipeline architecture
- `editorial-strategy.md` v1.2 — audience tiers, epistemic hierarchy, access model
- `development-plan.md` v1.2 — build sequence, corrections policy, open decisions
- `prompt-improvements.md` — running quality log
- `fcw-slimmed-analyst-cron.md` — FCW slimmed Analyst task (template for all 7)

## Housekeeping
- Trimmed to 5 steps, 204 lines (was 445) — runs Monday 08:00 UTC as normal
- Estimated ~200 credits/run (was ~400)

## Next Session — First Tasks
1. Fix apostrophe prompt rule in GMM/WDM/SCEM/AGM synthesiser prompts (v1.1)
2. Re-run all 4 after guard clears (after midnight UTC)
3. Once all 7 pass → enable scheduled triggers
4. Recreate FCW Analyst cron using fcw-slimmed-analyst-cron.md
5. Roll slimmed Analyst cron to all 7 monitors

## Open Decisions (from development-plan.md)
- Analytics provider: Plausible vs Fathom (decide before Tier 3)
- Buttondown cadence: manual weekly / automated monthly (recommended)
- API tier timing: defer until audience established

## Peter Action Required
- ⚠️ Q4/Q6/Q7/Q8 decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification

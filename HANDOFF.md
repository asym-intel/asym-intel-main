# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-04 evening session (~22:25 BST)

## Platform Status
- Site: ✅ asym-intel.info live, all dashboards rendering
- Build: ✅ Successful, staging clean (0/0)
- CF Cache: ✅ Zone ID cc419b7519eba04ef0dc6a7b851930c7

## Analyst Cron IDs — ALL SLIM (recreated 4 Apr 2026)
All old crons deleted by Peter. New slim crons created this session.
Each boots from repo prompt file — no inline task logic.

| Monitor | Cron ID | Schedule | Prompt |
|---|---|---|---|
| WDM | adad85f6 | Mon 06:00 UTC | docs/crons/wdm-slimmed-analyst-cron.md |
| GMM | 6efe51b0 | Tue 08:00 UTC | asym-intel-internal/gmm-prompts/gmm-slimmed-analyst-cron.md |
| ESA | 72398be9 | Wed 19:00 UTC | docs/crons/esa-slimmed-analyst-cron.md |
| FCW | 478f4080 | Thu 09:00 UTC | asym-intel-internal/fcw-slimmed-analyst-cron.md |
| AGM | b53d2f93 | Fri 09:00 UTC | docs/crons/agm-slimmed-analyst-cron.md |
| ERM | 0aaf2bd7 | Sat 05:00 UTC | docs/crons/erm-slimmed-analyst-cron.md |
| SCEM | 743bbe21 | Sun 18:00 UTC | docs/crons/scem-slimmed-analyst-cron.md |
| Housekeeping | c725855f | Mon 08:00 UTC | docs/crons/housekeeping.md |

## FCW Schema Migration — Merged (PR #35)
FCW dashboard.html, report.html, overview.html now have dual-schema fallbacks:
- `d.lead_signal || d.signal` — works with both old and new Analyst output
- `signalObj.mf_flags || signalObj.f_flags`
- `d.intelligence_highlights || d.cognitive_warfare`
Merged to main. Staging clean (0/0).

## Synthesiser Status
| Monitor | Output | Notes |
|---|---|---|
| FCW | ✅ Validated v1.1 | |
| ESA | ✅ Full output | |
| ERM | ✅ Full output | |
| GMM | ⚠️ Apostrophe parse error | Prompt rule already in place — re-run after guard clears |
| WDM | ⚠️ Apostrophe parse error | Same — re-run after guard clears |
| SCEM | ⚠️ Empty response | Re-run after guard clears |
| AGM | ⚠️ Empty response | Re-run after guard clears |

Guard clears after midnight UTC 5 April. Re-run GMM/WDM/SCEM/AGM then.
All 7 synthesiser workflows: workflow_dispatch only — enable schedules after all pass.

## COMPUTER.md Updates This Session
- Staging-reset protection rule added (pitfall #17)
- Wrap procedure Steps 5-6 updated to prohibit reset while files await sign-off
- Cron table updated with all 8 new slim IDs + prompt file column

## Pipeline Schedule
- Chatter: rotating daily Mon–Sun 06:00 UTC ✅
- Collectors: rotating daily Mon–Sun 07:00 UTC ✅
- Weekly-research: PAUSED | Reasoner: PAUSED
- Synthesisers: all 7 built, workflow_dispatch only

## Next Session — First Tasks
1. Re-run GMM/WDM/SCEM/AGM synthesisers (guard clears after midnight UTC)
2. Once all 7 pass → enable scheduled triggers
3. Monitor first slim Analyst runs: SCEM Sun 5 Apr, WDM Mon 6 Apr
4. PED Sprint 2: surface Q4/Q6/Q7/Q8 first
5. Analytics: decide Plausible vs Fathom

## Open — Peter Action Required
- ⚠️ Q4/Q6/Q7/Q8 decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification
- ⚠️ Analytics provider decision: Plausible vs Fathom (before Tier 3)
- ⚠️ GMM commercial site: decide repo structure before building Tier 3 GMM content

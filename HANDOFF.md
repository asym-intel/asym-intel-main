# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-05 morning session (~07:45 BST)

## Platform Status
- Site: ✅ asym-intel.info live, all dashboards rendering
- Build: ✅ Successful, staging clean (0/0)
- nav.js: v1.4 (Network link replaces The White Space)

## Analyst Cron IDs — ALL SLIM (recreated 4 Apr 2026)

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

## Synthesiser Status — All 7 Pass
| Monitor | Model | Status |
|---|---|---|
| FCW | sonar-deep-research | ✅ Full output |
| GMM | sonar-deep-research | ✅ Full output (JSON repaired) |
| WDM | sonar-deep-research | ✅ Passed (re-ran with sonar-pro — null_signal on thin inputs, correct) |
| SCEM | sonar-deep-research | ✅ Passed |
| AGM | sonar-deep-research | ✅ Passed |
| ESA | sonar-deep-research | ✅ null_signal (no collector data — correct) |
| ERM | sonar-deep-research | ✅ null_signal (no collector data — correct) |

**GMM root cause (5 Apr):** methodology file missing from workflow. Fixed — now
fetches prompt + methodology + addendum from asym-intel-internal. Not a model issue.

**Next:** Enable scheduled triggers on all 7 synthesiser .yml files.

## Infrastructure Shipped This Session
- `pipeline/synthesisers/synth_utils.py` — shared JSON repair (all 7 scripts)
- `SYNTH_MODEL` env var override — all 7 scripts + WDM/GMM workflow inputs
- GMM workflow fetches methodology + addendum from internal repo
- Empty-string SYNTH_MODEL bug fixed (`or` not default parameter)
- Tiered deployment rules in COMPUTER.md (LOW/MEDIUM/HIGH)
- Staging-reset protection rule (pitfall #17)

## Visual Components Shipped
- SCEM Trajectory Status Grid (NEW-01) — PR #37
- SCEM F-Flag Indicator Matrix (IMPROVE-01) — PR #37
- WDM Country Tracker visibility fix — PR #36
- GMM Fed Funds Path duplicate ID fix — PR #36
- Network link in nav.js v1.4 + Hugo partial

## Pipeline Schedule
- Chatter: rotating daily ✅
- Collectors: rotating daily ✅
- Synthesisers: all 7 built + pass, workflow_dispatch only → enable schedules next session
- Weekly-research: PAUSED | Reasoner: PAUSED

## Next Session — First Tasks
1. Enable scheduled triggers on all 7 synthesiser workflows
2. Monitor first slim Analyst runs: SCEM today 18:00 UTC, WDM Mon 06:00 UTC
3. SCEM visual Sprint 2: NEW-02 (Confidence Summary), NEW-03 (Deviation Heatmap)
4. Homepage network graph section (layouts/index.html)
5. PED Sprint 2: Q4/Q6/Q7/Q8

## Open — Peter Action Required
- ⚠️ GSC sitemap: delete and resubmit in Search Console (sitemap is valid, cached error)
- ⚠️ Q4/Q6/Q7/Q8 decisions.md (gates PED Sprint 2)
- ⚠️ Analytics provider decision: Plausible vs Fathom
- ⚠️ GMM commercial site: decide repo structure before building

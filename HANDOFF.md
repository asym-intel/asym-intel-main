# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-06 morning session (~08:30 BST)

## Platform Status
- Site: ✅ asym-intel.info live, all dashboards rendering
- Build: ✅ Successful, staging clean (0/0)
- nav.js: v1.4 (Network link replaces The White Space)

## Analyst Cron IDs — ALL SLIM

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

## GitHub Actions Pipeline — Full Schedule (as of 6 Apr 2026)

### Collectors — all daily 07:00 UTC (fixed today from single-day rotating)
FCW · GMM · WDM · SCEM · ESA · AGM · ERM — all `0 7 * * *`

### Weekly Research → Reasoner → Synthesiser cascade
| Monitor | Weekly Research | Reasoner | Synthesiser |
|---|---|---|---|
| FCW | Wed 18:00 | Wed 20:00 | Wed 22:00 |
| GMM | Mon 16:00 | Mon 18:00 | Mon 20:00 |
| WDM | Sun 18:00 | PAUSED (stub) | Sun 21:00 |
| SCEM | Sat 06:00 | Sat 08:00 | Sat 10:00 |
| ESA | Tue 18:00 | Tue 20:00 | Wed 09:00 |
| AGM | Thu 18:00 | Thu 20:00 | Thu 22:00 |
| ERM | Fri 16:00 | Fri 18:00 | Fri 20:00 |

**ESA/AGM/ERM weekly-research and reasoner scripts built and committed today.**

## IP-Protected Prompts
- GMM: all prompts in `asym-intel-internal/gmm-prompts/`
- FCW analyst cron: `asym-intel-internal/fcw-slimmed-analyst-cron.md`
- GMM/FCW scripts fetch via `gh api` from internal — NOT local filesystem path

## Pipeline Fixes Applied This Session (6 Apr 2026)
- WDM null_signal root cause diagnosed and fixed (3 issues: collector schedule, prompt quality, weekly-research PAUSED)
- WDM Issue 4 published manually (06:32 UTC)
- WDM brief missing from Hugo content/ — committed separately
- All 6 remaining collectors changed to daily schedule
- FCW/GMM/SCEM weekly-research + reasoner schedules enabled
- ESA/AGM/ERM weekly-research + reasoner scripts built and committed
- GMM collect.py + weekly-research.py prompt-loading bug fixed (was hardcoding local path)
- COMPUTER.md v3.5 — GA table corrected, duplicate section removed, IP note added
- Housekeeping prompt update: IN PROGRESS (this session)

## Next Session — First Tasks
1. Verify FCW weekly-research ran (Wed 18:00 UTC) and reasoner (Wed 20:00 UTC)
2. Verify GMM weekly-research ran (Mon 16:00 UTC) — check today
3. Housekeeping prompt update (was in-progress when this session started)
4. SCEM Visual Sprint 2: NEW-02 (Confidence Quality Summary Bar), NEW-03 (Deviation Heatmap)
5. Homepage network graph section (layouts/index.html)

## Open — Peter Action Required
- ⚠️ GSC sitemap: delete and resubmit in Search Console
- ⚠️ Q4/Q6/Q7/Q8 decisions.md (gates PED Sprint 2)
- ⚠️ Analytics provider decision: Plausible vs Fathom
- ⚠️ GMM commercial site: decide repo structure before building
- ⚠️ Branch protection on main (GitHub repo settings)

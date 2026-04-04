# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-04 session wrap (~15:20 BST)

## Platform Status
- Site: ✅ Live at asym-intel.info
- Build: ✅ build.yml with deploy-pages job
- Staging: ⚠️ 6 files ahead (FCW schema fallbacks — awaiting Peter visual sign-off)
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

## GitHub Actions Pipeline State
**Chatter:** 7/7 rotating daily (Mon-Sun 06:00 UTC) ✅
**Collectors:** 7/7 rotating daily (Mon-Sun 07:00 UTC) ✅
**Synthesisers:** All 7 built, workflow_dispatch only — schedules commented out until all 7 produce FULL_OUTPUT
**Weekly-research:** FCW/GMM/WDM/SCEM — PAUSED
**Reasoner:** FCW/GMM/WDM/SCEM — PAUSED

## Synthesiser Status (post quality audit — 4 Apr 2026)
| Monitor | Status | Ready for rerun? |
|---|---|---|
| FCW | ✅ FULL_OUTPUT validated | — (already working) |
| ESA | ✅ null (no Collector data yet — correct) | Auto-resolves Wed Collector |
| ERM | ✅ null (no Collector data yet — correct) | Auto-resolves Sun Collector |
| GMM | ✅ Fixes committed | Yes — trigger tomorrow |
| WDM | ✅ Fixes committed | Yes — trigger tomorrow |
| SCEM | ✅ Fixes committed | Yes — trigger tomorrow |
| AGM | ✅ Fixes committed | Yes — trigger tomorrow |

## Fixes committed this session (4 Apr 2026)
1. **repair_json corrected** in GMM/WDM/SCEM/AGM — was producing `\'` (invalid JSON); now uses `\u0027`
2. **Apostrophe rule added** to all 7 synthesiser API prompts — prevents bad model output at source
3. **FCW schema fallbacks staged** — dashboard/report/overview now read `d.signal || d.lead_signal`, `mf_flags`, `intelligence_highlights` — BUILD PASSES

## Staged files (awaiting Peter visual sign-off)
- `static/monitors/fimi-cognitive-warfare/dashboard.html`
- `static/monitors/fimi-cognitive-warfare/report.html`
- `static/monitors/fimi-cognitive-warfare/overview.html`
- `docs/monitors/fimi-cognitive-warfare/dashboard.html` (mirror)
- `docs/monitors/fimi-cognitive-warfare/report.html` (mirror)
- `docs/monitors/fimi-cognitive-warfare/overview.html` (mirror)

**Staging URL:** https://staging.asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html

## Open — Next session first tasks
1. Visual sign-off on FCW staging (3 pages) → merge PR → reset staging
2. Trigger GMM/WDM/SCEM/AGM synthesisers (stagger 45s) → verify FULL_OUTPUT
3. If all 4 pass → enable scheduled triggers on all 7 synthesiser .yml files
4. Recreate FCW Analyst cron (delete b17522c3, create from fcw-slimmed-analyst-cron.md)
5. Roll slimmed Analyst cron to all 7 monitors

## Open — Peter action required
- ⚠️ FCW staging sign-off (3 pages — schema fallbacks, no visual change expected)
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification

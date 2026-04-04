# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-04 session wrap (~14:32 BST)

## Platform Status
- Site: ✅ Live at asym-intel.info
- Build: ✅ build.yml with deploy-pages job
- Staging: ✅ Clean
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
**Weekly-research:** FCW/GMM/WDM/SCEM — PAUSED (pending synthesiser validation)
**Reasoner:** FCW/GMM/WDM/SCEM — PAUSED (pending synthesiser validation)
**Synthesisers:** All 7 built, workflow_dispatch only — schedules to enable after validation

## Synthesiser Test Results (2026-04-04)
| Monitor | Status | Notes |
|---|---|---|
| FCW | ✅ Validated v1.1 | Correct quiet-week output, schema fixed |
| ESA | ✅ Full output | All schema fields populated |
| ERM | ✅ Full output | All schema fields populated |
| GMM | ⚠️ JSON parse error | Apostrophe in string at char 13064 — see below |
| WDM | ⚠️ JSON parse error | Apostrophe in string at char 7683 |
| SCEM | ⚠️ Guard blocked | Dated file exists, retry tomorrow |
| AGM | ⚠️ Guard blocked | Dated file exists, retry tomorrow |

**GMM/WDM fix needed:** Model outputs unescaped apostrophes (e.g. "week's") inside JSON string values.
Two options for next session:
A. Add prompt instruction: "Never use apostrophes or contractions in JSON string values. Use full words."
B. Add `json-repair` pip dependency to the workflow and call it before json.loads()
Option A is simpler. Option B is more robust.

## Synthesiser File Locations
| Monitor | Script | Prompt | Workflow | Slimmed cron |
|---|---|---|---|---|
| FCW | pipeline/monitors/fimi-cognitive-warfare/fcw-synthesiser.py | same dir | .github/workflows/fcw-synthesiser.yml | asym-intel-internal/fcw-slimmed-analyst-cron.md |
| GMM-ERM | pipeline/synthesisers/{abbr}/ | same dir | .github/workflows/{slug}-synthesiser.yml | docs/crons/{abbr}-slimmed-analyst-cron.md |

## Methodology — now public
`docs/methodology/` — 14 files (7 full + 7 calibration), CC BY 4.0
Synthesiser scripts load from `docs/methodology/{slug}-full.md` at runtime.

## Open — Next session first tasks
1. Fix GMM/WDM/SCEM/AGM apostrophe issue (prompt fix — 1 line each)
2. Re-run SCEM and AGM (guard clear after midnight UTC)
3. Once all 7 pass manual test → enable scheduled triggers on all 7 synthesisers
4. Recreate FCW Analyst cron using fcw-slimmed-analyst-cron.md
5. Roll slimmed Analyst cron to all 7 monitors

## Open — Peter action required
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification

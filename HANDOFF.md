# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 13:10 UTC | **Last commit (main):** b5972038
**New thread prompt:** "Continuing asym-intel.info maintenance — please load the asym-intel skill first"

---

## FIRST ACTION IN ANY NEW SESSION

```bash
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md --jq '.content' | base64 -d
```

Load the skill: `load_skill("asym-intel", scope="user")`

---

## Repository

- **Main:** `asym-intel/asym-intel-main` → https://asym-intel.info
- **Staging:** `staging` branch → https://staging.asym-intel.info (synced to main ✅)
- **Hugo:** publishDir="docs", buildFuture=true
- **Branch protection:** Blueprint validator required; no direct HTML/CSS/JS to main

---

## Seven Monitors — Status

| Monitor | Abbr | Slug | Accent | Publish | Blueprint | Visual |
|---|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | Mon 06:00 | v2.1 ✅ | ✅ |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | Mon 08:00 | v2.1 ✅ | ✅ |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ |
| AI Governance Monitor | AGM | ai-governance | #3a7d5a | Fri 09:00 | v2.1 ✅ | ✅ |
| Environmental Risks Monitor | ERM | environmental-risks | #4caf7d | Sat 05:00 | v2.1 ✅ | ✅ |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | #dc2626 | Sun 18:00 | v2.1 ✅ | ✅ |

---

## Cron IDs (all active — data-only, no approval needed)

| Monitor | ID | Schedule | Scope |
|---|---|---|---|
| WDM | **db22db0d** | Mon 06:00 UTC | data/ + weekly-brief.md only |
| GMM | **02c25214** | **Tue** 08:00 UTC | data/ + weekly-brief.md only |
| ESA | **0fa1c44e** | Wed 19:00 UTC | data/ + weekly-brief.md only |
| FCW | **879686db** | Thu 09:00 UTC | data/ + weekly-brief.md only |
| AGM | **267fd76e** | Fri 09:00 UTC | data/ + weekly-digest.md only |
| ERM | **3e736a32** | Sat 05:00 UTC | data/ + weekly-brief.md only |
| SCEM | **eb312202** | Sun 18:00 UTC | data/ + weekly-brief.md only |
| Housekeeping | **73452bc6** | Mon 08:00 UTC | read-only audit, 12 checks |

All monitors have a 6-day recency guard in their cron prompts — they will skip silently if fewer than 6 days have elapsed since the last publish.

---

## PENDING TASKS (next session)

### ✅ WDM Category B field schemas — COMPLETE (prior session)
wdm-cron-prompt.md v2.1 already contains full JSON schemas for all 8 Category B fields:
electoral_watch, digital_civil, autocratic_export, state_capture,
institutional_pulse, legislative_watch, research_360.friction_notes, networks.
persistent-state update instructions also cover all 8. No action needed.

### ✅ Visual design pass — COMPLETE
Homepage live signal cards + per-monitor CSS personality. Merged to main.

### ✅ Homepage upgrade — COMPLETE
Domain cards fetch report-latest.json on page load. Merged to main.


### ✅ Schema v2.1 additions — COMPLETE (2026-04-01)
All 7 cron prompts updated on main (commit e2db654). Additions:
- `methodology_url` in meta (per-monitor static URL)
- `flag_definitions` in meta (f_flags for all; mf_flags additionally for FCW)
- `source_date` on FCW campaign/attribution_log source objects
- `summary` field on AGM module_1 Executive Insight items
- `changelog` rule on persistent array items (WDM, GMM, ESA, ERM, SCEM, AGM cross_monitor_flags)
Next cron run for each monitor will naturally produce JSON with the new fields.



### ✅ AGM renderer fixes — COMPLETE (2026-04-01)
Three rendering bugs fixed in AGM report.html + persistent.html (merged b5972038):
- renderCrossMonitor: replaced naive Object.keys/JSON.stringify with proper flags[] renderer
- programme_updates: corrected field names title/summary → programme/update; added lab tag
- arxiv_highlights: corrected field names summary→significance, added url fallback, published/venue/tier meta tags
- inject-network-bar YAML fix also confirmed working on this merge (first successful run)


### ✅ SCEM conflict_context — COMPLETE (2026-04-01)
Schema designed, reviewed, confirmed. Implemented in two commits:
- scem-cron-prompt.md (main, ce1f63e): full schema, data_confidence tiers, source assignments
  for all 10 conflicts, update rules, efficiency rule, Oryx week_delta, Iran F2/F3 note
- persistent.html (main via staging, PR #12): renderer with confidence badges,
  contested ranges, toggleable panel per baseline card
First data expected: SCEM cron run Sun Apr 5 18:00 UTC.

### ✅ Schema audit — COMPLETE (2026-04-01)
Full field audit across all 7 monitors (live JSON vs cron prompt schemas).
Findings and resolutions:
- INFO (7): methodology_url + flag_definitions missing from all meta — expected, appear on next cron run
- INFO (2): FCW source_date, AGM module_1 summary — expected, v2.1 fields appear on next run
- FIXED: ESA actor field promoted to REQUIRED with renderer context in prompt
- FIXED: FCW signal schema expanded from {} stub to full field definition
- FIXED: FCW actor_tracker summary marked REQUIRED with renderer consequence note
- CLEAN: GMM, AGM, ERM, SCEM — no gaps

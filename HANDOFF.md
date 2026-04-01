# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 12:45 UTC | **Last commit (main):** e2db654
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
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | Mon 06:00 | v2.1 ✅ | ⚠️ Build 2 pending |
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

### Priority 1 — WDM cron prompt: add Category B field schemas
Now that Build 2 HTML is live, extend wdm-cron-prompt.md so the WDM cron
starts populating: electoral_watch, digital_civil, autocratic_export,
state_capture, institutional_pulse, legislative_watch, research_360.friction_notes, networks.
This is a cron prompt edit — commits directly to main, no staging needed.

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

### Priority 4 — Schema audit
Check field alignment across all 7 monitors after renderer fixes.

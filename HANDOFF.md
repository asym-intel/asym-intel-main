# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 17:32 UTC | **Last commit (main):** 372d5104
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
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | **Mon 13 Apr** | v2.1 ✅ | ✅ + choropleth map |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | **Tue** 08:00 | v2.1 ✅ | ✅ + score history chart |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ (4 UX fixes merged today) |
| AI Governance Monitor | AGM | ai-governance | #3a7d5a | Fri 09:00 | v2.1 ✅ | ✅ + model tier layout |
| Environmental Risks Monitor | ERM | environmental-risks | #4caf7d | Sat 05:00 | v2.1 ✅ | ✅ |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | #dc2626 | Sun 18:00 | v2.1 ✅ | ✅ + I1-I6 chart + conflict_context (data: Sun Apr 5) |

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

## ESA — Changes merged today (2026-04-01, PR #16 + direct commits)

1. **archive.html** — View links fixed (were 404ing; now use source_url from archive.json)
2. **dashboard.html** — Lead Signal KPI card: first 4 words at body size + scroll-to-signal, not raw truncated title at text-2xl
3. **report.html** — Signal block darkened to #2d5a7e for WCAG AA contrast; Member State tracker now shows flag emoji + full country name + coloured status badge + change detail + source link
4. **persistent.html** — Timeline redesigned as grouped visual timeline (month headers, connector line, date pills, module badges); ceasefire_probability_ukraine removed from KPI cards; lagrange_point_progress renamed "Autonomy Score"; scorecard description text linked to Compossible series
5. **esa-cron-prompt.md** — Explicit KPI field allowlist added; ceasefire_probability_ukraine explicitly excluded (belongs to SCEM)

---

## PENDING TASKS (next session)

### Priority 1 — FCW campaign timeline (P5)
BLOCKED until FCW cron run Thu Apr 9 populates start_date on campaigns.
After Apr 9: build horizontal Gantt-style Chart.js timeline on FCW dashboard.
start_date field is now in the cron prompt (commit 724f0ae).

### Priority 2 — Verify first conflict_context data (SCEM)
SCEM cron runs Sun Apr 5 18:00 UTC — first run with conflict_context schema.
Check persistent.html after that run: "Conflict context ▸" buttons should appear
on each baseline card. Verify data quality and renderer for all 10 conflicts.

### Priority 3 — Mobile/tablet audit of new visual work
All 4 dashboard visual enhancements + homepage signal cards + per-monitor
personality CSS have not been audited on mobile. Quick visual review of staging
before the next significant build cycle.

### Priority 4 — Schema audit: v2.1 fields in production
methodology_url, flag_definitions, changelog, summary (AGM), source_date (FCW)
were added to all 7 cron prompts. First cron runs after today will produce these
fields. Verify after each monitor's first run that fields appear correctly.

### DEFERRED — requires data first
- FCW geospatial campaign map: needs lat/lng added to campaign schema
- SCEM humanitarian impact charts: wait for ≥2 issues of conflict_context data
- D3 force-directed FCW attribution network: Phase 3 if warranted

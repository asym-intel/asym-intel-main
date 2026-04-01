# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 18:15 UTC | **Last commit (main):** see below
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
- **Staging:** `staging` branch → https://staging.asym-intel.info (28 commits ahead of main)
- **Hugo:** publishDir="docs", buildFuture=true
- **Branch protection:** Blueprint validator required; no direct HTML/CSS/JS to main

---

## Seven Monitors — Status

| Monitor | Abbr | Slug | Accent | Publish | Blueprint | Visual |
|---|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | **Mon 13 Apr** | v2.1 ✅ | ✅ + choropleth map |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | **Tue** 08:00 | v2.1 ✅ | ✅ + tail risk heatmap (gauge removed) |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ (4 UX fixes + contrast fix) |
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

---

## PR #17 — OPEN (staging → main, awaiting user sign-off)

Contains two sets of changes:

### A. Global WCAG AA contrast fix (all 7 monitors)
- `shared/css/base.css` — signal-block !important, kpi-card__value + card__label darkened with color-mix(65%,#000)
- `european-strategic-autonomy/assets/monitor.css` — removed background linear-gradient override
- `conflict-escalation/assets/monitor.css` — removed background rgba(0.06) override
- `european-strategic-autonomy/dashboard.html` — removed inline color:var(--monitor-accent) on kpi-lead-signal
- COMPUTER.md v1.4 — CONTRAST RULES + SIGNAL-BLOCK OWNERSHIP architectural rules added (already on main)

### B. GMM tail risk heatmap
- `macro-monitor/dashboard.html` — gauge replaced with 3×3 likelihood × impact heatmap
- `macro-monitor/data/report-latest.json` — tail_risks backfilled for Issue 8 (already on main + staging)
- `macro-monitor/gmm-cron-prompt.md` — tail_risks schema + formalised methodology (already on main)

**Verified on staging:** all 7 signal-blocks ✅, KPI card values ✅, GMM heatmap ✅

---

## Changes already on main (not in PR)

- `COMPUTER.md` v1.4 — contrast rules, signal-block ownership
- `macro-monitor/data/report-latest.json` — tail_risks backfilled
- `macro-monitor/gmm-cron-prompt.md` — tail_risks schema

---

## PENDING TASKS (next session)

### Priority 1 — Merge PR #17
Awaiting user visual sign-off on staging. Once approved, squash-merge to main.

### Priority 2 — FCW campaign timeline (P5)
BLOCKED until FCW cron run Thu Apr 9 populates start_date on campaigns.
After Apr 9: build horizontal Gantt-style Chart.js timeline on FCW dashboard.
start_date field is now in the cron prompt (commit 724f0ae).

### Priority 3 — Verify first conflict_context data (SCEM)
SCEM cron runs Sun Apr 5 18:00 UTC — first run with conflict_context schema.
Check persistent.html after that run: "Conflict context ▸" buttons should appear
on each baseline card. Verify data quality and renderer for all 10 conflicts.

### Priority 4 — GMM heatmap: MED/LOW impact cells
Current backfilled data has all 6 tail risks in HIGH impact row. Next cron run
(Tue Apr 7) will produce fresh tail_risks — check if LLM naturally distributes
across all three impact bands. If not, review the impact formula in the prompt.

### Priority 5 — Mobile/tablet audit
All visual enhancements + heatmap not audited on mobile. Quick review of staging.

### DEFERRED — requires data first
- FCW geospatial campaign map: needs lat/lng added to campaign schema
- SCEM humanitarian impact charts: wait for ≥2 issues of conflict_context data

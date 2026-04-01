# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 07:45 UTC | **Last commit (main):** 936d31d7
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
| GMM | **02c25214** | Mon 08:00 UTC | data/ + weekly-brief.md only |
| FCW | **879686db** | Thu 09:00 UTC | data/ + weekly-brief.md only |
| ESA | **0fa1c44e** | Wed 19:00 UTC | data/ + weekly-brief.md only |
| AGM | **267fd76e** | Fri 09:00 UTC | data/ + weekly-digest.md only |
| ERM | **3e736a32** | Sat 05:00 UTC | data/ + weekly-brief.md only |
| SCEM | **eb312202** | Sun 18:00 UTC | data/ + weekly-brief.md only |
| Housekeeping | **73452bc6** | Mon 08:00 UTC | read-only audit, 12 checks |

---

## PENDING TASKS (next session)

### Priority 1 — WDM Build 2 (Category B sections)
HTML files already prepared in workspace — push to staging → verify → PR to main → extend cron prompt.
Fields to add: `electoral_watch`, `digital_civil`, `autocratic_export`, `state_capture`,
`institutional_pulse`, `legislative_watch`, `research_360.friction_notes`, `networks`
Workspace files: `/home/user/workspace/wdm-report-new.html`, `wdm-persistent-new.html`

### Priority 2 — Visual design quality pass (monitor pages)
From the session discussion — monitors need more individual character:
- More use of images (SVG illustrations, flag maps)
- Better contrast and colour variety per monitor
- GMM: tick marks and currency symbols on chart axes
- Overall: too text-heavy, needs more visual scanning points
This is a design/UX task, not a data task. Requires staging-first.

### Priority 3 — Homepage visual upgrade
The homepage (`asym-intel.info`) is functional but plain. Agreed to revisit with:
- Monitor cards with live signal pull
- More visual hierarchy
- Better mobile layout

### Priority 4 — WDM cron prompt extension (after Build 2 HTML is merged)
Add Category B field schemas to wdm-cron-prompt.md so the cron starts populating them.

### Priority 5 — Schema audit across all 7 monitors
Check if any monitor JSON is missing fields that the HTML now expects (e.g. AGM renderer
mismatches fixed this session — check others still have clean field alignment).

---

## Architecture State (Blueprint v2.1 — locked)

✅ 12/12 validator checks passing on main
✅ nav.js in `<head>` on all 57 pages
✅ Chart.js CDN in `<head>` on all pages using charts
✅ overflow-x:clip everywhere (not hidden) — sticky nav works on all mobile
✅ Network bar: position:fixed, full-bleed, always visible on mobile
✅ body{padding-top:40px} in base.css + main.css
✅ site-nav: About + Subscribe only (no brand duplication, no hamburger, no Monitors)
✅ main branch protection active
✅ COMPUTER.md v1.2 + asym-intel skill in user library
✅ 8 crons active with hard file-scope constraints

---

## Key Technical Rules (do not break)

1. **overflow-x: clip — never hidden** on body, monitor-layout, monitor-main
   `overflow:hidden` on a parent silently breaks `position:sticky` on children (mobile)
2. **nav.js in `<head>`** — must be before `</head>`, after theme.js
3. **Chart.js CDN before charts.js wrapper** in `<head>`
4. **Network bar: position:fixed** — not sticky — on both Hugo and monitor pages
5. **site-nav**: About + Subscribe only; no brand, no SVG, no Monitors, no hamburger
6. **Cron tasks**: data/ and content/monitors/{slug}/ only — no HTML/CSS/JS ever
7. **staging-first** for all HTML/CSS/JS/layout changes
8. **monitor.css**: ≤40 lines, accent tokens only
9. **archive.json**: append-only, never truncate
10. **schema_version: "2.0"** in all JSON files

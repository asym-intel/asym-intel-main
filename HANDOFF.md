# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 07:30 UTC | **Last commit (main):** 6509a7b0
**New thread prompt:** "Continuing asym-intel.info maintenance — please load the asym-intel skill first"

---

## FIRST ACTION IN ANY NEW SESSION

```bash
# Load the working agreement
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d
```

Load the skill: `load_skill("asym-intel", scope="user")`

---

## Repository

- **Main:** `asym-intel/asym-intel-main` → `docs/` on `main` → https://asym-intel.info
- **Staging:** `staging` branch → https://staging.asym-intel.info
- **Hugo:** publishDir="docs", buildFuture=true, baseURL="https://asym-intel.info/"
- **Staging is 4 commits ahead of main** — homepage site-nav fix awaiting review/merge

---

## Seven Monitors — Status

| Monitor | Abbr | Slug | Accent | Publish | Blueprint | Visual |
|---|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | Mon 06:00 | v2.1 ✅ | ⚠️ Build 2 pending |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | Mon 08:00 | v2.1 ✅ | ✅ Complete |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ Complete |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ Complete |
| AI Governance Monitor | AGM | ai-governance | #3a7d5a | Fri 09:00 | v2.1 ✅ | ✅ Complete |
| Environmental Risks Monitor | ERM | environmental-risks | #4caf7d | Sat 05:00 | v2.1 ✅ | ✅ Complete |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | #dc2626 | Sun 18:00 | v2.1 ✅ | ✅ Complete |

---

## Outstanding Tasks

### 1. Homepage site-nav fix — ON STAGING, AWAITING MERGE ⏳
**What:** Removed duplicate brand/SVG from white nav bar; Monitors+About+Subscribe now right-aligned
**Branch:** staging (4 commits ahead of main)
**Check:** https://staging.asym-intel.info — confirm homepage looks correct, then merge

### 2. WDM Build 2 — Category B sections
**Status:** HTML files prepared in workspace but NOT pushed anywhere yet:
  - `/home/user/workspace/wdm-report-new.html`
  - `/home/user/workspace/wdm-persistent-new.html`
**Category B fields** (not yet in JSON schema or HTML):
  - electoral_watch, digital_civil, autocratic_export, state_capture
  - institutional_pulse, legislative_watch, research_360.friction_notes, networks
**Next step:** Push both to `staging` branch → verify → PR to main → then update WDM cron prompt

---

## Cron IDs

| Monitor | ID | Schedule |
|---|---|---|
| WDM | **db22db0d** | Mon 06:00 UTC |
| GMM | **02c25214** | Mon 08:00 UTC |
| FCW | **879686db** | Thu 09:00 UTC |
| ESA | **0fa1c44e** | Wed 19:00 UTC |
| AGM | **267fd76e** | Fri 09:00 UTC |
| ERM | **3e736a32** | Sat 05:00 UTC |
| SCEM | **eb312202** | Sun 18:00 UTC |
| Housekeeping | **73452bc6** | Mon 08:00 UTC |

---

## Architecture State (Blueprint v2.1 — all enforced)

- `main` branch protection: Blueprint validator required, no direct HTML pushes
- `staging` branch: always sync to main before starting new work
- nav.js in `<head>` on all 57 pages ✅
- Chart.js CDN in `<head>` on all pages using charts ✅
- body{padding-top:40px} in base.css ✅
- network-bar{position:fixed} in main.css ✅
- All 12 validator checks passing ✅
- COMPUTER.md at repo root ✅
- asym-intel skill saved to user library ✅
- 8 cron schedules active with hard file-scope constraints ✅

---

## Key Technical Lessons (this session)

1. staging-first: ALL HTML/CSS/JS to staging before main — enforced by branch protection
2. COMPUTER.md + asym-intel skill = working agreement survives session handover
3. Blueprint validator catches real bugs (caught FCW future date, 2× schema_version errors)
4. nav.js must be in `<head>` — mobile bar requires pre-paint injection
5. `position:fixed` for network bar on ALL pages (Hugo and monitor)
6. Chart.js CDN must be in `<head>` before charts.js wrapper (or deferred via async)
7. Hugo `--buildFuture` required — cron publish time races with Hugo build clock
8. Hamburger dropdown: `height:auto`, `min-height:0`, `align-content:flex-start` — no blank overlay
9. site-nav: brand/SVG belong ONLY in network bar; white nav bar = links only
10. Cron schedules have hard file-scope constraints in Computer task description itself
11. GMM monitor.css had 200+ lines — component styles belong in base.css
12. archive.json is append-only — never truncate or overwrite

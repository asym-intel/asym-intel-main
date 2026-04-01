# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 07:00 UTC | **Last commit:** e2efa166
**New thread prompt:** "Continuing asym-intel.info maintenance — please load the asym-intel skill first"

---

## FIRST ACTION IN ANY NEW SESSION

```bash
# Load the working agreement
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d
```

The `asym-intel` skill is saved to user skill library. Load it:
`load_skill("asym-intel", scope="user")`

---

## Repository

- **Main:** `asym-intel/asym-intel-main` → served from `docs/` on `main` branch → https://asym-intel.info
- **Staging:** `staging` branch → https://staging.asym-intel.info (auto-deploys on push)
- **Hugo:** publishDir = "docs", buildFuture=true, baseURL = "https://asym-intel.info/"

---

## Seven Monitors — Status

| Monitor | Abbr | Slug | Accent | Publish | Blueprint | Visual |
|---|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | Mon 06:00 | v2.1 ✅ | ✅ Build 2 partial |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | Mon 08:00 | v2.1 ✅ | ✅ Complete |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ Complete |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ Complete |
| AI Governance Monitor | AGM | ai-governance | #3a7d5a | Fri 09:00 | v2.1 ✅ | ✅ Complete |
| Environmental Risks Monitor | ERM | environmental-risks | #4caf7d | Sat 05:00 | v2.1 ✅ | ✅ Complete |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | #dc2626 | Sun 18:00 | v2.1 ✅ | ✅ Complete |

---

## Priority Outstanding Tasks

### 1. nav.js → move to `<head>` — ON STAGING, AWAITING REVIEW ✅
**Why:** nav.js currently loads at bottom of `<body>`. The network bar is injected after content renders → invisible on mobile first paint. Moving to `<head>` fixes this.
**How:** Edit all 57 `static/monitors/**/*.html` pages to move `<script src="../shared/js/nav.js">` from bottom of `<body>` to `<head>`.
**Branch:** Pushed to `staging` — verify at https://staging.asym-intel.info/monitors/macro-monitor/dashboard.html on mobile, then PR to main.

### 2. Mobile hamburger menu overlay — ON STAGING, AWAITING REVIEW ✅
**Issue:** When hamburger opens on mobile, `.monitor-nav__links--open` renders as a full-screen overlay covering page content.
**Fix:** In `base.css`, add `max-height: calc(100vh - 40px - 52px)` and `overflow-y: auto` to `.monitor-nav__links` mobile open state. Also ensure it doesn't cover the whole viewport.
**Branch:** `staging` → verify → PR to main.

### 3. WDM Build 2 — complete Category B sections
**Status:** HTML work was prepared in workspace (`/home/user/workspace/wdm-report-new.html`, `wdm-persistent-new.html`) but NOT yet pushed. The cron prompt also needs extending.
**Category B fields** (not yet in JSON schema):
- electoral_watch, digital_civil, autocratic_export, state_capture
- institutional_pulse (10 entries), legislative_watch (11 entries)
- research_360.friction_notes (5 active), networks
**Approach:** Push HTML files to `staging` first, verify, then PR to main. Then update cron prompt.

### 4. Session-pushed changes that bypassed staging (KNOWN DEBT)
This entire session pushed directly to `main` before the staging rule was properly encoded. The main branch now has branch protection. Future sessions must use staging. No rollback needed — all changes were verified to build successfully.

---

## What Was Fixed/Built This Session

### Platform Architecture (Blueprint v2.1)
- ✅ `nav.js` v1.1: auto-injects network bar + offset styles; `setupSiteNavHamburger()` added
- ✅ `base.css`: `body{padding-top:40px}`, explicit `monitor-nav{top:40px}`, redesigned intel-item/card components, direction arrows, subsection-title, section-label with accent
- ✅ `main.css` (Hugo): `network-bar{position:fixed}`, full-bleed inner, `body{padding-top:40px}`, `site-nav` hamburger CSS
- ✅ `site-header.html`: replaced with canonical monitor-nav pattern (SVG + name left, links right)
- ✅ `baseof.html`: inline hamburger script for Hugo pages

### Centralisation Fixes
- ✅ `inject-network-bar.yml`: now covers all 8 pages per monitor (was dashboard only)
- ✅ `validate-blueprint.py`: 12 structural checks, blocks build on FAIL
- ✅ `build.yml`: validate job runs before Hugo build; `--buildFuture` added
- ✅ `cron-wrapper-instructions.md`: all 7 monitors listed, staging rule documented
- ✅ `housekeeping-cron-prompt.md`: repo-backed, 9 checks + staging audit check
- ✅ Housekeeping cron `73452bc6`: Mondays 08:00 UTC, reads from repo
- ✅ `main` branch protection: Blueprint validator required, no direct HTML pushes
- ✅ `COMPUTER.md`: canonical working agreement at repo root
- ✅ `asym-intel` skill: saved to user skill library

### Visual Enhancements (all pushed to main — session pre-dated staging rule)

**GMM:** SVG score gauge, regime badge, asset class bar chart (Chart.js), conviction sparkline + regime timeline
**WDM:** Severity score bars, tier distribution strip (Chart.js), weekly brief prose section, country severity league table (top 5 cards)
**SCEM:** F-flag matrix (F1–F7 visual board), conflict escalation cards, roster status icons, global escalation gauge
**FCW:** Cognitive warfare threat badge (pulsing), actor activity matrix, attribution donut (Chart.js), campaign Gantt timeline
**ESA:** Lagrange scorecard radar chart (Chart.js), KPI trend bars, member state tracker grid, autonomy score arc
**AGM:** EU AI Act pipeline tracker (countdown + layer nodes), risk vector heat grid, model tier pyramid, concentration index bars
**ERM:** Planetary boundary chart on dashboard, tipping system flags alarm board, risk category strip, attribution gap tracker

### Data Fixes (validator caught these)
- ✅ FCW `report-latest.json`: future date `2026-04-02` → `2026-04-01` (validator caught)
- ✅ SCEM `report-latest.json`: schema_version `1.0-corrected` → `2.0`
- ✅ ERM `report-latest.json`: schema_version `1.0` → `2.0`

---

## Cron IDs

| Cron | ID | Schedule | Reads from |
|---|---|---|---|
| WDM | **db22db0d** | Mon 06:00 UTC | wdm-cron-prompt.md |
| GMM | **02c25214** | Mon 08:00 UTC | gmm-cron-prompt.md |
| FCW | **879686db** | Thu 09:00 UTC | fcw-cron-prompt.md |
| ESA | **0fa1c44e** | Wed 19:00 UTC | esa-cron-prompt.md |
| AGM | **267fd76e** | Fri 09:00 UTC | agm-cron-prompt.md |
| ERM | **3e736a32** | Sat 05:00 UTC | erm-cron-prompt.md |
| SCEM | **eb312202** | Sun 18:00 UTC | scem-cron-prompt.md |
| Housekeeping | **73452bc6** | Mon 08:00 UTC | housekeeping-cron-prompt.md |

---

## Key Technical Lessons (additions this session)

11. Staging-first: ALL HTML/CSS/JS goes to staging branch before main — now enforced by branch protection
12. COMPUTER.md + asym-intel skill = working agreement survives session handover
13. Blueprint validator catches real bugs: caught FCW future date, 2× schema_version errors
14. nav.js must be in `<head>` not bottom of `<body>` — mobile bar requires pre-paint injection
15. `position:fixed` for network bar on ALL pages (Hugo and monitor) — sticky scrolls away
16. GMM monitor.css was 200+ lines — component styles belong in base.css
17. Hugo `--buildFuture` required: cron publish time races with Hugo build clock
19. Cron schedules now have hard file-scope constraints in the Computer task description itself — agents cannot touch HTML/CSS/JS even if confused by prompt content
18. Two nav systems (Hugo partials + static HTML nav.js) must share the same CSS architecture

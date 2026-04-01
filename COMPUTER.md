# COMPUTER.md — Asymmetric Intelligence Working Agreement
# Version: 1.3 — 1 April 2026
# This file is the canonical working agreement for all Computer sessions
# touching asym-intel.info. READ THIS BEFORE DOING ANYTHING ELSE.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — ALWAYS READ THIS FILE FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

At the start of every session, fetch and read this file:

  gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
    --jq '.content' | base64 -d

Then fetch the handoff brief for current task state:

  gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md \
    --jq '.content' | base64 -d

Do not begin any work until both files have been read.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CENTRALISED SHARED ASSETS — DO NOT DUPLICATE INLINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

These are defined ONCE in shared/ files. Never copy them inline into individual pages:

CSS in static/monitors/shared/css/base.css:
  - Search page styles (.search-wrap, .search-input-el, .search-result etc.)
  - Network bar link strip (.nb-links)
  - Font size tokens (--text-xs, --text-sm, --text-base, --text-min etc.)
  - All layout, component, and token CSS

JS in static/monitors/shared/js/renderer.js:
  - renderCrossMonitorFlags(cmf) — canonical CMF renderer, handles flags[] array
  - esc(str) / escHtml(str) — HTML escaping (use esc() in new code)
  - AsymRenderer.flag(code) — country flag emoji

JS in static/monitors/shared/js/nav.js:
  - Network bar injection, hamburger, scroll-spy, tab panels

When a bug is fixed in a shared file, it propagates to all 7 monitors automatically.
When a fix is made inline in one page, it must be manually replicated — this is the
root cause of rendering inconsistencies across monitors.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPLOYMENT RULE — STAGING FIRST, ALWAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALL changes to HTML, CSS, JS, Hugo layouts, or GitHub Actions workflows
MUST go to the STAGING branch first.

NEVER push HTML/CSS/JS/layout changes directly to main.

Workflow:
  1. Commit changes to the `staging` branch
  2. Verify at https://staging.asym-intel.info (wait for build)
  3. Check on both desktop and mobile before proceeding
  4. Open PR: staging → main
  5. Blueprint validator runs automatically (must pass)
  6. Merge only after explicit sign-off from the user

EXCEPTIONS (may commit directly to main):
  - JSON data files only — cron tasks do NOT need approval to publish data
    Each monitor cron publishes its data on schedule autonomously: report-latest.json, persistent-state.json,
    archive.json, report-{DATE}.json
  - Hugo brief markdown files: content/monitors/*/*.md
  - This file (COMPUTER.md) and HANDOFF.md
  - docs/ directory (auto-committed by github-actions[bot] build)

The `main` branch has protection rules:
  - Blueprint validator must pass before merge
  - No force pushes
  - PRs required for HTML/CSS/JS changes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECTURE — WHAT LIVES WHERE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHARED LIBRARY (one change propagates to all 7 monitors):
  static/monitors/shared/css/base.css     — all layout, components, tokens
  static/monitors/shared/js/nav.js        — network bar injection, hamburger,
                                            scroll-spy, tab panels
  static/monitors/shared/js/renderer.js  — AsymRenderer, AsymPersistent, flags
  static/monitors/shared/js/charts.js    — Chart.js wrappers

PER-MONITOR (accent colour only):
  static/monitors/{slug}/assets/monitor.css  — MAX 40 lines, accent tokens only
  static/monitors/{slug}/assets/monitor.css  NEVER contains component styles

HUGO LAYOUTS (for content pages — homepage, briefs, methodology):
  layouts/partials/network-bar.html  — dark top bar (position:fixed)
  layouts/partials/site-header.html — second-tier nav (sticky, top:40px)
  layouts/_default/baseof.html      — shell for all Hugo pages
  assets/css/main.css               — Hugo page styles

CANONICAL NAV ARCHITECTURE (Blueprint v2.1):
  Network bar: position:fixed, height:40px, full-bleed, always visible
  Body offset:  padding-top:40px on ALL pages (base.css + main.css)
  overflow-x:   ALWAYS clip (never hidden) on body, monitor-layout, monitor-main
                overflow:hidden on a parent breaks position:sticky on children
  Monitor-nav:  position:sticky, top:40px
  Site-nav:     position:sticky, top:40px (Hugo pages only)
  nav.js:       loaded in <head> (not bottom of body) — injects bar before paint

TYPOGRAPHY FLOOR:
  --text-min = var(--text-xs) = clamp(0.8125rem, ...) defined in base.css
  NEVER hardcode font-size below var(--text-min) (e.g. 0.7rem, 0.65rem, 0.62rem)
  Use var(--text-min) for badges, tags, metadata labels
  Use var(--text-xs) or larger for all body/content text
  Violation = text that becomes illegible on mobile

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRON TASK RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER.
Cron tasks write ONLY:
  - data/report-latest.json
  - data/report-{DATE}.json
  - data/archive.json
  - data/persistent-state.json
  - content/monitors/{slug}/{DATE}-weekly-brief.md

All 7 monitor crons read their prompts from the repo:
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{SLUG}/{ABBR}-cron-prompt.md \
    --jq '.content' | base64 -d

Housekeeping cron (73452bc6): Mondays 08:00 UTC
  Reads: static/monitors/housekeeping-cron-prompt.md
  Runs 12 structural checks. Notifies only on WARN/FAIL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BLUEPRINT v2.1 — STANDARD PAGE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8 standard pages per monitor:
  overview, dashboard, report, archive, persistent, about, methodology, search
  AGM also has: digest

Every HTML page MUST have:
  <script src="../shared/js/nav.js"> in <head> (NOT bottom of body)
  <link rel="stylesheet" href="../shared/css/base.css">
  <link rel="stylesheet" href="assets/monitor.css">

Every page using Chart.js MUST have in <head>:
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js">
  BEFORE <script src="../shared/js/charts.js">

NO page may contain:
  - Inline <style>body{padding-top:40px</style> (base.css owns this)
  - Inline <nav data-asym-network-bar> HTML (nav.js injects this)
  - Component styles in monitor.css (base.css owns all components)

Signal field: always object {headline, body, source_url}
Date rule:    always today's UTC date; never future dates
Schema:       schema_version: "2.0" in all JSON files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CI VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every push runs .github/validate-blueprint.py (12 checks).
A FAIL blocks the build — fix before merging.
WARNs are printed but do not block.

Checks include: page existence, nav.js presence, base.css presence,
monitor.css size, JSON validity, schema_version, future dates,
stale inline bars, body padding-top, network-bar fixed positioning.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KNOWN OUTSTANDING TASKS (update HANDOFF.md for specifics)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. nav.js must be moved from bottom of <body> to <head> on all 57 pages
   → Staging branch, then PR to main
   → This fixes mobile network bar not appearing on first paint

2. Mobile hamburger menu opens as full-screen overlay — needs CSS fix
   → monitor-nav__links needs max-height + proper z-index
   → Staging branch, then PR to main

3. WDM Build 2 — report.html + persistent.html Category B sections
   → In progress (see HANDOFF.md)

4. Handoff brief (HANDOFF.md) needs updating at end of each session

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPDATING THIS FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When a new architectural decision is made, update this file immediately.
This file may be committed directly to main (it is not HTML/CSS/JS).
Bump the version number and date at the top.

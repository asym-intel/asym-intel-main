# COMPUTER.md — Asymmetric Intelligence Working Agreement
# Version: 1.9 — 1 April 2026
# This file is the canonical working agreement for all Computer sessions
# touching asym-intel.info. READ THIS BEFORE DOING ANYTHING ELSE.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — ALWAYS READ THIS FILE FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

At the start of every session, fetch and read ALL of these:

  gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
    --jq '.content' | base64 -d

  gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md \
    --jq '.content' | base64 -d

  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/anti-patterns.json \
    --jq '.content' | base64 -d

  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/site-decisions.json \
    --jq '.content' | base64 -d

Do not begin any work until all four files have been read.

anti-patterns.json: known HTML/CSS/JS errors — check before writing any code.
site-decisions.json: WHY things are built the way they are — check before changing architecture.

INTERNAL METHODOLOGY REPO (private — asym-intel/asym-intel-internal):
  Full canonical specs for all 7 monitors live in the PRIVATE repo:
    gh api /repos/asym-intel/asym-intel-internal/contents/methodology/{slug}-full.md \
      --jq '.content' | base64 -d

  Slugs: wdm, macro-monitor, fimi-cognitive-warfare, european-strategic-autonomy,
         ai-governance, environmental-risks, conflict-escalation

  Read the relevant monitor's spec BEFORE any sprint work on that monitor.
  These contain scoring rubrics, source hierarchies, formula weights, and
  analytical frameworks that are not in the cron prompts.
  This repo is private and will NOT appear in web searches or public repo lists.
  Always use api_credentials=["github"] to access it.


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

SHARED INTELLIGENCE LAYER (read by all cron agents at Step 0B):
  static/monitors/shared/intelligence-digest.json
    — Cross-monitor flag aggregator. Compiled weekly by housekeeping cron
      from all 7 monitors' cross_monitor_flags. Every cron agent filters
      for flags relevant to its domain before beginning research.
      Never edit manually — housekeeping cron owns this file.

  static/monitors/shared/schema-changelog.json
    — Machine-readable record of all schema additions across all monitors.
      Each entry: id, date, monitor, field, description, required_from_issue.
      Cron agents read this to know exactly what they must produce.
      When adding any new field to any cron prompt, ADD AN ENTRY HERE.
      Append-only — never delete entries.

  static/monitors/shared/monitor-schema-requirements.json
    — Declarative spec of required fields per monitor. Housekeeping cron
      (Check 13) validates each report-latest.json against this weekly.
      When the cron prompt schema changes, UPDATE THIS FILE to match.

  docs/audits/
    — Domain expert audit files per monitor + master-action-plan.md.
      Updated with ✅/⏸ status as sprint items are implemented.
      All 7 audits completed 2026-04-01.

STEP 0B RULE — ALL CRON AGENTS:
  Every cron agent MUST read intelligence-digest.json and schema-changelog.json
  at Step 0B (after loading own persistent-state, before research). This is
  how adjacent-monitor signals propagate into each agent's analysis.

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
  --text-min = var(--text-xs) = clamp(0.8125rem, ...) ≈ 13px — defined in base.css
  NEVER hardcode font-size below var(--text-min) ANYWHERE:
    • In <style> blocks
    • In monitor.css
    • In JavaScript innerHTML strings: style="font-size:0.65rem" ← WRONG
    • In inline style= attributes in static HTML
  Use var(--text-min) for: badges, tags, metadata, timestamps, chart axis labels
  Use var(--text-xs) or larger for: all body/content/summary text
  Violation = illegible text on mobile

  VALIDATOR SCOPE LIMITATION: Check 19 only catches <style> block violations.
  JavaScript-generated font sizes (innerHTML strings) are invisible to the validator.
  Catch those via: anti-patterns.json FE-006 + visual sign-off on every PR.

CONTRAST RULES (WCAG AA — apply globally, never fix piecemeal):
  Raw --monitor-accent fails WCAG AA on white for 5 of 7 monitors (WDM/GMM/FCW/ESA/ERM).
  base.css uses color-mix(in srgb, var(--monitor-accent) 65%, #000) wherever accent
  appears on a white/surface background. This applies to:
    .signal-block { background } — dark bg, white text (darkened 35%)
    .kpi-card__value { color }   — accent text on white card
    .card__label { color }       — accent label text on white card
  When adding any new element that uses --monitor-accent on a light surface,
  ALWAYS use color-mix(in srgb, var(--monitor-accent) 65%, #000) not raw --monitor-accent.

  TEXT ON TINTED PANELS (JS-generated cards, badges, chips, timeline labels):
  Tinted panel = var(--monitor-accent-bg) = rgba(accent, 0.12) — a LIGHT surface.
  Text on this surface MUST use the darkened accent:
    WRONG: style="background:var(--monitor-accent-bg);color:var(--monitor-accent)"
    RIGHT: style="background:var(--monitor-accent-bg);color:color-mix(in srgb,var(--monitor-accent) 65%,#000)"
  This applies to ALL elements with light tinted backgrounds:
  badges, risk-heat cells, tag chips, timeline labels, actor boards, delta items.

  VALIDATOR SCOPE LIMITATION: Checks 19–20 only scan <style> blocks in static HTML.
  JavaScript innerHTML strings are invisible to the validator — most contrast
  violations occur there (chart renderers, card builders, tooltip callbacks).
  Catch those via: anti-patterns.json FE-003 + visual sign-off on every PR.
  Never rely on the validator alone for contrast compliance in JS-heavy pages.

SIGNAL BLOCK SOURCE LINK RULE (FE-018 — see anti-patterns.json):
  Every dashboard signal/lead-signal block MUST include a 'Read the top story ↓' link
  wherever source_url is available. This applies to all 7 monitors.
  Standard pattern:
    var sourceUrl = signalObj.source_url || d.source_url || '';
    // In innerHTML:
    (sourceUrl ? '<div style="margin-top:var(--space-3)"><a class="source-link" href="'
      + escHtml(sourceUrl) + '" target="_blank" rel="noopener">Read the top story ↓</a></div>' : '')
  Link text is always exactly: 'Read the top story ↓' — no variations.

COUNTRY FLAGS RULE (FE-016 — see anti-patterns.json):
  AsymRenderer.flag(iso2) is available on every page via renderer.js.
  ALWAYS use it wherever a country name or ISO-2 actor code appears:
    • Tables, chart labels, card headings, timeline actor labels
    • Delta strips, actor boards, threat boards, campaign names
  Pattern: (AsymRenderer.flag(code) ? AsymRenderer.flag(code) + '\u00a0' : '') + escHtml(name)
  Safe: returns '' for unknown codes — ternary guard is sufficient.

SIGNAL-BLOCK OWNERSHIP (architectural rule):
  base.css owns the background property on .signal-block. It is set with !important.
  monitor.css MUST NOT set background on .signal-block — any such override is silently
  defeated by !important and creates confusion. Personality files may only set:
  border, border-radius, font-family, and other non-background properties.

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONITOR IMPROVEMENT WORKFLOW — MANDATORY FOR ALL SPRINT WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When implementing any item from the domain audit (docs/audits/):

STEP 1 — IMPLEMENT (staging → PR → merge as normal)

STEP 2 — UPDATE AUDIT FILE (direct to main, after merge)
  Mark the implemented item in docs/audits/audit-{abbr}.md:
  Change: | Description |
  To:     | ~~Description~~ ✅ YYYY-MM-DD |
  Also mark in docs/audits/master-action-plan.md under the relevant section.

STEP 3 — UPDATE INTERNAL METHODOLOGY (direct to main, after merge)
  Update HANDOFF.md with what changed and when.
  If an architectural rule changed, update COMPUTER.md.

STEP 4 — UPDATE PUBLIC METHODOLOGY PAGE (staging → PR → merge)
  Every monitor has a public methodology page:
    https://asym-intel.info/monitors/{slug}/methodology/
  Rendered from: content/monitors/{slug}/methodology.md (Hugo markdown)
  
  Update the methodology page when any of these change:
  - How an indicator is scored or sourced
  - How a composite index / heatmap / score is calculated
  - What sections the monitor covers
  - What data schema fields are collected
  - Any change to the analytical framework or indicator set

  The methodology page must always accurately describe what the monitor
  CURRENTLY does — not what it did at launch. It is the user-facing
  source of truth.

  Methodology page update is part of the same PR as the feature change
  wherever possible. If updating methodology only, it may go direct to
  main (it is Hugo markdown, not HTML/CSS/JS).

STEP 5 — UPDATE CRON PROMPT (direct to main, if schema changed)
  If the change adds or modifies a collected data field, update the
  cron prompt schema documentation in {abbr}-cron-prompt.md to match.
  The cron prompt is the agent's source of truth — keep it current.

AUDIT FILE STATUS KEY:
  | Description |                    → Pending
  | ~~Description~~ ✅ YYYY-MM-DD |  → Implemented
  | ~~Description~~ ⏸ BLOCKED |      → Blocked (note reason inline)
  | Description 🔜 |                  → In progress this session

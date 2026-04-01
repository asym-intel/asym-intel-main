# Asymmetric Intelligence — Monitor Dashboard Blueprint
# Version: 1.0
# Created: 31 March 2026
# Status: Active — updated after each monitor rebuild

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1 — ARCHITECTURAL PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ONE SHELL, SEVEN PAINT JOBS.

Every monitor shares identical HTML structure, identical JavaScript,
identical CSS architecture. Per-monitor differences are CSS custom
properties only — accent colour, name, abbreviation, SVG logo.
A structural change is made once in shared/ and rolls out to all.

CRON TASKS NEVER TOUCH HTML, CSS, OR JS.
The weekly publish cycle writes only to data/ JSON files.
All structural and stylistic changes come through explicit instruction.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2 — FILE STRUCTURE (canonical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

static/monitors/
  shared/
    css/
      base.css          ← all layout, typography, components, dark mode
    js/
      renderer.js       ← JSON → HTML rendering engine (all monitors)
      nav.js            ← sidebar/nav behaviour (scroll spy, mobile)
      theme.js          ← dark/light toggle + persistence
      charts.js         ← shared Chart.js wrappers (used where needed)
  {monitor-slug}/
    dashboard.html      ← CANONICAL URL — landing page (KPIs, signal, nav)
    report.html         ← current issue rendered from report-latest.json
    archive.html        ← issue index from archive.json
    persistent.html     ← living knowledge / persistent state view
    about.html          ← links to Hugo methodology page + editor info
    assets/
      monitor.css       ← PAINT LAYER ONLY (see Section 4)
    data/
      report-latest.json
      report-{date}.json (created each publish cycle)
      archive.json
      persistent-state.json

CANONICAL URL RULE:
dashboard.html is the entry point for all external links.
report.html, archive.html etc are internal navigation within the monitor.
index.html is NOT used (dashboard.html is the index).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3 — SHARED SHELL SPECIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every HTML page follows this exact skeleton:

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Title] — [Monitor Name] · Asymmetric Intelligence</title>
  <meta name="description" content="[page description]">
  <!-- Fonts: Satoshi (all monitors use this as base) -->
  <link rel="preconnect" href="https://api.fontshare.com">
  <link href="https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700&display=swap" rel="stylesheet">
  <!-- Shared base styles -->
  <link rel="stylesheet" href="../shared/css/base.css">
  <!-- Monitor paint layer -->
  <link rel="stylesheet" href="assets/monitor.css">
  <!-- Theme init (must be before body to prevent flash) -->
  <script src="../shared/js/theme.js"></script>
</head>
<body>
  <!-- Network bar (injected by GitHub Actions — DO NOT REMOVE) -->
  <!-- [network bar HTML] -->

  <!-- Monitor top nav -->
  <nav class="monitor-nav" aria-label="Monitor navigation">
    <a class="monitor-nav__brand" href="dashboard.html">
      <!-- SVG logo from monitor.css var or inline -->
    </a>
    <ul class="monitor-nav__links">
      <li><a href="dashboard.html">Overview</a></li>
      <li><a href="report.html">Latest Issue</a></li>
      <li><a href="archive.html">Archive</a></li>
      <li><a href="persistent.html">Living Knowledge</a></li>
      <li><a href="about.html">About</a></li>
    </ul>
    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode"></button>
  </nav>

  <!-- Page content -->
  <main id="main-content">
    [page-specific content]
  </main>

  <!-- Shared footer -->
  <footer class="monitor-footer">
    <span>Asymmetric Intelligence · <a href="https://asym-intel.info">asym-intel.info</a></span>
    <span class="monitor-footer__credit">
      <a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener">
        Created with Perplexity Computer
      </a>
    </span>
  </footer>

  <!-- Shared JS -->
  <script src="../shared/js/nav.js"></script>
  <!-- Page-specific JS inline or in separate file -->
</body>
</html>
```

NETWORK BAR RULE:
The inject-network-bar GitHub Actions workflow injects the network bar
after `<body>`. The HTML skeleton above must have a plain `<body>` tag
with NO inline content immediately after it — the workflow pattern-matches
`<body>` and inserts the bar. Do not add padding-top hacks or bar offsets
in the shell — the network bar injects its own offset styles.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4 — PAINT LAYER SPECIFICATION (monitor.css)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Each monitor's assets/monitor.css contains ONLY CSS custom property
overrides. No layout rules. No component styles. No font-face declarations.

```css
/* assets/monitor.css — [Monitor Name] */
:root {
  /* Primary accent — used for headings, links, active states, KPI values */
  --monitor-accent:        #XXXXXX;
  /* Accent at low opacity — used for backgrounds, hover states */
  --monitor-accent-bg:     rgba(R, G, B, 0.12);
  /* Accent for dark mode (may differ from light) */
  --monitor-accent-dark:   #XXXXXX;

  /* Monitor identity */
  --monitor-name:          "Monitor Full Name";
  --monitor-abbr:          "XXX";

  /* Optional font override (default is Satoshi) */
  /* --monitor-font: 'Source Serif 4', Georgia, serif; */
}
```

CURRENT MONITOR PAINT VALUES:
| Monitor                    | Accent    | Abbr  | Font override |
|----------------------------|-----------|-------|---------------|
| European Strategic Autonomy | #5b8db0  | EGHTM | none          |
| Democratic Integrity        | #61a5d2  | WDM   | none          |
| Global Macro                | #22a0aa  | GMM   | none          |
| AI Governance               | #3a7d5a  | AIG   | none          |
| FIMI & Cognitive Warfare    | #38bdf8  | FIMI  | none          |
| Environmental Risks         | #4caf7d  | GERP  | none (Source Serif 4 available as override) |
| Strategic Conflict          | #dc2626  | SCEM  | none          |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5 — PAGE SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dashboard.html — LANDING / OVERVIEW
Purpose: First page a visitor sees. Answers "what is this monitor and
         what happened this week?"
Content:
  - Monitor name, abbreviation, publish day
  - KPI strip (3–6 headline metrics from persistent-state.json)
  - Lead signal (M00/signal from report-latest.json)
  - Delta strip (top 3 changes this week from report-latest.json)
  - Navigation to all other pages
  - Last updated timestamp
Data source: report-latest.json (signal, delta_strip, meta)
             persistent-state.json (KPI values)

report.html — CURRENT ISSUE
Purpose: Full structured content of the current week's issue.
Content: All modules rendered from report-latest.json.
         Module nav strip at top for jumping between sections.
         Cross-monitor flags panel at bottom.
Data source: report-latest.json (all modules + cross_monitor_flags)

archive.html — ISSUE INDEX
Purpose: Browseable history of all published issues.
Content: Reverse-chronological list of issues from archive.json.
         Each entry: issue number, date, signal (one-line), delta_strip.
         Link to the canonical Hugo brief URL for each issue.
Data source: archive.json

persistent.html — LIVING KNOWLEDGE
Purpose: The monitor's accumulated knowledge that persists across issues.
Content: All persistent state entities rendered from persistent-state.json.
         Version history for each entity.
         Last-updated timestamp per entity.
         Clear visual distinction between what changed this week vs stable.
Data source: persistent-state.json

about.html — ABOUT THIS MONITOR
Purpose: Context, editorial standards, links to full methodology.
Content:
  - Monitor description and analytical position
  - Editor name and link
  - Link to full methodology: asym-intel.info/monitors/{slug}/methodology/
  - Link to all briefings: asym-intel.info/monitors/{slug}/
  - Link to asym-intel.info homepage
  - Perplexity Computer credit (the ONLY place it appears)
Data source: static HTML (no JSON)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6 — DATA CONTRACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All monitors share these root-level fields in report-latest.json:

REQUIRED (renderer.js depends on these — never rename):
  meta.issue            integer
  meta.week_label       string "DD–DD Month YYYY"
  meta.published        string "YYYY-MM-DD"
  meta.publish_time_utc string ISO8601
  meta.editor           string
  signal                string (or meta.signal) — one-sentence lead
  cross_monitor_flags   object { network, updated, flags[], version_history[] }
  source_url            string — canonical Hugo brief URL

OPTIONAL STANDARD (renderer.js handles gracefully if absent):
  delta_strip[]         array — top 3–5 changes {rank, title, module, delta_type, one_line}

MONITOR-SPECIFIC:
  All other fields are monitor-specific (see each monitor's schema in
  the initialised report-latest.json in their data/ directory).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7 — CRON TASK RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT CRON TASKS MAY WRITE:
  data/report-latest.json     ← replace entirely each week
  data/report-{date}.json     ← create new dated copy each week
  data/archive.json           ← append one entry each week
  data/persistent-state.json  ← update changed entities only

WHAT CRON TASKS MAY NOT TOUCH:
  dashboard.html
  report.html
  archive.html
  persistent.html
  about.html
  assets/monitor.css
  assets/monitor-logo.svg
  ../shared/css/base.css
  ../shared/js/*.js

Any change to the above requires explicit instruction and is made
through this session — not by a cron task.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 8 — BUILD LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Format per entry:
  MONITOR: [name]
  DATE: [date]
  STATUS: [Complete / In Progress / Planned]
  DECISIONS: [decisions made during this build]
  ISSUES: [problems encountered and how resolved]
  SHELL CHANGES: [any changes made to shared/ as a result]
  ROLLOUT: [which other monitors received the shell change]

────────────────────────────────────────────────────────────────
MONITOR: AI Governance
DATE: Pre-blueprint (built before this framework existed)
STATUS: Reference standard (not rebuilt — already correct architecture)
DECISIONS:
  - Multi-page structure with dashboard.html, report.html, archive.html,
    digest.html, search.html, about.html
  - report.html renders from report-latest.json via report-renderer.js
  - Separate base.css, nav.js, theme.js in assets/
ISSUES: None documented (pre-blueprint)
SHELL CHANGES: N/A — this IS the reference standard
ROLLOUT: N/A

────────────────────────────────────────────────────────────────
MONITOR: Democratic Integrity (WDM)
DATE: 31 March 2026
STATUS: Complete ✓
DECISIONS:
  - shared/ (not _shared/) — GitHub Pages silently 404s directories
    starting with underscore (Jekyll reserved prefix). CRITICAL rule
    for all future builds: never use _ prefix for static asset dirs.
  - DOMContentLoaded guard added to renderer init calls in report.html
    to prevent race conditions on slow connections.
  - Custom renderer registration (window.AsymRenderer.register) works
    correctly — heatmap and mimicry chain custom renderers both render.
  - Relative path fetch('data/report-latest.json') works correctly from
    GitHub Pages once the JS files load (path resolves relative to HTML).
  - Network bar requires plain <body> tag with blank line after it.
    Inject workflow matches '<body>\n' pattern successfully.
ISSUES:
  - renderer.js initially 404ing — root cause: _shared/ directory prefix
    blocked by GitHub Pages/Jekyll. Fixed by renaming to shared/.
  - report.html showed "Loading report..." indefinitely until JS loaded.
    Added defensive fallback: if (window.AsymRenderer && ...) check.
  - Sidebar HTML comment bug: <!-- populated by renderer.js --> prevents
    empty-check in renderer.js. Fixed with comment-stripping regex before
    checking innerHTML. Standard pattern for all future pages.
  - about.html sidebar ID mismatch: sidebar hrefs used #about-monitor etc.
    but actual section IDs were #section-description etc. Fixed 31 Mar.
    RULE: about.html section IDs must always be #section-description,
    #section-schedule, #section-editor, #section-links. Sidebar hrefs
    must match exactly.
POST-LAUNCH SHELL CHANGES (31 March 2026):
  - base.css v1.1: Increased type scale minimums (xs→0.75rem, sm→0.875rem,
    base→0.9375rem). Improved text colour contrast (secondary #3d3a35,
    muted #6b6660, faint #9a958d). Sidebar links font bumped to text-sm.
    kpi-card__label and kpi-card__sub bumped to text-sm. page-header__meta
    bumped to text-sm.
SHELL CHANGES:
  - Added try/catch around render() in shared/js/renderer.js to surface
    JS errors as visible error-state div (not silent failure).
  - DOMContentLoaded guard pattern established for all page init calls.
PAGES DELIVERED: dashboard.html, report.html, archive.html,
                 persistent.html, about.html, assets/monitor.css
ROLLOUT: shared/ library created — used by all future monitor builds.


────────────────────────────────────────────────────────────────
MONITOR: Strategic Conflict & Escalation Monitor (SCEM)
DATE: 31 March – 1 April 2026
STATUS: Complete ✓ — live at asym-intel.info
DECISIONS:
  - overview.html (not index.html) — Hugo owns index.html at root
  - SVG in monitor-nav brand: 18×18px, var(--monitor-accent), no abbr text
  - Full monitor name in brand — no abbreviation shorthand
  - section.html redirect: Hugo section root → dashboard.html (all monitors)
  - base.css v1.5: overflow-x:hidden moved to body only (sticky fix)
  - network-bar full-bleed: no max-width inner wrapper
  - indicator-grid: repeat(6,1fr) — fixed 6-col for SCEM
  - cross_monitor_flags in persistent-state.json (schema v2.0 initialised)
ISSUES:
  - overflow-x:hidden on .monitor-layout breaks position:sticky — FIXED
  - index.html conflict with Hugo — renamed to overview.html
  - network bar CNAME bug: Hugo docs/ CNAME overwrites staging domain — FIXED
    (staging-deploy.yml now writes CNAME after Hugo build)
SHELL CHANGES:
  - base.css v1.5: overflow-x on body not layout container
  - nav.js: rootMargin '-10% 0px -60% 0px' (was -75% — short sections missed)
  - network-bar.html: full-bleed, mobile nb-links hide, re-inject pattern
PAGES DELIVERED: overview.html, dashboard.html, report.html, archive.html,
                 persistent.html, about.html, methodology.html, search.html
ROLLOUT: base.css v1.5, nav.js fix, network-bar full-bleed → all monitors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 9 — ROLLOUT TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tracks when shared shell changes have been applied to each monitor.
Format: shared/ change → which monitors updated → date

2026-03-31 | base.css v1.1 (larger fonts, better contrast) → WDM
2026-04-01 | base.css v1.3 (larger type scale 16px base) → SCEM
2026-04-01 | base.css v1.4 (mobile overflow fixes) → SCEM
2026-04-01 | base.css v1.5 (overflow-x on body, sticky fix) → SCEM
2026-04-01 | nav.js (rootMargin fix for short sections) → SCEM
2026-04-01 | network-bar.html (full-bleed, mobile hide) → SCEM + all 7 monitors
             Note: all shared/ changes apply to all monitors automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 10 — DECISIONS (resolved 31 March 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1 CHARTS: Shared. charts.js lives in shared/js/. Standard API:
   window.AsymCharts.line(canvasId, data, options)
   window.AsymCharts.bar(canvasId, data, options)
   window.AsymCharts.gauge(canvasId, value, options)
   Monitor-specific chart config passes data only — never chart logic.

Q2 VERSION HISTORY: Collapsed by default in persistent.html.
   Expand toggle per entity. Class: .version-history (hidden)
   Toggle class: .version-history--open (visible)

Q3 MODULE NAV: Auto-generated from report-latest.json keys.
   renderer.js reads top-level keys (excluding meta, source_url,
   cross_monitor_flags) and builds the module nav strip dynamically.
   Adding a new module to the JSON requires no HTML change.

Q4 SEARCH PAGE: Standard across all monitors.
   Implement after core 5 pages (dashboard, report, archive,
   persistent, about) are stable on the first monitor.
   search.html searches archive.json client-side (no server needed).

Q5 STICKY LEFT NAV: YES — use the sticky left sidebar nav for ALL monitors.
   The sidebar is sticky (position: sticky, top: network-bar + nav-height),
   scrolls independently from main content, and auto-highlights active section.
   This is the canonical section navigation pattern across all 7 monitors.
   Implementation: .monitor-sidebar with position:sticky is already in base.css.
   auto-nav highlighting: nav.js handles scroll-spy (already implemented).

Q6 SVG MONITOR LOGOS: DONE — implemented in SCEM Build 2, locked as standard.
   Pattern: 18×18px SVG inline in .monitor-nav__brand, left of full monitor name.
   Use var(--monitor-accent) for all stroke/fill — inherits per monitor.
   Do NOT show abbreviation (SCEM, WDM etc) in brand — SVG + full name only.
   All 7 monitor SVGs stored in: static/monitors/monitor-svg-notes.md

Q7 ABOUT.HTML SECTION ID STANDARD (locked):
   section IDs must be: #section-description, #section-schedule,
   #section-editor, #section-links, #section-credit
   Sidebar hrefs must match these exactly. Do not use #about-* prefixes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 11 — PRODUCTION GATE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE: Nothing is pushed to the live repo without editor confirmation
except automated cron data writes.

TWO CLASSES OF CHANGE:

  DATA WRITES (automated — no confirm needed)
    Cron tasks writing: data/report-latest.json, data/report-{date}.json,
    data/archive.json, data/persistent-state.json
    These are pre-agreed automated operations — no structural change.

  STRUCTURAL CHANGES (always require editor confirm before push)
    Any .html, .css, .js file
    Any Hugo template or partial (layouts/, assets/)
    Any GitHub Actions workflow (.github/workflows/)
    The network bar template (.github/network-bar.html)
    MONITOR-BLUEPRINT.md, publishing-workflow.md, methodology.md files
    Any new file creation in the repo

CONFIRM PROCEDURE:
  1. Show the full diff (or full file content for new files)
  2. State which files will be committed
  3. State the intended effect
  4. Wait for explicit editor approval before any git commit

RATIONALE: The live site at asym-intel.info is production. Structural
changes go through the editor — the same discipline as any production
deployment workflow.

NOTE ON SITE HIERARCHY AND MONITOR IDENTITY:
  THE NETWORK BAR (40px, dark, fixed) — SITE INFRASTRUCTURE
    Controlled centrally. Height, colours, font, content, and behaviour
    never modified by individual monitors or cron tasks.
    Identical on every page across the entire site and all monitors.

  THE MONITOR NAV (below the network bar) — MONITOR IDENTITY
    Larger than the network bar. Carries the monitor name, abbreviation,
    and SVG logo in the monitor accent colour. This is where each monitor
    has its own visual identity.
    Each monitor can style its brand area (name, colour, SVG) via
    monitor.css — the nav links (Overview, Latest Issue, Archive…) are
    standard across all monitors and defined in the HTML shell.
    The monitor nav is structural HTML — never touched by cron tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 12 — BLUEPRINT v2.0 (locked 31 March 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Supersedes the v1.0 decisions (Sections 3–10) where in conflict.
Reference standard: AI Governance Monitor architecture + WDM
persistent-state patterns + lessons from Build 1.

────────────────────────────────────────────────────────────────
STANDARD PAGE SET (8 pages per monitor)
────────────────────────────────────────────────────────────────

  overview.html    Monitor landing page — CLEAN BRIEF INDEX only.
                   Shows: page header, issue list (title/date/signal),
                   archive entries, identity panel (SVG + CTAs).
                   NO KPI strip — KPIs belong on dashboard.html only.
                   NOTE: Hugo owns index.html — use overview.html.
                   Hugo section.html redirects root URL → dashboard.html.

  dashboard.html   Current issue: KPI strip + signal block +
                   delta strip. Canonical monitor URL.

  report.html      Full current issue — all modules rendered from
                   report-latest.json. Right-hand sticky nav.
                   Optional horizontal module jump strip (auto-
                   generated from JSON keys; shown if 6+ modules).

  archive.html     All past issues from archive.json.

  persistent.html  Living knowledge — entities that persist and
                   accumulate across issues with full version
                   history. Cross-monitor flags live here (not
                   just in weekly report JSON).

  about.html       Editor, publication schedule, methodology link,
                   technical credit. Section IDs: #section-
                   description, #section-schedule, #section-editor,
                   #section-links, #section-credit (locked).

  methodology.html PUBLIC methodology page — WHAT the monitor
                   tracks and WHY those sources/frameworks were
                   chosen. Credibility signalling only.
                   NEVER includes: scoring rubrics, prompt
                   structure, weighting logic, or editorial
                   process. The full 'how-to' methodology stays
                   in private internal files only.

  search.html      Client-side search across archive.json.
                   Standard across all monitors.

NO per-monitor digest.html. See Section 12 — Digest below.
NO index.html — Hugo owns this path. Use overview.html instead.

────────────────────────────────────────────────────────────────
NAVIGATION ARCHITECTURE
────────────────────────────────────────────────────────────────

LAYER 1 — NETWORK BAR (site infrastructure, never modified per monitor)
  40px, fixed, dark (#1a1918), z-index 9999.
  Content: Asymmetric Intelligence brand + Monitors / Compossible
  / The White Space links.
  Injected automatically by GitHub Actions workflow.
  No monitor may alter height, colour, font, content, or behaviour.

LAYER 2 — MONITOR NAV (monitor identity, consistent structure)
  52px, sticky below network bar, background: var(--color-bg).
  Left: monitor SVG logo + abbreviation + full name (styled via
  monitor.css — colour, font weight tweakable).
  Centre: standard page links — Overview · Latest Issue · Archive
  · Living Knowledge · About (all monitors identical).
  Right: theme toggle.
  The monitor name/abbr area is LARGER than the network bar text
  to give each monitor its own visual identity. Styled via:
    .monitor-nav__brand in monitor.css (accent colour, SVG).

LAYER 3 — RIGHT-HAND STICKY SECTION NAV (all pages, all monitors)
  Position: sticky right sidebar, ~220px wide.
  Behaviour: stays in view as user scrolls; highlights active
  section via Intersection Observer scroll-spy (nav.js).
  Content: auto-generated from page sections or JSON module keys.
  Used on: all 8 standard pages (not just report.html).
  Replaces: the left sidebar used in WDM Build 1.

LAYER 4 — MODULE JUMP STRIP (report.html only, 6+ modules)
  Horizontal strip below monitor-nav, sticky.
  Auto-generated from report-latest.json top-level keys
  (excluding meta, source_url, cross_monitor_flags).
  Short labels only (M00, M01... or abbreviated module names).

────────────────────────────────────────────────────────────────
CANONICAL MONITOR NAMES (use these names consistently — always)
────────────────────────────────────────────────────────────────

  Full name                                Abbr   Slug
  ─────────────────────────────────────── ──────  ──────────────────────────────
  World Democracy Monitor                  WDM    democratic-integrity
  Global Macro Monitor                     GMM    macro-monitor
  FIMI & Cognitive Warfare Monitor         FCW    fimi-cognitive-warfare
  European Strategic Autonomy Monitor      ESA    european-strategic-autonomy
  AI Governance Monitor                    AGM    ai-governance
  Environmental Risks Monitor              ERM    environmental-risks
  Strategic Conflict & Escalation Monitor  SCEM   conflict-escalation

RULE: Always refer to monitors by their full name or abbreviation
above. Never use partial names, slug names, or informal variants
in documentation, prompts, or user communications.

────────────────────────────────────────────────────────────────
EMAIL DIGEST
────────────────────────────────────────────────────────────────

ONE digest for the whole network — not per monitor.
Schedule: one email per day of the week, one per monitor,
matching existing publish schedule:
  Monday    — World Democracy Monitor (WDM)
  Monday    — Global Macro Monitor (GMM) [08:00 UTC, after WDM]
  Thursday  — FIMI & Cognitive Warfare Monitor (FCW)
  Wednesday — European Strategic Autonomy Monitor (ESA)
  Friday    — AI Governance Monitor (AGM)
  Saturday  — Environmental Risks Monitor (ERM)
  Sunday    — Strategic Conflict & Escalation Monitor (SCEM)

Subscribers choose which days they want. Managed via Buttondown
at https://buttondown.com/asym-intel (single list).

No per-monitor digest.html pages. The network-wide subscribe
page at /subscribe/ is the single entry point.
The existing per-monitor digest.html (AI Governance) will be
deprecated and redirected to /subscribe/.

────────────────────────────────────────────────────────────────
JSON PIPELINE (v2.0 — MANDATORY FOR ALL MONITORS)
────────────────────────────────────────────────────────────────

The JSON pipeline is NON-NEGOTIABLE. It is the backbone of:
  1. All monitor dashboards, report, archive, and persistent pages
  2. Data quality and consistency across issues
  3. The Whitespace network graph tool (reads cross_monitor_flags
     from all 7 monitors to build the inter-monitor connection
     graph — this ONLY works if all monitors publish consistent,
     machine-readable JSON at known paths)

CRON TASKS WRITE ONLY THESE FILES — nothing else:
  Path: static/monitors/{slug}/data/

  report-latest.json    Current issue — always overwritten
  report-{date}.json    Dated archive copy — never overwritten
  archive.json          Append-only issue index
  persistent-state.json Living knowledge — surgically updated,
                        never wholesale replaced

FILE SCHEMAS:

  report-latest.json
  ──────────────────
  {
    "meta": {
      "issue":           integer,
      "volume":          integer,
      "week_label":      "string",
      "published":       "ISO-8601",
      "slug":            "monitor-slug",
      "publish_time_utc":"HH:MM",
      "editor":          "string",
      "schema_version":  "2.0"
    },
    "signal":            { ... },   ← named semantic keys
    [module keys]:       { ... },   ← named, never module_0
    "delta_strip":       [ ... ],
    "cross_monitor_flags": { ... }, ← ALSO in persistent-state
    "source_url":        "string"
  }
  RULE: All top-level keys must be named semantically.
  NEVER use module_0, module_1 etc. Adding a module requires
  only adding a new named key — no renumbering.

  archive.json
  ────────────
  {
    "issues": [
      {
        "issue":     integer,
        "published": "ISO-8601",
        "slug":      "string",
        "title":     "string",
        "signal":    "one-sentence summary",
        "url":       "path/to/report-{date}.json"
      }
    ]
  }
  RULE: Append only. Never delete or modify past entries.

  persistent-state.json
  ─────────────────────
  {
    "_meta": {
      "monitor_slug":    "string",
      "monitor_name":    "canonical name",
      "last_updated":    "ISO-8601",
      "last_issue":      "ISO-8601",
      "schema_version":  "2.0",
      "description":     "string"
    },
    [named entity groups]: { ... },  ← monitor-specific living data
    "cross_monitor_flags": {         ← LIVES HERE (not just report)
      "updated": "ISO-8601",
      "flags": [
        {
          "id":                      "cmf-NNN",
          "monitors_involved":       ["Canonical Monitor Name"],
          "monitor_url":             "https://...",
          "title":                   "string",
          "linkage":                 "string",
          "this_monitor_perspective":"string",
          "type":                    "string",
          "status":                  "Active | Resolved | Watching",
          "first_flagged":           "ISO-8601",
          "unchanged_since":         "ISO-8601",
          "version_history": [
            {
              "date":        "ISO-8601",
              "change":      "string",
              "reason":      "string",
              "prior_value": null or "string"
            }
          ]
        }
      ],
      "version_history": [ ... ]
    }
  }
  RULES:
  — Flags are NEVER deleted. Closed = status: "Resolved".
  — Each entity group uses version_history[] for audit trail.
  — Surgical updates only — never replace the whole file.
  — monitor_name must use canonical name from Section 12.

WHITESPACE NETWORK GRAPH — PIPELINE DEPENDENCY
  The Whitespace tool reads cross_monitor_flags from all 7
  persistent-state.json files to build the network graph
  showing inter-monitor connections.

  For this to work, every monitor MUST:
  1. Publish persistent-state.json at the standard path
  2. Include cross_monitor_flags with the standard schema above
  3. Use canonical monitor names in monitors_involved[]
  4. Keep status field current (Active / Resolved / Watching)

  If any monitor omits cross_monitor_flags or uses non-standard
  monitor names, that monitor will be an isolated node in the
  Whitespace graph — breaking the network visualisation.

schema_version "2.0" signals Blueprint v2.0 compliance.
All monitors must bump to "2.0" when rebuilt.

────────────────────────────────────────────────────────────────
METHODOLOGY PAGE — PUBLIC/PRIVATE BOUNDARY (locked)
────────────────────────────────────────────────────────────────

PUBLIC (in methodology.html on live site):
  — What the monitor tracks (scope, domain, geographic coverage)
  — Why those sources were chosen (credibility, independence,
    track record — the 'standing' of the monitor)
  — Which organisations/databases are primary sources
  — Publication frequency and editorial standards

PRIVATE (internal methodology files only — never published):
  — Scoring rubrics and numerical weighting
  — Prompt structure and AI instruction sets
  — Step-by-step editorial process and workflow
  — How severity levels are assigned
  — How confidence levels are determined

RATIONALE: The public methodology establishes credibility and
transparency for readers. The private methodology is operational
IP. Mixing them would either expose operational details or
dilute the public credibility signal with procedural noise.

────────────────────────────────────────────────────────────────
SHARED LIBRARY — v2.0 CHANGES
────────────────────────────────────────────────────────────────

base.css: v1.1 in effect (larger type scale, better contrast).
          Right-hand sidebar replaces left sidebar.
          .monitor-sidebar → position: sticky, RIGHT side.

nav.js: Update Intersection Observer to highlight right-hand
        nav links (not left). Same scroll-spy logic.

renderer.js: Add support for named persistent-state entity
             groups. Auto-detect cross_monitor_flags key in
             persistent-state.json and render dedicated panel.

────────────────────────────────────────────────────────────────
BUILD ORDER (revised)
────────────────────────────────────────────────────────────────

  1. ✅ Update Blueprint shell (shared/) for v2.0
     — right-hand nav, 8-page set, new renderer features
  2. ✅ Build SCEM (conflict-escalation) — Build 2 complete
     Lessons: overview.html not index.html; SVG in nav brand;
     full-bleed network bar; base.css v1.5 sticky fix
  3. Build ERM (environmental-risks) — Build 3 (next)
  4. Rebuild WDM (democratic-integrity) to v2.0 shell
     — adds index.html, search.html, methodology.html,
       migrates to right-hand nav, adds persistent cross-monitor
       flags
  5. FCW (fimi-cognitive-warfare)
  6. GMM (macro-monitor)
  7. ESA (european-strategic-autonomy)
  8. AGM (ai-governance) — last, migrate to shared/ library,
     rename module keys to semantic naming, add persistent.html

────────────────────────────────────────────────────────────────
LESSONS FROM BUILD 1 (WDM) — carried into v2.0
────────────────────────────────────────────────────────────────

1. _shared/ → shared/: GitHub Pages silently 404s underscore
   dirs. All shared assets in shared/ only. NEVER use _ prefix.

2. HTML comment bug: <!-- populated by renderer.js --> prevents
   empty-check. Strip comments before checking innerHTML.

3. Network bar requires plain <body> tag + blank line after.
   Inject workflow matches '<body>\n' pattern.

4. DOMContentLoaded guard: all renderer init calls need guard.

5. about.html section IDs locked:
   #section-description, #section-schedule, #section-editor,
   #section-links, #section-credit. Sidebar hrefs must match.

6. sidebar.js scroll-spy: use scroll-margin-top equal to
   network-bar-height + nav-height + space-4 on all
   .module-section elements.

7. Confirm before pushing to main (Section 11). All build work
   on staging branch → review at staging.asym-intel.info →
   PR to main for production release.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 13 — CRON TASK ARCHITECTURE (repo-first pattern)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEM SOLVED: Cron tasks baked with static instructions cannot
receive Blueprint updates without manual re-configuration of each
of the 7 cron schedules. This caused the April 2026 SCEM incident
where an intra-week run used v1.0 instructions and overwrote HTML.

SOLUTION: Repo-first instruction loading. Each cron schedule
contains only a thin wrapper that reads its canonical instructions
from the repo at runtime.

CRON SCHEDULE CONTENT (identical for all monitors — change slug only):
  Read your full instructions from the repo before doing anything:

  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{SLUG}/cron-prompt.md \
    --jq '.content' | base64 -d

  Then follow those instructions exactly. The repo file is the
  canonical source of truth. Ignore any older instructions.
  Use api_credentials=["github"] for all GitHub operations.

CANONICAL PROMPT FILES (stored in repo, version-controlled):
  static/monitors/conflict-escalation/scem-cron-prompt.md     ✅
  static/monitors/environmental-risks/erm-cron-prompt.md      ✅
  static/monitors/democratic-integrity/wdm-cron-prompt.md     (Build 3 revision)
  static/monitors/macro-monitor/gmm-cron-prompt.md            (Build 5)
  static/monitors/fimi-cognitive-warfare/fcw-cron-prompt.md   (Build 4)
  static/monitors/european-strategic-autonomy/esa-cron-prompt.md (Build 6)
  static/monitors/ai-governance/agm-cron-prompt.md            (Build 7)

UPDATING INSTRUCTIONS: Edit the repo file → all future cron runs
pick up the change automatically. Never edit the cron schedule itself
unless changing timing or the slug.

WRAPPER REFERENCE: static/monitors/cron-wrapper-instructions.md

CRITICAL RULE (from April 2026 incident):
  Cron prompts must begin with:
  "CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER."
  This must be the first rule, in caps, before anything else.

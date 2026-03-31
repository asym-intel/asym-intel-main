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
DATE: [pending]
STATUS: Planned — FIRST BUILD
NOTES: Chosen as first build because: simplest existing architecture
       (no Chart.js, no theme toggle), rich JSON schema already
       initialised, good test of heatmap/severity score rendering.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 9 — ROLLOUT TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tracks when shared shell changes have been applied to each monitor.
Format: shared/ change → which monitors updated → date

[No entries yet — populate as builds progress]

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

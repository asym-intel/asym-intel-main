# Charts & Visualisations — Role Handoff
# asym-intel.info + whitespace.asym-intel.info
# Written: 3 April 2026
# Purpose: cold-start context for any future Computer session working on charts/viz

---

## 1. What I Own

### Files I have directly written or substantially modified

**whitespace.asym-intel.info (repo: asym-intel/asym-intel-whitespace)**

| File | What it is | Last commit |
|---|---|---|
| `docs/index.html` | Full interactive knowledge graph canvas (950 lines) | `6474fbb` |
| `docs/data/graph.json` | Graph data: 42 nodes, 112 edges, auto-rebuilt weekly | `6474fbb` |
| `docs/data/graph-edge-audit.md` | Rationale notes for every edge | `95af1f7` |
| `scripts/build_graph.py` | Python script that rebuilds graph.json from live monitor JSON | `6474fbb` |
| `.github/workflows/rebuild-graph.yml` | GitHub Action: runs every Monday 09:00 UTC | `6474fbb` |

**asym-intel/asym-intel-main (monitor site) — audit only, no files modified in this session**

No monitor HTML/CSS/JS files were modified in this session. The work was limited to the whitespace repo and a full visual audit of the live site (documented in `chart-audit-2026-04-01.md`, committed to whitespace repo or attachable separately).

### Monitors I have studied in depth

All 7 dashboards reviewed live (2 April 2026):
- AGM (ai-governance) — dark-mode dashboard, no Chart.js charts currently
- WDM (democratic-integrity) — broken map, heatmap is a plain table
- GMM (macro-monitor) — most chart-rich; 5 Chart.js instances; one version mismatch
- FCW (fimi-cognitive-warfare) — 1 Chart.js instance (AI trend chart)
- ESA (european-strategic-autonomy) — 1 Chart.js instance (defence radar), companion bar
- ERM (environmental-risks) — 1 Chart.js instance (planetary boundary bars); best single chart on site
- SCEM (conflict-escalation) — 0 Chart.js instances; indicator breakdown uses custom HTML bars

---

## 2. What I Know About the Chart System

### Architecture: no shared charts.js

Despite the `asym-intel-charts` skill referencing `static/monitors/shared/js/charts.js`, **that file does not exist in the repo as of 1 April 2026**. Chart code is entirely inline in each monitor's `dashboard.html`. Each dashboard is a self-contained HTML file with all JS written inside `<script>` blocks at the bottom.

There is no shared chart wrapper. Each monitor rolled its own. The skill's reference to `shared/js/charts.js` describes an intended architecture that has not been built yet — treat it as aspirational, not factual.

### Chart.js versions in use — MISMATCH EXISTS

| Monitor | File | Chart.js version |
|---|---|---|
| GMM | `static/monitors/macro-monitor/dashboard.html` | **4.4.0** ← older |
| ERM | `static/monitors/environmental-risks/dashboard.html` | 4.4.7 |
| ESA | `static/monitors/european-strategic-autonomy/dashboard.html` | 4.4.7 |
| FCW | `static/monitors/fimi-cognitive-warfare/dashboard.html` | 4.4.7 |
| AGM | `static/monitors/ai-governance/dashboard.html` | none (no Chart.js) |
| WDM | `static/monitors/democratic-integrity/dashboard.html` | none (no Chart.js) |
| SCEM | `static/monitors/conflict-escalation/dashboard.html` | none (no Chart.js) |

**GMM is on 4.4.0; all others on 4.4.7.** The chart skill's canonical reference is 4.4.4. Stick to 4.4.7 for any new work — it is the most recent and already in use on 3 of the 4 monitors that have charts. The GMM version should be bumped to 4.4.7 when next touching that file.

### CI Validator checks (`.github/validate-blueprint.py`)

Two checks are relevant to chart work:

- **Check 14**: If a page contains `<canvas` or `new Chart(`, it must have `cdn.jsdelivr.net/npm/chart.js` in the file. Forgetting the CDN = `Chart is not defined` error at runtime and a CI failure.
- **Check 17**: If both Chart.js CDN and `shared/js/charts.js` are present, CDN must come first. Currently only applies if the shared wrapper file ever gets created. Until then this check passes by default (both positions are -1 so it skips).

### Dark mode support — inconsistent

| Monitor | Has dark mode chart support |
|---|---|
| GMM | ✅ Yes — `updateChartColors()` function, responds to `data-theme` toggle |
| ERM | ✅ Yes |
| ESA | ✅ Yes |
| FCW | ✅ Yes |
| AGM | ✅ Yes (dashboard is permanently dark chrome) |
| WDM | ❌ No |
| SCEM | ❌ No |

Pattern for dark mode in charts (established in GMM):
```js
const isDark = () => document.documentElement.dataset.theme === 'dark';
function updateChartColors() { /* rebuild or update chart options */ }
document.addEventListener('themechange', updateChartColors);
```

### Chart patterns established (GMM is the reference)

- **Destroy before rebuild**: GMM uses `const riskChart = new Chart(...)` at top level, then `updateChartColors()` updates options. For pages with a rebuild pattern, always call `.destroy()` first.
- **Container sizing**: `<div style="height:Xpx;"><canvas id="..."></canvas></div>` + `maintainAspectRatio: false` in chart options.
- **Zero line emphasis**: Grid `color` callback checks `ctx.tick.value === 0` to draw a bolder zero line. GMM uses this consistently.
- **Semantic colour set** (from chart skill):
  - positive: `#059669`, high: `#d97706`, critical: `#dc2626`, moderate: `#2563eb`, contested: `#94a3b8`
- **Monitor accent colours**: AGM `#3a7d5a`, WDM `#61a5d2`, GMM `#22a0aa`, FCW `#38bdf8`, ESA `#5b8db0`, ERM `#4caf7d`, SCEM `#dc2626`

### Page inventory per monitor

AGM is the only monitor with a full set of sub-pages. All others have only `dashboard.html`:

| Monitor | Pages |
|---|---|
| AGM | dashboard, report, digest, archive, about, search |
| WDM | dashboard only |
| GMM | dashboard only |
| FCW | dashboard only |
| ESA | dashboard only |
| ERM | dashboard only |
| SCEM | dashboard only |

Report, persistent, and archive pages for WDM/GMM/FCW/ESA/ERM/SCEM are served by the Hugo content pipeline (rendered from brief markdown), not as static HTML. Charts on those pages are not yet built.

---

## 3. The White Space Network Graph

### What it is

An interactive force-directed knowledge graph at `whitespace.asym-intel.info` showing relationships between the 7 monitors and 35 Compossible posts. Built with `vasturiano/force-graph` v1.49.0 (CDN). Dark canvas (`#0d0d0b`). Single-page app, no framework.

### Where it lives

- **Repo**: `asym-intel/asym-intel-whitespace`
- **Served from**: `docs/` folder, GitHub Pages, CNAME: `whitespace.asym-intel.info`
- **Entry point**: `docs/index.html`
- **Graph data**: `docs/data/graph.json` (relative path: `data/graph.json` from index.html)
- **Edge audit**: `docs/data/graph-edge-audit.md`
- **Build script**: `scripts/build_graph.py`
- **CI**: `.github/workflows/rebuild-graph.yml`

### Current state (as of 1 April 2026)

- 42 nodes: 7 monitor hubs + 35 Compossible posts (1 orphan excluded at render time)
- 112 edges: 24 monitor↔monitor, 81 post→monitor, 7 series chains
- Relation types in use: `analyses` (53), `extends` (35), `contextualises` (21), `correlates` (3)
- `contradicts` and `cites` are defined in the schema but not yet appearing in data
- graph.json auto-rebuilds every Monday 09:00 UTC via GitHub Action

### Auto-rebuild pipeline

`scripts/build_graph.py` fetches:
- `https://asym-intel.info/monitors/{slug}/data/report-latest.json` (×7)
- `https://asym-intel.info/monitors/{slug}/data/archive.json` (×7)
- `https://compossible.asym-intel.info/posts-index.json`

Each monitor→monitor edge carries:
- `first_flagged`: date the cross-monitor flag was first raised
- `report_url`: direct URL to the dated report that raised it (e.g. `/monitors/ai-governance/2026-03-30/`)
- `flag_id`: the CMF flag ID from the monitor's `cross_monitor_flags` schema

Both `report_url` and `first_flagged` are shown in the side panel when clicking a node.

### Canvas features

- Perspective filter chips: All / each monitor / Compossible
- Search box: highlights matches, dims others
- Click node → side panel slides in from right: type badge, title, date, description, connections list (with `first_flagged` date and `↗` link to source report per connection), "Open monitor dashboard" / "Read on Compossible" button
- Double-click selected node → dismisses panel
- Background click → dismisses panel
- Moving particles on `extends`-type edges (teal, 2 particles)
- Monitor nodes: always-visible labels, `val=18` (larger radius)
- Compossible nodes: label visible only on hover/select, `val=6`
- Legend: bottom-left, dark glass effect

### Commits in order

```
b78de66  Initial commit
4be5198  Create CNAME
6c8025b  chore: add Hugo .gitignore
4cfbc3a  feat: placeholder — pure white canvas below network bar
95af1f7  data: initial graph.json — 46 nodes, 128 edges + edge audit
367c119  feat: deploy interactive knowledge graph canvas
36fa0a6  fix: force graph layout, DOM structure, and orphan nodes  ← critical bug fix
8166ab0  improve: text legibility and font sizes
a9c3841  fix: click-after-close and double-click to dismiss panel
6474fbb  feat: auto-rebuild pipeline for graph.json               ← current HEAD
```

---

## 4. Chart Improvement Findings

### What works well

**ERM Planetary Boundary chart** — best single chart on the site. Horizontal bars coloured by transgression status (red/amber/green) are clear and immediately communicative. The only improvement needed: add a quantitative distance-from-safe-limit value per bar.

**GMM Real M2 Deflator Waterfall** — second-best. Colour shifts from blue (nominal) to orange→red (real) as each deflator is applied. Well-executed visual encoding of monetary erosion.

**SCEM Friction Flag Status Board** — not a chart but the clearest status display on the site. Clean 7-cell grid with CLEAR/ACTIVE and colour coding. Consider adding a 4-week history strip (● / ○) per flag.

**GMM Asset Class Scores bar chart** — structurally sound but has one colour problem: prior-week bars use a uniform flat grey instead of a 40% opacity version of the current bar colour. The comparison is the entire analytical purpose of this chart — the colour encoding undermines it.

### What doesn't work

**WDM Geographic View map** — does not render. Completely blank section. This is the most impactful bug on the site. The section heading and "Map view" button exist; the map library either isn't loading or the data binding is broken. Investigate before adding any new charts to WDM.

**SCEM Indicator Breakdown chart** — shows a CONTESTED BASELINE watermark over all 10 conflicts because baselines don't lock until week 13. Visually looks broken even though behaviour is correct. Fix: show current absolute readings (not deviations) until baselines establish, and move the explanation text above the chart.

**"Heatmap" label mismatch** — used on WDM, ERM, and SCEM report pages, but in all three cases renders as a plain text/table with no colour gradient or matrix. The word sets an expectation the implementation doesn't meet. Either implement proper colour encoding or rename the sections.

**GMM Tail Risk Heatmap** — MED and LOW impact rows are entirely empty. Either all risks genuinely cluster at HIGH this week (plausible in a STAGFLATION regime) or the data pipeline isn't populating those rows. Empty cells in a matrix look like a bug rather than an analytical finding — add an explicit label if the emptiness is intentional.

**GMM Score History chart** — only 2 data points (2026-03-25 baseline + 2026-04-01). Will improve naturally. But consider adding a regime band overlay (light red fill below -0.5) so even early issues look meaningful rather than just two dots.

**ESA Lagrange Point Radar** — polygon hugs the centre (all 6 dimensions below 55/100) making it hard to read individual dimension values. The companion horizontal bar chart is clearer and should be treated as primary. Add a 50% target benchmark line to the radar to give readers a reference point.

**AGM dashboard** — all 5 risk dimensions (Governance Fragmentation, Cyber Escalation, Platform Power, Export Controls, Disinfo Velocity) are text cards only, despite all having clear quantitative ratings. A radar chart would give AGM a visual centrepiece comparable to ESA's Lagrange Point.

### What's missing (data exists, no visual yet)

Pulled from the chart skill's Sprint 2 queue and the visual audit:

| Item | Monitor | Data field | Suggested type | Notes |
|---|---|---|---|---|
| Tipping Point Proximity | ERM | `tipping_systems[*].proximity_score` | Horizontal gauge bars | Highest visual impact after fixing WDM map |
| Country severity ranking | WDM | Severity scores, 29 countries | Ranked horizontal bar | Data in dashboard already, needs renderer |
| Regime Shift Probability | GMM | `signal.regime_shift_probabilities` | 4-bar horizontal | In Sprint 2 chart skill |
| Composite Escalation Score | SCEM | `conflict_roster[*].esc_score` | Multi-conflict bar | Data lands Sun 5 Apr 2026 |
| Escalation Velocity | SCEM | `conflict_roster[*].escalation_velocity` | Direction indicator | Sprint 2 |
| Defence Spending by Member State | ESA | `defence_spending[]` | Horizontal bar | Sprint 2 schema |
| AGM Governance Health Score | AGM | `governance_health` | Composite dial | Sprint 2 |
| Concentration Index | AGM | Compute/Models/Infra/Apps/Safety | Centre-anchored bar | Data in report page |
| Scenario probability bars | GMM | Existing 3 scenarios | Inline CSS bars | 20-line change |
| Fed Funds Path chart | GMM | 5 FOMC dates + cut probabilities | Bar chart | Replace current table |
| Mimicry Chain flow diagram | WDM | 2 chains, ~5 nodes each | Node-link diagram | Analytically distinctive |
| FIMI Campaign Timeline | FCW | 12 campaigns with dates/status | Horizontal timeline | Differentiating feature |
| Regime Conviction History | GMM | Weekly regime label + score | Colour timeline strip | Builds value over time |
| Horizon Matrix | GMM | `horizon_matrix` | Structured table | Sprint 2 schema |
| Factor Attribution | GMM | `factor_attribution` | Per-asset breakdown | Sprint 2 schema |

---

## 5. Open Work

### Nothing partially implemented and left broken

All changes made in this session were completed and pushed. No half-built features exist in the repo.

### Graph auto-rebuild — one known gap

The `build_graph.py` script extracts monitor→monitor edges from `cross_monitor_flags` in `report-latest.json`. Compossible→monitor edges come from `monitors_referenced` frontmatter in `posts-index.json`.

**Gap**: the script has no fallback for monitors whose `report-latest.json` uses field name variants not yet in the lookup table (`MONITOR_NAME_TO_SLUG` dict in `build_graph.py`). The script prints a `WARN:` line for any unresolved flag but does not error — those edges are silently dropped. As new monitors publish reports with new name variants, add them to the lookup table. As of the last run (31 March 2026), zero warnings were produced.

### Sprint 2 charts — pending data

Several charts in the chart skill's Sprint 2 queue are waiting on data that doesn't exist in `report-latest.json` yet:
- `conflict_roster[*].esc_score` and `escalation_velocity` — **arrive SCEM publish Sun 5 Apr 2026**
- `governance_health` (AGM), `tipping_systems[*].proximity_score` (ERM), `defence_spending[]` (ESA) — waiting on cron prompt upgrades

Don't try to build these charts until the data fields are confirmed present in the live JSON.

### WDM map

The Geographic View section is blank in the live dashboard. No investigation was done in this session into the root cause (missing map library? broken data binding? empty GeoJSON?). This is the highest-priority item before any new WDM chart work begins.

---

## 6. Things a Fresh Instance Must Know

### gitignore in whitespace repo will fight you

`/docs/` is in `.gitignore` (a Hugo repo artifact). Every file in `docs/` must be force-added:
```bash
git add -f docs/index.html docs/data/graph.json
```
Regular `git add docs/` will silently add nothing and the commit will be empty. This will waste a full iteration cycle if you don't know about it.

### force-graph library replaces innerHTML of its container

`ForceGraph()(container)` does not append to the container — it **replaces** the container's innerHTML with its own `<div class="force-graph-container">`. Any child elements placed inside the container div will be destroyed when the graph initialises.

The whitespace canvas puts the panel, legend, tooltip, and loading overlay as **siblings** to `#graph-container` inside a `#graph-wrap` outer div — not as children of `#graph-container`. If you ever restructure the HTML, never put overlay elements inside the div that force-graph targets.

### force-graph physics: star topology collapses without tuning

The graph has a star topology (every Compossible post connects to 2-3 monitor hubs). Without explicit tuning, the link forces overpower repulsion and the entire graph collapses to a tight cluster. Current working config:
```js
Graph.d3Force('charge').strength(n => n.type === 'monitor' ? -500 : -120);
Graph.d3Force('link').distance(/* 180px monitor-monitor, 100px post-monitor */).strength(0.5).iterations(2);
```
Do not remove the center force (it was tried — without it, nodes fly apart in the Y direction and the graph spans 3000+ pixels vertically). Also: orphan nodes (no edges) must be filtered out before the simulation runs — they drift arbitrarily far under pure repulsion.

### Pre-spread nodes on a ring to avoid cold-start collapse

The simulation is initialised with nodes spread on a ring based on their index:
```js
const angle = (2 * Math.PI * i) / initData.nodes.length;
const r = n.type === 'monitor' ? Math.min(W, H) * 0.25 : Math.min(W, H) * 0.38;
n.x = Math.cos(angle) * r; n.y = Math.sin(angle) * r;
```
Without this, all nodes start at (0,0) and the simulation can't spread them effectively. Don't remove it.

### closePanel() must clear selectedNode

Early versions had closePanel() only removing the `.open` CSS class and not resetting `selectedNode`. This caused a bug where clicking any node after closing the panel appeared to do nothing (the state was already "selected" so no update happened). `closePanel()` now always does three things: removes `.open`, sets `selectedNode = null`, calls `refreshColors()`. Keep this invariant.

### Monitor HTML changes go to staging, not main

The `asym-intel-main` repo enforces staging-first for any `static/monitors/` HTML/CSS/JS changes. Do not push monitor dashboard changes directly to main. Create a `staging` branch, push there, screenshot, get visual sign-off, then open a PR. The CI validator runs 15+ checks on every push and will fail a broken build — check the validator output in GitHub Actions.

Hugo source files (`assets/css/main.css`, `layouts/`) go directly to main without staging.

### Chart.js CDN belongs in `<head>`, not body

CI Check 14 enforces this. If you put the CDN script at the bottom of body (or forget it), the CI build fails. Always add it in `<head>` before any `<script>` that calls `new Chart(...)`. This is especially easy to miss when adding a canvas to a page that didn't previously have one.

### GMM is on Chart.js 4.4.0; everything else is on 4.4.7

Bump GMM to 4.4.7 the next time that file is touched. There are no known breaking changes between these versions, but having a mixed codebase is a maintenance hazard. The chart skill's canonical version was 4.4.4 — use 4.4.7 for all new work.

### graph.json edge count drift

The initial graph.json (commit `95af1f7`) had 46 nodes and 128 edges. After the auto-rebuild script ran (commit `6474fbb`), it had 42 nodes and 112 edges. The reduction is because:
1. The script filters orphan nodes (no edges) — the initial version didn't
2. The script deduplicates edges bidirectionally — the initial version may have created some duplicates
3. Compossible post count may have changed between sessions

The counts will drift slightly each Monday as new posts and monitor reports publish. This is expected and correct — it's not a data loss.

### The chart skill lists a `shared/js/charts.js` that doesn't exist

As of 1 April 2026, `static/monitors/shared/` does not exist as a directory. Only `ai-governance/assets/css/base.css` exists as a shared asset. All chart code is inline. The skill describes an intended architecture. Build toward it when creating new charts (put reusable chart code in `shared/js/charts.js` and reference it), but don't reference it in code expecting it to already exist.

### SCEM baseline contest period

SCEM baselines do not lock until week 13 (minimum 12 weekly observations). Until then, all 10 conflicts show CONTESTED BASELINE and the Indicator Breakdown chart shows a watermark overlay with all bars at zero. This is correct behaviour — but it looks broken to any user who hasn't read the methodology. The indicator breakdown chart will remain visually empty until approximately week 13 (late June 2026). Do not "fix" the data — address it with UX (move explanation above chart, show absolute readings rather than deviations until baselines are set).

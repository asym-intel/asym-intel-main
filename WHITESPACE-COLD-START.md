# White Space — Cold Start Prompt
# Use this when picking up the whitespace.asym-intel.info work in a new session
# with no prior conversation history.
# Date written: 3 April 2026

---

## What you are doing

You are the Computer instance responsible for the White Space knowledge graph at
**whitespace.asym-intel.info** — an interactive force-directed graph showing
relationships between the 7 Asymmetric Intelligence monitors and analytical
Compossible posts. This is a separate project from the main asym-intel.info site
management task. You built this graph from scratch and own all its files.

Load these skills before doing anything:
- `asym-intel` (user skill) — working agreement, deployment rules, monitor reference
- `asym-intel-charts` (user skill) — chart patterns, Sprint 2 queue, colour conventions

---

## Step 0 — Always read these first

```bash
# Working agreement (read every session)
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d

# Current task state
gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md \
  --jq '.content' | base64 -d

# Your full knowhow on charts + whitespace (read before any whitespace work)
gh api /repos/asym-intel/asym-intel-main/contents/CHARTS-KNOWHOW.md \
  --jq '.content' | base64 -d

# Visual audit of all 7 monitor dashboards (read before any chart sprint work)
gh api /repos/asym-intel/asym-intel-main/contents/chart-audit-2026-04-01.md \
  --jq '.content' | base64 -d
```

---

## The two repos you work across

### 1. asym-intel/asym-intel-main
The main site. Monitor JSON data lives here. You read from it but make changes
via staging branch + PR (for HTML/CSS/JS) or directly to main (for Hugo source,
JSON data, docs). Full rules in COMPUTER.md.

### 2. asym-intel/asym-intel-whitespace
The White Space. You own this entirely. GitHub Pages serves from `docs/` on `main`.

**Clone if not already in workspace:**
```bash
gh repo clone asym-intel/asym-intel-whitespace /home/user/workspace/whitespace-repo
```

**CRITICAL — gitignore trap:** `/docs/` is gitignored. Always use:
```bash
git add -f docs/index.html docs/data/graph.json
```
Regular `git add docs/` silently adds nothing and creates empty commits.

**Git identity:**
```bash
git config user.email "peterhowitt@gmail.com"
git config user.name "Peter Howitt"
```

---

## Current state of the whitespace repo

**HEAD commit:** `6474fbb`  
**Live URL:** https://whitespace.asym-intel.info/

### File inventory

| File | What it is |
|---|---|
| `docs/index.html` | Full interactive canvas — 1029 lines, self-contained |
| `docs/data/graph.json` | Graph data — 42 nodes, 112 edges — auto-rebuilt weekly |
| `docs/data/graph-edge-audit.md` | Rationale notes for every edge |
| `scripts/build_graph.py` | Rebuild script (stdlib only, no pip needed) |
| `.github/workflows/rebuild-graph.yml` | GitHub Action: Mon 09:00 UTC |

### Commit history
```
6474fbb  feat: auto-rebuild pipeline for graph.json       ← HEAD
a9c3841  fix: click-after-close and double-click to dismiss
8166ab0  improve: text legibility and font sizes
36fa0a6  fix: force graph layout, DOM structure, orphan nodes
367c119  feat: deploy interactive knowledge graph canvas
95af1f7  data: initial graph.json — 46 nodes, 128 edges
4cfbc3a  feat: placeholder — pure white canvas
```

---

## What the canvas does

- Force-directed graph using `vasturiano/force-graph` v1.49.0 (CDN)
- Dark canvas `#0d0d0b`, Satoshi + Instrument Serif fonts
- Network bar pixel-matched to asym-intel.info (`#1a1918` bg, `#4f98a3` teal)
- 7 monitor hub nodes (larger, always-labelled, colour-coded)
- 35 Compossible post nodes (smaller, label on hover/select only)
- Perspective filter chips: All / each monitor / Compossible
- Search box: highlights matches, dims others
- Click node → side panel slides in from right:
  - Type badge, title, date, description
  - Connections list with `first_flagged` date + `↗` link to source report per edge
  - "Open monitor dashboard" / "Read on Compossible" button
- Double-click selected node → dismisses panel
- Background click → dismisses panel
- Moving teal particles on `extends`-type edges

### Monitor colour coding
```
ai-governance:               #4f98a3
conflict-escalation:         #c0392b
democratic-integrity:        #8e44ad
environmental-risks:         #27ae60
european-strategic-autonomy: #2980b9
fimi-cognitive-warfare:      #e67e22
macro-monitor:               #f39c12
compossible:                 #c8c4bc
```

---

## Auto-rebuild pipeline

`scripts/build_graph.py` runs every Monday 09:00 UTC via GitHub Actions.
It fetches:
- `https://asym-intel.info/monitors/{slug}/data/report-latest.json` (×7)
- `https://asym-intel.info/monitors/{slug}/data/archive.json` (×7)
- `https://compossible.asym-intel.info/posts-index.json`

Every monitor→monitor edge carries `first_flagged`, `report_url`, and `flag_id`
so each connection is traceable to the specific report that raised it.
These appear in the side panel as a date + ↗ link per connection.

The Action only commits if `graph.json` actually changed. It runs as
`github-actions[bot]` and has `permissions: contents: write`.

Monday 09:00 UTC is safe: the last monitor to publish is SCEM at Sun 18:00 UTC,
giving 15 hours before the whitespace rebuild.

---

## Critical technical gotchas

### 1. force-graph replaces innerHTML of its target container
`ForceGraph()(container)` wipes the container's children entirely. The side panel,
legend, tooltip, and loading overlay must be **siblings** of `#graph-container`,
not children. They live inside `#graph-wrap` which is the outer positioning context.
Never put overlay elements inside the div that force-graph targets.

### 2. Star topology collapses without force tuning
Every Compossible post connects to 2-3 monitor hubs. Without tuning, link forces
overpower repulsion and everything collapses. Working config:
```js
Graph.d3Force('charge').strength(n => n.type === 'monitor' ? -500 : -120);
Graph.d3Force('link').distance(/* 180px monitor-monitor, 100px post-monitor */)
  .strength(0.5).iterations(2);
```
Do not remove the center force — without it, nodes fly 3000px in the Y direction.

### 3. Pre-spread nodes on a ring at init
Without this, all nodes start at (0,0) and the simulation can't spread them:
```js
initData.nodes.forEach((n, i) => {
  const angle = (2 * Math.PI * i) / initData.nodes.length;
  const r = n.type === 'monitor' ? Math.min(W,H)*0.25 : Math.min(W,H)*0.38;
  n.x = Math.cos(angle) * r; n.y = Math.sin(angle) * r;
});
```

### 4. Orphan nodes must be filtered before simulation
Nodes with no edges drift arbitrarily far under pure repulsion.
`buildGraphData()` already filters them — don't remove that logic.

### 5. closePanel() must always reset state
`closePanel()` does three things in one place: removes `.open` CSS class,
sets `selectedNode = null`, calls `refreshColors()`. If you split these or
move them, clicking a node after closing the panel will appear to do nothing.

### 6. onEngineStop fires zoomToFit
The graph calls `window._Graph.zoomToFit(600, 40)` when physics finishes.
`window._Graph` is the exposed Graph instance. Don't remove the exposure —
it's needed for the reset button and filter chip zoom callbacks too.

---

## What's working, what needs improvement

**Working well:**
- Graph layout and physics — stable, fills canvas
- Side panel — click, close, double-click all reliable
- Filter chips and search — working
- Auto-rebuild pipeline — tested, zero warnings on last run
- Text legibility — improved (drop shadows on labels, raised muted colour values)

**Known issues / improvement opportunities (from visual audit):**
See `chart-audit-2026-04-01.md` in asym-intel-main for the full list.
The whitespace graph itself has no outstanding bugs.

**Sprint 2 chart items pending for the main site monitors** (not whitespace):
See `asym-intel-charts` skill — these are charts on monitor dashboards,
not changes to the whitespace graph.

---

## If the auto-rebuild Action fails

Check the Actions tab on `asym-intel/asym-intel-whitespace`.
The most likely causes:
1. A monitor's `report-latest.json` URL changed — fix the URL in `build_graph.py`
2. A new monitor name variant appeared in `cross_monitor_flags` — add it to
   `MONITOR_NAME_TO_SLUG` dict in `build_graph.py`
3. Network timeout — re-run manually via workflow_dispatch

The script prints `WARN:` for unresolved flag targets but does not raise an error —
those edges are silently skipped. A true failure will show in the Action log as
a Python exception.

---

## If you need to rebuild graph.json manually

```bash
cd /home/user/workspace/whitespace-repo
python3 scripts/build_graph.py
git add -f docs/data/graph.json
git commit -m "data: manual graph.json rebuild [YYYY-MM-DD]"
git push origin main
```

GitHub Pages redeploys automatically within ~1 minute of push.

---

## Reference: graph.json schema

```json
{
  "generated": "ISO timestamp",
  "node_count": 42,
  "edge_count": 112,
  "nodes": [
    {
      "id": "ai-governance",
      "type": "monitor",
      "monitor": "ai-governance",
      "label": "AI Governance",
      "color": "#4f98a3",
      "url": "https://asym-intel.info/monitors/ai-governance/2026-03-30/",
      "dashboard_url": "https://asym-intel.info/monitors/ai-governance/dashboard.html",
      "week_label": "23–29 March 2026",
      "date": "2026-03-30",
      "report_slug": "2026-03-30",
      "issue": 2,
      "description": "..."
    },
    {
      "id": "compossible-some-post-slug",
      "type": "compossible",
      "monitor": "ai-governance",
      "label": "Post Title",
      "url": "https://compossible.asym-intel.info/posts/...",
      "date": "2026-03-15",
      "description": "...",
      "post_type": "essay",
      "series": "",
      "series_part": null,
      "graph_tags": ["ai-governance", "tech-power-concentration"],
      "monitors_referenced": ["ai-governance"]
    }
  ],
  "edges": [
    {
      "id": "e-001",
      "source": "ai-governance",
      "target": "fimi-cognitive-warfare",
      "relation": "contextualises",
      "title": "Flag title",
      "rationale": "Why this edge exists",
      "edge_type": "monitor-monitor",
      "status": "Active",
      "flag_id": "cmf-001",
      "first_flagged": "2026-03-30",
      "report_url": "https://asym-intel.info/monitors/ai-governance/2026-03-30/"
    }
  ]
}
```

**Relation types:** `analyses`, `extends`, `contextualises`, `correlates`, `contradicts`, `cites`
(`contradicts` and `cites` defined in schema, not yet appearing in data as of 3 Apr 2026)

**Edge types:** `monitor-monitor`, `compossible-monitor`, `series-chain`

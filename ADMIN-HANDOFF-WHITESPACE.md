# Administrator Handoff — White Space & Compossible Graph Pipeline
# Session: 31 March – 3 April 2026
# This covers work done outside the normal asym-intel-main scope.
# Read alongside HANDOFF.md and COMPUTER.md.

---

## What happened

A separate Computer session (not the site management task) built the interactive
knowledge graph at whitespace.asym-intel.info. This is now a live, auto-updating
system with its own repo, cron schedule, and data pipeline. The Administrator
needs to know about it because:

1. It reads from the monitor JSON files this task publishes every week
2. It has its own GitHub Action that runs after the monitor crons
3. The Compossible posts were modified to support it

---

## New repo: asym-intel/asym-intel-whitespace

**Purpose:** Interactive force-directed knowledge graph showing relationships
between the 7 monitors and all analytical Compossible posts.

**Live at:** https://whitespace.asym-intel.info/

**Served from:** `docs/` folder on `main` branch (GitHub Pages, CNAME set)

**CRITICAL — gitignore trap:** `/docs/` is listed in `.gitignore` (Hugo artifact
left from initial setup). Every commit touching `docs/` needs:
```bash
git add -f docs/index.html docs/data/graph.json
```
Regular `git add docs/` silently adds nothing.

### File inventory

| File | What it is |
|---|---|
| `docs/index.html` | Full interactive canvas (~950 lines, self-contained) |
| `docs/data/graph.json` | Graph data — auto-rebuilt weekly |
| `docs/data/graph-edge-audit.md` | Rationale for every edge (for review) |
| `scripts/build_graph.py` | Rebuild script — fetches live monitor + Compossible JSON |
| `.github/workflows/rebuild-graph.yml` | Weekly GitHub Action |
| `CHARTS-KNOWHOW.md` | Does NOT exist in this repo — lives in asym-intel-main |

### Commit history (most recent first)

```
6474fbb  feat: auto-rebuild pipeline for graph.json  ← current HEAD
a9c3841  fix: click-after-close and double-click to dismiss panel
8166ab0  improve: text legibility and font sizes
36fa0a6  fix: force graph layout, DOM structure, and orphan nodes
367c119  feat: deploy interactive knowledge graph canvas
95af1f7  data: initial graph.json — 46 nodes, 128 edges + edge audit
4cfbc3a  feat: placeholder — pure white canvas below network bar
```

---

## Auto-rebuild cron: every Monday 09:00 UTC

**Workflow file:** `.github/workflows/rebuild-graph.yml`
**Schedule:** `cron: '0 9 * * 1'` (Monday 09:00 UTC)
**Also triggers on:** manual dispatch, or push to `scripts/build_graph.py`

### Why Monday 09:00 UTC is safe

The rebuild reads `report-latest.json` from all 7 monitors. The last monitor
to publish each week is SCEM at **Sunday 18:00 UTC**. Monday 09:00 UTC is
15 hours later — all 7 monitors will have published before the graph rebuilds.

Current monitor publish schedule for reference:
```
WDM  → Mon 06:00 UTC   (publishes before whitespace rebuild on the same Monday)
GMM  → Tue 08:00 UTC
ESA  → Wed 19:00 UTC
FCW  → Thu 09:00 UTC
AGM  → Fri 09:00 UTC
ERM  → Sat 05:00 UTC
SCEM → Sun 18:00 UTC   ← last to publish; whitespace rebuild is 15h after this
```

**Note:** WDM publishes at Mon 06:00 UTC, which is 3 hours BEFORE the whitespace
rebuild at Mon 09:00 UTC. So even WDM's latest data is included. Safe on all monitors.

### What the rebuild does

`scripts/build_graph.py` (stdlib only, no pip installs needed):

1. Fetches `https://asym-intel.info/monitors/{slug}/data/report-latest.json` (×7)
2. Fetches `https://asym-intel.info/monitors/{slug}/data/archive.json` (×7)
3. Fetches `https://compossible.asym-intel.info/posts-index.json`
4. Builds graph.json with nodes + edges
5. Writes to `docs/data/graph.json`
6. Commits only if the file changed (`git diff --quiet` check)
7. Commits as `github-actions[bot]`

The Action has `permissions: contents: write` — this is intentional and required
for the commit step.

### What appears in graph.json

- **42 nodes** (as of 31 March 2026 run): 7 monitor nodes + 35 Compossible posts
- **112 edges**: 24 monitor↔monitor, 81 post→monitor, 7 series chains
- Every monitor→monitor edge carries:
  - `first_flagged`: date the cross-monitor flag was first raised
  - `report_url`: direct URL to the dated report that raised it
  - `flag_id`: the CMF flag ID from `cross_monitor_flags`

Node/edge counts will drift slightly each week as new posts publish and
monitor reports update. This is correct behaviour.

---

## Change to Compossible posts: monitors_referenced frontmatter

A maintenance task (separate from this session) added a new frontmatter field
to all Compossible posts:

```yaml
monitors_referenced:
  - ai-governance
  - fimi-cognitive-warfare
```

This field tells the graph which monitors a post connects to. It is the primary
source for Compossible→monitor edges in graph.json. Without it, the script falls
back to inferring connections from `graph_tags` (less precise but still works).

### What the Administrator needs to ensure

The **Compossible cron prompt** must continue to populate `monitors_referenced`
on all new posts. If it stops doing so:
- New posts will fall back to graph_tag inference (still works, just less precise)
- Posts with no graph_tags and no monitors_referenced will be excluded from the graph as orphans

This is not a breaking failure — the graph will just be less connected for new posts.
Check it periodically by looking at `posts-index.json` and verifying new entries
have `monitors_referenced: [...]` populated.

---

## New governance file: CHARTS-KNOWHOW.md

Committed to `asym-intel/asym-intel-main` at root level (alongside COMPUTER.md).

**Commit:** `a80b814`

**How to read it:**
```bash
gh api /repos/asym-intel/asym-intel-main/contents/CHARTS-KNOWHOW.md \
  --jq '.content' | base64 -d
```

**What it contains:** Full chart/visualisation role handoff — Chart.js versions,
dark mode status per monitor, whitespace graph architecture, visual audit findings,
Sprint 2 pending charts, and failure modes. Primarily for the charts/site-management
role. The Administrator only needs Section 3 (White Space Network Graph).

---

## Nothing broken, nothing pending in this repo

The whitespace repo is in a clean state. The auto-rebuild runs autonomously.
No PR approvals needed, no staging branch, no CI validator (unlike asym-intel-main).

The only ongoing maintenance tasks are:
1. Ensure Compossible cron continues populating `monitors_referenced` on new posts
2. If the rebuild Action ever fails (check Actions tab on the whitespace repo),
   the most likely cause is a changed URL or field name in a monitor's JSON.
   The script prints `WARN:` lines for unresolved flags but does not error on them.
   A true failure would be a network error or JSON parse error — check the Action log.

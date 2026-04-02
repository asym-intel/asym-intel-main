# Asymmetric Intelligence — Working Agreement (COMPUTER.md)
## Version 2.1 — April 2026
## Read this at the start of every session touching asym-intel.info

---

> **Before any HTML, CSS, JS, or layout work — read `docs/ARCHITECTURE.md`.**
> It explains the two-source-tree rule (`static/` is source, `docs/` is output),
> both failure modes that have occurred, and the Hugo vs. static page distinction.
> Three minutes. Prevents hours of debugging.
>
> ```bash
> gh api /repos/asym-intel/asym-intel-main/contents/docs/ARCHITECTURE.md \
>   --jq '.content' | base64 -d
> ```

---

## Step 0 — Load Working Agreement (ALWAYS FIRST)

Before any other action, fetch and read both files:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d

gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md \
  --jq '.content' | base64 -d
```

Use `api_credentials=["github"]` for all GitHub operations.

## Two Systems — Different Rules

### Monitor pages (static HTML in static/monitors/)
- **Staging first** for any HTML/CSS/JS changes — ALWAYS
- Edit `static/monitors/{slug}/*.html` — NEVER edit `docs/monitors/{slug}/*.html` directly
- Shared library: `static/monitors/shared/` — one change hits all 7 monitors
- Per-monitor: `assets/monitor.css` ≤40 lines, accent tokens only
- CI validator runs 15+ checks on every push against `static/monitors/`
- After editing, always sync: `cp static/monitors/{slug}/page.html docs/monitors/{slug}/page.html`

### Hugo content pages (layouts/, assets/css/main.css)
- `assets/css/main.css` and `layouts/` are Hugo source — edit **directly on main**
- No staging detour needed for Hugo CSS/layout changes
- Hugo rebuilds on every push and overwrites `docs/` — source of truth is `layouts/` and `assets/`
- New Hugo page: create `content/{name}.md` + `layouts/{type}/single.html` — never a raw file in `docs/`

## Deployment Rules

| Change type | Branch | Approval needed |
|---|---|---|
| Monitor HTML/CSS/JS pages | staging → PR → main | Yes — user visual sign-off |
| Hugo layouts/main.css | main directly | No — validator catches regressions |
| JSON data files (cron output) | main directly | No — autonomous |
| Hugo brief markdown | main directly | No — autonomous |
| COMPUTER.md / HANDOFF.md / ARCHITECTURE.md | main directly | No — documentation |

## Architecture (Blueprint v2.1)

### Network bar (both Hugo and monitor pages)
- `position: fixed`, `height: 40px`, full-bleed, `z-index: 9999`
- Brand name always visible on mobile
- Monitors/Compossible/White Space in hamburger dropdown on mobile (640px)
- Implemented in: `layouts/partials/network-bar.html` + `assets/css/main.css`
- On monitor pages: injected at runtime by `shared/js/nav.js` — NOT in the HTML source

### Monitor nav (monitor pages only)
- `position: sticky`, `top: 40px` (sits below fixed network bar)
- Hamburger shows 8 page links on mobile (768px)
- Implemented in: `static/monitors/shared/css/base.css` + `static/monitors/shared/js/nav.js`
- **8 standard links (all monitors):** Overview · Dashboard · Latest Issue · Archive · Living Knowledge · About · Methodology · Search
- When adding a nav link: edit EVERY page for that monitor in `static/monitors/{slug}/*.html` AND sync each to `docs/monitors/{slug}/*.html`

### Body offset
- ALL pages: `body { padding-top: 40px }` (network bar is fixed)
- Hugo pages: in `assets/css/main.css`
- Monitor pages: in `static/monitors/shared/css/base.css`

### Critical CSS rules (NEVER violate)
- `overflow-x: clip` — NEVER `overflow-x: hidden` on body, monitor-layout, or monitor-main
  → `overflow:hidden` on a parent silently breaks `position:sticky` on all children
- `nav.js` must be in `<head>` after `theme.js` — not bottom of body
- `Chart.js CDN` must be in `<head>` before `charts.js` wrapper on any page using `<canvas>`

### Site-nav (Hugo pages — homepage/briefs)
- White bar below network bar, `position: sticky`, `top: 40px`
- Contains: About (plain link) + Search (plain link with icon) + Subscribe (button)
- NO brand name, NO SVG, NO Monitors link (all in black bar)
- NO hamburger — About and Search are always visible
- Implemented in: `layouts/partials/site-header.html`
- Search links to `/search/` — clean Hugo URL (asym-intel.info/search/), NOT /search.html

## CI Validator (15+ checks)
`.github/validate-blueprint.py` runs on every push. FAIL = broken build.
Checks: page existence, nav.js in head, base.css present, monitor.css ≤40 lines,
JSON validity, schema_version 2.0, no future dates, no stale inline bars,
body padding-top, network-bar fixed, monitor-nav top:40px,
nav.js in head (not body), Chart.js CDN, no overflow:hidden on layout containers.

**Validator reads `static/monitors/` — not `docs/`.** A file missing from `static/`
but present in `docs/` will pass validation but vanish on the next Hugo build.

## Cron Tasks (data-only, fully autonomous)

Each monitor cron publishes on its schedule without approval:
- Writes ONLY: `data/report-latest.json`, `data/report-DATE.json`, `data/archive.json`,
  `data/persistent-state.json`, `content/monitors/{slug}/DATE-brief.md`
- NEVER touches HTML, CSS, JS, or any other file
- All prompts start by reading COMPUTER.md and ARCHITECTURE.md from repo

| Monitor | Cron ID | Schedule |
|---|---|---|
| WDM | db22db0d | Mon 06:00 UTC |
| GMM | 02c25214 | Mon 08:00 UTC |
| FCW | 879686db | Thu 09:00 UTC |
| ESA | 0fa1c44e | Wed 19:00 UTC |
| AGM | 267fd76e | Fri 09:00 UTC |
| ERM | 3e736a32 | Sat 05:00 UTC |
| SCEM | eb312202 | Sun 18:00 UTC |
| Housekeeping | 73452bc6 | Mon 08:00 UTC |

## Monitor Reference

| Abbr | Slug | Accent | Publish |
|------|------|--------|---------| 
| WDM | democratic-integrity | #61a5d2 | Mon 06:00 |
| GMM | macro-monitor | #22a0aa | Mon 08:00 |
| FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 |
| ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 |
| AGM | ai-governance | #3a7d5a | Fri 09:00 |
| ERM | environmental-risks | #4caf7d | Sat 05:00 |
| SCEM | conflict-escalation | #dc2626 | Sun 18:00 |

## Flags (Country Emoji Flags)

Country flag emojis are available via `AsymRenderer.flag(countryName)` in all
monitor dashboard pages. The function is implemented in `static/monitors/shared/js/renderer.js`.

**Usage:**
```js
AsymRenderer.flag('Hungary')    // → '🇭🇺'
AsymRenderer.flag('Russia')     // → '🇷🇺'
AsymRenderer.flagLabel('Serbia') // → '🇷🇸 Serbia'
```

**Where flags must appear (all monitors):**
- Country Severity Ranking bar (renderSeverityBar)
- Severity cards (renderSeverityCards)
- Country tables (any `<td>` with a country name)
- Any ranked list of countries

**When adding a new country display:** always check whether `AsymRenderer.flag()` is
being called. Omitting it is a persistent bug pattern — search for `escHtml(c.country)`
or `esc(country)` and verify the flag call precedes it.

## Common Pitfalls — Do Not Repeat

1. **Editing docs/ directly** — use `static/` then sync to `docs/`. Next Hugo build overwrites `docs/`.
2. **Editing docs/ but not static/** — same result. Both must always match.
3. **overflow:hidden on layout containers** — use `overflow-x:clip` always
4. **nav.js in body** — must be in `<head>` after `theme.js`
5. **Chart.js CDN missing** — add before `charts.js` in `<head>`
6. **Raw HTML file in docs/** — Hugo-rendered pages must be `content/` + `layouts/`, never a raw `docs/*.html`. Hugo clean URLs produce `docs/{name}/index.html`, not `docs/{name}.html`. Both can coexist and confuse — delete the `.html` version if the Hugo page exists.
7. **Hugo comment in static HTML** — `{{/* */}}` only works in Hugo templates, not in `static/` files
8. **Nav link missing from some pages** — when adding a nav link, update ALL pages for that monitor in BOTH `static/` and `docs/`
9. **Flag missing from country display** — always call `AsymRenderer.flag()` before `escHtml(c.country)`
10. **monitor.css bloat** — component styles belong in base.css, not per-monitor CSS
11. **Future-dated JSON** — validator catches this; Hugo skips future pages silently
12. **archive.json** — append only, never truncate
13. **schema_version** — must be "2.0" in all JSON files
14. **COMPUTER.md wiped** — never use Python `open(path, 'w')` without reading the file first; use `read()` → modify → `write()`

## Three-Layer Intelligence Architecture (v2.2)

Canonical strategy document (read before building any Collector or Analyst):
  gh api /repos/asym-intel/asym-intel-internal/contents/COLLECTOR-ANALYST-ARCHITECTURE.md \
    --jq '.content' | base64 -d



Every monitor runs an Analyst. Selected monitors also run a Collector.
One Validator (Housekeeping) covers all monitors.

LAYER 1 — COLLECTOR (daily Computer cron)
  Searches public sources → structures into Tier 0 JSON → commits to pipeline/
  Authority: confidence_preliminary only. Never touches data/, report-latest.json,
  persistent-state.json, or archive.json. The Analyst reads and decides.
  Prompt location: asym-intel-internal/prompts/{MONITOR}-COLLECTOR-PROMPT-v{N}.md
  Bootstrap pattern: short cron wrapper (<1000 chars) loads prompt at runtime.

LAYER 2 — ANALYST (weekly Computer cron)
  Reads pipeline/daily-latest.json at Step 0C (if Collector exists).
  Applies monitor methodology → assigns final confidence → publishes to data/.
  Prompt location: static/monitors/{slug}/{abbr}-cron-prompt.md (public repo)

LAYER 3 — VALIDATOR (weekly Computer cron, Monday)
  Validates all Analyst outputs + all Collector pipeline files.
  Compiles intelligence-digest.json. Runs checks 1–20.

## Active Crons

| Layer | Name | Cron ID | Schedule |
|-------|------|---------|----------|
| Collector | FCW Collector | GitHub Actions | Daily 07:00 UTC (external — see .github/workflows/fcw-collector.yml) |
| Analyst | WDM Analyst | db22db0d | Mon 06:00 UTC |
| Analyst | GMM Analyst | 02c25214 | Tue 08:00 UTC |
| Analyst | ESA Analyst | 0fa1c44e | Wed 19:00 UTC |
| Analyst | FCW Analyst | 879686db | Thu 09:00 UTC |
| Analyst | AGM Analyst | 267fd76e | Fri 09:00 UTC |
| Analyst | ERM Analyst | 3e736a32 | Sat 05:00 UTC |
| Analyst | SCEM Analyst | eb312202 | Sun 18:00 UTC |
| Validator | Platform Validator | 73452bc6 | Mon 08:00 UTC |

## pipeline/ Directory
pipeline/monitors/{slug}/daily/ — Collector outputs, internal only.
Hugo never builds from pipeline/ — never publicly served.
See pipeline/README.md for full pattern documentation.

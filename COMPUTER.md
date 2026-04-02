# Asymmetric Intelligence — Working Agreement (COMPUTER.md)
## Version 2.3 — 2 April 2026
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
| GMM | 02c25214 | Tue 08:00 UTC |
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
| GMM | macro-monitor | #22a0aa | Tue 08:00 |
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

## Three-Layer Intelligence Architecture (v2.3)

Canonical strategy document (read before building any Collector or Analyst):
  gh api /repos/asym-intel/asym-intel-internal/contents/COLLECTOR-ANALYST-ARCHITECTURE.md \
    --jq '.content' | base64 -d

Pipeline build guide (step-by-step for adding any monitor):
  gh api /repos/asym-intel/asym-intel-main/contents/pipeline/PIPELINE-BUILD-PATTERN.md \
    --jq '.content' | base64 -d

LAYER 1 — COLLECTOR (GitHub Actions — NOT a Computer cron)
  Runs in GitHub Actions (.github/workflows/{monitor}-collector.yml)
  Calls Perplexity API → validates schema → commits to pipeline/monitors/{slug}/daily/
  Model: sonar (daily) | sonar-pro (weekly research) | sonar-deep-research (Reasoner only)
  CRITICAL: sonar-deep-research does NOT search the web. Use only for reasoning over
  structured data you provide. sonar-pro for all live web search workflows.
  Output: pipeline/monitors/{slug}/daily/ and pipeline/monitors/{slug}/weekly/
  NEVER write to data/, report-latest.json, persistent-state.json, or archive.json

LAYER 2 — ANALYST (Computer weekly cron)
  Reads Steps 0C (daily Collector), 0D (weekly research), 0E (Reasoner) from pipeline/
  Applies monitor methodology → assigns final confidence → publishes to data/

LAYER 3 — PLATFORM VALIDATOR (Computer weekly cron, Monday)
  Validates all Analyst outputs + all Collector pipeline files (checks 1–20)
  Compiles intelligence-digest.json

## Active Crons (Computer)

| Layer | Name | Cron ID | Schedule |
|---|---|---|---|
| Analyst | WDM Analyst | db22db0d | Mon 06:00 UTC |
| Analyst | GMM Analyst | 02c25214 | Tue 08:00 UTC |
| Analyst | ESA Analyst | 0fa1c44e | Wed 19:00 UTC |
| Analyst | FCW Analyst | 879686db | Thu 09:00 UTC |
| Analyst | AGM Analyst | 267fd76e | Fri 09:00 UTC |
| Analyst | ERM Analyst | 3e736a32 | Sat 05:00 UTC |
| Analyst | SCEM Analyst | eb312202 | Sun 18:00 UTC |
| Validator | Platform Validator | 73452bc6 | Mon 08:00 UTC |
| Verification | SCEM verification | a67a9739 | Sun 5 Apr 18:30 UTC (one-shot) |
| Verification | WDM verification | 10ddf5f0 | Mon 6 Apr 06:30 UTC (one-shot) |

## Active GitHub Actions (external pipeline — NOT Computer crons)

| Monitor | Workflow | Schedule | Model |
|---|---|---|---|
| FCW | fcw-collector.yml | Daily 07:00 UTC | sonar |
| FCW | fcw-weekly-research.yml | Wed 18:00 UTC | sonar-pro |
| FCW | fcw-reasoner.yml | Wed 20:00 UTC | sonar-deep-research |
| GMM | gmm-collector.yml | Daily 06:00 UTC | sonar |
| GMM | gmm-weekly-research.yml | Mon 18:00 UTC | sonar-pro |
| GMM | gmm-reasoner.yml | Mon 20:00 UTC | sonar-deep-research |
| SCEM | scem-collector.yml | Daily 06:00 UTC | sonar |
| SCEM | scem-weekly-research.yml | Sat 18:00 UTC | sonar-pro |
| SCEM | scem-reasoner.yml | Sat 20:00 UTC | sonar-deep-research |

## pipeline/ Directory
pipeline/monitors/{slug}/ — GitHub Actions Collector outputs. Internal only.
Hugo never builds from pipeline/. Never publicly served.

---

## Session Continuity Protocol

### Trigger word: "wrap"
Say "wrap" at any point to run the session checkpoint. Computer will surface
what has accumulated and confirm before committing. Same pattern as "merge".

### During-session logging (not batched at end)
Whenever a significant change occurs during a session, Computer logs it to
notes-for-computer.md immediately -- not at the end. Significant = any of:
  - New cron created or deleted
  - New GitHub Actions workflow
  - Architecture decision made
  - Methodology gap identified and fixed
  - New file pattern established
  - Bug fixed that could recur on other monitors

Computer checks in at natural checkpoints (after a sprint of related work,
before moving to a new topic) and asks: "Ready to log this to notes and
update HANDOFF.md?" -- same as asking "approve merge?".

### "wrap" trigger procedure
When you say "wrap", Computer:
1. Summarises what changed this session (commits, decisions, new patterns)
2. Logs significant items to notes-for-computer.md
3. Updates HANDOFF.md with current session state
4. Checks: any unmerged staging changes? any new crons missing from COMPUTER.md?
5. **Open staging check** — if staging is ahead of main, list the staged files and ask:
   "Staging has N files ready. Do you want to merge before closing?"
   If yes: open PR staging → main and merge immediately.
   Never leave the day with an unreviewed staging branch unless Peter explicitly defers.
6. Confirms all done before ending

### HANDOFF.md ownership
- Auto-generated every Monday by Housekeeping (from live repo state)
- Updated mid-week by "wrap" trigger or Computer checkpoint
- Never left empty -- if empty, something went wrong with both mechanisms
- Never hand-written speculatively -- always generated from actual state

```bash
# 1. Verify all commits reached main (not stuck in staging)
gh api /repos/asym-intel/asym-intel-main/commits --jq '.[0] | {sha:.sha[:8], message:.commit.message[:80]}'

# 2. Check no staging branch changes are unmerged (if staging was used)
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '.ahead_by'
# If ahead_by > 0: either merge or document why staging diverges

# 3. If methodology or architecture changed: update notes-for-computer.md
# gh api /repos/asym-intel/asym-intel-internal/contents/notes-for-computer.md ...

# 4. If significant session (new features, architecture changes, new crons):
#    Update HANDOFF.md manually -- do not wait for Monday Housekeeping
gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md --jq '.size'
# If HANDOFF.md size is 0 or suspiciously small: rewrite it now

# 5. If COMPUTER.md was not updated this session but should have been:
#    Bump the version date and add the changes
```

**Log to notes-for-computer.md immediately (not at session end) when:**
- New cron created or deleted -> log cron ID, schedule, purpose
- New GitHub Actions workflow -> log what it does and when
- Architecture decision made -> log the decision and the reason
- Methodology gap identified and fixed -> log what changed and why
- New file pattern established (e.g. annual calibration convention) -> log it

**HANDOFF.md:** auto-generated Monday by Housekeeping. Updated mid-week by "wrap".

## ARCHITECTURE.md (MANDATORY for HTML/CSS/JS work)

Read before any build work:
  gh api /repos/asym-intel/asym-intel-main/contents/docs/ARCHITECTURE.md --jq '.content' | base64 -d

Update it when new patterns or fixes are discovered. Never end a build session without checking if ARCHITECTURE.md should be updated.
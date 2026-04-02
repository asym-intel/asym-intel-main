# Asymmetric Intelligence — Build & Deployment Architecture
## Version 1.0 — April 2026
## Read this before touching any HTML, CSS, JS, or layout file.

---

## The Two-Source-Tree Rule

This repository has **two source trees** that serve different purposes. Every
bug we have had with changes "not appearing" traces back to editing one tree
when both needed to be changed, or vice versa.

```
asym-intel-main/
│
├── static/monitors/{slug}/*.html   ← MONITOR PAGES — edit these
├── layouts/                        ← HUGO LAYOUTS — edit these
├── assets/css/main.css             ← HUGO CSS — edit this
├── content/                        ← HUGO CONTENT — edit this
│
└── docs/                           ← NEVER EDIT DIRECTLY
    ├── monitors/{slug}/*.html      ← auto-generated copies of static/monitors/
    ├── index.html                  ← built from layouts/ + content/
    ├── css/main.css                ← built from assets/css/main.css
    └── ...all other Hugo output
```

**`docs/` is always generated output. It is never the source of truth.**

---

## What Goes Where — Decision Table

| What you want to change | Edit this | Never edit this |
|---|---|---|
| Monitor nav, dashboard, report, archive, persistent, about, search, overview | `static/monitors/{slug}/*.html` | `docs/monitors/{slug}/*.html` |
| Homepage layout | `layouts/index.html` | `docs/index.html` |
| Site-wide CSS (Hugo pages) | `assets/css/main.css` | `docs/css/main.css` |
| Network bar | `layouts/partials/network-bar.html` | anything in `docs/` |
| Site-nav (About / Search / Subscribe bar) | `layouts/partials/site-header.html` | anything in `docs/` |
| Hugo brief / methodology page | `content/monitors/{slug}/*.md` | anything in `docs/` |
| New Hugo page type (e.g. search) | `content/` + `layouts/{type}/single.html` | `docs/` directly |
| Monitor JSON data | `static/monitors/{slug}/data/*.json` | `docs/monitors/{slug}/data/*.json` |
| Shared monitor CSS | `static/monitors/shared/css/base.css` | `docs/monitors/shared/css/base.css` |
| Shared monitor JS | `static/monitors/shared/js/*.js` | `docs/monitors/shared/js/*.js` |

---

## How a Change Gets from Source to Live Site

### Monitor pages (`static/monitors/`)

```
You edit static/monitors/{slug}/dashboard.html
        ↓
git push → main
        ↓
GitHub Actions: build.yml
  1. validate-blueprint.py runs against static/monitors/ ← validator reads static/
  2. hugo --minify runs
     Hugo copies static/monitors/ → docs/monitors/    ← docs/ is OVERWRITTEN
  3. GitHub Actions commits docs/ to main ("build: auto-rebuild [skip ci]")
        ↓
GitHub Pages serves docs/
        ↓
Live at asym-intel.info
```

**Key implication:** If you edit `docs/monitors/` directly, the next push that
triggers a Hugo build will **overwrite your edit**. The only durable change
is in `static/monitors/`.

**Key implication:** The validator (`validate-blueprint.py`) runs against
`static/monitors/` — not `docs/`. A file present in `docs/` but absent from
`static/` will pass validation but disappear on the next build.

### Hugo content pages (`layouts/`, `assets/`, `content/`)

```
You edit layouts/partials/site-header.html
        ↓
git push → main
        ↓
GitHub Actions: build.yml
  1. validate-blueprint.py runs (does not check Hugo source files)
  2. hugo --minify rebuilds ALL Hugo-rendered pages into docs/
  3. GitHub Actions commits docs/ ("build: auto-rebuild [skip ci]")
        ↓
Live at asym-intel.info
```

Hugo processes: `layouts/` + `content/` + `assets/` → outputs to `docs/`

Hugo does **not** process: `static/monitors/*.html` — these are copied verbatim.

### What triggers the Hugo build

The build workflow (`build.yml`) triggers on push to `main` or `staging`
**unless the only changed files are in `docs/`**:

```yaml
paths-ignore:
  - 'docs/**'
```

This means: editing `docs/` directly and pushing will **not** trigger a rebuild.
The next push to a non-`docs/` file will rebuild and may overwrite your `docs/` edit.

---

## The Two Failure Modes (both have happened)

### Failure Mode 1: Editing docs/ directly

**What it looks like:** Change appears on the live site temporarily, then
disappears after the next unrelated push.

**Example:** Writing `docs/search.html` as a raw HTML file. It served correctly
until a subsequent push triggered `hugo --minify`, which overwrote `docs/` and
the file was gone.

**Fix:** Always edit `static/monitors/` for monitor pages. For Hugo-rendered
pages, create `content/` + `layouts/` — never touch `docs/` directly.

### Failure Mode 2: Editing docs/ but not static/

**What it looks like:** Change appears live immediately, but the validator
reports the old state, and the next build reverts the change.

**Example:** PR #26 patched `docs/monitors/` for 5 monitors but missed
`static/monitors/`. Changes appeared merged but nav was still 6 links because
`static/` was the source Hugo built from — so the next build restored the old nav.

**Fix:** Always confirm both trees are in sync. After any monitor HTML change,
check: is it in `static/monitors/{slug}/` (source) AND `docs/monitors/{slug}/`
(current served copy)?

---

## The Build Workflow in Full

Three GitHub Actions workflows run on push to `main`:

| Workflow | File | What it does | Reads | Writes |
|---|---|---|---|---|
| **Build and deploy** | `build.yml` | Runs validator, then Hugo build | `static/`, `layouts/`, `assets/`, `content/` | `docs/` |
| **Inject network bar** | `inject-network-bar.yml` | Strips stale inline network bars from monitor pages | `static/monitors/` | `static/monitors/` |
| **Compress images** | `compress-images.yml` | Optimises images in `static/` | `static/` | `static/` |

The build workflow is the one that produces `docs/`. It:
1. Runs `validate-blueprint.py` against `static/monitors/`
2. Runs `hugo --minify --buildFuture`
3. Commits any changes to `docs/` with message `"build: auto-rebuild [skip ci]"`

The `[skip ci]` tag prevents the auto-commit from re-triggering the workflow.

---

## Hugo Pages vs. Monitor Pages — Critical Distinction

The site has two completely different rendering systems. Understanding which
system a page belongs to determines where to edit it.

### Hugo-rendered pages

These are generated by Hugo from templates and markdown:

- `asym-intel.info/` (homepage)
- `asym-intel.info/about/`
- `asym-intel.info/mission/`
- `asym-intel.info/monitors/` (index listing)
- `asym-intel.info/monitors/{slug}/` (per-monitor brief listing)
- `asym-intel.info/monitors/{slug}/{date}-weekly-brief/` (individual briefs)
- `asym-intel.info/monitors/{slug}/methodology/` (methodology pages)
- `asym-intel.info/search/` (site-wide search)
- `asym-intel.info/subscribe/`

These pages have the full network bar, site-nav (About/Search/Subscribe),
and footer from Hugo partials. **Edit the layout or markdown, not `docs/`.**

### Static monitor pages (verbatim copies)

These are HTML files copied verbatim from `static/` into `docs/`:

- `asym-intel.info/monitors/{slug}/dashboard.html`
- `asym-intel.info/monitors/{slug}/report.html`
- `asym-intel.info/monitors/{slug}/archive.html`
- `asym-intel.info/monitors/{slug}/persistent.html`
- `asym-intel.info/monitors/{slug}/about.html`
- `asym-intel.info/monitors/{slug}/search.html`
- `asym-intel.info/monitors/{slug}/overview.html`
- `asym-intel.info/monitors/{slug}/methodology.html`

These pages use the shared monitor library (`shared/css/base.css`,
`shared/js/nav.js`, `shared/js/renderer.js`). The network bar is injected
by `nav.js` at runtime — it is **not** in the HTML source.
**Edit `static/monitors/{slug}/*.html` directly.**

### How to tell which system a page uses

Look at the URL:
- URL ends in `/` (clean URL) → Hugo-rendered → edit `content/` or `layouts/`
- URL ends in `.html` → static monitor page → edit `static/monitors/{slug}/`

---

## Staging Workflow

HTML/CSS/JS changes to monitor pages go through staging before merge to main.

```
Create branch: staging/your-feature-name
        ↓
Push changes to static/monitors/
        ↓
GitHub Actions builds a staging preview
        ↓
Peter visual sign-off
        ↓
Merge PR to main → build.yml rebuilds docs/ → live
```

Hugo source changes (`layouts/`, `assets/css/main.css`) go **direct to main**
— Hugo rebuilds on every push and the validator will catch regressions.

JSON data files from cron agents go **direct to main** — they are autonomous
and pre-validated by the cron prompt.

---

## Quick Reference Card

```
WANT TO CHANGE                          EDIT
────────────────────────────────────────────────────────────
Monitor nav links                       static/monitors/{slug}/*.html (ALL pages)
Monitor page content/layout             static/monitors/{slug}/{page}.html
Shared monitor component (all 7)        static/monitors/shared/css/base.css
                                        static/monitors/shared/js/renderer.js
Network bar (black top bar)             layouts/partials/network-bar.html
Site-nav (About/Search/Subscribe)       layouts/partials/site-header.html
Homepage                                layouts/index.html
Hugo site CSS                           assets/css/main.css
New Hugo page type                      content/{name}.md + layouts/{type}/single.html
Monitor JSON data                       static/monitors/{slug}/data/*.json
Hugo brief (weekly)                     content/monitors/{slug}/{date}-brief.md

NEVER EDIT docs/ DIRECTLY.
If docs/ is wrong, find the source file in the table above and fix that.
```

---

## Why docs/ Exists in the Repo at All

GitHub Pages can serve from the repo root, a `docs/` folder, or a separate
branch. This repo uses `docs/` because:

1. It keeps the source and built output in the same branch (easier to inspect)
2. It avoids a separate `gh-pages` branch that diverges from main

The cost is that `docs/` looks editable — it is a folder full of `.html` files.
The rule is simple: **never edit it**. It is the build artifact, not the source.

---

## Known CI/CDN timing issues

- **Hugo CI race condition:** The `build.yml` workflow triggers on every push to non-`docs/` paths, rebuilds, then commits `docs/` with `[skip ci]`. If two pushes land in quick succession, the second CI build may run from a tree that includes the first push's source changes but not its `docs/` output — producing stale output. **Fix:** After any layout or partial change, run Hugo locally (`/tmp/hugo --minify`), then commit `docs/` with `[skip ci]` in the message. This bypasses the CI entirely and the race cannot occur.

- **GitHub Pages CDN cache:** After a `docs/` commit, GitHub Pages CDN may serve a stale version for 2–5 minutes. The repo file size via `gh api ... --jq '.size'` is the ground truth — if the repo has the correct size, the CDN will catch up without intervention.

---

*This document is the single source of truth for build and deployment architecture.
Update it when the pipeline changes. Commit directly to main.*
*Maintainer: Computer*

---

## Governance File Protection

Critical platform governance files are protected by three layers:

### Layer 1 — CODEOWNERS (prevention)
`.github/CODEOWNERS` requires owner review before any commit that touches:
`COMPUTER.md`, `HANDOFF.md`, `MISSION.md`, `ROLES.md`, `ARCHITECTURE.md`,
`publishing-workflow.md`, `docs/audits/master-action-plan.md`,
the shared monitor library, and GitHub Actions workflows.

A PR touching these files cannot be merged without approval — even from `monitor-bot`.

### Layer 2 — Validator check 21 (detection)
`validate-blueprint.py` Check 21 runs on every push and **fails the build** if any
critical governance file is 0 bytes or suspiciously small (<500 bytes).
This catches silent wipes within one build cycle.

### Layer 3 — Governance mirror (recovery)
All critical governance files are mirrored to `asym-intel-internal/governance/`.
This repo is private and append-only by convention.

**Recovery procedure — if a file is wiped:**

```bash
# Step 1: Read good copy from internal mirror
gh api /repos/asym-intel/asym-intel-internal/contents/governance/COMPUTER.md \
  --jq '.content' | base64 -d > /tmp/restored.md

# Step 2: Verify it has real content (must be > 500 bytes)
wc -c /tmp/restored.md

# Step 3: Restore to public repo
cd /tmp && gh repo clone asym-intel/asym-intel-main restore-run -- --depth=1 --quiet
cp /tmp/restored.md /tmp/restore-run/COMPUTER.md
cd /tmp/restore-run
git config user.name "monitor-bot"
git config user.email "monitor-bot@asym-intel.info"
git add COMPUTER.md
git commit -m "restore: COMPUTER.md from governance mirror (asym-intel-internal)"
git push origin main
```

Replace `COMPUTER.md` with whichever file needs restoring. The mirror filename
matches the basename of the public repo file.

### The root cause this protects against

Python's `open(path, 'w')` truncates the file to 0 bytes before writing.
If the write is then conditional, partial, or errored, the file is left empty.
The empty file gets `git add`ed and committed — silently.

**Safe pattern for all file operations:**
```python
# ALWAYS read first
with open(path) as f:
    content = f.read()
# Modify in memory
content = content.replace(old, new)
# Write only after successful modification
with open(path, 'w') as f:
    f.write(content)
```

**Never:**
```python
with open(path, 'w') as f:       # File is now empty
    f.write(generate_content())   # If this raises, file stays empty
```

---

## Rendering LLM-Generated Content (FE-020)

**Anti-pattern:** calling `escHtml()` or `esc()` directly on fields generated by cron agents.

Cron agent output fields — `weekly_brief`, `note`, `summary`, `narrative` and similar — contain a mix of:
- Markdown syntax: `**bold text**`, `# headings`
- Raw HTML anchor tags: `<a href="..." target="_blank">link text</a>`

Running `escHtml()` on these fields produces literal `**text**` and `&lt;a href=...&gt;` in the rendered page.

### The canonical fix: inline renderMarkdown (report.html pattern)

```js
// WRONG — escHtml destroys markdown syntax and <a> tags
element.innerHTML = '<p>' + escHtml(d.weekly_brief) + '</p>';

// CORRECT — inline pattern from report.html (proven working)
function renderMarkdown(md) {
  if (!md) return '';
  return md
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, ' ')
    .replace(/^/, '<p>').replace(/$/, '</p>');
}
element.innerHTML = '<div style="line-height:1.75;font-size:var(--text-sm)">' + renderMarkdown(d.weekly_brief) + '</div>';
```

This pattern is proven working in `static/monitors/democratic-integrity/report.html`. Copy it inline into each dashboard — do not use `AsymRenderer.renderMarkdown()` for `weekly_brief`.

**Why not `AsymRenderer.renderMarkdown()`?** It splits on `<a>` tags before applying the `**bold**` regex. If a paragraph opens with `**bold text**` and the closing `**` is in the same text segment as an `<a>` tag, the split can leave orphaned asterisks that the regex doesn't match. The inline pattern avoids this by doing a single-pass replace with no splitting.

**Rule:** Use `escHtml()` only for structured data fields (scores, IDs, country codes, dates). For narrative text fields (`weekly_brief`, `summary`, `note`), use the inline renderMarkdown pattern above.

**Added:** 2 April 2026 | **Updated:** 2 April 2026 (corrected — inline pattern is canonical, not AsymRenderer) | **Anti-pattern:** FE-020 in `static/monitors/shared/anti-patterns.json`

---

## SCEM: roster_watch Deduplication Rule (DQ-001)

**Pattern:** The SCEM Analyst cron must never place a conflict in `roster_watch.approaching_inclusion` if it is already present in `conflict_roster`.

**Root cause observed:** 2 April 2026. `US–Israel vs Iran` appeared in both `conflict_roster` (entry #10) and `roster_watch.approaching_inclusion`. The Analyst correctly identified escalation criteria but failed to cross-check against the current roster.

**Fix location:** SCEM Analyst cron prompt — add to the `roster_watch` population step:
> "Before adding any conflict to `roster_watch.approaching_inclusion`, verify it is not already present in `conflict_roster`. Scan `conflict_roster[*].conflict` values and exclude any matches."

**Self-correcting?** Yes — next weekly run will not re-add a rostered conflict. But the explicit rule prevents edge cases where a conflict is promoted and watch-listed in the same cycle.

**When to apply:** Next time the SCEM Analyst cron prompt is edited (Sprint 4 or sooner).

**Added:** 2 April 2026

---

## Pre-Staging Checklist (run before every `git push staging`)

When adding any new section to a monitor dashboard, verify ALL of the following before pushing:

### 1. Section is inside `<main>`
```
grep -n "</main>\|id=\"section-{your-id}\"" dashboard.html
```
Section position must be LESS than `</main>` position. If greater — the section is orphaned outside the layout and will render broken.

### 2. Sidebar nav link added
```
grep "your-section-id" dashboard.html | grep "monitor-sidebar\|sidebar-nav"
```
Every new section needs a corresponding `<li><a href="#section-id">Label</a></li>` in the right-hand sidebar nav.

### 3. Render call is inside the fetch `.then()` block — not after `.catch`
```
grep -n "renderYourFunction\|\.catch(" dashboard.html
```
The render call must be INSIDE the `.then(function(d) { ... })` block — not after the `.catch`.
The simplest check: the render call should be followed by `})` then `.catch` within a few lines.
Note: in large fetch blocks (e.g. GMM), the `.catch` may be hundreds of lines after the render call — this is fine as long as the render call is inside the `then` block, not after the closing `});`.
The reliable check is visual: look at the closing `}` immediately after your render call — it should be the close of the `then` block, not a standalone function.

### 4. Both `static/` and `docs/` mirrors updated
Every change to `static/monitors/{slug}/page.html` must be mirrored to `docs/monitors/{slug}/page.html`. Hugo overwrites `docs/` on build — if `static/` and `docs/` diverge, the next build silently reverts your change.

### 5. Flag field names match the monitor's actual data schema
Before writing a render function, check the actual JSON:
```
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{slug}/data/report-latest.json \
  --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(list(d['cross_monitor_flags']['flags'][0].keys()))"
```
Different monitors use different field names (e.g. `title` vs `headline`). Always check before assuming.

**Recurring bugs caught by this checklist:**
- FE-021 (2 Apr 2026): cross-monitor section injected outside `</main>` on 5/6 dashboards — "Loading…" never resolved
- FE-022 (2 Apr 2026): render call injected after `.catch` block — function defined but never called with live data
- FE-023 (2 Apr 2026): sidebar nav link omitted on new sections — section unreachable from nav

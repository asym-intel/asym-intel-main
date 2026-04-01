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

*This document is the single source of truth for build and deployment architecture.
Update it when the pipeline changes. Commit directly to main.*
*Maintainer: Computer*

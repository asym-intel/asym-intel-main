# Asymmetric Intelligence — Working Agreement (COMPUTER.md)
## Version 3.10 — 7 April 2026
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

Before any other action, fetch and read all three files:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d

gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md \
  --jq '.content' | base64 -d

gh api /repos/asym-intel/asym-intel-main/contents/docs/ROADMAP.md \
  --jq '.content' | base64 -d

# Pipeline specs — canonical source for ALL prompt requirements
# Read before ANY work on analyst crons, synthesisers, or collector scripts
gh api /repos/asym-intel/asym-intel-main/contents/docs/pipeline/ANALYST-CRON-SPEC.md \
  --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/docs/pipeline/SYNTHESISER-SPEC.md \
  --jq '.content' | base64 -d
```

**ROADMAP.md** is the single source of truth for all planned work — sprints, pipeline,
schema items, parking lot. Read it to understand what is queued, what is schema-gated,
and what needs a design session before building. Update it at every wrap when items
are completed or added.

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

## Deployment Rules — Tiered by Risk (updated 5 Apr 2026)

Now that the site architecture is stable and the CI validator catches structural
regressions, most monitor HTML changes go direct to main. Staging is reserved
for changes that modify existing rendered behaviour or shared infrastructure.

### LOW RISK → main directly (validator sufficient)
| Change type | Example |
|---|---|
| New additive JS-AUTO section | Adding a new `<section>` + render function that reads existing JSON |
| New sidebar nav link | Adding `<li><a href="#section-new">` to sidebar |
| New render function (additive) | `renderTrajectoryGrid()` — doesn't replace anything |
| Hugo layouts/main.css | Hugo rebuilds on push, validator catches regressions |
| JSON data files (cron output) | Autonomous — no approval |
| Hugo brief markdown | Autonomous — no approval |
| COMPUTER.md / HANDOFF.md / docs | Documentation — no approval |
| Pipeline scripts (synthesisers, collectors) | Infrastructure — no approval |

### MEDIUM RISK → staging, Computer screenshots, then merge (no Peter sign-off needed)
| Change type | Example |
|---|---|
| Replacing an existing section | Swapping F-Flag tile board for indicator matrix |
| Modifying an existing render function | Changing how `renderConflictCards()` displays data |
| Per-monitor CSS changes | `monitor.css` accent changes |

### HIGH RISK → staging, Peter visual sign-off required
| Change type | Example |
|---|---|
| Shared CSS (`base.css`) changes | Layout, typography, spacing changes hitting all 7 monitors |
| `nav.js` structural changes | Navigation rewrite, hamburger logic, scroll-spy |
| Network bar changes | Brand, links, mobile behaviour |
| Shared library files | `renderer.js`, `charts.js`, `theme.js` |

**Rule of thumb:** if the change is additive (new section, new function) and reads
existing JSON fields, it is LOW risk. If it replaces or modifies existing rendered
output, it is MEDIUM. If it touches shared infrastructure used by all 7 monitors,
it is HIGH.

For LOW risk: commit to main (static/ + docs/ mirror), take a screenshot to verify,
log to notes-for-computer.md. No staging round-trip needed.

For MEDIUM risk: push to staging, Computer takes a screenshot to verify, then
immediately opens PR and merges. No need to wait for Peter unless something
looks wrong.

For HIGH risk: push to staging, screenshot, share with Peter, wait for sign-off.

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

| Monitor | Cron ID | Schedule | Prompt |
|---|---|---|---|
| WDM | adad85f6 | Mon 06:00 UTC | docs/crons/wdm-slimmed-analyst-cron.md |
| GMM | 6efe51b0 | Tue 08:00 UTC | asym-intel-internal/gmm-prompts/gmm-slimmed-analyst-cron.md |
| ESA | 72398be9 | Wed 19:00 UTC | docs/crons/esa-slimmed-analyst-cron.md |
| FCW | 478f4080 | Thu 09:00 UTC | asym-intel-internal/fcw-slimmed-analyst-cron.md |
| AGM | b53d2f93 | Fri 09:00 UTC | docs/crons/agm-slimmed-analyst-cron.md |
| ERM | 0aaf2bd7 | Sat 05:00 UTC | docs/crons/erm-slimmed-analyst-cron.md |
| SCEM | 743bbe21 | Sun 18:00 UTC | docs/crons/scem-slimmed-analyst-cron.md |
| Housekeeping | c725855f | Mon 08:00 UTC | docs/crons/housekeeping.md |

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

## Platform-First Fix Rule

Before fixing any bug, gap, or prompt issue — always ask:

> "Is this specific to one monitor/file, or is it likely present across multiple monitors, workflows, scripts, or pages?"

If the answer is "likely platform-wide" or "I'm not sure":

1. **Audit first** — check all affected monitors/files before touching anything
2. **Fix the spec** — update `docs/pipeline/ANALYST-CRON-SPEC.md` or `SYNTHESISER-SPEC.md`
3. **Apply platform-wide** — fix all affected files in one pass

**Examples of platform-wide fixes (always audit before patching):**
- Workflow env variables (`GH_TOKEN`, `PPLX_API_KEY`)
- API call parameters (`search_recency_filter`, `return_citations`)
- Required JSON fields (`meta.pipeline_inputs`, `weekly_brief`)
- Publish guard checks
- Two-Pass Commit Rule compliance

**Examples of monitor-specific fixes (document why before fixing):**
- SCEM deviation calculation — only SCEM has indicator bands
- WDM living knowledge fields — only WDM has persistent.html sections
- AGM Ramparts publication — only AGM has Step 7

**The cost of reactive patching:** each gap found in one monitor that affects all 7 means 6 additional session tool calls, 6 additional commits, 6 opportunities for inconsistency. One properly scoped fix costs less than two reactive ones.

**Pipeline specs are the canonical source:** `docs/pipeline/ANALYST-CRON-SPEC.md` and `docs/pipeline/SYNTHESISER-SPEC.md` define what every prompt must contain. When a gap is found — fix the spec first, then make every monitor conform.

## API Offload Rule — Outsource Generation to Perplexity API

Before doing any generative work in a Computer session, ask:
> "Can this be generated by a sonar-pro API call instead?"

If yes — write a generation script, commit it to `tools/`, trigger via `workflow_dispatch`, and review the output in the next session. Computer credits are spent on judgement and refinement only, not generation.

### What to outsource via API (tools/ scripts → GA workflow_dispatch)

| Task | Model | Output |
|---|---|---|
| HTML/CSS component drafts (triage strip, badges, cards) | sonar-pro | `docs/generated/*.html` |
| Monitor Overview page templates | sonar-pro | `docs/generated/*.html` |
| Python script drafts (new pipeline scripts) | sonar-pro | `docs/generated/*.py` |
| Prompt drafts (new collector/analyst prompts) | sonar-pro | `docs/generated/*.md` |
| Copy variants (section headings, nav labels, value statements) | sonar-pro | `docs/generated/*.md` |

### What stays in Computer sessions

| Task | Why |
|---|---|
| Visual review and variant selection | Requires judgement against spec |
| Promoting drafts to production (base.css, shared library) | Requires architecture knowledge |
| Debugging and fixing broken output | Requires repo context |
| Pipeline data work (cron runs, JSON commits) | Requires auth and repo writes |
| Governance doc updates | Requires session context |

### Batching rule

When generating multiple components, batch into one API call — not one call per component.
A single sonar-pro call with 5 components costs roughly the same as a call with 1 component.
Always request 2-3 variants per component — iteration is free at generation time, expensive at review time.

### How to trigger

Generation scripts live in `tools/`. Workflows in `.github/workflows/` expose them via `workflow_dispatch`.
Computer triggers via:
```bash
gh api /repos/asym-intel/asym-intel-main/actions/workflows/{workflow}.yml/dispatches \
  --method POST --field ref=main
```
Then poll for completion and check `docs/generated/` for output.

### Session length rule

Long-running sessions have inflated per-call costs due to context accumulation.
If a session has been running >3 hours or has >50 tool calls: wrap and start fresh.
The Step 0 overhead of a new session is always cheaper than the inflated cost of a long context.

## Credit-Saving Workflows

Four decision rules. Apply before starting any task.

| Trigger | Correct action |
|---|---|
| New idea, visual, workflow, methodology, or prompt draft | **Peter creates externally first.** Bring the file back to Computer for implementation only. Computer's job is execution, not ideation. Examples: visual mockups in external AI tools, prompt drafts in a text editor, methodology docs written offline, UX review outputs. Do not ask Computer to design something it will then immediately build — that doubles the cost. |
| Multi-file sprint (3+ files changing) | **Spec first, implement second.** Computer produces a spec doc listing every file that will change, every schema field being added, and what the rendered output will look like. Peter reviews and approves before any commit. Catches missing files, wrong paths, and schema gaps before subagents run. |
| A page section shows a placeholder ("Build 2", "schema-gated", "coming soon") | **Classify before acting.** Schema-gated = cron prompt fix, no HTML needed, do it now. Design-gated = needs a PED or methodology decision first, park it. Confusing these wastes credits on implementation work that then has to be redone after the design decision. Check ROADMAP.md — if it's in the parking lot, it's design-gated. |
| A visual element appears on 2+ monitor pages | **Fix in shared library, not per page.** CSS changes go to `static/monitors/shared/css/base.css` (all 7 monitors) or per-monitor `assets/monitor.css` (≤40 lines, accent tokens only). JS changes go to `static/monitors/shared/js/`. Never fix the same thing 7 times. If a fix is right for one monitor it is almost certainly right for all — check base.css first. |

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
14. **Cancelled subagent treated as done** — a subagent that errors, cancels, or
    returns "something went wrong" has NOT completed its work. Always verify outputs
    exist (check repo, check workspace files) before marking a task complete. Surface
    at wrap as an incomplete item.
15. **Platform IDs in public files** — Zone IDs, account IDs, GSC tokens belong in
    `asym-intel-internal/platform-config.md`. Never paste them into COMPUTER.md,
    HANDOFF.md, or any file in the public repo.
15. **COMPUTER.md wiped** — never use Python `open(path, 'w')` without reading the file first; use `read()` → modify → `write()`
16. **New governance file not wired into Step 0** — any new persistent reference file created in a session (ROADMAP.md, new methodology doc, new spec) must be added to Step 0 in COMPUTER.md, the asym-intel skill, and noted in notes-for-computer.md. If only one place is updated, other sessions won't find it. Canonical test (from `docs/prompts/platform-developer.md`): "Could a fresh Computer instance reading only the Step 0 files find this file without being told it exists?"
17. **Staging reset while files await sign-off** — NEVER reset staging to main when staged files are awaiting Peter's visual review. This has destroyed staged work at least three times. At wrap: if staging is ahead and unreviewed, leave it in place and record the state in HANDOFF.md. See STAGING RESET PROTECTION rule.

## Three-Layer Intelligence Architecture (v2.3)

Canonical strategy document (read before building any Collector or Analyst):
  gh api /repos/asym-intel/asym-intel-main/contents/docs/COLLECTOR-ANALYST-ARCHITECTURE.md \
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

**CRON RECREATION RULE — CONFIRM BEFORE EXECUTING:**
Never recreate crons autonomously in response to a hypothetical, question, or perceived gap.
If a user asks "what would you do if X cron was missing?" — answer the question, do not execute.
If crons appear missing from `schedule_cron list`, DO NOT conclude a "wipe" has occurred.
Crons created in a previous session are invisible to a new session — this is normal, not an emergency.
Cross-check COMPUTER.md cron table against `schedule_cron list`. Report the discrepancy and ask:
"These cron IDs are in COMPUTER.md but not visible in this session — shall I recreate them?"
Never log a "cron wipe" to notes-for-computer.md without first verifying with the user.

**MERGE RULE — VERIFY STAGING BEFORE ACCEPTING APPROVAL:**
When a user says "staging looks good" or "approved" or similar, DO NOT accept this at face value
in a fresh session that has not yet inspected staging.
Always fetch the staged file list first:
  gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '[.files[].filename]'
Show the user exactly what will be merged and ask: "This will apply these N files to main — confirm?"
Never merge based on approval given before the file list has been shown in the current session.

**STAGING RESET PROTECTION — NEVER reset staging while files await visual sign-off:**
If staging is ahead of main and contains files awaiting Peter's visual review:
  1. Do NOT reset staging to main — this destroys the staged work.
  2. At wrap: list the staged files, note "awaiting Peter sign-off — DO NOT RESET".
  3. Write this state into HANDOFF.md so the next session knows.
  4. Only reset staging AFTER a successful merge OR after Peter explicitly abandons the staged work.
Violating this rule has caused staged work to be silently destroyed at least three times.
The wrap procedure Step 5 exception ("incomplete or visually unreviewed") means LEAVE IN PLACE, not RESET.

**AFTER EVERY DIRECT-FILE MERGE — reset staging to main:**
When files are applied directly to main (not via PR merge), staging retains its old commit history
and will appear "ahead" with identical content. Always reset staging after a direct-file merge:
  MAIN_SHA=$(gh api /repos/asym-intel/asym-intel-main/git/refs/heads/main --jq '.object.sha')
  gh api /repos/asym-intel/asym-intel-main/git/refs/heads/staging -X PATCH -f sha="$MAIN_SHA" -F force=true
Verify with: gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '{ahead_by:.ahead_by,behind_by:.behind_by}'
Expected result: {ahead_by: 0, behind_by: 0}

**Cron prompt registry:** `docs/crons/` — all cron logic lives here, not in the task.
Cron tasks are slim pointers: `gh api .../docs/crons/{file}.md --jq '.content' | base64 -d`
To update a cron: edit the .md file in docs/crons/ and commit. No cron task edit needed.
To recreate a lost cron: see `docs/crons/README.md` for the pattern.

| Layer | Name | Cron ID | Schedule |
|---|---|---|---|
| Analyst (slim) | WDM Analyst | adad85f6 | Mon 06:00 UTC |
| Analyst (slim) | GMM Analyst | 6efe51b0 | Tue 08:00 UTC |
| Analyst (slim) | ESA Analyst | 72398be9 | Wed 19:00 UTC |
| Analyst (slim) | FCW Analyst | 478f4080 | Thu 09:00 UTC |
| Analyst (slim) | AGM Analyst | b53d2f93 | Fri 09:00 UTC |
| Analyst (slim) | ERM Analyst | 0aaf2bd7 | Sat 05:00 UTC |
| Analyst (slim) | SCEM Analyst | 743bbe21 | Sun 18:00 UTC |
| Housekeeping | Platform Housekeeping | c725855f | Mon 08:00 UTC |

**DELETED CRONS (3 April 2026 — do not recreate):**
- Staging divergence guard (aec126c5) — deleted. Wrap procedure catches unmerged staging. Daily runs wasted credits.
- GSC quarterly audit (f78e0c2c) — deleted. GSC property not yet verified; audit was running against unverified property. Recreate after GSC DNS TXT record confirmed.

## Active GitHub Actions (external pipeline — NOT Computer crons)

**All collectors run daily. Weekly-research and Reasoner fire in sequence before Synthesiser.**
Schedules are live in the workflow files — this table is the canonical record.

### Chatter (daily — one monitor per day, rotating)
| Monitor | Workflow | Schedule | Model |
|---|---|---|---|
| FCW | fcw-chatter.yml | Mon 06:00 UTC | sonar |
| GMM | gmm-chatter.yml | Tue 06:00 UTC | sonar |
| WDM | wdm-chatter.yml | Wed 06:00 UTC | sonar |
| SCEM | scem-chatter.yml | Thu 06:00 UTC | sonar |
| ESA | esa-chatter.yml | Fri 06:00 UTC | sonar |
| AGM | agm-chatter.yml | Sat 06:00 UTC | sonar |
| ERM | erm-chatter.yml | Sun 06:00 UTC | sonar |

### Collector (daily — all monitors, 07:00 UTC)
| Monitor | Workflow | Schedule | Model |
|---|---|---|---|
| FCW | fcw-collector.yml | Daily 07:00 UTC | sonar |
| GMM | gmm-collector.yml | Daily 07:00 UTC | sonar |
| WDM | wdm-collector.yml | Daily 07:00 UTC | sonar |
| SCEM | scem-collector.yml | Daily 07:00 UTC | sonar |
| ESA | esa-collector.yml | Daily 07:00 UTC | sonar |
| AGM | agm-collector.yml | Daily 07:00 UTC | sonar |
| ERM | erm-collector.yml | Daily 07:00 UTC | sonar |

### Weekly Research → Reasoner → Synthesiser (per-monitor cascade)
| Monitor | Weekly Research | Reasoner | Synthesiser | Model chain |
|---|---|---|---|---|
| FCW | Wed 18:00 UTC | Wed 20:00 UTC | Wed 22:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| GMM | Mon 16:00 UTC | Mon 18:00 UTC | Mon 20:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| WDM | Sun 18:00 UTC | Sun 20:00 UTC | Sun 21:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| SCEM | Sat 06:00 UTC | Sat 08:00 UTC | Sat 10:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| ESA | Tue 18:00 UTC | Tue 20:00 UTC | Wed 09:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| AGM | Thu 18:00 UTC | Thu 20:00 UTC | Thu 22:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |
| ERM | Fri 16:00 UTC | Fri 18:00 UTC | Fri 20:00 UTC | sonar-pro → sonar-deep-research → sonar-deep-research |

**IP-protected prompts (asym-intel-internal):**
GMM: all prompts in `asym-intel-internal/gmm-prompts/` (commercial IP — Leverage Signal).
FCW: analyst cron at `asym-intel-internal/fcw-slimmed-analyst-cron.md` (FIMI methodology sensitivity).
Scripts for GMM and FCW must fetch prompts via `gh api` from internal, not local filesystem.
All other monitors (WDM/ESA/AGM/ERM/SCEM): prompts public in `docs/crons/` and `pipeline/monitors/{slug}/`.

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
0. **Incomplete work check (ALWAYS FIRST)** — before summarising, audit the current session
   for any work that was started but not completed:
   - Any subagents that were cancelled, errored, or returned partial results?
   - Any todo list items still marked in_progress or pending?
   - Any staged files that were pushed but the PR was never opened?
   - Any files committed to a draft location that needed a follow-up step?
   Surface every incomplete item explicitly. Do not proceed to step 1 until Peter
   has confirmed: complete it now, defer to next session, or explicitly abandon it.
   **Never silently drop incomplete work.** A cancelled subagent is not the same as
   completed work — treat it as a gap until explicitly resolved.
1. Summarises what changed this session (commits, decisions, new patterns)
2. Logs significant items to notes-for-computer.md
3. Updates HANDOFF.md with current session state
4. Checks: any unmerged staging changes? any new crons missing from COMPUTER.md? any new governance files missing from Step 0?
5. **Open staging check** — if staging is ahead of main, list the staged files and ask:
   "Staging has N files ready. Do you want to merge before closing?"
   If yes: open PR staging → main and merge immediately.
   If no (Peter defers): **leave staging untouched** and record in HANDOFF.md:
   "Staging: N files awaiting sign-off — DO NOT RESET". List the filenames.
   NEVER reset staging when files await visual sign-off. See STAGING RESET PROTECTION rule above.
6. **Reset staging to main HEAD** — ONLY after a successful merge, or after Peter explicitly
   abandons staged work. Never reset as a cleanup step while files await review.
7. **Update next-session.md** — this is ALWAYS the final commit of the session.
   Write it AFTER merge and staging reset — not before. The file must reflect the
   true final state of the repo. If next-session.md was written earlier in the session
   and anything changed after (merge, new commit, staging reset), it is stale and must
   be rewritten now.
   Overwrite `docs/prompts/next-session.md` with the highest-priority prompt for the
   next session. Do NOT recite it back to Peter. Do NOT paste it into the conversation.
   Write it to the file and confirm done with one line:
   "next-session.md updated — start next session with: Computer: asym-intel.info"
8. Confirms all done before ending

### New governance files — mandatory wiring rule
When any new persistent reference file is created (e.g. ROADMAP.md, a new methodology doc,
a new architecture spec) that every future session should read:

1. Add a fetch command to **Step 0** in this file (COMPUTER.md)
2. Add the same fetch command to **Step 0** in the **asym-intel skill** (save_custom_skill)
3. Add a note to **notes-for-computer.md** explaining what the file is and why it matters

If you skip any of these three, the next session will not know the file exists.
Canonical test (from `docs/prompts/platform-developer.md`): "Could a fresh Computer instance reading only the Step 0 files find this file without being told it exists?" If not — wire it.

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


## Subagent Usage — Known Limits and Patterns

### Why subagents get cancelled

Two distinct failure modes observed in practice (3 April 2026):

**1. Step-count exhaustion** — a subagent that must do many sequential things
(browse 5 live pages + read 7 files + write 2 large docs + update 3 governance files)
will approach or exceed the 200-step limit. Signs: subagent is on the right track
but never returns. Fix: **split the task**. Observation pass first (read + browse),
write pass second (commit docs from findings).

**2. Session-level timeout** — after ~90 minutes of intensive work in one session,
launching additional subagents increases cancellation risk. Signs: subagent cancelled
immediately with no partial output. Outputs may still exist in repo if the subagent
completed just before the cancellation signal. Always verify repo state after any
cancellation — do not assume nothing happened.

### Subagent sizing rules

| Task complexity | Approach |
|---|---|
| Single file change, <5 tool calls | Do it directly (no subagent) |
| Multi-file change, same domain, <15 tool calls | Single subagent |
| Observe 5+ live pages AND write docs | Two subagents: observe → write |
| 3+ parallel subagents after 90min session | Defer to next session instead |

### After a cancellation — always verify

```bash
# Check if subagent outputs exist despite cancellation
gh api /repos/asym-intel/asym-intel-main/commits?per_page=5 --jq '[.[] | {sha:.sha[:8], msg:.commit.message[:80]}]'
ls /home/user/workspace/*.md 2>/dev/null
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '.ahead_by'
```

A cancelled subagent ≠ no work done. Verify before re-running — you may be about
to duplicate work that already succeeded.

### Session length awareness

When a session has been running for >90 minutes, note it in wrap:
"Session is >90min — recommend deferring remaining subagent work to a fresh session."
Do not launch complex multi-step subagents as the last act of a long session.

### Minimum session size rule (efficiency)

Do not open a Computer session for fewer than 3 queued tasks. The Step 0 loading
cost (6 API calls to read governance files) is fixed overhead paid on every session
regardless of how much work gets done. Amortise it over more work per session.

Good session: 3–6 tasks batched, run in sequence, closed with wrap.
Waste session: open session → check one thing → close. Use the Housekeeping
notification system instead — silence means all-OK.

Housekeeping cron sends a notification on any WARN or FAIL. Absence of notification
means the platform is healthy. Do not open a session to verify health — trust the silence.


## ARCHITECTURE.md (MANDATORY for HTML/CSS/JS work)

Read before any build work:
  gh api /repos/asym-intel/asym-intel-main/contents/docs/ARCHITECTURE.md --jq '.content' | base64 -d

Update it when new patterns or fixes are discovered. Never end a build session without checking if ARCHITECTURE.md should be updated.

## Efficiency Configuration
**Target: ≤6,000 Computer credits/week normal · ≤$25 PPLX API/month**

Chatter workflows rotate one monitor per day (not all daily) to reduce API cost.
Collectors are daily for all 7 monitors (required for pipeline freshness).
Weekly research and Reasoner fire once per week per monitor (see GA table above).
Computer Analyst crons: 7 monitors × ~100 credits/run = ~700 credits/week.

### Session Gate — read before opening any Computer session

**Before opening a session, answer these three questions:**

1. **Is there a housekeeping notification?** No notification = platform healthy = no session needed.
   Trust the silence. Do not open a diagnostic session to verify health.

2. **Is the work urgent or can it batch?** Rendering work, schema additions, and prompt
   improvements can wait for the next scheduled session. Only pipeline failures, live bugs,
   and missed publishes justify an unscheduled session.

3. **Can this be done in one session?** If yes, do it all in one session. Never open a
   second session the same day unless the first session produced an incident requiring
   immediate follow-up.

**Target:** ≤2 Computer sessions per week. One Monday session (if housekeeping flags issues),
one mid-week sprint session. Infrastructure rebuilds (like pipeline builds, governance rewrites)
are quarterly events — not weekly.

### Subagent Rule — sequential first

**Default: sequential.** Run subagents one at a time unless tasks are genuinely independent
AND time is the binding constraint (e.g. a publish deadline).

Parallel subagents are 3× faster but 3× the credit cost. For most work — schema additions,
prompt updates, rendering fixes — sequential is identical in outcome at 1/3 the cost.

| Scenario | Approach |
|---|---|
| 3 independent file builds, no deadline | Sequential — one subagent, then next |
| 3 independent file builds, publish in 1hr | Parallel — time is binding |
| Research + write (dependent) | Sequential — always (second depends on first) |
| Diagnostic + fix (dependent) | Sequential — always |

**Manual publish fallback:** if a publish is missed, give the subagent the synthesiser
output directly rather than asking it to do its own research. Full synthesis is 3–5× more
expensive than methodology-only publication.


## Efficiency Configuration (2026-04-03)
**Target: ≤6,000 Computer credits/month, ≤$25 API/month**

### GitHub Actions pipeline schedules
| Workflow | New schedule | Old schedule |
|---|---|---|
| FCW chatter | Mon 06:00 UTC | daily |
| GMM chatter | Tue 06:00 UTC | daily |
| WDM chatter | Wed 06:00 UTC | daily |
| SCEM chatter | Thu 06:00 UTC | daily |
| ESA chatter | Fri 06:00 UTC | daily |
| AGM chatter | Sat 06:00 UTC | daily |
| ERM chatter | Sun 06:00 UTC | daily |
| FCW collector | Mon 07:00 UTC | daily |
| GMM collector | Tue 07:00 UTC | daily |
| WDM collector | Wed 07:00 UTC | daily |
| SCEM collector | Thu 07:00 UTC | daily |
| ESA collector | Fri 07:00 UTC | daily |
| AGM collector | Sat 07:00 UTC | daily |
| ERM collector | Sun 07:00 UTC | daily |
| Test workflows | DISABLED | scheduled |

**Pattern: 1 monitor/day rotating. Chatter at 06:00, Collector at 07:00 same day.**
Total GitHub Actions API calls: 14/week (was 42/week). Saves ~$1.20/month.

### Analyst cron cadence
All 7 monitors remain weekly. Under the synthesiser architecture the Analyst
cron is lightweight (~100 credits/run) so weekly is affordable for all.
Quarterly cadence idea superseded — see COLLECTOR-ANALYST-ARCHITECTURE.md v2.1.
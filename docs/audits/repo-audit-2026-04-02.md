# Repository File Audit — 2 April 2026
**Scope:** asym-intel-main (public) + asym-intel-internal (private)  
**Conducted:** 2026-04-02 ~23:15 CEST (role enhancement addenda session)  
**Auditor:** Computer  
**Method:** Full recursive git tree walk + targeted content inspection  

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 2 | Queued for Platform Developer session |
| HIGH | 2 | Queued for resolution |
| MEDIUM | 3 | Verify and act |
| LOW | 2 | Minor housekeeping |
| EXPECTED-DUPLICATE / KEEP | 11 | Confirmed clean — no action |

---

## CRITICAL Findings

### C-001 — FCW dashboard.html: static/ vs docs/ architecture divergence

**File:** `static/monitors/fimi-cognitive-warfare/dashboard.html` (139,939 bytes)  
**vs:** `docs/monitors/fimi-cognitive-warfare/dashboard.html` (37,521 bytes)

**Finding:** The `static/` version is a legacy pre-shared-library monolithic file:
- Embedded CSS (~100+ lines of `:root` variables and component styles)
- No reference to `../shared/css/base.css`, `theme.js`, or `nav.js`
- Per-actor static sections: Russia, China, Iran, Gulf States, United States, Israel
- Its own sidebar nav implementation (not the Blueprint v2.1 shared library nav)
- No `section-kpi`, `section-actor-matrix`, `section-signal`, `section-cross-monitor` IDs

The `docs/` version is the correct modern Blueprint v2.1 shared-library file:
- Links `../shared/css/base.css` and `assets/monitor.css`
- Loads `theme.js` and `nav.js` from shared library in `<head>`
- All 8 standard sections present with correct IDs
- Cross-monitor flags widget (Sprint 3B) present

**Root cause:** The shared-library migration was applied to `docs/` but never to `static/`. The maintenance cron (commit d17790b0, 2 April 2026) continued writing into the legacy `static/` version, further diverging it (+2,326 / −820 lines). Because Hugo copies `static/` → `docs/` on every build, the next push to `main` after d17790b0 would overwrite the modern `docs/` version with the 139k legacy file, reverting all Sprint 3 work on FCW.

**Risk:** HIGH — next Hugo build would silently revert FCW dashboard to legacy architecture.

**Action required:** Platform Developer to replace `static/dashboard.html` with the modern shared-library version (currently in `docs/`). Staging → PR → visual sign-off → merge.

**Resolution (same session):** PR #28 opened. `static/` replaced with modern version on staging branch. Awaiting visual sign-off.

---

### C-002 — FCW-DAILY-FEEDER-PROMPT-v4.md missing

**File referenced:** `asym-intel-internal/prompts/FCW-DAILY-FEEDER-PROMPT-v4.md`  
**Referenced by:** `static/monitors/fimi-cognitive-warfare/fcw-daily-feeder-cron.md` and `docs/monitors/fimi-cognitive-warfare/fcw-daily-feeder-cron.md`  
**Actual contents of `asym-intel-internal/prompts/`:** `FCW-COLLECTOR-PROMPT-v1.md` + `README.md`

**Finding:** Both stub files contain:
```
# The canonical prompt (v4.0) is at:
#   asym-intel-internal/prompts/FCW-DAILY-FEEDER-PROMPT-v4.md
```
This file does not exist and was never created.

**Root cause:** The "daily feeder" cron concept predates the GitHub Actions Collector architecture. During the March/April 2026 migration:
- The FCW Collector moved from a Computer cron to GitHub Actions (`fcw-collector.yml`, daily 07:00 UTC)
- The prompt was renamed from `FCW-DAILY-FEEDER-PROMPT` to `FCW-COLLECTOR-PROMPT-v1.md`
- The stub files were never updated to reflect the new architecture and filename

**Is any active cron broken?** No. COMPUTER.md lists no Computer cron for FCW daily collection — only the FCW Analyst (cron b17522c3, Thu 09:00 UTC). The daily Collector runs in GitHub Actions (`fcw-collector.yml`), which calls `pipeline/monitors/fimi-cognitive-warfare/collect.py` directly and does not reference the stub files.

**Risk:** MEDIUM operational, HIGH documentation — any future session reading the stub to understand FCW architecture would be misled and might attempt to recreate a now-obsolete Computer cron, duplicating the GitHub Actions workflow.

**Resolution (same session):** Both stub files updated to reflect current architecture:
- GA workflow: `.github/workflows/fcw-collector.yml` (daily 07:00 UTC)
- Correct prompt: `asym-intel-internal/prompts/FCW-COLLECTOR-PROMPT-v1.md`
- History note: `FCW-DAILY-FEEDER-PROMPT-v4.md` is obsolete — do not create
- Committed to both `static/` and `docs/` on main (commits fc489ff2, d08a69fb, then corrected to 00835ff2)

---

## HIGH Findings

### H-001 — docs/monitors/_shared/ stale build artefact

**Path:** `docs/monitors/_shared/css/base.css` (34,798 bytes) + `docs/monitors/_shared/js/` (charts.js, nav.js, renderer.js, theme.js)

**Finding:** A second shared-library directory exists at `docs/monitors/_shared/` alongside the current `docs/monitors/shared/` (without underscore). The `_shared/` path appears to be an older build artefact from when the directory was named with a leading underscore. No current monitor HTML file references `_shared/` — all dashboards reference `../shared/`.

**No corresponding `static/monitors/_shared/` exists** — confirming this is a `docs/`-only artefact never regenerated from source.

**Risk:** LOW operational (nothing serves from it), MEDIUM confusion (a future session inspecting `docs/monitors/` might treat it as canonical).

**Action required:** Verify no workflow or build step references `_shared/`, then delete the directory from `docs/`. (Note: direct deletion of `docs/` files is safe — Hugo overwrites `docs/` on next build anyway; `_shared/` would not be regenerated as it has no `static/` source.)

---

### H-002 — housekeeping-cron-prompt.md: docs/ only, no static/ counterpart

**File:** `docs/monitors/housekeeping-cron-prompt.md` (21,026 bytes)  
**Status:** Present in `docs/monitors/` but absent from `static/monitors/`

**Finding:** The housekeeping cron prompt file exists only in the `docs/` output tree, not in `static/`. This appears to be a legacy location from before `docs/crons/` was created. `docs/crons/housekeeping.md` (21,026 bytes) contains identical content and is the authoritative location now referenced by the cron registry.

**Is a cron broken?** No. The Housekeeping cron (7e058f57) reads from `docs/crons/housekeeping.md` via the slim pointer pattern. `docs/monitors/housekeeping-cron-prompt.md` is orphaned.

**Action required:** Assess whether to:
1. Delete `docs/monitors/housekeeping-cron-prompt.md` (it's a `docs/` file so Hugo won't regenerate it — safe to delete directly), or
2. Leave it as a harmless duplicate

No `static/monitors/housekeeping-cron-prompt.md` should be created — this file type belongs in `docs/crons/`, not in monitor directories.

---

## MEDIUM Findings

### M-001 — eghtm-full.md: stale filename in methodology/

**File:** `asym-intel-internal/methodology/eghtm-full.md` (19,758 bytes)  
**Alongside:** `asym-intel-internal/methodology/european-strategic-autonomy-full.md` (20,495 bytes)

**Finding:** `eghtm-full.md` uses the pre-rename acronym (EGHTM = European Geopolitical and Hard Power Tracker Monitor, superseded by ESA = European Strategic Autonomy). The ESA rename was completed across 21 files in asym-intel-main on 2 April 2026 but the internal methodology file was not renamed.

**Action required:** Rename `eghtm-full.md` → `eghtm-full-ARCHIVED-2026-04-02.md` (or delete after confirming `european-strategic-autonomy-full.md` is complete and current). The FCW Analyst cron reads `methodology/fimi-cognitive-warfare-full.md` — verify ESA Analyst reads `european-strategic-autonomy-full.md` not `eghtm-full.md`.

---

### M-002 — conflict-escalation-tasks-prompt.md: possibly superseded

**File:** `asym-intel-internal/methodology/conflict-escalation-tasks-prompt.md` (14,936 bytes)  
**Alongside:** `static/monitors/conflict-escalation/scem-cron-prompt.md` (48,322 bytes — 3× larger)

**Finding:** `conflict-escalation-tasks-prompt.md` appears to be an earlier version of the SCEM cron prompt, predating the current `scem-cron-prompt.md`. It is located in `methodology/` (internal) rather than `static/monitors/conflict-escalation/` (operational).

**Action required:** Compare content with `scem-cron-prompt.md`. If fully superseded, archive or delete. If it contains supplementary methodology content not in the main prompt, assess whether to merge.

---

### M-003 — democratic-integrity-full.md: possible workspace path contamination

**File:** `asym-intel-internal/methodology/democratic-integrity-full.md` (21,438 bytes)  
**Also present:** `asym-intel-internal/methodology/wdm-full.md` (25,000 bytes)

**Finding:** Two files cover the WDM methodology. `democratic-integrity-full.md` may be a session-generated draft containing workspace-local file paths (e.g., `/home/user/workspace/...`) embedded in content — a known pattern from early methodology sessions before the canonical file location was established.

**Action required:** Content-inspect both files. If `democratic-integrity-full.md` contains workspace paths, clean or delete. Confirm the ESA Analyst (and any other consumers) reads the correct file.

---

## LOW Findings

### L-001 — scem-daily-test.py in pipeline output directory

**File:** `pipeline/monitors/conflict-escalation/daily/scem-daily-test.py` (4,222 bytes)  
**Also:** `pipeline/monitors/conflict-escalation/daily/daily-test-2026-04-02.json` (3,651 bytes)  
**Also:** `.github/workflows/scem-daily-test.yml` (885 bytes)

**Finding:** A test script and its JSON output are in the live pipeline output directory. `scem-daily-test.py` is a development/testing artefact that should not coexist with production Collector output (`daily-latest.json`, `verified-YYYY-MM-DD.json`). The `.github/workflows/scem-daily-test.yml` workflow also exists — assess whether it is still needed or should be removed now that SCEM Collector is in production.

**Action required:** Move `scem-daily-test.py` out of `daily/` (e.g., to `pipeline/monitors/conflict-escalation/dev/`). Assess whether `scem-daily-test.yml` should be deleted or converted to a proper test workflow.

---

### L-002 — README.md is a 69-byte stub

**File:** `asym-intel-main/README.md` (69 bytes)

**Finding:** The root README is a minimal stub. External visitors to the GitHub repo (journalists, researchers, collaborators) see no context. The site, its purpose, and key documentation links are invisible.

**Action required:** Expand to at minimum: one-paragraph mission statement, link to asym-intel.info, link to `docs/ARCHITECTURE.md` for contributors, link to `COMPUTER.md` for AI sessions. Low priority — no operational impact.

---

## EXPECTED-DUPLICATE / KEEP Items (confirmed clean — no action)

The following files were inspected and confirmed as intentional duplicates, expected pairs, or correctly structured:

| File | Status | Reason |
|------|--------|--------|
| `docs/crons/housekeeping.md` vs `docs/monitors/housekeeping-cron-prompt.md` | Duplicate | Same content — `docs/crons/` is canonical; `docs/monitors/` version is legacy orphan (see H-002) |
| `methodology/fimi-full.md` vs `methodology/fimi-cognitive-warfare-full.md` | Possibly duplicate | Both present; FCW cron reads `fimi-cognitive-warfare-full.md`. Inspect `fimi-full.md` for supersession. |
| `methodology/conflict-escalation-acled-2026.md` | Supplementary | Source-specific methodology annex — not a duplicate of `conflict-escalation-full.md` |
| `methodology/democratic-integrity-vdem-2026.md` | Supplementary | Source-specific methodology annex — intentional |
| All other `*-2026.md` source annex files | Keep | Source-specific methodology annexes per monitor |
| `docs/monitors/shared/` vs `docs/monitors/_shared/` | Two paths, only one is active | `_shared/` is stale artefact (see H-001) |
| `static/monitors/shared/` contents (anti-patterns.json, site-decisions.json, etc.) | Keep | Shared platform governance files — not HTML, correctly located in `static/` |
| `pipeline/monitors/*/daily/README.md` stub files | Keep | Pipeline directory markers — intentional |
| `pipeline/monitors/*/daily/daily-latest.json` stub files | Keep | Collector output placeholders — intentional |
| All `docs/crons/*.md` slim pointer files | Keep | Canonical cron prompt registry — correct location |
| All per-monitor `*-cron-prompt.md` in `static/monitors/` | Keep | Layer 2 Analyst prompts — correct location |

---

## Files Confirmed Present and Correct

All 7 monitor directories in `static/monitors/` contain the expected 8+ HTML pages (overview, dashboard, report, archive, persistent, about, search, methodology — plus monitor-specific additions).

All 7 `data/report-latest.json` files present (sizes not individually checked in this audit — deferred to Housekeeping validator).

GitHub Actions workflows (12 active): fcw-collector.yml, fcw-weekly-research.yml, fcw-reasoner.yml, gmm-collector.yml, gmm-weekly-research.yml, gmm-reasoner.yml, scem-collector.yml, scem-weekly-research.yml, scem-reasoner.yml, wdm-collector.yml, wdm-weekly-research.yml, wdm-reasoner.yml. All confirmed present.

---

## Resolutions Applied This Session

| Finding | Action | Commits |
|---------|--------|---------|
| C-001 FCW dashboard divergence | staging branch updated, PR #28 opened | a02c6e44 (staging) |
| C-002 FCW feeder stub | Both `static/` and `docs/` stubs corrected | fc489ff2, d08a69fb → 00835ff2 |
| H-001 `_shared/` artefact | Documented — deferred to future session | — |
| H-002 housekeeping-cron-prompt.md | Documented — deferred | — |
| M-001 eghtm-full.md | Documented — deferred | — |
| M-002 conflict-escalation-tasks-prompt.md | Documented — deferred | — |
| M-003 democratic-integrity-full.md | Documented — deferred | — |
| L-001 scem-daily-test.py | Documented — deferred | — |
| L-002 README.md stub | Documented — deferred | — |

---

*Audit conducted by Computer. Next audit: Platform Auditor role (see `docs/prompts/platform-auditor.md`).*

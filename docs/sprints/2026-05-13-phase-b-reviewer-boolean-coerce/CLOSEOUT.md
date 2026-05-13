# CLOSEOUT — Phase B Fleet-Unfreeze: Reviewer/Composer Boolean Coerce

**Sprint:** `docs/sprints/2026-05-13-phase-b-reviewer-boolean-coerce/`
**BRIEF:** `/tmp/fleet-2026-05-13-1547cest/briefs/BRIEF-D-reviewer-composer-boolean-coerce.md`
**Posture:** Executor (BRIEF-D)
**Merged via PR:** [#314](https://github.com/asym-intel/asym-intel-main/pull/314) `fix(workflows): coerce force boolean in 16 thin callers (Phase B fleet-unfreeze)`
**Merge SHA:** `4f6fe3e67396602d8be6468d0322251f12e13e91`
**Date:** 2026-05-13

---

## Description

This sprint cures **Defect A** of the Phase B fleet-freeze: a boolean contract rejection that silently failed all `workflow_run`-triggered reviewer and composer jobs across 8 monitors (agm, erm, esa, fcw, fim, gmm, scem, wdm) since commit `c38971f9` (2026-05-05).

### Root cause

Commit `c38971f9` added a `force` boolean input to 16 thin-caller workflows. The callers passed the input as:

```yaml
force: ${{ inputs.force }}
```

Under `workflow_run` triggers, `inputs` is undefined, so `${{ inputs.force }}` evaluates to `""` (empty string). GitHub Actions rejects the `workflow_call` invocation because `""` is not assignable to `type: boolean`. No job is spawned (`jobs.total_count: 0`).

**Smoking-gun evidence:** Run `25634402378` (scem-reviewer, 2026-05-10T16:54:19Z, `event=workflow_run`) returned `{"jobs":[],"total_count":0}` — contract rejection, no jobs materialised.

### Fix applied

Changed `force: ${{ inputs.force }}` to `force: ${{ inputs.force == true }}` in all 16 thin callers. The `==` operator coerces undefined/empty-string to boolean `false`, preserving `true` only when `inputs.force` is genuinely `true`.

**Files changed (16):**
- `agm-composer.yml`, `agm-reviewer.yml`
- `erm-composer.yml`, `erm-reviewer.yml`
- `esa-composer.yml`, `esa-reviewer.yml`
- `fcw-composer.yml`, `fcw-reviewer.yml`
- `fim-composer.yml`, `fim-reviewer.yml`
- `gmm-composer.yml`, `gmm-reviewer.yml`
- `scem-composer.yml`, `scem-reviewer.yml`
- `wdm-composer.yml`, `wdm-reviewer.yml`

Reusables (`_reusable-composer.yml`, `_reusable-reviewer.yml`) are correct and were not modified.

---

## Verification Table

| Test | Run ID | Trigger | Conclusion | jobs.total_count |
|------|--------|---------|------------|-----------------|
| `scem-reviewer.yml` via `workflow_dispatch` (force=false) | [25814455576](https://github.com/asym-intel/asym-intel-main/actions/runs/25814455576) | `workflow_dispatch` | **success** | **1** |
| `scem-reviewer.yml` via interpreter → `workflow_run` chain | [25814842625](https://github.com/asym-intel/asym-intel-main/actions/runs/25814842625) | `workflow_run` | **success** | **1** |
| `scem-reviewer.yml` via `workflow_dispatch` (force=true smoke) | [25814469325](https://github.com/asym-intel/asym-intel-main/actions/runs/25814469325) | `workflow_dispatch` | failure at commit step (git merge conflict — two same-day runs wrote review-2026-05-13.json concurrently; boolean contract itself succeeded, `jobs.total_count: 1`) | **1** |

**All three tests confirm `jobs.total_count: 1`** — no contract rejections. The failure in test 3 is a runtime git conflict from concurrent same-day writes, not a boolean coercion issue.

---

## Scope boundary

**In scope:** Defect A only — boolean contract rejection in 16 thin callers.
**Out of scope:**
- Defect B (CQ-6 `persistent_state_writeback_not_wired` re-flag) — BRIEF-E
- Defect C (visibility/pipeline-status proxy gates) — BRIEF-F
- Phase B fleet-freeze sprint (broader G2–G4 class-cure) — commons Architect per F-D4
- 8 `*-applier.yml` files: also contain `force: ${{ inputs.force }}` but are NOT broken (appliers use `workflow_dispatch` only, never `workflow_run`; the bug is specific to `workflow_run` context). Flagged for Fleet Architect as low-priority cleanup.

---

Per DEFECT-CLASS-RETRO Class E (closeout-in-merge-PR).

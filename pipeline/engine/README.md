# pipeline/engine/

Engine modules for the commons-monitor Publisher Bot. This directory is the
asym-intel-main landing zone for engine modules that run inside the public repo
(as distinct from `asym-intel-internal:pipeline/engine/`, which holds the
Interpreter, Reviewer, and Composer stage scripts that run under the
`ASYM_INTEL_PIPELINE` PAT with access to private infrastructure).

## Modules

| File | Purpose |
|---|---|
| `publisher_floor_gate.py` | Publish-floor gate — validates a candidate brief before commit (BX-9). |
| `publisher_floor_config.json` | Per-monitor floor-rule configuration. Config absence = gate fails closed. |

## week_ending vs. publish_date — convention (BX-9 §3.3 reconcile)

**Symptom:** `apply-debug-2026-05-14.json` reports `week_ending: "2026-05-13"` while the
brief is dated `2026-05-14`. This is **not a bug** — it is the intended convention:

| Field | Owner stage | Value | Semantics |
|---|---|---|---|
| `interpret._meta.week_ending` | Interpreter | Last day of the data-collection window | "The data covers events up to and including this date." |
| `publish_date` (env: `PUBLISH_DATE`, default: today UTC) | Publisher | Date of public release | "The brief was committed to the public surface on this date." |
| `apply-debug-{date}.json:week_ending` | Applier | Copied from `interpret._meta.week_ending` | Forensic provenance only. |

**Relationship rule:** `publish_date = week_ending + 1 calendar day` is the normal publish cadence.
Deviations (e.g., forced re-issue via `PUBLISH_DATE=`) are legitimate and not offset errors.

**Parity assertion:** the Publisher does not need to validate `week_ending` == `publish_date - 1 day`
because the Applier's `week_ending` is forensic (it records what the Interpreter saw, not what the
Publisher expects). Operators can use the field as a cross-check but it is not a blocking constraint.

**Registry:** see `asym-intel-internal:pipeline/engine/compose_base.py` for the Composer stage,
and `asym-intel-internal:pipeline/engine/metadata.py` for how `week_ending` is stamped on
`interpret._meta`. The Publisher reads `interpret._meta.week_ending` for freshness checks only
(see `publisher.py:check_synthesis_freshness`); the public-facing date is always `publish_date`.

_Authored: BX-9-PUBLISH-FLOOR-GATE (2026-05-14). Authority: AD-2026-05-14-SPRINT-3-BX-READER-IMPACT-BATCH._

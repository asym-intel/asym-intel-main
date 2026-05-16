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
| `flow_quality_contract.json` | Engine-wide flow-quality contract — per-monitor audit expectations, four contract states, applier/curator field requirements, absence-provenance rules (BX-3). |

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

## flow_quality_contract.json — contract specification (BX-3)

`flow_quality_contract.json` encodes the engine-wide flow-quality data contract for all seven live commons monitors. It is the machine-readable authority for:

- The four valid contract states at every stage: `present`, `absent_explained`, `absent_unknown`, `blocked`.
- Per-monitor `required_slots` (AIM/AGM is the fixture for BX-3 — `module_3` Investment and M&A must not be silent-empty).
- Applier eligibility rule: `review.verdict in {APPROVE, APPROVE_WITH_FLAGS, SKIP_NULL_CYCLE} AND compose.composer_error == false`.
- Curator gate calibration posture: schema validation is `WARN` (missing schema = HK item, not curator failure). Authority: `AD-2026-05-13-CI-GATE-CALIBRATION-DOCTRINE`.
- Absence provenance contract: interpreter-stage must stamp explicit absence before publisher sanitisation.

The `pipeline_flow_audit.py` harness (`pipeline/tools/`) and `_reusable-curator.yml` both read this contract at runtime. Any deviation from the contract is a data-quality defect reportable by the audit harness.

_Authored: BX-3-engine-wide-pipeline-flow-quality-contract (2026-05-14). Authority: AD-2026-05-14-SPRINT-3-BX-READER-IMPACT-BATCH._

## ERM Module Naming Convention (m00 sentinel)

**Context (HK-2026-05-14-erm-m00-legacy-key-emission):** The Environmental Risks Monitor (ERM) curator
emits `m00_*` keys alongside the fleet-standard `m01..mNN` module naming convention.

**`m00` is the canonical index/sentinel module** for ERM — it aggregates cross-module signals that
apply to the monitor as a whole rather than to any individual thematic module. The naming follows
the ERM module structure where `m00` is the zero-indexed sentinel/index position, consistent with
how `m00` is used in the ERM applier persistent-state schema.

**This is deliberate**, not drift. The fleet convention `m01..mNN` applies to thematic content
modules; `m00` is orthogonal — it is a structural sentinel, not a content module. Future monitors
that need a sentinel slot should follow this pattern.

**Authority:** W4-A cure (HK-2026-05-14-erm-m00-legacy-key-emission, session hk-20260516-183132).
Cross-reference: `pipeline/engine/flow_quality_contract.json` notes field for `environmental-risks`.

_Authored: W4-A (2026-05-16). Authority: AD-2026-05-14-SPRINT-3-BX-READER-IMPACT-BATCH._

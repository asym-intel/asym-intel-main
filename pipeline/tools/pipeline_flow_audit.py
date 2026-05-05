#!/usr/bin/env python3
"""
pipeline_flow_audit.py — reusable pipeline-flow data-quality audit harness.

BRIEF 1 of the Pipeline Flow Quality Sprint. Inspects generated artifacts and
published outputs for a monitor / consumer and produces a stage-by-stage flow
quality summary so an Architect can see, for each module slot:

    collection -> classification -> interpretation -> review -> compose -> apply -> publish

what state it is in (`present`, `absent_explained`, `absent_unknown`, `blocked`,
`missing_artifact`, `unknown`), where it first broke, and what user-facing
state was published. The tool reads only repository artifacts; no live web.

Usage
-----
    # Module-level trace for a specific report date
    python -m pipeline.tools.pipeline_flow_audit \\
        --consumer ai-governance --report-date 2026-05-02

    # Single module
    python -m pipeline.tools.pipeline_flow_audit \\
        --consumer ai-governance --report-date 2026-05-02 --module module_3

    # All indexed monitors compact summary
    python -m pipeline.tools.pipeline_flow_audit --all --output csv

Output formats
--------------
    --output json     (default) one row per module per stage
    --output rows     newline-delimited JSON, one per row
    --output csv      compact CSV summary, one row per module (last seen state)
    --output summary  short human-readable summary per monitor

Detections
----------
The harness flags, where derivable from artifacts:
    1. Bare empty module without absence provenance.
    2. Placeholder-only arrays such as [{}].
    3. Literal "null" strings treated as content.
    4. Apply/review hold or ready_to_publish=false not honored by publish.
    5. Module emptiness with material_change cycle disposition (suspected
       classification drift / interpreter break — flagged for follow-up,
       not solved here).
    6. Missing artifact at any stage.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

# Stable canonical stage order. The audit emits rows in this order so the
# first-break-stage detection is deterministic.
STAGES: tuple[str, ...] = (
    "collection",
    "classification",
    "interpretation",
    "review",
    "compose",
    "apply",
    "publish",
    "screen",
)

# State enum used in row output.
STATE_PRESENT = "present"
STATE_ABSENT_EXPLAINED = "absent_explained"
STATE_ABSENT_UNKNOWN = "absent_unknown"
STATE_BLOCKED = "blocked"
STATE_MISSING_ARTIFACT = "missing_artifact"
STATE_UNKNOWN = "unknown"

# Consumer-adapter auditability status (BRIEF BX-2). One of these is reported
# per registered consumer so the harness can surface coverage gaps the
# stage-by-stage audit alone cannot — e.g. consumers whose artifacts are not
# yet stable enough for a full adapter.
AUDIT_FULLY = "fully_auditable"
AUDIT_PARTIAL = "partially_auditable"
AUDIT_MISSING_FLOW_MAP = "missing_flow_map"
AUDIT_WAIVED = "temporarily_waived"

# Module-meta keys excluded from "is body empty" checks. Mirrors publisher's
# _module_body_is_empty meta_keys so the harness sees the same shape.
_MODULE_META_KEYS = {"title", "null_signal", "empty_reason", "fallback_message"}


# ── Data shapes ────────────────────────────────────────────────────────────


@dataclass
class FlowRow:
    """One row of the pipeline-flow audit output.

    Fields kept aligned with the contract draft (pipeline-flow-contract-draft.md
    "Minimum artifact fields" block) but only populated where derivable from
    repository artifacts. Anything we cannot determine from artifacts stays None
    rather than being guessed; downstream consumers can branch on None.
    """

    consumer: str
    report_date: str | None
    stage: str
    artifact: str | None
    module_id: str | None
    state: str
    meaningful_leaf_count: int | None = None
    evidence_count: int | None = None
    classified_as: str | None = None
    absence_reason: str | None = None
    absence_basis: str | None = None
    review_verdict: str | None = None
    ready_to_publish: bool | None = None
    hold_reason: str | None = None
    first_break_stage: str | None = None
    user_facing_state: str | None = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Consumer adapter contract (BRIEF BX-2) ────────────────────────────────
#
# Onboarding a new consumer (engine-internal or external like Advennt):
#
#   1. Define a ConsumerAdapter and call register_consumer(adapter). The
#      adapter declares: where the consumer's stage artifacts live, how its
#      slot map is keyed, and which fields carry eligibility / publication
#      state / absence provenance. These fields are the contract the harness
#      reads against; rename a field in the consumer and you must update the
#      adapter at the same time.
#   2. If the consumer's artifacts already match the monitor shape (per-stage
#      JSON keyed by `module_*`), reuse `consumer_type="monitor"` and the
#      monitor flow walker handles it automatically (see _MONITOR_ADAPTER).
#   3. If the consumer's shape differs (e.g. jurisdiction-keyed instead of
#      module-keyed) and is not yet stable, register as a STUB with status
#      AUDIT_WAIVED and a `waiver_reason`. The harness lists the consumer in
#      `--all` output but does not attempt to walk its stages. Once the shape
#      stabilises, replace the stub with a fully-populated adapter and a
#      consumer-specific row builder.
#
# The adapter is intentionally a flat dataclass rather than an ABC: stubs
# carry empty dicts for fields they cannot yet populate, and a future
# strategy-pattern extension can dispatch on `consumer_type` without
# requiring every consumer to subclass.


@dataclass
class ConsumerAdapter:
    """Declares how the harness should audit one pipeline consumer.

    Required minimum fields per BRIEF BX-2 §"adapter pattern". A stub adapter
    (one whose artifacts are not yet stable) sets `status=AUDIT_WAIVED` and
    populates `waiver_reason`; the artifact-path/slot-map fields may be empty
    on a stub since the harness will not walk them.
    """

    consumer_id: str
    consumer_type: str
    stage_artifacts: dict[str, str] = field(default_factory=dict)
    slot_map: dict[str, str] = field(default_factory=dict)
    eligibility_source: str | None = None
    published_output_source: str | None = None
    absence_state_fields: list[str] = field(default_factory=list)
    classification_trace_fields: list[str] = field(default_factory=list)
    screen_or_output_state_fields: list[str] = field(default_factory=list)
    status: str = AUDIT_FULLY
    waiver_reason: str | None = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# Canonical adapter for the monitor consumer type. Every monitor in
# static/monitors/monitor-registry.json is audited through this template;
# the per-consumer registration below clones it with the slug populated.
_MONITOR_ADAPTER = ConsumerAdapter(
    consumer_id="<monitor-template>",
    consumer_type="monitor",
    stage_artifacts={
        "weekly": "pipeline/monitors/<slug>/weekly/weekly-<date>.json",
        "reasoner": "pipeline/monitors/<slug>/reasoner/reasoner-<date>.json",
        "interpret": "pipeline/monitors/<slug>/synthesised/interpret-<date>.json",
        "review": "pipeline/monitors/<slug>/synthesised/review-<date>.json",
        "compose": "pipeline/monitors/<slug>/synthesised/compose-<date>.json",
        "apply": "pipeline/monitors/<slug>/applied/apply-<date>.json",
        "publish": "static/monitors/<slug>/data/report-<date>.json",
    },
    slot_map={"key_pattern": "module_*", "container": "report root object"},
    eligibility_source="apply.publication.ready_to_publish",
    published_output_source="static/monitors/<slug>/data/report-latest.json",
    absence_state_fields=["null_signal", "empty_reason", "fallback_message"],
    classification_trace_fields=[
        "_meta.cycle_disposition", "_meta.null_signal_week",
    ],
    screen_or_output_state_fields=[
        "user_facing_state",  # synthesised by the harness on the publish row
    ],
    status=AUDIT_FULLY,
)


# Adapter stub for Advennt (BRIEF BX-2 §3). Not a full working adapter —
# Advennt's artifacts are not stable yet (Sprint CO jurisdiction baselining
# still in progress). Harness reports the consumer with status=AUDIT_WAIVED
# and the documented field requirements that must be met before the stub
# can be replaced with a real adapter.
_ADVENNT_STUB = ConsumerAdapter(
    consumer_id="advennt",
    consumer_type="jurisdiction-intelligence",
    stage_artifacts={
        # Required artifact paths to be confirmed by Sprint CO. Populated
        # placeholders so the contract is documented even while waived.
        "collection": "pipeline/consumers/advennt/collection/<jurisdiction>-<date>.json",
        "classification": "pipeline/consumers/advennt/classification/<jurisdiction>-<date>.json",
        "interpretation": "pipeline/consumers/advennt/interpretation/<jurisdiction>-<date>.json",
        "review": "pipeline/consumers/advennt/review/<jurisdiction>-<date>.json",
        "screen": "pipeline/consumers/advennt/screen/<jurisdiction>-<date>.json",
        "publish": "static/consumers/advennt/data/<jurisdiction>-latest.json",
    },
    slot_map={
        "key_pattern": "<jurisdiction-code>",
        "container": "per-jurisdiction document",
        "TBD": "exact jurisdiction code set + nesting confirmed by Sprint CO baseline",
    },
    eligibility_source="screen.eligibility (TBD: exact field name)",
    published_output_source="static/consumers/advennt/data/<jurisdiction>-latest.json",
    absence_state_fields=[
        # Confirmed by Sprint CO once jurisdiction baselining lands.
        "null_signal", "empty_reason", "fallback_message",
    ],
    classification_trace_fields=[
        "classification.regime", "classification.confidence",
    ],
    screen_or_output_state_fields=[
        "screen.user_facing_state", "screen.regulatory_outlook",
    ],
    status=AUDIT_WAIVED,
    waiver_reason=(
        "Sprint CO jurisdiction baselining in progress — adapter stub only. "
        "See Sprint CO (asym-intel/asym-intel-internal:docs/sprints/2026-05-04-CJ/). "
        "Replace this stub with a fully-populated adapter + consumer-specific "
        "row walker once jurisdiction artifact shape stabilises."
    ),
    notes=[
        "Not yet audited end-to-end; --all output will list this consumer "
        "under registered_consumers but skip stage-by-stage walk.",
    ],
)


# Module-level consumer registry. Keyed by consumer_id. Mutating helpers are
# exposed (`register_consumer`, `unregister_consumer`) so tests can install
# fixture adapters without rewriting the module.
_CONSUMER_REGISTRY: dict[str, ConsumerAdapter] = {
    _ADVENNT_STUB.consumer_id: _ADVENNT_STUB,
}


def register_consumer(adapter: ConsumerAdapter) -> None:
    """Register a consumer adapter. Last-write-wins on consumer_id collision.

    Stub adapters (status=AUDIT_WAIVED) are valid; the harness lists them in
    --all output without walking their stages.
    """
    _CONSUMER_REGISTRY[adapter.consumer_id] = adapter


def unregister_consumer(consumer_id: str) -> None:
    """Remove a consumer from the registry. No-op if not registered."""
    _CONSUMER_REGISTRY.pop(consumer_id, None)


def list_consumers() -> list[ConsumerAdapter]:
    """Snapshot of currently registered consumers, sorted by consumer_id."""
    return sorted(_CONSUMER_REGISTRY.values(), key=lambda a: a.consumer_id)


def _monitor_adapter_for(slug: str) -> ConsumerAdapter:
    """Materialise the monitor template for a specific monitor slug."""
    template = _MONITOR_ADAPTER
    return ConsumerAdapter(
        consumer_id=slug,
        consumer_type=template.consumer_type,
        stage_artifacts={
            k: v.replace("<slug>", slug) for k, v in template.stage_artifacts.items()
        },
        slot_map=dict(template.slot_map),
        eligibility_source=template.eligibility_source,
        published_output_source=(
            template.published_output_source or ""
        ).replace("<slug>", slug) or None,
        absence_state_fields=list(template.absence_state_fields),
        classification_trace_fields=list(template.classification_trace_fields),
        screen_or_output_state_fields=list(template.screen_or_output_state_fields),
        status=template.status,
        waiver_reason=template.waiver_reason,
        notes=list(template.notes),
    )


# ── Artifact path resolution ───────────────────────────────────────────────


def _repo_root() -> Path:
    """Repo root resolved from this file's location.

    pipeline/tools/pipeline_flow_audit.py -> repo root is parents[2].
    """
    return Path(__file__).resolve().parents[2]


def _artifact_paths(
    repo: Path, consumer: str, report_date: str | None
) -> dict[str, Path]:
    """Return canonical artifact path candidates per stage.

    The harness does not insist on every path existing; missing artifacts
    become STATE_MISSING_ARTIFACT rows. Date-stamped variants are preferred;
    `*-latest.json` is the fallback for the publish/apply layers.
    """
    base = repo / "pipeline" / "monitors" / consumer
    static = repo / "static" / "monitors" / consumer / "data"

    def _dated_or_latest(folder: Path, prefix: str) -> Path:
        if report_date:
            dated = folder / f"{prefix}-{report_date}.json"
            if dated.exists():
                return dated
        return folder / f"{prefix}-latest.json"

    paths: dict[str, Path] = {
        # collection: weekly research / collected signals
        "weekly": _dated_or_latest(base / "weekly", "weekly"),
        "reasoner": _dated_or_latest(base / "reasoner", "reasoner"),
        # interpretation / review / compose
        "interpret": _dated_or_latest(base / "synthesised", "interpret"),
        "review": _dated_or_latest(base / "synthesised", "review"),
        "compose": _dated_or_latest(base / "synthesised", "compose"),
        # apply (publication eligibility)
        "apply": _dated_or_latest(base / "applied", "apply"),
        # publish: static published JSON
        "publish": (
            static / f"report-{report_date}.json"
            if report_date and (static / f"report-{report_date}.json").exists()
            else static / "report-latest.json"
        ),
    }
    return paths


def _safe_load_json(path: Path) -> dict | list | None:
    """Load JSON or return None on missing / invalid file. No raises."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


# ── Emptiness detection ────────────────────────────────────────────────────
#
# These mirror publisher.sanitise_for_public's _is_empty_placeholder so the
# audit reads the same emptiness contract the publisher enforces post-#185.


def _is_empty_value(v: Any) -> bool:
    """True if v is a 'silently empty' value under the contract.

    Matches publisher._is_empty_placeholder semantics: empty dicts/lists,
    placeholder-only lists like [{}], empty strings, and the literal "null"
    sentinel string (case-insensitive).
    """
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == "" or v.strip().lower() == "null"
    if isinstance(v, dict):
        return all(_is_empty_value(x) for x in v.values()) if v else True
    if isinstance(v, list):
        if not v:
            return True
        return all(_is_empty_value(x) for x in v)
    return False


def _module_body_is_empty(module: dict) -> bool:
    """Module body emptiness — same shape as publisher._module_body_is_empty."""
    if not isinstance(module, dict):
        return False
    body = {k: v for k, v in module.items() if k not in _MODULE_META_KEYS}
    if not body:
        return True
    return all(_is_empty_value(v) for v in body.values())


def _meaningful_leaf_count(value: Any) -> int:
    """Count meaningful (non-empty) leaves under a module body.

    Strings, numbers, bools count as 1 leaf; dicts/lists are walked. Empty
    placeholders (per _is_empty_value) contribute 0. Used as a coarse signal
    of module richness — module_2.models with 23 entries should easily exceed
    threshold while module_3 with [{}] arrays should score 0.
    """
    if value is None:
        return 0
    if isinstance(value, (bool, int, float)):
        return 1
    if isinstance(value, str):
        return 0 if _is_empty_value(value) else 1
    if isinstance(value, dict):
        return sum(_meaningful_leaf_count(v) for v in value.values())
    if isinstance(value, list):
        return sum(_meaningful_leaf_count(v) for v in value)
    return 0


def _has_placeholder_array(module: dict) -> bool:
    """True if any list-valued field contains only placeholder objects ([{}])."""
    if not isinstance(module, dict):
        return False
    for k, v in module.items():
        if k in _MODULE_META_KEYS:
            continue
        if isinstance(v, list) and v and all(
            isinstance(x, dict) and _is_empty_value(x) for x in v
        ):
            return True
    return False


def _has_literal_null_string(module: dict) -> bool:
    """True if any string field contains the literal "null" sentinel."""
    if not isinstance(module, dict):
        return False
    for k, v in module.items():
        if k in _MODULE_META_KEYS:
            continue
        if isinstance(v, str) and v.strip().lower() == "null":
            return True
    return False


# ── Per-stage row builders ─────────────────────────────────────────────────


def _module_keys(*sources: dict | None) -> list[str]:
    """Union of `module_*` keys across one or more dicts, in numeric order."""
    keys: set[str] = set()
    for src in sources:
        if not isinstance(src, dict):
            continue
        for k in src.keys():
            if isinstance(k, str) and k.startswith("module_"):
                keys.add(k)

    def _sort_key(k: str) -> tuple[int, str]:
        suffix = k[len("module_") :]
        try:
            return (int(suffix), k)
        except ValueError:
            return (10**9, k)

    return sorted(keys, key=_sort_key)


def _interpret_row(
    consumer: str,
    report_date: str | None,
    interpret: dict | None,
    interpret_path: Path,
    module_id: str,
) -> FlowRow:
    """Row describing the interpretation stage for one module."""
    if interpret is None:
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="interpretation",
            artifact=str(interpret_path),
            module_id=module_id,
            state=STATE_MISSING_ARTIFACT,
            absence_basis="missing_artifact",
        )

    module = interpret.get(module_id)
    meta = interpret.get("_meta", {}) if isinstance(interpret, dict) else {}
    cycle = (meta.get("cycle_disposition") or "").strip().lower() if isinstance(meta, dict) else ""
    null_week = bool(meta.get("null_signal_week")) if isinstance(meta, dict) else False

    if not isinstance(module, dict):
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="interpretation",
            artifact=str(interpret_path),
            module_id=module_id,
            state=STATE_UNKNOWN,
            notes=[f"module key {module_id} missing or non-dict in interpret"],
        )

    leaves = _meaningful_leaf_count(
        {k: v for k, v in module.items() if k not in _MODULE_META_KEYS}
    )
    notes: list[str] = []
    state: str
    absence_reason: str | None = None
    absence_basis: str | None = None

    body_empty = _module_body_is_empty(module)
    has_placeholder = _has_placeholder_array(module)
    has_null_str = _has_literal_null_string(module)

    if has_placeholder:
        notes.append("placeholder_array_detected")
    if has_null_str:
        notes.append("literal_null_string_detected")

    if not body_empty:
        state = STATE_PRESENT
    else:
        # Body empty: is it explained?
        if module.get("null_signal") is True and module.get("empty_reason"):
            state = STATE_ABSENT_EXPLAINED
            absence_reason = module.get("empty_reason")
            absence_basis = "module_null_signal"
        elif null_week or cycle in {"null_cycle", "partial_cycle"}:
            # Week-level absence available; module-level absence implicit.
            state = STATE_ABSENT_EXPLAINED
            absence_reason = "no_material_content"
            absence_basis = (
                "cycle_disposition" if cycle else "null_signal_week"
            )
            notes.append("module_level_provenance_missing_relies_on_week_level")
        else:
            # Material cycle but module empty without provenance — silent empty.
            state = STATE_ABSENT_UNKNOWN
            absence_reason = "unknown"
            absence_basis = "interpreter_silent_empty"
            notes.append("bare_empty_module_no_provenance")
            if cycle == "material_change":
                notes.append("suspected_classification_drift")

    return FlowRow(
        consumer=consumer,
        report_date=report_date,
        stage="interpretation",
        artifact=str(interpret_path),
        module_id=module_id,
        state=state,
        meaningful_leaf_count=leaves,
        absence_reason=absence_reason,
        absence_basis=absence_basis,
        notes=notes,
    )


def _review_row(
    consumer: str,
    report_date: str | None,
    review: dict | None,
    review_path: Path,
    module_id: str,
) -> FlowRow:
    """Row describing the review stage. Review is week-level, not per-module,
    so the row attributes the verdict to each module slot."""
    if review is None:
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="review",
            artifact=str(review_path),
            module_id=module_id,
            state=STATE_MISSING_ARTIFACT,
            absence_basis="missing_artifact",
        )

    verdict = review.get("verdict") if isinstance(review, dict) else None
    legacy = review.get("verdict_legacy") if isinstance(review, dict) else None
    reason = review.get("verdict_reason") if isinstance(review, dict) else None
    notes: list[str] = []
    state: str
    if isinstance(verdict, str) and verdict.lower() in {
        "hold-for-review", "hold_for_review", "reject", "rejected",
    }:
        state = STATE_BLOCKED
        notes.append(f"review_verdict={verdict}")
        if reason:
            notes.append(f"review_reason={reason}")
    elif isinstance(verdict, str) and verdict:
        state = STATE_PRESENT
    elif isinstance(legacy, str) and legacy.lower() in {"reject", "rejected"}:
        state = STATE_BLOCKED
        notes.append(f"review_verdict_legacy={legacy}")
    else:
        state = STATE_UNKNOWN

    return FlowRow(
        consumer=consumer,
        report_date=report_date,
        stage="review",
        artifact=str(review_path),
        module_id=module_id,
        state=state,
        review_verdict=verdict if isinstance(verdict, str) else None,
        notes=notes,
    )


def _apply_row(
    consumer: str,
    report_date: str | None,
    apply_doc: dict | None,
    apply_path: Path,
    module_id: str,
) -> FlowRow:
    """Row describing apply / publication-eligibility for one module slot."""
    if apply_doc is None:
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="apply",
            artifact=str(apply_path),
            module_id=module_id,
            state=STATE_MISSING_ARTIFACT,
            absence_basis="missing_artifact",
        )

    pub = apply_doc.get("publication") if isinstance(apply_doc, dict) else None
    if not isinstance(pub, dict):
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="apply",
            artifact=str(apply_path),
            module_id=module_id,
            state=STATE_UNKNOWN,
            notes=["apply_publication_block_missing"],
        )

    ready = pub.get("ready_to_publish")
    hold_reason = pub.get("hold_reason")
    notes: list[str] = []
    if ready is False:
        state = STATE_BLOCKED
        if hold_reason:
            notes.append(f"hold_reason={hold_reason}")
    elif ready is True:
        state = STATE_PRESENT
    else:
        state = STATE_UNKNOWN
        notes.append("ready_to_publish_unset")

    return FlowRow(
        consumer=consumer,
        report_date=report_date,
        stage="apply",
        artifact=str(apply_path),
        module_id=module_id,
        state=state,
        ready_to_publish=ready if isinstance(ready, bool) else None,
        hold_reason=hold_reason if isinstance(hold_reason, str) else None,
        notes=notes,
    )


def _publish_row(
    consumer: str,
    report_date: str | None,
    published: dict | None,
    publish_path: Path,
    module_id: str,
    apply_blocked: bool,
) -> FlowRow:
    """Row describing the publish stage — what actually reached published JSON.

    Honors apply-stage blocking: if apply said ready_to_publish=false but
    published JSON still exists for this module, that's a contract violation
    (the pre-#186 break). Flagged in notes.
    """
    if published is None:
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="publish",
            artifact=str(publish_path),
            module_id=module_id,
            state=STATE_MISSING_ARTIFACT,
            absence_basis="missing_artifact",
        )

    module = published.get(module_id) if isinstance(published, dict) else None
    notes: list[str] = []
    if not isinstance(module, dict):
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="publish",
            artifact=str(publish_path),
            module_id=module_id,
            state=STATE_UNKNOWN,
            notes=[f"module {module_id} not in published report"],
        )

    leaves = _meaningful_leaf_count(
        {k: v for k, v in module.items() if k not in _MODULE_META_KEYS}
    )
    body_empty = _module_body_is_empty(module)
    has_placeholder = _has_placeholder_array(module)
    has_null_str = _has_literal_null_string(module)
    if has_placeholder:
        notes.append("placeholder_array_detected")
    if has_null_str:
        notes.append("literal_null_string_detected")

    state: str
    absence_reason: str | None = None
    absence_basis: str | None = None
    user_facing: str | None = None

    if not body_empty:
        state = STATE_PRESENT
        user_facing = "content"
    elif module.get("null_signal") is True and module.get("empty_reason"):
        state = STATE_ABSENT_EXPLAINED
        absence_reason = module.get("empty_reason")
        absence_basis = "module_null_signal"
        user_facing = (
            "explicit_unknown"
            if absence_reason == "unknown"
            else "explicit_absence"
        )
    else:
        state = STATE_ABSENT_UNKNOWN
        absence_reason = "unknown"
        absence_basis = "publish_silent_empty"
        user_facing = "silent_empty"
        notes.append("bare_empty_module_no_provenance")

    if apply_blocked and state != STATE_MISSING_ARTIFACT:
        # Apply blocked publication, but a report exists → contract violation.
        notes.append("apply_block_not_honored")

    return FlowRow(
        consumer=consumer,
        report_date=report_date,
        stage="publish",
        artifact=str(publish_path),
        module_id=module_id,
        state=state,
        meaningful_leaf_count=leaves,
        absence_reason=absence_reason,
        absence_basis=absence_basis,
        user_facing_state=user_facing,
        notes=notes,
    )


def _collection_row(
    consumer: str,
    report_date: str | None,
    weekly: dict | None,
    weekly_path: Path,
    module_id: str,
) -> FlowRow:
    """Row describing the collection stage at module-level granularity.

    Collection artifacts (weekly research) are not module-keyed in current
    monitors, so we emit a coarse 'present if weekly artifact non-empty'
    state per module slot. Future per-module classification linkage would
    refine this; explicit follow-up.
    """
    if weekly is None:
        return FlowRow(
            consumer=consumer,
            report_date=report_date,
            stage="collection",
            artifact=str(weekly_path),
            module_id=module_id,
            state=STATE_MISSING_ARTIFACT,
            absence_basis="missing_artifact",
        )
    leaves = _meaningful_leaf_count(weekly) if isinstance(weekly, dict) else 0
    state = STATE_PRESENT if leaves > 0 else STATE_ABSENT_UNKNOWN
    return FlowRow(
        consumer=consumer,
        report_date=report_date,
        stage="collection",
        artifact=str(weekly_path),
        module_id=module_id,
        state=state,
        meaningful_leaf_count=leaves,
        notes=["collection_module_granularity_unavailable"],
    )


# ── Audit driver ───────────────────────────────────────────────────────────


def audit_consumer(
    consumer: str,
    report_date: str | None = None,
    repo: Path | None = None,
    module_filter: list[str] | None = None,
) -> list[FlowRow]:
    """Run the pipeline-flow audit for a single consumer/monitor.

    Returns one row per module per stage. Does not raise on missing artifacts;
    the caller can detect via STATE_MISSING_ARTIFACT.
    """
    repo = repo or _repo_root()
    paths = _artifact_paths(repo, consumer, report_date)

    weekly = _safe_load_json(paths["weekly"])
    interpret = _safe_load_json(paths["interpret"])
    review = _safe_load_json(paths["review"])
    apply_doc = _safe_load_json(paths["apply"])
    published = _safe_load_json(paths["publish"])

    apply_blocked = False
    if isinstance(apply_doc, dict):
        pub = apply_doc.get("publication") or {}
        apply_blocked = pub.get("ready_to_publish") is False

    keys = _module_keys(interpret, published)
    if module_filter:
        keys = [k for k in keys if k in set(module_filter)]

    rows: list[FlowRow] = []
    for module_id in keys:
        per_stage_rows = [
            _collection_row(consumer, report_date, weekly, paths["weekly"], module_id),
            _interpret_row(consumer, report_date, interpret, paths["interpret"], module_id),
            _review_row(consumer, report_date, review, paths["review"], module_id),
            _apply_row(consumer, report_date, apply_doc, paths["apply"], module_id),
            _publish_row(consumer, report_date, published, paths["publish"], module_id, apply_blocked),
        ]
        # Compute first_break_stage: earliest stage whose state is not
        # PRESENT/ABSENT_EXPLAINED. Propagate to every row for that module
        # so a CSV-only consumer sees the locus on each line.
        first_break = None
        for r in per_stage_rows:
            if r.state not in (STATE_PRESENT, STATE_ABSENT_EXPLAINED):
                first_break = r.stage
                break
        # Carry review/apply verdicts forward onto publish row for convenience.
        review_verdict = next(
            (r.review_verdict for r in per_stage_rows if r.stage == "review" and r.review_verdict),
            None,
        )
        apply_row = next((r for r in per_stage_rows if r.stage == "apply"), None)
        for r in per_stage_rows:
            r.first_break_stage = first_break
            if r.stage == "publish":
                if review_verdict and r.review_verdict is None:
                    r.review_verdict = review_verdict
                if apply_row is not None:
                    if r.ready_to_publish is None:
                        r.ready_to_publish = apply_row.ready_to_publish
                    if r.hold_reason is None:
                        r.hold_reason = apply_row.hold_reason
        rows.extend(per_stage_rows)

    return rows


def audit_all_indexed(
    repo: Path | None = None,
    report_date: str | None = None,
) -> dict[str, list[FlowRow]]:
    """Audit every monitor in static/monitors/monitor-registry.json.

    Returns {consumer_slug: [rows]}. Monitors without artifacts produce only
    STATE_MISSING_ARTIFACT rows but are still listed so the caller can see
    full coverage. `report_date` falls back to *-latest.json if absent.
    """
    repo = repo or _repo_root()
    registry_path = repo / "static" / "monitors" / "monitor-registry.json"
    out: dict[str, list[FlowRow]] = {}
    registry = _safe_load_json(registry_path)
    if not isinstance(registry, dict):
        return out
    for monitor in registry.get("monitors", []) or []:
        slug = monitor.get("slug") if isinstance(monitor, dict) else None
        if not slug:
            continue
        out[slug] = audit_consumer(slug, report_date=report_date, repo=repo)
    return out


def collect_consumer_adapters(
    repo: Path | None = None,
) -> list[ConsumerAdapter]:
    """Return the full set of registered consumer adapters for `--all`.

    Combines:
      • Every monitor in static/monitors/monitor-registry.json, materialised
        from the monitor adapter template (consumer_type="monitor").
      • All consumers in `_CONSUMER_REGISTRY` (e.g. the Advennt stub).

    Monitors are not stored in `_CONSUMER_REGISTRY` because the registry on
    disk is the source of truth for them; this keeps the two indexes from
    drifting. Explicit registrations win on consumer_id collision so a future
    monitor that needs a custom adapter can override the template.
    """
    repo = repo or _repo_root()
    registry_path = repo / "static" / "monitors" / "monitor-registry.json"
    by_id: dict[str, ConsumerAdapter] = {}
    registry = _safe_load_json(registry_path)
    if isinstance(registry, dict):
        for monitor in registry.get("monitors", []) or []:
            slug = monitor.get("slug") if isinstance(monitor, dict) else None
            if slug:
                by_id[slug] = _monitor_adapter_for(slug)
    for adapter in _CONSUMER_REGISTRY.values():
        by_id[adapter.consumer_id] = adapter
    return sorted(by_id.values(), key=lambda a: a.consumer_id)


def consumer_auditability_report(
    repo: Path | None = None,
    report_date: str | None = None,
) -> list[dict[str, Any]]:
    """Per-consumer auditability summary for `--all` output.

    Each entry records consumer_id, consumer_type, status, and (for active
    monitors) a brief audit snapshot derived from the same run as
    audit_all_indexed. Stubs (AUDIT_WAIVED) include their waiver_reason and
    are NOT walked stage-by-stage.
    """
    repo = repo or _repo_root()
    adapters = collect_consumer_adapters(repo=repo)
    monitor_audit: dict[str, list[FlowRow]] | None = None
    out: list[dict[str, Any]] = []
    for adapter in adapters:
        entry: dict[str, Any] = {
            "consumer_id": adapter.consumer_id,
            "consumer_type": adapter.consumer_type,
            "status": adapter.status,
            "waiver_reason": adapter.waiver_reason,
        }
        if adapter.consumer_type == "monitor" and adapter.status == AUDIT_FULLY:
            if monitor_audit is None:
                monitor_audit = audit_all_indexed(repo=repo, report_date=report_date)
            rows = monitor_audit.get(adapter.consumer_id, [])
            summary = summarise_consumer(adapter.consumer_id, rows)
            entry["audit_summary"] = {
                "report_date": summary.get("report_date"),
                "module_count": summary.get("module_count"),
                "publish_present": summary.get("publish_present"),
                "publish_silent_empty": summary.get("publish_silent_empty"),
                "missing_artifacts": summary.get("missing_artifacts"),
            }
        out.append(entry)
    return out


# ── Output formatters ──────────────────────────────────────────────────────


def rows_to_json(rows: list[FlowRow]) -> str:
    return json.dumps([r.as_dict() for r in rows], indent=2)


def rows_to_ndjson(rows: list[FlowRow]) -> str:
    return "\n".join(json.dumps(r.as_dict()) for r in rows)


def rows_to_csv(rows: list[FlowRow]) -> str:
    """Compact CSV: one row per module per stage with primary fields.

    Keeps the column set narrow — full row data is available in JSON output.
    """
    buf = io.StringIO()
    cols = [
        "consumer", "report_date", "stage", "module_id", "state",
        "meaningful_leaf_count", "review_verdict", "ready_to_publish",
        "hold_reason", "absence_basis", "first_break_stage",
        "user_facing_state", "notes",
    ]
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        d = r.as_dict()
        d["notes"] = ";".join(d.get("notes") or [])
        w.writerow([d.get(c) for c in cols])
    return buf.getvalue()


def summarise_consumer(consumer: str, rows: list[FlowRow]) -> dict[str, Any]:
    """Compact per-consumer summary suited to triage output.

    Aggregates module-level state at the publish stage (the user-visible
    surface) but also surfaces apply/review hold violations and silent-empty
    counts derivable from earlier stages. Empty rows means the audit could
    not load any artifact.
    """
    publish_rows = [r for r in rows if r.stage == "publish"]
    interp_rows = [r for r in rows if r.stage == "interpretation"]
    apply_rows = [r for r in rows if r.stage == "apply"]
    review_rows = [r for r in rows if r.stage == "review"]

    def _count(rs: Iterable[FlowRow], state: str) -> int:
        return sum(1 for r in rs if r.state == state)

    silent_empty_publish = [
        r.module_id for r in publish_rows if r.state == STATE_ABSENT_UNKNOWN
    ]
    silent_empty_interp = [
        r.module_id for r in interp_rows if r.state == STATE_ABSENT_UNKNOWN
    ]
    apply_block_violations = [
        r.module_id for r in publish_rows
        if "apply_block_not_honored" in (r.notes or [])
    ]
    placeholder_publish = [
        r.module_id for r in publish_rows
        if "placeholder_array_detected" in (r.notes or [])
    ]
    null_string_publish = [
        r.module_id for r in publish_rows
        if "literal_null_string_detected" in (r.notes or [])
    ]

    review_verdict = next(
        (r.review_verdict for r in review_rows if r.review_verdict), None
    )
    ready = next(
        (r.ready_to_publish for r in apply_rows if r.ready_to_publish is not None),
        None,
    )

    return {
        "consumer": consumer,
        "report_date": (rows[0].report_date if rows else None),
        "module_count": len({r.module_id for r in publish_rows if r.module_id}),
        "publish_present": _count(publish_rows, STATE_PRESENT),
        "publish_absent_explained": _count(publish_rows, STATE_ABSENT_EXPLAINED),
        "publish_silent_empty": silent_empty_publish,
        "interpret_silent_empty": silent_empty_interp,
        "apply_block_not_honored": apply_block_violations,
        "placeholder_arrays": placeholder_publish,
        "literal_null_strings": null_string_publish,
        "review_verdict": review_verdict,
        "ready_to_publish": ready,
        "missing_artifacts": sorted({
            r.stage for r in rows if r.state == STATE_MISSING_ARTIFACT
        }),
    }


def summary_csv(summaries: list[dict[str, Any]]) -> str:
    """Compact CSV summary across multiple consumers — for triage."""
    buf = io.StringIO()
    cols = [
        "consumer", "report_date", "module_count", "publish_present",
        "publish_absent_explained", "publish_silent_empty_count",
        "interpret_silent_empty_count", "apply_block_not_honored_count",
        "placeholder_arrays_count", "literal_null_strings_count",
        "review_verdict", "ready_to_publish", "missing_artifacts",
    ]
    w = csv.writer(buf)
    w.writerow(cols)
    for s in summaries:
        w.writerow([
            s.get("consumer"),
            s.get("report_date"),
            s.get("module_count"),
            s.get("publish_present"),
            s.get("publish_absent_explained"),
            len(s.get("publish_silent_empty") or []),
            len(s.get("interpret_silent_empty") or []),
            len(s.get("apply_block_not_honored") or []),
            len(s.get("placeholder_arrays") or []),
            len(s.get("literal_null_strings") or []),
            s.get("review_verdict"),
            s.get("ready_to_publish"),
            ";".join(s.get("missing_artifacts") or []),
        ])
    return buf.getvalue()


def summary_text(summaries: list[dict[str, Any]]) -> str:
    """Short human-readable summary — one block per consumer."""
    lines: list[str] = []
    for s in summaries:
        lines.append(f"[{s['consumer']}] report_date={s.get('report_date') or '<latest>'}")
        lines.append(
            f"  modules={s['module_count']} present={s['publish_present']} "
            f"absent_explained={s['publish_absent_explained']} "
            f"silent_empty(publish)={len(s.get('publish_silent_empty') or [])} "
            f"silent_empty(interpret)={len(s.get('interpret_silent_empty') or [])}"
        )
        if s.get("publish_silent_empty"):
            lines.append(f"  silent-empty publish modules: {s['publish_silent_empty']}")
        if s.get("interpret_silent_empty"):
            lines.append(f"  silent-empty interpret modules: {s['interpret_silent_empty']}")
        if s.get("apply_block_not_honored"):
            lines.append(
                f"  apply-block-not-honored: {s['apply_block_not_honored']}"
            )
        if s.get("placeholder_arrays"):
            lines.append(f"  placeholder arrays: {s['placeholder_arrays']}")
        if s.get("literal_null_strings"):
            lines.append(f"  literal 'null' strings: {s['literal_null_strings']}")
        lines.append(
            f"  review_verdict={s.get('review_verdict')} "
            f"ready_to_publish={s.get('ready_to_publish')}"
        )
        if s.get("missing_artifacts"):
            lines.append(f"  missing artifacts: {s['missing_artifacts']}")
    return "\n".join(lines)


def consumers_text(report: list[dict[str, Any]]) -> str:
    """Human-readable rendering of the registered-consumers block.

    Used as a footer on `--all --output summary` so an Architect sees the
    full consumer registration alongside the monitor walk.
    """
    lines: list[str] = ["", "Registered consumers (BRIEF BX-2 adapter contract):"]
    for entry in report:
        lines.append(
            f"  - {entry['consumer_id']} "
            f"(type={entry['consumer_type']}, status={entry['status']})"
        )
        if entry.get("waiver_reason"):
            lines.append(f"      waiver_reason: {entry['waiver_reason']}")
        audit = entry.get("audit_summary")
        if audit:
            lines.append(
                f"      audit: report_date={audit.get('report_date') or '<latest>'} "
                f"modules={audit.get('module_count')} "
                f"present={audit.get('publish_present')} "
                f"silent_empty={len(audit.get('publish_silent_empty') or [])}"
            )
    return "\n".join(lines)


def consumers_csv(report: list[dict[str, Any]]) -> str:
    """CSV rendering of the registered-consumers block."""
    buf = io.StringIO()
    cols = ["consumer_id", "consumer_type", "status", "waiver_reason"]
    w = csv.writer(buf)
    w.writerow(cols)
    for entry in report:
        w.writerow([entry.get(c) for c in cols])
    return buf.getvalue()


# ── CLI entrypoint ─────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pipeline_flow_audit",
        description="Pipeline-flow data-quality audit harness (BRIEF 1).",
    )
    p.add_argument("--consumer", help="Monitor / consumer slug (e.g. ai-governance)")
    p.add_argument(
        "--report-date",
        help="Report date slug (e.g. 2026-05-02). Falls back to *-latest.json.",
    )
    p.add_argument(
        "--module",
        action="append",
        dest="modules",
        help="Filter to one or more module ids (e.g. module_3). Repeatable.",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="Audit every monitor in static/monitors/monitor-registry.json.",
    )
    p.add_argument(
        "--output",
        choices=["json", "rows", "csv", "summary", "summary-csv", "consumers-json"],
        default="json",
        help="Output format. 'summary' for per-consumer triage text, "
             "'summary-csv' for compact CSV across consumers, "
             "'consumers-json' for the BX-2 registered-consumers block "
             "(monitors + non-monitor consumers like Advennt) as JSON.",
    )
    p.add_argument(
        "--repo",
        help="Override repo root (default: derived from this file).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo = Path(args.repo).resolve() if args.repo else _repo_root()

    if args.all:
        if args.output == "consumers-json":
            print(json.dumps(
                consumer_auditability_report(
                    repo=repo, report_date=args.report_date,
                ),
                indent=2,
            ))
            return 0
        all_rows = audit_all_indexed(repo=repo, report_date=args.report_date)
        consumer_report = consumer_auditability_report(
            repo=repo, report_date=args.report_date,
        )
        if args.output in ("summary", "summary-csv"):
            summaries = [summarise_consumer(c, rows) for c, rows in all_rows.items()]
            if args.output == "summary":
                print(summary_text(summaries))
                print(consumers_text(consumer_report))
            else:
                print(summary_csv(summaries), end="")
                print()
                print(consumers_csv(consumer_report), end="")
        elif args.output == "csv":
            flat = [r for rows in all_rows.values() for r in rows]
            print(rows_to_csv(flat), end="")
            print()
            print(consumers_csv(consumer_report), end="")
        elif args.output == "rows":
            flat = [r for rows in all_rows.values() for r in rows]
            print(rows_to_ndjson(flat))
            for entry in consumer_report:
                print(json.dumps({"_consumer_registration": entry}))
        else:
            # JSON output preserves the historical {slug: rows} top-level
            # shape so existing consumers (e.g. .github/workflows/
            # flow-quality-monitor.yml) iterating `for slug, rows in d.items()`
            # keep working unchanged. Surface the consumer-adapter report via
            # the dedicated `--output consumers-json` mode below instead of
            # mixing it into this dict.
            print(json.dumps(
                {c: [r.as_dict() for r in rows] for c, rows in all_rows.items()},
                indent=2,
            ))
        return 0

    if args.output == "consumers-json":
        print(
            "error: --output consumers-json requires --all",
            file=sys.stderr,
        )
        return 2

    if not args.consumer:
        print("error: --consumer required (or pass --all)", file=sys.stderr)
        return 2

    rows = audit_consumer(
        args.consumer,
        report_date=args.report_date,
        repo=repo,
        module_filter=args.modules,
    )
    if args.output == "json":
        print(rows_to_json(rows))
    elif args.output == "rows":
        print(rows_to_ndjson(rows))
    elif args.output == "csv":
        print(rows_to_csv(rows), end="")
    elif args.output == "summary":
        print(summary_text([summarise_consumer(args.consumer, rows)]))
    elif args.output == "summary-csv":
        print(summary_csv([summarise_consumer(args.consumer, rows)]), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

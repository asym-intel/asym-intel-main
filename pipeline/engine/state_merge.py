"""
state_merge — posture-aware merge of DR output against prior persistent state.

This is the F.5 deliverable of sprint BR-10 (Fleet Collection Runtime). It is
the merge layer between F.3 (collect_base — DR runner) and F.7 (run_collection
— write/archive lifecycle). It is not a writer; it returns an envelope that F.7
then applies.

The merge layer generalises the consolidation doctrine in
`pipeline/monitors/_baseliner/*-baseline-spec.md` and the merge semantics in
`ops/BASELINER-KNOWHOW.md` into one function — `merge()` — that handles every
consumer (Advennt, commons, future) through a single 4-cell decision matrix:

    posture × prior_state:
        baseline  + empty/stub  → whole_file_overwrite  (cell 1)
        baseline  + populated   → diff_manifest         (cell 2 — review-and-merge)
        periodic  + empty/stub  → PeriodicOnEmptyStateError (cell 3 — fail closed)
        periodic  + populated   → diff_manifest         (cell 4)

DiffManifest shape is uniform across cells 2 and 4 (operator verdict V6 — apply
to persistent based on periodic should be the same whatever the valence). Only
the audit metadata and array-keying differ between Advennt and commons.

Two non-obvious doctrine bindings:

  - F.5 NEVER deletes. R4 (operator override at PR review) is enforced by
    emitting OperatorOverride hints; F.7 writes only what the reviewer signs
    off in the PR. This is the single most important guard against silent data
    loss across the merge layer.

  - F.5 NEVER branches on `period`. The cadence is consumer-declared metadata
    (operator verdict V1) and appears only in the audit block. The merge logic
    is identical for every cadence.

This module imports nothing from `weekly_research_base`, `advennt_baseline`, or
any consumer-specific code. It is engine substrate. Per AD-2026-05-05-BR-10 it
lives in `asym-intel-internal` only — engine code is single-source.

Reader-delta: nothing yet. F.5 is engine substrate. The reader-delta milestone
for BR-10 is F.8 (Advennt consumer migration — CN baseline through engine entry
with v2.5 federal-sub-jurisdiction structure live on advennt.io).
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Literal, Mapping, Optional

from pipeline.engine.persistent_state import _identity_match


# ── Module-level constants (V1, V-A, V-B, V-C bindings) ─────────────────────

ALLOWED_PERIODS: frozenset[str] = frozenset(
    {"weekly", "monthly", "on-demand", "quarterly", "yearly"}
)
ALLOWED_CONSUMERS: frozenset[str] = frozenset({"advennt", "commons"})
ALLOWED_POSTURES: frozenset[str] = frozenset({"baseline", "periodic"})
SCHEMA_VERSION: str = "1.0"

_PROVENANCE_FIELDS: frozenset[str] = frozenset(
    {"first_seen", "evidence_id", "source_url", "retrieval_timestamp"}
)


# ── Errors ──────────────────────────────────────────────────────────────────


class StateMergeError(Exception):
    """Base for all F.5 errors."""


class PeriodicOnEmptyStateError(StateMergeError):
    """Cell 3: posture=periodic on empty/stub state — fail closed."""


class UndeclaredArrayError(StateMergeError):
    """DR output contains an array not declared in state_arrays map."""


class InvalidPostureError(StateMergeError):
    """posture not in {'baseline', 'periodic'}."""


class InvalidPeriodError(StateMergeError):
    """period not in ALLOWED_PERIODS."""


# ── Time helper (test-monkeypatchable per BRIEF) ────────────────────────────


def _now_iso() -> str:
    """Module-level helper for the merge timestamp; tests monkeypatch this
    so envelopes are deterministic. Never call datetime.now() inline."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Public entry point ──────────────────────────────────────────────────────


def merge(
    *,
    consumer: Literal["advennt", "commons"],
    posture: Literal["baseline", "periodic"],
    period: str,
    monitor_id: Optional[str],
    jurisdiction_id: Optional[str],
    run_id: str,
    dr_run_id: str,
    prior_state: Mapping[str, Any],
    dr_output: Mapping[str, Any],
    state_arrays: Mapping[str, Mapping[str, Any]],
):
    """Posture-aware merge of DR output against prior persistent state.

    Returns dict envelope with kind="whole_file_overwrite" (cell 1) or
    kind="diff_manifest" (cells 2 + 4). Raises PeriodicOnEmptyStateError on
    cell 3. F.5 NEVER writes to disk and NEVER deletes implicitly.
    """
    _validate_inputs(consumer, posture, period, state_arrays)

    is_empty_or_stub = _is_empty_or_stub(prior_state)
    # _validate_no_undeclared_arrays guards the diff-manifest path (Cell 2/4) only.
    # Cell 1 (baseline + empty/stub prior) is a whole-file overwrite — state_arrays
    # is not consulted, so undeclared arrays are not a merge hazard.
    if not (posture == "baseline" and is_empty_or_stub):
        _validate_no_undeclared_arrays(dr_output, state_arrays)

    audit = _build_audit(
        consumer=consumer, posture=posture, period=period,
        monitor_id=monitor_id, jurisdiction_id=jurisdiction_id,
        run_id=run_id, dr_run_id=dr_run_id,
        prior_state_run_id=None if is_empty_or_stub else _extract_prior_run_id(prior_state),
    )

    if posture == "baseline" and is_empty_or_stub:
        return _emit_whole_file_overwrite(run_id=run_id, dr_output=dr_output, audit=audit)

    if posture == "periodic" and is_empty_or_stub:
        target = jurisdiction_id if jurisdiction_id else monitor_id
        raise PeriodicOnEmptyStateError(
            f"Cannot run periodic posture on empty/stub state: "
            f"consumer={consumer}, monitor_id={monitor_id}, "
            f"jurisdiction_id={jurisdiction_id} (target={target}). "
            f"Run baseline posture first to bootstrap state."
        )

    return _emit_diff_manifest(
        consumer=consumer, monitor_id=monitor_id,
        prior_state=prior_state, dr_output=dr_output,
        state_arrays=state_arrays, audit=audit,
    )


# ── Validation ──────────────────────────────────────────────────────────────


def _validate_inputs(
    consumer: str, posture: str, period: str,
    state_arrays: Mapping[str, Mapping[str, Any]],
) -> None:
    if consumer not in ALLOWED_CONSUMERS:
        raise StateMergeError(
            f"consumer {consumer!r} not in ALLOWED_CONSUMERS {sorted(ALLOWED_CONSUMERS)}"
        )
    if posture not in ALLOWED_POSTURES:
        raise InvalidPostureError(
            f"posture {posture!r} not in ALLOWED_POSTURES {sorted(ALLOWED_POSTURES)}"
        )
    if period not in ALLOWED_PERIODS:
        raise InvalidPeriodError(
            f"period {period!r} not in ALLOWED_PERIODS {sorted(ALLOWED_PERIODS)}"
        )
    if not isinstance(state_arrays, Mapping):
        raise StateMergeError("state_arrays must be a mapping")


def _validate_no_undeclared_arrays(
    dr_output: Mapping[str, Any], state_arrays: Mapping[str, Mapping[str, Any]],
) -> None:
    """Any top-level array key in dr_output must be declared in state_arrays.
    F.5 fails closed on undeclared arrays per V-B + doc 09 guard 2.

    Called only on non-Cell-1 paths (diff-manifest routing: Cell 2 and Cell 4).
    Cell 1 (baseline + empty/stub prior) is a whole-file overwrite; state_arrays
    is not consulted and undeclared arrays are not a merge hazard."""
    declared = {cfg.get("path") for cfg in state_arrays.values() if isinstance(cfg, Mapping)}
    declared.update(state_arrays.keys())
    for key, value in dr_output.items():
        if key.startswith("_"):
            continue
        if isinstance(value, list) and value and isinstance(value[0], Mapping):
            if key not in declared:
                raise UndeclaredArrayError(
                    f"DR output array {key!r} not declared in state_arrays map"
                )


def _is_empty_or_stub(prior_state: Mapping[str, Any]) -> bool:
    """Per verdict C: presence of `_meta.last_baseline_run_id` is the
    canonical signal for 'has this state been baselined?'.
    """
    if not prior_state:
        return True
    meta = prior_state.get("_meta")
    if not isinstance(meta, Mapping):
        return True
    return not meta.get("last_baseline_run_id")


# ── Cell 1: whole-file overwrite ────────────────────────────────────────────


def _emit_whole_file_overwrite(*, run_id: str, dr_output: Mapping[str, Any], audit: dict) -> dict:
    merged_state: dict = copy.deepcopy(dict(dr_output))
    meta = merged_state.get("_meta")
    if not isinstance(meta, dict):
        meta = {}
    meta["last_baseline_run_id"] = run_id
    merged_state["_meta"] = meta
    return {
        "kind": "whole_file_overwrite",
        "schema_version": SCHEMA_VERSION,
        "audit": audit,
        "merged_state": merged_state,
    }


# ── Cells 2 + 4: diff manifest ──────────────────────────────────────────────


def _emit_diff_manifest(
    *, consumer: str, monitor_id: Optional[str],
    prior_state: Mapping[str, Any], dr_output: Mapping[str, Any],
    state_arrays: Mapping[str, Mapping[str, Any]], audit: dict,
) -> dict:
    field_diffs: dict = {}
    array_diffs: dict = {}
    open_findings_diffs: dict = {}
    carry_forward: list = []
    consolidation_log: list = []

    declared_paths = {cfg.get("path") for cfg in state_arrays.values() if isinstance(cfg, Mapping)}
    declared_paths.update(state_arrays.keys())

    _walk_fields(
        prior=prior_state, current=dr_output, prefix="", out=field_diffs,
        declared_array_paths=declared_paths,
        carry_forward=carry_forward, consolidation_log=consolidation_log,
    )

    for logical_name, cfg in state_arrays.items():
        if not isinstance(cfg, Mapping):
            continue
        path = cfg.get("path", logical_name)
        prior_arr = list(_resolve_path(prior_state, path) or [])
        dr_arr = list(_resolve_path(dr_output, path) or [])
        if not prior_arr and not dr_arr:
            continue
        diff = _consolidate_array(
            path=path, scope=cfg.get("scope", "monitor_local"),
            prior=prior_arr, current=dr_arr,
            consolidation_log=consolidation_log, carry_forward=carry_forward,
        )
        if cfg.get("r4_sensitive"):
            key = "_per_jurisdiction" if consumer == "advennt" else (monitor_id or "_unkeyed")
            open_findings_diffs[key] = diff
        else:
            array_diffs[logical_name] = diff

    envelope = {
        "kind": "diff_manifest",
        "schema_version": SCHEMA_VERSION,
        "audit": audit,
        "field_diffs": field_diffs,
        "array_diffs": array_diffs,
        "open_findings_diffs": open_findings_diffs,
        "carry_forward": carry_forward,
        "consolidation_log": consolidation_log,
    }
    # Internal invariant — silent-pass guard (BRIEF + doc 09).
    assert envelope["consolidation_log"], (
        "diff_manifest emitted with empty consolidation_log — "
        "indicates merge logic produced no R1–R5 events"
    )
    return envelope


def _walk_fields(
    *, prior: Any, current: Any, prefix: str, out: dict,
    declared_array_paths: set, carry_forward: list, consolidation_log: list,
) -> None:
    """Walk scalar / object paths, emitting FieldDiff per change."""
    if not isinstance(prior, Mapping) or not isinstance(current, Mapping):
        return
    for key in sorted(set(prior.keys()) | set(current.keys())):
        if key.startswith("_"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if path in declared_array_paths:
            continue
        p_val, c_val = prior.get(key), current.get(key)
        if isinstance(p_val, Mapping) and isinstance(c_val, Mapping):
            _walk_fields(
                prior=p_val, current=c_val, prefix=path, out=out,
                declared_array_paths=declared_array_paths,
                carry_forward=carry_forward, consolidation_log=consolidation_log,
            )
            continue
        if key in current and key not in prior:
            out[path] = {"op": "set", "path": path, "prior": None, "current": c_val,
                         "merged": c_val, "rule": "R1",
                         "rationale": "first surface — DR-authoritative."}
            consolidation_log.append({"rule": "R1", "path": path,
                                      "summary": "DR-authoritative new scalar."})
        elif key in prior and key not in current:
            out[path] = {"op": "carry_forward", "path": path, "prior": p_val,
                         "current": None, "merged": p_val, "rule": "R2",
                         "rationale": "prior carried forward; DR did not surface."}
            carry_forward.append(path)
            consolidation_log.append({"rule": "R2", "path": path,
                                      "summary": "Prior carried forward; DR did not surface."})
        elif p_val != c_val:
            out[path] = {"op": "update", "path": path, "prior": p_val, "current": c_val,
                         "merged": c_val, "rule": "R1",
                         "rationale": "DR-authoritative scalar update."}
            consolidation_log.append({"rule": "R1", "path": path,
                                      "summary": "DR-authoritative scalar update."})


def _resolve_path(state: Any, path: str) -> Any:
    cur: Any = state
    for seg in path.split("."):
        if not isinstance(cur, Mapping) or seg not in cur:
            return None
        cur = cur[seg]
    return cur


def _consolidate_array(
    *, path: str, scope: str, prior: list, current: list,
    consolidation_log: list, carry_forward: list,
) -> dict:
    """Identity-keyed consolidation per R1–R5; emits ArrayDiff."""
    appended: list = []
    amended: list = []
    carried_forward: list = []
    matched_prior_idx: set = set()

    for cur_entry in current:
        match_idx = _find_match(prior, cur_entry, exclude=matched_prior_idx)
        if match_idx is None:
            appended.append(cur_entry)
            consolidation_log.append({"rule": "R1", "path": path,
                                      "summary": "DR appended new entry (no identity match)."})
            continue
        matched_prior_idx.add(match_idx)
        prior_entry = prior[match_idx]
        merged_entry, preserved, per_field_diffs, priority, confidence = (
            _merge_entry_preserving_provenance(prior_entry, cur_entry)
        )
        if merged_entry == prior_entry:
            carried_forward.append(prior_entry)
            consolidation_log.append({"rule": "R5", "path": path,
                                      "summary": "Byte-identical entry carried forward."})
        else:
            amended.append({
                "identity_match_key": _identity_key_label(prior_entry, cur_entry),
                "match_priority": priority, "match_confidence": confidence,
                "prior_entry": prior_entry, "current_entry": cur_entry,
                "field_diffs": per_field_diffs, "merged_entry": merged_entry,
            })
            consolidation_log.append({"rule": "R1", "path": path,
                                      "summary": "Amendment via identity-merge with provenance preservation."})
        if preserved:
            label = _identity_key_label(prior_entry, cur_entry)
            for f in preserved:
                carry_forward.append(f"{path}[{label}].{f}")
            consolidation_log.append({"rule": "R5", "path": path,
                                      "summary": f"Provenance preserved on amendment: {sorted(preserved)}"})

    # R2 carry-forward for prior entries DR didn't surface.
    for idx, prior_entry in enumerate(prior):
        if idx in matched_prior_idx:
            continue
        carried_forward.append(prior_entry)
        consolidation_log.append({"rule": "R2", "path": path,
                                  "summary": "Prior entry carried forward; DR did not surface this run."})

    merged_count = len(appended) + len(amended) + len(carried_forward)
    operator_overrides: list = []
    if len(prior) > 0 and merged_count == 0:
        for prior_entry in prior:
            operator_overrides.append({
                "path": path, "prior_entry": prior_entry,
                "reason": "prior_count > 0 AND merged_count == 0 — array fully emptied",
                "suggested_action": "keep",
            })
        consolidation_log.append({"rule": "R4", "path": path,
                                  "summary": "Array fully emptied; OperatorOverride hints emitted (F.5 NEVER deletes)."})

    return {
        "path": path, "scope": scope,
        "prior_count": len(prior), "current_count": len(current),
        "appended": appended, "amended": amended,
        "carried_forward": carried_forward, "aged_out": [],
        "operator_overrides_required": operator_overrides,
        "merged_count": merged_count,
    }


def _find_match(prior: list, current_entry: Mapping, exclude: set) -> Optional[int]:
    for idx, prior_entry in enumerate(prior):
        if idx in exclude or not isinstance(prior_entry, Mapping):
            continue
        if _identity_match(prior_entry, current_entry):
            return idx
    return None


def _identity_key_label(prior_entry: Mapping, current_entry: Mapping) -> str:
    """Human-readable identity label for the manifest, mirroring the
    persistent_state._detect_strategy priority chain."""
    if prior_entry.get("evidence_id") and current_entry.get("evidence_id"):
        return f"evidence_id:{current_entry.get('evidence_id')}"
    if prior_entry.get("source_url") and current_entry.get("source_url"):
        return "composite:url+date+actor"
    if prior_entry.get("title") and current_entry.get("title"):
        return f"fallback:title:{current_entry.get('title')}"
    return "unknown"


def _merge_entry_preserving_provenance(
    prior_entry: Mapping[str, Any], current_entry: Mapping[str, Any],
):
    """R5: prior provenance preserved verbatim on amendment.
    Returns (merged, preserved_fields, per_field_diffs, priority, confidence).
    """
    merged: dict = dict(current_entry)
    preserved: list[str] = []
    for f in _PROVENANCE_FIELDS:
        if f in prior_entry and prior_entry[f]:
            merged[f] = prior_entry[f]
            preserved.append(f)

    per_field_diffs: dict = {}
    for k in sorted(set(prior_entry.keys()) | set(current_entry.keys())):
        if k in _PROVENANCE_FIELDS:
            continue
        p, c = prior_entry.get(k), current_entry.get(k)
        if p != c:
            per_field_diffs[k] = {
                "op": "update" if k in prior_entry else "set",
                "path": k, "prior": p, "current": c, "merged": c,
                "rule": "R1",
                "rationale": "DR-authoritative for non-provenance fields.",
            }

    if prior_entry.get("evidence_id") and current_entry.get("evidence_id"):
        priority, confidence = 1, "exact"
    elif (prior_entry.get("source_url") and current_entry.get("source_url")
          and prior_entry.get("event_date") == current_entry.get("event_date")
          and prior_entry.get("actor") == current_entry.get("actor")):
        priority, confidence = 4, "composite"
    else:
        priority, confidence = 7, "fallback"

    return merged, preserved, per_field_diffs, priority, confidence


def _extract_prior_run_id(prior_state: Mapping[str, Any]) -> Optional[str]:
    meta = prior_state.get("_meta")
    if not isinstance(meta, Mapping):
        return None
    return meta.get("last_baseline_run_id")


def _build_audit(
    *, consumer: str, posture: str, period: str,
    monitor_id: Optional[str], jurisdiction_id: Optional[str],
    run_id: str, dr_run_id: str, prior_state_run_id: Optional[str],
) -> dict:
    return {
        "consumer": consumer,
        "monitor_id": monitor_id,
        "jurisdiction_id": jurisdiction_id,
        "period": period,
        "posture": posture,
        "run_id": run_id,
        "dr_run_id": dr_run_id,
        "prior_state_run_id": prior_state_run_id,
        "merge_timestamp": _now_iso(),
    }


# ── F.5.1 — Apply-side public helper (BR-10 corrigendum) ────────────────────

def apply_diff_manifest(
    prior_state: Mapping[str, Any], envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply an F.5 merge envelope to prior state, returning new merged state.
    Inverse of `_emit_diff_manifest` / `_emit_whole_file_overwrite`. Pure;
    no I/O; no input mutation; deterministic over (prior_state, envelope).
    Cell 1 (whole_file_overwrite): returns deepcopy of envelope.merged_state.
    Cells 2/4 (diff_manifest): walks field_diffs / array_diffs /
    open_findings_diffs and sets last_baseline_run_id (posture=baseline) or
    last_periodic_run_id (posture=periodic). R4 doctrine: when an array_diff
    carries operator_overrides_required, the prior array is preserved
    verbatim — F.5 NEVER deletes implicitly.
    """
    if not isinstance(envelope, Mapping):
        raise StateMergeError("envelope must be a mapping")
    kind = envelope.get("kind")
    if kind == "whole_file_overwrite":
        if "merged_state" not in envelope:
            raise StateMergeError("envelope missing required key: merged_state")
        return copy.deepcopy(dict(envelope["merged_state"]))
    if kind != "diff_manifest":
        raise StateMergeError(f"envelope kind {kind!r} not recognised")
    for req in ("audit", "field_diffs", "array_diffs", "open_findings_diffs"):
        if req not in envelope:
            raise StateMergeError(f"envelope missing required key: {req}")
    audit = envelope["audit"]
    if not isinstance(audit, Mapping):
        raise StateMergeError("envelope['audit'] must be a mapping")

    working: dict[str, Any] = copy.deepcopy(dict(prior_state))
    # field_diffs: set/update assigns merged value; carry_forward is a no-op.
    for path, fdiff in (envelope.get("field_diffs") or {}).items():
        if isinstance(fdiff, Mapping) and fdiff.get("op") in ("set", "update"):
            _set_path(working, path, fdiff.get("merged"))
    # array_diffs and open_findings_diffs share identical apply semantics.
    for adiff in list((envelope.get("array_diffs") or {}).values()) + \
                 list((envelope.get("open_findings_diffs") or {}).values()):
        _apply_array_diff(working, adiff)
    # _meta: preserve prior keys; set posture-specific run_id.
    meta = working.get("_meta") if isinstance(working.get("_meta"), dict) else {}
    posture = audit.get("posture")
    if posture == "baseline":
        meta["last_baseline_run_id"] = audit.get("run_id")
    elif posture == "periodic":
        meta["last_periodic_run_id"] = audit.get("run_id")
    working["_meta"] = meta
    return working


def _apply_array_diff(working: dict[str, Any], adiff: Mapping[str, Any]) -> None:
    """Replace adiff['path'] with appended+amended.merged_entry+carried_forward,
    OR preserve prior unchanged when R4 override fires (F.5 NEVER deletes)."""
    if not isinstance(adiff, Mapping):
        return
    path = adiff.get("path")
    if not path:
        return
    if adiff.get("operator_overrides_required"):
        return  # R4 — leave prior array untouched
    new_array = (
        list(adiff.get("appended") or [])
        + [a["merged_entry"] for a in (adiff.get("amended") or [])
           if isinstance(a, Mapping) and "merged_entry" in a]
        + list(adiff.get("carried_forward") or [])
    )
    _set_path(working, path, new_array)


def _set_path(state: dict[str, Any], path: str, value: Any) -> None:
    """Walk a dot-segmented path into state and assign value at the leaf.
    Creates intermediate dicts on demand; raises StateMergeError if any
    intermediate parent is a non-Mapping."""
    if not path:
        raise StateMergeError("path must be a non-empty string")
    segments = path.split(".")
    cur: Any = state
    for seg in segments[:-1]:
        nxt = cur.get(seg) if isinstance(cur, dict) else None
        if nxt is None:
            new_child: dict = {}
            cur[seg] = new_child
            cur = new_child
        elif isinstance(nxt, dict):
            cur = nxt
        else:
            raise StateMergeError(
                f"array_diff path {path!r} parent is not a Mapping at segment {seg!r}"
            )
    if not isinstance(cur, dict):
        raise StateMergeError(f"array_diff path {path!r} parent is not a Mapping")
    cur[segments[-1]] = value


# ── Envelope-2 — merge_from_patches() ───────────────────────────────────────
#
# AD-2026-05-15-STATE-COMPUTER (DRAFT, commit 64d3be43) §3.1–§3.4
# Self-ratified by operator directive 2026-05-15 21:07 PDT.
#
# Canonical pipeline review (check_canonical_pipeline_deviation.py):
#   comparator            = pipeline/engine/state_merge.py::merge()
#   deviation_rationale   = parallel entry point translating Interpreter-shape
#                           patches through the same diff_manifest machinery;
#                           F.5 NEVER deletes invariant preserved; no live writes
#
# Translation table (patch.operation → envelope slot) per AD §3.3:
#   create               → field_diffs[target_kb_path] = {op:"set", ...}
#   update (leaf path)   → field_diffs[target_kb_path] = {op:"update", ...}
#   update (bracket path)→ array_diffs[base_path].amended[]
#   append_to_array      → array_diffs[target_kb_path].appended[]
#   append (SCEM alias)  → array_diffs[target_kb_path].appended[]  ← BLOCKER-1 cure
#   replace_array        → array_diffs[target_kb_path].appended[] + replace_semantics:true
#   update_array_entry   → array_diffs[base_path].amended[]
#   carry-forward-verified → no envelope entry (audit trail only)
#
# Disjoint-as-diff contract (THE BAKE-CYCLE-1 CASE):
#   When append_to_array incoming items are disjoint from existing items by
#   key_field, DO NOT raise. Emit array_diff with appended=[incoming items].
#   This is the critical behavioural difference from _merge_array_additive
#   and the reason envelope-2 unblocks eu_legislation_tracker.


import logging as _logging
import re as _re

_LOG = _logging.getLogger(__name__)

# Bracket path detector: "some.path[key_value]" or "some.path[key_value].field"
_BRACKET_RE = _re.compile(r"^(.+)\[([^\]]+)\](.*)$")


def merge_from_patches(
    *,
    prior_state: Mapping[str, Any],
    proposed_patches: list[Mapping[str, Any]],
    arrays_schema: Optional[Mapping[str, Any]],
    posture: Literal["baseline", "periodic"],
    consumer: str,
    slug: str,
    run_id: str,
) -> dict[str, Any]:
    """Envelope-2: translate Interpreter-shape patches into a diff_manifest
    envelope using the F.5 machinery. Inverse: apply_diff_manifest(prior_state,
    envelope) → new_state. Pure; no I/O; no mutation of inputs.

    Translation table (patch.operation → envelope slot) per AD-2026-05-15-STATE-COMPUTER §3.3:
      create               → field_diffs[target_kb_path] = {"op": "set", "merged": new_value}
      update (leaf path)   → field_diffs[target_kb_path] = {"op": "update", "merged": new_value}
      update (bracket path)→ array_diffs[base_path].amended[]
      append_to_array      → array_diffs[target_kb_path].appended[]
      append (SCEM alias)  → array_diffs[target_kb_path].appended[]
      replace_array        → array_diffs[target_kb_path].appended[] + replace_semantics:true
      update_array_entry   → array_diffs[base_path].amended[]
      carry-forward-verified → no envelope entry (audit trail only)

    Disjoint-as-diff contract: when append_to_array incoming items are disjoint
    from existing items by key_field, DO NOT raise DisjointKeySchemeError. Emit
    array_diff.appended=[incoming items] and let validate_diff (future) judge
    business rules. This is the critical behavioural difference from
    _merge_array_additive and the reason envelope-2 unblocks eu_legislation_tracker.

    Note on 'append' alias: the `append` operation is a temporary alias for
    `append_to_array` to unblock SCEM Observer-3 BLOCKER-1 without an Interpreter
    contract change. The Interpreter contract amendment (replacing `append` with
    `append_to_array` in SCEM's output) is a follow-on PR.
    """
    if posture not in ALLOWED_POSTURES:
        raise InvalidPostureError(
            f"posture {posture!r} not in ALLOWED_POSTURES {sorted(ALLOWED_POSTURES)}"
        )

    audit = {
        "consumer": consumer,
        "posture": posture,
        "slug": slug,
        "run_id": run_id,
        "patch_count": len(proposed_patches) if proposed_patches else 0,
        "merge_timestamp": _now_iso(),
        "envelope_version": "envelope-2",
        "ad_ref": "AD-2026-05-15-STATE-COMPUTER",
    }

    field_diffs: dict[str, Any] = {}
    array_diffs: dict[str, Any] = {}
    carry_forward_audit: list[str] = []
    consolidation_log: list[dict] = []

    for patch in (proposed_patches or []):
        if not isinstance(patch, Mapping):
            continue
        _translate_patch(
            patch=patch,
            prior_state=prior_state,
            arrays_schema=arrays_schema,
            slug=slug,
            field_diffs=field_diffs,
            array_diffs=array_diffs,
            carry_forward_audit=carry_forward_audit,
            consolidation_log=consolidation_log,
        )

    return {
        "kind": "diff_manifest",
        "schema_version": SCHEMA_VERSION,
        "audit": audit,
        "field_diffs": field_diffs,
        "array_diffs": array_diffs,
        "open_findings_diffs": {},
        "carry_forward": carry_forward_audit,
        "consolidation_log": consolidation_log,
    }


# ── Patch translation helpers ────────────────────────────────────────────────


def _translate_patch(
    *,
    patch: Mapping[str, Any],
    prior_state: Mapping[str, Any],
    arrays_schema: Optional[Mapping[str, Any]],
    slug: str,
    field_diffs: dict,
    array_diffs: dict,
    carry_forward_audit: list,
    consolidation_log: list,
) -> None:
    """Translate one Interpreter-shape patch into the appropriate diff slot."""
    operation = patch.get("operation", "")
    target_path = patch.get("target_kb_path", "")
    new_value = patch.get("new_value")
    patch_id = patch.get("patch_id", target_path)

    # ── carry-forward-verified: no envelope mutation ─────────────────────────
    if operation == "carry-forward-verified":
        carry_forward_audit.append(target_path)
        consolidation_log.append({
            "rule": "R2",
            "path": target_path,
            "patch_id": patch_id,
            "summary": "carry-forward-verified — no diff slot emitted; audit trail only.",
        })
        return

    # ── create → field_diff set ───────────────────────────────────────────────
    if operation == "create":
        # If new_value is a list-of-objects, route to array_diffs.appended.
        if isinstance(new_value, list):
            _ensure_array_diff(array_diffs, target_path, prior_state, arrays_schema, slug)
            array_diffs[target_path]["appended"].extend(new_value)
            consolidation_log.append({
                "rule": "R1",
                "path": target_path,
                "patch_id": patch_id,
                "summary": f"create (list) → array_diff appended {len(new_value)} items.",
            })
        else:
            field_diffs[target_path] = {
                "op": "set",
                "path": target_path,
                "prior": None,
                "current": new_value,
                "merged": new_value,
                "rule": "R1",
                "patch_id": patch_id,
                "rationale": "create → field_diff set per AD §3.3.",
            }
            consolidation_log.append({
                "rule": "R1",
                "path": target_path,
                "patch_id": patch_id,
                "summary": "create → field_diff set.",
            })
        return

    # ── update: branch on bracket-path vs bare-array vs leaf ─────────────────
    if operation == "update":
        bracket_match = _BRACKET_RE.match(target_path)
        if bracket_match:
            # Bracket path → array_diffs.amended (single-entry update)
            base_path = bracket_match.group(1)
            bracket_key = bracket_match.group(2)
            sub_field = bracket_match.group(3).lstrip(".")
            _ensure_array_diff(array_diffs, base_path, prior_state, arrays_schema, slug)
            key_field = _resolve_key_field_for_path(arrays_schema, base_path)
            amended_entry: dict[str, Any] = {
                "patch_id": patch_id,
                "bracket_key": bracket_key,
                "sub_field": sub_field or None,
                "new_value": new_value,
                "key_field": key_field,
                "rule": "R1",
            }
            if patch.get("operator_overrides_required"):
                amended_entry["operator_overrides_required"] = True
            array_diffs[base_path]["amended"].append(amended_entry)
            consolidation_log.append({
                "rule": "R1",
                "path": base_path,
                "patch_id": patch_id,
                "summary": f"update (bracket-path [{bracket_key}]) → array_diff amended.",
            })
        elif isinstance(new_value, list):
            # Bare array path with list new_value → disjoint-as-diff: route to
            # appended[]. This is the envelope-2 contract for the ESA bake-cycle-1
            # case where `operation=update` targets a whole array (eu_legislation_tracker)
            # with incoming items whose key_field values are disjoint from existing.
            # Do NOT route to amended[] — that is for single-entry bracket-keyed updates.
            items = new_value
            _ensure_array_diff(array_diffs, target_path, prior_state, arrays_schema, slug)
            array_diffs[target_path]["appended"].extend(items)
            consolidation_log.append({
                "rule": "R1",
                "path": target_path,
                "patch_id": patch_id,
                "summary": (
                    f"update (bare array) → array_diff appended {len(items)} items "
                    "(disjoint-as-diff: no DisjointKeySchemeError per envelope-2 contract)."
                ),
            })
        else:
            # Leaf scalar update → field_diff
            prior_val = _resolve_path(prior_state, target_path)
            field_diffs[target_path] = {
                "op": "update",
                "path": target_path,
                "prior": prior_val,
                "current": new_value,
                "merged": new_value,
                "rule": "R1",
                "patch_id": patch_id,
                "rationale": "update leaf → field_diff update per AD §3.3.",
            }
            consolidation_log.append({
                "rule": "R1",
                "path": target_path,
                "patch_id": patch_id,
                "summary": "update leaf → field_diff update.",
            })
        return

    # ── append_to_array + append alias (SCEM BLOCKER-1 unblock) ─────────────
    # 'append' is a temporary alias for 'append_to_array' to unblock SCEM
    # Observer-3 BLOCKER-1. The Interpreter contract amendment (renaming
    # `append` → `append_to_array` in SCEM output) is a follow-on PR.
    if operation in ("append_to_array", "append"):
        items = new_value if isinstance(new_value, list) else [new_value]
        _ensure_array_diff(array_diffs, target_path, prior_state, arrays_schema, slug)
        array_diffs[target_path]["appended"].extend(items)
        op_label = operation if operation == "append_to_array" else "append (alias→append_to_array)"
        consolidation_log.append({
            "rule": "R1",
            "path": target_path,
            "patch_id": patch_id,
            "summary": f"{op_label} → array_diff appended {len(items)} items (disjoint-as-diff: no error).",
        })
        return

    # ── replace_array → appended[] + replace_semantics:true ─────────────────
    if operation == "replace_array":
        items = new_value if isinstance(new_value, list) else [new_value]
        _ensure_array_diff(array_diffs, target_path, prior_state, arrays_schema, slug)
        array_diffs[target_path]["appended"].extend(items)
        array_diffs[target_path]["replace_semantics"] = True
        consolidation_log.append({
            "rule": "R1",
            "path": target_path,
            "patch_id": patch_id,
            "summary": (
                f"replace_array → array_diff appended {len(items)} items "
                "with replace_semantics:true (diff IS whole new array)."
            ),
        })
        return

    # ── update_array_entry → array_diffs[base_path].amended[] ───────────────
    if operation == "update_array_entry":
        bracket_match = _BRACKET_RE.match(target_path)
        if bracket_match:
            base_path = bracket_match.group(1)
            bracket_key = bracket_match.group(2)
            sub_field = bracket_match.group(3).lstrip(".") or None
        else:
            base_path = target_path
            bracket_key = None
            sub_field = None
        _ensure_array_diff(array_diffs, base_path, prior_state, arrays_schema, slug)
        key_field = _resolve_key_field_for_path(arrays_schema, base_path)
        amended_entry = {
            "patch_id": patch_id,
            "bracket_key": bracket_key,
            "sub_field": sub_field,
            "new_value": new_value,
            "key_field": key_field,
            "rule": "R1",
        }
        if patch.get("operator_overrides_required"):
            amended_entry["operator_overrides_required"] = True
        array_diffs[base_path]["amended"].append(amended_entry)
        consolidation_log.append({
            "rule": "R1",
            "path": base_path,
            "patch_id": patch_id,
            "summary": f"update_array_entry → array_diff amended (key={bracket_key}).",
        })
        return

    # ── unknown operation: log WARN, skip ────────────────────────────────────
    _LOG.warning(
        "[merge_from_patches] unknown operation %r on path %r (patch_id=%r) — skipping",
        operation, target_path, patch_id,
    )
    consolidation_log.append({
        "rule": "WARN",
        "path": target_path,
        "patch_id": patch_id,
        "summary": f"Unknown operation {operation!r} — skipped.",
    })


def _ensure_array_diff(
    array_diffs: dict,
    path: str,
    prior_state: Mapping[str, Any],
    arrays_schema: Optional[Mapping[str, Any]],
    slug: str,
) -> None:
    """Initialise an array_diff slot for `path` if not already present.

    Key-field resolution per AD §3.3: call _resolve_key_field_for_path
    (wraps persistent_state._resolve_array_key_field). If returns None,
    log WARN and use legacy probe tuple — matches pre-wire behaviour per
    the TestArraysSchemaFallback contract.
    """
    if path in array_diffs:
        return
    key_field = _resolve_key_field_for_path(arrays_schema, path)
    if key_field is None:
        _LOG.warning(
            "[merge_from_patches] no key_field declared for array path %r (slug=%r)"
            " — falling back to legacy identity-field probe (pre-wire behaviour preserved)",
            path, slug,
        )

    # Disjoint-as-diff: we do NOT call _merge_array_additive here.
    # We accumulate items in appended[] and let apply_diff_manifest handle them.
    # This is the critical behavioural difference from the old Applier path.
    prior_arr = _get_prior_array(prior_state, path)
    array_diffs[path] = {
        "path": path,
        "scope": "monitor_local",
        "key_field": key_field,
        "prior_count": len(prior_arr),
        "prior_items": prior_arr,
        "appended": [],
        "amended": [],
        "carried_forward": list(prior_arr),  # R2: prior items carried forward
        "aged_out": [],
        "operator_overrides_required": [],
        "merged_count": len(prior_arr),  # will be updated by apply_diff_manifest
    }


def _get_prior_array(prior_state: Mapping[str, Any], path: str) -> list:
    """Resolve a (possibly nested) array path in prior_state. Returns []
    on missing or non-list value."""
    val = _resolve_path(prior_state, path)
    return list(val) if isinstance(val, list) else []


def _resolve_key_field_for_path(
    arrays_schema: Optional[Mapping[str, Any]],
    path: str,
) -> Optional[str]:
    """Thin wrapper around persistent_state._resolve_array_key_field so
    merge_from_patches doesn't import from persistent_state at module level
    (engine substrate isolation). Reimplements the same logic locally."""
    if not isinstance(arrays_schema, Mapping):
        return None
    # Accept either full schema (with 'arrays' key) or inner arrays mapping.
    arrays = arrays_schema.get("arrays") if "arrays" in arrays_schema else arrays_schema
    if not isinstance(arrays, Mapping):
        return None
    entry = arrays.get(path)
    if not isinstance(entry, Mapping):
        return None
    kf = entry.get("key_field")
    return kf if isinstance(kf, str) and kf else None

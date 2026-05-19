#!/usr/bin/env python3
"""
shadow_apply_monitor.py — generalised shadow harness for any commons monitor.

Runs merge_from_patches + apply_diff_manifest (envelope-2) on existing bake
data for a given monitor. NO writes. NO new collections.

Authority: AD-2026-05-15-STATE-COMPUTER §4 acceptance gate (a)
Fleet session: fleet-2026-05-15-78863913
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from typing import Any

_WORKSPACE = pathlib.Path(__file__).resolve().parent
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from pipeline.engine.state_merge import apply_diff_manifest, merge_from_patches

LOG = logging.getLogger("shadow_apply_monitor")
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    level=logging.INFO,
)


def _load_json(path: pathlib.Path, label: str) -> dict:
    if not path.is_file():
        LOG.error("[FATAL] %s not found at %s", label, path)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    LOG.info("Loaded %s from %s (%d top-level keys)", label, path, len(data) if isinstance(data, dict) else -1)
    return data


def _find_patches(interpret_doc: dict, compose_doc: dict) -> tuple[list, str]:
    """Find proposed_patches. Prefer interpret, fallback to compose."""
    if interpret_doc and "proposed_patches" in interpret_doc:
        patches = interpret_doc["proposed_patches"]
        LOG.info("Found %d patches in interpret-latest.json", len(patches))
        return patches, "interpret-latest.json[proposed_patches]"
    if compose_doc and "proposed_patches" in compose_doc:
        patches = compose_doc["proposed_patches"]
        LOG.info("Found %d patches in compose-latest.json (fallback)", len(patches))
        return patches, "compose-latest.json[proposed_patches] (fallback)"
    LOG.warning("No proposed_patches found in either document. Shadow runs with empty list.")
    return [], "none"


def _count_arrays(state: dict, schema_arrays: dict) -> dict[str, int]:
    """Count items in each tracked array in a state document."""
    counts: dict[str, int] = {}
    for array_path in schema_arrays:
        # Handle nested paths like "cross_monitor_flags.flags"
        parts = array_path.split(".")
        val = state
        try:
            for p in parts:
                if isinstance(val, dict):
                    val = val.get(p)
                else:
                    val = None
                    break
            counts[array_path] = len(val) if isinstance(val, list) else -1
        except Exception:
            counts[array_path] = -1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-monitor shadow harness — envelope-2")
    parser.add_argument("--abbr", required=True, help="Monitor abbreviation e.g. GMM, SCEM")
    parser.add_argument("--slug", required=True, help="Monitor slug e.g. macro-monitor")
    parser.add_argument("--persistent-state", required=True, type=pathlib.Path)
    parser.add_argument("--interpret", required=True, type=pathlib.Path)
    parser.add_argument("--compose", required=True, type=pathlib.Path)
    parser.add_argument("--apply-latest", required=True, type=pathlib.Path, dest="apply_latest")
    parser.add_argument("--arrays-schema", required=True, type=pathlib.Path, dest="arrays_schema")
    parser.add_argument("--out", default=None, type=pathlib.Path)
    args = parser.parse_args()

    abbr_lower = args.abbr.lower()
    if args.out is None:
        args.out = pathlib.Path(f"/tmp/shadow-{abbr_lower}-cycle1-report.json")

    # ── 1. Load inputs ───────────────────────────────────────────────────────
    prior_state = _load_json(args.persistent_state, "persistent-state.json")
    interpret_doc = _load_json(args.interpret, "interpret-latest.json") if args.interpret.is_file() else {}
    compose_doc = _load_json(args.compose, "compose-latest.json") if args.compose.is_file() else {}
    apply_latest = _load_json(args.apply_latest, "apply-latest.json")
    arrays_schema = _load_json(args.arrays_schema, "persistent-state-schema.json")

    # ── 2. Extract arrays block from schema ──────────────────────────────────
    schema_arrays = arrays_schema.get("arrays", {})
    LOG.info("Schema declares %d tracked arrays: %s", len(schema_arrays), list(schema_arrays.keys()))

    # ── 3. Find proposed_patches ─────────────────────────────────────────────
    proposed_patches, patch_source = _find_patches(interpret_doc, compose_doc)

    if not proposed_patches:
        LOG.warning("No proposed_patches — recording SKIP")
        report = {
            "shadow_cycle": f"{abbr_lower}-2026-05-15",
            "monitor_abbr": args.abbr,
            "monitor_slug": args.slug,
            "verdict": "SKIP",
            "skip_reason": "no proposed_patches found in interpret-latest or compose-latest",
            "patch_source": patch_source,
            "patch_count": 0,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\nSKIP: {args.abbr} — no proposed_patches\n")
        return

    # ── 4. Pre-shadow array counts (F.5 baseline) ───────────────────────────
    prior_array_counts = _count_arrays(prior_state, schema_arrays)
    LOG.info("Prior array counts: %s", prior_array_counts)

    # ── 5. Call merge_from_patches ───────────────────────────────────────────
    LOG.info("Running merge_from_patches (envelope-2) for %s …", args.abbr)
    try:
        envelope = merge_from_patches(
            prior_state=prior_state,
            proposed_patches=proposed_patches,
            arrays_schema=arrays_schema,
            posture="periodic",
            consumer="commons",
            slug=args.slug,
            run_id=f"shadow-{abbr_lower}-bake-cycle-1",
        )
    except Exception as e:
        LOG.error("merge_from_patches raised: %s", e)
        report = {
            "shadow_cycle": f"{abbr_lower}-2026-05-15",
            "monitor_abbr": args.abbr,
            "monitor_slug": args.slug,
            "verdict": "ERROR",
            "error": str(e),
            "patch_source": patch_source,
            "patch_count": len(proposed_patches),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\nERROR: {args.abbr} — merge_from_patches: {e}\n")
        return

    LOG.info("merge_from_patches complete. kind=%s", envelope.get("kind"))

    # ── 6. Apply diff manifest ───────────────────────────────────────────────
    LOG.info("Running apply_diff_manifest …")
    try:
        shadow_target_state = apply_diff_manifest(prior_state, envelope)
    except Exception as e:
        LOG.error("apply_diff_manifest raised: %s", e)
        report = {
            "shadow_cycle": f"{abbr_lower}-2026-05-15",
            "monitor_abbr": args.abbr,
            "monitor_slug": args.slug,
            "verdict": "ERROR",
            "error": f"apply_diff_manifest: {e}",
            "patch_source": patch_source,
            "patch_count": len(proposed_patches),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\nERROR: {args.abbr} — apply_diff_manifest: {e}\n")
        return

    LOG.info("apply_diff_manifest complete.")

    # ── 7. Post-shadow array counts and F.5 check ───────────────────────────
    shadow_array_counts = _count_arrays(shadow_target_state, schema_arrays)
    LOG.info("Shadow array counts: %s", shadow_array_counts)

    f5_violations: list[dict] = []
    for arr_path, prior_count in prior_array_counts.items():
        shadow_count = shadow_array_counts.get(arr_path, -1)
        if prior_count >= 0 and shadow_count >= 0 and shadow_count < prior_count:
            f5_violations.append({
                "array": arr_path,
                "prior_count": prior_count,
                "shadow_count": shadow_count,
                "shrinkage": prior_count - shadow_count,
            })

    # ── 8. Envelope summary ──────────────────────────────────────────────────
    field_diffs = envelope.get("field_diffs") or {}
    array_diffs = envelope.get("array_diffs") or {}
    
    shadow_array_appends = sum(
        len(ad.get("appended") or [])
        for ad in array_diffs.values()
        if isinstance(ad, dict)
    )
    shadow_field_updates = sum(
        1 for fd in field_diffs.values()
        if isinstance(fd, dict) and fd.get("op") in ("set", "update")
    )
    shadow_would_update = shadow_array_appends > 0 or shadow_field_updates > 0

    # Old applier verdict
    old_ps_updated = apply_latest.get("persistent_state_updated", False)
    old_applier_flags = apply_latest.get("_meta", {}).get("applier_flags", [])
    old_failed = any("apply_failed" in str(f) for f in old_applier_flags)

    # ── 9. PASS/FAIL verdict ─────────────────────────────────────────────────
    if shadow_would_update and not f5_violations:
        verdict = "PASS"
    elif f5_violations:
        verdict = "FAIL_F5_VIOLATION"
    elif not shadow_would_update:
        verdict = "FAIL_NO_UPDATE"
    else:
        verdict = "FAIL_UNKNOWN"

    # ── 10. Build full report ────────────────────────────────────────────────
    report: dict[str, Any] = {
        "shadow_cycle": f"{abbr_lower}-2026-05-15",
        "monitor_abbr": args.abbr,
        "monitor_slug": args.slug,
        "verdict": verdict,
        "patch_source": patch_source,
        "patch_count": len(proposed_patches),
        "old_applier_summary": {
            "persistent_state_updated": old_ps_updated,
            "applier_flags": old_applier_flags,
            "old_applier_failed_disjoint_key": old_failed,
        },
        "envelope_summary": {
            "kind": envelope.get("kind"),
            "field_diff_count": len(field_diffs),
            "array_diff_count": len(array_diffs),
            "array_diff_paths": list(array_diffs.keys()),
            "operator_overrides_required_count": sum(
                len(ad.get("operator_overrides_required") or [])
                for ad in array_diffs.values()
                if isinstance(ad, dict)
            ),
        },
        "shadow_metrics": {
            "shadow_would_update_state": shadow_would_update,
            "shadow_array_appends": shadow_array_appends,
            "shadow_field_updates": shadow_field_updates,
        },
        "f5_check": {
            "f5_invariant_holds": len(f5_violations) == 0,
            "violations": f5_violations,
        },
        "array_counts": {
            "prior": prior_array_counts,
            "shadow": shadow_array_counts,
        },
        "pass_criteria": {
            "shadow_would_update_state": shadow_would_update,
            "no_array_shrinkage": len(f5_violations) == 0,
            "patch_count_nonzero": len(proposed_patches) > 0,
        },
    }

    # ── 11. Write report ─────────────────────────────────────────────────────
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    LOG.info("Shadow report written to %s", args.out)

    print(f"\n{'='*60}")
    print(f"SHADOW HARNESS REPORT — {args.abbr} {report['shadow_cycle']}")
    print(f"{'='*60}")
    print(f"Verdict:                  {verdict}")
    print(f"Patch source:             {patch_source}")
    print(f"Patch count:              {len(proposed_patches)}")
    print(f"Old applier updated:      {old_ps_updated}")
    print(f"Old applier failed:       {old_failed}")
    print(f"Shadow would update:      {shadow_would_update}")
    print(f"Shadow array appends:     {shadow_array_appends}")
    print(f"Shadow field updates:     {shadow_field_updates}")
    print(f"F.5 violations:           {f5_violations}")
    print(f"Prior array counts:       {prior_array_counts}")
    print(f"Shadow array counts:      {shadow_array_counts}")
    print(f"Report:                   {args.out}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

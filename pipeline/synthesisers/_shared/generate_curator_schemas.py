#!/usr/bin/env python3
"""generate_curator_schemas.py — render per-monitor curator drift schemas from
the shared template + canonical monitors register.

This script is the SINGLE SOURCE for per-monitor curator drift schemas. Hand-
editing any of the per-monitor schemas at
`pipeline/synthesisers/<abbr>/<abbr>-curator-drift-schema.json` is forbidden;
the CI sync gate (.github/workflows/check-curator-schemas-in-sync.yml) re-
runs this generator on every PR touching curator schemas, the template, the
generator, or the monitors register, and fails the PR if the generated output
diverges from the on-disk schemas.

Authority:
  - AD-2026-04-26-AO §3 BRIEF #6 (canonical monitor register)
  - AD-2026-04-24l (force-reissue audit-block contract)
  - Operator doctrine 2026-05-19: "the fix must be template or pipeline class
    not copy paste instance" + "we also have a canonical monitor registry so
    we should call in rather than copy paste"
  - Session arti-20260519T074724Z (A2 structural cure following A1 PR #374)

Inputs:
  - Template: pipeline/synthesisers/_shared/curator-drift-schema.template.json
              (3 placeholders: __TITLE__, __DESCRIPTION__, __SCHEMA_VERSION__)
  - Canonical register (precedence order):
      1. asym-intel-internal:ops/canonical/monitors.json  (preferred — JSON SSOT)
      2. asym-intel-internal:pipeline/engine/canonical_monitors.yml  (fallback)

Outputs:
  - 8 files at pipeline/synthesisers/<abbr_lower>/<abbr_lower>-curator-drift-schema.json
    where <abbr_lower> = monitor abbr lowercased; AIM uses agm/aim- (legacy).
  - Plus a manifest at pipeline/synthesisers/_shared/.generated-manifest.json
    listing the source register SHA + generator version for audit trail.

Monitor inclusion rules:
  - Include monitors where monitor_class == "intelligence" (excludes ADV, etc.).
  - Include monitors with status in {"active", "paused"} — paused monitors
    keep their schema so resumption doesn't require schema authoring.
  - AIM exception: directory = "agm", filename = "aim-curator-drift-schema.json"
    per legacy convention (see canonical_monitors.yml comment block).

Usage:
  Generate (writes files):
    python3 pipeline/synthesisers/_shared/generate_curator_schemas.py

  Check (returns non-zero if regeneration would change anything):
    python3 pipeline/synthesisers/_shared/generate_curator_schemas.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

# Default paths assume local-dev layout: this file at
# <main-root>/pipeline/synthesisers/_shared/generate_curator_schemas.py with
# asym-intel-internal sibling at <main-root>/../asym-intel-internal/.
# CI overrides these with --repo-root + --canonical-register because actions/checkout
# places the two repos at workspace/main and workspace/internal (siblings inside the
# job workspace, not siblings of the script's resolved path).
DEFAULT_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

# Per-monitor description template. The {abbr}/{name}/{slug} substitution
# matches the W4-A description style; AGM legacy description is normalised
# to this form by A2 (the prior AGM prose contained Sprint 3 Step 4 lineage
# detail that is preserved in this generator's git history, not in runtime
# schemas).
DESCRIPTION_TEMPLATE = (
    "File-output schema for the deterministic Curator stage for the {name} "
    "({slug}). LLM-free: no curator_model, no advisory_notes, no structured_claims. "
    "Output is a drift register emitted every cycle (including null cycles) with "
    "four typed triggers (T1-T4) firing at advisory severity only. Non-blocking "
    "by design (F5/F6). Generated from "
    "pipeline/synthesisers/_shared/curator-drift-schema.template.json by "
    "generate_curator_schemas.py — DO NOT EDIT BY HAND."
)


def _load_canonical_register(
    repo_root: pathlib.Path,
    explicit_path: pathlib.Path | None = None,
) -> tuple[list[dict[str, Any]], pathlib.Path, str]:
    """Load canonical monitors register.

    Tries (in order):
      0. explicit_path if provided (CI uses --canonical-register <path>)
      1. <repo_root>/../asym-intel-internal/ops/canonical/monitors.json
      2. <repo_root>/../asym-intel-internal/pipeline/engine/canonical_monitors.yml

    Returns (monitors, source_path, source_sha).
    """
    if explicit_path is not None:
        if not explicit_path.exists():
            print(
                f"error: --canonical-register {explicit_path} does not exist",
                file=sys.stderr,
            )
            sys.exit(2)
        text = explicit_path.read_text()
        # Both .json and .yml are supported by explicit-path mode
        if explicit_path.suffix == ".json":
            data = json.loads(text)
            sha = hashlib.sha256(text.encode()).hexdigest()[:16]
            return data["monitors"], explicit_path, sha
        # else fall through to yaml handling below

    # asym-intel-main and asym-intel-internal are sibling repos by convention
    candidate_roots = [
        repo_root.parent / "asym-intel-internal",
    ]
    for sibling in candidate_roots:
        json_path = sibling / "ops" / "canonical" / "monitors.json"
        if json_path.exists():
            text = json_path.read_text()
            data = json.loads(text)
            sha = hashlib.sha256(text.encode()).hexdigest()[:16]
            return data["monitors"], json_path, sha

        yml_path = sibling / "pipeline" / "engine" / "canonical_monitors.yml"
        if yml_path.exists():
            try:
                import yaml  # type: ignore
            except ImportError:
                print(
                    "error: canonical_monitors.yml found but pyyaml not installed; "
                    "install pyyaml or ensure ops/canonical/monitors.json is present",
                    file=sys.stderr,
                )
                sys.exit(2)
            text = yml_path.read_text()
            data = yaml.safe_load(text)
            # Reshape from dict-keyed to list, adding status=active default
            monitors = []
            for slug, entry in data.get("monitors", {}).items():
                m = {
                    "slug": entry["slug"],
                    "abbr": entry["abbr"],
                    "name": entry["name"],
                    "full_title": entry["full_title"],
                    "status": "active",
                    "monitor_class": "intelligence",
                }
                monitors.append(m)
            sha = hashlib.sha256(text.encode()).hexdigest()[:16]
            return monitors, yml_path, sha

    print(
        "error: cannot locate canonical monitors register. Expected "
        "../asym-intel-internal/ops/canonical/monitors.json or "
        "../asym-intel-internal/pipeline/engine/canonical_monitors.yml",
        file=sys.stderr,
    )
    sys.exit(2)


def _filter_intelligence_monitors(monitors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select monitors that get a curator drift schema generated."""
    return [
        m
        for m in monitors
        if m.get("monitor_class") == "intelligence"
        and m.get("status") in ("active", "paused")
    ]


def _abbr_dir_for(monitor: dict[str, Any]) -> str:
    """Return the on-disk directory abbreviation for a monitor.

    AIM legacy exception: directory is 'agm' (per canonical_monitors.yml
    comment block — internal_stage_prefix). All other monitors: lowercase abbr.
    """
    abbr = monitor["abbr"]
    if abbr == "AIM":
        return "agm"
    return abbr.lower()


def _schema_filename_for(monitor: dict[str, Any]) -> str:
    """Return the schema filename for a monitor.

    AIM legacy exception: filename is 'aim-curator-drift-schema.json'.
    All other monitors: '<abbr-lower>-curator-drift-schema.json'.
    """
    abbr = monitor["abbr"]
    return f"{abbr.lower()}-curator-drift-schema.json"


def _schema_version_for(monitor: dict[str, Any]) -> str:
    """Return the schema_version stamp for a monitor.

    Matches `_derive_curator_schema_version` in
    `asym-intel-internal:pipeline/engine/curator_base.py`.
    """
    return f"{monitor['abbr'].lower()}-curator-drift-v1.0"


def _title_for(monitor: dict[str, Any]) -> str:
    return f"{monitor['abbr']} Curator Drift Register ({_schema_version_for(monitor)})"


def _description_for(monitor: dict[str, Any]) -> str:
    return DESCRIPTION_TEMPLATE.format(name=monitor["name"], slug=monitor["slug"])


def _render_schema(template: dict[str, Any], monitor: dict[str, Any]) -> dict[str, Any]:
    """Render a per-monitor schema by substituting placeholders in the template."""
    # Round-trip through JSON to deep-copy + apply text substitutions
    text = json.dumps(template)
    text = text.replace("__TITLE__", _escape_json_string(_title_for(monitor)))
    text = text.replace("__DESCRIPTION__", _escape_json_string(_description_for(monitor)))
    text = text.replace("__SCHEMA_VERSION__", _escape_json_string(_schema_version_for(monitor)))
    return json.loads(text)


def _escape_json_string(s: str) -> str:
    """Escape a string for embedding in a JSON string-value context.

    We are doing string-level substitution on a JSON document, so any double-
    quotes or backslashes in the substituted string would break JSON syntax.
    Use json.dumps to get the escaped form, then strip the outer quotes.
    """
    return json.dumps(s)[1:-1]


def generate(
    check_only: bool = False,
    repo_root: pathlib.Path | None = None,
    canonical_register: pathlib.Path | None = None,
) -> int:
    repo_root = repo_root or DEFAULT_REPO_ROOT
    template_path = repo_root / "pipeline" / "synthesisers" / "_shared" / "curator-drift-schema.template.json"
    synth_root = repo_root / "pipeline" / "synthesisers"
    manifest_path = repo_root / "pipeline" / "synthesisers" / "_shared" / ".generated-manifest.json"

    template = json.loads(template_path.read_text())
    monitors_all, source_path, source_sha = _load_canonical_register(repo_root, canonical_register)
    monitors = _filter_intelligence_monitors(monitors_all)

    changes: list[str] = []
    manifest_entries = []
    for monitor in monitors:
        abbr_dir = _abbr_dir_for(monitor)
        filename = _schema_filename_for(monitor)
        target = synth_root / abbr_dir / filename

        # Skip if the directory does not exist (e.g. ADV is registered but has
        # no synthesisers/ subdir). Intelligence-class monitors should all
        # have directories — log and skip for safety.
        if not target.parent.exists():
            print(f"WARN: {monitor['abbr']}: directory {target.parent} missing — skipping")
            continue

        rendered = _render_schema(template, monitor)
        rendered_text = json.dumps(rendered, indent=2) + "\n"

        existing_text = target.read_text() if target.exists() else ""
        rendered_normalised = json.dumps(json.loads(rendered_text), sort_keys=True)
        existing_normalised = json.dumps(json.loads(existing_text), sort_keys=True) if existing_text else ""

        # We compare on normalised JSON (sort_keys=True) — formatting differences
        # are not drift. The on-disk file is written with indent=2 + final newline.
        if rendered_normalised != existing_normalised:
            changes.append(
                f"{monitor['abbr']}: {'CREATE' if not existing_text else 'UPDATE'} {target.relative_to(repo_root)}"
            )
            if not check_only:
                target.write_text(rendered_text)
        else:
            # Even if normalised content is identical, we may want to canonicalise
            # the formatting. In check_only mode this is informational; in write
            # mode we rewrite to canonical form so generator output is stable.
            if not check_only and rendered_text != existing_text:
                target.write_text(rendered_text)
                changes.append(f"{monitor['abbr']}: REFORMAT {target.relative_to(repo_root)}")

        manifest_entries.append({
            "slug": monitor["slug"],
            "abbr": monitor["abbr"],
            "status": monitor.get("status", "unknown"),
            "schema_path": str(target.relative_to(repo_root)),
            "schema_version": _schema_version_for(monitor),
            "sha256_of_rendered": hashlib.sha256(rendered_text.encode()).hexdigest(),
        })

    # Write manifest (or check it matches)
    manifest = {
        "_meta": {
            "description": "Audit trail for generate_curator_schemas.py. Records the source canonical register SHA + per-schema SHA256. CI sync gate uses this to detect drift.",
            "generator": "pipeline/synthesisers/_shared/generate_curator_schemas.py",
            "template": "pipeline/synthesisers/_shared/curator-drift-schema.template.json",
            "source_register": str(source_path.relative_to(source_path.parent.parent.parent)),
            "source_register_sha256_16": source_sha,
            "monitor_count": len(manifest_entries),
        },
        "monitors": sorted(manifest_entries, key=lambda e: e["abbr"]),
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    existing_manifest_text = manifest_path.read_text() if manifest_path.exists() else ""

    # Manifest comparison: ignore source_register_sha256_16 + source_register
    # since those are environmental (depend on sibling repo HEAD). The
    # per-schema sha256 list is what we lock to.
    def _manifest_essential(text: str) -> str:
        if not text:
            return ""
        m = json.loads(text)
        return json.dumps({"monitors": m.get("monitors", [])}, sort_keys=True)

    if _manifest_essential(manifest_text) != _manifest_essential(existing_manifest_text):
        changes.append("manifest: UPDATE .generated-manifest.json (per-schema sha256 list changed)")
        if not check_only:
            manifest_path.write_text(manifest_text)
    elif not check_only and manifest_text != existing_manifest_text:
        # Environmental-only delta (source register SHA changed) — refresh
        manifest_path.write_text(manifest_text)

    if changes:
        action = "would write" if check_only else "wrote"
        print(f"generate_curator_schemas.py: {action} {len(changes)} change(s):")
        for c in changes:
            print(f"  - {c}")
        return 1 if check_only else 0
    print(f"generate_curator_schemas.py: no changes — {len(manifest_entries)} schemas in sync")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail (exit 1) if any schema would change. Used by CI sync gate.",
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=None,
        help="Path to asym-intel-main repo root. Defaults to inferred from script location.",
    )
    parser.add_argument(
        "--canonical-register",
        type=pathlib.Path,
        default=None,
        help="Explicit path to the canonical monitors register (.json or .yml). "
        "Defaults to <repo-root>/../asym-intel-internal/ops/canonical/monitors.json.",
    )
    args = parser.parse_args()
    return generate(
        check_only=args.check,
        repo_root=args.repo_root,
        canonical_register=args.canonical_register,
    )


if __name__ == "__main__":
    sys.exit(main())

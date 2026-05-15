#!/usr/bin/env python3
"""tools/check_persistent_state_schema_coverage.py — Sprint-5 Phase 2 gate (E10 cure).

Authority: asym-intel-internal:docs/sprints/2026-05-15-sprint-5-persistent-state-key-lock/BRIEF.md
(committed at SHA cf14eabd), §4 Phase 2 task 3.

Walks every monitor under `pipeline/synthesisers/<slug>/` (commons monitors) and
`pipeline/monitors/<slug>/` (advennt + non-synthesiser monitors). For each:

  1. Locates `persistent-state-schema.json`. If missing → FATAL (or WARN if bootstrap).
  2. Validates the schema against the meta-schema at
     `asym-intel-internal:policy/contracts/persistent-state-schema-meta-schema.json`
     (path supplied via --meta-schema or auto-discovered in sibling-repo layout).
  3. Walks every array property in the monitor's `interpreter-schema.json`
     (`pipeline/monitors/<slug>/interpreter-schema.json`) whose item-shape carries
     a key-shaped field (one of `id`, `country`, `code`, `case_id`, `actor_id`,
     `module_id`, `iso`, `jurisdiction`). For each such array, asserts the array
     is declared in the persistent-state-schema's `arrays` block (by dotted path
     prefix match — the persistent-state-schema may carry a coarser path than
     interpreter-schema's nested `properties.x.properties.y` form).

Posture-WARN bootstrap exemption: when the env var `SPRINT_5_PHASE_2_BOOTSTRAP=1`
is set, all FAILs degrade to WARNs and the gate exits 0. This is the Phase 2
self-trigger exemption per gate-calibration primitive #2 (the Phase 2 PR itself
inevitably triggers the gate it ships, since seven of the eight commons monitors
have no persistent-state-schema.json yet — that is Phase 3 work). Once Phase 3
lands all schemas, remove the env var from the workflow.

Usage:
    python3 tools/check_persistent_state_schema_coverage.py [--monitor <slug>] \
        [--meta-schema <path>] [--repo-root <path>]

Exit codes:
  0 — all monitors pass (or bootstrap mode + WARN-only)
  1 — at least one FATAL gap (missing schema, invalid schema, undeclared array)
  2 — usage error / meta-schema cannot be located

Key-field heuristic — array items are considered "key-shaped" if `properties`
contains any field in KEY_SHAPED_FIELDS. This intentionally over-flags; a false
positive is one extra `arrays.<path>` declaration; a false negative is silent
key-scheme drift (the E10 pathology).

Linked: bugs.json::E10-PERSISTENT-STATE-KEY-SCHEME-DRIFT
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterator

try:
    import jsonschema
except ImportError:
    print("FATAL: jsonschema library not installed. `pip install jsonschema`.", file=sys.stderr)
    sys.exit(2)


KEY_SHAPED_FIELDS = frozenset({
    "id", "country", "code", "case_id", "actor_id",
    "module_id", "iso", "jurisdiction",
})

BOOTSTRAP_ENV = "SPRINT_5_PHASE_2_BOOTSTRAP"


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upwards to find the asym-intel-main repo root."""
    base = (start or Path.cwd()).resolve()
    for parent in [base] + list(base.parents):
        if (parent / "pipeline" / "monitors").exists() and (parent / "tools").exists():
            return parent
    return Path(__file__).resolve().parent.parent


def find_meta_schema(repo_root: Path, override: str | None) -> Path:
    """Locate the meta-schema. Search order:
      1. --meta-schema CLI arg
      2. $PS_SCHEMA_META env var
      3. Sibling repo: ../asym-intel-internal/policy/contracts/persistent-state-schema-meta-schema.json
      4. Sibling repo via CI checkout: ../internal/policy/contracts/persistent-state-schema-meta-schema.json
    """
    if override:
        p = Path(override).resolve()
        if not p.exists():
            print(f"FATAL: --meta-schema path does not exist: {p}", file=sys.stderr)
            sys.exit(2)
        return p

    env = os.environ.get("PS_SCHEMA_META", "").strip()
    if env:
        p = Path(env).resolve()
        if not p.exists():
            print(f"FATAL: PS_SCHEMA_META path does not exist: {p}", file=sys.stderr)
            sys.exit(2)
        return p

    candidates = [
        repo_root.parent / "asym-intel-internal" / "policy" / "contracts" / "persistent-state-schema-meta-schema.json",
        repo_root.parent / "internal" / "policy" / "contracts" / "persistent-state-schema-meta-schema.json",
    ]
    for c in candidates:
        if c.exists():
            return c

    print(
        "FATAL: could not locate persistent-state-schema-meta-schema.json. "
        "Pass --meta-schema, set PS_SCHEMA_META, or check out asym-intel-internal "
        f"as a sibling. Tried: {[str(c) for c in candidates]}",
        file=sys.stderr,
    )
    sys.exit(2)


def discover_monitor_dirs(repo_root: Path) -> list[tuple[str, Path, Path]]:
    """Return list of (slug, monitor_dir, persistent_state_schema_candidate_path).

    Walks both pipeline/synthesisers/<slug>/ (commons monitors) and
    pipeline/monitors/<slug>/ (advennt + monitor-config). For commons monitors
    that have both (interpreter-schema in pipeline/monitors/<slug>/, persistent-
    state-schema in pipeline/synthesisers/<slug>/), the gate inspects both
    surfaces but reports under the synthesiser-slug (which is also the
    canonical monitor-slug via monitor-config.yml mapping).
    """
    out: list[tuple[str, Path, Path]] = []
    seen: set[str] = set()

    # 1) Synthesisers — canonical home for AGM, ERM, ESA, FCW, FIM, GMM, SCEM, WDM persistent-state schemas
    synth_root = repo_root / "pipeline" / "synthesisers"
    if synth_root.is_dir():
        for entry in sorted(synth_root.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            if entry.name in {"cross-monitor"}:  # not a monitor
                continue
            # Heuristic: synthesiser dir name == short slug (agm, esa, ...)
            slug = entry.name
            if slug in seen:
                continue
            schema_path = entry / "persistent-state-schema.json"
            out.append((slug, entry, schema_path))
            seen.add(slug)

    # 2) Monitors — advennt and any monitor that hasn't placed schema under synthesisers/
    monitors_root = repo_root / "pipeline" / "monitors"
    if monitors_root.is_dir():
        # Map short-slug → long-slug. We only add a monitor row if its short-slug
        # equivalent isn't already in `seen` (i.e. the synthesiser dir owns it).
        long_to_short = {
            "ai-governance": "agm",
            "european-strategic-autonomy": "esa",
            "democratic-integrity": "wdm",
            "fimi-cognitive-warfare": "fcw",
            "macro-monitor": "gmm",
            "environmental-risks": "erm",
            "conflict-escalation": "scem",
            "financial-integrity": "fim",
        }
        for entry in sorted(monitors_root.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            long_slug = entry.name
            short_slug = long_to_short.get(long_slug, long_slug)
            if short_slug in seen:
                continue
            schema_path = entry / "persistent-state-schema.json"
            out.append((long_slug, entry, schema_path))
            seen.add(short_slug)

    return out


def find_interpreter_schema(repo_root: Path, slug: str) -> Path | None:
    """Locate the interpreter-schema.json for a monitor. Maps short→long slug."""
    short_to_long = {
        "agm": "ai-governance",
        "esa": "european-strategic-autonomy",
        "wdm": "democratic-integrity",
        "fcw": "fimi-cognitive-warfare",
        "gmm": "macro-monitor",
        "erm": "environmental-risks",
        "scem": "conflict-escalation",
        "fim": "financial-integrity",
    }
    long_slug = short_to_long.get(slug, slug)
    p = repo_root / "pipeline" / "monitors" / long_slug / "interpreter-schema.json"
    return p if p.exists() else None


def iter_key_shaped_arrays(schema: Any, path: str = "") -> Iterator[tuple[str, list[str]]]:
    """Yield (dotted_path, key_field_candidates) for every array in `schema`
    whose items declare a key-shaped field. dotted_path is the persistent-state
    path (collapsed — `properties.x.properties.y.items` → `x.y`).
    """
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "array" and isinstance(schema.get("items"), dict):
        item_props = schema["items"].get("properties", {}) or {}
        key_candidates = [k for k in item_props if k in KEY_SHAPED_FIELDS]
        if key_candidates:
            yield (path, key_candidates)
    # Walk into nested properties / additionalProperties / items
    if "properties" in schema and isinstance(schema["properties"], dict):
        for k, v in schema["properties"].items():
            child_path = f"{path}.{k}" if path else k
            yield from iter_key_shaped_arrays(v, child_path)
    if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
        yield from iter_key_shaped_arrays(schema["additionalProperties"], path)
    if "items" in schema and isinstance(schema["items"], dict):
        # collapse `items` into path (do not append a literal `.items` segment)
        yield from iter_key_shaped_arrays(schema["items"], path)


def is_path_declared(dotted_path: str, declared_paths: set[str]) -> bool:
    """A persistent-state arrays declaration covers an interpreter-schema array
    iff one is a prefix-match of the other on dotted components."""
    if dotted_path in declared_paths:
        return True
    target_parts = dotted_path.split(".")
    for d in declared_paths:
        d_parts = d.split(".")
        # Either the declaration is a prefix of the target, or vice versa.
        if d_parts == target_parts[: len(d_parts)]:
            return True
        if target_parts == d_parts[: len(target_parts)]:
            return True
    return False


def check_monitor(
    slug: str,
    monitor_dir: Path,
    schema_path: Path,
    repo_root: Path,
    meta_schema: dict,
) -> tuple[bool, list[str]]:
    """Returns (passed, messages). messages always include any WARN/FATAL findings."""
    msgs: list[str] = []

    if not schema_path.exists():
        msgs.append(
            f"FAIL[{slug}]: persistent-state-schema.json missing at {schema_path.relative_to(repo_root)}"
        )
        return (False, msgs)

    try:
        schema = json.loads(schema_path.read_text())
    except json.JSONDecodeError as e:
        msgs.append(f"FAIL[{slug}]: persistent-state-schema.json is not valid JSON: {e}")
        return (False, msgs)

    validator = jsonschema.Draft202012Validator(meta_schema)
    errors = sorted(validator.iter_errors(schema), key=lambda e: list(e.path))
    if errors:
        for e in errors[:5]:
            msgs.append(
                f"FAIL[{slug}]: persistent-state-schema validation: "
                f"{'.'.join(str(p) for p in e.path) or '<root>'} → {e.message[:240]}"
            )
        return (False, msgs)

    # Coverage check: every interpreter-schema array with a key-shaped field
    # must be declared in arrays block.
    interp_path = find_interpreter_schema(repo_root, slug)
    declared = set((schema.get("arrays") or {}).keys())

    if interp_path is None:
        # No interpreter-schema → nothing to coverage-check. Schema-only pass.
        msgs.append(f"PASS[{slug}]: schema present + valid; no interpreter-schema (coverage check skipped)")
        return (True, msgs)

    try:
        interp = json.loads(interp_path.read_text())
    except json.JSONDecodeError as e:
        msgs.append(f"FAIL[{slug}]: interpreter-schema.json is not valid JSON: {e}")
        return (False, msgs)

    gaps: list[tuple[str, list[str]]] = []
    for arr_path, key_candidates in iter_key_shaped_arrays(interp):
        if not is_path_declared(arr_path, declared):
            gaps.append((arr_path, key_candidates))

    if gaps:
        for arr_path, key_candidates in gaps:
            msgs.append(
                f"FAIL[{slug}]: interpreter-schema array `{arr_path}` (key-shaped fields: "
                f"{','.join(key_candidates)}) not declared in persistent-state-schema arrays block"
            )
        return (False, msgs)

    msgs.append(
        f"PASS[{slug}]: schema present + valid + {len(declared)} array declaration(s); "
        f"interpreter-schema coverage clean"
    )
    return (True, msgs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--monitor", help="Restrict check to a single monitor slug (short or long form)")
    parser.add_argument("--meta-schema", help="Path to persistent-state-schema-meta-schema.json")
    parser.add_argument("--repo-root", help="Path to asym-intel-main repo root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    meta_schema_path = find_meta_schema(repo_root, args.meta_schema)

    try:
        meta_schema = json.loads(meta_schema_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FATAL: meta-schema is not valid JSON: {e}", file=sys.stderr)
        return 2

    bootstrap = os.environ.get(BOOTSTRAP_ENV, "").strip() == "1"

    print(f"check_persistent_state_schema_coverage: repo_root={repo_root}")
    print(f"  meta-schema: {meta_schema_path}")
    print(f"  bootstrap mode: {bootstrap} (env {BOOTSTRAP_ENV}={os.environ.get(BOOTSTRAP_ENV, '<unset>')})")
    print()

    monitors = discover_monitor_dirs(repo_root)
    if args.monitor:
        monitors = [m for m in monitors if m[0] == args.monitor or m[0].startswith(args.monitor)]
        if not monitors:
            print(f"FATAL: no monitor matches --monitor {args.monitor}", file=sys.stderr)
            return 2

    failed: list[str] = []
    passed: list[str] = []
    all_msgs: list[str] = []
    for slug, monitor_dir, schema_path in monitors:
        ok, msgs = check_monitor(slug, monitor_dir, schema_path, repo_root, meta_schema)
        all_msgs.extend(msgs)
        if ok:
            passed.append(slug)
        else:
            failed.append(slug)

    for m in all_msgs:
        print(m)

    print()
    print(f"Summary: {len(passed)} passed, {len(failed)} failed.")
    if passed:
        print(f"  passed: {', '.join(passed)}")
    if failed:
        print(f"  failed: {', '.join(failed)}")

    if failed and not bootstrap:
        print(
            "\nFATAL: persistent-state-schema coverage gate failed. "
            "Add or amend the listed schemas. "
            "Authority: BRIEF-SPRINT-5-PERSISTENT-STATE-KEY-LOCK §4 Phase 2.",
            file=sys.stderr,
        )
        return 1
    if failed and bootstrap:
        print(
            "\nBOOTSTRAP-WARN: persistent-state-schema coverage gate has gaps but "
            f"{BOOTSTRAP_ENV}=1; treating as WARN-only. Phase 3 must close these.",
        )
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

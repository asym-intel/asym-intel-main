#!/usr/bin/env python3
"""Reusable-workflow input-type uniformity lint.

Sprint-2 G-NORMALISE-FORCE-TYPE Part C (2026-05-13-class-a-consumer-governance-sprint-1).
Doctrine: F-D2 (bind-don't-fork) + F-D6 (canonical-template uniformity).
Lineage: PR #316 cured the interpreter `force` input from string to boolean,
aligning the four role-class reusables. This lint enforces that uniformity
holds going forward and extends to any new reusable (e.g. `_reusable-publisher.yml`).

Scope
-----
- Globs `.github/workflows/_reusable-*.yml`.
- Parses each file's `on.workflow_call.inputs:` block.
- For every input name that appears in two or more reusable files, verifies
  that all declarations share the same `type:` value.
- Exits 1 on any drift; exits 0 when uniform.

Failure output (stable, machine-parseable):
    INPUT-TYPE-DRIFT:
      input '<name>'
        declared as type '<t1>' in <file1>
        declared as type '<t2>' in <file2>

The lint is observation-only — it never edits a workflow file.
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import yaml


REUSABLE_GLOB = ".github/workflows/_reusable-*.yml"


def collect_input_declarations(reusable_paths: list[str]) -> dict[str, list[tuple[str, str]]]:
    """Return {input_name: [(file, declared_type), ...]} across all reusables.

    A reusable without `on.workflow_call.inputs:` contributes nothing.
    A reusable that fails to parse is reported as a hard error so the lint
    never silently passes on broken YAML.
    """
    declarations: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(reusable_paths):
        try:
            doc = yaml.safe_load(Path(path).read_text())
        except yaml.YAMLError as exc:
            print(f"ERROR: failed to parse {path}: {exc}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(doc, dict):
            continue
        # `on` may be parsed as the bool True (YAML 1.1 footgun). Workflows here
        # use the `on:` key; safe_load yields the string key in either reading.
        on_block = doc.get("on") or doc.get(True)
        if not isinstance(on_block, dict):
            continue
        wf_call = on_block.get("workflow_call")
        if not isinstance(wf_call, dict):
            continue
        inputs = wf_call.get("inputs") or {}
        if not isinstance(inputs, dict):
            continue
        for name, spec in inputs.items():
            if not isinstance(spec, dict):
                continue
            declared_type = spec.get("type", "<unset>")
            declarations.setdefault(name, []).append((path, str(declared_type)))
    return declarations


def find_drift(declarations: dict[str, list[tuple[str, str]]]) -> list[str]:
    """Return human-readable drift lines for each input declared with >1 type."""
    drifts: list[str] = []
    for name in sorted(declarations):
        entries = declarations[name]
        if len(entries) < 2:
            continue
        types = {t for _, t in entries}
        if len(types) == 1:
            continue
        drifts.append(f"  input '{name}'")
        for path, declared_type in entries:
            drifts.append(f"    declared as type '{declared_type}' in {path}")
    return drifts


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    reusables = sorted(glob.glob(str(root / REUSABLE_GLOB)))
    if not reusables:
        print(f"ERROR: no files match {REUSABLE_GLOB} under {root}", file=sys.stderr)
        return 2

    print(f"Scanning {len(reusables)} reusable workflow(s):")
    for path in reusables:
        print(f"  - {path}")

    declarations = collect_input_declarations(reusables)
    drifts = find_drift(declarations)

    if drifts:
        print()
        print("INPUT-TYPE-DRIFT:")
        for line in drifts:
            print(line)
        print()
        print("Cure: align the type: declaration across all reusables that share the input.")
        print("Reference: Sprint-2 G-NORMALISE-FORCE-TYPE, PR #316.")
        return 1

    shared = sum(1 for entries in declarations.values() if len(entries) >= 2)
    total = sum(len(entries) for entries in declarations.values())
    print()
    print(f"OK: {len(declarations)} distinct input(s), {total} declaration(s), "
          f"{shared} appearing in 2+ reusables — all type-uniform.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

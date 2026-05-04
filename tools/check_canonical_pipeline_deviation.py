#!/usr/bin/env python3
"""Gate structural pipeline diffs behind canonical-class review sign-off.

Every commons monitor and additional consumer is an instance of the approved
generic pipeline class. A PR that changes structural pipeline surfaces must
classify the change before merge:

- canonical/common-code fix;
- consumer-specific config returning to canonical parity;
- justified consumer deviation, with the data-shape or structural-consumer
  reason recorded.

This script is deliberately mechanical. It does not decide whether a deviation
is justified; it blocks silent drift by requiring the PR body to carry the
review block before the PR can merge.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


STRUCTURAL_PATTERNS = [
    re.compile(r"^pipeline/engine/"),
    re.compile(r"^pipeline/monitors/[^/]+/(metadata\.yml|metadata\.yaml)$"),
    re.compile(r"^pipeline/monitors/[^/]+/(weekly-research|reasoner|synthesiser|interpreter|reviewer|composer)-"),
    re.compile(r"^pipeline/monitors/[^/]+/(collector|applier|curator)-"),
    re.compile(r"^pipeline/monitors/[^/]+/(interpreter|reviewer|composer|reasoner)-schema\.json$"),
    re.compile(r"^pipeline/monitors/[^/]+/registry/(collections|tiers)\.ya?ml$"),
    re.compile(r"^\.github/workflows/(_reusable-|[a-z0-9-]+-(collector|weekly-research|reasoner|synthesiser|interpreter|reviewer|composer|applier|curator|publisher)\.ya?ml$)"),
    re.compile(r"^\.github/workflows/canonical-pipeline-deviation-gate\.ya?ml$"),
    re.compile(r"^tools/(check_canonical_pipeline_deviation|consumer_readiness|scaffold_monitor|preflight_parity|commons_drift_scan)\.py$"),
    re.compile(r"^docs/architecture/(consumer-onboarding|canonical-monitor-shape|PIPELINE-TRIGGERS)\.md$"),
    re.compile(r"^docs/PIPELINE-CANONICAL\.md$"),
    re.compile(r"^ops/(PIPELINE-CONSUMER-KNOWHOW|PIPELINE-UPGRADE-TO-COMMON-SPEC-KNOWHOW|COLLECTION-SCHEMA-ALIGNMENT-CHECKLIST|METHODOLOGY-MAPPING-KNOWHOW)\.md$"),
]


REQUIRED_HEADINGS = [
    "canonical pipeline review",
]

REQUIRED_FIELDS = {
    "canonical-pipeline-reviewed": {"yes"},
    "classification": {
        "canonical/common-code fix",
        "canonical parity restoration",
        "justified consumer deviation",
        "no structural deviation",
    },
}

REQUIRED_FREE_TEXT_FIELDS = [
    "canonical comparator",
    "deviation rationale",
]

PLACEHOLDERS = {
    "",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
    "pending",
    "<fill>",
    "<fill in>",
    "<tbd>",
}


@dataclass(frozen=True)
class Result:
    ok: bool
    structural_files: list[str]
    errors: list[str]


def _run_git_diff(base: str, head: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", base, head],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def is_structural(path: str) -> bool:
    return any(pattern.search(path) for pattern in STRUCTURAL_PATTERNS)


def _normalise_body(body: str) -> str:
    return body.replace("\r\n", "\n").lower()


def _field_value(body: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(body)
    if not match:
        return None
    return match.group(1).strip()


def evaluate(body: str, changed_files: list[str]) -> Result:
    structural = [path for path in changed_files if is_structural(path)]
    if not structural:
        return Result(ok=True, structural_files=[], errors=[])

    errors: list[str] = []
    normalised = _normalise_body(body)

    for heading in REQUIRED_HEADINGS:
        if heading not in normalised:
            errors.append(
                "PR body must include a 'Canonical pipeline review' section "
                "for structural pipeline diffs."
            )

    for field, allowed in REQUIRED_FIELDS.items():
        value = _field_value(body, field)
        if value is None:
            errors.append(f"Missing required field: {field}:")
            continue
        if value.lower() not in allowed:
            allowed_list = ", ".join(sorted(allowed))
            errors.append(f"Invalid {field}: {value!r}; expected one of: {allowed_list}")

    for field in REQUIRED_FREE_TEXT_FIELDS:
        value = _field_value(body, field)
        if value is None:
            errors.append(f"Missing required field: {field}:")
            continue
        cleaned = value.strip().lower()
        if cleaned in PLACEHOLDERS or cleaned.startswith("<"):
            errors.append(f"Field {field}: must contain a substantive value, not {value!r}")

    return Result(ok=not errors, structural_files=structural, errors=errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    changed = _run_git_diff(args.base, args.head)
    body = Path(args.body_file).read_text(encoding="utf-8")
    result = evaluate(body, changed)

    payload = {
        "ok": result.ok,
        "structural_files": result.structural_files,
        "errors": result.errors,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not result.structural_files:
            print("PASS: no structural pipeline files changed.")
        elif result.ok:
            print("PASS: canonical pipeline review block present.")
            for path in result.structural_files:
                print(f"  - {path}")
        else:
            print("FAIL: structural pipeline diff lacks canonical review sign-off.")
            for path in result.structural_files:
                print(f"  - {path}")
            for error in result.errors:
                print(f"ERROR: {error}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

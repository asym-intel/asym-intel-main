#!/usr/bin/env python3
"""
tools/no_direct_provider_calls.py — CI gate (Sprint CS, BRIEF CS-2).

Scans every .py file under pipeline/monitors/** and pipeline/synthesisers/**
for direct LLM-provider calls (Anthropic / Perplexity SDK imports, hardcoded
provider hostnames, or provider env-var references). Such calls must go
through the engine clients (pipeline/engine/*) — direct calls bypass routing
provenance, exchange recording, and the Anthropic blocklist.

Allow-list:
  - tools/**          ops/maintenance scripts may invoke clients directly
  - pipeline/engine/** the engine clients are the legitimate consumers
                       (engine code lives only on asym-intel-internal and is
                       sparse-checked-out at workflow runtime; this entry is
                       defensive in case engine code is ever staged on main)

Note: pipeline/engine/ does not currently exist on this repo; the entry above
is intentional defence-in-depth, not a current path.

Exit codes:
  0 — no violations
  1 — one or more violations
  2 — tool error (file read failure, regex compile failure)

Usage:
  python3 tools/no_direct_provider_calls.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories to scan
_SCAN_ROOTS = (
    "pipeline/monitors",
    "pipeline/synthesisers",
)

# Path prefixes exempt from scanning. Matched against POSIX paths relative
# to REPO_ROOT.
_ALLOW_LIST = (
    "tools/",
    "pipeline/engine/",
)

# (label, compiled regex). Order is preserved for stable output.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("api.perplexity.ai",   re.compile(r"https?://api\.perplexity\.ai")),
    ("api.anthropic.com",   re.compile(r"https?://api\.anthropic\.com")),
    ("import anthropic",    re.compile(r"^\s*import\s+anthropic(\b|\s|$)")),
    ("from anthropic import", re.compile(r"^\s*from\s+anthropic\s+import")),
    ("from anthropic",      re.compile(r"^\s*from\s+anthropic\b")),
    ("requests->perplexity", re.compile(r"requests\.(post|get|put|patch)\s*\([^)]*perplexity")),
    ("requests->anthropic", re.compile(r"requests\.(post|get|put|patch)\s*\([^)]*anthropic")),
    ("PPLX_API_KEY",        re.compile(r"PPLX_API_KEY")),
    ("ANTHROPIC_API_KEY",   re.compile(r"ANTHROPIC_API_KEY")),
)


def _is_allow_listed(rel_posix: str) -> bool:
    return any(rel_posix.startswith(prefix) for prefix in _ALLOW_LIST)


def _iter_py_files(root: Path, scan_roots: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for sub in scan_roots:
        base = root / sub
        if not base.exists():
            continue
        files.extend(sorted(base.rglob("*.py")))
    return files


def scan(root: Path = REPO_ROOT) -> tuple[list[str], int]:
    """Return (violation_lines, files_scanned).

    Each violation_line is in the form
        VIOLATION: <path>:<line>: <pattern> — <matched text>
    """
    violations: list[str] = []
    scanned = 0

    for py in _iter_py_files(root, _SCAN_ROOTS):
        rel = py.relative_to(root).as_posix()
        if _is_allow_listed(rel):
            continue
        scanned += 1
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"ERROR: failed to read {rel}: {exc}", file=sys.stderr)
            return [], -1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, rx in _PATTERNS:
                if rx.search(line):
                    matched = line.strip()
                    violations.append(
                        f"VIOLATION: {rel}:{lineno}: {label} — {matched}"
                    )

    return violations, scanned


def main() -> int:
    print("no_direct_provider_calls.py — checking pipeline/monitors/** and pipeline/synthesisers/**...\n")
    try:
        violations, scanned = scan(REPO_ROOT)
    except re.error as exc:
        print(f"ERROR: regex compile failure: {exc}", file=sys.stderr)
        return 2

    if scanned < 0:
        return 2

    for v in violations:
        print(v)

    if violations:
        files_with = len({v.split(":", 2)[1] for v in violations})
        print(f"\n{scanned} files scanned, {len(violations)} violations found across {files_with} files.")
        print("Exit 1.")
        return 1

    print(f"\n{scanned} files scanned, 0 violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

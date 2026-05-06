#!/usr/bin/env python3
"""
tools/no_direct_provider_calls.py — CI gate (Sprint CS-min, BRIEF CS-2).

Scans the canonical engine surface for direct LLM-provider calls (Anthropic /
Perplexity SDK imports, hardcoded provider hostnames, or provider env-var
references). Such calls inside the engine bypass the routing layer that the
engine itself is supposed to provide — exchange recording, model-routing
provenance, and the Anthropic blocklist all flow through the engine clients.

Scope (intentional and narrow)
------------------------------
The gate scans **only** these paths:

  pipeline/engine/**             — the engine clients themselves
  pipeline/chatter/unified-chatter.py — the consolidated chatter dispatcher

Everything else under pipeline/** is OUT OF SCOPE for this gate. Pre-engine
files (per-monitor weekly-research.py, <abbr>-reasoner.py, per-monitor
synthesisers, collect.py, the cross-monitor synthesiser, daily test scripts,
test fixtures) may carry one of several roles — legacy entry point retained
for direct invocation, lab/debug tool, scheduled fallback, or dead residue
awaiting cleanup — and Sprint CS-min did not classify them. A future sprint
will audit and decide; this gate makes no claim about them.

The narrow scope is deliberate. It gives the gate a positive guarantee
("the engine path stays clean") while declining to take a position on
files whose status is uncertain.

Allow-list policy
-----------------
None. The scope IS the allow-list — anything inside the scoped paths must
either route through the engine or be removed. There is no per-file
exemption mechanism, by design.

Engine code lives only on asym-intel-internal and is sparse-checked-out at
workflow runtime. On asym-intel-main the gate's scan paths are typically
empty or nearly so; that is expected. A clean gate on main means "no engine
code accidentally landed in the public repo and bypasses routing." A clean
gate on internal means "the engine itself is honest about its own
boundary."

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

# Scoped scan targets. The gate scans these paths and only these paths.
# Each entry is either a directory (recursive) or an exact file path,
# all relative to REPO_ROOT and using POSIX separators.
_SCAN_DIRS: tuple[str, ...] = (
    "pipeline/engine",
)
_SCAN_FILES: tuple[str, ...] = (
    "pipeline/chatter/unified-chatter.py",
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


def _iter_py_files(root: Path,
                   scan_dirs: Iterable[str],
                   scan_files: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for sub in scan_dirs:
        base = root / sub
        if base.exists():
            files.extend(sorted(base.rglob("*.py")))
    for rel in scan_files:
        path = root / rel
        if path.exists():
            files.append(path)
    return files


def scan(root: Path = REPO_ROOT) -> tuple[list[str], int]:
    """Return (violation_lines, files_scanned).

    Each violation_line is in the form
        VIOLATION: <path>:<line>: <pattern> — <matched text>
    """
    violations: list[str] = []
    scanned = 0

    for py in _iter_py_files(root, _SCAN_DIRS, _SCAN_FILES):
        rel = py.relative_to(root).as_posix()
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


def _scope_description() -> str:
    parts = list(_SCAN_DIRS) + list(_SCAN_FILES)
    return ", ".join(parts)


def main() -> int:
    print(f"no_direct_provider_calls.py — scanning {_scope_description()}...\n")
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

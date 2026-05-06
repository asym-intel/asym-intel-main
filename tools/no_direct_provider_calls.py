#!/usr/bin/env python3
"""
tools/no_direct_provider_calls.py — CI gate (Sprint CS-min, BRIEF CS-2).

Scans every .py file under pipeline/monitors/** and pipeline/synthesisers/**
for direct LLM-provider calls (Anthropic / Perplexity SDK imports, hardcoded
provider hostnames, or provider env-var references). Such calls must go
through the engine clients (pipeline/engine/*) — direct calls bypass routing
provenance, exchange recording, and the Anthropic blocklist.

Allow-list policy
-----------------
Two kinds of entries:

1. PREFIX EXEMPTIONS — directory trees that are inherently allowed:
     tools/            ops/maintenance scripts may invoke clients directly
     pipeline/engine/  the engine clients themselves (engine code lives only
                       on asym-intel-internal and is sparse-checked-out at
                       workflow runtime; this entry is defensive in case
                       engine code is ever staged on main)

2. RESIDUE EXEMPTIONS — exact file paths that genuinely still call providers
   directly because their pre-engine code path has not been migrated yet.
   Each entry is tagged with the housekeeping ticket that tracks migration.
   These exemptions are TEMPORARY — when Sprint CT (or successor) lands, the
   corresponding entry must be removed and the file re-scanned.

   The entries below are the inventory captured at the close of Sprint CS-min
   (2026-05-05). If any entry is removed without the live workflow being
   migrated to engine dispatch, the gate will start failing — that IS the
   intended forcing function.

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

# Prefix exemptions — directory trees inherently outside the gate's remit.
_ALLOW_PREFIXES: tuple[str, ...] = (
    "tools/",
    "pipeline/engine/",
)

# Residue exemptions — exact file paths still on the pre-engine code path.
# Tagged with the housekeeping ticket tracking their migration. These entries
# are removed one-by-one as files migrate to engine dispatch.
#
# Captured 2026-05-05 (Sprint CS-min close). See ops/HOUSEKEEPING-INBOX.md
# entry "Sprint CT — engine cutover residue (collect.py + cross-monitor)".
_ALLOW_RESIDUE_FILES: tuple[str, ...] = (
    # Daily collectors — still pre-engine; called directly from
    # <abbr>-collector.yml workflows. Migration target: pipeline.engine.collect_base.
    "pipeline/monitors/ai-governance/collect.py",                # CT residue
    "pipeline/monitors/conflict-escalation/collect.py",          # CT residue
    "pipeline/monitors/democratic-integrity/collect.py",         # CT residue
    "pipeline/monitors/environmental-risks/collect.py",          # CT residue
    "pipeline/monitors/european-strategic-autonomy/collect.py",  # CT residue
    "pipeline/monitors/fimi-cognitive-warfare/collect.py",       # CT residue
    "pipeline/monitors/financial-integrity/collect.py",          # CT residue
    "pipeline/monitors/macro-monitor/collect.py",                # CT residue

    # Cross-monitor synthesiser — still pre-engine; called directly from
    # cross-monitor-synthesiser.yml. The seven per-monitor synthesisers
    # already migrated to pipeline.engine.synth_base. Migration target same.
    "pipeline/synthesisers/cross-monitor/cross-monitor-synthesiser.py",  # CT residue
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
    if any(rel_posix.startswith(prefix) for prefix in _ALLOW_PREFIXES):
        return True
    if rel_posix in _ALLOW_RESIDUE_FILES:
        return True
    return False


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

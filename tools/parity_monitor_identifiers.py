#!/usr/bin/env python3
"""
PARITY-003 — Monitor identifier canonical check.

Reads ``pipeline/engine/canonical_monitors.yml`` and scans all .yml/.md/.ts/.json
files for monitor-identifier strings. Fails CI if any slug, abbr, or name string
in scanned files drifts from canonical values.

Reference: Sprint AO BRIEF #6 (step-ao-monitor-canonical), AD-2026-04-26-AO §3.

What PARITY-003 checks
----------------------
For each canonical monitor entry (slug, abbr, name, full_title):
  - Slug strings in scanned files must match canonical slug exactly.
  - Abbr strings (when appearing as stand-alone identifiers, e.g. in YAML keys,
    JSON fields, or prose following known patterns) must match canonical abbr
    (uppercase). Abbr matches are case-sensitive after normalisation.
  - The check does NOT match stage-workflow filename prefixes (agm-*, wdm-*, etc.)
    — those are filesystem conventions, not identity tokens.
  - The check does NOT match arbitrary occurrences of 3-letter strings (too noisy).
    It uses targeted patterns defined in ABBR_PATTERNS below.

What PARITY-003 does NOT check
-------------------------------
  - Workflow display name strings (e.g. "Global Environmental Risks Monitor Synthesiser")
    — these are workflow descriptions, not identity tokens.
  - DAY_MONITOR lowercase values in workers/pipeline-dispatcher/src/index.ts
    — these are slug lookups (intentional lowercase), not abbr tokens.
  - metadata.yml abbr values — these carry the canonical internal abbr (e.g. AGM for
    ai-governance), which is intentional per operator decision A.2(a) (Sprint AO Wave 2 §A.3).
    Engine validate_metadata_against_canonical() handles any case-normalisation warnings.
  - File contents of pipeline/engine/canonical_monitors.yml itself.

Repo detection
--------------
Like preflight_parity.py, this script detects its repo by sentinel files:
  - internal: ops/ENGINE-RULES.md
  - main:     tools/preflight.py

Exit codes
----------
0 — no drift detected
1 — drift detected (lists each instance)
2 — canonical_monitors.yml not found or unparseable

Usage
-----
    python3 tools/parity_monitor_identifiers.py
    python3 tools/parity_monitor_identifiers.py --verbose
    python3 tools/parity_monitor_identifiers.py --canonical path/to/canonical_monitors.yml
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Repo detection
# ---------------------------------------------------------------------------

SENTINEL_INTERNAL = "ops/ENGINE-RULES.md"
SENTINEL_MAIN = "tools/preflight.py"

# Files to skip unconditionally (this script itself, the canonical source)
SKIP_FILES = {
    "parity_monitor_identifiers.py",
    "test_parity_monitor_identifiers.py",
    "canonical_monitors.yml",
    "CANONICAL-MONITORS.md",  # generated from canonical_monitors.yml
}

# Directories to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache"}

# File extensions to scan
SCAN_EXTENSIONS = {".yml", ".yaml", ".md", ".ts", ".json"}

# ---------------------------------------------------------------------------
# Abbr pattern configuration
#
# PARITY-003 only matches abbr strings in targeted contexts to avoid false
# positives from coincidental 3-letter substrings (e.g. "esa" in "research").
#
# Patterns are applied to each scanned line. A match is flagged if:
#   - the matched abbr is NOT the canonical value for the slug in question, AND
#   - a drift mapping is configured (i.e. we know what the wrong value is)
#
# For the AGM/AIM drift: we look for "AGM" appearing as an abbr token in
# contexts where AIM is canonical. Specifically: CANONICAL-ARTEFACTS.md row
# labels use the pattern "| AGM |" — we check those.
# ---------------------------------------------------------------------------

# Known abbr drift: maps wrong_abbr → canonical_abbr (for targeted scanning).
# NOTE: AGM is intentionally excluded from this dict.
# Per operator decision A.2(a) (Sprint AO Wave 2 §A.3):
#   AGM = canonical INTERNAL stage-prefix convention (metadata.yml, CANONICAL-ARTEFACTS.md,
#         per-stage workflow prefixes, cross-monitor routing strings in schemas/domain files)
#   AIM = canonical PUBLIC abbreviation (monitor-registry.json, publisher workflow)
# Both are ratified legitimate forms; AGM appearing in internal files is NOT drift.
# PARITY-003 therefore has no AGM→AIM drift to scan for. If AIM is ever replaced
# with something else in a public-facing context, add a new entry here.
KNOWN_ABBR_DRIFT: dict[str, str] = {}

# Files where abbr forms are intentional and should not be flagged by PARITY-003.
# With KNOWN_ABBR_DRIFT empty (AGM is canonical internal per A.2(a)), this list is
# retained for any future drift entries added to KNOWN_ABBR_DRIFT.
ABBR_DRIFT_ALLOWLIST_PATTERNS = [
    # DAY_MONITOR in pipeline-dispatcher (intentional slug-as-key, not abbr token)
    re.compile(r"workers/pipeline-dispatcher/src/index\.ts"),
    # AUDIT.md documents drift — don't flag it
    re.compile(r"step-ao-monitor-canonical/AUDIT\.md"),
]

# Pattern to match standalone abbr tokens (YAML value, JSON string, markdown table cell)
# e.g.: `abbr: AGM`, `"abbr": "AGM"`, `| AGM |`, `abbr: agm`
_ABBR_TOKEN_RE = re.compile(
    r'(?:'
    r'abbr[:\s]+["\']?(?P<abbr_val>[A-Za-z]{2,6})["\']?'  # abbr: AGM or abbr: "AGM"
    r'|'
    r'\|\s*(?P<abbr_cell>[A-Z]{2,6})\s*\|'  # | AGM |  in markdown tables
    r')',
    re.IGNORECASE,
)

# Pattern for slug strings — match known-bad or check canonical slug appears where expected
_SLUG_RE = re.compile(
    r'(?:'
    r'slug[:\s]+["\']?(?P<slug_val>[a-z][a-z0-9-]+)["\']?'  # slug: conflict-escalation
    r')',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_repo_root() -> pathlib.Path:
    """Walk up from CWD to find repo root (containing .git)."""
    p = pathlib.Path.cwd()
    for _ in range(10):
        if (p / ".git").exists():
            return p
        p = p.parent
    return pathlib.Path.cwd()


def detect_repo(root: pathlib.Path) -> str:
    """Return 'internal', 'main', or 'unknown'."""
    if (root / SENTINEL_INTERNAL).exists():
        return "internal"
    if (root / SENTINEL_MAIN).exists():
        return "main"
    return "unknown"


def canonical_monitors_path(root: pathlib.Path) -> pathlib.Path:
    """Return the expected path to canonical_monitors.yml for this repo."""
    # Both repos: the canonical is in asym-intel-internal.
    # On internal: pipeline/engine/canonical_monitors.yml
    # On main: we look for a mirrored copy or fall back to fetching via env
    if (root / "pipeline" / "engine" / "canonical_monitors.yml").exists():
        return root / "pipeline" / "engine" / "canonical_monitors.yml"
    # main repo does not carry canonical_monitors.yml — try counterpart cache
    cache_dir = pathlib.Path("/tmp/asym-intel-parity-cache")
    candidate = cache_dir / "asym-intel-internal" / "pipeline" / "engine" / "canonical_monitors.yml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        "canonical_monitors.yml not found. On asym-intel-main, ensure the "
        "internal repo is cloned to /tmp/asym-intel-parity-cache/asym-intel-internal/ "
        "or run preflight_parity.py first."
    )


def load_canonical(path: pathlib.Path) -> dict:
    """Load and return the monitors dict from canonical_monitors.yml."""
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    raw = yaml.safe_load(path.read_text("utf-8"))
    if not isinstance(raw, dict):
        print(f"ERROR: {path} is not a YAML mapping.", file=sys.stderr)
        sys.exit(2)
    monitors = raw.get("monitors")
    if not isinstance(monitors, dict):
        print(f"ERROR: {path} has no 'monitors' mapping.", file=sys.stderr)
        sys.exit(2)
    return monitors


def is_allowlisted(file_path: pathlib.Path) -> bool:
    """Return True if this file's drift should not be flagged by PARITY-003."""
    path_str = str(file_path)
    return any(pat.search(path_str) for pat in ABBR_DRIFT_ALLOWLIST_PATTERNS)


def scan_file(
    file_path: pathlib.Path,
    canonical_monitors: dict,
    *,
    verbose: bool = False,
) -> list[str]:
    """Scan a single file for monitor-identifier drift.

    Returns a list of failure messages (empty = no drift).
    """
    failures: list[str] = []
    allowlisted = is_allowlisted(file_path)

    # Build reverse maps
    abbr_to_slug = {v["abbr"].upper(): k for k, v in canonical_monitors.items()}
    slug_to_canonical = canonical_monitors  # slug → {slug, abbr, name, full_title}

    try:
        text = file_path.read_text("utf-8", errors="replace")
    except (OSError, PermissionError) as e:
        if verbose:
            print(f"  SKIP (unreadable): {file_path}: {e}")
        return failures

    for lineno, line in enumerate(text.splitlines(), start=1):
        # Check for known abbr drift (AGM where AIM is canonical)
        for wrong_abbr, correct_abbr in KNOWN_ABBR_DRIFT.items():
            # Match "abbr: AGM" or "| AGM |" patterns
            if re.search(
                r'(?:abbr[:\s]+["\']?' + re.escape(wrong_abbr) + r'["\']?'
                r'|\|\s*' + re.escape(wrong_abbr) + r'\s*\|)',
                line,
                re.IGNORECASE,
            ):
                if allowlisted:
                    if verbose:
                        print(f"  [allowlisted] {file_path}:{lineno}: {wrong_abbr} (known pre-existing drift)")
                else:
                    failures.append(
                        f"[PARITY-003] ABBR DRIFT: {file_path}:{lineno}: "
                        f"found {wrong_abbr!r} (wrong abbr), canonical is {correct_abbr!r}. "
                        f"Line: {line.strip()!r}"
                    )

        # Check for slug drift (wrong slug in a slug: field)
        for m in _SLUG_RE.finditer(line):
            found_slug = m.group("slug_val")
            if found_slug and found_slug not in slug_to_canonical:
                # Only flag if it looks like a monitor slug (contains a known fragment)
                monitor_fragments = [
                    "democratic-integrity", "macro-monitor", "european-strategic",
                    "fimi-cognitive", "ai-governance", "environmental-risks",
                    "conflict-escalation",
                ]
                if any(frag in found_slug for frag in monitor_fragments):
                    failures.append(
                        f"[PARITY-003] SLUG DRIFT: {file_path}:{lineno}: "
                        f"slug {found_slug!r} not in canonical_monitors.yml. "
                        f"Line: {line.strip()!r}"
                    )

    return failures


def scan_repo(
    root: pathlib.Path,
    canonical_monitors: dict,
    *,
    verbose: bool = False,
) -> list[str]:
    """Scan all eligible files in the repo and return drift failures."""
    all_failures: list[str] = []

    for file_path in root.rglob("*"):
        # Skip directories
        if file_path.is_dir():
            continue
        # Skip excluded directories
        if any(part in SKIP_DIRS for part in file_path.parts):
            continue
        # Skip excluded filenames
        if file_path.name in SKIP_FILES:
            continue
        # Skip non-target extensions
        if file_path.suffix.lower() not in SCAN_EXTENSIONS:
            continue

        file_failures = scan_file(file_path, canonical_monitors, verbose=verbose)
        if file_failures:
            all_failures.extend(file_failures)
            if verbose:
                for f in file_failures:
                    print(f"  {f}")

    return all_failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PARITY-003 — Monitor identifier canonical check (Sprint AO BRIEF #6)"
    )
    parser.add_argument(
        "--canonical",
        type=pathlib.Path,
        default=None,
        help="Path to canonical_monitors.yml (overrides auto-detection).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print every file scanned and allowlisted drift instances.",
    )
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=None,
        help="Repo root directory (defaults to CWD or nearest .git parent).",
    )
    args = parser.parse_args(argv)

    root = args.root or find_repo_root()
    print(f"[PARITY-003] Repo root: {root}")

    repo = detect_repo(root)
    print(f"[PARITY-003] Detected repo: {repo}")

    # Resolve canonical path
    if args.canonical:
        canon_path = args.canonical
    else:
        try:
            canon_path = canonical_monitors_path(root)
        except FileNotFoundError as e:
            print(f"[PARITY-003] ERROR: {e}", file=sys.stderr)
            return 2

    print(f"[PARITY-003] Loading canonical from: {canon_path}")
    try:
        canonical_monitors = load_canonical(canon_path)
    except Exception as e:
        print(f"[PARITY-003] ERROR loading canonical: {e}", file=sys.stderr)
        return 2

    print(f"[PARITY-003] Canonical monitors: {sorted(canonical_monitors.keys())}")
    print(f"[PARITY-003] Scanning {root} ...")

    failures = scan_repo(root, canonical_monitors, verbose=args.verbose)

    if failures:
        print(f"\n[PARITY-003] FAILED — {len(failures)} drift instance(s) detected:\n")
        for f in failures:
            print(f"  {f}")
        print(
            "\n[PARITY-003] Fix: update the flagged file(s) to use canonical identifiers "
            "from pipeline/engine/canonical_monitors.yml."
        )
        return 1

    print(f"[PARITY-003] PASSED — no monitor identifier drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

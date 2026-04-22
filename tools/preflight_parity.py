#!/usr/bin/env python3
"""
preflight_parity.py — cross-repo canonical artefact parity check.

Enforces the invariants declared in `CANONICAL-ARTEFACTS.md` (`ops/` on
internal, `pipeline/` on main — byte-identical copies).

Two checks are run:

PARITY-001 (md5 identicality): for each `byte-identical` row in the
manifest, both paired files must exist and share an md5 hash. Fails
with both paths + both hashes on divergence.

PARITY-002 (pair existence): for each `byte-identical` or `known-drift`
row in the manifest, both paired files must exist. Fails if only one
side is present (catches e.g. "prompt added to main but never authored
in internal" — the exact Class E gap this preflight is built to close).

Rows classified `canonical-only` or `pre-canonical` are exempt from
both checks. Rows classified `known-drift` are exempt from PARITY-001
(md5) until their dated expiry; PARITY-002 still applies.

Spec: SCOPE-2026-04-22-002 Class B. Doctrine: ENGINE-RULES §5 +
`ops/PIPELINE-UPGRADE-TO-COMMON-SPEC-KNOWHOW.md`.

Dual-context execution
----------------------
The manifest lists paths for both repos. This script runs in both and
uses the repo it's living in as the "local" side; the other side is
fetched via a cached `gh repo clone --depth=1` to
`$ASYM_PARITY_CACHE` (default `/tmp/asym-intel-parity-cache`). Follows
the `_ensure_main_on_path()` pattern in
`pipeline/lab/perplexity/client.py`.

Repo detection is by presence of an unambiguous sentinel file:
  - internal: `ops/ENGINE-RULES.md`
  - main:     `tools/preflight.py`

Usage
-----
    python3 tools/preflight_parity.py            # exit 0 on pass, 1 on fail
    python3 tools/preflight_parity.py --json     # machine-readable output
    python3 tools/preflight_parity.py --manifest path/to/CANONICAL-ARTEFACTS.md
    python3 tools/preflight_parity.py --self-test  # no cross-repo, uses fixtures

Exit codes
----------
0 — all byte-identical rows pass md5 + existence checks; known-drift
    rows exist on both sides (but md5 mismatch is allow-listed).
1 — one or more PARITY-001 or PARITY-002 failures.
2 — manifest not found or unparseable; sentinel detection failed;
    cross-repo clone failed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Literal


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

SELF_SKIP_FILES = {
    "preflight_parity.py",
    "test_preflight_parity.py",
}

# Manifest location in each repo
MANIFEST_INTERNAL = "ops/CANONICAL-ARTEFACTS.md"
MANIFEST_MAIN = "pipeline/CANONICAL-ARTEFACTS.md"

# Sentinel files for unambiguous repo detection
SENTINEL_INTERNAL = "ops/ENGINE-RULES.md"
SENTINEL_MAIN = "tools/preflight.py"

# Category tokens (match the headings in CANONICAL-ARTEFACTS.md)
CATEGORY_BYTE_IDENTICAL = "byte-identical"
CATEGORY_CANONICAL_ONLY = "canonical-only"
CATEGORY_PRE_CANONICAL = "pre-canonical"
CATEGORY_KNOWN_DRIFT = "known-drift"

# Repos
REPO_INTERNAL = "asym-intel/asym-intel-internal"
REPO_MAIN = "asym-intel/asym-intel-main"

Category = Literal["byte-identical", "canonical-only", "pre-canonical", "known-drift"]
Side = Literal["internal", "main"]


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #


@dataclass
class ParityRow:
    """One row of the manifest."""
    monitor: str
    slot: str
    category: Category
    canonical_path: str  # relative to asym-intel-internal root
    live_path: str       # relative to asym-intel-main root
    # For known-drift rows only:
    drift_cause: str = ""
    drift_expiry: str = ""


@dataclass
class CheckResult:
    """Result of one PARITY-001 or PARITY-002 check."""
    check: Literal["PARITY-001", "PARITY-002"]
    row: ParityRow
    passed: bool
    message: str
    canonical_md5: str = ""
    live_md5: str = ""


@dataclass
class Results:
    """Aggregate preflight run."""
    rows_total: int = 0
    rows_checked: int = 0
    rows_exempt: int = 0
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def failures(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed]

    def any_failed(self) -> bool:
        return bool(self.failures)


# --------------------------------------------------------------------------- #
# Repo detection + cross-repo cache
# --------------------------------------------------------------------------- #


def detect_local_side(repo_root: pathlib.Path) -> Side:
    """Return 'internal' or 'main' based on sentinel presence."""
    has_internal = (repo_root / SENTINEL_INTERNAL).is_file()
    has_main = (repo_root / SENTINEL_MAIN).is_file()
    if has_internal and not has_main:
        return "internal"
    if has_main and not has_internal:
        return "main"
    if has_internal and has_main:
        # Both sentinels present → combined checkout (e.g. in a dev sandbox).
        # Prefer internal since canonical is authoritative.
        return "internal"
    raise FileNotFoundError(
        f"Neither sentinel found under {repo_root}: expected "
        f"{SENTINEL_INTERNAL} (internal) or {SENTINEL_MAIN} (main)."
    )


def ensure_other_repo(other_side: Side, cache_dir: pathlib.Path | None = None) -> pathlib.Path:
    """Clone (or refresh) the other repo to a cache dir; return the cache path.

    Follows the _ensure_main_on_path pattern in pipeline/lab/perplexity/client.py
    but targets whichever side is the non-local one.
    """
    if cache_dir is None:
        cache_dir = pathlib.Path(
            os.environ.get("ASYM_PARITY_CACHE", tempfile.gettempdir() + f"/asym-intel-parity-{other_side}")
        )
    repo_slug = REPO_INTERNAL if other_side == "internal" else REPO_MAIN

    if not cache_dir.exists():
        subprocess.run(
            ["gh", "repo", "clone", repo_slug, str(cache_dir), "--", "--depth=1"],
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        try:
            subprocess.run(
                ["git", "-C", str(cache_dir), "fetch", "--depth=1", "origin", "main"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(cache_dir), "reset", "--hard", "origin/main"],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            # Cache may be corrupt; re-clone
            import shutil
            shutil.rmtree(cache_dir)
            subprocess.run(
                ["gh", "repo", "clone", repo_slug, str(cache_dir), "--", "--depth=1"],
                check=True,
                capture_output=True,
                text=True,
            )
    return cache_dir


# --------------------------------------------------------------------------- #
# Manifest parsing
# --------------------------------------------------------------------------- #


_HEADING_BYTE_IDENTICAL = re.compile(r"^##\s+Byte-identical pairs", re.MULTILINE)
_HEADING_CANONICAL_ONLY = re.compile(r"^##\s+Canonical-only rows", re.MULTILINE)
_HEADING_PRE_CANONICAL = re.compile(r"^##\s+Pre-canonical rows", re.MULTILINE)
_HEADING_KNOWN_DRIFT = re.compile(r"^##\s+Known-drift rows", re.MULTILINE)
_HEADING_SELF_REF = re.compile(r"^##\s+Manifest self-reference", re.MULTILINE)
_HEADING_ANY = re.compile(r"^##\s+", re.MULTILINE)


def _extract_section(text: str, start_re: re.Pattern) -> str:
    """Extract the text between a heading and the next heading (or EOF)."""
    m = start_re.search(text)
    if not m:
        return ""
    start = m.end()
    nxt = _HEADING_ANY.search(text, pos=start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def _parse_table_rows(section: str) -> list[list[str]]:
    """Parse pipe-delimited rows from a markdown section.

    Skips header rows (those whose cells are all whitespace/dashes) and
    non-table lines. Returns cells with surrounding whitespace stripped and
    backticks removed.
    """
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # Skip the separator row (cells are all dashes/colons)
        if all(re.fullmatch(r"[\s\-:]*", c) for c in cells):
            continue
        # Skip the header row — convention: contains "Monitor" or "Abbr" as first cell
        if cells and cells[0] in ("Monitor", "Abbr", "Artefact"):
            continue
        # Strip backticks from path cells
        cells = [c.strip("` ") for c in cells]
        rows.append(cells)
    return rows


def parse_manifest(manifest_path: pathlib.Path) -> list[ParityRow]:
    """Parse CANONICAL-ARTEFACTS.md into ParityRow objects."""
    text = manifest_path.read_text(encoding="utf-8")

    rows: list[ParityRow] = []

    # Byte-identical: Monitor | Slot | Canonical (internal) | Live (main)
    for cells in _parse_table_rows(_extract_section(text, _HEADING_BYTE_IDENTICAL)):
        if len(cells) >= 4:
            rows.append(ParityRow(
                monitor=cells[0],
                slot=cells[1],
                category=CATEGORY_BYTE_IDENTICAL,
                canonical_path=cells[2],
                live_path=cells[3],
            ))

    # Canonical-only: Monitor | Slot | Canonical (internal)   — live_path = ""
    for cells in _parse_table_rows(_extract_section(text, _HEADING_CANONICAL_ONLY)):
        if len(cells) >= 3:
            rows.append(ParityRow(
                monitor=cells[0],
                slot=cells[1],
                category=CATEGORY_CANONICAL_ONLY,
                canonical_path=cells[2],
                live_path="",
            ))

    # Pre-canonical: Abbr | Slot | Canonical path (empty today) | Live path
    for cells in _parse_table_rows(_extract_section(text, _HEADING_PRE_CANONICAL)):
        if len(cells) >= 4:
            rows.append(ParityRow(
                monitor=cells[0],
                slot=cells[1],
                category=CATEGORY_PRE_CANONICAL,
                canonical_path=cells[2],
                live_path=cells[3],
            ))

    # Known-drift: Monitor | Slot | Canonical | Live | Cause | Expiry
    for cells in _parse_table_rows(_extract_section(text, _HEADING_KNOWN_DRIFT)):
        if len(cells) >= 6:
            rows.append(ParityRow(
                monitor=cells[0],
                slot=cells[1],
                category=CATEGORY_KNOWN_DRIFT,
                canonical_path=cells[2],
                live_path=cells[3],
                drift_cause=cells[4],
                drift_expiry=cells[5],
            ))

    # Manifest self-reference: Artefact | Canonical (internal) | Live (main) | Category
    for cells in _parse_table_rows(_extract_section(text, _HEADING_SELF_REF)):
        if len(cells) >= 4:
            cat = cells[3]
            if cat == CATEGORY_BYTE_IDENTICAL:
                rows.append(ParityRow(
                    monitor="manifest",
                    slot="self-reference",
                    category=CATEGORY_BYTE_IDENTICAL,
                    canonical_path=cells[1],
                    live_path=cells[2],
                ))

    return rows


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #


def _md5(path: pathlib.Path) -> str:
    """Return hex md5 of the file contents. Empty string if missing."""
    if not path.is_file():
        return ""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_checks(
    rows: list[ParityRow],
    internal_root: pathlib.Path,
    main_root: pathlib.Path,
) -> Results:
    r = Results()
    for row in rows:
        r.rows_total += 1

        if row.category in (CATEGORY_CANONICAL_ONLY, CATEGORY_PRE_CANONICAL):
            r.rows_exempt += 1
            continue

        r.rows_checked += 1
        c_path = internal_root / row.canonical_path
        l_path = main_root / row.live_path

        c_exists = c_path.is_file()
        l_exists = l_path.is_file()

        # PARITY-002 (pair existence)
        if c_exists and l_exists:
            r.checks.append(CheckResult(
                check="PARITY-002",
                row=row,
                passed=True,
                message=f"both sides present ({row.canonical_path} ↔ {row.live_path})",
            ))
        else:
            missing = []
            if not c_exists:
                missing.append(f"canonical missing: {row.canonical_path}")
            if not l_exists:
                missing.append(f"live missing: {row.live_path}")
            r.checks.append(CheckResult(
                check="PARITY-002",
                row=row,
                passed=False,
                message=" | ".join(missing),
            ))
            # If a side is missing, skip PARITY-001 — it can only fail noisily
            continue

        # PARITY-001 (md5 identicality) — only for byte-identical
        if row.category == CATEGORY_BYTE_IDENTICAL:
            cmd5 = _md5(c_path)
            lmd5 = _md5(l_path)
            if cmd5 == lmd5:
                r.checks.append(CheckResult(
                    check="PARITY-001",
                    row=row,
                    passed=True,
                    message=f"md5 match ({cmd5[:8]}…)",
                    canonical_md5=cmd5,
                    live_md5=lmd5,
                ))
            else:
                r.checks.append(CheckResult(
                    check="PARITY-001",
                    row=row,
                    passed=False,
                    message=(
                        f"md5 mismatch: canonical {cmd5} ≠ live {lmd5} "
                        f"({row.canonical_path} vs {row.live_path})"
                    ),
                    canonical_md5=cmd5,
                    live_md5=lmd5,
                ))
        elif row.category == CATEGORY_KNOWN_DRIFT:
            # Log but do not fail. md5 may still be computed for visibility.
            cmd5 = _md5(c_path)
            lmd5 = _md5(l_path)
            r.checks.append(CheckResult(
                check="PARITY-001",
                row=row,
                passed=True,  # allow-listed
                message=(
                    f"allow-listed drift (expires: {row.drift_expiry}) — "
                    f"canonical {cmd5[:8]}… ≠ live {lmd5[:8]}… OK"
                ),
                canonical_md5=cmd5,
                live_md5=lmd5,
            ))

    return r


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def format_human(r: Results) -> str:
    lines = []
    lines.append(
        f"preflight_parity: {r.rows_total} rows total, "
        f"{r.rows_checked} checked, {r.rows_exempt} exempt"
    )
    fails = r.failures
    if not fails:
        lines.append("  ✅ all checks passed")
    else:
        lines.append(f"  ❌ {len(fails)} failure(s):")
        for c in fails:
            lines.append(f"    [{c.check}] {c.row.monitor}/{c.row.slot}: {c.message}")
    return "\n".join(lines)


def format_json(r: Results) -> str:
    return json.dumps({
        "rows_total": r.rows_total,
        "rows_checked": r.rows_checked,
        "rows_exempt": r.rows_exempt,
        "failures": len(r.failures),
        "checks": [
            {
                "check": c.check,
                "monitor": c.row.monitor,
                "slot": c.row.slot,
                "category": c.row.category,
                "canonical_path": c.row.canonical_path,
                "live_path": c.row.live_path,
                "passed": c.passed,
                "message": c.message,
                "canonical_md5": c.canonical_md5,
                "live_md5": c.live_md5,
            }
            for c in r.checks
        ],
    }, indent=2)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--repo-root", default=".", help="Local repo root (default: cwd)")
    parser.add_argument("--manifest", default=None, help="Override manifest path")
    parser.add_argument("--other-root", default=None,
                        help="Override the non-local repo root (bypasses gh clone)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true",
                        help="Skip cross-repo clone; use --repo-root for both sides (fixture mode)")
    args = parser.parse_args(argv)

    repo_root = pathlib.Path(args.repo_root).resolve()

    try:
        local_side = detect_local_side(repo_root)
    except FileNotFoundError as e:
        print(f"preflight_parity: {e}", file=sys.stderr)
        return 2

    # Manifest path
    if args.manifest:
        manifest_path = pathlib.Path(args.manifest)
    else:
        manifest_rel = MANIFEST_INTERNAL if local_side == "internal" else MANIFEST_MAIN
        manifest_path = repo_root / manifest_rel
    if not manifest_path.is_file():
        print(f"preflight_parity: manifest not found at {manifest_path}", file=sys.stderr)
        return 2

    try:
        rows = parse_manifest(manifest_path)
    except Exception as e:  # noqa: BLE001 — parser must never traceback in CI
        print(f"preflight_parity: failed to parse manifest: {e}", file=sys.stderr)
        return 2

    # Resolve internal_root and main_root
    if args.self_test or args.other_root:
        # Either fixture mode (both sides same root) or dev override
        other_root = pathlib.Path(args.other_root).resolve() if args.other_root else repo_root
        if local_side == "internal":
            internal_root, main_root = repo_root, other_root
        else:
            internal_root, main_root = other_root, repo_root
    else:
        other_side: Side = "main" if local_side == "internal" else "internal"
        try:
            other_root = ensure_other_repo(other_side)
        except subprocess.CalledProcessError as e:
            print(f"preflight_parity: gh clone failed: {e.stderr or e}", file=sys.stderr)
            return 2
        if local_side == "internal":
            internal_root, main_root = repo_root, other_root
        else:
            internal_root, main_root = other_root, repo_root

    results = run_checks(rows, internal_root, main_root)

    if args.json:
        print(format_json(results))
    else:
        print(format_human(results))

    return 1 if results.any_failed() else 0


if __name__ == "__main__":
    sys.exit(main())

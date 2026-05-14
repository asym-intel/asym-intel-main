#!/usr/bin/env python3
"""
publisher_floor_gate.py — Layer A pre-commit gate for the publisher.

Called by the publisher BEFORE writing to the static site.  Reads
compose-latest.json and enforces minimum quality thresholds on the
weekly_brief_draft field so a sentinel or trivially-short brief cannot
propagate to the reader surface.

Usage
-----
    python3 publisher_floor_gate.py --compose-file <path> --slug <slug>
    python3 publisher_floor_gate.py --compose-file <path> --slug <slug> --min-length 1200

Exit codes
----------
    0 — all checks pass
    1 — one or more checks failed (details printed to stdout)

Gate calibration primitives used
---------------------------------
    None — this gate is stateless and unconditional by design.
    Recalibrate via --min-length if the 800-char floor is too strict for a
    particular deployment posture; default must not be lowered below 800.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Sentinel strings that indicate a placeholder rather than real content.
SENTINEL_STRINGS: frozenset[str] = frozenset(
    {
        "A",
        "No brief available this week.",
        "[BRIEF UNAVAILABLE]",
        "[ERROR]",
    }
)

DEFAULT_MIN_LENGTH: int = 800


def load_compose(path: Path) -> dict | None:
    """Load and return compose JSON, or None on missing / invalid file."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def run_gate(compose_path: Path, slug: str, min_length: int = DEFAULT_MIN_LENGTH) -> bool:
    """Run all floor-gate checks.

    Prints a PASS or FAIL line per check and returns True iff all pass.
    """
    tag = f"[{slug}]"

    compose = load_compose(compose_path)
    if compose is None:
        print(f"FLOOR GATE: FAIL {tag} compose artifact absent or invalid: {compose_path}")
        return False

    all_pass = True

    # ── Check 1: weekly_brief_draft present and a string ───────────────────
    brief = compose.get("weekly_brief_draft")
    if brief is None or not isinstance(brief, str):
        print(f"FLOOR GATE: FAIL {tag} weekly_brief_draft missing or not a string")
        all_pass = False
        # Cannot run length / sentinel checks without a string.
        brief = None

    # ── Check 2: length floor ───────────────────────────────────────────────
    if brief is not None:
        brief_len = len(brief)
        if brief_len < min_length:
            print(
                f"FLOOR GATE: FAIL {tag} brief={brief_len} chars"
                f" (floor={min_length})"
            )
            all_pass = False
        else:
            # Length check passed — will report at the end if all pass.
            pass

    # ── Check 3: sentinel detection ────────────────────────────────────────
    if brief is not None:
        stripped = brief.strip()
        if stripped == "" or stripped in SENTINEL_STRINGS:
            print(f"FLOOR GATE: FAIL {tag} brief matches sentinel string: {stripped!r}")
            all_pass = False

    # ── Check 4: _meta.cycle_disposition present ────────────────────────────
    meta = compose.get("_meta")
    if not isinstance(meta, dict) or not meta.get("cycle_disposition"):
        print(f"FLOOR GATE: FAIL {tag} _meta.cycle_disposition absent or empty")
        all_pass = False

    if all_pass:
        brief_len = len(brief) if brief is not None else 0
        print(f"FLOOR GATE: PASS {tag} brief={brief_len} chars")

    return all_pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-commit floor gate for the publisher."
    )
    parser.add_argument(
        "--compose-file",
        required=True,
        type=Path,
        help="Path to compose-latest.json (or a dated compose JSON).",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Monitor slug, used in log output (e.g. european-strategic-autonomy).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=DEFAULT_MIN_LENGTH,
        help=f"Minimum character count for weekly_brief_draft (default: {DEFAULT_MIN_LENGTH}).",
    )
    args = parser.parse_args()

    passed = run_gate(args.compose_file, args.slug, min_length=args.min_length)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
check_module_provenance.py — module-level null-signal provenance auditor.

Scans monitor `report-latest.json` artefacts (or any caller-supplied report
files) for top-level ``module_<n>`` objects that are structurally empty but
do not carry the publisher's null-signal provenance contract
(``null_signal`` + ``empty_reason``). The same rule the publisher already
enforces at write time (see ``pipeline/publishers/publisher.py``
``_find_unprovenanced_empty_modules``) — exposed here as a stand-alone CLI
so we can audit historical artefacts and run the gate outside a publish.

Usage::

    # Audit every commons monitor (default)
    python tools/check_module_provenance.py

    # Audit a single artefact (used by tests / spot checks)
    python tools/check_module_provenance.py --report path/to/report-latest.json

    # Machine-readable failure list
    python tools/check_module_provenance.py --json

Exit code is 0 when every audited report is clean, 1 when any report has
unprovenanced empty modules, 2 on hard I/O / parse errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
# Reuse the publisher's pure helpers — single source of truth for what
# "structurally empty" and "has provenance" mean.
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "publishers"))
from publisher import (  # noqa: E402
    _find_unprovenanced_empty_modules,
    _module_body_is_empty,
)

DEFAULT_GLOB = "docs/monitors/*/data/report-latest.json"


def _slug_from_path(path: Path) -> str:
    """Best-effort monitor slug extraction from a docs/monitors/<slug>/data path."""
    parts = path.parts
    if "monitors" in parts:
        i = parts.index("monitors")
        if i + 1 < len(parts):
            return parts[i + 1]
    return path.stem


def audit_report(report: dict) -> list[str]:
    """Return module keys that are structurally empty but lack provenance."""
    return _find_unprovenanced_empty_modules(report)


def audit_path(path: Path) -> dict:
    """Audit one report file and return a result record.

    Returns a dict with keys: path, slug, ok, empty_unprovenanced, error.
    `ok` is True when the file parsed and contained no unprovenanced empty
    modules. `error` is non-empty only on I/O or JSON-parse failures.
    """
    record = {
        "path": str(path),
        "slug": _slug_from_path(path),
        "ok": False,
        "empty_unprovenanced": [],
        "error": "",
    }
    try:
        with path.open("r", encoding="utf-8") as fh:
            report = json.load(fh)
    except FileNotFoundError:
        record["error"] = "file_not_found"
        return record
    except json.JSONDecodeError as e:
        record["error"] = f"json_parse_error: {e}"
        return record
    except OSError as e:  # pragma: no cover — surfaces e.g. permission errors
        record["error"] = f"os_error: {e}"
        return record
    if not isinstance(report, dict):
        record["error"] = "report_not_object"
        return record
    record["empty_unprovenanced"] = audit_report(report)
    record["ok"] = not record["empty_unprovenanced"]
    return record


def discover_reports(repo_root: Path) -> list[Path]:
    """Return every commons report-latest.json under docs/monitors/."""
    return sorted(repo_root.glob(DEFAULT_GLOB))


def _format_text(records: Iterable[dict]) -> str:
    lines: list[str] = []
    fail_count = 0
    err_count = 0
    total = 0
    for rec in records:
        total += 1
        if rec["error"]:
            err_count += 1
            lines.append(f"ERROR  {rec['slug']:32s}  {rec['error']}  ({rec['path']})")
            continue
        if rec["ok"]:
            lines.append(f"PASS   {rec['slug']:32s}  no unprovenanced empty modules")
            continue
        fail_count += 1
        modules = ", ".join(rec["empty_unprovenanced"])
        lines.append(
            f"FAIL   {rec['slug']:32s}  unprovenanced empty modules: {modules}"
        )
    lines.append("")
    lines.append(f"audited={total} pass={total - fail_count - err_count} fail={fail_count} error={err_count}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    parser.add_argument(
        "--report",
        action="append",
        default=[],
        metavar="PATH",
        help="Audit a specific report file. May be passed multiple times. "
        "If omitted, audits every commons report-latest.json under "
        f"{DEFAULT_GLOB}.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repo root used for default discovery (default: this checkout).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human-readable text.",
    )
    args = parser.parse_args(argv)

    if args.report:
        paths = [Path(p) for p in args.report]
    else:
        paths = discover_reports(Path(args.repo_root))

    if not paths:
        print(f"No reports found (searched: {DEFAULT_GLOB} under {args.repo_root})",
              file=sys.stderr)
        return 2

    records = [audit_path(p) for p in paths]

    if args.json:
        out = {
            "audited": len(records),
            "fail_count": sum(1 for r in records if not r["ok"] and not r["error"]),
            "error_count": sum(1 for r in records if r["error"]),
            "results": records,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(_format_text(records))

    if any(r["error"] for r in records):
        return 2
    if any(not r["ok"] for r in records):
        return 1
    return 0


__all__ = [
    "audit_path",
    "audit_report",
    "discover_reports",
    "main",
    "_module_body_is_empty",
    "_find_unprovenanced_empty_modules",
]


if __name__ == "__main__":
    sys.exit(main())

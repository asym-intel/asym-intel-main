#!/usr/bin/env python3
"""
engine_smoke_test.py — Layer B North Star post-deploy smoke test.

Run after deployment to verify real content is live on each monitor's
reader URL.  Uses only stdlib (urllib.request); no third-party dependencies.

Gates implemented
-----------------
    GATE-P3-BRIEF-PRESENT  HTTP 200 + response body >= 5000 chars.
    GATE-P3-NORTH-STAR     Body has <h1>/<h2> tags AND no sentinel strings.

Note: GATE-P3-KB-WRITE is NOT in this script — that gate reads
persistent-state.json from the repo and lives in a separate tool.

Usage
-----
    # Single monitor
    python3 engine_smoke_test.py --monitor european-strategic-autonomy \\
        --reader-url https://asym-intel.info/monitors/european-strategic-autonomy/report.html

    # All 7 monitors (hardcoded reader URLs)
    python3 engine_smoke_test.py --all

Exit codes
----------
    0 — all checks pass
    1 — one or more monitors failed
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
import urllib.error
from typing import NamedTuple

# ── Hardcoded monitor list ──────────────────────────────────────────────────
MONITOR_URLS: dict[str, str] = {
    "european-strategic-autonomy": (
        "https://asym-intel.info/monitors/european-strategic-autonomy/report.html"
    ),
    "ai-governance": (
        "https://asym-intel.info/monitors/ai-governance/report.html"
    ),
    "fimi-cognitive-warfare": (
        "https://asym-intel.info/monitors/fimi-cognitive-warfare/report.html"
    ),
    "macro-monitor": (
        "https://asym-intel.info/monitors/macro-monitor/report.html"
    ),
    "democratic-integrity": (
        "https://asym-intel.info/monitors/democratic-integrity/report.html"
    ),
    "environmental-risks": (
        "https://asym-intel.info/monitors/environmental-risks/report.html"
    ),
    "conflict-escalation": (
        "https://asym-intel.info/monitors/conflict-escalation/report.html"
    ),
}

# Sentinel strings that must NOT appear in a live page.
SENTINEL_PATTERNS: tuple[str, ...] = (
    "No brief available this week.",
    "A</h",  # single-char brief leaking into a heading close tag
)

BODY_MIN_CHARS: int = 5000
REQUEST_TIMEOUT_SECONDS: int = 20


class GateResult(NamedTuple):
    slug: str
    url: str
    gate_brief_present: bool   # GATE-P3-BRIEF-PRESENT
    gate_north_star: bool      # GATE-P3-NORTH-STAR
    http_status: int | None
    body_length: int
    failure_reasons: list[str]


def fetch_page(url: str) -> tuple[int | None, str]:
    """Fetch URL; return (status_code, body_text). Body is empty string on error."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "asym-intel-smoke-test/1.0"},
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception:
        return None, ""


def check_monitor(slug: str, url: str) -> GateResult:
    """Run both gates for one monitor and return a GateResult."""
    status, body = fetch_page(url)
    body_len = len(body)
    reasons: list[str] = []

    # ── GATE-P3-BRIEF-PRESENT ───────────────────────────────────────────────
    brief_present = status == 200 and body_len >= BODY_MIN_CHARS
    if status != 200:
        reasons.append(f"HTTP {status} (expected 200)")
    elif body_len < BODY_MIN_CHARS:
        reasons.append(f"body too short: {body_len} chars (floor={BODY_MIN_CHARS})")

    # ── GATE-P3-NORTH-STAR ──────────────────────────────────────────────────
    has_heading = "<h1>" in body or "<h2>" in body or "<H1>" in body or "<H2>" in body
    sentinel_hit: str | None = None
    for pattern in SENTINEL_PATTERNS:
        if pattern in body:
            sentinel_hit = pattern
            break

    north_star = has_heading and sentinel_hit is None
    if not has_heading:
        reasons.append("no <h1>/<h2> heading found in body")
    if sentinel_hit is not None:
        reasons.append(f"sentinel string detected: {sentinel_hit!r}")

    return GateResult(
        slug=slug,
        url=url,
        gate_brief_present=brief_present,
        gate_north_star=north_star,
        http_status=status,
        body_length=body_len,
        failure_reasons=reasons,
    )


def print_table(results: list[GateResult]) -> None:
    """Print a fixed-width summary table to stdout."""
    col_slug = max(len(r.slug) for r in results)
    header = (
        f"{'MONITOR':<{col_slug}}  {'HTTP':>4}  {'BODY':>7}  "
        f"{'BRIEF-PRESENT':>13}  {'NORTH-STAR':>10}  ISSUES"
    )
    print(header)
    print("-" * len(header))
    for r in results:
        status_str = str(r.http_status) if r.http_status is not None else "ERR"
        bp = "PASS" if r.gate_brief_present else "FAIL"
        ns = "PASS" if r.gate_north_star else "FAIL"
        issues = "; ".join(r.failure_reasons) if r.failure_reasons else "—"
        print(
            f"{r.slug:<{col_slug}}  {status_str:>4}  {r.body_length:>7}  "
            f"{bp:>13}  {ns:>10}  {issues}"
        )


def run_single(slug: str, url: str) -> bool:
    """Check one monitor; print result and return True iff all gates pass."""
    result = check_monitor(slug, url)
    all_pass = result.gate_brief_present and result.gate_north_star
    if all_pass:
        print(
            f"SMOKE TEST: PASS [{slug}] "
            f"HTTP {result.http_status} body={result.body_length} chars"
        )
    else:
        for reason in result.failure_reasons:
            print(f"SMOKE TEST: FAIL [{slug}] {reason}")
    return all_pass


def run_all() -> bool:
    """Check all 7 monitors; print table and return True iff all pass."""
    results = [check_monitor(slug, url) for slug, url in MONITOR_URLS.items()]
    print_table(results)
    any_fail = any(not (r.gate_brief_present and r.gate_north_star) for r in results)
    return not any_fail


def main() -> None:
    parser = argparse.ArgumentParser(
        description="North Star smoke test — verifies live monitor reader pages."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--monitor",
        metavar="SLUG",
        help="Monitor slug to check (requires --reader-url).",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check all 7 monitors using hardcoded reader URLs.",
    )
    parser.add_argument(
        "--reader-url",
        metavar="URL",
        help="Reader URL (required when --monitor is used).",
    )
    args = parser.parse_args()

    if args.all:
        passed = run_all()
    else:
        if not args.reader_url:
            parser.error("--reader-url is required when --monitor is used")
        passed = run_single(args.monitor, args.reader_url)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

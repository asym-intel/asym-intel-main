#!/usr/bin/env python3
"""
ESA (European Strategic Autonomy) end-to-end smoke test.

Three named gates:
  GATE-P3-BRIEF-PRESENT  — HTTP 200 + body >= 5000 chars
  GATE-P3-NORTH-STAR     — heading tags present, no sentinel strings
  GATE-P3-KB-WRITE       — persistent-state.json updated within 14 days

Usage:
    python3 esa_smoke_test.py
    python3 esa_smoke_test.py --reader-url https://example.com/custom/path.html

Exit codes:
    0 — all gates PASS (GATE-P3-KB-WRITE WARN is treated as pass)
    1 — one or more gates FAIL
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

DEFAULT_READER_URL = (
    "https://asym-intel.info/monitors/european-strategic-autonomy/report.html"
)

PERSISTENT_STATE_PATH = (
    "static/monitors/european-strategic-autonomy/data/persistent-state.json"
)
REPO = "asym-intel/asym-intel-main"

SENTINEL_STRINGS = [
    "No brief available this week.",
    ">A<",
    ">A </",
]

KB_WRITE_WINDOW_DAYS = 14


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fetch_url(url: str) -> tuple[int, str]:
    """Return (status_code, body_text). On network error raises."""
    req = urllib.request.Request(url, headers={"User-Agent": "esa-smoke-test/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def gh_api(endpoint: str, extra_flags: list[str] | None = None) -> dict | list:
    """Run `gh api <endpoint>` and return parsed JSON."""
    cmd = ["gh", "api", endpoint] + (extra_flags or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"gh api {endpoint!r} failed (rc={result.returncode}): {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def gate_brief_present(url: str) -> tuple[str, str | None]:
    """
    GATE-P3-BRIEF-PRESENT
    HTTP GET the reader URL; expect 200 and body >= 5000 chars.
    Returns (status, reason_or_None) and also returns body for reuse.
    """
    try:
        status_code, body = fetch_url(url)
    except Exception as exc:
        return "FAIL", f"network error: {exc}", ""

    reasons = []
    if status_code != 200:
        reasons.append(f"HTTP {status_code} (expected 200)")
    if len(body) < 5000:
        reasons.append(f"body length {len(body)} < 5000 chars")

    if reasons:
        return "FAIL", "; ".join(reasons), body
    return "PASS", None, body


def gate_north_star(body: str) -> tuple[str, str | None]:
    """
    GATE-P3-NORTH-STAR
    Body must contain <h1> or <h2> (case-insensitive).
    Body must NOT contain any sentinel string.
    """
    reasons = []

    if not re.search(r"<h[12][\s>]", body, re.IGNORECASE):
        reasons.append("no <h1> or <h2> heading tag found in body")

    for sentinel in SENTINEL_STRINGS:
        if sentinel in body:
            reasons.append(f"sentinel string found: {sentinel!r}")

    if reasons:
        return "FAIL", "; ".join(reasons)
    return "PASS", None


def gate_kb_write() -> tuple[str, str | None]:
    """
    GATE-P3-KB-WRITE
    Checks whether persistent-state.json has been updated recently.

    1. Fetch the two most recent commits touching that file on main.
    2. Only 1 commit ever → WARN (never been updated after init).
    3. Most recent commit within 14 days → PASS.
    4. Most recent commit older than 14 days → FAIL.
    """
    endpoint = (
        f"repos/{REPO}/commits"
        f"?path={PERSISTENT_STATE_PATH}&per_page=2"
    )
    try:
        commits = gh_api(endpoint)
    except RuntimeError as exc:
        return "FAIL", str(exc)

    if not commits:
        return "FAIL", "no commits found for persistent-state.json — file may not exist"

    if len(commits) == 1:
        return (
            "WARN",
            "persistent-state.json has only one commit (never updated after init) "
            "— KB write pipeline not yet exercised",
        )

    # Most recent commit is commits[0]
    commit_date_str = (
        commits[0].get("commit", {}).get("committer", {}).get("date")
        or commits[0].get("commit", {}).get("author", {}).get("date")
    )
    if not commit_date_str:
        return "FAIL", "could not read commit date from gh api response"

    commit_date = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    age_days = (now - commit_date).days

    if age_days <= KB_WRITE_WINDOW_DAYS:
        return "PASS", None
    return (
        "FAIL",
        f"persistent-state.json not updated in >{KB_WRITE_WINDOW_DAYS} days "
        f"(last commit {age_days} days ago) — KB write pipeline may be broken",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ESA end-to-end smoke test (GATE-P3-*)"
    )
    parser.add_argument(
        "--reader-url",
        default=DEFAULT_READER_URL,
        help="Override the ESA report URL for testing",
    )
    args = parser.parse_args()

    overall_fail = False

    # --- GATE-P3-BRIEF-PRESENT ---
    bp_status, bp_reason, body = gate_brief_present(args.reader_url)
    if bp_status == "FAIL":
        print(f"GATE-P3-BRIEF-PRESENT: FAIL — {bp_reason}")
        overall_fail = True
    else:
        print("GATE-P3-BRIEF-PRESENT: PASS")

    # --- GATE-P3-NORTH-STAR (reuses body from above) ---
    if body:
        ns_status, ns_reason = gate_north_star(body)
    else:
        # If the fetch itself failed we have no body to evaluate
        ns_status, ns_reason = "FAIL", "no response body available (GATE-P3-BRIEF-PRESENT failed fetch)"

    if ns_status == "FAIL":
        print(f"GATE-P3-NORTH-STAR: FAIL — {ns_reason}")
        overall_fail = True
    else:
        print("GATE-P3-NORTH-STAR: PASS")

    # --- GATE-P3-KB-WRITE ---
    kb_status, kb_reason = gate_kb_write()
    if kb_status == "FAIL":
        print(f"GATE-P3-KB-WRITE: FAIL — {kb_reason}")
        overall_fail = True
    elif kb_status == "WARN":
        print(f"GATE-P3-KB-WRITE: WARN — {kb_reason}")
        # WARN is not a FAIL; exit 0
    else:
        print("GATE-P3-KB-WRITE: PASS")

    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())

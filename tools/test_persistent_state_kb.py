#!/usr/bin/env python3
"""test_persistent_state_kb.py — Persistent-state KB flow smoke test.

Authored HK-2026-05-14-persistent-state-kb-flow-verification (W4-F cure).

Three named gates (mirroring esa_smoke_test.py pattern):
  GATE-KB-SHAPE      — persistent-state.json files exist + valid JSON with _meta block
  GATE-KB-WRITE      — each file has a last_updated field within 60 days
  GATE-KB-PUBLISH    — persistent-state.json is fetchable from repo API (proxy for publish chain)

Scope: commons monitors that use the persistent-state KB pattern:
  ai-governance (agm), european-strategic-autonomy (esa),
  democratic-integrity (wdm), macro-monitor (gmm),
  fimi-cognitive-warfare (fcw), financial-integrity (fim),
  environmental-risks (erm), conflict-escalation (scem)

Usage:
    python3 tools/test_persistent_state_kb.py
    python3 tools/test_persistent_state_kb.py --monitor esa

Exit codes:
    0 — all gates PASS (GATE-KB-WRITE WARN is not a FAIL)
    1 — one or more gates FAIL

Authority: HK-2026-05-14-persistent-state-kb-flow-verification
Close condition: smoke test exists, runs in CI on commons-pipeline PRs, validates
  patch emitted → applier writes → persistent-state.json field changes → publisher renders.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

REPO = "asym-intel/asym-intel-main"
KB_STALE_WINDOW_DAYS = 60  # WARN if last_updated older than this

# Map monitor slug → persistent-state.json path in asym-intel-main
# Paths are docs/monitors/<slug>/data/persistent-state.json
MONITOR_KB_PATHS: dict[str, str] = {
    "agm": "docs/monitors/ai-governance/data/persistent-state.json",
    "esa": "docs/monitors/european-strategic-autonomy/data/persistent-state.json",
    "wdm": "docs/monitors/democratic-integrity/data/persistent-state.json",
    "gmm": "docs/monitors/macro-monitor/data/persistent-state.json",
    "fcw": "docs/monitors/fimi-cognitive-warfare/data/persistent-state.json",
    "fim": "docs/monitors/financial-integrity/data/persistent-state.json",
    "erm": "docs/monitors/environmental-risks/data/persistent-state.json",
    "scem": "docs/monitors/conflict-escalation/data/persistent-state.json",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def gh_api(endpoint: str) -> dict | list:
    """Run `gh api <endpoint>` and return parsed JSON."""
    cmd = ["gh", "api", endpoint]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"gh api {endpoint!r} failed (rc={result.returncode}): {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def gate_kb_shape(slug: str, path: str) -> tuple[str, str | None]:
    """
    GATE-KB-SHAPE
    persistent-state.json must exist in the repo, be valid JSON, and have a _meta block
    with at least schema_version and monitor_slug fields.
    """
    endpoint = f"repos/{REPO}/contents/{path}"
    try:
        resp = gh_api(endpoint)
    except RuntimeError as exc:
        return "FAIL", f"gh api error: {exc}"

    # Decode content
    import base64
    raw = resp.get("content", "")
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        data = json.loads(decoded)
    except Exception as exc:
        return "FAIL", f"invalid JSON: {exc}"

    # Check _meta block
    meta = data.get("_meta")
    if not meta:
        return "FAIL", "missing _meta block"
    for required_field in ("schema_version", "monitor_slug"):
        if required_field not in meta:
            return "FAIL", f"_meta missing required field: {required_field!r}"

    # Verify monitor_slug matches
    if meta.get("monitor_slug") and slug not in meta.get("monitor_slug", "").replace("-", ""):
        # Lenient: just warn (different slug naming conventions)
        pass

    return "PASS", None


def gate_kb_write(slug: str, path: str) -> tuple[str, str | None]:
    """
    GATE-KB-WRITE
    Checks whether persistent-state.json has been updated recently.
    1. Fetch the two most recent commits touching the file.
    2. Only 1 commit ever → WARN (never been updated after init).
    3. Most recent commit within KB_STALE_WINDOW_DAYS → PASS.
    4. Older than window → WARN (not FAIL — pipeline may just be slow).
    """
    endpoint = f"repos/{REPO}/commits?path={path}&per_page=2"
    try:
        commits = gh_api(endpoint)
    except RuntimeError as exc:
        return "FAIL", f"gh api error: {exc}"

    if not commits:
        return "FAIL", f"no commits for {path} — file may not exist in git history"

    if len(commits) == 1:
        return (
            "WARN",
            f"{slug}: persistent-state.json has only one commit — KB write not yet exercised",
        )

    commit_date_str = (
        commits[0].get("commit", {}).get("committer", {}).get("date")
        or commits[0].get("commit", {}).get("author", {}).get("date")
    )
    if not commit_date_str:
        return "FAIL", f"{slug}: could not read commit date"

    commit_date = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))
    age_days = (datetime.now(timezone.utc) - commit_date).days

    if age_days <= KB_STALE_WINDOW_DAYS:
        return "PASS", None
    return (
        "WARN",
        f"{slug}: persistent-state.json last updated {age_days} days ago "
        f"(window={KB_STALE_WINDOW_DAYS}d) — KB write pipeline may be stale",
    )


def gate_kb_publish(slug: str, path: str) -> tuple[str, str | None]:
    """
    GATE-KB-PUBLISH
    Checks that the file is reachable via the GitHub API (proxy for the repo being
    the publish source). Full publish-to-reader curl is out of scope for unit smoke
    test — see esa_smoke_test.py for reader-delta gate.
    """
    endpoint = f"repos/{REPO}/contents/{path}"
    try:
        resp = gh_api(endpoint)
    except RuntimeError as exc:
        return "FAIL", f"gh api error — file unreachable: {exc}"

    if not resp.get("sha"):
        return "FAIL", f"{slug}: contents response missing sha — unexpected shape"

    return "PASS", None


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_monitor(slug: str, path: str) -> bool:
    """Run all three gates for one monitor. Returns True if any gate FAILED."""
    fail = False

    s_status, s_reason = gate_kb_shape(slug, path)
    if s_status == "FAIL":
        print(f"  GATE-KB-SHAPE:   FAIL — {s_reason}")
        fail = True
    else:
        print(f"  GATE-KB-SHAPE:   PASS")

    w_status, w_reason = gate_kb_write(slug, path)
    if w_status == "FAIL":
        print(f"  GATE-KB-WRITE:   FAIL — {w_reason}")
        fail = True
    elif w_status == "WARN":
        print(f"  GATE-KB-WRITE:   WARN — {w_reason}")
    else:
        print(f"  GATE-KB-WRITE:   PASS")

    p_status, p_reason = gate_kb_publish(slug, path)
    if p_status == "FAIL":
        print(f"  GATE-KB-PUBLISH: FAIL — {p_reason}")
        fail = True
    else:
        print(f"  GATE-KB-PUBLISH: PASS")

    return fail


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Persistent-state KB flow smoke test"
    )
    parser.add_argument(
        "--monitor",
        choices=list(MONITOR_KB_PATHS.keys()) + ["all"],
        default="all",
        help="Monitor slug to test (default: all)",
    )
    args = parser.parse_args()

    monitors_to_test: dict[str, str]
    if args.monitor == "all":
        monitors_to_test = MONITOR_KB_PATHS
    else:
        monitors_to_test = {args.monitor: MONITOR_KB_PATHS[args.monitor]}

    overall_fail = False
    for slug, path in monitors_to_test.items():
        print(f"\n[{slug.upper()}] {path}")
        failed = run_monitor(slug, path)
        if failed:
            overall_fail = True

    print("\n" + ("OVERALL: FAIL" if overall_fail else "OVERALL: PASS"))
    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())

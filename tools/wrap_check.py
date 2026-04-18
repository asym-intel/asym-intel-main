#!/usr/bin/env python3
"""
wrap_check.py — mechanical gate for ENGINE-RULES §5 wrap protocol.

Computer MUST run this as the first action on any "wrap" trigger, for any engine
project (asym-intel, resilience, payments-gi, asymmetric-investor). The script
inspects repo state and emits the canonical wrap-summary template with
machine-measured fields pre-filled so Computer cannot self-report them.

Usage:
    python tools/wrap_check.py --project asym-intel
    python tools/wrap_check.py --project resilience
    python tools/wrap_check.py --project payments-gi
    python tools/wrap_check.py --project asymmetric-investor

Requires: `gh` CLI authenticated for the asym-intel org.

Exit codes:
    0 — all gates pass, wrap may proceed
    1 — thinning gate failed (notes file >12KB — HARD limit, no margin as of 17 Apr 2026)
    2 — staging gate failed (staging ahead of main, must merge before wrap)
    3 — script error (gh CLI missing, network failure, unknown project)
    4 — bug-log gate failed (bug-signal commits this session with no BUG-LOG entry) — hard from 2026-05-01

Version: 2.1 — 18 Apr 2026. Added gate_workspace_artifacts(): advisory scan of
/home/user/workspace/ for session-produced files that will be lost at session end
unless committed. v2.0 note: the 20% margin removed on 17 Apr. See wrap-enforcement log.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

# -------------------------------------------------------------------
# Project registry — where notes-for-computer.md lives for each project
# -------------------------------------------------------------------
PROJECTS = {
    "asym-intel": {
        "notes_repo": "asym-intel/asym-intel-internal",
        "notes_path": "notes-for-computer.md",
        "archive_path_fmt": "ops/notes-archive-{yyyy_mm}.md",
        "code_repo": "asym-intel/asym-intel-main",
        "staging_branch": "staging",
        "next_session_phrase": "Computer: asym-intel.info",
    },
    "resilience": {
        "notes_repo": "asym-intel/resilience",
        "notes_path": "ops/notes-for-computer.md",
        "archive_path_fmt": "ops/notes-archive-{yyyy_mm}.md",
        "code_repo": "asym-intel/resilience",
        "staging_branch": "staging",
        "next_session_phrase": "Computer: Resilience",
    },
    "payments-gi": {
        "notes_repo": "asym-intel/payments-gi",
        "notes_path": "ops/notes-for-computer.md",
        "archive_path_fmt": "ops/notes-archive-{yyyy_mm}.md",
        "code_repo": "asym-intel/payments-gi",
        "staging_branch": None,  # per COMPUTER-core.md — direct to main
        "next_session_phrase": "Computer: Payments",
    },
    "asymmetric-investor": {
        # Commercial product; session state lives in asym-intel-internal/commercial
        "notes_repo": "asym-intel/asym-intel-internal",
        "notes_path": "commercial/notes-for-computer-asymmetric-investor.md",
        "archive_path_fmt": "commercial/notes-archive-{yyyy_mm}.md",
        "code_repo": "asym-intel/asym-intel-internal",
        "staging_branch": None,
        "next_session_phrase": "Computer: Asymmetric Investor",
    },
}

SIZE_TARGET_BYTES = 12 * 1024          # 12 KB (ENGINE-RULES §5.3c) — HARD limit, no margin
# Note: the 20% margin that existed in v1 was removed on 17 Apr 2026 after sessions
# consistently landed in the 12–14.4 KB "grace band" and never returned to target.
# ENGINE-RULES §5.3 is now a cliff, not a slope. See wrap-enforcement session log.
SESSION_WINDOW_HOURS = 12               # "this session" = commits in last 12h

# ENGINE-RULES §1e — Bug Discovery Protocol
# Advisory from 2026-04-17 to 2026-04-30. Hard enforcement from 2026-05-01.
BUG_LOG_REPO = "asym-intel/asym-intel-internal"
BUG_LOG_PATH = "ops/BUG-LOG.md"
BUG_LOG_ENFORCEMENT_DATE = datetime(2026, 5, 1, tzinfo=timezone.utc)

# Phrases in commit messages that signal bug work. Lowercased match.
BUG_SIGNAL_PATTERNS = [
    r"\bfix:", r"\bbug:", r"\bbugfix\b", r"\bregression\b", r"\bresolves? #",
    r"\bfixes? #", r"\bclose[sd]? #", r"\bparse_error\b", r"\bbroken\b",
    r"\bfailing\b", r"\bnot publishing\b", r"\bnot working\b", r"\broot cause\b",
    r"\bschema mismatch\b", r"\bcrash\b", r"\bmis[- ]label\b",
]


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def gh(args: list[str]) -> str:
    """Run `gh` with args, return stdout as str. Raise on non-zero."""
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"gh failed: {' '.join(args)}\nstderr: {result.stderr.strip()}"
        )
    return result.stdout


def file_size_bytes(repo: str, path: str) -> int:
    """Return file size in bytes from GitHub Contents API."""
    out = gh(["api", f"/repos/{repo}/contents/{path}", "--jq", ".size"])
    return int(out.strip())


def file_line_count(repo: str, path: str) -> int:
    """Count lines in a file via raw download."""
    out = gh(["api", f"/repos/{repo}/contents/{path}", "--jq", ".content"])
    import base64
    decoded = base64.b64decode(out.strip()).decode("utf-8", errors="replace")
    return decoded.count("\n") + (0 if decoded.endswith("\n") else 1)


def last_commit_iso(repo: str, path: str) -> str | None:
    """Return ISO timestamp of last commit touching path, or None if file absent."""
    try:
        out = gh(
            [
                "api",
                f"/repos/{repo}/commits",
                "-X", "GET",
                "-f", f"path={path}",
                "-f", "per_page=1",
                "--jq", ".[0].commit.committer.date",
            ]
        )
        out = out.strip()
        return out if out else None
    except RuntimeError:
        return None


def compare_branches(repo: str, base: str, head: str) -> dict:
    """Return {ahead, behind, status} from GitHub compare API."""
    out = gh(
        [
            "api",
            f"/repos/{repo}/compare/{base}...{head}",
            "--jq", "{ahead: .ahead_by, behind: .behind_by, status: .status}",
        ]
    )
    return json.loads(out)


def recent_commits(repo: str, hours: int) -> list[dict]:
    """Return commits on default branch from the last `hours` hours."""
    since_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    since_iso = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = gh([
        "api", f"/repos/{repo}/commits",
        "-X", "GET",
        "-f", f"since={since_iso}",
        "-f", "per_page=100",
        "--jq", "[.[] | {sha: .sha[0:7], msg: .commit.message, date: .commit.committer.date}]",
    ])
    return json.loads(out or "[]")


def bug_log_entries_today(repo: str, path: str) -> list[str]:
    """Return list of BUG-LOG entry IDs dated today (UTC)."""
    try:
        out = gh(["api", f"/repos/{repo}/contents/{path}", "--jq", ".content"])
    except RuntimeError:
        return []
    import base64, re as _re
    content = base64.b64decode(out.strip()).decode("utf-8", errors="replace")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Entry IDs look like: BUG-2026-04-17-001
    matches = _re.findall(rf"BUG-{today}-\d{{3}}", content)
    return sorted(set(matches))


def open_prs(repo: str) -> list[dict]:
    out = gh(
        [
            "pr", "list",
            "--repo", repo,
            "--state", "open",
            "--json", "number,title,headRefName",
        ]
    )
    return json.loads(out)


# -------------------------------------------------------------------
# Gates
# -------------------------------------------------------------------
def gate_thinning(project: dict) -> tuple[CheckResult, dict]:
    """§5.3 — thinning gate. Fails if notes >12KB and no archive commit this session."""
    repo = project["notes_repo"]
    path = project["notes_path"]
    try:
        size = file_size_bytes(repo, path)
        lines = file_line_count(repo, path)
    except RuntimeError as e:
        return (
            CheckResult("thinning", False, f"Could not fetch notes: {e}"),
            {"size": None, "lines": None},
        )

    now = datetime.now(timezone.utc)
    yyyy_mm = now.strftime("%Y-%m")
    archive_path = project["archive_path_fmt"].format(yyyy_mm=yyyy_mm)
    archive_last = last_commit_iso(repo, archive_path)

    session_cutoff = now - timedelta(hours=SESSION_WINDOW_HOURS)
    archive_this_session = False
    if archive_last:
        archive_dt = datetime.fromisoformat(archive_last.replace("Z", "+00:00"))
        archive_this_session = archive_dt >= session_cutoff

    detail = (
        f"{path}: {size} bytes / {lines} lines "
        f"(HARD limit {SIZE_TARGET_BYTES} bytes = 12 KB). "
        f"Archive {archive_path} last commit: "
        f"{archive_last or 'never'} "
        f"({'this session' if archive_this_session else 'not this session'})."
    )

    if size <= SIZE_TARGET_BYTES:
        return (
            CheckResult("thinning", True, detail + " Verdict: PASS."),
            {"size": size, "lines": lines, "archive_this_session": archive_this_session},
        )
    return (
        CheckResult(
            "thinning", False,
            detail
            + f" Verdict: FAIL — {size - SIZE_TARGET_BYTES} bytes over hard limit. "
            "Thin the file before wrap completes. Commit-time gate "
            "(.github/workflows/notes-size-gate.yml) will also block push.",
        ),
        {"size": size, "lines": lines, "archive_this_session": archive_this_session},
    )


def gate_staging(project: dict) -> CheckResult:
    """§5.4 — staging must be identical to or behind main."""
    if not project["staging_branch"]:
        return CheckResult(
            "staging", True, "No staging branch configured (per project policy)."
        )
    try:
        cmp = compare_branches(
            project["code_repo"], "main", project["staging_branch"]
        )
    except RuntimeError as e:
        return CheckResult("staging", False, f"Could not compare branches: {e}")
    if cmp["ahead"] == 0:
        return CheckResult(
            "staging", True,
            f"main...{project['staging_branch']}: {cmp['status']} "
            f"(ahead 0, behind {cmp['behind']}).",
        )
    return CheckResult(
        "staging", False,
        f"staging is ahead of main by {cmp['ahead']} commits. "
        f"Merge before wrap.",
    )


def gate_bug_log(project: dict) -> CheckResult:
    """§1e — every bug-signal commit this session must have a matching BUG-LOG entry.

    Advisory until 2026-05-01 (returns passed=True with warning detail).
    Hard from 2026-05-01 (returns passed=False on mismatch).
    """
    import re as _re
    now = datetime.now(timezone.utc)
    enforced = now >= BUG_LOG_ENFORCEMENT_DATE
    phase = "ENFORCED" if enforced else "ADVISORY"

    # 1. Scan recent commits in the project's code repo for bug-signal phrases.
    try:
        commits = recent_commits(project["code_repo"], SESSION_WINDOW_HOURS)
    except RuntimeError as e:
        return CheckResult(
            "bug_log", True,
            f"[{phase}] Could not fetch recent commits ({e}) — skipping bug-signal scan.",
        )

    signal_commits = []
    for c in commits:
        msg_lower = c["msg"].lower()
        for pat in BUG_SIGNAL_PATTERNS:
            if _re.search(pat, msg_lower):
                signal_commits.append(c)
                break

    # 2. Check BUG-LOG for entries dated today.
    entries_today = bug_log_entries_today(BUG_LOG_REPO, BUG_LOG_PATH)

    # 3. Verdict.
    if not signal_commits:
        return CheckResult(
            "bug_log", True,
            f"[{phase}] No bug-signal commits in last {SESSION_WINDOW_HOURS}h. "
            f"BUG-LOG entries today: {len(entries_today)}.",
        )

    commit_lines = "\n".join(
        f"    {c['sha']} {c['msg'].splitlines()[0][:80]}" for c in signal_commits
    )
    if entries_today:
        return CheckResult(
            "bug_log", True,
            f"[{phase}] {len(signal_commits)} bug-signal commit(s), "
            f"{len(entries_today)} BUG-LOG entr(y/ies) today ({', '.join(entries_today)}). "
            f"Verify every bug is logged:\n{commit_lines}",
        )

    # Signal commits exist, no BUG-LOG entries today.
    detail = (
        f"[{phase}] {len(signal_commits)} bug-signal commit(s) this session with "
        f"NO BUG-LOG entries today:\n{commit_lines}\n"
        f"  File entries in {BUG_LOG_REPO}/{BUG_LOG_PATH} per ENGINE-RULES §1e, "
        f"or override with explicit line in wrap summary: "
        f'"Wrap: no BUG-LOG entry needed — [reason]"'
    )
    # Advisory: pass with warning. Enforced: fail.
    return CheckResult("bug_log", not enforced, detail)


def gate_open_prs(project: dict) -> CheckResult:
    """Advisory — lists open PRs for awareness, never fails."""
    try:
        prs = open_prs(project["code_repo"])
    except RuntimeError as e:
        return CheckResult("open_prs", True, f"Could not list PRs: {e}")
    if not prs:
        return CheckResult("open_prs", True, "No open PRs.")
    lines = [
        f"  #{p['number']} ({p['headRefName']}): {p['title']}" for p in prs
    ]
    return CheckResult(
        "open_prs", True,
        f"{len(prs)} open PR(s) — confirm intent to carry:\n" + "\n".join(lines),
    )


def gate_workspace_artifacts() -> CheckResult:
    """Workspace artifact safety gate — warns about uncommitted session documents.

    Scans /home/user/workspace/ for files that look like session-produced
    documents (.md, .py, .json, .txt, .csv, .yaml, .yml, .html) and are
    NOT inside known system/skill paths. These files are ephemeral — they
    live only for the duration of the session and will be silently lost when
    the session ends unless committed to a repo or explicitly shared.

    Always advisory (returns passed=True) — never a hard blocker, because
    not all workspace files need to be committed. But the gate surfaces them
    so Computer and Peter can make a conscious decision.
    """
    import pathlib

    SKIP_PREFIXES = [
        "/home/user/workspace/skills/",
        "/home/user/workspace/.git",
    ]
    EXTENSIONS = {".md", ".py", ".json", ".txt", ".csv", ".yaml", ".yml", ".html"}

    workspace = pathlib.Path("/home/user/workspace")
    if not workspace.exists():
        return CheckResult(
            "workspace_artifacts", True,
            "Workspace directory not found — skipping (not running in Computer sandbox)."
        )

    found = []
    for p in workspace.rglob("*"):
        if not p.is_file():
            continue
        p_str = str(p)
        if any(p_str.startswith(skip) for skip in SKIP_PREFIXES):
            continue
        if p.suffix not in EXTENSIONS:
            continue
        if p.name.startswith("."):
            continue
        try:
            rel = p.relative_to(workspace)
        except ValueError:
            rel = p
        found.append(str(rel))

    found.sort()

    if not found:
        return CheckResult(
            "workspace_artifacts", True,
            "No uncommitted workspace documents found."
        )

    lines = "\n".join(f"    {f}" for f in found)
    return CheckResult(
        "workspace_artifacts", True,
        f"[ADVISORY] {len(found)} workspace file(s) will be lost at session end unless "
        f"committed to a repo or already shared with Peter.\n"
        f"  Review each — commit, confirm ephemeral, or note in wrap summary:\n{lines}"
    )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project", required=True, choices=sorted(PROJECTS.keys()),
        help="Engine project being wrapped",
    )
    args = parser.parse_args()
    project = PROJECTS[args.project]

    now = datetime.now(timezone.utc)
    header = f"=== WRAP CHECK — {now.isoformat(timespec='seconds')} — {args.project} ==="

    # Run gates
    thin_result, thin_data = gate_thinning(project)
    staging_result = gate_staging(project)
    bug_log_result = gate_bug_log(project)
    prs_result = gate_open_prs(project)
    ws_result = gate_workspace_artifacts()

    print(header)
    print(f"\n[§5.3 Thinning] {'PASS' if thin_result.passed else 'FAIL'}")
    print(f"  {thin_result.detail}")
    print(f"\n[§5.4 Staging] {'PASS' if staging_result.passed else 'FAIL'}")
    print(f"  {staging_result.detail}")
    print(f"\n[§1e BUG-LOG] {'PASS' if bug_log_result.passed else 'FAIL'}")
    print(f"  {bug_log_result.detail}")
    print(f"\n[Open PRs] advisory")
    print(f"  {prs_result.detail}")
    print(f"\n[Workspace artifacts] advisory")
    print(f"  {ws_result.detail}")

    # Emit the canonical wrap-summary template
    size_str = f"{thin_data['size']}" if thin_data['size'] is not None else "?"
    lines_str = f"{thin_data['lines']}" if thin_data['lines'] is not None else "?"
    thin_line = (
        f"Thinning (§5.3): <before> → {size_str} bytes "
        f"(<before_lines> → {lines_str} lines). "
        f"Moved: <FILL blocks>. Promoted: <FILL follow-ups>."
    )
    if not thin_result.passed:
        thin_line = "Thinning (§5.3): FAIL — re-run §5.3 3a→3d then re-invoke wrap_check"

    print("\n--- Required wrap-summary (paste verbatim, fill <FILL> fields) ---")
    print("Incomplete work: <FILL — none | list>")
    print("This session shipped: <FILL — one line>")
    print(thin_line)
    staging_label = (
        "identical" if staging_result.passed and project["staging_branch"]
        else "n/a" if not project["staging_branch"]
        else "FAIL"
    )
    print(f"Staging: {staging_label}")
    print(f"next-session.md updated — start next session with: {project['next_session_phrase']}")
    print("--- End wrap-summary ---")
    print(f"\n=== END WRAP CHECK ===")

    # Exit code
    if not thin_result.passed:
        return 1
    if not staging_result.passed:
        return 2
    if not bug_log_result.passed:
        return 4
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f"[wrap_check error] {e}", file=sys.stderr)
        sys.exit(3)

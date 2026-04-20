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

Version: 2.3 — 20 Apr 2026 (evening). Added gate_next_session_freshness():
advisory check that warns if next-session.md "Primary task" still names an AD
that landed in this session (i.e. a wrap from yesterday forgot to promote the
next task, so the boot prompt is stale). Per AD-2026-04-20g, in response to
the live failure observed at boot 2026-04-20: yesterday's wrap landed
AD-2026-04-20c/d/e but next-session.md still pointed at "Implement R-1, R-2,
R-8" — i.e. the trio that had just been completed. Computer detected the
staleness manually at boot; the gate now catches it at wrap.

v2.2 — 20 Apr 2026. Project registry moved out of this file to
`asym-intel-internal/ops/engine-projects.json` (single source of truth for all
engine tooling). Registry fetched at startup; local cache fallback in
`ops/engine-projects.json` (asym-intel-main root-relative path resolved from
this script's location).

New flags: `--list-projects` prints the registry and exits 0. Used by CI drift
checks to assert parity with the COMPUTER-SKILL.md trigger table.

Rationale (AD-2026-04-20d, R-2 audit fix):
  - Hardcoded PROJECTS dict was missing `advennt` and `Ramparts`, so any wrap
    from those projects failed at argparse. The drift was a category-1
    enforcement gap per AUDIT-SCOPE-v2 RECOMMENDATIONS.md C-014.
  - Moving the registry to a canonical JSON means one file to edit when a new
    project joins the engine, and future tooling (CI drift checks, adversarial
    reviewer, per-project smoke tests) reads the same file.

v2.1 — 18 Apr 2026. Added gate_workspace_artifacts(): advisory scan of
/home/user/workspace/ for session-produced files that will be lost at session end
unless committed. v2.0 note: the 20% margin removed on 17 Apr. See wrap-enforcement log.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -------------------------------------------------------------------
# Project registry — loaded from canonical source
# -------------------------------------------------------------------
# Source of truth: asym-intel-internal/ops/engine-projects.json
# This script fetches via `gh api` at startup. If the fetch fails (offline,
# auth missing, rate-limit) it falls back to a local cache file at
# ./engine-projects-cache.json next to this script. The cache is refreshed
# on every successful fetch.

PROJECTS_REPO = "asym-intel/asym-intel-internal"
PROJECTS_PATH = "ops/engine-projects.json"
_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_CACHE = _SCRIPT_DIR / "engine-projects-cache.json"


def _load_projects_via_gh() -> dict:
    """Fetch ops/engine-projects.json from the internal repo via gh."""
    out = subprocess.run(
        ["gh", "api", f"/repos/{PROJECTS_REPO}/contents/{PROJECTS_PATH}", "--jq", ".content"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"gh api failed: {out.stderr.strip()}")
    decoded = base64.b64decode(out.stdout.strip()).decode("utf-8")
    return json.loads(decoded)


def _load_projects() -> dict:
    """Load project registry. Prefer live fetch; fall back to local cache."""
    try:
        data = _load_projects_via_gh()
        # Refresh cache on successful fetch
        try:
            PROJECTS_CACHE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass  # cache refresh is best-effort
        return data["projects"]
    except (RuntimeError, KeyError, json.JSONDecodeError) as exc:
        if PROJECTS_CACHE.exists():
            try:
                data = json.loads(PROJECTS_CACHE.read_text(encoding="utf-8"))
                print(
                    f"[wrap_check] registry fetch failed ({exc}); using cache at {PROJECTS_CACHE}",
                    file=sys.stderr,
                )
                return data["projects"]
            except (OSError, KeyError, json.JSONDecodeError) as exc2:
                raise RuntimeError(
                    f"registry fetch failed ({exc}) and cache unreadable ({exc2})"
                ) from exc
        raise RuntimeError(
            f"registry fetch failed ({exc}) and no cache at {PROJECTS_CACHE}"
        ) from exc


# Loaded lazily in main() so --help works without network.
PROJECTS: dict = {}

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

# next-session.md freshness gate (AD-2026-04-20g, advisory).
# The path is currently hardcoded for the asym-intel project only — the only
# project where the prompt-file convention is known and stable. Other projects
# do not yet have a documented next-session.md path; generalising the gate is a
# follow-up. When the path moves into engine-projects.json (per-project
# `next_session_path` key) the hardcode goes away.
NEXT_SESSION_REPO = "asym-intel/asym-intel-internal"
NEXT_SESSION_PATH = "docs/prompts/next-session.md"
# Match AD IDs of the form AD-YYYY-MM-DD or AD-YYYY-MM-DDx (single suffix letter).
AD_ID_PATTERN = r"AD-\d{4}-\d{2}-\d{2}[a-z]?"
# The "Primary task" block starts at the H2 header containing that phrase and
# ends at the next H2. Captured non-greedily.
PRIMARY_TASK_BLOCK_PATTERN = (
    r"##\s*Primary task[^\n]*\n(.*?)(?=\n## |\Z)"
)

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


def gate_next_session_freshness(project_name: str) -> CheckResult:
    """Advisory gate — warns if next-session.md Primary task references an AD
    that landed in this session window.

    Heuristic: for each AD ID found in commit messages on the internal repo in
    the last SESSION_WINDOW_HOURS, check whether the same AD ID appears in the
    next-session.md "Primary task" block. If yes, the prompt is stale — it is
    instructing the next session to do work that just landed.

    Limitation: only runs for the 'asym-intel' project (others have no known
    prompt path yet). Always advisory — returns passed=True.

    Per AD-2026-04-20g — closes the wrap-hygiene gap observed at 2026-04-20
    boot when next-session.md still pointed at the just-landed R-1/R-2/R-8 trio.
    """
    import re as _re

    if project_name != "asym-intel":
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] Skipped — prompt-path convention not yet documented for "
            f"project '{project_name}'. Gate currently runs for asym-intel only.",
        )

    # 1. Collect AD IDs from session-window commits on the internal repo.
    try:
        commits = recent_commits(NEXT_SESSION_REPO, SESSION_WINDOW_HOURS)
    except RuntimeError as e:
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] Could not fetch commits ({e}) — skipping freshness check.",
        )

    landed_ads: set[str] = set()
    for c in commits:
        for match in _re.findall(AD_ID_PATTERN, c["msg"]):
            landed_ads.add(match)

    if not landed_ads:
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] No AD IDs in last {SESSION_WINDOW_HOURS}h of commits — "
            f"freshness check skipped (nothing to compare).",
        )

    # 2. Fetch next-session.md.
    try:
        out = gh([
            "api", f"/repos/{NEXT_SESSION_REPO}/contents/{NEXT_SESSION_PATH}",
            "--jq", ".content",
        ])
    except RuntimeError as e:
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] Could not fetch {NEXT_SESSION_PATH} ({e}) — skipping.",
        )
    content = base64.b64decode(out.strip()).decode("utf-8", errors="replace")

    # 3. Extract the Primary task block.
    block_match = _re.search(PRIMARY_TASK_BLOCK_PATTERN, content, _re.DOTALL)
    if not block_match:
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] No '## Primary task' block found in {NEXT_SESSION_PATH} "
            f"— freshness check skipped (cannot locate task block to scan).",
        )
    primary_block = block_match.group(1)

    # 4. Look for any landed AD that appears in the Primary task block.
    stale_refs = sorted(ad for ad in landed_ads if ad in primary_block)

    if not stale_refs:
        return CheckResult(
            "next_session_freshness", True,
            f"[ADVISORY] {NEXT_SESSION_PATH} Primary task does not reference any "
            f"AD landed this session. Landed: {sorted(landed_ads)}. Verdict: FRESH.",
        )

    return CheckResult(
        "next_session_freshness", True,
        f"[ADVISORY] {NEXT_SESSION_PATH} Primary task references AD(s) that "
        f"landed in this session: {stale_refs}. "
        f"This usually means the prior wrap forgot to promote the next task, "
        f"so the boot prompt is stale. Rewrite the Primary task block before "
        f"closing wrap, then re-run wrap_check to confirm. "
        f"All landed ADs this window: {sorted(landed_ads)}.",
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
        "/home/user/workspace/skills/",        # platform skill cache — not session docs
        "/home/user/workspace/.git",            # git internals
        "/home/user/workspace/past_session_contexts/",  # platform-managed session memory
        "/home/user/workspace/tool_calls/",     # platform tool call I/O scratch
    ]
    # Suffixes that indicate a session-produced document worth flagging
    EXTENSIONS = {".md", ".py", ".json", ".txt", ".csv", ".yaml", ".yml", ".html"}
    # Root-level files in the workspace are typically fetched working copies
    # (e.g. boot-context.md, patched workflow YAMLs) — not persistent outputs.
    # Only flag files that are at least one directory deep, since deliberate
    # session outputs (specs, audit reports, data files) always live in a subdir.
    MIN_DEPTH = 1  # must be inside at least one subdirectory

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
        # Skip root-level working copies
        if len(rel.parts) <= MIN_DEPTH:
            continue
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
    # NOTE: --project choices are populated after the registry is loaded below.
    parser.add_argument(
        "--project", required=False,
        help="Engine project being wrapped. Required unless --list-projects is passed.",
    )
    parser.add_argument(
        "--list-projects", action="store_true",
        help="Print the loaded project registry as JSON and exit 0. Used by CI drift checks.",
    )
    args = parser.parse_args()

    # Load registry (may hit network).
    global PROJECTS
    try:
        PROJECTS = _load_projects()
    except RuntimeError as exc:
        print(f"[wrap_check error] could not load project registry: {exc}", file=sys.stderr)
        return 3

    if args.list_projects:
        # Emit a stable, machine-readable listing so CI can diff it against other
        # sources of truth (e.g. the COMPUTER-SKILL.md trigger table).
        listing = {name: cfg.get("next_session_phrase") for name, cfg in PROJECTS.items()}
        print(json.dumps(listing, indent=2, sort_keys=True))
        return 0

    if not args.project:
        parser.error("--project is required (use --list-projects to see the registry)")
    if args.project not in PROJECTS:
        parser.error(
            f"unknown project '{args.project}'. Known: {', '.join(sorted(PROJECTS.keys()))}"
        )
    project = PROJECTS[args.project]

    now = datetime.now(timezone.utc)
    header = f"=== WRAP CHECK — {now.isoformat(timespec='seconds')} — {args.project} ==="

    # Run gates
    thin_result, thin_data = gate_thinning(project)
    staging_result = gate_staging(project)
    bug_log_result = gate_bug_log(project)
    prs_result = gate_open_prs(project)
    ws_result = gate_workspace_artifacts()
    freshness_result = gate_next_session_freshness(args.project)

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
    print(f"\n[next-session.md freshness] advisory")
    print(f"  {freshness_result.detail}")

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

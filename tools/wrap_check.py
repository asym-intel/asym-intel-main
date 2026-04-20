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

Version: 2.4 — 21 Apr 2026. Added gate_ad_chain(), gate_handover_sweep_needed(),
and gate_monthly_archive_rollover(). Per AD-2026-04-21b (P-12 Phase A, Tool 6)
— wrap-side gates for the three new failure classes covered by the Phase-A
boot/wrap tooling. All three are advisory (passed=True regardless of finding)
since the authoritative tools in tools/ already exit non-zero; wrap_check’s
job here is to raise the finding in the wrap board rather than gate the wrap.

v2.3 — 20 Apr 2026 (evening). Added gate_next_session_freshness():
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

# -------------------------------------------------------------------
# P-12 Phase A additions (v2.4) — boot-gate parity advisory gates
# -------------------------------------------------------------------
# All three new gates reach into the asym-intel-internal repo, since that
# is where the files they check (architectural-decisions.md, HANDOVER.md,
# gate-telemetry/) live. Each gate is ADVISORY: it never blocks the wrap.
# Authoritative enforcement lives in the standalone tools under tools/
# (validate_ad_chain.py, sweep_handover.py) which exit non-zero on failure.

AD_LOG_REPO = "asym-intel/asym-intel-internal"
AD_LOG_PATH = "ops/architectural-decisions.md"
HANDOVER_REPO = "asym-intel/asym-intel-internal"
HANDOVER_PATH = "ops/HANDOVER.md"
HANDOVER_SWEEP_AGE_DAYS = 30
HANDOVER_LINE_CAP = 300
TELEMETRY_REPO = "asym-intel/asym-intel-internal"
TELEMETRY_DIR = "ops/gate-telemetry"

# AD header patterns (kept in sync with tools/validate_ad_chain.py).
_AD_HDR_A = r"^#{1,2}\s+AD-(\d{4}-\d{2}-\d{2}[a-z]?(?:-\d+)?)\s*[—\-–]"
_AD_HDR_B = r"^#{1,2}\s+\d{4}-\d{2}-\d{2}\s*[—\-–]\s*AD-(\d{4}-\d{2}-\d{2}[a-z]?(?:-\d+)?)\s*[:\-]"


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
# P-12 Phase A (v2.4) gates — advisory only
# -------------------------------------------------------------------

def gate_ad_chain(project_name: str) -> CheckResult:
    """Advisory gate — reports structural problems in the AD log.

    Three failure classes detected (mirrors tools/validate_ad_chain.py):
      - duplicate: same AD ID appears under two distinct headers
      - dangling: `Retires: AD-X` names an ID that is not in the log
      - double_retire: same AD ID retired by two different live ADs

    Only runs for project 'asym-intel' — the AD log lives in the internal
    repo and the same log governs all engine projects. Always advisory
    (passed=True). Authoritative enforcement lives in tools/validate_ad_chain.py
    which exits non-zero. This gate surfaces the same finding in the wrap board
    so Computer notices at wrap time.

    Per AD-2026-04-21b (P-12 Phase A, Tool 6 — wrap-side parity).
    """
    import re as _re

    if project_name != "asym-intel":
        return CheckResult(
            "ad_chain", True,
            f"[ADVISORY] Skipped — AD log convention runs through asym-intel "
            f"project (checked there). Skipping for '{project_name}'.",
        )

    # 1. Fetch AD log.
    try:
        out = gh([
            "api", f"/repos/{AD_LOG_REPO}/contents/{AD_LOG_PATH}",
            "--jq", ".content",
        ])
    except RuntimeError as e:
        return CheckResult(
            "ad_chain", True,
            f"[ADVISORY] Could not fetch {AD_LOG_PATH} ({e}) — skipping AD chain check.",
        )
    try:
        content = base64.b64decode(out.strip()).decode("utf-8", errors="replace")
    except Exception as e:
        return CheckResult(
            "ad_chain", True,
            f"[ADVISORY] Could not decode {AD_LOG_PATH} ({e}) — skipping.",
        )

    # 2. Walk the log: find every AD header, then for each AD walk its body
    # until the next AD header, collecting the `**Retires:**` block and
    # extracting AD-IDs from it. Mirrors tools/validate_ad_chain.py block walk.
    hdr_a = _re.compile(_AD_HDR_A)
    hdr_b = _re.compile(_AD_HDR_B)
    ad_id_any = _re.compile(r"\bAD-(\d{4}-\d{2}-\d{2}[a-z]?(?:-\d+)?)\b")
    retires_marker = "**Retires:**"
    block_end_markers = (
        "**Signed off:**", "**Commit(s):**", "**Commit:**", "**Review:**",
        "**Tension log:**", "**Verification:**", "**Rollback:**", "**Status:**",
    )

    seen: dict[str, list[int]] = {}           # id -> [line numbers of headers]
    ad_ids_in_log: set[str] = set()
    retires_edges: list[tuple[str, str]] = []  # (retiring_ad_id, retired_ad_id)

    lines = content.splitlines()

    # Pass 1 — collect header positions.
    header_positions: list[tuple[int, str]] = []  # (line_index_0based, ad_id)
    for idx, line in enumerate(lines):
        m = hdr_a.match(line) or hdr_b.match(line)
        if m:
            ad_id = f"AD-{m.group(1)}"
            seen.setdefault(ad_id, []).append(idx + 1)
            ad_ids_in_log.add(ad_id)
            header_positions.append((idx, ad_id))

    # Pass 2 — for each AD, walk body to find Retires block and extract AD-IDs.
    for k, (hdr_idx, ad_id) in enumerate(header_positions):
        body_start = hdr_idx + 1
        body_end = header_positions[k + 1][0] if k + 1 < len(header_positions) else len(lines)
        # Find Retires marker within this AD's body.
        retires_start = None
        for j in range(body_start, body_end):
            if retires_marker in lines[j]:
                retires_start = j
                break
        if retires_start is None:
            continue
        # Walk from retires_start until block-end marker or next AD header.
        for j in range(retires_start, body_end):
            line = lines[j]
            stripped = line.lstrip()
            # Stop at another metadata marker (but not the Retires marker line itself).
            if j != retires_start and any(
                stripped.startswith(m) for m in block_end_markers
            ):
                break
            for mm in ad_id_any.finditer(line):
                rid = f"AD-{mm.group(1)}"
                if rid != ad_id:
                    retires_edges.append((ad_id, rid))

    # 3. Classify findings.
    duplicates = {aid: lns for aid, lns in seen.items() if len(lns) > 1}

    dangling = sorted({retired for _retiring, retired in retires_edges
                       if retired not in ad_ids_in_log})

    retired_count: dict[str, list[str]] = {}
    for retiring, retired in retires_edges:
        retired_count.setdefault(retired, []).append(retiring)
    double_retired = {aid: rs for aid, rs in retired_count.items() if len(rs) > 1}

    if not duplicates and not dangling and not double_retired:
        return CheckResult(
            "ad_chain", True,
            f"[ADVISORY] AD chain clean — {len(ad_ids_in_log)} AD(s) in log, "
            f"{len(retires_edges)} Retires edge(s), no duplicates / dangling / double-retires.",
        )

    parts: list[str] = [
        f"[ADVISORY] AD chain findings in {AD_LOG_PATH} "
        f"({len(ad_ids_in_log)} AD(s), {len(retires_edges)} Retires edge(s)):"
    ]
    if duplicates:
        for aid, lns in sorted(duplicates.items()):
            parts.append(f"  - DUPLICATE {aid} at lines {lns}")
    if dangling:
        parts.append(f"  - DANGLING Retires targets (not in log): {dangling}")
    if double_retired:
        for aid, retirers in sorted(double_retired.items()):
            parts.append(f"  - DOUBLE-RETIRED {aid} by {sorted(retirers)}")
    parts.append(
        "  Run `python3 tools/validate_ad_chain.py` for the authoritative verdict "
        "(non-zero exit on these classes)."
    )
    return CheckResult("ad_chain", True, "\n".join(parts))


def gate_handover_sweep_needed(project_name: str) -> CheckResult:
    """Advisory gate — warns if HANDOVER.md contains resolved entries older than
    HANDOVER_SWEEP_AGE_DAYS, or if the file is approaching the line cap.

    Heuristic for 'resolved + old':
      - Find `### YYYY-MM-DD — title` headers (skip obvious placeholders).
      - An entry is 'resolved' if its block contains a line matching
        `**Status:**` with `resolved|closed|done|complete` (case-insensitive).
      - An entry is 'old' if its header date is older than today − N days.

    Only runs for project 'asym-intel' (HANDOVER.md lives in the internal repo).
    Always advisory; authoritative sweep is tools/sweep_handover.py.

    Per AD-2026-04-21b (P-12 Phase A, Tool 6 — wrap-side parity).
    """
    import re as _re

    if project_name != "asym-intel":
        return CheckResult(
            "handover_sweep", True,
            f"[ADVISORY] Skipped — HANDOVER.md lives in asym-intel-internal; "
            f"not checked for project '{project_name}'.",
        )

    try:
        out = gh([
            "api", f"/repos/{HANDOVER_REPO}/contents/{HANDOVER_PATH}",
            "--jq", ".content",
        ])
    except RuntimeError as e:
        return CheckResult(
            "handover_sweep", True,
            f"[ADVISORY] Could not fetch {HANDOVER_PATH} ({e}) — skipping sweep check.",
        )
    try:
        content = base64.b64decode(out.strip()).decode("utf-8", errors="replace")
    except Exception as e:
        return CheckResult(
            "handover_sweep", True,
            f"[ADVISORY] Could not decode {HANDOVER_PATH} ({e}) — skipping.",
        )

    lines = content.splitlines()
    total_lines = len(lines)
    header_re = _re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\s*[—\-–]\s*(.+)$")
    status_re = _re.compile(r"^\*\*Status:\*\*\s*(.+)$", _re.IGNORECASE)
    resolved_words = _re.compile(r"\b(resolved|closed|done|complete[d]?)\b", _re.IGNORECASE)

    # Split the file into blocks keyed by header.
    blocks: list[tuple[str, str, list[str]]] = []  # (date_str, title, body_lines)
    current: tuple[str, str, list[str]] | None = None
    for line in lines:
        m = header_re.match(line)
        if m:
            if current is not None:
                blocks.append(current)
            date_str, title = m.group(1), m.group(2).strip()
            # Skip obvious placeholder entries.
            if title.lower().startswith(("placeholder", "example", "template")):
                current = None
                continue
            current = (date_str, title, [])
            continue
        if current is not None:
            current[2].append(line)
    if current is not None:
        blocks.append(current)

    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=HANDOVER_SWEEP_AGE_DAYS)
    stale_resolved: list[tuple[str, str]] = []

    for date_str, title, body in blocks:
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if entry_date > cutoff:
            continue
        # Look for a Status line indicating resolution.
        for bline in body:
            sm = status_re.match(bline.strip())
            if sm and resolved_words.search(sm.group(1)):
                stale_resolved.append((date_str, title))
                break

    warnings: list[str] = []
    if stale_resolved:
        warnings.append(
            f"{len(stale_resolved)} resolved entr(ies) older than "
            f"{HANDOVER_SWEEP_AGE_DAYS}d in {HANDOVER_PATH}:"
        )
        for date_str, title in stale_resolved[:5]:
            warnings.append(f"    - {date_str} — {title}")
        if len(stale_resolved) > 5:
            warnings.append(f"    ... and {len(stale_resolved) - 5} more")
        warnings.append(
            "  Run `python3 tools/sweep_handover.py` to archive these into "
            "ops/handover-archive-YYYY-MM.md."
        )

    if total_lines > HANDOVER_LINE_CAP:
        warnings.append(
            f"{HANDOVER_PATH} is {total_lines} lines "
            f"(cap {HANDOVER_LINE_CAP}) — sweep recommended regardless of age."
        )

    if not warnings:
        return CheckResult(
            "handover_sweep", True,
            f"[ADVISORY] {HANDOVER_PATH} OK — {total_lines} line(s), "
            f"no resolved entries older than {HANDOVER_SWEEP_AGE_DAYS}d.",
        )

    return CheckResult("handover_sweep", True, "[ADVISORY] " + "\n  ".join(warnings))


def gate_monthly_archive_rollover() -> CheckResult:
    """Advisory gate — on the 1st of a month, warn if the prior month's
    gate-telemetry JSONL has not yet been committed to ops/gate-telemetry/.

    The telemetry rollover is discipline-based (see ops/gate-telemetry/README.md).
    Each gate execution appends to `ops/gate-telemetry/YYYY-MM.jsonl`. When a new
    month starts, the prior file stops receiving writes. This gate detects the
    case where the rollover day has arrived but the prior month's file is not
    present in the repo (e.g. still only in a local workspace, or was never
    committed).

    Only active on the 1st–3rd of the month UTC (gives a small grace window).
    Always advisory.

    Per AD-2026-04-21b (P-12 Phase A, Tool 6 — wrap-side parity).
    """
    now = datetime.now(timezone.utc)
    if now.day > 3:
        return CheckResult(
            "telemetry_rollover", True,
            f"[ADVISORY] Not in rollover window (day {now.day} of month; "
            f"gate active days 1–3 UTC) — skipping.",
        )

    # Prior month stamp.
    first_of_this_month = now.replace(day=1)
    prior = first_of_this_month - timedelta(days=1)
    prior_stamp = prior.strftime("%Y-%m")
    prior_path = f"{TELEMETRY_DIR}/{prior_stamp}.jsonl"

    # Probe the file via `gh api`.
    try:
        gh([
            "api", f"/repos/{TELEMETRY_REPO}/contents/{prior_path}",
            "--jq", ".sha",
        ])
    except RuntimeError as e:
        msg = str(e).lower()
        if "not found" in msg or "404" in msg:
            return CheckResult(
                "telemetry_rollover", True,
                f"[ADVISORY] Rollover pending — {prior_path} not yet committed to "
                f"{TELEMETRY_REPO}. If gates ran in {prior_stamp} the local JSONL "
                f"must be committed before it is lost. Run the gate telemetry "
                f"review: `python3 tools/review_gate_telemetry.py --month {prior_stamp}`.",
            )
        return CheckResult(
            "telemetry_rollover", True,
            f"[ADVISORY] Could not probe {prior_path} ({e}) — skipping rollover check.",
        )

    return CheckResult(
        "telemetry_rollover", True,
        f"[ADVISORY] Rollover OK — {prior_path} present in {TELEMETRY_REPO}.",
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
    ad_chain_result = gate_ad_chain(args.project)
    handover_result = gate_handover_sweep_needed(args.project)
    rollover_result = gate_monthly_archive_rollover()

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
    print(f"\n[AD chain] advisory")
    print(f"  {ad_chain_result.detail}")
    print(f"\n[HANDOVER sweep] advisory")
    print(f"  {handover_result.detail}")
    print(f"\n[Telemetry rollover] advisory")
    print(f"  {rollover_result.detail}")

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

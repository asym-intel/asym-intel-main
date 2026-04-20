#!/usr/bin/env python3
"""
gh_put.py — atomic file commit via GitHub Contents API, race-safe.

Solves the SHA-race class of bugs where `gh api PUT` fails with 409 because the
blob SHA captured earlier has been invalidated by an intervening commit (either
by a concurrent GA workflow or an earlier commit in the same session).

Root cause addressed:
  - Stale SHA: blob SHA fetched before the PUT has been invalidated
  - Shell quoting: $SHA substitution fails inside nested heredocs

This helper refetches the SHA immediately before the PUT, uses python-native
JSON construction (no shell quoting), and retries on 409 with a fresh SHA up
to N times before surfacing the error.

Usage (as a library):

    from gh_put import gh_put
    gh_put(
        repo="asym-intel/asym-intel-internal",
        path="ops/ENGINE-RULES.md",
        content_path="/tmp/engine-rules-new.md",
        message="rules: §22 — Integrity Floor",
        branch="main",
    )

Usage (as a CLI):

    python3 gh_put.py \\
        --repo asym-intel/asym-intel-internal \\
        --path ops/ENGINE-RULES.md \\
        --content /tmp/engine-rules-new.md \\
        --message "rules: §22 — Integrity Floor"

Environment:
  GH_TOKEN must be set. In GA, use secrets.GH_TOKEN.

Exit codes:
  0  success (prints commit SHA to stdout)
  1  usage error
  2  API error after all retries
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 1.0


def _gh_api(args, input_data=None):
    """Thin wrapper around `gh api`. Returns (stdout, stderr, returncode)."""
    cmd = ["gh", "api"] + args
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


def _fetch_sha(repo: str, path: str, branch: str) -> str | None:
    """Fetch current blob SHA for path on branch. Returns None if file does not exist.

    NOTE: branch is embedded in the URL query string (?ref=), NOT passed via `-f`.
    `gh api -f key=value` implicitly switches the request to POST with form data,
    which for the Contents API GET endpoint returns a misleading 404. Learned
    the hard way on 17 April 2026 — caught by §1g failure-trigger check.
    """
    out, err, rc = _gh_api([
        f"/repos/{repo}/contents/{path}?ref={branch}",
        "--jq", ".sha",
    ])
    if rc != 0:
        if "404" in err or "Not Found" in err:
            return None
        raise RuntimeError(f"gh api fetch failed: {err.strip()}")
    return out.strip() or None


def gh_put(
    repo: str,
    path: str,
    content_path: str,
    message: str,
    branch: str = "main",
    max_retries: int = MAX_RETRIES,
) -> str:
    """
    Atomically PUT file content to GitHub, refetching SHA each attempt.
    Returns the new commit SHA on success. Raises RuntimeError on failure.
    """
    content_bytes = Path(content_path).read_bytes()
    encoded = base64.b64encode(content_bytes).decode()

    last_err = None
    for attempt in range(1, max_retries + 1):
        sha = _fetch_sha(repo, path, branch)

        body = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }
        if sha is not None:
            body["sha"] = sha

        body_path = f"/tmp/gh_put_body_{os.getpid()}.json"
        Path(body_path).write_text(json.dumps(body))

        out, err, rc = _gh_api(
            [f"/repos/{repo}/contents/{path}", "-X", "PUT", "--input", body_path,
             "--jq", ".commit.sha"],
        )

        try:
            os.unlink(body_path)
        except OSError:
            pass

        if rc == 0:
            return out.strip()

        last_err = err.strip()
        # 409 is the SHA race — retry with fresh SHA
        if "409" in err or "does not match" in err or "is at " in err:
            backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            print(f"  [gh_put] attempt {attempt}/{max_retries}: SHA race, retrying in {backoff:.1f}s",
                  file=sys.stderr)
            time.sleep(backoff)
            continue
        # Any other error: fail fast
        raise RuntimeError(f"gh api PUT failed ({rc}): {err.strip()}")

    raise RuntimeError(
        f"gh_put failed after {max_retries} attempts (last error: {last_err})"
    )


def _cli():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", required=True, help="owner/name, e.g. asym-intel/asym-intel-internal")
    p.add_argument("--path", required=True, help="file path in repo, e.g. ops/ENGINE-RULES.md")
    p.add_argument("--content", required=True, help="local path to file with new content")
    p.add_argument("--message", required=True, help="commit message")
    p.add_argument("--branch", default="main")
    p.add_argument("--max-retries", type=int, default=MAX_RETRIES)
    args = p.parse_args()

    try:
        commit_sha = gh_put(
            repo=args.repo,
            path=args.path,
            content_path=args.content,
            message=args.message,
            branch=args.branch,
            max_retries=args.max_retries,
        )
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    print(commit_sha)


if __name__ == "__main__":
    _cli()

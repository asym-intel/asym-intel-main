#!/usr/bin/env python3
"""
commit_exchange_log.py — Push pipeline exchange log to asym-intel-internal.

Called as the final step of each pipeline GA workflow AFTER the pipeline
script has run. Reads the local JSONL written by prompt_exchange_log.py,
groups records by (monitor, stage), and appends each group to the
corresponding monthly file in asym-intel-internal/archive/exchanges/.

Uses GitHub API with optimistic-concurrency retry (SHA-based).

Environment:
    GH_TOKEN          — PAT with write scope to asym-intel-internal
    GITHUB_RUN_ID     — propagated by GA (informational; already in records)

Input:
    pipeline/incidents/prompt-exchanges.jsonl   (written by log_exchange())

Exit codes:
    0 — success OR no records to commit (idempotent)
    1 — auth / permissions failure
    2 — transient failure after retries (non-fatal; pipeline continues)

This tool NEVER fails the overall workflow. Commit failures print a
WARNING and exit 0, on the principle that a broken archive must not
take down the pipeline that feeds it.
"""

import base64
import collections
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

# Archive repo configuration
ARCHIVE_REPO = "asym-intel/asym-intel-internal"
ARCHIVE_BASE = "archive/exchanges"

# Map monitor slug (as written by log_exchange) to short abbreviation
# for the archive path. Keeps archive paths short and stable.
MONITOR_SLUG_TO_ABBR = {
    "democratic-integrity":        "WDM",
    "macro-monitor":               "GMM",
    "european-strategic-autonomy": "ESA",
    "fimi-cognitive-warfare":      "FCW",
    "ai-governance":               "AGM",
    "environmental-risks":         "ERM",
    "conflict-escalation":         "SCEM",
    "financial-integrity":         "FIM",  # future
}

SOURCE_JSONL = pathlib.Path("pipeline/incidents/prompt-exchanges.jsonl")


class _ArchivePushError(Exception):
    """Internal signal that a push attempt failed — never propagates to caller."""


def _gh_request(method, path, token, data=None, etag=None):
    """Minimal GitHub API client — no third-party deps."""
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "asym-intel-exchange-archiver",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try:
            body_json = json.loads(body_text)
        except json.JSONDecodeError:
            body_json = {"message": body_text}
        return e.code, body_json


def _fetch_file(path, token):
    """Return (content_bytes, sha) or (None, None) if file does not exist."""
    status, body = _gh_request("GET", f"/repos/{ARCHIVE_REPO}/contents/{path}", token)
    if status == 404:
        return None, None
    if status != 200:
        # Non-fatal: caller will treat as "cannot write" and warn.
        raise _ArchivePushError(f"fetch {path} → {status}: {body}")
    content_b64 = body.get("content", "").replace("\n", "")
    content = base64.b64decode(content_b64) if content_b64 else b""
    return content, body.get("sha")


def _put_file(path, new_content_bytes, sha, token, message):
    """PUT a file, using sha for optimistic concurrency if provided."""
    data = {
        "message": message,
        "content": base64.b64encode(new_content_bytes).decode("ascii"),
    }
    if sha:
        data["sha"] = sha
    return _gh_request("PUT", f"/repos/{ARCHIVE_REPO}/contents/{path}", token, data=data)


def _append_to_archive(monitor_abbr, stage, records, token, *, run_id, max_retries=4):
    """Append records (list of dicts) to the monthly JSONL for this (monitor, stage)."""
    if not records:
        return True
    # Use month of the FIRST record to choose the file. Mid-month boundary edge
    # cases put a record at most one month "off" — acceptable.
    ts = records[0].get("ts", "")
    yyyymm = ts[:7] if len(ts) >= 7 else time.strftime("%Y-%m", time.gmtime())
    path = f"{ARCHIVE_BASE}/{monitor_abbr}/{stage}/{yyyymm}.jsonl"

    new_lines = b"".join(
        (json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8") for r in records
    )

    for attempt in range(1, max_retries + 1):
        try:
            existing, sha = _fetch_file(path, token)
        except _ArchivePushError as e:
            print(f"WARNING: archive fetch failed ({monitor_abbr}/{stage}): {e}")
            return False
        combined = (existing or b"") + new_lines
        msg = (
            f"archive({monitor_abbr.lower()}-{stage}): {len(records)} exchange(s) "
            f"from run {run_id}"
        )
        status, body = _put_file(path, combined, sha, token, msg)
        if status in (200, 201):
            print(
                f"ARCHIVE ✓ {monitor_abbr}/{stage}/{yyyymm}.jsonl "
                f"(+{len(records)} records, {len(new_lines)} bytes)"
            )
            return True
        if status == 409 or (status == 422 and "sha" in str(body).lower()):
            # SHA race — refetch and retry
            print(f"ARCHIVE retry {attempt}/{max_retries} ({monitor_abbr}/{stage}): sha race")
            time.sleep(0.5 * attempt)
            continue
        # Other failures: surface and stop retrying
        print(f"WARNING: archive push failed ({monitor_abbr}/{stage}): {status} {body}")
        return False
    print(f"WARNING: archive push exhausted retries ({monitor_abbr}/{stage})")
    return False


def main():
    if not SOURCE_JSONL.exists():
        print("ARCHIVE: no exchanges to commit (source file absent) — OK")
        return 0
    if SOURCE_JSONL.stat().st_size == 0:
        print("ARCHIVE: source file empty — OK")
        return 0

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("WARNING: GH_TOKEN not set — cannot push archive; pipeline continues.")
        return 0

    run_id = os.environ.get("GITHUB_RUN_ID", "local")

    # Group records by (monitor, stage)
    grouped = collections.defaultdict(list)
    bad_lines = 0
    for line in SOURCE_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            bad_lines += 1
            continue
        monitor_slug = rec.get("monitor", "")
        stage = rec.get("stage", "")
        abbr = MONITOR_SLUG_TO_ABBR.get(monitor_slug)
        if not abbr or not stage:
            bad_lines += 1
            continue
        grouped[(abbr, stage)].append(rec)

    if bad_lines:
        print(f"ARCHIVE: skipped {bad_lines} malformed lines")

    if not grouped:
        print("ARCHIVE: nothing to push after grouping")
        return 0

    print(f"ARCHIVE: pushing {sum(len(v) for v in grouped.values())} records "
          f"across {len(grouped)} (monitor,stage) buckets")

    all_ok = True
    for (abbr, stage), records in grouped.items():
        ok = _append_to_archive(abbr, stage, records, token, run_id=run_id)
        all_ok = all_ok and ok

    # Never fail the workflow over archive hiccups
    return 0 if all_ok else 0


if __name__ == "__main__":
    sys.exit(main())

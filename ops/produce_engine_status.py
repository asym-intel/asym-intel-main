#!/usr/bin/env python3
"""
ops/produce_engine_status.py

Reads the freshly-written public roll-up `static/ops/pipeline-status.json`
(produced by ops/update-pipeline-status.py earlier in this workflow) and
writes a single KV entry consumed by the admin.advennt.io EngineBanner via
/api/engine/status.

Sprint H Item 2 — engine status banner data wiring (AD-2026-04-30-BG).
Sprint BH disposition — engine-classifier convergence (AD-2026-04-30-BP):
this script is now a **thin reader** of the canonical classifier's output;
it does not re-classify. The single canonical engine classifier is
`ops/update-pipeline-status.py:_classify_monitor` (lines 892–972), whose
output is exposed in the public roll-up (schema v4.0+) under `engine.status`
and per-monitor `monitors[].status`.

Output shape — must match `EngineStatus` (less the `cached`/`fetched_at`/`source`
runtime fields) declared in:
  asym-intel/advennt-admin:src/pages/api/engine/status.ts

  {
    "engine": "green" | "amber" | "red" | "unknown",
    "last_updated": ISO8601 | null,
    "red_count":   <int>,
    "amber_count": <int>,
    "green_count": <int>
  }

Engine roll-up: read directly from `engine.status` in the public roll-up.
Per-monitor counts: tally `monitors[].status` ∈ {red, amber, green}.

Writes to KV via Cloudflare API:
  PUT /accounts/{ACCOUNT_ID}/storage/kv/namespaces/{KV_ID}/values/engine:status:latest

Environment:
  CF_API_TOKEN   — Cloudflare API token with KV write scope
                   (engine-standard: PPLX_COMPUTER_ASYM_ENGINE)
  CF_ACCOUNT_ID  — Cloudflare account id (passed by workflow)
  KV_NAMESPACE_ID — KV namespace id for ADMIN_PACKETS on advennt-admin Pages project
                    (passed by workflow)
  STATUS_PATH     — path to the freshly-written public roll-up
                    (default: static/ops/pipeline-status.json)
"""

import json
import os
import sys
import urllib.request
import urllib.error


def derive_status(data: dict) -> dict:
    """Read engine status from the public roll-up.

    The public roll-up (schema v4.0+) exposes the canonical classifier's
    output directly. This function is a thin reader, not a classifier
    (per AD-2026-04-30-BP: convergence on `update-pipeline-status.py:_classify_monitor`).

    Expected input shape:
      {
        "schema_version": "...",
        "generated_at": "...",
        "engine":   {"status": "red"|"amber"|"green", "last_updated": ISO8601|null},
        "monitors": [{"slug": "...", "status": "red"|"amber"|"green", ...}, ...],
        ...
      }
    """
    engine_block = data.get("engine") or {}
    if not isinstance(engine_block, dict):
        engine_block = {}
    engine = engine_block.get("status") or "unknown"
    last_updated = engine_block.get("last_updated")

    red = amber = green = 0
    monitors = data.get("monitors") or []
    if isinstance(monitors, list):
        for m in monitors:
            if not isinstance(m, dict):
                continue
            status = m.get("status")
            if status == "red":
                red += 1
            elif status == "amber":
                amber += 1
            elif status == "green":
                green += 1
            # Anything else (e.g. FIM-non-canonical states) is intentionally
            # not counted into the green/amber/red totals; the canonical
            # `engine.status` already accounts for them in its roll-up.

    return {
        "engine": engine,
        "last_updated": last_updated,
        "red_count": red,
        "amber_count": amber,
        "green_count": green,
    }


def put_kv(account_id: str, ns_id: str, key: str, value: str, token: str) -> None:
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/storage/kv/namespaces/{ns_id}/values/{key}"
    )
    req = urllib.request.Request(
        url,
        method="PUT",
        data=value.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"  KV PUT {key} -> HTTP {resp.status}")
            print(f"  body: {body}")
            if resp.status >= 300:
                sys.exit(f"KV write failed (HTTP {resp.status})")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        sys.exit(f"KV write failed: HTTP {e.code} {e.reason} — {body}")
    except urllib.error.URLError as e:
        sys.exit(f"KV write failed: URLError {e.reason}")


def main() -> int:
    status_path = os.environ.get("STATUS_PATH", "static/ops/pipeline-status.json")
    token = os.environ.get("CF_API_TOKEN")
    account_id = os.environ.get("CF_ACCOUNT_ID")
    ns_id = os.environ.get("KV_NAMESPACE_ID")

    missing = [
        n for n, v in [
            ("CF_API_TOKEN", token),
            ("CF_ACCOUNT_ID", account_id),
            ("KV_NAMESPACE_ID", ns_id),
        ] if not v
    ]
    if missing:
        sys.exit(f"missing required env: {', '.join(missing)}")

    if not os.path.exists(status_path):
        sys.exit(f"pipeline-status not found at {status_path}")

    with open(status_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    derived = derive_status(data)
    print("Derived engine status:")
    print(json.dumps(derived, indent=2))

    payload = json.dumps(derived, separators=(",", ":"))
    put_kv(account_id, ns_id, "engine:status:latest", payload, token)
    print("OK — engine:status:latest written")
    return 0


if __name__ == "__main__":
    sys.exit(main())

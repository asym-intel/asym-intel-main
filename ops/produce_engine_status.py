#!/usr/bin/env python3
"""
ops/produce_engine_status.py

Reads the freshly-written `static/ops/pipeline-status.json` (the public
roll-up produced by ops/update-pipeline-status.py earlier in this
workflow) and produces a single KV entry consumed by the admin.advennt.io
EngineBanner via /api/engine/status.

Sprint H Item 2 — engine status banner data wiring (AD-2026-04-30-BG).

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

Classifier (mirrors `classifyMonitor` in status.ts):
  red    if any station.last_conclusion == 'failure'
  amber  else if any station.last_conclusion == 'cancelled'
  green  otherwise

Engine roll-up:
  red    if red_count > 0
  amber  else if amber_count > 0
  green  otherwise

Skipped top-level keys (same as consumer): _meta, _verification, _incidents, _build.

Writes to KV via Cloudflare API:
  PUT /accounts/{ACCOUNT_ID}/storage/kv/namespaces/{KV_ID}/values/engine:status:latest

Environment:
  CF_API_TOKEN   — Cloudflare API token with KV write scope
                   (engine-standard: PPLX_COMPUTER_ASYM_ENGINE)
  CF_ACCOUNT_ID  — Cloudflare account id (passed by workflow)
  KV_NAMESPACE_ID — KV namespace id for ADMIN_PACKETS on advennt-admin Pages project
                    (passed by workflow)
  STATUS_PATH     — path to the freshly-written pipeline-status.json
                    (default: static/ops/pipeline-status.json)
"""

import json
import os
import sys
import urllib.request
import urllib.error

SKIP_KEYS = {"_meta", "_verification", "_incidents", "_build"}


def classify_monitor(stations: dict) -> str:
    has_failure = False
    has_cancelled = False
    for station in stations.values():
        if not isinstance(station, dict):
            continue
        c = station.get("last_conclusion")
        if c == "failure":
            has_failure = True
        elif c == "cancelled":
            has_cancelled = True
    if has_failure:
        return "red"
    if has_cancelled:
        return "amber"
    return "green"


def derive_status(data: dict) -> dict:
    red = amber = green = 0
    for key, value in data.items():
        if key in SKIP_KEYS:
            continue
        if not isinstance(value, dict):
            continue
        stations = value.get("stations")
        if not isinstance(stations, dict):
            continue
        colour = classify_monitor(stations)
        if colour == "red":
            red += 1
        elif colour == "amber":
            amber += 1
        else:
            green += 1

    if red > 0:
        engine = "red"
    elif amber > 0:
        engine = "amber"
    else:
        engine = "green"

    meta = data.get("_meta") or {}
    last_updated = meta.get("generated") if isinstance(meta, dict) else None

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

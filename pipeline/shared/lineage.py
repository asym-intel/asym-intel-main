"""
pipeline/shared/lineage.py — Lineage envelope writer for Asymmetric Intelligence engine.

Provides:
  - mint_ulid()            : stdlib ULID (no external deps)
  - content_sha256(obj)    : canonical JSON SHA-256 (sorted keys, no trailing whitespace)
  - build_envelope(...)    : construct a validated lineage-envelope dict
  - write_lineage_envelope(...) : write envelope to asym-intel-internal via GitHub Contents API

Internal-only. Envelopes are NEVER written to public paths (ENGINE-RULES §15/§16).
Archive path: asym-intel-internal/archive/lineage/{tenant}/{product}/{YYYY-MM-DD}.json

Dependencies: stdlib only (hashlib, os, time, json, base64, urllib, random).
"""

import base64
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional


# ── ULID (stdlib, no external deps) ────────────────────────────────────────
# Crockford base32 alphabet (uppercase, no I L O U)
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def mint_ulid() -> str:
    """
    Generate a ULID (Universally Unique Lexicographically Sortable Identifier).
    26 chars, Crockford base32. First 10 chars = 48-bit ms timestamp; last 16 = 80-bit random.
    Matches pattern ^[0-9A-HJKMNP-TV-Z]{26}$ required by lineage-envelope.schema.json.
    """
    # 48-bit millisecond timestamp
    ts_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF  # 48 bits

    # Encode 48-bit timestamp into 10 Crockford chars (each char = 5 bits)
    ts_chars = []
    t = ts_ms
    for _ in range(10):
        ts_chars.append(_CROCKFORD[t & 0x1F])
        t >>= 5
    ts_part = "".join(reversed(ts_chars))

    # 80-bit random into 16 Crockford chars
    rand_bytes = random.getrandbits(80)
    rand_chars = []
    r = rand_bytes
    for _ in range(16):
        rand_chars.append(_CROCKFORD[r & 0x1F])
        r >>= 5
    rand_part = "".join(reversed(rand_chars))

    return ts_part + rand_part


# ── Content SHA-256 ─────────────────────────────────────────────────────────

def content_sha256(obj) -> str:
    """
    Compute SHA-256 over canonical JSON serialisation: sorted keys, no trailing whitespace.
    Returns 'sha256:<hex64>' as required by lineage-envelope.schema.json output_hash pattern.
    """
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


# ── Envelope builder ─────────────────────────────────────────────────────────

def build_envelope(
    *,
    run_id: str,
    tenant: str,
    stage: str,
    product: str,
    schema_version: str,
    produced_at: str,
    input_artifact_ids: list,
    input_hashes: dict,
    output_obj,
    status: str = "published",
    git_sha: Optional[str] = None,
    supersedes: Optional[str] = None,
) -> dict:
    """
    Build a lineage envelope dict conforming to lineage-envelope.schema.json v1.0.

    Args:
        run_id            : ULID minted at pipeline entry (mint_ulid())
        tenant            : 'asym-intel' or 'advennt'
        stage             : 'collector'|'weekly_research'|'chatter'|'reasoner'|'synthesiser'|'publisher'
        product           : slug or jurisdiction code (e.g. 'macro-monitor', 'CA-ON')
        schema_version    : version of the OUTPUT artefact schema (e.g. '2.0') — not this envelope
        produced_at       : ISO-8601 UTC timestamp string
        input_artifact_ids: list of upstream run_ids (empty list for collector stage)
        input_hashes      : dict of {artifact_id: 'sha256:<hex>'} for consumed inputs
        output_obj        : the output artefact dict (used to compute output_hash)
        status            : lifecycle state (default 'published')
        git_sha           : optional git commit SHA (7-40 hex chars)
        supersedes        : optional prior run_id this envelope replaces
    """
    envelope = {
        "envelope_version": "1.0",
        "run_id": run_id,
        "tenant": tenant,
        "stage": stage,
        "product": product,
        "schema_version": schema_version,
        "produced_at": produced_at,
        "input_artifact_ids": input_artifact_ids,
        "input_hashes": input_hashes,
        "output_hash": content_sha256(output_obj),
        "status": status,
    }
    if git_sha is not None:
        envelope["git_sha"] = git_sha
    if supersedes is not None:
        envelope["supersedes"] = supersedes
    return envelope


# ── GitHub Contents API write ────────────────────────────────────────────────

_INTERNAL_REPO = "asym-intel/asym-intel-internal"
_LINEAGE_BASE = "archive/lineage"


def write_lineage_envelope(
    envelope: dict,
    *,
    tenant: str,
    product: str,
    date_str: str,
    token: Optional[str] = None,
) -> bool:
    """
    Write envelope JSON to asym-intel-internal/archive/lineage/{tenant}/{product}/{date_str}.json
    via GitHub Contents API (PUT).

    Uses LINEAGE_WRITE_TOKEN env var (or token arg). Falls back gracefully — never blocks publish.
    Returns True on success, False on failure (failure is logged, not raised).

    Race-safe: fetches current SHA before write, retries once on 409 Conflict.
    """
    write_token = token or os.environ.get("LINEAGE_WRITE_TOKEN") or os.environ.get("GH_TOKEN")
    if not write_token:
        print("  ⚠ lineage: no write token available (LINEAGE_WRITE_TOKEN / GH_TOKEN) — skipping")
        return False

    path = f"{_LINEAGE_BASE}/{tenant}/{product}/{date_str}.json"
    api_url = f"https://api.github.com/repos/{_INTERNAL_REPO}/contents/{path}"
    content_bytes = json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("ascii")

    headers = {
        "Authorization": f"token {write_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    def _get_sha() -> Optional[str]:
        """Fetch existing file SHA if it exists (needed for update vs create)."""
        req = urllib.request.Request(api_url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return data.get("sha")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # file doesn't exist yet — create
            raise

    def _put(sha: Optional[str]) -> bool:
        payload = {
            "message": f"lineage: {tenant}/{product} publisher envelope {date_str}",
            "content": content_b64,
        }
        if sha:
            payload["sha"] = sha
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=body, headers=headers, method="PUT")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
                return True
        except urllib.error.HTTPError as e:
            if e.code == 409:
                return None  # conflict — caller should retry with fresh SHA
            err_body = e.read().decode("utf-8", errors="replace")[:200]
            print(f"  ⚠ lineage: GitHub API {e.code} — {err_body}")
            return False
        except Exception as e:
            print(f"  ⚠ lineage: write error — {e}")
            return False

    try:
        # Attempt 1
        sha = _get_sha()
        result = _put(sha)
        if result is None:
            # 409 conflict — refetch SHA and retry once
            print("  ↻ lineage: 409 conflict — retrying with fresh SHA")
            sha = _get_sha()
            result = _put(sha)
        if result:
            print(f"  ✓ lineage envelope written → internal:{path}")
            return True
        return False
    except Exception as e:
        print(f"  ⚠ lineage: unexpected error — {e} (publish continues)")
        return False

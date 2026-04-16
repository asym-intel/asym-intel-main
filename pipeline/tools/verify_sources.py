#!/usr/bin/env python3
"""
verify_sources.py — Shared source verification utility for the Asymmetric Intelligence pipeline.

Implements ENGINE-RULES.md Section 13 guardrails:
  R1 — URL reachability check: HEAD every source_url returned by LLM.
       Flag unreachable URLs as source_unverified=True. Log incidents.
  R2 — Date cross-validation: flag temporal mismatches >30 days between
       a claimed event_date and the source publication date (from HTTP headers).

Used by:
  - All 8 weekly-research.py scripts (post-API, pre-validation)
  - All 8 collect.py scripts (post-API, pre-validation)
  - publisher.py (R4: lead signal source gate — block if unreachable)

Outputs per URL:
  {
    "url": str,
    "reachable": bool,         # True if HTTP 2xx, False otherwise
    "http_status": int | None, # Actual status code, None if request failed
    "source_verified": bool,   # Alias of reachable (used in data fields)
    "error": str | None,       # Request error message if failed
    "publication_date": str | None,  # Date from Last-Modified header if available
    "date_mismatch": bool,     # R2: True if |event_date - pub_date| > 30 days
    "date_mismatch_days": int | None,
  }

Usage:
  from verify_sources import verify_url, verify_item_sources, check_lead_signal_gate

  # R1+R2: Check a single URL
  result = verify_url("https://example.com/article", claimed_date="2026-04-14")

  # R1+R2: Check all source_url fields in a list of findings
  findings, stats = verify_item_sources(findings_list, monitor_slug, stage, log_fn)

  # R4: Publisher gate — check lead signal source before publishing
  ok, result = check_lead_signal_gate(signal_dict, monitor_slug, log_fn)

  # R4-ext: Check all key judgment sources (warn-only, does not block)
  results, summary = check_key_judgment_sources(report_dict, monitor_slug, log_fn)
"""

import datetime
import requests
import sys
from typing import Callable

# ── Constants ────────────────────────────────────────────────────────────────

DATE_MISMATCH_THRESHOLD_DAYS = 30
REQUEST_TIMEOUT_SECONDS = 10
VERIFY_USER_AGENT = "AsymmetricIntelligence-SourceVerifier/1.0 (+https://asym-intel.info)"

# HTTP status codes that indicate the content exists
REACHABLE_STATUS_CODES = set(range(200, 300)) | {301, 302, 303, 307, 308}

# Status codes that indicate definite non-existence (not just auth walls)
UNREACHABLE_STATUS_CODES = {404, 410, 451}

# Status codes that are ambiguous (Cloudflare challenge, paywalls, etc.)
# We treat these as "unverified" but not "definitely fabricated"
AMBIGUOUS_STATUS_CODES = {403, 406, 429, 503}


# ── Core: single URL check ───────────────────────────────────────────────────

def verify_url(url: str, claimed_date: str | None = None) -> dict:
    """
    HEAD-check a URL and optionally validate claimed_date against publication date.

    Args:
        url:          The source URL to check.
        claimed_date: ISO date string (YYYY-MM-DD) of the claimed event, for R2.

    Returns:
        dict with keys: url, reachable, http_status, source_verified, error,
                        publication_date, date_mismatch, date_mismatch_days
    """
    result = {
        "url": url,
        "reachable": False,
        "http_status": None,
        "source_verified": False,
        "error": None,
        "publication_date": None,
        "date_mismatch": False,
        "date_mismatch_days": None,
    }

    if not url or not url.startswith(("http://", "https://")):
        result["error"] = f"Invalid URL format: {url!r}"
        return result

    try:
        resp = requests.head(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
            headers={"User-Agent": VERIFY_USER_AGENT},
        )
        result["http_status"] = resp.status_code

        if resp.status_code in REACHABLE_STATUS_CODES:
            result["reachable"] = True
            result["source_verified"] = True

            # R2: extract publication date from Last-Modified header
            last_mod = resp.headers.get("Last-Modified") or resp.headers.get("Date")
            if last_mod and claimed_date:
                pub_date = _parse_http_date(last_mod)
                if pub_date:
                    result["publication_date"] = pub_date.isoformat()
                    # R2: check mismatch
                    try:
                        ev_date = datetime.date.fromisoformat(claimed_date[:10])
                        delta = abs((ev_date - pub_date).days)
                        if delta > DATE_MISMATCH_THRESHOLD_DAYS:
                            result["date_mismatch"] = True
                            result["date_mismatch_days"] = delta
                    except ValueError:
                        pass  # unparseable claimed_date — skip R2

        elif resp.status_code in AMBIGUOUS_STATUS_CODES:
            # Ambiguous — mark as unverified but not definitively unreachable
            result["error"] = f"Ambiguous response: HTTP {resp.status_code} (auth wall or rate limit)"
        else:
            result["error"] = f"HTTP {resp.status_code}"

    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection error: {str(e)[:120]}"
    except requests.exceptions.Timeout:
        result["error"] = f"Timeout after {REQUEST_TIMEOUT_SECONDS}s"
    except requests.exceptions.TooManyRedirects:
        result["error"] = f"Too many redirects"
    except Exception as e:
        result["error"] = f"Request failed: {str(e)[:120]}"

    return result


def _parse_http_date(date_str: str) -> datetime.date | None:
    """Parse HTTP date formats (RFC 7231 / RFC 850 / ANSI asctime)."""
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %Z",   # RFC 7231: Thu, 01 Jan 2026 00:00:00 GMT
        "%A, %d-%b-%y %H:%M:%S %Z",   # RFC 850: Thursday, 01-Jan-26 00:00:00 GMT
        "%a %b %d %H:%M:%S %Y",       # ANSI asctime: Thu Jan  1 00:00:00 2026
    ):
        try:
            return datetime.datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


# ── R1+R2: Batch verify findings list ────────────────────────────────────────

def verify_item_sources(
    items: list[dict],
    monitor_slug: str,
    stage: str,
    log_incident_fn: Callable | None = None,
    claimed_date_field: str = "event_date",
    source_url_field: str = "source_url",
) -> tuple[list[dict], dict]:
    """
    R1+R2: HEAD-check all source_url fields in a list of findings.

    Mutates items in-place:
      - Adds item["source_verified"] = bool
      - Adds item["source_http_status"] = int | None
      - Adds item["source_error"] = str | None (if failed)
      - Adds item["date_mismatch"] = bool (R2)
      - Adds item["date_mismatch_days"] = int | None (R2)

    Logs incidents for:
      - Unreachable sources (R1 violation)
      - Date mismatches > 30 days (R2 violation)

    Args:
        items:              List of finding dicts to verify.
        monitor_slug:       Monitor slug for incident logging.
        stage:              Pipeline stage name ("weekly-research", "collector", etc.).
        log_incident_fn:    Callable matching incident_log.log_incident signature.
        claimed_date_field: Field name for the event date in each item.
        source_url_field:   Field name for the source URL in each item.

    Returns:
        (mutated_items, stats) where stats = {
            "total": int, "verified": int, "unverified": int,
            "unreachable": int, "date_mismatches": int, "no_url": int
        }
    """
    if log_incident_fn is None:
        log_incident_fn = _noop_log

    stats = {
        "total": len(items),
        "verified": 0,
        "unverified": 0,
        "unreachable": 0,      # definitively 404/410
        "date_mismatches": 0,
        "no_url": 0,
    }

    for i, item in enumerate(items):
        url = item.get(source_url_field, "")
        claimed_date = item.get(claimed_date_field, "")

        if not url:
            item["source_verified"] = False
            item["source_http_status"] = None
            item["source_error"] = "No source_url provided"
            stats["no_url"] += 1
            stats["unverified"] += 1
            continue

        result = verify_url(url, claimed_date=claimed_date or None)

        # Write verification fields back into the item
        item["source_verified"] = result["source_verified"]
        item["source_http_status"] = result["http_status"]
        if result["error"]:
            item["source_error"] = result["error"]
        if result["date_mismatch"]:
            item["date_mismatch"] = True
            item["date_mismatch_days"] = result["date_mismatch_days"]

        if result["source_verified"]:
            stats["verified"] += 1
        else:
            stats["unverified"] += 1
            if result["http_status"] in UNREACHABLE_STATUS_CODES:
                stats["unreachable"] += 1

        # R1: Log incident for unreachable sources
        if not result["source_verified"]:
            severity = "critical" if result["http_status"] == 404 else "warning"
            log_incident_fn(
                monitor=monitor_slug,
                stage=stage,
                incident_type="source_unverified",
                severity=severity,
                detail=(
                    f"Source URL not reachable: {url} "
                    f"[HTTP {result['http_status']} | {result['error']}]. "
                    f"Item [{i}]: {item.get('headline', item.get('title', ''))[:80]}"
                ),
                errors=[result["error"]] if result["error"] else [],
            )

        # R2: Log incident for date mismatches
        if result["date_mismatch"]:
            stats["date_mismatches"] += 1
            log_incident_fn(
                monitor=monitor_slug,
                stage=stage,
                incident_type="date_mismatch",
                severity="warning",
                detail=(
                    f"Date mismatch {result['date_mismatch_days']} days: "
                    f"claimed event={claimed_date}, source published={result['publication_date']}. "
                    f"URL: {url}. "
                    f"Item [{i}]: {item.get('headline', item.get('title', ''))[:80]}"
                ),
            )

    return items, stats


# ── R4: Publisher lead signal gate ───────────────────────────────────────────

def check_lead_signal_gate(
    signal: dict,
    monitor_slug: str,
    log_incident_fn: Callable | None = None,
) -> tuple[bool, dict]:
    """
    R4: Before publishing, HEAD-check the lead signal's source_url.
    Block publication if the source is definitively unreachable (404/410).

    Ambiguous responses (403, 503) are logged as warnings but do NOT block.
    Missing source_url is logged as a warning but does NOT block (some monitors
    carry signals without a direct source URL).

    Args:
        signal:           The signal dict (from build_signal()).
        monitor_slug:     Monitor slug for incident logging.
        log_incident_fn:  Callable matching incident_log.log_incident.

    Returns:
        (should_block: bool, verify_result: dict)
        should_block=True means: do NOT publish this report.
    """
    if log_incident_fn is None:
        log_incident_fn = _noop_log

    url = signal.get("source_url", "")

    if not url:
        log_incident_fn(
            monitor=monitor_slug,
            stage="publisher",
            incident_type="source_unverified",
            severity="warning",
            detail="Lead signal has no source_url — cannot verify. Publishing anyway.",
        )
        return False, {"url": url, "reachable": None, "blocked": False,
                       "reason": "no_url"}

    result = verify_url(url)
    result["blocked"] = False

    if result["http_status"] in UNREACHABLE_STATUS_CODES:
        # R4: Hard block — source definitively does not exist
        result["blocked"] = True
        log_incident_fn(
            monitor=monitor_slug,
            stage="publisher",
            incident_type="source_gate_block",
            severity="critical",
            detail=(
                f"R4 PUBLISHER GATE BLOCKED: Lead signal source_url returned "
                f"HTTP {result['http_status']} — source does not exist. "
                f"Headline: {signal.get('headline', '')[:100]}. "
                f"URL: {url}. Publication blocked."
            ),
            errors=[f"HTTP {result['http_status']}: {result['error']}"],
        )
        return True, result  # BLOCK

    if not result["source_verified"]:
        # Ambiguous or connection failure — warn but do not block
        log_incident_fn(
            monitor=monitor_slug,
            stage="publisher",
            incident_type="source_unverified",
            severity="warning",
            detail=(
                f"Lead signal source_url could not be verified "
                f"(HTTP {result['http_status']} | {result['error']}). "
                f"URL: {url}. Publishing with warning."
            ),
        )

    return False, result  # Allow publish


# ── R4-ext: Key judgment source verification ────────────────────────────────────

def check_key_judgment_sources(
    report: dict,
    monitor_slug: str,
    log_incident_fn: Callable | None = None,
) -> tuple[list[dict], dict]:
    """
    R4 extension: HEAD-check all source_urls in key_judgments[*].

    Behaviour (per Engine Audit Control Plane spec):
      - 404/410 on a secondary source: log WARNING (does NOT block publish)
      - Missing source_urls array: log info, skip (graceful — field populates
        after first post-R1 weekly run, w/e 20 Apr 2026)
      - Lead source is already gated by check_lead_signal_gate(); this covers
        the remaining key judgment sources only.

    Args:
        report:           The assembled report dict (after build_signal).
        monitor_slug:     Monitor slug for incident logging.
        log_incident_fn:  Callable matching incident_log.log_incident.

    Returns:
        (results: list[dict], summary: dict)
        Each result: {"kj_id": str, "url": str, **verify_url_result}
        summary: {"total_urls": int, "verified": int, "unverified": int,
                  "unreachable": int, "skipped_no_urls": int}
    """
    if log_incident_fn is None:
        log_incident_fn = _noop_log

    key_judgments = report.get("key_judgments", [])
    results = []
    summary = {
        "total_urls": 0,
        "verified": 0,
        "unverified": 0,
        "unreachable": 0,
        "skipped_no_urls": 0,
    }

    if not key_judgments:
        return results, summary

    for kj in key_judgments:
        if not isinstance(kj, dict):
            continue
        kj_id = kj.get("id", kj.get("judgment", "?")[:40])
        source_urls = kj.get("source_urls", [])

        if not source_urls:
            summary["skipped_no_urls"] += 1
            continue

        if isinstance(source_urls, str):
            source_urls = [source_urls]  # normalise single URL to list

        for url in source_urls:
            if not url or not isinstance(url, str):
                continue
            summary["total_urls"] += 1
            result = verify_url(url)
            result["kj_id"] = kj_id
            results.append(result)

            if result["source_verified"]:
                summary["verified"] += 1
            else:
                summary["unverified"] += 1
                if result["http_status"] in UNREACHABLE_STATUS_CODES:
                    summary["unreachable"] += 1
                    # Log warning for unreachable secondary source
                    log_incident_fn(
                        monitor=monitor_slug,
                        stage="publisher",
                        incident_type="secondary_source_unreachable",
                        severity="warning",
                        detail=(
                            f"R4-ext: key_judgment source_url returned "
                            f"HTTP {result['http_status']}. "
                            f"KJ: {kj_id}. URL: {url}. "
                            f"Warning only — does not block publish."
                        ),
                    )
                elif not result["source_verified"]:
                    log_incident_fn(
                        monitor=monitor_slug,
                        stage="publisher",
                        incident_type="secondary_source_unverified",
                        severity="info",
                        detail=(
                            f"R4-ext: key_judgment source_url unverified "
                            f"(HTTP {result['http_status']} | {result['error']}). "
                            f"KJ: {kj_id}. URL: {url}."
                        ),
                    )

    return results, summary


# ── Reporting helpers ─────────────────────────────────────────────────────────

def log_verification_summary(stats: dict, stage: str, monitor_slug: str) -> None:
    """Print a verification summary to stdout (for GA logs)."""
    total = stats["total"]
    verified = stats["verified"]
    rate = (verified / total * 100) if total > 0 else 0
    print(
        f"[verify_sources] {monitor_slug}/{stage}: "
        f"{verified}/{total} sources verified ({rate:.0f}%) | "
        f"unreachable={stats['unreachable']} | "
        f"date_mismatches={stats['date_mismatches']} | "
        f"no_url={stats['no_url']}"
    )


def emit_verification_record(
    items: list[dict],
    stats: dict,
    monitor_slug: str,
    stage: str,
    run_date: str,
) -> dict:
    """
    Build a verification_record dict suitable for embedding in weekly-latest.json
    under a "_verification" key. This feeds the epistemic integrity dashboard.

    Shape:
    {
      "verified_at": "2026-04-16T19:00:00Z",
      "monitor": "european-strategic-autonomy",
      "stage": "weekly-research",
      "run_date": "2026-04-16",
      "total_sources": 8,
      "verified_sources": 6,
      "verification_rate": 0.75,
      "unreachable_count": 1,
      "date_mismatch_count": 1,
      "no_url_count": 0,
      "unverified_urls": ["https://fabricated.example.com/..."],
      "date_mismatch_urls": ["https://old-source.example.com/..."],
    }
    """
    unverified_urls = [
        item.get("source_url", "")
        for item in items
        if not item.get("source_verified") and item.get("source_url")
    ]
    date_mismatch_urls = [
        item.get("source_url", "")
        for item in items
        if item.get("date_mismatch") and item.get("source_url")
    ]
    total = stats["total"]
    verified = stats["verified"]

    return {
        "verified_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "monitor": monitor_slug,
        "stage": stage,
        "run_date": run_date,
        "total_sources": total,
        "verified_sources": verified,
        "verification_rate": round(verified / total, 4) if total > 0 else None,
        "unreachable_count": stats["unreachable"],
        "date_mismatch_count": stats["date_mismatches"],
        "no_url_count": stats["no_url"],
        "unverified_urls": unverified_urls,
        "date_mismatch_urls": date_mismatch_urls,
    }


# ── Internal helpers ─────────────────────────────────────────────────────────

def _noop_log(**kwargs) -> None:
    """Fallback log function when incident_log is unavailable."""
    pass


# ── CLI test mode ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Quick smoke test: verify a list of URLs from the command line.
    Usage: python3 verify_sources.py https://example.com https://nonexistent.invalid/page
    """
    urls = sys.argv[1:] or [
        "https://asym-intel.info",
        "https://www.euractiv.com/section/defence/news/eu-unveils-first-rearm-europe-contracts-for-joint-ammo-production/",  # fabricated URL from ESA incident
        "https://defence-industry-space.ec.europa.eu/edip-commission-adopts-eu15-billion-work-programme-boost-european-and-ukrainian-defence-industry-2026-03-30_en",
    ]
    print(f"Testing {len(urls)} URL(s):\n")
    for url in urls:
        r = verify_url(url)
        status = "✅ VERIFIED" if r["source_verified"] else "❌ UNVERIFIED"
        print(f"  {status} | HTTP {r['http_status']} | {url}")
        if r["error"]:
            print(f"           Error: {r['error']}")
        if r["date_mismatch"]:
            print(f"           ⚠ Date mismatch: {r['date_mismatch_days']} days")
        print()

#!/usr/bin/env python3
"""
snapshot.py — Rendered-HTML + adapter-output snapshot and sanity check.

Purpose
-------
Catch renderer/adapter regressions (the P-011 class — field-name mismatches
producing `undefined` in rendered HTML) by capturing a post-publish baseline
of the live page + the adapter output that produced it.

Usage
-----
Manual (pre/post structural change):
    python3 tools/snapshot.py \\
        --url https://ramparts.gi/ai-frontier-monitor-issue-2026-04-17/ \\
        --issue-slug 2026-04-17 \\
        --label pre-change

Publisher post-publish sanity check (fails run on regression unless
SOFT_FAIL=true):
    python3 tools/snapshot.py \\
        --url https://ramparts.gi/ai-frontier-monitor-issue-2026-04-17/ \\
        --issue-slug 2026-04-17 \\
        --label post-publish \\
        --sanity-check

Exit codes
----------
0  — snapshot written, sanity checks passed (or no previous baseline to diff)
2  — sanity check hard-fail (undefined count regressed, section missing)
3  — fetch failed

Output layout
-------------
ops/snapshots/<issue-slug>/<ISO-timestamp>-<label>/
    rendered.html        — curl output of the live URL (post-JS-plugin)
    metadata.json        — url, timestamp, label, sha256, sanity results
    adapter-output.json  — (optional) slice of report-latest.json + persistent

Retention: last 10 snapshots per issue-slug; older pruned (git history
preserves them regardless).

Sanity checks
-------------
1. **M9/Law & Guidance section present** — "Law &amp; Guidance" or
   "Law & Guidance" substring must appear.
2. **M9 section has zero `undefined` matches** — the exact P-011 signature.
   WordPress plugin JS fallbacks (Complianz cookie banner, Elementor) can
   legitimately contain the substring `undefined` elsewhere on the page, so
   this check is scoped to the M9 section only.
3. **Expected M9 layer count >= 7** — Layer 1..Layer 7 headings present.
4. **Regression check vs last-good snapshot for same issue-slug**:
     - If previous snapshot had N undefineds in M9 and current has >N → fail.
     - If previous had >=7 layers and current has fewer → fail.

SOFT_FAIL=true env escape hatch demotes hard-fail to warning. Use when a
known-acceptable regression needs to ship.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = REPO_ROOT / "ops" / "snapshots"
RETENTION_PER_SLUG = 10

# Sanity check regexes (scoped to Ramparts issue pages — extend as needed)
_M9_SECTION_PATTERNS = [
    # Ramparts renderM8_LawGuidance outputs these.
    # WordPress re-encodes `&` as the numeric entity `&#038;` in headings, so
    # we accept the literal, `&amp;`, or `&#038;` forms.
    re.compile(
        r'(?is)Law\s*(?:&amp;|&#0*38;|&)\s*Guidance'
    ),
]
_LAYER_PATTERN = re.compile(r'Layer\s+\d+\s*[—-]', re.IGNORECASE)
_UNDEFINED_PATTERN = re.compile(r'\bundefined\b')


def fetch(url: str) -> bytes:
    """Fetch URL with a friendly UA. Raises on non-200."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "asym-intel-snapshot/1.0 (+https://asym-intel.info)",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status != 200:
            raise RuntimeError(f"fetch {url} returned HTTP {r.status}")
        return r.read()


def extract_m9_section(html: str) -> str:
    """
    Extract just the M9 / Law & Guidance section for scoped sanity checks.

    Heuristic: take the window from the first Law & Guidance marker to the
    next monitor heading (M10+) or 8000 chars, whichever is shorter.
    """
    for p in _M9_SECTION_PATTERNS:
        m = p.search(html)
        if m:
            start = m.start()
            break
    else:
        return ""  # not found; caller flags this
    # Bound the section at the next known M9+ heading. Ramparts renderer
    # emits Personnel & Org Watch (M10) directly after the Law & Guidance
    # subsections (EU AI Act, Country Grid, Country Watch, AI Governance,
    # Ethics, Technical Standards, Litigation Tracker).
    tail = html[start:start + 30000]
    next_module = re.search(
        r'(?is)Personnel\s*(?:&amp;|&#0*38;|&)\s*Org\s+Watch',
        tail[200:],  # skip a little to avoid matching ourselves
    )
    if next_module:
        return tail[: 200 + next_module.start()]
    return tail[:12000]


def sanity_check(html_bytes: bytes) -> dict:
    """
    Run sanity checks against rendered HTML. Returns dict with:
      - m9_section_found: bool
      - m9_undefined_count: int
      - m9_layer_count: int
      - errors: list[str]  (hard-fail conditions; empty = pass)
      - warnings: list[str]
    """
    html = html_bytes.decode("utf-8", errors="replace")
    m9 = extract_m9_section(html)
    errors: list[str] = []
    warnings: list[str] = []

    m9_found = bool(m9)
    if not m9_found:
        errors.append("sanity: M9 (Law & Guidance) section not found in page")

    m9_undef = len(_UNDEFINED_PATTERN.findall(m9)) if m9 else 0
    if m9_undef > 0:
        errors.append(
            f"sanity: {m9_undef} `undefined` string(s) in M9 section — "
            "P-011 regression"
        )

    m9_layers = len(_LAYER_PATTERN.findall(m9)) if m9 else 0
    if m9_found and m9_layers < 7:
        errors.append(
            f"sanity: M9 has only {m9_layers} Layer rows (expected >= 7) — "
            "EU AI Act tracker may have lost entries"
        )

    # Page-level undefined total (warning only — WP plugin JS uses the token
    # legitimately in Complianz and Elementor)
    page_undef_total = len(_UNDEFINED_PATTERN.findall(html))
    if page_undef_total > 5:
        warnings.append(
            f"sanity: {page_undef_total} `undefined` matches page-wide "
            "(expected ~2 from WP plugins; investigate if higher)"
        )

    return {
        "m9_section_found": m9_found,
        "m9_undefined_count": m9_undef,
        "m9_layer_count": m9_layers,
        "page_undefined_total": page_undef_total,
        "errors": errors,
        "warnings": warnings,
    }


def last_good_snapshot(slug_dir: Path) -> Path | None:
    """Return directory of most recent previous snapshot for this slug, or None."""
    if not slug_dir.exists():
        return None
    subs = sorted(
        [p for p in slug_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
    )
    return subs[-1] if subs else None


def regression_check(current: dict, previous_dir: Path | None) -> list[str]:
    """
    Compare current sanity results against previous snapshot's metadata.
    Returns list of regression error strings (empty = no regression).
    """
    if previous_dir is None:
        return []
    meta_file = previous_dir / "metadata.json"
    if not meta_file.exists():
        return []
    try:
        prev = json.loads(meta_file.read_text())
    except Exception:
        return []
    prev_sanity = prev.get("sanity", {})
    errors: list[str] = []
    prev_undef = prev_sanity.get("m9_undefined_count", 0)
    cur_undef = current.get("m9_undefined_count", 0)
    if cur_undef > prev_undef:
        errors.append(
            f"regression: M9 undefineds went {prev_undef} → {cur_undef} "
            f"(vs {previous_dir.name})"
        )
    prev_layers = prev_sanity.get("m9_layer_count", 0)
    cur_layers = current.get("m9_layer_count", 0)
    if prev_layers >= 7 and cur_layers < prev_layers:
        errors.append(
            f"regression: M9 layers went {prev_layers} → {cur_layers} "
            f"(vs {previous_dir.name})"
        )
    return errors


def prune_old(slug_dir: Path, keep: int = RETENTION_PER_SLUG) -> None:
    if not slug_dir.exists():
        return
    subs = sorted(
        [p for p in slug_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
    )
    for p in subs[:-keep]:
        for f in p.iterdir():
            f.unlink()
        p.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="Live URL to snapshot")
    ap.add_argument(
        "--issue-slug", required=True,
        help="Issue slug (e.g. 2026-04-17) — becomes the snapshot dir",
    )
    ap.add_argument(
        "--label", required=True,
        help="Short label (e.g. pre-change, post-publish, manual)",
    )
    ap.add_argument(
        "--sanity-check", action="store_true",
        help="Run sanity checks and exit non-zero on hard-fail",
    )
    ap.add_argument(
        "--adapter-output",
        help="Optional path to report-latest.json to slice into snapshot",
    )
    args = ap.parse_args()

    soft_fail = os.environ.get("SOFT_FAIL", "").lower() in ("1", "true", "yes")

    slug_dir = SNAPSHOTS_DIR / args.issue_slug
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = slug_dir / f"{ts}-{args.label}"

    # Fetch first so we don't create empty dirs on failure
    try:
        html_bytes = fetch(args.url)
    except Exception as e:
        print(f"[snapshot] FETCH FAILED: {e}", file=sys.stderr)
        return 3

    # Find previous snapshot BEFORE writing current one
    previous = last_good_snapshot(slug_dir)

    out.mkdir(parents=True, exist_ok=True)
    (out / "rendered.html").write_bytes(html_bytes)
    sha = hashlib.sha256(html_bytes).hexdigest()

    sanity = sanity_check(html_bytes) if args.sanity_check else {}
    regressions = regression_check(sanity, previous) if args.sanity_check else []

    metadata = {
        "url": args.url,
        "issue_slug": args.issue_slug,
        "label": args.label,
        "timestamp_utc": ts,
        "bytes": len(html_bytes),
        "sha256": sha,
        "sanity": sanity,
        "regressions": regressions,
        "previous_snapshot": previous.name if previous else None,
    }

    if args.adapter_output:
        ap_path = Path(args.adapter_output)
        if ap_path.exists():
            try:
                ap_data = json.loads(ap_path.read_text())
                # Slice: keep module_9 + meta only (full report is large)
                slice_ = {
                    "meta": ap_data.get("meta"),
                    "module_9": ap_data.get("module_9"),
                }
                (out / "adapter-output.json").write_text(
                    json.dumps(slice_, indent=2, sort_keys=True)
                )
                metadata["adapter_output_sliced"] = True
            except Exception as e:
                metadata["adapter_output_error"] = str(e)

    (out / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True)
    )

    prune_old(slug_dir)

    # Report
    print(f"[snapshot] wrote {out.relative_to(REPO_ROOT)}")
    print(f"[snapshot] sha256={sha[:12]}… bytes={len(html_bytes)}")
    if args.sanity_check:
        print(f"[sanity]   m9_section_found={sanity['m9_section_found']} "
              f"m9_undefineds={sanity['m9_undefined_count']} "
              f"m9_layers={sanity['m9_layer_count']} "
              f"page_undef_total={sanity['page_undefined_total']}")
        for w in sanity.get("warnings", []):
            print(f"[warn]     {w}")
        hard = sanity.get("errors", []) + regressions
        if hard:
            for e in hard:
                print(f"[error]    {e}", file=sys.stderr)
            if soft_fail:
                print("[sanity]   SOFT_FAIL=true — demoting hard-fail to warn",
                      file=sys.stderr)
                return 0
            print(f"[sanity]   HARD FAIL — {len(hard)} issue(s). "
                  "Set SOFT_FAIL=true to override.", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())

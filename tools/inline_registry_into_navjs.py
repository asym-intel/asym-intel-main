#!/usr/bin/env python3
"""
inline_registry_into_navjs.py — Build step for ENGINE-RULES §17.

Rewrites the MONITOR_REGISTRY literal inside
static/monitors/shared/js/nav.js from static/monitors/monitor-registry.json.

The literal is delimited by:
    /* BEGIN @REGISTRY_INLINE */ ... /* END @REGISTRY_INLINE */

If the delimiters are missing, exits with an error — catches accidental
drift-by-deletion.

Run locally:
    python tools/inline_registry_into_navjs.py

CI: run as a pre-Hugo-build step. Also re-run this in any PR that touches
either monitor-registry.json or nav.js. If the working-tree nav.js differs
from the generated output, the pre-commit / CI check fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "static" / "monitors" / "monitor-registry.json"
NAVJS = REPO_ROOT / "static" / "monitors" / "shared" / "js" / "nav.js"
SUBNAVJS = REPO_ROOT / "static" / "monitors" / "shared" / "js" / "sub-nav.js"

BEGIN = "/* BEGIN @REGISTRY_INLINE */"
END = "/* END @REGISTRY_INLINE */"
SUB_NAV_BEGIN = "/* BEGIN @SUB_NAV_INLINE */"
SUB_NAV_END = "/* END @SUB_NAV_INLINE */"


def build_literal(registry: dict) -> str:
    """Produce a 2-space-indented JS literal block from the registry.

    Emits two top-level constants:
      - MONITOR_REGISTRY: slug -> {abbr, name, accent, url, svg_url, vb,
                                   strip_label, accent_2?}
      - MONITOR_TRIAGE_ORDER: array of abbrs in canonical triage sequence,
                              used by injectMonitorStrip().
    nav.js consumes both: nav rendering uses MONITOR_REGISTRY by slug;
    the cross-monitor strip iterates MONITOR_TRIAGE_ORDER and resolves
    each abbr against MONITOR_REGISTRY (+ a slug-by-abbr map below).
    Adding/reordering monitors = edit monitor-registry.json only.
    """
    # --- MONITOR_REGISTRY (slug-keyed) ---
    # CR-2 guard: parked monitors have no publication surface (no url/svg_url);
    # skip them here so they do not appear in nav.js or the monitor strip.
    # Parked monitors remain in monitor-registry.json for registry-driven
    # tooling (pipeline_flow_audit, monitor_urls.py) but are excluded from
    # nav/strip until a publication surface exists.
    active_monitors = [m for m in registry["monitors"] if not m.get("parked")]
    lines = ["var MONITOR_REGISTRY = {"]
    for m in active_monitors:
        slug = m["slug"]
        entry = {
            "abbr":        m["abbr"],
            "name":        m["name"],
            "accent":      m["accent"],
            "url":         m["url"],
            "svg_url":     m["svg_url"],
            "vb":          m["svg_viewbox"],
            "strip_label": m["strip_label"],
        }
        if m.get("accent_2"):
            entry["accent_2"] = m["accent_2"]
        line = f"    {json.dumps(slug)}: {json.dumps(entry, separators=(', ', ': '))},"
        lines.append(line)
    lines.append("  };")

    # --- MONITOR_TRIAGE_ORDER (abbr array) ---
    if "triage_order" not in registry:
        raise KeyError(
            "monitor-registry.json missing required 'triage_order' array "
            "(used by nav.js injectMonitorStrip)."
        )
    # Filter triage_order to active (non-parked) monitors only.
    active_abbrs = {m["abbr"] for m in active_monitors}
    all_abbrs = {m["abbr"] for m in registry["monitors"]}
    triage = [a for a in registry["triage_order"] if a in active_abbrs]
    # Validate: every entry in triage_order must be a known monitor abbr.
    unknown = [a for a in registry["triage_order"] if a not in all_abbrs]
    if unknown:
        raise ValueError(
            f"triage_order contains unknown abbrs: {unknown}"
        )
    # Validate: every active (non-parked) monitor must appear in triage_order.
    missing = sorted(active_abbrs - set(registry["triage_order"]))
    if missing:
        raise ValueError(
            f"triage_order missing active monitor abbrs: {missing}"
        )
    triage_js = json.dumps(triage, separators=(", ", ": "))
    lines.append("")
    lines.append(f"  var MONITOR_TRIAGE_ORDER = {triage_js};")

    return "\n".join(lines)


def build_sub_nav_literal(registry: dict) -> str:
    """Produce the MONITOR_SUB_NAV literal for sub-nav.js.

    Source: registry['sub_nav'] — list of {href, label} objects.
    Inlining keeps sub-nav.js self-contained (no fetch at render time)
    and preserves the P13 single-source-of-truth invariant: editing the
    JSON + running this tool is the only path to change the sub-nav.
    """
    if "sub_nav" not in registry:
        raise KeyError(
            "monitor-registry.json missing required 'sub_nav' array "
            "(consumed by sub-nav.js — BRIEF-FE-SUB-NAV-PRIMITIVE)."
        )
    items = registry["sub_nav"]
    if not isinstance(items, list) or not items:
        raise ValueError("'sub_nav' must be a non-empty array")
    for it in items:
        if not isinstance(it, dict) or "href" not in it or "label" not in it:
            raise ValueError(
                f"sub_nav entry malformed (need href + label): {it!r}"
            )
    lines = ["var MONITOR_SUB_NAV = ["]
    for it in items:
        entry = {"href": it["href"], "label": it["label"]}
        lines.append(f"    {json.dumps(entry, separators=(', ', ': '))},")
    lines.append("  ];")
    return "\n".join(lines)


def main() -> int:
    if not REGISTRY.exists():
        print(f"FAIL: {REGISTRY} missing", file=sys.stderr)
        return 2
    if not NAVJS.exists():
        print(f"FAIL: {NAVJS} missing", file=sys.stderr)
        return 2

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    navjs = NAVJS.read_text(encoding="utf-8")

    if BEGIN not in navjs or END not in navjs:
        print(f"FAIL: nav.js missing {BEGIN}...{END} markers", file=sys.stderr)
        print("Expected to find a block to replace. Has nav.js been "
              "migrated to the inline-registry pattern?", file=sys.stderr)
        return 2

    before, _, rest = navjs.partition(BEGIN)
    _, _, after = rest.partition(END)

    new_block = BEGIN + "\n  " + build_literal(registry) + "\n  " + END
    new_navjs = before + new_block + after

    changed_navjs = (new_navjs != navjs)
    if changed_navjs:
        NAVJS.write_text(new_navjs, encoding="utf-8")
        print(f"✓ nav.js updated from registry "
              f"({len(registry['monitors'])} monitors)")
    else:
        print(f"✓ nav.js already up-to-date with registry "
              f"({len(registry['monitors'])} monitors)")

    # sub-nav.js — inline registry['sub_nav'] (BRIEF-FE-SUB-NAV-PRIMITIVE)
    if not SUBNAVJS.exists():
        print(f"FAIL: {SUBNAVJS} missing", file=sys.stderr)
        return 2
    subnav = SUBNAVJS.read_text(encoding="utf-8")
    if SUB_NAV_BEGIN not in subnav or SUB_NAV_END not in subnav:
        print(f"FAIL: sub-nav.js missing {SUB_NAV_BEGIN}...{SUB_NAV_END} markers",
              file=sys.stderr)
        return 2
    before_sn, _, rest_sn = subnav.partition(SUB_NAV_BEGIN)
    _, _, after_sn = rest_sn.partition(SUB_NAV_END)
    new_sn_block = (
        SUB_NAV_BEGIN
        + "\n  "
        + build_sub_nav_literal(registry)
        + "\n  "
        + SUB_NAV_END
    )
    new_subnav = before_sn + new_sn_block + after_sn
    if new_subnav != subnav:
        SUBNAVJS.write_text(new_subnav, encoding="utf-8")
        print(f"✓ sub-nav.js updated from registry "
              f"({len(registry['sub_nav'])} nav items)")
    else:
        print(f"✓ sub-nav.js already up-to-date with registry "
              f"({len(registry['sub_nav'])} nav items)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

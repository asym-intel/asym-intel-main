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

BEGIN = "/* BEGIN @REGISTRY_INLINE */"
END = "/* END @REGISTRY_INLINE */"


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
    lines = ["var MONITOR_REGISTRY = {"]
    for m in registry["monitors"]:
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
    triage = registry["triage_order"]
    abbrs = {m["abbr"] for m in registry["monitors"]}
    unknown = [a for a in triage if a not in abbrs]
    if unknown:
        raise ValueError(
            f"triage_order contains unknown abbrs: {unknown}"
        )
    missing = sorted(abbrs - set(triage))
    if missing:
        raise ValueError(
            f"triage_order missing abbrs present in monitors[]: {missing}"
        )
    triage_js = json.dumps(triage, separators=(", ", ": "))
    lines.append("")
    lines.append(f"  var MONITOR_TRIAGE_ORDER = {triage_js};")

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

    if new_navjs == navjs:
        print(f"✓ nav.js already up-to-date with registry "
              f"({len(registry['monitors'])} monitors)")
        return 0

    NAVJS.write_text(new_navjs, encoding="utf-8")
    print(f"✓ nav.js updated from registry "
          f"({len(registry['monitors'])} monitors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

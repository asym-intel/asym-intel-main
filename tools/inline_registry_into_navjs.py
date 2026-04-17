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
    """Produce a 2-space-indented JS object literal from the registry."""
    # Shape: slug -> {abbr, name, accent, svg_url, url, viewbox, accent_2}
    # nav.js needs abbr, name, accent, svg (URL or inline), vb for backwards compat.
    # We switch to svg_url (img-loaded) instead of inline svg string. nav.js
    # rendering code will need a one-line change to prefer m.svg_url if present.
    lines = ["var MONITOR_REGISTRY = {"]
    for m in registry["monitors"]:
        slug = m["slug"]
        entry = {
            "abbr":    m["abbr"],
            "name":    m["name"],
            "accent":  m["accent"],
            "url":     m["url"],
            "svg_url": m["svg_url"],
            "vb":      m["svg_viewbox"],
        }
        if m.get("accent_2"):
            entry["accent_2"] = m["accent_2"]
        line = f"    {json.dumps(slug)}: {json.dumps(entry, separators=(', ', ': '))},"
        lines.append(line)
    lines.append("  };")
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

#!/usr/bin/env python3
"""
test_preflight_monitor_links.py — fixture suite for ENGINE-RULES §17 preflight.

These cases pin down the boundary between:
  - canonical monitor URL construction (BANNED \u2014 must use registry)
  - sub-path construction (out of scope for this preflight; awaiting
    SCOPE-2026-04-17-002 / monitor_path() resolver migration)

If you change RX_CONCAT in preflight_monitor_links.py, run this file:
    python tools/test_preflight_monitor_links.py

Every case must pass. Adding a new case is encouraged whenever a real-world
violation or false-positive surfaces in CI.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preflight_monitor_links import RX_CONCAT  # noqa: E402

# Lines that build the CANONICAL monitor URL by string concat \u2014 MUST flag.
SHOULD_FLAG = [
    # Bare concat
    "var u = '/monitors/' + slug;",
    "var u = '/monitors/' + slug + '/';",
    "return '/monitors/' + slug",
    # Banned overview.html shape
    "href = '/monitors/' + m.slug + '/overview.html'",
    " ' href=\"/monitors/' + m.slug + '/overview.html\"' +",
    # Full-host prefix
    "url = 'https://asym-intel.info/monitors/' + slug + '/'",
    # Template literals
    "var x = `/monitors/${slug}/`;",
    "var x = `/monitors/${slug}/overview.html`;",
    "var x = `/monitors/${slug}`;",
    "var x = `https://asym-intel.info/monitors/${slug}/`;",
    # Parenthesised expression / function-call producing the canonical URL
    "var u = '/monitors/' + (slug || 'foo')",
    "var u = '/monitors/' + getCurrentSlug() + '/'",
]

# Lines that build a SUB-PATH \u2014 MUST NOT flag (deferred to SCOPE-2026-04-17-002).
SHOULD_PASS = [
    # Common sub-paths
    "var u = '/monitors/' + slug + '/dashboard.html';",
    "var u = '/monitors/' + slug + '/data/report-latest.json';",
    "link.href = '/monitors/' + slug + '/data/report-latest.md';",
    "var BASE = '/monitors/' + (slug || '') + '/data/';",
    # Template literal sub-paths
    "var x = `/monitors/${slug}/data/chatter-latest.json`;",
    "var x = `/monitors/${slug}/dashboard.html`;",
    # Dotted identifiers
    "var u = '/monitors/' + f.monitor_slug + '/dashboard.html';",
    "if (linked) return '/monitors/' + linked + '/dashboard.html';",
    # Function-call expressions producing a slug
    "var u = '/monitors/' + escHtml(slug) + '/dashboard.html';",
    "var u = '/monitors/' + _esc(s) + '/dashboard.html';",
    "var u = '/monitors/' + getCurrentSlug() + '/dashboard.html';",
]


def main() -> int:
    failures = 0
    for s in SHOULD_FLAG:
        if not RX_CONCAT.search(s):
            print(f"  \u2717 SHOULD_FLAG missed: {s}")
            failures += 1
    for s in SHOULD_PASS:
        if RX_CONCAT.search(s):
            print(f"  \u2717 SHOULD_PASS false-positive: {s}")
            failures += 1
    if failures == 0:
        print(f"  \u2713 preflight_monitor_links regex: "
              f"{len(SHOULD_FLAG)} flag + {len(SHOULD_PASS)} pass = OK")
        return 0
    print(f"  \u2717 {failures} regression(s) in RX_CONCAT")
    return 1


if __name__ == "__main__":
    sys.exit(main())

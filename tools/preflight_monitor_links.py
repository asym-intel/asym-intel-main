#!/usr/bin/env python3
"""
preflight_monitor_links.py — ENGINE-RULES §17 validator.

For every HTML/Hugo/JS file in the repo, find anchors or chip markup with
`data-monitor="ABBR"` and assert that the accompanying href is exactly the
canonical URL from the registry. Also flags hardcoded `asym-intel.info/{abbr}`
patterns and string-concatenation attempts like `'asym-intel.info/monitors/' + slug`.

Exit 0 if clean, 1 if violations found.

Usage:
    python tools/preflight_monitor_links.py
    python tools/preflight_monitor_links.py --verbose
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Import the resolver (registry is the source of truth).
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.shared.monitor_urls import all_monitors, all_abbrs, monitor_url  # noqa: E402

# Files we scan.
SCAN_EXTS = {".html", ".js", ".py", ".md"}
# Dirs we skip.
SKIP_DIRS = {".git", "node_modules", "archive", "docs", "resources", ".hugo_build.lock"}

# Regex 1: anchor with data-monitor="X" — capture href for comparison.
RX_DATA_MONITOR = re.compile(
    r'<a\b[^>]*\bdata-monitor=["\'](?P<abbr>[A-Za-z]+)["\'][^>]*\bhref=["\'](?P<href>[^"\']+)["\']'
    r'|<a\b[^>]*\bhref=["\'](?P<href2>[^"\']+)["\'][^>]*\bdata-monitor=["\'](?P<abbr2>[A-Za-z]+)["\']',
    re.IGNORECASE,
)

# Regex 2: hardcoded /{abbr} pattern (the tonight-bug shape).
ABBRS_LOWER = "|".join(a.lower() for a in all_abbrs())
RX_HARDCODED_ABBR_PATH = re.compile(
    r'asym-intel\.info/(' + ABBRS_LOWER + r')(?:[/"\'\s]|$)',
    re.IGNORECASE,
)

# Regex 3: string concatenation that builds a CANONICAL monitor URL.
#
# Scope (ENGINE-RULES §17): the canonical monitor URL is the registry
# `url` field — `https://asym-intel.info/monitors/{slug}/`. The tonight-bug
# class was code that built that exact value by string concat instead of
# reading from the registry. The wrong-overview.html shape is a sub-class:
# `/monitors/{slug}/overview.html` was historically used as the canonical
# landing URL and is now banned in favour of trailing-slash.
#
# What this regex MUST flag:
#   '/monitors/' + slug                       (canonical, no suffix)
#   '/monitors/' + slug + '/'                 (canonical, trailing slash)
#   '/monitors/' + slug + '/overview.html'    (banned legacy canonical)
#   `/monitors/${slug}/`                      (template-literal canonical)
#   `/monitors/${slug}/overview.html`         (template-literal banned)
#
# What this regex MUST NOT flag (sub-paths — not registry-governed):
#   '/monitors/' + slug + '/dashboard.html'
#   '/monitors/' + slug + '/data/report-latest.json'
#   `/monitors/${slug}/data/chatter-latest.json`
#
# A sub-path migration sweep (SCOPE-2026-04-17-002) will add a
# monitor_path(abbr, subpath) resolver and migrate those callsites; until
# then they pass preflight.
# Variable/expression token allowed inside the concat. Wrapped in an atomic
# group (?>...) so the regex engine cannot backtrack and truncate the
# identifier just to satisfy a later negative lookahead — a real bug we hit
# building this regex (logged in KNOWHOW: regex-design-pitfalls).
# Alternation order is longest-first (function-call → dotted → bare → parens)
# so the FIRST match is the longest legal token at this position.
# Examples: slug, m.slug, f.monitor_slug, escHtml(slug), _esc(s), (slug || '').
# Requires Python 3.11+ for atomic groups; CI runs 3.12.
_VAR = (
    r'''(?>'''
    r'''[A-Za-z_$][\w.$]*\([^)]*\)'''   # function call (longest — must come first)
    r'''|[A-Za-z_$][\w.$]+'''            # dotted identifier (e.g. m.slug)
    r'''|[A-Za-z_$]\w*'''                # bare identifier
    r'''|\([^)]*\)'''                    # parenthesised expression
    r''')'''
)

RX_CONCAT = re.compile(
    # JS/Python concat shape:
    #   "<prefix>/monitors/" + <var> [ + "/[overview.html]" ]   end
    # The trailing-literal group is OPTIONAL but must be exactly "/" or
    # "/overview.html" — anything else ("/dashboard.html", "/data/...") means
    # this is a sub-path concat, which is out of scope. We use a negative
    # lookahead to rule out a following `+ '/sub...'` segment.
    r'''["'`](?:https?://asym-intel\.info)?/monitors/["'`]\s*\+\s*'''
    + _VAR +
    r'''(?:\s*\+\s*["'`]/(?:overview\.html)?["'`])?'''
    r'''(?!\s*\+\s*["'`]/)'''      # NOT followed by `+ '/sub...'` (sub-path — out of scope)
    r'''|'''
    # JS template literal: `/monitors/${slug}` or `${slug}/` or `${slug}/overview.html` ONLY.
    # Sub-path template literals (e.g. `/monitors/${slug}/data/...`) are out of scope.
    r'''`(?:https?://asym-intel\.info)?/monitors/\$\{[^}]+\}(?:/(?:overview\.html)?)?`''',
)


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_no, category, message) violations for one file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [(0, "READ_ERROR", f"Could not read: {e}")]

    violations: list[tuple[int, str, str]] = []
    lines = text.splitlines()

    # Check data-monitor + href correspondence.
    for m in RX_DATA_MONITOR.finditer(text):
        abbr = (m.group("abbr") or m.group("abbr2") or "").upper()
        href = m.group("href") or m.group("href2") or ""
        line_no = text[: m.start()].count("\n") + 1
        try:
            expected = monitor_url(abbr)
        except KeyError:
            violations.append(
                (line_no, "UNKNOWN_ABBR",
                 f'data-monitor="{abbr}" not in registry — href={href}')
            )
            continue
        if href != expected:
            violations.append(
                (line_no, "HREF_MISMATCH",
                 f'data-monitor="{abbr}" has href="{href}"; '
                 f'registry says "{expected}"')
            )

    # Check hardcoded /{abbr} paths (the tonight-bug).
    for i, line in enumerate(lines, start=1):
        if RX_HARDCODED_ABBR_PATH.search(line):
            # Allow in this very file and the registry itself.
            if path.name in ("preflight_monitor_links.py", "test_preflight_monitor_links.py", "monitor-registry.json"):
                continue
            violations.append(
                (i, "HARDCODED_ABBR_PATH",
                 f'hardcoded "asym-intel.info/{{abbr}}" pattern — use resolver: {line.strip()[:160]}')
            )

    # Check string concatenation.
    for i, line in enumerate(lines, start=1):
        if RX_CONCAT.search(line):
            if path.name in ("preflight_monitor_links.py", "test_preflight_monitor_links.py"):
                continue
            violations.append(
                (i, "URL_CONCAT",
                 f'string-concat monitor URL — use resolver: {line.strip()[:160]}')
            )

    return violations


def walk_repo(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in SCAN_EXTS:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    print(f"  ✈︎ preflight_monitor_links — scanning {root}")
    print(f"  Registry: {len(all_monitors())} monitors — "
          f"{', '.join(all_abbrs())}")

    total_files = 0
    total_violations = 0
    for f in walk_repo(root):
        total_files += 1
        v = scan_file(f)
        if not v:
            if args.verbose:
                print(f"  ✓ {f.relative_to(root)}")
            continue
        for line_no, cat, msg in v:
            print(f"  ✗ {f.relative_to(root)}:{line_no}  [{cat}]  {msg}")
            total_violations += 1

    print()
    print(f"  Scanned: {total_files} files")
    print(f"  Violations: {total_violations}")
    if total_violations == 0:
        print("  ✓ preflight passed")
        return 0
    print("  ✗ preflight failed — ENGINE-RULES §17 URL Construction")
    return 1


if __name__ == "__main__":
    sys.exit(main())

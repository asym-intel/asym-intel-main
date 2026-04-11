#!/usr/bin/env python3
"""Add monitor-layout + sidebar wrapper to chatter and search pages.

These pages currently use a flat <main> without the monitor-layout wrapper
and sidebar that other pages (about, methodology, dashboard, etc.) have.
This script wraps them to match.

Run from repo root:  python3 tools/add-sidebar-to-pages.py [--dry-run]
"""

import os
import re
import sys

DRY_RUN = '--dry-run' in sys.argv
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONITOR_SLUGS = [
    'ai-governance',
    'conflict-escalation',
    'democratic-integrity',
    'environmental-risks',
    'european-strategic-autonomy',
    'fimi-cognitive-warfare',
    'macro-monitor',
]

MONITOR_ABBRS = {
    'ai-governance': 'AGM',
    'conflict-escalation': 'SCEM',
    'democratic-integrity': 'WDM',
    'environmental-risks': 'ERM',
    'european-strategic-autonomy': 'ESA',
    'fimi-cognitive-warfare': 'FCW',
    'macro-monitor': 'GMM',
}

CHATTER_SIDEBAR = '''  <nav class="monitor-sidebar" aria-label="Page sections">
    <div class="sidebar-nav__title">Chatter</div>
    <ul>
      <li><a href="#chatter-items">Today's Signals</a></li>
    </ul>
    <div class="sidebar-nav__title" style="margin-top:var(--space-6)">Navigate</div>
    <ul>
      <li><a href="dashboard.html">Dashboard</a></li>
      <li><a href="report.html">Latest Issue</a></li>
      <li><a href="persistent.html">Living Knowledge</a></li>
    </ul>
  </nav>'''

SEARCH_SIDEBAR = '''  <nav class="monitor-sidebar" aria-label="Page sections">
    <div class="sidebar-nav__title">Search</div>
    <ul>
      <li><a href="#search-input">Search</a></li>
      <li><a href="#search-results">Results</a></li>
    </ul>
    <div class="sidebar-nav__title" style="margin-top:var(--space-6)">Navigate</div>
    <ul>
      <li><a href="dashboard.html">Dashboard</a></li>
      <li><a href="report.html">Latest Issue</a></li>
      <li><a href="archive.html">Archive</a></li>
    </ul>
  </nav>'''


def wrap_page(filepath, sidebar_html):
    """Wrap a flat-main page in monitor-layout + sidebar."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Skip if already wrapped
    if 'monitor-layout' in html:
        return False

    # Replace <main id="main-content" style="..."> with wrapped version
    # Match the opening <main> tag (with or without inline styles)
    main_open = re.search(r'<main\s+id="main-content"[^>]*>', html)
    if not main_open:
        print(f"  SKIP (no <main>): {os.path.relpath(filepath, REPO_ROOT)}")
        return False

    # Replace opening <main> with monitor-layout wrapper
    old_main_tag = main_open.group(0)
    new_main_open = '<div class="monitor-layout">\n  <main class="monitor-main" id="main-content">'
    html = html.replace(old_main_tag, new_main_open, 1)

    # Replace </main> with </main> + sidebar + closing </div>
    html = html.replace(
        '</main>',
        '  </main>\n\n' + sidebar_html + '\n\n</div>',
        1
    )

    if DRY_RUN:
        print(f"  WOULD WRAP: {os.path.relpath(filepath, REPO_ROOT)}")
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  WRAPPED: {os.path.relpath(filepath, REPO_ROOT)}")
    return True


def main():
    print("Adding monitor-layout + sidebar to chatter and search pages")
    if DRY_RUN:
        print("(DRY RUN)\n")
    else:
        print()

    changed = 0
    for slug in MONITOR_SLUGS:
        base = os.path.join(REPO_ROOT, 'static', 'monitors', slug)

        chatter = os.path.join(base, 'chatter.html')
        if os.path.exists(chatter):
            if wrap_page(chatter, CHATTER_SIDEBAR):
                changed += 1

        search = os.path.join(base, 'search.html')
        if os.path.exists(search):
            if wrap_page(search, SEARCH_SIDEBAR):
                changed += 1

    print(f"\n{'Would wrap' if DRY_RUN else 'Wrapped'}: {changed} pages")


if __name__ == '__main__':
    main()

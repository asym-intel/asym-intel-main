#!/usr/bin/env python3
"""Merge methodology.html content into about.html for each monitor.

For each monitor:
1. Extract all <section class="module-section"> blocks from methodology.html
2. Wrap them in a methodology divider section
3. Insert before </main> in about.html
4. Update the sidebar nav to include methodology sections
5. Replace methodology.html with a redirect to about.html#methodology

Run from repo root:  python3 tools/merge-methodology-into-about.py [--dry-run]
"""

import os
import re
import sys
import glob

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


def extract_methodology_sections(html):
    """Extract all <section> blocks with an id from methodology page's <main> content."""
    # First try to isolate <main> content
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if not main_match:
        return []
    main_content = main_match.group(1)
    
    # Extract sections — handle both class="module-section" and plain <section id="...">
    sections = []
    for m in re.finditer(
        r'(<section[^>]+id="[^"]*"[^>]*>.*?</section>)',
        main_content, re.DOTALL
    ):
        sections.append(m.group(1))
    return sections


def extract_sidebar_links(html):
    """Extract sidebar <li><a> items from methodology page."""
    # Try <nav class="monitor-sidebar"> first, then <aside class="monitor-sidebar">
    sidebar_match = re.search(
        r'(?:nav|aside)\s+class="monitor-sidebar"[^>]*>.*?<ul>(.*?)</ul>',
        html, re.DOTALL
    )
    if sidebar_match:
        links = re.findall(r'<li>.*?</li>', sidebar_match.group(1), re.DOTALL)
        return links
    return []


def build_methodology_block(sections):
    """Wrap methodology sections with a divider header."""
    divider = '''
    <section class="module-section" id="methodology">
      <div class="module-header">
        <div class="module-title" style="font-size:var(--text-2xl);border-top:1px solid var(--color-border);padding-top:var(--space-8);margin-top:var(--space-4)">Methodology</div>
      </div>
    </section>
'''
    return divider + '\n' + '\n\n'.join(sections)


def insert_into_about(about_html, methodology_block, sidebar_links):
    """Insert methodology block before </main> and add sidebar links."""
    # Insert methodology sections before </main>
    about_html = about_html.replace(
        '  </main>',
        methodology_block + '\n\n  </main>'
    )
    
    # Add methodology sidebar links
    # Find the closing </ul> in the sidebar
    sidebar_ul_pattern = r'(<nav\s+class="monitor-sidebar"[^>]*>.*?<ul>)(.*?)(</ul>)'
    
    def add_sidebar_links(match):
        existing = match.group(2)
        # Add a methodology header link + sub-links
        new_links = '\n      <li style="margin-top:var(--space-3);border-top:1px solid var(--color-border);padding-top:var(--space-3)"><a href="#methodology"><strong>Methodology</strong></a></li>'
        for link in sidebar_links:
            new_links += '\n      ' + link
        return match.group(1) + existing + new_links + '\n    ' + match.group(3)
    
    about_html = re.sub(sidebar_ul_pattern, add_sidebar_links, about_html, flags=re.DOTALL)
    
    return about_html


def build_redirect_page(slug):
    """Build a minimal redirect page for methodology.html → about.html#methodology."""
    # Get monitor name from slug for the title
    names = {
        'ai-governance': 'Artificial Intelligence Monitor',
        'conflict-escalation': 'Strategic Conflict & Escalation Monitor',
        'democratic-integrity': 'World Democracy Monitor',
        'environmental-risks': 'Environmental Risks Monitor',
        'european-strategic-autonomy': 'European Strategic Autonomy Monitor',
        'fimi-cognitive-warfare': 'FIMI & Cognitive Warfare Monitor',
        'macro-monitor': 'Global Macro Monitor',
    }
    name = names.get(slug, 'Monitor')
    
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Methodology — {name} · Asymmetric Intelligence</title>
  <meta name="description" content="{name} methodology. Redirecting to About page.">
  <link rel="canonical" href="about.html#methodology">
  <meta http-equiv="refresh" content="0;url=about.html#methodology">
  <link rel="stylesheet" href="../shared/css/base.css">
  <link rel="stylesheet" href="assets/monitor.css">
  <script src="../shared/js/theme.js"></script>
  <script src="../shared/js/nav.js"></script>
</head>
<body>
<nav class="monitor-nav" aria-label="Monitor navigation">
  <a class="monitor-nav__brand" href="dashboard.html"></a>
  <button class="monitor-nav__hamburger" aria-label="Toggle menu" aria-expanded="false">
    <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
      <line x1="2" y1="4.5" x2="16" y2="4.5"/><line x1="2" y1="9" x2="16" y2="9"/><line x1="2" y1="13.5" x2="16" y2="13.5"/>
    </svg>
  </button>
  <ul class="monitor-nav__links" role="list"></ul>
  <div class="monitor-nav__actions"></div>
</nav>
<main id="main-content" style="max-width:var(--content-max);margin:0 auto;padding:var(--space-10) var(--space-6)">
  <p>Redirecting to <a href="about.html#methodology">About &amp; Methodology</a>…</p>
</main>
<footer class="monitor-footer"></footer>
</body>
</html>'''


def process_monitor(slug):
    """Process one monitor: merge methodology into about."""
    base = os.path.join(REPO_ROOT, 'static', 'monitors', slug)
    about_path = os.path.join(base, 'about.html')
    meth_path = os.path.join(base, 'methodology.html')
    
    if not os.path.exists(about_path) or not os.path.exists(meth_path):
        print(f"  SKIP: {slug} — missing about or methodology")
        return False
    
    with open(about_path, 'r', encoding='utf-8') as f:
        about_html = f.read()
    with open(meth_path, 'r', encoding='utf-8') as f:
        meth_html = f.read()
    
    # Extract methodology content
    sections = extract_methodology_sections(meth_html)
    if not sections:
        print(f"  SKIP: {slug} — no methodology sections found")
        return False
    
    sidebar_links = extract_sidebar_links(meth_html)
    
    # Build the methodology block
    meth_block = build_methodology_block(sections)
    
    # Merge into about
    new_about = insert_into_about(about_html, meth_block, sidebar_links)
    
    # Build redirect
    redirect = build_redirect_page(slug)
    
    if DRY_RUN:
        print(f"  WOULD MERGE: {slug} ({len(sections)} sections, {len(sidebar_links)} sidebar links)")
        return True
    
    with open(about_path, 'w', encoding='utf-8') as f:
        f.write(new_about)
    with open(meth_path, 'w', encoding='utf-8') as f:
        f.write(redirect)
    
    print(f"  MERGED: {slug} ({len(sections)} sections, {len(sidebar_links)} sidebar links)")
    return True


def main():
    print(f"Merging methodology into about for {len(MONITOR_SLUGS)} monitors")
    if DRY_RUN:
        print("(DRY RUN)\n")
    else:
        print()
    
    merged = 0
    for slug in MONITOR_SLUGS:
        if process_monitor(slug):
            merged += 1
    
    print(f"\n{'Would merge' if DRY_RUN else 'Merged'}: {merged}/{len(MONITOR_SLUGS)} monitors")


if __name__ == '__main__':
    main()

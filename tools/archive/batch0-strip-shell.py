#!/usr/bin/env python3
"""Batch 0 — Strip hardcoded shell from monitor HTML files.

Replaces redundant nav/footer markup with minimal skeletons that nav.js fills.
Standardises <head> while preserving page-specific additions (Chart.js, inline styles).

Run from repo root:  python3 tools/batch0-strip-shell.py [--dry-run]
"""

import os
import re
import sys
import glob

DRY_RUN = '--dry-run' in sys.argv
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Canonical nav skeleton (nav.js fills brand, links, theme toggle) ──
NAV_SKELETON = '''<nav class="monitor-nav" aria-label="Monitor navigation">
  <a class="monitor-nav__brand" href="dashboard.html"></a>
  <button class="monitor-nav__hamburger" aria-label="Toggle menu" aria-expanded="false">
    <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
      <line x1="2" y1="4.5" x2="16" y2="4.5"/><line x1="2" y1="9" x2="16" y2="9"/><line x1="2" y1="13.5" x2="16" y2="13.5"/>
    </svg>
  </button>
  <ul class="monitor-nav__links" role="list"></ul>
  <div class="monitor-nav__actions"></div>
</nav>'''

# ── Canonical footer skeleton (nav.js fills content) ──
FOOTER_SKELETON = '<footer class="monitor-footer"></footer>'

# ── Canonical head template ──
# {title}, {description}, {extra_head} are filled per-file
HEAD_TEMPLATE = '''<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="../shared/css/base.css">
  <link rel="stylesheet" href="assets/monitor.css">
  <script src="../shared/js/theme.js"></script>
  <script src="../shared/js/nav.js"></script>
{extra_head}</head>'''


def extract_title(head_content):
    """Extract <title> text."""
    m = re.search(r'<title>(.*?)</title>', head_content, re.DOTALL)
    return m.group(1).strip() if m else 'Asymmetric Intelligence'


def extract_description(head_content):
    """Extract meta description content attribute."""
    m = re.search(r'<meta\s+name="description"\s+content="(.*?)"', head_content, re.DOTALL)
    return m.group(1).strip() if m else ''


def extract_extra_head(head_content):
    """Extract page-specific head content: Chart.js CDN, charts.js, inline <style> blocks.
    Excludes: charset, viewport, title, description, base.css, monitor.css, theme.js, nav.js, fontshare."""
    extra_lines = []
    
    # Chart.js CDN links (with or without SRI)
    for m in re.finditer(r'^\s*<script\s+src="https://cdn\.jsdelivr\.net/npm/chart\.js[^"]*"[^>]*></script>\s*$', head_content, re.MULTILINE):
        extra_lines.append(m.group(0).strip())
    
    # Local charts.js
    for m in re.finditer(r'^\s*<script\s+src="\.\./shared/js/charts\.js"[^>]*></script>\s*$', head_content, re.MULTILINE):
        extra_lines.append(m.group(0).strip())
    
    # Inline <style> blocks in head
    for m in re.finditer(r'<style[\s>].*?</style>', head_content, re.DOTALL):
        extra_lines.append(m.group(0).strip())
    
    # HTML comments about Chart.js (preserve context)
    for m in re.finditer(r'^\s*<!--.*?[Cc]hart.*?-->\s*$', head_content, re.MULTILINE):
        extra_lines.append(m.group(0).strip())
    
    if extra_lines:
        return '  ' + '\n  '.join(extra_lines) + '\n'
    return ''


def extract_nav_block(html):
    """Find the <nav class="monitor-nav"> ... </nav> block, including any stray
    content before it that's after <body> (like the FCW </nav><style> issue)."""
    # Match from <nav class="monitor-nav" to its closing </nav>
    # Account for nested elements but monitor-nav has no nested <nav>
    pattern = r'<nav\s+class="monitor-nav"[^>]*>.*?</nav>'
    m = re.search(pattern, html, re.DOTALL)
    if m:
        return m.start(), m.end()
    return None, None


def extract_footer_block(html):
    """Find <footer class="monitor-footer"> ... </footer>."""
    pattern = r'<footer\s+class="monitor-footer"[^>]*>.*?</footer>'
    m = re.search(pattern, html, re.DOTALL)
    if m:
        return m.start(), m.end()
    return None, None


def clean_body_preamble(html, nav_start):
    """Remove stray content between <body> and <nav> (e.g. FCW has a stray </nav><style> block)."""
    body_match = re.search(r'<body[^>]*>', html)
    if not body_match or nav_start is None:
        return html
    
    body_end = body_match.end()
    between = html[body_end:nav_start].strip()
    
    if between:
        # There's stray content — remove it
        html = html[:body_end] + '\n' + html[nav_start:]
    return html


def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    original = html
    
    # ── 1. Standardise <head> ──
    head_match = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
    if head_match:
        old_head = head_match.group(1)
        title = extract_title(old_head)
        description = extract_description(old_head)
        extra = extract_extra_head(old_head)
        new_head = HEAD_TEMPLATE.format(
            title=title,
            description=description,
            extra_head=extra
        )
        html = html[:head_match.start()] + new_head + html[head_match.end():]
    
    # ── 2. Clean stray content before nav ──
    nav_start, nav_end = extract_nav_block(html)
    if nav_start is not None:
        html = clean_body_preamble(html, nav_start)
        # Re-find nav after potential modification
        nav_start, nav_end = extract_nav_block(html)
    
    # ── 3. Replace nav block ──
    if nav_start is not None:
        html = html[:nav_start] + NAV_SKELETON + html[nav_end:]
    
    # ── 4. Replace footer block ──
    footer_start, footer_end = extract_footer_block(html)
    if footer_start is not None:
        html = html[:footer_start] + FOOTER_SKELETON + html[footer_end:]
    
    # ── 5. Remove stray fontshare preconnect/link tags ──
    html = re.sub(r'\s*<link\s+rel="preconnect"\s+href="https://api\.fontshare\.com"[^>]*>\s*', '\n', html)
    html = re.sub(r'\s*<link\s+href="https://api\.fontshare\.com[^"]*"[^>]*>\s*', '\n', html)
    
    # ── 6. Normalise whitespace (collapse multiple blank lines to max 1) ──
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    if html != original:
        if DRY_RUN:
            print(f"  WOULD CHANGE: {os.path.relpath(filepath, REPO_ROOT)}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  CHANGED: {os.path.relpath(filepath, REPO_ROOT)}")
        return True
    else:
        print(f"  UNCHANGED: {os.path.relpath(filepath, REPO_ROOT)}")
        return False


def main():
    # Find all monitor HTML files (excluding shared/ templates)
    pattern = os.path.join(REPO_ROOT, 'static', 'monitors', '*', '*.html')
    files = sorted(glob.glob(pattern))
    
    # Exclude shared/ directory and assets/ subdirectories
    files = [f for f in files if '/shared/' not in f and '/assets/' not in f]
    
    print(f"Batch 0: Processing {len(files)} monitor HTML files")
    if DRY_RUN:
        print("(DRY RUN — no files will be modified)\n")
    else:
        print()
    
    changed = 0
    for f in files:
        if process_file(f):
            changed += 1
    
    print(f"\n{'Would change' if DRY_RUN else 'Changed'}: {changed}/{len(files)} files")


if __name__ == '__main__':
    main()

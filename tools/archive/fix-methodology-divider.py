#!/usr/bin/env python3
"""Remove the bare 'Methodology' divider section from about.html files.

The merge-methodology-into-about script inserted a divider section:
    <section class="module-section" id="methodology">
      <div class="module-header">
        <div class="module-title" style="...">Methodology</div>
      </div>
    </section>

This should be removed. The id="methodology" anchor should transfer to the
next real section that follows it, so sidebar links still work.
"""
import re
import glob
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONITORS = glob.glob(os.path.join(BASE, "static", "monitors", "*", "about.html"))

# Pattern: the bare divider section with just "Methodology" title
# Captures the section and the following whitespace
DIVIDER_PATTERN = re.compile(
    r'\n?\s*<section class="module-section" id="methodology">\s*'
    r'<div class="module-header">\s*'
    r'<div class="module-title"[^>]*>Methodology</div>\s*'
    r'</div>\s*'
    r'</section>\s*\n?',
    re.DOTALL
)

changes = 0
for fpath in sorted(MONITORS):
    slug = os.path.basename(os.path.dirname(fpath))
    with open(fpath, 'r') as f:
        html = f.read()

    if not DIVIDER_PATTERN.search(html):
        print(f"  {slug}: no bare divider found, skipping")
        continue

    # Remove the divider
    new_html = DIVIDER_PATTERN.sub('\n\n', html, count=1)

    # Now we need the id="methodology" anchor on the next section
    # Find the first <section after where the divider was and add id="methodology" if not present
    # The next section typically has its own id — we need to ADD id="methodology" so sidebar links work
    
    # Check if there's already another element with id="methodology" 
    if 'id="methodology"' in new_html:
        # ESA case: the page-header section already exists with methodology content
        # but it has a different id. Let's check.
        pass
    
    # Find the section that follows where the divider was removed
    # Strategy: find the first <section after the removal point that doesn't have id="methodology"
    # and add it as an additional attribute
    
    # Actually, simpler: just add an anchor <div id="methodology"></div> before the next section
    # This preserves the existing section IDs while making the #methodology link work
    
    # Find where divider was (now just \n\n) followed by a <section
    anchor_pattern = re.compile(r'(\n\n)(\s*<section\s)')
    
    # Find the position where divider was removed — look for double newline before next section
    # after the "About" content
    # Better approach: just insert an anchor div
    
    if 'id="methodology"' not in new_html:
        # Need to add an anchor. Find the first section after the old divider location.
        # The old divider was right after the last "About" section.
        # Look for the pattern of double newline + section that has methodology content
        
        # Find sections that are methodology-related by content
        # These typically have ids like "section-what", "section-what-we-track", "section-scope", "scope"
        methodology_sections = {
            'ai-governance': 'scope',
            'conflict-escalation': 'section-what',
            'democratic-integrity': 'section-what',
            'environmental-risks': 'section-scope',
            'european-strategic-autonomy': 'section-what-we-track',
            'fimi-cognitive-warfare': 'section-what',
            'macro-monitor': 'section-what-gmm-tracks',
        }
        
        target_id = methodology_sections.get(slug)
        if target_id:
            # Add id="methodology" as a named anchor just before this section
            section_tag = f'<section class="module-section" id="{target_id}">'
            if slug == 'ai-governance':
                section_tag = f'<section id="{target_id}"'
            
            # Insert a simple anchor div before the target section
            if section_tag in new_html:
                new_html = new_html.replace(
                    section_tag,
                    f'<div id="methodology"></div>\n{section_tag}',
                    1
                )
            elif f'id="{target_id}"' in new_html:
                # Try a more flexible match
                new_html = re.sub(
                    rf'(<section[^>]*id="{target_id}")',
                    r'<div id="methodology"></div>\n\1',
                    new_html,
                    count=1
                )
            else:
                print(f"  WARNING: {slug}: could not find target section '{target_id}'")

    with open(fpath, 'w') as f:
        f.write(new_html)
    
    changes += 1
    print(f"  {slug}: removed bare methodology divider ✓")

print(f"\nDone: {changes} file(s) updated")

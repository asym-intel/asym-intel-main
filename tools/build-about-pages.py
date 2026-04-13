#!/usr/bin/env python3
"""Generate About pages for all 7 monitors.

Structure: shell + description_fragment + schedule_fragment + standard sections + methodology_fragment.

Per-monitor editorial content lives in fragment files:
  static/monitors/shared/fragments/about-description-{slug}.html
  static/monitors/shared/fragments/about-schedule-{slug}.html
  static/monitors/shared/fragments/about-methodology-{slug}.html

To edit a monitor's about page content, edit the fragment file and re-run this generator.
The shell (head, nav, sidebar, editor, links, credit) is shared — edit it here.
"""
import os
import html as html_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(BASE, "static", "monitors")
FRAGMENTS = os.path.join(STATIC, "shared", "fragments")

MONITORS = {
    "democratic-integrity":        ("WDM",  "World Democracy Monitor"),
    "macro-monitor":               ("GMM",  "Global Macro Monitor"),
    "european-strategic-autonomy":  ("ESA",  "European Strategic Autonomy Monitor"),
    "fimi-cognitive-warfare":      ("FCW",  "FIMI & Cognitive Warfare Monitor"),
    "ai-governance":               ("AGM",  "Artificial Intelligence Monitor"),
    "environmental-risks":         ("ERM",  "Environmental Risks Monitor"),
    "conflict-escalation":         ("SCEM", "Strategic Conflict & Escalation Monitor"),
}

# Short methodology descriptions for the Links section
METHODOLOGY_LINK_DESC = {
    "democratic-integrity": "Sources, heatmap tiers, integrity flag definitions, and mimicry chain methodology.",
    "macro-monitor": "Indicator scoring, stress labels, regime framework, blind spot override rules, and source hierarchy.",
    "european-strategic-autonomy": "Primary sources, module structure, severity ratings, and Lagrange Point framework.",
    "fimi-cognitive-warfare": "MF1–MF4 filters, F-flag definitions, attribution confidence levels, and source standards.",
    "ai-governance": "16-module structure, source hierarchy, inclusion criteria, and governance health scoring.",
    "environmental-risks": "Planetary boundaries framework, filter tags F1–F4, tipping system tracking, and source criteria.",
    "conflict-escalation": "Six indicators (I1–I6), deviation-over-level methodology, F-flags, and roster inclusion criteria.",
}


def esc(s):
    return html_mod.escape(str(s)) if s else ""


def load_fragment(name, slug):
    """Load a fragment file. Returns content or empty string if missing."""
    path = os.path.join(FRAGMENTS, f"{name}-{slug}.html")
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"  WARNING: missing fragment {path}")
        return f'<!-- MISSING FRAGMENT: {name}-{slug}.html -->'


def build_about(slug, abbr, name):
    description = load_fragment("about-description", slug)
    schedule = load_fragment("about-schedule", slug)
    methodology = load_fragment("about-methodology", slug)
    meth_desc = esc(METHODOLOGY_LINK_DESC.get(slug, "Full methodology documentation."))

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About — {esc(name)} · Asymmetric Intelligence</title>
  <meta name="description" content="About the {esc(name)} — what it tracks, who produces it, and how to use it.">
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

<div class="monitor-layout">
  <main class="monitor-main" id="main-content">

    <div class="page-header">
      <div class="page-header__eyebrow">{esc(abbr)} · Asymmetric Intelligence</div>
      <h1 class="page-header__title">About</h1>
    </div>

    {description}

    {schedule}

    <section class="module-section" id="section-editor">
      <div class="module-header">
        <div class="module-title">Editor</div>
      </div>
      <p><strong>Peter Howitt</strong> — Gibraltar. Published via <a href="https://asym-intel.info" target="_blank" rel="noopener">asym-intel.info</a>.</p>
    </section>

    <section class="module-section" id="section-links">
      <div class="module-header">
        <div class="module-title">Links</div>
      </div>
      <ul style="list-style:none;padding:0">
        <li style="padding:var(--space-3) 0;border-bottom:1px solid var(--color-border-subtle)">
          <a href="#methodology">{esc(abbr)} Methodology</a>
          <span class="text-muted" style="display:block;font-size:var(--text-xs);margin-top:var(--space-1)">{meth_desc}</span>
        </li>
        <li style="padding:var(--space-3) 0;border-bottom:1px solid var(--color-border-subtle)">
          <a href="https://asym-intel.info/monitors/{slug}/">All {esc(abbr)} Briefs</a>
          <span class="text-muted" style="display:block;font-size:var(--text-xs);margin-top:var(--space-1)">Full weekly briefs on the Asymmetric Intelligence platform.</span>
        </li>
        <li style="padding:var(--space-3) 0;border-bottom:1px solid var(--color-border-subtle)">
          <a href="https://asym-intel.info/monitors/">All Monitors</a>
          <span class="text-muted" style="display:block;font-size:var(--text-xs);margin-top:var(--space-1)">Asymmetric Intelligence monitor suite — conflict, governance, AI, FIMI, environment, and more.</span>
        </li>
        <li style="padding:var(--space-3) 0">
          <a href="https://asym-intel.info" target="_blank" rel="noopener">asym-intel.info</a>
          <span class="text-muted" style="display:block;font-size:var(--text-xs);margin-top:var(--space-1)">Asymmetric Intelligence main platform.</span>
        </li>
      </ul>
    </section>

    <section class="module-section" id="section-credit">
      <div class="module-header">
        <div class="module-title">Credit</div>
      </div>
      <p>This monitor dashboard was built with <a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener">Perplexity Computer</a>.</p>
    </section>

<div id="methodology"></div>
    {methodology}

  </main>

  <nav class="monitor-sidebar" aria-label="Page sections">
    <div class="sidebar-nav__title">About</div>
    <ul>
      <li><a href="#section-description">Description</a></li>
      <li><a href="#section-schedule">Schedule</a></li>
      <li><a href="#section-editor">Editor</a></li>
      <li><a href="#section-links">Links</a></li>
      <li><a href="#methodology">Methodology</a></li>
    </ul>
    <div style="padding:var(--space-6) var(--space-4) var(--space-4);border-top:1px solid var(--color-border-subtle);margin-top:var(--space-4)">
      <a href="dashboard.html" class="btn btn--primary" style="display:block;text-align:center;font-size:var(--text-xs)">Dashboard &rarr;</a>
    </div>
  </nav>

</div>

<footer class="monitor-footer"></footer>
</body>
</html>'''


# ── Generate ──────────────────────────────────────────────────────────
for slug, (abbr, name) in MONITORS.items():
    out_path = os.path.join(STATIC, slug, "about.html")
    html = build_about(slug, abbr, name)
    with open(out_path, "w") as f:
        f.write(html)
    lines = html.count("\n") + 1
    print(f"  {slug}/about.html — {lines} lines ✓")

print(f"\nDone: 7 about pages generated")
print(f"Fragment files in: static/monitors/shared/fragments/")
print(f"  about-description-{{slug}}.html  — per-monitor description")
print(f"  about-schedule-{{slug}}.html     — per-monitor schedule")
print(f"  about-methodology-{{slug}}.html  — per-monitor methodology")

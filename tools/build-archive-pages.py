#!/usr/bin/env python3
"""Generate Archive pages for all 7 monitors.

Structure: shared shell (head, nav, layout, sidebar, footer) + per-monitor JS render fragment.

Per-monitor JS render logic lives in fragment files:
  static/monitors/shared/fragments/archive-render-{slug}.js

To edit a monitor's archive render logic, edit the fragment file and re-run this generator.
The shell (head, nav, page-header, sidebar, footer) is shared — edit it here.
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
    "ai-governance":               ("AGM",  "AI Governance Monitor"),
    "environmental-risks":         ("ERM",  "Environmental Risks Monitor"),
    "conflict-escalation":         ("SCEM", "Strategic Conflict & Escalation Monitor"),
}

META_DESC = {
    "democratic-integrity": "Full issue archive of the World Democracy Monitor — all weekly briefs since volume 1.",
    "macro-monitor": "All published issues of the Global Macro Monitor. Weekly macro-financial intelligence from Asymmetric Intelligence.",
    "european-strategic-autonomy": "Archive of all published issues of the European Strategic Autonomy Monitor.",
    "fimi-cognitive-warfare": "Archive of all FIMI &amp; Cognitive Warfare Monitor weekly briefs.",
    "ai-governance": "Archive of all AI Governance Monitor weekly issues.",
    "environmental-risks": "Full issue archive of the Environmental Risks Monitor — all weekly briefs since volume 1.",
    "conflict-escalation": "Archive of all past SCEM weekly intelligence issues.",
}

SUB_DESC = {
    "democratic-integrity": "All weekly issues, most recent first.",
    "macro-monitor": "All published issues. Each includes the system stress label, regime, delta strip, and full brief link.",
    "european-strategic-autonomy": "All published issues of the European Strategic Autonomy Monitor.",
    "fimi-cognitive-warfare": "All published issues. Links to full briefs on the Asymmetric Intelligence platform.",
    "ai-governance": "All published issues of the AI Governance Monitor.",
    "environmental-risks": "All weekly issues, most recent first.",
    "conflict-escalation": "Every weekly issue, most recent first. Each entry shows the lead signal and top delta items.",
}


def esc(s):
    return html_mod.escape(str(s)) if s else ""


def load_fragment(slug):
    """Load a per-monitor JS render fragment."""
    path = os.path.join(FRAGMENTS, f"archive-render-{slug}.js")
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"  WARNING: missing fragment {path}")
        return f'// MISSING FRAGMENT: archive-render-{slug}.js'


def build_archive(slug, abbr, name):
    render_js = load_fragment(slug)
    meta_desc = META_DESC.get(slug, f"Archive of all {esc(name)} weekly issues.")
    sub_desc = SUB_DESC.get(slug, f"All published issues of the {esc(name)}.")

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Archive — {esc(name)} · Asymmetric Intelligence</title>
  <meta name="description" content="{esc(meta_desc)}">
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
      <h1 class="page-header__title">Archive</h1>
      <p class="page-header__sub">{sub_desc}</p>
    </div>

    <section class="module-section" id="section-archive">
      <div id="archive-count" class="section-label" style="margin-bottom:var(--space-4)"></div>
      <div id="archive-list">
        <div class="loading-state">Loading archive…</div>
      </div>
    </section>

  </main>

  <nav class="monitor-sidebar" aria-label="Page sections">
    <div class="sidebar-nav__title">Archive</div>
    <ul id="sidebar-links">
      <li><a href="#section-archive">All Issues</a></li>
    </ul>
  </nav>

</div>

<footer class="monitor-footer"></footer>
<script src="../shared/js/renderer.js"></script>
<script>
{render_js}
</script>
</body>
</html>'''


# ── Generate ──────────────────────────────────────────────────────────
for slug, (abbr, name) in MONITORS.items():
    out_path = os.path.join(STATIC, slug, "archive.html")
    html = build_archive(slug, abbr, name)
    with open(out_path, "w") as f:
        f.write(html)
    lines = html.count("\n") + 1
    print(f"  {slug}/archive.html — {lines} lines ✓")

print(f"\nDone: 7 archive pages generated")
print(f"Fragment files in: static/monitors/shared/fragments/")
print(f"  archive-render-{{slug}}.js  — per-monitor JS render logic")

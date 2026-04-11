#!/usr/bin/env python3
"""Generate Archive pages for all 7 monitors.

All JS rendering is generated inline from per-monitor ARCHIVE_CONFIG.
No external JS fragment files needed — edit the config or templates here.

Config dimensions per monitor:
  - group_by_year: bool — wrap entries in year sections (SCEM only)
  - extra_badges: list — additional badge fields to render (e.g. GMM stress/regime)
  - sidebar_dynamic: bool — populate sidebar from issue list at runtime

Everything else is shared: fetch, sort newest-first, escape, date format,
cap-at-3 delta items with "… and N more", error/empty states.
"""
import os
import html as html_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(BASE, "static", "monitors")

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
    "macro-monitor": "All published issues, most recent first.",
    "european-strategic-autonomy": "All published issues, most recent first.",
    "fimi-cognitive-warfare": "All published issues, most recent first.",
    "ai-governance": "All published issues, most recent first.",
    "environmental-risks": "All weekly issues, most recent first.",
    "conflict-escalation": "Every weekly issue, grouped by year, most recent first.",
}

# ── Per-monitor config ────────────────────────────────────────────────
ARCHIVE_CONFIG = {
    "democratic-integrity":       {"group_by_year": False, "extra_badges": [],                       "sidebar_dynamic": True},
    "macro-monitor":              {"group_by_year": False, "extra_badges": ["system_stress_label", "regime"], "sidebar_dynamic": True},
    "european-strategic-autonomy": {"group_by_year": False, "extra_badges": [],                       "sidebar_dynamic": True},
    "fimi-cognitive-warfare":     {"group_by_year": False, "extra_badges": [],                       "sidebar_dynamic": True},
    "ai-governance":              {"group_by_year": False, "extra_badges": [],                       "sidebar_dynamic": True},
    "environmental-risks":        {"group_by_year": False, "extra_badges": [],                       "sidebar_dynamic": True},
    "conflict-escalation":        {"group_by_year": True,  "extra_badges": [],                       "sidebar_dynamic": True},
}


def esc(s):
    return html_mod.escape(str(s)) if s else ""


# ── JS Template ───────────────────────────────────────────────────────
def build_js(slug, conf):
    """Generate the inline JS for an archive page."""

    # Badge rendering for GMM-style extra fields
    badge_js = ""
    if conf["extra_badges"]:
        badge_parts = []
        for field in conf["extra_badges"]:
            css_class = "flag-badge flag-badge--elevated" if field == "system_stress_label" else "regime-badge"
            badge_parts.append(
                f"(issue.{field} ? '<span class=\"{css_class}\" style=\"margin-right:var(--space-2)\">' + esc(issue.{field}) + '</span>' : '')"
            )
        badge_js = f"""
        var badgeHtml = {' + '.join(badge_parts)};
        if (badgeHtml) {{
          badgeHtml = '<div style="display:flex;gap:var(--space-2);flex-wrap:wrap;margin-top:var(--space-2)">' + badgeHtml + '</div>';
        }}"""
    else:
        badge_js = "\n        var badgeHtml = '';"

    # Entry renderer (shared across grouped and flat)
    entry_fn = f"""
    function renderEntry(issue) {{
      var pub = issue.published
        ? new Date(issue.published).toLocaleDateString('en-GB', {{day:'numeric', month:'long', year:'numeric'}})
        : '';
      var anchor = 'issue-' + (issue.issue || issue.slug || '');
      var allDeltas = issue.delta_strip || [];
      var deltaHtml = allDeltas.slice(0, 3).map(function (d) {{
        return '<span class="badge badge--accent" style="margin-right:4px">' + esc(d.module_tag || d.module || '') + '</span>' +
          '<span style="font-size:var(--text-xs);color:var(--color-text-muted);margin-right:var(--space-3)">' + esc(d.title || '') + '</span>';
      }}).join('');
      if (allDeltas.length > 3) {{
        deltaHtml += '<span style="font-size:var(--text-xs);color:var(--color-text-muted)">\\u2026 and ' + (allDeltas.length - 3) + ' more</span>';
      }}
{badge_js}

      return '<div class="archive-entry" id="' + esc(anchor) + '" style="scroll-margin-top:calc(var(--network-bar-height,40px) + var(--nav-height,52px) + var(--space-4,16px))">' +
        '<div class="archive-entry__date">' + pub + '</div>' +
        '<div style="flex:1;min-width:0">' +
          '<div class="archive-entry__issue">Issue ' + esc(issue.issue || '\\u2014') + ' \\u00b7 ' + esc(issue.week_label || '') + '</div>' +
          '<div class="archive-entry__signal">' + esc(issue.signal || '') + '</div>' +
          badgeHtml +
          (deltaHtml ? '<div class="archive-entry__delta" style="margin-top:var(--space-2);line-height:1.8">' + deltaHtml + '</div>' : '') +
          (issue.source_url ? '<div style="margin-top:var(--space-3)"><a class="archive-entry__link" href="' + esc(issue.source_url) + '" target="_blank" rel="noopener">Full brief \\u2192</a></div>' : '') +
        '</div>' +
      '</div>';
    }}"""

    # Flat vs year-grouped rendering
    if conf["group_by_year"]:
        render_body = """
      // Group by year
      var byYear = {};
      sorted.forEach(function (issue) {
        var year = (issue.published || '').split('-')[0] || 'Unknown';
        if (!byYear[year]) byYear[year] = [];
        byYear[year].push(issue);
      });

      var allHtml = '';
      Object.keys(byYear).sort().reverse().forEach(function (year) {
        sidebarHtml += '<li><a href="#section-archive-' + year + '">' + year + '</a></li>';
        var yearHtml = byYear[year].map(function (issue) {
          sidebarHtml += '<li style="padding-left:var(--space-2)"><a href="#issue-' + (issue.issue||'') + '" style="font-size:var(--text-sm)">Issue ' + (issue.issue||'\\u2014') + '</a></li>';
          return renderEntry(issue);
        }).join('');
        allHtml += '<div class="module-section" id="section-archive-' + year + '">' +
          '<div class="module-header"><div class="module-title">' + year + '</div></div>' +
          '<div>' + yearHtml + '</div>' +
        '</div>';
      });
      listEl.innerHTML = allHtml;"""
    else:
        render_body = """
      var html = '';
      sorted.forEach(function (issue) {
        sidebarHtml += '<li><a href="#issue-' + (issue.issue||'') + '">Issue ' + esc(issue.issue||'\\u2014') + ' \\u00b7 ' + esc(issue.week_label||'') + '</a></li>';
        html += renderEntry(issue);
      });
      listEl.innerHTML = html;"""

    return f"""document.addEventListener('DOMContentLoaded', function () {{
  function esc(s) {{
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}
{entry_fn}

  fetch('data/archive.json')
    .then(function (r) {{ return r.json(); }})
    .then(function (issues) {{
      var listEl  = document.getElementById('archive-list');
      var countEl = document.getElementById('archive-count');
      var sidebar = document.getElementById('sidebar-links');

      if (!issues || !issues.length) {{
        if (countEl) countEl.textContent = '0 issues';
        listEl.innerHTML = '<p class="text-muted">No archived issues yet.</p>';
        return;
      }}

      var sorted = issues.slice().sort(function (a, b) {{
        return new Date(b.published || 0) - new Date(a.published || 0);
      }});

      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      var sidebarHtml = '<li><a href="#section-archive">All Issues</a></li>';
{render_body}
      if (sidebar) sidebar.innerHTML = sidebarHtml;
    }})
    .catch(function () {{
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive data.</div>';
    }});
}});"""


# ── HTML Shell ────────────────────────────────────────────────────────
def build_archive(slug, abbr, name, conf):
    js = build_js(slug, conf)
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
{js}
</script>
</body>
</html>'''


# ── Generate ──────────────────────────────────────────────────────────
for slug, (abbr, name) in MONITORS.items():
    conf = ARCHIVE_CONFIG[slug]
    out_path = os.path.join(STATIC, slug, "archive.html")
    page_html = build_archive(slug, abbr, name, conf)
    with open(out_path, "w") as f:
        f.write(page_html)
    lines = page_html.count("\n") + 1
    print(f"  {slug}/archive.html — {lines} lines ✓")

print(f"\nDone: 7 archive pages generated from ARCHIVE_CONFIG")
print(f"Config dimensions: group_by_year, extra_badges, sidebar_dynamic")
print(f"To customise a monitor, edit ARCHIVE_CONFIG in this file — no fragment files needed.")

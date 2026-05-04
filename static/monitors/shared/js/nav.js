/* ============================================================
   Asymmetric Intelligence Monitor — nav.js  v1.5
   Intersection Observer scroll-spy for .module-section[id]
   Updates active state on .monitor-nav a, .monitor-sidebar a,
   and .module-nav-strip a matching href="#id".
   Mobile: hamburger toggle for sidebar.
   Network bar + site bar: auto-injected if absent (Blueprint standard).
   Site bar: About | Search | theme toggle | Subscribe — all pages.
   Exposes window.AsymNav.init()
   ============================================================ */
(function () {
  'use strict';

  /* ── Network Bar Auto-Injection ──────────────────────────── */
  /* Injected once at script parse time — before DOMContentLoaded —
     so it appears at the top of the viewport immediately.
     Safe to call repeatedly; skips if already present.          */
  function injectNetworkBar() {
    if (document.querySelector('[data-asym-network-bar]')) return;

    // Offset styles — injected into <head> so they apply before paint
    // Offset styles — fallback for pages without base.css
    /* Heights: network bar 40px, site bar 44px = 84px combined */
    var NB_H = 40;
    var SB_H = 44;
    var CHROME_H = NB_H + SB_H; /* 84px */

    if (!document.querySelector('[data-asym-nb-styles]')) {
      var style = document.createElement('style');
      style.setAttribute('data-asym-nb-styles', '');
      style.textContent = [
        'html{scrollbar-gutter:stable}',
        'html.no-scrollbar-gutter{scrollbar-gutter:auto}',
        'body{padding-top:' + NB_H + 'px!important}',
        '.monitor-nav{position:sticky!important;top:' + CHROME_H + 'px!important}',
        '.monitor-sidebar{top:calc(' + CHROME_H + 'px + 52px)!important;height:calc(100vh - ' + CHROME_H + 'px - 52px)!important}',
        'nav.sidebar,#sidebar,.sidebar-header{top:' + CHROME_H + 'px!important}',
        'nav.sidebar{height:calc(100vh - ' + CHROME_H + 'px)!important}',
        '.left-nav{top:' + CHROME_H + 'px!important;height:calc(100vh - ' + CHROME_H + 'px)!important}',
        '.header:not([data-asym-network-bar]){top:' + CHROME_H + 'px!important}',
        'nav:not([data-asym-network-bar]):not(.monitor-nav):not(.site-bar){top:' + CHROME_H + 'px!important}',
        '.nb-links{display:flex}',
        '@media(max-width:640px){.nb-links{display:none}}',
        /* Site bar styles */
        '.site-bar{position:sticky;top:' + NB_H + 'px;z-index:100;height:' + SB_H + 'px;',
          'display:flex;align-items:center;padding:0 clamp(1rem,4vw,2rem);gap:1.5rem;',
          'border-bottom:1px solid var(--color-border,rgba(40,37,29,0.10));',
          'background:var(--color-bg,#f9f8f6);',
          "font-family:'Satoshi','Inter',sans-serif}",
        '.site-bar__spacer{flex:1;display:none}', /* spacer hidden — links use margin-left:auto */
        '.site-bar__links{display:flex;align-items:center;gap:0;list-style:none;padding:0;margin:0;margin-left:auto}',
        '.site-bar__links a{font-size:0.8rem;font-weight:500;color:var(--color-text-muted,#6b6660);',
          'text-transform:uppercase;letter-spacing:0.06em;padding:0.25rem 0.75rem;border-radius:4px;',
          'text-decoration:none;transition:color 0.15s,background 0.15s;white-space:nowrap}',
        '.site-bar__links a:hover{color:var(--color-text,#1a1917);',
          'background:color-mix(in srgb,var(--color-text,#1a1917) 8%,transparent)}',
        '.site-bar__actions{display:flex;align-items:center;gap:0.75rem}',
        '.site-bar__subscribe{display:inline-flex;align-items:center;padding:5px 14px;',
          'font-size:0.85rem;font-weight:700;color:var(--color-primary,#01696f);',
          'border:1.5px solid var(--color-primary,#01696f);border-radius:6px;',
          'text-decoration:none;transition:background 0.15s,color 0.15s;',
          'letter-spacing:0.01em;white-space:nowrap}',
        '.site-bar__subscribe:hover{background:var(--color-primary,#01696f);color:#fff}',
        '.site-bar .theme-toggle{background:none;border:1px solid var(--color-border,#d8d4cd);',
          'border-radius:4px;width:32px;height:32px;display:flex;align-items:center;',
          'justify-content:center;cursor:pointer;color:var(--color-text-muted,#6b6660);',
          'transition:border-color 0.15s,color 0.15s}',
        '.site-bar .theme-toggle:hover{border-color:var(--color-text,#1a1917);color:var(--color-text,#1a1917)}',
        '.site-bar .theme-toggle .icon-sun,.site-bar .theme-toggle .icon-moon{width:15px;height:15px}',
        '[data-theme="dark"] .site-bar .icon-sun{display:none}',
        '[data-theme="light"] .site-bar .icon-moon,:not([data-theme]) .site-bar .icon-moon{display:none}',
        '[data-theme="dark"] .site-bar .icon-moon{display:block}',
        '@media(max-width:640px){.site-bar__actions{display:none}}',
        /* ── Light-mode overrides for standalone pages (Map, Network etc.) ──── */
        /* These pages hardcode dark `:root` colours; this layer makes toggle work */
        '[data-theme="light"] body{background:#f9f8f6!important;color:#28251d!important}',
        '[data-theme="light"] .controls{background:rgba(249,248,246,0.95)!important;border-color:rgba(40,37,29,0.10)!important}',
        '[data-theme="light"] .controls__label,[data-theme="light"] .filter-btn{color:#7a7974!important}',
        '[data-theme="light"] .filter-btn.active,[data-theme="light"] .filter-btn:hover{background:rgba(40,37,29,0.08)!important;color:#28251d!important}',
        '[data-theme="light"] .info-panel,[data-theme="light"] .panel{background:#f3f0ec!important;border-color:rgba(40,37,29,0.10)!important;color:#28251d!important}',
        '[data-theme="light"] .info-panel__title{color:#28251d!important}',
        '[data-theme="light"] .info-panel p,[data-theme="light"] .info-panel span,[data-theme="light"] .panel__label{color:#7a7974!important}',
        '[data-theme="light"] .info-panel a,[data-theme="light"] .panel a{color:#01696f!important}',
        /* Site bar appearance by theme */
        '[data-theme="dark"] .site-bar{background:#1c1b19!important;border-color:#2d2c2a!important}',
        '[data-theme="dark"] .site-bar__links a{color:#a8a7a4!important}',
        '[data-theme="dark"] .site-bar__links a:hover{color:#e0dfdc!important}',
        '[data-theme="dark"] .site-bar .theme-toggle{border-color:#3d3a35!important;color:#a8a7a4!important}',
        '[data-theme="dark"] .site-bar .theme-toggle:hover{border-color:#e0dfdc!important;color:#e0dfdc!important}',
        '[data-theme="dark"] .site-bar__subscribe{color:#4f98a3!important;border-color:#4f98a3!important}',
        '[data-theme="dark"] .site-bar__subscribe:hover{background:#4f98a3!important;color:#fff!important}'
      ].join('');
      document.head.appendChild(style);
    }

    var nav = document.createElement('nav');
    nav.setAttribute('data-asym-network-bar', '');
    nav.setAttribute('aria-label', 'Asymmetric Intelligence network');
    nav.style.cssText = [
      'height:40px','position:fixed','top:0','left:0','right:0',
      'z-index:9999','background:#1a1918','border-bottom:1px solid #2d2c2a',
      "font-family:'Satoshi','Inter',sans-serif",'font-size:15px',
      'letter-spacing:0.02em','display:flex','align-items:center',
      'padding:0 24px','gap:1.5rem'
    ].join(';');

    nav.innerHTML = [
      '<a href="https://asym-intel.info" style="display:flex;align-items:center;gap:0.5rem;text-decoration:none;color:#e0dfdc;font-weight:500;flex-shrink:0">',
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">',
          '<rect x="2" y="4" width="10" height="2.5" rx="1.25" fill="#4f98a3"/>',
          '<rect x="6" y="9" width="12" height="2.5" rx="1.25" fill="#4f98a3" opacity=".65"/>',
          '<rect x="2" y="14" width="7" height="2.5" rx="1.25" fill="#4f98a3" opacity=".35"/>',
        '</svg>',
        '<span>Asymmetric Intelligence</span>',
      '</a>',
      '<div style="flex:1"></div>',
      '<nav class="nb-links" style="display:flex;align-items:center;gap:1.25rem;" aria-label="Platform sections">',
        '<a href="https://asym-intel.info/monitors/" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">Monitors</a>',
        '<a href="https://asym-intel.info/network/" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">Network</a>',
        '<a href="https://asym-intel.info/map/" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">World Map</a>',
        '<a href="https://a-i.gi/" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">Commercial</a>',
      '</nav>'
    ].join('');

    // Insert as very first child of <body>, or before <body> opens if called early
    var body = document.body || document.querySelector('body');
    if (body) {
      body.insertBefore(nav, body.firstChild);
    } else {
      // Called before body exists — defer to DOMContentLoaded
      document.addEventListener('DOMContentLoaded', function () {
        document.body.insertBefore(nav, document.body.firstChild);
      });
    }
  }

  // Run immediately so bar appears before any other paint
  injectNetworkBar();

  // Map and Network pages use overflow:hidden (no scrollbar) — opt out of
  // scrollbar-gutter so they don't get an empty gap on the right.
  (function () {
    var p = window.location.pathname;
    if (p.indexOf('/map/') !== -1 || p.indexOf('/network/') !== -1) {
      document.documentElement.classList.add('no-scrollbar-gutter');
    }
  })();


  /* ── Site Bar Injection ──────────────────────────────────────
     About | Search | [theme toggle] | Subscribe
     Injected on ALL pages below the network bar.
     Replaces Hugo site-header.html partial on Hugo pages.
     On monitor pages, sits between network bar and monitor strip.
     ──────────────────────────────────────────────────────────── */
  function injectSiteBar() {
    // Skip if already present (idempotent)
    if (document.querySelector('.site-bar')) return;

    // Hide Hugo site-header if it exists (nav.js now owns this bar)
    var hugoSiteNav = document.querySelector('.site-nav');
    if (hugoSiteNav) hugoSiteNav.style.display = 'none';

    var bar = document.createElement('nav');
    bar.className = 'site-bar';
    bar.setAttribute('aria-label', 'Site navigation');

    bar.innerHTML = [
      '<div class="site-bar__spacer"></div>',
      '<ul class="site-bar__links" role="list">',
        '<li><a href="/about/">About</a></li>',
        '<li><a href="/search/">Search</a></li>',
      '</ul>',
      '<div class="site-bar__actions">',
        '<button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">',
          '<svg class="icon-sun" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">',
            '<circle cx="7.5" cy="7.5" r="3"/>',
            '<line x1="7.5" y1="1" x2="7.5" y2="2.5"/><line x1="7.5" y1="12.5" x2="7.5" y2="14"/>',
            '<line x1="1" y1="7.5" x2="2.5" y2="7.5"/><line x1="12.5" y1="7.5" x2="14" y2="7.5"/>',
          '</svg>',
          '<svg class="icon-moon" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">',
            '<path d="M7.5 1a6.5 6.5 0 1 0 6.5 6.5A6.5 6.5 0 0 0 7.5 1zm0 12A5.5 5.5 0 1 1 11.7 3.8 6.5 6.5 0 0 0 7.5 13z"/>',
          '</svg>',
        '</button>',
        '<a class="site-bar__subscribe" href="/subscribe/">Subscribe</a>',
      '</div>'
    ].join('');

    // Insert after network bar
    var nb = document.querySelector('[data-asym-network-bar]');
    if (nb && nb.nextSibling) {
      nb.parentNode.insertBefore(bar, nb.nextSibling);
    } else if (document.body) {
      // Fallback: insert as second child of body
      var first = document.body.firstChild;
      if (first && first.nextSibling) {
        document.body.insertBefore(bar, first.nextSibling);
      } else {
        document.body.appendChild(bar);
      }
    }

    // Hide theme toggle on Map/Network pages (toggle doesn't work there;
    // full light mode for those pages is a future task)
    var p = window.location.pathname;
    if (p.indexOf('/map/') !== -1 || p.indexOf('/network/') !== -1) {
      var toggleBtn = bar.querySelector('.theme-toggle');
      if (toggleBtn) toggleBtn.style.display = 'none';
    }

    // Wire theme toggle
    if (window.AsymTheme && window.AsymTheme._wire) {
      window.AsymTheme._wire();
    }

    // Highlight active link
    var path = window.location.pathname;
    bar.querySelectorAll('.site-bar__links a').forEach(function (a) {
      if (path.indexOf(a.getAttribute('href')) === 0) {
        a.style.color = 'var(--color-text, #1a1917)';
        a.style.background = 'color-mix(in srgb, var(--color-text, #1a1917) 8%, transparent)';
      }
    });
  }

  // Inject site bar at parse time (same as network bar)
  if (document.body) {
    injectSiteBar();
  } else {
    document.addEventListener('DOMContentLoaded', injectSiteBar);
  }


  /* ── Cross-Monitor Strip Injection ──────────────────────────
     Single source of truth for the cross-monitor navigation strip:
     MONITOR_REGISTRY (slug-keyed) + MONITOR_TRIAGE_ORDER (abbr array)
     are inlined from monitor-registry.json by
     tools/inline_registry_into_navjs.py at build/commit time.
     ENGINE-RULES §17: never construct monitor URLs by string concat —
     every pill href = registry `url` field, resolved through the abbr.
     Adding/reordering monitors = edit monitor-registry.json only.
     Hierarchy: network bar (40px) → strip (50px) → monitor nav (52px)
     ──────────────────────────────────────────────────────────── */

  function injectMonitorStrip() {
    // Only on monitor pages
    if (window.location.pathname.indexOf('/monitors/') === -1) return;
    // Skip if already present
    if (document.querySelector('.monitor-strip')) return;
    // Defensive: registry+triage must be available (inliner has run)
    if (typeof MONITOR_REGISTRY === 'undefined' ||
        typeof MONITOR_TRIAGE_ORDER === 'undefined') {
      return;
    }

    // Build {abbr -> slug} index over MONITOR_REGISTRY for triage_order resolution.
    var slugByAbbr = {};
    for (var s in MONITOR_REGISTRY) {
      if (Object.prototype.hasOwnProperty.call(MONITOR_REGISTRY, s)) {
        slugByAbbr[MONITOR_REGISTRY[s].abbr] = s;
      }
    }

    var currentSlug = getMonitorSlug();
    var pills = '';

    MONITOR_TRIAGE_ORDER.forEach(function (abbr) {
      var slug = slugByAbbr[abbr];
      if (!slug) return;                  // abbr not in registry — skip silently
      var m = MONITOR_REGISTRY[slug];
      if (!m) return;
      var active = (slug === currentSlug) ? ' monitor-strip__pill--active' : '';
      // href = canonical registry URL — NEVER concatenate (ENGINE-RULES §17)
      pills +=
        '<a class="monitor-strip__pill' + active + '"' +
        ' href="' + m.url + '"' +
        ' data-monitor="' + m.abbr + '"' +
        ' style="--pill-accent:' + m.accent + '">' +
          '<img class="monitor-strip__icon" src="' + m.svg_url + '"' +
          ' alt="" width="24" height="24" aria-hidden="true">' +
          '<span>' + m.strip_label + '</span>' +
        '</a>';
    });

    var strip = document.createElement('nav');
    strip.className = 'monitor-strip';
    strip.setAttribute('role', 'navigation');
    strip.setAttribute('aria-label', 'Monitor navigation');
    strip.innerHTML = '<span class="monitor-strip__label">Monitors</span>' + pills;

    // Insert before .monitor-nav (hierarchy: network bar → strip → monitor nav)
    var monitorNav = document.querySelector('.monitor-nav');
    if (monitorNav && monitorNav.parentNode) {
      monitorNav.parentNode.insertBefore(strip, monitorNav);
    }

    // Adjust monitor-nav sticky top: 40 (nb) + 44 (site bar) + 50 (strip) = 134px
    if (monitorNav) {
      monitorNav.style.setProperty('top', '134px', 'important');
    }
    // Adjust sidebar offset too
    var sidebar = document.querySelector('.monitor-sidebar');
    if (sidebar) {
      sidebar.style.setProperty('top', 'calc(134px + 52px)', 'important');
      sidebar.style.setProperty('height', 'calc(100vh - 134px - 52px)', 'important');
    }
  }

  // Strip injection deferred until AFTER MONITOR_REGISTRY is defined below.
  // (See bottom-of-file binding — injectMonitorStrip() now depends on the
  // inlined registry, which is declared further down in this IIFE.)


  /* ── Monitor Nav Injection ───────────────────────────────────
     Derives current monitor slug and page from the URL path.
     Replaces .monitor-nav__links contents with the canonical
     9-link set. Adding a new page = one line here, zero HTML.
     ──────────────────────────────────────────────────────────── */

  /* ── Monitor Chrome Registry ─────────────────────────────────
     Single source of truth for per-monitor identity:
     accent colour, SVG logo, full name, abbreviation.
     Used by injectMonitorNav(), injectMonitorBrand(),
     injectThemeToggle(), injectMonitorFooter().
     Adding a new monitor = one entry here, zero HTML changes.
     ──────────────────────────────────────────────────────────── */
  /* BEGIN @REGISTRY_INLINE */
  var MONITOR_REGISTRY = {
    "democratic-integrity": {"abbr": "WDM", "name": "World Democracy Monitor", "accent": "#61a5d2", "url": "https://asym-intel.info/monitors/democratic-integrity/", "svg_url": "https://asym-intel.info/images/monitors/wdm.svg", "vb": "0 0 32 32", "strip_label": "World Democracy"},
    "macro-monitor": {"abbr": "GMM", "name": "Global Macro Monitor", "accent": "#22a0aa", "url": "https://asym-intel.info/monitors/macro-monitor/", "svg_url": "https://asym-intel.info/images/monitors/gmm.svg", "vb": "0 0 38 38", "strip_label": "Global Macro", "accent_2": "#e87040"},
    "european-strategic-autonomy": {"abbr": "ESA", "name": "European Strategic Autonomy Monitor", "accent": "#5b8db0", "url": "https://asym-intel.info/monitors/european-strategic-autonomy/", "svg_url": "https://asym-intel.info/images/monitors/esa.svg", "vb": "0 0 36 36", "strip_label": "Strategic Autonomy"},
    "fimi-cognitive-warfare": {"abbr": "FCW", "name": "FIMI & Cognitive Warfare Monitor", "accent": "#38bdf8", "url": "https://asym-intel.info/monitors/fimi-cognitive-warfare/", "svg_url": "https://asym-intel.info/images/monitors/fcw.svg", "vb": "0 0 36 36", "strip_label": "FIMI & Cognitive Warfare", "accent_2": "#dc2626"},
    "ai-governance": {"abbr": "AIM", "name": "AI Governance Monitor", "accent": "#3a7d5a", "url": "https://asym-intel.info/monitors/ai-governance/", "svg_url": "https://asym-intel.info/images/monitors/aim.svg", "vb": "0 0 36 36", "strip_label": "Artificial Intelligence"},
    "environmental-risks": {"abbr": "ERM", "name": "Environmental Risks Monitor", "accent": "#4caf7d", "url": "https://asym-intel.info/monitors/environmental-risks/", "svg_url": "https://asym-intel.info/images/monitors/erm.svg", "vb": "0 0 36 36", "strip_label": "Environmental Risks"},
    "conflict-escalation": {"abbr": "SCEM", "name": "Strategic Conflict & Escalation Monitor", "accent": "#dc2626", "url": "https://asym-intel.info/monitors/conflict-escalation/", "svg_url": "https://asym-intel.info/images/monitors/scem.svg", "vb": "0 0 36 36", "strip_label": "Strategic Conflict"},
     "advennt": {"abbr": "ADVENNT", "name": "Advennt — Gambling Regulatory Intelligence", "accent": "#f5a524", "url": "https://advennt.io/", "svg_url": null, "vb": null, "strip_label": "Advennt"},
  };

  var MONITOR_TRIAGE_ORDER = ["GMM", "SCEM", "FCW", "AIM", "WDM", "ESA", "ERM", "ADVENNT"];
  /* END @REGISTRY_INLINE */

  // Inject strip at parse time for immediate render (same as network bar).
  // MUST be after MONITOR_REGISTRY + MONITOR_TRIAGE_ORDER are defined above.
  if (document.body) {
    injectMonitorStrip();
  } else {
    document.addEventListener('DOMContentLoaded', injectMonitorStrip);
  }

  /* Derive monitor slug from URL path: /monitors/{slug}/{page}.html */
  function getMonitorSlug() {
    var parts = window.location.pathname.split('/');
    var idx = parts.indexOf('monitors');
    return (idx !== -1 && parts[idx + 1]) ? parts[idx + 1] : null;
  }

  /* ── Brand injection ─────────────────────────────────────────
     Replaces .monitor-nav__brand contents with registry SVG + name.
     No-ops gracefully if brand element or registry entry missing. */
  function injectMonitorBrand() {
    var brand = document.querySelector('.monitor-nav__brand');
    if (!brand) return;
    var slug = getMonitorSlug();
    var m = slug && MONITOR_REGISTRY[slug];
    if (!m) return;

    // Set CSS accent token
    document.documentElement.style.setProperty('--monitor-accent', m.accent);

    brand.innerHTML =
      '<img src="' + m.svg_url + '" width="18" height="18" alt="" aria-hidden="true" style="flex-shrink:0">' +
      '<span>' + m.name + '</span>';
  }

  /* ── Theme toggle injection ──────────────────────────────────
     Theme toggle now lives in the site bar (injected by injectSiteBar).
     This function is kept as a no-op for backward compatibility. */
  function injectThemeToggle() {
    // Theme toggle is now in the site bar — no monitor-nav injection needed.
    // Re-wire in case site bar was injected after theme.js DOMContentLoaded.
    if (window.AsymTheme && window.AsymTheme._wire) {
      window.AsymTheme._wire();
    }
  }

  /* ── Canonical powered-by block ─────────────────────────────
     Single source of truth for logo + brand name + link.
     Every footer on every powered-by site uses this.
     To change the logo or text, edit ONLY here. */
  var ASYM_LOGO_SVG =
    '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" aria-hidden="true">' +
      '<rect x="2" y="4" width="10" height="2.5" rx="1.25" fill="#4f98a3"/>' +
      '<rect x="6" y="9" width="12" height="2.5" rx="1.25" fill="#4f98a3" opacity=".65"/>' +
      '<rect x="2" y="14" width="7" height="2.5" rx="1.25" fill="#4f98a3" opacity=".35"/>' +
    '</svg>';

  var ASYM_BRAND_NAME = 'Asymmetric Intelligence';
  var ASYM_COMMERCIAL_URL = 'https://a-i.gi/';

  var POWERED_BY_HTML =
    '<a href="' + ASYM_COMMERCIAL_URL + '" style="display:inline-flex;align-items:center;gap:0.35rem;text-decoration:none;color:inherit">' +
      ASYM_LOGO_SVG +
      ' Powered by ' + ASYM_BRAND_NAME +
    '</a>';

  /* ── Footer injection (monitors) ────────────────────────────
     Normalises .monitor-footer markup to canonical form.
     No-ops if footer absent. */
  function injectMonitorFooter() {
    var footer = document.querySelector('.monitor-footer');
    if (!footer) return;

    footer.innerHTML =
      '<div style="display:flex;align-items:center;justify-content:center;gap:0.4rem;margin-bottom:0.5rem">' +
        '<a href="' + ASYM_COMMERCIAL_URL + '" style="display:inline-flex;align-items:center;gap:0.4rem;text-decoration:none;color:inherit">' +
          ASYM_LOGO_SVG.replace('width="16"','width="18"').replace('height="16"','height="18"') +
          '<span style="font-weight:500">' + ASYM_BRAND_NAME + '</span>' +
        '</a>' +
      '</div>' +
      '<span>' +
        '&copy; ' + new Date().getFullYear() + ' ' + ASYM_BRAND_NAME + '. ' +
        'Published by <a href="https://ramparts.gi/people/peter-howitt/">Peter Howitt</a>. ' +
        'Content is published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>. ' +
        '<a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener">Produced with Perplexity Computer</a>.' +
      '</span>';
  }

  /* ── Shared footer for powered-by sites ─────────────────────
     Called by external sites: AsymNav.footer({ ... })
     Finds .site-footer (or opts.target selector) and renders
     site-specific content PLUS the canonical powered-by block.

     opts.brand     — site brand name, e.g. 'ADVENNT' (required)
     opts.tagline   — one-line description (optional)
     opts.legal     — legal/disclaimer HTML string (optional)
     opts.extras    — array of additional HTML lines (optional)
     opts.target    — CSS selector for footer element (default '.site-footer')
  */
  function renderFooter(opts) {
    if (!opts || !opts.brand) return;
    var sel = opts.target || '.site-footer';
    var footer = document.querySelector(sel);
    if (!footer) return;

    var html = '<div style="text-align:center;padding:40px 24px">';

    // Site brand
    html += '<div style="font-weight:700;font-size:15px;letter-spacing:0.03em">' + opts.brand + '</div>';

    // Tagline
    if (opts.tagline) {
      html += '<div style="font-size:13px;opacity:0.6;margin-top:8px">' + opts.tagline + '</div>';
    }

    // Legal
    if (opts.legal) {
      html += '<div style="font-size:11px;opacity:0.5;margin-top:12px;max-width:640px;margin-left:auto;margin-right:auto;line-height:1.5">' + opts.legal + '</div>';
    }

    // Extras (e.g. 'Member of Gibraltar Finance Centre Council')
    if (opts.extras && opts.extras.length) {
      for (var i = 0; i < opts.extras.length; i++) {
        html += '<div style="font-size:11px;opacity:0.5;margin-top:6px">' + opts.extras[i] + '</div>';
      }
    }

    // Canonical powered-by — always last, never omittable
    html += '<div style="font-size:11px;letter-spacing:0.04em;margin-top:12px;opacity:0.6">' + POWERED_BY_HTML + '</div>';

    html += '</div>';
    footer.innerHTML = html;
  }

  /* ── AI discovery link tag ──────────────────────────────────
     Injects <link rel="alternate" type="text/markdown"> for AI crawlers.
     Points to report-latest.md sidecar (when it exists). */
  function injectDiscoveryTag() {
    var slug = getMonitorSlug();
    if (!slug) return;
    var link = document.createElement('link');
    link.rel = 'alternate';
    link.type = 'text/markdown';
    link.title = 'AI-Readable Version';
    link.href = '/monitors/' + slug + '/data/report-latest.md';
    document.head.appendChild(link);
  }

  var MONITOR_NAV_LINKS = [
    { href: 'overview.html',       label: 'Overview'         },
    { href: 'dashboard.html',      label: 'Dashboard'        },
    { href: 'report.html',         label: 'Latest Issue'     },
    { href: 'persistent.html',     label: 'Living Knowledge' },
    { href: 'chatter.html',        label: 'Chatter'          },
    { href: 'cross-monitor.html',  label: 'Cross-Monitor'    },
    { href: 'archive.html',        label: 'Archive'          },
    { href: 'search.html',         label: 'Search'           },
    { href: 'about.html',          label: 'About'            },
  ];

  function injectMonitorNav() {
    var ul = document.querySelector('.monitor-nav__links');
    if (!ul) return;

    // Derive current page filename from URL
    var pathname = window.location.pathname;
    var currentPage = pathname.split('/').pop() || '';
    // Strip query/hash
    currentPage = currentPage.split('?')[0].split('#')[0];

    // Build canonical li list
    var html = '';
    MONITOR_NAV_LINKS.forEach(function (link) {
      var isActive = (link.href === currentPage);
      html += '<li><a href="' + link.href + '"' +
        (isActive ? ' class="active"' : '') +
        '>' + link.label + '</a></li>';
    });

    ul.innerHTML = html;

    // Re-wire hamburger click-to-close on the new anchors
    var hamburger = document.querySelector('.monitor-nav__hamburger');
    if (hamburger) {
      ul.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
          ul.classList.remove('monitor-nav__links--open');
          hamburger.setAttribute('aria-expanded', 'false');
        });
      });
    }
  }

  function init() {
    injectMonitorBrand();
    injectMonitorNav();
    injectThemeToggle();
    injectMonitorFooter();
    injectDiscoveryTag();
    setupScrollSpy();
    setupHamburger();
    setupSiteNavHamburger();
    setupSidebarOverlay();
    setupCmsExpanders();
    setupVersionToggles();
    setupTabPanels();
  }


  /* ── Hugo site-nav hamburger ─────────────────────────────── */
  function setupSiteNavHamburger() {
    var btn   = document.querySelector('.site-nav__hamburger');
    var links = document.querySelector('.site-nav__links');
    if (!btn || !links) return;
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('site-nav__links--open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('site-nav__links--open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('click', function (e) {
      if (links.classList.contains('site-nav__links--open') &&
          !links.contains(e.target) && !btn.contains(e.target)) {
        links.classList.remove('site-nav__links--open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ── Scroll Spy ── */
  function setupScrollSpy() {
    var sections = document.querySelectorAll('.module-section[id]');
    if (!sections.length) return;

    var navSelectors = [
      '.module-nav-strip a',
      '.monitor-sidebar a',
      '.monitor-nav__links a'
    ].join(', ');
    var navLinks = document.querySelectorAll(navSelectors);
    if (!navLinks.length) return;

    var activeId = null;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = entry.target.getAttribute('id');
          if (id !== activeId) {
            activeId = id;
            navLinks.forEach(function (link) {
              var href = link.getAttribute('href');
              if (href === '#' + id) {
                link.classList.add('active');
              } else {
                link.classList.remove('active');
              }
            });
          }
        }
      });
    }, { rootMargin: '-10% 0px -60% 0px', threshold: 0 });

    sections.forEach(function (s) { observer.observe(s); });
  }

  /* ── Hamburger / Mobile Nav ── */
  function setupHamburger() {
    var hamburger = document.querySelector('.monitor-nav__hamburger');
    var navLinks  = document.querySelector('.monitor-nav__links');
    if (!hamburger || !navLinks) return;

    hamburger.addEventListener('click', function () {
      var open = navLinks.classList.toggle('monitor-nav__links--open');
      hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // Close on nav link click (mobile)
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navLinks.classList.remove('monitor-nav__links--open');
        hamburger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ── Sidebar overlay toggle (mobile) ── */
  function setupSidebarOverlay() {
    var sidebar   = document.querySelector('.monitor-sidebar');
    var hamburger = document.querySelector('.monitor-nav__hamburger');
    if (!sidebar || !hamburger) return;

    var sidebarToggle = document.querySelector('.sidebar-toggle');
    if (!sidebarToggle) sidebarToggle = hamburger;

    function openSidebar() {
      sidebar.classList.add('monitor-sidebar--open');
      sidebarToggle.setAttribute('aria-expanded', 'true');
    }
    function closeSidebar() {
      sidebar.classList.remove('monitor-sidebar--open');
      sidebarToggle.setAttribute('aria-expanded', 'false');
    }

    sidebarToggle.addEventListener('click', function () {
      if (sidebar.classList.contains('monitor-sidebar--open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    sidebar.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', closeSidebar);
    });

    document.addEventListener('click', function (e) {
      if (
        sidebar.classList.contains('monitor-sidebar--open') &&
        !sidebar.contains(e.target) &&
        !sidebarToggle.contains(e.target)
      ) {
        closeSidebar();
      }
    });
  }

  /* ── Cross-monitor panel read-more expanders ── */
  function setupCmsExpanders() {
    document.querySelectorAll('.cms-read-more').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var body = btn.previousElementSibling;
        if (!body) return;
        if (body.classList.contains('cms-flag__body--collapsed')) {
          body.classList.remove('cms-flag__body--collapsed');
          btn.textContent = 'Show less';
        } else {
          body.classList.add('cms-flag__body--collapsed');
          btn.textContent = 'Read more →';
        }
      });
    });
  }

  /* ── Version history toggles ── */
  function setupVersionToggles() {
    document.querySelectorAll('.version-history__toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var vh = btn.nextElementSibling;
        if (!vh) vh = btn.parentElement.querySelector('.version-history');
        if (!vh) return;
        var open = vh.classList.toggle('version-history--open');
        btn.textContent = open ? 'Hide history ↑' : 'Version history →';
      });
    });
  }

  /* ── Tab panels ── */
  function setupTabPanels() {
    document.querySelectorAll('.tabs').forEach(function (tabGroup) {
      var buttons = tabGroup.querySelectorAll('.tab-btn');
      buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          buttons.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var panelContainer = tabGroup.nextElementSibling;
          if (!panelContainer) return;
          var panels = panelContainer.querySelectorAll('.tab-panel');
          var target = btn.getAttribute('data-tab');
          panels.forEach(function (p) {
            if (p.getAttribute('data-tab') === target) {
              p.classList.add('active');
            } else {
              p.classList.remove('active');
            }
          });
        });
      });
    });
  }

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API
  window.AsymNav = { init: init, injectNetworkBar: injectNetworkBar, footer: renderFooter };
})();

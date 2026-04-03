/* ============================================================
   Asymmetric Intelligence Monitor — nav.js  v1.3
   Intersection Observer scroll-spy for .module-section[id]
   Updates active state on .monitor-nav a, .monitor-sidebar a,
   and .module-nav-strip a matching href="#id".
   Mobile: hamburger toggle for sidebar.
   Network bar: auto-injected if absent (Blueprint standard).
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
    if (!document.querySelector('[data-asym-nb-styles]')) {
      var style = document.createElement('style');
      style.setAttribute('data-asym-nb-styles', '');
      style.textContent = [
        'body{padding-top:40px!important}',
        '.monitor-nav{position:sticky!important;top:40px!important}',
        '.monitor-sidebar{top:calc(40px + 52px)!important;height:calc(100vh - 40px - 52px)!important}',
        'nav.sidebar,#sidebar,.sidebar-header{top:40px!important}',
        'nav.sidebar{height:calc(100vh - 40px)!important}',
        '.left-nav{top:40px!important;height:calc(100vh - 40px)!important}',
        '.header:not([data-asym-network-bar]){top:40px!important}',
        'nav:not([data-asym-network-bar]):not(.monitor-nav){top:40px!important}',
        '.nb-links{display:flex}',
        '@media(max-width:640px){.nb-links{display:none}}'
      ].join('');
      document.head.appendChild(style);
    }

    var nav = document.createElement('nav');
    nav.setAttribute('data-asym-network-bar', '');
    nav.setAttribute('aria-label', 'Asymmetric Intelligence network');
    nav.style.cssText = [
      'height:40px','position:fixed','top:0','left:0','right:0',
      'z-index:9999','background:#1a1918','border-bottom:1px solid #2d2c2a',
      "font-family:'Satoshi','Inter',sans-serif",'font-size:13px',
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
        '<a href="https://compossible.asym-intel.info" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">Compossible</a>',
        '<a href="https://whitespace.asym-intel.info" style="color:#a8a7a4;text-decoration:none;transition:color 0.15s">The White Space</a>',
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
  var MONITOR_REGISTRY = {
    'fimi-cognitive-warfare': {
      abbr:   'FCW',
      name:   'FIMI & Cognitive Warfare Monitor',
      accent: '#38bdf8',
      svg:    '<circle cx="18" cy="18" r="14" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none"/><circle cx="18" cy="18" r="9" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.6"/><circle cx="18" cy="18" r="4" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.35"/><line x1="18" y1="4" x2="18" y2="32" stroke="var(--monitor-accent)" stroke-width="0.75" opacity="0.4"/><line x1="4" y1="18" x2="32" y2="18" stroke="var(--monitor-accent)" stroke-width="0.75" opacity="0.4"/><circle cx="18" cy="18" r="2" fill="#dc2626"/><circle cx="26" cy="10" r="1.5" fill="#dc2626" opacity="0.8"/><circle cx="10" cy="24" r="1" fill="var(--monitor-accent)" opacity="0.9"/>',
      vb:     '0 0 36 36',
    },
    'democratic-integrity': {
      abbr:   'WDM',
      name:   'World Democracy Monitor',
      accent: '#61a5d2',
      svg:    '<circle cx="16" cy="16" r="13" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none"/><ellipse cx="16" cy="16" rx="13" ry="5" stroke="var(--monitor-accent)" stroke-width="1" fill="none"/><ellipse cx="16" cy="16" rx="13" ry="9" stroke="var(--monitor-accent)" stroke-width="1" fill="none"/><ellipse cx="16" cy="16" rx="5" ry="13" stroke="var(--monitor-accent)" stroke-width="1" fill="none"/><line x1="3" y1="16" x2="29" y2="16" stroke="var(--monitor-accent)" stroke-width="1"/><line x1="16" y1="3" x2="16" y2="29" stroke="var(--monitor-accent)" stroke-width="1"/>',
      vb:     '0 0 32 32',
    },
    'macro-monitor': {
      abbr:   'GMM',
      name:   'Global Macro Monitor',
      accent: '#22a0aa',
      svg:    '<rect x="2" y="2" width="34" height="34" rx="6" stroke="var(--monitor-accent)" stroke-width="2" fill="none"/><circle cx="12" cy="10" r="2.5" fill="#e87040"/><line x1="12" y1="12.5" x2="12" y2="18" stroke="#e87040" stroke-width="1.5"/><line x1="8" y1="15" x2="16" y2="15" stroke="#e87040" stroke-width="1.5"/><line x1="12" y1="18" x2="9" y2="22" stroke="#e87040" stroke-width="1.5"/><line x1="12" y1="18" x2="15" y2="22" stroke="#e87040" stroke-width="1.5"/><polyline points="5,30 10,30 13,24 17,33 21,26 25,33 29,22 33,30" stroke="#e87040" stroke-width="2" fill="none" stroke-linejoin="round"/>',
      vb:     '0 0 38 38',
    },
    'european-strategic-autonomy': {
      abbr:   'ESA',
      name:   'European Strategic Autonomy Monitor',
      accent: '#5b8db0',
      svg:    '<polygon points="18,2 32,10 32,26 18,34 4,26 4,10" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none"/><polygon points="18,7 27,12 27,24 18,29 9,24 9,12" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.7"/><polygon points="18,11 24,14.5 24,21.5 18,25 12,21.5 12,14.5" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.4"/><line x1="18" y1="2" x2="18" y2="34" stroke="var(--monitor-accent)" stroke-width="0.7" opacity="0.5"/><line x1="4" y1="10" x2="32" y2="26" stroke="var(--monitor-accent)" stroke-width="0.7" opacity="0.5"/><line x1="4" y1="26" x2="32" y2="10" stroke="var(--monitor-accent)" stroke-width="0.7" opacity="0.5"/><circle cx="18" cy="18" r="2.5" fill="var(--monitor-accent)" opacity="0.8"/>',
      vb:     '0 0 36 36',
    },
    'ai-governance': {
      abbr:   'AGM',
      name:   'AI Governance Monitor',
      accent: '#3a7d5a',
      svg:    '<rect x="3" y="3" width="30" height="30" rx="3" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none"/><rect x="8" y="8" width="8" height="8" rx="1" fill="var(--monitor-accent)" opacity="0.9"/><rect x="20" y="8" width="8" height="8" rx="1" fill="var(--monitor-accent)" opacity="0.6"/><rect x="8" y="20" width="8" height="8" rx="1" fill="var(--monitor-accent)" opacity="0.6"/><rect x="20" y="20" width="8" height="8" rx="1" fill="var(--monitor-accent)" opacity="0.3"/><line x1="12" y1="16" x2="12" y2="20" stroke="var(--monitor-accent)" stroke-width="1.5"/><line x1="24" y1="16" x2="24" y2="20" stroke="var(--monitor-accent)" stroke-width="1.5"/><line x1="16" y1="12" x2="20" y2="12" stroke="var(--monitor-accent)" stroke-width="1.5"/>',
      vb:     '0 0 36 36',
    },
    'environmental-risks': {
      abbr:   'ERM',
      name:   'Environmental Risks Monitor',
      accent: '#4caf7d',
      svg:    '<circle cx="18" cy="18" r="14" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none"/><circle cx="18" cy="18" r="9" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.5"/><path d="M18 4 Q22 10 18 18 Q14 26 18 32" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.6"/><path d="M4 18 Q10 14 18 18 Q26 22 32 18" stroke="var(--monitor-accent)" stroke-width="1" fill="none" opacity="0.6"/><circle cx="18" cy="18" r="2.5" fill="var(--monitor-accent)" opacity="0.9"/>',
      vb:     '0 0 36 36',
    },
    'conflict-escalation': {
      abbr:   'SCEM',
      name:   'Strategic Conflict & Escalation Monitor',
      accent: '#dc2626',
      svg:    '<line x1="6" y1="30" x2="30" y2="6" stroke="var(--monitor-accent)" stroke-width="1.8" stroke-linecap="round"/><line x1="6" y1="6" x2="30" y2="30" stroke="var(--monitor-accent)" stroke-width="1.8" stroke-linecap="round"/><circle cx="18" cy="18" r="3" fill="var(--monitor-accent)" opacity="0.9"/><polyline points="22,6 30,6 30,14" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="6,22 6,30 14,30" stroke="var(--monitor-accent)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
      vb:     '0 0 36 36',
    },
  };

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
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="' + m.vb + '" fill="none" aria-hidden="true" style="flex-shrink:0">' +
        m.svg +
      '</svg>' +
      '<span>' + m.name + '</span>';
  }

  /* ── Theme toggle injection ──────────────────────────────────
     Injects the standard theme toggle button into .monitor-nav__actions
     if it is not already present. Idempotent. */
  function injectThemeToggle() {
    var actions = document.querySelector('.monitor-nav__actions');
    if (!actions) return;
    if (actions.querySelector('.theme-toggle')) return; // already present

    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.id = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle theme');
    btn.innerHTML =
      '<svg class="icon-sun" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">' +
        '<circle cx="7.5" cy="7.5" r="3"/>' +
        '<line x1="7.5" y1="1" x2="7.5" y2="2.5"/><line x1="7.5" y1="12.5" x2="7.5" y2="14"/>' +
        '<line x1="1" y1="7.5" x2="2.5" y2="7.5"/><line x1="12.5" y1="7.5" x2="14" y2="7.5"/>' +
      '</svg>' +
      '<svg class="icon-moon" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">' +
        '<path d="M7.5 1a6.5 6.5 0 1 0 6.5 6.5A6.5 6.5 0 0 0 7.5 1zm0 12A5.5 5.5 0 1 1 11.7 3.8 6.5 6.5 0 0 0 7.5 13z"/>' +
      '</svg>';
    actions.insertBefore(btn, actions.firstChild);
  }

  /* ── Footer injection ────────────────────────────────────────
     Normalises .monitor-footer markup to canonical form.
     No-ops if footer absent. */
  function injectMonitorFooter() {
    var footer = document.querySelector('.monitor-footer');
    if (!footer) return;
    var slug = getMonitorSlug();
    var m = slug && MONITOR_REGISTRY[slug];
    if (!m) return;

    footer.innerHTML =
      '<span>' + m.name + ' &middot; <a href="https://asym-intel.info">asym-intel.info</a></span>' +
      '<span class="monitor-footer__credit">' +
        '<a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener">Produced with Perplexity Computer</a>' +
      '</span>';
  }

  var MONITOR_NAV_LINKS = [
    { href: 'overview.html',    label: 'Overview'        },
    { href: 'chatter.html',     label: 'Chatter'         },
    { href: 'dashboard.html',   label: 'Dashboard'       },
    { href: 'report.html',      label: 'Latest Issue'    },
    { href: 'archive.html',     label: 'Archive'         },
    { href: 'persistent.html',  label: 'Living Knowledge'},
    { href: 'search.html',      label: 'Search'          },
    { href: 'about.html',       label: 'About'           },
    { href: 'methodology.html', label: 'Methodology'     },
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
  window.AsymNav = { init: init, injectNetworkBar: injectNetworkBar };
})();

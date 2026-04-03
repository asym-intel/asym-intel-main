/* ============================================================
   Asymmetric Intelligence Monitor — nav.js  v1.2
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
    injectMonitorNav();
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

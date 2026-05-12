/* ============================================================
   Asymmetric Intelligence — sub-nav.js  v1.0
   Shared-layer primitive: monitor sub-navigation (9-item strip).
   Single source of truth: static/monitors/monitor-registry.json
   (inlined at build by tools/inline_registry_into_navjs.py).

   Doctrine bindings:
     P12 — product-not-library: one primitive serves all commons monitors.
     P13 — no-per-page-edits: adding/removing a nav item is a single JSON
            edit; no per-monitor HTML touch.
     P1  — cluster-4: renderer is schema-driven projection.
     P5  — cluster-4: reusable composition primitive.

   Host markup (already standard across all monitor pages):
     <nav class="monitor-nav">
       <a class="monitor-nav__brand"></a>
       <button class="monitor-nav__hamburger">…</button>
       <ul class="monitor-nav__links"></ul>          ← populated here
       <div class="monitor-nav__actions"></div>
     </nav>

   Also supports a generic host element:
     <div data-sub-nav data-monitor="<slug>"></div>

   PI-1 graceful-fallback: if MONITOR_SUB_NAV is missing/empty, the
   element is left untouched (no broken markup emitted).
   ============================================================ */
(function () {
  'use strict';

  /* BEGIN @SUB_NAV_INLINE */
  var MONITOR_SUB_NAV = [
    {"href": "overview.html", "label": "Overview"},
    {"href": "dashboard.html", "label": "Dashboard"},
    {"href": "report.html", "label": "Latest Issue"},
    {"href": "persistent.html", "label": "Living Knowledge"},
    {"href": "chatter.html", "label": "Chatter"},
    {"href": "cross-monitor.html", "label": "Cross-Monitor"},
    {"href": "archive.html", "label": "Archive"},
    {"href": "search.html", "label": "Search"},
    {"href": "about.html", "label": "About"},
  ];
  /* END @SUB_NAV_INLINE */

  /* Validate the inlined registry projection. PI-1: bail silently if
     the array is missing, empty, or malformed — leaving the host element
     empty is preferable to rendering a broken nav. */
  function isValidLinks(items) {
    if (!Array.isArray(items) || items.length === 0) return false;
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      if (!it || typeof it.href !== 'string' || typeof it.label !== 'string') {
        return false;
      }
    }
    return true;
  }

  function renderInto(hostEl, items, currentPage) {
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var link = items[i];
      var isActive = (link.href === currentPage);
      html += '<li><a href="' + link.href + '"' +
        (isActive ? ' class="active"' : '') +
        '>' + link.label + '</a></li>';
    }
    hostEl.innerHTML = html;
  }

  function getCurrentPage() {
    var pathname = window.location.pathname;
    var currentPage = pathname.split('/').pop() || '';
    return currentPage.split('?')[0].split('#')[0];
  }

  function injectSubNav() {
    if (!isValidLinks(MONITOR_SUB_NAV)) return; /* PI-1 fallback */

    var currentPage = getCurrentPage();

    /* Primary host: existing <ul class="monitor-nav__links"> */
    var ul = document.querySelector('.monitor-nav__links');
    if (ul) {
      renderInto(ul, MONITOR_SUB_NAV, currentPage);

      /* Re-wire hamburger close-on-click for the freshly-rendered anchors */
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

    /* Generic host: <div data-sub-nav> — render as a <ul> inside */
    document.querySelectorAll('[data-sub-nav]').forEach(function (host) {
      var existingUl = host.querySelector('ul');
      if (!existingUl) {
        existingUl = document.createElement('ul');
        existingUl.className = 'sub-nav__links';
        host.appendChild(existingUl);
      }
      renderInto(existingUl, MONITOR_SUB_NAV, currentPage);
    });
  }

  /* Expose for nav.js delegation / tests */
  window.AsymSubNav = {
    init: injectSubNav,
    items: function () { return MONITOR_SUB_NAV.slice(); }
  };

  /* Self-init when DOM is ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectSubNav);
  } else {
    injectSubNav();
  }
})();

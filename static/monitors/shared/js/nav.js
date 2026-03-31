/* ============================================================
   Asymmetric Intelligence Monitor — nav.js
   Intersection Observer scroll-spy for .module-section[id]
   Updates active state on .monitor-nav a, .monitor-sidebar a,
   and .module-nav-strip a matching href="#id".
   Mobile: hamburger toggle for sidebar.
   Exposes window.AsymNav.init()
   ============================================================ */
(function () {
  'use strict';

  function init() {
    setupScrollSpy();
    setupHamburger();
    setupSidebarOverlay();
    setupCmsExpanders();
    setupVersionToggles();
    setupTabPanels();
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

    // Add a sidebar toggle button if it isn't already the hamburger
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

    // Close sidebar when a section link is clicked
    sidebar.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', closeSidebar);
    });

    // Close on outside click
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
          // Deactivate all in group
          buttons.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          // Find panels — look for parent and then sibling .tab-panels
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
  window.AsymNav = { init: init };
})();

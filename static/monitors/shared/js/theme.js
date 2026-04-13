/* ============================================================
   Asymmetric Intelligence Monitor — theme.js
   Detects system preference, stores in localStorage as
   'asym-monitor-theme', applies on load (no flash).
   Exposes window.AsymTheme.toggle()
   ============================================================ */
(function () {
  'use strict';

  var STORAGE_KEY = 'asym-monitor-theme';
  var html = document.documentElement;

  function getInitialTheme() {
    var stored = null;
    try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (stored === 'dark' || stored === 'light') return stored;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  var current = getInitialTheme();
  html.setAttribute('data-theme', current);

  function applyTheme(theme) {
    current = theme;
    html.setAttribute('data-theme', theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
    // Update toggle button icons if present
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
    // Dispatch event for any listeners
    if (window.dispatchEvent) {
      window.dispatchEvent(new CustomEvent('asym-theme-change', { detail: { theme: theme } }));
    }
  }

  function toggle() {
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  function setTheme(theme) {
    if (theme === 'dark' || theme === 'light') applyTheme(theme);
  }

  // Wire up button after DOM ready
  function wireButton() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    if (btn._asymWired) return; // guard: only wire once
    btn._asymWired = true;

    // Inject sun/moon SVG icons if not already present
    if (!btn.innerHTML.trim()) {
      btn.innerHTML =
        '<svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
          '<circle cx="12" cy="12" r="5"/>' +
          '<line x1="12" y1="1" x2="12" y2="3"/>' +
          '<line x1="12" y1="21" x2="12" y2="23"/>' +
          '<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>' +
          '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>' +
          '<line x1="1" y1="12" x2="3" y2="12"/>' +
          '<line x1="21" y1="12" x2="23" y2="12"/>' +
          '<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>' +
          '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>' +
        '</svg>' +
        '<svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
          '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>' +
        '</svg>';
    }
    btn.setAttribute('aria-label', current === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    btn.addEventListener('click', toggle);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireButton);
  } else {
    wireButton();
  }

  // Public API
  window.AsymTheme = {
    toggle: toggle,
    set: setTheme,
    current: function () { return current; },
    _wire: wireButton  // exposed so nav.js can re-trigger after injecting the button
  };
})();

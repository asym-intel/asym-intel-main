/* theme.js — Light/Dark mode toggle (in-memory only, no localStorage) */
(function () {
  const html = document.documentElement;
  // Detect system preference
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  let current = prefersDark ? 'dark' : 'light';
  html.setAttribute('data-theme', current);

  function toggle() {
    current = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', current);
  }

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggle);
  });
})();

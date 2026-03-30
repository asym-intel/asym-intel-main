/* nav.js — Sticky nav active-section tracking */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const sections = document.querySelectorAll('.module-section[id]');
    const navLinks = document.querySelectorAll('.module-nav-strip a, .sidebar-nav a');

    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(function (link) {
            const href = link.getAttribute('href');
            if (href === '#' + id) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });

    sections.forEach(function (s) { observer.observe(s); });
  });
})();

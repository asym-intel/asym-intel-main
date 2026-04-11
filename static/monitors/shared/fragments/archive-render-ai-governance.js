document.addEventListener('DOMContentLoaded', function () {
  function esc(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  fetch('data/archive.json')
    .then(function (r) { return r.json(); })
    .then(function (issues) {
      issues = Array.isArray(issues) ? issues : [];
      var sorted = issues.slice().sort(function (a, b) { return b.issue - a.issue; });

      var container = document.getElementById('archive-list');
      var countEl = document.getElementById('archive-count');
      var sidebar = document.getElementById('sidebar-links');

      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      if (!sorted.length) {
        container.innerHTML = '<p class="empty-state">No issues yet.</p>';
        return;
      }

      container.innerHTML = '<div class="archive-grid">' + sorted.map(function (iss) {
        var deltaItems = Array.isArray(iss.delta_strip) ? iss.delta_strip : [];
        return '<article class="archive-card" id="issue-' + iss.issue + '">' +
          '<div class="archive-card__issue">Issue ' + esc(iss.issue) + '</div>' +
          '<div class="archive-card__week">' + esc(iss.week_label) + '</div>' +
          '<div class="archive-card__date">Published ' + esc(iss.published) + '</div>' +
          (iss.signal ? '<p class="archive-card__signal">' + esc(iss.signal.slice(0, 220)) + (iss.signal.length > 220 ? '…' : '') + '</p>' : '') +
          (deltaItems.length ? '<div class="archive-card__deltas"><div class="archive-card__deltas-label">Top signals this issue</div><ul>' +
            deltaItems.slice(0, 3).map(function (d) {
              return '<li class="archive-card__delta-item"><span class="tag">' + esc(d.module) + '</span> ' + esc(d.title) + '</li>';
            }).join('') +
            '</ul></div>' : '') +
          '<div class="archive-card__actions">' +
            '<a class="btn-accent" href="report.html">View Latest →</a>' +
            (iss.source_url ? '<a class="btn-secondary" href="' + esc(iss.source_url) + '" target="_blank" rel="noopener">Source →</a>' : '') +
          '</div>' +
          '</article>';
      }).join('') + '</div>';

      if (sidebar) {
        sidebar.innerHTML = '<li><a href="#section-archive">All Issues</a></li>' +
          sorted.map(function (iss) {
            return '<li><a href="#issue-' + iss.issue + '">Issue ' + esc(iss.issue) + ' · ' + esc(iss.published) + '</a></li>';
          }).join('');
      }
    })
    .catch(function () {
      document.getElementById('archive-list').innerHTML = '<p class="error-state">Could not load archive.</p>';
    });
});
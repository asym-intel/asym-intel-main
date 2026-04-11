document.addEventListener('DOMContentLoaded', function () {
  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  fetch('data/archive.json')
    .then(function (r) { return r.json(); })
    .then(function (issues) {
      var list = document.getElementById('archive-list');
      var sidebar = document.getElementById('sidebar-links');
      var countEl = document.getElementById('archive-count');

      if (!issues || !issues.length) {
        if (countEl) countEl.textContent = '0 issues';
        list.innerHTML = '<p class="text-muted">No archived issues yet.</p>';
        return;
      }

      var sorted = issues.slice().reverse();
      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      var html = '';
      var sidebarHtml = '<li><a href="#section-archive">All Issues</a></li>';

      sorted.forEach(function (issue) {
        var pub = issue.published
          ? new Date(issue.published).toLocaleDateString('en-GB', {day:'numeric', month:'long', year:'numeric'})
          : '';
        var anchor = 'issue-' + (issue.issue || issue.slug || '');
        var deltas = (issue.delta_strip || []).slice(0, 5);

        var deltaHtml = deltas.map(function (d) {
          return '<div class="delta-item" style="margin-bottom:var(--space-2)">' +
            '<div class="delta-item__rank">' + (d.rank || '') + '</div>' +
            '<div class="delta-item__body">' +
              '<div class="delta-item__module">' + escHtml(d.module_tag || '') + ' · ' + escHtml(d.delta_type || '') + '</div>' +
              '<div class="delta-item__title">' + escHtml(d.title || '') + '</div>' +
              (d.one_line ? '<div class="delta-item__one-line">' + escHtml(d.one_line) + '</div>' : '') +
            '</div>' +
          '</div>';
        }).join('');

        html +=
          '<div class="archive-entry" id="' + escHtml(anchor) + '" style="scroll-margin-top:calc(var(--network-bar-height,40px) + var(--nav-height,52px) + var(--space-4,16px))">' +
            '<div class="archive-entry__date">' + pub + '</div>' +
            '<div>' +
              '<div class="archive-entry__issue">Issue ' + (issue.issue || '—') + ' · ' + escHtml(issue.week_label || '') + '</div>' +
              '<div class="archive-entry__signal">' + escHtml(issue.signal || '') + '</div>' +
              (deltaHtml ? '<div style="margin-top:var(--space-3)">' + deltaHtml + '</div>' : '') +
              (issue.source_url ? '<div style="margin-top:var(--space-3)"><a class="archive-entry__link source-link" href="' + escHtml(issue.source_url) + '" target="_blank" rel="noopener">Full brief →</a></div>' : '') +
            '</div>' +
          '</div>';

        sidebarHtml += '<li><a href="#' + escHtml(anchor) + '">Issue ' + (issue.issue || '—') + ' · ' + escHtml(issue.week_label || '') + '</a></li>';
      });

      list.innerHTML = html;
      if (sidebar) sidebar.innerHTML = sidebarHtml;
    })
    .catch(function () {
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive data.</div>';
    });
});
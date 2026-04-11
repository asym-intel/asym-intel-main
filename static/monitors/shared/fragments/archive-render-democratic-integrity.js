document.addEventListener('DOMContentLoaded', function () {
  function escHtml(str) {
    return String(str == null ? '' : str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  fetch('data/archive.json')
    .then(function (r) { return r.json(); })
    .then(function (issues) {
      var list = document.getElementById('archive-list');
      var countEl = document.getElementById('archive-count');
      if (!issues || !issues.length) {
        if (countEl) countEl.textContent = '0 issues';
        list.innerHTML = '<p class="text-muted">No issues archived yet.</p>';
        return;
      }

      var sorted = issues.slice().reverse();
      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      var html = '';
      sorted.forEach(function (issue) {
        var pub = issue.published
          ? new Date(issue.published).toLocaleDateString('en-GB', {day:'numeric',month:'long',year:'numeric'})
          : '';
        var deltaItems = (issue.delta_strip || []).slice(0, 3).map(function (d) {
          return '<span class="severity-badge severity-badge--high" style="margin-right:4px">' + escHtml(d.module || d.title || '') + '</span>';
        }).join('');
        html +=
          '<div class="archive-entry">' +
            '<div class="archive-entry__date">' + escHtml(pub) + '</div>' +
            '<div>' +
              '<div class="archive-entry__issue">Issue ' + escHtml(issue.issue || '—') + ' · ' + escHtml(issue.week_label || '') + '</div>' +
              '<div class="archive-entry__signal">' + escHtml(issue.signal || '') + '</div>' +
              (deltaItems ? '<div class="archive-entry__delta">' + deltaItems + '</div>' : '') +
              (issue.source_url
                ? '<a class="archive-entry__link" href="' + escHtml(issue.source_url) + '" target="_blank" rel="noopener">Full brief →</a>'
                : '') +
            '</div>' +
          '</div>';
      });
      list.innerHTML = html;
    })
    .catch(function () {
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive data.</div>';
    });
});
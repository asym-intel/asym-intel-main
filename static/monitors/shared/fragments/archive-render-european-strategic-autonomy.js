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
        list.innerHTML = '<p class="text-muted">No archived issues yet.</p>';
        return;
      }

      var sorted = issues.slice().reverse();
      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      var html = '';
      sorted.forEach(function (issue) {
        var pub = issue.published
          ? new Date(issue.published).toLocaleDateString('en-GB', {day:'numeric', month:'long', year:'numeric'})
          : '';
        var deltas = issue.delta_strip || [];
        html +=
          '<div class="archive-entry">' +
            '<div class="archive-entry__date">' + escHtml(pub) + '</div>' +
            '<div style="flex:1;min-width:0">' +
              '<div class="archive-entry__issue">Issue ' + escHtml(issue.issue || '—') + ' · ' + escHtml(issue.week_label || '') + '</div>' +
              '<div class="archive-entry__signal">' + escHtml(issue.signal || '') + '</div>';
        if (deltas.length) {
          html += '<ul style="margin-top:var(--space-2);padding-left:var(--space-4);font-size:var(--text-xs);color:var(--color-text-muted)">';
          deltas.slice(0, 3).forEach(function (d) {
            html += '<li>' + escHtml(d.title || '') + '</li>';
          });
          html += '</ul>';
        }
        html +=
            '</div>' +
            '<div style="margin-left:var(--space-4);flex-shrink:0">' +
              (issue.source_url
                ? '<a href="' + escHtml(issue.source_url) + '" class="btn btn--outline" style="font-size:var(--text-xs)">View →</a>'
                : '') +
            '</div>' +
          '</div>';
      });
      list.innerHTML = html;
    })
    .catch(function () {
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive.</div>';
    });
});
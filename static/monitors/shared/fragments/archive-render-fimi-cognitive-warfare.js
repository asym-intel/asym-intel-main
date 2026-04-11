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

        // Delta strip entries
        var deltaHtml = '';
        if (Array.isArray(issue.delta_strip) && issue.delta_strip.length) {
          deltaHtml = '<div style="margin-top:var(--space-4)">' +
            '<div style="font-size:var(--text-xs);font-weight:600;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:var(--space-2)">Intelligence Highlights</div>';
          issue.delta_strip.forEach(function(item) {
            deltaHtml +=
              '<div style="display:flex;gap:var(--space-3);padding:var(--space-2) 0;border-bottom:1px solid var(--color-border-subtle)">' +
                '<div style="flex-shrink:0;font-family:var(--font-mono);font-size:var(--text-xs);color:var(--color-text-muted);min-width:1.5rem">' + escHtml(String(item.rank || '')) + '</div>' +
                '<div>' +
                  '<div style="display:flex;gap:var(--space-2);align-items:center;margin-bottom:var(--space-1)">' +
                    (item.module_tag ? '<span style="font-family:var(--font-mono);font-size: var(--text-min);background:var(--monitor-accent-bg);color:var(--monitor-accent);padding:1px 5px;border-radius:3px">' + escHtml(item.module_tag) + '</span>' : '') +
                    (item.delta_type ? '<span style="font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(item.delta_type) + '</span>' : '') +
                  '</div>' +
                  '<div style="font-size:var(--text-sm);font-weight:500;color:var(--color-text-primary)">' + escHtml(item.title || '') + '</div>' +
                  '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-top:var(--space-1)">' + escHtml(item.one_line || '') + '</div>' +
                '</div>' +
              '</div>';
          });
          deltaHtml += '</div>';
        }

        html +=
          '<div class="card" style="margin-bottom:var(--space-6)">' +
            '<div class="card__label">' +
              'Issue ' + escHtml(issue.issue || '—') + ' · ' + escHtml(issue.week_label || '') +
              (pub ? ' <span style="color:var(--color-text-muted);font-weight:400">· ' + pub + '</span>' : '') +
            '</div>' +
            '<div class="card__title">' + escHtml(issue.signal || '') + '</div>' +
            deltaHtml +
            '<div class="card__footer">' +
              (issue.source_url
                ? '<a class="btn btn--outline" href="' + escHtml(issue.source_url) + '" target="_blank" rel="noopener">Full brief →</a>'
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
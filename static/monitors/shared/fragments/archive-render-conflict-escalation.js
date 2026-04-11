document.addEventListener('DOMContentLoaded', function () {
  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  fetch('data/archive.json')
    .then(function (r) { return r.json(); })
    .then(renderArchive)
    .catch(function (e) {
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive: ' + e.message + '</div>';
    });

  function renderArchive(issues) {
    var listEl = document.getElementById('archive-list');
    var sidebar = document.getElementById('sidebar-links');
    var countEl = document.getElementById('archive-count');

    if (!issues || !issues.length) {
      if (countEl) countEl.textContent = '0 issues';
      listEl.innerHTML = '<p class="text-muted">No archived issues yet.</p>';
      return;
    }

    if (countEl) countEl.textContent = issues.length + ' issue' + (issues.length !== 1 ? 's' : '');

    // Group by year
    var byYear = {};
    issues.forEach(function (issue) {
      var year = (issue.published || '').split('-')[0] || '2026';
      if (!byYear[year]) byYear[year] = [];
      byYear[year].push(issue);
    });

    // Update sidebar and sections
    var sidebarHtml = '<li><a href="#section-archive">All Issues</a></li>';
    var allHtml = '';

    Object.keys(byYear).sort().reverse().forEach(function (year) {
      var yearIssues = byYear[year].slice().reverse();
      sidebarHtml += '<li><a href="#section-archive-' + year + '">' + year + '</a></li>';
      yearIssues.forEach(function (issue) {
        sidebarHtml += '<li style="padding-left:var(--space-2)"><a href="#section-archive-' + year + '" style="font-size:var(--text-sm)">Issue ' + (issue.issue||'—') + '</a></li>';
      });

      var issuesHtml = yearIssues.map(function (issue) {
        var pub = issue.published ? new Date(issue.published).toLocaleDateString('en-GB', {day:'numeric', month:'long', year:'numeric'}) : '';
        var deltaHtml = (issue.delta_strip||[]).slice(0,5).map(function (d) {
          return '<div style="font-size:var(--text-sm);color:var(--color-text-secondary);padding:var(--space-1) 0;border-bottom:1px solid var(--color-border-subtle)">' +
            '<strong style="color:var(--monitor-accent)">#' + d.rank + ' ' + escHtml(d.module_tag||'') + '</strong> — ' + escHtml(d.title||'') +
            '<br><span style="color:var(--color-text-muted)">' + escHtml(d.one_line||'') + '</span>' +
          '</div>';
        }).join('');

        return '<div class="archive-entry">' +
          '<div class="archive-entry__date">' + pub + '</div>' +
          '<div>' +
            '<div class="archive-entry__issue">Issue ' + (issue.issue||'—') + ' · ' + escHtml(issue.week_label||'') + '</div>' +
            '<div class="archive-entry__signal">' + escHtml(issue.signal||'') + '</div>' +
            (deltaHtml ? '<div class="archive-entry__delta">' + deltaHtml + '</div>' : '') +
            (issue.source_url ? '<a class="archive-entry__link" href="' + escHtml(issue.source_url) + '" target="_blank" rel="noopener">Full brief →</a>' : '') +
          '</div>' +
        '</div>';
      }).join('');

      allHtml += '<div class="module-section" id="section-archive-' + year + '">' +
        '<div class="module-header"><div class="module-title">' + year + '</div></div>' +
        '<div>' + issuesHtml + '</div>' +
      '</div>';
    });

    if (sidebar) sidebar.innerHTML = sidebarHtml;
    listEl.innerHTML = allHtml;
  }
});
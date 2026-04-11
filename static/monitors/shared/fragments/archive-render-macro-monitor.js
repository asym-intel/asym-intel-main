document.addEventListener('DOMContentLoaded', function () {

  function esc(str) {
    return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function fmtDate(str) {
    if (!str) return '';
    try { return new Date(str).toLocaleDateString('en-GB', {day:'numeric', month:'long', year:'numeric'}); }
    catch(e) { return str; }
  }

  fetch('data/archive.json')
    .then(function (r) { return r.json(); })
    .then(function (issues) {
      var countEl = document.getElementById('archive-count');
      var listEl  = document.getElementById('archive-list');

      if (!issues || !issues.length) {
        if (countEl) countEl.textContent = '0 issues';
        listEl.innerHTML = '<p class="text-muted text-sm">No archived issues yet.</p>';
        return;
      }

      // Sort newest first
      var sorted = issues.slice().sort(function(a,b){
        return new Date(b.published||b.date||0) - new Date(a.published||a.date||0);
      });

      if (countEl) countEl.textContent = sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '');

      var html = '';
      sorted.forEach(function (issue) {
        var pub = fmtDate(issue.published || issue.date || '');
        var stress = issue.system_stress_label || issue.signal || '';
        var regime = issue.regime || '';
        var delta  = issue.delta_strip || [];

        html += '<div class="card" style="margin-bottom:var(--space-6)">' +
          '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:var(--space-4);flex-wrap:wrap;margin-bottom:var(--space-3)">' +
            '<div>' +
              '<div class="card__label">Issue ' + esc(issue.issue||'—') + ' · Vol ' + esc(issue.volume||'—') + ' · ' + esc(pub) + '</div>' +
              '<div class="card__title" style="margin-top:var(--space-1)">' + esc(issue.week_label || '') + '</div>' +
            '</div>' +
            '<div style="display:flex;gap:var(--space-2);flex-wrap:wrap">' +
              (stress ? '<span class="flag-badge flag-badge--elevated">' + esc(stress) + '</span>' : '') +
              (regime ? '<span class="regime-badge" style="font-size: var(--text-min)">' + esc(regime) + '</span>' : '') +
            '</div>' +
          '</div>' +
          (issue.signal ? '<p style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.6;margin-bottom:var(--space-3)">' + esc(issue.signal) + '</p>' : '') +
          (delta.length ? renderDeltaChips(delta) : '') +
          '<div style="margin-top:var(--space-4);display:flex;gap:var(--space-3)">' +
            (issue.source_url ? '<a class="btn btn--primary" href="' + esc(issue.source_url) + '" target="_blank" rel="noopener">Full Brief →</a>' : '') +
          '</div>' +
        '</div>';
      });

      listEl.innerHTML = html;
    })
    .catch(function () {
      document.getElementById('archive-list').innerHTML = '<div class="error-state">Failed to load archive data.</div>';
      var countEl = document.getElementById('archive-count');
      if (countEl) countEl.textContent = 'Error';
    });

  function renderDeltaChips(delta) {
    var chips = delta.slice(0, 5).map(function (d) {
      return '<span class="badge badge--accent" style="margin-right:4px">' + esc(d.delta_type || d.module_tag || '') + '</span>' +
        '<span style="font-size:var(--text-xs);color:var(--color-text-muted);margin-right:var(--space-3)">' + esc(d.title || '') + '</span>';
    }).join('');
    return '<div style="font-size:var(--text-xs);color:var(--color-text-faint);line-height:1.8">' + chips + '</div>';
  }
});
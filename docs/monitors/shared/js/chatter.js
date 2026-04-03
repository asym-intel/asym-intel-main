/* ============================================================
   chatter.js  v1.0  — Asymmetric Intelligence shared module
   Renders chatter-latest.json for any monitor chatter page.
   Derives monitor slug from URL path — no per-page config needed.
   Requires: nav.js loaded first (for MONITOR_REGISTRY + --monitor-accent)
   ============================================================ */
(function () {
  /* Derive monitor slug from URL: /monitors/{slug}/chatter.html */
  var slug = (function () {
    var parts = window.location.pathname.split('/');
    var idx = parts.indexOf('monitors');
    return (idx !== -1 && parts[idx + 1]) ? parts[idx + 1] : null;
  })();

  var BASE = '/monitors/' + (slug || '') + '/data/';

  /* Inject page header from MONITOR_REGISTRY (set by nav.js v1.3+) */
  function injectHeader() {
    if (!slug) return;
    var reg = window.AsymNav && window.AsymNav.MONITOR_REGISTRY;
    if (!reg || !reg[slug]) return;
    var m = reg[slug];
    var eyebrow = document.getElementById('chatter-eyebrow');
    var title   = document.getElementById('chatter-title');
    if (eyebrow) eyebrow.textContent = m.abbr + ' CHATTER';
    if (title)   title.textContent   = m.name + ' — Chatter';
  }

(function() {

  function escHtml(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function tierBadge(tier) {
    var label = 'T' + tier;
    var colours = {1:'#059669', 2:'#2563eb', 3:'#d97706', 4:'#94a3b8'};
    var bg = colours[tier] || '#94a3b8';
    return '<span style="font-size:var(--text-xs);font-family:var(--font-mono);background:' + bg + ';color:#fff;padding:1px 5px;border-radius:3px;margin-right:4px">' + label + '</span>';
  }

  function formatTime(iso) {
    if (!iso) return '';
    try {
      var d = new Date(iso);
      return d.toLocaleTimeString('en-GB', {hour:'2-digit', minute:'2-digit'}) + ' UTC';
    } catch(e) { return iso; }
  }

  fetch(BASE + 'chatter-latest.json')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var meta  = data._meta || {};
      var items = data.items || [];

      // Update meta
      var metaEl = document.getElementById('chatter-meta');
      if (metaEl) {
        metaEl.innerHTML =
          'W/E ' + escHtml(meta.data_date || '') +
          ' &nbsp;·&nbsp; Updated ' + formatTime(meta.generated_at) +
          ' &nbsp;·&nbsp; ' + items.length + ' items' +
          ' &nbsp;·&nbsp; <em style="color:var(--text-muted)">' + escHtml(meta.coverage_note || '') + '</em>';
      }

      // Render items
      var listEl = document.getElementById('chatter-list');
      if (!listEl) return;

      if (!items.length) {
        listEl.innerHTML = '<p class="text-muted text-sm" style="padding:var(--space-6) 0">No chatter items for today yet. Check back after 08:00 UTC.</p>';
        return;
      }

      var html = '<ol style="list-style:none;padding:0;margin:0">';
      items.forEach(function(item, idx) {
        var tags = '';
        if (item.cross_monitor_tag && item.cross_monitor_tag.length) {
          item.cross_monitor_tag.forEach(function(t) {
            tags += '<span style="font-size:var(--text-xs);background:var(--surface-2);color:var(--text-muted);padding:1px 6px;border-radius:3px;margin-right:3px">' + escHtml(t.toUpperCase()) + '</span>';
          });
        }
        if (item.is_episodic) {
          tags += '<span style="font-size:var(--text-xs);background:var(--surface-2);color:var(--text-muted);padding:1px 6px;border-radius:3px;font-style:italic">Episodic</span>';
        }

        html += '<li style="padding:var(--space-4) 0;border-bottom:1px solid var(--border)">';
        html += '<div style="display:flex;align-items:flex-start;gap:var(--space-3)">';
        html += '<span style="font-size:var(--text-xs);font-family:var(--font-mono);color:var(--text-muted);min-width:20px;padding-top:2px">' + (idx+1) + '</span>';
        html += '<div style="flex:1;min-width:0">';

        // Title linked
        html += '<div style="margin-bottom:var(--space-1)">';
        html += tierBadge(item.source_tier || 3);
        if (tags) html += '<span style="display:inline">' + tags + '</span>';
        html += '</div>';
        html += '<a href="' + escHtml(item.source_url || '#') + '" target="_blank" rel="noopener" ' +
          'style="font-weight:600;color:var(--text-heading);text-decoration:none;line-height:1.3;display:block;margin-bottom:var(--space-1)" ' +
          'onmouseover="this.style.color=\'color-mix(in srgb,var(--monitor-accent) 65%,#000)\'" ' +
          'onmouseout="this.style.color=\'var(--text-heading)\'">' +
          escHtml(item.title) + '</a>';

        // Source + relevance
        html += '<div style="font-size:var(--text-xs);color:var(--text-muted);margin-bottom:var(--space-2)">';
        html += escHtml(item.source_name || '');
        if (item.domain_relevance) {
          html += ' &nbsp;·&nbsp; <span style="color:color-mix(in srgb,var(--monitor-accent) 65%,#000)">' + escHtml(item.domain_relevance) + '</span>';
        }
        html += '</div>';

        // Summary
        html += '<p style="font-size:var(--text-sm);color:var(--text-body);margin:0">' + escHtml(item.summary || '') + '</p>';

        html += '</div></div></li>';
      });
      html += '</ol>';
      listEl.innerHTML = html;
    })
    .catch(function() {
      var metaEl = document.getElementById('chatter-meta');
      if (metaEl) metaEl.innerHTML = 'Not yet available';
      document.getElementById('chatter-list').innerHTML =
        '<p class="text-muted text-sm" style="padding:var(--space-6) 0">Chatter data not yet available. First run after 06:00 UTC.</p>';
    });
})();

  /* Run header injection on DOM ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectHeader);
  } else {
    injectHeader();
  }
})();

/* ============================================================
   search.js  v1.0  — Asymmetric Intelligence shared module
   Full-text search across all published issues of any monitor.
   Derives data path from window.location — no per-page config needed.
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
    var corpus = [];
    var loaded = false;

    function esc(s) {
      return String(s||'')        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    function highlight(text, q) {
      var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&') + ')', 'gi');
      return esc(text).replace(re, '<mark>$1</mark>');
    }

    function flatten(obj, issue, items) {
      if (!obj || typeof obj !== 'object') return;
      if (Array.isArray(obj)) { obj.forEach(function(i){ flatten(i, issue, items); }); return; }
      var text = '';
      ['title','headline','summary','body','detail','note','signal','significance','description'].forEach(function(k){
        if (obj[k] && typeof obj[k] === 'string') text += ' ' + obj[k];
      });
      if (text.trim()) items.push({ text: text.trim(), issue: issue });
      Object.keys(obj).forEach(function(k){
        if (typeof obj[k] === 'object') flatten(obj[k], issue, items);
      });
    }

    function doSearch(q) {
      var statusEl  = document.getElementById('search-status');
      var resultsEl = document.getElementById('search-results');
      q = q.trim();
      if (!q) { resultsEl.innerHTML = ''; statusEl.textContent = ''; return; }
      if (!loaded) { statusEl.textContent = 'Loading corpus…'; return; }
      var lower = q.toLowerCase();
      var matches = corpus.filter(function(item){
        return item.text.toLowerCase().indexOf(lower) > -1;
      });
      // Deduplicate
      var seen = {}, deduped = [];
      matches.forEach(function(m){
        var k = m.issue + '|' + m.text.slice(0,80);
        if (!seen[k]) { seen[k] = true; deduped.push(m); }
      });
      statusEl.textContent = deduped.length
        ? deduped.length + ' result' + (deduped.length !== 1 ? 's' : '') + ' for "' + q + '"'
        : 'No results for "' + q + '"';
      if (!deduped.length) {
        resultsEl.innerHTML = '<p style="color:var(--color-text-muted);padding:var(--space-6) 0;font-size:var(--text-sm)">No results found. Try a different term.</p>';
        return;
      }
      resultsEl.innerHTML = deduped.slice(0,40).map(function(item){
        var preview = item.text.length > 200 ? item.text.slice(0,200) + '…' : item.text;
        return '<div class="search-result">' +
          '<div class="search-result__meta">Issue ' + esc(item.issue) + '</div>' +
          '<div class="search-result__body">' + highlight(preview, q) + '</div>' +
          '<a class="search-result__link" href="report.html">View issue →</a>' +
        '</div>';
      }).join('');
    }

    // Load corpus from archive.json then each report
    fetch('data/archive.json')
      .then(function(r){ return r.json(); })
      .then(function(issues){
        issues = Array.isArray(issues) ? issues : (issues.issues || []);
        statusEl_temp = document.getElementById('search-status');
        if (statusEl_temp) statusEl_temp.textContent = issues.length + ' issue' + (issues.length !== 1 ? 's' : '') + ' indexed.';
        var promises = issues.map(function(issue){
          var url = issue.url || ('data/report-' + (issue.slug || issue.published) + '.json');
          return fetch(url).then(function(r){ return r.json(); })
            .then(function(d){ flatten(d, issue.slug || issue.published || '?', corpus); })
            .catch(function(){});
        });
        return Promise.all(promises);
      })
      .then(function(){
        loaded = true;
        var statusEl = document.getElementById('search-status');
        if (statusEl) statusEl.textContent = corpus.length + ' searchable items loaded across all issues.';
      })
      .catch(function(){ 
        document.getElementById('search-status').textContent = 'Failed to load search index.';
      });

    var input = document.getElementById('search-input');
    var timer;
    input.addEventListener('input', function(){
      clearTimeout(timer);
      timer = setTimeout(function(){ doSearch(input.value); }, 200);
    });
    input.focus();
  });
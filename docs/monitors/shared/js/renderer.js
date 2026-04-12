/* ============================================================
   Asymmetric Intelligence Monitor — renderer.js
   Generic JSON → HTML renderer for all monitors.
   Exposes window.AsymRenderer.init(dataPath)
           window.AsymRenderer.register(key, fn)
   ============================================================ */
(function () {
  'use strict';

  /* Keys excluded from generic module rendering */
  var EXCLUDED_KEYS = ['meta', 'signal', 'delta_strip', 'cross_monitor_flags', 'source_url'];

  /* Custom renderer registry: key → function(data) → htmlString */
  var customRenderers = {};

  /* Human-readable module names */
  var MODULE_LABELS = {
    heatmap: 'Country Heatmap',
    intelligence_items: 'Intelligence Items',
    institutional_integrity_flags: 'Institutional Integrity Flags',
    regional_mimicry_chains: 'Mimicry Chains'
  };

  /* ── Utility ── */
  function esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function humanLabel(key) {
    if (MODULE_LABELS[key]) return MODULE_LABELS[key];
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function formatDate(str) {
    if (!str) return '';
    try {
      var d = new Date(str);
      if (isNaN(d.getTime())) return str;
      return d.toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) { return str; }
  }

  function severityClass(score) {
    if (score == null) return '';
    var s = parseFloat(score);
    if (s >= 8) return 'critical';
    if (s >= 6) return 'high';
    if (s >= 4) return 'moderate';
    return 'positive';
  }

  /* ── Meta Header ── */
  function renderMeta(meta) {
    if (!meta) return '';
    return '<div class="page-header">' +
      '<div class="page-header__eyebrow">Issue ' + esc(meta.issue) + ' · ' + esc(meta.week_label) + '</div>' +
      '<h1 class="page-header__title">World Democracy Monitor</h1>' +
      '<div class="page-header__meta">' +
        (meta.published ? '<span>Published ' + formatDate(meta.published) + '</span>' : '') +
        (meta.editor ? '<span>Editor: ' + esc(meta.editor) + '</span>' : '') +
        (meta.schema_version ? '<span>Schema v' + esc(meta.schema_version) + '</span>' : '') +
      '</div>' +
    '</div>';
  }

  /* ── Signal Block ── */
  function renderSignal(signal) {
    if (!signal) return '';
    return '<div class="signal-block">' +
      '<div class="signal-block__label">Lead Signal — M00</div>' +
      '<p>' + esc(signal) + '</p>' +
    '</div>';
  }

  /* ── Delta Strip ── */
  function renderDeltaStrip(items) {
    if (!items || !items.length) return '';
    var html = '<div class="section-label">Top Changes This Week</div>' +
      '<ul class="delta-strip">';
    items.forEach(function (item) {
      html += '<li class="delta-item">' +
        '<div class="delta-item__rank">' + esc(item.rank || '') + '</div>' +
        '<div class="delta-item__body">' +
          (item.module ? '<div class="delta-item__module">' + esc(item.module) + '</div>' : '') +
          (item.title ? '<div class="delta-item__title">' + esc(item.title) + '</div>' : '') +
          (item.one_line ? '<div class="delta-item__one-line">' + esc(item.one_line) + '</div>' : '') +
        '</div>' +
        (item.delta_type ? '<div class="delta-item__type"><span class="badge">' + esc(item.delta_type) + '</span></div>' : '') +
      '</li>';
    });
    html += '</ul>';
    return html;
  }

  /* ── Generic card for a single object ── */
  function renderObjectCard(obj) {
    var html = '<div class="card">';
    var usedAsTitle = false;

    // Title-like fields first
    ['headline', 'title', 'country', 'name', 'flag_type', 'chain_id'].forEach(function (f) {
      if (obj[f] != null) {
        html += '<div class="card__title">' + esc(obj[f]) + '</div>';
        usedAsTitle = true;
      }
    });

    // Summary/body
    if (obj.summary) {
      html += '<div class="card__body">' + esc(obj.summary) + '</div>';
    } else if (obj.body) {
      html += '<div class="card__body">' + esc(obj.body) + '</div>';
    }

    // Footer meta — all remaining non-null scalar fields
    var footerParts = [];
    var skip = new Set(['headline', 'title', 'country', 'name', 'flag_type', 'chain_id',
                        'summary', 'body', 'source_url', 'chain', 'links', 'version_history',
                        'triggers', 'flags']);
    Object.keys(obj).forEach(function (k) {
      if (skip.has(k)) return;
      var v = obj[k];
      if (v == null || v === '') return;
      if (typeof v === 'object') return; // skip nested objects/arrays in footer
      footerParts.push('<span><strong>' + esc(humanLabel(k)) + ':</strong> ' + esc(String(v)) + '</span>');
    });

    if (footerParts.length) {
      html += '<div class="card__footer">' + footerParts.join('') + '</div>';
    }

    if (obj.source_url) {
      html += ' <a class="source-link" href="' + esc(obj.source_url) + '" target="_blank" rel="noopener">Source →</a>';
    }

    html += '</div>';
    return html;
  }

  /* ── Generic array section ── */
  function renderArraySection(key, items, sectionIndex) {
    if (!items || !items.length) return '';
    var html = '<section class="module-section" id="module-' + esc(key) + '">' +
      '<div class="module-header">' +
        '<div class="module-num-large">' + String(sectionIndex).padStart(2, '0') + '</div>' +
        '<h2 class="module-title">' + esc(humanLabel(key)) + '</h2>' +
      '</div>';

    items.forEach(function (item) {
      if (typeof item === 'object' && !Array.isArray(item)) {
        html += renderObjectCard(item);
      } else {
        html += '<div class="card"><div class="card__body">' + esc(String(item)) + '</div></div>';
      }
    });

    html += '</section>';
    return html;
  }

  /* ── Generic object section (non-array) ── */
  function renderObjectSection(key, obj, sectionIndex) {
    var html = '<section class="module-section" id="module-' + esc(key) + '">' +
      '<div class="module-header">' +
        '<div class="module-num-large">' + String(sectionIndex).padStart(2, '0') + '</div>' +
        '<h2 class="module-title">' + esc(humanLabel(key)) + '</h2>' +
      '</div>' +
      renderObjectCard(obj) +
    '</section>';
    return html;
  }

  /* ── Cross-monitor flags panel ── */
  function renderCrossMonitorFlags(cmf) {
    if (!cmf || !cmf.flags || !cmf.flags.length) return '';
    var html = '<div class="cross-monitor-panel">' +
      '<div class="cross-monitor-panel__title">Cross-Monitor Flags' +
        (cmf.updated ? ' · Updated ' + formatDate(cmf.updated) : '') +
      '</div>';

    cmf.flags.forEach(function (flag) {
      var statusClass = flag.status === 'Active' ? 'badge--accent' : 'badge';
      html += '<div class="cms-flag">' +
        '<div class="cms-flag__header">' +
          '<span class="cms-flag__id">' + esc(flag.id) + '</span>' +
          '<span class="badge ' + statusClass + '">' + esc(flag.status || '') + '</span>' +
        '</div>' +
        '<div class="cms-flag__title">' + esc(flag.title) + '</div>' +
        (flag.monitors_involved && flag.monitors_involved.length
          ? '<div class="cms-flag__monitors">' + flag.monitors_involved.map(esc).join(' · ') + '</div>'
          : '') +
        (flag.body
          ? '<div class="cms-flag__body cms-flag__body--collapsed">' + esc(flag.body) + '</div>' +
            '<span class="cms-read-more">Read more →</span>'
          : '') +
      '</div>';
    });

    html += '</div>';
    return html;
  }

  /* ── Auto-generate module nav from JSON keys ── */
  function buildModuleNav(data) {
    var keys = Object.keys(data).filter(function (k) {
      return EXCLUDED_KEYS.indexOf(k) === -1 && data[k] != null;
    });
    if (!keys.length) return '';

    var html = '<nav class="module-nav-strip" aria-label="Module navigation">';
    keys.forEach(function (k) {
      html += '<a href="#module-' + esc(k) + '">' + esc(humanLabel(k)) + '</a>';
    });
    html += '</nav>';
    return html;
  }

  /* ── Build sidebar nav from JSON keys ── */
  function buildSidebarNav(data) {
    var keys = Object.keys(data).filter(function (k) {
      return EXCLUDED_KEYS.indexOf(k) === -1 && data[k] != null;
    });
    if (!keys.length) return '';

    var html = '<div class="sidebar-nav__title">Sections</div><ul>';
    keys.forEach(function (k, i) {
      html += '<li><a href="#module-' + esc(k) + '">' +
        '<span class="sidebar-num">' + String(i + 1).padStart(2, '0') + '</span>' +
        esc(humanLabel(k)) +
      '</a></li>';
    });
    html += '</ul>';
    return html;
  }

  /* ── Main render function ── */
  function render(data, container) {
    var html = '';

    // Meta header
    html += renderMeta(data.meta);

    // Module nav strip (auto-generated)
    html += buildModuleNav(data);

    // Signal
    html += renderSignal(data.signal || (data.meta && data.meta.signal));

    // Delta strip
    if (data.delta_strip) {
      html += renderDeltaStrip(data.delta_strip);
    }

    // Source URL (top-level)
    if (data.source_url) {
      html += '<p style="margin-bottom:var(--space-6)">' +
        '<a class="source-link" href="' + esc(data.source_url) + '" target="_blank" rel="noopener">Read full brief on asym-intel.info →</a>' +
      '</p>';
    }

    // All other top-level keys
    var sectionIndex = 1;
    Object.keys(data).forEach(function (key) {
      if (EXCLUDED_KEYS.indexOf(key) !== -1) return;
      var value = data[key];
      if (value == null) return;

      // Use custom renderer if registered
      if (customRenderers[key]) {
        html += '<section class="module-section" id="module-' + esc(key) + '">' +
          '<div class="module-header">' +
            '<div class="module-num-large">' + String(sectionIndex).padStart(2, '0') + '</div>' +
            '<h2 class="module-title">' + esc(humanLabel(key)) + '</h2>' +
          '</div>' +
          customRenderers[key](value) +
        '</section>';
        sectionIndex++;
        return;
      }

      if (Array.isArray(value)) {
        html += renderArraySection(key, value, sectionIndex);
        sectionIndex++;
      } else if (typeof value === 'object') {
        html += renderObjectSection(key, value, sectionIndex);
        sectionIndex++;
      }
      // skip primitives at top level (already handled: signal, source_url)
    });

    // Cross-monitor flags panel
    if (data.cross_monitor_flags) {
      html += renderCrossMonitorFlags(data.cross_monitor_flags);
    }

    container.innerHTML = html;

    // Populate sidebar if present
    var sidebar = document.querySelector('.monitor-sidebar');
    /* populate sidebar if empty or only has a comment */
    var sidebarText = (sidebar.innerHTML || '').replace(/<!--[\s\S]*?-->/g, '').trim();
    if (sidebar && !sidebarText) {
      sidebar.innerHTML = buildSidebarNav(data);
    }

    // Re-init nav after render
    if (window.AsymNav) window.AsymNav.init();
  }

  /* ── Public init ── */
  function init(dataPath) {
    var container = document.getElementById('report-content');
    if (!container) {
      container = document.querySelector('main') || document.body;
    }

    container.innerHTML = '<div class="loading-state">Loading…</div>';

    fetch(dataPath)
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        try {
          render(data, container);
        } catch (renderErr) {
          container.innerHTML = '<div class="error-state">Render error: ' + esc(renderErr.message) + '<br><small>' + esc(renderErr.stack || '') + '</small></div>';
        }
      })
      .catch(function (err) {
        container.innerHTML = '<div class="error-state">Failed to load data: ' + esc(err.message) + '</div>';
      });
  }

  /* ── Register custom renderer ── */
  function register(key, fn) {
    customRenderers[key] = fn;
  }

  // Public API
  window.AsymRenderer = {
    init: init,
    register: register,
    /* stubs — overwritten by real implementations later in this file.
       Ensures callers never hit 'is not a function' if a later IIFE fails. */
    sourceLink:  function () { return ''; },
    sourceLabel: function () { return 'Source'; },
    flag:        function () { return ''; },
    /* exposed for testing */
    _renderMeta: renderMeta,
    _renderSignal: renderSignal,
    _renderDeltaStrip: renderDeltaStrip,
    _renderCrossMonitorFlags: renderCrossMonitorFlags
  };
})();

/* ─── Persistent State Renderer ─────────────────────────────
   window.AsymPersistent — renders persistent-state.json sections
   into container elements. Handles null/missing fields gracefully.
   ─────────────────────────────────────────────────────────── */

window.AsymPersistent = (function () {
  'use strict';

  function escHtml(str) {
    return String(str == null ? '' : str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function severityClass(val) {
    var v = String(val||'').toLowerCase();
    if (v==='transgressed'||v==='critical'||v==='rapid decay'||v==='red'||v==='high') return 'critical';
    if (v==='high risk'||v==='elevated'||v==='amber'||v==='watchlist') return 'high';
    if (v==='increasing risk'||v==='contested'||v==='moderate') return 'moderate';
    if (v==='safe'||v==='green'||v==='recovery'||v==='positive') return 'positive';
    return 'moderate';
  }

  /* Render version history toggle */
  function renderVersionHistory(history) {
    if (!history || !history.length) return '';
    var entries = history.map(function(h) {
      return '<div class="version-entry">' +
        '<div class="version-entry__date">' + escHtml(h.date||'') + '</div>' +
        '<div class="version-entry__change">' + escHtml(h.change||'') + '</div>' +
        (h.reason ? '<div class="version-entry__reason">' + escHtml(h.reason) + '</div>' : '') +
      '</div>';
    }).join('');
    return '<div class="version-history" id="vh-' + Math.random().toString(36).slice(2,7) + '">' + entries + '</div>' +
           '<button class="version-history__toggle" onclick="var vh=this.previousElementSibling;vh.classList.toggle(\'version-history--open\');this.textContent=vh.classList.contains(\'version-history--open\')?\'Hide history ↑\':\'Version history →\'">Version history →</button>';
  }

  /* Generic entity card — works for any persistent entity with standard fields */
  function renderEntityCard(entity, opts) {
    opts = opts || {};
    var statusVal  = entity.status || entity.tier || entity.band || entity.severity || '';
    var scoreVal   = entity.severity_score != null ? entity.severity_score : (entity.score != null ? entity.score : '');
    var trendVal   = entity.trend || entity.severity_arrow || entity.trajectory_arrow || '';
    var nameVal    = entity.country || entity.boundary || entity.conflict || entity.name || entity.chain_id || '';
    var bodyVal    = entity.headline || entity.lead_signal || entity.summary || entity.signal || entity.note || '';
    var metaItems  = [];
    if (entity.theatre)      metaItems.push(escHtml(entity.theatre));
    if (entity.first_seen)   metaItems.push('First seen: ' + escHtml(entity.first_seen));
    if (entity.last_updated) metaItems.push('Updated: ' + escHtml(entity.last_updated));
    if (entity.last_material_change) metaItems.push('Changed: ' + escHtml(entity.last_material_change));

    return '<div class="persistent-entity">' +
      '<div class="persistent-entity__header">' +
        '<div class="persistent-entity__country">' + escHtml(nameVal) + '</div>' +
        '<div class="persistent-entity__badges">' +
          (statusVal ? '<span class="severity-badge severity-badge--' + severityClass(statusVal) + '">' + escHtml(statusVal) + '</span>' : '') +
          (scoreVal !== '' ? '<span class="severity-badge severity-badge--' + severityClass(statusVal) + '">' + escHtml(scoreVal) + (trendVal ? ' ' + escHtml(trendVal) : '') + '</span>' : '') +
        '</div>' +
      '</div>' +
      (metaItems.length ? '<div class="persistent-entity__meta">' + metaItems.join(' · ') + '</div>' : '') +
      (bodyVal ? '<div class="card__body" style="margin-top:var(--space-3)">' + escHtml(bodyVal) + '</div>' : '') +
      renderVersionHistory(entity.version_history || []) +
    '</div>';
  }

  /* Render a cross_monitor_flags block */
  function renderCrossMonitorFlags(cmf, containerId) {
    var el = document.getElementById(containerId);
    if (!el) return;
    var flags = [];
    if (cmf && Array.isArray(cmf.flags)) flags = cmf.flags;
    else if (cmf && typeof cmf === 'object') flags = Object.values(cmf).filter(Array.isArray).flat();

    var active = flags.filter(function(f){ return (f.status||'').toLowerCase() !== 'resolved'; });
    if (!active.length) {
      el.innerHTML = '<p class="text-muted text-sm">Cross-monitor flags are written by the weekly cron task and accumulate here across issues. Flags will appear after the next publish cycle.</p>';
      return;
    }
    el.innerHTML = active.map(function(f) {
      return '<div class="cms-flag">' +
        '<div class="cms-flag__header">' +
          '<div><div class="cms-flag__id">' + escHtml(f.id||'') + '</div>' +
          '<div class="cms-flag__title">' + escHtml(f.title||'') + '</div></div>' +
          '<span class="severity-badge severity-badge--moderate">' + escHtml(f.status||'Active') + '</span>' +
        '</div>' +
        (f.monitors_involved&&f.monitors_involved.length ? '<div class="cms-flag__monitors">↔ ' + f.monitors_involved.map(escHtml).join(' · ') + '</div>' : '') +
        '<div class="cms-flag__body cms-flag__body--collapsed">' + escHtml(f.linkage||f.title||'') + '</div>' +
        '<span class="cms-read-more" onclick="var b=this.previousElementSibling;b.classList.toggle(\'cms-flag__body--collapsed\');this.textContent=b.classList.contains(\'cms-flag__body--collapsed\')?\'Read more →\':\'Show less ↑\'">Read more →</span>' +
      '</div>';
    }).join('');
  }

  /* Render an array of entities into a container */
  function renderEntityList(items, containerId, opts) {
    var el = document.getElementById(containerId);
    if (!el) return;
    if (!items || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">No entries recorded yet.</p>';
      return;
    }
    // Flatten if items is an object (dict of arrays)
    var list = Array.isArray(items) ? items : Object.values(items).flat();
    el.innerHTML = list.map(function(item) { return renderEntityCard(item, opts); }).join('');
  }

  return {
    renderEntityCard: renderEntityCard,
    renderEntityList: renderEntityList,
    renderCrossMonitorFlags: renderCrossMonitorFlags,
    renderVersionHistory: renderVersionHistory,
    severityClass: severityClass,
    escHtml: escHtml
  };
}());

/* ─── Cross-Monitor Section Renderers ────────────────────────────
   window.AsymSections — reusable render functions for new data
   sections produced by schema enrichment sprints.

   Every function takes (data, targetId) and renders into the
   element. No monitor-specific labels or colours — uses
   var(--monitor-accent) throughout. Ready to call from any
   monitor's orchestrator.

   Added: 12 April 2026 (SCEM schema sprint)
   ─────────────────────────────────────────────────────────────── */

window.AsymSections = (function () {
  'use strict';

  /* ── Shared helpers ─────────────────────────────────────────── */

  function escHtml(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function deriveStatusClass(text) {
    var t = (text || '').toLowerCase();
    if (t.indexOf('ceasefire')  >= 0) return 'ceasefire';
    if (t.indexOf('de-escal')   >= 0 || t.indexOf('deescal') >= 0) return 'deescalating';
    if (t.indexOf('watch')      >= 0 || t.indexOf('monitor') >= 0) return 'monitoring';
    if (t.indexOf('escal')      >= 0) return 'escalating';
    if (t.indexOf('stable')     >= 0) return 'stable';
    if (t.indexOf('active')     >= 0) return 'active';
    return 'monitoring';
  }

  function buildStatusBadge(text, cls) {
    var icons = {
      active: '●', ceasefire: '⏸', deescalating: '↓',
      monitoring: '◎', escalating: '↑', stable: '→'
    };
    var icon = icons[cls] || '◎';
    return '<span class="status-badge status-badge--' + cls + '">' +
      '<span class="status-badge__icon" aria-hidden="true">' + icon + '</span>' +
      escHtml(text) +
    '</span>';
  }

  function bandToRowClass(band) {
    var b = (band || '').toUpperCase();
    if (b === 'RED'   || b === 'ANOMALOUS') return 'critical';
    if (b === 'AMBER' || b === 'ELEVATED')  return 'high';
    if (b === 'CONTESTED')                  return 'moderate';
    if (b === 'GREEN' || b === 'NORMAL')    return 'positive';
    return 'moderate';
  }

  function confBadgeClass(conf) {
    var c = (conf || '').toLowerCase();
    if (c === 'confirmed') return 'conf-badge--confirmed';
    if (c === 'high')      return 'conf-badge--high';
    if (c === 'assessed')  return 'conf-badge--assessed';
    return '';
  }

  function deviationBandClass(band) {
    var b = (band || '').toLowerCase();
    if (b.indexOf('green') !== -1) return 'ind-band--green';
    if (b.indexOf('amber') !== -1) return 'ind-band--amber';
    if (b.indexOf('red')   !== -1) return 'ind-band--red';
    return '';
  }

  function levelLabelClass(label) {
    var l = (label || '').toLowerCase();
    if (l === 'green')  return 'ind-level--green';
    if (l === 'amber')  return 'ind-level--amber';
    if (l === 'red')    return 'ind-level--red';
    if (l === 'crisis') return 'ind-level--crisis';
    return '';
  }

  /* ── Report / Dashboard sections ────────────────────────────── */

  /**
   * Escalation alert banner — threshold crossings.
   * Shows/hides parent section via optional sectionEl argument.
   * If empty, renders nothing (section stays hidden).
   */
  function renderEscalationAlerts(indicators, targetId, sectionEl) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!indicators || !indicators.length) return;
    if (sectionEl) sectionEl.style.display = '';

    var count = indicators.length;
    var html = '<div class="alert-banner">' +
      '<div class="alert-banner__heading">' +
        '<span aria-hidden="true">▲</span>' +
        escHtml(String(count)) + ' active threshold' + (count > 1 ? 's' : '') + ' crossed' +
      '</div>';

    indicators.forEach(function (item) {
      html +=
        '<div class="alert-banner__row">' +
          '<div class="alert-banner__entity">' + escHtml(item.theatre_id || '') + '</div>' +
          '<div class="alert-banner__indicator">' + escHtml(item.indicator || '') + '</div>' +
          '<div class="alert-banner__type">' + escHtml(item.type || '') + '</div>' +
          '<div class="alert-banner__threshold">' +
            '<span class="alert-banner__threshold-label">⚑ ' +
              escHtml(item.threshold_crossed || '') + '</span>' +
            (item.confidence_preliminary
              ? '<span class="alert-banner__conf">Confidence: ' +
                  escHtml(item.confidence_preliminary) + '</span>'
              : '') +
          '</div>' +
        '</div>';
    });

    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Global escalation snapshot — KPI card row.
   */
  function renderGlobalSnapshot(snapshot, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!snapshot || !Object.keys(snapshot).length) {
      el.innerHTML = '<p class="text-muted text-sm">No snapshot data available.</p>';
      return;
    }

    var kpis = [
      { key: 'active_theatres',           label: 'Active Theatres',   sub: '',          accent: true },
      { key: 'new_escalations_this_week', label: 'New Escalations',   sub: 'this week', accent: false },
      { key: 'de_escalations_this_week',  label: 'De-escalations',    sub: 'this week', accent: false },
      { key: 'highest_intensity_theatre', label: 'Highest Intensity', sub: '',          accent: false, text: true }
    ];

    var html = '<div class="kpi-row">';
    kpis.forEach(function (def) {
      var val = snapshot[def.key];
      if (val === undefined || val === null) return;
      var valStr = escHtml(String(val));
      var valClass = 'kpi-card__value' + (def.accent ? ' kpi-card__value--accent' : '');
      var valStyle = def.text
        ? ' style="font-size:var(--text-base,1rem);font-weight:700"'
        : '';
      html +=
        '<div class="kpi-card">' +
          '<div class="' + valClass + '"' + valStyle + '>' + valStr + '</div>' +
          '<div class="kpi-card__label">' + escHtml(def.label) + '</div>' +
          (def.sub ? '<div class="kpi-card__sub">' + escHtml(def.sub) + '</div>' : '') +
        '</div>';
    });
    html += '</div>';

    if (snapshot.lead_signal) {
      html += '<div class="snapshot-note">' + escHtml(snapshot.lead_signal) + '</div>';
    }

    el.innerHTML = html;
  }

  /**
   * Weekly brief — narrative paragraphs in a card.
   * Splits string on double newlines.
   */
  function renderWeeklyBrief(brief, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!brief) {
      el.innerHTML = '<p class="text-muted text-sm">No brief available this issue.</p>';
      return;
    }
    var html = '<div class="brief-card">';
    brief.split('\n\n').forEach(function (para) {
      var t = para.trim();
      if (t) html += '<p>' + escHtml(t) + '</p>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Theatre tracker — responsive card grid.
   */
  function renderTheatreTracker(theatres, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!theatres || !theatres.length) {
      el.innerHTML = '<p class="text-muted text-sm">No tracker data available.</p>';
      return;
    }

    var html = '<div class="theatre-grid">';
    theatres.forEach(function (t) {
      var deltaClass = deriveStatusClass(t.intensity_delta || '');

      var actorTags = (t.primary_actors || []).map(function (a) {
        return '<span class="tag tag--actor">' + escHtml(a) + '</span>';
      }).join('');

      var hybridTags = (t.hybrid_dimensions || []).map(function (h) {
        return '<span class="tag tag--hybrid">' + escHtml(h) + '</span>';
      }).join('');

      var warnTag = t.nuclear_threshold_concern
        ? '<span class="tag tag--warn">Nuclear Threshold</span>'
        : '';

      var riskClass = (function () {
        var r = (t.escalation_risk || '').toLowerCase();
        if (r === 'critical' || r === 'high') return 'critical';
        if (r === 'medium')  return 'high';
        if (r === 'low')     return 'positive';
        return 'moderate';
      })();

      var hasEventStats = t.acled_event_count_7d !== undefined ||
                          t.acled_fatality_count_7d !== undefined;

      html +=
        '<div class="theatre-card theatre-card--' + deltaClass + '">' +
          '<div class="theatre-card__header">' +
            '<div class="theatre-card__name">' +
              escHtml(t.theatre_name || t.theatre_id || '') + '</div>' +
            (t.intensity
              ? '<span class="theatre-card__intensity">' + escHtml(t.intensity) + '</span>'
              : '') +
          '</div>' +
          (actorTags
            ? '<div class="theatre-card__tags">' + actorTags + '</div>' : '') +
          (t.key_development
            ? '<div class="theatre-card__key-dev">' + escHtml(t.key_development) + '</div>' : '') +
          '<div class="theatre-card__row">' +
            (t.intensity_delta
              ? '<span class="theatre-card__delta theatre-card__delta--' + deltaClass + '">' +
                  escHtml(t.intensity_delta) + '</span>'
              : '') +
            (t.escalation_risk
              ? '<span class="severity-badge severity-badge--' + riskClass + '">Risk: ' +
                  escHtml(t.escalation_risk) + '</span>'
              : '') +
          '</div>' +
          (hasEventStats
            ? '<div class="theatre-card__stats">' +
                (t.acled_event_count_7d !== undefined
                  ? '<span>Events 7d: <strong>' +
                      escHtml(String(t.acled_event_count_7d)) + '</strong></span>'
                  : '') +
                (t.acled_fatality_count_7d !== undefined
                  ? '<span>Fatalities 7d: <strong>' +
                      escHtml(String(t.acled_fatality_count_7d)) + '</strong></span>'
                  : '') +
              '</div>'
            : '') +
          ((hybridTags || warnTag)
            ? '<div class="theatre-card__tags">' + hybridTags + warnTag + '</div>' : '') +
          '<div class="theatre-card__footer">' +
            (t.ceasefire_status !== undefined
              ? '<span>Ceasefire: ' + escHtml(t.ceasefire_status) + '</span>'
              : '<span></span>') +
            (t.source
              ? '<span style="font-size:var(--text-min)">' + escHtml(t.source) + '</span>'
              : '') +
          '</div>' +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Indicator scoring — per-entity tables with full detail.
   */
  function renderIndicatorScoring(scoring, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!scoring || !scoring.length) {
      el.innerHTML = '<p class="text-muted text-sm">No indicator scoring data available.</p>';
      return;
    }

    var html = '';
    scoring.forEach(function (entity) {
      var indicators = entity.indicators || [];
      html +=
        '<div class="scoring-block">' +
          '<div class="scoring-block__title">' + escHtml(entity.theatre_id || '') + '</div>' +
          '<table class="indicator-table">' +
            '<thead><tr>' +
              '<th>Indicator</th>' +
              '<th>Level</th>' +
              '<th>Baseline</th>' +
              '<th>Deviation</th>' +
              '<th>Label</th>' +
              '<th>Confidence</th>' +
              '<th>Tier / Source</th>' +
              '<th>Key Evidence</th>' +
              '<th>Note</th>' +
            '</tr></thead>' +
            '<tbody>';

      indicators.forEach(function (ind) {
        var levelClass = (function () {
          var ll = (ind.level_label || '').toLowerCase();
          if (ll === 'red' || ll === 'crisis' || ll === 'anomalous') return 'critical';
          if (ll === 'amber' || ll === 'elevated') return 'high';
          if (ll === 'green' || ll === 'normal')   return 'positive';
          return 'moderate';
        })();

        var pips = '';
        for (var i = 1; i <= 5; i++) {
          pips += '<div class="level-bar__pip' +
            (i <= (ind.level || 0) ? ' level-bar__pip--' + levelClass : '') +
          '"></div>';
        }

        var dev    = ind.deviation !== undefined ? Number(ind.deviation) : 0;
        var devStr = dev > 0 ? '+' + dev : String(dev);
        var devCol = dev > 0 ? 'var(--critical)' : dev < 0 ? 'var(--positive)' : 'var(--color-text-muted)';

        html +=
          '<tr>' +
            '<td>' +
              '<strong>' + escHtml(ind.indicator || '') + '</strong>' +
              (ind.indicator_name
                ? ' <span style="color:var(--color-text-muted);font-weight:400">' +
                    escHtml(ind.indicator_name) + '</span>'
                : '') +
              (ind.ai_generation_check
                ? ' <span title="AI generation check flagged" ' +
                    'style="color:var(--high,#d97706);font-size:var(--text-min)">AI⚑</span>'
                : '') +
            '</td>' +
            '<td>' +
              '<div class="level-bar">' + pips + '</div>' +
              '<span style="font-size:var(--text-min);margin-left:4px;color:var(--color-text-muted)">' +
                escHtml(String(ind.level !== undefined ? ind.level : 0)) + '/5</span>' +
            '</td>' +
            '<td>' + escHtml(String(ind.baseline !== undefined ? ind.baseline : '—')) + '</td>' +
            '<td>' +
              '<strong style="color:' + devCol + '">' + escHtml(devStr) + '</strong>' +
              (ind.deviation_band
                ? '<br><span style="font-size:var(--text-min);color:var(--color-text-muted)">' +
                    escHtml(ind.deviation_band) + '</span>'
                : '') +
            '</td>' +
            '<td><span class="severity-badge severity-badge--' + levelClass + '">' +
              escHtml(ind.level_label || '') + '</span></td>' +
            '<td>' + escHtml(ind.confidence_preliminary || '') + '</td>' +
            '<td style="white-space:nowrap">' +
              escHtml(ind.source_tier || '') +
              (ind.source
                ? '<br><span style="font-size:var(--text-min);color:var(--color-text-muted)">' +
                    escHtml(ind.source) + '</span>'
                : '') +
            '</td>' +
            '<td style="max-width:200px;white-space:normal;font-size:var(--text-min);' +
              'color:var(--color-text-secondary)">' +
              escHtml(ind.key_evidence || '') + '</td>' +
            '<td style="max-width:160px;white-space:normal;font-size:var(--text-min);' +
              'color:var(--color-text-muted)">' +
              escHtml(ind.note || '—') + '</td>' +
          '</tr>';
      });

      html += '</tbody></table></div>';
    });
    el.innerHTML = html;
  }

  /**
   * F-flag matrix — per-entity grid of flag tiles.
   */
  function renderFlagMatrix(matrix, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!matrix || !matrix.length) {
      el.innerHTML = '<p class="text-muted text-sm">No flag matrix data available.</p>';
      return;
    }

    var html = '';
    matrix.forEach(function (entity) {
      var flags = entity.f_flags || [];
      html +=
        '<div class="flag-matrix-entity">' +
          '<div class="flag-matrix-entity__title">' + escHtml(entity.theatre_id || '') + '</div>' +
          '<div class="flag-matrix-grid">';

      flags.forEach(function (f) {
        var detected = !!f.detected;
        html +=
          '<div class="flag-matrix-item' + (detected ? ' flag-matrix-item--detected' : '') + '">' +
            '<div class="flag-matrix-item__header">' +
              '<span class="f-flag-tag">' + escHtml(f.flag || '') + '</span>' +
              '<span class="flag-matrix-item__status ' +
                (detected ? 'flag-matrix-item__status--detected' : 'flag-matrix-item__status--clear') +
                '">' + (detected ? '● DETECTED' : '○ Clear') + '</span>' +
            '</div>' +
            '<div class="flag-matrix-item__name">' + escHtml(f.flag_name || '') + '</div>' +
            (f.indicator_affected
              ? '<div class="flag-matrix-item__desc">Affects: ' +
                  escHtml(f.indicator_affected) + '</div>'
              : '') +
            (f.description
              ? '<div class="flag-matrix-item__desc">' + escHtml(f.description) + '</div>'
              : '') +
            (f.fcw_link
              ? '<a class="flag-matrix-item__link" href="' + escHtml(f.fcw_link) +
                  '" target="_blank" rel="noopener">FCW link →</a>'
              : '') +
          '</div>';
      });

      html += '</div></div>';
    });
    el.innerHTML = html;
  }

  /**
   * ACLED reference — alignment table + global top-N.
   * Accepts both `scem_theatre_id`/`scem_tracked` and generic
   * `monitor_theatre_id`/`monitor_tracked` field names.
   */
  function renderACLEDReference(acled, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!acled || !Object.keys(acled).length) {
      el.innerHTML = '<p class="text-muted text-sm">No ACLED reference data available.</p>';
      return;
    }

    var html = '';

    // Meta row
    html += '<div class="ref-meta">' +
      (acled.index_version
        ? '<span>Index version: <strong>' + escHtml(acled.index_version) + '</strong></span>'
        : '') +
      (acled.last_updated
        ? '<span>Updated: <strong>' + escHtml(acled.last_updated) + '</strong></span>'
        : '') +
      (acled.source_url
        ? '<span><a href="' + escHtml(acled.source_url) +
            '" target="_blank" rel="noopener">Source index →</a></span>'
        : '') +
    '</div>';

    // Theatre alignment table
    var alignment = acled.theatre_alignment || [];
    if (alignment.length) {
      html += '<div class="ref-table-label">Theatre Alignment</div>' +
        '<table class="ref-table">' +
          '<thead><tr>' +
            '<th>Theatre</th>' +
            '<th>ACLED Rank</th>' +
            '<th>Category</th>' +
            '<th>Deadliness</th>' +
            '<th>Danger / Civilians</th>' +
            '<th>Geo Diffusion</th>' +
            '<th>Group Frag.</th>' +
            '<th>Band</th>' +
            '<th>Alignment</th>' +
            '<th>Divergence</th>' +
          '</tr></thead>' +
          '<tbody>';

      alignment.forEach(function (row) {
        var scores = row.acled_scores || {};
        // Support both scem_* and monitor_* field names
        var theatreId = row.scem_theatre_id || row.monitor_theatre_id || '';
        var overallBand = row.scem_overall_band || row.monitor_overall_band || '';
        html +=
          '<tr>' +
            '<td><strong>' + escHtml(theatreId) + '</strong></td>' +
            '<td style="text-align:center">' + escHtml(String(row.acled_rank || '—')) + '</td>' +
            '<td><span class="severity-badge severity-badge--critical">' +
              escHtml(row.acled_category || '') + '</span></td>' +
            '<td>' + buildScoreBar(scores.deadliness) + '</td>' +
            '<td>' + buildScoreBar(scores.danger_to_civilians) + '</td>' +
            '<td>' + buildScoreBar(scores.geographic_diffusion) + '</td>' +
            '<td>' + buildScoreBar(scores.armed_group_fragmentation) + '</td>' +
            '<td><span class="severity-badge severity-badge--' +
              bandToRowClass(overallBand) + '">' +
              escHtml(overallBand) + '</span></td>' +
            '<td>' + escHtml(row.alignment_status || '') + '</td>' +
            '<td style="font-size:var(--text-min);color:var(--color-text-muted)">' +
              escHtml(row.divergence_note || '—') + '</td>' +
          '</tr>';
      });
      html += '</tbody></table>';
    }

    // Global top-N table
    var topN = acled.global_top_20 || [];
    if (topN.length) {
      html += '<div class="ref-table-label" style="margin-top:var(--space-6)">Global Top ' +
        topN.length + ' — tracked entries highlighted</div>' +
        '<table class="ref-table">' +
          '<thead><tr>' +
            '<th>Rank</th>' +
            '<th>Country</th>' +
            '<th>Category</th>' +
            '<th>Deadliness</th>' +
            '<th>Danger / Civilians</th>' +
            '<th>Geo Diffusion</th>' +
            '<th>Group Frag.</th>' +
            '<th>Tracked</th>' +
          '</tr></thead>' +
          '<tbody>';

      topN.forEach(function (row) {
        // Support both scem_tracked and monitor_tracked
        var tracked = !!(row.scem_tracked || row.monitor_tracked);
        var theatreId = row.scem_theatre_id || row.monitor_theatre_id || '';
        html +=
          '<tr' + (tracked ? ' class="ref-table__row--tracked"' : '') + '>' +
            '<td style="text-align:center;font-weight:700;color:var(--color-text-muted)">' +
              escHtml(String(row.rank || '')) + '</td>' +
            '<td><strong>' + escHtml(row.country || '') + '</strong></td>' +
            '<td><span class="severity-badge severity-badge--critical">' +
              escHtml(row.category || '') + '</span></td>' +
            '<td>' + buildScoreBar(row.deadliness) + '</td>' +
            '<td>' + buildScoreBar(row.danger_to_civilians) + '</td>' +
            '<td>' + buildScoreBar(row.geographic_diffusion) + '</td>' +
            '<td>' + buildScoreBar(row.armed_group_fragmentation) + '</td>' +
            '<td>' +
              (tracked
                ? '<span class="tracked-badge">✓</span>'
                : '<span style="color:var(--color-text-muted);font-size:var(--text-min)">—</span>') +
            '</td>' +
          '</tr>';
      });
      html += '</tbody></table>';
    }

    el.innerHTML = html;
  }

  /** Score bar helper for ACLED reference tables. */
  function buildScoreBar(score) {
    if (score === undefined || score === null) {
      return '<span style="color:var(--color-text-muted)">—</span>';
    }
    var pct = Math.max(0, Math.min(100, Number(score)));
    return '<div class="score-bar">' +
      '<div class="score-bar__track">' +
        '<div class="score-bar__fill" style="width:' + pct + '%"></div>' +
      '</div>' +
      '<span class="score-bar__num">' + escHtml(String(score)) + '</span>' +
    '</div>';
  }

  /**
   * Key judgments — analyst judgment cards.
   */
  function renderKeyJudgments(judgments, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!judgments || !judgments.length) {
      el.innerHTML = '<p class="text-muted text-sm">No key judgments this issue.</p>';
      return;
    }

    var html = '<div class="kj-list">';
    judgments.forEach(function (kj) {
      var trajClass = kj.trajectory ? deriveStatusClass(kj.trajectory) : '';
      var trajBadge = kj.trajectory ? buildStatusBadge(kj.trajectory, trajClass) : '';

      var confClass = (function () {
        var c = (kj.confidence_preliminary || '').toLowerCase();
        if (c === 'confirmed') return 'positive';
        if (c === 'high')      return 'high';
        return 'moderate';
      })();

      html +=
        '<div class="kj-card">' +
          '<div class="kj-card__id">' + escHtml(kj.id || '') + '</div>' +
          '<div class="kj-card__body">' +
            '<div class="kj-card__text">' + escHtml(kj.judgment || '') + '</div>' +
            '<div class="kj-card__meta">' +
              (kj.theatre
                ? '<span class="kj-card__context">' + escHtml(kj.theatre) + '</span>'
                : '') +
              (kj.confidence_preliminary
                ? '<span class="severity-badge severity-badge--' + confClass + '">' +
                    escHtml(kj.confidence_preliminary) + '</span>'
                : '') +
              (trajBadge ? trajBadge : '') +
            '</div>' +
          '</div>' +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Cross-monitor candidates — signals flagged for other monitors.
   */
  function renderCrossMonitorCandidates(candidates, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!candidates || !candidates.length) {
      el.innerHTML = '<p class="text-muted text-sm">No cross-monitor candidates this issue.</p>';
      return;
    }

    var html = '<div class="cmc-list">';
    candidates.forEach(function (c) {
      html +=
        '<div class="cmc-item">' +
          '<div class="cmc-item__target">' + escHtml(c.target_monitor || '') + '</div>' +
          '<div class="cmc-item__body">' +
            '<div class="cmc-item__signal">' + escHtml(c.signal || '') + '</div>' +
            '<div class="cmc-item__meta">' +
              (c.type
                ? '<span>' + escHtml(c.type) + '</span>'
                : '') +
              (c.confidence_preliminary
                ? '<span>Confidence: ' + escHtml(c.confidence_preliminary) + '</span>'
                : '') +
            '</div>' +
          '</div>' +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  /* ── Persistent-page helpers ────────────────────────────────── */

  /**
   * Enrich a baseline card with theatre tracker data.
   * Returns HTML string for a theatre metadata strip.
   */
  function enrichBaselineWithTheatre(t) {
    if (!t) return '';

    var deltaKey = (t.intensity_delta || '').toLowerCase().replace(/\s+/g, '-');
    var deltaClass = deltaKey ? 'delta-badge--' + deltaKey : '';

    var riskKey = (t.escalation_risk || '').toLowerCase();
    var riskClass = riskKey === 'high' ? 'esc-risk-val--high'
      : riskKey === 'medium' ? 'esc-risk-val--medium'
      : riskKey === 'low'    ? 'esc-risk-val--low'
      : '';

    var ceasefireRaw = t.ceasefire_status || '';
    var ceasefireActive = ceasefireRaw &&
      ceasefireRaw.toLowerCase() !== 'none' &&
      ceasefireRaw.toLowerCase() !== 'no';
    var ceasefireClass = ceasefireActive ? 'ceasefire-badge--active' : '';

    var actors = Array.isArray(t.primary_actors)    ? t.primary_actors.join(', ')    : (t.primary_actors || '');
    var hybrid = Array.isArray(t.hybrid_dimensions) ? t.hybrid_dimensions.join(', ') : (t.hybrid_dimensions || '');

    var items = [];

    if (t.intensity) {
      items.push(
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Intensity</span>' +
          '<span class="theatre-strip__value">' + escHtml(t.intensity) + '</span>' +
        '</div>'
      );
    }

    if (t.intensity_delta) {
      items.push(
        '<div class="theatre-strip__divider"></div>' +
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Delta</span>' +
          '<span class="theatre-strip__value">' +
            '<span class="delta-badge ' + deltaClass + '">' + escHtml(t.intensity_delta) + '</span>' +
          '</span>' +
        '</div>'
      );
    }

    if (t.escalation_risk) {
      items.push(
        '<div class="theatre-strip__divider"></div>' +
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Esc. Risk</span>' +
          '<span class="theatre-strip__value esc-risk-val ' + riskClass + '">' + escHtml(t.escalation_risk) + '</span>' +
        '</div>'
      );
    }

    if (ceasefireRaw) {
      items.push(
        '<div class="theatre-strip__divider"></div>' +
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Ceasefire</span>' +
          '<span class="theatre-strip__value">' +
            '<span class="ceasefire-badge ' + ceasefireClass + '">' + escHtml(ceasefireRaw) + '</span>' +
          '</span>' +
        '</div>'
      );
    }

    if (actors) {
      items.push(
        '<div class="theatre-strip__divider"></div>' +
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Primary Actors</span>' +
          '<span class="theatre-strip__value">' + escHtml(actors) + '</span>' +
        '</div>'
      );
    }

    if (hybrid) {
      items.push(
        '<div class="theatre-strip__divider"></div>' +
        '<div class="theatre-strip__item">' +
          '<span class="theatre-strip__label">Hybrid Dims</span>' +
          '<span class="theatre-strip__value">' + escHtml(hybrid) + '</span>' +
        '</div>'
      );
    }

    if (!items.length) return '';
    return '<div class="theatre-strip">' + items.join('') + '</div>';
  }

  /**
   * Enrich an indicator cell with detailed scoring data.
   * Returns HTML string with expand button + detail panel.
   */
  function enrichIndicatorCell(s) {
    if (!s) return '';

    var uid = 'ind-' + Math.random().toString(36).slice(2, 9);
    var lvlClass  = levelLabelClass(s.level_label);
    var bandClass = deviationBandClass(s.deviation_band);
    var cClass    = confBadgeClass(s.confidence_preliminary);

    var levelDisplay = s.level_label
      ? escHtml(s.level_label) + (s.level !== undefined ? ' (' + escHtml(String(s.level)) + ')' : '')
      : (s.level !== undefined ? escHtml(String(s.level)) : '—');

    var rows = '';

    rows += '<div class="ind-scoring-detail__row">' +
      '<span class="ind-scoring-detail__label">Level</span>' +
      '<span class="ind-scoring-detail__val ' + lvlClass + '">' + levelDisplay + '</span>' +
    '</div>';

    if (s.deviation !== undefined && s.deviation !== null) {
      rows += '<div class="ind-scoring-detail__row">' +
        '<span class="ind-scoring-detail__label">Deviation</span>' +
        '<span class="ind-scoring-detail__val ' + bandClass + '">' +
          escHtml(String(s.deviation)) +
          (s.deviation_band ? ' — ' + escHtml(s.deviation_band) : '') +
        '</span>' +
      '</div>';
    }

    if (s.confidence_preliminary) {
      rows += '<div class="ind-scoring-detail__row">' +
        '<span class="ind-scoring-detail__label">Confidence</span>' +
        '<span class="ind-scoring-detail__val">' +
          '<span class="conf-badge ' + cClass + '">' + escHtml(s.confidence_preliminary) + '</span>' +
        '</span>' +
      '</div>';
    }

    if (s.key_evidence) {
      rows += '<div class="ind-scoring-detail__row">' +
        '<span class="ind-scoring-detail__label">Evidence</span>' +
        '<span class="ind-scoring-detail__val">' + escHtml(s.key_evidence) + '</span>' +
      '</div>';
    }

    if (s.source) {
      var srcVal = escHtml(s.source) + (s.source_tier ? ' (' + escHtml(s.source_tier) + ')' : '');
      rows += '<div class="ind-scoring-detail__row">' +
        '<span class="ind-scoring-detail__label">Source</span>' +
        '<span class="ind-scoring-detail__val">' + srcVal + '</span>' +
      '</div>';
    }

    if (s.note) {
      rows += '<div class="ind-scoring-detail__row">' +
        '<span class="ind-scoring-detail__label">Note</span>' +
        '<span class="ind-scoring-detail__val" style="font-style:italic">' + escHtml(s.note) + '</span>' +
      '</div>';
    }

    return (
      '<button class="ind-expand-btn" type="button" aria-expanded="false" aria-controls="' + uid + '">Details ▸</button>' +
      '<div class="ind-scoring-detail" id="' + uid + '" role="region">' +
        rows +
      '</div>'
    );
  }

  /**
   * Escalation log — accumulating threshold crossings (persistent page).
   */
  function renderEscalationLog(indicators, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;

    if (!indicators || !indicators.length) {
      el.innerHTML = '<p class="text-muted text-sm">No threshold crossings recorded.</p>';
      return;
    }

    var html = '<div class="esc-log">';
    indicators.forEach(function (item) {
      var cClass = confBadgeClass(item.confidence_preliminary);
      html +=
        '<div class="esc-log__entry">' +
          '<div class="esc-log__entry-body">' +
            (item.theatre_id
              ? '<div class="esc-log__theatre-id">' + escHtml(item.theatre_id) + '</div>'
              : '') +
            (item.indicator
              ? '<div class="esc-log__indicator-name">' + escHtml(item.indicator) + '</div>'
              : '') +
            '<div class="esc-log__meta">' +
              (item.type
                ? '<span class="esc-type-badge">' + escHtml(item.type) + '</span>'
                : '') +
              (item.threshold_crossed
                ? '<span>Threshold: <span class="esc-threshold-val">' + escHtml(item.threshold_crossed) + '</span></span>'
                : '') +
              (item.confidence_preliminary
                ? '<span class="conf-badge ' + cClass + '">' + escHtml(item.confidence_preliminary) + '</span>'
                : '') +
            '</div>' +
          '</div>' +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  /* ── ESA-specific sections ──────────────────────────────────── */

  /**
   * Domain tracker — 6 autonomy domain cards in a 2-column grid.
   * domain_tracker[] → each card: accent bar, score %, delta badge,
   * dependency risk/actor, key development, policy response, source link.
   */
  function renderDomainTracker(domains, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!domains || !domains.length) {
      el.innerHTML = '<p class="text-muted text-sm">No domain tracker data available.</p>';
      return;
    }

    var DOMAIN_COLOURS = {
      defence_security:       '#dc2626',
      energy_climate:         '#22a0aa',
      digital_ai:             '#38bdf8',
      financial_economic:     '#3a7d5a',
      supply_chain_industrial:'#f59e0b',
      space_satellite:        '#8b5cf6'
    };

    var DOMAIN_LABELS = {
      defence_security:       'Defence & Security',
      energy_climate:         'Energy & Climate',
      digital_ai:             'Digital & AI',
      financial_economic:     'Financial & Economic',
      supply_chain_industrial:'Supply Chain & Industrial',
      space_satellite:        'Space & Satellite'
    };

    function deltaBadge(delta) {
      var d = (delta || '').toLowerCase();
      var colour = d === 'improving'  ? 'var(--positive,#4caf7d)'
                 : d === 'declining'  ? 'var(--critical,#dc2626)'
                 : 'var(--color-text-muted,#888)';
      var arrow  = d === 'improving' ? '↑' : d === 'declining' ? '↓' : '→';
      return '<span class="domain-card__delta" style="color:' + colour +
        ';font-size:var(--text-xs);font-weight:600;letter-spacing:.02em">' +
        arrow + ' ' + escHtml(delta || 'Stable') + '</span>';
    }

    function depRiskBadge(risk) {
      var r = (risk || '').toLowerCase();
      var colour = r === 'high'   ? 'var(--critical,#dc2626)'
                 : r === 'medium' ? 'var(--high,#d97706)'
                 : r === 'low'    ? 'var(--positive,#4caf7d)'
                 : 'var(--color-text-muted)';
      return '<span class="domain-card__dep-badge" style="color:' + colour +
        ';font-weight:600">' + escHtml(risk || '—') + '</span>';
    }

    var html =
      '<style>' +
        '@media(min-width:640px){.domain-tracker-grid{grid-template-columns:1fr 1fr!important}}' +
      '</style>' +
      '<div class="domain-tracker-grid" style="display:grid;grid-template-columns:1fr;gap:var(--space-4)">';

    domains.forEach(function (d) {
      var key    = d.domain || '';
      var colour = DOMAIN_COLOURS[key] || 'var(--monitor-accent)';
      var label  = DOMAIN_LABELS[key] || escHtml(key.replace(/_/g, ' '));
      var score  = d.autonomy_score_preliminary;
      var pct    = (score !== undefined && score !== null)
                   ? Math.round(Number(score) * 100) : null;

      html +=
        '<div class="domain-card" style="border-radius:var(--radius-md,6px);' +
          'background:var(--color-surface-raised,#1a1a2e);overflow:hidden;' +
          'border:1px solid var(--color-border,rgba(255,255,255,.08))">' +

          // Accent bar
          '<div class="domain-card__bar" style="height:3px;background:' + colour + '"></div>' +

          '<div style="padding:var(--space-4)">' +

            // Header row: label + delta
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-2)">' +
              '<span class="domain-card__label" style="font-weight:700;font-size:var(--text-sm);' +
                'color:' + colour + '">' + escHtml(label) + '</span>' +
              deltaBadge(d.score_delta) +
            '</div>' +

            // Score bar
            (pct !== null
              ? '<div style="margin-bottom:var(--space-3)">' +
                  '<div style="display:flex;align-items:center;gap:var(--space-2)">' +
                    '<div style="flex:1;height:6px;background:var(--color-border,rgba(255,255,255,.1));' +
                      'border-radius:3px;overflow:hidden">' +
                      '<div style="width:' + pct + '%;height:100%;background:' + colour +
                        ';border-radius:3px;transition:width .3s"></div>' +
                    '</div>' +
                    '<span style="font-size:var(--text-xs);color:var(--color-text-muted);' +
                      'white-space:nowrap;min-width:2.5rem;text-align:right">' +
                      pct + '%' +
                    '</span>' +
                  '</div>' +
                '</div>'
              : '') +

            // Dependency risk + actor
            '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-2);' +
              'font-size:var(--text-xs)">' +
              '<span style="color:var(--color-text-muted)">Dep. risk:</span>' +
              depRiskBadge(d.dependency_risk) +
              (d.dependency_actor
                ? '<span style="color:var(--color-text-muted)">/ <strong>' +
                    escHtml(d.dependency_actor) + '</strong></span>'
                : '') +
            '</div>' +

            // Key development
            (d.key_development
              ? '<div class="domain-card__dev" style="font-size:var(--text-xs);' +
                  'color:var(--color-text-secondary,#bbb);margin-bottom:var(--space-2);' +
                  'line-height:1.5">' + escHtml(d.key_development) + '</div>'
              : '') +

            // Policy response
            (d.policy_response
              ? '<div style="font-size:var(--text-xs);color:var(--color-text-muted);' +
                  'font-style:italic;margin-bottom:var(--space-2);line-height:1.5">' +
                  '↳ ' + escHtml(d.policy_response) + '</div>'
              : '') +

            // Source link
            (d.source_url
              ? '<div style="margin-top:var(--space-1)">' +
                  '<a href="' + escHtml(d.source_url) + '" target="_blank" rel="noopener" ' +
                  'style="color:' + colour + ';font-size:var(--text-min);text-decoration:none" ' +
                  'onmouseover="this.style.textDecoration=\'underline\'" ' +
                  'onmouseout="this.style.textDecoration=\'none\'">' +
                  'Source →</a>' +
                '</div>'
              : '') +

          '</div>' +
        '</div>';
    });

    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Autonomy snapshot — KPI row (4 cards) + lead signal.
   * autonomy_snapshot{} → Trajectory, Lead Domain, US Decoupling, ReArm Status.
   */
  function renderAutonomySnapshot(snapshot, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!snapshot || !Object.keys(snapshot).length) {
      el.innerHTML = '<p class="text-muted text-sm">No autonomy snapshot available.</p>';
      return;
    }

    var DOMAIN_LABELS = {
      defence_security:       'Defence & Security',
      energy_climate:         'Energy & Climate',
      digital_ai:             'Digital & AI',
      financial_economic:     'Financial & Economic',
      supply_chain_industrial:'Supply Chain & Industrial',
      space_satellite:        'Space & Satellite'
    };

    function trajColour(traj) {
      var t = (traj || '').toLowerCase();
      if (t === 'improving')     return 'var(--positive,#4caf7d)';
      if (t === 'declining')     return 'var(--critical,#dc2626)';
      if (t === 'accelerating')  return 'var(--positive,#4caf7d)';
      if (t === 'deteriorating') return 'var(--critical,#dc2626)';
      return 'var(--monitor-accent)';
    }

    var leadDomainRaw = snapshot.lead_domain || '';
    var leadDomainLabel = DOMAIN_LABELS[leadDomainRaw] ||
      leadDomainRaw.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });

    var kpis = [
      {
        label: 'Trajectory',
        value: escHtml(snapshot.overall_trajectory || '—'),
        style: 'color:' + trajColour(snapshot.overall_trajectory) + ';font-weight:700'
      },
      {
        label: 'Lead Domain',
        value: escHtml(leadDomainLabel || '—'),
        style: 'font-size:var(--text-sm);font-weight:700'
      },
      {
        label: 'US Decoupling Signal',
        value: escHtml(snapshot.us_decoupling_signal || '—'),
        style: 'font-weight:700'
      },
      {
        label: 'ReArm Europe Status',
        value: escHtml(snapshot.rearm_europe_status || '—'),
        style: 'font-size:var(--text-xs);font-weight:600;line-height:1.4'
      }
    ];

    var html = '<div class="kpi-row">';
    kpis.forEach(function (k) {
      html +=
        '<div class="kpi-card">' +
          '<div class="kpi-card__value" style="' + k.style + '">' + k.value + '</div>' +
          '<div class="kpi-card__label">' + escHtml(k.label) + '</div>' +
        '</div>';
    });
    html += '</div>';

    if (snapshot.lead_signal) {
      html += '<div class="snapshot-note">' + escHtml(snapshot.lead_signal) + '</div>';
    }

    el.innerHTML = html;
  }

  /**
   * US-EU tracker — status panel: 4 items in a grid + key development.
   * us_eu_tracker{} → decoupling_level, nato_status, trade_pressure,
   *                    intelligence_sharing, key_development_this_week, source_url
   */
  function renderUsEuTracker(tracker, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!tracker || !Object.keys(tracker).length) {
      el.innerHTML = '<p class="text-muted text-sm">No US-EU tracker data available.</p>';
      return;
    }

    function decouplingColour(level) {
      var l = (level || '').toLowerCase();
      if (l === 'aligned')    return 'var(--positive,#4caf7d)';
      if (l === 'drifting')   return 'var(--high,#d97706)';
      if (l === 'decoupling') return 'var(--critical,#dc2626)';
      if (l === 'hostile')    return '#7f1d1d';
      return 'var(--color-text-muted)';
    }

    function statusChip(value, colour) {
      if (!value) return '<span style="color:var(--color-text-muted);font-size:var(--text-xs)">—</span>';
      return '<span class="useu-chip" style="display:inline-block;padding:2px 8px;' +
        'border-radius:3px;background:' + colour + '20;color:' + colour + ';' +
        'font-weight:700;font-size:var(--text-xs)">' + escHtml(value) + '</span>';
    }

    var dColour = decouplingColour(tracker.decoupling_level);

    var items = [
      {
        label: 'Decoupling Level',
        content: statusChip(tracker.decoupling_level, dColour)
      },
      {
        label: 'NATO Status',
        content: '<span style="font-size:var(--text-xs);color:var(--color-text-secondary)">' +
          escHtml(tracker.nato_status || '—') + '</span>'
      },
      {
        label: 'Trade Pressure',
        content: tracker.trade_pressure
          ? '<span style="font-size:var(--text-xs);color:var(--high,#d97706)">' +
              escHtml(tracker.trade_pressure) + '</span>'
          : '<span style="color:var(--positive,#4caf7d);font-size:var(--text-xs)">None reported</span>'
      },
      {
        label: 'Intelligence Sharing',
        content: (function () {
          var v = tracker.intelligence_sharing || '—';
          var c = v.toLowerCase() === 'full' ? 'var(--positive,#4caf7d)'
                : v.toLowerCase() === 'partial' ? 'var(--high,#d97706)'
                : v.toLowerCase() === 'suspended' ? 'var(--critical,#dc2626)'
                : 'var(--color-text-muted)';
          return statusChip(v, c);
        })()
      }
    ];

    var html =
      '<div class="useu-grid" style="display:grid;grid-template-columns:1fr 1fr;' +
        'gap:var(--space-3);margin-bottom:var(--space-4)">';

    items.forEach(function (item) {
      html +=
        '<div class="useu-item" style="padding:var(--space-3);' +
          'background:var(--color-surface-raised,#1a1a2e);' +
          'border-radius:var(--radius-sm,4px);' +
          'border:1px solid var(--color-border,rgba(255,255,255,.08))">' +
          '<div style="font-size:var(--text-xs);color:var(--color-text-muted);' +
            'text-transform:uppercase;letter-spacing:.05em;margin-bottom:var(--space-1)">' +
            escHtml(item.label) +
          '</div>' +
          item.content +
        '</div>';
    });

    html += '</div>';

    if (tracker.key_development_this_week) {
      html +=
        '<div class="useu-key-dev" style="padding:var(--space-3);' +
          'background:var(--monitor-accent,#5b8db0)1a;' +
          'border-left:3px solid var(--monitor-accent,#5b8db0);' +
          'border-radius:0 var(--radius-sm,4px) var(--radius-sm,4px) 0;' +
          'font-size:var(--text-sm);color:var(--color-text-secondary);' +
          'margin-bottom:var(--space-3)">' +
          '<span style="font-weight:700;color:var(--monitor-accent,#5b8db0);' +
            'font-size:var(--text-xs);text-transform:uppercase;letter-spacing:.05em;' +
            'display:block;margin-bottom:var(--space-1)">Key Development</span>' +
          escHtml(tracker.key_development_this_week) +
        '</div>';
    }

    if (tracker.source_url) {
      html +=
        '<div style="font-size:var(--text-xs)">' +
          '<a href="' + escHtml(tracker.source_url) + '" target="_blank" rel="noopener" ' +
          'style="color:var(--monitor-accent);text-decoration:none" ' +
          'onmouseover="this.style.textDecoration=\'underline\'" ' +
          'onmouseout="this.style.textDecoration=\'none\'">Source →</a>' +
        '</div>';
    }

    el.innerHTML = html;
  }

  /**
   * Election threats — sortable table.
   * elections[] → Country, Election Date, Type, Days Until, Risk Rating, FIMI Risk.
   * Risk rating badges: Critical=red, High=orange, Elevated=amber, Monitored=blue.
   */
  function renderElectionThreats(elections, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!elections || !elections.length) {
      el.innerHTML =
        '<p class="text-muted text-sm">No elections within monitoring window.</p>';
      return;
    }

    function riskClass(rating) {
      var r = (rating || '').toLowerCase();
      if (r === 'critical')  return 'critical';
      if (r === 'high')      return 'high';
      if (r === 'elevated')  return 'moderate';
      if (r === 'monitored' || r === 'low') return 'positive';
      return 'moderate';
    }

    function daysUntil(dateStr) {
      if (!dateStr) return '—';
      try {
        var d = new Date(dateStr);
        if (isNaN(d.getTime())) return '—';
        var diff = Math.round((d - Date.now()) / 86400000);
        if (diff < 0) return 'Past';
        if (diff === 0) return 'Today';
        return diff + 'd';
      } catch (e) { return '—'; }
    }

    function formatShortDate(dateStr) {
      if (!dateStr) return '—';
      try {
        var d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
      } catch (e) { return dateStr; }
    }

    var html =
      '<div style="overflow-x:auto">' +
      '<table class="election-table" style="width:100%;border-collapse:collapse;font-size:var(--text-sm)">' +
        '<thead>' +
          '<tr style="border-bottom:1px solid var(--color-border,rgba(255,255,255,.12))">' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Country</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Election Date</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Type</th>' +
            '<th style="text-align:center;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Days Until</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Risk Rating</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">FIMI Risk</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>';

    elections.forEach(function (e, idx) {
      var rc   = riskClass(e.risk_rating);
      var days = daysUntil(e.election_date);
      var daysColour = (function () {
        if (days === 'Today') return 'var(--critical,#dc2626)';
        var n = parseInt(days, 10);
        if (!isNaN(n) && n <= 7)  return 'var(--critical,#dc2626)';
        if (!isNaN(n) && n <= 30) return 'var(--high,#d97706)';
        return 'inherit';
      })();
      var rowBg = idx % 2 === 1
        ? 'background:var(--color-surface-raised,rgba(255,255,255,.02))'
        : '';

      html +=
        '<tr style="border-bottom:1px solid var(--color-border,rgba(255,255,255,.06));' + rowBg + '">' +
          '<td style="padding:var(--space-2) var(--space-3);font-weight:700">' +
            (window.AsymRenderer && window.AsymRenderer.flag
              ? window.AsymRenderer.flag(e.country || '') + ' ' : '') +
            escHtml(e.country || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);white-space:nowrap">' +
            escHtml(formatShortDate(e.election_date)) +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);color:var(--color-text-muted)">' +
            escHtml(e.election_type || e.type || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);text-align:center;' +
            'font-weight:700;color:' + daysColour + '">' + escHtml(days) + '</td>' +
          '<td style="padding:var(--space-2) var(--space-3)">' +
            (e.risk_rating
              ? '<span class="severity-badge severity-badge--' + rc + '">' +
                  escHtml(e.risk_rating) + '</span>'
              : '<span style="color:var(--color-text-muted)">—</span>') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3)">' +
            (e.fimi_risk
              ? '<span class="severity-badge severity-badge--' + riskClass(e.fimi_risk) + '">' +
                  escHtml(e.fimi_risk) + '</span>'
              : '<span style="color:var(--color-text-muted)">—</span>') +
          '</td>' +
        '</tr>';
    });

    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  /**
   * Lagrange point scores — vertical list.
   * lagrange_point_scores[] → vector label, progress status badge,
   *                           key metric, blocker, source link.
   * NOT the radar chart — that lives in persistent.html.
   */
  function renderLagrangeScores(scores, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!scores || !scores.length) {
      el.innerHTML = '<p class="text-muted text-sm">No Lagrange point data available.</p>';
      return;
    }

    function progressColour(prog) {
      var p = (prog || '').toLowerCase();
      if (p === 'regressing')    return 'var(--critical,#dc2626)';
      if (p === 'stalled')       return 'var(--high,#d97706)';
      if (p === 'incremental')   return 'var(--monitor-accent,#5b8db0)';
      if (p === 'advancing')     return 'var(--positive,#4caf7d)';
      if (p === 'breakthrough')  return '#22c55e';
      if (p === 'stable')        return 'var(--color-text-muted,#888)';
      return 'var(--color-text-muted,#888)';
    }

    function progressIcon(prog) {
      var p = (prog || '').toLowerCase();
      if (p === 'regressing')   return '↓';
      if (p === 'stalled')      return '⏸';
      if (p === 'incremental')  return '→';
      if (p === 'advancing')    return '↑';
      if (p === 'breakthrough') return '⚡';
      if (p === 'stable')       return '→';
      return '◎';
    }

    var html = '<div class="lagrange-list" style="display:flex;flex-direction:column;gap:var(--space-2)">';

    scores.forEach(function (s) {
      var colour = progressColour(s.progress_preliminary);
      var icon   = progressIcon(s.progress_preliminary);

      html +=
        '<div class="lagrange-row" style="display:flex;align-items:flex-start;gap:var(--space-3);' +
          'padding:var(--space-3);' +
          'background:var(--color-surface-raised,rgba(255,255,255,.03));' +
          'border-radius:var(--radius-sm,4px);' +
          'border:1px solid var(--color-border,rgba(255,255,255,.07))">' +

          // Progress badge
          '<div class="lagrange-row__badge" style="flex-shrink:0;display:flex;align-items:center;' +
            'gap:4px;min-width:90px">' +
            '<span style="color:' + colour + ';font-size:1rem" aria-hidden="true">' + icon + '</span>' +
            '<span style="color:' + colour + ';font-weight:700;font-size:var(--text-xs);' +
              'white-space:nowrap">' + escHtml(s.progress_preliminary || '—') + '</span>' +
          '</div>' +

          // Body
          '<div style="flex:1;min-width:0">' +
            '<div style="font-weight:700;font-size:var(--text-sm);' +
              'color:var(--color-text-primary,#fff);margin-bottom:2px">' +
              escHtml(s.vector || '') +
            '</div>' +
            (s.key_metric
              ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary,#bbb);' +
                  'margin-bottom:2px">' + escHtml(s.key_metric) + '</div>'
              : '') +
            (s.blocker
              ? '<div style="font-size:var(--text-xs);color:var(--high,#d97706)">' +
                  '⚑ Blocker: ' + escHtml(s.blocker) + '</div>'
              : '') +
            (s.source_url
              ? '<div style="margin-top:4px">' +
                  '<a href="' + escHtml(s.source_url) + '" target="_blank" rel="noopener" ' +
                  'style="color:var(--monitor-accent);font-size:var(--text-min);text-decoration:none" ' +
                  'onmouseover="this.style.textDecoration=\'underline\'" ' +
                  'onmouseout="this.style.textDecoration=\'none\'">Source →</a>' +
                '</div>'
              : '') +
          '</div>' +

        '</div>';
    });

    html += '</div>';
    el.innerHTML = html;
  }

  /**
   * Defence spending — sortable table with flag emoji, GDP%, target,
   * budget (€bn), EDIP committed, change, on-track badge.
   */
  function renderDefenceSpending(spending, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!spending || !spending.length) {
      el.innerHTML =
        '<p class="text-muted text-sm">Defence spending data not yet available for this period.</p>';
      return;
    }

    var html =
      '<div style="overflow-x:auto">' +
      '<table class="defence-spending-table" ' +
        'style="width:100%;border-collapse:collapse;font-size:var(--text-sm)">' +
        '<thead>' +
          '<tr style="border-bottom:2px solid var(--color-border,rgba(255,255,255,.15))">' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Country</th>' +
            '<th style="text-align:right;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">GDP%</th>' +
            '<th style="text-align:right;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Target</th>' +
            '<th style="text-align:right;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Budget (€bn)</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">EDIP Committed</th>' +
            '<th style="text-align:left;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">Change</th>' +
            '<th style="text-align:center;padding:var(--space-2) var(--space-3);font-size:var(--text-xs);' +
              'text-transform:uppercase;letter-spacing:.05em;color:var(--color-text-muted);font-weight:600">On Track</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>';

    spending.forEach(function (row, idx) {
      var flagHtml = (window.AsymRenderer && window.AsymRenderer.flag)
        ? window.AsymRenderer.flag(row.country || '') + ' '
        : '';
      var rowBg = idx % 2 === 1
        ? 'background:var(--color-surface-raised,rgba(255,255,255,.02))'
        : '';

      var onTrack = row.on_track;
      var trackBadge = onTrack === true || onTrack === 'true' || onTrack === 'yes'
        ? '<span style="color:var(--positive,#4caf7d);font-size:1rem" title="On track">✓</span>'
        : onTrack === false || onTrack === 'false' || onTrack === 'no'
          ? '<span style="color:var(--critical,#dc2626);font-size:1rem" title="Not on track">✗</span>'
          : '<span style="color:var(--color-text-muted)">—</span>';

      var changeColour = (function () {
        var c = (row.change || '').toString();
        if (c.indexOf('+') >= 0) return 'var(--positive,#4caf7d)';
        if (c.indexOf('-') >= 0) return 'var(--critical,#dc2626)';
        return 'inherit';
      })();

      html +=
        '<tr style="border-bottom:1px solid var(--color-border,rgba(255,255,255,.06));' + rowBg + '">' +
          '<td style="padding:var(--space-2) var(--space-3);font-weight:700">' +
            flagHtml + escHtml(row.country || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);text-align:right;font-weight:700;' +
            'color:var(--monitor-accent)">' +
            escHtml(row.gdp_pct !== undefined ? String(row.gdp_pct) + '%' : '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);text-align:right;' +
            'color:var(--color-text-muted)">' +
            escHtml(row.target || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);text-align:right">' +
            escHtml(row.budget_bn !== undefined ? String(row.budget_bn) : '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);color:var(--color-text-muted);' +
            'font-size:var(--text-xs)">' +
            escHtml(row.edip_committed || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);font-weight:700;color:' + changeColour + '">' +
            escHtml(row.change || '—') +
          '</td>' +
          '<td style="padding:var(--space-2) var(--space-3);text-align:center">' +
            trackBadge +
          '</td>' +
        '</tr>';
    });

    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  /**
   * Defence programmes — card grid.
   * defence_programmes[] → name, status badge, capability area, budget committed/disbursed,
   *                        lead nations, score impact, update this week.
   * Status colours: Announced=blue, Funded=green, In procurement=amber,
   *                 Operational=bright green, Delayed=red, Cancelled=grey.
   */
  function renderDefenceProgrammes(programmes, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!programmes || !programmes.length) {
      el.innerHTML =
        '<p class="text-muted text-sm">No defence programme updates this period.</p>';
      return;
    }

    function statusColour(status) {
      var s = (status || '').toLowerCase();
      if (s === 'announced')       return { bg: '#2563eb20', border: '#2563eb', text: '#60a5fa' };
      if (s === 'funded')          return { bg: '#4caf7d20', border: '#4caf7d', text: '#4caf7d' };
      if (s === 'in procurement')  return { bg: '#d9770620', border: '#d97706', text: '#fbbf24' };
      if (s === 'operational')     return { bg: '#22c55e20', border: '#22c55e', text: '#22c55e' };
      if (s === 'delayed')         return { bg: '#dc262620', border: '#dc2626', text: '#f87171' };
      if (s === 'cancelled')       return { bg: '#6b728020', border: '#6b7280', text: '#9ca3af' };
      return { bg: 'rgba(255,255,255,.05)', border: 'var(--color-border)', text: 'var(--color-text-muted)' };
    }

    function scoreBadge(impact) {
      if (!impact) return '';
      var i = (impact || '').toString();
      var colour = i.indexOf('+') >= 0 ? 'var(--positive,#4caf7d)'
                 : i.indexOf('-') >= 0 ? 'var(--critical,#dc2626)'
                 : 'var(--color-text-muted)';
      return '<span style="font-size:var(--text-xs);color:' + colour + ';font-weight:700">' +
        'Score: ' + escHtml(i) + '</span>';
    }

    var html = '<div class="programmes-grid" style="display:grid;grid-template-columns:1fr;' +
      'gap:var(--space-3)">';

    programmes.forEach(function (p) {
      var colours = statusColour(p.status);

      var leadNations = Array.isArray(p.lead_nations)
        ? p.lead_nations.join(', ')
        : (p.lead_nations || '');

      html +=
        '<div class="programme-card" style="border-radius:var(--radius-md,6px);' +
          'background:var(--color-surface-raised,#1a1a2e);' +
          'border:1px solid var(--color-border,rgba(255,255,255,.08));overflow:hidden">' +

          // Status colour bar
          '<div style="height:2px;background:' + colours.border + '"></div>' +

          '<div style="padding:var(--space-4)">' +

            // Header: name + status badge
            '<div style="display:flex;align-items:flex-start;justify-content:space-between;' +
              'gap:var(--space-3);margin-bottom:var(--space-2)">' +
              '<div style="font-weight:700;font-size:var(--text-sm);' +
                'color:var(--color-text-primary,#fff)">' + escHtml(p.name || p.programme || '') + '</div>' +
              (p.status
                ? '<span style="flex-shrink:0;padding:2px 8px;border-radius:3px;' +
                    'background:' + colours.bg + ';border:1px solid ' + colours.border + ';' +
                    'color:' + colours.text + ';font-size:var(--text-xs);font-weight:700;' +
                    'white-space:nowrap">' + escHtml(p.status) + '</span>'
                : '') +
            '</div>' +

            // Meta row: capability + lead nations + score impact
            '<div style="display:flex;flex-wrap:wrap;gap:var(--space-3);' +
              'margin-bottom:var(--space-2);font-size:var(--text-xs)">' +
              (p.capability_area
                ? '<span style="color:var(--color-text-muted)">Capability: ' +
                    '<strong style="color:var(--color-text-secondary)">' +
                    escHtml(p.capability_area) + '</strong></span>'
                : '') +
              (leadNations
                ? '<span style="color:var(--color-text-muted)">Lead: ' +
                    '<strong style="color:var(--color-text-secondary)">' +
                    escHtml(leadNations) + '</strong></span>'
                : '') +
              (p.score_impact ? scoreBadge(p.score_impact) : '') +
            '</div>' +

            // Budget line
            (p.budget_committed || p.budget_disbursed
              ? '<div style="font-size:var(--text-xs);color:var(--color-text-muted);' +
                  'margin-bottom:var(--space-2)">' +
                  (p.budget_committed
                    ? '<span>Committed: <strong style="color:var(--color-text-secondary)">' +
                        escHtml(String(p.budget_committed)) + '</strong></span>'
                    : '') +
                  (p.budget_committed && p.budget_disbursed ? '  ' : '') +
                  (p.budget_disbursed
                    ? '<span>Disbursed: <strong style="color:var(--positive,#4caf7d)">' +
                        escHtml(String(p.budget_disbursed)) + '</strong></span>'
                    : '') +
                '</div>'
              : '') +

            // Update this week
            (p.update_this_week
              ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);' +
                  'line-height:1.5;border-top:1px solid var(--color-border,rgba(255,255,255,.07));' +
                  'padding-top:var(--space-2);margin-top:var(--space-2)">' +
                  escHtml(p.update_this_week) +
                '</div>'
              : '') +

          '</div>' +
        '</div>';
    });

    html += '</div>';
    el.innerHTML = html;
  }


  /* ── Generic Radar Chart ────────────────────────────────────
   * renderRadarChart(config, targetId)
   *
   * Renders a Chart.js radar with side-by-side bar list.
   * Works for any dataset — Lagrange scores, threat dimensions,
   * capability assessments, etc.
   *
   * config: {
   *   title:      string — section heading (optional)
   *   subtitle:   string — description text (optional)
   *   badge:      string — large centre value e.g. "~35%" (optional)
   *   badgeLabel: string — small label below badge (optional)
   *   accent:     string — CSS colour, defaults to var(--monitor-accent)
   *   dimensions: [
   *     { label: 'Energy Independence', score: 52, note: 'Russian gas...' },
   *     ...
   *   ]
   * }
   */
  function renderRadarChart(config, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    var dims = config.dimensions || [];
    if (!dims.length) {
      el.innerHTML = '<p class="text-muted text-sm">No radar data available.</p>';
      return;
    }

    var accent = config.accent || 'var(--monitor-accent,#5b8db0)';
    var accentRaw = config.accent || '#5b8db0';
    var canvasId = 'radar-canvas-' + targetId;
    var dimListId = 'radar-dim-list-' + targetId;

    // Radar CSS is now in base.css (Sprint 1 D1 migration) — no inline injection needed.

    // Build HTML
    var html = '';
    if (config.badge) {
      html +=
        '<div class="asym-radar-badge">' +
          '<div class="asym-radar-badge__value" style="color:' + accentRaw + '">' + escHtml(config.badge) + '</div>' +
          (config.badgeLabel ? '<div class="asym-radar-badge__label">' + escHtml(config.badgeLabel) + '</div>' : '') +
        '</div>';
    }

    html +=
      '<div class="asym-radar-wrap">' +
        '<div class="asym-chart-wrap asym-chart-wrap--square">' +
          '<canvas id="' + canvasId + '" aria-label="' + escHtml(config.title || 'Radar Chart') + '" role="img"></canvas>' +
        '</div>' +
        '<div class="asym-radar-dim-list" id="' + dimListId + '"></div>' +
      '</div>';
    el.innerHTML = html;

    // Build bar list
    var dimListEl = document.getElementById(dimListId);
    var barsHtml = '';
    dims.forEach(function(d) {
      var score = parseFloat(d.score || 0);
      var barColor = score >= 50 ? 'var(--positive,#4caf7d)' : score >= 30 ? accentRaw : 'var(--high,#d97706)';
      barsHtml +=
        '<div class="asym-radar-dim-row">' +
          '<div>' +
            '<div class="asym-radar-dim-row__label">' + escHtml(d.label || '') + '</div>' +
            (d.note ? '<div class="asym-radar-dim-row__note">' + escHtml(d.note) + '</div>' : '') +
          '</div>' +
          '<div class="asym-radar-dim-row__score" style="color:' + barColor + '">' + escHtml(String(d.score != null ? d.score : '—')) + '</div>' +
          '<div class="asym-radar-dim-row__bar-wrap">' +
            '<div class="asym-radar-dim-row__bar" style="width:' + Math.min(score, 100) + '%;background:' + barColor + '"></div>' +
          '</div>' +
        '</div>';
    });
    if (dimListEl) dimListEl.innerHTML = barsHtml;

    // Draw Chart.js radar
    var radarCanvas = document.getElementById(canvasId);
    if (!radarCanvas || typeof Chart === 'undefined') return;

    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    var labelColor = isDark ? 'rgba(224,223,220,0.85)' : 'rgba(26,25,23,0.75)';
    var gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)';
    var labels = dims.map(function(d) { return d.label || ''; });
    var scores = dims.map(function(d) { return parseFloat(d.score || 0); });
    var maxVal = config.max || 100;

    var chart = new Chart(radarCanvas.getContext('2d'), {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: config.title || 'Score',
          data: scores,
          backgroundColor: (accentRaw + '30'),
          borderColor: accentRaw,
          borderWidth: 2,
          pointBackgroundColor: accentRaw,
          pointBorderColor: isDark ? '#1e1d1b' : '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { top: 20, bottom: 25, left: 50, right: 50 } },
        animation: { duration: 700, easing: 'easeInOutQuart' },
        scales: {
          r: {
            min: 0,
            max: maxVal,
            ticks: {
              stepSize: maxVal / 4,
              color: labelColor,
              backdropColor: 'transparent',
              font: { size: 11 }
            },
            grid: { color: gridColor },
            angleLines: { color: gridColor },
            pointLabels: {
              color: labelColor,
              font: { size: 12, weight: '600' },
              padding: 12
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                return ' ' + ctx.parsed.r + ' / ' + maxVal;
              }
            }
          }
        }
      }
    });

    // Theme toggle listener
    var themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', function() {
        setTimeout(function() {
          var dark = document.documentElement.getAttribute('data-theme') === 'dark';
          var lc = dark ? 'rgba(224,223,220,0.85)' : 'rgba(26,25,23,0.75)';
          var gc = dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)';
          chart.options.scales.r.ticks.color = lc;
          chart.options.scales.r.pointLabels.color = lc;
          chart.options.scales.r.grid.color = gc;
          chart.options.scales.r.angleLines.color = gc;
          chart.data.datasets[0].pointBorderColor = dark ? '#1e1d1b' : '#ffffff';
          chart.update();
        }, 80);
      });
    }
  }


  /* ── Public API ─────────────────────────────────────────────── */

  // ── ERM: Policy, Law & Compliance (F2 Regulatory Vacuum) ──────────────
  function renderPolicyLawCompliance(items, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!items || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">No policy or regulatory data available.</p>';
      return;
    }
    var STATUS_COLORS = {
      'In force':     { bg: '#22c55e20', text: '#22c55e', border: '#22c55e' },
      'Proposed':     { bg: '#2563eb20', text: '#60a5fa', border: '#2563eb' },
      'Under review': { bg: '#d9770620', text: '#fbbf24', border: '#d97706' },
      'Withdrawn':    { bg: '#dc262620', text: '#f87171', border: '#dc2626' },
      'Unenforced':   { bg: '#ef444420', text: '#f87171', border: '#ef4444' }
    };
    var html = '<div style="display:flex;flex-direction:column;gap:var(--space-3)">';
    items.forEach(function (p) {
      var sc = STATUS_COLORS[p.status] || { bg: 'rgba(255,255,255,.05)', text: 'var(--color-text-muted)', border: 'var(--color-border)' };
      html +=
        '<div style="padding:var(--space-3) var(--space-4);border-left:3px solid ' + sc.border + ';background:var(--color-surface);border-radius:var(--radius-sm)">' +
          '<div style="display:flex;flex-wrap:wrap;gap:var(--space-2);align-items:center;margin-bottom:var(--space-2)">' +
            '<span style="font-size:var(--text-sm);font-weight:600">' + escHtml(p.item || '') + '</span>' +
            '<span style="font-size:var(--text-xs);padding:1px 6px;border-radius:3px;background:' + sc.bg + ';color:' + sc.text + ';border:1px solid ' + sc.border + '">' + escHtml(p.status || '') + '</span>' +
            (p.filter_tag ? '<span style="font-size:var(--text-min);padding:1px 5px;border-radius:2px;background:rgba(239,68,68,0.1);color:#f87171;font-family:var(--font-mono)">' + escHtml(p.filter_tag) + '</span>' : '') +
          '</div>' +
          '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-bottom:var(--space-1)">' +
            escHtml(p.jurisdiction || '') +
            (p.type ? ' · ' + escHtml(p.type) : '') +
          '</div>' +
          (p.governance_gap ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;margin-bottom:var(--space-1)"><strong style="font-weight:600;color:var(--color-text-body)">Gap:</strong> ' + escHtml(p.governance_gap) + '</div>' : '') +
          (p.root_cause ? '<div style="font-size:var(--text-min);color:var(--color-text-muted)">Root cause: ' + escHtml(p.root_cause) + '</div>' : '') +
          (p.source ? '<div style="margin-top:var(--space-1);font-size:var(--text-min);color:var(--color-text-muted)">' + escHtml(p.source) + '</div>' : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  // ── ERM: ICJ Climate Advisory Opinion — Standing Tracker ─────────────
  function renderICJTracker(tracker, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!tracker || typeof tracker !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">No ICJ tracker data available.</p>';
      return;
    }
    var STATUS_COLORS = {
      'Pending':                  { bg: '#d9770620', text: '#fbbf24', icon: '⏳' },
      'Hearings':                 { bg: '#2563eb20', text: '#60a5fa', icon: '⚖️' },
      'Deliberation':             { bg: '#7c3aed20', text: '#a78bfa', icon: '🔍' },
      'Advisory opinion issued':  { bg: '#22c55e20', text: '#22c55e', icon: '✓' }
    };
    var sc = STATUS_COLORS[tracker.status] || { bg: 'rgba(255,255,255,.05)', text: 'var(--color-text-muted)', icon: '—' };
    var html =
      '<div style="padding:var(--space-4);background:var(--color-surface);border:1px solid var(--color-border-subtle);border-radius:var(--radius-md)">' +
        '<div style="display:flex;align-items:center;gap:var(--space-3);margin-bottom:var(--space-3)">' +
          '<span style="font-size:1.25rem">' + sc.icon + '</span>' +
          '<span style="font-size:var(--text-sm);font-weight:600">ICJ Climate Advisory Opinion</span>' +
          '<span style="font-size:var(--text-xs);padding:2px 8px;border-radius:3px;background:' + sc.bg + ';color:' + sc.text + '">' + escHtml(tracker.status || '') + '</span>' +
        '</div>' +
        (tracker.last_development ? '<div style="font-size:var(--text-xs);line-height:1.55;margin-bottom:var(--space-2)">' + escHtml(tracker.last_development) + '</div>' : '') +
        (tracker.last_development_date ? '<div style="font-size:var(--text-min);color:var(--color-text-muted);margin-bottom:var(--space-2)">Last development: ' + escHtml(tracker.last_development_date) + '</div>' : '') +
        (tracker.next_milestone ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-bottom:var(--space-2)"><strong style="font-weight:600">Next:</strong> ' + escHtml(tracker.next_milestone) + '</div>' : '') +
        (tracker.significance ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;padding-top:var(--space-2);border-top:1px solid var(--color-border-subtle)">' + escHtml(tracker.significance) + '</div>' : '') +
        (tracker.source_url ? '<div style="margin-top:var(--space-2)"><a class="source-link" style="font-size:var(--text-min)" href="' + escHtml(tracker.source_url) + '" target="_blank" rel="noopener">ICJ Case 187 →</a></div>' : '') +
      '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Loss & Damage Finance Mechanism — Standing Tracker ──────────
  function renderLossDamageTracker(tracker, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!tracker || typeof tracker !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">No loss and damage tracker data available.</p>';
      return;
    }
    var committed = tracker.committed_usd || 0;
    var disbursed = tracker.disbursed_usd || 0;
    var ratio = tracker.disbursement_ratio != null ? tracker.disbursement_ratio : (committed > 0 ? disbursed / committed : 0);
    var pct = Math.round(ratio * 100);
    var barColor = pct < 25 ? '#dc2626' : pct < 50 ? '#d97706' : pct < 75 ? '#2563eb' : '#22c55e';

    function fmtUSD(n) {
      if (n >= 1e9) return '$' + (n / 1e9).toFixed(1) + 'B';
      if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M';
      if (n >= 1e3) return '$' + (n / 1e3).toFixed(0) + 'K';
      return '$' + n;
    }

    var html =
      '<div style="padding:var(--space-4);background:var(--color-surface);border:1px solid var(--color-border-subtle);border-radius:var(--radius-md)">' +
        '<div style="display:flex;align-items:center;gap:var(--space-3);margin-bottom:var(--space-3)">' +
          '<span style="font-size:var(--text-sm);font-weight:600">Loss & Damage Finance Mechanism</span>' +
          '<span style="font-size:var(--text-xs);padding:2px 8px;border-radius:3px;background:rgba(76,175,125,0.1);color:#4caf7d">' + escHtml(tracker.mechanism_status || '') + '</span>' +
          (tracker.filter_tag ? '<span style="font-size:var(--text-min);padding:1px 5px;border-radius:2px;background:rgba(239,68,68,0.1);color:#f87171;font-family:var(--font-mono)">' + escHtml(tracker.filter_tag) + '</span>' : '') +
        '</div>' +
        // Disbursement bar
        '<div style="margin-bottom:var(--space-3)">' +
          '<div style="display:flex;justify-content:space-between;font-size:var(--text-xs);margin-bottom:var(--space-1)">' +
            '<span>Disbursed: ' + fmtUSD(disbursed) + '</span>' +
            '<span>Committed: ' + fmtUSD(committed) + '</span>' +
          '</div>' +
          '<div style="height:20px;background:rgba(100,116,139,0.08);border-radius:10px;overflow:hidden">' +
            '<div style="width:' + pct + '%;height:100%;background:' + barColor + ';border-radius:10px;opacity:0.85;transition:width 0.4s"></div>' +
          '</div>' +
          '<div style="text-align:center;font-size:var(--text-xs);font-weight:600;color:' + barColor + ';margin-top:var(--space-1)">' + pct + '% disbursed</div>' +
        '</div>' +
        (tracker.compliance_cycle ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-bottom:var(--space-2)"><strong style="font-weight:600">Compliance cycle:</strong> ' + escHtml(tracker.compliance_cycle) + '</div>' : '') +
        (tracker.key_development ? '<div style="font-size:var(--text-xs);line-height:1.55;margin-bottom:var(--space-2)">' + escHtml(tracker.key_development) + '</div>' : '') +
        (tracker.source ? '<div style="font-size:var(--text-min);color:var(--color-text-muted)">' + escHtml(tracker.source) + '</div>' : '') +
      '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Attribution Gap Cases (F4) ──────────────────────────────────
  function renderAttributionGapCases(cases, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!cases || !cases.length) {
      el.innerHTML = '<p class="text-muted text-sm">No attribution gap data available.</p>';
      return;
    }
    var GOV_COLORS = {
      'No binding framework': { bg: '#dc262615', border: '#dc2626', text: '#f87171' },
      'Framework contested':  { bg: '#d9770615', border: '#d97706', text: '#fbbf24' },
      'Framework unenforced': { bg: '#ef444415', border: '#ef4444', text: '#fb923c' }
    };
    var html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:var(--space-3)">';
    cases.forEach(function (c) {
      var gc = GOV_COLORS[c.governance_status] || { bg: 'rgba(255,255,255,.05)', border: 'var(--color-border)', text: 'var(--color-text-muted)' };
      html +=
        '<div style="padding:var(--space-3) var(--space-4);border:1px solid ' + gc.border + ';border-radius:var(--radius-md);background:' + gc.bg + '">' +
          '<div style="font-size:var(--text-sm);font-weight:600;margin-bottom:var(--space-2)">' + escHtml(c.case || c['case'] || '') + '</div>' +
          '<div style="font-size:var(--text-xs);margin-bottom:var(--space-2)">' +
            '<span style="padding:1px 6px;border-radius:3px;background:' + gc.bg + ';color:' + gc.text + ';border:1px solid ' + gc.border + '">' + escHtml(c.governance_status || '') + '</span>' +
            (c.filter_tag ? ' <span style="font-size:var(--text-min);padding:1px 5px;border-radius:2px;background:rgba(239,68,68,0.1);color:#f87171;font-family:var(--font-mono)">' + escHtml(c.filter_tag) + '</span>' : '') +
          '</div>' +
          (c.key_metric ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;margin-bottom:var(--space-1)"><em>' + escHtml(c.key_metric) + '</em></div>' : '') +
          (c.this_week_development ? '<div style="font-size:var(--text-xs);line-height:1.5">' + escHtml(c.this_week_development) + '</div>' : '<div style="font-size:var(--text-min);color:var(--color-text-muted);font-style:italic">No new development this week</div>') +
          (c.source ? '<div style="margin-top:var(--space-2);font-size:var(--text-min);color:var(--color-text-muted)">' + escHtml(c.source) + '</div>' : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Reverse Cascade Check (FM-ERM-04) ──────────────────────────
  function renderReverseCascadeCheck(check, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!check || typeof check !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">No reverse cascade check data available.</p>';
      return;
    }
    var isPositive = check.accelerates_boundary === true;
    var borderColor = isPositive ? '#dc2626' : '#22c55e';
    var bgColor = isPositive ? 'rgba(220,38,38,0.05)' : 'rgba(34,197,94,0.05)';
    var statusLabel = isPositive ? 'CASCADE CONFIRMED' : 'No cascade detected';
    var statusColor = isPositive ? '#f87171' : '#4ade80';

    var html =
      '<div style="padding:var(--space-4);border-left:3px solid ' + borderColor + ';background:' + bgColor + ';border-radius:var(--radius-sm)">' +
        '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-2)">' +
          '<span style="font-size:var(--text-min);font-weight:700;padding:2px 8px;border-radius:3px;background:' + (isPositive ? 'rgba(220,38,38,0.15)' : 'rgba(34,197,94,0.15)') + ';color:' + statusColor + '">' + statusLabel + '</span>' +
          '<span style="font-size:var(--text-min);color:var(--color-text-muted);font-family:var(--font-mono)">FM-ERM-04</span>' +
        '</div>' +
        (check.geopolitical_event ? '<div style="font-size:var(--text-xs);margin-bottom:var(--space-2)"><strong style="font-weight:600">Event checked:</strong> ' + escHtml(check.geopolitical_event) + '</div>' : '') +
        (isPositive && check.affected_boundary ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-bottom:var(--space-1)"><strong style="font-weight:600;color:#f87171">Affected boundary:</strong> ' + escHtml(check.affected_boundary) + '</div>' : '') +
        (check.cascade_description ? '<div style="font-size:var(--text-xs);line-height:1.55;margin-bottom:var(--space-2)">' + escHtml(check.cascade_description) + '</div>' : '') +
        (check.note ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;font-style:italic">' + escHtml(check.note) + '</div>' : '') +
      '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Regional Coverage (FM-ERM-02 Compliance) ────────────────────
  function renderRegionalCoverage(coverage, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!coverage || typeof coverage !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">No regional coverage data available.</p>';
      return;
    }
    var regions = [
      { key: 'sub_saharan_africa_items', label: 'Sub-Saharan Africa', icon: '🌍' },
      { key: 'mena_items', label: 'MENA', icon: '🏜️' },
      { key: 'south_asia_items', label: 'South Asia', icon: '🌏' },
      { key: 'ocean_systems_items', label: 'Ocean Systems', icon: '🌊' }
    ];
    var met = coverage.fm_erm_02_met === true;
    var metColor = met ? '#22c55e' : '#dc2626';
    var metBg = met ? 'rgba(34,197,94,0.1)' : 'rgba(220,38,38,0.1)';

    var html =
      '<div style="padding:var(--space-4);background:var(--color-surface);border:1px solid var(--color-border-subtle);border-radius:var(--radius-md)">' +
        '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-3)">' +
          '<span style="font-size:var(--text-min);font-weight:700;padding:2px 8px;border-radius:3px;background:' + metBg + ';color:' + metColor + '">' + (met ? 'FM-ERM-02 MET' : 'FM-ERM-02 NOT MET') + '</span>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:var(--space-3);text-align:center">';
    regions.forEach(function (r) {
      var count = coverage[r.key] || 0;
      html +=
        '<div>' +
          '<div style="font-size:1.25rem;margin-bottom:var(--space-1)">' + r.icon + '</div>' +
          '<div style="font-size:var(--text-lg);font-weight:700;color:' + (count > 0 ? '#4caf7d' : 'var(--color-text-muted)') + '">' + count + '</div>' +
          '<div style="font-size:var(--text-min);color:var(--color-text-muted)">' + r.label + '</div>' +
        '</div>';
    });
    html += '</div>' +
        (coverage.note ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;margin-top:var(--space-3);padding-top:var(--space-2);border-top:1px solid var(--color-border-subtle)">' + escHtml(coverage.note) + '</div>' : '') +
      '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Extreme Events Log ──────────────────────────────────────────
  function renderExtremeEventsLog(events, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!events || !events.length) {
      el.innerHTML = '<p class="text-muted text-sm">No extreme events logged this issue.</p>';
      return;
    }
    var SEV_COLORS = {
      'Moderate':        { bg: '#2563eb20', text: '#60a5fa', border: '#2563eb' },
      'Severe':          { bg: '#d9770620', text: '#fbbf24', border: '#d97706' },
      'Extreme':         { bg: '#ef444420', text: '#fb923c', border: '#ef4444' },
      'Record-breaking': { bg: '#dc262620', text: '#f87171', border: '#dc2626' }
    };
    var html = '<div style="display:flex;flex-direction:column;gap:var(--space-3)">';
    events.forEach(function (evt) {
      var sc = SEV_COLORS[evt.severity] || { bg: 'rgba(255,255,255,.05)', text: 'var(--color-text-muted)', border: 'var(--color-border)' };
      var filterBadges = '';
      if (evt.filter_tags && evt.filter_tags.length) {
        evt.filter_tags.forEach(function (ft) {
          if (ft) filterBadges += '<span style="font-size:var(--text-min);padding:1px 5px;border-radius:2px;background:rgba(239,68,68,0.1);color:#f87171;font-family:var(--font-mono);margin-left:var(--space-1)">' + escHtml(ft) + '</span>';
        });
      }
      html +=
        '<div style="padding:var(--space-3) var(--space-4);border-left:3px solid ' + sc.border + ';background:var(--color-surface);border-radius:var(--radius-sm)">' +
          '<div style="display:flex;flex-wrap:wrap;gap:var(--space-2);align-items:center;margin-bottom:var(--space-2)">' +
            '<span style="font-size:var(--text-xs);padding:1px 6px;border-radius:3px;background:' + sc.bg + ';color:' + sc.text + '">' + escHtml(evt.severity || '') + '</span>' +
            '<span style="font-size:var(--text-sm);font-weight:600">' + escHtml(evt.event_type || '') + '</span>' +
            '<span style="font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(evt.location || '') + '</span>' +
            filterBadges +
          '</div>' +
          // Non-linear departure test (FM-ERM-01)
          (evt.non_linear_test_result ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-bottom:var(--space-1)"><span style="font-family:var(--font-mono);font-size:var(--text-min);color:var(--color-text-muted)">FM-ERM-01:</span> ' + escHtml(evt.non_linear_test_result) + (evt.non_linear_departure ? ' <span style="color:#f87171;font-weight:600">NON-LINEAR</span>' : '') + '</div>' : '') +
          (evt.geopolitical_implication ? '<div style="font-size:var(--text-xs);line-height:1.55">' + escHtml(evt.geopolitical_implication) + '</div>' : '') +
          (evt.conflict_nexus && evt.conflict_nexus_note ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);margin-top:var(--space-1)"><strong style="font-weight:600;color:#d97706">Conflict nexus:</strong> ' + escHtml(evt.conflict_nexus_note) + '</div>' : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Climate Security Nexus (Threat Multiplier) ──────────────────
  function renderClimateSecurityNexus(items, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!items || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">No climate-security nexus data available.</p>';
      return;
    }
    var SEV_COLORS = {
      'Emerging':  { bg: '#2563eb20', text: '#60a5fa', border: '#2563eb' },
      'Moderate':  { bg: '#d9770620', text: '#fbbf24', border: '#d97706' },
      'Severe':    { bg: '#ef444420', text: '#fb923c', border: '#ef4444' },
      'Critical':  { bg: '#dc262620', text: '#f87171', border: '#dc2626' }
    };
    var html = '<div style="display:flex;flex-direction:column;gap:var(--space-3)">';
    items.forEach(function (item) {
      var sc = SEV_COLORS[item.severity] || { bg: 'rgba(255,255,255,.05)', text: 'var(--color-text-muted)', border: 'var(--color-border)' };
      html +=
        '<div style="padding:var(--space-3) var(--space-4);border-left:3px solid ' + sc.border + ';background:var(--color-surface);border-radius:var(--radius-sm)">' +
          '<div style="display:flex;flex-wrap:wrap;gap:var(--space-2);align-items:center;margin-bottom:var(--space-2)">' +
            '<span style="font-size:var(--text-xs);padding:1px 6px;border-radius:3px;background:' + sc.bg + ';color:' + sc.text + '">' + escHtml(item.severity || '') + '</span>' +
            '<span style="font-size:var(--text-sm);font-weight:600">' + escHtml(item.risk_type || '') + '</span>' +
            '<span style="font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(item.region || '') + '</span>' +
          '</div>' +
          (item.cascade_chain ? '<div style="font-size:var(--text-xs);line-height:1.55;margin-bottom:var(--space-2)"><strong style="font-weight:600;color:var(--color-text-body)">Cascade:</strong> ' + escHtml(item.cascade_chain) + '</div>' : '') +
          (item.conflict_link ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary)"><strong style="font-weight:600">Conflict link:</strong> ' + escHtml(item.conflict_link) + '</div>' : '') +
          (item.scem_link ? '<div style="font-size:var(--text-min);color:var(--color-text-muted);margin-top:var(--space-1)">SCEM: ' + escHtml(item.scem_link) + '</div>' : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  // ── ERM: Planetary Status Snapshot (header KPI card) ─────────────────
  function renderPlanetaryStatusSnapshot(snapshot, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!snapshot || typeof snapshot !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">No planetary status data available.</p>';
      return;
    }
    var deltaColor = snapshot.status_delta_this_week === 'Deteriorating' ? '#f87171' :
                     snapshot.status_delta_this_week === 'Improving' ? '#4ade80' : 'var(--color-text-muted)';
    var html =
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:var(--space-3);margin-bottom:var(--space-3)">' +
        '<div style="text-align:center;padding:var(--space-3);background:rgba(220,38,38,0.08);border-radius:var(--radius-md)">' +
          '<div style="font-size:var(--text-2xl);font-weight:700;color:#f87171">' + (snapshot.boundaries_exceeded || 0) + '</div>' +
          '<div style="font-size:var(--text-min);color:var(--color-text-muted)">Beyond Boundary</div>' +
        '</div>' +
        '<div style="text-align:center;padding:var(--space-3);background:rgba(239,68,68,0.06);border-radius:var(--radius-md)">' +
          '<div style="font-size:var(--text-2xl);font-weight:700;color:#fb923c">' + (snapshot.boundaries_high_risk || 0) + '</div>' +
          '<div style="font-size:var(--text-min);color:var(--color-text-muted)">High Risk</div>' +
        '</div>' +
        '<div style="text-align:center;padding:var(--space-3);background:rgba(217,119,6,0.06);border-radius:var(--radius-md)">' +
          '<div style="font-size:var(--text-2xl);font-weight:700;color:#fbbf24">' + (snapshot.boundaries_increasing_risk || 0) + '</div>' +
          '<div style="font-size:var(--text-min);color:var(--color-text-muted)">Increasing Risk</div>' +
        '</div>' +
        '<div style="text-align:center;padding:var(--space-3);background:rgba(34,197,94,0.06);border-radius:var(--radius-md)">' +
          '<div style="font-size:var(--text-2xl);font-weight:700;color:#4ade80">' + (snapshot.boundaries_safe || 0) + '</div>' +
          '<div style="font-size:var(--text-min);color:var(--color-text-muted)">Safe</div>' +
        '</div>' +
      '</div>' +
      '<div style="display:flex;align-items:center;gap:var(--space-2)">' +
        '<span style="font-size:var(--text-xs);color:' + deltaColor + ';font-weight:600">' + escHtml(snapshot.status_delta_this_week || 'Stable') + '</span>' +
      '</div>' +
      (snapshot.lead_signal ? '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.55;margin-top:var(--space-2)">' + escHtml(snapshot.lead_signal) + '</div>' : '');
    el.innerHTML = html;
  }

  // ── GMM / Cross-Monitor Reusable Sections ──────────────────────────────

  function renderScenarioFramework(scenarios, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(scenarios) || !scenarios.length) {
      el.innerHTML = '<p class="text-muted text-sm">Scenario framework data will appear after the next publish cycle.</p>';
      return;
    }
    var html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:var(--space-4)">';
    scenarios.forEach(function(s) {
      var pct = s.probability_pct != null ? s.probability_pct : (s.probability != null ? Math.round(s.probability * 100) : '—');
      var deltaHtml = '';
      if (s.probability_delta) {
        var isNeg = String(s.probability_delta).indexOf('-') === 0;
        var deltaCls = isNeg ? 'color:var(--color-critical,#ef4444)' : 'color:var(--color-green,#22c55e)';
        deltaHtml = '<span style="font-size:var(--text-xs);' + deltaCls + ';margin-left:var(--space-2)">' + escHtml(s.probability_delta) + '</span>';
      }
      var chipsHtml = '';
      if (Array.isArray(s.affected_asset_classes) && s.affected_asset_classes.length) {
        chipsHtml = '<div style="display:flex;flex-wrap:wrap;gap:var(--space-1);margin-top:var(--space-3)">' +
          s.affected_asset_classes.map(function(ac) {
            return '<span style="font-size:var(--text-xs);padding:2px 8px;border-radius:var(--radius-sm);background:var(--surface-3,rgba(255,255,255,0.06));color:var(--color-text-secondary)">' + escHtml(ac) + '</span>';
          }).join('') + '</div>';
      }
      html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4);border-left:3px solid var(--monitor-accent,#22a0aa)">' +
        '<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:var(--space-2)">' +
          '<div style="font-weight:600;font-size:var(--text-sm)">' + escHtml(s.scenario || s.label || '') + '</div>' +
          '<div style="font-size:var(--text-lg);font-weight:700;font-family:var(--font-mono);color:var(--monitor-accent,#22a0aa)">' + escHtml(String(pct)) + '%' + deltaHtml + '</div>' +
        '</div>' +
        '<div style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.55;margin-bottom:var(--space-2)">' + escHtml(s.description || '') + '</div>' +
        (s.key_trigger ? '<div style="font-size:var(--text-xs);font-style:italic;color:var(--color-text-muted)"><strong>Trigger:</strong> ' + escHtml(s.key_trigger) + '</div>' : '') +
        chipsHtml +
      '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  function renderPositioningOverlay(overlay, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!overlay || typeof overlay !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">Positioning overlay data will appear after the next publish cycle.</p>';
      return;
    }
    var html = '';

    // Fed Funds Futures sub-section
    var fff = overlay.fed_funds_futures;
    if (fff && typeof fff === 'object') {
      var pzc = fff.prob_zero_cuts_2026 != null ? Math.round(fff.prob_zero_cuts_2026 * 100) : null;
      html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4);margin-bottom:var(--space-4)">' +
        '<div style="font-weight:600;font-size:var(--text-sm);margin-bottom:var(--space-3)">Fed Funds Futures</div>' +
        '<div style="display:flex;gap:var(--space-6);flex-wrap:wrap">' +
          '<div><div style="font-size:var(--text-xs);color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.05em">Implied Cuts 2026</div>' +
            '<div style="font-size:var(--text-lg);font-weight:700;font-family:var(--font-mono)">' + escHtml(String(fff.implied_cuts_2026 != null ? fff.implied_cuts_2026 : '—')) + '</div></div>' +
          (pzc != null ? '<div><div style="font-size:var(--text-xs);color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.05em">P(Zero Cuts)</div>' +
            '<div style="font-size:var(--text-lg);font-weight:700;font-family:var(--font-mono)">' + pzc + '%</div></div>' : '') +
          (fff.source ? '<div style="align-self:flex-end;font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(fff.source) + '</div>' : '') +
        '</div></div>';
    }

    // MATT Framework sub-section
    var matt = overlay.matt_framework;
    if (Array.isArray(matt) && matt.length) {
      html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4);margin-bottom:var(--space-4)">' +
        '<div style="font-weight:600;font-size:var(--text-sm);margin-bottom:var(--space-3)">MATT Framework — Market Agreement to Themes</div>' +
        '<div style="overflow-x:auto"><table style="width:100%;font-size:var(--text-sm);border-collapse:collapse">' +
        '<thead><tr style="border-bottom:1px solid var(--color-border)">' +
          '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Theme</th>' +
          '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Score</th>' +
          '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Market Pricing</th>' +
          '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Our View</th>' +
          '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Alpha</th>' +
        '</tr></thead><tbody>';
      matt.forEach(function(m) {
        var sc = m.matt_score || 0;
        var barW = Math.min(Math.max(sc, 0), 10) * 10;
        var barColor = sc <= 3 ? 'var(--color-green,#22c55e)' : sc <= 6 ? 'var(--color-amber,#f59e0b)' : 'var(--color-critical,#ef4444)';
        html += '<tr style="border-bottom:1px solid var(--color-border)">' +
          '<td style="padding:var(--space-2);font-weight:500">' + escHtml(m.theme || '') + '</td>' +
          '<td style="padding:var(--space-2);text-align:center"><div style="display:flex;align-items:center;gap:var(--space-2);justify-content:center">' +
            '<div style="width:60px;height:6px;border-radius:3px;background:var(--surface-3,rgba(255,255,255,0.08));overflow:hidden">' +
              '<div style="width:' + barW + '%;height:100%;border-radius:3px;background:' + barColor + '"></div>' +
            '</div>' +
            '<span style="font-family:var(--font-mono);font-size:var(--text-xs)">' + escHtml(String(sc)) + '</span>' +
          '</div></td>' +
          '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary)">' + escHtml(m.market_pricing || '') + '</td>' +
          '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary)">' + escHtml(m.our_assessment || '') + '</td>' +
          '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--monitor-accent,#22a0aa);font-weight:500">' + escHtml(m.alpha_signal || '—') + '</td>' +
        '</tr>';
      });
      html += '</tbody></table></div></div>';
    }

    // Contrarian Corner sub-section
    var cc = overlay.contrarian_corner;
    if (Array.isArray(cc) && cc.length) {
      html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4)">' +
        '<div style="font-weight:600;font-size:var(--text-sm);margin-bottom:var(--space-3)">Contrarian Corner</div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:var(--space-3)">';
      cc.forEach(function(c) {
        html += '<div style="padding:var(--space-3);border-left:3px solid var(--color-amber,#f59e0b);background:var(--surface-3,rgba(255,255,255,0.04));border-radius:var(--radius-sm)">' +
          '<div style="font-size:var(--text-xs);font-weight:600;color:var(--color-amber,#f59e0b);margin-bottom:var(--space-1)">' + escHtml(c.source || '') + '</div>' +
          '<div style="font-size:var(--text-sm);font-weight:500;margin-bottom:var(--space-2)">' + escHtml(c.view || '') + '</div>' +
          '<div style="font-size:var(--text-xs);color:var(--color-text-muted);font-style:italic">Correct if: ' + escHtml(c.scenario_under_which_correct || '') + '</div>' +
        '</div>';
      });
      html += '</div></div>';
    }

    if (!html) {
      el.innerHTML = '<p class="text-muted text-sm">Positioning overlay data will appear after the next publish cycle.</p>';
      return;
    }
    el.innerHTML = html;
  }

  function renderCentralBankTracker(banks, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(banks) || !banks.length) {
      el.innerHTML = '<p class="text-muted text-sm">Central bank tracker data will appear after the next publish cycle.</p>';
      return;
    }
    var postureColor = function(p) {
      if (!p) return '';
      var lp = p.toLowerCase();
      if (lp === 'easing' || lp === 'emergency') return 'var(--color-green,#22c55e)';
      if (lp === 'tightening') return 'var(--color-critical,#ef4444)';
      return 'var(--color-amber,#f59e0b)';
    };
    var html = '<div style="overflow-x:auto"><table style="width:100%;font-size:var(--text-sm);border-collapse:collapse">' +
      '<thead><tr style="border-bottom:1px solid var(--color-border)">' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Institution</th>' +
        '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Posture</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Last Action</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Next Meeting</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Guidance</th>' +
      '</tr></thead><tbody>';
    banks.forEach(function(b) {
      html += '<tr style="border-bottom:1px solid var(--color-border)">' +
        '<td style="padding:var(--space-2);font-weight:600">' + escHtml(b.institution || '') + '</td>' +
        '<td style="padding:var(--space-2);text-align:center"><span style="font-size:var(--text-xs);padding:2px 8px;border-radius:var(--radius-sm);background:' + postureColor(b.posture) + '20;color:' + postureColor(b.posture) + ';font-weight:600">' + escHtml(b.posture || '—') + '</span></td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary)">' + escHtml(b.last_action || '—') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);font-family:var(--font-mono)">' + escHtml(b.next_meeting ? b.next_meeting.slice(0,10) : '—') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary);max-width:280px">' + escHtml(b.forward_guidance || '—') + '</td>' +
      '</tr>';
    });
    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  function renderTariffTracker(tariffs, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(tariffs) || !tariffs.length) {
      el.innerHTML = '<p class="text-muted text-sm">No active tariff measures tracked this issue.</p>';
      return;
    }
    var statusColor = function(s) {
      if (!s) return '';
      var ls = s.toLowerCase();
      if (ls === 'in force') return 'var(--color-critical,#ef4444)';
      if (ls === 'announced') return 'var(--color-amber,#f59e0b)';
      if (ls === 'suspended') return 'var(--color-green,#22c55e)';
      if (ls === 'retaliated') return 'var(--color-orange,#f97316)';
      return 'var(--color-text-muted)';
    };
    var html = '<div style="overflow-x:auto"><table style="width:100%;font-size:var(--text-sm);border-collapse:collapse">' +
      '<thead><tr style="border-bottom:1px solid var(--color-border)">' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Actor</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Target</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Measure</th>' +
        '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Status</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Eff. Date</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Impact</th>' +
      '</tr></thead><tbody>';
    tariffs.forEach(function(t) {
      html += '<tr style="border-bottom:1px solid var(--color-border)">' +
        '<td style="padding:var(--space-2);font-weight:500">' + escHtml(t.actor || '') + '</td>' +
        '<td style="padding:var(--space-2)">' + escHtml(t.target || '') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs)">' + escHtml(t.measure || '') + '</td>' +
        '<td style="padding:var(--space-2);text-align:center"><span style="font-size:var(--text-xs);padding:2px 8px;border-radius:var(--radius-sm);background:' + statusColor(t.status) + '20;color:' + statusColor(t.status) + ';font-weight:600">' + escHtml(t.status || '—') + '</span></td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);font-family:var(--font-mono)">' + escHtml(t.effective_date ? t.effective_date.slice(0,10) : '—') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary);max-width:240px">' + escHtml(t.macro_impact_assessment || '—') + '</td>' +
      '</tr>';
    });
    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  function renderDebtDynamics(items, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(items) || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">Debt dynamics data will appear after the next publish cycle.</p>';
      return;
    }
    var trajColor = function(t) {
      if (!t) return '';
      var lt = t.toLowerCase();
      if (lt.indexOf('deteriorat') > -1) return 'var(--color-critical,#ef4444)';
      if (lt.indexOf('improv') > -1) return 'var(--color-green,#22c55e)';
      return 'var(--color-amber,#f59e0b)';
    };
    var html = '<div style="overflow-x:auto"><table style="width:100%;font-size:var(--text-sm);border-collapse:collapse">' +
      '<thead><tr style="border-bottom:1px solid var(--color-border)">' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Entity</th>' +
        '<th style="text-align:right;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Debt/GDP</th>' +
        '<th style="text-align:right;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Deficit/GDP</th>' +
        '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Trajectory</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Key Risk</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Source</th>' +
      '</tr></thead><tbody>';
    items.forEach(function(d) {
      var debtGdp = d.debt_to_gdp != null ? parseFloat(d.debt_to_gdp).toFixed(1) + '%' : (d.reading || '—');
      var defGdp = d.deficit_to_gdp != null ? parseFloat(d.deficit_to_gdp).toFixed(1) + '%' : '—';
      var traj = d.trajectory || d.direction || '';
      html += '<tr style="border-bottom:1px solid var(--color-border)">' +
        '<td style="padding:var(--space-2);font-weight:600">' + escHtml(d.entity || d.indicator || '') + '</td>' +
        '<td style="padding:var(--space-2);text-align:right;font-family:var(--font-mono)">' + escHtml(debtGdp) + '</td>' +
        '<td style="padding:var(--space-2);text-align:right;font-family:var(--font-mono)">' + escHtml(defGdp) + '</td>' +
        '<td style="padding:var(--space-2);text-align:center"><span style="font-size:var(--text-xs);color:' + trajColor(traj) + ';font-weight:600">' + escHtml(traj || '—') + '</span></td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary);max-width:240px">' + escHtml(d.key_risk || '') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(d.source || '') + '</td>' +
      '</tr>';
    });
    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  function renderCreditStress(items, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(items) || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">Credit stress data will appear after the next publish cycle.</p>';
      return;
    }
    var stressColor = function(s) {
      if (!s) return '';
      var ls = s.toLowerCase();
      if (ls === 'red') return 'var(--color-critical,#ef4444)';
      if (ls === 'amber') return 'var(--color-amber,#f59e0b)';
      if (ls === 'green') return 'var(--color-green,#22c55e)';
      return 'var(--color-text-muted)';
    };
    var html = '<div style="overflow-x:auto"><table style="width:100%;font-size:var(--text-sm);border-collapse:collapse">' +
      '<thead><tr style="border-bottom:1px solid var(--color-border)">' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Segment</th>' +
        '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Stress</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Key Metric</th>' +
        '<th style="text-align:center;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Direction</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Contagion Risk</th>' +
        '<th style="text-align:left;padding:var(--space-2);font-size:var(--text-xs);text-transform:uppercase;color:var(--color-text-muted)">Source</th>' +
      '</tr></thead><tbody>';
    items.forEach(function(c) {
      var stress = c.stress_level || c.flag || '';
      var dir = c.direction || '';
      html += '<tr style="border-bottom:1px solid var(--color-border)">' +
        '<td style="padding:var(--space-2);font-weight:600">' + escHtml(c.segment || c.indicator || '') + '</td>' +
        '<td style="padding:var(--space-2);text-align:center"><span style="font-size:var(--text-xs);padding:2px 8px;border-radius:var(--radius-sm);background:' + stressColor(stress) + '20;color:' + stressColor(stress) + ';font-weight:600">' + escHtml(stress || '—') + '</span></td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);font-family:var(--font-mono)">' + escHtml(c.key_metric || c.reading || '') + '</td>' +
        '<td style="padding:var(--space-2);text-align:center;font-size:var(--text-xs);color:' + stressColor(dir.indexOf('Deterior') > -1 ? 'Red' : dir.indexOf('Improv') > -1 ? 'Green' : 'Amber') + '">' + escHtml(dir || '—') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-secondary)">' + escHtml(c.contagion_risk || '—') + '</td>' +
        '<td style="padding:var(--space-2);font-size:var(--text-xs);color:var(--color-text-muted)">' + escHtml(c.source || '') + '</td>' +
      '</tr>';
    });
    html += '</tbody></table></div>';
    el.innerHTML = html;
  }

  function renderSystemicRisk(items, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!Array.isArray(items) || !items.length) {
      el.innerHTML = '<p class="text-muted text-sm">Systemic risk data will appear after the next publish cycle.</p>';
      return;
    }
    var probColor = function(p) {
      if (!p) return '';
      var lp = String(p).toLowerCase();
      if (lp === 'critical' || lp === 'high') return 'var(--color-critical,#ef4444)';
      if (lp === 'medium') return 'var(--color-amber,#f59e0b)';
      return 'var(--color-green,#22c55e)';
    };
    var typeColor = function(t) {
      if (!t) return 'var(--color-text-muted)';
      var lt = t.toLowerCase();
      if (lt === 'structural') return 'var(--color-critical,#ef4444)';
      if (lt === 'cyclical') return 'var(--color-amber,#f59e0b)';
      return 'var(--color-text-secondary)';
    };
    var html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--space-3)">';
    items.forEach(function(r) {
      var prob = r.probability_preliminary || r.probability || '';
      var chipsHtml = '';
      if (Array.isArray(r.affected_asset_classes) && r.affected_asset_classes.length) {
        chipsHtml = '<div style="display:flex;flex-wrap:wrap;gap:var(--space-1);margin-top:var(--space-2)">' +
          r.affected_asset_classes.map(function(ac) {
            return '<span style="font-size:10px;padding:1px 6px;border-radius:var(--radius-sm);background:var(--surface-3,rgba(255,255,255,0.06));color:var(--color-text-secondary)">' + escHtml(ac) + '</span>';
          }).join('') + '</div>';
      }
      html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4);border-left:3px solid ' + probColor(prob) + '">' +
        '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-2)">' +
          '<span style="font-weight:600;font-size:var(--text-sm)">' + escHtml(r.label || r.indicator || '') + '</span>' +
          '<span style="font-size:10px;padding:1px 6px;border-radius:var(--radius-sm);color:' + typeColor(r.type) + ';border:1px solid ' + typeColor(r.type) + '40">' + escHtml(r.type || '') + '</span>' +
          '<span style="font-size:10px;padding:1px 6px;border-radius:var(--radius-sm);background:' + probColor(prob) + '20;color:' + probColor(prob) + ';font-weight:600">' + escHtml(String(prob)) + '</span>' +
        '</div>' +
        '<div style="font-size:var(--text-xs);color:var(--color-text-secondary);line-height:1.5;margin-bottom:var(--space-2)">' +
          '<strong>Channel:</strong> ' + escHtml(r.transmission_channel || '—') +
        '</div>' +
        (r.monitoring_indicator ? '<div style="font-size:var(--text-xs);color:var(--color-text-muted)"><strong>Watch:</strong> ' + escHtml(r.monitoring_indicator) + '</div>' : '') +
        chipsHtml +
      '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  function renderSafeHavenV2(data, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!data || typeof data !== 'object') {
      el.innerHTML = '<p class="text-muted text-sm">Safe haven data will appear after the next publish cycle.</p>';
      return;
    }
    // Handle v2 format (gold_thesis, bonds_note, cash_note)
    if (data.gold_thesis || data.bonds_note || data.cash_note) {
      var items = [
        { icon: '🥇', label: 'Gold', text: data.gold_thesis },
        { icon: '📊', label: 'Bonds', text: data.bonds_note },
        { icon: '💵', label: 'Cash', text: data.cash_note }
      ];
      var html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:var(--space-3)">';
      items.forEach(function(item) {
        if (!item.text) return;
        html += '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4)">' +
          '<div style="font-size:var(--text-sm);font-weight:600;margin-bottom:var(--space-2)">' + item.icon + ' ' + escHtml(item.label) + '</div>' +
          '<div style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.55">' + escHtml(item.text) + '</div>' +
        '</div>';
      });
      html += '</div>';
      el.innerHTML = html;
      return;
    }
    // Legacy format fallback (asset, regime, rationale)
    if (data.asset) {
      el.innerHTML = '<div style="background:var(--surface-2);border-radius:var(--radius-md);padding:var(--space-4)">' +
        '<div style="font-size:var(--text-xs);color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.05em">' + escHtml(data.regime || '') + ' · ' + escHtml(data.horizon || '') + '</div>' +
        '<div style="font-size:var(--text-sm);font-weight:600;margin:var(--space-2) 0">' + escHtml(data.asset) + '</div>' +
        '<div style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.55">' + escHtml(data.rationale || '') + '</div>' +
        (data.condition_for_reassessment ? '<div style="font-size:var(--text-xs);font-style:italic;color:var(--color-text-muted);margin-top:var(--space-3)"><strong>Reassess if:</strong> ' + escHtml(data.condition_for_reassessment) + '</div>' : '') +
      '</div>';
      return;
    }
    el.innerHTML = '<p class="text-muted text-sm">Safe haven data will appear after the next publish cycle.</p>';
  }



  /* ── Triage Strip (SL-02 / D2) ──────────────────────────────────────────
   *
   * renderTriageStrip(config, targetId)
   *
   * Renders the canonical five-zone above-the-fold triage sequence into
   * the element with id=targetId. Zone order is enforced by this function —
   * the caller cannot reorder zones.
   *
   * config shape:
   * {
   *   kpis: [{ label, value, sub?, trend?, accent? }],   // required
   *   signal: { label?, title, body, source_url? },       // required
   *   structural: {                                        // required
   *     label: string,          // section heading e.g. "Risk Vector Heat"
   *     targetId: string,       // id of the container to render into
   *     renderFn: function(targetId)  // caller provides their own renderer
   *   },
   *   delta: {                                            // required
   *     label: string,          // e.g. "Top Moves This Issue"
   *     items: array            // array passed to renderDeltaStrip() or equivalent
   *   },
   *   threshold: {              // optional — omit if no threshold this issue
   *     label: string,
   *     html: string            // pre-rendered HTML string (caller owns content)
   *   }
   * }
   *
   * Usage:
   *   AsymSections.renderTriageStrip(config, 'triage-container');
   *
   * The structural slot uses caller-supplied renderFn to remain monitor-agnostic.
   * The triage strip owns layout + order. The monitor owns the structural visual.
   * ─────────────────────────────────────────────────────────────────────────── */

  function renderTriageStrip(config, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (!config) {
      el.innerHTML = '<p class="text-muted text-sm">Triage data unavailable.</p>';
      return;
    }

    var html = '<div class="triage-strip">';

    /* ── Zone 1: KPI Strip ── */
    if (config.kpis && config.kpis.length) {
      html += '<div class="triage-section" data-triage-zone="kpis">';
      html += '<div class="triage-section__label">At a Glance</div>';
      html += '<div class="kpi-strip">';
      config.kpis.forEach(function (kpi) {
        var valClass = 'kpi-card__value' + (kpi.accent ? ' kpi-card__value--accent' : '');
        html +=
          '<div class="kpi-card">' +
            '<div class="kpi-card__label">' + escHtml(kpi.label) + '</div>' +
            (kpi.sub ? '<div class="kpi-card__sub">' + escHtml(kpi.sub) + '</div>' : '') +
            '<div class="' + valClass + '">' + escHtml(String(kpi.value != null ? kpi.value : '—')) + '</div>' +
            (kpi.trend ? '<div class="kpi-card__trend">' + escHtml(kpi.trend) + '</div>' : '') +
          '</div>';
      });
      html += '</div>';
      html += '</div>';
    }

    /* ── Zone 2: Lead Signal ── */
    if (config.signal) {
      var sig = config.signal;
      html += '<div class="triage-section" data-triage-zone="signal">';
      html += '<div class="triage-section__label">Lead Signal</div>';
      html += '<div class="signal-block">';
      if (sig.label) {
        html += '<div class="signal-block__label">' + escHtml(sig.label) + '</div>';
      }
      if (sig.title) {
        html += '<div class="signal-block__title">' + escHtml(sig.title) + '</div>';
      }
      if (sig.body) {
        html += '<p class="signal-block__body">' + escHtml(sig.body) + '</p>';
      }
      if (sig.source_url && typeof window.AsymRenderer !== 'undefined' && window.AsymRenderer.sourceLink) {
        html += '<div style="margin-top:var(--space-3)">' + window.AsymRenderer.sourceLink(sig.source_url) + '</div>';
      }
      if (sig.confidence) {
        var confClass = 'badge-confidence badge-confidence--' + escHtml(sig.confidence.toLowerCase());
        html += '<div style="margin-top:var(--space-3)"><span class="' + confClass + '">' + escHtml(sig.confidence) + '</span></div>';
      }
      html += '</div>';
      html += '</div>';
    }

    /* ── Zone 3: Structural Snapshot (caller's renderFn) ── */
    if (config.structural) {
      var st = config.structural;
      var stId = st.targetId || (targetId + '-structural');
      html += '<div class="triage-section" data-triage-zone="structural">';
      html += '<div class="triage-section__label">' + escHtml(st.label || 'Structural Snapshot') + '</div>';
      html += '<div id="' + escHtml(stId) + '"></div>';
      html += '</div>';
    }

    /* ── Zone 4: Primary Delta ── */
    if (config.delta && config.delta.items && config.delta.items.length) {
      var dl = config.delta;
      html += '<div class="triage-section" data-triage-zone="delta">';
      html += '<div class="triage-section__label">' + escHtml(dl.label || 'Top Moves This Issue') + '</div>';
      html += '<ul class="delta-strip">';
      dl.items.forEach(function (item, i) {
        html +=
          '<li class="delta-item">' +
            '<span class="delta-item__rank">' + (i + 1) + '</span>' +
            '<div class="delta-item__body">' +
              (item.module ? '<div class="delta-item__module">' + escHtml(item.module) + '</div>' : '') +
              '<div class="delta-item__title">' + escHtml(item.title || item.headline || '') + '</div>' +
              (item.one_line || item.summary ? '<div class="delta-item__one-line">' + escHtml(item.one_line || item.summary) + '</div>' : '') +
              (item.source_url && typeof window.AsymRenderer !== 'undefined' && window.AsymRenderer.sourceLink
                ? '<div style="margin-top:var(--space-1)">' + window.AsymRenderer.sourceLink(item.source_url) + '</div>'
                : '') +
            '</div>' +
            (item.type ? '<span class="delta-item__type">' + escHtml(item.type) + '</span>' : '') +
          '</li>';
      });
      html += '</ul>';
      html += '</div>';
    }

    /* ── Zone 5: Threshold (optional) ── */
    if (config.threshold) {
      var th = config.threshold;
      html += '<div class="triage-section triage-section--threshold" data-triage-zone="threshold">';
      html += '<div class="triage-section__label">' + escHtml(th.label || 'Threshold Watch') + '</div>';
      html += th.html || '';
      html += '</div>';
    }

    html += '</div>'; /* end .triage-strip */
    el.innerHTML = html;

    /* ── Fire structural renderFn after DOM is written ── */
    if (config.structural && typeof config.structural.renderFn === 'function') {
      var stTargetId = config.structural.targetId || (targetId + '-structural');
      try {
        config.structural.renderFn(stTargetId);
      } catch (e) {
        var stEl = document.getElementById(stTargetId);
        if (stEl) stEl.innerHTML = '<p class="text-muted text-sm">Structural snapshot unavailable.</p>';
      }
    }
  }


  return {
    // Helpers (exposed for inline orchestrators)
    escHtml: escHtml,
    deriveStatusClass: deriveStatusClass,
    buildStatusBadge: buildStatusBadge,
    bandToRowClass: bandToRowClass,
    confBadgeClass: confBadgeClass,
    deviationBandClass: deviationBandClass,
    levelLabelClass: levelLabelClass,

    // Report / Dashboard sections
    renderEscalationAlerts: renderEscalationAlerts,
    renderGlobalSnapshot: renderGlobalSnapshot,
    renderWeeklyBrief: renderWeeklyBrief,
    renderTheatreTracker: renderTheatreTracker,
    renderIndicatorScoring: renderIndicatorScoring,
    renderFlagMatrix: renderFlagMatrix,
    renderACLEDReference: renderACLEDReference,
    renderKeyJudgments: renderKeyJudgments,
    renderCrossMonitorCandidates: renderCrossMonitorCandidates,

    // Persistent-page enrichment helpers
    enrichBaselineWithTheatre: enrichBaselineWithTheatre,
    enrichIndicatorCell: enrichIndicatorCell,
    renderEscalationLog: renderEscalationLog,
    // ESA-specific sections
    renderDomainTracker: renderDomainTracker,
    renderAutonomySnapshot: renderAutonomySnapshot,
    renderUsEuTracker: renderUsEuTracker,
    renderElectionThreats: renderElectionThreats,
    renderLagrangeScores: renderLagrangeScores,
    renderDefenceSpending: renderDefenceSpending,
    renderDefenceProgrammes: renderDefenceProgrammes,
    // Generic reusable chart
    renderRadarChart: renderRadarChart,
    // ERM-specific sections (reusable cross-monitor where applicable)
    renderPolicyLawCompliance: renderPolicyLawCompliance,
    renderICJTracker: renderICJTracker,
    renderLossDamageTracker: renderLossDamageTracker,
    renderAttributionGapCases: renderAttributionGapCases,
    renderReverseCascadeCheck: renderReverseCascadeCheck,
    renderRegionalCoverage: renderRegionalCoverage,
    renderExtremeEventsLog: renderExtremeEventsLog,
    renderClimateSecurityNexus: renderClimateSecurityNexus,
    renderPlanetaryStatusSnapshot: renderPlanetaryStatusSnapshot,
    // GMM / Cross-Monitor reusable sections
    renderScenarioFramework: renderScenarioFramework,
    renderPositioningOverlay: renderPositioningOverlay,
    renderCentralBankTracker: renderCentralBankTracker,
    renderTariffTracker: renderTariffTracker,
    renderDebtDynamics: renderDebtDynamics,
    renderCreditStress: renderCreditStress,
    renderSystemicRisk: renderSystemicRisk,
    renderSafeHavenV2: renderSafeHavenV2,
    // Sprint 1 SL-02: Shared triage strip
    renderTriageStrip: renderTriageStrip
  };
}());


/* ─── Country Flag Utility ───────────────────────────────────
   AsymRenderer.flag(code) — returns emoji flag for ISO 3166-1 alpha-2
   or common abbreviations used across monitors.
   Usage: AsymRenderer.flag('RU') → '🇷🇺'
          AsymRenderer.flagLabel('RU') → '🇷🇺 RU'
   ─────────────────────────────────────────────────────────── */

(function () {
  // Extended map covering all monitor-relevant country codes + abbreviations
  var ALIASES = {
    /* — Major powers — */
    'RU': 'RU', 'RUSSIA': 'RU',
    'US': 'US', 'USA': 'US', 'UNITED STATES': 'US',
    'CN': 'CN', 'CHINA': 'CN',
    'IN': 'IN', 'INDIA': 'IN',
    'JP': 'JP', 'JAPAN': 'JP',
    'DE': 'DE', 'GERMANY': 'DE',
    'FR': 'FR', 'FRANCE': 'FR',
    'GB': 'GB', 'UK': 'GB', 'UNITED KINGDOM': 'GB',
    'TR': 'TR', 'TURKEY': 'TR', 'TÜRKIYE': 'TR',
    'SA': 'SA', 'SAUDI ARABIA': 'SA', 'GULF': 'SA',
    /* — Europe — */
    'UA': 'UA', 'UKRAINE': 'UA',
    'PL': 'PL', 'POLAND': 'PL',
    'HU': 'HU', 'HUNGARY': 'HU',
    'RO': 'RO', 'ROMANIA': 'RO',
    'RS': 'RS', 'SERBIA': 'RS',
    'SK': 'SK', 'SLOVAKIA': 'SK',
    'SI': 'SI', 'SLOVENIA': 'SI',
    'CZ': 'CZ', 'CZECH REPUBLIC': 'CZ', 'CZECHIA': 'CZ',
    'AT': 'AT', 'AUSTRIA': 'AT',
    'CY': 'CY', 'CYPRUS': 'CY',
    'IT': 'IT', 'ITALY': 'IT',
    'ES': 'ES', 'SPAIN': 'ES',
    'PT': 'PT', 'PORTUGAL': 'PT',
    'GR': 'GR', 'GREECE': 'GR',
    'NL': 'NL', 'NETHERLANDS': 'NL',
    'BE': 'BE', 'BELGIUM': 'BE',
    'SE': 'SE', 'SWEDEN': 'SE',
    'FI': 'FI', 'FINLAND': 'FI',
    'NO': 'NO', 'NORWAY': 'NO',
    'DK': 'DK', 'DENMARK': 'DK',
    'CH': 'CH', 'SWITZERLAND': 'CH',
    'BA': 'BA', 'BOSNIA': 'BA', 'BOSNIA-HERZEGOVINA (RS)': 'BA', 'BOSNIA-HERZEGOVINA': 'BA',
    /* — Post-Soviet / Caucasus — */
    'GE': 'GE', 'GEORGIA': 'GE',
    'AM': 'AM', 'ARMENIA': 'AM',
    'AZ': 'AZ', 'AZERBAIJAN': 'AZ',
    'KZ': 'KZ', 'KAZAKHSTAN': 'KZ',
    'BY': 'BY', 'BELARUS': 'BY',
    'MD': 'MD', 'MOLDOVA': 'MD',
    /* — Middle East — */
    'IL': 'IL', 'ISRAEL': 'IL',
    'IR': 'IR', 'IRAN': 'IR',
    'IQ': 'IQ', 'IRAQ': 'IQ',
    'SY': 'SY', 'SYRIA': 'SY',
    'LB': 'LB', 'LEBANON': 'LB',
    'YE': 'YE', 'YEMEN': 'YE',
    'JO': 'JO', 'JORDAN': 'JO',
    'EG': 'EG', 'EGYPT': 'EG',
    'TN': 'TN', 'TUNISIA': 'TN',
    'LY': 'LY', 'LIBYA': 'LY',
    'MA': 'MA', 'MOROCCO': 'MA',
    'QA': 'QA', 'QATAR': 'QA',
    'AE': 'AE', 'UAE': 'AE', 'UNITED ARAB EMIRATES': 'AE',
    /* — Asia-Pacific — */
    'KP': 'KP', 'DPRK': 'KP', 'NORTH KOREA': 'KP',
    'KR': 'KR', 'SOUTH KOREA': 'KR',
    'TW': 'TW', 'TAIWAN': 'TW',
    'TH': 'TH', 'THAILAND': 'TH',
    'MM': 'MM', 'MYANMAR': 'MM',
    'PH': 'PH', 'PHILIPPINES': 'PH',
    'ID': 'ID', 'INDONESIA': 'ID',
    'MY': 'MY', 'MALAYSIA': 'MY',
    'VN': 'VN', 'VIETNAM': 'VN',
    'BD': 'BD', 'BANGLADESH': 'BD',
    'PK': 'PK', 'PAKISTAN': 'PK',
    'AF': 'AF', 'AFGHANISTAN': 'AF',
    'NP': 'NP', 'NEPAL': 'NP',
    'LK': 'LK', 'SRI LANKA': 'LK',
    'AU': 'AU', 'AUSTRALIA': 'AU',
    'NZ': 'NZ', 'NEW ZEALAND': 'NZ',
    /* — Africa — */
    'ZA': 'ZA', 'SOUTH AFRICA': 'ZA',
    'NG': 'NG', 'NIGERIA': 'NG',
    'ET': 'ET', 'ETHIOPIA': 'ET',
    'KE': 'KE', 'KENYA': 'KE',
    'TZ': 'TZ', 'TANZANIA': 'TZ',
    'UG': 'UG', 'UGANDA': 'UG',
    'RW': 'RW', 'RWANDA': 'RW',
    'SD': 'SD', 'SUDAN': 'SD',
    'CD': 'CD', 'DRC': 'CD', 'DEMOCRATIC REPUBLIC OF THE CONGO': 'CD',
    'CM': 'CM', 'CAMEROON': 'CM',
    'GH': 'GH', 'GHANA': 'GH',
    'SN': 'SN', 'SENEGAL': 'SN',
    'ML': 'ML', 'MALI': 'ML',
    'BF': 'BF', 'BURKINA FASO': 'BF',
    'NE': 'NE', 'NIGER': 'NE',
    'TD': 'TD', 'CHAD': 'TD',
    'SO': 'SO', 'SOMALIA': 'SO',
    'MZ': 'MZ', 'MOZAMBIQUE': 'MZ',
    'ZM': 'ZM', 'ZAMBIA': 'ZM',
    'ZW': 'ZW', 'ZIMBABWE': 'ZW',
    'CI': 'CI', "CÔTE D'IVOIRE": 'CI', "COTE D'IVOIRE": 'CI',
    'BJ': 'BJ', 'BENIN': 'BJ',
    'HT': 'HT', 'HAITI': 'HT',
    'AO': 'AO', 'ANGOLA': 'AO',
    /* — Americas — */
    'MX': 'MX', 'MEXICO': 'MX',
    'BR': 'BR', 'BRAZIL': 'BR',
    'AR': 'AR', 'ARGENTINA': 'AR',
    'CL': 'CL', 'CHILE': 'CL',
    'CO': 'CO', 'COLOMBIA': 'CO',
    'VE': 'VE', 'VENEZUELA': 'VE',
    'PE': 'PE', 'PERU': 'PE',
    'BO': 'BO', 'BOLIVIA': 'BO',
    'NI': 'NI', 'NICARAGUA': 'NI',
    'SV': 'SV', 'EL SALVADOR': 'SV',
    'HN': 'HN', 'HONDURAS': 'HN',
    'GT': 'GT', 'GUATEMALA': 'GT',
    'CU': 'CU', 'CUBA': 'CU',
    'CA': 'CA', 'CANADA': 'CA',
    /* — Supranational — */
    'EU': 'EU', 'EUROPEAN UNION': 'EU',
  };

  function toEmoji(iso2) {
    if (!iso2 || iso2.length !== 2) return '';
    // EU is not a country — use a special rendering
    if (iso2 === 'EU') return '🇪🇺';
    var cp1 = iso2.toUpperCase().charCodeAt(0) - 65 + 0x1F1E6;
    var cp2 = iso2.toUpperCase().charCodeAt(1) - 65 + 0x1F1E6;
    return String.fromCodePoint(cp1) + String.fromCodePoint(cp2);
  }

  function flag(code) {
    if (!code) return '';
    var upper = String(code).toUpperCase().trim();
    var iso = ALIASES[upper] || (upper.length === 2 ? upper : null);
    if (!iso) return '';
    return toEmoji(iso);
  }

  function flagLabel(code) {
    var f = flag(code);
    if (!f) return code || '';
    return f + ' ' + code.toUpperCase();
  }

  // Attach to AsymRenderer if available, otherwise to window directly
  if (window.AsymRenderer) {
    window.AsymRenderer.flag = flag;
    window.AsymRenderer.flagLabel = flagLabel;
  }
  window.AsymFlag = { flag: flag, flagLabel: flagLabel };
}());

/* ── AsymRenderer.renderMarkdown(text) ──────────────────────────────────────
 * Safe renderer for LLM-generated narrative fields (weekly_brief, note, etc.)
 * that contain markdown (**bold**) AND raw HTML anchor tags mixed together.
 *
 * Anti-pattern FE-020: never run escHtml() on these fields directly.
 * That destroys both the markdown syntax and the <a href> tags.
 *
 * Usage:
 *   element.innerHTML = AsymRenderer.renderMarkdown(d.weekly_brief);
 * ─────────────────────────────────────────────────────────────────────────── */
(function () {
  function renderMarkdown(text) {
    if (!text) return '<p class="text-muted text-sm">No content available.</p>';
    var paras = String(text).split(/\n{2,}/).filter(function (p) { return p.trim(); });
    return paras.map(function (para) {
      var parts = para.split(/(<a\s[^>]*>.*?<\/a>)/gi);
      var safe = parts.map(function (part, i) {
        if (i % 2 === 1) return part; // <a> tag — pass through untouched
        var s = part
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;');
        s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/^#{1,3}\s+(.+)$/gm, '<strong>$1</strong>');
        return s;
      }).join('');
      return '<p style="margin-bottom:var(--space-4);line-height:1.7">' + safe + '</p>';
    }).join('');
  }

  if (window.AsymRenderer) {
    window.AsymRenderer.renderMarkdown = renderMarkdown;
  }
  window.AsymRenderMarkdown = renderMarkdown; // fallback direct access
}());

/* ── AsymRenderer.sourceLabel(url) ──────────────────────────────────────────
 * Returns a short human-readable source name from a URL.
 * Used to replace generic "Source →" labels with "Reuters →", "BBC →", etc.
 *
 * Usage:
 *   AsymRenderer.sourceLabel('https://reuters.com/...')  → 'Reuters'
 *   AsymRenderer.sourceLink(url)  → '<a href="..." ...>Reuters →</a>'
 *   AsymRenderer.sourceInline(url, accent) → inline link for appending to text
 * ─────────────────────────────────────────────────────────────────────────── */
(function () {
  var DOMAIN_MAP = {
    // News wires
    'reuters.com':          'Reuters',
    'apnews.com':           'AP',
    'afp.com':              'AFP',
    // Broadcast
    'bbc.co.uk':            'BBC',
    'bbc.com':              'BBC',
    'cnn.com':              'CNN',
    'aljazeera.com':        'Al Jazeera',
    'dw.com':               'DW',
    'euronews.com':         'Euronews',
    'rferl.org':            'RFE/RL',
    'politico.eu':          'Politico EU',
    'politico.com':         'Politico',
    // Financial
    'bloomberg.com':        'Bloomberg',
    'ft.com':               'FT',
    'wsj.com':              'WSJ',
    'economist.com':        'The Economist',
    'cnbc.com':             'CNBC',
    // EU / Institutional
    'ec.europa.eu':         'European Commission',
    'eeas.europa.eu':       'EEAS',
    'consilium.europa.eu':  'EU Council',
    'europarl.europa.eu':   'European Parliament',
    'eda.europa.eu':        'EDA',
    'digital-strategy.ec.europa.eu': 'EU AI Office',
    '2eu.brussels':         'European Commission',
    // NATO / Defence
    'nato.int':             'NATO',
    'stratcomcoe.org':      'NATO StratCom',
    'hybridcoe.fi':         'Hybrid CoE',
    // Intelligence / OSINT
    'bellingcat.com':       'Bellingcat',
    'vsquare.org':          'VSquare',
    'dfrlabs.org':          'DFRLab',
    'atlanticcouncil.org':  'DFRLab',
    'understandingwar.org': 'ISW',
    'euvsdisinfo.eu':       'EUvsDisinfo',
    'disinfo.eu':           'EU DisinfoLab',
    'stopfake.org':         'StopFake',
    // Think tanks
    'ecfr.eu':              'ECFR',
    'rusi.org':             'RUSI',
    'iiss.org':             'IISS',
    'chathamhouse.org':     'Chatham House',
    'carnegieeurope.eu':    'Carnegie Europe',
    'rand.org':             'RAND',
    'piie.com':             'PIIE',
    'wto.org':              'WTO',
    'imf.org':              'IMF',
    'worldbank.org':        'World Bank',
    'bis.org':              'BIS',
    'federalreserve.gov':   'Federal Reserve',
    'ecb.europa.eu':        'ECB',
    'ustr.gov':             'USTR',
    // Democracy / Rights
    'freedomhouse.org':     'Freedom House',
    'v-dem.net':            'V-Dem',
    'transparency.org':     'TI',
    'rsf.org':              'RSF',
    'hrw.org':              'HRW',
    'amnesty.org':          'Amnesty',
    // Climate / Environment
    'ipcc.ch':              'IPCC',
    'wmo.int':              'WMO',
    'climate.copernicus.eu':'Copernicus',
    'stockholmresilience.org': 'Stockholm Resilience',
    'pik-potsdam.de':       'Potsdam Institute',
    'nature.com':           'Nature',
    'carbonbrief.org':      'Carbon Brief',
    'climatechangenews.com':'Climate Home',
    'internal-displacement.org': 'IDMC',
    // Conflict / Humanitarian
    'acleddata.com':        'ACLED',
    'ucdp.uu.se':           'UCDP',
    'reliefweb.int':        'UN OCHA',
    'unocha.org':           'UN OCHA',
    'crisisgroup.org':      'ICG',
    // AI / Tech
    'openai.com':           'OpenAI',
    'anthropic.com':        'Anthropic',
    'deepmind.google':      'DeepMind',
    'hai.stanford.edu':     'Stanford HAI',
    'governance.ai':        'GovAI',
    'safe.ai':              'CAIS',
    'nist.gov':             'NIST',
    'techpolicy.press':     'Tech Policy Press',
    'wired.com':            'Wired',
    'theguardian.com':      'The Guardian',
    'nytimes.com':          'NYT',
    'washingtonpost.com':   'WaPo',
    // Asym-intel monitors
    'asym-intel.info':      'Asymmetric Intelligence',
  };

  function sourceLabel(url) {
    if (!url) return 'Source';
    try {
      var hostname = new URL(url).hostname.replace(/^www\./, '');
      // Exact match
      if (DOMAIN_MAP[hostname]) return DOMAIN_MAP[hostname];
      // Subdomain match (e.g. climate.copernicus.eu)
      var keys = Object.keys(DOMAIN_MAP);
      for (var i = 0; i < keys.length; i++) {
        if (hostname === keys[i] || hostname.endsWith('.' + keys[i])) {
          return DOMAIN_MAP[keys[i]];
        }
      }
      // Fallback: first meaningful segment of hostname
      var parts = hostname.split('.');
      var name = parts.length >= 2 ? parts[parts.length - 2] : hostname;
      return name.charAt(0).toUpperCase() + name.slice(1);
    } catch (e) {
      return 'Source';
    }
  }

  /* Returns a complete inline <a> tag: "Reuters →"
   * Returns '' (empty string) when url is falsy — callers need no guard logic.
   * Canonical call: AsymRenderer.sourceLink(item.source_url)
   * Never wrap url in esc() — sourceLink handles its own output safely. */
  function sourceLink(url, opts) {
    if (!url) return '';
    opts = opts || {};
    var label = sourceLabel(url);
    var color = opts.color || 'var(--monitor-accent)';
    var size  = opts.size  || 'var(--text-xs)';
    return '<a href="' + url + '" target="_blank" rel="noopener" ' +
      'style="color:' + color + ';font-size:' + size + ';text-decoration:none;white-space:nowrap" ' +
      'onmouseover="this.style.textDecoration=\'underline\'" ' +
      'onmouseout="this.style.textDecoration=\'none\'">' +
      label + ' →</a>';
  }

  /* Attach to AsymRenderer */
  if (window.AsymRenderer) {
    window.AsymRenderer.sourceLabel = sourceLabel;
    window.AsymRenderer.sourceLink  = sourceLink;
  }
  window.AsymSourceLabel = sourceLabel;
  window.AsymSourceLink  = sourceLink;
})();



/* ─────────────────────────────────────────────────────────────
   SL-02B  Shared Chart & Cross-Monitor Functions
   Added Sprint 1 — centralise inline patterns from WDM/GMM/ESA
   ─────────────────────────────────────────────────────────────

   All three functions are attached to AsymSections:
     AsymSections.renderTierBar(config, targetId)
     AsymSections.renderRankedBar(config, targetId)
     AsymSections.renderCrossMonitorFlags(cmf, targetId)

   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  /* ── Helpers ─────────────────────────────────────────────── */
  function _esc(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function _isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  /* ── renderTierBar ───────────────────────────────────────────
   * Stacked horizontal Chart.js bar (single-row) for tier counts.
   *
   * config: {
   *   segments: [{ label: string, count: number, color: string }],
   *   legendId?: string   — ID of an existing <div> to write legend into
   *   canvasId?: string   — ID of an existing <canvas>; if absent, one is
   *                         created inside targetId
   *   height?:  number    — canvas height px (default 60)
   * }
   * targetId: ID of container element. Populated with <canvas> when
   *           config.canvasId is absent.
   *
   * Segment border-radius rule: first → leftRound, last → rightRound,
   * middle → square.  Segments with count 0 are skipped from rendering
   * but kept in legend.
   * ──────────────────────────────────────────────────────────── */
  function renderTierBar(config, targetId) {
    if (!config || !Array.isArray(config.segments)) return;
    if (typeof Chart === 'undefined') return;

    var container = document.getElementById(targetId);
    if (!container) return;

    var segs = config.segments;
    var height = config.height || 60;
    var labelColor = _isDark() ? '#9d9893' : '#6b6660';

    /* Total — guard divide-by-zero */
    var total = 0;
    segs.forEach(function (s) { total += (s.count || 0); });
    if (total === 0) {
      container.innerHTML = '<p class="text-muted text-sm">No tier data available.</p>';
      return;
    }

    /* Canvas: reuse existing or create */
    var canvasId = config.canvasId || (targetId + '-canvas');
    var canvas = document.getElementById(canvasId);
    if (!canvas) {
      container.innerHTML = '<canvas id="' + canvasId + '" height="' + height + '" ' +
        'aria-label="Tier distribution chart" role="img"></canvas>';
      canvas = document.getElementById(canvasId);
    }
    if (!canvas) return;

    /* Build datasets — first/last track for border-radius */
    var nonZeroIdx = [];
    segs.forEach(function (s, i) { if ((s.count || 0) > 0) nonZeroIdx.push(i); });
    var firstNZ = nonZeroIdx[0];
    var lastNZ  = nonZeroIdx[nonZeroIdx.length - 1];

    var datasets = segs.map(function (s, i) {
      var isFirst = i === firstNZ;
      var isLast  = i === lastNZ;
      var br = isFirst && isLast
        ? 4
        : isFirst
          ? { topLeft: 4, bottomLeft: 4, topRight: 0, bottomRight: 0 }
          : isLast
            ? { topLeft: 0, bottomLeft: 0, topRight: 4, bottomRight: 4 }
            : 0;
      return {
        label: _esc(s.label) + ' (' + (s.count || 0) + ')',
        data: [s.count || 0],
        backgroundColor: s.color || 'rgba(148,163,184,0.6)',
        borderWidth: 0,
        borderRadius: br
      };
    });

    new Chart(canvas, {
      type: 'bar',
      data: { labels: [''], datasets: datasets },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) { return ctx.dataset.label; }
            }
          },
          datalabels: false
        },
        scales: {
          x: { stacked: true, display: false, grid: { display: false } },
          y: { stacked: true, display: false, grid: { display: false } }
        },
        layout: { padding: 0 },
        animation: { duration: 500 }
      },
      plugins: [{
        id: 'asymTierCountLabels',
        afterDatasetsDraw: function (chart) {
          var c2 = chart.ctx;
          chart.data.datasets.forEach(function (dataset, di) {
            var meta = chart.getDatasetMeta(di);
            if (meta.hidden) return;
            meta.data.forEach(function (bar) {
              var count = dataset.data[0];
              if (!count) return;
              var barW = bar.width;
              if (barW < 28) return;
              c2.save();
              c2.fillStyle = 'rgba(255,255,255,0.92)';
              c2.font = 'bold 13px Satoshi, system-ui, sans-serif';
              c2.textAlign = 'center';
              c2.textBaseline = 'middle';
              c2.fillText(String(count), bar.x - barW / 2 + barW / 2, bar.y);
              c2.restore();
            });
          });
        }
      }]
    });

    /* Legend injection */
    var legendId = config.legendId;
    if (legendId) {
      var legendEl = document.getElementById(legendId);
      if (legendEl) {
        legendEl.innerHTML = segs.map(function (s) {
          return '<span class="tier-legend-item">' +
            '<span class="tier-legend-dot" style="background:' + _esc(s.color || '#94a3b8') + '"></span>' +
            _esc(s.label) + ': <strong>' + (s.count || 0) + '</strong>' +
            '</span>';
        }).join('');
      }
    }
  }


  /* ── renderRankedBar ──────────────────────────────────────────
   * Sorted horizontal bar list (CSS, no Chart.js).
   * Canonical replacement for the inline renderSeverityBar pattern.
   *
   * config: {
   *   items: [{ label: string, score: number, color: string, flag?: string }],
   *   maxScore?: number   — override bar scale ceiling (default: max of items)
   *   showScore?: boolean — show score value at bar end (default: true)
   *   labelWidth?: string — CSS width for label column (default: '145px')
   * }
   * targetId: container element to populate
   * ──────────────────────────────────────────────────────────── */
  function renderRankedBar(config, targetId) {
    if (!config || !Array.isArray(config.items)) return;
    var el = document.getElementById(targetId);
    if (!el) return;

    var items = config.items.slice().sort(function (a, b) {
      return (b.score || 0) - (a.score || 0);
    });

    if (!items.length) {
      el.innerHTML = '<p class="text-muted text-sm">No ranked data available.</p>';
      return;
    }

    var maxScore = config.maxScore != null
      ? config.maxScore
      : (items[0].score || 10);
    if (maxScore === 0) maxScore = 10;

    var showScore  = config.showScore !== false;
    var labelWidth = config.labelWidth || '145px';

    var html = '<div style="display:flex;flex-direction:column;gap:6px">';
    items.forEach(function (c) {
      var pct = Math.max(4, Math.round(((c.score || 0) / maxScore) * 100));
      var col = c.color || 'var(--monitor-accent)';
      var flagHtml = '';
      if (c.flag) {
        /* Accept either a pre-rendered emoji or a code to pass through AsymRenderer.flag */
        if (/\p{Emoji_Presentation}/u.test(c.flag)) {
          flagHtml = _esc(c.flag) + ' ';
        } else if (typeof window.AsymRenderer !== 'undefined' && window.AsymRenderer.flag) {
          flagHtml = (_esc(window.AsymRenderer.flag(c.flag)) || '') + ' ';
        }
      }
      html +=
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">' +
          '<div style="width:' + labelWidth + ';font-size:var(--text-xs);' +
            'color:var(--color-text-secondary);flex-shrink:0;text-align:right">' +
            flagHtml + _esc(c.label) +
          '</div>' +
          '<div style="position:relative;flex:1;height:16px;' +
            'background:rgba(100,116,139,0.1);border-radius:3px">' +
            '<div style="position:absolute;top:0;left:0;width:' + pct + '%;height:100%;' +
              'background:' + col + ';border-radius:3px;opacity:0.80"></div>' +
          '</div>' +
          (showScore
            ? '<div style="width:34px;font-size:var(--text-xs);font-weight:600;' +
                'color:' + col + ';flex-shrink:0;text-align:right">' +
                parseFloat(c.score || 0).toFixed(1) + '</div>'
            : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }


  /* ── renderCrossMonitorFlags ─────────────────────────────────
   * Canonical shared implementation (v2 — 12 Apr 2026).
   * Handles all field-name variants across 7 monitors.
   *
   * cmf: {
   *   flags: [{
   *     id|flag_id:       string
   *     headline|title|signal: string
   *     linkage|detail|body|summary|description: string
   *     monitor|source_monitor: string (slug)
   *     monitors_involved?: string[]
   *     classification|type|structural_or_transient?: string
   *     status?:           string  — 'Active', 'Active — ESCALATED', 'Resolved'
   *     severity?:         string  — border colour tier
   *     source_url|monitor_url?: string
   *     monitor_slug?:     string  — fallback for URL
   *     first_flagged|first_raised?: string
   *     updated|last_updated?:      string
   *     action?:           string
   *     unchanged_since?:  string
   *     conflict?:         string
   *     indicator?:        string
   *   }],
   *   updated?: string
   * }
   * ──────────────────────────────────────────────────────────── */

  var _MONITOR_DISPLAY_NAMES = {
    'democratic-integrity':       'World Democracy Monitor',
    'macro-monitor':             'Global Macro Monitor',
    'european-strategic-autonomy':'European Strategic Autonomy',
    'fimi-cognitive-warfare':    'FIMI & Cognitive Warfare',
    'ai-governance':             'AI Governance Monitor',
    'environmental-risks':       'Environmental Risks Monitor',
    'conflict-escalation':       'Conflict & Escalation Monitor'
  };

  function _cmfTitle(f) {
    return f.headline || f.title || f.signal || f.summary || '';
  }
  function _cmfBody(f) {
    return f.linkage || f.detail || f.body || f.description || '';
  }
  /* Abbreviation map for ID-based target extraction (e.g. wdm-fcw-001 → fcw → fimi-cognitive-warfare) */
  var _ABBR_TO_SLUG = {
    'wdm': 'democratic-integrity', 'gmm': 'macro-monitor',
    'esa': 'european-strategic-autonomy', 'fcw': 'fimi-cognitive-warfare',
    'agm': 'ai-governance', 'aim': 'ai-governance',
    'erm': 'environmental-risks', 'scem': 'conflict-escalation'
  };
  function _cmfLinkedSlug(f) {
    /* Extract the linked (target) monitor slug — not the host monitor.
       Priority: source_url path > ID-encoded abbreviation > monitor field */
    if (f.source_url) {
      var m = f.source_url.match(/\/monitors\/([^\/]+)\//);
      if (m) return m[1];
    }
    var id = (f.id || f.flag_id || '').toLowerCase();
    var parts = id.split('-');
    /* Pattern: host-target-seq, e.g. wdm-fcw-001 → target = parts[1] */
    if (parts.length >= 3 && _ABBR_TO_SLUG[parts[1]]) return _ABBR_TO_SLUG[parts[1]];
    return '';
  }
  function _cmfMonitor(f) {
    if (f.monitors_involved && f.monitors_involved.length) return f.monitors_involved;
    var linked = _cmfLinkedSlug(f);
    return linked ? [linked] : [];
  }
  function _cmfUrl(f) {
    if (f.source_url) return f.source_url;
    if (f.monitor_url) return f.monitor_url;
    var linked = _cmfLinkedSlug(f);
    if (linked) return '/monitors/' + linked + '/dashboard.html';
    var slug = f.monitor_slug || f.monitor || f.source_monitor || '';
    return slug ? '/monitors/' + slug + '/dashboard.html' : '';
  }
  function _cmfId(f) { return f.id || f.flag_id || ''; }
  function _cmfFormatDate(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d)) return _esc(iso);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  }
  function _slugToName(slug) {
    return _MONITOR_DISPLAY_NAMES[slug] || slug.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
  }

  function renderCrossMonitorFlags(cmf, targetId) {
    var el = document.getElementById(targetId);
    if (!el) return;

    var flags = (cmf && Array.isArray(cmf.flags)) ? cmf.flags : [];
    if (!flags.length) {
      el.innerHTML = '<p class="text-muted text-sm">No cross-monitor flags this issue.</p>';
      return;
    }

    function _sevBorderColor(sev) {
      var s = (sev || '').toLowerCase();
      if (s === 'critical' || s === 'high' || s.indexOf('escalat') >= 0) return 'var(--color-critical, #dc2626)';
      if (s === 'elevated' || s === 'amber')      return 'var(--color-high, #d97706)';
      return 'var(--color-border, #94a3b8)';
    }
    function _statusClass(s) {
      if (!s) return 'badge';
      var sl = s.toLowerCase();
      if (sl.indexOf('escalat') >= 0 || sl.indexOf('critical') >= 0) return 'badge badge--critical';
      if (sl.indexOf('active') >= 0)   return 'badge badge--accent';
      if (sl.indexOf('resolved') >= 0) return 'badge';
      return 'badge';
    }

    var html = '<div class="cross-monitor-panel">';
    if (cmf && cmf.updated) {
      html += '<div style="font-size:var(--text-xs);color:var(--text-muted);margin-bottom:var(--space-3)">' +
        'Updated ' + _cmfFormatDate(cmf.updated) +
        '</div>';
    }

    flags.forEach(function (flag) {
      var id      = _cmfId(flag);
      var title   = _cmfTitle(flag);
      var body    = _cmfBody(flag);
      var slugs   = _cmfMonitor(flag);
      var url     = _cmfUrl(flag);
      var status  = flag.status || '';
      var classification = flag.classification || flag.type || flag.structural_or_transient || '';
      var severity = flag.severity || status || 'moderate';
      var borderColor = _sevBorderColor(severity);
      var firstFlagged = flag.first_flagged || flag.first_raised || '';
      var updated = flag.updated || flag.last_updated || '';

      /* Monitor display names — linked to source URL */
      var monitorHtml = '';
      if (slugs.length) {
        var names = slugs.map(function(s) { return _slugToName(s); });
        if (url) {
          monitorHtml = '<a href="' + _esc(url) + '" style="color:var(--monitor-accent);text-decoration:underline;font-size:var(--text-xs)">' +
            _esc(names.join(' · ')) + '</a>';
        } else {
          monitorHtml = '<span style="font-size:var(--text-xs);color:var(--text-muted)">' +
            _esc(names.join(' · ')) + '</span>';
        }
      }

      /* Badges row */
      var badgesHtml = '';
      if (classification) badgesHtml += '<span class="badge">' + _esc(classification) + '</span>';
      if (status)         badgesHtml += '<span class="' + _statusClass(status) + '">' + _esc(status) + '</span>';

      /* Meta line (dates, extras) */
      var meta = [];
      if (firstFlagged) meta.push('First flagged: ' + _cmfFormatDate(firstFlagged));
      if (updated)      meta.push('Updated: ' + _cmfFormatDate(updated));
      if (flag.conflict) meta.push('Conflict: ' + flag.conflict);
      if (flag.indicator) meta.push('Indicator: ' + flag.indicator);

      html +=
        '<div class="cms-flag" style="border-left:3px solid ' + borderColor + '">' +
          '<div class="cms-flag__header">' +
            '<span class="cms-flag__id">' + _esc(id) + '</span>' +
            (badgesHtml
              ? '<div style="display:flex;gap:var(--space-2);flex-wrap:wrap;align-items:center">' + badgesHtml + '</div>'
              : '') +
          '</div>' +
          '<div class="cms-flag__title">' + _esc(title) + '</div>' +
          (monitorHtml
            ? '<div class="cms-flag__monitors">' + monitorHtml + '</div>'
            : '') +
          (body
            ? '<div class="cms-flag__body cms-flag__body--collapsed">' + _esc(body) + '</div>' +
              '<span class="cms-read-more" onclick="var b=this.previousElementSibling;' +
                'b.classList.toggle(\'cms-flag__body--collapsed\');' +
                'this.textContent=b.classList.contains(\'cms-flag__body--collapsed\')' +
                '?\'Read more \u2192\':\'Show less \u2191\'">Read more \u2192</span>'
            : '') +
          (flag.action
            ? '<div style="margin-top:var(--space-2);font-size:var(--text-xs);font-weight:600;' +
                'color:var(--monitor-accent)">\u2192 ' + _esc(flag.action) + '</div>'
            : '') +
          (meta.length
            ? '<div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:var(--space-2)">' +
                _esc(meta.join(' \u00b7 ')) + '</div>'
            : '') +
        '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }


  /* ── Attach to AsymSections ──────────────────────────────── */
  if (window.AsymSections) {
    window.AsymSections.renderTierBar           = renderTierBar;
    window.AsymSections.renderRankedBar         = renderRankedBar;
    window.AsymSections.renderCrossMonitorFlags = renderCrossMonitorFlags;
  }

  /* Fallback direct access (defensive) */
  window.AsymTierBar           = renderTierBar;
  window.AsymRankedBar         = renderRankedBar;
  window.AsymCrossMonitorFlags = renderCrossMonitorFlags;

}());


/* ══════════════════════════════════════════════════════════════
   SHARED TOOLKIT — Ramparts UI Pattern Functions
   Extracted from Ramparts AI Frontier Monitor (2026-04-12)
   Attached to window.AsymSections
   ══════════════════════════════════════════════════════════════

   AsymSections.renderFixedSidenav(sections, subscribeUrl)
   AsymSections.renderSubscribeCTA(config)

   Scroll-spy is self-contained and activates on call.
   ══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── 1. renderFixedSidenav
          Renders a position:fixed right-hand section nav with scroll-spy.
          Bypasses WordPress sticky constraints.

          @param sections  Array of { id, label, num } objects
                           id     — matches section's HTML id attribute
                           label  — display text in the nav
                           num    — short prefix (e.g. "Δ", "01", "02")
          @param subscribeUrl  URL for the subscribe button (or null to omit)
          @param targetId  ID of element to inject the sidenav after (default: appends to body)
   ─────────────────────────────────────────────────────────── */
  function renderFixedSidenav(sections, subscribeUrl, targetId) {
    // Build links
    var linksHtml = sections.map(function (s) {
      return '<a id="rnav-' + s.id + '" href="#' + s.id + '" class="asym-sidenav__link"' +
        ' onclick="event.preventDefault();var el=document.getElementById(\'' + s.id + '\');if(el)el.scrollIntoView({behavior:\'smooth\',block:\'start\'})">' +
        '<span class="asym-sidenav__num">' + s.num + '</span>' + s.label +
        '</a>';
    }).join('\n');

    // Subscribe panel
    var subscribeHtml = subscribeUrl ? (
      '<div class="asym-sidenav__subscribe">' +
        '<div class="asym-sidenav__subscribe-label">Weekly Digest</div>' +
        '<a href="' + subscribeUrl + '" class="asym-sidenav__subscribe-btn">↯ Subscribe Free</a>' +
      '</div>'
    ) : '';

    var html = '<div class="asym-sidenav" id="asym-sidenav" aria-label="Section navigation">' +
      '<div class="asym-sidenav__label">Modules</div>' +
      '<nav id="asym-sidenav-links" style="display:flex;flex-direction:column">' + linksHtml + '</nav>' +
      subscribeHtml +
      '</div>';

    // Inject
    var target = targetId ? document.getElementById(targetId) : null;
    var wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    if (target) {
      target.parentNode.insertBefore(wrapper.firstChild, target.nextSibling);
    } else {
      document.body.appendChild(wrapper.firstChild);
    }

    // Scroll-spy
    var ids = sections.map(function (s) { return s.id; });
    var active = null;

    function setActive(id) {
      if (id === active) return;
      if (active) {
        var prev = document.getElementById('rnav-' + active);
        if (prev) prev.classList.remove('is-active');
      }
      active = id;
      if (id) {
        var el = document.getElementById('rnav-' + id);
        if (el) el.classList.add('is-active');
      }
    }

    function onScroll() {
      var offset = window.innerHeight * 0.35;
      var current = null;
      for (var i = ids.length - 1; i >= 0; i--) {
        var sec = document.getElementById(ids[i]);
        if (sec && sec.getBoundingClientRect().top <= offset) {
          current = ids[i];
          break;
        }
      }
      setActive(current || ids[0]);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── 2. renderSubscribeCTA
          Renders a teal CTA block — card or full-bleed variant.

          @param config {
            variant:      'card' | 'fullbleed'  (default: 'fullbleed')
            eyebrow:      string  (default: 'Weekly Digest')
            heading:      string
            body:         string
            primaryUrl:   string
            primaryLabel: string  (default: '↯ Subscribe Free')
            ghostUrl:     string | null
            ghostLabel:   string | null
            footnote:     string | null
          }
          @param targetId  ID of element to insert the CTA before (or append to body)
   ─────────────────────────────────────────────────────────── */
  function renderSubscribeCTA(config, targetId) {
    var c = config || {};
    var variant = c.variant === 'card' ? 'asym-cta--card' : 'asym-cta--fullbleed';

    var ghostHtml = c.ghostUrl ? (
      '<a href="' + c.ghostUrl + '" class="asym-cta__btn-ghost">' + (c.ghostLabel || 'Learn More') + '</a>'
    ) : '';

    var footnoteHtml = c.footnote ? (
      '<p class="asym-cta__footnote">' + c.footnote + '</p>'
    ) : '';

    var html = '<div class="asym-cta ' + variant + '">' +
      '<div class="asym-cta__inner">' +
        '<div class="asym-cta__eyebrow">' + (c.eyebrow || 'Weekly Digest') + '</div>' +
        '<h2 class="asym-cta__heading">' + (c.heading || '') + '</h2>' +
        '<p class="asym-cta__body">' + (c.body || '') + '</p>' +
        '<div class="asym-cta__actions">' +
          '<a href="' + (c.primaryUrl || '#') + '" class="asym-cta__btn-primary">' +
            (c.primaryLabel || '↯ Subscribe Free') +
          '</a>' +
          ghostHtml +
        '</div>' +
        footnoteHtml +
      '</div>' +
    '</div>';

    var target = targetId ? document.getElementById(targetId) : null;
    var wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    var node = wrapper.firstChild;
    if (target) {
      target.parentNode.insertBefore(node, target);
    } else {
      document.body.appendChild(node);
    }
  }

  /* ── Attach to AsymSections ── */
  if (window.AsymSections) {
    window.AsymSections.renderFixedSidenav = renderFixedSidenav;
    window.AsymSections.renderSubscribeCTA = renderSubscribeCTA;
  }

}());

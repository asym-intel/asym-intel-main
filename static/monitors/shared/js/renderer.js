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
      html += '<div style="margin-top:var(--space-3)">' +
        '<a class="source-link" href="' + esc(obj.source_url) + '" target="_blank" rel="noopener">Source →</a>' +
      '</div>';
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

  /* ── Public API ─────────────────────────────────────────────── */
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
    renderEscalationLog: renderEscalationLog
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


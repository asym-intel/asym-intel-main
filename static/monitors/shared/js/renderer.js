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

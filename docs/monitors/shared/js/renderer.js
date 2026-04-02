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

  /* ── Source label map: domain → short display name ── */
  var SOURCE_LABEL_MAP = [
    /* Asym-intel internal monitor links */
    { match: /asym-intel\.info\/monitors\/democratic-integrity/,      label: 'WDM Monitor' },
    { match: /asym-intel\.info\/monitors\/macro-monitor/,             label: 'GMM Monitor' },
    { match: /asym-intel\.info\/monitors\/fimi-cognitive-warfare/,     label: 'FCW Monitor' },
    { match: /asym-intel\.info\/monitors\/european-strategic-autonomy/,label: 'ESA Monitor' },
    { match: /asym-intel\.info\/monitors\/ai-governance/,             label: 'AGM Monitor' },
    { match: /asym-intel\.info\/monitors\/environmental-risks/,       label: 'ERM Monitor' },
    { match: /asym-intel\.info\/monitors\/conflict-escalation/,       label: 'SCEM Monitor' },
    { match: /asym-intel\.info/,                                       label: 'asym-intel.info' },
    /* News & media */
    { match: /reuters\.com/,              label: 'Reuters' },
    { match: /bloomberg\.com/,            label: 'Bloomberg' },
    { match: /ft\.com/,                   label: 'FT' },
    { match: /wsj\.com/,                  label: 'WSJ' },
    { match: /nytimes\.com/,              label: 'NYT' },
    { match: /washingtonpost\.com/,       label: 'Washington Post' },
    { match: /theguardian\.com/,          label: 'The Guardian' },
    { match: /bbc\.co\.uk|bbc\.com/,      label: 'BBC' },
    { match: /politico\.eu|politico\.com/,label: 'Politico' },
    { match: /euobserver\.com/,           label: 'EUobserver' },
    { match: /euronews\.com/,             label: 'Euronews' },
    { match: /cnbc\.com/,                 label: 'CNBC' },
    { match: /apnews\.com/,               label: 'AP News' },
    { match: /axios\.com/,                label: 'Axios' },
    { match: /semafor\.com/,              label: 'Semafor' },
    /* Intelligence & research */
    { match: /eeas\.europa\.eu/,          label: 'EEAS' },
    { match: /ec\.europa\.eu/,            label: 'European Commission' },
    { match: /europa\.eu/,                label: 'EU' },
    { match: /understandingwar\.org/,     label: 'ISW' },
    { match: /iswresearch\.org/,          label: 'ISW' },
    { match: /dfrlab\.org/,               label: 'DFRLab' },
    { match: /bellingcat\.com/,           label: 'Bellingcat' },
    { match: /icj-cij\.org/,              label: 'ICJ' },
    { match: /un\.org/,                   label: 'UN' },
    { match: /unfccc\.int/,               label: 'UNFCCC' },
    { match: /nato\.int/,                 label: 'NATO' },
    { match: /iiss\.org/,                 label: 'IISS' },
    { match: /cfr\.org/,                  label: 'CFR' },
    { match: /chathamhouse\.org/,         label: 'Chatham House' },
    { match: /ecfr\.eu/,                  label: 'ECFR' },
    { match: /v-dem\.net/,                label: 'V-Dem' },
    { match: /civicus\.org/,              label: 'CIVICUS' },
    { match: /scotusblog\.com/,           label: 'SCOTUSblog' },
    { match: /politpro\.eu/,              label: 'PolitPro' },
    { match: /mi5\.gov\.uk/,              label: 'MI5' },
    { match: /protectdefenders\.eu/,      label: 'ProtectDefenders' },
    { match: /euromaidanpress\.com/,      label: 'Euromaidan Press' },
    /* Finance & macro */
    { match: /federalreserve\.gov/,       label: 'Federal Reserve' },
    { match: /imf\.org/,                  label: 'IMF' },
    { match: /worldbank\.org/,            label: 'World Bank' },
    { match: /bls\.gov/,                  label: 'BLS' },
    { match: /eia\.gov/,                  label: 'EIA' },
    { match: /ismworld\.org/,             label: 'ISM' },
    { match: /tradingeconomics\.com/,     label: 'Trading Economics' },
    { match: /trepp\.com/,                label: 'Trepp' },
    { match: /coface\.com/,               label: 'Coface' },
    { match: /edwardconard\.com/,         label: 'Conrad Macro' },
    /* Science & environment */
    { match: /rapid\.ac\.uk/,             label: 'RAPID Array' },
    { match: /nsidc\.org/,                label: 'NSIDC' },
    { match: /globalforestwatch\.org/,    label: 'Global Forest Watch' },
    { match: /gml\.noaa\.gov/,            label: 'NOAA GML' },
    { match: /noaa\.gov/,                 label: 'NOAA' },
    { match: /nasa\.gov/,                 label: 'NASA' },
    { match: /ipbes\.net/,                label: 'IPBES' },
    { match: /iea\.org/,                  label: 'IEA' },
    { match: /nature\.com/,               label: 'Nature' },
    { match: /science\.org/,              label: 'Science' },
    { match: /arxiv\.org/,                label: 'arXiv' },
    { match: /fews\.net/,                 label: 'FEWS NET' },
    { match: /icj-cij\.org/,              label: 'ICJ' },
    { match: /isa\.org\.jm/,              label: 'ISA' },
    /* Tech */
    { match: /about\.fb\.com/,            label: 'Meta' },
    { match: /blog\.google/,              label: 'Google' },
    { match: /openai\.com/,               label: 'OpenAI' },
    { match: /anthropic\.com/,            label: 'Anthropic' },
    { match: /deepmind\.google/,          label: 'DeepMind' },
    { match: /military\.com/,             label: 'Military.com' },
    { match: /nber\.org/,                 label: 'NBER' },
    { match: /alphafold\.ebi\.ac\.uk/,   label: 'AlphaFold' },
    { match: /wikipedia\.org/,            label: 'Wikipedia' },
  ];

  /**
   * AsymRenderer.sourceLabel(url)
   * Returns a short human-readable label for a source URL.
   * Falls back to the bare hostname if no match.
   * Usage: AsymRenderer.sourceLabel('https://reuters.com/...') → 'Reuters'
   */
  function sourceLabel(url) {
    if (!url) return 'Source';
    for (var i = 0; i < SOURCE_LABEL_MAP.length; i++) {
      if (SOURCE_LABEL_MAP[i].match.test(url)) {
        return SOURCE_LABEL_MAP[i].label;
      }
    }
    // Fallback: extract hostname
    try {
      var m = url.match(/^https?:\/\/(?:www\.)?([^/]+)/);
      return m ? m[1] : 'Source';
    } catch (e) { return 'Source'; }
  }

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
        '<a class="source-link" href="' + esc(obj.source_url) + '" target="_blank" rel="noopener">' + sourceLabel(obj.source_url) + ' →</a>' +
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
    sourceLabel: sourceLabel,
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

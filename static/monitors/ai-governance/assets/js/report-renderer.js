/* ============================================================
   report-renderer.js — Artificial Intelligence Monitor (asym-intel.info)
   Renders all 15 modules from JSON into the report page.
   ============================================================ */

const REPORT_PATH = 'data/report-latest.json';

/* ── Helpers ───────────────────────────────────────────────── */
function esc(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function sourceLink(label, url) {
  if (!url) return esc(label);
  return `<a class="source-link" href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
}

function badge(text, cls) {
  return `<span class="badge badge--${esc(cls)}">${esc(text)}</span>`;
}

function callout(label, body, cls) {
  return `<div class="callout callout--${esc(cls)}">
    <div class="callout__label">${esc(label)}</div>
    <div>${body}</div>
  </div>`;
}

function noContent(msg) {
  return `<p class="loading-state">${esc(msg || 'No material developments this week.')}</p>`;
}

/* Filter out placeholder array entries — upstream data sometimes contains `[{}]`
   (empty object) as a "no content this cycle" marker that still passes the
   permissive schema validation. Without this, renderers see a non-empty
   array and emit a section header + an empty card shell.

   An entry is "non-empty" if it's a primitive (string/number/bool) with any
   value, or an object/array with at least one own key whose value is itself
   non-empty (recursive). Strings are trimmed before the empty-check. */
function isMeaningful(v) {
  if (v == null) return false;
  if (typeof v === 'string') return v.trim().length > 0;
  if (typeof v === 'number' || typeof v === 'boolean') return true;
  if (Array.isArray(v)) return v.some(isMeaningful);
  if (typeof v === 'object') return Object.values(v).some(isMeaningful);
  return false;
}

function nonEmpty(arr) {
  if (!Array.isArray(arr)) return [];
  return arr.filter(isMeaningful);
}

/* ── M00 — The Signal ──────────────────────────────────────── */
function renderM0(data) {
  const m = data.module_0;
  if (!m || !m.body) return noContent();
  return `<div class="signal-block">
    <div class="signal-block__label">The Signal · Editor's Assessment</div>
    <p>${esc(m.body)}</p>
  </div>`;
}

/* ── M01 — Executive Insight ───────────────────────────────── */
function renderM1(data) {
  const m = data.module_1;
  if (!m) return noContent();

  function renderItems(items, offset) {
    items = nonEmpty(items);
    if (!items.length) return '<p class="text-muted text-sm">None this week.</p>';
    return items.map(function (item, i) {
      const src = item.source_url
        ? `<a class="source-link" href="${esc(item.source_url)}" target="_blank" rel="noopener">${esc(item.source_label || 'Source')}</a>`
        : '';
      return `<div class="insight-item">
        <div class="insight-item__num">${offset + i + 1}</div>
        <div class="insight-item__body">
          <div class="insight-item__title">${esc(item.headline || item.title)}</div>
          <div class="insight-item__detail">${esc(item.detail || item.summary || '')}${src ? ' ' + src : ''}</div>
        </div>
      </div>`;
    }).join('');
  }

  return `<div class="insight-grid">
    <div class="insight-panel">
      <div class="insight-panel__header">Mainstream · Items 1–5</div>
      ${renderItems(m.mainstream, 0)}
    </div>
    <div class="insight-panel">
      <div class="insight-panel__header">Underweighted · Items 6–10</div>
      ${renderItems(m.underweighted, 5)}
    </div>
  </div>`;
}

/* ── M02 — Model Frontier ──────────────────────────────────── */
function renderM2(data) {
  const m = data.module_2;
  if (!m) return noContent();
  let html = '';

  const models = nonEmpty(m.models);
  if (models.length === 0) {
    html += noContent('No confirmed model releases this week.');
  } else {
    html += models.map(function (model) {
      const src = model.source_url
        ? `<a class="source-link" href="${esc(model.source_url)}" target="_blank" rel="noopener">${esc(model.source_label || 'Source')}</a>`
        : '';
      const arch = model.architecture ? badge(model.architecture, 'muted') : '';
      const flags = (model.flags || []).map(function (f) {
        return badge(f, 'amber');
      }).join(' ');
      return `<div class="card">
        <div class="card__label">${esc(model.lab || '')} ${arch} ${flags}</div>
        <div class="card__title">${esc(model.name)}</div>
        <div class="card__body">${esc(model.summary || '')}${src ? ' ' + src : ''}</div>
        ${model.asymmetric ? callout('Asymmetric Signal', esc(model.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  const benchmarks = nonEmpty(m.benchmarks_table);
  if (benchmarks.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Benchmark Movements</div>
    <table class="data-table">
      <thead><tr>
        <th>Model</th><th>Benchmark</th><th>Score</th><th>Prior</th><th>Source</th>
      </tr></thead>
      <tbody>
        ${benchmarks.map(function (row) {
          return `<tr>
            <td class="mono">${esc(row.model)}</td>
            <td>${esc(row.benchmark)}</td>
            <td class="mono">${esc(row.score)}</td>
            <td class="mono">${esc(row.prior || '—')}</td>
            <td>${row.source_url ? sourceLink(row.source_label || 'Link', row.source_url) : '—'}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
  }

  return html;
}

/* ── M03 — Investment & M&A ────────────────────────────────── */
function renderM3(data) {
  const m = data.module_3;
  if (!m) return noContent();
  let html = '';

  const fundingRounds = nonEmpty(m.funding_rounds);
  const strategicDeals = nonEmpty(m.strategic_deals);
  const energyWall = nonEmpty(m.energy_wall);

  if (fundingRounds.length) {
    html += `<div class="section-label">Funding Rounds (&gt;$50M)</div>`;
    html += fundingRounds.map(function (round) {
      const src = round.source_url ? sourceLink(round.source_label || 'Source', round.source_url) : '';
      return `<div class="card">
        <div class="card__label">${esc(round.sector || '')} · ${esc(round.stage || '')} · ${esc(round.date || '')}</div>
        <div class="card__title">${esc(round.company)} — ${esc(round.amount)}</div>
        <div class="card__body">${esc(round.summary || '')}${src ? ' ' + src : ''}</div>
        ${round.energy_wall_flag ? callout('⚡ Energy Wall Signal', esc(round.energy_wall_flag), 'signal') : ''}
        ${round.asymmetric ? callout('Asymmetric Signal', esc(round.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  if (strategicDeals.length) {
    html += `<div class="divider"></div><div class="section-label">Strategic Deals & M&A</div>`;
    html += strategicDeals.map(function (deal) {
      return `<div class="card">
        <div class="card__label">${esc(deal.type || 'Deal')} · ${esc(deal.date || '')}</div>
        <div class="card__title">${esc(deal.parties || deal.title)}</div>
        <div class="card__body">${esc(deal.summary || '')} ${deal.source_url ? sourceLink(deal.source_label || 'Source', deal.source_url) : ''}</div>
        ${deal.asymmetric ? callout('Asymmetric Signal', esc(deal.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  if (energyWall.length) {
    html += `<div class="divider"></div><div class="section-label">⚡ Energy Wall</div>`;
    html += energyWall.map(function (item) {
      return `<div class="card">
        <div class="card__label">${esc(item.category || 'Infrastructure')}</div>
        <div class="card__title">${esc(item.company)} — ${esc(item.amount || item.description || '')}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
      </div>`;
    }).join('');
  }

  return html || noContent();
}

/* ── M04 — Sector Penetration ──────────────────────────────── */
function renderM4(data) {
  const m = data.module_4;
  if (!m) return noContent();
  const sectors = nonEmpty(m.sectors);
  if (!sectors.length) return noContent();

  const statusClass = { 'Accelerating': 'signal', 'Stalling': 'amber', 'Emerging': 'primary', 'Monitoring': 'muted' };

  return sectors.map(function (sector) {
    const cls = statusClass[sector.status] || 'muted';
    return `<div class="card">
      <div class="card__label">${esc(sector.name)} ${badge(sector.status || '', cls)}</div>
      <div class="card__body">${esc(sector.summary || '')}</div>
      ${sector.asymmetric ? callout('Asymmetric Signal', esc(sector.asymmetric), 'asymmetric') : ''}
      ${sector.stealth ? callout('Stealth Deployment', esc(sector.stealth), 'threshold') : ''}
    </div>`;
  }).join('');
}

/* ── M05 — European & China Watch ─────────────────────────── */
function renderM5(data) {
  const m = data.module_5;
  if (!m) return noContent();
  let html = '';

  const european = nonEmpty(m.european);
  const china = nonEmpty(m.china);

  if (european.length) {
    html += `<div class="section-label">European Watch</div>`;
    html += european.map(function (item) {
      return `<div class="card">
        <div class="card__label">${esc(item.jurisdiction || 'EU')} · ${esc(item.category || '')}</div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
        ${item.standards_vacuum ? callout('Standards Vacuum Signal', esc(item.standards_vacuum), 'threshold') : ''}
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  if (china.length) {
    html += `<div class="divider"></div><div class="section-label">China Watch</div>`;
    html += china.map(function (item) {
      return `<div class="card">
        <div class="card__label">China · ${esc(item.category || '')}</div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
        ${item.ciyuan_flag ? callout('Ciyuan Signal', esc(item.ciyuan_flag), 'threshold') : ''}
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  return html || noContent();
}

/* ── M06 — AI in Science ───────────────────────────────────── */
function renderM6(data) {
  const m = data.module_6;
  if (!m) return noContent();
  let html = '';

  function renderSciItem(item) {
    const src = item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : '';
    return `<div class="card">
      <div class="card__label">${esc(item.domain || '')} · ${esc(item.lab || '')} ${item.landmark_programme ? badge(item.landmark_programme, 'primary') : ''}</div>
      <div class="card__title">${esc(item.title)}</div>
      <div class="card__body">
        ${esc(item.summary || '')}${src ? ' ' + src : ''}
        ${item.capability ? `<div class="divider"></div><strong>Capability:</strong> ${esc(item.capability)}` : ''}
        ${item.reliability_flags ? `<br><strong>Reliability:</strong> ${esc(item.reliability_flags)}` : ''}
        ${item.institutional_partners ? `<br><strong>Partners:</strong> ${esc(item.institutional_partners)}` : ''}
      </div>
      ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
    </div>`;
  }

  const thresholdEvents = nonEmpty(m.threshold_events);
  const programmeUpdates = nonEmpty(m.programme_updates);
  const arxivHighlights = nonEmpty(m.arxiv_highlights);
  const drillDownResults = nonEmpty(m.drill_down_results);

  if (thresholdEvents.length) {
    html += `<div class="section-label">Threshold Events</div>`;
    html += thresholdEvents.map(renderSciItem).join('');
  }
  if (programmeUpdates.length) {
    html += `<div class="divider"></div><div class="section-label">Programme Updates</div>`;
    html += programmeUpdates.map(renderSciItem).join('');
  }
  if (arxivHighlights.length) {
    html += `<div class="divider"></div><div class="section-label">arXiv / Preprint Highlights</div>`;
    html += arxivHighlights.map(renderSciItem).join('');
  }
  if (drillDownResults.length) {
    html += `<div class="divider"></div><div class="section-label">Drill-Down Results</div>`;
    html += drillDownResults.map(renderSciItem).join('');
  }

  return html || noContent();
}

/* ── M07 — Risk Indicators: 2028 ──────────────────────────── */
function renderM7(data) {
  const m = data.module_7;
  if (!m) return noContent();
  const vectors = nonEmpty(m.vectors);
  if (!vectors.length) return noContent();

  const riskCls = { 'HIGH': 'high', 'ELEVATED': 'elevated', 'VACUUM': 'vacuum' };

  return `<div class="risk-grid">
    ${vectors.map(function (v) {
      const cls = riskCls[v.level] || 'elevated';
      return `<div class="risk-card risk-card--${cls}">
        <div class="risk-card__vector">${badge(v.level || '', 'risk-' + cls)} ${esc(v.vector)}</div>
        <div class="risk-card__body">${esc(v.summary || '')} ${v.source_url ? sourceLink(v.source_label || 'Source', v.source_url) : ''}</div>
        ${v.asymmetric ? `<div style="margin-top:var(--space-3);font-size:var(--text-xs);color:var(--color-text-muted)">${esc(v.asymmetric)}</div>` : ''}
      </div>`;
    }).join('')}
  </div>`;
}

/* ── M08 — Military AI Watch ───────────────────────────────── */
function renderM8_Military(data) {
  const m = data.module_8;
  if (!m) return noContent();
  const items = nonEmpty(m.items);
  if (!items.length) return noContent();

  const catBadge = { procurement: 'muted', doctrine: 'primary', capability: 'amber', international: 'signal' };

  return items.map(function (item) {
    const cat = item.category || 'procurement';
    return `<div class="card">
      <div class="card__label">${badge(cat, catBadge[cat] || 'muted')} ${esc(item.jurisdiction || '')}</div>
      <div class="card__title">${esc(item.title)}</div>
      <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
      ${item.ihl_friction ? callout('IHL Friction', esc(item.ihl_friction), 'threshold') : ''}
      ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
    </div>`;
  }).join('');
}

/* ── M09 — Law & Litigation ──────────────────────────────────── */
function renderM9(data) {
  const m = data.module_9;
  if (!m) return noContent();
  let html = '';

  function renderItemList(items, sectionLabel) {
    items = nonEmpty(items);
    if (!items.length) return '';
    let out = sectionLabel ? `<div class="section-label">${sectionLabel}</div>` : '';
    out += items.map(function (item) {
      return `<div class="card">
        <div class="card__label">${esc(item.jurisdiction || item.category || '')} · ${esc(item.domain || item.date || '')}</div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">
          ${esc(item.summary || '')} ${item.source_url ? sourceLink('Source', item.source_url) : ''}
          ${item.obligations ? `<br><strong>Obligations:</strong> ${esc(item.obligations)}` : ''}
          ${item.timeline ? `<br><strong>Timeline:</strong> ${esc(item.timeline)}` : ''}
        </div>
        ${item.friction ? callout('⚙️ Technical Friction', esc(item.friction), 'friction') : ''}
        ${item.standards_vacuum ? callout('Standards Vacuum', esc(item.standards_vacuum), 'threshold') : ''}
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
    return out;
  }

  // Support both new schema (law_highlights / standards_highlights / litigation_highlights)
  // and legacy schema (new_developments)
  const lawHighlights = nonEmpty(m.law_highlights);
  const standardsHighlights = nonEmpty(m.standards_highlights);
  const litigationHighlights = nonEmpty(m.litigation_highlights);
  const newDevelopments = nonEmpty(m.new_developments);

  if (lawHighlights.length) {
    html += renderItemList(lawHighlights, 'Law');
  }
  if (standardsHighlights.length) {
    html += `<div class="divider"></div>` + renderItemList(standardsHighlights, 'Standards');
  }
  if (litigationHighlights.length) {
    html += `<div class="divider"></div>` + renderItemList(litigationHighlights, 'Litigation');
  }
  if (!lawHighlights.length && newDevelopments.length) {
    html += renderItemList(newDevelopments, '');
  }
  // EU AI Act Layered System
  if (m.eu_ai_act_layered) {
    const layers = m.eu_ai_act_layered;
    html += `<div class="divider"></div>
    <div class="section-label">EU AI Act — Layered Tracker</div>
    <table class="data-table">
      <thead><tr><th>Layer</th><th>Status</th><th>Note</th></tr></thead>
      <tbody>`;
    const layerNames = [
      'AI Act Text', 'Delegated / Implementing Acts', 'Harmonised Standards (CEN-CENELEC JTC21)',
      'GPAI Code of Practice', 'National Enforcement (NCAs)', 'AI Office Supervisory Decisions',
      'Digital Omnibus Trilogue'
    ];
    (Array.isArray(layers) ? layers : Object.values(layers)).forEach(function (l, i) {
      html += `<tr>
        <td class="mono">${esc(layerNames[i] || ('Layer ' + i))}</td>
        <td>${l.status ? badge(l.status, l.status === 'Active' ? 'signal' : l.status === 'Delayed' ? 'amber' : 'muted') : '—'}</td>
        <td class="text-sm">${esc(l.note || l.summary || '—')}</td>
      </tr>`;
    });
    html += `</tbody></table>`;
  }

  // Country Grid
  const countryGrid = nonEmpty(data.country_grid);
  if (countryGrid.length) {
    html += `<div class="divider"></div>
    <div class="section-label" id="country-grid">Country Grid</div>
    <table class="country-grid-table data-table">
      <thead><tr>
        <th>Country</th><th>Status</th><th>Key Development</th><th>Change</th><th>Source</th>
      </tr></thead>
      <tbody>
        ${countryGrid.map(function (row) {
          return `<tr>
            <td>${esc(row.country)}</td>
            <td>${row.status ? badge(row.status, row.status === 'Active' ? 'signal' : 'muted') : '—'}</td>
            <td class="text-sm">${esc(row.development || row.note || '—')}</td>
            <td>${esc(row.change_flag || '—')}</td>
            <td>${row.source_url ? sourceLink(row.source_label || 'Link', row.source_url) : '—'}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
  }

  const countryGridWatch = nonEmpty(data.country_grid_watch);
  if (countryGridWatch.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Country Grid Watch</div>
    <table class="data-table">
      <thead><tr><th>Country</th><th>Signal</th><th>Note</th></tr></thead>
      <tbody>
        ${countryGridWatch.map(function (row) {
          return `<tr>
            <td>${esc(row.country)}</td>
            <td>${badge(row.signal || 'Watch', 'amber')}</td>
            <td class="text-sm">${esc(row.note || '—')}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
  }

  return html || noContent();
}

/* ── M10 — AI Governance ───────────────────────────────────── */
function renderM10_AIG(data) {
  const m = data.module_10;
  if (!m) return noContent();
  let html = '';

  function renderGovItems(items, label) {
    items = nonEmpty(items);
    if (!items.length) return '';
    return `<div class="section-label">${esc(label)}</div>` +
      items.map(function (item) {
        return `<div class="card">
          <div class="card__label">${esc(item.category || '')} · ${esc(item.jurisdiction || '')}</div>
          <div class="card__title">${esc(item.title)}</div>
          <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
          ${item.accountability_friction ? callout('Accountability Friction', esc(item.accountability_friction), 'threshold') : ''}
          ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
        </div>`;
      }).join('');
  }

  html += renderGovItems(m.international_soft_law, 'International Soft Law');
  if (nonEmpty(m.corporate_governance).length) html += '<div class="divider"></div>';
  html += renderGovItems(m.corporate_governance, 'Corporate Governance');
  if (nonEmpty(m.product_liability).length) html += '<div class="divider"></div>';
  html += renderGovItems(m.product_liability, 'Product Liability Tracker');
  if (nonEmpty(m.algorithmic_accountability).length) html += '<div class="divider"></div>';
  html += renderGovItems(m.algorithmic_accountability, 'Algorithmic Accountability');
  if (nonEmpty(m.governance_gaps).length) html += '<div class="divider"></div>';
  html += renderGovItems(m.governance_gaps, 'Governance Gaps');

  return html || noContent();
}

/* ── M11 — Ethics & Accountability ────────────────────────── */
function renderM11_Ethics(data) {
  const m = data.module_11;
  if (!m) return noContent();
  const items = nonEmpty(m.items);
  if (!items.length) return noContent();

  const catCls = {
    corporate_accountability: 'threshold',
    standards: 'primary',
    lab_ethics: 'amber',
    research: 'signal'
  };

  return items.map(function (item) {
    const cls = catCls[item.category] || 'muted';
    return `<div class="card">
      <div class="card__label">${badge(item.category || 'ethics', cls)}</div>
      <div class="card__title">${esc(item.title)}</div>
      <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
      ${item.accountability_friction ? callout('Accountability Friction', esc(item.accountability_friction), 'threshold') : ''}
      ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
    </div>`;
  }).join('');
}

/* ── M12 — Information Operations ───────────────────────────── */
function renderM12(data) {
  const m = data.module_12;
  if (!m) return noContent();
  let html = '';

  const actorCls = {
    state_actor: 'red', synthetic_media: 'amber', narrative_manipulation: 'threshold',
    platform_response: 'signal', detection: 'primary'
  };

  const m12Items = nonEmpty(m.items);
  if (m12Items.length) {
    html += m12Items.map(function (item) {
      const cls = actorCls[item.category] || 'muted';
      return `<div class="card">
        <div class="card__label">
          ${badge(item.category || '', cls)}
          ${esc(item.actor_type || '')}
          ${item.region ? ' · ' + esc(item.region) : ''}
        </div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink('Source', item.source_url) : ''}</div>
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  const capabilityWatch = nonEmpty(m.capability_watch);
  if (capabilityWatch.length) {
    html += `<div class="divider"></div><div class="section-label">Capability Watch</div>`;
    html += capabilityWatch.map(function (item) {
      return `<div class="card">
        <div class="card__label">${esc(item.capability || '')}</div>
        <div class="card__body">${esc(item.detail || '')} ${item.source_url ? sourceLink('Source', item.source_url) : ''}</div>
      </div>`;
    }).join('');
  }

  const m12Flags = nonEmpty(m.asymmetric_flags);
  if (m12Flags.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Asymmetric Flags</div>
    <ul style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.8">
      ${m12Flags.map(function (f) { return `<li>${esc(f)}</li>`; }).join('')}
    </ul>`;
  }

  return html || noContent();
}

/* ── M13 — AI & Society ─────────────────────────────────────── */
function renderM13(data) {
  const m = data.module_13;
  if (!m) return noContent();
  let html = '';

  const catCls = {
    labour: 'amber', education: 'signal', public_trust: 'threshold',
    social_cohesion: 'primary', inequality: 'red', demographic: 'muted'
  };

  const m13Items = nonEmpty(m.items);
  if (m13Items.length) {
    html += m13Items.map(function (item) {
      const cls = catCls[item.category] || 'muted';
      return `<div class="card">
        <div class="card__label">
          ${badge(item.category || '', cls)}
          ${item.affected_groups ? ' · ' + esc(item.affected_groups) : ''}
        </div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink('Source', item.source_url) : ''}</div>
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  const structuralTrends = nonEmpty(m.structural_trends);
  if (structuralTrends.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Structural Trends</div>
    <ul style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.8">
      ${structuralTrends.map(function (t) { return `<li>${esc(t)}</li>`; }).join('')}
    </ul>`;
  }

  const m13Flags = nonEmpty(m.asymmetric_flags);
  if (m13Flags.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Asymmetric Flags</div>
    <ul style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.8">
      ${m13Flags.map(function (f) { return `<li>${esc(f)}</li>`; }).join('')}
    </ul>`;
  }

  return html || noContent();
}

/* ── M14 — AI & Power Structures ─────────────────────────── */
function renderM14(data) {
  const m = data.module_14;
  if (!m) return noContent();
  let html = '';

  const catCls = {
    infrastructure_control: 'red',
    compute_concentration: 'amber',
    corporate_power: 'amber',
    geopolitical: 'threshold',
    regulatory_capture: 'threshold',
    access_asymmetry: 'primary',
    market_structure: 'muted'
  };

  const m14Items = nonEmpty(m.items);
  if (m14Items.length) {
    html += m14Items.map(function (item) {
      const cls = catCls[item.category] || 'muted';
      return `<div class="card">
        <div class="card__label">${badge(item.category || '', cls)} ${esc(item.actors || item.region || '')}</div>
        <div class="card__title">${esc(item.title)}</div>
        <div class="card__body">${esc(item.summary || '')} ${item.source_url ? sourceLink(item.source_label || 'Source', item.source_url) : ''}</div>
        ${item.power_implication ? callout('Power Implication', esc(item.power_implication), 'threshold') : ''}
        ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
      </div>`;
    }).join('');
  }

  const concentrationIndex = nonEmpty(m.concentration_index);
  if (concentrationIndex.length) {
    html += `<div class="divider"></div><div class="section-label">Concentration Index</div>
    <table class="data-table">
      <thead><tr><th>Domain</th><th>Top Actors</th><th>Trend</th><th>Note</th></tr></thead>
      <tbody>
        ${concentrationIndex.map(function (row) {
          const trendCls = row.trend === 'Concentrating' ? 'red' : row.trend === 'Fragmenting' ? 'signal' : 'muted';
          return `<tr>
            <td class="mono">${esc(row.domain)}</td>
            <td class="text-sm">${esc(row.top_actors || '—')}</td>
            <td>${badge(row.trend || '—', trendCls)}</td>
            <td class="text-sm">${esc(row.note || '—')}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
  }

  const m14Flags = nonEmpty(m.asymmetric_flags);
  if (m14Flags.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Asymmetric Flags</div>
    <ul style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.8">
      ${m14Flags.map(function (f) { return `<li>${esc(f)}</li>`; }).join('')}
    </ul>`;
  }

  return html || noContent();
}

/* ── M15 — Personnel & Org Watch ──────────────────────────── */
function renderM15(data) {
  const m = data.module_15;
  if (!m) return noContent();
  let html = '';

  function renderMovements(items, label) {
    items = nonEmpty(items);
    if (!items.length) return '';
    const typeCls = { appointment: 'signal', departure: 'amber', strategic_signal: 'threshold' };
    return `<div class="section-label">${esc(label)}</div>` +
      items.map(function (item) {
        const cls = typeCls[item.type] || 'muted';
        const aisi = item.aisi_pipeline ? `<div class="callout callout--threshold" style="margin-top:var(--space-3)">
          <div class="callout__label">🔄 AISI Pipeline</div>
          <div>${esc(item.aisi_pipeline)}</div>
        </div>` : '';
        return `<div class="card">
          <div class="card__label">${badge(item.type || '', cls)}</div>
          <div class="card__title">${esc(item.name)} — ${esc(item.role_to || item.significance || '')}</div>
          <div class="card__body">
            ${esc(item.role_from ? 'From: ' + item.role_from : '')}
            ${item.significance ? '<br>' + esc(item.significance) : ''}
            ${item.source_url ? ' ' + sourceLink(item.source_label || 'Source', item.source_url) : ''}
          </div>
          ${item.asymmetric ? callout('Asymmetric Signal', esc(item.asymmetric), 'asymmetric') : ''}
          ${aisi}
        </div>`;
      }).join('');
  }

  html += renderMovements(m.lab_movements, 'Lab Movements');
  if (nonEmpty(m.government_ai_bodies).length) html += '<div class="divider"></div>';
  html += renderMovements(m.government_ai_bodies, 'Government AI Bodies');
  if (nonEmpty(m.revolving_door).length) html += '<div class="divider"></div>';
  html += renderMovements(m.revolving_door, 'Revolving Door');

  const m15Flags = nonEmpty(m.asymmetric_flags);
  if (m15Flags.length) {
    html += `<div class="divider"></div>
    <div class="section-label">Asymmetric Flags</div>
    <ul style="font-size:var(--text-sm);color:var(--color-text-secondary);line-height:1.8">
      ${m15Flags.map(function (f) { return `<li>${esc(f)}</li>`; }).join('')}
    </ul>`;
  }

  return html || noContent();
}

/* ── Delta Strip ────────────────────────────────────────────── */
function renderDeltaStrip(data) {
  if (!data.delta_strip || !data.delta_strip.length) return;
  const el = document.getElementById('delta-strip');
  if (!el) return;
  el.innerHTML = `<div class="section-label">Δ Top Signals This Issue</div>
    <div style="display:flex;flex-direction:column;gap:var(--space-2)">
      ${data.delta_strip.map(function (d) {
        // d is an object: { rank, title, module, delta_type, one_line }
        if (typeof d === 'string') return `<div class="delta-item"><span class="delta-item__text">${esc(d)}</span></div>`;
        return `<div class="delta-item" style="display:flex;gap:var(--space-3);align-items:baseline;padding:var(--space-2) 0;border-bottom:1px solid var(--color-border)">
          <span style="font-family:var(--font-mono);font-size:var(--text-xs);color:var(--color-text-faint);min-width:1.8rem;flex-shrink:0">${esc(String(d.rank || ''))}</span>
          <span style="font-family:var(--font-mono);font-size:var(--text-xs);color:var(--color-primary);min-width:2.8rem;flex-shrink:0">${esc(d.module || '')}</span>
          <span style="flex:1">
            <strong style="font-size:var(--text-sm)">${esc(d.title || '')}</strong>
            ${d.delta_type ? `<span style="font-family:var(--font-mono);font-size:var(--text-xs);color:var(--color-text-faint);margin-left:var(--space-2)">${esc(d.delta_type)}</span>` : ''}
            ${d.one_line ? `<br><span style="font-size:var(--text-sm);color:var(--color-text-secondary)">${esc(d.one_line)}</span>` : ''}
          </span>
        </div>`;
      }).join('')}
    </div>`;
}

/* ── Cross-Monitor Signals ───────────────────────────────────── */
function renderCrossMonitor(data) {
  const cmf = data.cross_monitor_flags;
  if (!cmf) return '<p class="text-muted text-sm">No material cross-monitor signals identified in this period.</p>';

  const flags = nonEmpty(cmf.flags);
  if (!flags.length) {
    return '<p class="text-muted text-sm">No material cross-monitor signals identified in this period.</p>';
  }

  const statusCls = { Active: 'signal', Monitoring: 'amber', Closed: 'muted' };

  let html = flags.map(function (f) {
    const cls = statusCls[f.status] || 'muted';
    const monitors = (f.monitors_involved || []).map(function (m) {
      return f.monitor_url
        ? `<a href="${esc(f.monitor_url)}" target="_blank" rel="noopener" style="color:var(--color-primary)">${esc(m)}</a>`
        : esc(m);
    }).join(', ');

    return `<div class="card">
      <div class="card__label">
        ${badge(f.status || 'Active', cls)}
        ${esc(f.type || '')}
        <span style="margin-left:var(--space-2);font-family:var(--font-mono);font-size:var(--text-xs);color:var(--color-text-faint)">${monitors}</span>
      </div>
      <div class="card__title">${esc(f.title || '')}</div>
      <div class="card__body">${esc(f.linkage || '')}</div>
      ${f.ai_governance_perspective ? callout('AI Governance Perspective', esc(f.ai_governance_perspective), 'asymmetric') : ''}
    </div>`;
  }).join('');

  if (cmf.updated) {
    html += `<p class="text-sm text-muted" style="margin-top:var(--space-4)">Last scanned: ${esc(cmf.updated)}</p>`;
  }

  return html;
}

/* ── Render Map ─────────────────────────────────────────────── */
function renderReport(data) {
  const renderMap = {
    'm0-content':  renderM0,
    'm1-content':  renderM1,
    'm2-content':  renderM2,
    'm3-content':  renderM3,
    'm4-content':  renderM4,
    'm5-content':  renderM5,
    'm6-content':  renderM6,
    'm7-content':  renderM7,
    'm8-content':  renderM8_Military,
    'm9-content':  renderM9,
    'm10-content': renderM10_AIG,
    'm11-content': renderM11_Ethics,
    'm12-content': renderM12,
    'm13-content': renderM13,
    'm14-content': renderM14,
    'm15-content': renderM15,
    'cross-monitor-content': renderCrossMonitor,
  };

  Object.entries(renderMap).forEach(function ([id, fn]) {
    const el = document.getElementById(id);
    if (el) {
      try {
        el.innerHTML = fn(data);
      } catch (e) {
        el.innerHTML = `<p class="text-muted text-sm">Render error: ${esc(e.message)}</p>`;
      }
    }
  });

  // Update meta
  const meta = data.meta || {};
  const titleEl = document.getElementById('report-title');
  if (titleEl) titleEl.textContent = 'Artificial Intelligence Monitor — Issue ' + (meta.issue || '') + ' · ' + (meta.week_label || '');
  const dateEl = document.getElementById('report-date');
  if (dateEl) dateEl.textContent = meta.published || '';
  const issueEl = document.getElementById('report-issue');
  if (issueEl) issueEl.textContent = 'Vol. ' + (meta.volume || 1) + ' · Issue ' + (meta.issue || '');

  renderDeltaStrip(data);
}


/* ── Bootstrap ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  fetch(REPORT_PATH)
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function (data) { renderReport(data); })
    .catch(function (err) {
      const el = document.getElementById('report-error');
      if (el) el.innerHTML = `<div class="callout callout--threshold">
        <div class="callout__label">Load Error</div>
        <div>Could not load report data: ${esc(err.message)}</div>
      </div>`;
    });
});

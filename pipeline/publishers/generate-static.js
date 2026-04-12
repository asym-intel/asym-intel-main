/**
 * Ramparts AI Frontier Monitor — Static HTML Generator
 * 
 * Generates a fully-branded, SEO-optimised, JavaScript-free static HTML page
 * from the weekly report JSON. Designed for publication at ramparts.gi/AI-frontier-monitor/
 * 
 * Usage: node generate-static.js [YYYY-MM-DD]
 * Output: data/static-report-YYYY-MM-DD.html
 */

const fs = require('fs');
const path = require('path');

const reportDate = process.argv[2] || '2026-03-26';
const dataDir = path.join(__dirname, 'ramparts-v2/data');
const data = JSON.parse(fs.readFileSync(path.join(dataDir, `report-${reportDate}.json`), 'utf8'));

const { meta, module_0, module_1, module_2, module_3, module_4, module_5,
        module_6, module_7, module_8, module_9, module_10, module_11, module_12,
        module_13, module_14,
        country_grid, country_grid_watch } = data;

const SITE_URL = 'https://ramparts.gi/AI-frontier-monitor';
const RAMPARTS_URL = 'https://ramparts.gi';
const CANONICAL = `${SITE_URL}/`;
// PDF hosted on WordPress media library: /wp-content/uploads/YYYY/MM/report-YYYY-MM-DD.pdf
const [year, month] = reportDate.split('-');
const PDF_URL = `https://ramparts.gi/wp-content/uploads/${year}/${month}/report-${reportDate}.pdf`;

/* ── Helpers ── */
function stripHtml(s) { return (s||'').replace(/<[^>]+>/g, ''); }
function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function badge(cls, text) {
  const colors = {
    teal: '#006b6f', amber: '#b45309', red: '#c0392b',
    green: '#15803d', blue: '#1d4ed8', yellow: '#d97706',
    'risk-high': '#c0392b', 'risk-elevated': '#b45309', 'risk-vacuum': '#d97706'
  };
  const bgs = {
    teal: '#e8f4f4', amber: '#fef3c7', red: '#fef2f2',
    green: '#dcfce7', blue: '#dbeafe', yellow: '#fffbeb',
    'risk-high': '#fef2f2', 'risk-elevated': '#fef3c7', 'risk-vacuum': '#fffbeb'
  };
  const c = colors[cls] || colors.teal;
  const b = bgs[cls] || bgs.teal;
  return `<span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.05em;text-transform:uppercase;background:${b};color:${c}">${text}</span>`;
}
function sourceLink(label, url) {
  if (!url) return '';
  return `<a href="${url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:4px;font-size:15px;color:#6b6860;border:1px solid #ddd;border-radius:9999px;padding:0.2em 0.7em;margin-top:10px;text-decoration:none">↗ ${label}</a>`;
}
function callout(type, label, body) {
  const styles = {
    asymmetric: { bg: '#fef3c7', border: '#b45309', labelColor: '#b45309' },
    signal: { bg: '#e8f4f4', border: '#006b6f', labelColor: '#006b6f' },
    threshold: { bg: '#fef2f2', border: '#c0392b', labelColor: '#c0392b' },
  };
  const s = styles[type] || styles.signal;
  return `<div style="padding:14px 18px;border-radius:6px;border-left:4px solid ${s.border};background:${s.bg};margin:12px 0">
    <div style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.08em;text-transform:uppercase;color:${s.labelColor};margin-bottom:6px">${label}</div>
    <p style="margin:0;font-size:17px;line-height:1.7">${body}</p>
  </div>`;
}
function card(content, style='') {
  return `<div style="background:#fff;border:1px solid #ddd;border-radius:10px;padding:22px;margin-bottom:16px;${style}">${content}</div>`;
}
function sectionHeader(num, title) {
  return `<div style="display:flex;align-items:baseline;gap:20px;margin-bottom:32px;padding-top:48px;border-top:1px solid #e5e5e5">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:clamp(2.5rem,6vw,4rem);font-weight:800;line-height:1;color:#c8d8d8;letter-spacing:-0.03em;flex-shrink:0">${num}</span>
    <h2 style="font-family:'Space Grotesk',sans-serif;font-size:clamp(1.25rem,2.5vw,1.75rem);font-weight:700;margin:0;letter-spacing:-0.01em">${title}</h2>
  </div>`;
}

/* ── Module renderers ── */
function renderM0() {
  return callout('signal', `⚡ The Signal — Week of ${meta.week_label}`, module_0.body);
}

function renderM1() {
  const item = (it, asymmetric) => card(`
    <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:14px">
      <span style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#c8d8d8;line-height:1;flex-shrink:0;min-width:2rem">${it.rank}</span>
      <div>
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0 0 4px">${it.headline}</h4>
        <span style="font-size:15px;color:#888">${it.date}</span>
      </div>
    </div>
    <p style="font-size:17px;color:#555;margin:0 0 12px">${it.body}</p>
    ${callout('asymmetric', '⚡ Asymmetric Implication', it.asymmetric)}
    ${sourceLink(it.source_label, it.source_url)}
  `, asymmetric ? 'border-left:3px solid #b45309' : '');

  return `
    <div style="margin-bottom:32px">
      <h3 style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.08em;text-transform:uppercase;color:#888;border-bottom:1px solid #eee;padding-bottom:10px;margin-bottom:18px">Items 1–5 · Mainstream High-Impact Developments</h3>
      ${module_1.mainstream.map(i => item(i, false)).join('')}
    </div>
    <div>
      <h3 style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.08em;text-transform:uppercase;color:#b45309;border-bottom:1px solid #eee;padding-bottom:10px;margin-bottom:18px">Items 6–10 · Underweighted / Asymmetric Signals</h3>
      ${module_1.underweighted.map(i => item(i, true)).join('')}
    </div>`;
}

function renderM2() {
  const models = module_2.models.map(m => card(`
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:12px">
      <div>
        <div style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.08em;text-transform:uppercase;color:#006b6f;margin-bottom:4px">${m.lab}</div>
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;margin:0 0 4px">${m.model}</h4>
        <span style="font-size:15px;color:#888">${m.date}</span>
      </div>
      ${m.architecture_flag ? badge('teal', '🏗 Architecture Innovation') : ''}
    </div>
    <p style="font-size:16px;color:#666;background:#f5f5f5;border-radius:6px;padding:10px;margin-bottom:12px">${m.architecture}</p>
    ${m.benchmarks.length ? `<table style="width:100%;border-collapse:collapse;font-size:16px;margin-bottom:12px">
      <thead><tr style="background:#f5f5f5"><th style="padding:8px;text-align:left;font-size:13px;text-transform:uppercase;letter-spacing:0.05em;color:#888">Benchmark</th><th style="padding:8px;text-align:left">Score</th><th style="padding:8px;text-align:left;color:#888">Note</th></tr></thead>
      <tbody>${m.benchmarks.map(b => `<tr style="border-bottom:1px solid #eee"><td style="padding:8px">${b.name}</td><td style="padding:8px;font-weight:700">${b.score}</td><td style="padding:8px;color:#888;font-size:15px">${b.note}</td></tr>`).join('')}</tbody>
    </table>` : ''}
    ${callout('asymmetric', '⚡ Asymmetric Flag', m.asymmetric)}
    ${sourceLink(m.source_label, m.source_url)}
  `)).join('');

  // Benchmark tables
  const bt = module_2.benchmarks_table;
  const scoreColor = { superhuman: '#15803d', 'above-human': '#006b6f', 'human-parity': '#888', baseline: '#888', fail: '#c0392b' };
  const benchTable = (title, rows, note) => `
    <div style="margin-bottom:28px">
      <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;margin-bottom:6px">${title}</h4>
      <p style="font-size:16px;color:#888;margin-bottom:10px">${note}</p>
      <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:16px">
          <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;letter-spacing:0.05em;color:#888">Model</th><th style="padding:8px 12px;text-align:left">Score</th></tr></thead>
          <tbody>${rows.map(r => `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px">${r.model}</td><td style="padding:8px 12px;font-weight:700;color:${scoreColor[r.tier]||'#333'}">${r.score}</td></tr>`).join('')}</tbody>
        </table>
      </div>
    </div>`;

  return `${models}
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:40px 0 20px">Benchmark Leaderboard — ${meta.week_label}</h3>
    ${benchTable('ARC-AGI-2 (Static Reasoning)', bt.arc_agi_2, 'Human average ~60%. Models above this line are superhuman on this benchmark.')}
    ${benchTable('ARC-AGI-3 (Interactive/Agentic)', bt.arc_agi_3, 'Humans score 100%. Frontier AI near-zero — reveals the adaptive intelligence gap.')}
    ${benchTable('GPQA Diamond (Graduate Science)', bt.gpqa_diamond, 'Human expert ceiling ~70–80%.')}`;
}

function renderM3() {
  const rounds = module_3.funding_rounds.map(r => card(`
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:12px">
      <div>
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;margin:0 0 4px">${r.company}</h4>
        <span style="font-size:15px;color:#888">${r.date} · Lead: ${r.lead}</span>
      </div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;color:#006b6f">${r.amount}</div>
    </div>
    ${r.valuation && r.valuation !== 'Undisclosed' ? `<div style="font-size:16px;color:#888;margin-bottom:8px">${r.valuation} valuation</div>` : ''}
    <p style="font-size:17px;margin:0 0 10px">${r.focus}</p>
    <div style="margin-bottom:10px">${badge(r.cursor_curve ? 'green' : r.cursor_note.startsWith('PROBABLE') ? 'amber' : 'teal', (r.cursor_curve ? '🚀' : r.cursor_note.startsWith('PROBABLE') ? '⚠️' : '—') + ' Cursor Curve')} <span style="font-size:15px;color:#888;margin-left:8px">${r.cursor_note}</span></div>
    ${callout('asymmetric', '⚡ Asymmetric Signal', r.asymmetric)}
    ${sourceLink(r.source_label, r.source_url)}
  `)).join('');

  const strategic = module_3.strategic_deals.map(d => card(`
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:10px">
      <div><h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0">${d.name}</h4>${badge('teal', d.type)}</div>
      <span style="font-size:15px;color:#888">${d.date}</span>
    </div>
    <p style="font-size:17px;margin:0">${d.detail}</p>
    ${sourceLink(d.source_label, d.source_url)}
  `)).join('');

  const secondaryRows = module_3.secondary_markets.map(s =>
    `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px;font-weight:700">${s.company}</td><td style="padding:8px 12px">${s.valuation}</td><td style="padding:8px 12px;color:#888;font-size:16px">${s.note}</td></tr>`
  ).join('');

  return `<h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:20px">Funding Rounds &gt;$50M</h3>
    ${rounds}
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:32px 0 16px">Strategic Infrastructure Deals</h3>
    ${strategic}
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:32px 0 12px">Secondary Market Valuations</h3>
    <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
      <table style="width:100%;border-collapse:collapse;font-size:17px">
        <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;letter-spacing:0.05em;color:#888">Company</th><th style="padding:8px 12px;text-align:left">Valuation</th><th style="padding:8px 12px;text-align:left">Note</th></tr></thead>
        <tbody>${secondaryRows}</tbody>
      </table>
    </div>`;
}

function renderM4() {
  const statusColors = { accelerating: '#15803d', stalling: '#b45309', emerging: '#1d4ed8' };
  const statusBgs = { accelerating: '#dcfce7', stalling: '#fef3c7', emerging: '#dbeafe' };
  return module_4.sectors.map(s => {
    const sc = s.status.toLowerCase();
    return card(`
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:10px">
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;margin:0">${s.name}</h4>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.7em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;background:${statusBgs[sc]||'#f5f5f5'};color:${statusColors[sc]||'#333'}">${s.status}</span>
      </div>
      <p style="font-size:17px;font-weight:600;margin:0 0 8px">${s.headline}</p>
      <p style="font-size:17px;color:#555;margin:0">${s.detail}</p>
      ${callout('asymmetric', '⚡ Asymmetric Signal', s.asymmetric)}
      ${sourceLink(s.source_label, s.source_url)}
    `);
  }).join('');
}

function renderM5() {
  const eu = module_5.european;
  const cn = module_5.china;
  const fundingRows = eu.funding.map(f =>
    `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px;font-weight:700">${f.company}</td><td style="padding:8px 12px">${f.amount}</td><td style="padding:8px 12px;font-size:16px;color:#888">${f.note}</td></tr>`
  ).join('');
  const dispRows = eu.displacement.map(d =>
    `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px;font-weight:700">${d.challenger}</td><td style="padding:8px 12px;color:#888">vs</td><td style="padding:8px 12px">${d.incumbent}</td><td style="padding:8px 12px;font-size:16px;color:#888">${d.domain}</td></tr>`
  ).join('');

  return `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px">
      <div>
        <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:16px">🇪🇺 European AI</h3>
        ${callout('signal', 'This Week\'s Thesis', eu.headline)}
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:17px;margin:20px 0 10px">Funding Rounds &gt;$50M</h4>
        <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden"><table style="width:100%;border-collapse:collapse;font-size:16px">
          <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Company</th><th style="padding:8px 12px;text-align:left">Amount</th><th style="padding:8px 12px;text-align:left">Signal</th></tr></thead>
          <tbody>${fundingRows}</tbody>
        </table></div>
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:17px;margin:20px 0 10px">Incumbent Displacement</h4>
        <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden"><table style="width:100%;border-collapse:collapse;font-size:16px">
          <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Challenger</th><th></th><th style="padding:8px 12px;text-align:left">Displaced</th><th style="padding:8px 12px;text-align:left">Domain</th></tr></thead>
          <tbody>${dispRows}</tbody>
        </table></div>
        ${cn.ciyuan_signal ? `<div style="margin-top:20px">${callout('signal', 'Digital Omnibus Update', eu.digital_omnibus)}</div>` : ''}
        ${eu.standards_vacuum ? callout('asymmetric', '⚙️ Standards Vacuum', eu.standards_vacuum.summary) : ''}
      </div>
      <div>
        <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:16px">🇨🇳 China AI</h3>
        ${callout('signal', 'This Week\'s Thesis', cn.headline)}
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:17px;margin:20px 0 6px">DeepSeek</h4>
        <p style="font-size:17px;margin:0 0 16px">${cn.deepseek}</p>
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:17px;margin:0 0 6px">Alibaba</h4>
        <p style="font-size:17px;margin:0 0 16px">${cn.alibaba}</p>
        ${cn.ciyuan_signal ? callout('threshold', `🚨 Ciyuan Signal — ${cn.ciyuan_signal.flag}`, cn.ciyuan_signal.summary + '<br><br><strong>Asymmetric implication:</strong> ' + cn.ciyuan_signal.asymmetric) : ''}
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:17px;margin:16px 0 6px">Export Controls</h4>
        <p style="font-size:17px;margin:0">${cn.export_controls}</p>
      </div>
    </div>`;
}

function renderM6() {
  const thresholds = module_6.threshold_events.map(t => `
    <div style="border:1px solid #ddd;border-left:4px solid #c0392b;border-radius:10px;padding:22px;margin-bottom:20px">
      ${callout('threshold', '🚨 Threshold Crossing', '')}
      <h4 style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;margin:0 0 4px">${t.title}</h4>
      <span style="font-size:15px;color:#888">${t.date} · ${t.domain}</span>
      <div style="font-size:17px;margin-top:14px;display:flex;flex-direction:column;gap:8px">
        <div><strong>(b) Lab / Model:</strong> ${t.lab} / ${t.model}</div>
        <div><strong>(c) Capability:</strong> ${t.capability}</div>
        <div><strong>(d) Reliability:</strong> <em>${t.reliability}</em></div>
        <div><strong>(e) Partnerships:</strong> ${t.partnerships}</div>
        <div><strong>(f) Programme:</strong> ${t.programme}</div>
      </div>
      ${callout('asymmetric', '⚡ Asymmetric Assessment', t.asymmetric)}
      ${sourceLink(t.source_label, t.source_url)}
    </div>`).join('');

  const programmes = module_6.programme_updates.map(p => card(`
    <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0 0 4px">${p.title}</h4>
    <span style="font-size:15px;color:#888">${p.date} · ${p.domain}</span>
    <p style="font-size:17px;margin:10px 0 0">${p.detail}</p>
    ${sourceLink(p.source_label, p.source_url)}
  `)).join('');

  const arxiv = module_6.arxiv_highlights.map(a => card(`
    <div style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap">
      <a href="${a.url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;background:#e8f4f4;color:#006b6f;text-decoration:none">${a.id}</a>
      <div><strong style="font-size:17px">${a.title}</strong><span style="font-size:15px;color:#888;display:block">${a.domain}</span></div>
    </div>
    <p style="font-size:17px;margin:8px 0 0">${a.note}</p>
  `)).join('');

  return `<h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:20px">Threshold Events</h3>
    ${thresholds}
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:32px 0 16px">Programme Updates</h3>
    ${programmes}
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:32px 0 16px">arXiv Highlights</h3>
    ${arxiv}`;
}

function renderM7() {
  const colorMap = { red: '#c0392b', amber: '#b45309', yellow: '#d97706' };
  const bgMap   = { red: '#fef2f2', amber: '#fef3c7', yellow: '#fffbeb' };
  const levelMap = { red: 'HIGH', amber: 'ELEVATED', yellow: 'VACUUM' };
  return module_7.vectors.map(v => {
    const c = colorMap[v.color] || colorMap.amber;
    const bg = bgMap[v.color] || bgMap.amber;
    const mainCard = `<div style="border:1px solid #ddd;border-radius:10px;padding:22px;margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:10px">
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;margin:0">${v.name}</h4>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.7em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;background:${bg};color:${c}">${levelMap[v.color]||v.level}</span>
      </div>
      <p style="font-size:17px;font-weight:600;margin:0 0 8px">${v.headline}</p>
      <p style="font-size:17px;color:#555;margin:0">${v.detail}</p>
      ${callout('asymmetric', '⚡ 2028 Horizon Signal', v.asymmetric)}
      ${sourceLink(v.source_label, v.source_url)}
    </div>`;
    const extra = (v.additional_items||[]).map(ai =>
      `<div style="border:1px solid #ddd;border-left:3px solid ${c};border-radius:10px;padding:22px;margin-bottom:12px">
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;margin:0 0 4px">${ai.title}</h4>
        <span style="font-size:15px;color:#888">${ai.date}</span>
        <p style="font-size:17px;margin:10px 0">${ai.detail}</p>
        ${callout('asymmetric', '⚡ Asymmetric Signal', ai.asymmetric)}
        ${sourceLink(ai.source_label, ai.source_url)}
      </div>`
    ).join('');
    return mainCard + extra;
  }).join('');
}

function renderM8() {
  const flagLabels = { new: '🆕 New this week', enforcement: '⚠️ Enforcement / Amendment' };
  const devs = module_8.new_developments.map(d => `
    <details style="border:1px solid #ddd;border-radius:8px;overflow:hidden;margin-bottom:8px">
      <summary style="padding:14px 18px;cursor:pointer;font-weight:600;font-family:'Space Grotesk',sans-serif;display:flex;align-items:center;gap:12px;flex-wrap:wrap;list-style:none;background:#fafafa">
        <strong>${d.jurisdiction}</strong>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;background:${d.flag==='new'?'#e8f4f4':'#fef3c7'};color:${d.flag==='new'?'#006b6f':'#b45309'}">${flagLabels[d.flag]||d.flag}</span>
        <span style="font-size:17px">${d.instrument}</span>
      </summary>
      <div style="padding:18px;border-top:1px solid #eee">
        <div style="display:flex;flex-direction:column;gap:8px;font-size:17px;margin-bottom:12px">
          <div><strong>(a) Issuing body:</strong> ${d.issuer}</div>
          <div><strong>(b) Domain:</strong> ${d.domain}</div>
          <div><strong>(c) Key obligations:</strong> ${d.obligations}</div>
          <div><strong>(d) Enforcement:</strong> ${d.enforcement}</div>
          ${d.science_friction ? `<div><strong>(e) Science friction:</strong> ${d.science_friction}</div>` : ''}
        </div>
        ${d.asymmetric ? callout('asymmetric', '⚡ Asymmetric Flag', d.asymmetric) : ''}
        ${sourceLink(d.source_label, d.source_url)}
      </div>
    </details>`).join('');

  // EU AI Act Layers
  const layers = (module_8.eu_ai_act_layered?.layers||[]).map(l => `
    <details style="border:1px solid #ddd;border-radius:8px;overflow:hidden;margin-bottom:8px">
      <summary style="padding:14px 18px;cursor:pointer;font-family:'Space Grotesk',sans-serif;display:flex;align-items:center;gap:12px;flex-wrap:wrap;list-style:none;background:#fafafa">
        <strong>${l.layer}</strong>
        <span style="font-size:15px;color:#888">${l.instrument}</span>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;background:${l.status_class==='active'?'#e8f4f4':l.status_class==='gap'?'#fef2f2':'#fef3c7'};color:${l.status_class==='active'?'#006b6f':l.status_class==='gap'?'#c0392b':'#b45309'}">${l.status}</span>
      </summary>
      <div style="padding:18px;border-top:1px solid #eee">
        <p style="font-size:16px;color:#888;margin:0 0 10px"><strong>Timeline:</strong> ${l.timeline}</p>
        ${!l.week_update.startsWith('No new') ? callout('signal', '↯ This Week', l.week_update) : '<p style="font-size:15px;color:#888">No material developments this week.</p>'}
        ${sourceLink('Primary source', l.source_url)}
      </div>
    </details>`).join('');

  // Country grid
  const gridRows = country_grid.map(c => {
    const newFlag = c.change_flag === '🆕';
    const amendFlag = c.change_flag === '⚠️';
    return `<tr style="border-bottom:1px solid #eee${newFlag?';border-left:3px solid #006b6f':''}${amendFlag?';border-left:3px solid #b45309':''}">
      <td style="padding:8px 12px;font-weight:700">${c.jurisdiction} ${c.status_icon}</td>
      <td style="padding:8px 12px;font-size:16px">${c.binding_law}</td>
      <td style="padding:8px 12px;font-size:16px;color:#888">${c.key_guidance}</td>
      <td style="padding:8px 12px;font-size:15px;color:#888;white-space:nowrap">${c.last_updated}</td>
      <td style="padding:8px 12px">${c.change_flag}</td>
    </tr>`;
  }).join('');

  const watchRows = (country_grid_watch||[]).map(c =>
    `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px;font-weight:700">${c.jurisdiction} ${c.status_icon}</td><td style="padding:8px 12px;font-size:16px">${c.threshold_trigger}</td><td style="padding:8px 12px;font-size:16px;color:#888">${c.current_framework}</td><td style="padding:8px 12px"><a href="${c.source_url}" target="_blank" rel="noopener" style="font-size:15px;color:#006b6f">↗</a></td></tr>`
  ).join('');

  return `${devs}
    <div style="margin-top:40px;padding-top:32px;border-top:2px solid #006b6f">
      <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:6px">${module_8.eu_ai_act_layered?.title||'EU AI Act — The Layered System'}</h3>
      <p style="font-size:17px;color:#888;margin-bottom:16px">${module_8.eu_ai_act_layered?.note||''}</p>
      ${layers}
    </div>
    <div style="margin-top:40px;padding-top:32px;border-top:2px solid #ddd">
      <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:6px">Country Grid — Law &amp; Standards Status</h3>
      <p style="font-size:16px;color:#888;margin-bottom:12px">🟢 Binding law in force &nbsp;·&nbsp; 🟡 Law passed/in implementation &nbsp;·&nbsp; 🟠 Guidance/soft law only &nbsp;·&nbsp; ⚪ No framework &nbsp;·&nbsp; 🆕 New this week &nbsp;·&nbsp; ⚠️ Amendment/enforcement</p>
      <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden;overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:16px">
          <thead><tr style="background:#f5f5f5">
            <th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Jurisdiction</th>
            <th style="padding:8px 12px;text-align:left">Binding Law</th>
            <th style="padding:8px 12px;text-align:left">Key Guidance</th>
            <th style="padding:8px 12px;text-align:left;white-space:nowrap">Last Updated</th>
            <th style="padding:8px 12px;text-align:left">🔔</th>
          </tr></thead>
          <tbody>${gridRows}</tbody>
        </table>
      </div>
      ${watchRows ? `
      <div style="margin-top:28px;padding-top:24px;border-top:1px solid #ddd">
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;margin-bottom:6px">Country Watch — Threshold Tracker</h4>
        <p style="font-size:16px;color:#888;margin-bottom:10px">Countries approaching entry to the grid. Promoted when threshold is met: draft AI-specific law published, public consultation opened, or binding guidance issued.</p>
        <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
          <table style="width:100%;border-collapse:collapse;font-size:16px">
            <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Jurisdiction</th><th style="padding:8px 12px;text-align:left">Threshold &amp; Trigger</th><th style="padding:8px 12px;text-align:left">Current Framework</th><th></th></tr></thead>
            <tbody>${watchRows}</tbody>
          </table>
        </div>
      </div>` : ''}
    </div>`;
}

function genericModule(mod, sections) {
  if (!mod) return '<p style="color:#888">No material developments this week.</p>';
  return sections.map(([title, items]) => {
    if (!items || !items.length) return '';
    const cards = items.map(item => {
      const parts = [];
      if (item.title || item.instrument || item.body || item.company || item.case) {
        parts.push(`<h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0 0 4px">${item.title||item.instrument||item.body||item.company||item.case||''}</h4>`);
      }
      const meta = [item.jurisdiction, item.date, item.status, item.type].filter(Boolean).join(' · ');
      if (meta) parts.push(`<span style="font-size:15px;color:#888">${meta}</span>`);
      const body = item.development || item.detail || item.summary || item.significance || '';
      if (body) parts.push(`<p style="font-size:17px;margin:10px 0">${body}</p>`);
      const asym = item.asymmetric || item.leading_indicator || '';
      if (asym) parts.push(callout('asymmetric', item.leading_indicator ? '📅 Leading Indicator — 12–24 Month Horizon' : '⚡ Asymmetric Signal', asym));
      if (item.source_label || item.source_url) parts.push(sourceLink(item.source_label||'Source', item.source_url));
      return card(parts.join(''));
    }).join('');
    return `<h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin:32px 0 16px">${title}</h3>${cards}`;
  }).join('');
}

function renderM8_Military() {
  if (!module_8 || !module_8.items) return '<p style="color:#888">No material developments this week.</p>';
  const catColors = { procurement: '#1d4ed8', doctrine: '#b45309', capability: '#c0392b', international: '#006b6f' };
  const catBgs    = { procurement: '#dbeafe', doctrine: '#fef3c7', capability: '#fef2f2', international: '#e8f4f4' };
  const catLabels = { procurement: 'Procurement', doctrine: 'Doctrine', capability: 'Capability', international: 'International' };
  return module_8.items.map(item => {
    const cat = (item.category || 'doctrine').toLowerCase();
    return card(`
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:12px">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
            <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;background:${catBgs[cat]||catBgs.doctrine};color:${catColors[cat]||catColors.doctrine}">${catLabels[cat]||item.category}</span>
            <span style="font-size:15px;color:#888">${item.jurisdiction} · ${item.date}</span>
          </div>
          <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0">${item.title}</h4>
        </div>
      </div>
      <p style="font-size:17px;color:#555;margin:0 0 12px;line-height:1.7">${item.body}</p>
      ${item.ihl_friction ? callout('threshold', '⚖️ IHL Friction', item.ihl_friction) : ''}
      ${callout('asymmetric', '⚡ Asymmetric Signal', item.asymmetric)}
      ${sourceLink(item.source_label, item.source_url)}
    `);
  }).join('');
}

function renderM9() {
  // Law & Guidance (was module_8, now module_9)
  return renderM8_LawGuidance();
}
function renderM8_LawGuidance() {
  // Full Law & Guidance renderer using module_9 data
  const m = module_9;
  if (!m) return '<p style="color:#888">No material developments this week.</p>';
  const flagLabels = { new: '\ud83c\udd95 New this week', enforcement: '\u26a0\ufe0f Enforcement / Amendment' };
  const devs = (m.new_developments||[]).map(d => `
    <details style="border:1px solid #ddd;border-radius:8px;overflow:hidden;margin-bottom:8px">
      <summary style="padding:14px 18px;cursor:pointer;font-weight:600;font-family:'Space Grotesk',sans-serif;display:flex;align-items:center;gap:12px;flex-wrap:wrap;list-style:none;background:#fafafa">
        <strong>${d.jurisdiction}</strong>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;background:${d.flag==='new'?'#e8f4f4':'#fef3c7'};color:${d.flag==='new'?'#006b6f':'#b45309'}">${flagLabels[d.flag]||d.flag}</span>
        <span style="font-size:17px">${d.instrument}</span>
      </summary>
      <div style="padding:18px;border-top:1px solid #eee">
        <div style="display:flex;flex-direction:column;gap:8px;font-size:17px;margin-bottom:12px">
          <div><strong>(a) Issuing body:</strong> ${d.issuer}</div>
          <div><strong>(b) Domain:</strong> ${d.domain}</div>
          <div><strong>(c) Key obligations:</strong> ${d.obligations}</div>
          <div><strong>(d) Enforcement:</strong> ${d.enforcement}</div>
          ${d.science_friction ? `<div><strong>(e) Science friction:</strong> ${d.science_friction}</div>` : ''}
        </div>
        ${d.asymmetric ? callout('asymmetric', '\u26a1 Asymmetric Flag', d.asymmetric) : ''}
        ${sourceLink(d.source_label, d.source_url)}
      </div>
    </details>`).join('');
  const layers = (m.eu_ai_act_layered?.layers||[]).map(l => `
    <details style="border:1px solid #ddd;border-radius:8px;overflow:hidden;margin-bottom:8px">
      <summary style="padding:14px 18px;cursor:pointer;font-family:'Space Grotesk',sans-serif;display:flex;align-items:center;gap:12px;flex-wrap:wrap;list-style:none;background:#fafafa">
        <strong>${l.layer}</strong>
        <span style="font-size:15px;color:#888">${l.instrument}</span>
        <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;background:${l.status_class==='active'?'#e8f4f4':l.status_class==='gap'?'#fef2f2':'#fef3c7'};color:${l.status_class==='active'?'#006b6f':l.status_class==='gap'?'#c0392b':'#b45309'}">${l.status}</span>
      </summary>
      <div style="padding:18px;border-top:1px solid #eee">
        <p style="font-size:16px;color:#888;margin:0 0 10px"><strong>Timeline:</strong> ${l.timeline}</p>
        ${!l.week_update.startsWith('No new') ? callout('signal', '\u21af This Week', l.week_update) : '<p style="font-size:15px;color:#888">No material developments this week.</p>'}
        ${sourceLink('Primary source', l.source_url)}
      </div>
    </details>`).join('');
  const gridRows = (country_grid||[]).map(c => {
    const newFlag = c.change_flag === '\ud83c\udd95';
    const amendFlag = c.change_flag === '\u26a0\ufe0f';
    return `<tr style="border-bottom:1px solid #eee${newFlag?';border-left:3px solid #006b6f':''}${amendFlag?';border-left:3px solid #b45309':''}">
      <td style="padding:8px 12px;font-weight:700">${c.jurisdiction} ${c.status_icon}</td>
      <td style="padding:8px 12px;font-size:16px">${c.binding_law}</td>
      <td style="padding:8px 12px;font-size:16px;color:#888">${c.key_guidance}</td>
      <td style="padding:8px 12px;font-size:15px;color:#888;white-space:nowrap">${c.last_updated}</td>
      <td style="padding:8px 12px">${c.change_flag}</td>
    </tr>`;
  }).join('');
  const watchRows = (country_grid_watch||[]).map(c =>
    `<tr style="border-bottom:1px solid #eee"><td style="padding:8px 12px;font-weight:700">${c.jurisdiction} ${c.status_icon}</td><td style="padding:8px 12px;font-size:16px">${c.threshold_trigger}</td><td style="padding:8px 12px;font-size:16px;color:#888">${c.current_framework}</td><td style="padding:8px 12px"><a href="${c.source_url}" target="_blank" rel="noopener" style="font-size:15px;color:#006b6f;text-decoration:none">\u2197</a></td></tr>`
  ).join('');
  return `${devs}
    <div style="margin-top:40px;padding-top:32px;border-top:2px solid #006b6f">
      <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:6px">${m.eu_ai_act_layered?.title||'EU AI Act \u2014 The Layered System'}</h3>
      <p style="font-size:17px;color:#888;margin-bottom:16px">${m.eu_ai_act_layered?.note||''}</p>
      ${layers}
    </div>
    <div style="margin-top:40px;padding-top:32px;border-top:2px solid #ddd">
      <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;margin-bottom:6px">Country Grid \u2014 Law &amp; Standards Status</h3>
      <p style="font-size:16px;color:#888;margin-bottom:12px">\ud83d\udfe2 Binding law in force &nbsp;\u00b7&nbsp; \ud83d\udfe1 Law passed/in implementation &nbsp;\u00b7&nbsp; \ud83d\udfe0 Guidance/soft law only &nbsp;\u00b7&nbsp; \u26aa No framework &nbsp;\u00b7&nbsp; \ud83c\udd95 New this week &nbsp;\u00b7&nbsp; \u26a0\ufe0f Amendment/enforcement</p>
      <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden;overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:16px">
          <thead><tr style="background:#f5f5f5">
            <th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Jurisdiction</th>
            <th style="padding:8px 12px;text-align:left">Binding Law</th>
            <th style="padding:8px 12px;text-align:left">Key Guidance</th>
            <th style="padding:8px 12px;text-align:left;white-space:nowrap">Last Updated</th>
            <th style="padding:8px 12px;text-align:left">\ud83d\udd14</th>
          </tr></thead>
          <tbody>${gridRows}</tbody>
        </table>
      </div>
      ${watchRows ? `
      <div style="margin-top:28px;padding-top:24px;border-top:1px solid #ddd">
        <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;margin-bottom:6px">Country Watch \u2014 Threshold Tracker</h4>
        <p style="font-size:16px;color:#888;margin-bottom:10px">Countries approaching entry to the grid.</p>
        <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
          <table style="width:100%;border-collapse:collapse;font-size:16px">
            <thead><tr style="background:#f5f5f5"><th style="padding:8px 12px;text-align:left;font-size:13px;text-transform:uppercase;color:#888">Jurisdiction</th><th style="padding:8px 12px;text-align:left">Threshold &amp; Trigger</th><th style="padding:8px 12px;text-align:left">Current Framework</th><th></th></tr></thead>
            <tbody>${watchRows}</tbody>
          </table>
        </div>
      </div>` : ''}
    </div>`;
}

function renderM11_Ethics() {
  if (!module_11 || !module_11.items) return '<p style="color:#888">No material developments this week.</p>';
  const catColors = { corporate_accountability: '#c0392b', standards: '#006b6f', lab_ethics: '#b45309', research: '#1d4ed8' };
  const catBgs    = { corporate_accountability: '#fef2f2', standards: '#e8f4f4', lab_ethics: '#fef3c7', research: '#dbeafe' };
  const catLabels = { corporate_accountability: 'Corporate Accountability', standards: 'Standards', lab_ethics: 'Lab Ethics', research: 'Research Ethics' };
  return module_11.items.map(item => {
    const cat = (item.category || 'standards').toLowerCase();
    return card(`
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:12px">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
            <span style="display:inline-flex;align-items:center;padding:0.15em 0.6em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;background:${catBgs[cat]||catBgs.standards};color:${catColors[cat]||catColors.standards}">${catLabels[cat]||item.category}</span>
            <span style="font-size:15px;color:#888">${item.jurisdiction} · ${item.date}</span>
          </div>
          <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0">${item.title}</h4>
        </div>
      </div>
      <p style="font-size:17px;color:#555;margin:0 0 12px;line-height:1.7">${item.body}</p>
      ${item.accountability_friction ? callout('threshold', '⚖️ Accountability Friction', item.accountability_friction) : ''}
      ${callout('asymmetric', '⚡ Asymmetric Signal', item.asymmetric)}
      ${sourceLink(item.source_label, item.source_url)}
    `);
  }).join('');
}

function renderM10_AIG() {
  // AI Governance (module_10)
  return genericModule(module_10, [
    ['(a) International Soft Law & Principles', module_10?.international_soft_law],
    ['(b) Corporate Governance Signals', module_10?.corporate_governance],
    ['(c) Product Liability Tracker', module_10?.product_liability],
    ['(d) Algorithmic Accountability', module_10?.algorithmic_accountability],
    ['(e) Governance Gaps Being Exploited', module_10?.governance_gaps],
  ]);
}

function renderM12() {
  // Technical Standards (module_12)
  if (!module_12 || !module_12.bodies) return '<p style="color:#888">No material developments this week.</p>';
  const statusColors = { active: '#15803d', 'in-development': '#b45309', planned: '#1d4ed8', withdrawn: '#c0392b' };
  const statusBgs   = { active: '#dcfce7', 'in-development': '#fef3c7', planned: '#dbeafe', withdrawn: '#fef2f2' };
  const statusLabels = { active: 'In Force', 'in-development': 'In Development', planned: 'Planned', withdrawn: 'Withdrawn' };
  return module_12.bodies.map(b => {
    const standards = b.standards.map(s => {
      const sc = (s.status_class || 'active').toLowerCase();
      const hasUpdate = s.week_update && !s.week_update.startsWith('No material');
      return `<div style="background:#fff;border:1px solid #ddd;border-radius:10px;padding:20px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:10px">
          <div>
            <h4 style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:0 0 4px">${s.standard}</h4>
            ${s.source_url ? `<a href="${s.source_url}" target="_blank" rel="noopener" style="font-size:15px;color:#006b6f;text-decoration:none">${s.source_label||'Primary source'} \u2197</a>` : ''}
          </div>
          <span style="display:inline-flex;align-items:center;padding:0.2em 0.7em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;white-space:nowrap;background:${statusBgs[sc]||statusBgs.active};color:${statusColors[sc]||statusColors.active}">${statusLabels[sc]||s.status}</span>
        </div>
        <p style="font-size:17px;color:#555;line-height:1.7;margin:0 0 10px;border-left:3px solid #e5e5e5;padding-left:12px">${s.scope}</p>
        ${hasUpdate ? callout('signal', '\u21af This Week', s.week_update) : '<p style="font-size:15px;color:#aaa;margin:0">No material update this week.</p>'}
      </div>`;
    }).join('');
    return `<div style="margin-bottom:36px">
      <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #e5e5e5">
        <h3 style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;margin:0">${b.body}</h3>
        <span style="font-size:15px;color:#888">${b.jurisdiction}</span>
      </div>
      ${standards}
    </div>`;
  }).join('');
}

function renderM13() {
  // Litigation Tracker (module_13)
  return genericModule(module_13, [['Active Cases', module_13?.cases||[]]]);
}

function renderM14() {
  // Personnel & Org Watch (module_14)
  return genericModule(module_14, [
    ['Lab & Industry Movements', module_14?.lab_movements||[]],
    ['Government AI Bodies', module_14?.government_ai_bodies||[]],
  ]);
}

/* ── Full page assembly ── */
const modules = [
  { num: '00', title: 'The Signal',               id: 'module-0',  content: renderM0() },
  { num: '01', title: 'Executive Insight',         id: 'module-1',  content: renderM1() },
  { num: '02', title: 'Model Frontier',            id: 'module-2',  content: renderM2() },
  { num: '03', title: 'Investment & M&A',          id: 'module-3',  content: renderM3() },
  { num: '04', title: 'Sector Penetration',        id: 'module-4',  content: renderM4() },
  { num: '05', title: 'European & China Watch',    id: 'module-5',  content: renderM5() },
  { num: '06', title: 'AI in Science',             id: 'module-6',  content: renderM6() },
  { num: '07', title: 'Risk Indicators: 2028',     id: 'module-7',  content: renderM7() },
  { num: '08', title: 'Military AI Watch',         id: 'module-8',  content: renderM8_Military() },
  { num: '09', title: 'Law & Guidance',            id: 'module-9',  content: renderM9() },
  { num: '10', title: 'AI Governance',             id: 'module-10', content: renderM10_AIG() },
  { num: '11', title: 'Ethics & Accountability',   id: 'module-11', content: renderM11_Ethics() },
  { num: '12', title: 'Technical Standards',       id: 'module-12', content: renderM12() },
  { num: '13', title: 'Litigation Tracker',        id: 'module-13', content: renderM13() },
  { num: '14', title: 'Personnel & Org Watch',     id: 'module-14', content: renderM14() },
];

// Right-hand sidebar nav — fixed position via JS to avoid WordPress sticky constraints
const navItemsJson = JSON.stringify(modules.map(m => ({ id: m.id, num: m.num, title: m.title })));
const rightNavLinks = modules.map(m =>
  `<a id="rnav-${m.id}" href="#${m.id}" onclick="event.preventDefault();document.getElementById('${m.id}').scrollIntoView({behavior:'smooth',block:'start'})" style="display:block;font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:500;color:#6b6860;padding:6px 11px;border-radius:6px;text-decoration:none !important;line-height:1.3;border-left:3px solid transparent">
    <span style="font-size:10px;color:#006b6f;font-weight:700;display:block;margin-bottom:2px">${m.num === '00' ? '\u0394' : 'M' + m.num}</span>${m.title}
  </a>`).join('');
const navLinks = '';

const moduleSections = modules.map(m => `
  <section id="${m.id}" style="border-bottom:1px solid #e5e5e5;padding-bottom:48px;scroll-margin-top:180px">
    ${sectionHeader(m.num, m.title)}
    ${m.content}
  </section>`).join('');

// Map module IDs to full names for delta strip labels
const moduleNameMap = Object.fromEntries(modules.map(m => [m.id, m.title]));

const deltaItems = data.delta_strip.map(d => {
  const moduleName = moduleNameMap[d.module] || d.label;
  return `<li style="display:flex;align-items:baseline;gap:8px;font-size:17px;flex-wrap:wrap">
    <span style="color:#006b6f;font-weight:700;flex-shrink:0">→</span>
    <span>${d.text}</span>
    <a href="#${d.module}" style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#006b6f;background:#e8f4f4;border-radius:9999px;padding:0.1em 0.6em;text-decoration:none;margin-left:auto;white-space:nowrap">${moduleName}</a>
  </li>`;
}).join('');

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ramparts AI Frontier Monitor — Asymmetric Intelligence | Ramparts Gibraltar</title>
<meta name="description" content="Weekly AI intelligence brief for investors, regulators, legal professionals and compliance teams. Week of ${meta.week_label}. 12 intelligence modules. All primary sources. Published by Ramparts, Gibraltar.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="${CANONICAL}">
<meta property="og:title" content="Ramparts AI Frontier Monitor — Week of ${meta.week_label}">
<meta property="og:description" content="The signal that everyone else missed — in the regulatory filing no one opened, the preprint that rewrites the consensus. 12 intelligence modules. All primary sources.">
<meta property="og:type" content="article">
<meta property="og:url" content="${CANONICAL}">
<meta name="author" content="Peter Howitt, Ramparts Gibraltar">
<meta name="publisher" content="Ramparts">
<script type="application/ld+json">${JSON.stringify({
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": `Ramparts AI Frontier Monitor — Week of ${meta.week_label}`,
  "description": "Weekly AI intelligence brief for investors, regulators, legal professionals and compliance teams.",
  "author": { "@type": "Person", "name": "Peter Howitt", "url": RAMPARTS_URL },
  "publisher": { "@type": "Organization", "name": "Ramparts", "url": RAMPARTS_URL },
  "datePublished": meta.published,
  "mainEntityOfPage": CANONICAL,
  "keywords": "AI governance, AI regulation, EU AI Act, frontier AI, AI investment, legal AI, AI compliance"
})}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  /* ── Design tokens (matches base.css) ── */
  :root {
    /* Base scale +20% vs homepage to match visual size on WordPress */
    --text-xs:   clamp(0.9rem,   0.84rem + 0.3vw,  1.05rem);
    --text-sm:   clamp(1.05rem,  0.96rem + 0.42vw, 1.2rem);
    --text-base: clamp(1.2rem,   1.14rem + 0.3vw,  1.35rem);
    --text-lg:   clamp(1.35rem,  1.2rem  + 0.9vw,  1.8rem);
    --text-xl:   clamp(1.8rem,   1.44rem + 1.5vw,  2.7rem);
    --text-2xl:  clamp(2.4rem,   1.44rem + 3vw,    4.2rem);
    --color-primary: #006b6f;
    --color-primary-light: #e8f4f4;
    --color-text: #1a1915;
    --color-text-muted: #6b6860;
    --color-bg: #f8f7f4;
    --color-surface: #ffffff;
    --color-border: #ccc8c0;
    --color-divider: #ddd9d2;
  }
  /* ── Reset & base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', -apple-system, sans-serif; font-size: var(--text-base); line-height: 1.65; color: #1a1915; background: #f8f7f4; }
  h1,h2,h3,h4,h5 { font-family: 'Space Grotesk', sans-serif; }
  /* ── Links: scoped to #ramparts-monitor to avoid bleeding into WP site nav ── */
  #ramparts-monitor a, #ramparts-monitor a:link,
  #ramparts-monitor a:visited {
    text-decoration: none !important;
    color: #006b6f;
  }
  #ramparts-monitor a:hover { opacity: 0.8; text-decoration: none !important; }
  #ramparts-monitor a *     { text-decoration: none !important; }
  /* Override Elementor global typography variable */
  * { --e-global-typography-0fb681b-text-decoration: none !important; }
  /* White-text buttons: ramparts-btn class preserves color against teal backgrounds */
  a.ramparts-btn, a.ramparts-btn:link, a.ramparts-btn:visited,
  a.ramparts-btn:hover, a.ramparts-btn:active { color: #ffffff !important; }
  p { line-height: 1.7; }
  details summary::-webkit-details-marker { display: none; }
  details[open] summary { background: #f0f0f0 !important; }
  /* ── Hide WordPress page title injected by theme ── */
  .page-header, .entry-title, h1.entry-title { display: none !important; }
  /* ── Full-width breakout: override Hello Elementor theme constraints ── */
  /* Theme sets body:not([class*=elementor-page-]) .site-main { max-width:1140px } */
  .site-main, .page-content, .entry-content, .wp-block-html, .site-main article,
  .elementor-widget-wrap, .elementor-section-wrap,
  body .site-main, body:not([class*=elementor-page-]) .site-main { 
    max-width: none !important;
    width: 100% !important;
    padding-left: 0 !important; 
    padding-right: 0 !important;
  }
  /* ── Sticky sidebar fix: ensure parent allows sticky ── */
  #ramparts-layout { overflow: visible !important; }
  @media (max-width: 768px) {
    .grid-2col { grid-template-columns: 1fr !important; }
    .hide-mobile { display: none !important; }
  }
  @media print {
    .site-header, .no-print { display: none !important; }
    body { font-size: 11pt; background: white; }
    section { break-inside: avoid; }
  }
</style>
</head>
<body>
<div id="ramparts-monitor">

<!-- Site Header -->
<header style="background:#fff;border-bottom:1px solid #ddd;position:sticky;top:0;z-index:100">
  <div style="max-width:1400px;margin:0 auto;padding:0 clamp(16px,4vw,64px);display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px">
    <a href="https://ramparts.gi/ai-frontier-monitor/" style="display:flex;align-items:center;gap:12px;text-decoration:none !important;color:inherit">
      <svg width="32" height="32" viewBox="0 0 36 36" fill="none" aria-hidden="true">
        <path d="M18 2L4 8v10c0 8.5 6 16 14 18 8-2 14-9.5 14-18V8L18 2z" fill="#006b6f" fill-opacity="0.1" stroke="#006b6f" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M13 17h10M18 13v8M15 15l3-2 3 2" stroke="#006b6f" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div style="line-height:1.1">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#1a1915">Ramparts</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:500;letter-spacing:0.18em;text-transform:uppercase;color:#888">AI Frontier Monitor</div>
      </div>
      <span style="font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:#006b6f;margin-left:8px">Asymmetric Intelligence</span>
    </a>
    <nav style="display:flex;align-items:center;gap:4px" class="hide-mobile">
      <a href="${RAMPARTS_URL}" style="font-size:17px;color:#888;padding:6px 12px;text-decoration:none !important;border-radius:6px">Ramparts.gi</a>
      <a href="https://ramparts.gi/ai-frontier-monitor/" style="font-size:17px;color:#888;padding:6px 12px;text-decoration:none !important;border-radius:6px">All Issues</a>
      <a href="https://ramparts.gi/ai-frontier-monitor-about/" style="font-size:17px;color:#888;padding:6px 12px;text-decoration:none !important;border-radius:6px">About</a>
      <a href="https://ramparts.gi/ai-frontier-monitor-digest/" style="display:inline-flex;align-items:center;gap:5px;font-size:16px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#fff;background:#006b6f;padding:7px 16px;border-radius:6px;text-decoration:none !important;letter-spacing:0.02em">↯ Subscribe</a>
    </nav>
  </div>
</header>

<!-- Report Header -->
<div style="background:#fff;border-bottom:2px solid #006b6f;padding:40px clamp(16px,4vw,64px)">
  <div style="max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:flex-start;gap:32px;flex-wrap:wrap">
    <div>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap">
        <span style="display:inline-flex;align-items:center;padding:0.2em 0.7em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.05em;text-transform:uppercase;background:#e8f4f4;color:#006b6f">AI Intelligence Brief</span>
        <span style="display:inline-flex;align-items:center;padding:0.2em 0.7em;border-radius:9999px;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;background:#ef4444;color:#fff;animation:pulse 2s ease-in-out infinite">● Live</span>
      </div>
      <h1 style="font-family:'Space Grotesk',sans-serif;font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;letter-spacing:-0.02em;line-height:1.1;margin-bottom:8px">
        <a href="${RAMPARTS_URL}" style="color:inherit;text-decoration:none">Ramparts</a>
        <span style="color:#006b6f"> AI Frontier Monitor</span>
      </h1>
      <p style="font-size:16px;color:#888">Week of ${meta.week_label} · Asymmetric Intelligence · Published ${meta.published} ${meta.publish_time_utc||'07:00 UTC'}</p>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div style="margin-bottom:8px"><span style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.06em;text-transform:uppercase;color:#888">Issue</span><br><span style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700">Vol. ${meta.volume} · Issue ${meta.issue}</span></div>
      <div style="margin-bottom:8px"><span style="font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;letter-spacing:0.06em;text-transform:uppercase;color:#888">Jurisdiction Grid</span><br><span style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700">12 countries</span></div>
      <a href="${PDF_URL}" download style="display:inline-flex;align-items:center;gap:6px;font-size:15px;font-weight:600;font-family:'Space Grotesk',sans-serif;color:#006b6f;border:1px solid #006b6f;padding:6px 14px;border-radius:6px;text-decoration:none;margin-top:8px">↓ Download PDF</a>
    </div>
  </div>
</div>

<!-- Delta Strip -->
<div style="background:#f0f0ec;border-bottom:1px solid #ddd;padding:18px clamp(16px,4vw,64px)">
  <div style="max-width:1400px;margin:0 auto">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#888;margin-bottom:12px">↯ This Week's Five Key Changes</div>
    <ul style="list-style:none;display:flex;flex-direction:column;gap:8px">${deltaItems}</ul>
  </div>
</div>

<!-- Layout: sidebar + content -->
<div id="ramparts-layout" style="max-width:1400px;margin:0 auto;padding:0 clamp(12px,3vw,48px) 80px;display:flex;gap:32px;align-items:flex-start">

  <!-- Main Content -->
  <main style="flex:1;min-width:0">
    ${moduleSections}

    <!-- In-content subscribe section after M14 -->
    <div style="background:#006b6f;border-radius:12px;padding:40px 48px;margin-top:48px;margin-bottom:16px">
      <div style="max-width:600px">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.6);margin-bottom:10px">Weekly Digest</div>
        <h2 style="font-family:'Space Grotesk',sans-serif;font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:700;color:#fff;margin:0 0 12px;letter-spacing:-0.01em">The signal in your inbox every Thursday</h2>
        <p style="font-size:17px;color:rgba(255,255,255,0.82);line-height:1.65;margin:0 0 28px">Primary sources only. No press summaries. 09:00 GMT without exception — reliable enough to build into your morning routine.</p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">
          <a href="https://ramparts.gi/ai-frontier-monitor-digest/" class="ramparts-btn" style="display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#006b6f;background:#fff;padding:13px 28px;border-radius:8px;text-decoration:none !important;letter-spacing:0.01em">↯ Subscribe Free</a>
          <a href="https://ramparts.gi/ai-frontier-monitor-about/" style="display:inline-flex;align-items:center;gap:8px;font-size:14px;font-weight:600;font-family:'Space Grotesk',sans-serif;color:rgba(255,255,255,0.9);background:rgba(255,255,255,0.12);padding:13px 22px;border-radius:8px;text-decoration:none !important;border:1px solid rgba(255,255,255,0.3)">About the Monitor</a>
        </div>
        <p style="font-size:13px;color:rgba(255,255,255,0.4);margin-top:16px">No spam. Unsubscribe in one click. Published by <a href="https://ramparts.gi" style="color:rgba(255,255,255,0.6);text-decoration:none">Ramparts</a>, Gibraltar.</p>
      </div>
    </div>
  </main>

  <!-- Spacer to reserve room for fixed nav -->
  <div class="hide-mobile" style="width:220px;flex-shrink:0"></div>

</div>

<!-- Fixed right-hand module nav (position:fixed bypasses WordPress sticky constraints) -->
<div id="ramparts-sidenav" class="hide-mobile" style="position:fixed;top:140px;right:16px;width:190px;z-index:9999;background:#fff;border:1px solid #ddd;border-radius:10px;padding:8px 0;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-height:calc(100vh - 160px);overflow-y:auto">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#aaa;padding:4px 12px 8px">Modules</div>
  <nav id="ramparts-sidenav-links" aria-label="Module navigation" style="display:flex;flex-direction:column">
    ${rightNavLinks}
  </nav>
  <!-- Subscribe panel -->
  <div style="margin:8px 8px 4px;padding:11px;background:#e8f4f4;border-radius:8px">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#006b6f;margin-bottom:8px">Weekly Digest</div>
    <a href="https://ramparts.gi/ai-frontier-monitor-digest/" style="display:block;text-align:center;font-size:13px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#fff;background:#006b6f;padding:8px 12px;border-radius:6px;text-decoration:none !important">↯ Subscribe Free</a>
  </div>
</div>

<script>
(function(){
  // Scroll-spy: highlight active module in fixed sidebar
  var ids = ${navItemsJson}.map(function(m){ return m.id; });
  var active = null;
  function setActive(id){
    if(id===active) return;
    if(active){
      var prev = document.getElementById('rnav-'+active);
      if(prev){
        prev.style.color='#6b6860';
        prev.style.borderLeftColor='transparent';
        prev.style.background='transparent';
        prev.style.fontWeight='500';
        var num = prev.querySelector('span');
        if(num) num.style.color='#aaa';
      }
    }
    active = id;
    if(id){
      var el = document.getElementById('rnav-'+id);
      if(el){
        el.style.color='#1a1915';
        el.style.borderLeftColor='#006b6f';
        el.style.background='#e8f4f4';
        el.style.fontWeight='700';
        var num = el.querySelector('span');
        if(num) num.style.color='#006b6f';
      }
    }
  }
  function onScroll(){
    var offset = window.innerHeight * 0.35;
    var current = null;
    for(var i=ids.length-1;i>=0;i--){
      var sec = document.getElementById(ids[i]);
      if(sec && sec.getBoundingClientRect().top <= offset){ current=ids[i]; break; }
    }
    setActive(current || ids[0]);
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();
</script>

<!-- End-of-report subscribe section -->
<div style="background:#006b6f;padding:clamp(40px,6vw,72px) clamp(16px,4vw,64px)">
  <div style="max-width:720px;margin:0 auto;text-align:center">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.6);margin-bottom:12px">Weekly Digest</div>
    <h2 style="font-family:'Space Grotesk',sans-serif;font-size:clamp(1.4rem,3vw,2rem);font-weight:700;color:#fff;margin-bottom:12px;letter-spacing:-0.01em">The signal in your inbox every Thursday</h2>
    <p style="font-size:16px;color:rgba(255,255,255,0.8);line-height:1.6;max-width:54ch;margin:0 auto 32px">Primary sources only. No press summaries. 09:00 GMT without exception — reliable enough to build into your morning routine.</p>
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
      <a href="https://ramparts.gi/ai-frontier-monitor-digest/" class="ramparts-btn" style="display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#006b6f;background:#fff;padding:13px 28px;border-radius:8px;text-decoration:none !important;letter-spacing:0.01em">↯ Subscribe Free</a>
      <a href="https://ramparts.gi/ai-frontier-monitor-about/" style="display:inline-flex;align-items:center;gap:8px;font-size:17px;font-weight:600;font-family:'Space Grotesk',sans-serif;color:rgba(255,255,255,0.9);background:rgba(255,255,255,0.15);padding:13px 24px;border-radius:8px;text-decoration:none !important;border:1px solid rgba(255,255,255,0.3)">About the Monitor</a>
    </div>
    <p style="font-size:15px;color:rgba(255,255,255,0.45);margin-top:20px">No spam. Unsubscribe in one click. Published by Ramparts, Gibraltar.</p>
  </div>
</div>

<!-- Footer -->
<footer style="background:#fff;border-top:1px solid #ddd;padding:40px clamp(16px,4vw,64px)">
  <div style="max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
    <div>
      <a href="${RAMPARTS_URL}" style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:17px;color:#1a1915;text-decoration:none">Ramparts</a>
      <span style="font-size:16px;color:#888"> — AI Frontier Monitor — Asymmetric Intelligence</span><br>
      <span style="font-size:16px;color:#888">Gibraltar · <a href="mailto:info@ramparts.gi" style="color:#006b6f">info@ramparts.gi</a> · <a href="${SITE_URL}/" style="color:#006b6f">All Issues</a></span>
    </div>
    <div style="font-size:15px;color:#bbb">
      © 2026 Ramparts. All rights reserved.
    </div>
  </div>
</footer>

<style>
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.65} }
  details summary { user-select:none; }
  /* link underline suppressed globally in base styles above */
</style>
</div><!-- /#ramparts-monitor -->
</body>
</html>`;

const outputPath = path.join(dataDir, `static-report-${reportDate}.html`);
fs.writeFileSync(outputPath, html, 'utf8');
const sizeKB = Math.round(fs.statSync(outputPath).size / 1024);
console.log(`✅ Static HTML generated: ${outputPath}`);
console.log(`   Size: ${sizeKB}KB`);
console.log(`   Modules: ${modules.length}`);
console.log(`   SEO: canonical=${CANONICAL}`);

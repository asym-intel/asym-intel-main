#!/usr/bin/env node
/**
 * Ramparts AI Frontier Monitor — Static Site Generator
 * Generates 6 static HTML pages for ramparts.gi/ai-frontier-monitor/
 *
 * Usage: node generate-site.js [YYYY-MM-DD]
 * Default date: 2026-03-26
 *
 * Output: /home/user/workspace/ramparts-v2/data/
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ── Configuration ──────────────────────────────────────────────────────────────
const DATE_ARG = process.argv[2] || '2026-03-26';
const DATA_DIR = path.join(__dirname, 'ramparts-v2/data');
const BASE_URL = 'https://ramparts.gi/ai-frontier-monitor';
const ISSUE_URL = 'https://ramparts.gi/ai-frontier-monitor-issue/';
const ABOUT_URL = 'https://ramparts.gi/ai-frontier-monitor-about/';
const ARCHIVE_URL = 'https://ramparts.gi/ai-frontier-monitor-archive/';
const DIGEST_URL = 'https://ramparts.gi/ai-frontier-monitor-digest/';
const GIBRALTAR_URL = 'https://ramparts.gi/ai-frontier-monitor-gibraltar/';
const SEARCH_URL = 'https://ramparts.gi/ai-frontier-monitor-search/';
const ARCHIVE_BASE_URL = 'https://ramparts.gi/wp-content/uploads/';

// ── Load JSON data ─────────────────────────────────────────────────────────────
const archiveData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'archive.json'), 'utf8'));
const gibraltarData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'gibraltar-observatory.json'), 'utf8'));
const reportData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, `report-${DATE_ARG}.json`), 'utf8'));

// ── Shared Helpers ─────────────────────────────────────────────────────────────

function stripHtml(str) {
  return String(str || '').replace(/<[^>]+>/g, '');
}

function pplxAttribution() {
  return `<!--
   ______                            __
  / ____/___  ____ ___  ____  __  __/ /____  _____
 / /   / __ \\/ __ \`__ \\/ __ \\/ / / / __/ _ \\/ ___/
/ /___/ /_/ / / / / / / /_/ / /_/ / /_/  __/ /
\\____/\\____/_/ /_/ /_/ .___/\\__,_/\\__/\\___/_/
                    /_/
        Created with Perplexity Computer
        https://www.perplexity.ai/computer
-->
<meta name="generator" content="Perplexity Computer">
<meta name="author" content="Perplexity Computer">
<meta property="og:see_also" content="https://www.perplexity.ai/computer">
<link rel="author" href="https://www.perplexity.ai/computer">`;
}

function googleFonts() {
  return `<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">`;
}

// ── Base CSS (inlined) ─────────────────────────────────────────────────────────
function baseCSS() {
  return `/* ============================================================
   RAMPARTS AI FRONTIER MONITOR — Base Design System
   Light theme only (static)
   ============================================================ */

/* ---------- Design Tokens ---------- */
:root {
  --text-xs:   clamp(0.75rem,  0.7rem  + 0.25vw, 0.875rem);
  --text-sm:   clamp(0.875rem, 0.8rem  + 0.35vw, 1rem);
  --text-base: clamp(1rem,     0.95rem + 0.25vw, 1.125rem);
  --text-lg:   clamp(1.125rem, 1rem    + 0.75vw, 1.5rem);
  --text-xl:   clamp(1.5rem,   1.2rem  + 1.25vw, 2.25rem);
  --text-2xl:  clamp(2rem,     1.2rem  + 2.5vw,  3.5rem);

  --space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem;
  --space-4: 1rem;    --space-5: 1.25rem; --space-6: 1.5rem;
  --space-8: 2rem;    --space-10: 2.5rem; --space-12: 3rem;
  --space-16: 4rem;   --space-20: 5rem;   --space-24: 6rem;

  --radius-sm: 0.25rem; --radius-md: 0.5rem;
  --radius-lg: 0.75rem; --radius-xl: 1rem;
  --radius-full: 9999px;

  --transition: 150ms ease;

  --color-bg:              #f8f7f4;
  --color-surface:         #ffffff;
  --color-surface-2:       #f3f2ef;
  --color-surface-offset:  #eceae5;
  --color-divider:         #ddd9d2;
  --color-border:          #ccc8c0;

  --color-text:            #1a1915;
  --color-text-muted:      #6b6860;
  --color-text-faint:      #a8a49e;
  --color-text-inverse:    #f8f7f4;

  --color-primary:         #006b6f;
  --color-primary-hover:   #005054;
  --color-primary-active:  #00393d;
  --color-primary-light:   #e8f4f4;
  --color-primary-medium:  #b8dcdc;

  --color-amber:           #b45309;
  --color-amber-hover:     #92400e;
  --color-amber-light:     #fef3c7;
  --color-amber-medium:    #fcd34d;

  --color-red:             #c0392b;
  --color-red-hover:       #9b2c2c;
  --color-red-light:       #fef2f2;
  --color-red-medium:      #fca5a5;

  --color-yellow:          #d97706;
  --color-yellow-light:    #fffbeb;

  --color-accelerating:    #15803d;
  --color-accelerating-bg: #dcfce7;
  --color-stalling:        #b45309;
  --color-stalling-bg:     #fef3c7;
  --color-emerging:        #1d4ed8;
  --color-emerging-bg:     #dbeafe;

  --color-cursor-yes:      #15803d;
  --color-cursor-yes-bg:   #dcfce7;
  --color-cursor-probable: #b45309;
  --color-cursor-probable-bg: #fef3c7;
  --color-cursor-no:       #6b7280;
  --color-cursor-no-bg:    #f3f4f6;
}

/* ---------- Reset & Base ---------- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; font-size: 16px; -webkit-text-size-adjust: 100%; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: var(--text-base);
  line-height: 1.65;
  color: var(--color-text);
  background-color: var(--color-bg);
}

/* ---------- Typography ---------- */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', -apple-system, sans-serif;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--color-text);
}
h1 { font-size: var(--text-2xl); }
h2 { font-size: var(--text-xl); }
h3 { font-size: var(--text-lg); font-weight: 600; }
h4 { font-size: var(--text-base); font-weight: 700; }

p { max-width: none; }
p + p { margin-top: var(--space-4); }

a { color: var(--color-primary); text-decoration: none !important; transition: color var(--transition); }
a:hover { color: var(--color-primary-hover); text-decoration: none !important; }
a *, a:hover * { text-decoration: none !important; }

strong { font-weight: 700; }
em { font-style: italic; }
code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875em;
  background: var(--color-surface-2);
  padding: 0.1em 0.3em;
  border-radius: var(--radius-sm);
}

/* ---------- Layout ---------- */
.container {
  width: 100%;
  max-width: 1400px;
  margin-inline: auto;
  padding-inline: clamp(var(--space-4), 4vw, var(--space-16));
}
.container--narrow { max-width: 900px; }
.section { padding-block: clamp(var(--space-12), 6vw, var(--space-24)); }

/* ---------- Utilities ---------- */
.text-muted  { color: var(--color-text-muted); }
.text-faint  { color: var(--color-text-faint); }
.text-sm     { font-size: var(--text-sm); }
.text-xs     { font-size: var(--text-xs); }
.text-primary { color: var(--color-primary); }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
.divider { border: none; border-top: 1px solid var(--color-divider); margin-block: var(--space-8); }

/* ---------- Badge ---------- */
.badge {
  display: inline-flex; align-items: center; gap: var(--space-1);
  padding: 0.2em 0.6em; border-radius: var(--radius-full);
  font-size: var(--text-xs); font-weight: 600;
  font-family: 'Space Grotesk', sans-serif;
  letter-spacing: 0.03em; text-transform: uppercase; white-space: nowrap;
}
.badge--teal   { background: var(--color-primary-light); color: var(--color-primary); }
.badge--red    { background: var(--color-red-light);     color: var(--color-red); }
.badge--amber  { background: var(--color-amber-light);   color: var(--color-amber); }
.badge--yellow { background: var(--color-yellow-light);  color: var(--color-yellow); }
.badge--new    { background: var(--color-primary-light); color: var(--color-primary); }
.badge--live   { background: #ef4444; color: #fff; animation: pulse-live 2s ease-in-out infinite; }
.badge--accelerating { background: var(--color-accelerating-bg); color: var(--color-accelerating); }
.badge--stalling     { background: var(--color-stalling-bg);     color: var(--color-stalling); }
.badge--emerging     { background: var(--color-emerging-bg);     color: var(--color-emerging); }
.badge--risk-elevated { background: var(--color-amber-light);  color: var(--color-amber); }
@keyframes pulse-live { 0%, 100% { opacity: 1; } 50% { opacity: 0.65; } }

/* ---------- Cards ---------- */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.card:hover { border-color: var(--color-primary-medium); box-shadow: 0 4px 24px rgba(0,0,0,0.06); }

/* ---------- Callout ---------- */
.callout { padding: var(--space-4) var(--space-5); border-radius: var(--radius-md); border-left: 4px solid; margin-block: var(--space-4); }
.callout--asymmetric { background: var(--color-amber-light); border-left-color: var(--color-amber); }
.callout--threshold  { background: var(--color-red-light);   border-left-color: var(--color-red); }
.callout--signal     { background: var(--color-primary-light); border-left-color: var(--color-primary); }
.callout__label { font-size: var(--text-xs); font-weight: 700; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: var(--space-2); }
.callout--asymmetric .callout__label { color: var(--color-amber); }
.callout--threshold  .callout__label { color: var(--color-red); }
.callout--signal     .callout__label { color: var(--color-primary); }

/* ---------- Tables ---------- */
.table-wrapper { overflow-x: auto; border-radius: var(--radius-lg); border: 1px solid var(--color-border); }
table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
thead tr { background: var(--color-surface-2); border-bottom: 2px solid var(--color-divider); }
thead th { padding: var(--space-3) var(--space-4); text-align: left; font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--color-text-muted); white-space: nowrap; }
tbody tr { border-bottom: 1px solid var(--color-divider); transition: background var(--transition); }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: var(--color-surface-2); }
tbody td { padding: var(--space-3) var(--space-4); vertical-align: top; line-height: 1.5; }

/* ---------- Source Link ---------- */
.source-link { display: inline-flex; align-items: center; gap: var(--space-1); font-size: var(--text-xs); color: var(--color-text-muted); border: 1px solid var(--color-divider); border-radius: var(--radius-full); padding: 0.2em 0.7em; margin-top: var(--space-3); transition: color var(--transition), border-color var(--transition); text-decoration: none; }
.source-link:hover { color: var(--color-primary); border-color: var(--color-primary-medium); text-decoration: none; }

/* ---------- Print ---------- */
@media print {
  .site-nav, .theme-toggle { display: none !important; }
  body { font-size: 11pt; background: white; color: black; }
  a { color: black; }
  .card { border: 1px solid #ccc; break-inside: avoid; }
  h2 { break-before: page; }
}

/* ---------- Focus / Accessibility ---------- */
:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 3px; border-radius: var(--radius-sm); }`;
}

// ── Site Chrome (header + nav) ─────────────────────────────────────────────────
function navCSS() {
  return `/* ---- Site Chrome ---- */
.site-header { background: var(--color-surface); border-bottom: 1px solid var(--color-border); position: sticky; top: 0; z-index: 100; }
.site-header-inner { display: flex; align-items: center; justify-content: space-between; padding-block: var(--space-4); gap: var(--space-4); }
.logo-link { display: flex; align-items: center; gap: var(--space-3); text-decoration: none; color: var(--color-text); }
.logo-link:hover { text-decoration: none; color: var(--color-text); }
.logo-wordmark { display: flex; flex-direction: column; line-height: 1.1; }
.logo-name { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-sm); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-text); }
.logo-sub { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-text-muted); }
.logo-tagline { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: var(--color-primary); }
.site-nav { display: flex; align-items: center; gap: var(--space-1); }
.site-nav a { font-size: var(--text-sm); font-weight: 500; color: var(--color-text-muted); padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); transition: color var(--transition), background var(--transition); text-decoration: none; white-space: nowrap; }
.site-nav a:hover { color: var(--color-text); background: var(--color-surface-2); text-decoration: none; }
.site-nav a.active { color: var(--color-primary); font-weight: 600; }
.site-footer { background: var(--color-surface); border-top: 1px solid var(--color-border); padding-block: var(--space-10); margin-top: var(--space-20); }
.footer-bottom { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--space-4); }
.footer-bottom p { font-size: var(--text-xs); color: var(--color-text-faint); }
.footer-bottom a { color: var(--color-text-faint); }
.footer-bottom a:hover { color: var(--color-text-muted); }
@media (max-width: 600px) { .site-nav { display: none; } }`;
}

function logoSVG(size = 32) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 36 36" fill="none" aria-hidden="true">
  <path d="M18 2L4 8v10c0 8.5 6 16 14 18 8-2 14-9.5 14-18V8L18 2z" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M18 6L7 11v8c0 6.5 4.5 12 11 13.5 6.5-1.5 11-7 11-13.5v-8L18 6z" fill="currentColor" fill-opacity="0.12"/>
  <path d="M13 17h10M18 13v8M15 15l3-2 3 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;
}

function header(activePage) {
  const navItems = [
    { label: 'Home', url: `${BASE_URL}/` },
    { label: 'Latest Issue', url: ISSUE_URL },
    { label: 'Archive', url: ARCHIVE_URL },
    { label: 'Search', url: SEARCH_URL },
    { label: 'About', url: ABOUT_URL },
    { label: 'Digest', url: DIGEST_URL },
    { label: 'Gibraltar', url: GIBRALTAR_URL },
  ];
  const navHtml = navItems.map(item => {
    const isActive = item.label === activePage;
    return `<a href="${item.url}"${isActive ? ' class="active"' : ''}>${item.label}</a>`;
  }).join('\n        ');

  return `<header class="site-header">
  <div class="container">
    <div class="site-header-inner">
      <a href="${BASE_URL}/" class="logo-link" aria-label="Ramparts AI Frontier Monitor home">
        ${logoSVG(36)}
        <div class="logo-wordmark">
          <span class="logo-name">Ramparts</span>
          <span class="logo-sub">AI Frontier Monitor</span>
        </div>
        <span class="logo-tagline" style="margin-left:var(--space-2)">Asymmetric Intelligence</span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        ${navHtml}
      </nav>
    </div>
  </div>
</header>`;
}

function footer() {
  return `<footer class="site-footer">
  <div class="container">
    <div class="footer-bottom">
      <p>© 2026 Ramparts. All rights reserved. Gibraltar.</p>
      <p><a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener noreferrer">Created with Perplexity Computer</a></p>
    </div>
  </div>
</footer>`;
}

// ── Page Builder ───────────────────────────────────────────────────────────────
function buildPage({ title, description, canonical, activePage, extraCSS, body }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
${pplxAttribution()}

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title}</title>
<meta name="description" content="${description}">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${description}">
<meta property="og:type" content="website">
<link rel="canonical" href="${canonical}">

${googleFonts()}

<style>
${baseCSS()}
${navCSS()}
${extraCSS || ''}
</style>
</head>
<body>
${header(activePage)}
${body}
${footer()}
</body>
</html>`;
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 1: HOMEPAGE (static-index.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateIndex() {
  const meta = reportData.meta;
  const deltaStrip = reportData.delta_strip || [];

  const moduleNameLookup = {
    'module-0':'The Signal','module-1':'Executive Insight','module-2':'Model Frontier',
    'module-3':'Investment & M\u0026A','module-4':'Sector Penetration','module-5':'European & China Watch',
    'module-6':'AI in Science','module-7':'Risk Indicators: 2028','module-8':'Military AI Watch',
    'module-9':'Law & Guidance','module-10':'AI Governance','module-11':'Ethics & Accountability',
    'module-12':'Technical Standards','module-13':'Litigation Tracker','module-14':'Personnel & Org Watch'
  };
  const deltaItems = deltaStrip.slice(0, 5).map(d => {
    const moduleUrl = `${ISSUE_URL}#${d.module}`;
    const moduleName = moduleNameLookup[d.module] || d.label;
    return `<li>
          <span class="delta-arrow">→</span>
          <span>${stripHtml(d.text)}</span>
          <a href="${moduleUrl}" class="delta-module">${moduleName}</a>
        </li>`;
  }).join('\n');

  const moduleCards = [
    { num: '00', title: 'The Signal', desc: 'One paragraph. The single most strategically important signal of the week and why it matters in 12 months. Editorial judgment, not a summary of headlines.' },
    { num: '01', title: 'Executive Insight', desc: 'Top 5 mainstream shifts + 5 underweighted signals the mainstream press missed — from technical appendices, regulatory filings, niche research blogs, and academic preprints.' },
    { num: '02', title: 'Model Frontier', desc: 'Capability tracking across OpenAI, Anthropic, Google DeepMind, xAI, Meta, Mistral, DeepSeek, Alibaba, Nvidia and others. Benchmark tables and architectural innovation flags every week.' },
    { num: '03', title: 'Investment &amp; M&amp;A', desc: 'Funding rounds above $50M, hyper-growth companies on the Cursor Curve (zero to $1B ARR in under 24 months), acqui-hires disguised as partnerships, and secondary market valuations.' },
    { num: '04', title: 'Sector Penetration', desc: 'Healthcare, Legal, Finance, Defence, Media, Education, Critical Infrastructure — Accelerating, Stalling, or Emerging. Capability-to-deployment gaps and stealth deployments flagged.' },
    { num: '05', title: 'European &amp; China Watch', desc: 'EU AI Act compliance posture, sovereign AI infrastructure, DeepSeek/Alibaba/Zhipu AI capability trajectory, export control impacts, and state-directed AI deployment.' },
    { num: '06', title: 'AI in Science', desc: 'Tracking the threshold from "useful assistant" to "autonomous research contributor" across biology, medicine, physics, climate, and more. Genesis Mission, AlphaFold, and peer-reviewed threshold events.' },
    { num: '07', title: 'Risk Indicators: 2028', desc: 'Governance fragmentation, cyber escalation, platform power, export controls, and disinformation velocity — tracked against a 2028 horizon with asymmetric governance gap analysis.' },
    { num: '08', title: 'Military AI Watch', desc: 'Defence procurement, autonomous weapons doctrine, IHL friction, and international treaty developments. Tracks asymmetric implications of AI in weapons systems and dual-use capability.' },
    { num: '09', title: 'Law &amp; Guidance', desc: 'Every major jurisdiction, every binding law, every enforcement action and regulatory guidance — updated weekly. The 12-jurisdiction Country Grid is embedded within this module.' },
    { num: '10', title: 'AI Governance', desc: 'International soft law, corporate governance signals, product liability tracker, algorithmic accountability enforcement, and governance gaps being exploited. Voluntary commitments today are leading indicators of binding law in 12–24 months.' },
    { num: '11', title: 'Ethics &amp; Accountability', desc: 'Bias measurement, transparency obligations, corporate accountability signals, lab ethics commitments, and research ethics developments — with primary source citations and asymmetric accountability analysis.' },
    { num: '12', title: 'Technical Standards', desc: 'ISO/IEC (42001, 23894, 5338), NIST AI RMF, IEEE 7000-series, EU CEN-CENELEC harmonised standards, ETSI ISG SAI, and OECD AI Principles — tracked on independent timelines from law.' },
    { num: '13', title: 'Litigation Tracker', desc: 'Live AI court cases — copyright, platform regulation, export control, competition, and constitutional challenges. Status updated weekly with primary court document links.' },
    { num: '14', title: 'Personnel &amp; Org Watch', desc: 'Leadership movements at AI labs and government AI bodies, revolving-door signals, and appointments that signal institutional AI priorities before any public announcement.' },
  ];

  const modulesHtml = moduleCards.map((m, i) => `      <a href="${ISSUE_URL}#module-${i}" class="module-overview-card">
        <div class="module-num">${m.num}</div>
        <h3>${m.title}</h3>
        <p>${m.desc}</p>
      </a>`).join('\n');

  const css = `
/* ---- Latest Issue Banner ---- */
.latest-banner { background: var(--color-primary); color: #fff; padding-block: var(--space-4); text-align: center; }
.latest-banner a { color: #fff; text-decoration: none; font-weight: 600; }
.latest-banner a:hover { color: #d0f0ef; }

/* ---- Hero Section ---- */
.hero { background: var(--color-surface); border-bottom: 1px solid var(--color-border); padding-block: clamp(var(--space-12), 6vw, var(--space-20)); }
.hero-inner { display: grid; grid-template-columns: 1fr auto; gap: var(--space-12); align-items: center; }
@media (max-width: 768px) { .hero-inner { grid-template-columns: 1fr; } }
.hero-eyebrow { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); flex-wrap: wrap; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-2xl); font-weight: 700; line-height: 1.15; letter-spacing: -0.02em; margin-bottom: var(--space-4); }
.hero-title .accent { color: var(--color-primary); }
.hero-tagline { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-lg); font-weight: 500; color: var(--color-text-muted); letter-spacing: 0.02em; margin-bottom: var(--space-6); }
.hero-desc { font-size: var(--text-base); color: var(--color-text-muted); max-width: 60ch; line-height: 1.7; }
.hero-cta { display: flex; gap: var(--space-4); margin-top: var(--space-8); flex-wrap: wrap; }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-6); border-radius: var(--radius-md); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-sm); font-weight: 600; letter-spacing: 0.02em; cursor: pointer; transition: all var(--transition); text-decoration: none; white-space: nowrap; }
.btn--primary { background: var(--color-primary); color: #fff; border: 1px solid transparent; }
.btn--primary:hover { background: var(--color-primary-hover); color: #fff; text-decoration: none; }
.btn--outline { background: transparent; color: var(--color-primary); border: 1px solid var(--color-primary); }
.btn--outline:hover { background: var(--color-primary-light); text-decoration: none; }
.hero-stats { display: flex; flex-direction: column; gap: var(--space-6); }
.stat-card { background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-6); text-align: center; min-width: 140px; }
.stat-number { font-family: 'Inter', -apple-system, sans-serif; font-size: var(--text-xl); font-weight: 800; color: var(--color-primary); line-height: 1; display: block; font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
.stat-label { font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-text-muted); margin-top: var(--space-1); display: block; }

/* ---- Delta Strip ---- */
.delta-strip { background: var(--color-surface-2); border-bottom: 1px solid var(--color-divider); padding-block: var(--space-5); }
.delta-label { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--color-text-muted); margin-bottom: var(--space-3); }
.delta-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-2); }
.delta-list li { font-size: var(--text-sm); display: flex; align-items: baseline; gap: var(--space-2); flex-wrap: wrap; }
.delta-arrow { color: var(--color-primary); font-weight: 700; flex-shrink: 0; }
.delta-module { font-size: var(--text-xs); font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: var(--color-primary); background: var(--color-primary-light); border-radius: var(--radius-full); padding: 0.1em 0.6em; text-decoration: none; margin-left: auto; white-space: nowrap; }
.delta-module:hover { background: var(--color-primary-medium); text-decoration: none; }

/* ---- Module Cards ---- */
.modules-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-5); margin-top: var(--space-8); }
.module-overview-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-6); transition: all var(--transition); text-decoration: none !important; color: var(--color-text); display: block; }
.module-overview-card:hover { border-color: var(--color-primary-medium); box-shadow: 0 4px 24px rgba(0,107,111,0.08); text-decoration: none !important; color: var(--color-text); }
.module-overview-card *, .module-overview-card h3, .module-overview-card p, .module-overview-card div { text-decoration: none !important; }
.module-num { font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; font-weight: 800; color: var(--color-primary-medium); line-height: 1; margin-bottom: var(--space-2); }
.module-overview-card h3 { font-size: var(--text-base); font-weight: 700; margin-bottom: var(--space-2); }
.module-overview-card p { font-size: var(--text-sm); color: var(--color-text-muted); line-height: 1.6; max-width: none; }

/* ---- Section Headings ---- */
.section-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-3); display: block; }
.section-title { font-size: var(--text-xl); margin-bottom: var(--space-4); }
.section-desc { font-size: var(--text-base); color: var(--color-text-muted); max-width: 70ch; line-height: 1.7; }

/* ---- Audience ---- */
.audience-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-5); margin-top: var(--space-8); }
.audience-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-6); }
.audience-icon { font-size: 1.8rem; margin-bottom: var(--space-3); display: block; }
.audience-card h4 { margin-bottom: var(--space-2); }
.audience-card p { font-size: var(--text-sm); color: var(--color-text-muted); max-width: none; }
`;

  const body = `
<!-- Latest issue banner -->
<div class="latest-banner">
  <div class="container">
    <span class="text-sm">Latest Issue: Week of ${meta.week_label} · Vol. ${meta.volume} · Issue ${meta.issue} &nbsp;
      <a href="${ISSUE_URL}">Read now →</a>
    </span>
  </div>
</div>

<!-- Hero -->
<section class="hero">
  <div class="container">
    <div class="hero-inner">
      <div>
        <div class="hero-eyebrow">
          <span class="badge badge--teal">Intelligence Platform</span>
          <span class="badge badge--live">● Live</span>
          <span class="text-xs text-muted">Weekly · Every Thursday</span>
        </div>
        <h1 class="hero-title">
          <a href="https://ramparts.gi" target="_blank" rel="noopener" style="color:inherit;text-decoration:none">Ramparts</a>
          <span class="accent"> AI Frontier Monitor</span>
        </h1>
        <p class="hero-tagline">Asymmetric Intelligence</p>
        <p class="hero-desc">
          A weekly 360-degree intelligence brief built for professionals who cannot afford to be last to the signal.
          We do not summarise headlines. We find the signal everyone else missed — in the regulatory filing no one opened,
          the preprint that rewrites the consensus, the capability jump that outpaces the law that was supposed to govern it.
        </p>
        <div class="hero-cta">
          <a href="${ISSUE_URL}" class="btn btn--primary">Read Latest Issue →</a>
          <a href="${ABOUT_URL}" class="btn btn--outline">About the Monitor</a>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-card">
          <span class="stat-number">15</span>
          <span class="stat-label">Intelligence Modules</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">12</span>
          <span class="stat-label">Jurisdictions Tracked</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">11+</span>
          <span class="stat-label">AI Labs Monitored</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Delta Strip -->
<section class="delta-strip">
  <div class="container">
    <div class="delta-label">⚡ This week's key shifts</div>
    <ul class="delta-list">
${deltaItems}
    </ul>
  </div>
</section>

<!-- Module overview -->
<section class="section" style="background:var(--color-bg)">
  <div class="container">
    <span class="section-eyebrow">What We Cover</span>
    <h2 class="section-title">Fifteen Intelligence Modules</h2>
    <p class="section-desc">Every edition is structured as a Research Launchpad across twelve modules, each with primary-source citations and asymmetric signal analysis.</p>
    <div class="modules-grid">
${modulesHtml}
    </div>
  </div>
</section>

<!-- Built for you -->
<section class="section" style="background:var(--color-surface);border-top:1px solid var(--color-border)">
  <div class="container">
    <span class="section-eyebrow">Built for You</span>
    <h2 class="section-title">Who This Is For</h2>
    <div class="audience-grid">
      <div class="audience-card">
        <span class="audience-icon">⚖️</span>
        <h4>Legal Professionals</h4>
        <p>AI liability, copyright, regulatory compliance, and enforcement actions — with primary source links to the actual filings.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">📊</span>
        <h4>Investors &amp; Analysts</h4>
        <p>Funding rounds, valuation trajectories, Cursor Curve signals, and the infrastructure bets that don't make headlines.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🏛️</span>
        <h4>Regulators &amp; Policy Advisors</h4>
        <p>Governance gaps, regulatory arbitrage windows, and the implementation failures that emerge between law and enforcement.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🔒</span>
        <h4>Compliance Teams</h4>
        <p>Jurisdiction-by-jurisdiction law updates, enforcement actions, and the asymmetric obligations that catch firms off-guard.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">📰</span>
        <h4>Journalists</h4>
        <p>Primary-source citations you can verify and cite directly — lab blogs, arXiv preprints, court filings, regulatory texts. Every asymmetric signal documented before the mainstream press covers it.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🔍</span>
        <h4>Auditors</h4>
        <p>ISO 42001 conformity evidence, NIST AI RMF control mapping, EU AI Act compliance posture, and enforcement actions — structured to support AI system audits and assurance engagements.</p>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="section" style="background:var(--color-primary);color:#fff">
  <div class="container" style="text-align:center">
    <h2 style="color:#fff;margin-bottom:var(--space-4)">Read the Latest Issue</h2>
    <p style="color:rgba(255,255,255,0.8);max-width:55ch;margin-inline:auto;margin-bottom:var(--space-8)">Week of ${meta.week_label} · Vol. ${meta.volume} · Issue ${meta.issue}. All primary sources linked. All asymmetric signals flagged.</p>
    <a href="${ISSUE_URL}" class="btn" style="background:#fff;color:var(--color-primary);border:1px solid transparent">Open Report →</a>
    <p style="color:rgba(255,255,255,0.6);font-size:var(--text-xs);margin-top:var(--space-6)">Get in touch: <a href="mailto:info@ramparts.gi" style="color:rgba(255,255,255,0.8)">info@ramparts.gi</a></p>
  </div>
</section>`;

  return buildPage({
    title: 'Ramparts AI Frontier Monitor — Asymmetric Intelligence',
    description: 'Weekly AI intelligence monitor for investors, regulators, legal professionals, and compliance teams. Built by Ramparts, Gibraltar.',
    canonical: `${BASE_URL}/`,
    activePage: 'Home',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 2: ABOUT (static-about.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateAbout() {
  const css = `
.about-header { background: var(--color-surface); border-bottom: 1px solid var(--color-border); padding-block: var(--space-16); }
.about-header-inner { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-16); align-items: center; }
@media (max-width: 768px) { .about-header-inner { grid-template-columns: 1fr; } }
.about-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-4); display: block; }
.about-title { font-size: var(--text-2xl); font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: var(--space-5); }
.about-title a { color: var(--color-primary); text-decoration: none; }
.about-title a:hover { text-decoration: underline; }
.about-intro { font-size: var(--text-lg); font-weight: 500; color: var(--color-text-muted); line-height: 1.6; margin-bottom: var(--space-6); }
.about-lead { font-size: var(--text-base); color: var(--color-text-muted); line-height: 1.75; max-width: 65ch; }
.about-divider-card { background: var(--color-primary); color: #fff; border-radius: var(--radius-xl); padding: var(--space-8); font-family: 'Space Grotesk', sans-serif; }
.about-divider-card h3 { color: #fff; font-size: var(--text-lg); margin-bottom: var(--space-4); }
.about-divider-card p { color: rgba(255,255,255,0.85); font-size: var(--text-sm); line-height: 1.7; max-width: none; }
.about-divider-card a { color: #fff; font-weight: 700; }
.modules-table-section { padding-block: var(--space-16); background: var(--color-bg); }
.modules-table { width: 100%; border-collapse: collapse; }
.modules-table th { padding: var(--space-3) var(--space-5); text-align: left; background: var(--color-surface); border-bottom: 2px solid var(--color-divider); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--color-text-muted); }
.modules-table td { padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--color-divider); vertical-align: top; font-size: var(--text-sm); line-height: 1.6; }
.modules-table tr:last-child td { border-bottom: none; }
.modules-table tr:hover td { background: var(--color-surface-2); }
.mod-num { font-family: 'Space Grotesk', sans-serif; font-weight: 800; color: var(--color-primary-medium); font-size: var(--text-lg); }
.audience-section { padding-block: var(--space-16); background: var(--color-surface); border-top: 1px solid var(--color-border); }
.audience-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-5); margin-top: var(--space-8); }
.audience-card { background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-6); }
.audience-icon { font-size: 1.8rem; margin-bottom: var(--space-3); display: block; }
.audience-card h4 { margin-bottom: var(--space-2); }
.audience-card p { font-size: var(--text-sm); color: var(--color-text-muted); max-width: none; line-height: 1.65; }
.why-now { padding-block: var(--space-16); background: var(--color-bg); }
.why-now-inner { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-12); }
@media (max-width: 768px) { .why-now-inner { grid-template-columns: 1fr; } }
.cta-section { background: var(--color-primary); color: #fff; padding-block: var(--space-16); text-align: center; }
.cta-section h2 { color: #fff; margin-bottom: var(--space-4); }
.cta-section p { color: rgba(255,255,255,0.8); max-width: 55ch; margin-inline: auto; margin-bottom: var(--space-8); }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-6); border-radius: var(--radius-md); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-sm); font-weight: 600; cursor: pointer; transition: all var(--transition); text-decoration: none; white-space: nowrap; border: 1px solid transparent; }
`;

  const body = `
<!-- About Header -->
<section class="about-header">
  <div class="container">
    <div class="about-header-inner">
      <div>
        <span class="about-eyebrow">Introducing</span>
        <h1 class="about-title">
          <a href="https://ramparts.gi" target="_blank" rel="noopener">Ramparts</a> AI Frontier Monitor<br>
          <span style="color:var(--color-text-muted);font-weight:500;font-size:0.6em;letter-spacing:0">Asymmetric Intelligence</span>
        </h1>
        <p class="about-intro">
          <a href="https://ramparts.gi" target="_blank" rel="noopener">Ramparts law firm</a>, Gibraltar, is today launching a weekly AI intelligence monitor built for the professionals who cannot afford to be last to the news and information.
        </p>
        <div class="about-lead">
          <p>This is not another AI newsletter. It does not summarise headlines. It exists for one purpose: to find the signal that everyone else missed — in the regulatory filing no one opened, the preprint that rewrites the consensus, the capability jump that outpaces the law that was supposed to govern it, or the under-appreciated AI investment opportunities and risks.</p>
        </div>
      </div>
      <div class="about-divider-card">
        <h3>Why This Exists</h3>
        <p>The gap between what AI can do and what lawyers think it can do has never been wider. The gap between what the mainstream press covers and what actually matters to a boardroom, a regulator, or a fund manager is where the asymmetric reward exists.</p>
        <p style="margin-top:var(--space-4)">Ramparts closes the gaps, every week using AI.</p>
        <p style="margin-top:var(--space-4)">Get in touch: <a href="mailto:info@ramparts.gi">info@ramparts.gi</a></p>
      </div>
    </div>
  </div>
</section>

<!-- What the Monitor Covers -->
<section class="modules-table-section">
  <div class="container">
    <span class="about-eyebrow">What the Monitor Covers</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-3)">Fifteen Intelligence Modules</h2>
    <p style="font-size:var(--text-base);color:var(--color-text-muted);max-width:65ch;margin-bottom:var(--space-8)">Each weekly edition is structured as a 360-degree Research Launchpad. Every item includes a working hyperlink to the primary source — the official regulatory text, lab research blog, arXiv preprint, or court filing — not the press article about it.</p>
    <div class="table-wrapper">
      <table class="modules-table">
        <thead><tr><th>#</th><th>Module</th><th>What It Covers</th></tr></thead>
        <tbody>
          <tr><td class="mod-num">00</td><td><strong>The Signal</strong></td><td>One paragraph. The single most strategically important signal of the week and why it matters in 12 months. Editorial judgment — not a summary of headlines.</td></tr>
          <tr><td class="mod-num">01</td><td><strong>Executive Insight</strong></td><td>The top five mainstream shifts and five underweighted signals the mainstream press missed — found in technical appendices, obscure regulatory filings, niche research blogs, and academic preprints.</td></tr>
          <tr><td class="mod-num">02</td><td><strong>Model Frontier</strong></td><td>Capability tracking across OpenAI, Anthropic, Google DeepMind, xAI, Meta, Mistral, DeepSeek, Alibaba, Nvidia and others. Benchmark tables. Architectural innovation flags.</td></tr>
          <tr><td class="mod-num">03</td><td><strong>Investment &amp; M&amp;A</strong></td><td>Funding rounds above $50M, hyper-growth companies on the "Cursor Curve" (zero to $1B ARR in under 24 months), and acqui-hires disguised as partnerships.</td></tr>
          <tr><td class="mod-num">04</td><td><strong>Sector Penetration</strong></td><td>Healthcare, Legal, Finance, Defence, Media, Education, Critical Infrastructure — Accelerating, Stalling, or Emerging. Capability-to-deployment gaps flagged. Stealth deployments noted.</td></tr>
          <tr><td class="mod-num">05</td><td><strong>European &amp; China Watch</strong></td><td>EU AI Act compliance posture. Sovereign AI infrastructure. DeepSeek/Alibaba/Zhipu AI capability trajectory. Export control bypasses. State-directed AI deployment.</td></tr>
          <tr><td class="mod-num">06</td><td><strong>AI in Science</strong></td><td>Tracking the threshold from "useful assistant" to "autonomous research contributor" across biology, medicine, physics, climate, and more. AlphaFold, Genesis Mission, and peer-reviewed threshold events.</td></tr>
          <tr><td class="mod-num">07</td><td><strong>Risk Indicators: 2028</strong></td><td>Governance fragmentation, cyber escalation, platform power, export controls, and disinformation velocity — with 2028 horizon implications and governance gap analysis.</td></tr>
          <tr><td class="mod-num">08</td><td><strong>Law &amp; Guidance</strong></td><td>Every major jurisdiction, every binding law and regulatory guidance, updated weekly. Includes the 12-jurisdiction Country Grid (full status table, 🆕/⚠️ change flags) embedded within this module.</td></tr>
          <tr><td class="mod-num">09</td><td><strong>AI Governance</strong></td><td>International soft law and principles, corporate governance signals, product liability tracker (EU PLD, US strict liability), algorithmic accountability enforcement (Colorado AI Act, NYC AEDT, CFPB), and governance gaps being actively exploited. Voluntary commitments flagged as leading indicators of binding law.</td></tr>
          <tr><td class="mod-num">08</td><td><strong>Military AI Watch</strong></td><td>Defence procurement signals, autonomous weapons doctrine updates, IHL friction analysis, and international treaty developments. Tracks asymmetric implications of AI in weapons systems and dual-use capabilities for legal, compliance, and investment professionals.</td></tr>
          <tr><td class="mod-num">09</td><td><strong>Law &amp; Guidance</strong></td><td>Every major jurisdiction, every binding law and regulatory guidance, updated weekly. Includes the 12-jurisdiction Country Grid and EU AI Act Layered System tracker.</td></tr>
          <tr><td class="mod-num">10</td><td><strong>AI Governance</strong></td><td>International soft law and principles, corporate governance signals, product liability tracker (EU PLD, US strict liability), algorithmic accountability enforcement, and governance gaps being actively exploited.</td></tr>
          <tr><td class="mod-num">11</td><td><strong>Ethics &amp; Accountability</strong></td><td>Bias measurement standards, transparency obligations, corporate accountability signals, lab ethics commitments and their commercial implications, research ethics developments — with primary source citations and asymmetric accountability analysis.</td></tr>
          <tr><td class="mod-num">12</td><td><strong>Technical Standards</strong></td><td>ISO/IEC JTC1 SC42 (42001, 23894, 5338), NIST AI RMF, IEEE 7000-series, EU CEN-CENELEC harmonised standards, ETSI ISG SAI, and OECD AI Principles — tracked separately from law because they move on independent timelines.</td></tr>
          <tr><td class="mod-num">13</td><td><strong>Litigation Tracker</strong></td><td>Running table of active AI litigation across copyright, liability, data protection, competition, and constitutional law. Status updated weekly. Primary court documents linked. Covers USA, EU, and UK jurisdictions.</td></tr>
          <tr><td class="mod-num">14</td><td><strong>Personnel &amp; Org Watch</strong></td><td>Leadership movements at AI labs and government AI bodies, revolving-door signals, and the appointments that signal institutional AI priorities before any public announcement. Covers labs, defence, regulatory agencies, and international bodies.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- Built for You -->
<section class="audience-section">
  <div class="container">
    <span class="about-eyebrow">Built for You</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-3)">Who This Is For</h2>
    <p style="font-size:var(--text-base);color:var(--color-text-muted);max-width:60ch">Ramparts is designed for investors, regulators, legal professionals, compliance teams, and policy advisors who need to act on what is happening now — not what has already been covered.</p>
    <div class="audience-grid">
      <div class="audience-card">
        <span class="audience-icon">⚖️</span>
        <h4>Legal Professionals</h4>
        <p>AI liability frameworks, copyright developments, enforcement actions, and regulatory compliance obligations — with primary-source links to the actual filings, not the coverage.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">📊</span>
        <h4>Investors &amp; Analysts</h4>
        <p>Funding rounds, valuation trajectories, secondary market signals, Cursor Curve hyper-growth companies, and the infrastructure bets that don't make mainstream headlines.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🏛️</span>
        <h4>Regulators &amp; Policy Advisors</h4>
        <p>Governance gaps, regulatory arbitrage windows, implementation failures, and the technical capability jumps that outpace the law designed to govern them.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🔒</span>
        <h4>Compliance Teams</h4>
        <p>Jurisdiction-by-jurisdiction law updates, enforcement actions, and the asymmetric obligations that emerge between legislative intent and implementation reality.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">📰</span>
        <h4>Journalists</h4>
        <p>Primary-source citations you can verify and cite directly — lab blogs, arXiv preprints, court filings, regulatory texts. Every asymmetric signal is documented before the mainstream press covers it.</p>
      </div>
      <div class="audience-card">
        <span class="audience-icon">🔍</span>
        <h4>Auditors</h4>
        <p>ISO 42001 conformity evidence, NIST AI RMF control mapping, EU AI Act compliance posture, and enforcement actions — structured to support AI system audits and third-party assurance engagements.</p>
      </div>
    </div>
  </div>
</section>

<!-- Author card -->
<section style="background:var(--color-bg);padding-block:clamp(var(--space-12),6vw,var(--space-20));border-top:1px solid var(--color-border)">
  <div class="container">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:var(--text-xs);font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--color-primary);margin-bottom:var(--space-3);display:block">Editor &amp; Lead Analyst</span>
    <div style="display:grid;grid-template-columns:auto 1fr;gap:var(--space-8);align-items:start;max-width:780px">
      <div style="width:72px;height:72px;border-radius:50%;background:var(--color-primary-light);border:2px solid var(--color-primary-medium);display:flex;align-items:center;justify-content:center;flex-shrink:0">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" aria-hidden="true">
          <circle cx="18" cy="13" r="6" stroke="currentColor" stroke-width="1.8" fill="none" style="color:var(--color-primary)"/>
          <path d="M6 31c0-6.627 5.373-12 12-12s12 5.373 12 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none" style="color:var(--color-primary)"/>
        </svg>
      </div>
      <div>
        <h3 style="font-size:var(--text-lg);margin-bottom:var(--space-1)">Peter Howitt</h3>
        <p style="font-size:var(--text-sm);color:var(--color-primary);font-weight:600;margin-bottom:var(--space-4)">CEO, <a href="https://ramparts.gi" target="_blank" rel="noopener">Ramparts</a> · Gibraltar</p>
        <p style="font-size:var(--text-base);color:var(--color-text-muted);line-height:1.75;max-width:60ch">Peter Howitt is CEO of Ramparts, a Gibraltar law firm specialising in cross-border financial services regulation, payments, AI governance, and strategic intelligence. He is a recognised leader on the intersection of emerging technology and law. He created the Ramparts AI Frontier Monitor to show what AI can do and to help professionals track developments.</p>
        <div style="display:flex;gap:var(--space-4);margin-top:var(--space-5);flex-wrap:wrap">
          <a href="https://ramparts.gi" target="_blank" rel="noopener" style="font-size:var(--text-sm);color:var(--color-primary);text-decoration:none;display:flex;align-items:center;gap:var(--space-1)">↗ Ramparts.gi</a>
          <a href="mailto:peterhowitt@ramparts.gi" style="font-size:var(--text-sm);color:var(--color-text-muted);text-decoration:none">peterhowitt@ramparts.gi</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Editorial Policy -->
<section style="background:var(--color-surface);padding-block:clamp(var(--space-12),6vw,var(--space-20));border-top:1px solid var(--color-border)">
  <div class="container">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:var(--text-xs);font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--color-primary);margin-bottom:var(--space-3);display:block">Editorial Standards</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-6)">How We Work</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--space-6)">
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Source Hierarchy</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">Every item links to its primary source: a lab research blog, arXiv preprint, official regulatory text, court filing, or government gazette. Specialist press (Reuters, Bloomberg, The Information, Lawfare) is used only when no primary source exists. General tech press is used only as a last resort and is always flagged <strong>⚠️ Tier 3</strong>.</p>
      </div>
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Temporal Scope</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">Each edition covers the 7 calendar days ending on publication date. If no material development exists for a module in a given week, we state this explicitly rather than padding with stale material.</p>
      </div>
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Asymmetric Analysis</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">For every major development, we identify one non-obvious consequence — information found in technical appendices, obscure regulatory filings, or academic preprints that the mainstream press has missed or underweighted.</p>
      </div>
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Independence</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">The Ramparts AI Frontier Monitor is editorially independent. Coverage is not influenced by commercial relationships, client mandates, or external funding.</p>
      </div>
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Corrections</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">Factual errors are corrected inline in the published report with a visible correction note and timestamp. We do not silently edit published content. To report an error: <a href="mailto:corrections@ramparts.gi">corrections@ramparts.gi</a></p>
      </div>
      <div style="background:var(--color-bg);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-6)">
        <h4 style="margin-bottom:var(--space-3)">Research Methodology</h4>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:none">Each edition is produced using AI-assisted research (Perplexity Computer) under editorial direction and review by the named analyst. All source verification, asymmetric analysis, and editorial judgments are human-reviewed before publication. Research window closes at 07:00 UTC each Thursday.</p>
      </div>
    </div>
  </div>
</section>

<!-- Why Now -->
<section class="why-now">
  <div class="container">
    <div class="why-now-inner">
      <div>
        <span class="about-eyebrow">Why Now</span>
        <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-5)">The Gap Has Never Been Wider</h2>
        <div style="font-size:var(--text-base);color:var(--color-text-muted);line-height:1.75;display:flex;flex-direction:column;gap:var(--space-4)">
          <p>The gap between what AI can do and what lawyers think it can do has never been wider. The gap between what the mainstream press covers and what actually matters to a boardroom, a regulator, or a fund manager is where the asymmetric reward exists.</p>
          <p>Frontier AI models are simultaneously superhuman on domain-specific reasoning and sub-toddler on novel adaptive tasks. Regulatory frameworks calibrated for one version of capability are being outrun by the next. The enforcement infrastructure in 19 of 27 EU member states does not yet exist.</p>
          <p>Ramparts closes the gaps, every week using AI.</p>
        </div>
      </div>
      <div>
        <span class="about-eyebrow">Source Hierarchy</span>
        <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-5)">Primary Sources Only</h2>
        <div style="display:flex;flex-direction:column;gap:var(--space-4)">
          <div class="card">
            <div style="display:flex;align-items:flex-start;gap:var(--space-3)">
              <span class="badge badge--teal">Tier 1</span>
              <div>
                <h4 style="margin-bottom:var(--space-1)">Primary Sources</h4>
                <p class="text-sm text-muted">Lab research blogs, arXiv/bioRxiv preprints, official regulatory texts, court filings, government gazettes. Always the first choice.</p>
              </div>
            </div>
          </div>
          <div class="card">
            <div style="display:flex;align-items:flex-start;gap:var(--space-3)">
              <span class="badge badge--amber">Tier 2</span>
              <div>
                <h4 style="margin-bottom:var(--space-1)">Specialist Press</h4>
                <p class="text-sm text-muted">The Information, Import AI, MLCommons, Politico Pro Tech, Lawfare, Reuters, Bloomberg. Used when primary source unavailable.</p>
              </div>
            </div>
          </div>
          <div class="card">
            <div style="display:flex;align-items:flex-start;gap:var(--space-3)">
              <span class="badge badge--risk-elevated">⚠️ Tier 3</span>
              <div>
                <h4 style="margin-bottom:var(--space-1)">General Tech Press</h4>
                <p class="text-sm text-muted">Used only if no Tier 1 or Tier 2 source exists. Always flagged explicitly as "⚠️ Tier 3 source — primary not found."</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <div class="container">
    <h2>Read the Latest Issue</h2>
    <p>Week of ${reportData.meta.week_label} · Vol. ${reportData.meta.volume} · Issue ${reportData.meta.issue}. All primary sources linked. All asymmetric signals flagged.</p>
    <a href="${ISSUE_URL}" class="btn" style="background:#fff;color:var(--color-primary)">Open Report →</a>
    <p style="color:rgba(255,255,255,0.6);font-size:var(--text-xs);margin-top:var(--space-6)">Contact: <a href="mailto:info@ramparts.gi" style="color:rgba(255,255,255,0.8)">info@ramparts.gi</a> · <a href="https://ramparts.gi" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.8)">ramparts.gi</a></p>
  </div>
</section>`;

  return buildPage({
    title: 'About — Ramparts AI Frontier Monitor',
    description: 'About the Ramparts AI Frontier Monitor — weekly AI intelligence built for investors, regulators, legal professionals, and compliance teams.',
    canonical: ABOUT_URL,
    activePage: 'About',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 3: ARCHIVE (static-archive.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateArchive() {
  const css = `
.page-header { background: var(--color-surface); border-bottom: 1px solid var(--color-border); padding-block: var(--space-12); }
.page-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-3); display: block; }
.page-title { font-size: var(--text-xl); font-weight: 700; margin-bottom: var(--space-3); }
.page-desc { font-size: var(--text-base); color: var(--color-text-muted); max-width: 65ch; }
.archive-grid { display: flex; flex-direction: column; gap: var(--space-5); padding-block: var(--space-10); }
.archive-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4); transition: all var(--transition); text-decoration: none; color: var(--color-text); }
.archive-card:hover { border-color: var(--color-primary-medium); box-shadow: 0 4px 24px rgba(0,107,111,0.08); text-decoration: none; color: var(--color-text); }
.archive-card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-6); flex-wrap: wrap; }
.archive-issue { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-text-muted); }
.archive-week { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-lg); font-weight: 700; }
.archive-date { font-size: var(--text-xs); color: var(--color-text-muted); }
.archive-signal { font-size: var(--text-sm); color: var(--color-text-muted); font-style: italic; border-left: 3px solid var(--color-primary); padding-left: var(--space-4); }
.archive-signals-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-2); }
.archive-signals-list li { font-size: var(--text-sm); display: flex; gap: var(--space-2); }
.archive-signals-list li::before { content: '→'; color: var(--color-primary); flex-shrink: 0; }
`;

  // Render archive cards in reverse chronological order
  const issues = [...archiveData].reverse();
  const cardsHtml = issues.map(issue => {
    const pubDate = new Date(issue.published).toLocaleDateString('en-GB', {day: 'numeric', month: 'long', year: 'numeric'});
    const pubTime = issue.published_utc ? ` · ${issue.published_utc} UTC` : '';
    const signalsHtml = (issue.top_signals || []).map(s => `          <li>${s}</li>`).join('\n');
    const issueUrl = issue.wp_url || `https://ramparts.gi/ai-frontier-monitor-issue-${issue.slug}/`;
    return `    <a href="${issueUrl}" class="archive-card">
      <div class="archive-card-header">
        <div>
          <div class="archive-issue">Vol. ${issue.volume} · Issue ${issue.issue}</div>
          <div class="archive-week">Week of ${issue.week_label}</div>
          <div class="archive-date">Published ${pubDate}${pubTime}</div>
        </div>
        <span class="badge badge--teal">Read →</span>
      </div>
      <div class="archive-signal">${issue.editors_signal_preview}</div>
      <ul class="archive-signals-list">
${signalsHtml}
      </ul>
    </a>`;
  }).join('\n');

  const body = `
<div class="page-header">
  <div class="container">
    <span class="page-eyebrow">All Issues</span>
    <h1 class="page-title">Archive</h1>
    <p class="page-desc">Every weekly edition of the Ramparts AI Frontier Monitor, with The Signal preview and key developments.</p>
  </div>
</div>

<div class="container">
  <div class="archive-grid">
${cardsHtml}
  </div>
</div>`;

  return buildPage({
    title: 'Archive — Ramparts AI Frontier Monitor',
    description: 'Every weekly edition of the Ramparts AI Frontier Monitor — The Signal preview, key developments, and primary source links.',
    canonical: ARCHIVE_URL,
    activePage: 'Archive',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 4: DIGEST (static-digest.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateDigest() {
  const meta = reportData.meta;
  const signalText = stripHtml(reportData.module_0?.body || '');
  const words = signalText.split(' ');
  const signalTruncated = words.slice(0, 80).join(' ') + (words.length > 80 ? '…' : '');
  const deltaItems = (reportData.delta_strip || []).map(d => `          <li>${stripHtml(d.text)}</li>`).join('\n');

  const css = `
.digest-hero { background: var(--color-surface); border-bottom: 1px solid var(--color-border); padding-block: clamp(var(--space-16),8vw,var(--space-24)); text-align: center; }
.digest-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-4); display: block; }
.digest-title { font-size: var(--text-2xl); font-weight: 800; letter-spacing: -0.02em; margin-bottom: var(--space-4); }
.digest-sub { font-size: var(--text-lg); color: var(--color-text-muted); max-width: 55ch; margin-inline: auto; margin-bottom: var(--space-10); line-height: 1.6; }
.email-preview { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-xl); max-width: 620px; margin-inline: auto; overflow: hidden; box-shadow: 0 8px 40px rgba(0,0,0,0.08); }
.email-header { background: var(--color-primary); padding: var(--space-6) var(--space-8); text-align: left; }
.email-header-top { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }
.email-logo-text { font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #fff; font-size: var(--text-sm); letter-spacing: 0.08em; text-transform: uppercase; }
.email-subject { color: #fff; font-family: 'Space Grotesk', sans-serif; font-size: var(--text-lg); font-weight: 700; line-height: 1.3; margin-bottom: var(--space-2); }
.email-meta { color: rgba(255,255,255,0.7); font-size: var(--text-xs); }
.email-body { padding: var(--space-8); background: var(--color-bg); }
.email-signal-label { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--color-primary); border-bottom: 2px solid var(--color-primary); padding-bottom: var(--space-2); margin-bottom: var(--space-4); display: block; }
.email-signal-text { font-size: var(--text-sm); line-height: 1.75; color: var(--color-text); margin-bottom: var(--space-6); }
.email-delta-label { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--color-text-muted); margin-bottom: var(--space-3); display: block; }
.email-delta-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-6); }
.email-delta-list li { font-size: var(--text-sm); display: flex; gap: var(--space-2); line-height: 1.5; }
.email-delta-list li::before { content: '→'; color: var(--color-primary); font-weight: 700; flex-shrink: 0; }
.email-cta { display: block; background: var(--color-primary); color: #fff; text-align: center; padding: var(--space-3) var(--space-6); border-radius: var(--radius-md); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-sm); font-weight: 600; text-decoration: none; transition: background var(--transition); }
.email-cta:hover { background: var(--color-primary-hover); text-decoration: none; color: #fff; }
.email-footer-note { text-align: center; font-size: 11px; color: var(--color-text-faint); margin-top: var(--space-5); line-height: 1.5; }
.subscribe-section { padding-block: clamp(var(--space-12),6vw,var(--space-20)); background: var(--color-bg); }
.subscribe-inner { max-width: 540px; margin-inline: auto; text-align: center; }
.subscribe-inner h2 { font-size: var(--text-xl); margin-bottom: var(--space-3); }
.subscribe-inner p { font-size: var(--text-base); color: var(--color-text-muted); margin-bottom: var(--space-8); }
.subscribe-form { display: flex; gap: var(--space-3); flex-wrap: wrap; }
.subscribe-input { flex: 1; min-width: 240px; padding: var(--space-3) var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-base); background: var(--color-surface); color: var(--color-text); font-family: 'Inter', sans-serif; transition: border-color var(--transition); }
.subscribe-input:focus { outline: none; border-color: var(--color-primary); }
.subscribe-btn { padding: var(--space-3) var(--space-6); background: var(--color-primary); color: #fff; border: none; border-radius: var(--radius-md); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-sm); font-weight: 600; cursor: pointer; transition: background var(--transition); white-space: nowrap; }
.subscribe-btn:hover { background: var(--color-primary-hover); }
.subscribe-note { font-size: var(--text-xs); color: var(--color-text-faint); margin-top: var(--space-4); }
.subscribe-success { display: none; background: var(--color-primary-light); border: 1px solid var(--color-primary-medium); border-radius: var(--radius-md); padding: var(--space-5); text-align: center; color: var(--color-primary); font-weight: 600; }
.promises-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: var(--space-5); margin-top: var(--space-10); text-align: left; }
.promise-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-5); }
.promise-icon { font-size: 1.5rem; margin-bottom: var(--space-3); display: block; }
.promise-card h4 { font-size: var(--text-sm); margin-bottom: var(--space-2); }
.promise-card p { font-size: var(--text-xs); color: var(--color-text-muted); max-width: none; line-height: 1.65; }
`;

  const body = `
<!-- Hero -->
<section class="digest-hero">
  <div class="container">
    <span class="digest-eyebrow">Weekly Digest</span>
    <h1 class="digest-title">The Signal. Five Developments. 200 Words.</h1>
    <p class="digest-sub">Every Thursday at 09:00 GMT — The Signal from this week's issue, the five key changes, and one link to the full report. Nothing else.</p>

    <!-- Email preview from latest report -->
    <div class="email-preview">
      <div class="email-header">
        <div class="email-header-top">
          <svg width="20" height="20" viewBox="0 0 36 36" fill="none"><path d="M18 2L4 8v10c0 8.5 6 16 14 18 8-2 14-9.5 14-18V8L18 2z" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"/></svg>
          <span class="email-logo-text">Ramparts AI Frontier Monitor</span>
        </div>
        <div class="email-subject">The Signal — Week of ${meta.week_label}</div>
        <div class="email-meta">Vol. ${meta.volume} · Issue ${meta.issue} · Asymmetric Intelligence · ramparts.gi</div>
      </div>
      <div class="email-body">
        <span class="email-signal-label">⚡ The Signal</span>
        <p class="email-signal-text">${signalTruncated}</p>
        <span class="email-delta-label">↯ Five Key Changes This Week</span>
        <ul class="email-delta-list">
${deltaItems}
        </ul>
        <a href="${ISSUE_URL}" class="email-cta">Read the full report →</a>
        <p class="email-footer-note">Published by Ramparts, Gibraltar · <a href="${BASE_URL}/about/" style="color:inherit">Editorial Policy</a> · You are receiving this because you subscribed at ramparts.gi/ai-frontier-monitor/digest/</p>
      </div>
    </div>
  </div>
</section>

<!-- Subscribe -->
<section class="subscribe-section">
  <div class="container">
    <div class="subscribe-inner">
      <h2>Subscribe to the Digest</h2>
      <p>One email, every Thursday. The Signal and five developments. No summaries of what you already know.</p>
      <form class="subscribe-form" id="subscribe-form" onsubmit="handleSubscribe(event)">
        <input type="email" class="subscribe-input" placeholder="your@email.com" required aria-label="Email address">
        <button type="submit" class="subscribe-btn">Subscribe →</button>
      </form>
      <p class="subscribe-note">No tracking. No third-party tools. Unsubscribe in one click. Contact: <a href="mailto:info@ramparts.gi">info@ramparts.gi</a></p>
      <div class="subscribe-success" id="subscribe-success">
        ✓ Subscribed. Check your inbox for a confirmation email — click the link to activate your subscription.
      </div>
      <div class="promises-grid">
        <div class="promise-card">
          <span class="promise-icon">⏱</span>
          <h4>200 words maximum</h4>
          <p>The Signal in full, the five key changes, one link. Respects your time completely.</p>
        </div>
        <div class="promise-card">
          <span class="promise-icon">📅</span>
          <h4>Every Thursday</h4>
          <p>09:00 GMT without exception. Reliable enough to build into your morning routine.</p>
        </div>
        <div class="promise-card">
          <span class="promise-icon">🔗</span>
          <h4>Primary sources only</h4>
          <p>Every link in the digest goes to the primary source — the actual regulatory text, the actual preprint.</p>
        </div>
        <div class="promise-card">
          <span class="promise-icon">🔒</span>
          <h4>No data sharing</h4>
          <p>Your email address is used solely to send the digest. It is never shared, sold, or used for any other purpose.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<script>
async function handleSubscribe(e) {
  e.preventDefault();
  const email = e.target.querySelector('input[type="email"]').value;
  const btn = e.target.querySelector('.subscribe-btn');
  btn.textContent = 'Subscribing…';
  btn.disabled = true;

  try {
    const res = await fetch('https://api.buttondown.com/v1/subscribers', {
      method: 'POST',
      headers: {
        'Authorization': 'Token baac934d-47b3-4e37-b6e3-1dbd1f3a89f4',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email_address: email, tags: ['digest'] })
    });

    if (res.ok || res.status === 409) {
      document.getElementById('subscribe-form').style.display = 'none';
      document.getElementById('subscribe-success').style.display = 'block';
    } else {
      const data = await res.json().catch(() => ({}));
      btn.textContent = 'Subscribe →';
      btn.disabled = false;
      alert('Something went wrong — please try again or email info@ramparts.gi');
      console.error('Buttondown error:', data);
    }
  } catch(err) {
    btn.textContent = 'Subscribe →';
    btn.disabled = false;
    alert('Network error — please try again or email info@ramparts.gi');
  }
}
</script>`;

  return buildPage({
    title: 'Weekly Digest — Ramparts AI Frontier Monitor',
    description: 'Subscribe to the Ramparts AI Frontier Monitor weekly digest — The Signal and five key developments, every Thursday. 200 words. No noise.',
    canonical: DIGEST_URL,
    activePage: 'Digest',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 5: GIBRALTAR (static-gibraltar.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateGibraltar() {
  const gib = gibraltarData;

  const regulatorsHtml = (gib.jurisdiction_profile?.key_regulators || []).map(r => `      <div class="obs-card">
        <h4>${r.name}</h4>
        <p>${r.ai_relevance}</p>
        <a href="${r.url}" target="_blank" rel="noopener" class="source-link" style="margin-top:var(--space-4)">↗ ${r.url.replace('https://', '')}</a>
      </div>`).join('\n');

  const frameworkRowsHtml = (gib.standing_frameworks || []).map(f => {
    const statusBadge = f.status.toLowerCase().includes('force') ? 'badge--teal' : 'badge--amber';
    return `          <tr>
            <td><strong>${f.instrument}</strong></td>
            <td><span class="badge ${statusBadge}">${f.status}</span></td>
            <td>${f.ai_relevance}</td>
            <td>${f.source_url ? `<a href="${f.source_url}" target="_blank" rel="noopener" class="source-link">↗ Source</a>` : '—'}</td>
          </tr>`;
  }).join('\n');

  const crownItems = (gib.crown_dependency_watch?.items || []).map(item => `      <div class="obs-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:var(--space-3);margin-bottom:var(--space-3)">
          <h4>${item.jurisdiction}</h4>
          <span class="badge badge--teal">Active</span>
        </div>
        <p>${item.development}</p>
        <a href="${item.source_url}" target="_blank" rel="noopener" class="source-link" style="margin-top:var(--space-4)">↗ ${item.source_url.replace('https://', '')}</a>
      </div>`).join('\n');

  const weeklyHtml = (gib.weekly_developments || []).map(w => `      <div class="weekly-item">
        <div class="weekly-item-date">${w.date}</div>
        <p class="text-sm">${w.item}</p>
      </div>`).join('\n');

  const css = `
.obs-header { background: linear-gradient(135deg,var(--color-surface) 0%,var(--color-primary-light) 100%); border-bottom: 2px solid var(--color-primary); padding-block: clamp(var(--space-12),6vw,var(--space-20)); }
.obs-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-4); display: flex; align-items: center; gap: var(--space-3); }
.obs-title { font-size: var(--text-2xl); font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: var(--space-4); }
.obs-sub { font-size: var(--text-lg); color: var(--color-text-muted); margin-bottom: var(--space-5); font-weight: 500; }
.obs-desc { font-size: var(--text-base); color: var(--color-text-muted); max-width: 70ch; line-height: 1.75; }
.obs-unique { background: var(--color-primary); color: #fff; border-radius: var(--radius-lg); padding: var(--space-5) var(--space-6); margin-top: var(--space-8); max-width: 600px; }
.obs-unique p { color: rgba(255,255,255,0.9); font-size: var(--text-sm); line-height: 1.7; max-width: none; }
.obs-unique strong { color: #fff; }
.obs-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(340px,1fr)); gap: var(--space-5); margin-top: var(--space-8); }
.obs-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-6); }
.obs-card h4 { margin-bottom: var(--space-3); }
.obs-card p { font-size: var(--text-sm); color: var(--color-text-muted); max-width: none; line-height: 1.65; }
.obs-card a { font-size: var(--text-sm); }
.section-label { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-3); display: block; }
.framework-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.framework-table th { padding: var(--space-3) var(--space-4); text-align: left; background: var(--color-surface-2); border-bottom: 2px solid var(--color-divider); font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--color-text-muted); }
.framework-table td { padding: var(--space-4); border-bottom: 1px solid var(--color-divider); vertical-align: top; line-height: 1.6; }
.framework-table tr:last-child td { border-bottom: none; }
.framework-table tr:hover td { background: var(--color-surface-2); }
.weekly-item { background: var(--color-surface); border: 1px solid var(--color-border); border-left: 4px solid var(--color-primary); border-radius: var(--radius-md); padding: var(--space-5); margin-bottom: var(--space-4); }
.weekly-item-date { font-size: var(--text-xs); font-weight: 700; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-2); }
`;

  const body = `
<!-- Observatory Header -->
<section class="obs-header">
  <div class="container">
    <div class="obs-eyebrow">
      <svg width="18" height="18" viewBox="0 0 36 36" fill="none"><path d="M18 2L4 8v10c0 8.5 6 16 14 18 8-2 14-9.5 14-18V8L18 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
      Gibraltar AI Regulatory Observatory
    </div>
    <h1 class="obs-title">Gibraltar &amp; Crown Dependencies<br>AI Governance Tracker</h1>
    <p class="obs-sub">The only dedicated monitor for AI regulatory developments in Gibraltar, the Crown Dependencies, and their relationship with UK and EU frameworks.</p>
    <p class="obs-desc">${gib.description}</p>
    <div class="obs-unique">
      <strong style="font-family:'Space Grotesk',sans-serif;font-size:var(--text-sm);letter-spacing:0.04em">Why this matters</strong>
      <p style="margin-top:var(--space-2)">${gib.strategic_context}</p>
    </div>
  </div>
</section>

<!-- Jurisdiction Profile -->
<section class="section" style="background:var(--color-bg)">
  <div class="container">
    <span class="section-label">Jurisdiction Profile</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-3)">Gibraltar — Regulatory Position</h2>
    <p class="text-sm text-muted" style="margin-bottom:var(--space-6);max-width:70ch">${gib.jurisdiction_profile.relationship_to_eu}</p>
    <div class="obs-grid">
${regulatorsHtml}
      <div class="obs-card" style="border-left:3px solid var(--color-primary)">
        <h4>EU AI Act — Extraterritorial Reach</h4>
        <p>The EU AI Act does not directly apply in Gibraltar, but Gibraltar firms deploying AI systems to EU-market users or within EU-regulated entities face EU AI Act obligations as deployers. This is the primary cross-border compliance exposure for Gibraltar's financial sector.</p>
        <a href="https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/artificial-intelligence-act-delayed-application-ban-on-nudifier-apps" target="_blank" rel="noopener" class="source-link" style="margin-top:var(--space-4)">↗ Latest EU AI Act status</a>
      </div>
      <div class="obs-card">
        <h4>UK AI Framework — Indirect Application</h4>
        <p>Gibraltar maintains close alignment with UK financial services frameworks. UK FCA and PRA supervisory expectations on AI governance (model risk, explainability, fairness) apply to Gibraltar firms operating in UK markets or under UK regulatory equivalence arrangements.</p>
        <a href="https://www.fca.org.uk/publication/corporate/ai-update.pdf" target="_blank" rel="noopener" class="source-link" style="margin-top:var(--space-4)">↗ FCA AI Update</a>
      </div>
    </div>
  </div>
</section>

<!-- Standing Frameworks -->
<section class="section" style="background:var(--color-surface);border-top:1px solid var(--color-border)">
  <div class="container">
    <span class="section-label">Standing Frameworks</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-6)">Gibraltar AI Governance Baseline</h2>
    <div class="table-wrapper">
      <table class="framework-table">
        <thead>
          <tr><th>Instrument</th><th>Status</th><th>AI Relevance</th><th>Source</th></tr>
        </thead>
        <tbody>
${frameworkRowsHtml}
          <tr>
            <td><strong>Dedicated Gibraltar AI Framework</strong></td>
            <td><span class="badge badge--amber">Not yet enacted</span></td>
            <td>No dedicated AI statute or binding guidance from GFSC or GRA as of March 2026. Existing governance frameworks apply. Ramparts monitors GFSC communications for signals of upcoming guidance.</td>
            <td>—</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- Crown Dependencies Watch -->
<section class="section" style="background:var(--color-bg);border-top:1px solid var(--color-border)">
  <div class="container">
    <span class="section-label">Crown Dependencies Watch</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-3)">Jersey · Guernsey · Isle of Man</h2>
    <p class="text-sm text-muted" style="margin-bottom:var(--space-6);max-width:70ch">${gib.crown_dependency_watch.note}</p>
    <div class="obs-grid">
${crownItems}
      <div class="obs-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:var(--space-3);margin-bottom:var(--space-3)">
          <h4>Guernsey</h4>
          <span class="badge badge--amber">Watch</span>
        </div>
        <p>Guernsey Financial Services Commission has not yet published AI-specific guidance. Data protection framework (Data Protection (Bailiwick of Guernsey) Law 2017, GDPR-equivalent) applies to AI data processing. Monitoring for 2026 guidance signals.</p>
        <a href="https://www.gfsc.gg" target="_blank" rel="noopener" class="source-link" style="margin-top:var(--space-4)">↗ GFSC Guernsey</a>
      </div>
    </div>
  </div>
</section>

<!-- Weekly Updates -->
<section class="section" style="background:var(--color-surface);border-top:1px solid var(--color-border)">
  <div class="container container--narrow">
    <span class="section-label">Weekly Updates</span>
    <h2 style="font-size:var(--text-xl);margin-bottom:var(--space-6)">Recent Developments</h2>
    <div id="weekly-updates">
${weeklyHtml}
    </div>
  </div>
</section>

<!-- Contact / Contribute -->
<section class="section" style="background:var(--color-primary);color:#fff;text-align:center">
  <div class="container">
    <h2 style="color:#fff;margin-bottom:var(--space-4)">Contribute to the Observatory</h2>
    <p style="color:rgba(255,255,255,0.85);max-width:55ch;margin-inline:auto;margin-bottom:var(--space-6);font-size:var(--text-base)">If you are a Gibraltar practitioner, regulator, or academic with a development to flag — GFSC guidance, court proceedings, parliamentary questions, or policy consultations — contact the editorial team.</p>
    <a href="mailto:observatory@ramparts.gi" style="display:inline-flex;align-items:center;gap:var(--space-2);padding:var(--space-3) var(--space-6);background:#fff;color:var(--color-primary);border-radius:var(--radius-md);font-family:'Space Grotesk',sans-serif;font-size:var(--text-sm);font-weight:600;text-decoration:none">observatory@ramparts.gi</a>
    <p style="color:rgba(255,255,255,0.6);font-size:var(--text-xs);margin-top:var(--space-6)">Published weekly as part of the <a href="${ISSUE_URL}" style="color:rgba(255,255,255,0.8)">Ramparts AI Frontier Monitor</a></p>
  </div>
</section>`;

  return buildPage({
    title: 'Gibraltar AI Regulatory Observatory — Ramparts AI Frontier Monitor',
    description: 'The only dedicated tracker of AI governance developments in Gibraltar, the Crown Dependencies, and their relationship with UK and EU regulatory frameworks.',
    canonical: GIBRALTAR_URL,
    activePage: 'Gibraltar',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE 6: SEARCH (static-search.html)
// ══════════════════════════════════════════════════════════════════════════════
function generateSearch() {
  const SEARCH_DATA = [{"module": "The Signal", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "The strategic signal of the week is not any single model launch — it is the  simultaneous disintegration of frontier AI's regulatory vacuum on both sides of the Atlantic . On March 20, the White House released a National AI Legislative Framework explicitly preempting state laws and asserting federal supremacy over AI model development. On March 26, the EU Parliament voted 569–45 to advance the Digital Omnibus amendment to the AI Act, which delays high-risk enforcement to December 2027 while  expanding  the AI Office's supervisory power over GPAI models. The asymmetry is profound: the US is racing to remove sub-national friction from model development while the EU is centralising cross-border enforcement. Within 12 months, this creates a concrete regulatory arbitrage window — labs with EU-compliant GPAI codes of practice will face a simpler single regulator (the AI Office), while US-based labs operating in a preemption-first environment may face litigation from states whose laws were overridden. Legal counsel and compliance teams should begin mapping exposure now.", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-0"}, {"module": "Executive Insight", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Trump White House National AI Legislative Framework The White House published a comprehensive National AI Legislative Framework structured around six objectives including federal preemption of state AI laws, no new federal regulatory agency, and a proposed liability shield for AI developers against third-party misuse claims. The clause prohibiting state liability for downstream third-party misuse is the most legally consequential provision — if enacted, it retroactively shields frontier labs from tort claims. Plaintiff attorneys in Colorado, California, and New York are likely to mount constitutional challenges on Commerce Clause grounds. https://www.whitehouse.gov/articles/2026/03/president-donald-j-trump-unveils-national-ai-legislative-framework/ EU Parliament Votes 569–45 to Advance AI Act Digital Omnibus The Parliament adopted its mandate: high-risk Annex III obligations delayed to December 2, 2027; Annex I delayed to August 2, 2028; new nudifier ban added; watermarking deadline shortened to November 2026; AI Office jurisdiction over GPAI in VLOPs reinforced. Trilogue begins April 2026. The AI Office's new exclusive jurisdiction over GPAI models in VLOP deployments is a structural power shift buried in amendment text. It creates a single centralised EU supervisor for Google Gemini, Meta Llama, and OpenAI's EU deployments — categorically different from GDPR's decentralised structure. https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/artificial-intelligence-act-delayed-application-ban-on-nudifier-apps Super Micro Co-Founder Indicted for $2.5B Nvidia Chip Diversion to China Federal prosecutors indicted Yih-Shyan \"Wally\" Liaw (Super Micro co-founder/SVP) and associates for conspiring to divert $2.5B in Nvidia AI servers to China via Southeast Asian shell companies, falsified documentation, and \"dummy\" server replicas. $510M confirmed shipped. DOJ enforcement has moved to server-level supply chain circumvention. Any firm purchasing Nvidia-grade AI compute in APAC through third parties now carries acute legal exposure requiring supply chain audit triggers. https://apnews.com/article/artificial-intelligence-china-charges-e8f5135a71b8863c66b9c73d04cb0eb2 ARC Prize 2026 Launches ARC-AGI-3: AI Scores <1%, Humans 100% The ARC Prize Foundation released ARC-AGI-3 — an interactive, turn-based, agentic benchmark. Frontier AI scores: Gemini 3.1 Pro (0.37%), GPT-5.4 (0.26%), Claude Opus 4.6 (0.25%), Grok 4.20 (0.00%). Humans score 100%. $2M prize competition launched. Models that exceed human performance on ARC-AGI-2 (73–83%) cannot navigate a novel turn-based puzzle without instructions. Current large reasoning models may be at the ceiling of their architectural paradigm. Autonomous agent investment theses need recalibrating. ARC-AGI-3 Technical Report, March 24 https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf Cursor Composer 2 Revealed to Be Built on Chinese Kimi K2.5 Cursor (~$9B valuation) launched Composer 2 without disclosing i", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-1"}, {"module": "Model Frontier", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Dense transformer (undisclosed); 1M token context; native computer-use First model to exceed human average (~60%) Simultaneously superhuman on domain reasoning (ARC-AGI-2) and sub-toddler on adaptive exploration (ARC-AGI-3). Current frontier model regulatory definitions cannot capture this split capability profile. https://openai.com/index/introducing-gpt-5-4/ MoE: 128 experts / 4 active; 119B total / 6B active; 256k context; Apache 2.0 vs Qwen requiring 5.8K chars for comparable Apache 2.0 + extreme MoE sparsity undercuts proprietary API SaaS moat for enterprises with on-premises requirements. Deployable on 4× H100s with full weights portability. https://mistral.ai/news/mistral-small-4 Based on Ministral 3B; edge-device capable; 9 languages Real-time voice cloning at smartphone scale lands directly in EU Omnibus watermarking crosshairs — technically impossible to watermark by November 2026 deadline without hardware-level attestation that does not yet exist. ⚠️ Tier 3 — TechCrunch, March 26 https://techcrunch.com/2026/03/26/mistral-releases-a-new-open-source-model-for-speech-generation/ March 11 (production launch this week) Hybrid Mamba-Transformer-MoE + Latent MoE + Multi-Token Prediction + NVFP4; 120B total / 12B active; 1M context 12B active parameters = well below EU AI Act GPAI systemic risk threshold, yet represents frontier-class capability. Hybrid and sparse architectures create a definitional arbitrage gap in all current frontier model regulations. NVIDIA Developer Blog, March 11 https://developer.nvidia.com/blog/introducing-nemotron-3-super-an-open-hybrid-mamba-transformer-moe-for-agentic-reasoning/ Transformer (Kimi K2.5 base); ~25% Kimi compute, ~75% Cursor RL fine-tuning First confirmed Chinese open-source foundation in a major US commercial product without disclosure. FedRAMP/ITAR procurement policies for AI coding tools should now require base model provenance certification. https://cursor.com/blog/composer-2 Transformer-based; agentic workflow optimisation; ZClawBench open-sourced Zhipu's release of ZClawBench as an open dataset means a Chinese lab is now defining the global benchmark for agentic performance — the lab that defines the benchmark defines the optimisation target. https://docs.z.ai/guides/llm/glm-5-turbo gemini-3.1-flash-live-preview (Audio-to-Audio) Audio-to-audio (A2A) real-time streaming; distinct modality from TTS Two voice/audio frontier releases on a single calendar day (Voxtral + Gemini A2A) signals a convergence in real-time audio modality. Both challenge OpenAI's Realtime API. The report's 'no releases' designation for Google DeepMind was incorrect for March 26. https://ai.google.dev/gemini-api/docs/changelog Lyria 3 Pro (Music Generation — Developer API) March 25 (API/Vertex AI launch) Multimodal text+image→audio; SynthID watermarking integrated by default; 48kHz stereo; up to ~3 minutes EU AI Act watermarking-ready by design SynthID watermarking embedded by default makes Lyria 3 Pro natively compliant with", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-2"}, {"module": "Investment & M&A", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Legal AI operating system — autonomous agents for M&A, contract drafting, document review PROBABLE — $3B→$5B→$8B→$11B in 9 months; 100,000+ lawyers across 1,300 organisations McCann Fitzgerald going firmwide signals Harvey has replaced, not augmented, prior document review workflows. GIC as lead investor signals cross-border expansion strategy, not just capital. https://www.harvey.ai/blog/harvey-raises-at-dollar11-billion-valuation-to-scale-agents-across-law-firms-and-enterprises Precision health AI — clinical research data harmonisation, disease monitoring, NIH All of Us Research Program NO — 10-year-old Alphabet spinout; restructuring round UCHealth and CU Anschutz moving from customer to investor. Workbench powers NIH All of Us (21,500+ researchers). Verily is quietly becoming the data backbone of federally-funded US precision medicine. https://verily.com/perspectives/verily-secures-300-million-investment-to-advance-its-precision-health-ai-strategy UK sovereign AI infrastructure hyperscaler — 31,000 NVIDIA GPUs for Stargate UK WATCH — Europe's largest-ever venture round NVIDIA-backed European alternative to US hyperscalers, explicitly positioned for government and regulated-sector workloads with EU legal jurisdiction. https://www.nscale.com/press-releases/nscale-series-c Cathay Innovation, Bezos Expeditions, Greycroft World models via JEPA architecture — direct architectural challenge to transformer/LLM paradigm Long research horizon — not a Cursor Curve candidate Europe's largest-ever seed round, backed by NVIDIA, Samsung, Temasek, Bezos, Schmidt, and Mark Cuban. LeCun's JEPA architecture is a credible long-term alternative to scaling transformers. https://techcrunch.com/2026/03/09/yann-lecuns-ami-labs-raises-1-03-billion-to-build-world-models/ Accel, Benchmark, General Catalyst Legal AI displacing Microsoft Copilot across 50+ markets; White & Case, Cleary Gottlieb clients YES — $25M ARR (Dec 2023) → $330M+ ARR (Dec 2025); 40→400 employees in 12 months Primary European challenger to Harvey. GDPR-native architecture cited as procurement advantage in EU jurisdictions. Displacing Microsoft Copilot at enterprise law firms. https://legora.com/newsroom/legora-raises-550-million-series-d-to-fuel-us-growth Palantir Maven — Pentagon Program of Record Maven designated core US military AI system. Strike-proven against Iran. Army contract ceiling $10B. Anthropic designated supply-chain risk in same week. https://www.reuters.com/technology/pentagon-adopt-palantir-ai-as-core-us-military-system-memo-says-2026-03-20/ Anduril — $20B US Army Enterprise Contract Lattice platform becomes C2 backbone for counter-UAS across all US government agencies. 10-year enterprise vehicle. https://www.army.mil/article/291074/u_s_army_awards_enterprise_contract_for_it_commercial_solutions Nebius / Meta — $27B Infrastructure Deal Meta commits $12B+ to Dutch-listed Nebius for NVIDIA Vera Rubin capacity. NVIDIA takes $2B equity stake in Nebius. EU-registered entity hosts Meta's ", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-3"}, {"module": "Sector Penetration", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "75% of US health systems use AI; FDA has cleared zero generative AI devices AI diagnostic tools clinically validated at scale (77 hospitals, 21,603 stroke patients in BMJ RCT). Governance gap is regulatory, not technical. FDA TEMPO digital health pilot is the first mechanism to bridge the gap. Verily's Salesforce Agentforce Health integration embeds precision health AI agents directly into enterprise CRM platforms — a trojan horse for clinical AI adoption inside health systems that are not formally 'buying AI'. https://www.fiercehealthcare.com/ai-and-machine-learning/75-us-healthcare-systems-use-plan-use-ai-platform-2026 Harvey + Legora reach deployment inflection; firmwide rollouts displacing prior workflows 70% of legal professionals now use generative AI; only 56% of firms have formal governance policies. 'Firmwide' deployments (McCann Fitzgerald) signal workflow replacement, not augmentation. Anthropic's Claude legal plug-in is compressing the market for basic tasks while simultaneously accelerating enterprise demand for the agentic workflow layer (Harvey, Legora) that sits above the model. This dynamic is underreported. Draftwise / Legalweek 2026, March 20 https://www.draftwise.com/blog/contract-intelligence-and-4-other-terms-you-should-know-coming-out-of-legalweek-2026 Treasury FS-AI RMF now in implementation; agentic AI replacing manual KYC/onboarding 'Embedded' stage banks face 230 control objectives vs 21 for 'Initial' stage — structurally advantages large banks. $19.2B+ total bank AI budgets. No bank has yet reported measurable AI revenue. Nasdaq's tokenised securities order book requires AI for real-time settlement reconciliation — an invisible but structurally significant AI deployment not covered by mainstream financial press. https://www.fticonsulting.com/insights/articles/bankings-ai-rulebook-turning-treasury-framework-action Maven strike-proven; Pentagon building internal LLMs on classified data; Anthropic excluded Seven DoD 'Pace-Setting Projects' in active execution (Swarm Forge, Agent Network, Ender's Foundry, Open Arsenal, GenAI.mil). Pentagon plans to train commercial AI models on classified data within secure facilities. Anthropic's supply-chain risk designation permanently bifurcates the AI vendor landscape into defense-willing and defense-restricted categories. Any AI company with ethics restrictions on weapons applications will be excluded from the world's largest AI procurement market. https://www.reuters.com/technology/pentagon-adopt-palantir-ai-as-core-us-military-system-memo-says-2026-03-20/ Sora consolidated into ChatGPT; Adobe Firefly Custom Models in beta; governance 12–18 months behind OpenAI discontinued standalone Sora, consolidating video into ChatGPT super-app. Adobe Firefly Custom Models enables brand-trained AI image generators. Major media incumbents quietly licensing AI without announcements. The lack of any major public media AI deployment announcement this week is itself informative — major incumbents (D", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-4"}, {"module": "European & China Watch", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Europe's Infrastructure Moment vs. Regulatory Drift Europe's largest-ever venture round; NVIDIA-backed sovereign AI infrastructure Europe's largest-ever seed; Yann LeCun world models; JEPA architecture $5.55B valuation; displacing Microsoft Copilot in law firms across 50+ markets $27B Meta deal + $2B NVIDIA equity Most significant sovereign infrastructure signal of the week Berlin vector search; Bosch Ventures strategic signal of German industrial AI building own software stack Mistral AI confirmed working with 15+ governments on nationwide AI agreements with sovereign data centres in Paris (July 2026 opening) and Sweden. Nebius/Meta $27B deal proves the sovereign infrastructure model at commercial scale: EU-registered entity hosting Meta's frontier compute with EU legal jurisdiction. EURO-3C (€75M, EC-backed): 87-consortium federated Telco-Edge-Cloud infrastructure connecting national nodes. Parliament IMCO/LIBE voted 101–9–8 (March 18); plenary 569–45 (March 26). Trilogue targeting May 2026. Only 8 of 27 Member States have designated AI governance authorities — the week's most underreported structural risk. AI infrastructure for hyperscaler workloads Government and public administration AI Standards Vacuum — EU AI Act Harmonised Standards Gap Confirmed March 19–26 (multiple practitioner sources) Multiple practitioner publications during the reporting window explicitly documented the 'standards vacuum' condition created by the Digital Omnibus delay: high-risk AI legal obligations under the AI Act technically apply before CEN-CENELEC harmonised standards — the technical standards that enable compliance assessment — are available. Inside Privacy/Covington (March 20): 'likely before the necessary supporting standards and guidance are in place.' IAPP Global Summit (March 18): 'Some EU organizations are currently arguing they cannot effectively comply with the AI Act without the industry standards they were promised before implementation deadlines.' KLA Digital analysis: practitioners must rely on 'documented alternative measures, internal conformity logic, and evidence-heavy justification' absent harmonised standards. Under current (pre-Omnibus) AI Act: Annex III high-risk obligations apply August 2, 2026. CEN-CENELEC harmonised standards: not finalised (Code of Practice for AI-generated content not final until June 2026; high-risk system standards timeline unclear). Under proposed Omnibus (not yet law): Annex III delayed to December 2, 2027 — giving standards development until 2027. But Omnibus is not yet law. If trilogue fails before August 2, the original deadline applies without the standards being ready. The standards vacuum is a double-bind for deployers: (1) they cannot achieve 'presumption of conformity' (the safe harbour created by compliance with harmonised standards) because the standards don't exist yet; (2) they also cannot get regulatory clarity from national competent authorities (only 8 of 27 EU member states have designated them). T", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-5"}, {"module": "AI in Science", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "AI Scientist — Peer-Reviewed in Nature Machine learning / autonomous science methodology Completes full scientific discovery cycle autonomously: literature search → hypothesis generation → research design → code execution → results measurement → paper authorship. One AI-generated paper accepted at ICLR 2025 ML workshop. Results toned down from preprint. 'Not at same level as best human-produced papers.' Workshop context (not main conference). Turing test disclosed in advance to reviewers. Sakana AI, University of British Columbia, Nature Portfolio New category — first peer-reviewed autonomous AI paper authorship cycle This is the formal, published documentation of AI as autonomous research contributor — not merely assistant. The bar cleared is modest, but it has been cleared and published in Nature. This is the reference point from which future capability gains will be measured. https://www.nature.com/articles/d41586-026-00899-w ORI Protein Engineering — 100-Fold Enzyme Activity Gain ORI (Ontology Reinforcement Iteration) framework Closed-loop RLWF framework: 100-fold higher lysozyme activity; chitinase stable at 85°C; dual-function enzymes with both lysozyme and chitinase activities. All experimentally validated. Model weights public on Zenodo. Peer-reviewed, experimentally validated. Reproducibility: model weights publicly released. Limitation: demonstrated in specific enzyme classes only. Tencent AI4Science. Published Nature Communications (open access). Extends AlphaFold lineage — AlphaFold predicted structure; ORI optimises function. Together: complete structure-to-function AI pipeline. 100-fold enzyme activity gain is significantly beyond what directed evolution campaigns typically achieve. Dual-function enzyme design meets the threshold: AI output exceeded researchers' own prior capability. Nature Communications, March 19 https://www.nature.com/articles/s41467-026-69855-6 Genesis Mission — $293M DOE Funding Multi-domain (fusion, materials, earth science, biology, physics) Google DeepMind + Anthropic (core partner) across all 17 US National Laboratories $293M Request for Applications to expand AI access at National Labs. DeepMind AI co-scientist: synthesises vast information to generate novel hypotheses agentically. Anthropic confirmed as core partner via new Science Blog launch. https://www.energy.gov/articles/energy-department-announces-293-million-funding-support-genesis-mission-national-science Biology, physics, chemistry, life sciences New dedicated programme: AI for Science (API credits to researchers), Claude for Life Sciences, Genesis Mission core partnership. Accompanies Anthropic Economic Index 'Learning Curves' report (March 24). https://www.anthropic.com/research/introducing-anthropic-science GPT-5.4 Thinking — First General-Purpose Model at Cybersecurity HIGH Under OpenAI Preparedness Framework March 2026 (System Card published this week) AI safety / preparedness framework The GPT-5.4 Thinking System Card documents that this is", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-6"}, {"module": "Risk Indicators: 2028", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "EU standards vacuum confirmed to Dec 2027; US preemption framework eliminates state regulation EU Digital Omnibus creates confirmed standards vacuum until December 2027 for high-risk AI. White House framework blocks state AI regulation. US-China alignment dialogue signal (Hicks/Axios, March 25) — any bilateral deal could undermine multilateral frameworks. Compliance investment being deferred by incumbents; smaller entrants face earlier-applying GPAI obligations without the extended runway larger labs benefit from under the high-risk delay. https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/artificial-intelligence-act-delayed-application-ban-on-nudifier-apps Stryker wiper attack; CISA advisory; AI-assisted ICS reconnaissance documented as operational doctrine CISA advisory (March 19) following Stryker Corporation wiper attack by Handala (Iran-aligned). AI tools materially lowered barrier to ICS reconnaissance for 60+ Iranian-aligned cyber groups activated after Feb 28 US-Iran escalation. CISA released 5 ICS advisories March 19. AI-enabled wiper attacks targeting healthcare and critical manufacturing will scale. Admin access to enterprise MDM (Microsoft Intune) = ability to wipe 200,000 endpoints simultaneously. The 60-group activation pattern suggests this is now a doctrine, not an incident. CISA via Industrial Cyber, March 19 https://industrialcyber.co/cisa/cisa-flags-rising-threats-to-endpoint-management-systems-after-stryker-breach-urges-stronger-defense/ CVE-2026-33017 — Langflow Unauthenticated RCE: First CISA KEV for Pure AI Workflow Platform Critical (CVSS 9.3) unauthenticated RCE in Langflow — open-source visual AI workflow/RAG pipeline builder with 145,000+ GitHub stars. Vulnerability exploited within 20 hours of disclosure with no public PoC. Attackers harvested OpenAI, Anthropic, and AWS API keys from compromised instances. CISA added to KEV March 25 with April 8 FCEB remediation deadline. First CISA KEV for a pure AI workflow platform. Langflow is deployed by data science teams building AI agents and RAG pipelines — often outside standard security review cycles. The median org patch time is ~20 days; exploitation began within 20 hours. This gap will be exploited repeatedly as AI tooling proliferates. 'AI workloads are increasingly falling into threat actors' crosshairs as they offer high-value data, software supply chain access, and often lack robust security' (Sysdig). CISA KEV + Sysdig threat research, March 25 https://nvd.nist.gov/vuln/detail/CVE-2026-33017 CISA Institutional Degradation — 60% Workforce Furloughed, Forced Into 'Reactive Posture' DHS funding lapse has sidelined ~60% of CISA's workforce. Remaining personnel focused on mission-essential functions without pay. Capabilities suspended: proactive cybersecurity services, stakeholder engagement, binding operational directive issuance, private-sector coordination, cyber incident reporting rule development. Six members of a highly technical threat hunting/incid", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-7"}, {"module": "Law & Guidance", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Digital Omnibus — EU Parliament Plenary Vote European Parliament (plenary). Negotiating position — not yet binding law. General-purpose AI (GPAI) and high-risk AI — cross-sectoral Annex III high-risk → Dec 2, 2027; Annex I sectoral → Aug 2, 2028; watermarking → Nov 2, 2026; nudifier ban added; AI Office reinforced over GPAI in VLOPs; registration obligation reinstated; AI literacy obligation softened. Not yet law. Trilogue target May 2026. Penalties unchanged: up to €35M/7% turnover for prohibited AI. Research exemptions under Art. 2(6)/(8) unchanged. Legitimate interest expansion for personal data eases research training friction. Hollowing-out signal. Compliance timelines extended, literacy obligations weakened, SME support expanded — all reducing effective regulatory burden. Human rights bodies warn process bypassed impact assessment. https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/artificial-intelligence-act-delayed-application-ban-on-nudifier-apps DSA Non-Compliance Proceedings — X / Grok Active (proceedings opened January 26, confirmed March 17–19) European Commission — binding enforcement under DSA Platform AI / generative AI embedded in VLOP Articles 34/35 DSA: systemic risk assessment required before deploying materially risk-altering AI features. Also: ad repository transparency, identity verification failures. Fines up to 6% of global annual turnover. X contesting prior €120M DSA fine via three CJEU cases. DSA systemic risk assessment requirement, being tested here for the first time, will create a new de facto standard for any research or commercial AI tool embedded in a VLOP. https://insights.policy-insider.ai/22-03-2026-dsa-enforcement-ai-act-safety-dma-compliance/ White House National AI Legislative Framework White House — legislative recommendations (non-binding). Signals Administration priorities for Congress. General-purpose AI — cross-sectoral Federal preemption of state AI model regulation; no developer liability for third-party misuse; no new federal AI agency; AI training on copyrighted material does not violate copyright (Administration view); collective licensing with antitrust exemption proposed. Consultative only. No bill introduced. DOJ AI Litigation Task Force operative under One Rule EO. Copyright position directly enables frontier model training at scale — collides with EU, UK, and Brazilian frameworks. Developer liability shield for AI labs being embedded in federal law. Eliminates primary legal theory in billion-dollar AI copyright/harm litigation. https://www.whitehouse.gov/wp-content/uploads/2026/03/03.20.26-National-Policy-Framework-for-Artificial-Intelligence-Legislative-Recommendations.pdf DSIT/IPO/DCMS — statutory report under Data (Use and Access) Act 2025. Non-binding. AI development / training data / copyright Wide TDM opt-out abandoned as preferred approach. Licensing market to be monitored. All four policy options remain open. Summer 2026 consultation on digital replicas planned. No ne", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-8"}, {"module": "AI Governance", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Soft Law · Corporate Commitments · Accountability · Governance Gaps The governance layer that sits above internal compliance and below binding law. Covers international soft law, corporate governance signals, product liability developments, algorithmic accountability enforcement, and governance gaps being actively exploited. Voluntary commitments today are leading indicators of mandatory obligations in 12–24 months. No new OECD AI Principles output this week. Standing reference: OECD AI Principles (2019, updated 2024) — adopted by 46+ countries. OECD AI Policy Observatory tracks national implementation at oecd.ai/en/dashboards. No material developments this week Paris AI Action Summit — Follow-Up The Paris AI Action Summit (February 10–11, 2026) produced the 'Statement on Inclusive and Sustainable AI' — signed by 60+ countries including the US and UK. Key commitments: open-source AI governance frameworks; AI for public services; compute access for the Global South. Implementation tracking began in March 2026. No binding follow-up mechanism exists; commitments are voluntary. The Paris Statement's voluntary commitment to 'inclusive AI governance' creates a soft-law template that civil society will invoke in litigation against deployers who publicly signed but failed to implement. The absence of a binding mechanism is an asymmetric governance gap — signatories assume reputational benefit without legal obligation, but courts may hold them to their own stated standards. Elysée Palace — Paris AI Action Summit Statement https://www.elysee.fr/en/emmanuel-macron/2026/02/11/paris-ai-action-summit-statement-on-inclusive-and-sustainable-ai UN AI Resolution — Implementation UN General Assembly Resolution 78/311 ('Seizing the Opportunities of Safe, Secure and Trustworthy AI Systems for Sustainable Development', March 2024) — implementation monitoring ongoing. The UN Secretary-General's High-Level Advisory Body on AI published its final report in September 2024 recommending an International AI Safety Institute Network and a Global AI Fund. No binding implementation this week. No material developments this week https://www.un.org/sites/un2.un.org/files/governing_ai_for_humanity_final_report_en.pdf G7 Hiroshima AI Process (2023) established the International Guiding Principles for AI and the Code of Conduct for AI Developers — voluntary. The 2026 G7 cycle (Canada presidency) has not yet produced AI-specific output this week. https://www.meti.go.jp/press/2023/10/20231030002/20231030002-1.pdf Anthropic's Responsible Scaling Policy (RSP) v3.0 published February 24, 2026 — current operative version. RSP March 24 update (this week): procedural only — noncompliance reporting channels expanded. No ASL reclassification or capability threshold crossing. The RSP is the most sophisticated voluntary safety governance framework in the frontier AI sector. Anthropic's Science Blog launch (March 18) included commitment to Genesis Mission (DOE, $293M) — a government-partnered AI-", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-9"}, {"module": "Technical Standards", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "ISO / NIST / IEEE / CEN-CENELEC / ETSI / OECD ISO/IEC 42001:2023 — AI Management System Certifiable AI management system standard. Equivalent to ISO 27001 but for AI governance. Adopted by EU AI Act as a conformity route for GPAI providers. https://www.iso.org/standard/81230.html ISO/IEC 23894 — AI Risk Management Guidance Provides guidance on how organisations can manage risk specific to AI. Complements 42001. https://www.iso.org/standard/77304.html ISO/IEC 5338 — AI Lifecycle Processes AI system lifecycle processes — development, deployment, operation, maintenance, decommission. https://www.iso.org/standard/81118.html USA / De facto global reference NIST AI RMF 1.0 + Generative AI Profile (NIST AI 600-1) Primary US voluntary AI risk management framework. Generative AI Profile (600-1) extends RMF to foundation models. Adopted as the compliance reference for US federal agency AI procurement. NIST AI 800-4 (Post-Deployment AI Monitoring Framework) updated March 18 — provides federal agencies with guidance on monitoring deployed AI systems for performance degradation, bias drift, and security vulnerabilities. First update to the post-deployment monitoring framework since initial publication. → see also Module 7 (Cyber Escalation — Langflow KEV demonstrates need for AI deployment monitoring). NIST AI 800-4 + CAISI MOU, March 18 https://www.nist.gov/artificial-intelligence NIST AI 100-1 — Trustworthy and Responsible AI Foundational conceptual framework for AI trustworthiness properties (valid, reliable, safe, secure, explainable, privacy-enhanced, fair, accountable, transparent). Harmonised Standards under EU AI Act — in development CEN-CENELEC JTC21 is developing harmonised standards that will provide presumption of conformity under the EU AI Act. Critical for high-risk AI system compliance. Standards not yet published. ⚠️ Digital Omnibus vote (March 26) delays high-risk AI obligations to December 2027 — directly extending the window for harmonised standards development. Reduces urgency pressure on CEN-CENELEC JTC21 but raises questions about whether standards will be published before the new compliance deadlines. → see also Module 8 (EU). https://www.cencenelec.eu/areas-of-work/cenelec-sectors/digital-society-cenelec/artificial-intelligence/ IEEE 7000-Series — Ethics in AI Design Active (multiple standards at various stages) Suite of standards addressing ethical considerations in AI and autonomous system design. Covers transparency (7001), data privacy (7002), algorithmic bias (7003), child/student data governance (7004), employer data governance (7005), and more. https://standards.ieee.org/initiatives/artificial-intelligence-systems/ ETSI ISG SAI — Securing AI Standards Industry Specification Group on Securing Artificial Intelligence. Focuses on AI system security, adversarial ML, and securing AI against threats. Feeds into EU AI Act cybersecurity requirements for high-risk systems. https://www.etsi.org/technologies/artificial-intelligence OECD AI", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-10"}, {"module": "Litigation Tracker", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Live AI Court Cases by Jurisdiction Running table of active AI litigation that matters to legal professionals, compliance teams, and investors. Covers copyright, liability, data protection, competition, and constitutional challenges. Updated weekly with status changes, rulings, and filings. Getty alleges Stability AI trained on 12M+ copyrighted images without licence. UK appeal ongoing (Getty v. Stability AI EWHC). US case in discovery. Landmark test of whether AI training on copyrighted material constitutes infringement. UK Government Copyright & AI Report (~March 18) abandoned the wide TDM opt-out approach — directly affects the legal landscape for this case. → see also Module 8 (UK). A US ruling that AI training constitutes fair use would directly contradict the UK's emerging licensing-first framework, creating a transatlantic copyright arbitrage. Labs with UK operations are watching both jurisdictions simultaneously. https://www.courtlistener.com/docket/66732129/getty-images-us-inc-v-stability-ai-inc/ X Corp v. European Commission (DSA / Grok) Platform Regulation / Generative AI Deployment X is contesting the €120M DSA fine (December 2025) via three CJEU cases. EU Commission simultaneously opened new DSA proceedings against X for Grok's deployment without prior systemic risk assessment. First major test of DSA governance over embedded generative AI in a VLOP. EU Commission confirmed active proceedings in Parliamentary responses (March 17–19). Commission position: embedding GenAI in a VLOP without prior Article 34/35 risk assessment is automatically non-compliant. → see also Module 7 (Platform Power), Module 8 (EU). If the Commission's legal theory is upheld by CJEU, retroactive liability exposure for every VLOP that embedded generative AI without a prior systemic risk assessment — including Meta AI in Facebook/Instagram, Google Gemini in Search, and Microsoft Copilot in Bing. EU Commission Parliamentary responses, March 19 https://insights.policy-insider.ai/22-03-2026-dsa-enforcement-ai-act-safety-dma-compliance/ In re: Super Micro / Nvidia Chip Export (DOJ) Federal indictment of Super Micro co-founder Yih-Shyan Liaw and associates for conspiring to divert $2.5B in Nvidia AI servers to China via Southeast Asian shell companies and falsified compliance documentation. $510M confirmed shipped. Super Micro cooperating; one defendant at large. Indictment filed March 19–20, 2026. This is the first criminal case targeting server-level AI supply chain circumvention (not chip-level smuggling). → see also Module 1 (Item 3), Module 7 (Export Controls). The DOJ indictment theory — that falsified end-user certificates and dummy server replicas constitute export control fraud — establishes criminal liability exposure for any data centre operator or component distributor using opaque APAC logistics chains for Nvidia-grade compute. https://apnews.com/article/artificial-intelligence-china-charges-e8f5135a71b8863c66b9c73d04cb0eb2 Authors Guild et al. v. OpenAI", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-11"}, {"module": "Personnel & Org Watch", "week": "19–26 March 2026", "issue": "Vol. 1 · Issue 1", "text": "Leadership Movements · Government Appointments · Revolving Door Tracks leadership changes at AI labs, government AI bodies, and regulatory agencies — and the revolving door between industry, government, and academia. The people who set AI policy and capability direction often signal institutional priorities before any public announcement. Updated weekly. Anthropic's public refusal of Pentagon weapons-targeting contracts and consequent supply-chain risk designation (reported March 6) represents a structural strategic decision made at CEO level. Amodei's position on autonomous weapons is now a permanent fixture of Anthropic's market positioning — and its exclusion from the world's largest AI procurement market. https://www.reuters.com/technology/pentagon-adopt-palantir-ai-as-core-us-military-system-memo-says-2026-03-20/ Head of Qwen Model Division, Alibaba Departure of Alibaba's Qwen division head — reported by Reuters March 18 — coincides with a 67% quarterly profit drop and CEO Eddie Wu taking direct control of the new AI-focused business group. Raises investor questions about strategic coherence of China's second-largest AI model programme. No new Qwen release followed in the monitoring window. https://www.reuters.com/world/china/alibabas-ai-strategy-shift-comes-into-focus-with-big-bets-on-agents-2026-03-18/ DOGE (White House efficiency office) Pentagon CDO (Chief Digital Officer appointee, under Dep. Sec. Feinberg) Kliger's appointment as Pentagon CDO — bringing Silicon Valley execution speed to military AI procurement — is the organisational mechanism behind Maven's rapid program-of-record designation. The DOGE-to-DoD pipeline represents a structural shift in how the Pentagon acquires AI: faster, more concentrated, less subject to traditional acquisition oversight. https://www.reuters.com/technology/pentagon-adopt-palantir-ai-as-core-us-military-system-memo-says-2026-03-20/ Feinberg's March 9 memo designating Palantir Maven as a Program of Record is the single most consequential AI procurement decision in the monitoring window. His private equity background and DOGE alignment signals that the Pentagon's AI acquisition model is shifting from risk-averse bureaucratic procurement toward outcome-first deployment at speed. https://www.reuters.com/technology/pentagon-adopt-palantir-ai-as-core-us-military-system-memo-says-2026-03-20/ Canada's first Minister of Artificial Intelligence and Digital Innovation Appointed April 2025 (active in monitoring window) Canada's decision to create a dedicated AI Minister — and appoint a journalist and broadcaster rather than a technologist or lawyer — signals a communications-first, public-trust-building approach to AI governance. Solomon's national AI Strategy (based on February 2026 sprint consultation) is expected in H1 2026 and will determine whether AIDA's successor is risk-based, sector-specific, or principles-only. PM Carney announcement, March 5 https://www.pm.gc.ca/en/news/news-releases/2026/03/05/prime-m", "url": "https://ramparts.gi/ai-frontier-monitor-issue/#module-12"}];

  const css = `
.search-header { background: var(--color-surface); border-bottom: 1px solid var(--color-border); padding-block: var(--space-12); }
.search-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-primary); margin-bottom: var(--space-3); display: block; }
.search-title { font-size: var(--text-xl); font-weight: 700; margin-bottom: var(--space-3); }
.search-desc { font-size: var(--text-base); color: var(--color-text-muted); max-width: 65ch; margin-bottom: var(--space-8); }
.search-input-wrapper { position: relative; max-width: 640px; }
.search-input { width: 100%; padding: var(--space-4) var(--space-5); padding-left: var(--space-10); font-size: var(--text-base); font-family: Inter,-apple-system,sans-serif; border: 2px solid var(--color-border); border-radius: var(--radius-lg); background: var(--color-bg); color: var(--color-text); transition: border-color var(--transition); outline: none; }
.search-input:focus { border-color: var(--color-primary); }
.search-input::placeholder { color: var(--color-text-faint); }
.search-icon { position: absolute; left: var(--space-4); top: 50%; transform: translateY(-50%); color: var(--color-text-faint); pointer-events: none; }
.search-status { margin-top: var(--space-4); font-size: var(--text-sm); color: var(--color-text-muted); }
.search-results { padding-block: var(--space-8); }
.result-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-6); margin-bottom: var(--space-4); }
.result-card:hover { border-color: var(--color-primary-medium); }
.result-meta { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-2); flex-wrap: wrap; }
.result-module { font-family: 'Space Grotesk', sans-serif; font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--color-primary); background: var(--color-primary-light); padding: 0.15em 0.6em; border-radius: 9999px; }
.result-issue { font-size: var(--text-xs); color: var(--color-text-muted); font-weight: 600; }
.result-snippet { font-size: var(--text-sm); color: var(--color-text-muted); line-height: 1.7; max-width: none; }
.result-snippet mark { background: var(--color-primary-light); color: var(--color-text); padding: 0.05em 0.2em; border-radius: 2px; }
.no-results { text-align: center; padding: var(--space-16) 0; color: var(--color-text-muted); }
`;

  const body = `
<div class="search-header">
  <div class="container">
    <span class="search-eyebrow">Full-Text Search</span>
    <h1 class="search-title">Search all issues</h1>
    <p class="search-desc">Every primary source, every asymmetric signal, every law — searchable across all editions.</p>
    <div class="search-input-wrapper">
      <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      <input type="text" class="search-input" id="search-input" placeholder="Search modules, cases, jurisdictions, signals…" autocomplete="off">
    </div>
    <div class="search-status" id="search-status"></div>
  </div>
</div>

<div class="container">
  <div class="search-results" id="search-results"></div>
</div>

<script>
(function(){
  var DATA = ${JSON.stringify(SEARCH_DATA)};
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  var status = document.getElementById('search-status');

  function highlight(text, q) {
    var esc = q.replace(/[.*+?^$\x7b\x7d()|[\\\\]\\\\]/g, '\\\\$&');
    return text.replace(new RegExp('(' + esc + ')', 'gi'), '<mark>$1</mark>');
  }

  function doSearch(q) {
    q = (q || '').trim();
    results.innerHTML = '';
    if (q.length < 2) { status.textContent = DATA.length + ' modules indexed. Type to search.'; return; }
    var hits = DATA.filter(function(d) { return d.text.toLowerCase().indexOf(q.toLowerCase()) > -1 || d.module.toLowerCase().indexOf(q.toLowerCase()) > -1; });
    status.textContent = hits.length + ' result' + (hits.length !== 1 ? 's' : '') + ' for \u201c' + q + '\u201d';
    if (!hits.length) { results.innerHTML = '<div class="no-results"><h3>No results found</h3><p>Try different keywords.</p></div>'; return; }
    results.innerHTML = hits.slice(0,100).map(function(h) {
      var idx = h.text.toLowerCase().indexOf(q.toLowerCase());
      var snip = h.text.substring(Math.max(0,idx-80), idx+220).trim();
      return '<div class="result-card">' +
        '<div class="result-meta"><span class="result-module">' + h.module + '</span>' +
        '<span class="result-issue">' + h.issue + ' · ' + h.week + '</span></div>' +
        '<div class="result-snippet">' + highlight('…' + snip + '…', q) + '</div>' +
        '<a href="' + h.url + '" style="font-size:13px;color:#006b6f;text-decoration:none;font-weight:600;display:inline-block;margin-top:8px">View in report →</a>' +
        '</div>';
    }).join('');
  }

  var timer;
  input.addEventListener('input', function() { clearTimeout(timer); timer = setTimeout(function(){ doSearch(input.value); }, 180); });
  status.textContent = DATA.length + ' modules indexed across 1 issue(s). Type to search.';
})();
</script>`;

  return buildPage({
    title: 'Search — Ramparts AI Frontier Monitor',
    description: 'Search across all editions of the Ramparts AI Frontier Monitor.',
    canonical: SEARCH_URL,
    activePage: 'Search',
    extraCSS: css,
    body,
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN: Generate all files
// ══════════════════════════════════════════════════════════════════════════════
function writeFile(filename, content) {
  const filePath = path.join(DATA_DIR, filename);
  fs.writeFileSync(filePath, content, 'utf8');
  const sizeKB = (Buffer.byteLength(content, 'utf8') / 1024).toFixed(1);
  console.log(`  ✓ ${filename.padEnd(28)} ${sizeKB} KB`);
  return { filename, sizeKB, path: filePath };
}

function main() {
  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('  Ramparts AI Frontier Monitor — Static Site Generator');
  console.log(`  Date: ${DATE_ARG}  →  Output: ${DATA_DIR}`);
  console.log('═══════════════════════════════════════════════════════════\n');

  const results = [];

  try {
    console.log('Generating pages…\n');
    results.push(writeFile('static-index.html',     generateIndex()));
    results.push(writeFile('static-about.html',     generateAbout()));
    results.push(writeFile('static-archive.html',   generateArchive()));
    results.push(writeFile('static-digest.html',    generateDigest()));
    results.push(writeFile('static-gibraltar.html', generateGibraltar()));
    results.push(writeFile('static-search.html',    generateSearch()));

    const totalKB = results.reduce((sum, r) => sum + parseFloat(r.sizeKB), 0).toFixed(1);
    console.log(`\n  Total: ${results.length} files · ${totalKB} KB\n`);
    console.log('  All files written to:', DATA_DIR);
    console.log('═══════════════════════════════════════════════════════════\n');
  } catch (err) {
    console.error('\n✗ Error generating site:', err.message);
    console.error(err.stack);
    process.exit(1);
  }
}

main();

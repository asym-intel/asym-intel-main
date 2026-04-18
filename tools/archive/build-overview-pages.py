#!/usr/bin/env python3
"""Generate rich Overview pages for all 7 monitors.

Uses the existing base.css design system + new overview-specific classes.
Pulls live data from report-latest.json where available.
"""
import json
import os
import html as html_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(BASE, "static", "monitors")

# ── Monitor data ──────────────────────────────────────────────────────
MONITORS = {
    "democratic-integrity": {
        "abbr": "WDM",
        "name": "World Democracy Monitor",
        "mission": "The World Democracy Monitor tracks structural erosion of democratic institutions — electoral integrity, judicial independence, civil society space, press freedom, and legislative process.",
        "why_now_title": "Democratic resilience under compound pressure",
        "why_now_body": "WDM is built to detect when democratic institutions lose their capacity to self-correct — long before a collapse becomes headline news. It tracks the structural health of democracy, not individual political events.",
        "cadence": "Weekly",
        "output": "Signals",
        "edge": "Structural",
        "chips": ["Weekly · risk watch", "Primary-source linked", "Structural decay tracking"],
        "tracks": [
            {"title": "Electoral integrity", "desc": "Integrity of elections, voter suppression, institutional manipulation, and electoral calendar risk."},
            {"title": "Judicial independence", "desc": "Court packing, constitutional erosion, rule-of-law regression, and prosecutorial independence."},
            {"title": "Civil society & press", "desc": "NGO restrictions, press freedom indices, journalist safety, and media capture patterns."},
            {"title": "State capture", "desc": "Institutional hollowing, patronage networks, legislative bypass, and mimicry chain dynamics."},
        ],
        "how_dashboard": "Start here for the lead signal, global health snapshot, and heatmap of democratic stress this week.",
        "how_latest": "Read the current weekly report for detailed country-level democratic health assessments and integrity flags.",
        "how_lk": "Use this for persistent structural context — ongoing erosion patterns and historical trend data.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh democratic stress indicators before elevation.",
        "why_different": "WDM distinguishes transient episodes from persistent structural conditions. It focuses on institutional health, not policy preferences — a strong economy can mask democratic decay.",
        "why_different_points": [
            "Tracks erosion across five structural dimensions, not headline events.",
            "Heatmap tiers measure institutional health over time, not single incidents.",
            "Mimicry chain methodology detects democratic backsliding that imitates democratic process.",
        ],
        "cross_monitors": [
            {"monitor": "FCW", "desc": "FIMI operations targeting electoral integrity and democratic discourse."},
            {"monitor": "ESA", "desc": "EU democratic conditionality and member-state governance stress."},
            {"monitor": "SCEM", "desc": "Conflict-driven governance collapse and democratic transitions under pressure."},
        ],
        "publish": "Mondays at 06:00 UTC",
    },
    "macro-monitor": {
        "abbr": "GMM",
        "name": "Global Macro Monitor",
        "mission": "The Global Macro Monitor tracks systemic financial stress, macro-economic risk transmission, and structural vulnerabilities across sovereign, corporate, and market domains.",
        "why_now_title": "Macro stress regimes no longer mean-revert on schedule",
        "why_now_body": "GMM maps how financial shocks propagate through interconnected systems — from tariff escalation through commodity markets to sovereign debt dynamics — treating macro-financial risk as strategic intelligence, not market commentary.",
        "cadence": "Weekly",
        "output": "Indicators",
        "edge": "Transmission",
        "chips": ["Weekly · macro signal", "25+ indicators scored", "Public signals only"],
        "tracks": [
            {"title": "Stress regime", "desc": "System-wide stress level computed from 25+ indicators across six domains, with cascade protocol triggers."},
            {"title": "Sovereign & debt", "desc": "Government bond dynamics, fiscal sustainability, reserve adequacy, and sovereign risk transmission."},
            {"title": "Central bank policy", "desc": "Rate decisions, liquidity operations, emergency facilities, and central bank communication shifts."},
            {"title": "Trade & tariffs", "desc": "Tariff escalation tracking, trade flow disruption, supply chain stress, and retaliatory dynamics."},
        ],
        "how_dashboard": "Start here for the stress regime score, top-moving indicators, and key judgments this week.",
        "how_latest": "Read the current report for the full executive briefing, indicator domain scores, and tail risk assessment.",
        "how_lk": "Use this for persistent context — structural macro risk pipelines, debt dynamics history, and indicator baselines.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh macro developments before they enter the scored framework.",
        "why_different": "GMM uses only publicly available sources and applies a structured scoring methodology — it does not offer investment advice or predict markets.",
        "why_different_points": [
            "Structured indicator framework with transparent scoring, not narrative forecasting.",
            "Cascade Protocol triggers when multiple stress domains activate simultaneously.",
            "Blind spot rules flag when important signals fall outside the indicator framework.",
        ],
        "cross_monitors": [
            {"monitor": "ERM", "desc": "Insurance stress, food prices, and climate-related supply shocks entering macro channels."},
            {"monitor": "SCEM", "desc": "Conflict-driven commodity disruption and sanctions cascades."},
            {"monitor": "ESA", "desc": "EU fiscal capacity and defence spending impacts on sovereign debt dynamics."},
        ],
        "publish": "Tuesdays at 08:00 UTC",
    },
    "european-strategic-autonomy": {
        "abbr": "ESA",
        "name": "European Strategic Autonomy Monitor",
        "mission": "The European Strategic Autonomy Monitor tracks EU defence investment, hybrid threats, institutional developments, and member state alignment across the dimensions of European strategic independence.",
        "why_now_title": "Europe's autonomy gap is being tested in real time",
        "why_now_body": "ESA tracks the structural contest across energy, defence, technology, finance, critical materials, and institutional dimensions — measuring how far Europe is from genuine strategic independence on each axis.",
        "cadence": "Weekly",
        "output": "Signals",
        "edge": "Lagrange Point",
        "chips": ["Weekly · strategic watch", "Primary-source linked", "Autonomy dimension tracking"],
        "tracks": [
            {"title": "EU Defence", "desc": "NATO burden-sharing, European defence industrial output, SAFE programme disbursements, and US-equipment dependency."},
            {"title": "Hybrid threats", "desc": "FIMI operations, critical infrastructure attacks, election interference, and state capture in EU member states."},
            {"title": "Institutional developments", "desc": "EU-level policy, regulatory shifts, integration steps, and institutional posture changes."},
            {"title": "Strategic autonomy contest", "desc": "Energy, defence, technology, finance, critical materials measured against the Lagrange Point framework."},
        ],
        "how_dashboard": "Start here for the lead signal, defence developments, and hybrid threat overview this week.",
        "how_latest": "Read the current report for the full ESA weekly analysis with member state tracker and cross-monitor flags.",
        "how_lk": "Use this for persistent context — Lagrange Point framework data and structural autonomy metrics over time.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh strategic autonomy indicators before weekly elevation.",
        "why_different": "ESA measures strategic autonomy as a multi-dimensional structural condition, not a political preference.",
        "why_different_points": [
            "Lagrange Point framework maps dependency-to-independence distance across six axes.",
            "Combines defence, hybrid, and institutional analysis in a single integrated monitor.",
            "Member state tracker reveals alignment divergence beneath EU-level consensus.",
        ],
        "cross_monitors": [
            {"monitor": "WDM", "desc": "Democratic governance stress in EU member states affecting institutional cohesion."},
            {"monitor": "FCW", "desc": "FIMI operations targeting EU political discourse and defence consensus."},
            {"monitor": "SCEM", "desc": "Conflict escalation driving European defence urgency and spending decisions."},
        ],
        "publish": "Wednesdays at 19:00 UTC",
    },
    "fimi-cognitive-warfare": {
        "abbr": "FCW",
        "name": "FIMI & Cognitive Warfare Monitor",
        "mission": "The FIMI & Cognitive Warfare Monitor tracks foreign information manipulation, cognitive warfare operations, attribution complexity, and platform responses across all state and near-state actors.",
        "why_now_title": "Information operations now move faster than institutional response",
        "why_now_body": "FCW is built to map how state-backed information campaigns are designed, deployed, and attributed — treating cognitive warfare as a first-order security threat, not a communications problem.",
        "cadence": "Weekly",
        "output": "Campaigns",
        "edge": "Attribution",
        "chips": ["Weekly · threat watch", "Attribution tracked", "Multi-actor scope"],
        "tracks": [
            {"title": "Active campaigns", "desc": "Ongoing FIMI operations with tracked actors, targets, platforms, and assessed objectives."},
            {"title": "Actor tracking", "desc": "State and near-state actor profiles, capability assessment, and operational pattern changes."},
            {"title": "Platform responses", "desc": "Tech platform enforcement actions, takedowns, policy changes, and detection capability shifts."},
            {"title": "Attribution complexity", "desc": "Multi-factor attribution scoring, impersonation chains, and structurally invisible operations."},
        ],
        "how_dashboard": "Start here for the lead signal, active campaign summary, and attribution status this week.",
        "how_latest": "Read the current report for the full campaign analysis, actor tracker, and cognitive warfare assessment.",
        "how_lk": "Use this for persistent context — long-running campaigns, actor profiles, and structural attribution patterns.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh FIMI indicators and campaign movement before elevation.",
        "why_different": "FCW applies a structured attribution framework that distinguishes confirmed from assessed operations, and tracks the structurally invisible.",
        "why_different_points": [
            "Multi-factor attribution scoring rather than binary confirmed/denied classification.",
            "Tracks operations below institutional detection thresholds (MF4 category).",
            "All state and near-state actors in scope — not limited to Russia and China.",
        ],
        "cross_monitors": [
            {"monitor": "WDM", "desc": "FIMI campaigns targeting democratic processes and electoral integrity."},
            {"monitor": "ESA", "desc": "Information operations directed at EU defence consensus and strategic autonomy discourse."},
            {"monitor": "SCEM", "desc": "Cognitive warfare as a conflict-zone capability and escalation tool."},
        ],
        "publish": "Thursdays at 09:00 UTC",
    },
    "ai-governance": {
        "abbr": "AGM",
        "name": "Artificial Intelligence Monitor",
        "mission": "The Artificial Intelligence Monitor tracks frontier model releases, regulatory movements, military AI applications, and the global governance competition across sixteen thematic modules.",
        "why_now_title": "AI governance is forming faster than the systems it governs",
        "why_now_body": "AGM maps the full strategic surface of AI development — from frontier model capabilities and investment flows to regulatory frameworks, military applications, and societal effects — treating AI governance as a first-order geopolitical question.",
        "cadence": "Weekly",
        "output": "Modules",
        "edge": "Breadth",
        "chips": ["Weekly · governance watch", "16 modules scored", "Regulatory + capability tracking"],
        "tracks": [
            {"title": "Frontier models", "desc": "Capability releases, benchmark results, safety evaluations, and competitive dynamics among leading labs."},
            {"title": "Regulatory landscape", "desc": "AI Act implementation, US executive orders, international frameworks, and regulatory competition."},
            {"title": "Military & security AI", "desc": "Autonomous weapons, intelligence applications, defence procurement, and dual-use technology governance."},
            {"title": "Governance competition", "desc": "US-China-EU positioning, standards bodies, international agreements, and governance gap analysis."},
        ],
        "how_dashboard": "Start here for the lead signal, top modules, and this week's governance developments at a glance.",
        "how_latest": "Read the current report for all 16 module assessments and cross-cutting governance analysis.",
        "how_lk": "Use this for persistent context — regulatory timelines, model release histories, and structural governance trends.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh AI developments before they enter the module framework.",
        "why_different": "AGM covers the full strategic surface of AI governance — not just regulation, not just capabilities, but the interaction between them.",
        "why_different_points": [
            "16 modules covering regulation, capability, military, economic, and societal dimensions.",
            "Treats AI governance as geopolitical competition, not just technology policy.",
            "Tracks structural gaps between capability development and governance response.",
        ],
        "cross_monitors": [
            {"monitor": "FCW", "desc": "AI-generated content in FIMI operations and deepfake campaign attribution."},
            {"monitor": "ESA", "desc": "EU AI Act implementation and European technology sovereignty."},
            {"monitor": "GMM", "desc": "AI investment flows and their macro-financial implications."},
        ],
        "publish": "Fridays at 09:00 UTC",
    },
    "environmental-risks": {
        "abbr": "ERM",
        "name": "Environmental Risks Monitor",
        "mission": "The Environmental Risks Monitor tracks climate-security pressure, resource stress, extreme events, and environmental statecraft as strategic risk.",
        "why_now_title": "Environmental disruption becomes strategic long before it is treated that way politically",
        "why_now_body": "ERM identifies how ecological shocks translate into geopolitical and systemic consequences through food, water, migration, infrastructure, conflict, and state capacity.",
        "cadence": "Weekly",
        "output": "Signals",
        "edge": "Transmission",
        "chips": ["Weekly · risk watch", "Primary-source linked", "Stress + transmission tracking"],
        "tracks": [
            {"title": "Risk regions", "desc": "States and regions under active environmental or climate-security stress."},
            {"title": "Stress categories", "desc": "Climate security, resource conflict, environmental statecraft, and multilateral governance signals."},
            {"title": "Extreme events", "desc": "Weather and ecological shocks with assessed strategic or political implications."},
            {"title": "Tipping & resilience", "desc": "Threshold systems, infrastructure strain, governance capacity, and long-duration risk accumulation."},
        ],
        "how_dashboard": "Start here for the lead signal, current regional stress picture, and top developments this issue.",
        "how_latest": "Read the current full report for the week's environmental-risk narrative, evidence, and implications.",
        "how_lk": "Use this for persistent risk regions, tipping systems, and cumulative structural context.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh hazard and event movement before elevation.",
        "why_different": "ERM shows how environmental pressure moves through political, economic, and security systems rather than staying inside a policy silo.",
        "why_different_points": [
            "Treats transmission into conflict, governance, food, and infrastructure as central.",
            "Chronic stress and acute events are analysed together but not conflated.",
            "Structural risk remains visible even when no single event dominates the week.",
        ],
        "cross_monitors": [
            {"monitor": "SCEM", "desc": "Resource stress and displacement intensifying fragile theatres."},
            {"monitor": "GMM", "desc": "Insurance stress, food prices, and supply shocks translating into macro consequences."},
            {"monitor": "WDM", "desc": "Environmental shocks amplifying governance stress and legitimacy challenges."},
        ],
        "publish": "Saturdays at 05:00 UTC",
    },
    "conflict-escalation": {
        "abbr": "SCEM",
        "name": "Strategic Conflict & Escalation Monitor",
        "mission": "The Strategic Conflict & Escalation Monitor tracks 8–12 active armed conflicts, assessing escalation paths, friction indicators, spillover risk, and strategic consequences.",
        "why_now_title": "Conflict escalation paths are multiplying faster than containment responses",
        "why_now_body": "SCEM maintains a curated conflict roster and tracks how each conflict's dynamics interact with broader geopolitical systems — treating escalation as a structural pattern, not a series of isolated events.",
        "cadence": "Weekly",
        "output": "Roster",
        "edge": "Escalation",
        "chips": ["Weekly · conflict watch", "8–12 active conflicts", "Escalation path tracking"],
        "tracks": [
            {"title": "Conflict roster", "desc": "Active armed conflicts meeting inclusion thresholds — assessed individually for escalation and spillover risk."},
            {"title": "Escalation indicators", "desc": "Friction indicators, nuclear/WMD signals, third-party involvement, and threshold-crossing patterns."},
            {"title": "Spillover dynamics", "desc": "Refugee flows, proxy activation, supply chain disruption, and regional destabilisation risk."},
            {"title": "Roster watch", "desc": "Conflicts approaching inclusion or retirement, with two-week minimum watch period before changes."},
        ],
        "how_dashboard": "Start here for the lead signal, conflict roster status, and escalation indicators this week.",
        "how_latest": "Read the current report for detailed per-conflict analysis, roster watch, and cross-monitor flags.",
        "how_lk": "Use this for persistent context — historical conflict dynamics, escalation baselines, and structural patterns.",
        "how_chatter": "Check the pre-synthesis signal flow for fresh conflict indicators and escalation movement before elevation.",
        "why_different": "SCEM is depth-first: a curated roster of 8–12 conflicts allows genuine analysis per conflict rather than shallow global coverage.",
        "why_different_points": [
            "Curated roster with inclusion/retirement criteria — not a comprehensive conflict database.",
            "Tracks escalation paths as structural dynamics, not just event-level developments.",
            "Cross-monitor flags connect conflict dynamics to macro, environmental, and democratic stress.",
        ],
        "cross_monitors": [
            {"monitor": "GMM", "desc": "Conflict-driven commodity disruption and sanctions cascade effects."},
            {"monitor": "ERM", "desc": "Environmental stress compounding fragile-state and conflict-zone dynamics."},
            {"monitor": "FCW", "desc": "Information warfare and cognitive operations as conflict-zone capabilities."},
        ],
        "publish": "Sundays at 18:00 UTC",
    },
}


def esc(s):
    """HTML-escape a string."""
    return html_mod.escape(str(s)) if s else ""


# Note: load_report, get_signal_title, get_signal_body, get_issue_meta, get_pill_data
# have been removed. Latest Issue + pills + glance are now JS-fetch-driven.
# The per-monitor DATA_CONFIG (below) maps real JSON shapes to a unified JS config.


# ── Per-monitor data config ──────────────────────────────────────────
# Maps real report-latest.json shapes to a unified JS config.
# When schema sprints normalise fields, update HERE — JS + template untouched.
#
# signal_path: dotted path to headline string
# signal_body_path: dotted path to body/summary string (may be null)
# meta_issue_path / meta_week_path: dotted paths for issue metadata
# pills: list of {label_tpl, path, type} where type is:
#   "value" = resolve path to string
#   "count" = len(resolve path to array)
#   "count_dict" = len(resolve path, expect dict with .flags or similar)
#   "count_prefix" = count keys starting with prefix
# glance_slots: list of {label, path, type} same semantics
#
# cross_monitor_flags shape:
#   WDM = raw list; all others = dict with .flags array
#   We handle this with "count_dict_key" type: count items at path.key

DATA_CONFIG = {
    "democratic-integrity": {
        "signal_path": "signal.headline",
        "signal_body_path": "signal.body",
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} countries tracked", "path": "heatmap", "type": "count"},
            {"label_tpl": "{n} integrity flags", "path": "institutional_integrity_flags", "type": "count"},
            {"label_tpl": "{n} intelligence items", "path": "intelligence_items", "type": "count"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "signal.headline", "type": "value"},
            {"label": "Countries tracked", "path": "heatmap", "type": "count"},
            {"label": "Integrity flags", "path": "institutional_integrity_flags", "type": "count"},
            {"label": "Watch items", "path": "intelligence_items", "type": "count"},
        ],
    },
    "macro-monitor": {
        "signal_path": "signal.headline",
        "signal_body_path": None,
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} indicator domains", "path": "indicator_domains", "type": "count"},
            {"label_tpl": "{n} tail risks", "path": "tail_risks", "type": "count"},
            {"label_tpl": "Regime: {v}", "path": "stress_regime.regime", "type": "value"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "signal.headline", "type": "value"},
            {"label": "Stress regime", "path": "signal.regime", "type": "value"},
            {"label": "Domains scored", "path": "indicator_domains", "type": "count"},
            {"label": "Tail risks", "path": "tail_risks", "type": "count"},
        ],
    },
    "european-strategic-autonomy": {
        "signal_path": "signal.title",
        "signal_body_path": "signal.body",
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} defence developments", "path": "defence_developments", "type": "count"},
            {"label_tpl": "{n} hybrid threats", "path": "hybrid_threats", "type": "count"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "signal.title", "type": "value"},
            {"label": "Defence items", "path": "defence_developments", "type": "count"},
            {"label": "Hybrid threats", "path": "hybrid_threats", "type": "count"},
            {"label": "Cross-monitor flags", "path": "cross_monitor_flags.flags", "type": "count"},
        ],
    },
    "fimi-cognitive-warfare": {
        "signal_path": "signal.headline",
        "signal_body_path": "signal.note",
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} campaigns tracked", "path": "campaigns", "type": "count"},
            {"label_tpl": "{n} actors tracked", "path": "actor_tracker", "type": "count"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "signal.headline", "type": "value"},
            {"label": "Active campaigns", "path": "campaigns", "type": "count"},
            {"label": "Actors tracked", "path": "actor_tracker", "type": "count"},
            {"label": "Cross-monitor flags", "path": "cross_monitor_flags.flags", "type": "count"},
        ],
    },
    "ai-governance": {
        # AGM has no top-level signal; key_judgments[0].judgment is closest
        "signal_path": "key_judgments.0.judgment",
        "signal_body_path": None,
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} modules covered", "path": "_prefix:module_", "type": "count_prefix"},
            {"label_tpl": "{n} key judgments", "path": "key_judgments", "type": "count"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "key_judgments.0.judgment", "type": "value"},
            {"label": "Modules covered", "path": "_prefix:module_", "type": "count_prefix"},
            {"label": "Key judgments", "path": "key_judgments", "type": "count"},
            {"label": "Cross-monitor flags", "path": "cross_monitor_flags.flags", "type": "count"},
        ],
    },
    "environmental-risks": {
        # ERM uses m00_the_signal.lead_signal (plain string)
        "signal_path": "m00_the_signal.lead_signal",
        "signal_body_path": None,
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} events logged", "path": "extreme_events_log", "type": "count"},
            {"label_tpl": "{n} tipping points", "path": "tipping_point_tracker", "type": "count"},
            {"label_tpl": "{n} boundaries exceeded", "path": "m00_the_signal.boundaries_exceeded", "type": "value"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "m00_the_signal.lead_signal", "type": "value"},
            {"label": "Events logged", "path": "extreme_events_log", "type": "count"},
            {"label": "Tipping points", "path": "tipping_point_tracker", "type": "count"},
            {"label": "Cross-monitor flags", "path": "cross_monitor_flags.flags", "type": "count"},
        ],
    },
    "conflict-escalation": {
        "signal_path": "lead_signal.headline",
        "signal_body_path": "lead_signal.summary",
        "meta_issue_path": "meta.issue",
        "meta_week_path": "meta.week_label",
        "pills": [
            {"label_tpl": "{n} active conflicts", "path": "conflict_roster", "type": "count"},
            {"label_tpl": "{n} on watch", "path": "roster_watch", "type": "count"},
        ],
        "glance_slots": [
            {"label": "Lead signal", "path": "lead_signal.headline", "type": "value"},
            {"label": "Active conflicts", "path": "conflict_roster", "type": "count"},
            {"label": "Roster watch", "path": "roster_watch", "type": "count"},
            {"label": "Cross-monitor flags", "path": "cross_monitor_flags.flags", "type": "count"},
        ],
    },
}


# Note: _resolve_glance_value and get_glance_data removed.
# Glance + Latest Issue are now populated client-side via JS fetch from report-latest.json.
# The DATA_CONFIG above provides the per-monitor path mapping.
# When Sprint 4 normalises signal fields, update DATA_CONFIG — JS stays untouched.


def build_sidebar(m, slug):
    """Build sidebar HTML."""
    return f'''  <nav class="monitor-sidebar" aria-label="Page sections">
    <div class="sidebar-nav__title">Sections</div>
    <ul>
      <li><a href="#section-hero" class="active">Overview</a></li>
      <li><a href="#section-latest">Latest Issue</a></li>
      <li><a href="#section-how">How to Use</a></li>
      <li><a href="#section-tracks">What {m["abbr"]} Tracks</a></li>
      <li><a href="#section-glance">This Week</a></li>
      <li><a href="#section-different">Analytical Approach</a></li>
    </ul>

    <div style="padding:var(--space-6) var(--space-4) var(--space-4);border-top:1px solid var(--color-border-subtle);margin-top:var(--space-4)">
      <div style="display:flex;flex-direction:column;gap:var(--space-2)">
        <a href="dashboard.html" class="btn btn--primary" style="justify-content:center;font-size:var(--text-xs)">Dashboard &rarr;</a>
      </div>
    </div>
  </nav>'''


# ── Shared JS for client-side data fetch ──────────────────────────────
# This JS block is embedded in every overview page.
# It reads DATA_CONFIG (per-monitor, embedded as JSON) and fetches report-latest.json.
# Handles: dotted paths ("signal.headline"), array indices ("key_judgments.0.judgment"),
# count of arrays, count_prefix (keys matching prefix), and graceful null fallback.
#
# ARCHITECTURE NOTE:
# - Hero, route cards, tracks, analytical approach = STATIC (editorial copy, baked by generator)
# - Latest Issue card + Glance section = DYNAMIC (JS fetch from report-latest.json)
# - When schema Sprint 4 normalises signal fields, update DATA_CONFIG in Python — JS untouched.

OVERVIEW_JS = r'''
<script>
(function() {
  var CFG = window.__OV_CONFIG;
  if (!CFG) return;

  /**
   * Resolve a dotted path against a JSON object.
   * Supports: "signal.headline", "key_judgments.0.judgment" (array index),
   * and returns null on any miss.
   */
  function resolvePath(obj, path) {
    if (!obj || !path) return null;
    var parts = path.split('.');
    var cur = obj;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return null;
      var p = parts[i];
      // Array index: "0", "1", etc.
      if (Array.isArray(cur) && /^\d+$/.test(p)) {
        cur = cur[parseInt(p, 10)];
      } else if (typeof cur === 'object') {
        cur = cur[p];
      } else {
        return null;
      }
    }
    return cur;
  }

  /**
   * Extract a display value from report data using a slot config.
   * type: "value" = resolve path to string (truncate to 120 chars)
   *       "count" = len(resolved array)
   *       "count_prefix" = count top-level keys matching prefix
   */
  function extractSlotValue(data, slot) {
    var path = slot.path;
    var type = slot.type;
    if (type === 'count_prefix') {
      // path = "_prefix:module_" -> count keys starting with "module_"
      var prefix = path.replace('_prefix:', '');
      var n = 0;
      for (var k in data) { if (k.indexOf(prefix) === 0) n++; }
      return n > 0 ? String(n) : null;
    }
    var val = resolvePath(data, path);
    if (val == null) return null;
    if (type === 'count') {
      if (Array.isArray(val)) return val.length > 0 ? String(val.length) : null;
      return null;
    }
    // type === 'value'
    if (typeof val === 'string') return val.length > 120 ? val.slice(0, 117) + '...' : val;
    if (typeof val === 'number') return String(val);
    return null;
  }

  function esc(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function populateLatestIssue(data) {
    var card = document.getElementById('latest-card');
    if (!card) return;

    // Issue metadata
    var issue = resolvePath(data, CFG.meta_issue_path);
    var week = resolvePath(data, CFG.meta_week_path);
    var label = card.querySelector('.card__label');
    if (label) {
      var parts = [];
      if (issue != null) parts.push('Issue ' + issue);
      if (week) parts.push(week);
      label.textContent = parts.length > 0 ? parts.join(' · ') : '';
    }

    // Signal headline
    var headline = resolvePath(data, CFG.signal_path);
    var titleEl = card.querySelector('.card__title');
    if (titleEl) {
      if (headline) {
        titleEl.textContent = headline.length > 160 ? headline.slice(0, 157) + '...' : headline;
      } else {
        titleEl.textContent = 'No signal data available';
        titleEl.style.color = 'var(--color-text-tertiary)';
      }
    }

    // Signal body (optional)
    var bodyEl = card.querySelector('.card__body');
    if (CFG.signal_body_path) {
      var body = resolvePath(data, CFG.signal_body_path);
      if (body && bodyEl) {
        bodyEl.textContent = body;
        bodyEl.style.display = '';
      } else if (!body && !bodyEl) {
        // No body path and no element — fine
      }
    }

    // Pills
    var pillBox = document.getElementById('latest-pills');
    if (pillBox && CFG.pills) {
      var html = '';
      for (var i = 0; i < CFG.pills.length; i++) {
        var pill = CFG.pills[i];
        var pv = extractSlotValue(data, pill);
        if (pv != null) {
          var txt = pill.label_tpl.replace('{n}', pv).replace('{v}', pv);
          html += '<span class="ov-chip">' + esc(txt) + '</span>';
        }
      }
      pillBox.innerHTML = html;
    }

    // Remove loading state
    card.classList.remove('ov-loading');
  }

  function populateGlance(data) {
    var row = document.getElementById('glance-row');
    if (!row || !CFG.glance_slots) return;

    var html = '';
    for (var i = 0; i < CFG.glance_slots.length; i++) {
      var slot = CFG.glance_slots[i];
      var val = extractSlotValue(data, slot);
      html += '<div class="ov-glance-box">';
      html += '<div class="ov-glance-box__label">' + esc(slot.label) + '</div>';
      if (val != null) {
        html += '<div class="ov-glance-box__value">' + esc(val) + '</div>';
      } else {
        html += '<div class="ov-glance-box__value ov-glance-box__empty">Awaiting data</div>';
      }
      html += '</div>';
    }
    row.innerHTML = html;
  }

  // Fetch and populate
  var url = 'data/report-latest.json';
  fetch(url)
    .then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function(data) {
      populateLatestIssue(data);
      populateGlance(data);
    })
    .catch(function(err) {
      console.warn('[Overview] Could not load ' + url + ':', err.message);
      // Leave graceful empty states in place
      var card = document.getElementById('latest-card');
      if (card) card.classList.remove('ov-loading');
    });
})();
</script>
'''


def build_overview(slug, m):
    """Build the full overview HTML for a monitor.
    
    Static sections: hero, route cards, tracks, analytical approach, cross-monitor.
    Dynamic sections (JS fetch): Latest Issue card, This Week at a Glance.
    """
    config = DATA_CONFIG.get(slug, {})
    config_json = json.dumps(config)

    tracks_html = ""
    for t in m["tracks"]:
        tracks_html += f'''        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title">{esc(t["title"])}</div>
          <div class="card__body">{esc(t["desc"])}</div>
        </div>
'''

    cross_html = ""
    for c in m["cross_monitors"]:
        cross_html += f"          <li><strong>{esc(c['monitor'])}</strong> — {esc(c['desc'])}</li>\n"

    chips_html = ""
    for chip in m["chips"]:
        chips_html += f'          <span class="ov-chip">{esc(chip)}</span>\n'

    different_points = ""
    for pt in m["why_different_points"]:
        different_points += f"          <li>{esc(pt)}</li>\n"

    sidebar = build_sidebar(m, slug)

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(m["name"])} — Overview · Asymmetric Intelligence</title>
  <meta name="description" content="{esc(m["mission"][:160])}">
  <link rel="stylesheet" href="../shared/css/base.css">
  <link rel="stylesheet" href="assets/monitor.css">
  <script src="../shared/js/theme.js"></script>
  <script src="../shared/js/nav.js"></script>
</head>

<body>
<nav class="monitor-nav" aria-label="Monitor navigation">
  <a class="monitor-nav__brand" href="dashboard.html"></a>
  <button class="monitor-nav__hamburger" aria-label="Toggle menu" aria-expanded="false">
    <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
      <line x1="2" y1="4.5" x2="16" y2="4.5"/><line x1="2" y1="9" x2="16" y2="9"/><line x1="2" y1="13.5" x2="16" y2="13.5"/>
    </svg>
  </button>
  <ul class="monitor-nav__links" role="list"></ul>
  <div class="monitor-nav__actions"></div>
</nav>

<div class="monitor-layout">
  <main class="monitor-main" id="main-content">

    <!-- ── Hero (STATIC — editorial copy) ── -->
    <section class="module-section" id="section-hero">
      <div class="page-header" style="border-bottom:none;margin-bottom:var(--space-4);padding-top:var(--space-4)">
        <div class="page-header__eyebrow">{esc(m["abbr"])} &middot; Asymmetric Intelligence</div>
        <p class="page-header__sub" style="margin-top:var(--space-2)">{esc(m["mission"])}</p>
        <div class="page-header__meta">
          <span>Published {esc(m["publish"])}</span>
        </div>
      </div>

      <!-- Why it matters now -->
      <div class="ov-hero-band">
        <div class="ov-hero-band__content">
          <div class="ov-band-title">Why it matters now</div>
          <div class="ov-band-head">{esc(m["why_now_title"])}</div>
          <p class="ov-band-copy">{esc(m["why_now_body"])}</p>
          <div class="ov-chips">
{chips_html}          </div>
        </div>
        <div class="ov-band-stats">
          <div class="ov-mini-stat">
            <span>Current cadence</span>
            <strong>{esc(m["cadence"])}</strong>
          </div>
          <div class="ov-mini-stat">
            <span>Core output</span>
            <strong>{esc(m["output"])}</strong>
          </div>
          <div class="ov-mini-stat">
            <span>Distinctive edge</span>
            <strong>{esc(m["edge"])}</strong>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Latest Issue (DYNAMIC — JS fetch from report-latest.json) ── -->
    <section class="module-section" id="section-latest">
      <div class="module-header">
        <div class="module-title">Latest Issue</div>
      </div>
      <article class="card ov-loading" id="latest-card" style="border-left:4px solid var(--monitor-accent)">
        <div class="card__label">Loading&hellip;</div>
        <div class="card__title" style="font-size:var(--text-lg);line-height:1.35">Loading latest issue&hellip;</div>
        <div class="card__body" style="display:none"></div>
        <div id="latest-pills" style="display:flex;gap:var(--space-2);flex-wrap:wrap;margin:var(--space-3) 0"></div>
        <div class="card__footer">
          <a class="btn btn--primary" href="dashboard.html">Dashboard &rarr;</a>
          <a class="btn btn--outline" href="report.html">Full Report &rarr;</a>
        </div>
      </article>
    </section>

    <!-- ── How to use this monitor (STATIC — editorial copy) ── -->
    <section class="module-section" id="section-how">
      <div class="module-header">
        <div class="module-title">How to use this monitor</div>
      </div>
      <p style="color:var(--color-text-secondary);margin-bottom:var(--space-4);max-width:680px">{esc(m["abbr"])} is designed for both rapid risk orientation and deeper structural reading.</p>
      <div class="ov-route-grid">
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title">Dashboard</div>
          <div class="card__body">{esc(m["how_dashboard"])}</div>
          <div class="card__footer"><a href="dashboard.html" class="source-link">Open Dashboard &rarr;</a></div>
        </div>
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title">Latest Issue</div>
          <div class="card__body">{esc(m["how_latest"])}</div>
          <div class="card__footer"><a href="report.html" class="source-link">Read latest issue &rarr;</a></div>
        </div>
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title">Living Knowledge</div>
          <div class="card__body">{esc(m["how_lk"])}</div>
          <div class="card__footer"><a href="living-knowledge.html" class="source-link">Open Living Knowledge &rarr;</a></div>
        </div>
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title">Chatter</div>
          <div class="card__body">{esc(m["how_chatter"])}</div>
          <div class="card__footer"><a href="chatter.html" class="source-link">Scan Chatter &rarr;</a></div>
        </div>
      </div>
    </section>

    <!-- ── What this monitor tracks (STATIC — editorial copy) ── -->
    <section class="module-section" id="section-tracks">
      <div class="module-header">
        <div class="module-title">What {esc(m["abbr"])} tracks</div>
      </div>
      <p style="color:var(--color-text-secondary);margin-bottom:var(--space-4);max-width:680px">{esc(m["name"])} covers the systems and structures that matter — not headlines.</p>
      <div class="ov-route-grid">
{tracks_html}      </div>
    </section>

    <!-- ── This week at a glance (DYNAMIC — JS fetch from report-latest.json) ── -->
    <section class="module-section" id="section-glance">
      <div class="module-header">
        <div class="module-title">This week at a glance</div>
      </div>
      <div class="ov-glance-row" id="glance-row">
        <div class="ov-glance-box"><div class="ov-glance-box__label">Loading&hellip;</div><div class="ov-glance-box__value ov-glance-box__empty">&nbsp;</div></div>
      </div>
    </section>

    <!-- ── Analytical approach + Cross-monitor (STATIC — editorial copy) ── -->
    <section class="module-section" id="section-different">
      <div class="ov-split-grid">
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title" style="font-size:var(--text-lg)">Analytical approach</div>
          <div class="card__body">
            <p>{esc(m["why_different"])}</p>
            <ul style="margin-top:var(--space-3);padding-left:var(--space-5)">
{different_points}            </ul>
          </div>
        </div>
        <div class="card" style="border-left:3px solid var(--monitor-accent)">
          <div class="card__title" style="font-size:var(--text-lg)">Cross-monitor connections</div>
          <div class="card__body">
            <ul style="padding-left:var(--space-5)">
{cross_html}            </ul>
          </div>
        </div>
      </div>
    </section>

  </main>

{sidebar}

</div>

<footer class="monitor-footer"></footer>

<!-- Per-monitor data config (embedded by generator — update DATA_CONFIG in Python, not here) -->
<script>window.__OV_CONFIG = {config_json};</script>
{OVERVIEW_JS}
</body>
</html>'''


# ── Generate all 7 ─────────────────────────────────────────────
for slug, m in MONITORS.items():
    out_path = os.path.join(STATIC, slug, "overview.html")
    html_content = build_overview(slug, m)
    with open(out_path, "w") as f:
        f.write(html_content)
    line_count = html_content.count("\n") + 1
    print(f"  {slug}/overview.html — {line_count} lines ✓")

print(f"\nDone: 7 overview pages generated")

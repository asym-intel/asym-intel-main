# asym-intel — Visual Design & Infographics Handover
## All 7 Monitors + Platform-Wide Visuals
## Version: 2026-04-05 | For: Dedicated visuals/graphics thread

---

## 1. Purpose of this thread

This handover is for a dedicated thread focused on **visual design, charts, infographics,
and dashboard enhancements** across the entire asym-intel platform (asym-intel.info).

Goals for the new thread:
- Design a coherent **visual language** for the platform (colours, chart types, layout conventions).
- Build **exemplar visuals** for each monitor's dashboard.
- Design **methodology infographics** explaining the platform architecture.
- Plan **integration into Hugo** (build-time chart generation, template structure).
- Produce a **visual style guide** for future consistency.

This thread is scoped to the **open asym-intel site only**. The commercial product
(Leverage Signal at signal.asym-intel.info) has its own visual design thread.

---

## 2. Platform overview

### 2.1 What asym-intel is

A public, methodology-transparent OSINT/intelligence platform with 7 monitors
(an 8th — EGM — is planned to replace GMM in 2027).

Each monitor runs a structured data pipeline:
- **Collector** (GitHub Actions + Perplexity sonar) → `chatter-latest.json`
- **Synthesiser** (GHA + Perplexity API) → `synthesis-latest.json`
- **Analyst** (Computer task / cron) → `report-latest.json` + dated archive
- **Hugo static site** → dashboards and report pages

All content is open (CC BY 4.0), aimed at policy, research, and serious observer audiences.

### 2.2 Technical stack (visual context)

- Static site: **Hugo**
- Data: JSON files under `pipeline/monitors/{slug}/`
- Charts and visuals: **Python/Plotly** at build time → PNG/SVG → referenced in Hugo templates
- CSS: restrained, performance-focused (Nexus design system — warm neutral surfaces, teal accent)
- Typography: modern sans-serif, clear hierarchy, Swiss-influenced restraint

The visuals thread should work **with** the existing Hugo + JSON pattern, not replace it.
Build-time chart generation (PNG/SVG) is strongly preferred over heavy client-side JS.

### 2.3 Tone and audience

- Audience: policy analysts, researchers, risk professionals, informed citizens.
- Tone: **serious, calm, precise**. Visuals must communicate rigour, not hype.
- Avoid: trading-app aesthetics, meme graphics, rainbow colour schemes, heavy animation.
- Reference quality: V-Dem dashboards, ECFR policy charts, ACLED conflict visualisations,
  Economist-style small multiples.

---

## 3. Design constraints (non-negotiable)

- **Accessibility:** alt text on every chart, high contrast, no meaning conveyed by colour alone.
- **Mobile-first:** all visuals must work at 375px width; no tiny axis labels.
- **Performance:** total page weight target <1.5MB. Build-time PNG/SVG; no heavy client JS.
- **Epistemic honesty:** confidence bands and null signals must be shown explicitly,
  not hidden. No false precision. No visual elements that overstate certainty.
- **Reduced motion:** animated charts must respect `prefers-reduced-motion`.

---

## 4. Colour system for visuals

### 4.1 Monitor colour assignments

Each monitor gets a distinct accent colour. All colours are drawn from the existing
Nexus design system to guarantee consistency with the site's surfaces and type.

| Monitor | Abbr | Assigned colour | Hex | Use case |
|---|---|---|---|---|
| FIMI & Cognitive Warfare | FCW | Nexus Teal (primary) | `#01696f` | Narrative/info ops |
| Strategic Conflict & Escalation | SCEM | Notification Red | `#a13544` | Conflict/escalation |
| World Democracy Monitor | WDM | Success Green | `#437a22` | Democracy/governance |
| European Strategic Autonomy | ESA | Blue (Limsa) | `#006494` | European strategy |
| AI Governance Monitor | AGM | Purple (Kuja) | `#7a39bb` | Technology/AI |
| Global Environmental Risks | ERM | Orange (Costa) | `#da7101` | Environmental risk |
| Global Macro Monitor | GMM | Gold (Altana) | `#d19900` | Economics/macro |
| EGM (planned) | EGM | Warning Brown | `#964219` | Energy/resources |

**Dark mode variants** are already defined in the Nexus palette for each colour.
Always use the CSS variable (e.g. `var(--color-primary)`) not hardcoded hex.

### 4.2 Confidence level colours

| Level | Colour | Hex | Use |
|---|---|---|---|
| Confirmed | Success Green | `#437a22` | High-confidence findings |
| Probable | Gold | `#d19900` | Medium-confidence |
| Possible | Warning Brown | `#964219` | Lower-confidence |
| Monitoring | Teal | `#01696f` | Watch/track, no assessment yet |
| Null signal | Text Faint | `#bab9b4` | No material signal this period |

### 4.3 Chart surface and text

- Chart background: `var(--color-surface)` — never pure white
- Chart text: `var(--color-text)` and `var(--color-text-muted)`
- Grid lines: `var(--color-divider)` — very light
- Borders: `oklch(from var(--color-text) l c h / 0.12)` — alpha-blended

---

## 5. Chart types and conventions

### 5.1 Standard chart types for the platform

| Chart type | Use case | Monitor context |
|---|---|---|
| **Step/state chart** | Entity trajectory over time (escalating/stable/de-escalating) | All monitors |
| **Confidence distribution bar** | Weekly breakdown of finding confidence levels | All monitors |
| **Small multiples** | Same chart repeated per monitor for cross-platform view | Homepage/platform |
| **Timeline / event strip** | Key events on a shared time axis | SCEM, FCW, GMM |
| **Chokepoint status panel** | Status grid (normal/elevated/disrupted) | EGM (planned) |
| **Slope graph** | Entity state change week-over-week | All monitors |
| **Heatmap/matrix** | Cross-monitor flag frequency | Platform-wide |
| **Simple map inset** | Geographic context for conflict or energy events | SCEM, EGM |

### 5.2 Typography conventions for charts

- Chart titles: `var(--text-base)`, bold, `var(--color-text)`.
- Axis labels: `var(--text-sm)`, `var(--color-text-muted)`.
- Annotations/callouts: `var(--text-xs)`, `var(--color-text-muted)`.
- No text smaller than 12px (the absolute floor from the design system).
- No sideways axis labels — rotate or abbreviate if labels are too long.

### 5.3 Layout conventions

- Charts: max width matches the content column (`var(--content-default)` = 960px).
- On mobile: full-width, single column, minimum 375px.
- Margins: `var(--space-4)` on all sides inside chart area.
- Legend: below chart on mobile, right of chart on desktop.

---

## 6. The 7 monitors — visual requirements

### 6.1 FCW — FIMI & Cognitive Warfare Monitor

**Slug:** `fimi-cognitive-warfare`
**Colour:** Teal `#01696f`
**Focus:** information operations, influence campaigns, narrative weaponisation.

**Key entities tracked:**
- State-linked actors (GRU units, IRA-style operations, state-affiliated media).
- Narrative campaigns (identified per-week by the synthesiser).
- Platforms (Telegram, X/Twitter, Facebook, TikTok — as distribution infrastructure).
- Target countries/regions.

**Dashboard visual requirements:**
1. **Narrative campaign status panel** — active/monitoring/dormant campaigns,
   colour-coded by confidence.
2. **Weekly finding confidence chart** — bar chart: Confirmed / Probable / Possible
   count per week over the last 12 weeks.
3. **Entity trajectory chart** — slope graph: top 5 entities, week-over-week
   escalation/stable/de-escalation.
4. **Platform distribution strip** — simple visual showing which platforms feature
   most heavily in the current week's signal.

**Report-level visual:**
- One **timeline of campaign events** per monthly digest.
- One **entity spotlight** chart per significant new finding.

**Key JSON fields to map to visuals:**
- `key_judgments[].confidence` → confidence distribution chart.
- `entities[].trajectory` → entity trajectory chart.
- `entities[].status` → campaign status panel.
- `signal_panel.lead_signal` → dashboard headline callout.

---

### 6.2 SCEM — Strategic Conflict & Escalation Monitor

**Slug:** `conflict-escalation`
**Colour:** Red `#a13544`
**Focus:** kinetic conflict, escalation ladders, ceasefire dynamics, military posture.

**Key entities tracked:**
- State belligerents and allied parties.
- Non-state armed groups.
- Active conflict theatres.
- De-escalation processes / peace talks.

**Dashboard visual requirements:**
1. **Conflict theatre status panel** — named active theatres with escalation direction
   (escalating / stable / de-escalating), colour-coded.
2. **Escalation ladder visual** — for the highest-priority theatre: a stepped visual
   showing current assessed position on the escalation spectrum.
3. **Weekly confidence chart** — same format as FCW (Confirmed/Probable/Possible).
4. **Entity state chart** — top 5 tracked belligerents, status week-over-week.

**Report-level visual:**
- Simple **map inset** for the current focal theatre (no GIS; a clean contextual
  schematic or a minimal SVG/image map).
- **Escalation timeline** per monthly digest.

**Key JSON fields:**
- `signal_panel.lead_indicator_direction` → theatre status panel.
- `key_judgments[].confidence` → confidence chart.
- `entities[].trajectory` → entity state chart.

---

### 6.3 WDM — World Democracy Monitor

**Slug:** `democratic-integrity`
**Colour:** Green `#437a22`
**Focus:** democratic backsliding, electoral integrity, institutional erosion, civil liberties.

**Key entities tracked:**
- States under backsliding assessment.
- Electoral processes (upcoming or recent).
- Institutions under threat (courts, media, civil society).
- Specific political actors driving or resisting erosion.

**Dashboard visual requirements:**
1. **Backsliding status panel** — countries currently under active WDM assessment,
   with trajectory (worsening/stable/improving).
2. **Election calendar strip** — upcoming elections for monitored states (3-month
   forward window), derived from `signal_panel`.
3. **Confidence distribution chart** — same format as FCW/SCEM.
4. **Institutional health indicators** — a simple 3–4 category panel (judiciary,
   media, civil society, electoral body) for the focal state, where data allows.

**Report-level visual:**
- **Country spotlight chart** — trajectory of key indicators for the focal state
  over the last 8–12 weeks.
- **Cross-monitor callout** when WDM intersects with FCW (narrative ops targeting
  democratic processes) — a small flag badge in the report layout.

**Key JSON fields:**
- `entities[].status` → backsliding panel.
- `signal_panel.election_calendar` (if present) → election strip.
- `key_judgments[].confidence` → confidence chart.

---

### 6.4 ESA — European Strategic Autonomy Monitor

**Slug:** `european-strategic-autonomy`
**Colour:** Blue `#006494`
**Focus:** EU/European strategic posture, defence integration, transatlantic relations,
sovereignty-building.

**Key entities tracked:**
- EU institutions and key member states.
- NATO dynamics and transatlantic relationships.
- European defence industry and procurement.
- Specific autonomy-building initiatives (EDIP, REARM Europe, etc.).

**Dashboard visual requirements:**
1. **Strategic autonomy progress panel** — 4–5 tracked dimensions (defence spending,
   industrial capacity, diplomatic posture, energy independence, tech sovereignty)
   with a simple direction indicator per dimension.
2. **Key actor stance chart** — major member states' posture on core ESA dimensions
   this week (supportive/neutral/resistant).
3. **Confidence distribution chart** — standard format.
4. **Initiative status strip** — active EU strategic initiatives under monitoring,
   with status.

**Report-level visual:**
- **Progress indicators** for the focal initiative, week-over-week.
- **Map inset** if geographic posture shift is relevant (e.g. Baltic/Eastern flank).

**Key JSON fields:**
- `signal_panel` fields → strategic autonomy panel.
- `entities[].trajectory` → actor stance chart.
- `key_judgments[].confidence` → confidence chart.

---

### 6.5 AGM — AI Governance Monitor

**Slug:** `ai-governance`
**Colour:** Purple `#7a39bb`
**Focus:** AI regulation, governance frameworks, frontier model developments, geopolitics
of AI.

**Key entities tracked:**
- Regulatory bodies and legislative processes (EU AI Act, US executive orders, etc.).
- Frontier model developers (OpenAI, Anthropic, Google DeepMind, xAI, Baidu, etc.).
- Standards bodies (NIST, ISO/IEC, IEEE).
- State actors (US, EU, China, UK as governance rivals/partners).

**Dashboard visual requirements:**
1. **Governance tracker panel** — major regulatory processes with status
   (advancing/stalled/enacted).
2. **Actor posture chart** — key state actors' AI governance stance (open/restrictive/
   bilateral) this week.
3. **Confidence distribution chart** — standard format.
4. **Frontier development strip** — notable capability/deployment events in the
   current monitoring window (events, not assessments).

**Report-level visual:**
- **Regulatory process timeline** per monthly digest — showing where major frameworks
   are in their legislative journeys.
- **Cross-monitor callout** when AGM intersects with ESA (AI as strategic autonomy
  dimension) or FCW (AI-generated information operations).

**Key JSON fields:**
- `entities[].status` → governance tracker.
- `signal_panel` → actor posture chart.
- `key_judgments[].confidence` → confidence chart.

---

### 6.6 ERM — Global Environmental Risks Monitor

**Slug:** `environmental-risks`
**Colour:** Orange `#da7101`
**Focus:** climate security, resource stress, extreme weather as geopolitical risk,
environmental statecraft.

**Key entities tracked:**
- States/regions under active climate-security stress.
- Multilateral environmental processes (UNFCCC COPs, CBD, IPCC outputs).
- Resource stress nexuses (water, food, land — where geopolitically material).
- Extreme weather events with strategic/political consequences.

**Dashboard visual requirements:**
1. **Risk region status panel** — regions under active ERM assessment with
   stress direction.
2. **Stress category chart** — current week's findings distributed across
   4 categories (climate security, resource conflict, environmental statecraft,
   multilateral governance).
3. **Confidence distribution chart** — standard format.
4. **Event timeline strip** — notable extreme weather or environmental events
   in the monitoring window with assessed geopolitical relevance.

**Report-level visual:**
- **Regional stress map inset** for the focal country/region.
- **Cross-monitor callout** when ERM intersects with SCEM (conflict driven by
  resource stress) or EGM (energy/climate nexus — once EGM is live).

**Key JSON fields:**
- `signal_panel` → risk region panel.
- `key_judgments[].confidence` → confidence chart.
- `entities[].trajectory` → stress category chart.

---

### 6.7 GMM — Global Macro Monitor

**Slug:** `macro-monitor`
**Colour:** Gold `#d19900`
**Focus:** macroeconomic regime signals, central bank dynamics, sovereign risk,
geopolitics of capital flows.

**Note on GMM's future:** GMM is planned to **migrate to the commercial product
(Leverage Signal)** in 2027. EGM (Energy & Resource Geopolitics Monitor) will
replace it on asym-intel. Visual work for GMM on asym-intel should therefore be
**kept simple and low-investment** — a basic dashboard that works, rather than a
deeply designed product. The heavy visual investment for GMM belongs in the
commercial product thread.

**Dashboard visual requirements (keep minimal):**
1. **Macro regime indicator** — current assessed regime (expansion/contraction/
   transition) with confidence.
2. **Key central bank status panel** — Fed/ECB/BoE/PBoC: current assessed stance
   (hawkish/neutral/dovish) + trajectory.
3. **Confidence distribution chart** — standard format.

**Key JSON fields:**
- `signal_panel` → macro regime indicator.
- `entities[].trajectory` → central bank panel.

---

## 7. Platform-wide / cross-monitor visuals

These visuals appear on the **homepage dashboard**, not individual monitor pages.

### 7.1 Cross-monitor flag matrix

A heatmap showing which monitors have flagged relationships with each other this week.

- Rows and columns: monitor abbreviations (FCW, SCEM, WDM, ESA, AGM, ERM, GMM).
- Cell value: number of cross-monitor flags this week between each pair.
- Colour: the monitor-pair's shared accent, or a neutral scale.
- Null (no flags): faint grey cell.

This is the most distinctive platform-wide visual. It shows, at a glance, where
the most analytically active intersections are.

### 7.2 Platform signal status panel

A 7-item (or 6-item post-GMM) status row on the homepage:
- One cell per monitor showing:
  - Monitor name and colour.
  - Lead indicator direction this week (escalating/stable/de-escalating arrow).
  - Confidence of lead finding.
  - Days since last weekly report.
- Acts as the "heartbeat" of the platform.

### 7.3 Confidence distribution small multiples

A small bar chart per monitor, all in one row, showing this week's confidence
distribution (Confirmed/Probable/Possible). Allows instant comparison across monitors.

### 7.4 Timeline overlay

A shared time axis across all monitors, showing when significant escalation
events (Confirmed findings only) occurred. Useful for spotting cross-monitor
temporal clustering.

---

## 8. Methodology infographics

These are **explanatory**, not data-driven. They live on the Methodology and About pages.
They should be SVG or high-res PNG, built once and maintained as the platform evolves.

### 8.1 The 5-tier editorial architecture

A vertical diagram showing:

```
Tier 1   Daily Chatter Signal     ← automated, unvalidated
Tier 2   Weekly Synthesiser Report ← automated + validated
Tier 3   Slim Daily Digest         ← automated (FCW/SCEM only)
Tier 4   Monthly Digest            ← automated aggregation + editorial
Tier 5   Annual Reports            ← editorial, citing full evidence chain
```

With labels explaining:
- What each tier is and is not (epistemic status).
- Who produces it (GHA / Analyst / Editorial).
- Cadence.

### 8.2 The pipeline flow

A horizontal or diagonal flow diagram showing:

```
Web/sonar → Collector (GHA) → JSON → Synthesiser (GHA) → JSON
    → State Engine → Analyst (Computer) → Report → Hugo → Site
```

With brief labels on each step. Non-technical, readable by a policy audience.

### 8.3 The confidence model

A simple 4-level visual:

```
Confirmed   ███ Direct evidence + corroboration
Probable    ██░ Strong indirect evidence
Possible    █░░ Credible signal, unconfirmed
Monitoring  ░░░ Emerging pattern, not yet assessable
```

This appears on methodology pages and in report footers as a reference key.

### 8.4 Platform-to-commercial relationship

A clean two-column diagram:

```
asym-intel.info                  signal.asym-intel.info
(open platform)                  (Leverage Signal — commercial)
    │                                       │
    ├─ FCW reports ─────────────────────────┤
    ├─ SCEM reports ─────────────────────────┤
    ├─ GMM (migrating →) ──────────────────▶ │
    └─ Methodology (public) ───────────────▶ └─ Implications layer
                                               └─ Market data overlays
```

Used on the About page of both sites.

---

## 9. Integration into Hugo

### 9.1 Chart generation workflow

**Approach: Chart.js interactive charts (client-side), not build-time static images.**

Charts are rendered client-side using Chart.js, consistent with the existing monitor
dashboard architecture. This is intentional — the audience benefits from interactive
hover states, tooltips, and zoom, and the existing shared library already provides
Chart.js infrastructure.

The pattern:
1. JSON data is already published to `static/monitors/{slug}/data/` by the Analyst cron.
2. Hugo templates include Chart.js canvas elements in dashboard HTML.
3. A per-monitor `charts.js` file reads the JSON and renders charts on page load.
4. Chart.js CDN is loaded in `<head>` before `charts.js` (Blueprint v2.1 rule — required).

```
static/monitors/{slug}/
  dashboard.html    ← contains <canvas> elements
  assets/
    charts.js       ← reads JSON, calls Chart.js
static/monitors/shared/
  js/               ← shared chart helpers and renderer patterns
```

**What to avoid:** build-time Python/Plotly → PNG/SVG approach. Static images lose
interactivity, increase build complexity, and duplicate the Chart.js infrastructure
already in place. Use Chart.js for all new charts on monitor pages.

**Exception:** Methodology infographics (§8) and the platform-to-commercial diagram (§8.4)
are explanatory, not data-driven. These can remain as SVG — built once, not regenerated.

### 9.2 Hugo template structure (recommended)

```
layouts/
  monitors/
    single.html          ← per-monitor dashboard page
    _default/
      report.html        ← weekly report page
  partials/
    charts/
      confidence-bar.html     ← reusable chart partial
      entity-trajectory.html
      status-panel.html
      cross-monitor-matrix.html
  index.html             ← homepage with platform status panel
```

### 9.3 Dark mode

All charts must respect light/dark mode. Preferred approach:
- Use transparent background in chart images (where PNG).
- CSS overlay with `color-scheme` to swap chart variants where needed.
- Or: generate light and dark variants of each chart in the build step,
  and swap with CSS `prefers-color-scheme` media query.

---

## 10. Recommended build sequence for the visuals thread

1. **Establish the visual design system** (colours, chart conventions, typography rules).
2. **Exemplar charts for FCW** — one monitor as proof of concept:
   - Confidence distribution bar.
   - Entity trajectory slope graph.
   - Status panel.
3. **Platform-wide status panel** and **cross-monitor matrix** (homepage).
4. **Methodology infographics** (pipeline, tiers, confidence model).
5. **Apply the design system to remaining 6 monitors** — structurally identical, different data.
6. **Hugo integration plan** — how and where these assets live in templates.
7. **Visual style guide** — document conventions for future additions.

---

## 11. Files to attach to the new visuals thread

| File | Why |
|---|---|
| This handover `.md` | Full context |
| `COLLECTOR-ANALYST-ARCHITECTURE.md` | JSON schema structure across monitors |
| `pipeline/monitors/fimi-cognitive-warfare/report-latest.json` | Exemplar data for FCW charts |
| `pipeline/monitors/fimi-cognitive-warfare/daily/chatter-latest.json` | Daily signal panel data |
| One other `report-latest.json` (e.g. SCEM) | To test cross-monitor visuals |

The methodology files are secondary for visuals — useful if the thread needs to
understand what entities/confidence levels exist, but chart design can proceed
from the JSON schemas described above.

---

## 12. Opening prompt for the new thread

> "I'm designing the visual layer for asym-intel (asym-intel.info) — a 7-monitor
> OSINT/intelligence platform built on Hugo + Python with JSON-driven dashboards.
> Using the attached handover and sample JSON, help me design:
> (1) a visual design system for all charts (colours per monitor, chart conventions,
> typography, dark mode), then
> (2) exemplar charts for the FCW dashboard (confidence distribution, entity trajectory,
> status panel), then
> (3) a cross-monitor platform status panel for the homepage.
> All charts should be build-time generated (Python/Plotly → PNG/SVG), accessible,
> and follow the tone: serious, calm, precise — reference quality is V-Dem, ACLED,
> or Economist-style small multiples."

---

*Scope: open asym-intel site only. Commercial product (Leverage Signal) visuals are a separate thread.*
*Companion documents: asym-intel-development-plan-2026-04-04.md, asym-intel-egm-concept-note-2026-04-04.md*

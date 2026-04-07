SITE REBUILD SPEC — IMPLEMENTATION ROADMAP
Legend
Priority: P1 (highest), P2, P3

Mode: C (Computer-led), H+C (Human-led with Computer assist), M (Manual)

A. Shared Library & Validator (Cross-Monitor)
ID	Item	Priority	Mode	Est.	Notes
SL-01	Cross-Monitor Flags shared component (HTML/CSS/JS) and integration into all 7 Dashboards + Living Knowledge	P1	C	3–4 hrs	One render function + shared styles + per-monitor hooks.
SL-02	Triage strip shared layout/classes and basic styling across all monitors	P1	C	3–4 hrs	Define .triage-strip pattern, then re-wrap existing elements per monitor.
SL-03	Confidence badge system distinct from severity (styles + helpers) and refactor across monitors	P1	C	3–4 hrs	Introduce new badge classes, remove severity colours from confidence.
SL-04	Signal panel white-text rule enforcement (remove muted/secondary overrides on accent panels)	P1	C	2–3 hrs	Audit .signal-block usage and inline overrides; unify on canonical pattern.
SL-05	Encoded-systems helper (code + meaning) and application to SCEM F-flags, GMM MATT, FCW codes	P2	C	3–4 hrs	Add helper in shared JS; update tiles and labels per monitor.
SL-06	Inline source-link pattern (renderer + HTML) replacing “Source →” blocks on dashboards/reports	P1	C	3–4 hrs	Use canonical sourceLink usage; update layouts/monitor HTML accordingly.
SL-07	Section nav scroll-spy shared implementation across monitors	P2	C	2–3 hrs	One JS pattern; adjust HTML hooks if needed.
SL-08	Validator checks: nav/heading match, no orphan sections, no severity misuse, min font-size, no block-only sources	P1	C	3–4 hrs	Extend validation to enforce standards.
SL-09	Monitor accent colour tokens aligned between homepage and monitors, defined at global root	P2	C	1–2 hrs	Single source of truth for monitor colour tokens.
B. Per-Monitor Implementation
B1. WDM
ID	Item	Priority	Mode	Est.	Notes
WDM-01	Compose explicit triage strip (KPI + Lead Signal + structural snapshot + primary delta)	P2	H+C	1–2 hrs	Design composition, then code using shared triage layout.
WDM-02	Confirm single primary delta construct and label any structural lenses as “Structural”	P2	M	1 hr	Mostly copy/labels.
WDM-03	Clean up minor nav/heading mismatches and confirm no orphans	P2	M	1 hr	Quick HTML pass once naming registry is enforced.
B2. GMM (updated with commercial/regulatory layer)
ID	Item	Priority	Mode	Est.	Notes
GMM-01	Build triage strip (KPI + Weekly/Lead Signal + Tail Risk/structural snapshot + primary delta + key threshold)	P1	H+C	2–3 hrs	Use GMM review A–I; ensure copy stays in “signals + context, not recommendations” register.
GMM-02	Consolidate delta layers (single primary delta; structural vs episodic labelling)	P1	H+C	2 hrs	Clarify scenarios vs Tail Risk and label “Structural” vs “This Issue” clearly.
GMM-03	Fix nav/heading mismatches, add Tail Risk nav entry, remove near-empty nav targets	P1	C	1–2 hrs	Use naming registry; ensure all visible sections are in nav.
GMM-04	Apply inline sources and encoded-systems pattern (MATT etc.)	P2	C	2 hrs	Use shared source-link pattern and encoded-systems helper; ensure codes show meanings in tiles.
GMM-05	Regulatory wording audit (public GMM surfaces only)	P1	H+C or M	2–3 hrs	Audit dashboard + Living Knowledge copy to ensure: (a) no “do this” language (buy/sell/rotate/short), (b) no model portfolios or “easy profits / high win-rate / follow our calls” framing, (c) Blind Spot, Lead Signal, and other key surfaces are clearly framed as diagnostic signals and contextual analysis, not trade recommendations. Aligns with commercial/regulatory addendum and Arena signals-software framing.
Notes for GMM:

Asymmetric Investor features (Risk Factor cards, Regime Positioning, Market Context, Watch List with triggers, sector exposure, risk appetite framing) are not part of asym-intel GMM; they belong to a separate 2027 build on investor.asym-intel.info.

Schema-prep items RC1–RC3 (asset_class_tags, time_horizon, investor_relevance) and enforcement of RC4–RC5 (regime_conviction, one_indicator_lying discipline) are targeted for Q4 2026 and early 2027; they should be tracked separately under future-commercial work, not in this 2026 rebuild sprint.

B3. FCW
ID	Item	Priority	Mode	Est.	Notes
FCW-01	Triage strip with clear campaign structural snapshot and “Top Campaigns This Issue”	P1	H+C	2–3 hrs	Clarify lifecycle semantics + composition.
FCW-02	Remove or repurpose “All Operations” if persistently near-empty; ensure single primary delta	P1	H+C	1–2 hrs	Copy + small HTML changes.
FCW-03	Fix nav/heading mismatches and anchor-ID issues	P1	C	1–2 hrs	Leverage naming checks.
FCW-04	Replace block “Source →” with inline sources; fix confidence vs severity (no amber CONFIRMED)	P1	C	2–3 hrs	Uses SL-03, SL-06.
FCW-05	Apply encoded-systems helper to any codes; ensure in-situ explanations	P2	C	1–2 hrs	Uses SL-05.
B4. ESA
ID	Item	Priority	Mode	Est.	Notes
ESA-01	Triage strip (KPI + lead + autonomy snapshot + primary delta)	P2	H+C	2 hrs	Define composition, then implement.
ESA-02	Clarify EU-level vs Member State structural split and routing to Living Knowledge	P2	H+C	2–3 hrs	Structural IA decision.
ESA-03	Fix nav/heading mismatches (Autonomy Scorecard, Member States, Cross-Monitor)	P1	C	1–2 hrs	Straightforward renames.
ESA-04	Inline sources and mobile font-size confirmation for delta section	P2	C	1–2 hrs	Use shared source pattern + quick viewport check.
B5. AGM
ID	Item	Priority	Mode	Est.	Notes
AGM-01	Implement composed triage strip as per AGM review	P1	C	2–3 hrs	Already tightly specified.
AGM-02	Consolidate Top Items vs Top Movers; clarify semantics	P1	H+C	1–2 hrs	Decide fold vs relabel + implement.
AGM-03	Nav label alignment (Delta Strip, EU AI Act, Cross-Monitor)	P1	C	1–2 hrs	Consistent with registry.
AGM-04	Inline sources for structural panels; minimal confidence badges	P2	C	2–3 hrs	Uses SL-03, SL-06.
AGM-05	“Thresholds & Inflection Points” micro-section (EU AI Act and similar cliffs)	P2	H+C	1–2 hrs	Design + placement.
B6. ERM
ID	Item	Priority	Mode	Est.	Notes
ERM-01	Triage strip (KPI + lead + planetary boundary/tipping snapshot + primary delta)	P2	H+C	2 hrs	Composition decision first.
ERM-02	Clarify multi-boundary and tipping-system structure across Dashboard vs Living Knowledge	P2	H+C	2–3 hrs	Structural IA decision.
ERM-03	Nav alignment and inline sources for structural panels	P2	C	2 hrs	Uses SL-06; minor HTML changes.
ERM-04	Apply shared empty-state design where data is accumulating	P3	C	2 hrs	Depends on PL-02.
B7. SCEM
ID	Item	Priority	Mode	Est.	Notes
SCEM-01	Triage strip (KPI + Lead Signal + GEI snapshot + primary delta)	P1	H+C	2–3 hrs	High-stakes monitor; triage clarity crucial.
SCEM-02	Distinguish structural roster and indicators from episodic deltas; Conflict Overview clearly structural	P1	H+C	2–3 hrs	Includes routing to Living Knowledge.
SCEM-03	Fix nav/heading mismatches; add nav for Conflict Overview roster	P1	C	1–2 hrs	Use naming checks.
SCEM-04	Apply encoded-systems helper to F-flags and strengthen in-situ explanations	P1	C	2–3 hrs	Uses SL-05.
SCEM-05	Decide and implement SCEM emotional register and SCEM accent vs --critical collision	P1	H+C	1–2 hrs	Requires a design/stance decision first.
SCEM-06	Apply inline sources and shared confidence vs severity rules	P2	C	2 hrs	Uses SL-03, SL-06.
C. Homepage & Cross-Monitor Experience
ID	Item	Priority	Mode	Est.	Notes
HP-01	Implement homepage monitor strip, three-zone surface split, featured-article stripe, and report-card grid per visual spec	P1	C	3–4 hrs	Spec and mockup already exist.
HP-02	Add one-sentence platform value statement and explicit routing cues	P1	H+C	1–2 hrs	You draft copy; implementation follows.
HP-03	Homepage “Today’s Raw Signal (Chatter)” widget (top-5 cross-monitor, clearly badged pre-synthesis)	P2	H+C	2–3 hrs	Needs small design + data decision; then JS implementation.
HP-04	“What’s new this week” aggregate across monitors	P2	H+C	2–3 hrs	Decide metric; then implement using existing JSON.
HP-05	Ensure homepage monitor cards/tags use shared accent tokens and tag styles	P1	C	1–2 hrs	Uses SL-09; mostly CSS/template changes.
D. Platform-Level Patterns & Docs
ID	Item	Priority	Mode	Est.	Notes
PL-01	Update section-naming-registry.md using final Q11 tables from all 7 monitors; treat as canonical	P1	M	2–3 hrs	Synthesis-only work.
PL-02	Design empty-state and “data accumulating” pattern and implement for relevant charts/sections	P2	H+C	2–3 hrs	Decide copy/visual; then implement.
PL-03	Specify cross-monitor linkback phrasing and where it is allowed	P2	M	1–2 hrs	Copy-level; implementation uses SL-01.
PL-04	Update ARCHITECTURE, DECISIONS, ROADMAP to reflect implemented patterns and Site Rebuild Spec	P1	M	2–3 hrs	Documentation alignment.
PL-05	Define and document a credit-saving workflow (what is C vs H+C vs M)	P2	M	1–2 hrs	Internal process guidance.
PL-06	Draft high-level cross-monitor comparison view spec (for later sprint)	P3	M	2 hrs	Design-only; aligns with later structural work.
If you’d like a small snippet for the GMM section of the Site Rebuild Spec itself (“Regulatory & Commercial note”), I can provide that next so the narrative spec and this ROADMAP stay in sync.

can you provide it as a .md file and ensure it includes anything else we agreed in this whole thread
I can’t physically generate or attach a new .md file in this environment right now, but here is the full markdown content you can save as, for example, SITE-REBUILD-ROADMAP-2026.md. It folds in everything we’ve agreed across the thread, including the updated GMM commercial/regulatory points and the sprint structure.

text
# Asym-Intel — Site Rebuild Spec & Implementation Roadmap (2026)

## 0. Scope and Inputs

This document consolidates:

- Seven monitor Signal-Path & Structural-Friction reviews (WDM, GMM, FCW, ESA, AGM, ERM, SCEM) — including GMM commercial and regulatory addenda (2026-04-07).
- Platform-level documents: MISSION, ROADMAP, DECISIONS, COLOUR REGISTRY, ARCHITECTURE.
- Homepage visual spec (2026-04-05).
- Site Rebuild Specification and multi-sprint implementation plan agreed in April 2026.

It defines:

- Cross-monitor standards (triage, structural vs episodic, nav, evidence, Chatter, cross-monitor flags, visual rules).
- Per-monitor rebuild requirements.
- Homepage information architecture and OSINT surfaces.
- Shared library and validator changes.
- A five-sprint implementation roadmap with item IDs.
- Notes on commercialisation for GMM / Asymmetric Investor (schema and regulatory constraints).

Priorities (P1–P3) and effort estimates live in this file and in ROADMAP; this is the narrative and structural reference.

---

## 1. Cross-Monitor Standards

### 1.1 Triage Strip and Signal Path

Every monitor Dashboard must surface a **single, explicit triage strip** at the top of the page (above the fold). It is the first-read experience.

Each triage strip contains, in this order:

1. **KPI strip** — small cards for key KPIs (e.g. delta count, coverage, composite index).
2. **Lead Signal** — one strategically significant story, one paragraph, one confidence label.
3. **Structural snapshot** — monitor-specific structural picture (e.g. Risk Vector Heat, GEI, autonomy scorecard, planetary boundaries, core composite).
4. **Primary delta construct** — “Top Items This Issue” / “Top Moves This Week” / “Top Campaigns This Issue”.
5. **Threshold widget (if applicable)** — any imminent, time-bound structural threshold (e.g. EU AI Act date, escalation cliff).

The triage strip:

- Is visually grouped and labelled (e.g. “Triage — read this first”).
- Uses shared CSS classes (e.g. `.triage-strip`, `.triage-section`) so layout and behaviour are consistent across monitors.

### 1.2 Structural vs Episodic and Delta Layers

Each monitor Dashboard:

- Has **exactly one** primary weekly delta construct. Any secondary view is clearly marked as secondary (“Secondary Movers”, “Additional Changes”).
- Explicitly labels **structural** vs **episodic** content at point of encounter, e.g.:
  - “Structural — persistent index / scorecard / vectors”.
  - “This Issue — weekly change / deltas”.

Structural content (indices, long-run scores, rosters, cascades) primarily lives in Living Knowledge, with concise summary slices on the Dashboard.

### 1.3 Navigation, Naming, and Section Coverage

For all monitors:

- Right-hand section nav labels must match section headings or use a documented short form in `section-naming-registry.md`.
- Every visible section (heading + non-trivial content) must have a nav entry. Near-empty sections must either gain content or be removed from nav.
- There must be no orphan sections: visible content with no nav, or nav entries with no visible section.
- Scroll-spy behaviour (active section highlighting) is implemented once and shared across monitors.

### 1.4 Evidence, Attribution, and Confidence

Evidence:

- Source attribution is **inline and proximal** to claims; block “Source →” elements are not used as the only provenance pattern.
- A canonical inline source-link helper is used across monitors and Hugo pages.

Confidence vs severity:

- Severity palette (`--critical`, `--high`, `--moderate`, `--positive`, `--contested`) is **reserved for severity** only.
- Confidence (Confirmed / High / Assessed / Possible) uses a separate badge style (outline, neutral colours, icons) and never severity colours.
- Confidence badges and severity badges are visually distinct and used consistently.

### 1.5 Chatter and Epistemic Layers

Chatter:

- Lives on dedicated per-monitor Chatter/Digest pages.
- Is clearly labelled as “Pre-synthesis / Chatter” (or equivalent).
- Does not appear inside Dashboards or Living Knowledge as raw items; if upgraded, items become assessed intelligence.

Homepage:

- May show a small cross-monitor Chatter widget, but clearly labelled and linked to Chatter pages.

### 1.6 Cross-Monitor Flags and Journeys

Cross-monitor relationships use:

- A shared **Cross-Monitor Flags component** that appears on:
  - Each monitor Dashboard.
  - An appropriate Living Knowledge surface.
- Each flag shows:
  - Origin monitor(s).
  - Severity (and optionally confidence).
  - One-line explanation of the cross-domain link.
  - Links back to origin monitors or specific issues.

Cross-monitor linkbacks:

- Use consistent phrasing patterns (e.g. “See [monitor] for operations detail”).
- Are allowed in flags sections and, where appropriate, structural panels (with agreed patterns).

### 1.7 Visual Language and Accessibility

Platform-wide visual rules:

- Any solid accent signal panel uses white or near-white text with white-family secondary text (no muted tokens on accent backgrounds).
- Minimum body text size for analytic content is `--text-sm`; metadata and badges use at least `--text-xs`. No font sizes below `--text-xs`.
- Encoded systems (F-flags, MATT, other codes) show code **and** a short plain-language meaning inside tiles/cards, not only in legends.

---

## 2. Per-Monitor Requirements (Public Platform)

This section describes monitor-specific requirements on asym-intel.info (public platform). GMM commercialisation and Asymmetric Investor live on a separate domain and timeline (see §5).

### 2.1 WDM — World Democracy Monitor

- Implement explicit triage strip (KPI + Lead Signal + structural snapshot + primary delta) using shared layout.
- Confirm single primary delta construct; label any structural lenses as “Structural” and link to Living Knowledge.
- Clean up remaining nav/heading mismatches; ensure no orphan sections.
- Maintain inline sources; add confidence badges only where necessary, using shared confidence pattern.

### 2.2 GMM — Global Macro Monitor

Core structural requirements (unchanged from main review):

- Implement triage strip:
  - KPI strip.
  - Lead Signal (currently “Weekly Signal”).
  - Structural snapshot (Tail Risk / macro-stress).
  - Primary delta list.
  - Any key threshold widget.
- Consolidate delta layers:
  - Ensure one primary weekly delta construct; label secondary deltas.
  - Distinguish structural sections (Tail Risk, scenarios, structural composites) from episodic deltas with clear labels.
- Fix nav/heading mismatches:
  - Ensure headings and nav labels match naming registry.
  - Provide nav entries for Tail Risk and other major sections.
  - Remove or merge near-empty sections.
- Apply inline sources:
  - Replace block “Source →” patterns with canonical inline sources.
- Apply encoded-systems pattern:
  - Show code and meaning where MATT or other scores appear.

Regulatory & commercial note (public GMM):

- Public GMM on asym-intel.info remains a **signals and triage** surface for open intelligence:
  - It reports **what is happening**, not “what you should do”.
  - It does **not** carry investor-facing portfolio or trade suggestions.
- All copy on GMM (Dashboard and Living Knowledge) must remain within a **signals software** / analytics framing:
  - No “buy”, “sell”, “rotate”, “short” language in relation to instruments or allocations.
  - No model portfolios (even generic / risk-tiered) on the public platform.
  - No “high win-rate”, “easy profits”, “no hard work”, or “just follow our calls” framing.
- Blind Spot / `one_indicator_lying`:
  - Is a critical differentiator and must be a named, reliable surface.
  - Must be clearly framed as a **diagnostic signal** (e.g. “this indicator appears inconsistent with …; historically such divergences have coincided with …”) without “therefore you should …” tails.
- Schema-prep for future commercialisation:
  - Enforce discipline on `regime_conviction` and `one_indicator_lying` now (always populated).
  - Plan Q4 2026 schema additions:
    - `asset_class_tags` per indicator.
    - `time_horizon` per indicator.
    - `investor_relevance` flag on executive briefing items.

### 2.3 FCW — FIMI & Cognitive Warfare

- Implement triage strip:
  - KPI strip.
  - Lead Signal.
  - Structural campaign/operation snapshot.
  - “Top Campaigns This Issue” as primary delta.
- Remove or repurpose “All Operations” if near-empty; maintain single primary delta construct.
- Fix nav/heading mismatches and anchor issues; ensure all major sections are in nav.
- Replace block “Source →” patterns with inline sources; fix confidence vs severity visual misuse (no amber CONFIRMED).
- Apply encoded-systems helper to any codes and provide in-situ explanations.

### 2.4 ESA — European Strategic Autonomy

- Implement triage strip (KPI + lead + structural autonomy snapshot + primary delta).
- Clarify and label EU-level vs Member State structural splits and routing into Living Knowledge.
- Fix nav/heading mismatches (Scorecard, Member States, Cross-Monitor).
- Inline sources for key panels; confirm mobile font sizes meet thresholds.

### 2.5 AGM — AI Governance Monitor

- Implement triage strip per AGM review:
  - KPI strip.
  - Lead Signal.
  - Risk Vector Heat summary.
  - EU AI Act countdown.
  - Primary delta list.
- Consolidate Top Items vs Top Movers; clarify semantics.
- Align nav labels (Delta Strip, EU AI Act Tracker, Cross-Monitor) with headings and naming registry.
- Add inline sources for structural panels (Risk Heat, Country Watch, Market Concentration).
- Add “Thresholds & Inflection Points” micro-section for EU AI Act / similar governance cliffs.

### 2.6 ERM — Environmental Risks Monitor

- Implement triage strip (KPI + lead + planetary boundary/tipping snapshot + primary delta).
- Clarify structure of boundaries and tipping systems across Dashboard vs Living Knowledge, including cascades.
- Align nav and headings; ensure structural systems are represented and linked.
- Inline sources for structural panels; apply shared empty-state design where data accumulates.

### 2.7 SCEM — Strategic Conflict & Escalation

- Implement triage strip (KPI + Lead Signal + GEI snapshot + primary delta).
- Clarify structural vs episodic:
  - Conflict roster, GEI, structural indicators are clearly structural.
  - Weekly deltas clearly episodic.
- Fix nav/heading mismatches and add nav entry for Conflict Overview roster.
- Apply encoded-systems helper to F-flags and ensure tiles show code and meaning.
- Decide and implement a rule for SCEM’s emotional register and the collision between SCEM accent and `--critical`:
  - Either accept and formalise the “always-on critical” register for this monitor, or
  - Adjust accent usage to preserve cross-monitor severity semantics.

---

## 3. Homepage — IA and OSINT Surfaces

### 3.1 Role and Routing

Homepage roles:

- Cross-monitor router.
- Light OSINT surface (not a dashboard).
- Narrative anchor for mission and audience.

Required:

- One-sentence platform value statement aligned with MISSION (structural risk, pre-consensus, weekly + Chatter cadence).
- Explicit routing cues, e.g.:
  - “Triage now” → monitor Dashboards.
  - “This week’s analysis” → Latest Issue pages.
  - “Structural pipelines” → Living Knowledge.
  - “Raw signal” → Chatter.

### 3.2 Visual Implementation

Implement visual spec:

- Monitor strip under top nav: monitor pills with coloured dots using shared accent tokens.
- Three-zone surface split: left monitor sidebar and right Chatter sidebar on surface colour; main content on background colour.
- Featured article stripe: left accent stripe keyed to monitor, no hero background tint, respecting “no redundant CTAs”.
- Report-card grid: 3-column grid, 1px gaps, accent strip at top of each card keyed to monitor.
- Monitor tags: colour-mix-based badges driven by monitor accent variables.

### 3.3 Homepage OSINT Surfaces

- Chatter widget:
  - “Today’s Raw Signal (Chatter)” strip showing top 5 cross-monitor items.
  - Each item clearly labelled as pre-synthesis and linked to monitor Chatter pages.
- “What’s new this week” aggregate:
  - Small summary across monitors (e.g. number of domains deteriorating vs improving).
  - Links to relevant Dashboards or briefs.

---

## 4. Shared Library & Validator

### 4.1 Shared CSS and JS

Shared library must provide:

- Canonical classes/styles for:
  - Triage strip sections.
  - Confidence badges.
  - Signal panels.
  - Encoded systems (code + meaning).
  - Section nav and scroll-spy.
  - Cross-Monitor Flags component.
- Render helpers for:
  - Inline sources.
  - Encoded systems.
  - Chatter labels.
  - Cross-Monitor Flags.

### 4.2 Validator Extensions

Validator must enforce:

- nav/heading match; no orphan sections.
- no misuse of severity palette for non-severity concepts (especially confidence).
- minimum font-size rules and analytic text at least `--text-sm`.
- no reliance on block-only “Source →” elements for evidence on dashboards/reports.

---

## 5. GMM Commercialisation & Asymmetric Investor (Future Work)

This section records how GMM’s rebuild interacts with the planned Asymmetric Investor product.

### 5.1 Platform Separation

- **asym-intel.info** — public, open, credibility surface:
  - Reports **what is happening**.
  - No investment-framed copy; no portfolio or trade suggestions.
- **investor.asym-intel.info** — commercial product (2027+):
  - Adds “what it may mean for portfolios” as implications, not advice.
  - Separate Hugo repo, templates, and editorial register.

### 5.2 Schema & Editorial Discipline

To ease 2027 build:

- Enforce:
  - `regime_conviction` is always populated and consistent.
  - `one_indicator_lying` is treated as a required weekly field in the cron prompt.
  - 3-scenario framework with probabilities is stable week to week.
- Plan Q4 2026 schema additions:
  - `asset_class_tags` per indicator.
  - `time_horizon` per indicator.
  - `investor_relevance` flag at executive briefing level.

### 5.3 Regulatory Positioning

### GMM — Regulatory & Commercial Note (Public Platform Only)

The Global Macro Monitor on asym-intel.info is a **public signals and triage surface**, not an investor product. It reports what is happening in macro risk and regimes; it does not tell anyone what trades or portfolios they should adopt.

For public GMM:

- **No investment-advice framing**
  - Do not use imperative “do this” language in relation to instruments or allocations (no “buy”, “sell”, “rotate”, “short”, “overweight”, “underweight” in a prescriptive sense).
  - Do not present model portfolios (even generic or risk-tiered) on the public dashboard or Living Knowledge.
  - Avoid any framing that implies “easy profits”, “high win-rate”, “no hard work”, or “just follow our calls”.

- **Signals software, not recommendations**
  - All primary surfaces (Lead Signal, Blind Spot, Tail Risk, scenarios, deltas) must be framed as **structured signals and contextual analysis**.
  - Wording patterns should emphasise diagnostics and context, for example:
    - “This indicator appears inconsistent with [macro reality / other indicators]. Historically, similar divergences have coincided with [regime shifts / risk repricing].”
    - Avoid any “… therefore you should [action]” tails.

- **Blind Spot / `one_indicator_lying` as a disciplined signal**
  - `one_indicator_lying` is a required weekly field in the GMM executive briefing and must be rendered as a named **Blind Spot Alert** card on the public dashboard.
  - The Blind Spot card is explicitly a **diagnostic signal** about misaligned indicators (e.g. nominal vs real M2), not a trade suggestion for any specific instrument.
  - Editorial discipline: the field should be populated every issue; missing data is treated as an error condition, not “no blind spot this week”.

- **Separation from Asymmetric Investor**
  - Investor-facing features described in the commercial development plan (Risk Factor cards, Regime Positioning, Market Context, Watch List with triggers, sector/ETF exposure, risk appetite framing) **do not appear** on asym-intel.info.
  - These belong to a future commercial product on `investor.asym-intel.info` with:
    - separate Hugo site and templates,
    - an “implications, not advice” editorial register,
    - and a dedicated legal review before launch.
  - Decisions made now on GMM schema (e.g. `asset_class_tags`, `time_horizon`, `investor_relevance`, consistent `regime_conviction`, mandatory `one_indicator_lying`) should assume that the public GMM dashboard will become the analytical foundation for the commercial product in 2027, but must **not** pre-empt commercial features on the public site.

This note is part of the acceptance criteria for all GMM rebuild work: triage strip, delta consolidation, nav fixes, evidence/encoded systems, and copy changes must remain inside the “signals + context, not recommendations” boundary.

---

## 6. Implementation Roadmap — IDs, Sprints, Modes

### 6.1 Legend

- **Priority**: P1 (highest), P2, P3  
- **Mode**:  
  - C = Computer-led  
  - H+C = Human-led + Computer assist  
  - M = Manual  

### 6.2 Shared Library & Validator (Cross-Monitor)

(IDs SL-01–SL-09, as previously listed, unchanged.)

### 6.3 Per-Monitor Items

(IDs WDM-01–03, GMM-01–05, FCW-01–05, ESA-01–04, AGM-01–05, ERM-01–04, SCEM-01–06, as in the last ROADMAP block.)

GMM-05 is the new **Regulatory wording audit** item reflecting the commercial/regulatory addenda.

### 6.4 Homepage & Cross-Monitor Experience

(IDs HP-01–05, as previously listed.)

### 6.5 Platform-Level Patterns & Docs

(IDs PL-01–06, as previously listed.)

---

## 7. Sprint Structure (2026)

This sprint structure is recorded for context and planning:

- **Sprint 1 — Shared foundations + homepage**
  - SL-01, SL-02, SL-03, SL-04, SL-08, SL-09
  - HP-01, HP-02
  - PL-01
- **Sprint 2 — GMM as primary testbed**
  - GMM-01–05
  - Any remaining SL-05/SL-06 needed for GMM
- **Sprint 3 — FCW + SCEM**
  - FCW-01–05, SCEM-01–06
- **Sprint 4 — ESA + AGM + ERM**
  - ESA-01–04, AGM-01–05, ERM-01–04
- **Sprint 5 — Homepage OSINT + cross-monitor UX**
  - HP-03, HP-04, PL-02, PL-03, PL-04, PL-05
  - PL-06 (design-only, optional for later structural sprint)

Each sprint is run monitor-by-monitor (or pair-by-pair), using a shared per-monitor sprint checklist and a staging-first approach.

---
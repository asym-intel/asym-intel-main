# asym-intel — Site Rebuild Sprints 2026

## Overview

This document organises the Site Rebuild Specification into five implementation sprints. It is a working plan; priorities and estimates can be updated as work completes.

Sprints:
- Sprint 1 — Shared foundations + homepage
- Sprint 2 — GMM (Global Macro Monitor) as primary testbed
- Sprint 3 — FCW + SCEM (operational monitors)
- Sprint 4 — ESA + AGM + ERM (structural monitors)
- Sprint 5 — Homepage OSINT surfaces + cross-monitor UX

IDs below refer to items defined in ROADMAP.md (SL-*, GMM-*, FCW-*, ESA-*, AGM-*, ERM-*, SCEM-*, HP-*, PL-*).

---

## Sprint 1 — Shared Foundations + Homepage

**Goal:** Establish shared components and rules that affect all monitors and the homepage, so later monitor work can reuse proven patterns.

Includes:
- SL-01 — Cross-Monitor Flags shared component (HTML/CSS/JS) and integration into all 7 Dashboards + Living Knowledge.
- SL-02 — Shared triage strip layout/classes and basic styling across all monitors.
- SL-03 — Confidence badge system distinct from severity (styles + helpers) and refactor across monitors.
- SL-04 — Signal panel white-text rule enforcement (remove muted/secondary overrides on accent panels).
- SL-08 — Validator checks: nav/heading match, no orphan sections, no severity misuse, min font-size, source patterns.
- SL-09 — Monitor accent colour tokens aligned between homepage and monitors, defined at global root.
- HP-01 — Homepage visual spec implementation (monitor strip, three-zone surface split, featured-article stripe, report-card grid).
- HP-02 — Homepage value statement + routing cues (Triage now / This week’s analysis / Structural pipelines / Raw signal).
- PL-01 — Update section-naming-registry.md using final Q11 tables from all 7 monitors.

Pilot surfaces:
- Shared library: test on WDM first.
- Homepage: implement fully.

---

## Sprint 2 — GMM (Global Macro Monitor) Testbed

**Goal:** Prove the triage + delta + nav + evidence pattern end-to-end on GMM as the first fully rebuilt monitor.

Includes:
- GMM-01 — Build triage strip (KPI + Weekly Signal + Tail Risk/structural snapshot + primary delta + key threshold).
- GMM-02 — Consolidate delta layers (single primary delta; structural vs episodic labelling).
- GMM-03 — Fix nav/heading mismatches; add Tail Risk nav entry; remove near-empty nav targets.
- GMM-04 — Apply inline sources and encoded-systems pattern (MATT etc.).

Supporting shared work (if not fully completed in Sprint 1):
- SL-05 — Encoded-systems helper (code + meaning) and application to GMM where needed.
- SL-06 — Inline source-link pattern (renderer + HTML) replacing “Source →” blocks.

Pilot monitor:
- macro-monitor (GMM) only.

---

## Sprint 3 — FCW + SCEM (Operational Monitors)

**Goal:** Apply the rebuilt pattern to the most operational monitors, where clarity, attribution, and emotional register matter most.

### FCW (fimi-cognitive-warfare)

Includes:
- FCW-01 — Triage strip with clear campaign structural snapshot and “Top Campaigns This Issue”.
- FCW-02 — Remove or repurpose “All Operations” if persistently near-empty; ensure single primary delta.
- FCW-03 — Fix nav/heading mismatches and anchor-ID issues.
- FCW-04 — Replace block “Source →” with inline sources; fix confidence vs severity (no amber CONFIRMED).
- FCW-05 — Apply encoded-systems helper to codes; ensure in-situ explanations.

### SCEM (conflict-escalation)

Includes:
- SCEM-01 — Triage strip (KPI + Lead Signal + GEI snapshot + primary delta).
- SCEM-02 — Distinguish structural roster/indicators from episodic deltas; Conflict Overview clearly structural.
- SCEM-03 — Fix nav/heading mismatches; add nav for Conflict Overview roster.
- SCEM-04 — Apply encoded-systems helper to F-flags; strengthen in-situ explanations.
- SCEM-05 — Decide and implement SCEM emotional register and SCEM accent vs --critical collision rule.
- SCEM-06 — Apply inline sources and shared confidence vs severity rules.

Pilot order within Sprint 3:
1. FCW first (lighter structural change).
2. SCEM second (heavier encoded-system and emotional-register work).

---

## Sprint 4 — ESA + AGM + ERM (Structural Monitors)

**Goal:** Apply the rebuilt pattern to structurally heavy monitors that focus on scorecards, pipelines, and multi-dimensional risk.

### ESA (european-strategic-autonomy)

Includes:
- ESA-01 — Triage strip (KPI + lead + autonomy snapshot + primary delta).
- ESA-02 — Clarify EU-level vs Member State structural split and routing to Living Knowledge.
- ESA-03 — Fix nav/heading mismatches (Autonomy Scorecard, Member States, Cross-Monitor).
- ESA-04 — Inline sources and mobile font-size confirmation for delta section.

### AGM (ai-governance)

Includes:
- AGM-01 — Implement composed triage strip as per AGM review.
- AGM-02 — Consolidate Top Items vs Top Movers.
- AGM-03 — Align nav labels (Delta Strip, EU AI Act, Cross-Monitor) with headings/registry.
- AGM-04 — Inline sources for structural panels (Risk Heat, Country Watch, Market Concentration); minimal confidence/verification badges.
- AGM-05 — “Thresholds & Inflection Points” micro-section (EU AI Act and similar cliffs).

### ERM (environmental-risks)

Includes:
- ERM-01 — Triage strip (KPI + lead + planetary boundary/tipping snapshot + primary delta).
- ERM-02 — Clarify multi-boundary and tipping-system structure across Dashboard vs Living Knowledge.
- ERM-03 — Nav alignment and inline sources for structural panels.
- ERM-04 — Apply shared empty-state design where data is accumulating.

Pilot order within Sprint 4:
1. AGM (strongest existing structure, detailed review).
2. ESA.
3. ERM.

---

## Sprint 5 — Homepage OSINT Surfaces + Cross-Monitor UX

**Goal:** Complete the homepage as a cross-monitor OSINT surface and tighten cross-monitor journeys and platform-level patterns.

Includes:
- HP-03 — Homepage “Today’s Raw Signal (Chatter)” widget (top-5 cross-monitor, clearly badged pre-synthesis).
- HP-04 — “What’s new this week” aggregate across monitors (simple structural movement summary).
- PL-02 — Design and implement empty-state / data-accumulating pattern across relevant charts/sections.
- PL-03 — Specify cross-monitor linkback phrasing and where it is allowed (flags and/or structural panels).
- PL-04 — Update ARCHITECTURE, DECISIONS, ROADMAP to reflect implemented patterns and Site Rebuild Spec.
- PL-05 — Define and document a credit-saving workflow (what is Computer-led vs Human+Computer vs Manual) in ARCHITECTURE/COMPUTER docs.

Optional design-only (for a later structural sprint):
- PL-06 — Draft high-level cross-monitor comparison view spec.

Pilot surfaces:
- Homepage work can be staged independently.
- Cross-monitor linkbacks can be piloted on a small set of high-signal relationships (e.g. WDM↔FCW, GMM↔FCW, AGM↔ESA) before being generalised.

---

## Notes

- This sprint plan is derived from the Site Rebuild Specification and ROADMAP implementation block discussed in April 2026.
- Priorities (P1–P3) and estimates for each ID remain in ROADMAP.md; use that file as the canonical source for effort and sequencing.
- Each sprint should be run with a single-monitor pilot first before propagating patterns across monitors.

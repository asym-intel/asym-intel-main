---
title: "Methodology — Strategic Conflict & Escalation Monitor"
description: "What the Strategic Conflict & Escalation Monitor tracks, why it uses a deviation-over-level framework, and what its outputs mean."
date: 2020-01-01
monitor: "conflict-escalation"
type: "methodology"
draft: false
---

## Overview

The Strategic Conflict & Escalation Monitor tracks the trajectory of armed conflicts and military escalation risks across a defined roster of active and latent conflicts. Its defining analytical principle is **deviation over level**: an anomalous spike in a low-intensity context is more significant than a sustained high level in a familiar one. The framework is designed to surface early-warning signals even when absolute indicator levels are not extreme.

This monitor functions as a spoke in the [Asymmetric Intelligence hub-and-spoke architecture](https://asym-intel.info). It receives FIMI-coded signals from the [Global FIMI & Cognitive Warfare Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/) and feeds escalation context to the [European Geopolitical & Hybrid Threat Monitor](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html), the [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html), and the [Global Environmental Risks & Planetary Boundaries Monitor](https://asym-intel.info/monitors/environmental-risks/dashboard.html).

---

## 01 · What This Monitor Tracks

The monitor covers a **defined roster of 8–12 active or latent conflicts** at any time. The roster is selective, not exhaustive — analytical depth over breadth. Conflicts are added when independently verifiable signals cross a dual-indicator threshold across two consecutive weekly cycles, and retired when all tracked indicators return to normal historical range for a sustained period.

The current roster comprises eight conflicts across six theatres: Eastern Europe, Middle East, Sahel/Horn of Africa, Southeast Asia, Caribbean, Central Africa, and two latent/strategic tensions in East Asia.

---

## 02 · The Scoring Framework

Each conflict is scored weekly across **six indicators**:

- **I1 — Rhetoric Intensity**: Official statements, state-media tone, military spokesperson language
- **I2 — Military Posture Changes**: Deployments, readiness alerts, force movements (secondary OSINT sourcing only — no primary satellite analysis)
- **I3 — Nuclear & Strategic Weapons Signalling**: Doctrine references, test activity, delivery-system movements. Individual state baselines apply separately for each nuclear-capable actor
- **I4 — Economic Warfare Steps**: Sanctions, energy cutoffs, asset freezes, trade restrictions
- **I5 — Diplomatic Channel Status**: Ambassador recalls, high-level meeting cancellations, back-channel activity where independently verifiable
- **I6 — Civilian Displacement Velocity**: Weekly rate of change in displacement figures from UNHCR, IOM, and OCHA — scored against data dates, not publication dates, to prevent phantom divergence

Each indicator is scored on two dimensions — current level and deviation from that conflict's historical baseline — producing a **Colour Band** (Green / Amber / Red / Contested) and a **Confidence Label**. The specific scoring rubrics and deviation thresholds are not published.

---

## 03 · Colour Bands

| Band | Meaning |
|---|---|
| **Green** | Within normal historical range for this conflict |
| **Amber** | Elevated above baseline — monitor closely |
| **Red** | Anomalous spike — early-warning signal |
| **Contested** | Baseline data insufficient; score is provisional |

Negative deviations (de-escalation below baseline) are noted in the narrative. They are assessed for premature de-escalation signal patterns rather than triggering colour-band alerts.

---

## 04 · Why Deviation Over Level

Absolute intensity levels are poor early-warning signals in conflicts with persistently high baselines. A Level 4 military posture in an active war theatre may be unremarkable; the same reading in a historically quiet border dispute is analytically significant. By anchoring scores to each conflict's own historical baseline, the monitor surfaces genuine structural changes regardless of the absolute intensity of the context.

This approach also prevents the common analytical error of habituation — treating a persistent high level as the new normal and missing the moment when even that elevated baseline begins to shift.

---

## 05 · Anti-Disinformation Framework

Four disinformation tactic filters are applied to all scoring, drawn from the methodology shared with the Global FIMI & Cognitive Warfare Monitor:

- **F1 — Atrocity Amplification**: Coordinated amplification of civilian harm claims without Tier 1 verification
- **F2 — False-Flag Seeding**: Attribution claims lacking forensic corroboration appearing in actor-aligned outlets first
- **F3 — Capability Theatre**: Performative demonstrations of military capability without operational intent
- **F4 — Premature De-Escalation Signals**: Official claims of ceasefire or breakthrough not independently verified, potentially designed to reduce external pressure

When any F-flag is applied, the affected indicator is scored at the **verified level**, not the claimed level. The flag and the claimed level are both noted in the narrative.

---

## 06 · Source Standards

Sources are assessed on a tiered hierarchy. **Tier 1** sources (UN agencies, IAEA, OSCE, peer-reviewed conflict datasets) provide the ground truth for scoring. **Tier 2** sources (established OSINT outlets, quality national-security journalism) provide corroboration. **Tier 3** sources (official government statements, state media) are used for triage and context only — never accepted as ground truth regardless of the authority of the source.

A presidential statement is a signal, not a fact.

---

## 07 · Confidence Labels

Each scored entry carries one of five confidence labels: **Confirmed** (two or more independent Tier 1 sources), **Probable** (Tier 1 plus corroborating Tier 2), **Possible** (single Tier 2, no Tier 1 contradiction), **Unverified** (Tier 3/4 only), or **Contested** (conflicting accounts across equivalent-tier sources).

---

## 08 · What This Monitor Is Not

- **Not a real-time tracker.** Published weekly; intra-week events are not scored until the next cycle
- **Not based on classified sources.** All sourcing is open-source; attribution confidence is structurally limited for actors with strong operational security
- **Not exhaustive.** Conflicts not on the roster receive no coverage. Inclusion criteria are transparent and published; selection is not neutral
- **Not providing primary satellite analysis.** I2 (Military Posture) relies on secondary reporting from established OSINT outlets

---

## 09 · Output Format

Each weekly edition produces:

1. **Escalation Status cards** — one per conflict, with current trajectory (Escalating / Stable / De-escalating / Contested)
2. **Scoring table** — all active conflicts × 6 indicators, with Colour Band and Confidence Label (Level, Baseline, and Deviation values are not published individually)
3. **Weekly Update** — editorial narrative with lead signal, per-conflict summaries, and F-flag analysis where applied
4. **Cross-Monitor Signals** — items relevant to hub and spoke monitors
5. **Roster Watch** — conflicts approaching inclusion or retirement threshold

---

## 10 · Companion Monitors

| Monitor | Role |
|---|---|
| [FIMI & Cognitive Warfare](https://asym-intel.info/monitors/fimi-cognitive-warfare/) | Hub — provides F1–F4 disinformation coding; receives conflict narrative context |
| [European Geopolitical & Hybrid Threat](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html) | Spoke — receives I2/I5 escalation signals for European theatre conflicts |
| [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html) | Spoke — receives election-period conflict escalation signals |
| [Global Environmental Risks](https://asym-intel.info/monitors/environmental-risks/dashboard.html) | Spoke — receives I6 displacement and I4 resource-conflict signals |
| [Macro Monitor](https://asym-intel.info/monitors/macro-monitor/dashboard.html) | Spoke — receives I4 economic warfare and sanctions signals |
| [AI Governance](https://asym-intel.info/monitors/ai-governance/dashboard.html) | Spoke — receives signals where conflict intersects AI infrastructure or autonomous weapons |

---


## 11 · Persistent Data

The SCEM maintains the following baseline data week-to-week:

- **Conflict roster** — all active roster entries carry forward. Removal from the Active Roster requires two consecutive weekly cycles with no new Tier 1–2 documented activity and an explicit editorial note.
- **Indicator scores** — all six indicator readings (I1–I6) for each conflict carry forward from the previous week. Changes require primary-source evidence at Tier 1–2 level. The prior week's score is always displayed alongside the current score to make deviation visible.
- **Historical baselines** — each conflict's median indicator values (established over the first 12 observation cycles) are locked once set. Baseline revision requires a versioned methodology update.
- **F-flag history** — once an F-flag (F1 False-Flag, F2 Disinformation, F3 Access Denial, F4 Atrocity Inflation) is applied to an indicator reading, it is retained in the record for that cycle even after the claim is clarified. The correction is noted; the original flag is not erased.
- **Colour band trajectory** — RED/AMBER/GREEN band assignments and trajectory arrows (↑↓→) are carried forward and updated only when indicator movement justifies reclassification.

The full archive of published weekly briefs is available at [asym-intel.info/monitors/conflict-escalation/](https://asym-intel.info/monitors/conflict-escalation/).

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-30 | Initial publication |

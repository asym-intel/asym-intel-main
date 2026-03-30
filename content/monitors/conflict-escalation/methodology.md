---
title: "Methodology — Strategic Conflict & Escalation Monitor"
description: "How the Strategic Conflict & Escalation Monitor scores armed conflict trajectories and military escalation risks using a dual-dimension Level/Baseline/Deviation framework."
date: 2026-03-30
monitor: "conflict-escalation"
type: "methodology"
draft: false
---

## Overview

The Strategic Conflict & Escalation Monitor tracks the trajectory of armed conflicts and military escalation risks across a defined conflict roster. Its defining methodological principle is **deviation over level**: an anomalous spike in a low-intensity context is analytically more significant than a sustained high level in a high-intensity one. The framework is designed to trigger early-warning signals even when absolute indicator levels are not extreme.

This monitor functions as a spoke in the [Asymmetric Intelligence hub-and-spoke architecture](https://asym-intel.info). It receives FIMI-coded signals from the [Global FIMI & Cognitive Warfare Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/) and feeds escalation context to the [European Geopolitical & Hybrid Threat Monitor](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html), the [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html), and the [Global Environmental Risks & Planetary Boundaries Monitor](https://asym-intel.info/monitors/environmental-risks/dashboard.html).

---

## 1. Conflict Roster

### Definition

The monitor tracks a defined roster of **8–12 active or latent conflicts** at any time. The roster is not exhaustive — it is selective, designed to ensure analytical depth over breadth.

### Inclusion criteria

A conflict enters the roster when **two or more** of the following conditions are met for two consecutive weekly cycles:

- Civilian displacement velocity exceeds the actor-context historical median by +1.5 or more
- Military posture change is independently confirmed by two or more Tier 1/2 sources
- Rhetoric intensity reaches Level 3 or above with a deviation of +1.5 or more from baseline
- Nuclear or strategic weapons signalling is recorded at any level by a Tier 1 source

### Retirement criteria

A conflict is retired from the active roster when:

- All six indicators score Green band for eight consecutive weeks, **and**
- No Tier 1/2 source reports active hostilities for 90 days

Retired conflicts move to a **Dormant Watch** list and are not scored weekly but are monitored for re-entry triggers.

### Baseline flag for new conflicts

Conflicts added to the roster with fewer than 12 months of historical data per indicator–actor pair are flagged **Contested Baseline** across all indicators until the 12-month minimum is reached. This flag appears in the scoring table and narrative.

---

## 2. Dual-Dimension Scoring Framework

Every indicator is scored on two independent dimensions each week:

| Dimension | Scale | Definition |
|---|---|---|
| **Level** | 1–5 | Current intensity of the indicator, assessed against a standardised rubric for that indicator type |
| **Baseline** | 1–5 | Rolling 18-month median for that indicator–actor–context pair |
| **Deviation** | −3 to +3 | Level minus Baseline, capped at ±3 |

All three values are published in the weekly scoring table alongside a Colour Band and Confidence Label.

---

## 3. Baseline Construction

### Window and method

- **Window:** 18 months of weekly observations per indicator–actor pair
- **Method:** Rolling median with interquartile range trimming (IQR ×1.5 outlier exclusion)
- **Update frequency:** Baselines are recalculated every 3 months, not continuously, to avoid baseline drift that could mask genuine trend shifts
- **Minimum data requirement:** 12 weekly observations required before a baseline is considered valid; below this threshold the entry is flagged Contested Baseline

### Structural break override

When a datable, externally verifiable structural break occurs — a coup, ceasefire, new actor entry, doctrine change — the analyst may reset the baseline window to start from the break date. This override must be:

1. Recorded in the methodology log with the break date and source
2. Noted in the narrative for the week it is applied
3. Reflected in the scoring table with a footnote until the new baseline reaches the 12-observation minimum

### Actor-specificity

Baselines are computed per **indicator–actor–context triplet**, not globally. North Korea's rhetoric baseline is not compared to Kazakhstan's. Each nuclear posture state (P5 members individually, India, Pakistan, Israel, DPRK) has its own nuclear signalling baseline. This specificity is the core analytical advantage of the framework.

---

## 4. Indicators

Six indicators are scored weekly for each conflict on the roster.

### I1 — Rhetoric Intensity
Official statements, state-media tone, and military spokesperson remarks. Assessed from Tier 1/2 sources with actor-specific baseline. Social media and Tier 3/4 sources may triage but cannot constitute the scored assessment.

**Level rubric:**
1. Diplomatic/routine | 2. Elevated tension language | 3. Explicit threat framing | 4. Direct ultimatum or mobilisation language | 5. Declared hostility or imminent-attack framing

### I2 — Military Posture Changes
Satellite-observable deployments, readiness alerts, and force movements. Primary sourcing: secondary analysis from Middlebury Institute, CSIS iDeas Lab, UNOSAT, Bellingcat, and equivalent Tier 1/2 OSINT outlets. Direct primary satellite analysis is not conducted; AI-assisted triage is used to detect relevant secondary reporting velocity only.

**Level rubric:**
1. Routine posture | 2. Elevated readiness or repositioning | 3. Significant deployment or exercise near contested zone | 4. Forward deployment with offensive capability | 5. Attack posture or active engagement

### I3 — Nuclear & Strategic Weapons Signalling
Doctrine references, test activity, delivery-system movements, and declared posture changes. Individual state baselines apply for all P5 members and for India, Pakistan, Israel, and DPRK. A **Doctrine Shift** flag is applied separately from rhetoric spikes — a shift in written doctrine is structurally distinct from a speech act and must be coded differently.

**Level rubric:**
1. No signalling | 2. Rhetorical reference to nuclear doctrine | 3. Explicit doctrine invocation or alert status change | 4. Delivery system movement or test activity | 5. Declared readiness change or test conducted

### I4 — Economic Warfare Steps
Sanctions, energy cutoffs, asset freezes, and trade restrictions. Baseline is computed by geopolitical relationship tier (allied, adversarial, neutral), not by individual actor pair, except where actor-specific history warrants differentiation (e.g., Russia–EU energy).

**Level rubric:**
1. No measures | 2. Targeted individual/entity sanctions | 3. Sector-level sanctions or partial energy restriction | 4. Comprehensive sanctions package or full energy cutoff | 5. Financial system exclusion or total trade embargo

### I5 — Diplomatic Channel Status
Ambassador recalls, high-level meeting cancellations, back-channel activity (where verifiable), and multilateral forum participation. Baseline by relationship type (allied, adversarial, neutral, mediated).

**Level rubric:**
1. Normal diplomatic activity | 2. Reduced high-level contact | 3. Ambassador recall or major meeting cancellation | 4. Diplomatic mission suspended or expelled | 5. Full severance of diplomatic relations

### I6 — Civilian Displacement Velocity
Weekly rate of change in displacement figures from UNHCR, IOM, and OCHA. Baseline by conflict zone and historical displacement pattern.

**Data lag note:** UNHCR/IOM/OCHA figures carry a typical reporting lag of 2–6 weeks. Displacement scores are annotated with the source data date, not the publication date, to prevent phantom divergence from military posture or rhetoric indicators. A displacement spike contemporaneous with a rhetoric spike that is scored in the same week should be treated with caution unless the data dates align.

**Level rubric:**
1. Stable or decreasing displacement | 2. Marginal increase (<10% WoW) | 3. Moderate increase (10–30% WoW) | 4. Significant increase (30–100% WoW) | 5. Mass displacement event (>100% WoW or >50,000 new displaced in week)

---

## 5. Colour Bands and Thresholds

| Band | Deviation condition | Meaning |
|---|---|---|
| **Green** | Deviation within ±0.5 | Within normal historical range |
| **Amber** | Deviation +1.0 to +2.0 | Elevated above baseline; monitor closely |
| **Red** | Deviation ≥ +2.5 | Anomalous spike; early-warning signal |
| **Contested** | Baseline data insufficient | Score is provisional; treat with reduced confidence |

Negative deviations (de-escalation below baseline) are noted in the narrative but do not trigger colour-band alerts. They are assessed for premature de-escalation signal patterns (see §7).

---

## 6. Confidence Labels

Each scored entry carries a confidence label derived from OSINT verification standards:

| Label | Meaning |
|---|---|
| **Confirmed** | Independently corroborated by two or more Tier 1 sources |
| **Probable** | One Tier 1 source plus corroborating Tier 2 source |
| **Possible** | Single Tier 2 source; no contradiction from Tier 1 |
| **Unverified** | Tier 3/4 only; no Tier 1/2 corroboration available |
| **Contested** | Conflicting accounts across sources of equivalent tier |

Confidence labels apply to the scored entry as a whole, not to individual sub-components. Where different sub-components carry different confidence levels, the lowest confidence label applies to the entry.

---

## 7. Anti-Disinformation Framework

The monitor applies four specific disinformation tactic filters drawn from the methodology shared with the [Global FIMI & Cognitive Warfare Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/):

**F1 — Atrocity Amplification:** Coordinated amplification of civilian harm claims without Tier 1 verification. Flag when the same claim appears across Tier 3/4 sources within a short window without independent sourcing.

**F2 — False-Flag Seeding:** Claims attributing attacks to a party inconsistent with established capability or posture. Flag when attribution claims lack forensic corroboration and appear in actor-aligned outlets first.

**F3 — Capability Theatre:** Performative demonstrations of military capability designed to signal without operational intent. Distinguish from genuine posture change by cross-referencing against satellite analysis and deployment data.

**F4 — Premature De-Escalation Signals:** Official claims of ceasefire, withdrawal, or diplomatic breakthrough that are not independently verified and may serve to reduce external pressure or monitoring. Apply heightened scrutiny to any negative deviation in rhetoric or posture that is sourced solely from the actor making the claim.

When any of F1–F4 is flagged, the affected indicator is scored at the *verified level*, not the claimed level. The flag and the claimed level are noted in the narrative.

---

## 8. Source Hierarchy

| Tier | Source type | Use |
|---|---|---|
| **T1** | UN agencies (UNHCR, OCHA, UNSC reporting), IAEA, OSCE, peer-reviewed conflict studies | Ground-truth for scoring; Confirmed/Probable confidence |
| **T2** | Established OSINT outlets (Bellingcat, CSIS iDeas Lab, Middlebury, UNOSAT, Crisis Group, ACLED), quality national security journalism (Reuters, AP, BBC Verify) | Corroboration; Probable confidence with T1 support |
| **T3** | Official government statements, state media, international NGO reporting | Triage and context; never accepted as ground truth without T1/T2 corroboration; treated as Tier 3 regardless of source prominence |
| **T4** | Social media, Telegram channels, unverified video, crowd-sourced mapping | Velocity detection and hypothesis generation only; always labelled Unverified |

Official statements and social-media-derived signals are treated as **Tier 3/4** irrespective of the authority of the source. A presidential declaration is a signal, not a fact.

---

## 9. AI-Assisted Workflow

AI is used for triage functions only. All AI outputs are treated as preliminary hypotheses; human analysts apply the Level/Baseline/Deviation scoring.

**Permitted AI triage functions:**
- Detecting velocity spikes in conflict-related terms across multilingual sources
- Identifying coordinated amplification patterns consistent with F1–F4 disinformation tactics
- Monitoring secondary source volume for satellite-image analysis relevant to I2
- Summarising UNHCR/OCHA displacement data releases for I6 scoring

**Not permitted:**
- Direct Level scoring without analyst review
- Attribution of attacks or actors without Tier 1/2 corroboration
- Baseline calculation (performed by defined quantitative method only)

---

## 10. Cross-Monitor Integration

| Signal type | Receiving monitor | Mechanism |
|---|---|---|
| FIMI tactics detected in conflict narrative | [FIMI & Cognitive Warfare Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/) | Cross-tag in narrative; hub receives conflict context |
| Escalation affecting European theatre | [European Geopolitical & Hybrid Threat Monitor](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html) | Cross-link in weekly brief |
| Election-period escalation risks | [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html) | Cross-tag where conflict intersects with electoral interference |
| Environmental drivers of conflict (water, food, displacement) | [Global Environmental Risks Monitor](https://asym-intel.info/monitors/environmental-risks/dashboard.html) | Cross-tag in I6 and I4 entries |
| Macro financial contagion from conflict | Ramparts Global Macro Monitor | Cross-tag in I4 (economic warfare) entries |

---

## 11. Output Format

Each weekly update produces:

1. **Scoring table** — all active conflicts × 6 indicators, with Level, Baseline, Deviation, Colour Band, and Confidence Label
2. **Narrative summary** — highlights Red-band entries, explains deviation context, flags Contested Baseline entries, and applies the F1–F4 disinformation filter
3. **Escalation trajectory line** — one-sentence directional assessment per conflict (Escalating / Stable / De-escalating / Contested)
4. **Cross-monitor signals** — explicitly flagged items relevant to hub and spoke monitors

---

## 12. Scope Limitations

- **OSINT-only:** No classified sources. Attribution confidence is structurally limited for actors with strong operational security (e.g., cyber-enabled false flags, covert deployments).
- **Roster selection bias:** Conflicts on the roster receive analytical depth; conflicts not on it receive no coverage. The inclusion criteria are designed to be transparent and defensible, but selection is not neutral.
- **Satellite imagery:** No primary satellite analysis is conducted. The monitor relies on secondary reporting from established OSINT outlets. Capability theatre (F3) assessment is therefore dependent on the quality and timeliness of external satellite analysis.
- **Displacement data lag:** I6 scores reflect data dates, not publication dates. See §4 (I6) for detail.
- **Baseline instability for new conflicts:** Contested Baseline flag is applied until the 12-observation minimum is reached. Scores during this period are indicative only.
- **Nuclear signalling asymmetry:** States with strong deterrence cultures (France, UK) generate near-zero public signalling as baseline. Absence of signalling is not evidence of reduced capability or intent.

---

## Version history

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-30 | Initial publication |

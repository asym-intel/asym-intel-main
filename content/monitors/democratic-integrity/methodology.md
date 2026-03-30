---
title: "Methodology — World Democracy Monitor"
description: "How the monitor detects democratic backsliding using a five-tier source hierarchy, severity scoring rubric, and institutional integrity early-warning layer."
date: 2026-03-30
monitor: "democratic-integrity"
type: "methodology"
draft: false
---

Democratic breakdown today rarely arrives as a coup. It comes through lawfare, media capture, economic coercion, and digital manipulation that remain technically "legal" — and therefore largely invisible to traditional democracy indices until it is too late. This document explains how the World Democracy Monitor is built to detect it earlier.

## Purpose and Scope

The World Democracy Monitor provides a weekly risk picture of democratic backsliding and institutional resilience across a monitored set of countries and emerging risk cases. It is designed to sit *on top of* the major annual democracy indices — not to replace them — as a real-time institutional radar.

Most global democracy rankings update annually. They are indispensable for measuring long-term trajectories, but they only register change after months of quiet erosion. This monitor exists to fill that gap, tracking the leading indicators that precede index downgrades by 6–18 months.

The monitor tracks six dimensions:

- **Institutional hollowing** — court-packing, term-limit manipulation, emergency powers, lawfare
- **Economic coercion and oligarchization** — media, energy, finance
- **Election engineering** — rules, voter rolls, candidates, certification
- **AI-driven information operations**, censorship laws, shutdowns, and surveillance
- **Civil society and protest dynamics** — both repression and successful pushback
- **Cross-border autocratic model export** and transnational repression

## The Five-Tier Source Hierarchy

Every claim in the monitor is sourced to a specific primary source, organised into five tiers by proximity to ground truth. When Tier 3 or 4 sources directly contradict Tier 1 official claims, a Critical Friction Note is published explaining the discrepancy.

| Tier | Type | Role | Key Sources |
|------|------|------|-------------|
| **1** | Institutional & Diplomatic — *The "Official" View* | Stated policy, legislative texts, official election results | UN OHCHR, OSCE/ODIHR, Venice Commission, European Parliament |
| **2** | Quantitative Indices — *The "Benchmark" View* | Long-term scoring trends, global rankings, statistical backsliding measures | V-Dem (LDI, EDI), Freedom House, EIU Democracy Index, International IDEA Democracy Tracker (173 countries, 29 indices), RSF Press Freedom Index, Global Terrorism Index |
| **3** | Investigative & Independent Media — *The "Ground Truth"* | Corruption, suppression of dissent, grassroots movements | The Guardian, ProPublica, Haaretz, +972 Magazine, The Wire (India), El Faro (Latin America), Lawfare Media, IPI |
| **4** | Human Rights & Civic Oversight — *The "Accountability" View* | Detention logs, protest crackdowns, internet shutdowns | Amnesty International, HRW, CIVICUS Monitor, Access Now, CPJ, ISHR |
| **5** | Think Tanks & Strategic Analysis — *The "Expert" View* | Backsliding mechanics, institutional resilience, geopolitical drivers | Carnegie Endowment, Journal of Democracy, Chatham House, Brookings, Verfassungsblog, openDemocracy, compossible.blog |

## Country Status Classification

Every monitored country is assigned one of three status tiers, reviewed weekly. Status changes require corroboration from at least two independent primary sources from Tiers 2–4.

**Rapid Decay** — Active, documented deterioration in at least two institutional pillars (judiciary, press, civil service, civil society, elections, legislature). Severity scored 1–10.

**Recovery** — Net positive institutional trajectory after a period of documented decay. The severity score within this tier reflects residual fragility, not full democratic health.

**Watch List** — 2+ active leading indicators of democratic backsliding but not yet at Rapid Decay threshold. Each entry includes an explicit escalation trigger. Promoted to Rapid Decay when severity score exceeds 5.0 on two consecutive weekly assessments.

## Severity Scoring Rubric (1–10)

**Formula: Score = A + B + C + (2.5 − D)**

| Dimension | Description | Range |
|-----------|-------------|-------|
| **A — LDI Trajectory** | V-Dem LDI / Freedom House direction: 0 = stable/improving → 2.5 = collapse-speed | 0–2.5 |
| **B — Institutional Breadth** | Pillars under attack (judiciary, legislature, civil service, press, civil society, elections): 0 = 0–1 → 2.5 = all 6 | 0–2.5 |
| **C — Repression Severity** | Physical violence and imprisonment: 0 = none → 2.5 = mass killings/massacres | 0–2.5 |
| **D — Resilience (inverted)** | Courts, civil society, legislature pushing back — high resilience *lowers* the score: 0 = none → 2.5 = robust | 0–2.5 |

Direction arrows: ↑ worsening week-on-week · → stable · ↓ improving.

**The Resilience Paradox:** countries with functioning courts, civil society, and press score *lower* than countries at equivalent decay stages where those mechanisms have been captured — because active resilience genuinely constrains the trajectory. The United States (5.5) scores lower than Georgia (8.5) despite a larger V-Dem LDI decline, because the grand jury rejection of the Congressional indictment, federal courts blocking press restrictions, and active civil society all register as genuine resilience countervailing the decay.

## Institutional Integrity — Early Warning Layer

In addition to the reactive heatmap, the monitor tracks four institutional integrity signals that typically precede CIVICUS and Freedom House rating downgrades by 6–18 months, sourced from the [International IDEA Democracy Tracker](https://www.idea.int/democracytracker/home) (29 indices across Representation, Rights, Rule of Law and Participation) and V-Dem disaggregated sub-indicators:

- **Judicial independence** — court-packing, removal of judges, attacks on judicial review authority
- **Electoral administration integrity** — redistricting, voter roll manipulation, registration barriers, certification capture
- **Civil service politicisation** — replacement of career officials with political appointees, removal of due-process protections
- **Intelligence community misuse** — redirection of security apparatus toward domestic political targets, omission of electoral security threats from official assessments

## The Weekly Research Process

1. **Load baseline** — previous week's JSON is loaded. All scores and notes carry forward unless contradicted by new primary-source evidence.

2. **Primary source scan** — structured search covering all monitored countries plus three geographic zones requiring active scouting: Sub-Saharan Africa (Carnegie Endowment Africa, CIVICUS Monitor, Atlantic Council Africa), Latin America (Amnesty International Americas, Global Terrorism Index), and institutional integrity signals (IDEA Democracy Tracker, V-Dem disaggregated data). Watch List additions are identified proactively, not just reactively.

3. **Source verification and tier assignment** — each new claim is assigned a tier (1–5) and cross-checked against at least one independent source. Critical Friction Notes are created where Tier 1 official claims are directly contradicted by Tier 3 or 4 evidence. No claim based solely on a single Tier 5 source is used to change a country's status classification.

4. **Data merge and scoring update** — severity scores updated where primary-source evidence justifies change. Status reclassifications require corroboration from at least two independent Tier 2–4 sources. Monthly trend values recalculated from the 4-week rolling history.

5. **Weekly Intelligence Brief** — synthesis of up to 10 numbered analytical items covering all monitored dimensions. Named reports hyperlinked to primary sources. Minimum 600 words; target 900–1,200 words.

6. **Publication** — dashboard deployed to permanent URL; brief published to [asym-intel.info/monitors/democratic-integrity/](https://asym-intel.info/monitors/democratic-integrity/) every Monday morning.

## Regional Mimicry Tracking

The Legislative Watch tags each entry with its regional mimicry pattern — identifying which earlier law it copies and where it is spreading. This produces a traceable autocratic learning network: Russia's 2012 foreign agent law → Hungary 2017 → Georgia 2025 → Serbia (pending) → Uganda (proposed) → Kazakhstan (NGO disclosure provisions).

## Limitations

- **Does not replace V-Dem, Freedom House, or IDEA.** The annual indices provide the longitudinal quantitative baseline. This monitor uses them as a structural foundation and tracks what happens in the 51 weeks between their updates.
- **Does not cover all countries.** The heatmap focuses on countries in active acute phases. Countries outside both the heatmap and Watch List are not assessed as safe — they are outside the current monitoring scope.
- **Severity scores are analyst-assigned, not algorithmically derived.** The rubric provides a consistent framework but sub-dimension values reflect editorial judgment informed by primary sources. Two analysts may score the same country within a ±1 range.
- **Does not cover occupied territories as part of their occupying state's score.** Consistent with Freedom House and V-Dem methodology.
- **Weekly updates cannot be exhaustive.** Gradual deterioration in mid-range countries may take several weeks to register if no acute primary-source event occurs in the scan window.

## The Analytical Ecosystem

The World Democracy Monitor is part of the [Asymmetric Intelligence](https://asym-intel.info) platform:

- **[World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html)** — democratic resilience and institutional integrity (this monitor)
- **[European Geopolitical & Hybrid Threat Monitor](https://www.perplexity.ai/computer/a/european-geopolitical-hybrid-t-ONqW4DtqTFSe2IHZUBWnfw)** — external pressure vectors on European security and cohesion
- **[Global FIMI & Cognitive Warfare Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html)** — the information operations layer that connects both
- **[compossible.blog](https://compossible.blog)** — long-form analytical development of the underlying concepts

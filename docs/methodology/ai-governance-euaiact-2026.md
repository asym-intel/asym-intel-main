---
title: "AGM Enhancement Addendum — EU AI Act 2026 Compliance Phase & GPAI Code of Practice"
monitor: ai-governance
version: 1.0
date: 2026-04-02
author: Peter Howitt / Asymmetric Intelligence
classification: Internal — not for publication
---

# AGM Enhancement Addendum
## EU AI Act 2026 Compliance Phase, GPAI Code of Practice, and Frontier Capability Calibration

---

## 1. Purpose

This addendum extends the AGM internal methodology (`ai-governance-full-5.md`) with:

1. **EU AI Act 7-layer tracker calibration** — updated deadlines and compliance status as of Q1 2026
2. **GPAI Code of Practice** — final text analysis and M09 scoring implications
3. **Frontier capability calibration** — how to assess model capability jumps in 2026 using public benchmarks
4. **AISI Pipeline update** — institutional changes at UK and US AI Safety Institutes since mid-2025
5. **Ciyuan Standards Vacuum** — updated trigger criteria for 2026
6. **M07 Risk Vector calibration** — current ratings baseline and update triggers
7. **Cross-monitor routing updates** — AI Act enforcement intersecting FIMI, democratic regression, and macro conditions

Read this addendum at **Step 0B**, after loading `persistent-state.json` and before launching the 4 parallel research agents.

---

## 2. EU AI Act 7-Layer Tracker — 2026 Status and Deadlines

The EU AI Act entered into force on **1 August 2024**. As of Q1 2026, the following layer-specific deadlines are active or imminent. Load this table as the baseline for M09 Law & Litigation.

### Layer-by-Layer Status (Q1 2026 Baseline)

| Layer | Description | Status | Next Deadline |
|---|---|---|---|
| **Layer 1: AI Act Text** | Full text in Official Journal | Confirmed — OJ L 2024/1689 | Baseline — no update needed |
| **Layer 2: Delegated/Implementing Acts** | Commission acts on specific obligations | In progress — several acts in consultation | High-risk AI system classification list expected Q2 2026 |
| **Layer 3: Harmonised Standards** | CEN-CENELEC JTC 21 standardisation mandate | **Standards Vacuum active** — no harmonised standards in Official Journal as of Q1 2026; drafts in progress | Standards Vacuum flag: ACTIVE |
| **Layer 4: GPAI Code of Practice** | Voluntary but compliance-relevant code for general-purpose AI | **First general release published** (see section 3 below) | Full Code finalisation expected Q2 2026 |
| **Layer 5: National Competent Authorities** | Member state NCAs must be designated | Most EU member states have designated or designated-in-progress NCAs | NCA enforcement capacity — track monthly |
| **Layer 6: AI Office Supervisory** | EU AI Office direct supervision of GPAI models | AI Office operational; first supervisory opinions expected 2026 | First supervisory decision expected H1 2026 |
| **Layer 7: Digital Omnibus Trilogue** | Omnibus package amending AI Act liability provisions | **Critical — Omnibus vote in EP Q1 2026; outcome affects AI Liability Directive** | Monitor EP plenary outcomes |

### Standards Vacuum Flag — ACTIVE (as of Q1 2026)

**Trigger conditions:** All three of the following are met:
1. Compliance obligation deadline within 90 days ✓ (high-risk AI system obligations apply from August 2026)
2. Harmonised standards not yet in Official Journal ✓
3. No implementing guidance issued to bridge the gap ✓

**Score implication:** Standards Vacuum flag must be included in M09 every issue. The flag status is `ACTIVE`. Do not downgrade to `MONITORING` until at least one harmonised standard is published in the Official Journal.

**Weekly tracking action:** Check the CEN-CENELEC JTC 21 standards tracker at `artificialintelligenceact.eu/standard-setting-overview` every issue. Document the number of standards in draft vs. published.

---

## 3. GPAI Code of Practice — First General Release

The **GPAI (General-Purpose AI) Code of Practice** process was established under Article 56 of the EU AI Act. The first draft was circulated in late 2024; subsequent drafts emerged in Q1 2025. As of Q1 2026, a working text is in the final consultation phase.

### Key provisions to track weekly (M05 and M09):

**Transparency obligations:** GPAI model providers must document training data, compute usage, energy consumption, and capabilities. The transparency provisions are the most directly enforceable in the near term.

**Systemic risk assessment:** The Code establishes criteria for "systemic risk" GPAI models — those trained on compute above a threshold (initially 10²⁵ FLOPs, subject to revision). Models above this threshold face enhanced obligations including adversarial testing and incident reporting.

**Weekly trigger for M09:** Any lab announcing a new model that may exceed the systemic risk compute threshold is an **immediate M09 item**. Apply the 7-layer tracker Layer 4 update.

**Ciyuan Standards Vacuum intersection:** If a Chinese lab releases a model that would meet the GPAI systemic risk threshold under EU definitions but the model is not subject to EU jurisdiction, flag as a **Ciyuan Standards Vacuum trigger** — the EU framework creates obligations for EU-accessible models but cannot reach Chinese state-trained models distributed via API.

### GPAI Code – Lab Compliance Status Tracker

Maintain this table in `persistent-state.json` under `gpaiCompliance`:

| Lab | Self-declared GPAI signatory? | Transparency report published? | Compute disclosure? | AGM Assessment |
|---|---|---|---|---|
| OpenAI | Yes | System cards published | Partial | Monitor for completeness |
| Anthropic | Yes | RSP / system cards | Partial | Monitor for completeness |
| Google DeepMind | Yes | Gemini system cards | Partial | Monitor for completeness |
| Meta AI | Yes | Llama model cards | Partial | Open-weight compliance ambiguity |
| Mistral | Yes | Limited | Limited | EU-based; higher NCA scrutiny expected |
| xAI (Grok) | No formal commitment | Minimal | None | Flag as non-compliant track |
| Chinese labs (general) | No | No | No | Ciyuan Standards Vacuum flag — standing |

---

## 4. Frontier Capability Calibration — 2026 Benchmark Framework

### The Core Problem

The AGM is responsible for tracking capability jumps at M02 (Model Frontier). The challenge in 2026 is **benchmark saturation** — leading frontier models have saturated most public academic benchmarks (MMLU, HumanEval, GSM8K), making benchmark scores an unreliable capability signal. The following protocol upgrades M02 for 2026 conditions.

### Capability Jump Signals (in priority order)

1. **Novel capability domain crossing:** A model demonstrating for the first time a capability it could not perform at any previously tested threshold. Examples: autonomous multi-step scientific experiment design; passing bar exams in multiple jurisdictions simultaneously; generating functional novel protein structures without AlphaFold scaffolding.

2. **Autonomous agent performance:** Scores on SWE-bench (software engineering), GAIA (general assistant), and RE-Bench (research engineering) are more meaningful than MMLU in 2026. Track these specifically.

3. **Compute frontier extension:** Any model announced with training compute above 10²⁶ FLOPs is a structural event — it enters GPAI systemic risk territory and triggers both M02 (capability) and M09 (regulation) entries simultaneously.

4. **Open-weight releases with permissive licences:** Apache 2.0 or equivalent releases of models at or near frontier capability are a different kind of signal — they change the governance landscape by making frontier-class capabilities available without accountability infrastructure. Flag every such release regardless of benchmark scores.

5. **Chinese lab releases (special protocol):** If a Chinese lab releases a model with limited third-party evaluation access (e.g., API-only, no weights), apply the **maximum epistemic caution** flag: `chineseLab: true, evaluationAccess: limited, capabilityAssessment: uncertain`. Do not infer capability from Chinese government or lab press releases alone — these are Tier 3 sources for capability claims.

### Science Drill-Down — Mandatory Weekly Checks (unchanged but clarified)

These four checks must run every issue regardless of news:

1. **AlphaFold Database:** Check for volume updates or new complex types at `alphafold.ebi.ac.uk`. A new protein class or structure type added to the database is an M06 item.
2. **OpenAI Preparedness Scorecard:** Any tier change at `deploymentsafety.openai.com` is an M02 + M07 item.
3. **Anthropic RSP:** Any ASL (AI Safety Level) change is an M02 + M07 + M10 item.
4. **DeepMind programmes:** AlphaFold, AlphaGenome, AlphaEvolve, WeatherNext, GNoME — any new release or capability announcement.

---

## 5. AISI Pipeline — Institutional Update (2025–2026)

The AISI (AI Safety Institute) landscape has changed materially since the original methodology was drafted.

### UK AI Security Institute (DSIT)

The UK AISI was rebranded to the **AI Security Institute** in early 2025, reflecting a shift in emphasis from safety evaluation to security-focused oversight. Track this rebranding in all M15 entries — the institutional mandate has changed.

**Personnel alert:** The rebranding was accompanied by leadership changes. Run the M15 AISI Pipeline scan against the current staff page at each issue — the research direction change means departures and new appointments carry higher significance than in a stable institutional period.

### US AISI (NIST)

The Trump administration's posture toward AI safety has diverged significantly from the Biden-era NIST AI Safety framework. As of Q1 2026:
- The 2023 Biden Executive Order on AI has been substantially rescinded
- NIST AI RMF 1.0 remains in effect but lacks executive enforcement mandate
- A new voluntary framework emphasising innovation over risk management is expected

**Scoring implication for M07 Governance Fragmentation:** US governance posture has shifted from `ELEVATED` toward `HIGH`. Update the M07 Governance Fragmentation vector if not already done. Rationale: the Biden-era US/EU alignment on AI safety has collapsed; the governance schism is now confirmed.

### EU AI Office

The EU AI Office is the primary regulatory body for GPAI model supervision under the AI Act. As of Q1 2026, the AI Office is operational but has issued no binding enforcement decisions. Track at `digital-strategy.ec.europa.eu/en/policies/ai-office`.

**First enforcement action trigger:** The AI Office's first supervisory decision (expected H1 2026) will be a landmark M09 + M10 item regardless of subject matter — it establishes the enforcement precedent for the entire GPAI oversight regime.

---

## 6. M07 Risk Vectors — 2026 Baseline Ratings

Load these as the current baseline in `persistent-state.json` under `riskVectors`. Update only when update rules are met.

| Vector | Rating | Confidence | Last Updated | Update Trigger |
|---|---|---|---|---|
| **Governance Fragmentation** | HIGH | Confirmed | 2026-03-30 | EU/US schism confirmed; any new US AI executive action |
| **Cyber Escalation** | ELEVATED | Confirmed | 2026-03-30 | CISA KEV additions; state-attributed AI-enabled attacks |
| **Platform Power** | HIGH | Confirmed | 2026-03-30 | Big Five hyperscaler concentration; M&A activity |
| **Export Controls** | ELEVATED | Confirmed | 2026-03-30 | H20 chip ban (Nvidia); watch for next tier of controls |
| **Disinfo Velocity** | ELEVATED | Probable | 2026-03-30 | AI-generated content in electoral contexts; synthetic media detection gap |

**Governance Fragmentation — HIGH justification:** EU AI Act enforcement is proceeding on an independent trajectory from both the US (deregulatory pivot) and China (Ciyuan state integration). No international governance convergence mechanism exists. The Council of Europe AI Treaty provides partial overlap but is soft-law only and not ratified by US/China.

**Export Controls — weekly mandatory check:** BIS Federal Register notices must be checked every issue regardless of news. Any new Entity List addition involving AI hardware, semiconductor equipment, or software constitutes an M07 update.

---

## 7. Concentration Index — M14 AI Power Structures

Maintain the 5-domain Concentration Index in `persistent-state.json` under `concentrationIndex`. Update when material changes occur.

| Domain | Current Rating | Primary Concentration Actor | Key Signal to Watch |
|---|---|---|---|
| **Compute/GPU** | Extreme | NVIDIA (>80% data centre GPU market) | Any AMD/Intel data centre GPU market share gain ≥5%; custom silicon scale-up by Google/Amazon/Microsoft |
| **Foundation Models** | High | OpenAI, Google, Anthropic, Meta | Open-weight releases reducing lock-in; Chinese labs closing capability gap |
| **AI Infrastructure** | High–Extreme | AWS, Azure, GCP | Behind-the-meter power agreements; nuclear PPA announcements |
| **AI Applications** | Moderate | Sector-specific leaders | Stealth deployment flags (M04) — track healthcare, legal, defence |
| **AI Safety/Oversight** | Low–Fragmented | No dominant actor | AI Office first enforcement action; AISI capacity development |

**Critical 2026 update:** Microsoft/OpenAI structural relationship (Microsoft holds ~49% revenue share via Azure deal) is the most concentrated foundation model + infrastructure combination. Any change to this relationship (renegotiation, equity restructuring, partnership dissolution) is an M14 + M03 item.

---

## 8. Cross-Monitor Signal Routing — 2026 Updates

| Signal | Route To | Trigger |
|---|---|---|
| AI-enabled FIMI operations (new capability) | **FCW** | Any new AI tool entering FIMI workflows confirmed for the first time |
| AI model used in election interference | **WDM** | Election interference using AI-generated content in WDM-covered countries |
| AI Act enforcement action against a financial services AI system | **GMM** | Regulatory action affecting fintech/trading system AI |
| AI compute energy threshold breach | **ERM** | Quantifiable energy/water threshold confirmed per ERM methodology |
| AI-enabled military autonomous weapons deployment | **SCEM** | IHL friction confirmed in active conflict theatre |
| US AI deregulation affecting European competitiveness | **ESA** | Digital sovereignty vector of Lagrange Point Framework |
| AISI personnel move: government → frontier lab | **M15 + cross flag** | Revolving door signal; route to all monitors via intelligence-digest.json |

---

## 9. Known Failure Mode Corrections

### FM-AGM-01: Benchmark Saturation Mirage
**Problem:** Reporting benchmark score improvements as capability jumps when scores are within benchmark saturation territory.
**Correction:** Apply the capability signal hierarchy (section 4 above). Only report benchmark scores when accompanied by a novel capability demonstration or a compute threshold event.

### FM-AGM-02: China Lab Capability Inflation
**Problem:** Chinese lab press releases claiming parity with or superiority over Western frontier models being treated as T2 sources.
**Correction:** Chinese lab capability claims are **T3 sources** for capability assessment. Require third-party independent evaluation (Hugging Face leaderboard, academic benchmark replication, or Western security organisation assessment) before scoring capability level.

### FM-AGM-03: Voluntary Commitment Drift
**Problem:** Lab safety commitments (RSP, Preparedness scorecard) becoming stale without version-history updates when labs revise them downward.
**Correction:** Every issue, check whether any lab has quietly revised its safety commitment documents. "Downgrade" of a safety commitment is an M10 + M11 item and must be flagged under `accountabilityFriction`.

### FM-AGM-04: Standards Vacuum Normalisation
**Problem:** Treating the Standards Vacuum as a background condition rather than an active analytical signal because it has been present for multiple weeks.
**Correction:** The Standards Vacuum flag must appear in M09 every issue with the current status and the number of days remaining until the compliance deadline it was supposed to address. Do not let it become invisible through repetition.

---

## 10. Identity Card Supplement — 2026 Professional Standard

> The best AI governance analyst in 2026 understands that the field is no longer primarily about what AI *might* do — it is about what AI *is already doing* and whether the governance infrastructure is keeping pace. The EU AI Act is the world's most comprehensive binding AI governance framework and it is entering its first real enforcement phase in 2026. The analyst's primary contribution is tracking the gap between legal obligation and operational reality: where standards are absent, where enforcement capacity is inadequate, where voluntary commitments are being quietly revised downward, and where capability is racing ahead of the governance frameworks designed to contain its risks.

---

*Last updated: 2026-04-02. Primary external references: EU AI Act (OJ L 2024/1689); GPAI Code of Practice working text (2025); NIST AI RMF 1.0; Council of Europe AI Treaty; OECD AI Principles 2024 update.*

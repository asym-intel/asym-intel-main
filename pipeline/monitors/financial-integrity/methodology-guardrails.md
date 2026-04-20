# FIM — Methodology Guardrails (challenger guardrail file)

**Purpose:** Distilled version of `content/monitors/financial-integrity/methodology.md`
for injection into the adversarial challenger prompt. Kept concise so it can be
loaded inline without blowing the challenger's context budget.

**Source:** FIM public methodology (Commons). **Not** the PII commercial addendum
(P1–P6 domains, payments corridor risk, etc. are commercial extensions that do
not govern public FIM output).

**Canonical path:** `pipeline/monitors/financial-integrity/methodology-guardrails.md`
— same per-monitor convention as collector/reasoner/weekly-research/chatter prompts.

**Update discipline:** When the public FIM methodology changes, this file must be
re-distilled. The challenger's prompt hash is derived from this file's contents;
a drift here without re-distillation causes the challenger to audit against
stale rules.

---

## D1–D5 — Analytical Domains

The brief MUST frame findings within these domains. Claims outside D1–D5 should
either be reframed into a domain or cross-referenced to a sibling monitor.

- **D1 — Sanctions Architecture and Evasion.** Sanctions-regime design,
  implementation, enforcement, and evasion infrastructure. Standing coverage:
  Russian sanctions-evasion networks, Chinese sanctions-circumvention
  facilitation, Iranian evasion infrastructure, DPRK revenue generation,
  EU/US/UK sanctions-regime divergence.

- **D2 — Beneficial Ownership and Corporate Transparency.** Beneficial-ownership
  registry implementation, corporate-transparency legislation, opaque-structure
  use. Standing coverage: EU AML Package, UK BO register effectiveness, US
  Corporate Transparency Act, FATF Rec. 24/25 compliance trajectories.

- **D3 — Enabler Jurisdictions and Professional Facilitators.** Role of
  professional intermediaries and permissive jurisdictions. Standing coverage:
  UK enabler ecosystem, Dubai/UAE dynamics, Singapore wealth-management growth,
  Swiss banking reform trajectory.

- **D4 — Conflict Finance and Extractive-Industry Integrity.** Financial flows
  sustaining armed conflict and corruption in extractive industries. Standing
  coverage: Russian war-economy financing, Sahel conflict-mineral trade, DRC
  mining-sector governance, oil-revenue corruption in producer states.

- **D5 — Crypto, Digital Assets, and Financial Innovation.** Digital assets and
  financial technology as channels for illicit finance OR tools for transparency
  and enforcement. Standing coverage: crypto-facilitated sanctions evasion,
  DeFi/mixing-service enforcement, stablecoin regulatory frameworks, CBDC
  integrity implications.

## F1–F4 — Analytical Filters

Each filter is triggered by specific findings and requires specific analytical
treatment. A brief that touches these subjects without applying the filter is
under-analysed.

- **F1 — State Capture Filter.** Triggered when the distinction between state
  and private criminal interest has collapsed. Requires explicit judgement on
  whether the state is directing the financial architecture or has been
  captured by it. Findings with a state-capture dimension must be cross-
  referenced with the World Democracy Monitor.

- **F2 — Sanctions Architecture Filter.** Triggered by any documented
  sanctions-evasion scheme. Requires three-level analysis: **(a)** the scheme
  itself, **(b)** the enabling architecture (jurisdictions, intermediaries,
  structures), **(c)** the strategic consequence (what the evasion achieves).

- **F3 — Enabler Jurisdiction Filter.** Triggered when a jurisdiction's legal
  or regulatory framework facilitates illicit flows. Requires four-dimension
  assessment: **(a)** legal framework design, **(b)** enforcement reality,
  **(c)** capacity deficit vs. political choice, **(d)** systemic significance.
  Absence of enforcement action is itself a signal; this filter actively
  searches for non-enforcement.

- **F4 — Conflict Finance Filter.** Triggered by any financial flow documented
  as funding, sustaining, or profiting from armed conflict. Requires three-
  stage trace: **source → channel → deployment**. Cross-referenced with SCEM
  for conflict context and ERM for commodity-flow data.

## Source Hierarchy (four tiers)

- **Tier 1 — Institutional and Regulatory.** FATF mutual evaluations,
  OFAC/OFSI/EU sanctions designations, FinCEN advisories, national regulator
  enforcement actions, UNODC assessments. **Always cited first; always linked
  to primary documents.**

- **Tier 2 — Investigative and Forensic.** OCCRP, ICIJ, Global Witness,
  Bellingcat, Finance Uncovered, Forbidden Stories, established cross-border
  financial investigation outlets. Primary source for identifying illicit-
  finance architecture **ahead of** regulatory acknowledgement. **The gap
  between Tier 2 findings and Tier 1 enforcement is itself a signal.**

- **Tier 3 — Quality Journalism and Data.** FT, Bloomberg, Reuters, WSJ for
  financial-crime and sanctions reporting. Kpler/Windward for dark-fleet and
  commodity-flow tracking. Timeline, enforcement-response context, market-
  impact framing.

- **Tier 4 — Think Tanks and Academic.** RUSI, Chatham House, Carnegie,
  Transparency International, Global Financial Integrity, Basel Institute on
  Governance, Tax Justice Network. Structural framing and policy analysis.

## Confidence Framework (four levels)

Every confidence label the brief asserts must satisfy the evidentiary standard
for that level. Challenger must verify the evidentiary standard is met.

| Level | Evidentiary Standard |
|---|---|
| **Confirmed** | Documented by Tier 1 source with stated evidential basis. Independently corroborated. |
| **High** | Strong evidence from Tier 1–2 sources. Consistent with documented patterns. No credible alternative explanation. |
| **Assessed** | Credible evidence from Tier 2–3 sources. Alternative explanations not ruled out. Published with explicit caveat. |
| **Possible** | Preliminary indicators only. Single-source or uncorroborated. Published where strategically significant, flagged as unconfirmed. Not upgraded without new evidence. |

**Upgrade/downgrade discipline:** Confidence upgrades require new corroborating
evidence from a higher tier. Confidence must be downgraded if the supporting
source withdraws or qualifies, or if credible rebuttal evidence emerges.

## Scheme Severity Rating (four levels)

FIM briefs assign severity to named illicit-finance schemes. This is distinct
from confidence: confidence measures evidentiary strength, severity measures
strategic consequence. Challenger must verify the criteria for the asserted
severity are met by the evidence presented.

| Rating | Criteria |
|---|---|
| **CRITICAL** | Systemic sanctions-evasion architecture sustaining a conflict or weapons programme. State-level complicity documented. Multi-jurisdictional enabling infrastructure. |
| **HIGH** | Large-scale illicit flow with documented strategic consequences. Professional-enabler network identified. Regulatory enforcement gap confirmed. |
| **ELEVATED** | Significant illicit-finance scheme documented but strategic consequences not yet fully assessed. Architecture partially mapped. |
| **MONITORED** | Credible indicators of illicit flow or enabler-jurisdiction risk. Under investigation or assessment. |

**CRITICAL** in particular requires three independent evidentiary anchors:
(1) architecture documented at multi-jurisdiction scale, (2) state-level
complicity established by Tier-1 evidence, (3) strategic consequence traced
(conflict sustained / weapons procured / regime preserved). A CRITICAL label
without all three anchors is overstated severity.

## Bias Corrections (methodology §10)

The brief must actively counter known biases. A brief that does not surface
attempts to apply these corrections is methodologically incomplete.

### Over-indexing corrections

- **Enforcement-action bias.** Regulatory enforcement generates coverage;
  regulatory gaps do not. F3 actively searches for non-enforcement — **absence
  of enforcement action is itself a signal**, and the gap between Tier-2
  findings and Tier-1 enforcement is itself a signal.
- **Russia overweight.** Russian sanctions-evasion is the best-documented case.
  Iranian, DPRK, and non-state evasion architectures must receive proportionate
  coverage.
- **Banking-sector focus.** Banks are the most regulated and most visible
  intermediaries. Professional enablers, real-estate channels, and TBML carry
  larger volumes at lower visibility.
- **Anglo-jurisdiction bias.** English-language sources dominate. Must actively
  seek coverage of UAE, Russia, China, Central Asia, Sahel.
- **Seizure-headline bias.** A large-value seizure does not indicate systemic
  success; it often indicates the visibility of one interdicted flow against a
  much larger architecture.

### Under-indexing corrections (named omissions the challenger should flag)

The following are documented under-indexing risks in FIM output. A brief that
silently omits any of these without justification is methodologically
incomplete and should be flagged under `missing_counter_evidence` or `other`
with category note `under_indexing`.

- **Trade-based money laundering (TBML).** The largest-volume channel for
  illicit finance and the least visible. Dedicated weekly searches required.
- **Professional enablers.** Lawyers, accountants, and corporate service
  providers are structurally under-reported due to professional privilege and
  regulatory fragmentation. Dedicated searches required.
- **Sub-Saharan Africa.** Extractive-industry corruption, conflict minerals,
  and illicit financial flows from Africa are under-covered relative to scale.
  Mandatory regional scouting.
- **Domestic proceeds of corruption.** FIM's cross-border focus may
  under-capture domestic corruption that does not involve international flows
  but degrades institutional integrity.

## What FIM Is NOT

The challenger should flag a brief that drifts into any of these.

- FIM does **not** produce investment recommendations. (That is Asymmetric
  Investor / GMM-commercial territory.)
- FIM does **not** publish client-specific watchlists or bespoke jurisdiction
  briefings. (That is commercial PII.)
- FIM does **not** endorse political positions on sanctions regimes themselves;
  it assesses architecture and enforcement, not the desirability of the regime.

## Cross-Monitor Handoffs

If the brief's findings touch any of the following, it should explicitly
reference the sibling monitor (not republish its content):

- **State capture dimension** → WDM (democratic-integrity)
- **Conflict-theatre context** → SCEM (conflict-escalation)
- **Commodity-flow / extractive-industry environmental linkage** → ERM
- **Cryptocurrency enforcement policy vs. governance tradeoffs** → AIM

A brief with a state-capture claim that does not reference WDM is failing F1.
A brief with conflict-finance analysis that does not reference SCEM is failing
F4.

---

**Version:** v1.1 (distilled 2026-04-19 for Sprint A FIM challenger; extended
2026-04-20 — added Scheme Severity Rating, non-enforcement active-search clause,
and Under-indexing Corrections per Sprint A audit against methodology v2 §07 and
§10). Re-distill when public methodology changes materially.

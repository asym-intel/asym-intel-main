---
title: "FCW Enhancement Addendum — EEAS StratCom 2025 & 2026 Operational Calibration"
monitor: fimi-cognitive-warfare
version: 1.0
date: 2026-04-02
author: Peter Howitt / Asymmetric Intelligence
classification: Internal — not for publication
---

# FCW Enhancement Addendum
## EEAS StratCom 2025, AI-Generated FIMI, Platform Transparency 2026, and Campaign Baseline Recalibration

---

## 1. Purpose

This addendum extends `fimi-cognitive-warfare-full.md` with calibrations specific to the 2026 operating environment. Five structural changes have materially altered the FCW's operating conditions since the methodology was last reviewed:

1. **AI-generated FIMI at operational scale** — generative AI tools are now embedded in FIMI workflows across multiple actors, creating a systematic I1-equivalent inflation risk analogous to what SCEM identified for AI-generated rhetoric
2. **X/Twitter platform transparency collapse** — the existing methodology notes X/Twitter's declining publication rate; this addendum provides the calibrated 2026 reading protocol
3. **DISARM framework version alignment** — the DISARM TTP framework has been updated; this addendum specifies which version the FCW uses and how to handle TTPs that moved between versions
4. **Active campaign baseline recalibration** — three campaign categories require baseline reset based on 2025-2026 operational changes
5. **Commercial cognitive warfare 2026 landscape** — new operators and the Private Emanation sub-category (added 2 April 2026) require specific calibration guidance

**Read order at session start:**
1. `AGENT-IDENTITIES.md` → FCW Collector identity card
2. `fimi-cognitive-warfare-full.md` → full methodology (includes 5 analytical gaps added 2 April 2026)
3. This addendum → 2026 operational calibration
4. `persistent-state.json` → active campaign registry, attribution log
5. `intelligence-digest.json` → cross-monitor flags (WDM electoral contexts, SCEM conflict FIMI, AGM AI-enabled ops)

---

## 2. AI-Generated FIMI — 2026 Operational Calibration

### 2.1 Structural Change

Generative AI tools (image synthesis, text generation, voice cloning, video synthesis) have moved from experimental to operationally embedded in FIMI campaigns across all six actor categories. As of 2025-2026, AI-generated content is present in confirmed operations attributed to Russia (Doppelganger continuation), Iran (influence operations in US/EU electoral contexts), and commercial operators (election-adjacent sentiment manipulation).

This creates a **systematic detection gap** that affects scoring at every confidence tier:
- Tier 1 platform disclosures now routinely note AI-generated components without always specifying which operational layer used AI
- Tier 2-3 OSINT analysis faces a detection challenge: AI-generated content can be indistinguishable from human-authored content without forensic analysis tools
- The coordination evidence requirement is harder to meet when AI generation reduces the infrastructure footprint of an operation

### 2.2 AI-FIMI Indicator Protocol

Before scoring any FIMI operation with a content manipulation component, apply this protocol:

**Step 1 — Content authenticity check:**
Is the primary evidence of this operation based on content that could be AI-generated (synthetic images, consistent stylistic patterns across accounts, lack of platform tenure)?
- If yes: require at least one Tier 1 platform disclosure OR one Tier 2 academic/institutional forensic analysis before scoring at Assessed or above
- If no Tier 1/2 forensic confirmation: hold at Possible with `aiGenerationCheck: true` and `aiGenerationUnconfirmed: true`

**Step 2 — Infrastructure vs. content distinction:**
Operations using AI for content generation may still have human-directed coordination infrastructure. Distinguish:
- `contentGeneration: AI` — the content was AI-produced (affects confidence in content-based evidence)
- `coordinationInfrastructure: human` — the account network, timing, and amplification patterns remain human-directed (these are still valid coordination evidence)

Do not let AI-generated content automatically downgrade the coordination evidence — assess each layer independently.

**Step 3 — Actor AI capability baseline (2026):**

| Actor | AI-FIMI Capability Level | Known Tools/Patterns | Source Basis |
|---|---|---|---|
| Russia | High — operationally deployed | Doppelganger: AI-generated news sites; synthetic image deployment confirmed | Meta CIB 2024-2025; Stanford IO |
| China | High — operationally deployed | Spamouflage evolution: AI-generated avatars at scale; multilingual content farms | Meta CIB; ASPI |
| Iran | Medium — episodic deployment | Electoral influence operations using AI-generated content in US/IL contexts | Google TAG; Meta CIB |
| Gulf states | Medium — commercial procurement | Likely using commercial AI tools via operators; less direct attribution | DFRLab |
| United States | Assessed — capability clear, attribution limited | Psychological operations AI tools documented (US military PSYOP history); commercial procurement | Congressional hearings; FOIA documents |
| Israel | Assessed — capability clear, attribution limited | Unit 8200 AI capabilities confirmed; FIMI application assessed not confirmed | Haaretz; Citizen Lab |
| Commercial operators | High — AI is now core product | Multiple commercial FIMI operators offer AI-generated content as a service | Meta CIB; academic research |

### 2.3 AI-FIMI Failure Mode

**FM-FCW-05: AI Content Confidence Inflation**
Problem: Treating the detection of AI-generated content as sufficient evidence for state attribution. AI tools are commercially available; detecting AI-generated content in an operation tells you about the content production method, not the actor.
Correction: AI-generated content is evidence of operational method, not actor attribution. Attribution still requires the standard four-tier source hierarchy. `contentGeneration: AI` is a characteristic of the operation, not an attribution signal.

---

## 3. X/Twitter Platform Transparency — 2026 Reading Protocol

### 3.1 Updated Status

The existing methodology notes X/Twitter's declining publication rate and non-participation in EU DSA FIMI coordination. As of 2026, this requires a more specific calibrated reading:

**Factual 2026 baseline:**
- X/Twitter has not published a Coordinated Inauthentic Behaviour (CIB) equivalent report since Q3 2022 (pre-Musk acquisition)
- X/Twitter formally withdrew from the EU's Voluntary Code of Practice on Disinformation in May 2023
- X/Twitter's Trust & Safety team staffing has been reduced by approximately 80% since October 2022 (per multiple journalistic investigations, Tier 3/4 — exact figures unverifiable)
- X/Twitter has not participated in EEAS FIMI disclosure coordination exercises
- X/Twitter API access restrictions (2023) have materially reduced the capacity of third-party researchers to monitor platform activity

**Reading protocol for X/Twitter absence:**
`"X/Twitter has not disclosed this operation"` means:
- The platform's detection capacity is structurally degraded relative to 2022 baseline
- The platform has withdrawn from voluntary FIMI cooperation frameworks
- The absence of disclosure is **not** evidence of absence of activity

**Scoring implication:** When an operation is confirmed on Meta/Google platforms but absence of X/Twitter disclosure is noted, do NOT treat this as evidence the operation is not present on X/Twitter. Flag `platformTransparencyGap: true` and `xTwitterCoverageStructurallyDegraded: true`.

### 3.2 Alternative X/Twitter Coverage Sources

Since platform self-disclosure is no longer available, use these for X/Twitter coverage:

| Source | Coverage | Limitations |
|---|---|---|
| Stanford IO / Cyber Policy Center | Academic OSINT analysis of X/Twitter operations | Delayed (research cycle); API-restricted |
| DFRLab Digital Forensic Research Lab | X/Twitter network analysis for high-profile operations | Slower cadence since API restrictions |
| EU DSA Transparency Database | Mandated content moderation data | X/Twitter compliance under legal challenge |
| Whistleblower disclosures (Zatko et al.) | Internal platform security failures | Historical; not real-time |
| Academic network analysis | Graph-based coordination detection | Research-cycle delays |

**Standing check (mandatory every issue):** Has any Tier 1-3 source published new analysis of FIMI operations on X/Twitter this week? If yes, treat as significant — the detection gap means confirmed findings on X/Twitter carry higher analytical weight than equivalent findings on better-monitored platforms.

---

## 4. DISARM Framework — Version Alignment

### 4.1 Version in Use

The FCW uses the **DISARM Framework v1.5** (current as of Q1 2026). The DISARM Red Framework (attacker TTPs) is the primary reference for operational pattern classification. DISARM Blue (defender countermeasures) is noted but not used for scoring.

Source: `github.com/DISARMFoundation/DISARMframeworks`

### 4.2 Key TTPs Referenced in FCW Methodology

The following TTPs are specifically referenced in the FCW's operational pattern analysis. Version 1.5 designations:

| TTP | Code | Description | Change from v1.0 |
|---|---|---|---|
| Astroturfing | T0059 | Create fake grassroots movement | Unchanged |
| Search engine manipulation | T0046 | SEO manipulation to amplify narratives | Unchanged |
| Coordinated inauthentic behaviour | T0003 | Network coordination to appear organic | Unchanged |
| Hack and leak | T0019 | Obtain and release stolen materials | Unchanged |
| Impersonation | T0097 | Pose as legitimate entity | Added in v1.4 — use this, not legacy codes |
| AI-generated content | T0155 | Synthetic media in operations | **Added in v1.5** — not in earlier versions |
| Spear phishing for information | T0021 | Targeted phishing as FIMI precursor | Added in v1.4 |

**For spyware-as-targeting-infrastructure** (added 2 April 2026 to methodology): use T0021 as the closest DISARM mapping but note that the targeting-infrastructure pattern is not fully captured by existing DISARM TTPs. Flag as `dismarmTTP: T0021, dismarmNote: "targeting-infrastructure variant — precursor stage not delivery stage"`.

### 4.3 DISARM Update Protocol

When DISARM publishes a new version:
1. Check `github.com/DISARMFoundation/DISARMframeworks/releases` for changelog
2. Update this addendum with new TTP codes
3. Check whether any active campaign entries use deprecated TTP codes
4. Log the version update in `schema-changelog.json`

---

## 5. Campaign Baseline Recalibration — Q2 2026

Three campaign categories require baseline assessment at the start of Q2 2026:

### 5.1 Doppelganger Network (Russia)
**Baseline window opened:** September 2022 (initial disclosure)
**Structural break:** The network has undergone documented architecture changes — migration from domain-spoofing to subdomain approaches, increased use of AI-generated content, and documented attempts to operate via legitimate news aggregators rather than spoof sites.
**Recalibration action:** If Doppelganger is in the active campaign registry, review whether the current campaign entry reflects the 2024-2025 architecture evolution or the 2022 original detection. The network's continued activity should not be scored against the 2022 baseline — it is a structurally evolved operation.

### 5.2 AI-Generated Influence Operations (All Actors)
**New category (no prior baseline):** As of 2025-2026, AI-generated content operations are sufficiently widespread to warrant a standing baseline assessment rather than treatment as novel each time detected.
**Baseline establishment:** Set the following as 2026 baseline conditions (not new findings):
- Meta routinely detects and removes AI-generated influence operation content in their quarterly CIB reports
- Google TAG regularly documents AI-generated content in state-backed influence operations
- Commercial operators routinely offer AI-generated content as a FIMI service

Any report of AI-generated FIMI content is NOT automatically a new finding — assess whether it represents a departure from this baseline (new actor, new scale, new targeting) before scoring.

### 5.3 Commercial Cognitive Warfare Sector
**Structural change:** The commercial cognitive warfare sector has expanded since the methodology was drafted. Beyond the legacy operators (NSO Group, Black Cube, Psy-Group), the following categories now require active monitoring:

| Category | 2026 Status | Watch signal |
|---|---|---|
| Election consultancy-adjacent firms | Several documented post-Psy-Group successors | Cambridge Analytica successor entities; undisclosed client contracts |
| AI-powered influence platforms | New market segment 2023-2025 | Any platform marketing "narrative management" + "synthetic persona" services |
| Geopolitical intelligence-to-FIMI pipeline | Overlap between legitimate OSINT and FIMI targeting | Commercial OSINT firms with documented government FIMI clients |
| Private Emanation category (new 2026) | State-subsidised infrastructure actors | See methodology §Private Emanation — Musk/Thiel/Palantir-scale actors |

---

## 6. Source Hierarchy — 2026 Calibration Updates

### 6.1 New Tier 1 Additions

| Source | Coverage | URL |
|---|---|---|
| EEAS Annual FIMI Report | EU-level FIMI threat landscape (annual) | eeas.europa.eu |
| EUvsDisinfo Annual Activity Report | EUvsDisinfo cases and trends | euvsdisinfo.eu/reports |
| EU DSA Transparency Database | Platform content moderation data (FIMI-relevant) | transparency.dsa.europa.eu |
| Meta Adversarial Threat Report | Quarterly CIB disclosures (replaces semi-annual) | about.fb.com/news |

### 6.2 Source Tier Changes (2026)

| Source | Previous Tier | 2026 Tier | Reason |
|---|---|---|---|
| X/Twitter CIB disclosures | Tier 1 | N/A — discontinued | Last published Q3 2022; platform withdrawn from cooperation frameworks |
| X/Twitter API researcher data | Tier 2 | Tier 3 | API restrictions 2023 have materially degraded research capacity |
| EU DSA FIMI coordination | Tier 2 | Tier 1 | Formal legal framework now in force; platform obligations are binding |

### 6.3 EEAS StratCom Annual Report — Integration Protocol

The EEAS StratCom publishes an annual report on FIMI threats. When published (typically Q1-Q2):
- Update persistent-state with any new confirmed campaign attributions
- Check whether any Watch List entries have been formally attributed by EEAS
- Update the EEAS institutional perimeter note: which actors does the current report cover vs. omit
- Cross-check EEAS actor coverage against the FCW's six-actor framework — gaps are analytically significant per the EEAS political choice reading protocol (methodology §EEAS gap)
- Do NOT treat EEAS report publication as resetting the attribution confidence on operations the report does not mention — EEAS silence on US/IL operations remains a documented institutional choice, not evidence of absence

---

## 7. Cross-Monitor Calibration — 2026

### 7.1 AGM AI-FIMI Joint Flag Protocol

When AGM identifies a new AI capability entering operational use (M02 capability event), FCW must assess:
- Is this capability now available to FIMI operators (commercial or state)?
- Has any Tier 1-3 source documented this capability in a FIMI context?
- If yes to both: joint `crossmonitorflag` with `type: "AI-FIMI-capability-delta"`

**2026 standing flag:** Generative AI (text, image, voice, video synthesis) is already confirmed in FIMI operations. The joint flag trigger is now **new capability class** adoption, not initial AI adoption.

### 7.2 WDM Electoral Calendar Integration

FCW must check the WDM electoral calendar every issue. Any election within 90 days in a WDM-covered country is a mandatory FIMI watch trigger:
- Escalate source search intensity for that country's FIMI environment
- Check whether existing campaign registry has entries targeting that electoral context
- A Watch entry for election-adjacent FIMI is required even when evidence is only Possible confidence

### 7.3 SCEM Conflict-FIMI Pattern

When SCEM scores I1 Red-band in any theatre, FCW must assess:
- Is there confirmed or assessed FIMI activity in the same theatre?
- If yes: joint `crossmonitorflag` with `sharedCountryTag` in both monitor outputs
- The intersection of kinetic escalation + FIMI activity is a compound signal — neither monitor should carry it in isolation

---

## 8. Failure Mode Corrections — 2026 Supplement

### FM-FCW-05: AI Content Confidence Inflation
*(See §2.3 above)*

### FM-FCW-06: X/Twitter Absence as Evidence
**Problem:** Treating the absence of X/Twitter disclosure as evidence that an operation is not present on the platform.
**Correction:** X/Twitter disclosure capacity is structurally degraded. Absence of X/Twitter disclosure is a platform transparency gap, not an absence of activity signal. Flag `platformTransparencyGap: true` and continue assessment via Tier 2-3 research sources.

### FM-FCW-07: Doppelganger Architecture Conflation
**Problem:** Treating new Doppelganger variants (subdomain approach, AI-generated content, aggregator infiltration) as the same operation as the 2022 original.
**Correction:** The Doppelganger network has undergone documented architecture evolution. Each structural generation should be assessed against its own operational baseline, not the 2022 spoof-site baseline. Use `architectureGeneration` field to distinguish.

### FM-FCW-08: Commercial Operator Single-Client Assumption
**Problem:** Assuming a commercial cognitive warfare operator has a single state client when the documented evidence shows multiple engagements.
**Correction:** Commercial operators in the FIMI space frequently work with multiple clients across political, corporate, and state contexts. Unless a specific operation has a confirmed client attribution, use `client: [unattributed]` — do not infer sole-client status from partial evidence.

---

## 9. Identity Card Supplement — 2026 Professional Standard

> The best FIMI analyst in 2026 understands that the discipline has entered a second phase: the first phase (2017-2022) was about establishing that state-backed information operations exist and developing the evidentiary standards to attribute them. The second phase is harder. AI has industrialised content production to the point where the infrastructure footprint of an operation — the number of accounts, the volume of content, the server architecture — is no longer a reliable proxy for operational scale or state resourcing. A well-resourced operation in 2026 can leave a smaller technical footprint than a poorly-resourced one in 2018. The analyst's job is not to count accounts or measure content volume. It is to identify the coordination architecture, the targeting logic, the narrative persistence, and the state or commercial nexus — using evidence that survives the AI-generation noise floor.

---

*Last updated: 2026-04-02. Primary external references: EEAS StratCom Annual Report 2024; Meta Adversarial Threat Report Q4 2025; DISARM Framework v1.5; Stanford IO FIMI Tracker 2025; EU DSA Transparency Database.*

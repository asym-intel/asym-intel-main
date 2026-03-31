---
title: "Methodology — Global FIMI & Cognitive Warfare Monitor"
description: "Analytical standards, source hierarchy, attribution confidence framework, and actor inclusion criteria for the Global FIMI & Cognitive Warfare Monitor."
date: 2020-01-01
monitor: "fimi-cognitive-warfare"
type: "methodology"
draft: false
---

This document sets out the analytical and epistemic standards governing the Global FIMI & Cognitive Warfare Monitor. The companion scope document addresses *what* the monitor tracks — actors, campaign types, platform responses, regulatory frameworks, and publication cadence. This document addresses *how* analytical conclusions are reached, what evidentiary standards govern attribution, and where the monitor's methodology departs from or extends existing institutional frameworks.

The document is intended as a standing reference for analysts who use or cite the monitor's output.

---

## Definition of Terms

### FIMI — Foreign Information Manipulation and Interference

The EEAS definition, established in the 2022 FIMI framework and refined through subsequent annual reports, treats FIMI as a pattern of behaviour that threatens or has the potential to negatively impact values, procedures, and political processes. It is characterised by being (a) foreign in origin, (b) manipulative rather than merely persuasive, (c) conducted with an intent to interfere in political processes, and (d) covert or deceptive in at least one operational dimension.

This monitor adopts the EEAS definition as the baseline and extends it in one significant respect: where the EEAS framework formally tracks Russian and Chinese actors within its institutional mandate, this monitor applies the same definitional test to all actors whose operations meet the criteria, regardless of whether they fall within the EEAS perimeter. The definition is applied consistently; the institutional scope is not.

### Cognitive Warfare

Cognitive warfare is the doctrinal frame within which FIMI operations are frequently situated. Where FIMI describes the operational activity — a specific campaign, a network takedown, an attribution — cognitive warfare describes the strategic objective: the deliberate targeting of the cognitive domain to degrade an adversary's decision-making capacity, erode social cohesion, and manufacture epistemic confusion at scale.

The NATO StratCom Centre of Excellence defines cognitive warfare as "the weaponisation of brain science and neuroscience" operating at individual, group, and societal levels. This monitor uses the distinction as follows: FIMI is the instrument; cognitive warfare is the doctrine under which that instrument is deployed. A single coordinated inauthentic behaviour (CIB) campaign is a FIMI operation. The systematic, multi-platform, multi-actor effort to undermine trust in democratic institutions across a target society is cognitive warfare.

The terms are not interchangeable. Operations are tracked as FIMI. The doctrinal context — where relevant — is characterised as cognitive warfare.

### Information Operation vs. Influence Operation

These terms are used inconsistently across the literature. This monitor applies the following usage:

**Information operation (IO)**: the broader category — any deliberate effort to shape an information environment in support of strategic objectives. Includes both overt and covert activities.

**Influence operation**: a subset of IO in which the specific objective is to shift the beliefs, attitudes, or behaviour of a target audience, typically through covert or deceptive means. All tracked campaigns in this monitor are influence operations by this definition; the term IO is used where a broader reference to the actor's overall information capabilities is intended.

### Attribution vs. Assessment

**Attribution** is a factual claim: a specific actor conducted a specific operation. Attribution carries an evidentiary burden. Where this monitor uses attribution language ("Russia's Social Design Agency operated network X"), it does so only where the claim meets the Confirmed or High confidence threshold defined below.

**Assessment** is an analytical judgement: the available evidence is consistent with, or strongly suggests, a particular actor's involvement without meeting the evidentiary standard for attribution. Where this monitor makes assessment-level claims ("this operation is consistent with documented Iranian IRGC information operation TTPs"), it is explicit that the claim is analytical rather than evidential.

The distinction matters for how output is read. Assessments are valid analytical products; they are not attributions.

### Active Campaign vs. Historical Campaign

**Active campaign**: an operation with documented activity within the past 90 days. Tracked in the Active Campaigns table on the dashboard. Updated every Thursday.

**Historical campaign**: an operation with no activity in the past 12 months, or one that pre-dates the monitor's tracking period (1 January 2025). Referenced for doctrinal context — TTP continuity, actor capability assessment, infrastructure lineage — but not carried in the Active table.

Operations between 91 and 365 days since last documented activity carry status **CONCLUDED** or **DISRUPTED** and are retained in the Campaign Archive.

---

## Actor Inclusion Criteria

Six primary actor categories are tracked: Russia, China, Iran, Gulf states (UAE, Saudi Arabia, Qatar), United States, and Israel. The operative criterion for inclusion is not political judgement but operational fact: an actor is tracked when it is conducting documented cross-border information operations using covert means, foreign funding, or coordinated platform manipulation, with evidence from at least one Tier 3 or above source (see Source Hierarchy below).

The cross-border requirement is not incidental. It is the methodological boundary between FIMI and domestic political communication. Domestic propaganda — however sophisticated, however manipulative — is outside scope unless it involves at least one of the following: foreign funding flowing to a domestic actor; foreign platforms used as primary distribution infrastructure; or coordination with a foreign state actor or its proxies. The manipulation itself does not establish FIMI. The foreign dimension does.

**Why six actors and not more**: the six tracked actors share three characteristics that collectively justify the monitoring overhead. First, all six have documented, persistent cross-border information operations — not isolated incidents but established programmes with doctrinal continuity. Second, all six have sufficient OSINT coverage from Tier 1–3 sources to support meaningful attribution. Third, all six have active campaigns in the monitor's primary coverage area (Europe and Western democratic states). Actors with documented operations but insufficient OSINT coverage — North Korea is the clearest case — are noted in individual items where relevant but are not assigned an actor profile.

**The EEAS gap**: the EEAS FIMI framework formally tracks Russian and Chinese operations within its institutional mandate. US and Israeli information operations run at analytically comparable scale but fall outside the EEAS perimeter by design — a structural consequence of member state composition and institutional mandate, not an analytical judgement about significance. CIDOB and independent researchers have documented this gap explicitly.

This monitor tracks US and Israeli operations for a methodological reason, not a political one: an attribution framework that systematically excludes two of the six most active actors in the operational environment is not a methodology — it is a selection bias that produces a structurally distorted analytical picture. The inclusion of all six actors is required for the framework to function as an attribution system rather than as a politically bounded inventory. All six actors are assessed against identical criteria: documented cross-border operations using covert means, foreign funding, or platform manipulation. No actor receives either preferential coverage or preferential exclusion.

---

## Source Hierarchy and Trust Levels

Sources are assigned to four tiers based on the nature and reliability of the evidence they provide. Tier assignment determines how source evidence is weighted in the attribution confidence framework.

| Tier | Category | Key Sources | Trust Basis | Structural Limitation |
|------|----------|-------------|-------------|----------------------|
| **1** | Platform disclosures | Meta CIB, Google TAG, Microsoft MSTIC, TikTok Transparency | Primary technical evidence: network graph analysis, account behaviour clustering, infrastructure fingerprinting | Platforms have commercial and political incentives that may affect what they disclose and when; disclosure is not comprehensive |
| **2** | Institutional attributions | EEAS RAS, Five Eyes advisories, NATO StratCom CoE, Viginum, BfV, MI5/GCHQ, NCSC | Government-level intelligence with classified sources informing public conclusions; highest institutional authority | Institutional mandates create systematic blind spots: EEAS perimeter excludes US and Israeli operations; Five Eyes perimeter excludes own member states |
| **3** | Academic and specialist OSINT | Stanford Internet Observatory, DFRLab, ASPI ICPC, EU DisinfoLab, Bellingcat, Disinfo Lab Brussels | Methodologically rigorous, independent, multi-source; peer-reviewed or editorially scrutinised | Resource constraints mean coverage is selective rather than comprehensive; research cycles do not match operational tempo |
| **4** | Investigative journalism | Forbidden Stories, IJ4EU, OCCRP, Haaretz, Mediapart, Süddeutsche Zeitung, The Guardian | Primary-source document access, source networks, and financial investigation capability that OSINT alone cannot replicate | Publication timing driven by editorial rather than intelligence cycles; single-outlet reports without corroboration require caution |

**On Tier 1 limitations**: platform disclosures are the highest-confidence technical source available in an OSINT-only framework, but they are not neutral. Platforms decide when to take down networks, what to disclose in takedown reports, and how to characterise attribution. Meta CIB reports, for example, have historically been more forthcoming about Russian and Iranian networks than about networks with political relationships to the platform's home jurisdiction. X/Twitter's declining publication rate and non-participation in the EU DSA FIMI coordination exercise are treated as a structural transparency gap, not simply as absence of activity.

**On Tier 2 limitations**: government and institutional attribution carries the highest authority where it exists, but its systematic gaps are as significant as what it covers. This monitor does not defer to institutional perimeters when assessing what should be tracked. Where EEAS does not cover an actor, this monitor notes the absence of institutional attribution rather than treating it as absence of evidence.

**On Tier 4 limitations**: investigative journalism is the primary mechanism through which commercial cognitive warfare operations and covert lobbying are documented — categories that platform takedown reports and institutional bodies are structurally unlikely to cover. The financial investigation and human source capability of outlets like OCCRP, Haaretz, and Forbidden Stories fills attribution gaps that OSINT cannot. Single-outlet investigative reports at Tier 4 without corroboration from an independent source are flagged explicitly; they may justify Possible or Assessed confidence but not High or Confirmed.

---

## Attribution Confidence Framework

Attribution confidence is assigned to every tracked campaign and every item in the weekly brief. The four-level scale is defined by the evidentiary standard met, not by the analyst's subjective degree of certainty.

| Level | Evidentiary Standard |
|-------|---------------------|
| **Confirmed** | Attributed by at least one Tier 1 or Tier 2 source with stated technical evidence (network analysis, infrastructure fingerprint, or government attribution with stated intelligence basis). Corroborated by at least one independent source from a different tier or organisation. |
| **High** | Strong circumstantial and technical evidence from Tier 1–3 sources. Consistent with documented actor TTPs and pattern-of-life. No credible alternative attribution exists. Not yet formally attributed by a Tier 1 or Tier 2 source, or formal attribution exists without public technical evidence. |
| **Assessed** | Credible evidence from Tier 3–4 sources consistent with actor doctrine and prior behaviour. Alternative attributions have not been ruled out. Published with explicit caveat that this is an analytical judgement, not a factual attribution claim. |
| **Possible** | Preliminary indicators only. Single source, or multiple sources that are not independently corroborated. Published where operationally significant despite the absence of confirmation — most commonly in election-adjacent operations where the speed of disclosure matters — and explicitly flagged as unconfirmed. |

**Corroboration rule**: attribution claims that do not meet the Possible threshold are not published. Claims at Assessed and Possible confidence require evidence from a minimum of two independent source categories — that is, two sources that do not share a common institutional parent or data feed. A Meta CIB report corroborated by a DFRLab analysis of the same network meets this standard. Two DFRLab analyses of the same network do not, unless the second analysis introduces primary evidence not drawn from the first.

**On downgrading**: attribution confidence is downgraded — and the change noted explicitly — if rebuttal evidence emerges, if a previously Tier 1/2 source withdraws or qualifies its attribution, or if alternative attribution becomes credible. Confidence is not upgraded without new evidentiary grounds.

---

## Meta-FIMI Integrity Filters

The FIMI Monitor is uniquely exposed to the object of its own analysis.
State actors routinely generate false attribution claims, manufacture
fabricated "exposure" reports, seed counter-narratives designed to
discredit genuine FIMI researchers, and operate coordinated blowback
campaigns against institutional attribution findings. This is meta-FIMI —
FIMI operations targeting the FIMI monitoring space itself.

Four named filters are applied to every attribution claim before
publication. They precede the Attribution Confidence Framework — they
determine whether the evidentiary basis meets the threshold for the
confidence level being claimed. They do not replace the confidence
framework; they govern entry into it.

**MF1 — Reflexive Control Check**

Trigger: An "exposure" of a FIMI operation arrives primarily from a
source institutionally aligned with the accused actor — for example, a
Russian state outlet "exposing" a Ukrainian influence operation, or a US
government release attributing Chinese interference without published
technical evidence.

Action: Treat as **Possible** confidence maximum regardless of source
authority. The reflexive control pattern is documented explicitly. Require
independent corroboration from a source with no institutional alignment to
the accusing party before upgrading confidence. The existence of the
reflexive attribution claim is itself published as a data point.

Rationale: Reflexive control is a documented Russian information warfare
doctrine (Reflexivnoye Upravleniye) in which an adversary is manipulated
into taking actions that serve the originating actor's interests. In the
FIMI context, it manifests as attribution laundering — using the target's
own monitoring infrastructure to amplify disinformation.

**MF2 — Attribution Laundering Check**

Trigger: A claim appearing in a Tier 3/4 outlet is subsequently amplified
by Tier 1/2 sources without those sources publishing their own independent
evidence — they are citing the original Tier 3/4 report, creating a false
appearance of multi-source corroboration.

Action: Trace the full citation chain. If all published sources derive
from the same original report or dataset, treat as **single-source**
regardless of how many outlets have repeated it. Document the citation
chain. Apply the corroboration rule from the Attribution Confidence
Framework: sources sharing a common institutional parent or data feed do
not constitute independent corroboration.

Example: A Meta CIB takedown report cited by Reuters, BBC, and DFRLab
is one source (Meta) with three amplifiers — not four independent sources.
A DFRLab analysis that introduces original network analysis not drawn from
the Meta report constitutes genuine independent corroboration.

**MF3 — Takedown Inflation Check**

Trigger: A platform takedown report claims attribution to a state actor
without publishing technical indicators of compromise (network analysis,
infrastructure fingerprint, behavioural cluster analysis, or named
operator patterns).

Action: The takedown itself (the removal of accounts or content) is
treated as a factual event at the confidence level of the platform's
sourcing. The attribution claim within the takedown report is treated
separately: it is scored at **Assessed** confidence maximum unless
technical indicators are published alongside it. Platform self-attribution
without published technical evidence is treated as Tier 3 for attribution
purposes — not Tier 1.

Note: This filter does not downgrade the significance of the takedown
action. A Meta CIB removal of 10,000 accounts is a significant event
regardless of whether Meta's attribution claim meets the evidentiary
standard for Confirmed confidence. Both facts are published; they are
clearly distinguished.

**MF4 — Counter-Narrative Seeding Check**

Trigger: An operation denial, counter-narrative, or coordinated
"debunking" of an attributed FIMI campaign arrives in rapid coordination
across multiple actor-aligned accounts, outlets, or official spokespersons
— suggesting coordinated response rather than organic rebuttal.

Action: The coordinated denial is documented as a data point. A
coordinated denial of a **Confirmed** or **High** confidence attribution
increases rather than decreases the analytical weight of the original
attribution — it indicates the attributed actor has an interest in
suppressing the finding. Treat the denial pattern as supporting evidence
for the original finding, not as grounds for downgrading confidence.

The denial is published alongside the original attribution with its
source tier and coordination pattern noted. The confidence level of the
original finding is not downgraded on the basis of denial alone.

**Relationship to the Attribution Confidence Framework:** MF-filters are
applied before confidence is assigned. An item that triggers MF1 enters
the confidence framework at Possible maximum. An item that passes all
four MF-filters is assessed on the full evidentiary standard in the
Attribution Confidence Framework. The filters do not create a separate
confidence scale — they determine which entries into the existing scale
are permitted.


## What Constitutes a FIMI Operation for Inclusion

An operation enters the Active Campaigns table when it satisfies all four of the following conditions:

1. **Cross-border reach**: the operation targets audiences in a different state from the operator's primary base. Operations targeting diaspora communities in third states, or using domestic proxies to target a third state, satisfy this criterion.

2. **Use of covert means, foreign funding, or coordinated platform manipulation**: at least one of these three operational characteristics must be documented. Overt, attributed state communication — official government statements, state broadcaster output clearly labelled as such — does not satisfy this criterion, even where the content is false or distortive.

3. **Documented evidence from at least one Tier 3 or above source**: the operation must be documented, not merely alleged. Rumour, political accusation without evidentiary basis, and counter-claims in ongoing information conflicts do not satisfy this criterion.

4. **Identifiable actor**: the operation must be attributable to an actor at minimum Assessed confidence. Anonymous or unattributed operations may be tracked under "Unknown actor" where the operation itself is documented and operationally significant — for example, an election-adjacent CIB network disrupted by a platform takedown before attribution is established.

These four conditions are conjunctive. An operation meeting three of the four does not enter the Active table; it may be noted in the weekly brief pending further evidence.

---

## What Distinguishes FIMI from Adjacent Phenomena

### vs. Public Diplomacy

Public diplomacy is overt, attributed, and legally conducted foreign communication. Official government statements, embassy communications, and state-funded broadcasting operating transparently under their institutional identity are public diplomacy. They are outside scope. RT and CGTN enter scope not because they are state media but because they operate through proxy networks, undisclosed funding chains, or covert amplification infrastructure — the covert dimension is what establishes FIMI, not the state connection.

### vs. Propaganda

Domestic propaganda directed at a state's own population, without cross-border reach and without foreign funding or coordination, is outside scope. The monitor does not track what states do to their own citizens. The foreign and cross-border dimensions are not incidental to the FIMI definition — they are constitutive of it.

### vs. Cyberattack

Purely technical intrusion — data exfiltration, system compromise, infrastructure attack — without an information warfare objective is outside scope and is tracked separately in the cyber layer of the European Strategic Autonomy Monitor. Hybrid cyber-IO operations are in scope: a hack-and-leak operation uses technical intrusion in service of an information warfare objective, and the information warfare dimension determines inclusion. The cyber dimension is noted but does not itself determine inclusion or exclusion.

### vs. Lobbying

Overt, registered, and lawful lobbying — where the foreign connection is disclosed and the activity is legal under applicable jurisdiction — is outside scope. Covert lobbying using undisclosed proxies, or lobbying funded by undisclosed foreign sources, satisfies the covert means criterion and is in scope. The distinction turns on disclosure: disclosed foreign lobbying is not FIMI; undisclosed foreign lobbying is.

### vs. Lawfare Against Journalists

Strategic litigation against journalists and media freedom violations are tracked in the Rule of Law Monitor as domestic legal and institutional matters. They enter scope in this monitor only where they are directly in service of a documented FIMI operation — for example, legal suppression of a journalist actively investigating an attributed campaign, or foreign-state-directed litigation designed to suppress attribution reporting.

---

## Commercial Cognitive Warfare — Special Treatment

Commercial operators — NSO Group, Black Cube, Psy-Group (legacy), and their successors in the private intelligence market — require distinct methodological treatment from state actors because they introduce a structural attribution problem: the platform conducting the operation is documented, the operator is documented, but the state client directing the operation may not be.

This monitor tracks commercial operators as a distinct category with client attribution specified where possible as: **client: [attributed]** where a state or near-state client has been identified with sufficient confidence, or **client: [unattributed]** where the operator is documented but the client is not.

**In scope**: commercial operators acting on behalf of a state or near-state client — whether that client relationship is documented (Psy-Group/UAE) or assessed (Black Cube/[state client TBD]). The foreign state nexus is what brings the commercial operator within the FIMI framework.

**Out of scope**: purely commercial corporate intelligence operations with no documented state client and no political interference objective. Corporate competitor intelligence, due diligence, and executive protection are outside scope even where the methods are ethically questionable.

The attribution chain problem is acute with commercial operators because client confidentiality is a deliberate structural feature, not an incidental gap. Where the state client cannot be attributed, the monitor tracks the operation at Assessed or Possible confidence with an explicit note that the client relationship is unresolved.

---


## Cross-Monitor Signal Protocol

The FIMI Monitor functions as the **hub** in the Asymmetric Intelligence network. All six other monitors are potential recipients of FIMI-coded signals. Cross-monitor flags are issued when an operation has documented impact on another monitor's primary domain.

| Target Monitor | Trigger |
|---|---|
| [European Geopolitical & Hybrid Threat Monitor](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html) | Any confirmed Russian, Chinese, US or Israeli operation targeting EU institutions, member state elections, or NATO cohesion |
| [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html) | Any operation documented as directly interfering with an electoral process or targeting democratic institutions in a monitored country |
| [Strategic Conflict & Escalation Monitor](https://asym-intel.info/monitors/conflict-escalation/dashboard.html) | Any information operation designed to shape conflict perception, false-flag a military incident, or suppress coverage of escalation |
| [Global Environmental Risks Monitor](https://asym-intel.info/monitors/environmental-risks/dashboard.html) | State-attributed greenwashing disinformation or coordinated suppression of climate science |
| [Global Macro Monitor](https://asym-intel.info/monitors/macro-monitor/dashboard.html) | Information operations targeting financial markets, central bank credibility, or sanctions enforcement perception |
| [AI Governance Monitor](https://asym-intel.info/monitors/ai-governance/dashboard.html) | AI-generated or AI-amplified FIMI operations; disinformation targeting AI regulatory processes |

## Temporal Scope and Archive Policy

| Status | Time Since Last Activity | Treatment |
|--------|--------------------------|-----------|
| **Active** | 0–90 days | Carried in the Active Campaigns table; reviewed every Thursday |
| **Concluded / Disrupted** | 91–365 days | Retained in Campaign Archive with final status noted |
| **Historical** | Pre-2025 or 12+ months inactive | Referenced for doctrinal context only; not in Active table |

The 90-day threshold for Active status reflects the operational tempo of most sustained FIMI campaigns. A network dormant for more than 90 days may be reconstituted, but the absence of documented activity for that period is treated as a status change pending new evidence.

**Review cycle**: every Thursday update reviews all Active entries for status change. An entry moves from Active to Concluded where the operating infrastructure has been taken down and no reconstitution is documented. It moves to Disrupted where platform action or government intervention has degraded the operation without full takedown. It remains Active where new activity is documented within the 90-day window.

---

## Limitations and Known Gaps

The monitor operates on an OSINT-only basis. These limitations are structural, not provisional.

**No access to classified intelligence**: all analytical conclusions are derived from open-source material. Where classified intelligence informs public conclusions — as in Five Eyes attributions — the monitor cites the public attribution but cannot independently verify the classified basis. This is acknowledged, not corrected.

**Platform disclosure is selective**: takedown reports reflect what platforms choose to disclose, at the timing they choose, at the scale they choose to report. A platform takedown report documents one enforcement action; it does not document the full operational scope of the network disrupted. The absence of a platform disclosure does not mean the absence of activity.

**The EEAS institutional gap creates an attribution asymmetry**: Russian and Chinese operations have the deepest institutional attribution infrastructure — EEAS StratCom, Rapid Alert System, Five Eyes coverage, multiple national agencies. US and Israeli operations have fewer dedicated institutional attribution sources, meaning that operationally comparable activity is harder to attribute to Confirmed or High confidence. The monitor acknowledges this asymmetry explicitly: lower confidence levels for US and Israeli attributions reflect a structural OSINT gap, not lower operational significance.

**Commercial operator deniability is by design**: private intelligence contractors design their operations to be attributable to the client as late as possible and the contractor as early as possible. Attribution chains to state clients are routinely incomplete, and they are incomplete by architectural intention. The monitor tracks what is documented; it does not speculate on undocumented client relationships.

**Gulf state OSINT coverage is thinner**: Tier 3 and Tier 4 sources covering UAE, Saudi, and Qatari information operations are less dense than coverage of Russian, Chinese, or Iranian activity. OCCRP, Forbidden Stories, and investigative outlets carry a disproportionate share of the attribution load for Gulf actors. This means attribution for Gulf-origin operations is more frequently at Assessed or Possible confidence than for actors with deeper Tier 1–2 coverage.

**Speed vs. accuracy**: the monitor prioritises accurate attribution over fast publication. Campaign alerts are issued when time-sensitive disclosure is operationally significant, but they carry explicit confidence labelling. The weekly Thursday cadence is designed to allow sufficient review time before publication. Where a fast-moving situation requires a Possible-level publication, it is labelled as such and revisited in the subsequent weekly brief.

---

## Relationship to the EEAS FIMI Framework

The EEAS FIMI framework — produced through the StratCom Task Force, the Rapid Alert System, and the annual FIMI Reports — is the most systematic publicly available attribution framework in existence. The 4th Annual FIMI Report (March 2026) and the EEAS FIMI Explorer (interactive dashboard, March 2026) are primary sources for Russian and Chinese campaign attribution and are used for cross-referencing active campaigns.

Where this monitor's analytical conclusions diverge from EEAS conclusions, the divergence is noted explicitly in the relevant campaign entry or brief item, with the basis for divergence stated. This monitor does not treat EEAS output as authoritative beyond challenge; it treats it as the highest-quality available institutional source within its perimeter, subject to the limitations of that perimeter.

This monitor does not replicate EEAS work. Its function is to extend coverage to actors and regional dimensions outside the EEAS mandate, to apply consistent analytical standards across all actors regardless of institutional perimeter, and to operate on a faster publication cycle than annual and quarterly EEAS outputs allow. The two frameworks are complementary rather than competitive: the EEAS provides depth and institutional authority within its mandate; this monitor provides breadth and actor-consistency beyond it.

Where EEAS RAS activations, FIMI Explorer entries, or annual report attributions are directly relevant to a tracked campaign, they are cited as Tier 2 sources and weighted accordingly in the confidence framework.

---
title: "Methodology — Global FIMI & Cognitive Warfare Monitor"
description: "Analytical standards, source hierarchy, attribution confidence framework, and actor inclusion criteria for the Global FIMI & Cognitive Warfare Monitor."
date: 2026-03-30
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

**The EEAS gap — documented political choice, not structural limitation (updated 2 April 2026)**: the EEAS FIMI framework formally tracks Russian and Chinese operations within its institutional mandate. US and Israeli operations run at analytically comparable scale but are absent from the FIMI Explorer by documented political design — not as an incidental consequence of mandate scope. The EP PEGA Committee (2022–2023) documented specific operations meeting DISARM TTP criteria that were not entered into the FIMI Explorer. **Reading protocol**: "EEAS FIMI Explorer does not record this actor" ≠ "EEAS assessed this actor's operations as below threshold." It means: "EEAS has documented that this actor does not enter its institutional perimeter by political design." When citing EEAS sources on US or Israeli operations, note: "EEAS FIMI Explorer: no entry — reflects institutional perimeter by political design rather than evidentiary threshold."

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

**Distributed coordination architecture (added 2 April 2026)**: the coordination requirement applies to coordination *patterns*, not solely to identifiable coordinators. The absence of a documented command node is not evidence of absence of coordination — it is a documented architectural feature of sophisticated operations, deployed deliberately to frustrate attribution.

Where operational synchronisation across actors, platforms, or narratives exceeds plausible coincidence — consistent timing, messaging, and amplification patterns across otherwise unconnected entities — the coordination criterion can be met without a documented command structure. The analyst must demonstrate synchronisation that exceeds chance; the demonstration is of the pattern, not of the director.

The attribution form is: "coordinated network meeting FIMI four-part test; director unattributed; coordination evidenced by [specific synchronisation data]" at the appropriate confidence level.

---

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

**Spyware-as-targeting-infrastructure (added 2 April 2026)**: a distinct hybrid category from hack-and-leak. Commercial spyware (Pegasus is the reference case) deployed against political figures or civil society actors to harvest targeting data — social graphs, messaging content, movement patterns — that then informs the precision targeting of subsequent FIMI campaigns. The spyware creates a targeting intelligence layer enabling message precision that mass-broadcast FIMI cannot achieve.

In scope where: (1) deployment is against political/civil society targets in the FIMI operational environment; (2) harvested data is assessed to have informed subsequent FIMI campaign targeting; (3) at least one stage meets the standard attribution threshold.

The out-of-scope exclusion for "purely technical intrusion without an information warfare objective" does not apply — the information warfare objective is explicit, operating as the precursor stage of the FIMI pipeline. Tracked in the Attribution Log with `hybrid_type: targeting_infrastructure`.

### vs. Lobbying

Overt, registered, and lawful lobbying — where the foreign connection is disclosed and the activity is legal under applicable jurisdiction — is outside scope. Covert lobbying using undisclosed proxies, or lobbying funded by undisclosed foreign sources, satisfies the covert means criterion and is in scope. The distinction turns on disclosure: disclosed foreign lobbying is not FIMI; undisclosed foreign lobbying is.

**Legislative capture threshold (added 2 April 2026)**: the disclosure-based distinction is necessary but not sufficient. Disclosed-but-astroturfed lobbying can satisfy the FIMI four-part test (intentional, coordinated, manipulative, contrary to democratic values) even within registered lobbying structures. The operative pattern: disclosed foreign-linked funding + DISARM T0059 (astroturfing) + DISARM T0046 (search engine manipulation) + coordinated amplification infrastructure = FIMI regardless of disclosure status.

The coordination-and-manipulation threshold applies alongside the disclosure test: where a disclosed lobbying operation deploys covert amplification, manufactured grassroots support, or coordinated platform manipulation to present a foreign-backed position as organically held, it satisfies the covert means criterion through its amplification architecture. The BLOOM coalition/CSDDD legislative interference cases (EP PEGA Committee documentation) are the reference case for this threshold.

### vs. Lawfare Against Journalists

Strategic litigation against journalists and media freedom violations are tracked in the Rule of Law Monitor as domestic legal and institutional matters. They enter scope in this monitor only where they are directly in service of a documented FIMI operation — for example, legal suppression of a journalist actively investigating an attributed campaign, or foreign-state-directed litigation designed to suppress attribution reporting.

---

## Commercial Cognitive Warfare — Special Treatment

Commercial operators — NSO Group, Black Cube, Psy-Group (legacy), and their successors in the private intelligence market — require distinct methodological treatment from state actors because they introduce a structural attribution problem: the platform conducting the operation is documented, the operator is documented, but the state client directing the operation may not be.

This monitor tracks commercial operators as a distinct category with client attribution specified where possible as: **client: [attributed]** where a state or near-state client has been identified with sufficient confidence, or **client: [unattributed]** where the operator is documented but the client is not.

**In scope**: commercial operators acting on behalf of a state or near-state client — whether that client relationship is documented (Psy-Group/UAE) or assessed (Black Cube/[state client TBD]). The foreign state nexus is what brings the commercial operator within the FIMI framework.

**Out of scope**: purely commercial corporate intelligence operations with no documented state client and no political interference objective. Corporate competitor intelligence, due diligence, and executive protection are outside scope even where the methods are ethically questionable.

The attribution chain problem is acute with commercial operators because client confidentiality is a deliberate structural feature, not an incidental gap. Where the state client cannot be attributed, the monitor tracks the operation at Assessed or Possible confidence with an explicit note that the client relationship is unresolved.

### Private Emanation Sub-category (added 2 April 2026)

A distinct sub-category exists between "state actor" and "commercial operator": **private emanations of states** — entities receiving their operational existence primarily from state subsidy, exercising coercive infrastructure power at state scale, but operating outside state-level accountability frameworks.

The distinguishing characteristics are:
1. **Operational existence contingent on state subsidy**: the entity would not function at its current scale without state contractual revenue
2. **Infrastructure-level coercive power**: controls communications, data, AI capability, or surveillance infrastructure enabling suppression of political speech at scale
3. **Accountability gap**: not subject to oversight frameworks applicable to state actors despite exercising comparable operational power

**Attribution logic**: the standard commercial operator framework ("track where a state client is documented or assessed") does not apply. Private emanations are not contractors for a state client — in relevant cases they *are* the state, or are so structurally integrated into state power that the contractor/client distinction has collapsed. Attribution focuses on: documented revenue dependency on state contracts + documented deployment in information warfare contexts + documented coordination with state communications objectives.

The finding form is: "actor B, a private emanation of state A's security apparatus, deployed infrastructure C in information environment D" — not "state A directed actor B." Evidentiary standards for each element remain unchanged.

---

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

**The EEAS institutional gap creates an attribution asymmetry**: Russian and Chinese operations have the deepest institutional attribution infrastructure — EEAS StratCom, Rapid Alert System, Five Eyes coverage, multiple national agencies. US and Israeli operations have fewer dedicated institutional attribution sources, meaning that operationally comparable activity is harder to attribute to Confirmed or High confidence. The monitor acknowledges this asymmetry explicitly: lower confidence levels for US and Israeli attributions reflect a structural OSINT gap, not lower operational significance. More precisely: the EEAS asymmetry is a **documented political choice** — the FIMI Explorer's exclusion of US and Israeli operations has been documented by the EP PEGA Committee as reflecting institutional perimeter decisions, not evidentiary threshold determinations.

**Commercial operator deniability is by design**: private intelligence contractors design their operations to be attributable to the client as late as possible and the contractor as early as possible. Attribution chains to state clients are routinely incomplete, and they are incomplete by architectural intention. The monitor tracks what is documented; it does not speculate on undocumented client relationships.

**Gulf state OSINT coverage is thinner**: Tier 3 and Tier 4 sources covering UAE, Saudi, and Qatari information operations are less dense than coverage of Russian, Chinese, or Iranian activity. OCCRP, Forbidden Stories, and investigative outlets carry a disproportionate share of the attribution load for Gulf actors. This means attribution for Gulf-origin operations is more frequently at Assessed or Possible confidence than for actors with deeper Tier 1–2 coverage.

**Speed vs. accuracy**: the monitor prioritises accurate attribution over fast publication. Campaign alerts are issued when time-sensitive disclosure is operationally significant, but they carry explicit confidence labelling. The weekly Thursday cadence is designed to allow sufficient review time before publication. Where a fast-moving situation requires a Possible-level publication, it is labelled as such and revisited in the subsequent weekly brief.

---

## Relationship to the EEAS FIMI Framework

The EEAS FIMI framework — produced through the StratCom Task Force, the Rapid Alert System, and the annual FIMI Reports — is the most systematic publicly available attribution framework in existence. The 4th Annual FIMI Report (March 2026) and the EEAS FIMI Explorer (interactive dashboard, March 2026) are primary sources for Russian and Chinese campaign attribution and are used for cross-referencing active campaigns.

Where this monitor's analytical conclusions diverge from EEAS conclusions, the divergence is noted explicitly in the relevant campaign entry or brief item, with the basis for divergence stated. This monitor does not treat EEAS output as authoritative beyond challenge; it treats it as the highest-quality available institutional source within its perimeter, subject to the limitations of that perimeter.

This monitor does not replicate EEAS work. Its function is to extend coverage to actors and regional dimensions outside the EEAS mandate, to apply consistent analytical standards across all actors regardless of institutional perimeter, and to operate on a faster publication cycle than annual and quarterly EEAS outputs allow. The two frameworks are complementary rather than competitive: the EEAS provides depth and institutional authority within its mandate; this monitor provides breadth and actor-consistency beyond it.

Where EEAS RAS activations, FIMI Explorer entries, or annual report attributions are directly relevant to a tracked campaign, they are cited as Tier 2 sources and weighted accordingly in the confidence framework.

---

## CURRENT ARCHITECTURE — FIMI & Cognitive Warfare Monitor (updated 2026-04-01)

> This section was added 2026-04-01 to reflect the current production architecture.
> The publication workflow described in earlier sections references the legacy Perplexity
> deploy_website() pipeline. The current pipeline is GitHub/Hugo via asym-intel/asym-intel-main.

### Two-Pass Commit Rule (MANDATORY — all 7 monitors)

All cron outputs are written in two separate git commits to prevent silent truncation of
large JSON payloads. Never combine into one commit.

**PASS 1** — Core/fast sections: committed immediately after research completes.
**PASS 2** — Deep/slow sections: patched onto the Pass 1 JSON via:
  `gh api /repos/asym-intel/asym-intel-main/contents/[path] --jq '.content' | base64 -d`
  → modify in Python → PUT back

After Pass 2, verify ALL required top-level keys are present before proceeding to Step 3.
If any key is missing, re-run Pass 2 — do not proceed to notify.

### Publish Guard (MANDATORY — all 7 monitors)

Before writing any JSON, verify:
1. Today is the correct publish day (day-of-week check)
2. Current UTC hour is within ±3 of the scheduled publish hour
3. The existing report-latest.json does NOT already contain today's date in meta.published

If any check fails: EXIT. Do not publish. Log the reason.
"A prompt reload is NOT a reason to publish."

### Shared Intelligence Layer — Step 0B (MANDATORY — all 7 monitors)

After loading own persistent-state, BEFORE starting research:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/intelligence-digest.json \
  --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/schema-changelog.json \
  --jq '.content' | base64 -d
```

Filter intelligence-digest.json for flags relevant to this monitor's domain.
Check schema-changelog.json for any new required fields added since last run.

### Current Pipeline (GitHub/Hugo — replaces legacy deploy_website)

```bash
PUBLISH_DATE=$(date +%Y-%m-%d)
# ⚠️ Filename MUST equal PUBLISH_DATE — see anti-pattern FE-019
MONITOR_SLUG="fimi-cognitive-warfare"
REPO=/tmp/asym-intel-main

cd /tmp && rm -rf asym-intel-main
gh repo clone asym-intel/asym-intel-main asym-intel-main -- --depth=1 --quiet
cd $REPO
git config user.email "monitor-bot@asym-intel.info"
git config user.name "Monitor Bot"

# Data files (Pass 1 then Pass 2 — see Two-Pass Rule above)
# PASS 1: write core JSON
# PASS 2: patch deep sections

# Hugo brief (⚠️ filename = PUBLISH_DATE — not tomorrow or yesterday)
cat > content/monitors/fimi-cognitive-warfare/${PUBLISH_DATE}-weekly-brief.md << MDEOF
---
title: "FIMI & Cognitive Warfare Monitor — W/E {DATE}"
date: ${PUBLISH_DATE}T09:00:00Z
summary: "[lead signal summary]"
draft: false
monitor: "fimi-cognitive-warfare"
---
MDEOF

git add static/monitors/fimi-cognitive-warfare/data/
git add content/monitors/fimi-cognitive-warfare/
git commit -m "data(FCW): weekly pipeline — Issue [N] W/E ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main
```

### Schema Version

All JSON files must contain `"schema_version": "2.0"` at top level.
No future dates. No direct HTML/CSS/JS writes from cron tasks — data only.

### Monitor Accent & URLs

- Accent: #38bdf8
- Dashboard: https://asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html
- Data: https://asym-intel.info/monitors/fimi-cognitive-warfare/data/report-latest.json
- Internal spec: asym-intel/asym-intel-internal/methodology/fimi-cognitive-warfare-full.md

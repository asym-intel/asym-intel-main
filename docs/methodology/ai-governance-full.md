# Artificial Intelligence Monitor (AIM) — Full Research Methodology
## Asymmetric Intelligence · asym-intel.info
## INTERNAL — Not for publication

*Last updated: 9 April 2026*
*Editor: Peter Howitt*

---

## Source Tier Hierarchy

| Tier | Sources | Rule |
|------|---------|------|
| **T1** | Lab research blogs · arXiv/bioRxiv preprints · official regulatory texts · court filings · government gazettes · official changelogs · release notes · database update logs | **Always use.** Link directly to primary. Never link to press coverage of a T1 source. |
| **T2** | Reuters · Bloomberg · FT · The Information · Import AI (Jack Clark) · AI Snake Oil (Narayanan & Kapoor) · MLCommons · Lawfare · Politico Pro Tech · Nature News & Views · Brookings · RAND · Chatham House · IISS · RUSI · CSET · ARC Evals · METR · Apollo Research | Use only when no T1 exists |
| **T3** | The Verge · Wired · TechCrunch · Ars Technica · general tech press | Last resort. **Must flag:** `⚠️ Tier 3 source — primary not found` |

**Core rule: Never link to a press article when the primary source is publicly available.**

### T1 sources by module (priority check list)

**Modules 0–2 (Signal, Exec Insight, Model Frontier)**
arXiv (cs.AI, cs.LG, cs.CL) · openai.com/research · anthropic.com/research · deepmind.google/research · ai.meta.com/research · mistral.ai/news · huggingface.co/papers · paperswithcode.com/sota · LMArena · ARC Prize leaderboard

**Modules 3–4 (Investment, Sectors)**
Crunchbase News · PitchBook · SEC EDGAR 8-K filings (efts.sec.gov) · SAM.gov (government contracts) · SemiAnalysis · Datacenter Dynamics · AIxEnergy · Canary Media

**Modules 5–6 (EU/China Watch, AI in Science)**
EUR-Lex · EU AI Office (digital-strategy.ec.europa.eu) · State Council of PRC (english.www.gov.cn) · alphafold.ebi.ac.uk/download · deepmind.google/technologies/alphafold · anthropic.com/responsible-scaling-policy · USCC (uscc.gov) · CSET (cset.georgetown.edu) · DigiChina (digichina.stanford.edu) · arXiv q-bio.QM, physics.comp-ph · bioRxiv · medRxiv

**Modules 7–10 (Risk, Law, Governance, Standards)**
EUR-Lex · federalregister.gov · cisa.gov/news-events/alerts · nist.gov/artificial-intelligence · gov.uk/dsit · iso.org · standards.ieee.org · cencenelec.eu · etsi.org · oecd.ai · CourtListener · BAILII · CJEU · CanLII

**Modules 13–14 (Litigation, Personnel)**
CourtListener · PACER · BAILII · CJEU · CanLII · aisi.gov.uk/about · LinkedIn · Pentagon CDAO (ai.mil)

---

## Asymmetric Signal Rule

Every major development must include one **Asymmetric Signal** — a non-obvious consequence found in technical appendices, regulatory filings, niche research blogs, or academic preprints the mainstream press missed or underweighted.

**The asymmetric signal answers:** *"What does this mean in 12 months that no one is talking about yet?"*

**Required properties:**
- Specific and actionable for legal, governance, or investment professionals
- Non-obvious — if it is in every headline, it is not asymmetric
- Sourced — traceable to T1 or T2

**JSON field:** `asymmetric` on each item; also used as standalone editorial block in Module 01 items 6–10.

**Examples of good asymmetric signals:**
- "EU AI Act GPAI compute threshold (10²⁵ FLOPs) was calibrated for dense transformers — NVIDIA Nemotron 3 Super's sparse MoE architecture creates a definitional arbitrage gap."
- "AISI director moving to Anthropic signals the lab is prioritising regulatory pre-emption strategy — the person who assessed its safety posture is now internal."
- "Ciyuan appearing in State Council document signals AI tokens may be regulated as commodities — implications for export control applicability to model weights within 12 months."

---

## Friction Analysis Format

Applies to every legal/regulatory development in **Modules 9, 10, 12** and any legal development referenced in other modules.

**Format (exact):**
> **⚙️ Technical Friction:** [Law/standard] directly [complicates/enables/outpaces] [specific technical capability]. [One sentence on the practical implication.]

**Examples:**
- `⚙️ Technical Friction:` EU Omnibus watermarking deadline (November 2026) directly complicates Mistral Voxtral's real-time voice cloning at smartphone scale — hardware-level attestation that would be required does not yet exist.
- `⚙️ Technical Friction:` White House copyright position directly enables frontier model training at scale — collides with EU/UK/Brazilian frameworks that would require licensing.
- `⚙️ Technical Friction:` EU AI Act GPAI compute threshold (10²⁵ FLOPs) directly outpaces sparse MoE architecture — creates definitional arbitrage gap for Nemotron-class models.

**JSON field:** `friction_analysis` on the relevant item. For Module 9 items, also use `ihl_friction` where International Humanitarian Law is engaged.

---

## Confidence Levels

Use exactly these four values in the `confidence` field:

| Value | Meaning |
|-------|---------|
| `"Confirmed"` | Corroborated by T1 source(s) |
| `"Probable"` | Consistent with multiple T2 sources, no T1 contradiction |
| `"Uncertain"` | Single source or conflicting signals |
| `"Speculative"` | Analytical inference, no direct sourcing |

---

## Item Volume Rules — Signal over Noise

**There are no fixed item maximums per module** (except Module 00 which is always one paragraph, maximum 120 words).

Include an item if and only if it passes all four tests:
1. New this week (within the 7-day reporting window)?
2. Would a senior professional (FCA supervisor, fund manager, Anthropic researcher, FT journalist) want to know about it?
3. Does it have a primary source link?
4. Not already covered by another item in this report?

If borderline: apply the asymmetric filter. Non-obvious implication missed by mainstream press → include. Otherwise → omit.

**Module-specific guidance:**
| Module | Structure |
|--------|-----------|
| 00 Signal | Always exactly 1 paragraph, max 120 words |
| 01 Exec Insight | Always exactly 10 items (5 mainstream + 5 underweighted/asymmetric) |
| 02 Model Frontier | All confirmed lab releases, no maximum |
| 03 Investment | All rounds >$50M, no maximum — in active VC weeks may be 10+ |
| 06 AI in Science | All peer-reviewed threshold events + significant preprints, no cap |
| 13 Litigation | All cases with material activity this week |
| 14 Personnel | All confirmed movements at covered organisations |

---

## Data Lifecycle Management

**This monitor builds a cumulative intelligence picture, not a transient news feed.**

### Persistent vs Transient Data

**Treat as PERSISTENT** (remains visible until something material changes):
- Policy positions, doctrines, legal frameworks, military postures
- Baseline deviations and ongoing conflicts or campaigns
- Confirmed risk ratings and their justifications
- Standing vectors (M07), concentration index entries (M14), AISI pipeline status (M15)

**Treat as TRANSIENT** (archivable, never silently deleted):
- Single announcements, one-off events, dated statements, tactical incidents
- These may be summarised or rolled up once their implications are captured

### Update Rules

✓ Update an entry if new data **materially changes** the assessment (substance, direction, or level of concern)
✓ Update if **confidence improves** (e.g. Probable → Confirmed) or degrades
✓ Update if **source quality changes** (e.g. key claims now supported by higher-tier sources)
✗ Do NOT update merely because a week has passed
✗ Do NOT re-research and republish identical findings under new dates
✗ Do NOT delete data solely because it is old

### Version History Requirement

Every persistent entry must carry:
```json
{
  "version_history": [
    {
      "date": "YYYY-MM-DD",
      "change": "What changed",
      "reason": "Why it changed",
      "prior_value": "Previous assessment or level"
    }
  ]
}
```
Never silently overwrite a past assessment. Always create a new version entry.

### Persistent State File

The persistent-state.json file is the **living knowledge base** for this monitor. It tracks all persistent entries across modules.

**On each weekly run:**
1. Read `persistent-state.json` before running research agents
2. Pass the current persistent state to each agent as context
3. Agents update entries only when update rules are met
4. The weekly brief references this state — it does not recreate it from scratch
5. After compilation, write the updated state back to `persistent-state.json`

### Example: M07 Risk Vector

```json
{
  "vector": "Governance Fragmentation",
  "rating": "HIGH",
  "first_rated_high": "2026-03-30",
  "confidence": "Confirmed",
  "version_history": [
    {
      "date": "2026-03-30",
      "change": "Rated HIGH",
      "reason": "EU/US governance schism confirmed by EP Omnibus vote + White House nonbinding framework",
      "prior_value": null
    }
  ]
}
```

If Week 2 brings no new data on governance fragmentation, the agent does not re-rate, re-research, or re-date this entry. It simply carries forward with a note: `"unchanged_since": "2026-03-30"`.

---

## Specialist Filters

| Filter | Module | Trigger |
|--------|--------|---------|
| Science Drill-Down | 6 | Apply every week: AlphaFold, OpenAI Preparedness, Anthropic RSP, DeepMind programmes |
| Energy Wall | 3 | Apply every week: Physics-ML, Thermodynamic Computing, AI Energy Infrastructure rounds |
| Ciyuan Signal | 5 | Scan Chinese state documents for 词元 in regulatory context |
| Standards Vacuum | 5, 9 | Flag any EU amendment widening gap between obligation date and harmonised standard availability |
| Friction Analysis | 9, 10, 12 | Every legal/technical item — identify specific technical capability affected |
| AISI Pipeline | 14 | Weekly scan: senior departures UK AISI / US AISI / CAISI / EU AI Office → frontier labs |

### AISI Pipeline detail (Module 14)
Scan every week for senior departures from UK AISI, US AISI (NIST), Canadian CAISI, or EU AI Office moving to frontier labs (OpenAI, Anthropic, Google DeepMind, xAI, Meta AI, Mistral, Cohere).
Flag with `🔄 AISI Pipeline` callout.
Also flag reverse direction (lab → government) as regulatory capture risk or expertise transfer signal.

### Module 01 Executive Insight structure (fixed)
- Items 1–5: high-impact, broadly covered developments
- Items 6–10: CRITICAL — must come from technical appendices, regulatory filings, niche research blogs, or preprints the mainstream press missed. These are the Monitor's differentiating value.
Always exactly 10 items.

---

## Cross-Monitor Scan

**Before compiling the report JSON, scan the public dashboards of all other monitors on asym-intel.info.**

### What to include in `cross_monitor_flags`

Each flag must:
- Name the other monitor(s) by their self-described domain on asym-intel.info
- Link to their public dashboard URL
- Describe the overlap in 2–4 sentences: what links the domains, why it matters, whether it is transient or structural
- State the Artificial Intelligence Monitor's specific perspective on the linkage
- Carry an `id`, `status` (Active / Monitoring / Closed), `type`, `first_flagged`, and `version_history`

### No-signal case

If no material cross-monitor signals exist in a given period, include the section with a single note stating so. The section must be present in every issue — it may never be omitted.

### Privacy rule

Only reference public data, public dashboards, and public methodology pages. Never expose internal prompts, private workflows, or non-public operational details in cross-monitor flag descriptions.

---

## Module Research Table

| # | Module | Key Sources | Forensic Filter |
|---|--------|-------------|-----------------|
| 00 | The Signal | All modules | Editorial judgment |
| 01 | Executive Insight | All Tier 1/2 | Underweighted items from appendices/filings/preprints |
| 02 | Model Frontier | Lab blogs, HF Leaderboard, LMArena, Papers With Code | Architectural innovations, capability jumps |
| 03 | Investment & M&A | Crunchbase, SEC EDGAR, SAM.gov, SemiAnalysis | Energy Wall filter |
| 04 | Sector Penetration | Lab blogs, FT, Bloomberg, govt announcements | Stealth deployments |
| 05 | European & China | EUR-Lex, EU AI Office, USCC, CSET, DigiChina, State Council | Ciyuan + Standards Vacuum |
| 06 | AI in Science | arXiv, bioRxiv, Nature, Science, AlphaFold notes | Science Drill-Down |
| 07 | Risk Indicators | CISA, DoD, RAND, Brookings | Five vectors |
| 08 | Military AI | SAM.gov, DARPA, AFRL, DSTL, DIU, CDAO | IHL friction |
| 09 | Law & Litigation | **Full research** — law (EU AI Act, US federal/state law, international), technical standards (CEN-CENELEC, NIST, ISO), and active litigation. EU AI Act 7-layer tracker. Country Grid. Regulatory obligation timelines. Standards Vacuum filter applied. | Agent D (add to brief) |
| 10 | AI Governance | OECD AI, UNESCO, G7/G20, lab RSP/Preparedness | Soft law → binding law signals |
| 11 | Ethics | Lab ethics pages, ACM FAccT, FTC, Colorado AG | Accountability friction |
| 12 | Information Operations | EUvsDisinfo, EU DisinfoLab, Stanford Internet Observatory, DFRLab, NCSC advisories, Meta/Google/X transparency reports, Graphika, CISA | FIMI + synthetic media + state actor attribution |
| 13 | AI & Society | ILO, OECD Employment, McKinsey Global Institute, Pew Research, academic labour economics (NBER, IZA), national stats bureaux | Labour displacement + inequality + public trust + demographic impacts |
| 14 | AI & Power Structures | SemiAnalysis, Datacenter Dynamics, SEC EDGAR (ownership filings), FTC/DOJ competition actions, CSET, Brookings AI governance, academic political economy | Compute concentration + infrastructure control + regulatory capture |
| 15 | Personnel | LinkedIn, AISI staff pages, EU AI Office, Pentagon CDAO | AISI-to-Lab Pipeline |

---

## Per-Module Research Briefs

These are standing instructions for each research agent. Each module must be researched against named sources every week — not just searched broadly. "No material developments" is only acceptable if the sources have been checked and genuinely returned nothing within the 7-day window.

### M00 — The Signal
**What:** Single editorial paragraph ≤120 words identifying the single most strategically significant development of the week — not the most covered.
**Sources:** Synthesis of all 15 modules. Pick the item with the highest asymmetric signal-to-noise ratio.
**Standard:** Must be something a senior intelligence or policy professional would not have found in mainstream press.

### M01 — Executive Insight (always exactly 10 items)
**What:** 5 mainstream items (widely covered but strategically important) + 5 underweighted items (signal-quality, missed or under-covered by mainstream press).
**Sources for underweighted:** arXiv/bioRxiv preprints, regulatory filings (EUR-Lex, SEC EDGAR, Federal Register), lab technical appendices and system cards, NIST/ISO drafts, parliamentary committee evidence, academic working papers (NBER, SSRN).
**Standard:** Each underweighted item must have a Tier 1/2 source and must not appear in mainstream tech press.

### M02 — Model Frontier
**Standing weekly checks:**
- Hugging Face release feed (hf.co/models, sorted by recent)
- Papers With Code state-of-the-art leaderboards
- Lab blogs: openai.com/research, anthropic.com/research, deepmind.google/research, mistral.ai/news, ai.meta.com/blog
- arXiv cs.LG and cs.CL new submissions (past 7 days)
- LMArena (lmarena.ai) leaderboard changes
**Signal items:** New model releases, architecture innovations, benchmark records, capability jumps, open-weight releases with permissive licences (especially Apache 2.0).
**Flag:** Models from Chinese labs (⚠️ if Tier 3 only), models trained on domestic chips (export control signal).

### M03 — Investment & M&A
**Standing weekly checks:**
- Crunchbase funding alerts (AI sector, >$50M threshold)
- SEC EDGAR Form D filings (AI companies)
- SAM.gov contract awards (AI-related, >$10M)
- Pitchbook / Bloomberg funding announcements
- Reuters/FT M&A coverage
**Energy Wall secondary sweep:** Beyond >$50M threshold, search specifically for: liquid cooling, data center thermal management, nuclear PPA announcements, behind-the-meter power, grid interconnection queue movements, AI chip packaging/cooling, physical compute infrastructure.
**Standard:** Every round >$50M within the 7-day window. No exceptions for "boring" sectors — the most asymmetric signals are often in infrastructure.

### M04 — Sector Penetration
**Sectors to cover every week:** Healthcare · Legal · Finance · Defence · Media · Education · Critical Infrastructure.
**Standing sources per sector:**
- Healthcare: HIStalk, Fierce Healthcare, HLTH, Rock Health, FDA AI/ML device list, CMS reimbursement updates
- Legal: Law.com/ALM, Legal Tech News, Harvey/Clio/Legora blogs, ABA Tech Report
- Finance: Fintech Futures, FinTech Global, FinTech Weekly, Finextra, BIS working papers
- Defence: DefenseScoop, C4ISRNET, SAM.gov, DARPA BAAs, Breaking Defense
- Media: Reuters Institute, Pew Journalism, INMA, FutureMedia
- Education: EdSurge, FutureEd, Curriculum Associates, state DOE AI policy trackers
- Critical Infrastructure: CISA advisories, EIA energy data, NERC, Datacenter Dynamics
**Required per sector:** Status (Accelerating / Stalling / Emerging), capability-to-deployment gap, at least one stealth flag.

### M05 — European & China Watch
**EU standing weekly checks:**
- EUR-Lex new publications (AI Act, Digital Services Act, Data Act amendments)
- EU AI Office website (euaioffice.europa.eu)
- European Parliament press releases (AI-tagged)
- CEN-CENELEC JTC21 standards tracker (artificialintelligenceact.eu/standard-setting-overview/)
- European Commission DG CONNECT news
- EU Digital Policy newsletter / MLex (Tier 2)
**Standards Vacuum flag trigger:** Any week where harmonised standards are still in draft AND a compliance deadline is within 90 days.
**China standing weekly checks:**
- DigiChina (Stanford CISAC) — digichina.stanford.edu
- CSET — cset.georgetown.edu
- USCC — uscc.gov/research
- South China Morning Post tech section
- Chinese Ministry of Science and Technology (most.gov.cn) — English summaries
- Xinhua technology feed
**Ciyuan flag trigger:** Any state-level speech or policy document using ciyuan (词元) framing, token-export metrics, or token-denomination proposals.

### M06 — AI in Science
**Science Drill-Down — mandatory weekly checks (run every issue regardless of news):**
1. AlphaFold Database changelog (alphafold.ebi.ac.uk) — flag any volume update or new complex type
2. OpenAI Preparedness scorecard (deploymentsafety.openai.com) — flag any tier change
3. Anthropic RSP threshold triggers (anthropic.com/news) — flag any ASL change
4. DeepMind programme updates: AlphaFold, AlphaGenome, AlphaEvolve, WeatherNext, GNoME
5. arXiv cs.AI + q-bio + physics.bio-ph — threshold events (autonomous research, AI-authored papers, novel architectures)
**Sources:** Nature, Science, Cell, NEJM (AI papers), bioRxiv, arXiv, EMBL-EBI news, NIH Reporter, DOE Office of Science
**Threshold event standard:** A development that changes the pace or nature of scientific discovery itself (not just a new application).

### M07 — Risk Indicators: 2028
**Five vectors — mandatory every issue:**
1. **Governance Fragmentation:** Track EU/US/UK/China regulatory divergence. Sources: EUR-Lex, Federal Register, DSIT, Cyberspace Administration of China
2. **Cyber Escalation:** CISA KEV catalog (new additions), NCSC advisories, Wiz/Mandiant/CrowdStrike threat intelligence, BIS/CISA joint advisories
3. **Platform Power:** FTC/DOJ/EU DG COMP competition actions, lab acquisition announcements, infrastructure lock-in signals
4. **Export Controls:** BIS Federal Register notices, Commerce Department press releases, Applied Materials/ASML/TSMC filings, Reuters/Bloomberg chip export coverage
5. **Disinfo Velocity:** EEAS FIMI tracker, EU DisinfoLab weekly update, Stanford Internet Observatory, NewsGuard, DFRLab, Reuters fact-check feed
**Rating scale:** HIGH / ELEVATED / WATCH / VACUUM. Must be justified with at least one primary source per vector.

### M08 — Military AI Watch
**Standing weekly checks:**
- SAM.gov contract awards: search "artificial intelligence", "autonomous systems", "machine learning" >$10M
- DARPA programme announcements (darpa.mil/news)
- CDAO (Chief Digital and AI Office) releases (ai.mil)
- DefenseScoop, Breaking Defense, C4ISRNET
- AFRL (Air Force Research Laboratory) news
- DSTL (UK Defence Science and Technology Laboratory) releases
- NATO ACT (Allied Command Transformation) publications
- Jane's Defence (Tier 2)
**IHL friction:** Required for every capability or doctrine item. Assess against DoD Directive 3000.09 "meaningful human control" standard and ICRC autonomous weapons guidance.

### M09 — Law & Litigation
**Standing weekly checks:**
- EUR-Lex: new EU AI Act implementing acts, delegated acts, guidance documents
- EU AI Office: new opinions, decisions, guidance (digital-strategy.ec.europa.eu)
- CEN-CENELEC JTC21: standards progress (artificialintelligenceact.eu/standard-setting-overview/)
- Federal Register: FTC, FDA, FCC, HHS, EEOC AI-related rules and guidance
- Westlaw/LexisNexis AI litigation tracker (via public court filings: PACER, CourtListener)
- NIST AI publications (nist.gov/artificial-intelligence)
- ISO/IEC JTC 1/SC 42 AI standards tracker
- State AI legislation: National Conference of State Legislatures AI tracker, Transparency Coalition tracker
**EU AI Act 7-layer tracker:** Update all 7 layers every issue: (1) AI Act Text, (2) Delegated/Implementing Acts, (3) Harmonised Standards CEN-CENELEC JTC21, (4) GPAI Code of Practice, (5) National Enforcement NCAs, (6) AI Office Supervisory Decisions, (7) Digital Omnibus Trilogue.
**Standards Vacuum:** Flag active if compliance obligation deadline is within 90 days and harmonised standards not yet in Official Journal.

### M10 — AI Governance
**Standing weekly checks:**
- OECD AI Policy Observatory (oecd.ai) — new policy publications
- UNESCO AI Ethics (unesco.org/en/artificial-intelligence)
- G7/G20 AI working group outputs (hiroshima-process.org)
- Lab RSP/Preparedness documents: anthropic.com/news, openai.com/safety, deepmind.google/safety
- Council of Europe AI Treaty implementation tracker
- Partnership on AI (partnershiponai.org) publications
**Signal items:** Changes to voluntary commitments (downgrade = high signal), new soft law instruments, binding → non-binding transitions, governance gaps where no framework applies.

### M11 — Ethics & Accountability
**Standing weekly checks:**
- ACM FAccT, AIES, AAAI ethics track papers (proceedings and preprints)
- AI Now Institute (ainowinstitute.org) publications
- Algorithmic Justice League (ajl.org)
- FTC AI enforcement actions (ftc.gov/news-events)
- Colorado AG AI enforcement (coag.gov)
- Lab ethics/safety pages: anthropic.com/safety, openai.com/safety, deepmind.google/safety
- Accountability friction: check every lab public commitment against recent behaviour for gaps
**Required per item:** Accountability friction analysis — explicit assessment of the gap between stated commitment and observed action.

### M12 — Information Operations
**Standing weekly checks:**
- EEAS FIMI tracker and weekly reports (eeas.europa.eu/FIMI)
- EU DisinfoLab weekly update (disinfo.eu)
- DFRLab (Atlantic Council) publications (dfrlabs.medium.com, atlanticcouncil.org/DFRLab)
- Stanford Internet Observatory (io.stanford.edu)
- Graphika reports (graphika.com)
- NewsGuard AI tracking (newsguardtech.com)
- CISA foreign influence operations advisories
- Meta, Google, X/Twitter transparency reports and adversarial threat reports
- NCSC (UK) and BfV (Germany) state actor attribution advisories
**Required per item:** Actor type (state/non-state), region, platform response, detection method.
**Capability Watch:** Flag any new AI tool or capability entering FIMI workflows for the first time.

### M13 — AI & Society
**Standing weekly checks:**
- ILO Monitor on World of Work (ilo.org/research)
- OECD Employment Outlook AI chapter updates (oecd.org/employment)
- NBER working papers on AI and labour (nber.org — search "artificial intelligence")
- IZA Discussion Papers (iza.org/publications)
- Pew Research Center (pewresearch.org — AI and society)
- McKinsey Global Institute (mckinsey.com/mgi) AI reports
- World Economic Forum Future of Jobs tracker
- FutureEd AI in education legislative tracker (future-ed.org)
- Rock Health consumer AI surveys (rockhealth.com)
- Bureau of Labor Statistics occupational employment data (when AI-relevant)
- Academic journals: Journal of Economic Perspectives, Labour Economics, Work, Employment & Society
**Required categories every week:** Labour (displacement, job entry, occupational exposure), Education (policy, AI literacy, deployment), Public Trust (survey data, governance perceptions), Social Cohesion (inequality, demographic impacts, community effects).
**Standard:** "No material developments" is never acceptable for this module. Labour market data, education policy, and public trust surveys are published continuously. If no new primary research, surface the most relevant recent academic preprint.

### M14 — AI & Power Structures
**Standing weekly checks:**
- SemiAnalysis (semianalysis.com) — compute infrastructure
- Datacenter Dynamics (datacenterdynamics.com)
- BloombergNEF AI infrastructure tracker
- SEC EDGAR: ownership filings for major AI companies (OpenAI/Anthropic secondary markets via Form D)
- FTC/DOJ/EU DG COMP competition actions (antitrust, merger review)
- CSET (cset.georgetown.edu) — compute concentration, talent concentration
- Energy finance: Wood Mackenzie, BloombergNEF energy transition
- Revolving door: check CSPAN, LinkedIn, press releases for AI lab → government and government → AI lab movements
**Concentration Index:** Update the 5-domain table every issue (Compute/GPU, Foundation Models, AI Infrastructure, AI Applications, AI Safety/Oversight).

### M15 — Personnel & Org Watch
**AISI Pipeline — priority scan every issue:**
- UK AI Security Institute (gov.uk/government/organisations/ai-security-institute) — staff page, GOV.UK press releases
- US AISI (nist.gov/aisi) — staff changes, LinkedIn
- Canadian CAISI
- EU AI Office (digital-strategy.ec.europa.eu/en/policies/ai-office) — staff directory
- Also reverse direction: lab → regulator movements
**Lab movements:**
- LinkedIn: search "{person name} joined {lab}" for OpenAI, Anthropic, DeepMind, Meta AI, xAI, Mistral, Cohere
- Business Insider AI talent tracker, TechCrunch personnel coverage
- Lab official announcements and blog posts
**Government AI bodies:**
- CDAO (ai.mil), DARPA director changes, NSF AI Institute appointments
- DSIT (UK), BEIS AI team, EU AI Office senior appointments
**Required per person:** role_from, role_to, type (departure/appointment/internal), significance, asymmetric signal. Flag all Tier 3 sources.

---

## Analytical Upgrades — EU AI Act 2026

### FM-AGM-01: Benchmark Saturation — Capability Signal Hierarchy

Benchmark scores (MMLU, HumanEval, GSM8K) are unreliable capability signals in 2026 due to saturation. Apply capability signal hierarchy in priority order: (1) Novel capability domain crossing; (2) Autonomous agent performance on SWE-bench/GAIA/RE-Bench; (3) Training compute above 10²⁶ FLOPs (GPAI systemic risk territory); (4) Open-weight releases with permissive licences; (5) Chinese lab releases (apply maximum epistemic caution: chineseLab:true, evaluationAccess:limited). Only report benchmark scores when accompanied by a novel capability demonstration or compute threshold event.

### FM-AGM-02: Chinese Lab Capability Claims — T3 Source Rule

Chinese lab press releases claiming parity with or superiority over Western frontier models are T3 sources for capability assessment. Require third-party independent evaluation (Hugging Face leaderboard, academic benchmark replication, or Western security organisation assessment) before scoring capability level.

### FM-AGM-03: Voluntary Commitment Downgrade Detection

Every issue, check whether any lab has quietly revised its safety commitment documents downward. 'Downgrade' of a safety commitment (RSP, Preparedness scorecard) is an M10+M11 item and must be flagged under accountabilityFriction. Downward revisions are frequently made without announcement.

### FM-AGM-04: Standards Vacuum — Must Appear Every Issue

The EU AI Act Standards Vacuum is currently ACTIVE (no harmonised standards in OJ as of Q1 2026; compliance deadline August 2026). Include in M09 every issue with: current status + days remaining until compliance deadline. Do not let it become invisible through repetition. Downgrade to MONITORING only when at least one harmonised standard is published in the Official Journal.

---

## Country Grid Rules

### Inclusion threshold
Promote a country from Watch to the full Country Grid when **any one** of these thresholds is met:
- Draft AI-specific law published
- Public consultation on AI regulation opened
- Binding guidance issued

### Persistence in the grid
Country Grid entries are **persistent**. Once included, they remain until the status materially changes. Do not remove an entry because a week has passed without developments.

### Change flags (weekly)
Every country in the grid must carry a weekly change flag:
- `🆕` — new entry this week (threshold just met)
- `⚠️` — material status change this week
- `—` — no change this week

### Country Grid Watch
Maintain a separate `country_grid_watch` section for countries approaching but not yet meeting the threshold. Promote from Watch when the threshold is met. Add new countries when a credible signal of approaching regulatory action is detected.

---

## Persistence Rules

### Classification

**Persistent** — carry forward until material change:
- Policy, law, regulatory postures, doctrine
- Active litigation cases
- Country Grid entries
- Lab safety policies, RSP/Preparedness Framework commitments
- Treaty negotiations and ongoing enforcement sequences
- Baseline deviations with Confirmed/Probable status

**Transient** — include when fresh, archive once implications captured:
- Single announcements, one-off events, tactical incidents, dated statements
- Archive after 3 weeks if implications rolled into a persistent entry

**Archived** — excluded from rendered report but retained in JSON:
- Transient items >3 weeks old whose context is captured in a persistent entry

### Update rules

**Update an entry when:**
- New data materially changes the assessment (substance, direction, or concern level)
- Confidence improves or degrades
- Source quality improves (key claims now corroborated by T1)
- Status changes (litigation advances, law enacted, standard published)

**Do NOT update when:**
- A week has passed with no meaningful new data
- Re-research finds the same findings
- The only change is the date — identical findings must not be republished under a new date

### version_history requirement

Every persistent item must carry a `version_history` array. Minimum fields per entry:

```json
{
  "version": 1,
  "date": "YYYY-MM-DD",
  "change": "Description of what changed",
  "reason": "Why this counts as a material change",
  "prior_value": null
}
```

**Never silently overwrite** a past assessment. Always create a new version entry.

### Required lifecycle fields (every item in every module)

```json
{
  "persistence": "persistent | transient | archived",
  "confidence": "Confirmed | Probable | Uncertain | Speculative",
  "episode_status": "active | closed | new | ongoing | updated",
  "first_seen": "YYYY-MM-DD",
  "last_material_change": "YYYY-MM-DD",
  "version_history": [
    { "version": 1, "date": "YYYY-MM-DD", "change": "...", "reason": "...", "prior_value": null }
  ]
}
```

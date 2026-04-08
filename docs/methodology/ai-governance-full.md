# Artificial Intelligence Monitor (AIM) — Full Research Methodology
## Asymmetric Intelligence · asym-intel.info
## INTERNAL — Not for publication

*Last updated: 2026-04-08*
*Editor: Peter Howitt*

---

# Artificial Intelligence Monitor (AIM) — Asymmetric Intelligence
# Weekly Publication Cron Instructions

**Site:** asym-intel.info (static, deployed via deploy_website)  
**Project path:** `/home/user/workspace/asym-intel/`  
**Cron:** Fires on **Friday at 18:00 CEST** (16:00 UTC).  
**Ramparts cron ID:** `8a7e73c5` — **DO NOT TOUCH**

---

## Critical Rules

1. **NEVER modify `/home/user/workspace/ramparts-v2/`** or any file within it
2. **NEVER modify Ramparts cron ID `8a7e73c5`**
3. **NEVER reuse the Ramparts WordPress Application Password**
4. This task publishes to **asym-intel.info only**
5. Content source: **always independent research** — do not use Ramparts data

---

## Content Source Strategy

**Always: Option A — independent research.**  
This monitor conducts its own research independently. Do not use Ramparts data as a content source.

Run 4 parallel research agents as described below.

---

## Pre-flight

1. Check `/home/user/workspace/asym-intel/data/archive.json` — note the last published issue number
2. Set reporting window: today (Friday) minus 7 days
3. Launch 4 parallel research agents (see Research section below)

---

## Cross-Monitor Scan

**Before compiling the report JSON, scan the public dashboards of all other monitors on asym-intel.info.**

### How to scan

1. Fetch the public dashboard and/or latest brief for each monitor at `https://asym-intel.info/monitors/[slug]/dashboard.html`
2. Known slugs (treat as a starting point — new monitors may appear; check `https://asym-intel.info/monitors/` for the current list):
   - `conflict-escalation` — Strategic Conflict & Escalation Monitor
   - `democratic-integrity` — Democratic Integrity
   - `environmental-risks` — Global Environmental Risks & Planetary Boundaries Monitor
   - `european-strategic-autonomy` — European Strategic Autonomy
   - `fimi-cognitive-warfare` — Global FIMI & Cognitive Warfare
   - `macro-monitor` — Macro Monitor
3. For each monitor, look for: shared actors, campaigns, narratives, theatres, platforms, or structural conditions where their domain materially affects, or is affected by, AI governance developments.
4. Apply lifecycle rules: update a flag only if new data materially changes the linkage or its status. Do not re-describe unchanged structural connections under a new date.

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

## Research

**Agent A:** Modules 0, 1, 2 — The Signal, Executive Insight, Model Frontier  
**Agent B:** Modules 3, 4 — Investment (Energy Wall filter), Sector Penetration  
**Agent C:** Modules 5, 6 — European & China Watch (Ciyuan/Standards Vacuum), AI in Science (Science Drill-Down)  
**Agent D:** Modules 7, 8, 9–11, 12–15 — Risk, Military, Law & Litigation (full research: law + standards + litigation + EU AI Act 7-layer tracker), Governance, Ethics, Info Ops, AI & Society, Power Structures, Personnel (AISI Pipeline)

Each agent saves to: `/home/user/workspace/asym-intel/research/week-[DATE]-mod-[X].md`

Apply all forensic filters:
- Science Drill-Down (AlphaFold, OpenAI preparedness, Anthropic RSP, DeepMind)
- Energy Wall (Physics-ML, Thermodynamic Computing, AI Energy Infrastructure)
- Ciyuan / Standards Vacuum (China state commodity framing, EU compliance gap)
- AISI-to-Lab Pipeline (AISI/CAISI/EU AI Office → frontier lab movements)
- Friction Analysis (Technical Friction Point for every legal/standards item)

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

The file `/home/user/workspace/asym-intel/data/persistent-state.json` is the **living knowledge base** for this monitor. It tracks all persistent entries across modules.

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

## Compile Report JSON

Generate `/home/user/workspace/asym-intel/data/report-[YYYY-MM-DD].json` following the schema of `report-latest.json`.

**Branding:**
- `meta.editor`: `"Peter Howitt, asym-intel.info"`
- No cross-links to Ramparts or external sites in meta or module_0
- No Gibraltar Observatory section (asym-intel does not have gibraltar.html)

---

## Update report-latest.json

```bash
cp /home/user/workspace/asym-intel/data/report-[YYYY-MM-DD].json \
   /home/user/workspace/asym-intel/data/report-latest.json
```

---

## Update Archive

Prepend to `/home/user/workspace/asym-intel/data/archive.json`:

```json
{
  "slug": "YYYY-MM-DD",
  "week_label": "DD–DD Month YYYY",
  "published": "YYYY-MM-DD",
  "volume": 1,
  "issue": [increment from last],
  "editors_signal_preview": "[first 2 sentences of The Signal]",
  "top_signals": ["signal 1", "signal 2", "signal 3", "signal 4", "signal 5"]
}
```

---

## Deploy

```python
deploy_website(
  project_path="/home/user/workspace/asym-intel/",
  site_name="Artificial Intelligence Monitor — Asymmetric Intelligence",
  entry_point="index.html",
  should_validate=False
)
```

---

## Notify

Send notification with:
- Title: `Artificial Intelligence Monitor — Issue [N] · [Week Label]`
- Body: The Signal text + top 5 delta items + deployed URL

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

## Quality Checklist

- [ ] Module count correct (16)
- [ ] All page navs consistent
- [ ] `report-latest.json` updated
- [ ] `archive.json` prepended
- [ ] All source links `target="_blank" rel="noopener"`
- [ ] Primary source links verified (not press articles)
- [ ] Tier 3 sources flagged `⚠️ Tier 3 source — primary not found`
- [ ] All 4 forensic filters applied
- [ ] No arbitrary item caps
- [ ] No Ramparts cross-links present — verify grep result: `grep -i ramparts` returns nothing
- [ ] Dark mode functional
- [ ] Mobile layout intact
- [ ] GitHub publish step completed (dashboard.html + weekly digest pushed to asym-intel/asym-intel-main)

---

## FINAL STEP — Publish dashboard, Hugo digest, and JSON pipeline

After completing all updates, run the following using the bash tool with `api_credentials=["github"]`:

```bash
PUBLISH_DATE=$(date +%Y-%m-%d)
WEEK_ENDING=$(date +"%d %B %Y")
MONITOR_SLUG="ai-governance"
REPO_DIR=/tmp/asym-intel-main
DATA_DIR=$REPO_DIR/static/monitors/$MONITOR_SLUG/data

# ── Step 0: Load persistent state BEFORE researching ─────────────────────────
# (Do this before running research agents, not here — included for completeness)
# cat $DATA_DIR/persistent-state.json

# ── Clone repo ────────────────────────────────────────────────────────────────
cd /tmp && rm -rf asym-intel-main
gh repo clone asym-intel/asym-intel-main asym-intel-main -- --depth=1 --quiet
cd asym-intel-main
git config user.email "monitor-bot@asym-intel.info"
git config user.name "Monitor Bot"

mkdir -p $DATA_DIR
mkdir -p static/monitors/$MONITOR_SLUG/assets
mkdir -p content/monitors/$MONITOR_SLUG

# ── Step 1: Copy dashboard files ─────────────────────────────────────────────
cp /home/user/workspace/asym-intel/report.html       static/monitors/$MONITOR_SLUG/dashboard.html
cp /home/user/workspace/asym-intel/archive.html      static/monitors/$MONITOR_SLUG/archive.html
cp /home/user/workspace/asym-intel/about.html        static/monitors/$MONITOR_SLUG/about.html
cp /home/user/workspace/asym-intel/digest.html       static/monitors/$MONITOR_SLUG/digest.html
cp /home/user/workspace/asym-intel/search.html       static/monitors/$MONITOR_SLUG/search.html
cp /home/user/workspace/asym-intel/methodology.html  static/monitors/$MONITOR_SLUG/methodology.html
cp -r /home/user/workspace/asym-intel/assets/.       static/monitors/$MONITOR_SLUG/assets/

# ── Step 2: Write Hugo digest ─────────────────────────────────────────────────
cat > content/monitors/$MONITOR_SLUG/${PUBLISH_DATE}-weekly-digest.md << MDEOF
---
title: "Artificial Intelligence Monitor — Week of ${WEEK_ENDING}"
date: ${PUBLISH_DATE}T18:00:00Z
summary: "[One sentence: the single most strategically significant AI development this week]"
draft: false
monitor: "ai-governance"
---

## The Signal

[Single editorial paragraph from module_0.body — the week's most strategically important development]

## Top 5 underweighted signals

### [Signal title]
[Paragraph with source link]

### [Signal title]
[Paragraph with source link]

### [Signal title]
[Paragraph with source link]

### [Signal title]
[Paragraph with source link]

### [Signal title]
[Paragraph with source link]

## Module highlights

[Key developments from all 16 modules — bold module name, one sentence each]

## Asymmetric flags

[Top asymmetric signals — non-obvious implications for next 12 months]

---

*Full issue: [Artificial Intelligence Monitor](https://asym-intel.info/monitors/ai-governance/dashboard.html)*
MDEOF

# ── Step 3: Write Hugo methodology page ──────────────────────────────────────
cp /home/user/workspace/asym-intel/content-methodology.md    content/monitors/$MONITOR_SLUG/methodology.md

# ── Step 4: Write JSON pipeline files ────────────────────────────────────────
# 4a. Write report-latest.json (full structured content — built from compiled report JSON)
cp /home/user/workspace/asym-intel/data/report-latest.json $DATA_DIR/report-latest.json

# 4b. Write dated archive copy (never modified after creation)
cp /home/user/workspace/asym-intel/data/report-latest.json $DATA_DIR/report-${PUBLISH_DATE}.json

# 4c. Prepend to archive.json (append-only — do NOT replace existing entries)
# Read existing archive, prepend new entry, write back
python3 << PYEOF
import json, os
data_dir = os.environ.get('DATA_DIR', '$DATA_DIR')
archive_path = f"{data_dir}/archive.json"
report_path = f"{data_dir}/report-latest.json"

with open(archive_path) as f:
    archive = json.load(f)
with open(report_path) as f:
    report = json.load(f)

meta = report.get("meta", {})
new_entry = {
    "issue": meta.get("issue"),
    "volume": meta.get("volume"),
    "week_label": meta.get("week_label"),
    "published": meta.get("published"),
    "slug": meta.get("published"),
    "signal": report.get("module_0", {}).get("body", ""),
    "source_url": report.get("source_url", ""),
    "delta_strip": report.get("delta_strip", [])[:5]
}

# Only prepend if not already present (idempotency)
if not archive or archive[0].get("published") != new_entry["published"]:
    archive.insert(0, new_entry)
    with open(archive_path, "w") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
    print(f"archive.json updated: {len(archive)} entries")
else:
    print(f"archive.json already has entry for {new_entry['published']}")
PYEOF

# 4d. Update persistent-state.json (carry forward unchanged; update what changed)
cp /home/user/workspace/asym-intel/data/persistent-state.json $DATA_DIR/persistent-state.json

# ── Step 5: Commit and push everything ───────────────────────────────────────
git add static/monitors/$MONITOR_SLUG/
git add content/monitors/$MONITOR_SLUG/
git commit -m "content: Artificial Intelligence Monitor week of ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main

echo "✓ Dashboard: https://asym-intel.info/monitors/$MONITOR_SLUG/dashboard.html"
echo "✓ Digest: https://asym-intel.info/monitors/$MONITOR_SLUG/${PUBLISH_DATE}-weekly-digest/"
echo "✓ Methodology: https://asym-intel.info/monitors/$MONITOR_SLUG/methodology/"
echo "✓ JSON: https://asym-intel.info/monitors/$MONITOR_SLUG/data/report-latest.json"
echo "✓ Archive: https://asym-intel.info/monitors/$MONITOR_SLUG/data/archive.json"
```

**Rules:**
- Do NOT copy `index.html` — Hugo serves its own section page
- Never link to perplexity.ai URLs in the digest body
- The network bar is injected automatically — do NOT add it manually
- The `summary` field is what appears on the homepage feed card — make it specific
- Populate the digest body with real content, not placeholder text
- `report-{date}.json` is never modified after creation
- `archive.json` is append-only — never replace existing entries
- `cross_monitor_flags`: carry all forward; add new; never delete (use `status: "Resolved"`)
- Every change to `persistent-state.json` requires a `version_history` entry
- Add to notification body: "JSON pipeline: report-latest.json, report-{date}.json, archive.json ({N} issues), persistent-state.json — all updated"
---

*This document is the single source of truth for the asym-intel.info cron publication workflow.*

---

## CURRENT ARCHITECTURE — Artificial Intelligence Monitor (updated 2026-04-01)

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
MONITOR_SLUG="ai-governance"
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
cat > content/monitors/ai-governance/${PUBLISH_DATE}-weekly-brief.md << MDEOF
---
title: "Artificial Intelligence Monitor — W/E {DATE}"
date: ${PUBLISH_DATE}T09:00:00Z
summary: "[lead signal summary]"
draft: false
monitor: "ai-governance"
---
MDEOF

git add static/monitors/ai-governance/data/
git add content/monitors/ai-governance/
git commit -m "data(AGM): weekly pipeline — Issue [N] W/E ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main
```

### Schema Version

All JSON files must contain `"schema_version": "2.0"` at top level.
No future dates. No direct HTML/CSS/JS writes from cron tasks — data only.

### Monitor Accent & URLs

- Accent: #3a7d5a
- Dashboard: https://asym-intel.info/monitors/ai-governance/dashboard.html
- Data: https://asym-intel.info/monitors/ai-governance/data/report-latest.json
- Internal spec: asym-intel/asym-intel-internal/methodology/ai-governance-full.md

---

## ANALYTICAL UPGRADES — EU AI Act 2026 + GPAI Code of Practice (added 2 April 2026)

### FM-AGM-01: Benchmark Saturation — Capability Signal Hierarchy

Benchmark scores (MMLU, HumanEval, GSM8K) are unreliable capability signals in 2026 due to saturation. Apply capability signal hierarchy in priority order: (1) Novel capability domain crossing; (2) Autonomous agent performance on SWE-bench/GAIA/RE-Bench; (3) Training compute above 10²⁶ FLOPs (GPAI systemic risk territory); (4) Open-weight releases with permissive licences; (5) Chinese lab releases (apply maximum epistemic caution: chineseLab:true, evaluationAccess:limited). Only report benchmark scores when accompanied by a novel capability demonstration or compute threshold event.

### FM-AGM-02: Chinese Lab Capability Claims — T3 Source Rule

Chinese lab press releases claiming parity with or superiority over Western frontier models are T3 sources for capability assessment. Require third-party independent evaluation (Hugging Face leaderboard, academic benchmark replication, or Western security organisation assessment) before scoring capability level.

### FM-AGM-03: Voluntary Commitment Downgrade Detection

Every issue, check whether any lab has quietly revised its safety commitment documents downward. 'Downgrade' of a safety commitment (RSP, Preparedness scorecard) is an M10+M11 item and must be flagged under accountabilityFriction. Downward revisions are frequently made without announcement.

### FM-AGM-04: Standards Vacuum — Must Appear Every Issue

The EU AI Act Standards Vacuum is currently ACTIVE (no harmonised standards in OJ as of Q1 2026; compliance deadline August 2026). Include in M09 every issue with: current status + days remaining until compliance deadline. Do not let it become invisible through repetition. Downgrade to MONITORING only when at least one harmonised standard is published in the Official Journal.


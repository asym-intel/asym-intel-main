# World Democracy Monitor — Full Internal Methodology

**Monitor slug:** democratic-integrity  
**Last updated:** 2026-03-30  
**Published by:** Ramparts.gi / compossible.blog  
**Update cadence:** Every Monday, 08:00 CEST  
**Canonical dashboard:** https://asym-intel.info/monitors/democratic-integrity/dashboard.html

---

## 1. Purpose

Real-time institutional radar sitting on top of the annual democracy indices. Detects leading indicators of democratic backsliding 6–18 months before V-Dem, Freedom House, and IDEA register them in their annual updates. Publishes weekly to asym-intel.info and the Perplexity dashboard.

---

## 2. Data Architecture

All monitor data is stored in a single JSON file at:
`/home/user/workspace/democracy_monitor_YYYY-MM-DD.json`

### JSON sections

| Section | Type | Update method |
|---------|------|---------------|
| `heatmap[]` | Array | Direct HTML update each week |
| `headline` | Object | Direct HTML update |
| `institutional_pulse[]` | Array | Direct HTML update |
| `electoral_watch` | Object | Direct HTML update |
| `digital_civil` | Object | Direct HTML update |
| `autocratic_export` | Object | Direct HTML update |
| `state_capture` | Object | Direct HTML update |
| `watch_list[]` | Array | Direct HTML update |
| `institutional_integrity` | Object | Direct HTML update |
| `monthly_trend` | Object | Calculated from history |
| `legislative_watch.entries[]` | Array | **JS-rendered** — update JSON |
| `research_360.friction_notes[]` | Array | **JS-rendered** — update JSON |
| `weekly_brief` | String | Direct HTML update |

**JS-rendered sections** (legislative_watch and friction_notes) are embedded as JSON in the HTML page and rendered by client-side JavaScript. To update them, update the JSON file then inject the new JSON array into the correct `var entries = [...]` and `var notes = [...]` blocks in the HTML.

---

## 3. Severity Scoring Rubric

**Formula: Score = A + B + C + (2.5 − D)**  
Final score rounded to nearest 0.5, capped 1–10.

### Dimension A — LDI Trajectory
| Value | Meaning |
|-------|---------|
| 0 | Stable / improving |
| 1.0 | Gradual decline |
| 2.0 | Steep decline |
| 2.5 | Collapse-speed |

Source: V-Dem LDI annual score change; Freedom House direction

### Dimension B — Institutional Breadth
Pillars: judiciary, legislature, civil service, press, civil society, elections

| Value | Pillars under attack |
|-------|---------------------|
| 0 | 0–1 |
| 1.0 | 2–3 |
| 2.0 | 4–5 |
| 2.5 | All 6 |

### Dimension C — Repression Severity
| Value | Level |
|-------|-------|
| 0 | None documented |
| 0.5 | Harassment / administrative |
| 1.0 | Mass arrests |
| 2.0 | Killings |
| 2.5 | Mass killings / massacres |

Source: Amnesty International, HRW, HRANA, CPJ primary documentation

### Dimension D — Resilience (INVERTED — high resilience lowers total score)
| Value | Level |
|-------|-------|
| 0 | No resilience — subtracts 0 from total |
| 0.5 | Weak |
| 1.0 | Moderate |
| 1.5 | Significant |
| 2.0 | Strong |
| 2.5 | Robust |

Source: Courts, civil society, legislature, press functioning as checks

### Direction arrows
- ↑ Worsening week-on-week
- → Stable  
- ↓ Improving

### Status thresholds
- **Rapid Decay:** score determined by rubric; requires 2+ institutional pillars under attack
- **Recovery:** Rapid Decay country with net positive trajectory; severity score reflects residual fragility
- **Watch List:** 2+ leading indicators; promoted to Rapid Decay when score >5.0 on two consecutive weeks
- **Escalation trigger:** explicit specific development required for Watch List → Rapid Decay promotion

---

## 4. Five-Tier Source Hierarchy

### Tier 1 — Institutional & Diplomatic (The "Official" View)
- UN OHCHR country pages
- OSCE/ODIHR election reports and legal opinions
- Venice Commission opinions (authoritative on electoral and constitutional reform)
- European Parliament plenary votes and resolutions
- International IDEA Global State of Democracy indices
- National government statements and legislative texts

### Tier 2 — Quantitative Indices (The "Benchmark" View)
- V-Dem Democracy Report (annual, March) — LDI, EDI, autocratization coding
- V-Dem Dataset Archive — raw country-year data, 400+ indicators
- **V-Dem Annual Calibration Addendum** — read alongside this methodology at Step 0B each year:
  `asym-intel-internal/methodology/democratic-integrity-vdem-{YEAR}.md`
  Current file: `democratic-integrity-vdem-2026.md` (Dataset v16, through 2025, effective 2026-03-28)
  Contains: LDI anchors, ERT episode flags, Watchlist countries, Dimension A calibration table.
  V-Dem lag rule: treat as structural baseline (12–18 month lag), not current conditions.
  Next update: March 2027 (V-Dem Dataset v17).
- Freedom House Freedom in the World (annual) — Free/Partly Free/Not Free
- EIU Democracy Index (annual)
- **International IDEA Democracy Tracker** — 173 countries, 29 indices, monthly updates (primary early-warning layer)
- RSF World Press Freedom Index (annual)
- Freedom House Freedom on the Net (annual)
- **Global Terrorism Index** (IEP, annual, March) — state fragility leading indicator for Africa/Latin America/Asia

### Tier 3 — Investigative & Independent Media (The "Ground Truth")
- The Guardian — Democracy coverage
- ProPublica — US executive branch, judiciary, civil service
- Haaretz — Israel judicial reform, democratic erosion
- +972 Magazine — Israeli-Palestinian ground truth
- The Wire — India (BJP, NDTV/Adani, FCRA)
- El Faro — Latin America (Bukele, foreign agent laws)
- Lawfare Media — US rule of law, DOJ, judiciary
- IPI Press Freedom Alerts — journalist attacks, media capture, EMFA violations

### Tier 4 — Human Rights & Civic Oversight (The "Accountability" View)
- Amnesty International country pages
- Human Rights Watch World Report and country dispatches
- CIVICUS Monitor — civic space ratings and incident database
- Access Now #KeepItOn — internet shutdown tracking
- CPJ Imprisoned Journalists Database
- ISHR — UN NGO Committee access tracking
- HRANA — Iran detention and execution data

### Tier 5 — Think Tanks & Strategic Analysis (The "Expert" View)
- Carnegie Endowment — Democracy Program (Eastern Europe, Latin America, Africa)
- **Carnegie Endowment Africa Democracy** — required for Sub-Saharan Africa coverage
- Journal of Democracy (NED)
- Chatham House — Democracy & Governance
- Brookings Institution — Governance & Rule of Law
- Verfassungsblog — European constitutional law (EMFA, Article 7, judicial independence)
- openDemocracy — dark money, Russian funding networks, anti-gender movements
- Democratic Erosion Consortium — academic case studies
- OSW (Centre for Eastern Studies) — Serbia, Poland, Belarus, Russia, Eastern Europe
- **Atlantic Council Africa** — required for Sub-Saharan Africa coverage
- compossible.blog — conceptual framework development

---

## 5. Geographic Scouting Requirements

The cron must actively scout three regions that are structurally under-tracked by European-focused news sources:

### Sub-Saharan Africa
Required sources: CIVICUS Monitor Africa updates, Carnegie Endowment Africa Democracy, Atlantic Council Africa, Amnesty Africa
Key countries to check every week: Benin, Tanzania, Uganda, Côte d'Ivoire, Nigeria, South Africa, DRC, Sahel juntas (Mali, Burkina Faso, Niger)

### Latin America
Required sources: Amnesty International Americas, Global Terrorism Index (Latin America section), CIVICUS Americas, El Faro
Key countries: Colombia (GTI signal), Venezuela (transition fragility), Brazil (Bolsonarismo), Argentina (Milei), El Salvador (Bukele model export)

### Institutional Integrity Signals (upstream)
Required sources: International IDEA Democracy Tracker (monthly), V-Dem disaggregated sub-indicators
Four signals to track: judicial independence, electoral administration integrity, civil service politicisation, intelligence community misuse

---

## 6. Sections That Require Weekly Updates

### Always update
- `heatmap[]` — all country notes, severity scores, and direction arrows
- `headline.rapid_decay[]` and `headline.recovery[]` — top 5 entries
- `headline.silent_erosion` — single most important procedurally invisible development
- `headline.history[]` — append new week entry
- `monthly_trend` — recalculate from history
- `weekly_brief` — 600–1,200 words, up to 10 numbered items (see §8)

### Update when new evidence warrants
- `institutional_pulse[]` — add new institutional events; update existing
- `electoral_watch` — update environment and positive_transitions
- `digital_civil` — update closing_space and pushback lists
- `autocratic_export` — update matrix, transnational_repression, turnarounds
- `state_capture` — update sector_capture, media_timeline

### Review every week, update when status changes
- `legislative_watch.entries[]` — update status_code; add new bills/EOs; archive resolved
- `research_360.friction_notes[]` — review each: resolved? escalated? add new
- `institutional_integrity.indicators[]` — update signals; mark resolved
- `watch_list[]` — add new countries at 2+ triggers; promote to heatmap if >5.0 ×2

---

## 7. Legislative Watch Entry Schema

```json
{
  "id": "country-shortname-year",
  "country": "",
  "week": "YYYY-MM-DD",
  "name": "",
  "status": "Proposed | In Committee | Signed into Law | In Force",
  "status_code": "proposed | committee | signed",
  "tags": ["election_adjacent", "civil_society", "media_regulation", "constitutional_change", "anti_ngo", "lawfare"],
  "official_justification": "",
  "analytic_concern": "",
  "democratic_impact": "",
  "lawfare_angle": "",
  "election_adjacent": true,
  "fimi_link": false,
  "regional_mimicry": "" ,
  "source": "",
  "overlap": []
}
```

Set `fimi_link: true` when the legislative action is accompanied by documented foreign information operations.

---

## 8. Critical Friction Note Schema

```json
{
  "country": "",
  "week": "YYYY-MM-DD",
  "tier1_source": "",
  "tier1_claim": "",
  "ground_truth": "",
  "ground_truth_tiers": ["3", "4"],
  "ground_truth_sources": "",
  "status": "Active | Resolved",
  "resolution_note": "",
  "overlap": []
}
```

Move to `research_360.friction_archive[]` with `status: "Resolved"` and `resolution_note` when the discrepancy is resolved.

---

## 9. Weekly Intelligence Brief Requirements

The brief must cover ALL ten dimensions (combine where naturally related):
1. V-Dem / quantitative scores — what the numbers reveal this week
2. Networks coordination events — CPAC, NatCon, RNR, or other far-right network activity
3. Legislative Watch — most significant new bills/EOs/regulatory actions
4. Media Capture — three-phase analysis, new developments
5. Watch List — threshold changes, new entries
6. Critical Friction — sharpest official vs. ground-truth divergences
7. Electoral Watch — upcoming elections, environment changes
8. Severity gradient insights — Resilience Paradox, acceleration patterns
9. Autocratic Export / Transnational Repression — network patterns, model spread
10. Recovery / Positive Deviants — where democratic repair is happening

**Format:** Numbered items with ALL-CAPS bold lead sentence. Named reports hyperlinked to primary source URLs. Minimum 600 words; target 900–1,200 words.

---

## 10. Publication Workflow

### Step 1 — Update Perplexity dashboard
- Update `/home/user/workspace/democracy-monitor-2026-03-24/index.html`
- Deploy to: `/home/user/workspace/democracy-monitor-2026-03-24/` (fixed path — preserves public sharing)
- Site name: "World Democracy Monitor — [D Month YYYY]"

### Step 2 — Publish to asym-intel.info (public repo: asym-intel/asym-intel-main)
```bash
gh repo clone asym-intel/asym-intel-main
# Dashboard (raw HTML, no network bar — injected centrally)
cp index.html static/monitors/democratic-integrity/dashboard.html
# Brief (Hugo markdown)
cat > content/monitors/democratic-integrity/YYYY-MM-DD-weekly-brief.md
# Footer link MUST be: https://asym-intel.info/monitors/democratic-integrity/dashboard.html
# NEVER link to perplexity.ai in published content
git commit -m "content: WDM dashboard and brief YYYY-MM-DD"
git push origin main
```

### Step 3 — Save methodology to internal repo (asym-intel/asym-intel-internal)
```bash
gh repo clone asym-intel/asym-intel-internal
cp methodology-full.md methodology/democratic-integrity-full.md
git commit -m "methodology: update democratic-integrity YYYY-MM-DD"
git push origin main
```

---

## 11. CSS Font Size Rule

Any new CSS blocks added to the dashboard must use scaled values:
- Body / card text: **15.6px**
- Notes / secondary text: **14.4px**
- Labels / badges: **13.2px**
- Never use raw 12px / 11px / 13px values

---

## 12. Current Baseline State (30 March 2026)

- **Rapid Decay:** 15 countries (Philippines added 30 Mar)
- **Recovery:** 4 countries (South Korea, Romania, Bolivia, Poland)
- **Watch List:** 9 countries (Italy, UK, Bangladesh, Israel, India, Mexico, Benin, Colombia, Côte d'Ivoire)
- **Legislative Watch:** 11 entries
- **Active Friction Notes:** 5
- **Institutional Integrity Signals:** 6 active
- **High-risk elections:** Hungary Apr 12, Benin Apr 12, BiH Oct 4, Uganda Nov, US Nov 3, Serbia Dec

---

## 13. Data Lifecycle Management

**Version:** 1.0  **Established:** 2026-03-31

This monitor produces a cumulative intelligence picture, not a transient news feed. Old items do not disappear simply because time has passed.

### Entry Types

| Type | Meaning | Lifecycle rule |
|------|---------|----------------|
| **Persistent** | Structural data: legal frameworks, military postures, ongoing campaigns, doctrine shifts | Stays visible until material change, invalidation, or resolution |
| **Episode** | Bounded event sequence with defined start | Stays visible until resolution; then archived with `closed_date` and `resolution_summary` |
| **Transient** | Single announcement, one-off incident, dated statement | May be rolled up or summarised once implications are fully captured. Never deleted — moved to archive. |

### Confidence Levels

| Level | Meaning |
|-------|---------|
| **Confirmed** | Corroborated by 2+ independent Tier 2–4 sources |
| **Probable** | Single strong Tier 2–4 source, or multiple Tier 5 sources |
| **Reported** | Single Tier 3–4 source, not yet independently corroborated |

Confidence upgrades (Probable → Confirmed) and downgrades both trigger a changelog entry.

### Changelog Format

Every material change must be logged. Never silently overwrite past assessments.

```json
{
  "date": "YYYY-MM-DD",
  "change": "What changed — specific, concise",
  "reason": "Why this constitutes a material change",
  "source": "Primary source name and date"
}
```

### Update Rules

**✓ Update an entry when:**
- New data materially changes the assessment substance, direction, or level of concern
- Confidence improves (Probable → Confirmed) or degrades
- Source quality changes (claims now supported by higher-tier sources)
- Status changes (Watch List → Rapid Decay, Recovery designation changes)
- A new law passes, an election occurs, or a previously threatened action is executed

**✗ Do not update when:**
- A week has passed without new material information
- The same findings would be republished under a new date with no substantive change
- Data is old but the underlying situation is unchanged
- Only the phrasing would be refreshed

### Example Application

| Week | Signal | Action |
|------|--------|--------|
| Week 1 | "SAVE Act advancing in Congress — In Committee [Probable]" | Create entry |
| Week 2 | Same status, no new votes or amendments | **NO UPDATE** — do not republish |
| Week 3 | SAVE America Act (more restrictive version) passes House | **UPDATE** — material escalation; log changelog entry: "SAVE America Act passed House February 2026"; upgrade to Confirmed |
| Week 4 | Senate fails to take up bill | **UPDATE** — status change; log: "Senate inaction — bill stalled ahead of recess"; update `status_code` |

### Archive Process

When an Episode or Transient entry resolves:
1. Set `status: "Archived"` (heatmap) or `status_code: "archived"` (legislative)
2. Add `closed_date: "YYYY-MM-DD"`
3. Add `resolution_summary: "one sentence describing how it resolved"`
4. Append final changelog entry
5. Move from active array to corresponding `_archive` array (e.g. `legislative_watch.archive[]`, `research_360.friction_archive[]`)
6. Do NOT delete — archived entries remain in the JSON for historical analysis

### Weekly Brief Relationship

The brief must reference the evolving knowledge base, not recreate it from scratch. The correct framing:
- "Georgia's new March 2026 laws [confirmed, Changelog v2]..." — not re-narrating Week 1 context
- "The Venezuela friction note has been updated [Week 2→Week 3]..." — referencing the continuity
- "The US Schedule F entry remains unchanged this week — no material developments beyond what was documented on 24 March" — explicitly noting stability, not silently omitting

### Field Requirements by Section

| Section | Required lifecycle fields |
|---------|--------------------------|
| `heatmap[]` entries | `confidence`, `entry_type`, `first_seen`, `last_material_change`, `changelog[]` |
| `watch_list[]` entries | `confidence`, `first_seen`, `last_material_change`, `changelog[]` |
| `legislative_watch.entries[]` | `first_seen`, `last_material_change`, `changelog[]` |
| `research_360.friction_notes[]` | `first_seen`, `changelog[]` |
| `institutional_integrity.indicators[]` | `week` (existing), add `confidence` |

### Schema Version

The JSON file includes a top-level `schema_version` field. Current: `"2.0"` (lifecycle management introduced 2026-03-31). Increment to 2.1 if the schema changes materially.

---

## CURRENT ARCHITECTURE — World Democracy Monitor (updated 2026-04-01)

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
MONITOR_SLUG="democratic-integrity"
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
cat > content/monitors/democratic-integrity/${PUBLISH_DATE}-weekly-brief.md << MDEOF
---
title: "World Democracy Monitor — W/E {DATE}"
date: ${PUBLISH_DATE}T06:00:00Z
summary: "[lead signal summary]"
draft: false
monitor: "democratic-integrity"
---
MDEOF

git add static/monitors/democratic-integrity/data/
git add content/monitors/democratic-integrity/
git commit -m "data(WDM): weekly pipeline — Issue [N] W/E ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main
```

### Schema Version

All JSON files must contain `"schema_version": "2.0"` at top level.
No future dates. No direct HTML/CSS/JS writes from cron tasks — data only.

### Monitor Accent & URLs

- Accent: #61a5d2
- Dashboard: https://asym-intel.info/monitors/democratic-integrity/dashboard.html
- Data: https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json
- Internal spec: asym-intel/asym-intel-internal/methodology/democratic-integrity-full.md

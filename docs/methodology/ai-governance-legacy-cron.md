# AIM Legacy Cron Instructions — ARCHIVED
# These are the old Computer cron publication instructions, superseded by the
# GA pipeline (collector → weekly-research → reasoner → synthesiser → publisher).
# Retained for reference only. Do not use for new development.
# Archived: 9 April 2026

---

# Artificial Intelligence Monitor (AIM) — Asymmetric Intelligence
# Weekly Publication Cron Instructions (LEGACY)

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

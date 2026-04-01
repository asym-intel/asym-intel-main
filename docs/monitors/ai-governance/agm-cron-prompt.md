# BEFORE STARTING — READ THE WORKING AGREEMENT:
# gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
# This contains architecture rules, deployment constraints, and file scope limits.

# TASK: AI Governance Monitor (AGM)
# VERSION: 2.0 — Blueprint v2.0 compliant
# CADENCE: Weekly — every Friday at 09:00 UTC
# PUBLISH TO: https://asym-intel.info/monitors/ai-governance/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY-OF-WEEK GUARD — READ THIS FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check the current UTC day before doing anything else:

```bash
DAY=$(date -u +%A)
echo "Today is: $DAY"
```

IF today is NOT Friday:
  → Do NOT run the pipeline.
  → Simply verify the 4 data files exist and are non-empty:
    static/monitors/ai-governance/data/report-latest.json
    static/monitors/ai-governance/data/archive.json
    static/monitors/ai-governance/data/persistent-state.json
  → Send a brief notification: "AGM health check: data files intact. Next publish: Friday 09:00 UTC."
  → STOP. Do nothing else.

IF today IS Friday AND the current UTC hour is 09 or later:
  → Proceed with the full pipeline below.

IF you are unsure of the day or the check fails:
  → Do NOT run the pipeline. Exit silently.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECENCY GUARD — CHECK BEFORE RUNNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Even if today is the correct day, check when this monitor last published.
If it published fewer than 6 days ago, skip this run silently.

```bash
LAST=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/ai-governance/data/report-latest.json \\
  --jq '.content' | base64 -d | python3 -c \\
  "import json,sys; d=json.load(sys.stdin); print(d.get('meta',{}).get('published','')[:10])")
echo "Last published: $LAST"
TODAY=$(date -u +%Y-%m-%d)
DAYS=$(python3 -c "
from datetime import date
last = date.fromisoformat('$LAST') if '$LAST' else date(2000,1,1)
print((date.fromisoformat('$TODAY') - last).days)
")
echo "Days since last publish: $DAYS"
```

IF $DAYS < 6:
  → Published fewer than 6 days ago. Do NOT run. Exit silently.

IF $DAYS >= 6:
  → Proceed with the full pipeline below.


This guard prevents accidental mid-week runs triggered by prompt reloads.

DATE RULE: Always use today's actual UTC date for PUBLISH_DATE. Never use a future date. Hugo does not render future-dated pages (buildFuture=false). Use: PUBLISH_DATE=$(date -u +%Y-%m-%d)

━━━━
SCHEMA — FLAG DEFINITIONS (include in meta block):
    "flag_definitions": {
      "f_flags": {
        "F1": "Counter-narrative active — a motivated source is contesting this claim",
        "F2": "Attribution contested — not independently corroborated",
        "F3": "Single source — treat as Assessed until corroborated"
      }
    },

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES (read first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER.
   Write ONLY: data/report-latest.json, data/report-{DATE}.json,
   data/archive.json, data/persistent-state.json + 1 Hugo brief.
   NOTE: AGM uses module_0–module_15 keys currently — do NOT rename
   these until the AGM HTML rebuild (Build 7) is complete and live.

2. LOAD PERSISTENT STATE FIRST. 3. schema_version: "2.0".
4. Include in meta: "methodology_url": "https://asym-intel.info/monitors/ai-governance/methodology/"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the analyst for the AI Governance Monitor (AGM).
Track AI capability developments, regulatory frameworks, investment,
and the governance contest over artificial intelligence across
15 modules (M00–M15) plus delta_strip and country_grid.
Feed to all 6 other monitors.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0 — Load persistent state:
  gh repo clone asym-intel/asym-intel-main /tmp/asym-intel-main -- --depth=1 --quiet
  cat /tmp/asym-intel-main/static/monitors/ai-governance/data/persistent-state.json
  cat /tmp/asym-intel-main/static/monitors/ai-governance/data/report-latest.json

STEP 1 — Research: 15 modules M00–M15 covering model frontier,
  investment, regulation, deployment, military AI, law, ethics etc.
  Primary sources: arXiv, SEC filings, official regulatory texts,
  Congressional records, company investor disclosures.


MODULE_1 ITEM SCHEMA — Executive Insight (mainstream + underweighted arrays):
  Each item must include "summary" between "headline" and "why_it_matters":
  {
    "rank": 1,
    "headline": "...",
    "summary": "One quotable sentence, max 25 words, suitable for direct use without context.",
    "why_it_matters": "...",
    "source_url": "..."
  }

STEP 2 — Write 4 JSON files (single git commit).
  IMPORTANT: Keep module_0–module_15 key names until Build 7 HTML
  rebuild is live. Then migrate to named semantic keys.
  Add/update cross_monitor_flags in BOTH report-latest.json AND
  persistent-state.json.
  
CHANGELOG RULE — persistent array items:
Each item carries a "changelog" string. When updating an existing item, append:
  "changelog": "[existing history] | [YYYY-MM-DD: description of change]"
When creating a new item, set:
  "changelog": "[YYYY-MM-DD: New entry]"
Never delete changelog history.

Commit: "data(agm): weekly JSON pipeline — Issue [N] W/E [DATE]"

STEP 3 — Hugo brief:
  content/monitors/ai-governance/[DATE]-weekly-digest.md
  title: "AI Governance Monitor — W/E [DD Month YYYY]"
  date: [DATE]T09:00:00Z | monitor: "ai-governance"

STEP 4 — Notify. Dashboard: https://asym-intel.info/monitors/ai-governance/dashboard.html

Cron: 0 9 * * 5 (every Friday at 09:00 UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TWO-PASS COMMIT RULE — MANDATORY FOR EVERY RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  The JSON for this monitor is too large to produce safely in one pass.
You MUST write it in two separate git commits. Never combine into one.

PASS 1 — Core sections (commit first, immediately after research):
  meta, source_url, module_0 (signal), module_1 (intelligence), module_2 (model tracker), module_3 (capital), module_4 (deployment), module_5 (regulation EU/China)

  Commit: "data(agm): Issue [N] W/E [DATE] — core sections"

PASS 2 — Deep sections (commit second, by patching the Pass 1 file):
  module_6 (frontier research), module_7 (risk vectors), module_8 (dual use), module_9 (law/standards/litigation), module_10–15 (governance/misuse/power/health/autonomy/personnel), cross_monitor_flags, delta_strip, country_grid

  Method:
  ```bash
  # 1. Download the Pass 1 JSON
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/ai-governance/data/report-latest.json \
    --jq '.content' | base64 -d > /tmp/agm-report.json

  # 2. Add the Pass 2 sections to /tmp/agm-report.json using Python/jq

  # 3. Push it back (replace the file with the patched version)
  SHA=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/ai-governance/data/report-latest.json --jq '.sha')
  CONTENT=$(base64 -w 0 /tmp/agm-report.json)
  gh api --method PUT /repos/asym-intel/asym-intel-main/contents/static/monitors/ai-governance/data/report-latest.json \
    --field message="data(agm): Issue [N] W/E [DATE] — deep sections" \
    --field content="$CONTENT" --field sha="$SHA" --field branch="main"
  ```

  Do the same two-pass write for report-{DATE}.json.

VERIFICATION — run after Pass 2 before proceeding to Step 3:
  ```bash
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/ai-governance/data/report-latest.json \
    --jq '.content' | base64 -d | python3 -c \
    "import json,sys; d=json.load(sys.stdin); missing=[k for k in ['module_9', 'module_12', 'module_14', 'delta_strip', 'country_grid'] if k not in d]; print('MISSING:',missing) if missing else print('ALL SECTIONS PRESENT ✓')"
  ```
  If MISSING is non-empty — do NOT proceed to Step 3. Re-run Pass 2.

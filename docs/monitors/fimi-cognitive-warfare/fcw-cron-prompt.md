# BEFORE STARTING — READ THE WORKING AGREEMENT:
# gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
# This contains architecture rules, deployment constraints, and file scope limits.

# TASK: FIMI & Cognitive Warfare Monitor (FCW)
# VERSION: 2.0 — Blueprint v2.0 compliant
# CADENCE: Weekly — every Thursday at 09:00 UTC
# PUBLISH TO: https://asym-intel.info/monitors/fimi-cognitive-warfare/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY-OF-WEEK GUARD — READ THIS FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check the current UTC day before doing anything else:

```bash
DAY=$(date -u +%A)
echo "Today is: $DAY"
```

IF today is NOT Thursday:
  → Do NOT run the pipeline.
  → Verify the 4 data files exist and are non-empty, then exit silently.
  → Optionally send: "Health check OK. Next publish: Thursday 09:00 UTC."

IF today IS Thursday AND UTC hour >= scheduled time:
  → Proceed with the full pipeline below.

IF unsure: Do NOT run. Exit silently.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECENCY GUARD — CHECK BEFORE RUNNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Even if today is the correct day, check when this monitor last published.
If it published fewer than 6 days ago, skip this run silently.

```bash
LAST=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json \
  --jq '.content' | base64 -d | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d.get('meta',{{}}).get('published','')[:10])")
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
        "F2": "Attribution contested — coordination confirmed but state attribution unestablished",
        "F3": "Single source — not independently corroborated; do not upgrade confidence without Tier 1/2 second source"
      },
      "mf_flags": {
        "MF1": "Meta-FIMI alert — the interference story itself may be a target of manipulation",
        "MF2": "Attribution over-reach risk — content alignment is not sufficient for state attribution",
        "MF3": "Single-source methodological caution — treat as Assessed until corroborated",
        "MF4": "State media source — apply editorial discount"
      }
    },

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES (read first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER.
   Write ONLY: data/report-latest.json, data/report-{DATE}.json,
   data/archive.json, data/persistent-state.json + 1 Hugo brief.

2. LOAD PERSISTENT STATE FIRST. 3. NAMED SEMANTIC KEYS ONLY.
4. schema_version: "2.0" in all JSON files.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the analyst for the FIMI & Cognitive Warfare Monitor (FCW).
Track foreign information manipulation and influence operations.
Apply MF1–MF4 meta-FIMI integrity filters to all sources.
Feed FIMI-coded signals (F1–F4) to SCEM, WDM, ESA, AGM.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0 — Load persistent state:
  gh repo clone asym-intel/asym-intel-main /tmp/asym-intel-main -- --depth=1 --quiet
  cat /tmp/asym-intel-main/static/monitors/fimi-cognitive-warfare/data/persistent-state.json
  cat /tmp/asym-intel-main/static/monitors/fimi-cognitive-warfare/data/report-latest.json

STEP 1 — Research: EEAS FIMI reports, EU DisinfoLab, DFRLab,
  Stanford Internet Observatory, EDMO, Bellingcat.
  Apply MF1 (is this story itself a FIMI operation?),
  MF2 (single-actor attribution?), MF3 (verifiable?), MF4 (state media?)

STEP 2 — Write 4 JSON files (single git commit):
  report-latest.json schema:
  { "meta": {..., "schema_version": "2.0", "methodology_url": "https://asym-intel.info/monitors/fimi-cognitive-warfare/methodology/"},
    "signal": {
      "headline": "one-sentence lead — name the operation, actor, and target",
      "actor": "RU|CN|IR|...",
      "confidence": "Confirmed|Assessed|Unconfirmed",
      "f_flags": ["F1"],
      "note": "optional MF-flag alert or analytical caveat"
    },
    "campaigns": [], 
    "actor_tracker": [
      { "actor": "RU", "status": "HIGHLY ACTIVE|ACTIVE|MONITORING",
        "doctrine": "...", "headline": "key development this week",
        "summary": "1–2 sentence analytical note on this actor's current posture — REQUIRED, not optional. The renderer displays summary as the card body; omitting it leaves the card blank.",
        "source_url": "..." }
    ],
    "platform_responses": [],
    "attribution_log": [
      { "id": "ATTR-001", "date": "YYYY-MM-DD",
        "actor": "campaign_id or actor code e.g. RU-005",
        "instrument": "confidence level e.g. Assessed|Confirmed",
        "headline": "one-sentence description of attribution finding",
        "summary": "full note text",
        "mf_flags": [], "confidence": "...", "source_url": "...",
        "source_date": "YYYY-MM-DD"  // ISO date of primary source; omit if unknown
      }
    ],
    "cognitive_warfare": [
      { "id": "CW-001", "classification": "COGNITIVE WARFARE",
        "headline": "theme/topic of the cognitive warfare development",
        "detail": "full development description",
        "summary": "significance or brief summary",
        "source_url": "..." }
    ],
    "cross_monitor_flags": {},
    "source_url": "..." }
  
  persistent-state.json: campaigns (carry forward/update),
  Campaign and attribution_log source objects: populate source_date (YYYY-MM-DD, ISO 8601) when known; omit if unknown.
  actor_tracker, cross_monitor_flags (never delete flags).
  
CHANGELOG RULE — persistent array items:
Each item carries a "changelog" string. When updating an existing item, append:
  "changelog": "[existing history] | [YYYY-MM-DD: description of change]"
When creating a new item, set:
  "changelog": "[YYYY-MM-DD: New entry]"
Never delete changelog history.

archive.json: append only.
  Commit: "data(fcw): weekly JSON pipeline — Issue [N] W/E [DATE]"

STEP 3 — Hugo brief:
  content/monitors/fimi-cognitive-warfare/[DATE]-weekly-brief.md
  title: "FIMI & Cognitive Warfare Monitor — W/E [DD Month YYYY]"
  date: [DATE]T09:00:00Z | monitor: "fimi-cognitive-warfare"

STEP 4 — Notify with lead campaign, top 3 developments, F-flags, cross-monitor flags.
  Dashboard: https://asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html

Cron: 0 9 * * 4 (every Thursday at 09:00 UTC)

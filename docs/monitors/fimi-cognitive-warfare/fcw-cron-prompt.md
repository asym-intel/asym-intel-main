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
    "campaigns": [
      {
        "id": "FCW-001",
        "operation_name": "...",
        "start_date": "YYYY-MM-DD",  // date operation first observed/confirmed; REQUIRED for timeline visualisation
        "status": "ACTIVE|ONGOING|DISRUPTED|ASSESSED|RESOLVED",
        "attribution_confidence": "Confirmed|Assessed|Unconfirmed",
        "actor": "RU|CN|IR|...",
        "platform": "YouTube|Telegram|X|...",
        "target": "freetext — country/election/institution targeted",
        "summary": "...",
        "last_activity": "YYYY-MM-DD",
        "f_flags": [],
        "changelog": "[YYYY-MM-DD: New entry]",
        "source_url": "..."
      }
    ],
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
  
  persistent-state.json: campaigns (carry forward/update — IMPORTANT: when adding a new campaign,
  always set start_date to the first observed/confirmed date. This field is required for the
  campaign timeline visualisation on the dashboard. For existing campaigns missing start_date,
  backfill with best available date and note in changelog.),
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TWO-PASS COMMIT RULE — MANDATORY FOR EVERY RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  The JSON for this monitor is too large to produce safely in one pass.
You MUST write it in two separate git commits. Never combine into one.

PASS 1 — Core sections (commit first, immediately after research):
  meta, signal, campaigns, actor_tracker, platform_responses, source_url

  Commit: "data(fcw): Issue [N] W/E [DATE] — core sections"

PASS 2 — Deep sections (commit second, by patching the Pass 1 file):
  attribution_log, cognitive_warfare, cross_monitor_flags

  Method:
  ```bash
  # 1. Download the Pass 1 JSON
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json \
    --jq '.content' | base64 -d > /tmp/fcw-report.json

  # 2. Add the Pass 2 sections to /tmp/fcw-report.json using Python/jq

  # 3. Push it back (replace the file with the patched version)
  SHA=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json --jq '.sha')
  CONTENT=$(base64 -w 0 /tmp/fcw-report.json)
  gh api --method PUT /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json \
    --field message="data(fcw): Issue [N] W/E [DATE] — deep sections" \
    --field content="$CONTENT" --field sha="$SHA" --field branch="main"
  ```

  Do the same two-pass write for report-{DATE}.json.

VERIFICATION — run after Pass 2 before proceeding to Step 3:
  ```bash
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json \
    --jq '.content' | base64 -d | python3 -c \
    "import json,sys; d=json.load(sys.stdin); missing=[k for k in ['attribution_log', 'cognitive_warfare'] if k not in d]; print('MISSING:',missing) if missing else print('ALL SECTIONS PRESENT ✓')"
  ```
  If MISSING is non-empty — do NOT proceed to Step 3. Re-run Pass 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0B — READ SHARED INTELLIGENCE LAYER (before research)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After loading your own persistent-state.json, read these two shared files:

```bash
# Cross-monitor intelligence digest (compiled weekly by housekeeping cron)
# Filters for flags relevant to FCW (either targeting or sourced from this monitor)
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/intelligence-digest.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
abbr='fcw'
flags=[f for f in d.get('flags',[])
       if abbr in [x.lower() for x in f.get('target_monitors',[])]
       or f.get('source_monitor','')==abbr]
print(f'Relevant cross-monitor flags: {{len(flags)}} of {{d.get("total_flags",0)}} total')
for f in flags:
    print(f'  [{f["source_monitor"].upper()}→{abbr.upper()}] {f["title"][:80]}')
    if f.get('body'): print(f'    {f["body"][:120]}')
"

# Schema changelog — confirm what you must produce this issue
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/schema-changelog.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
entries=[e for e in d.get('entries',[]) if e.get('monitor') in ['FCW','ALL']]
print(f'Schema requirements for FCW ({len(entries)} entries):')
for e in entries:
    print(f'  [{e["id"]}] {e["field"]}: required from {e.get("required_from_issue","launch")}')
"
```

Use cross-monitor flags to incorporate adjacent signals into your analysis
and update your own cross_monitor_flags where new linkages are found.
Use schema changelog to verify your output includes all required fields.

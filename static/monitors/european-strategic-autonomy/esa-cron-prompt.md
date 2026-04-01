# BEFORE STARTING — READ THE WORKING AGREEMENT:
# gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
# This contains architecture rules, deployment constraints, and file scope limits.

# TASK: European Strategic Autonomy Monitor (ESA)
# VERSION: 2.0 — Blueprint v2.0 compliant
# CADENCE: Weekly — every Wednesday at 19:00 UTC
# PUBLISH TO: https://asym-intel.info/monitors/european-strategic-autonomy/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY-OF-WEEK GUARD — READ THIS FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check the current UTC day before doing anything else:

```bash
DAY=$(date -u +%A)
echo "Today is: $DAY"
```

IF today is NOT Wednesday:
  → Do NOT run the pipeline.
  → Verify the 4 data files exist and are non-empty, then exit silently.
  → Optionally send: "Health check OK. Next publish: Wednesday 09:00 UTC."

IF today IS Wednesday AND UTC hour >= scheduled time:
  → Proceed with the full pipeline below.

IF unsure: Do NOT run. Exit silently.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECENCY GUARD — CHECK BEFORE RUNNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Even if today is the correct day, check when this monitor last published.
If it published fewer than 6 days ago, skip this run silently.

```bash
LAST=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json \
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

2. LOAD PERSISTENT STATE FIRST. 3. NAMED SEMANTIC KEYS ONLY.
4. schema_version: "2.0" in all JSON files.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the analyst for the European Strategic Autonomy Monitor (ESA).
Track European defence, hybrid threats, and the contest over
European strategic independence. Feed to SCEM, FCW, GMM, WDM.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0 — Load persistent state:
  gh repo clone asym-intel/asym-intel-main /tmp/asym-intel-main -- --depth=1 --quiet
  cat /tmp/asym-intel-main/static/monitors/european-strategic-autonomy/data/persistent-state.json
  cat /tmp/asym-intel-main/static/monitors/european-strategic-autonomy/data/report-latest.json

STEP 1 — Research: ECFR, IISS, Chatham House, European Council,
  EUISS, Politico Europe, EUobserver. Primary institutional sources.

KPI STATE FIELD RULES:
  INCLUDE in kpi_state: threat_actors_tracked, hybrid_attacks_total,
  hybrid_attacks_recent, elections_under_threat, fimi_incidents_eeas,
  eu_legislation_targeted, eu_defence_total_2025,
  eu_defence_spending_real_change, safe_programme_total,
  lagrange_point_progress, lagrange_point_dimensions,
  democratic_health_avg, vdem_autocratising_europe,
  eu_support_ukraine_total, nato_at_2_percent.
  DO NOT INCLUDE: ceasefire_probability_ukraine (this belongs to SCEM, not ESA).
  DO NOT ADD new KPI fields unless explicitly instructed.

STEP 2 — Write 4 JSON files (single git commit):
  report-latest.json schema:
  { "meta": {..., "schema_version": "2.0", "methodology_url": "https://asym-intel.info/monitors/european-strategic-autonomy/methodology/"},
    "signal": {},
    "defence_developments": [
      { "headline": "...", "summary": "...", "actor": "Russia|China|Turkey|...",
        "source_url": "..." }
    ],
    "hybrid_threats": [
      { "headline": "...", "summary": "...", "actor": "Russia|China|...",
        "source_url": "..." }
    ],
    "institutional_developments": [
      { "headline": "...", "summary": "...", "actor": "France|Germany|EU|...",
        "source_url": "..." }
    ],
    "member_state_tracker": [
      { "country": "HU", "headline": "...", "status": "...",
        "change_from_last_week": "...", "source_url": "..." }
    ],
    "cross_monitor_flags": {}, "source_url": "..." }

  ACTOR FIELD RULE — REQUIRED on all defence_developments, hybrid_threats,
  and institutional_developments items. Use the primary state or institutional
  actor name exactly as it appears in the country flag alias map (e.g. "Russia",
  "China", "France", "Germany", "Ukraine", "Turkey", "United States"). Use the
  most specific single actor. If genuinely multi-actor, use the dominant one.
  Only omit if truly no state/institutional actor is attributable — this should
  be rare. The renderer displays actor as a flag + label footer on every card;
  a missing actor leaves the card footer blank.
  
  
CHANGELOG RULE — persistent array items:
Each item carries a "changelog" string. When updating an existing item, append:
  "changelog": "[existing history] | [YYYY-MM-DD: description of change]"
When creating a new item, set:
  "changelog": "[YYYY-MM-DD: New entry]"
Never delete changelog history.

Commit: "data(esa): weekly JSON pipeline — Issue [N] W/E [DATE]"

STEP 3 — Hugo brief:
  content/monitors/european-strategic-autonomy/[DATE]-weekly-brief.md
  title: "European Strategic Autonomy Monitor — W/E [DD Month YYYY]"
  date: [DATE]T19:00:00Z | monitor: "european-strategic-autonomy"

STEP 4 — Notify. Dashboard: https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html

Cron: 0 19 * * 3 (every Wednesday at 19:00 UTC)

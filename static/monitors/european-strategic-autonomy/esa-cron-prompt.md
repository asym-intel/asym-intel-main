# BEFORE STARTING — READ THE WORKING AGREEMENT:
# gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
# This contains architecture rules, deployment constraints, and file scope limits.

# TASK: European Strategic Autonomy Monitor (ESA)
# VERSION: 2.0 — Blueprint v2.0 compliant
# CADENCE: Weekly — every Wednesday at 19:00 UTC
# PUBLISH TO: https://asym-intel.info/monitors/european-strategic-autonomy/

# ══════════════════════════════════════════════════════════════
# STEP 0 — PUBLISH GUARD (MUST RUN FIRST — DO NOT SKIP)
# ══════════════════════════════════════════════════════════════
#
# This block MUST be the first thing executed. Run it before
# reading any further instructions. If it exits, stop completely.
#
# Two conditions must BOTH be true to proceed:
#   1. Today is the correct publish day (Wednesday)
#   2. This monitor has not published in the last 6 days
#
# If either condition fails → EXIT IMMEDIATELY. Do not research.
# Do not write any files. Do not send any notification.
# A prompt reload is NOT a reason to publish.

```bash
set -e

# Check 1: correct day of week
EXPECTED_DAY="Wednesday"
TODAY_DAY=$(date -u +%A)
if [ "$TODAY_DAY" != "$EXPECTED_DAY" ]; then
  echo "GUARD: Wrong day. Today=$TODAY_DAY, expected=$EXPECTED_DAY. Exiting."
  exit 0
fi

# Check 2: UTC hour >= scheduled hour (avoid running before scheduled time)
EXPECTED_HOUR=19
TODAY_HOUR=$(date -u +%H | sed 's/^0//')
if [ "${TODAY_HOUR:-0}" -lt "$EXPECTED_HOUR" ]; then
  echo "GUARD: Too early. UTC hour=$TODAY_HOUR, scheduled=$EXPECTED_HOUR. Exiting."
  exit 0
fi

# Check 3: not published within the last 6 days
LAST_PUB=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json \
  --jq '.content' | base64 -d | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d.get('meta',{{}}).get('published','2000-01-01')[:10])")
DAYS_AGO=$(python3 -c "
from datetime import date
last = date.fromisoformat('$LAST_PUB')
today = date.today()
print((today - last).days)
")
echo "GUARD: Last published $LAST_PUB ($DAYS_AGO days ago)"
if [ "$DAYS_AGO" -lt 6 ]; then
  echo "GUARD: Published $DAYS_AGO days ago — too recent. Minimum interval is 6 days. Exiting."
  exit 0
fi

echo "GUARD: All checks passed. Proceeding with publish pipeline."
```

If the bash block above exits with code 0 after printing "GUARD: ... Exiting" → STOP HERE.
Do not proceed. Do not perform any research or writes.
Only continue if the final line printed is "GUARD: All checks passed."

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
  PUBLISH_DATE = today's UTC date in YYYY-MM-DD format (e.g. 2026-04-08)
  ⚠️  The filename MUST equal PUBLISH_DATE. The front matter date: field must also equal PUBLISH_DATE.
      A mismatch causes a future-dated or wrong URL in sitemap.xml (anti-pattern FE-019).
  Filename: content/monitors/european-strategic-autonomy/[PUBLISH_DATE]-weekly-brief.md
  title: "European Strategic Autonomy Monitor — W/E [DD Month YYYY]"
  date: [PUBLISH_DATE]T19:00:00Z | monitor: "european-strategic-autonomy"

STEP 4 — Notify. Dashboard: https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html

Cron: 0 19 * * 3 (every Wednesday at 19:00 UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TWO-PASS COMMIT RULE — MANDATORY FOR EVERY RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  The JSON for this monitor is too large to produce safely in one pass.
You MUST write it in two separate git commits. Never combine into one.

PASS 1 — Core sections (commit first, immediately after research):
  meta, signal, defence_developments, hybrid_threats, source_url

  Commit: "data(esa): Issue [N] W/E [DATE] — core sections"

PASS 2 — Deep sections (commit second, by patching the Pass 1 file):
  institutional_developments, member_state_tracker, cross_monitor_flags

  Method:
  ```bash
  # 1. Download the Pass 1 JSON
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json \
    --jq '.content' | base64 -d > /tmp/esa-report.json

  # 2. Add the Pass 2 sections to /tmp/esa-report.json using Python/jq

  # 3. Push it back (replace the file with the patched version)
  SHA=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json --jq '.sha')
  CONTENT=$(base64 -w 0 /tmp/esa-report.json)
  gh api --method PUT /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json \
    --field message="data(esa): Issue [N] W/E [DATE] — deep sections" \
    --field content="$CONTENT" --field sha="$SHA" --field branch="main"
  ```

  Do the same two-pass write for report-{DATE}.json.

VERIFICATION — run after Pass 2 before proceeding to Step 3:
  ```bash
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/european-strategic-autonomy/data/report-latest.json \
    --jq '.content' | base64 -d | python3 -c \
    "import json,sys; d=json.load(sys.stdin); missing=[k for k in ['institutional_developments', 'member_state_tracker'] if k not in d]; print('MISSING:',missing) if missing else print('ALL SECTIONS PRESENT ✓')"
  ```
  If MISSING is non-empty — do NOT proceed to Step 3. Re-run Pass 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAGRANGE POINT DIMENSIONS — update persistent-state.json each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The dashboard Autonomy Radar chart requires lagrange_point_dimensions
inside kpi_state in persistent-state.json. This MUST be updated every
issue or the radar will not render.

Add/update "lagrange_point_dimensions" inside "kpi_state":

"lagrange_point_dimensions": {
  "defence":      { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" },
  "energy":       { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" },
  "technology":   { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" },
  "finance":      { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" },
  "materials":    { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" },
  "institutions": { "score": 0–100, "direction": "Improving|Stable|Deteriorating", "note": "One sentence key driver" }
}

Also update "lagrange_point_progress" in kpi_state:
  "lagrange_point_progress": "~35%" (or updated composite estimate)

SCORING GUIDANCE (analyst judgement, updated each issue):
  defence:      EU collective defence capability vs. full strategic autonomy target
                Anchors: EDIP progress, national defence spending vs. 2% GDP targets,
                EU defence industrial base (EDTIB) capacity, joint procurement
  energy:       EU energy independence from non-allied suppliers
                Anchors: Russian gas dependency (now <15% but LNG import concentration),
                renewable share, strategic reserve levels, interconnection capacity
  technology:   EU digital/AI sovereignty and strategic tech independence
                Anchors: EU AI Act implementation, semiconductor supply chain,
                cloud dependency on non-EU hyperscalers, 5G vendor diversity
  finance:      EU financial autonomy (capital markets, payment systems, FX)
                Anchors: CMU progress, SWIFT alternative capacity, EUR internationalisation,
                EU sovereign debt market depth
  materials:    EU critical raw material security (CRM Act implementation)
                Anchors: CRM stockpiles, mining/processing capacity, import concentration
                from China/Russia for battery minerals, rare earths
  institutions: EU institutional cohesion and decision-making capacity
                Anchors: QMV reform progress, Article 7 proceedings, rule-of-law compliance,
                EP cohesion on strategic autonomy votes, Council unanimity rate on foreign policy

CALIBRATION: Score 35 = current baseline (Issue 1). Scores should be
comparable across issues. If a pillar improves materially, note the trigger.
Scores carry forward if no new evidence this week.

Also add "composite_index_history" to kpi_state — append each issue:
"composite_index_history": [
  { "issue": N, "date": "YYYY-MM-DD", "composite": 35, "rationale": "..." }
]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0B — READ SHARED INTELLIGENCE LAYER (before research)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After loading your own persistent-state.json, read these two shared files:

```bash
# Cross-monitor intelligence digest (compiled weekly by housekeeping cron)
# Filters for flags relevant to ESA (either targeting or sourced from this monitor)
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/intelligence-digest.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
abbr='esa'
flags=[f for f in d.get('flags',[])
       if abbr in [x.lower() for x in f.get('target_monitors',[])]
       or f.get('source_monitor','')==abbr]
print(f'Relevant cross-monitor flags: {{len(flags)}} of {{d.get("total_flags",0)}} total')
for f in flags:
    print(f'  [{f["source_monitor"].upper()}→{abbr.upper()}] {f["title"][:80]}')
    if f.get('body'): print(f'    {f["body"][:120]}')
"

  # Internal full methodology spec (scoring rubrics, source hierarchy, formula weights):
  # Read this before any schema changes or analytical framework work on this monitor.
  SPEC=$(gh api /repos/asym-intel/asym-intel-internal/contents/methodology/european-strategic-autonomy-full.md \
    --jq '.content' | base64 -d 2>/dev/null || echo "spec unavailable")
  echo "$SPEC" | head -50  # Read the first 50 lines for context

# Schema changelog — confirm what you must produce this issue
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/schema-changelog.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
entries=[e for e in d.get('entries',[]) if e.get('monitor') in ['ESA','ALL']]
print(f'Schema requirements for ESA ({len(entries)} entries):')
for e in entries:
    print(f'  [{e["id"]}] {e["field"]}: required from {e.get("required_from_issue","launch")}')
"
```

Use cross-monitor flags to incorporate adjacent signals into your analysis
and update your own cross_monitor_flags where new linkages are found.
Use schema changelog to verify your output includes all required fields.

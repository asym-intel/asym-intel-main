# JSON DATA PIPELINE — FINAL STEP
# Universal addition to all monitor cron task instructions
# Version: 2.0 — 1 April 2026 (Blueprint v2.0)
#
# HOW TO USE: Append this entire document to each monitor's cron task prompt,
# replacing {MONITOR_SLUG}, {MONITOR_NAME}, {PUBLISH_DATE_FIELD}, and
# {SCHEMA_SECTION} with the monitor-specific values in Section B below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVISED PUBLISH SEQUENCE — HOW THE PIPELINE CHANGES YOUR WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every publish cycle now has FIVE steps, not four:

1. LOAD STATE — read persistent-state.json before researching
2. RESEARCH — use persistent state as baseline; only investigate what may have changed
3. UPDATE DASHBOARD — git clone/push as before
4. PUBLISH HUGO BRIEF — GitHub API as before
5. WRITE JSON PIPELINE — four files via git (included in the same commit as the dashboard)

The persistent-state.json is your memory. Load it first. Change only what the
week's evidence justifies changing. Record the change in version_history.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 (NEW) — LOAD PERSISTENT STATE BEFORE RESEARCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before conducting any research, load the current persistent state:

```bash
cd /tmp && rm -rf asym-intel-main
gh repo clone asym-intel/asym-intel-main asym-intel-main -- --depth=1 --quiet

# Read persistent state
cat asym-intel-main/static/monitors/{MONITOR_SLUG}/data/persistent-state.json
```

Use this as your analytical baseline:
- Carry forward all entities unchanged unless new primary-source evidence
  justifies updating them this week
- Do NOT re-derive what is already known — only investigate what may have changed
- Every change you make to persistent state MUST include a version_history entry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 (NEW) — WRITE JSON PIPELINE FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After completing the dashboard update and Hugo brief, write the four JSON
files in the SAME git commit as the dashboard (they are already in the
cloned repo from Step 0).

```bash
PUBLISH_DATE=$(date +%Y-%m-%d)
REPO_DIR=/tmp/asym-intel-main
DATA_DIR=$REPO_DIR/static/monitors/{MONITOR_SLUG}/data

# ── 1. Write report-latest.json (current issue, full structured content) ─────
# Build the full JSON object for this week's issue.
# See Section B below for the schema specific to this monitor.
# Every item MUST include source_url pointing to the primary source.
# The root object MUST include:
#   "source_url": "https://asym-intel.info/monitors/{MONITOR_SLUG}/${PUBLISH_DATE}-weekly-brief/"

cat > $DATA_DIR/report-latest.json << 'REPORT_EOF'
{FULL_REPORT_JSON_FOR_THIS_WEEK}
REPORT_EOF

# ── 2. Copy as dated archive ──────────────────────────────────────────────────
cp $DATA_DIR/report-latest.json $DATA_DIR/report-${PUBLISH_DATE}.json

# ── 3. Update archive.json (append index entry — do NOT replace) ───────────────
# Read current archive, append this issue's index entry, write back.
python3 - << 'PYEOF'
import json, os

archive_path = os.environ.get('DATA_DIR', '') + '/archive.json'
with open(archive_path, 'r') as f:
    archive = json.load(f)

# Get issue number (1-indexed, based on archive length + 1)
issue_num = len(archive) + 1

# Build archive entry — lightweight index only, not full content
new_entry = {
    "issue": issue_num,
    "volume": 1,
    "week_label": os.environ.get('WEEK_LABEL', ''),
    "published": os.environ.get('PUBLISH_DATE', ''),
    "slug": os.environ.get('PUBLISH_DATE', ''),
    "signal": "{THE_LEAD_SIGNAL_ONE_SENTENCE}",
    "source_url": f"https://asym-intel.info/monitors/{MONITOR_SLUG}/{os.environ.get('PUBLISH_DATE', '')}-weekly-brief/",
    "delta_strip": [
        # Top 3-5 items: rank, title, module_tag, delta_type, one_line
        # {DELTA_STRIP_ITEMS}
    ]
}

archive.append(new_entry)

with open(archive_path, 'w') as f:
    json.dump(archive, f, indent=2, ensure_ascii=False)

print(f"Archive updated: {len(archive)} issues")
PYEOF

# ── 4. Update persistent-state.json ────────────────────────────────────────────
# Load current state, update only what changed this week, write back.
# Every changed field MUST have a version_history entry appended.
# Fields that did not change are written back unchanged.
# The _meta block is always updated with last_updated and last_issue.

python3 - << 'PYEOF'
import json, os

state_path = os.environ.get('DATA_DIR', '') + '/persistent-state.json'
with open(state_path, 'r') as f:
    state = json.load(f)

publish_date = os.environ.get('PUBLISH_DATE', '')

# Always update _meta
state['_meta']['last_updated'] = publish_date
state['_meta']['last_issue'] = publish_date

# {PERSISTENT_STATE_UPDATES_FOR_THIS_WEEK}
# For each entity that changed, update the value and append to version_history:
# entity['version_history'].append({
#     "date": publish_date,
#     "change": "Brief description of what changed",
#     "reason": "What evidence justified the change",
#     "prior_value": "What it was before"
# })
# Entities that did NOT change: leave completely untouched.

with open(state_path, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("Persistent state updated")
PYEOF

# ── 5. Commit all four JSON files + dashboard in a single push ────────────────
cd $REPO_DIR
git config user.name "monitor-bot"
git config user.email "monitor-bot@asym-intel.info"
git add static/monitors/{MONITOR_SLUG}/data/
git add static/monitors/{MONITOR_SLUG}/dashboard.html  # already staged from dashboard step

# Check if there's anything new to commit
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "content: {MONITOR_NAME} issue ${PUBLISH_DATE} — dashboard + JSON pipeline"
    git pull --rebase origin main
    git push
    echo "Published: https://asym-intel.info/monitors/{MONITOR_SLUG}/data/report-latest.json"
fi
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION A — UNIVERSAL JSON RULES (apply to all monitors)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EVERY item in report-latest.json MUST have source_url pointing to the
   primary source for that specific item (not just the monitor homepage).

2. The root object of report-latest.json MUST include:
   "source_url": "https://asym-intel.info/monitors/{MONITOR_SLUG}/{PUBLISH_DATE}-weekly-brief/"
   This is the canonical URL for the network graph node.

3. cross_monitor_flags in report-latest.json:
   - Carry all existing flags forward unchanged (update "unchanged_since" stays)
   - Only add new flags when this week's research reveals a new cross-monitor connection
   - Update existing flags only when the underlying situation changes
   - Never delete flags — change status to "Resolved" with reason and date

4. persistent-state.json version_history discipline:
   - Every change appends one entry: {date, change, reason, prior_value}
   - "prior_value" is what the field contained before the change
   - If nothing changed this week for an entity, do NOT touch it at all

5. archive.json is append-only — never modify existing entries.

6. report-{date}.json is a point-in-time snapshot — never modify after creation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION B — MONITOR-SPECIFIC JSON SCHEMAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Replace {SCHEMA_SECTION} with the relevant block below for each monitor.

──────────────────────────────────────────────────────────────
B1. EUROPEAN STRATEGIC AUTONOMY (EGHTM) — Wednesday 19:00 UTC
──────────────────────────────────────────────────────────────
Slug: european-strategic-autonomy
Monitor name for commits: EGHTM

report-latest.json top-level keys:
  meta, m00_the_signal, m01_executive_insight, m02_ukraine_war,
  m03_threat_actors {RU, CN, US, IL}, m04_elections, m05_state_capture,
  m06_networks, m07_eu_legislation, m08_defence, m09_eu_response,
  m10_strategic_independence, m11_weekly_brief, cross_monitor_flags, source_url

persistent-state updates each week:
  - kpi_state: update any KPI that changed (NATO %, FIMI incidents, etc.)
  - active_elections: add new elections approaching, remove past ones
  - state_capture_cases: update severity scores where evidence justifies
  - active_actor_campaigns: add/close campaigns per actor
  - eu_legislation_tracker: update status of tracked legislation
  - timeline_events: APPEND new events (never modify historical entries)

archive delta_strip: top 5 developments by analytical significance
  Required fields: rank, title, module (e.g. "M03"), delta_type, one_line

──────────────────────────────────────────────────────────────
B2. DEMOCRATIC INTEGRITY (WDM) — Monday 06:00 UTC
──────────────────────────────────────────────────────────────
Slug: democratic-integrity
Monitor name for commits: WDM

report-latest.json top-level keys:
  meta, signal, heatmap {rapid_decay[], recovery[], watchlist[]},
  intelligence_items[], institutional_integrity_flags[],
  regional_mimicry_chains[], cross_monitor_flags, source_url

persistent-state updates each week:
  - heatmap_countries: update severity_score and severity_arrow only when
    primary-source evidence justifies change (requires ≥2 Tier 2–4 sources)
    Append version_history entry with prior score when changed.
  - mimicry_chains: APPEND new links — never modify existing chain entries
  - institutional_integrity_active_flags: add/clear flags as conditions change

archive delta_strip: top 5 country developments
  Required fields: rank, title, module (country name), delta_type
  (New Entry / Status Change / Score Change / Resolution), one_line

──────────────────────────────────────────────────────────────
B3. GLOBAL MACRO (GMM) — Monday 08:00 UTC
──────────────────────────────────────────────────────────────
Slug: macro-monitor
Monitor name for commits: GMM

report-latest.json top-level keys:
  meta, executive_briefing, asset_class_scores[],
  outlook {label, conviction, rationale}, tactical_alerts[],
  domain_indicators {domain_1 through domain_6},
  sentiment_overlay, 360_intelligence[], cross_monitor_flags, source_url

persistent-state updates each week:
  - asset_class_baseline: update flag and score for each asset class
  - active_tactical_alerts: add new alerts (|Δ| ≥ 0.45); remove resolved ones
  - oil_supply_shock_driver: update current_driver and note when changes
  - blind_spot_overrides: add/remove as analytical corrections are applied
  - conviction_history: APPEND this week's conviction label and rationale

archive delta_strip: top 5 macro developments
  Required fields: rank, title, module (domain tag), delta_type
  (Flag Change / Tactical Alert / Regime Shift / New Driver), one_line

──────────────────────────────────────────────────────────────
B4. FIMI & COGNITIVE WARFARE — Thursday 09:00 UTC
──────────────────────────────────────────────────────────────
Slug: fimi-cognitive-warfare
Monitor name for commits: FIMI

report-latest.json top-level keys:
  meta, signal, active_campaigns {RU, CN, IR, GULF, US, IL},
  campaign_archive[], platform_actions[], regulatory_developments[],
  cross_monitor_flags, source_url

persistent-state updates each week:
  - active_campaigns per actor: update status/last_activity for active ones;
    move to campaign_archive when status changes to Concluded/Disrupted
    (90-day rule: no activity = status change required)
  - actor_profiles: update doctrine_summary only when a confirmed new
    tactic or infrastructure change is documented
  - platform_enforcement_tracker: APPEND new takedowns/actions

archive delta_strip: top 5 campaign/operation developments
  Required fields: rank, title, module (actor: RU/CN/IR/GULF/US/IL),
  delta_type (New Campaign / Takedown / Attribution / Platform Action), one_line

──────────────────────────────────────────────────────────────
B5. ENVIRONMENTAL RISKS & PLANETARY BOUNDARIES (GERP) — Saturday 05:00 UTC
──────────────────────────────────────────────────────────────
Slug: environmental-risks
Monitor name for commits: GERP

report-latest.json top-level keys:
  meta, m00_the_signal, m01_executive_insight,
  m02_planetary_boundaries {boundaries[], tipping_systems[]},
  m03_threat_multiplier[], m04_extreme_weather[], m05_policy_law
  {icj_tracker, loss_damage_tracker, items[]},
  m06_ai_climate[], m07_biosphere[], m08_geostrategic_resources[],
  cross_monitor_flags, source_url

persistent-state updates each week:
  - planetary_boundary_status: update status only when Tier 1/2 scientific
    publication justifies revision (NOT on single weather event)
  - tipping_system_flags: update status when proxy metric crosses threshold
  - standing_trackers.icj_climate_advisory: update every week even if "no change"
  - standing_trackers.loss_damage_finance: update disbursed/committed figures
  - active_attribution_gap_cases: add new gaps; NEVER remove existing ones
  - regional_cascade_chains: APPEND new cascade links

archive delta_strip: top 5 Earth system / policy developments
  Required fields: rank, title, module (M02–M08), delta_type
  (Boundary Transgression / Tipping Signal / Policy Development /
  Attribution Gap / Cascade Chain), one_line

──────────────────────────────────────────────────────────────
B6. STRATEGIC CONFLICT & ESCALATION (SCEM) — Sunday 18:00 UTC
──────────────────────────────────────────────────────────────
Slug: conflict-escalation
Monitor name for commits: SCEM

report-latest.json top-level keys:
  meta, lead_signal {conflict, headline, indicator, deviation, summary, source_url},
  conflict_roster[] (all 8 entries, full indicator scoring),
  roster_watch {approaching_inclusion[], approaching_retirement[]},
  cross_monitor_flags, source_url

persistent-state updates each week:
  - conflict_baselines: increment week_count for each active conflict;
    update indicator_medians only at week 13 lock (do NOT update before);
    NEVER silently revise a locked baseline
  - f_flag_history: APPEND any F-flags applied this week (never remove)
  - roster_status: update status if a conflict is added or retired
    (retirement requires two consecutive zero-activity cycles)

WEEK COUNTER: The meta.week_number in report-latest.json tracks the issue
number. Increment by 1 each week. Baselines lock when week_count reaches 13
for each individual conflict — check each conflict separately.

archive delta_strip: top 5 escalation developments
  Required fields: rank, title, module (conflict name),
  delta_type (RED Band / F-Flag Applied / Roster Change / De-escalation),
  one_line

──────────────────────────────────────────────────────────────
B7. AI GOVERNANCE MONITOR (AGM) — Friday 16:00 UTC
──────────────────────────────────────────────────────────────
Slug: ai-governance
Monitor name for commits: AGM

report-latest.json top-level keys:
  meta, source_url, module_0 (signal), module_1 (executive insight),
  module_2 (model frontier), module_3 (investment/M&A),
  module_4 (sector penetration), module_5 (EU/China watch),
  module_6 (AI in science), module_7 (risk indicators),
  module_8 (military AI), module_9 (law & litigation),
  module_10 (AI governance), module_11 (ethics),
  module_12 (info ops), module_13 (AI & society),
  module_14 (power structures), module_15 (personnel),
  cross_monitor_flags, delta_strip, country_grid, country_grid_watch

persistent-state updates each week:
  - module_7_risk_vectors: update rating/confidence only when new primary-source
    evidence justifies it; carry unchanged_since forward when no change
  - module_9_eu_ai_act_tracker: update each of the 7 layers; update
    standards_vacuum_active flag and days_to_deadline on every issue
  - module_14_concentration_index: update trend/note when material market
    structure change; otherwise carry unchanged_since forward
  - module_15_aisi_pipeline: APPEND any confirmed movements; never remove
  - module_5_ciyuan and module_5_standards_vacuum: update status when
    trigger conditions change (see trigger definitions in each entry)
  - ongoing_lab_postures: update posture when material change in lab
    strategy, governance, or legal status; version_history required
  - cross_monitor_flags: carry all flags forward; update status/linkage
    if evidence changes; add new flags; never delete (use status: Resolved)

archive delta_strip: top 5 most significant AI governance developments
  Required fields: rank, title, module (M00–M15 or cross-monitor),
  delta_type (Signal / Capability / Investment / Regulatory / Geopolitical),
  one_line

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION C — WHAT THIS CHANGES ABOUT HOW YOU RESEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE (old approach):
- Start each week cold
- Re-derive all baseline knowledge from scratch
- Produce a standalone brief with no continuity

AFTER (with JSON pipeline):
- Load persistent-state.json first — this is your institutional memory
- Only research what may have changed since last week
- Produce a brief that explicitly notes what changed vs what is stable
- Record all changes with evidence in version_history

This means your research is more efficient (don't re-verify things that
haven't changed) and your output is more analytically valuable (readers
can see what is new vs what is persistent baseline).

The persistent-state.json is the single source of truth for ongoing
situations. The dashboard and Hugo brief are presentations of that truth.
The JSON pipeline is the truth itself.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION D — NOTIFICATION UPDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add to the weekly notification:
- "JSON pipeline: report-latest.json, report-{date}.json, archive.json
  ({N} issues), persistent-state.json — all updated"
- If any cross_monitor_flags were added or changed: list them explicitly
- If any persistent-state entities changed: summarise what changed and why


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BLUEPRINT v2.0 ADDITIONS (supersede any conflicting v1.0 instructions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL RULE: CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES.
Write ONLY the 4 data files listed above. Nothing else.

NAMED SEMANTIC KEYS: All top-level keys in report-latest.json must be
named semantically. Never use module_0, module_1 etc.

SCHEMA VERSION: All JSON files must include "schema_version": "2.0"
in their _meta or meta block.

CROSS-MONITOR FLAGS — now live in BOTH places:
  1. report-latest.json → cross_monitor_flags (for weekly render)
  2. persistent-state.json → cross_monitor_flags (accumulates across issues)

The persistent-state.json cross_monitor_flags is the source of truth.
The report-latest.json copy is a mirror for the weekly renderer only.

FLAGS NEVER DELETED: Set status:"Resolved" on closed flags.
Flags schema (both locations):
  {
    "id": "cmf-NNN",
    "monitors_involved": ["Canonical Monitor Name"],  ← use canonical names
    "monitor_url": "https://...",
    "title": "string",
    "linkage": "string",
    "this_monitor_perspective": "string",
    "type": "string",
    "status": "Active | Resolved | Watching",
    "first_flagged": "ISO-8601",
    "unchanged_since": "ISO-8601",
    "version_history": [{"date": "...", "change": "...", "reason": "...", "prior_value": null}]
  }

CANONICAL MONITOR NAMES (use these exactly in monitors_involved[]):
  World Democracy Monitor
  Global Macro Monitor
  FIMI & Cognitive Warfare Monitor
  European Strategic Autonomy Monitor
  AI Governance Monitor
  Environmental Risks Monitor
  Strategic Conflict & Escalation Monitor

ARCHIVE.JSON FORMAT (v2.0): append only, never modify past entries:
  {
    "issue": integer,
    "volume": integer,
    "week_label": "string",
    "published": "YYYY-MM-DD",
    "slug": "YYYY-MM-DD",
    "signal": "one sentence headline",
    "source_url": "https://..."
  }

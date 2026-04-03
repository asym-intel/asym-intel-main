# TASK: Weekly Housekeeping — Asymmetric Intelligence Platform
# CRON ID: fc210493
# CADENCE: Every Monday at 08:00 UTC (after all Monday publishes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. THIS TASK NEVER MODIFIES ANY FILE except HANDOFF.md and intelligence-digest.json.
2. Send notification ONLY on WARN or FAIL results, OR when digest flag count changes significantly.
3. On all-OK: exit silently (except the digest write, which always runs).
4. Use api_credentials=["github"] for all GitHub operations.

NOTE: HTML structural checks (network bar, shared JS, offset styles, font sizes,
search CSS) are enforced by the CI validator on every push. Housekeeping does NOT
re-run those checks — CI is the canonical source. Only data integrity, schema
freshness, and intelligence compilation are checked here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — DATE GUARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
DAY=$(date -u +%A)
echo "Today is: $DAY"
```

IF today is NOT Monday → exit silently. Do not run checks.
IF today IS Monday → proceed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONITORS & PAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONITORS (7):
  ai-governance            (AGM)  — 9 pages (includes digest.html)
  conflict-escalation      (SCEM) — 8 pages
  democratic-integrity     (WDM)  — 8 pages
  environmental-risks      (ERM)  — 8 pages
  european-strategic-autonomy (ESA) — 8 pages
  fimi-cognitive-warfare   (FCW)  — 8 pages
  macro-monitor            (GMM)  — 8 pages

STANDARD 8 PAGES: about, archive, dashboard, methodology, overview, persistent, report, search
AGM EXTRA PAGE: digest.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA CHECKS (run per monitor — JSON files only, not HTML)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each monitor fetch report-latest.json and persistent-state.json from:
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/data/{FILE} \
    --jq '.content' | base64 -d

CHECK 6 — No future dates in meta published fields
  FAIL: if meta.published date is in the future (Hugo will skip it)

CHECK 7 — report-latest.json and persistent-state.json exist and are non-empty
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/data/report-latest.json --jq '.size'
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/data/persistent-state.json --jq '.size'
  FAIL: if either file is missing (404) or size < 100 bytes

CHECK 8 — schema_version is "2.0" in report-latest.json
  PASS: meta.schema_version == "2.0"
  WARN: if schema_version is missing or != "2.0"

RESULT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compile results as:
  PASS  — check passed
  WARN  — non-critical issue (degraded experience, not broken)
  FAIL  — critical issue (broken functionality)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECK 13 — SCHEMA REQUIREMENTS VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read the schema requirements spec:
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/monitor-schema-requirements.json \
    --jq '.content' | base64 -d

For each monitor, fetch report-latest.json and validate:
  1. All required_top_level_keys are present and non-null
  2. Required sub-fields are present (e.g. executive_briefing fields for GMM)
  3. Required min counts are met (e.g. tail_risks >= 5 for GMM)
  4. Required_from_issue_N fields: check issue number vs. requirement date and flag if overdue

FAIL: any required_top_level_keys missing
WARN: any required sub-fields missing or min counts not met
WARN: any required_from_issue_N fields missing when current issue >= N

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECK 14 — COMPILE CROSS-MONITOR INTELLIGENCE DIGEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THIS IS A WRITE OPERATION (exception to read-only rule — digest is infrastructure).

After all checks complete, compile a fresh intelligence digest from all 7 monitors'
cross_monitor_flags arrays and WRITE it to:
  static/monitors/shared/intelligence-digest.json

Steps:
  1. For each of the 7 monitors, fetch cross_monitor_flags from report-latest.json
  2. Normalise each flag to the standard digest schema:
     { source_monitor, source_slug, flag_id, title, target_monitors[], body,
       status, type, first_flagged, source_url }
  3. Sort by source_monitor, then first_flagged
  4. Write the compiled digest as:
     {
       "schema_version": "1.0",
       "compiled": "[TODAY_UTC]",
       "total_flags": N,
       "flags_by_source": { "wdm": N, "gmm": N, ... },
       "flags": [...]
     }
  5. Commit as: "data(housekeeping): compile cross-monitor intelligence digest [DATE]"

NOTIFY: if total_flags changed significantly vs prior digest (±5 or more)
        with title "Cross-Monitor Digest: [N] flags ([+/-N] vs last week)"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECK 15 — DATA FRESHNESS CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each monitor, verify report-latest.json was published within its
expected cadence window:

  WDM:  published within last 8 days (Mon cadence)
  GMM:  published within last 8 days (Tue cadence)
  FCW:  published within last 8 days (Thu cadence)
  ESA:  published within last 8 days (Wed cadence)
  AGM:  published within last 8 days (Fri cadence)
  ERM:  published within last 8 days (Sat cadence)
  SCEM: published within last 8 days (Sun cadence)

FAIL: if any monitor's last publish is > 14 days ago (missed 2 cycles)
WARN: if any monitor's last publish is > 8 days ago (missed 1 cycle)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7 — VALIDATE TIER 0 DAILY FEEDER (FCW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The FCW Daily Feeder writes to pipeline/monitors/fimi-cognitive-warfare/daily/.
Scan ALL verified-YYYY-MM-DD.json files written in the past 7 days (not just
daily-latest.json which is overwritten daily — the dated files are the audit trail).

```bash
TODAY=$(date -u +%Y-%m-%d)
FEEDER_PATH="pipeline/monitors/fimi-cognitive-warfare/daily"

# Discover all dated files written this week
FILES_TO_CHECK=()
for i in 0 1 2 3 4 5 6; do
  CHECK_DATE=$(date -u -d "${i} days ago" +%Y-%m-%d 2>/dev/null || date -u -v-${i}d +%Y-%m-%d)
  SHA=$(gh api "/repos/asym-intel/asym-intel-main/contents/${FEEDER_PATH}/verified-${CHECK_DATE}.json" \
    --jq ".sha" 2>/dev/null || echo "")
  [ -n "$SHA" ] && FILES_TO_CHECK+=("verified-${CHECK_DATE}.json")
done

if [ ${#FILES_TO_CHECK[@]} -eq 0 ]; then
  echo "CHECK_16: WARN — no verified-YYYY-MM-DD.json files found in past 7 days (feeder may not have run yet)"
else
  echo "Scanning ${#FILES_TO_CHECK[@]} feeder file(s): ${FILES_TO_CHECK[*]}"
  for FILE in "${FILES_TO_CHECK[@]}"; do
    FEEDER=$(gh api "/repos/asym-intel/asym-intel-main/contents/${FEEDER_PATH}/${FILE}" \
      --jq ".content" | base64 -d 2>/dev/null || echo "")
    [ -z "$FEEDER" ] && echo "CHECK_16: WARN — could not read ${FILE}" && continue

    echo "$FEEDER" | python3 -c "
import json, sys
d = json.load(sys.stdin)
meta = d.get('_meta', {})
findings = d.get('findings', [])
fname = '${FILE}'

# CHECK 16 — Schema version
if meta.get('schema_version') != 'tier0-v1.0':
    print(f'CHECK_16: FAIL [{fname}] — schema_version not tier0-v1.0, got: {meta.get(\"schema_version\")}')
else:
    print(f'CHECK_16: PASS [{fname}] — schema_version ok')

# CHECK 17 — Freshness: data_date matches filename date
file_date = '${FILE}'.replace('verified-','').replace('.json','')
data_date = meta.get('data_date','')
if data_date != file_date:
    print(f'CHECK_17: WARN [{fname}] — data_date {data_date} does not match filename date {file_date}')
else:
    print(f'CHECK_17: PASS [{fname}] — data_date matches filename')

# CHECK 18 — research_traceback on High/Confirmed findings
for f in findings:
    conf = f.get('confidence_preliminary','')
    if conf in ['High','Confirmed']:
        sources = f.get('research_traceback',{}).get('sources_cited',[])
        if len(sources) < 2:
            print(f'CHECK_18: FAIL [{fname}] — {f[\"finding_id\"]} is {conf} but has {len(sources)} source(s) in traceback (need 2+)')
        else:
            print(f'CHECK_18: PASS [{fname}] — {f[\"finding_id\"]} ({conf}) has {len(sources)} sources')

# CHECK 19 — episodic_flag=true requires episodic_reason
for f in findings:
    if f.get('episodic_flag') and not (f.get('episodic_reason') or '').strip():
        print(f'CHECK_19: WARN [{fname}] — {f[\"finding_id\"]} has episodic_flag=true but no episodic_reason')

# CHECK 20 — campaign_status_candidate must be present on all findings
for f in findings:
    if not f.get('campaign_status_candidate'):
        print(f'CHECK_20: WARN [{fname}] — {f[\"finding_id\"]} missing campaign_status_candidate')

if not findings:
    print(f'INFO [{fname}]: 0 findings — normal if no qualifying FIMI activity detected that day')
"
  done
fi
```

REPORTING:
  Add any CHECK_16–CHECK_20 FAIL/WARN to the notification alongside CHECK_6–15.
  Update notification title count to include feeder check issues.

STEP 8 — GENERATE HANDOFF.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HANDOFF.md is auto-generated every Monday from repo state. Never hand-written.
This removes the systemic risk of it being empty or stale after long sessions.

```bash
TODAY=$(date -u +%Y-%m-%d)
REPO="asym-intel/asym-intel-main"

# Collect live state
COMPUTER_VER=$(gh api /repos/${REPO}/contents/COMPUTER.md \
  --jq '.content' | base64 -d | grep "^## Version" | head -1)

# Last published date per monitor
declare -A PUB_DATES
for SLUG in democratic-integrity macro-monitor fimi-cognitive-warfare \
            european-strategic-autonomy ai-governance environmental-risks conflict-escalation; do
  PUB=$(gh api /repos/${REPO}/contents/static/monitors/${SLUG}/data/report-latest.json \
    --jq '.content' | base64 -d | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  print(d.get('meta',{}).get('published','unknown')[:10])
except: print('error')
" 2>/dev/null || echo "unreadable")
  PUB_DATES[$SLUG]=$PUB
done

# Recent notes-for-computer entries (last 60 lines)
RECENT_NOTES=$(gh api /repos/asym-intel/asym-intel-internal/contents/notes-for-computer.md \
  --jq '.content' | base64 -d | tail -60)

# Write HANDOFF.md
python3 << PYEOF
import subprocess, base64, json, datetime

today = datetime.date.today().isoformat()

pub_dates = {
    "WDM (democratic-integrity)":           "${PUB_DATES[democratic-integrity]}",
    "GMM (macro-monitor)":                  "${PUB_DATES[macro-monitor]}",
    "FCW (fimi-cognitive-warfare)":         "${PUB_DATES[fimi-cognitive-warfare]}",
    "ESA (european-strategic-autonomy)":    "${PUB_DATES[european-strategic-autonomy]}",
    "AGM (ai-governance)":                  "${PUB_DATES[ai-governance]}",
    "ERM (environmental-risks)":            "${PUB_DATES[environmental-risks]}",
    "SCEM (conflict-escalation)":           "${PUB_DATES[conflict-escalation]}",
}

monitor_table = "\n".join(f"| {m} | {d} |" for m, d in pub_dates.items())

handoff = f"""# HANDOFF.md - Asymmetric Intelligence
**Generated:** {today} by Housekeeping cron (auto-generated -- do not hand-edit)
**Next generation:** Following Monday 08:00 UTC

---

## Recent Notes for Computer (from notes-for-computer.md)

${RECENT_NOTES}

---

## Monitor Publication Status

| Monitor | Last Published |
|---------|---------------|
{monitor_table}

---

## COMPUTER.md Version

${COMPUTER_VER}

---

## Stable Architecture Notes

- FCW pipeline: GitHub Actions daily 07:00 UTC (sonar) + Wed 18:00 (sonar-pro) + Wed 20:00 (sonar-deep-research)
- pipeline/ is internal only -- Hugo never builds from it
- Staging required for all monitor HTML/CSS/JS changes
- Two-pass commit mandatory for all 7 Analyst crons
- Annual calibration files: {slug}-{index}-{YEAR}.md auto-discovered at Step 0B+
- All 7 Analyst crons + Housekeeping in COMPUTER.md cron table
"""

sha_r = subprocess.run(
    ['gh', 'api', '/repos/asym-intel/asym-intel-main/contents/HANDOFF.md', '--jq', '.sha'],
    capture_output=True, text=True
)
sha = sha_r.stdout.strip()

payload = json.dumps({
    "message": f"docs(HANDOFF.md): auto-generated by Housekeeping -- {today}",
    "content": base64.b64encode(handoff.encode()).decode(),
    "sha": sha
})
with open('/tmp/hk-gen-handoff.json', 'w') as f:
    f.write(payload)

r = subprocess.run(
    ['gh', 'api', '/repos/asym-intel/asym-intel-main/contents/HANDOFF.md',
     '-X', 'PUT', '-H', 'Content-Type: application/json', '--input', '/tmp/hk-gen-handoff.json'],
    capture_output=True, text=True
)
if r.returncode == 0:
    d = json.loads(r.stdout)
    print(f"HANDOFF.md generated: {d['commit']['sha'][:8]}")
else:
    print(f"Error: {r.stderr[:200]}")
PYEOF

echo "STEP 8: HANDOFF.md generated and committed for ${TODAY}"
```

STEP 9 — CHECK COMPUTER.md VERSION CURRENCY (CHECK 21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
COMP_VER=$(gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d | grep "^## Version" | head -1)

echo "CHECK_21: $COMP_VER"

CURRENT_YEAR=$(date -u +"%Y")

echo "$COMP_VER" | grep -q "$CURRENT_YEAR" \
  && echo "CHECK_21: PASS -- COMPUTER.md version contains current year" \
  || echo "CHECK_21: WARN -- COMPUTER.md version may be stale. Verify it reflects current session state."
```

STEP 10 — CHATTER QUALITY AUDIT (CHECK 22-28)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each monitor, fetch chatter-latest.json and check:

```python
import subprocess, base64, json
from datetime import datetime, timezone

MONITORS = {
    'fimi-cognitive-warfare': 'FCW',
    'macro-monitor': 'GMM',
    'democratic-integrity': 'WDM',
    'conflict-escalation': 'SCEM',
    'european-strategic-autonomy': 'ESA',
    'ai-governance': 'AGM',
    'environmental-risks': 'ERM',
}

today = datetime.now(timezone.utc).date()
issues = []

for slug, abbr in MONITORS.items():
    r = subprocess.run(['gh','api',
        f'/repos/asym-intel/asym-intel-main/contents/static/monitors/{slug}/data/chatter-latest.json',
        '--jq','.content'], capture_output=True, text=True)
    if r.returncode != 0:
        issues.append(f'{abbr} chatter: WARN -- chatter-latest.json missing')
        continue

    d = json.loads(base64.b64decode(r.stdout.strip()).decode('utf-8'))
    meta = d.get('_meta', {})
    items = d.get('items', [])

    # Check 1: data_date recency (should be within 7 days)
    data_date_str = meta.get('data_date', '')
    if data_date_str:
        data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
        age_days = (today - data_date).days
        if age_days > 7:
            issues.append(f'{abbr} chatter: WARN -- data_date is {age_days} days old ({data_date_str})')

    # Check 2: item count (fewer than 3 = may be over-filtered)
    if len(items) < 3:
        issues.append(f'{abbr} chatter: WARN -- only {len(items)} items (prompt may be too restrictive)')

    # Check 3: Tier distribution (>60% T3/T4 = quality concern)
    if items:
        low_tier = sum(1 for i in items if int(str(i.get('source_tier', 3))) >= 3)
        pct = low_tier / len(items)
        if pct > 0.6:
            issues.append(f'{abbr} chatter: WARN -- {int(pct*100)}% Tier 3/4 sources ({low_tier}/{len(items)} items). Review prompt quality.')

    # Check 4: Source bloat (same domain 3+ times)
    from urllib.parse import urlparse
    from collections import Counter
    domains = []
    for item in items:
        url = item.get('source_url', '')
        if url:
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                domains.append(domain)
            except: pass
    for domain, count in Counter(domains).items():
        if count >= 3:
            issues.append(f'{abbr} chatter: WARN -- domain {domain} appears {count}x (source bloat)')

    print(f'CHECK: {abbr} chatter OK ({len(items)} items, data_date={data_date_str})')

for issue in issues:
    print(f'CHATTER_QUALITY: {issue}')
```

REPORTING:
  Add any CHATTER_QUALITY WARN to the weekly notification.
  No notification needed if all chatter checks pass.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL RESULT FORMAT (all checks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If all data checks (6–21) pass AND chatter checks pass AND digest compiled:
  Exit silently — no notification (digest write is the only output).

If any WARN or FAIL across all checks:
  Send notification with title: "Asym Intel — Housekeeping [DATE]: [N] issues"
  Body: list each WARN/FAIL with monitor, check number, and description.
  Format:
    ⚠️  WARN  macro-monitor — Check 15: last published 10 days ago (missed cycle)
    ❌  FAIL  democratic-integrity — Check 7: persistent-state.json missing or empty
    etc.

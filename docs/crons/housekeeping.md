# TASK: Weekly Housekeeping — Asymmetric Intelligence Platform
# CRON ID: fc210493
# CADENCE: Every Monday at 08:00 UTC (after all Monday publishes)
# VERSION: 2.0 — trimmed to 5 essential steps (4 Apr 2026, ~400 → ~200 credits/run)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. THIS TASK NEVER MODIFIES ANY FILE except HANDOFF.md and intelligence-digest.json.
2. Send notification ONLY on WARN or FAIL results, OR when digest flag count changes significantly.
3. On all-OK: exit silently (except the digest write, which always runs).
4. Use api_credentials=["github"] for all GitHub operations.
5. HTML/structural checks are handled by the CI validator on every push — do NOT repeat them here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — DATE GUARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check HANDOFF.md `last_updated` field. If already updated today (Monday),
exit silently — this run is a duplicate. Otherwise proceed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — DATA INTEGRITY (CHECK 1-3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each of the 7 monitors (fimi-cognitive-warfare, macro-monitor, democratic-integrity,
conflict-escalation, european-strategic-autonomy, ai-governance, environmental-risks):

```python
import subprocess, base64, json
from datetime import datetime, timezone, timedelta

MONITORS = [
    'fimi-cognitive-warfare', 'macro-monitor', 'democratic-integrity',
    'conflict-escalation', 'european-strategic-autonomy', 'ai-governance', 'environmental-risks'
]
today = datetime.now(timezone.utc).date()
issues = []

for slug in MONITORS:
    for fname in ['report-latest.json', 'persistent-state.json']:
        r = subprocess.run(['gh','api',
            f'/repos/asym-intel/asym-intel-main/contents/static/monitors/{slug}/data/{fname}',
            '--jq','.content'], capture_output=True, text=True)
        if r.returncode != 0:
            issues.append(f'CHECK_1: FAIL -- {slug}/{fname} missing')
            continue
        try:
            d = json.loads(base64.b64decode(r.stdout.strip()).decode('utf-8'))
        except:
            issues.append(f'CHECK_1: FAIL -- {slug}/{fname} invalid JSON')
            continue

        # CHECK 2: schema_version is "2.0"
        sv = d.get('schema_version') or d.get('_meta', {}).get('schema_version')
        if sv not in ('2.0', None):  # None = field absent, tolerate during transition
            if sv != '2.0':
                issues.append(f'CHECK_2: WARN -- {slug}/{fname} schema_version={sv}')

        # CHECK 3: report not stale (published within last 9 days)
        if fname == 'report-latest.json':
            pub = d.get('_meta', {}).get('published') or d.get('meta', {}).get('published')
            if pub:
                try:
                    pub_date = datetime.fromisoformat(pub.replace('Z','+00:00')).date()
                    age = (today - pub_date).days
                    if age > 9:
                        issues.append(f'CHECK_3: WARN -- {slug} report {age} days old (>{9})')
                except: pass

for issue in issues:
    print(issue)
if not issues:
    print('CHECK 1-3: OK')
```

REPORTING: Add any FAIL or WARN to the weekly notification.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — PIPELINE STUB CHECK (CHECK 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check that no pipeline output file still has status="stub". A stub means
the pipeline has never run for that monitor — it is silent breakage.

```python
PIPELINE_FILES = [
    'pipeline/monitors/{slug}/daily/daily-latest.json',
    'pipeline/monitors/{slug}/synthesised/synthesis-latest.json',
]

stubs = []
for slug in MONITORS:
    for template in PIPELINE_FILES:
        path = template.format(slug=slug)
        r = subprocess.run(['gh','api',f'/repos/asym-intel/asym-intel-main/contents/{path}',
            '--jq','.content'], capture_output=True, text=True)
        if r.returncode != 0: continue
        try:
            d = json.loads(base64.b64decode(r.stdout.strip()).decode('utf-8'))
            if d.get('_meta', {}).get('status') == 'stub':
                stubs.append(f'CHECK_4: WARN -- {path} still a stub')
        except: pass

for s in stubs:
    print(s)
if not stubs:
    print('CHECK 4: OK')
```

REPORTING: WARN on any stub found.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — CHATTER QUALITY AUDIT (CHECK 5-9)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each monitor, fetch chatter-latest.json and check signal quality.

```python
from collections import Counter
from urllib.parse import urlparse

MONITOR_ABBR = {
    'fimi-cognitive-warfare': 'FCW', 'macro-monitor': 'GMM',
    'democratic-integrity': 'WDM', 'conflict-escalation': 'SCEM',
    'european-strategic-autonomy': 'ESA', 'ai-governance': 'AGM',
    'environmental-risks': 'ERM',
}

for slug, abbr in MONITOR_ABBR.items():
    r = subprocess.run(['gh','api',
        f'/repos/asym-intel/asym-intel-main/contents/static/monitors/{slug}/data/chatter-latest.json',
        '--jq','.content'], capture_output=True, text=True)
    if r.returncode != 0:
        issues.append(f'CHECK_5: WARN -- {abbr} chatter-latest.json missing')
        continue
    d = json.loads(base64.b64decode(r.stdout.strip()).decode('utf-8'))
    meta = d.get('_meta', {})
    items = d.get('items', [])

    # CHECK 5: recency
    data_date_str = meta.get('data_date', '')
    if data_date_str:
        data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
        age = (today - data_date).days
        if age > 7:
            issues.append(f'CHECK_5: WARN -- {abbr} chatter {age} days old ({data_date_str})')

    # CHECK 6: item count
    if len(items) < 3:
        issues.append(f'CHECK_6: WARN -- {abbr} chatter only {len(items)} items')

    # CHECK 7: tier distribution
    if items:
        low = sum(1 for i in items if int(str(i.get('source_tier', 3))) >= 3)
        if low / len(items) > 0.6:
            issues.append(f'CHECK_7: WARN -- {abbr} chatter {int(low/len(items)*100)}% Tier 3/4')

    # CHECK 8: source bloat
    domains = []
    for item in items:
        url = item.get('source_url', '')
        if url:
            try: domains.append(urlparse(url).netloc.replace('www.', ''))
            except: pass
    for domain, count in Counter(domains).items():
        if count >= 3:
            issues.append(f'CHECK_8: WARN -- {abbr} chatter domain {domain} appears {count}x')

    if not any(abbr in i for i in issues):
        print(f'CHECK 5-8: {abbr} OK ({len(items)} items, {data_date_str})')

for issue in issues:
    print(issue)
```

REPORTING: Add any WARN to the weekly notification.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — GENERATE HANDOFF.md (always runs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read the current HANDOFF.md. Update the following fields only:
- `last_updated`: today's date (YYYY-MM-DD)
- `this_week_issues`: list any CHECK results that were WARN or FAIL
- `platform_status`: update any monitor status that changed this week
  (check if each monitor's report-latest.json published date changed vs last week)

Commit the updated HANDOFF.md to main with message:
`data(housekeeping): weekly update [skip ci]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — NOTIFY (conditional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If any CHECK returned WARN or FAIL:
  call send_notification() with:
    title: "Housekeeping — {N} issue(s) found"
    body: bullet list of all WARN/FAIL items from this run

If all checks passed:
  Exit silently. No notification.


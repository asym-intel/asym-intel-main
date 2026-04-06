# Housekeeping Cron — Asymmetric Intelligence Platform
<!-- VERSION: 3.0 | CRON ID: c725855f | Schedule: Mon 08:00 UTC -->

## Purpose
Runs every Monday at 08:00 UTC. Reads live repo state, checks platform health, regenerates HANDOFF.md from scratch. Sends notification only if issues found.

## Critical rules
1. **NEVER** modify any file except HANDOFF.md
2. Send notification **only** on WARN or FAIL, or significant digest flag change
3. All-OK: exit silently after writing HANDOFF.md
4. Use `api_credentials=["github"]` for all GitHub operations
5. HTML/structural checks handled by CI validator — do not repeat here

---

## Step 0 — Duplicate guard

```python
from datetime import date, timezone
import json

TODAY = date.today().isoformat()  # e.g. "2026-04-06"

# 1. Confirm it is Monday (weekday 0)
import datetime
if datetime.date.today().weekday() != 0:
    exit()  # not Monday — exit silently

# 2. Check last commit to HANDOFF.md was not already today
# Use GitHub API: GET /repos/{owner}/{repo}/commits?path=HANDOFF.md&per_page=1
# api_credentials=["github"]
last_commit_date = commits[0]["commit"]["committer"]["date"][:10]  # "YYYY-MM-DD"
if last_commit_date == TODAY:
    exit()  # already ran today — exit silently
```

---

## Step 1 — Report freshness (CHECK 1)

```python
MONITORS = {
    'fimi-cognitive-warfare': 'FCW',
    'macro-monitor': 'GMM',
    'democratic-integrity': 'WDM',
    'conflict-escalation': 'SCEM',
    'european-strategic-autonomy': 'ESA',
    'ai-governance': 'AGM',
    'environmental-risks': 'ERM',
}

import json
from datetime import date, timezone
import dateutil.parser

check1 = {}  # slug -> {status, published, age_days, issue}

for slug, code in MONITORS.items():
    path = f"static/monitors/{slug}/data/report-latest.json"
    # Fetch via GitHub Contents API — api_credentials=["github"]
    # GET /repos/{owner}/{repo}/contents/{path}
    try:
        content = base64.b64decode(response["content"]).decode()
        data = json.loads(content)
    except Exception:
        check1[slug] = {"status": "FAIL", "issue": f"{code}: report-latest.json missing or invalid JSON"}
        continue

    published_str = (
        data.get("meta", {}).get("published")
        or data.get("_meta", {}).get("published")
    )
    if not published_str:
        check1[slug] = {"status": "FAIL", "issue": f"{code}: published field missing in report-latest.json"}
        continue

    published = dateutil.parser.parse(published_str).date()
    age = (date.today() - published).days

    if age > 9:
        check1[slug] = {"status": "WARN", "published": published.isoformat(), "age": age,
                        "issue": f"{code}: report is {age}d old (missed weekly publish)"}
    else:
        check1[slug] = {"status": "OK", "published": published.isoformat(), "age": age}
```

---

## Step 2 — GA pipeline freshness (CHECK 2)

```python
check2 = {}  # slug -> {daily: {...}, synthesis: {...}}

for slug, code in MONITORS.items():
    result = {"daily": None, "synthesis": None}

    # --- Daily collector ---
    path = f"pipeline/monitors/{slug}/daily/daily-latest.json"
    try:
        data = fetch_json_from_repo(path)  # via GitHub Contents API, api_credentials=["github"]
        if data.get("status") == "stub":
            result["daily"] = {"status": "WARN", "issue": f"{code} daily: status=stub (pipeline never ran)"}
        else:
            gen_str = data.get("_meta", {}).get("generated_at") or data.get("_meta", {}).get("data_date")
            if gen_str:
                gen_date = dateutil.parser.parse(gen_str).date()
                age = (date.today() - gen_date).days
                if age > 2:
                    result["daily"] = {"status": "WARN", "date": gen_date.isoformat(), "age": age,
                                       "issue": f"{code} daily: {age}d old (collector stopped)"}
                else:
                    result["daily"] = {"status": "OK", "date": gen_date.isoformat(), "age": age}
            else:
                result["daily"] = {"status": "WARN", "issue": f"{code} daily: no date field found"}
    except FileNotFoundError:
        result["daily"] = {"status": "WARN", "issue": f"{code} daily: daily-latest.json missing"}

    # --- Synthesiser ---
    path = f"pipeline/monitors/{slug}/synthesised/synthesis-latest.json"
    try:
        data = fetch_json_from_repo(path)
        if data.get("status") == "stub":
            result["synthesis"] = {"status": "WARN", "issue": f"{code} synthesis: status=stub"}
        else:
            syn_str = (
                data.get("_meta", {}).get("synthesised_at")
                or data.get("_meta", {}).get("generated_at")
            )
            if syn_str:
                syn_date = dateutil.parser.parse(syn_str).date()
                age = (date.today() - syn_date).days
                if age > 9:
                    result["synthesis"] = {"status": "WARN", "date": syn_date.isoformat(), "age": age,
                                           "issue": f"{code} synthesis: {age}d old"}
                else:
                    result["synthesis"] = {"status": "OK", "date": syn_date.isoformat(), "age": age}
            else:
                result["synthesis"] = {"status": "WARN", "issue": f"{code} synthesis: no date field found"}
    except FileNotFoundError:
        result["synthesis"] = None  # optional file — absence is not a WARN

    check2[slug] = result
```

---

## Step 3 — Hugo brief freshness (CHECK 3)

```python
check3 = {}  # slug -> {status, brief_date, age, issue}

import re

for slug, code in MONITORS.items():
    dir_path = f"content/monitors/{slug}"
    # Fetch directory listing via GitHub Trees or Contents API — api_credentials=["github"]
    # GET /repos/{owner}/{repo}/contents/{dir_path}
    try:
        entries = fetch_dir_listing(dir_path)
    except Exception:
        check3[slug] = {"status": "WARN", "issue": f"{code} brief: content directory not found"}
        continue

    brief_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-weekly-brief\.md$")
    brief_dates = []
    for entry in entries:
        m = brief_pattern.search(entry["name"])
        if m:
            brief_dates.append(m.group(1))

    if not brief_dates:
        check3[slug] = {"status": "WARN", "issue": f"{code} brief: no weekly-brief.md file found"}
        continue

    latest_brief = max(brief_dates)
    brief_date = date.fromisoformat(latest_brief)
    age = (date.today() - brief_date).days

    if age > 9:
        check3[slug] = {"status": "WARN", "date": latest_brief, "age": age,
                        "issue": f"{code} brief: most recent brief is {age}d old"}
    else:
        check3[slug] = {"status": "OK", "date": latest_brief, "age": age}
```

---

## Step 4 — Pipeline stub check (CHECK 4)

```python
check4 = {}  # slug -> list of issues

for slug, code in MONITORS.items():
    issues = []

    for kind, label in [("weekly/weekly-latest.json", "weekly"),
                         ("reasoner/reasoner-latest.json", "reasoner")]:
        path = f"pipeline/monitors/{slug}/{kind}"
        try:
            data = fetch_json_from_repo(path)
            if data.get("status") == "stub":
                issues.append(f"{code} {label}: status=stub")
        except FileNotFoundError:
            pass  # optional — absence is OK

    check4[slug] = issues  # empty list = all OK
```

---

## Step 5 — Chatter quality (CHECK 5)

```python
from collections import Counter
from urllib.parse import urlparse

check5 = {}  # slug -> list of issues

for slug, code in MONITORS.items():
    issues = []
    path = f"static/monitors/{slug}/data/chatter-latest.json"

    try:
        data = fetch_json_from_repo(path)
    except FileNotFoundError:
        check5[slug] = [f"{code} chatter: chatter-latest.json missing"]
        continue

    # Age check
    data_date_str = data.get("_meta", {}).get("data_date")
    if data_date_str:
        data_date = dateutil.parser.parse(data_date_str).date()
        age = (date.today() - data_date).days
        if age > 7:
            issues.append(f"{code} chatter: data_date is {age}d old")
    else:
        issues.append(f"{code} chatter: no data_date field")

    # Item count
    items = data.get("items", [])
    if len(items) < 3:
        issues.append(f"{code} chatter: only {len(items)} item(s) (minimum 3)")

    # Domain concentration
    domains = []
    for item in items:
        url = item.get("source_url", "")
        if url:
            try:
                domains.append(urlparse(url).netloc.lower())
            except Exception:
                pass
    domain_counts = Counter(domains)
    for domain, count in domain_counts.items():
        if count >= 3:
            issues.append(f"{code} chatter: domain '{domain}' appears {count}x")

    check5[slug] = issues
```

---

## Step 5b — Computer task credit check (CHECK 6)

Check this week's Computer task list for unusually high credit usage. High usage weeks
indicate either a large infrastructure session (expected occasionally) or runaway/repeated
task invocations (unexpected — should be flagged).

**Target:** ≤6,000 credits/week for normal operation. Weeks with large infrastructure
work (pipeline builds, governance rewrites) may legitimately exceed this.

```python
# Use schedule_cron list output — fetch recent Computer tasks from the platform
# This step uses the list_cron_tasks tool available to Computer agents
import subprocess, json

# Fetch last 7 days of Computer task usage via the Computer tasks API
# Note: this requires the platform task listing tool — call it directly
task_result = subprocess.run(
    ['python3', '-c', '''
import json
# Call schedule_cron list to get active crons and their last-run metadata
# The weekly credit total must be estimated from session logs
# Housekeeping cannot directly query billing — log a reminder instead
print(json.dumps({"status": "manual_check", "note": "Review task credits at perplexity.ai/computer/tasks"}))
'''],
    capture_output=True, text=True
)

# Since direct billing API access is unavailable, housekeeping adds a standing
# weekly reminder to check credits, and flags if any single task this week
# shows an unusually large individual run (heuristic: check notes-for-computer.md
# for any session notes mentioning large subagent spawning)

# Check notes-for-computer.md for this week's session activity
notes_r = subprocess.run(
    ['gh', 'api',
     '/repos/asym-intel/asym-intel-internal/contents/notes-for-computer.md',
     '--jq', '.content'],
    capture_output=True, text=True
)
check6_note = None
if notes_r.returncode == 0:
    import base64, datetime
    notes = base64.b64decode(notes_r.stdout.strip()).decode('utf-8')
    # Check if this week has a large session note (subagent spawning, pipeline builds)
    this_week = datetime.date.today().isocalendar()[1]
    if 'subagent' in notes.lower() or 'parallel' in notes.lower():
        check6_note = "WARN: notes-for-computer.md shows subagent/parallel session activity this week — review credit usage at perplexity.ai/computer/tasks"
    else:
        check6_note = None

check6 = check6_note
```

**Credit budget reminder** — always include in HANDOFF.md regardless of check result:
- Target: ≤6,000 credits/week (normal operation)
- Normal Analyst cron week: ~700 credits (7 × ~100)
- Infrastructure sessions: 5,000–30,000 (expected occasionally)
- Review weekly at: https://www.perplexity.ai/computer/tasks


---

## Step 6 — Generate HANDOFF.md (ALWAYS runs)

Aggregate all check results then write HANDOFF.md. Fetch the previous HANDOFF.md first to carry forward the "Open — Peter Action Required" section verbatim.

```python
# --- Fetch previous HANDOFF.md ---
prev_handoff = fetch_file_from_repo("HANDOFF.md")  # api_credentials=["github"]

# Extract "Open — Peter Action Required" section verbatim
import re
open_section_match = re.search(
    r"(## Open — Peter Action Required\n)(.*?)(\n## |\Z)",
    prev_handoff,
    re.DOTALL
)
open_section_body = open_section_match.group(2).strip() if open_section_match else ""

# --- Compile all issues ---
all_issues = []

for slug, code in MONITORS.items():
    r = check1.get(slug, {})
    if r.get("status") in ("WARN", "FAIL"):
        all_issues.append(r["issue"])

for slug in MONITORS:
    r = check2.get(slug, {})
    for sub in ("daily", "synthesis"):
        if r.get(sub) and r[sub].get("status") == "WARN":
            all_issues.append(r[sub]["issue"])

for slug, r in check3.items():
    if r.get("status") == "WARN":
        all_issues.append(r["issue"])

for slug, issues in check4.items():
    all_issues.extend(issues)

for slug, issues in check5.items():
    all_issues.extend(issues)

if check6:
    all_issues.append(check6)

issues_text = "\n".join(f"- {i}" for i in all_issues) if all_issues else "None — all checks passed"

# --- Build Platform Status table ---
def status_emoji(slug):
    c1 = check1.get(slug, {}).get("status", "?")
    c3 = check3.get(slug, {}).get("status", "?")
    if c1 == "FAIL" or c3 == "FAIL":
        return "❌"
    if c1 == "WARN" or c3 == "WARN":
        return "⚠️"
    return "✅"

platform_rows = []
for slug, code in MONITORS.items():
    c1 = check1.get(slug, {})
    c3 = check3.get(slug, {})
    published = c1.get("published", "—")
    age = c1.get("age", "—")
    brief_date = c3.get("date", "—")
    issue_count = sum(1 for i in all_issues if i.startswith(code + ":") or i.startswith(code + " "))
    emoji = status_emoji(slug)
    platform_rows.append(
        f"| {code} | {published} | {'#' + str(issue_count) if issue_count else '—'} | {age}d | {brief_date} | {emoji} |"
    )

# --- Build GA Pipeline Status table ---
pipeline_rows = []
for slug, code in MONITORS.items():
    c2 = check2.get(slug, {})
    daily = c2.get("daily") or {}
    synth = c2.get("synthesis") or {}
    c4_issues = check4.get(slug, [])

    def fmt(d, label):
        if not d:
            return "—"
        pfx = "⚠️ " if d.get("status") == "WARN" else ""
        if d.get("date"):
            return f"{pfx}{d['date']} ({d.get('age', '?')}d)"
        return f"{pfx}{d.get('issue', '?')}"

    weekly_stub = "⚠️ stub" if any("weekly" in i for i in c4_issues) else "—"
    pipeline_rows.append(
        f"| {code} | {fmt(daily, 'daily')} | {fmt(synth, 'synthesis')} | {weekly_stub} |"
    )

# --- Render HANDOFF.md ---
handoff = f"""# HANDOFF.md — Asymmetric Intelligence Platform
**Generated:** {TODAY} by Housekeeping cron (Mon 08:00 UTC)

## Platform Status

| Monitor | Last Published | Issue | Age | Brief | Status |
|---|---|---|---|---|---|
{chr(10).join(platform_rows)}

## GA Pipeline Status

| Monitor | Daily Collector | Synthesiser | Weekly Research |
|---|---|---|---|
{chr(10).join(pipeline_rows)}

## Analyst Cron IDs

| Monitor | Cron ID | Schedule |
|---|---|---|
| WDM | adad85f6 | Mon 06:00 UTC |
| GMM | 6efe51b0 | Tue 08:00 UTC |
| ESA | 72398be9 | Wed 19:00 UTC |
| FCW | 478f4080 | Thu 09:00 UTC |
| AGM | b53d2f93 | Fri 09:00 UTC |
| ERM | 0aaf2bd7 | Sat 05:00 UTC |
| SCEM | 743bbe21 | Sun 18:00 UTC |
| Housekeeping | c725855f | Mon 08:00 UTC |

## This Week — Issues Found
{issues_text}

## Credit Budget
Target: ≤6,000 credits/week (normal operation). Analyst crons alone: ~700/week.  
Infrastructure sessions legitimately exceed this — check context in notes-for-computer.md.  
Review: https://www.perplexity.ai/computer/tasks

## Open — Peter Action Required
{open_section_body}

## Next Session
"""

# --- Commit HANDOFF.md ---
# PUT /repos/{owner}/{repo}/contents/HANDOFF.md
# message: "data(housekeeping): weekly HANDOFF regeneration — {TODAY} [skip ci]"
# api_credentials=["github"]
commit_file_to_repo(
    path="HANDOFF.md",
    content=handoff,
    message=f"data(housekeeping): weekly HANDOFF regeneration — {TODAY} [skip ci]"
)
```

---

## Step 7 — Notify (conditional)

```python
if all_issues:
    send_notification(
        title=f"Housekeeping — {len(all_issues)} issue(s) found",
        body="\n".join(f"- {i}" for i in all_issues)
    )
# All-OK: exit silently (no notification)
```

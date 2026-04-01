# TASK: Weekly Housekeeping — Asymmetric Intelligence Platform
# CRON ID: fc210493
# CADENCE: Every Monday at 06:00 UTC (after all monitor publishes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. THIS TASK NEVER MODIFIES ANY FILE. Read-only audit only.
2. Send notification ONLY on WARN or FAIL results.
3. On all-OK: exit silently with no notification.
4. Use api_credentials=["github"] for all GitHub operations.

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
CHECKS (run for every HTML page of every monitor)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each page, fetch content from:
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/{PAGE}.html \
    --jq '.content' | base64 -d

Run these checks:

CHECK 1 — Network bar present
  PASS: content contains 'data-asym-network-bar'
  NOTE: Since Blueprint v2.1, nav.js auto-injects the network bar if absent.
        This check verifies the JS is loading correctly by checking the
        rendered marker. Flag WARN if absent (may indicate nav.js not loading).

CHECK 2 — Inline offset style block absent (Blueprint v2.1+)
  PASS: content does NOT contain 'padding-top:40px'
  WARN: if inline offset style block is still present (should have been stripped)

CHECK 3 — Shared JS files referenced
  PASS: content contains 'shared/js/nav.js'
  FAIL: if nav.js reference is missing (network bar won't auto-inject)

CHECK 4 — Monitor CSS referenced
  PASS: content contains 'assets/monitor.css'
  WARN: if missing

CHECK 5 — No dead script blocks after </html>
  PASS: no content after closing </html> tag
  WARN: if content found after </html> (browser silently ignores it)

CHECK 6 — No future dates in meta published fields (data files only)
  For each monitor, fetch data/report-latest.json and check:
    meta.published date is <= today's UTC date
  FAIL: if published date is in the future (Hugo will skip it)

CHECK 7 — report-latest.json and persistent-state.json exist and are non-empty
  For each monitor:
    gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/data/report-latest.json --jq '.size'
    gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{MONITOR}/data/persistent-state.json --jq '.size'
  FAIL: if either file is missing (404) or size < 100 bytes

CHECK 8 — schema_version is "2.0" in all JSON files
  PASS: meta.schema_version == "2.0" in report-latest.json
  WARN: if schema_version is missing or != "2.0"

CHECK 9 — No inline network bar HTML present (Blueprint v2.1+)
  PASS: content does NOT contain '<nav data-asym-network-bar' as inline HTML
  NOTE: The bar is now injected by nav.js — if it appears as static HTML,
        the page has not been updated to Blueprint v2.1 and will render
        a duplicate bar once nav.js also injects one.
  WARN: if static network bar HTML found in page source

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHECK 10 — Staging branch is ahead of or equal to main
  Run: gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '.ahead_by'
  WARN: if staging is 0 commits ahead of main AND recent commits to main were not from
        github-actions[bot] (i.e. a human pushed HTML/CSS directly to main)

RESULT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compile results as:
  PASS  — check passed
  WARN  — non-critical issue (degraded experience, not broken)
  FAIL  — critical issue (broken functionality)

If all 9 checks pass for all monitors: exit silently. No notification.

If any WARN or FAIL:
  Send notification with title: "Asym Intel — Housekeeping [DATE]: [N] issues"
  Body: list each WARN/FAIL with monitor, page, check number, and description.
  Format:
    ⚠️  WARN  democratic-integrity/overview.html  — Check 2: inline offset styles still present
    ❌  FAIL  macro-monitor — Check 7: persistent-state.json missing or empty
    etc.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cron: 0 8 * * 1 (every Monday at 08:00 UTC — after all Monday publishes)

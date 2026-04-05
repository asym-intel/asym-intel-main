# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-05 afternoon wrap (~16:25 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session start checklist
Load asym-intel skill + asym-intel-charts skill. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, docs/ROADMAP.md.

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '{ahead_by:.ahead_by}'
gh api /repos/asym-intel/asym-intel-main/commits?per_page=5 --jq '[.[] | {sha:.sha[:8],msg:.commit.message[:60]}]'
```

---

## OPEN BUG — Fix first

### GMM sentiment overlay chart stuck on "Loading…"
Section: `#section-sentiment` / div `#sentiment-overlay-wrap`
Render function: `renderSentimentOverlay()` was added but chart never renders.
Data confirmed present: `d.sentiment_overlay.fed_funds_futures[]` (5 meetings populated).

Debug approach:
1. Open staging with DevTools console open
2. Load https://staging.asym-intel.info/monitors/macro-monitor/dashboard.html
3. Check for Chart.js errors, undefined variable errors, or canvas sizing issues
4. Likely cause: Chart.js `new Chart()` call failing silently — canvas may not exist
   at time of call, OR `getComputedStyle` returning empty string for accent colour
5. Fix: ensure canvas exists before Chart() call; fallback accent colour to '#22a0aa'

---

## Priority queue

### TASK 1 — Verify synthesiser pipeline runs
- SCEM: synthesiser fired Sun 5 Apr 10:00 UTC, Analyst 18:00 UTC — check data/report-latest.json
- WDM: synthesiser fires Sun 5 Apr 21:00 UTC
- GMM: synthesiser Mon 6 Apr 20:00 UTC, Analyst Tue 7 Apr 08:00 UTC
Check each: pipeline/ output exists → Analyst JSON valid → new issue published

### TASK 2 — SCEM Visual Sprint 2
NEW-02: Confidence Quality Summary Bar (LOW risk → main direct)
NEW-03: Deviation Heatmap PNG
Read: asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md

### TASK 3 — Per-monitor search.html chatter indexing
search.js v1.1 (built, never merged). MEDIUM risk → staging + screenshot.
Also: add chatter-index.json to Housekeeping cron (eliminates date-probing).

### TASK 4 — Homepage network graph section
layouts/index.html — Hugo layout change → main direct.

### THEN
- PED Sprint 2: Q4/Q6/Q7/Q8 (Peter decisions needed)
- Analytics: Plausible vs Fathom (Peter decision pending)
- Asymmetric Investor commercial entry point (Peter to revert)

---

## Key facts
- All 7 synthesiser schedules LIVE (commit 3ee1ff7c)
- All 8 Analyst crons live
- Data surfacing complete across all 7 monitors (PR #39 + PR #40)
- Canonical sourceLink: AsymRenderer.sourceLink(url) — no esc(), no guard (FE-027, ARCHITECTURE.md)
- Signal block body: class="signal-block__body" only — never --color-text-muted inside .signal-block
- Asymmetric Investor: investor.asym-intel.info — internal docs updated
- ERG monitor: Q3 2026 methodology stub only; no build until GMM migrates commercially
- Staging clean (ahead_by: 0)

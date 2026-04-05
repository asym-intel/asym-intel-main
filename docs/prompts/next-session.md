# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-05 wrap (~10:30 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session start checklist

Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, docs/ROADMAP.md before starting.

```bash
# Verify platform healthy
curl -s -o /dev/null -w "%{http_code}" https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json
# Verify staging clean
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '{ahead_by:.ahead_by}'
# Verify recent commits
gh api /repos/asym-intel/asym-intel-main/commits?per_page=5 --jq '[.[] | {sha:.sha[:8],msg:.commit.message[:60]}]'
```

---

## Priority queue

### TASK 1 — Verify synthesiser runs
All 7 synthesisers now scheduled. Check first runs landed:
- SCEM: fired Sun 5 Apr 10:00 UTC → check pipeline/monitors/conflict-escalation/
- SCEM Analyst: fires Sun 5 Apr 18:00 UTC → check data/report-latest.json after
- WDM synthesiser: fires Sun 5 Apr 21:00 UTC
- GMM synthesiser: fires Mon 6 Apr 20:00 UTC
For each: confirm synthesiser JSON valid → Analyst published cleanly.

### TASK 2 — SCEM Visual Sprint 2
NEW-02: Confidence Quality Summary Bar (JS-AUTO, LOW risk → main direct)
NEW-03: Deviation Heatmap PNG
Read: asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md first.

### TASK 3 — Homepage network graph section
Add section in layouts/index.html — Hugo layout change → main directly.

### TASK 4 — Per-monitor search.html chatter indexing
search.js v1.1 was built (commit b7872497 on staging) but staging was reset.
Rebuild from /tmp or re-apply the chatter date-probing logic from search.js v1.1.
This is MEDIUM risk (shared JS) → staging + screenshot before merge.

### TASK 5 — chatter-index.json (Housekeeping)
Add to Housekeeping cron: scan each monitor's data/ for chatter-{date}.json files,
write data/chatter-index.json with {"dates":["2026-04-03","..."]}
Unblocks fast chatter loading in search (no date-probing needed).

### THEN
- PED Sprint 2: Q4/Q6/Q7/Q8 (Peter decisions needed)
- Analytics: Plausible vs Fathom (Peter decision pending)
- Asymmetric Investor commercial entry point (Peter to revert)

---

## Key facts
- All 8 Analyst crons live (COMPUTER.md for IDs)
- All 7 synthesiser schedules LIVE (commit 3ee1ff7c)
- Tiered deployment: LOW risk → main direct; MEDIUM → staging + screenshot; HIGH → staging + Peter sign-off
- Canonical sourceLink: AsymRenderer.sourceLink(url) — no esc(), no guard (FE-027)
- Signal block body text: class="signal-block__body" only — never --color-text-muted inside .signal-block
- Asymmetric Investor brand confirmed: investor.asym-intel.info
- ERG monitor: methodology stub Q3 2026, no build until GMM migrates commercially

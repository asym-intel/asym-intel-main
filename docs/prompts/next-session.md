# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-06 wrap (~09:00 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session start checklist
Load asym-intel + asym-intel-charts skills. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, docs/ROADMAP.md.

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '{ahead_by:.ahead_by}'
gh api /repos/asym-intel/asym-intel-main/commits?per_page=5 --jq '[.[] | {sha:.sha[:8],msg:.commit.message[:60]}]'
```

## Session gate check (COMPUTER.md v3.6 rule)
Before doing anything: did housekeeping send a notification? If no notification and no
live incident, apply the session gate — batch work for next scheduled session.

---

## Priority queue

### TASK 1 — Validate first pipeline runs
Check these in order — most are first-ever runs:
- GMM weekly-research: Mon 16:00 UTC today → `pipeline/monitors/macro-monitor/weekly/weekly-latest.json`
- WDM collector: Tue 07:00 UTC → `pipeline/monitors/democratic-integrity/daily/daily-latest.json`
- ESA weekly-research: Tue 18:00 UTC → first ever run
- AGM weekly-research: Thu 18:00 UTC → first ever run
- ERM weekly-research: Fri 16:00 UTC → first ever run
For each: check _meta.status != stub, check finding_count > 0, check no debug-*.json left behind

### TASK 2 — SCEM Visual Sprint 2
NEW-02: Confidence Quality Summary Bar (LOW risk → main direct)
NEW-03: Deviation Heatmap PNG
Read: asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md
Note: SCEM deviation calculation now fixed in cron prompt — first corrected output next Sunday

### TASK 3 — WDM persistent.html validation
After next Monday WDM Analyst run, check persistent.html for:
- electoral_watch section populated (no "Build 2" placeholder)
- institutional_pulse, legislative_watch, digital_civil populated
- signal.history array present in signal_panel
- severity_sub sub-scores visible on heatmap entries

### TASK 4 — Homepage network graph
layouts/index.html Hugo layout change → main directly.

---

## Critical rules added last session
- **Session gate:** check 3 questions before opening a session (COMPUTER.md v3.6)
- **Sequential-first subagents:** parallel only when time is binding constraint
- **GMM/FCW prompts in internal:** scripts fetch via gh api — never local path
- **ESA/AGM/ERM reasoner prompts:** now external at docs/crons/reasoner-prompts/
- **WDM persistent.html living knowledge fields:** 8 fields now in cron Step 5 spec
- **SCEM deviation:** deviation = level - baseline; CONTESTED only when cannot assess

## Open — Peter Action Required
- ⚠️ GSC sitemap: delete and resubmit in Search Console
- ⚠️ PED Sprint 2 decisions: parked until June
- ⚠️ Analytics provider: Plausible vs Fathom (parked)
- ⚠️ Branch protection on main (GitHub repo settings)

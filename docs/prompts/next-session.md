# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-06 final wrap (~10:00 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

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
- AGM weekly-research: Thu 18:00 UTC → first ever run (also first Ramparts-methodology-informed run)
- ERM weekly-research: Fri 16:00 UTC → first ever run
- AGM Analyst: Fri 09:00 UTC → first run with Step 7 Ramparts publication
For each: check _meta.status != stub, finding_count > 0, no debug-*.json

### TASK 2 — Ramparts first integrated publish (Fri 09:00 UTC)
AGM Analyst Step 7 will attempt the first Ramparts publication from the integrated pipeline.
Monitor for: WordPress update success, PDF generation, Buttondown digest sent.
Credentials need adding to platform-config.md before this fires — read:
  asym-intel-internal/ramparts-prompts/platform-config-additions.md
Then add to asym-intel-internal/platform-config.md before Thu 18:00 UTC.

### TASK 3 — WDM persistent.html validation
After next Monday WDM Analyst run, check persistent.html sections populate (no "Build 2" placeholders).

### TASK 4 — SCEM Visual Sprint 2
NEW-02: Confidence Quality Summary Bar, NEW-03: Deviation Heatmap
Read: asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md

### TASK 5 — Homepage network graph
layouts/index.html Hugo layout → main directly.

---

## Ramparts/AGM integration status (completed 6 Apr 2026)
- AGM display name: Artificial Intelligence Monitor (AIM) — slug ai-governance unchanged
- AGM Analyst cron (b53d2f93): Step 7 added — publishes to ramparts.gi after asym-intel.info
- Publisher instructions: asym-intel-internal/ramparts-prompts/ramparts-publisher-cron.md
- Methodology digest: asym-intel-internal/ramparts-prompts/ramparts-methodology-digest.md
- asym-intel/Ramparts repo: marked as archive — no longer operational
- ⚠️ BEFORE FIRST RUN: add Ramparts credentials to platform-config.md (see platform-config-additions.md)
- ⚠️ ROTATE credentials: WP app password + Buttondown API key were previously in public repo

## Critical rules added this session
- **Session gate:** 3-question check before opening any session (COMPUTER.md v3.6)
- **Sequential-first subagents:** parallel only when time is the binding constraint
- **GMM/FCW prompts in internal:** scripts fetch via gh api — never local path
- **ESA/AGM/ERM reasoner prompts:** now external at docs/crons/reasoner-prompts/
- **WDM persistent.html living knowledge:** 8 fields now in cron Step 5 spec
- **SCEM deviation:** deviation = level - baseline; CONTESTED only when cannot assess
- **Ramparts architecture:** one cron, two publication targets — uniform slim-pointer pattern

## Open — Peter Action Required
- ⚠️ Add Ramparts credentials to platform-config.md BEFORE Thu 18:00 UTC (AGM weekly fires)
- ⚠️ Rotate WP app password + Buttondown API key (were briefly in public repo)
- ⚠️ GSC sitemap: delete and resubmit in Search Console
- ⚠️ PED Sprint 2 decisions: parked until June
- ⚠️ Analytics provider: Plausible vs Fathom (parked)
- ⚠️ Branch protection on main (GitHub repo settings)

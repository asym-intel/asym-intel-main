# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-07 wrap (~10:45 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session gate check (COMPUTER.md v3.9 rule)
No notification from housekeeping = platform healthy = no session needed.
Only open if: pipeline failure notification, missed publish, or Sprint 1 work scheduled.

---

## HIGHEST PRIORITY — Pipeline conformance pass

**Before any other pipeline work:** audit all 6 remaining analyst crons and synthesiser
prompts against the new specs. Do this as one focused session.

Read both specs first:
```bash
gh api /repos/asym-intel/asym-intel-main/contents/docs/pipeline/ANALYST-CRON-SPEC.md --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/docs/pipeline/SYNTHESISER-SPEC.md --jq '.content' | base64 -d
```

Monitors needing conformance pass: **WDM, ESA, AGM, ERM, FCW, SCEM**
(GMM is already conformant — updated 7 Apr 2026)

For each: run the conformance checklist in ANALYST-CRON-SPEC.md. Fix all gaps in one pass.
Then run SYNTHESISER-SPEC.md checklist against each synthesiser prompt.

---

## Priority queue

### TASK 1 — Validate pipeline runs (this week)
- ESA weekly-research: Tue 18:00 UTC today (first ever run — check output)
- WDM/FCW/SCEM collectors: Wed 07:00 UTC (first run with search_recency_filter)
- GMM weekly-research: Mon 16:00 UTC next week (first run with GH_TOKEN + search_recency)
- AGM weekly-research: Thu 18:00 UTC (first ever run)
- ERM weekly-research: Fri 16:00 UTC (first ever run)
For each: check _meta.status=complete, finding_count > 0, no null_signal_week=true

### TASK 2 — Conformance pass (6 monitors)
See above. Do not defer — every week without this risks another manual publish.

### TASK 3 — Sprint 1: Shared foundations
SL-09 first (accent tokens) → monitor strip → SL-04 → SL-08 → SL-03 → SL-02 → SL-01 → HP-01 → HP-02
All specs signed off. Homepage copy, badge spec, mockup all approved.

### TASK 4 — WDM persistent.html validation
After Mon 13 Apr WDM Analyst run — check living knowledge sections populated.

### TASK 5 — SCEM Visual Sprint 2
NEW-02 + NEW-03 — wait for first corrected SCEM deviation output (Sun 18 Apr).

---

## Pipeline fixes applied 7 Apr 2026
- GH_TOKEN: all 14 workflow files fixed
- search_recency_filter: all 7 collectors (week) + all 7 weekly-research (month)
- GMM synthesiser prompt v1.1: regime/conviction/system_average/lead_signal added
- GMM analyst cron: pipeline_inputs + weekly_brief JSON requirement added
- COMPUTER.md v3.9: Platform-First Fix Rule + pipeline specs in Step 0
- docs/pipeline/ANALYST-CRON-SPEC.md + SYNTHESISER-SPEC.md: v1.0 committed

## Open — Peter Action Required
- ⚠️ Rotate WP app password + Buttondown API key (were briefly public)
- ⚠️ GSC sitemap: delete and resubmit
- ⚠️ Analytics: Plausible vs Fathom
- ⚠️ Branch protection on main

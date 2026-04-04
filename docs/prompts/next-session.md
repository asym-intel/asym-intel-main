# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 evening wrap (~22:40 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, and docs/ROADMAP.md before starting.

--- VERIFY LIVE FIRST ---
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Must show v1.3
Screenshot https://asym-intel.info/monitors/democratic-integrity/dashboard.html
→ Must NOT show "Failed to load data."

--- GMM RULE (read before touching anything GMM) ---
GMM methodology and prompts are PRIVATE. They live in asym-intel-internal/gmm-prompts/ only.
Never commit GMM IP to asym-intel-main or any public repo.

--- SYNTHESISER RE-RUNS (do first) ---

TASK 1: Trigger GMM/WDM/SCEM/AGM synthesisers via workflow_dispatch.
  Stagger 45s apart. Guard should have cleared (last runs were 4 Apr).
  Verify synthesis-latest.json output_type is NOT null_signal_week.
  If any still fail: check debug-{date}.json for error details.

TASK 2: Once all 7 pass (FCW/ESA/ERM already pass) → enable scheduled triggers:
  FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC | SCEM: Sat 10:00 UTC
  ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC

TASK 3: Monitor first slim Analyst cron runs (all new IDs — see HANDOFF.md):
  SCEM: Sun 5 Apr 18:00 UTC (first to fire)
  WDM: Mon 6 Apr 06:00 UTC
  Check that each loads its prompt from repo and publishes successfully.

--- THEN ---
- PED Sprint 2: surface Q4/Q6/Q7/Q8 first
- Analytics: decide Plausible vs Fathom
```

## Session summary (4 Apr 2026 — evening)

### Crons
- All 8 slim crons created (old crons deleted by Peter from UI)
- COMPUTER.md, HANDOFF.md, docs/crons/README.md all updated with new IDs
- First runs: SCEM Sun 5 Apr, WDM/Housekeeping Mon 6 Apr

### FCW Schema Migration
- PR #35 merged — dual-schema fallbacks on dashboard, report, overview
- Works with both old (signal/f_flags/cognitive_warfare) and new (lead_signal/mf_flags/intelligence_highlights) schemas

### Governance
- Staging-reset protection rule added (COMPUTER.md pitfall #17, wrap Steps 5-6)
- Prevents reset of staging while files await visual sign-off

### Commercial / ERG
- Commercial development note committed to asym-intel-internal/commercial/
- ERG methodology skeleton committed to asym-intel-internal/methodology/
- ERG confirmed as abbreviation (not EGM — avoids ERM collision)
- No build work — future threads only

### Platform
- Staging: clean (0/0)
- Site: healthy, nav.js v1.3, dashboards rendering

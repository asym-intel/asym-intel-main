# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 final wrap (~16:20 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md,
and asym-intel-internal/prompt-improvements.md before starting.

--- VERIFY LIVE FIRST ---
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Must show v1.3. If not: workflow_dispatch build.yml + CF purge-all-files (Zone: cc419b7519eba04ef0dc6a7b851930c7)
Screenshot https://asym-intel.info/monitors/democratic-integrity/dashboard.html
→ Must NOT show "Failed to load data."

--- SYNTHESISER FIXES (do first) ---

TASK 1: Fix apostrophe JSON parse error — GMM/WDM/SCEM/AGM synthesiser prompts.
Add to RULES section of each prompt:
"Never use apostrophes or contractions in JSON string values.
Use full words only (e.g. 'this weeks' not 'this week's', 'does not' not 'doesn't')."
Files:
  pipeline/synthesisers/gmm/macro-monitor-synthesiser-api-prompt.txt
  pipeline/synthesisers/wdm/democratic-integrity-synthesiser-api-prompt.txt
  pipeline/synthesisers/scem/conflict-escalation-synthesiser-api-prompt.txt
  pipeline/synthesisers/agm/ai-governance-synthesiser-api-prompt.txt
Bump VERSION to v1.1 in each. Log to prompt-improvements.md.

TASK 2: Re-run all 4 after fix (guard clears after midnight UTC):
  macro-monitor-synthesiser.yml, democratic-integrity-synthesiser.yml,
  conflict-escalation-synthesiser.yml, ai-governance-synthesiser.yml
Stagger 45s apart. Verify FULL_OUTPUT (not _raw_fallback) in synthesis-latest.json.

TASK 3: Once all 7 pass manual test — enable scheduled triggers:
  FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC | SCEM: Sat 10:00 UTC
  ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC

TASK 4: Recreate FCW Analyst cron using asym-intel-internal/fcw-slimmed-analyst-cron.md
  - Delete cron b17522c3 (current FCW weekly full Analyst)
  - Create new slim cron from task description in fcw-slimmed-analyst-cron.md
  - Verify one end-to-end FCW Analyst run
  - Roll pattern to GMM, WDM, SCEM, ESA, AGM, ERM (each has docs/crons/{abbr}-slimmed-analyst-cron.md)

--- THEN ---
- PED Sprint 2: surface Q4/Q6/Q7/Q8 first
- Analytics: decide Plausible vs Fathom (needed before Tier 3 build)
```

## Session summary (4 Apr 2026)

### Architecture locked
- COLLECTOR-ANALYST-ARCHITECTURE v2.2 — all 7 monitors weekly, synthesiser layer defined
- editorial-strategy.md v1.2 — access model (all open, Buttondown, future API), CC BY 4.0
- development-plan.md v1.2 — corrections policy A-D, open decisions, build sequence to 2028

### All 7 synthesisers committed
FCW/ESA/ERM: ✅ validated | GMM/WDM: ⚠️ apostrophe fix needed | SCEM/AGM: ⚠️ guard (tomorrow)

### Platform ops
- Housekeeping trimmed: 5 steps, 204 lines, ~200 credits/run, runs Monday as normal
- Methodology published: docs/methodology/ CC BY 4.0 (14 files)
- pipeline-overview.md deleted (superseded)
- All synthesiser workflows: workflow_dispatch only (safe)

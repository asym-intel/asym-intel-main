# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 wrap (~14:32 BST)

> **Bootloader:** Say "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md,
and asym-intel-internal/prompt-improvements.md before starting.

--- VERIFY LIVE FIRST ---
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Must show v1.3. If not: workflow_dispatch build.yml + CF purge-all-files.
Screenshot https://asym-intel.info/monitors/democratic-integrity/dashboard.html
→ Must NOT show "Failed to load data."

--- SYNTHESISER FIXES (do first) ---

TASK 1: Fix apostrophe JSON parse error in GMM/WDM/SCEM/AGM synthesiser prompts.
Add this line to each prompt's RULES section:
"Never use apostrophes or contractions in JSON string values.
Use full words only (e.g. 'this weeks' not 'this week's', 'does not' not 'doesn't')."
Files:
- pipeline/synthesisers/gmm/macro-monitor-synthesiser-api-prompt.txt
- pipeline/synthesisers/wdm/democratic-integrity-synthesiser-api-prompt.txt
- pipeline/synthesisers/scem/conflict-escalation-synthesiser-api-prompt.txt
- pipeline/synthesisers/agm/ai-governance-synthesiser-api-prompt.txt
Bump VERSION to v1.1 in each. Log to prompt-improvements.md.

TASK 2: Re-run all 4 after fix (guard cleared after midnight UTC):
Trigger: macro-monitor-synthesiser.yml, democratic-integrity-synthesiser.yml,
conflict-escalation-synthesiser.yml, ai-governance-synthesiser.yml
Stagger 45s apart to avoid 429 rate limit.
Check synthesis-latest.json for FULL_OUTPUT (not _raw_fallback).

TASK 3: Once all 7 synthesisers produce FULL_OUTPUT:
- Enable scheduled triggers: uncomment cron lines in all 7 synthesiser .yml files
- FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC | SCEM: Sat 10:00 UTC
  ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC

TASK 4: Recreate FCW Analyst cron using fcw-slimmed-analyst-cron.md
- Delete cron b17522c3 (current FCW weekly Analyst)
- Create new slim cron using task from fcw-slimmed-analyst-cron.md
- Verify one FCW Analyst run end-to-end
Then roll to GMM, WDM, SCEM, ESA, AGM, ERM using their slimmed cron docs.

--- THEN ---
- PED Sprint 2 (surface Q4/Q6/Q7/Q8 decisions first)
- Housekeeping trim to 5 steps (~800 credits/month saving)
```

## Current synthesiser status
- FCW ✅ validated | ESA ✅ full output | ERM ✅ full output
- GMM ⚠️ apostrophe parse error | WDM ⚠️ apostrophe parse error
- SCEM ⚠️ guard (retry tomorrow) | AGM ⚠️ guard (retry tomorrow)

## Platform state
All 7 synthesisers committed, workflow_dispatch only.
All 7 Analyst crons still running full weekly (pre-synthesiser).
Weekly-research + Reasoner: PAUSED.
Methodology: public at docs/methodology/ (CC BY 4.0).

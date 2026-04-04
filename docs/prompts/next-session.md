# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 final wrap (~19:20 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md,
and asym-intel-internal/prompt-improvements.md before starting.

--- VERIFY LIVE FIRST ---
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Must show v1.3
Screenshot https://asym-intel.info/monitors/democratic-integrity/dashboard.html
→ Must NOT show "Failed to load data."
If either fail: ARCHITECTURE.md deployment runbook + CF purge-all-files (Zone: cc419b7519eba04ef0dc6a7b851930c7)

--- GMM RULE (read before touching anything GMM) ---
GMM methodology and prompts are PRIVATE. They live in asym-intel-internal/gmm-prompts/ only.
Never commit GMM IP to asym-intel-main or any public repo.
GMM synthesiser-api-prompt.txt is in asym-intel-internal/gmm-prompts/ — not in pipeline/synthesisers/gmm/.

--- SYNTHESISER FIXES (do first) ---

TASK 1: Fix apostrophe JSON parse error — add to RULES section of each prompt:
"Never use apostrophes or contractions in JSON string values.
Use full words only (e.g. 'this weeks' not 'this week's', 'does not' not 'doesn't')."
Files (public repo):
  pipeline/synthesisers/wdm/democratic-integrity-synthesiser-api-prompt.txt
  pipeline/synthesisers/scem/conflict-escalation-synthesiser-api-prompt.txt
  pipeline/synthesisers/agm/ai-governance-synthesiser-api-prompt.txt
GMM prompt: asym-intel-internal/gmm-prompts/macro-monitor-synthesiser-api-prompt.txt
Bump VERSION to v1.1 in each. Log to prompt-improvements.md.

TASK 2: Re-run all 4 after fix (guard clears after midnight UTC).
Stagger 45s apart. Verify FULL_OUTPUT (not _raw_fallback) in synthesis-latest.json.

TASK 3: Once all 7 pass → enable scheduled triggers:
  FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC | SCEM: Sat 10:00 UTC
  ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC

TASK 4: Recreate FCW Analyst cron using asym-intel-internal/fcw-slimmed-analyst-cron.md
  Delete cron b17522c3, create slim replacement, verify one end-to-end run.
  Then roll to GMM (asym-intel-internal/gmm-prompts/gmm-slimmed-analyst-cron.md)
  and WDM/SCEM/ESA/AGM/ERM (docs/crons/{abbr}-slimmed-analyst-cron.md).

--- THEN ---
- PED Sprint 2: surface Q4/Q6/Q7/Q8 first
- Analytics: decide Plausible vs Fathom
- GMM commercial repo: discuss structure with Peter before building
```

## Session summary (4 Apr 2026 — full day)

### Architecture
- COLLECTOR-ANALYST-ARCHITECTURE v2.2 locked
- editorial-strategy.md v1.2 — access model, corrections policy, CC BY 4.0
- development-plan.md v1.2 — corrections A–D, open decisions, GMM commercial section
- Methodology published: docs/methodology/ (6 monitors, CC BY 4.0 — GMM excluded)

### Synthesisers
- All 7 committed and tested
- FCW/ESA/ERM ✅ | GMM/WDM ⚠️ apostrophe | SCEM/AGM ⚠️ guard

### Ops
- Housekeeping: 5 steps, 204 lines, ~200 credits/run, runs Monday
- GMM IP ring-fenced to asym-intel-internal/gmm-prompts/
- Staging: clean (0/0)

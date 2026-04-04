# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 wrap (~15:20 BST)

> **Bootloader:** Say "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md before starting.

--- STEP 1: FCW STAGING SIGN-OFF ---
Show Peter the 3 staged FCW pages for visual sign-off:
  https://staging.asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html
  https://staging.asym-intel.info/monitors/fimi-cognitive-warfare/report.html
  https://staging.asym-intel.info/monitors/fimi-cognitive-warfare/overview.html

Changes are schema fallbacks only (d.signal || d.lead_signal etc) — no visual difference
expected. Once Peter approves: open PR staging→main, merge, reset staging to main HEAD.

--- STEP 2: SYNTHESISER RERUNS ---
Trigger these 4 workflows via workflow_dispatch (stagger 45s apart to avoid 429):
  macro-monitor-synthesiser.yml
  democratic-integrity-synthesiser.yml
  conflict-escalation-synthesiser.yml
  ai-governance-synthesiser.yml

Check each synthesis-latest.json:
  - output_type should NOT be null_signal_week
  - _raw_fallback should be absent (or minimal)
  - key top-level keys present (stress_regime / country_heatmap / theatre_tracker / capability_tier_tracker)

--- STEP 3: ENABLE SCHEDULED TRIGGERS ---
Once all 4 produce FULL_OUTPUT (and FCW already validated):
  Uncomment cron lines in all 7 synthesiser .yml files:
  FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC | SCEM: Sat 10:00 UTC
  ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC
  Note: ESA/ERM will still produce null until their Collectors run — that is correct.

--- STEP 4: RECREATE FCW ANALYST CRON ---
- Delete cron b17522c3 (current FCW weekly Analyst)
- Create new slim cron using task from asym-intel-internal/fcw-slimmed-analyst-cron.md
- Verify one FCW Analyst run end-to-end
- Then roll slimmed Analyst cron to GMM, WDM, SCEM, ESA, AGM, ERM using docs/crons/{abbr}-slimmed-analyst-cron.md

--- THEN: PED Sprint 2 ---
Surface Q4/Q6/Q7/Q8 decisions from docs/ux/decisions.md first.
```

## Current synthesiser status
- FCW ✅ FULL_OUTPUT validated
- ESA ✅ null (correct — Collector not yet run this cycle)
- ERM ✅ null (correct — Collector not yet run this cycle)
- GMM ✅ fixes committed — ready for rerun
- WDM ✅ fixes committed — ready for rerun
- SCEM ✅ fixes committed — ready for rerun
- AGM ✅ fixes committed — ready for rerun

## Fixes in place (committed 4 Apr)
- repair_json corrected in GMM/WDM/SCEM/AGM (was producing invalid `\'`; now uses `\u0027`)
- Apostrophe/contraction rule added to all 7 synthesiser API prompts
- FCW HTML schema fallbacks on staging (build ✅)

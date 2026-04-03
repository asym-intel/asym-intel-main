# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap (~03:15 CEST) — PED Session 1 + PVE role creation

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.
> It reads this file at Step 0. You do not need to paste the prompt below.

---

## Prompt (for reference — do not paste manually)

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: PED Sprint 2 ---

First: surface Peter's open decisions (HANDOFF items 2–5).
Do not begin implementation until Peter answers Q4/Q6/Q7/Q8 from decisions.md.

Check PR #31 — if not merged, remind Peter.
  gh api /repos/asym-intel/asym-intel-main/pulls/31 --jq '.state'

Then in order:
1. AGM + ERM dashboard audit (last 2 unreviewed monitors)
   Visit live pages, record findings, append to docs/ux/decisions.md Section 2
   Update docs/ux/colour-registry.md Section 6 (pending items)

2. ESA mobile test — 375px viewport on ESA dashboard
   Check #section-delta font size specifically

3. If Peter answered Q4 (confidence badges): spec the badge class
4. If Peter answered Q8 (SCEM/critical): update colour-registry.md §3

Read docs/ux/decisions.md + docs/ux/colour-registry.md before any UX work.
```

---

## What this session completed (do not re-do)

- ✅ docs/ux/decisions.md — 8 principles + 4-monitor findings + 8 open Qs
- ✅ docs/ux/colour-registry.md — created (severity, accents, 3 collision warnings)
- ✅ Homepage Read→ CTAs removed (live — 48e64d4, 9e9673a)
- ✅ PR #31 staged — FCW contrast + SCEM nav + GMM nav (awaiting Peter sign-off)
- ✅ WDM audited — PASS on contrast + attribution + 60s test
- ✅ ROADMAP — PED Sprint 1 ✅, Sprint 2 queued
- ✅ HANDOFF — updated
- ✅ Platform Visualisation Expert role — docs/prompts/platform-visualisation-expert.md (184a33b)
- ✅ Chart agent conversation safely retired — all knowhow in CHARTS-KNOWHOW.md + WHITESPACE-COLD-START.md
- ✅ INCOMPLETE WORK TRACKER added to notes-for-computer.md
- ✅ INCOMPLETE-002 resolved

## Open — Peter action required

- ⚠️ PR #31 visual sign-off → merge
- ⚠️ Q4: confidence badge visual class (decisions.md)
- ⚠️ Q6: homepage hero image (decisions.md)
- ⚠️ Q7: homepage chatter feed (decisions.md)
- ⚠️ Q8: SCEM accent / --critical collision (decisions.md)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ Cloudflare headers + Zone ID
- ⚠️ GSC property verification

# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap (~03:19 CEST) — final wrap, PR #31 merged

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.
> It reads this file at Step 0. You do not need to paste anything manually.

---

## Prompt (for reference — do not paste manually)

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: PED Sprint 2 ---

First: surface Peter's open decisions before any implementation.
Check decisions.md Section 4 — Q4, Q6, Q7, Q8 need answers:
  Q4: confidence badge visual class (FCW CONFIRMED badge uses severity colour)
  Q6: homepage hero image — in scope this sprint?
  Q7: homepage chatter feed — PED spec or Platform Developer feature?
  Q8: SCEM accent (#dc2626) = --critical — intentional or resolve?

Then in order:
1. AGM + ERM dashboard audit (last 2 unreviewed monitors)
   Visit https://asym-intel.info/monitors/ai-governance/
   Visit https://asym-intel.info/monitors/environmental-risks/
   Record findings using same categories as previous audits
   Append to docs/ux/decisions.md Section 2
   Update docs/ux/colour-registry.md Section 6

2. ESA mobile test — 375px viewport on ESA dashboard
   Check #section-delta font size specifically
   Peter observed small font — unconfirmed at desktop

3. Signal panel contrast fix — GMM + SCEM
   Extend Principle 5 fix (done on FCW) to GMM and SCEM signal panels
   Stage → PR → visual sign-off → merge at wrap

4. Severity badge font size — raise 0.6rem → --text-xs in base.css
   One-line CSS fix, Platform Developer, staging → PR

5. If Peter answered Q4: spec confidence badge class
   If Peter answered Q8: update colour-registry.md §3

Read docs/ux/decisions.md + docs/ux/colour-registry.md before any UX work.
```

---

## What the previous session completed (do not re-do)

- ✅ PR #31 merged — FCW contrast + SCEM nav + GMM nav (79b0b04)
- ✅ Staging reset to main — ahead_by: 0
- ✅ Homepage Read→ CTAs removed (live)
- ✅ docs/ux/decisions.md — 8 principles, 4-monitor findings, 8 open Qs
- ✅ docs/ux/colour-registry.md — created
- ✅ WDM audited — PASS
- ✅ Platform Visualisation Expert role — docs/prompts/platform-visualisation-expert.md
- ✅ Chart agent conversation retired — knowhow in CHARTS-KNOWHOW.md + WHITESPACE-COLD-START.md
- ✅ INCOMPLETE WORK TRACKER added to notes-for-computer.md
- ✅ ROADMAP — PED Sprint 1 ✅, Sprint 2 queued

## Open — Peter action required

- ⚠️ Q4: confidence badge visual class (decisions.md)
- ⚠️ Q6: homepage hero image (decisions.md)
- ⚠️ Q7: homepage chatter feed (decisions.md)
- ⚠️ Q8: SCEM accent / --critical collision (decisions.md)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ Cloudflare headers + Zone ID
- ⚠️ GSC property verification

# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap (~03:00 CEST) — PED Session 1 full

> **Bootloader:** Say "Load asym-intel" or "Computer: asym-intel.info" to the next instance.
> It reads this file at Step 0. You do not need to paste the prompt below.

---

## Prompt (for reference — do not paste manually)

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: PED Sprint 2 ---

Priority order:
1. Peter has decisions to make before implementation — check HANDOFF.md
   items 2–5 (Q4 confidence badges, Q6 hero image, Q7 chatter feed, Q8 SCEM/critical).
   Surface these to Peter at session start. Do not begin implementation until answered.

2. PR #31 — if not yet merged, remind Peter to visually check and merge.
   Check: gh api /repos/asym-intel/asym-intel-main/pulls/31 --jq '.state'

3. AGM + ERM dashboard audit (last 2 unreviewed monitors):
   - Visit https://asym-intel.info/monitors/ai-governance/
   - Visit https://asym-intel.info/monitors/environmental-risks/
   - Record findings using same observation categories as previous audits
   - Append to docs/ux/decisions.md Section 2 (AGM + ERM stubs)
   - Update docs/ux/colour-registry.md Section 6 pending items

4. ESA mobile test — 375px viewport on https://asym-intel.info/monitors/european-strategic-autonomy/
   Look specifically at #section-delta font size. If confirmed small: spec fix for Platform Developer.

5. If Peter answered Q4 (confidence badges): spec the badge class.
   If Peter answered Q8 (SCEM/critical): update colour-registry.md §3.

Read docs/ux/decisions.md before any UX work — it is the PED persistent memory.
Read docs/ux/colour-registry.md before any colour decisions.
```

---

## What this session completed (do not re-do)

- ✅ docs/ux/decisions.md — fully populated (8 principles + 4-monitor findings + 8 open Qs)
- ✅ docs/ux/colour-registry.md — created
- ✅ Homepage Read→ CTAs removed (live, commits 48e64d4 + 9e9673a)
- ✅ PR #31 staged — FCW contrast + SCEM nav + GMM nav (awaiting Peter sign-off)
- ✅ WDM dashboard audited — PASS, findings in decisions.md
- ✅ ROADMAP — PED Sprint 1 complete, Sprint 2 queued
- ✅ HANDOFF — updated
- ✅ notes-for-computer.md — INCOMPLETE WORK TRACKER added

## Open — Peter action required

- ⚠️ PR #31 visual sign-off → merge
- ⚠️ Q4: confidence badge visual class (decisions.md)
- ⚠️ Q6: homepage hero image (decisions.md)
- ⚠️ Q7: homepage chatter feed (decisions.md)
- ⚠️ Q8: SCEM accent / --critical collision (decisions.md)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ Cloudflare headers + Zone ID
- ⚠️ GSC property verification

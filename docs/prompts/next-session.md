# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-07 wrap (~15:35 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session gate check (COMPUTER.md v3.11)
No notification = no session needed. Only open for: pipeline failure, missed publish, Sprint 1 build, or homepage design discussion.

---

## TASK 1 — Validate pipeline runs this week

Check as each fires (some may already have output):
- ESA weekly-research: Tue 18:00 UTC (today — check pipeline/monitors/european-strategic-autonomy/weekly/)
- WDM/FCW/SCEM/ESA/AGM/ERM collectors: Wed 07:00 UTC (first run with search_recency_filter)
- AGM weekly-research: Thu 18:00 UTC (first ever)
- ERM weekly-research: Fri 16:00 UTC (first ever)
- AGM Analyst + Ramparts Step 7: Fri 09:00 UTC (first Ramparts integrated run)

For each: `_meta.status=complete`, `finding_count > 0`, no `null_signal_week=true`

---

## TASK 2 — Pipeline conformance pass

Audit WDM, ESA, AGM, ERM, FCW, SCEM analyst crons + synthesiser prompts against:
- `docs/pipeline/ANALYST-CRON-SPEC.md`
- `docs/pipeline/SYNTHESISER-SPEC.md`

GMM is already conformant. Do ALL 6 in one pass — Platform-First Fix Rule.

---

## TASK 3 — Sprint 1 components — build directly in-session

**Policy:** sonar-pro component generation retired for UI work. Build with Playwright screenshots.
Token system and class names from `docs/generated/sprint1-components-draft.html` are the starting point.

Build order:
1. **Group 1** — base.css token promotion + Confidence Badge (30 min)
2. **Group 2** — Triage Strip, Variant B canonical (45 min)
3. **Group 3** — Monitor Strip + Signal Panel (45 min)
4. **Group 4** — Overview Page Template, Variant B rich (1 hr)

Reference: `docs/ux/colour-registry.md`, `docs/ux/site-rebuild-sprints.md` for sprint IDs.

---

## TASK 4 — Homepage design discussion (before any HP-01/HP-02 implementation)

Peter supplied exploratory mockups and IA note about the space **below the cross-monitor nav**.
Before implementing HP-01/HP-02, run a short design discussion to decide which below-the-nav
elements are ready to be promoted from idea to sprint item.

Key questions:
- Does "Shape of the Week" move to HP-03 (Sprint 1) or stay in Sprint 5?
- Does "Explore by Mode" routing become HP-04?
- Do the left-rail visual tiles (Network/Map/Timeline/Signals/Connections) enter the sprint plan and at which sprint?

Reference material (ideas only — not locked spec):
- `docs/ux/homepage-ia-v4.md` — Peter's IA thinking
- `docs/ux/mockups/homepage-map-prototype-v2-3.html` — layout ideas (hero text too large)
- `docs/ux/mockups/world-map-page-mockup-v2-2.html` — /map/ page concept (Leaflet, filter sidebar)
- `docs/ux/decisions.md` Section 6 — observations from review

Agreed direction unchanged: HP-01 + HP-02 from `site-rebuild-sprints.md` Sprint 1.

---

## What happened this session (7 Apr 2026)
- API Offload Rule revised: sonar-pro component generation retired for HTML/CSS (COMPUTER.md v3.11)
- ROADMAP.md + notes-for-computer.md updated to reflect policy change
- Homepage mockups + IA note filed to `docs/ux/mockups/` and `docs/ux/homepage-ia-v4.md`
- decisions.md Section 6 added (reference/ideas, not locked)
- Staging reset to main HEAD (was behind_by:155, ahead_by:0 → now clean)

## Open — Peter Action Required
- ⚠️ Rotate WP app password + Buttondown API key (were briefly public)
- ⚠️ GSC sitemap: delete and resubmit
- ⚠️ Analytics: Plausible vs Fathom
- ⚠️ Branch protection on main
- ⚠️ Other 6 monitor Overview mockups → asym-intel-internal/visuals/overview-mockups/
- ⚠️ Homepage design discussion (Task 4 above) before HP-01/HP-02 build

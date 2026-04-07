# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-07 final wrap (~15:00 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session gate check (COMPUTER.md v3.9)
No notification = no session needed. Only open for: pipeline failure, missed publish, Sprint 1 review.

---

## TASK 1 — Sprint 1 components — build directly in-session

**Policy change (7 Apr 2026):** sonar-pro component generation is retired for UI work.
Components are built directly in-session with Playwright screenshots for visual confirmation.
See COMPUTER.md API Offload Rule for rationale.

`docs/generated/sprint1-components-draft.html` (sonar-pro output, 7 Apr) is the reference for:
- Token system (:root variables — these are good, use as-is)
- Class naming conventions (triage-strip, badge-confidence, monitor-strip, signal-panel, overview-*)
- Component structure (not the visual output — variants were near-identical)

Build order (one session per group, LOW risk — new additive sections, direct to main):

### Group 1 — base.css token promotion + Confidence Badge (30 min)
1. Promote :root token system from draft into `static/monitors/shared/css/base.css`
2. Add `.badge-confidence` + `.severity-badge` CSS classes to base.css
3. Screenshot one monitor dashboard to confirm no regressions
4. Apply confidence badges wherever `confidence` fields exist in rendered monitor HTML

### Group 2 — Triage Strip (45 min)
1. Write `.triage-strip` CSS directly in base.css — build Variant B (standard 4-zone) as the single canonical variant
2. Screenshot with WDM mock data using Playwright
3. Apply to all 7 dashboards (shared section, data-driven from report-latest.json)
4. Triage strip is LOW risk (new additive section) — direct to main

### Group 3 — Monitor Strip + Signal Panel (45 min)
1. `.monitor-strip` — pill row variant using data-monitor CSS attribute selectors
2. `.signal-panel` — compact variant (left-border accent, --color-surface bg)
3. Apply monitor strip to homepage + all 7 monitor overview pages
4. Apply signal panel to all 7 dashboards

### Group 4 — Overview Page Template (1 hr)
1. Build `.overview-layout` template with right-rail sticky nav — Variant B (rich) as canonical
2. ERM as reference implementation (accent #4caf7d)
3. Apply to all 7 overview pages once ERM is confirmed

Reference: `docs/ux/site-rebuild-sprints.md` for sprint IDs. `docs/ux/colour-registry.md` for accents.

---

## TASK 2 — Pipeline conformance pass

Audit WDM, ESA, AGM, ERM, FCW, SCEM analyst crons + synthesiser prompts against:
- `docs/pipeline/ANALYST-CRON-SPEC.md`
- `docs/pipeline/SYNTHESISER-SPEC.md`

GMM is already conformant. Do ALL 6 in one pass — Platform-First Fix Rule.

---

## TASK 3 — Validate pipeline runs this week

Check as each fires:
- ESA weekly-research: Tue 18:00 UTC (today — may have already fired)
- WDM/FCW/SCEM collectors: Wed 07:00 UTC (first run with search_recency_filter)
- AGM weekly-research: Thu 18:00 UTC (first ever)
- ERM weekly-research: Fri 16:00 UTC (first ever)
- AGM Analyst + Ramparts Step 7: Fri 09:00 UTC (first Ramparts integrated run)

For each: `_meta.status=complete`, `finding_count > 0`, no `null_signal_week=true`

---

## New this session (7 Apr 2026)
- GH_TOKEN: all 14 workflow files fixed
- search_recency_filter: all 14 scripts (collectors=week, weekly-research=month)
- GMM Issue 3 published (Liberation Day tariff shock, CRITICAL -0.664, STAGFLATION)
- GMM synthesiser prompt v1.1: regime/conviction/system_average/lead_signal
- COMPUTER.md v3.9: Platform-First Fix Rule + pipeline specs in Step 0
- docs/pipeline/ANALYST-CRON-SPEC.md + SYNTHESISER-SPEC.md: v1.0
- docs/ux/monitor-overview-brief.md: signed off, repo paths, canonical nav order
- ERM overview mockup: accent corrected to #4caf7d, committed to internal
- section-naming-registry.md: canonical nav tab order added and signed off
- tools/generate-sprint1-batch.py: batched sonar-pro generation script
- Sprint 1 components draft: docs/generated/sprint1-components-draft.html

## Open — Peter Action Required
- ⚠️ Rotate WP app password + Buttondown API key (were briefly public)
- ⚠️ GSC sitemap: delete and resubmit
- ⚠️ Analytics: Plausible vs Fathom
- ⚠️ Branch protection on main
- ⚠️ Other 6 monitor Overview mockups → asym-intel-internal/visuals/overview-mockups/

# Monitor Overview Pages — Computer Implementation Brief (v3)

## Purpose

Build a reusable **Overview page template** for all asym-intel monitors. This page replaces the current thin “about” pages and acts as the monitor’s public front door.

It must:
- orient a first-time reader quickly,
- explain what the monitor tracks and why it matters,
- route readers clearly to Dashboard / Latest Issue / Living Knowledge / Chatter,
- surface the current issue high on the page,
- preserve asym-intel’s calm, serious, methodology-transparent visual language,
- feel visibly connected to the existing monitor pages rather than like a disconnected redesign.

This is **not** a marketing page and **not** a dashboard.

---

## Inputs to attach

Attach these files when implementing:

Read these from the repo at session start:
- `docs/ux/site-rebuild-spec.md` (repo path)
- `docs/ux/site-rebuild-sprints.md` (repo path)
- `docs/ux/section-naming-registry.md` (repo path — signed off, canonical)
- `docs/ux/colour-registry.md` (repo path — authoritative for accent colours)
- `docs/ux/visuals-handover-all-monitors.md` (repo path)
- `docs/ux/homepage-copy.md` (repo path — monitor strip ordering rule)
- relevant `static/monitors/{slug}/data/report-latest.json` for the monitor
- `asym-intel-internal/visuals/overview-mockups/{slug}-overview-mockup-v3.html` as visual reference

**Colour rule:** if the mockup accent colour differs from `colour-registry.md`, implement the registry value. Mockups are visual placement references only.

---

## Key design direction

The new Overview pages should **not** look like generic neutral landing pages.

They should instead be a **bridge** between:
- the current monitor Overview/About pages, which often have useful colour presence and immediate utility,
- and the richer new Overview architecture we have now defined.

The target feel is:
- recognisably asym-intel,
- monitor-specific,
- slightly more alive than the earlier ultra-neutral mockups,
- still restrained, serious, and analytic.

---

## Navigation hierarchy

The Overview page must sit inside the **existing site shell**. Do **not** create a separate standalone top navigation for it.

### Final hierarchy

1. **Site-wide top nav**
   - Shared across asym-intel.info.
   - Same as the rest of the site.

2. **Multi-monitor strip**
   - Shared cross-monitor strip below the site-wide top nav.
   - Uses the ordering and monitor accent rules already agreed.

3. **Monitor header / identity block**
   - Monitor title, strapline, and high-level identity.

4. **Monitor-local nav tabs**
   - Canonical order:
     - Overview
     - Dashboard
     - Latest Issue
     - Living Knowledge
     - Chatter
     - Methodology
     - Archive / Search (where applicable)

### Canonical monitor nav tab order

```
Overview  |  Dashboard  |  Latest Issue  |  Living Knowledge  |  Chatter  |  Methodology  |  Archive / Search
```

This is the authoritative order. Signed off 7 April 2026.
Do not infer tab order from existing monitor HTML — implement this order exactly.
Archive / Search only shown where the monitor has those pages.

### Monitor strip ordering

On all Overview pages, the cross-monitor strip uses the canonical order:
**GMM · SCEM · FCW · AGM · WDM · ESA · ERM**
(triage urgency + expected user interest, not alphabetical — see `docs/ux/homepage-copy.md`)

### Important rule

The nav shown in the mockups is a **monitor-local placeholder row only**. It is **not** a replacement for the global site shell.

---

## Routing rules

Use these rules consistently across the site:

- **Homepage monitor strip links** → go to the monitor **Overview** page.
- **Homepage monitor cards** → usually go to the monitor **Overview** page unless the card is explicitly a report/article card.
- **Homepage featured article / report cards** → go to the specific article or latest issue.
- **Cross-monitor flags** → deep-link to the most relevant destination (Dashboard, Latest Issue, or Living Knowledge) rather than always the Overview.
- **Monitor-local nav** must allow movement between Overview, Dashboard, Latest Issue, Living Knowledge, Chatter, and Methodology from every monitor page.

Overview is the **default front door** for each monitor, not Dashboard.

---

## Canonical page structure

Every monitor Overview page should include these sections in this order:

### 1. Hero / orientation
Include:
- monitor name,
- one-sentence mission statement,
- one “why it matters now” block,
- 2–3 small factual metadata badges,
- 2–3 small stat boxes.

### 2. Latest Issue
This must appear high on the page.

Include:
- current issue title,
- short issue summary,
- 2–3 small issue pills or counters where available,
- route buttons to Dashboard and full report.

### 3. How to use this monitor
Four route cards:
- Dashboard
- Latest Issue
- Living Knowledge
- Chatter

### 4. What this monitor tracks
Use 4 cards describing the monitor’s tracked systems, entities, or domains.

### 5. This week at a glance
A compact row of 3–4 boxes populated from current monitor data where possible.

### 6. Why this monitor is different
Short explanatory section on the monitor’s analytical distinctiveness.

### 7. Cross-monitor connections
Short section showing the strongest adjacent monitor relationships.

---

## Right rail / sidebar

The new Overview pages should preserve some of the usefulness of the current monitor pages by keeping a **right rail** or equivalent secondary column where appropriate.

This rail should contain:
- a small section list / in-page wayfinding,
- one compact monitor summary block,
- direct buttons to Dashboard, Latest Issue, and Living Knowledge,
- optionally Subscribe.

This is important because the current monitor pages already have a practical, utility-first feel that should not be lost.

---

## Colour and visual rules

### Core principle
Use **more visible monitor colour than the earlier v2 mockups**, but still with discipline.

### Good uses of monitor accent colour
- eyebrow label,
- monitor identity dot / chip,
- active nav state,
- hero band tint,
- left rule on key cards,
- issue pills,
- CTA buttons,
- right-rail active section state,
- small stat borders or highlights.

### Avoid
- full-page saturation,
- broad glossy colour blocks,
- trading-app or startup-product aesthetics,
- gradients that overpower the content,
- colour being the only carrier of meaning.

### Visual target
The page should feel:
- lighter and more alive than the ultra-neutral v2 set,
- closer to the current WDM page in spirit,
- but richer, better structured, and more useful.

### Colour implementation note
`colour-registry.md` is the authoritative source for monitor accent assignment and token values. Use the v3 Overview mockups as references for **placement and intensity pattern** only — eyebrow, active nav state, hero band tint, left rule on key cards, pills, CTA buttons, and right-rail active states — not as authority for replacing registry colours. If any legacy CSS, older template, or mockup differs from `colour-registry.md`, implementation must normalise to the registry.

---

## Data population rules

Use real monitor data where available. Fall back to static copy only if data is absent.

### Preferred sources
- `report-latest.json`
- monitor metadata / front matter
- current issue title / lead signal / weekly brief / cross-monitor flags
- methodology page or about copy

### Populate dynamically where possible
- hero badges,
- current issue title and summary,
- issue pills/counters,
- “This week at a glance”,
- cross-monitor links,
- route URLs.

### If data is missing
- render a graceful empty state,
- do not invent precision,
- use neutral fallback copy.

---

## Monitor-specific adaptation rules

Use one shared template across all monitors, but adapt copy and emphasis by monitor type.

### WDM
Emphasise institutional erosion, electoral integrity, democratic resilience, state capture.

### FCW
Emphasise campaigns, attribution complexity, platforms, narrative spread.

### SCEM
Emphasise theatres, escalation path, friction indicators, spillover risk.

### ESA
Emphasise strategic autonomy dimensions, member-state posture, capability and initiative tracking.

### AGM
Emphasise regulatory processes, frontier-model developments, governance competition.

### ERM
Emphasise regional stress, environmental risk transmission, tipping systems, climate-security pressure.

### GMM
Keep the same more colourful v3 direction too, but preserve the public-signals/non-advice boundary.

---

## Hugo / implementation instructions

1. Create a shared Overview page layout or partial set for all monitors.
2. Add Overview as a first-class page in the monitor nav.
3. Reuse the existing site-wide top nav and shared multi-monitor strip; do not fork or replace them for Overview pages.
4. Preserve a monitor-specific right rail or equivalent utility column where the layout supports it.
5. Keep the current issue high on the page.
6. Reuse existing design tokens; do not hardcode one-off colours in templates.
7. Reuse shared card and panel primitives where possible.
8. Make the page mobile-safe from the start.
9. Use `rgba()` for tinted backgrounds, not `color-mix(in srgb, ...)` — `color-mix` is not supported on all target browsers. The equivalent of `color-mix(in srgb, var(--accent) 12%, transparent)` is `--monitor-accent-bg` (already defined in `base.css`).
9. Validate in light and dark mode.

---

## Immediate design references

Use these files as the current visual references for the more-colourful Overview direction:

- `wdm-overview-mockup-v3.html`
- `fcw-overview-mockup-v3.html`
- `scem-overview-mockup-v3.html`
- `esa-overview-mockup-v3.html`
- `agm-overview-mockup-v3.html`
- `erm-overview-mockup-v3.html`
- `gmm-overview-mockup-v2.html` (until a GMM v3 exists)

---

## Success criteria

The page succeeds if:
- a first-time reader understands the monitor in under 30 seconds,
- the current issue is visible immediately,
- the four primary routes are obvious,
- the page feels richer and more useful than the old About page,
- it remains recognisably asym-intel rather than becoming a product-marketing page,
- the navigation hierarchy is consistent with the rest of the site,
- the colour presence feels monitor-specific without becoming visually noisy,
- the template can be reused across all monitors with limited customisation.

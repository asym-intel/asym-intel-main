# docs/ux/decisions.md
## Platform Experience Designer — Accumulated Decisions
**Owner:** Platform Experience Designer
**Created:** April 2026
**Updated:** 2026-04-03 — PED Session 1 (first session knowhow dump)

First-ever PED session: 8 design principles confirmed from live page observation; per-monitor nav/heading audit across 4 monitors; colour system documented; signal panel contrast failure confirmed across FCW (screenshot), GMM, and SCEM; 7 open questions raised for Peter and next session.

---

## Section 1 — Design Principles

**Principle 1: No redundant affordances**
A CTA label placed beside an already-linked title is never acceptable. One element should do one navigational job. The title link is the affordance; a separate "Read →" or "Read briefing →" label adds visual noise without navigational value.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 2: Attribution proximity**
Source attribution belongs inline with the attributed item, not as a separate line element below it. Readers should not need to visually decouple a source from its claim. A block-level "Source →" rendered below item text breaks the cognitive connection between claim and evidence.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 3: Nav labels are promises**
A nav label is a promise about what the reader will see when they click. If the section heading says something different, the promise is broken. Nav labels must match section headings exactly or within one word. Abbreviated labels are acceptable only if unambiguous. "KPI" for "Tail Risk Heatmap" is not acceptable. "Signal" for "Weekly Signal" is acceptable.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 4: Coloured panels require white or near-white text**
When `--monitor-accent` is used as a solid panel background (not a light tint at rgba 8–15%), all text on that panel must be white or near-white (≥#f0f0f0). Accent-derived text colours collapse in contrast when used on a solid accent background. This creates near-collision or WCAG failure at --text-sm body size. No exceptions.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 5: Encoded systems need visible context at point of encounter**
F-flags, MATT scores, severity bands, and confidence levels cannot rely on a reader having studied methodology documentation. Plain-language context must be visible at the point the encoded element appears — not in a separate legend below, not on a methodology page. A tile reading "F2 ACTIVE Sudan" communicates status but not significance. An integrated label reads "F2 (Adjacent escalation risk) ACTIVE — Sudan".
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 6: Minimum readable body size is --text-sm**
`--text-xs` (≈13px) is acceptable for metadata, timestamps, and UI chrome. It is not acceptable for body text that carries analytical meaning. `--text-sm` (≈15px) is the minimum for sustained analytical reading. Severity badges at `0.6rem` (≈9.6px) are below even the system's own `--text-min` floor — this is a CSS inconsistency, not a design choice.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 7: Every visible section has a nav entry**
If a section is prominent enough to appear on the page, it is prominent enough to appear in the right-hand nav. Orphaned sections — sections on the page with no corresponding nav entry — are a navigation failure. They are invisible to keyboard navigation and break the reader's spatial memory of the page.
*Date agreed: 2026-04-03 — PED Session 1*

**Principle 8: Severity and confidence are separate analytical dimensions**
Using severity colours (amber = HIGH severity) for confidence-level badges (CONFIRMED) creates analytical ambiguity. A reader may interpret a confidence label as a severity rating. Severity encodes "how bad is this". Confidence encodes "how certain are we". They must be visually distinct — separate badge classes, not separate values within the same colour system.
*Date agreed: 2026-04-03 — PED Session 1*

---

## Section 2 — Per-Monitor Decisions

### GMM — Global Macro Monitor

**Nav label / section heading mismatches (confirmed — PED Session 1):**
- Nav "KPIs" → No H2 heading — KPI area shows four stat cards with no heading text
- Nav "KPIs" → Also orphans "TAIL RISK HEATMAP" section (sits under the KPIs anchor, no dedicated nav entry)
- Nav "Signal" → Page heading "Weekly Signal"
- Nav "Regime Shift" → Page heading "Regime Shift Probabilities"
- Nav "Delta Strip" → Page heading "Delta Strip — Top Moves This Week"
- Nav "Asset Chart" → Label "Asset Class Scores — Visual"
- Nav "Asset Outlook" → Label "Asset Outlook Summary"
- Nav "Scenarios" → Body text label "Macro Scenarios"
- Nav "Fed Path" → Label "Fed Funds Path — Market vs. Analyst"
- Nav "Real M2" → Label "Real M2 — Deflator Waterfall"
- Nav "Cross-Monitor" → Label "Cross-Monitor Flags"

**Orphaned sections:**
- "TAIL RISK HEATMAP" — no dedicated nav entry; sits under "KPIs" anchor. Substantive section invisible from nav.

**Signal panel contrast status:**
- Confirmed contrast problem: "One number to watch" sub-block renders lighter teal text on solid teal background — noticeably hard to read.
- "Read the top story ↓" CTA: muted teal-on-teal — easily missed.
- Assessment: terminal aesthetic is distinctive but sacrifices scan-ability for dense prose text.

**Known presentation problems:**
- Fed Path section shows "Loading…" — chart render failure or data not yet available at time of review.
- Two simultaneous nav systems: page-level sub-nav (Overview/Dashboard/Latest Issue/Archive) AND right-hand section nav — potential orientation confusion for new readers.
- Section heading conventions inconsistent: some H2, some all-caps eyebrow labels, some table/chart labels.
- Source "→" labels rendered as separate block elements below items, not inline.

---

### FCW — FIMI & Cognitive Warfare Monitor

**Nav label / section heading mismatches (confirmed — PED Session 1):**
- Nav "Top Campaigns" → Heading "Top Campaigns — This Issue"
- Nav "Top Campaigns" → anchor href is `#section-delta` (not `#section-top-campaigns`) — anchor ID mismatch
- Nav "Cross-Monitor" → Heading "Cross-Monitor Flags"

**Orphaned sections:**
- None confirmed. "All Operations" has a nav entry but near-empty content.

**Signal panel contrast status:**
- CONFIRMED WCAG FAILURE — screenshot from Peter confirms this directly.
- Panel background: solid mid-teal (~#2a7fa0 range, FCW accent #38bdf8 family).
- Primary text: near-white — readable.
- Secondary paragraph (MF1 alert text): muted teal-on-teal — contrast estimated below WCAG 2:1 at --text-sm size.
- "Full brief →" link: lighter teal-on-teal — marginal contrast.
- Contrast failure is architectural: signal panel uses monitor accent as background, then renders secondary text in accent-derived colour.

**Known presentation problems:**
- "All Operations" section: contains only "All campaigns shown in featured section above." — minimal content, looks near-empty.
- Nav "Top Campaigns" uses wrong anchor (#section-delta) — clicking may not navigate to expected position.
- "CONFIRMED" badge uses `.severity-badge--high` styling (amber) — confidence level encoded with severity colour. See Section 3 Collision note.
- "F1" badge: 0.6rem (≈9.6px) — below system --text-min floor.

---

### ESA — European Strategic Autonomy Monitor

**Nav label / section heading mismatches (confirmed — PED Session 1):**
- Nav "Autonomy Score" → Heading "Strategic Autonomy Scorecard"
- Nav "Top Items" → Heading "Top Items This Issue"
- Nav "Member States" → Heading "Member State Tracker"
- Nav "Cross-Monitor" → Heading "Cross-Monitor Flags"

**Orphaned sections:**
- None confirmed at time of review.

**Signal panel contrast status:**
- Not directly observed in PED Session 1 — ESA accent is #5b8db0 (slate blue). Assume same pattern risk as FCW/GMM; audit in PED Session 2.

**Known presentation problems:**
- Peter observed small font in #section-delta. Desktop review shows consistent sizing — this may be a mobile-specific rendering issue (see Q5 in Section 4).
- Section delta heading says "Top Items This Issue" (nav says "Top Items") — mismatch confirmed.

---

### SCEM — Conflict Escalation Monitor

**Nav label / section heading mismatches (confirmed — PED Session 1):**
- Nav "F-Flag Matrix" → Heading "Friction Flag Status Board"
- Nav "Escalation Index" → Heading "Global Escalation Index"

**Orphaned sections:**
- "Conflict Overview — All Active Roster" — visible section on page, no nav entry. Nav jumps from "Delta Strip" directly to "Active Conflicts". The section contains a substantive bar-chart roster of all 10 active conflicts with indicator scores and deviation columns.

**Signal panel contrast status:**
- Confirmed contrast problem. SCEM accent is #dc2626 (red). Lead Signal panel: dark red/crimson background, white headline text (readable), lighter pink-tinted secondary text — same pattern as FCW: accent-background panel with accent-derived secondary text colour.

**Known presentation problems:**
- F-flag matrix opaque to non-specialist: F1–F7 tiles with "ACTIVE/CLEAR" status and country name; legend below in small low-weight type. Without reading legend, codes are meaningless. Fails 60-second activist citizen test.
- SCEM uses red/crimson accent — most visually alarming of all 7 monitors. Emotional register is high-urgency even when individual conflicts may be stable (separate from nav/contrast issues — carry to emotional register discussion Q1).
- SCEM accent #dc2626 is identical to --critical severity hex. See Section 3 collision note.

---

### WDM, AGM, ERM

Not yet reviewed in PED — audit pending.

---

## Section 3 — Cross-Monitor Standards

**Severity colour conventions (confirmed — Blueprint v2.1):**
- CRITICAL / Rapid Decay: `--critical` = #c1440e (dark orange-red)
- HIGH / Watchlist: `--high` = #d97706 (amber)
- MODERATE / Stable: `--moderate` = #2563eb (blue)
- POSITIVE / Recovery / Improving: `--positive` = #059669 (green)
- CONTESTED / Uncertain: `--contested` = #6366f1 (indigo)
- Corresponding `--{name}-bg` tints at 8–10% alpha (light mode), 12–15% alpha (dark mode)

**Confidence level vocabulary (confirmed — from methodology):**
Confirmed / High / Assessed / Possible — in descending order of certainty.
Never substitute editorial adjectives (Definite, Likely, Suspected).

**Signal panel rule (NEW — PED Session 1):**
When `--monitor-accent` is used as a solid panel background, all text must be white (≥#f0f0f0) or near-white. Accent-derived text colours MUST NOT be used on accent-coloured panel backgrounds. Acceptable deemphasised secondary text: `rgba(255,255,255,0.75)` minimum. This rule supersedes any per-monitor override.

Confirmed violations: FCW (screenshot), GMM ("One number to watch" sub-block), SCEM (Lead Signal secondary text). WDM, ESA, AGM, ERM: audit in PED Session 2.

**Severity badge font size (FINDING — PED Session 1):**
Current CSS: `.severity-badge { font-size: 0.6rem }` = ≈9.6px at 16px root. This is below the `--text-min` floor (`--text-xs` = clamp(0.8125rem+)) defined in the same stylesheet. The badge font is smaller than the system's own documented minimum — a CSS inconsistency, not a design choice.
Required fix: raise to `--text-xs` minimum.

**Severity vs confidence encoding (COLLISION — unresolved):**
FCW "CONFIRMED" confidence badge uses `.severity-badge--high` (amber/--high) styling. Severity HIGH and confidence CONFIRMED are different analytical dimensions — one encodes "how bad is this finding", the other encodes "how certain are we of this finding". They must not share a colour class.
Resolution required: create separate `.confidence-badge` class with distinct visual treatment. Do not implement without Peter sign-off (see Q4).

**SCEM accent / --critical collision (COLLISION — documented):**
SCEM accent #dc2626 is identical to `--critical` (#c1440e and #dc2626 — NOTE: Blueprint v2.1 uses #c1440e for --critical; SCEM accent #dc2626 is the same red family). In cross-monitor contexts (compound signal indicators, cross-monitor landing page), SCEM identity colour and critical severity indicator may be indistinguishable. Raise with Peter — may be intentional (SCEM is always in the critical register) or may need resolution (see Q8).

**Nav label standard (NEW — PED Session 1):**
Nav labels must match section headings within one word. Abbreviated labels acceptable only if unambiguous. "KPI" for "Tail Risk Heatmap" is not acceptable. "Signal" for "Weekly Signal" is acceptable.

**Empty state standard:**
Not yet established — carry forward to Section 4 (Q2).

**Caption format:**
Not yet established — carry forward to Section 4.

---

## Section 4 — Open Questions

**Q1: Emotional register calibration**
The platform covers democratic backsliding, cognitive warfare, and escalation risk. How alarming should the visual language be? Where is the line between "accurately serious" and "unnecessarily distressing" for the activist citizen audience? SCEM's red/crimson accent is an example of this question made concrete — is the high-urgency register appropriate even when individual conflicts are stable?
*Needs: session with Peter reviewing live pages.*

**Q2: Empty states — broken vs explained**
Several sections show blank renders while data accumulates (WDM map, SCEM baselines, chart history lines with 2 data points). These currently look like bugs.
*Needs: agreed pattern for "data accumulating" vs "no data" vs "rendering error".*

**Q3: Cross-monitor journey design**
When a WDM finding is flagged as relevant to FCW, can a reader follow that connection? Currently: `cross_monitor_flags` exist in data but no navigation pattern surfaces them.
*Needs: decision on whether cross-monitor linking is in scope for this role or Platform Developer sprint.*

**Q4 (NEW): Severity vs confidence visual encoding**
Should CONFIRMED/ASSESSED/POSSIBLE use a separate `.confidence-badge` class with a distinct colour family from the severity system? Raise with Peter before Platform Developer implements.
*Blocks: FCW badge fix, any confidence badge implementation across all monitors.*

**Q5 (NEW): ESA #section-delta font size**
Peter observed small font in ESA #section-delta. Desktop review shows consistent sizing with rest of page. Is this a mobile-specific rendering issue? Needs mobile viewport test before speccing a fix.
*Needs: mobile viewport test (320px, 375px, 768px) of ESA dashboard.*

**Q6 (NEW): Homepage hero image**
Peter referenced whitespace.asym-intel.info as a visual benchmark — uses imagery above the fold. Is a hero image in scope for the homepage this sprint, or a later sprint item? If in scope: PED needs to spec the image type, dimensions, and content guidance before Platform Developer implements.
*Needs: Peter decision on sprint scope.*

**Q7 (NEW): Homepage chatter feed**
Peter suggested surfacing top-5 daily chatters as an OSINT surface on the homepage. Is this a PED spec item (interaction design, information architecture) or a Platform Developer feature request (data pipeline, schema)? If both, what is the sequence?
*Needs: Peter decision on ownership and sprint scope.*

---

## Section 5 — What Has Been Tried

*(No failed approaches yet — first session. This section will be populated as subsequent sessions attempt implementations.)*

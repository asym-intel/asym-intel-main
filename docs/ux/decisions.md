# docs/ux/decisions.md
## Platform Experience Designer — Accumulated Decisions
**Owner:** Platform Experience Designer
**Created:** April 2026
**Updated:** 2026-04-03 — PED Session 1 (first-session knowhow dump + WDM audit)

This is the persistent memory of the Platform Experience Designer role.
It accumulates design principles, per-monitor decisions, cross-monitor standards,
open questions, and lessons from what has been tried and didn't work.

A fresh session reads this file before doing anything else. If this file is absent,
run the first-session knowhow dump (see docs/prompts/platform-experience-designer.md)
before any implementation.

---

## Section 1 — Design Principles

Principles confirmed through direct observation and session work with Peter.
Each entry includes the confirming example(s) so future sessions can recognise new violations.

---

**Principle 1: No redundant affordances**
A CTA label beside or below an already-linked element adds no navigational value and costs
vertical space that should show content. One element should do one navigational job.

*Confirmed by (2026-04-03):*
- Homepage brief cards: "Read →" and "Read briefing →" appeared below hyperlinked titles on
  every card. The title itself was the link. Peter observed the CTA was forcing readers to scroll
  past the excerpt to reach content that would otherwise fit above the fold.
- Screenshot confirmed: secondary grid cards had excerpt text cut mid-sentence because the CTA
  consumed the vertical space.

*Fix applied (2026-04-03):* Removed `tn-lead__cta` and `tn-story__cta` elements from
`layouts/index.html`. Dead CSS cleaned from `assets/css/main.css`. Commits 48e64d4, 9e9673a.

*Watch for:* Any `Read →`, `View →`, `See more →` label that appears adjacent to or below
a linked heading on any page. This includes monitor archive pages, brief index pages, and
any future feed-style layout.

---

**Principle 2: Attribution proximity**
Source attribution must be visually and spatially integrated with the item it supports.
A "Source →" link rendered as a separate block element below the item body creates
a visual gap between claim and evidence — readers have to mentally re-associate them.

*Confirmed by (2026-04-03):*
- `.intel-item__source` CSS: `display: inline-block; margin-top: var(--space-3)` — structurally
  a separate block, not inline within body text.
- Observed on GMM (Cross-Monitor Flags), FCW (campaign items), ESA (Top Items section):
  "Source →" appears on its own line after the body paragraph.
- Peter's observation: "Source → labels should be inline hyperlinks on the item itself."

*Status:* Unimplemented — CSS structural change required. Raise with Platform Developer
before implementing; inline vs block has implications for multi-source items.

*Watch for:* Any element using `.intel-item__source`, `.source-link`, or equivalent that
appears as a block-level element below item text rather than inline within it.

---

**Principle 3: Nav labels are promises**
A right-hand section nav label is a promise about what the reader will find when they click.
If the visible section heading says something different, the promise is broken.
Nav labels must match section headings — exact text, or a clearly unambiguous abbreviation.
Truncation is acceptable ("Regime Shift" for "Regime Shift Probabilities").
Substitution is not ("KPI" for "Tail Risk Heatmap").

*Confirmed by (2026-04-03) — systemic across all 4 monitors reviewed:*

GMM (11 mismatches observed):
- "KPIs" → section has no heading; TAIL RISK HEATMAP sits under this anchor with no own entry
- "Signal" → heading reads "Weekly Signal"
- "Regime Shift" → heading reads "Regime Shift Probabilities"
- "Delta Strip" → heading reads "Delta Strip — Top Moves This Week"
- "Asset Chart" → label reads "Asset Class Scores — Visual"
- "Scenarios" → heading reads "Macro Scenarios"
- "Fed Path" → label reads "Fed Funds Path — Market vs. Analyst"
- "Cross-Monitor" → label reads "Cross-Monitor Flags"

FCW:
- "Top Campaigns" → heading reads "Top Campaigns — This Issue"
- "Top Campaigns" anchor href points to #section-delta (wrong anchor ID)
- "Cross-Monitor" → heading reads "Cross-Monitor Flags"

ESA (4 mismatches):
- "Autonomy Score" → heading reads "Strategic Autonomy Scorecard"
- "Top Items" → heading reads "Top Items This Issue"
- "Member States" → heading reads "Member State Tracker"
- "Cross-Monitor" → heading reads "Cross-Monitor Flags"

SCEM:
- "F-Flag Matrix" → heading reads "Friction Flag Status Board"
- "Escalation Index" → heading reads "Global Escalation Index"

*Status:* Unimplemented — Platform Developer audit pass required across all 7 monitors.
Decision needed: should nav labels be updated to match headings, or headings updated to match
nav labels? In most cases nav labels are the abbreviation — update headings to use the
same abbreviated form where the section heading is not a reader-facing title but a label.

*Watch for:* Any nav entry whose label text cannot be recognised as the section heading by
a first-time reader. Test: can someone click the nav label and immediately confirm they
arrived at the right section?

---

**Principle 4: Every visible section has a nav entry**
If a section is prominent enough to be on the page, it is prominent enough to be in the
right-hand section nav. Orphaned sections are invisible to readers using the nav for
orientation — they either scroll past them without reading, or cannot return to them.

*Confirmed by (2026-04-03):*
- SCEM: "Conflict Overview — All Active Roster" — a full bar-chart roster of all 10 active
  conflicts with indicator scores — has no nav entry. Nav jumps from "Delta Strip" directly
  to "Active Conflicts". Peter's exact observation.
- GMM: "TAIL RISK HEATMAP" section (all-caps eyebrow label, visually prominent, full-width
  heatmap grid) sits under the "KPIs" anchor with no own nav entry.
- FCW: "All Operations" has a nav entry but renders "All campaigns shown in featured section
  above." — near-empty, which is the inverse problem (nav entry for a near-empty section).

*Status:* Unimplemented. Add nav entries to SCEM (Conflict Overview) and GMM (Tail Risk).
Review FCW "All Operations" — if it persistently has no independent content, remove nav entry.

*Watch for:* Any section with a visible heading, chart, or table that does not have a
corresponding entry in the right-hand section nav. Run this check when new sections are
added to any monitor.

---

**Principle 5: Coloured panels require white text**
When `--monitor-accent` is used as a solid panel background (not a tint/rgba), all text
on that panel must be white or near-white (≥ rgba(255,255,255,0.75)).
Accent-derived text colours on accent-coloured backgrounds create near-collision contrast.
This is not a border case — it fails WCAG at the text sizes used.

*Confirmed by (2026-04-03):*
- FCW Lead Signal panel (screenshot confirmed by Peter): panel background mid-teal (#38bdf8 family).
  Primary headline text near-white — readable. Secondary paragraph ("MF1 alert: pro-Orbán
  Hungarian Conservative outlet running counter-narrative...") rendered in dark teal on mid-teal
  background. Estimated contrast ratio ≈ 2:1. WCAG minimum for body text is 4.5:1.
  Peter's exact observation: "isn't the text too hard to see given the contrast between the
  panel colour and this text."
- GMM signal block: "One number to watch" sub-block rendered in lighter teal on dark teal.
  Visually strained. "Read the top story ↓" CTA also in muted teal-on-teal.
- SCEM Lead Signal panel: dark red/crimson background (#dc2626). Secondary text in pink-tinted
  tone — reduced contrast against the crimson.

*Root cause:* Signal panel uses `--monitor-accent` as solid background, then applies
accent-derived or muted text colours. The muted tokens (--color-text-muted, --color-text-faint)
are calibrated for the light/dark page background — not for solid accent backgrounds.

*Fix rule:* On any solid accent-background panel:
- All text: `#ffffff` or `rgba(255,255,255,0.9)`
- Deemphasised secondary text: `rgba(255,255,255,0.72)` minimum
- Never: accent-derived colours, muted tokens, or any colour not independently verified
  for contrast against the specific panel background

*Status:* Unimplemented. Affects FCW, GMM, SCEM confirmed. WDM, ESA, AGM, ERM: audit pending.
Platform Developer implementation spec needed — raise in next session.

*Watch for:* Any `.signal-block`, `.lead-signal`, or coloured panel element where text colour
is set to anything other than white-family on a solid-coloured background.

---

**Principle 6: Encoded systems need visible context at point of encounter**
Proprietary codes (F1–F7 flags, MATT score, severity bands, confidence levels) cannot
rely on the reader having read methodology documentation. Plain-language context must be
visible at the exact point the code appears — not in a separate legend below, not in a
methodology page linked from the footer.

*Confirmed by (2026-04-03):*
- SCEM Friction Flag Status Board: 7 tiles labelled F1–F7, each showing CLEAR/ACTIVE and
  a country name. Legend mapping codes to meanings (e.g. "F2: Adjacent escalation / false-flag
  risk") is rendered in small, low-weight type below the matrix.
  Peter's exact observation: "SCEM flag matrix — value unclear to non-specialist reader."
  A reader sees "F2 ACTIVE Sudan" — ACTIVE communicates status but not significance.
  Without reading the legend: what does F2 mean? Is ACTIVE serious?
- GMM MATT score: score visible on dashboard but meaning not explained at point of encounter.
- FCW confidence badges ("CONFIRMED", "F1"): shown without explanation of the confidence
  vocabulary or what CONFIRMED means in the context of attribution.

*The test:* A reader who has never seen the platform before should be able to read a data
element and understand its significance without scrolling, clicking, or leaving the page.
If they cannot, the context is missing.

*Fix pattern:* Integrate the label meaning into the tile/badge itself, not just in a legend
below. For F-flags: tile shows "F2 · False-flag risk" alongside ACTIVE/CLEAR status.
Legend below can remain as reference — it is not sufficient as the only explanation.

*Status:* Unimplemented. PED spec needed before Platform Developer implementation.
Scope: SCEM flag matrix minimum; GMM MATT score; FCW confidence badges.

*Watch for:* Any badge, tile, score, or encoded label where the meaning is defined only
in a legend, tooltip, or external page — not visible at point of encounter.

---

**Principle 7: Minimum readable body size is --text-sm**
`--text-xs` (clamp 0.8125rem → 0.875rem, ≈13–14px) is acceptable for metadata, timestamps,
UI chrome, and non-semantic labels. It is not acceptable for body text that carries
analytical meaning and requires sustained reading.

*Confirmed by (2026-04-03):*
- `.severity-badge { font-size: 0.6rem }` — 9.6px at 16px root. This is below the system's
  own documented `--text-min` floor (which aliases to `--text-xs`). The badge font violates
  the system's own minimum.
- `.signal-block__label`, `.intel-item__source`: both use `--text-xs` (≈13px). These are
  labels and attribution — metadata — so --text-xs may be acceptable here.
- `.signal-block__body`: uses `--text-sm` (≈15px) — correct for body text.
- Peter's observation: "small font sitewide" with ESA #section-delta called out specifically.
  Desktop review showed consistent sizing on ESA — this may be a mobile viewport issue.
  Requires mobile test.

*Fix rule:*
- Body text carrying analytical meaning: `--text-sm` minimum (≈15px)
- Metadata (dates, source labels, UI chrome): `--text-xs` acceptable (≈13px)
- Badges: raise from 0.6rem to `--text-xs` minimum — currently below system floor

*Status:* Badge font size fix unimplemented. ESA mobile font issue unconfirmed — needs test.

*Watch for:* Any `font-size` value set below `--text-xs` in base.css or any monitor.css.
Any body text — paragraph, summary, signal narrative — set to `--text-xs` or below.

---

**Principle 8: Severity and confidence are separate analytical dimensions**
Severity (how bad is this situation?) and confidence (how certain are we of the attribution?)
are fundamentally different analytical claims. Using the same visual encoding (colour, badge
style) for both creates ambiguity — a reader may interpret a confidence label as severity
information, or vice versa.

*Confirmed by (2026-04-03):*
- FCW uses `.severity-badge--high` (amber, `--high` colour token) for confidence badges
  such as "CONFIRMED". This means amber = severity HIGH = confidence CONFIRMED — two different
  meanings, one colour.
- The "CONFIRMED" badge in the FCW Lead Signal panel uses orange/amber styling — the same
  visual weight as a HIGH severity badge. A reader scanning the panel receives mixed signals.

*Status:* Unresolved — requires Peter decision before implementation.
Open question: should confidence badges use a separate class with distinct visual treatment
(e.g. outline/border style vs filled severity badge, or a separate colour family entirely)?

*Watch for:* Any badge, chip, or label that uses a severity colour token to communicate
a confidence level. Check FCW attribution log, any monitor using "Confirmed/Assessed/Possible"
vocabulary.

---

## Section 2 — Per-Monitor Decisions

### GMM (macro-monitor)
**Nav/heading mismatches:** 11 confirmed — see Principle 3 for full list.
**Orphaned sections:** TAIL RISK HEATMAP has no nav entry (sits under KPIs anchor).
**Signal panel:** "One number to watch" sub-block — teal-on-teal contrast failure (Principle 5).
**Heading conventions:** Mixed — some H2, some all-caps eyebrow labels, some chart/table labels.
  This creates an inconsistent visual hierarchy across 12 sections. Standardise in future sprint.
**Fed Path:** Showed "Loading…" during observation — possible chart render failure or data gap.
  Needs investigation.
**Two simultaneous nav systems:** Page-level sub-nav (Overview/Dashboard/Latest Issue/Archive...)
  AND right-hand section nav both visible. Potential orientation confusion for new readers.
**Status:** No PED changes implemented yet. Nav/heading alignment is highest priority.

### FCW (fimi-cognitive-warfare)
**Nav/heading mismatches:** 2 confirmed + 1 anchor ID mismatch (Top Campaigns → #section-delta).
**Signal panel contrast:** CONFIRMED failure — screenshot evidence. Secondary paragraph text
  in dark teal on mid-teal background. (Principle 5)
**Confidence badge collision:** CONFIRMED badge uses severity colour (Principle 8).
**All Operations section:** Nav entry present but section renders near-empty ("All campaigns
  shown in featured section above."). Either populate or remove nav entry.
**Source labels:** Separate block elements, not inline (Principle 2).
**Status:** No PED changes implemented yet beyond Principle 1 fix (CTA removal, homepage only).

### ESA (european-strategic-autonomy)
**Nav/heading mismatches:** 4 confirmed — see Principle 3.
**#section-delta font size:** Peter observed small font. Desktop review showed consistent sizing.
  Mobile viewport test required before any fix is specified.
**Source labels:** "Source →" as separate block elements (Principle 2).
**Status:** No PED changes implemented yet.

### SCEM (conflict-escalation)
**Nav/heading mismatches:** 2 confirmed (F-Flag Matrix, Escalation Index).
**Orphaned section:** "Conflict Overview — All Active Roster" — no nav entry. (Principle 4)
  Peter's exact observation. Contains a full bar-chart roster of 10 active conflicts.
**Flag matrix:** Non-specialist legibility failure confirmed. F-codes opaque without legend;
  legend is present but visually subordinate. (Principle 6)
**Signal panel:** Dark red background + pink-tinted secondary text — reduced contrast. (Principle 5)
**Emotional register:** Red/crimson accent throughout creates high-urgency feel even when
  individual conflicts may be stable. This may be intentional (SCEM = highest-stakes monitor)
  but should be confirmed with Peter.
**Status:** No PED changes implemented yet.

### WDM (democratic-integrity)
**Audited:** PED Session 1 (2026-04-03) — live dashboard review.

**Nav/heading mismatches (minor — 4 found):**
- "Overview" → eyebrow label reads "GLOBAL DEMOCRATIC HEALTH — THIS ISSUE" (loose match; acceptable)
- "Most Severe" → heading reads "Most Severe — Rapid Decay"
- "Severity Ranking" → heading reads "Country Severity Ranking"
- "Cross-Monitor" → heading reads "Cross-Monitor Flags"

**Orphaned sections:** None — all visible sections have nav entries. ✅

**Signal panel contrast:** PASS. White text on dark teal background — no contrast failure.
Secondary "Read the top story ↓" link is muted but readable. No violation of Principle 5. ✅

**Source attribution:** PASS. Sources are inline hyperlinks within body text prose — not
separate "Source →" block elements. WDM is ahead of other monitors on this standard. ✅

**60-second test:** PASS. Lead finding visible above fold in KPI strip. Lead signal panel
(dark teal block) delivers the headline democratic story in one readable paragraph.
Non-specialist can grasp the top finding without scrolling.

**Minor issues:**
- Country cards in "Most Severe" show truncated body text at ~12–13px — tight but acceptable for card format
- "WDM" abbreviation in page eyebrow may not be immediately clear to a first-time reader
- No scroll-spy active state on right-hand nav during scroll (may not be implemented)
- Loading flash on "Most Severe" and hero area before JS hydration — cosmetic, resolves quickly

**Status:** No PED changes required this session. Minor nav label fixes can be batched
with a future pass across all monitors.

### AGM (ai-governance)
Not yet reviewed in PED. Audit pending — PED Session 2.

### ERM (environmental-risks)
Not yet reviewed in PED. Audit pending — PED Session 2.

---

## Section 3 — Cross-Monitor Standards

### Severity colour system (confirmed — Blueprint v2.1)
| Token | Hex | Meaning |
|---|---|---|
| `--critical` / `--rapid-decay` | #c1440e | Critical / Rapid Decay / Highest severity |
| `--high` / `--watchlist` | #d97706 | High / Elevated / Watchlist |
| `--moderate` | #2563eb | Moderate / Stable |
| `--positive` / `--recovery` | #059669 | Positive / Recovery / Improving |
| `--contested` | #6366f1 | Contested / Uncertain |

These tokens carry severity meaning across ALL monitors.
Using them for confidence levels, monitor identity, or any other purpose creates collision.

### Confidence level vocabulary (from methodology)
Confirmed / High / Assessed / Possible — in descending order of certainty.
These exact words only. Never substitute: "Definite", "Likely", "Suspected", "Probable".
Visual encoding: **not yet established** — see Open Questions Q4.

### Signal panel text rule (confirmed — PED Session 1)
When `--monitor-accent` is used as a solid panel background:
- All text must be white or near-white (≥ rgba(255,255,255,0.9))
- Secondary/deemphasised text: rgba(255,255,255,0.72) minimum
- No accent-derived colours. No muted tokens. No exceptions.

### Badge font size floor (confirmed — PED Session 1)
`.severity-badge { font-size: 0.6rem }` violates the system's own `--text-min` floor.
Minimum badge font: `--text-xs` (clamp 0.8125rem → 0.875rem).
Fix queued — Platform Developer.

### Nav completeness standard (confirmed — PED Session 1)
Every visible section (heading + content) must have a right-hand nav entry.
Near-empty sections should either be populated or removed from the nav.
Nav labels must be recognisable as the section heading (see Principle 3).

### Empty state standard
Not yet established. Open question — see Section 4 Q2.

### Caption format
Not yet established. Open question — see Section 4 Q2.

### Source attribution pattern
Current: `.intel-item__source` is `display: inline-block; margin-top: var(--space-3)` — block.
Target: inline within item body text, or immediately adjacent without block separation.
Implementation: CSS + template change required. Not yet specified.

---

## Section 4 — Open Questions

**Q1: Emotional register calibration**
The platform covers democratic backsliding, cognitive warfare, and escalation risk.
How alarming should the visual language be? Where is the line between "accurately serious"
and "unnecessarily distressing" for the activist citizen audience?
SCEM uses red/crimson throughout — is this intentional (always critical-register monitor)
or should calm states be visually represented differently?
*Needs: session with Peter reviewing live pages.*

**Q2: Empty states — broken vs explained**
Several sections show blank renders while data accumulates (WDM map, SCEM baselines, chart
history lines with 2 data points). These currently look like bugs.
*Needs: agreed pattern for "data accumulating" vs "no data" vs "rendering error".*

**Q3: Cross-monitor journey design**
When a WDM finding connects to FCW, can a reader follow that connection?
`cross_monitor_flags` exist in the data schema but no navigation pattern surfaces them
beyond a text list. The compound signal indicator format is specified in the PED prompt
addenda but not implemented.
*Needs: decision on scope — this sprint or Sprint 5 structural work?*

**Q4: Severity vs confidence visual encoding**
FCW "CONFIRMED" badge uses amber (--high severity colour). Two dimensions, one colour.
Should confidence badges use a separate visual class? Options:
  a) Outline/border badge vs filled severity badge (distinguishes by form)
  b) Separate colour family not in the severity system
  c) Icon + label (no colour encoding for confidence)
*Needs: Peter decision before Platform Developer implements anything.*

**Q5: ESA #section-delta font size**
Peter observed small font in ESA dashboard #section-delta. Desktop review showed consistent
sizing across the page. This may be a mobile viewport issue, a zoom-level issue, or specific
to a sub-element within the section (e.g. a table or metadata block).
*Needs: mobile viewport test (375px) on ESA dashboard before any fix is specified.*

**Q6: Homepage hero image**
Peter noted whitespace.asym-intel.info uses visual imagery and suggested considering a
hero image for the homepage. The current homepage is entirely text-based above the fold.
*Needs: Peter decision on scope — this sprint, or later? Static image or dynamic?*

**Q7: Homepage chatter feed**
Peter suggested a consolidated top-5 daily chatters feed on the homepage as an active
OSINT surface. Individual monitors have Chatter/Digest pages (FCW Chatter, AGM Digest)
but nothing is surfaced on the homepage.
*Needs: Peter decision — PED spec item (design) or Platform Developer feature request (data)?
If data: which monitors' chatter feeds would be included?*

**Q8: SCEM accent / --critical collision**
SCEM accent (#dc2626) is identical to `--critical`. In cross-monitor contexts (compound
signal indicator, cross-monitor landing page), a red element could be SCEM monitor identity
or platform-level CRITICAL severity — indistinguishable.
*Needs: Peter decision — intentional (SCEM is always critical-register) or resolve?*

---

## Section 5 — What Has Been Tried

### Homepage CTA removal (2026-04-03) — DONE, working
Removed `tn-lead__cta` ("Read briefing →") and `tn-story__cta` ("Read →") elements from
`layouts/index.html`. Dead CSS removed from `assets/css/main.css`.
Result: titles carry the link; cards recover vertical space for excerpt content.
Commits: 48e64d4 (template), 9e9673a (CSS cleanup).

*(No failed or reverted approaches yet — first session.)*

---

## Section 6 — Homepage ideas reference (7 April 2026)

**Source:** `docs/ux/homepage-ia-v4.md` + mockups in `docs/ux/mockups/`
**Status:** ⚠️ Reference/ideas only — NOT signed-off decisions. Filed for future design discussion.
Peter confirmed these were exploratory ideas for feedback, not implementation direction.
Agreed homepage direction remains HP-01 + HP-02 from `site-rebuild-sprints.md`.

The IA note and mockups contain useful thinking about what might go in the space below the
cross-monitor nav. Key observations worth preserving for future design discussion:

- Hero text at `clamp(3rem,5.2vw,5.8rem)` is too large — compresses above-the-fold space
- Left-rail visual tile concept (Network, Map, Timeline, Signals, Connections) is interesting
- World map page concept uses Leaflet + filter sidebar — same library as WDM dashboard, just larger
- Three-zone layout (left sidebar + main + right rail) aligns with agreed visual spec
- GMM register constraint (no investment/trading language) is pre-existing and remains in force

None of the above overrides or adds to the agreed HP-01/HP-02 Sprint 1 direction.
When the design discussion for the space below the nav happens, read `docs/ux/homepage-ia-v4.md`
and the two mockups in `docs/ux/mockups/` as starting material.

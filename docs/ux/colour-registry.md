# docs/ux/colour-registry.md
## Platform Colour-Meaning Registry
**Owner:** Platform Experience Designer
**Created:** 2026-04-03 — PED Session 1
**Status:** v1.0 — initial registry from CSS audit + live page observation

This is the single source of truth for what every colour means across all 7 monitors.
No colour may carry contradictory analytical meaning across monitors.
A new colour encoding may not be implemented without first checking this registry.

---

## 1. Severity / Regime System (platform-wide)

These colours carry severity/regime meaning across ALL monitors.
Any use of these colours MUST align with the meaning defined here.

| CSS Token | Hex | Meaning | Do NOT use for |
|---|---|---|---|
| --critical | #c1440e | Critical / Rapid Decay / Highest severity | Confidence levels |
| --high | #d97706 | High / Elevated / Watchlist | Confidence levels |
| --moderate | #2563eb | Moderate / Stable | Confidence levels |
| --positive | #059669 | Positive / Recovery / Improving | General success states |
| --contested | #6366f1 | Contested / Uncertain | Severity levels |

**Severity badge class → colour mapping:**
- `.severity-badge--critical`, `.severity-badge--rapid-decay` → --critical
- `.severity-badge--high`, `.severity-badge--watchlist` → --high
- `.severity-badge--moderate` → --moderate
- `.severity-badge--positive`, `.severity-badge--recovery` → --positive
- `.severity-badge--contested` → --contested

---

## 2. Monitor Accent Colours

Each monitor has a unique accent colour for visual identity.
Accent colours carry monitor identity meaning ONLY — they do not carry severity or confidence meaning.

| Monitor | Accent Hex | Usage |
|---|---|---|
| WDM (democratic-integrity) | #61a5d2 | Borders, links, panel tints |
| GMM (macro-monitor) | #22a0aa | Borders, links, panel tints |
| FCW (fimi-cognitive-warfare) | #38bdf8 | Borders, links, panel tints |
| ESA (european-strategic-autonomy) | #5b8db0 | Borders, links, panel tints |
| AGM (ai-governance) | #3a7d5a | Borders, links, panel tints |
| ERM (environmental-risks) | #4caf7d | Borders, links, panel tints |
| SCEM (conflict-escalation) | #dc2626 | Borders, links, panel tints |

**⚠️ COLLISION RISK — AGM (#3a7d5a) and ERM (#4caf7d):**
Both are green-family. In cross-monitor contexts (compound signal indicators, cross-monitor landing page), these may be indistinguishable. Do not render AGM and ERM signals side by side using accent colour alone — add monitor label.

**⚠️ COLLISION RISK — SCEM accent (#dc2626) and --critical severity:**
SCEM uses the same red family as the platform severity "critical" token (#dc2626 vs #c1440e — both dark red). In cross-monitor contexts, a critical-severity finding on SCEM renders nearly identically to SCEM's monitor identity colour. Is the red SCEM identity, or SCEM-critical? Document and raise with Peter (see decisions.md Section 4, Q8).

---

## 3. Confidence Level Encoding

**Vocabulary (confirmed — from methodology):**
Confirmed / High / Assessed / Possible — in descending order of certainty.

**Current implementation (COLLISION — unresolved):**
FCW uses `.severity-badge--high` (amber/--high) for confidence badges (e.g. "CONFIRMED").
This creates a collision: amber = severity HIGH = confidence CONFIRMED. These are different analytical dimensions.

**Required fix (pending Peter approval):**
Create a separate `.confidence-badge` class with distinct visual treatment:
- Uses a different shape or icon from severity badges (to distinguish by form, not just colour)
- Uses a distinct colour family not in the severity system
- Possible treatment: border-only badge (outline style) vs filled severity badge
- DO NOT implement without Peter sign-off on the visual treatment

**Interim rule:** Until resolved, document the collision. Do not extend the amber/severity treatment to additional confidence labels.

---

## 4. Signal Panel Text Rule (CRITICAL)

**Rule:** When `--monitor-accent` is used as a **solid panel background** (not a tint/rgba), ALL text on that panel must be white (≥#f0f0f0) or near-white.

**Never use on a solid accent background:**
- The accent colour itself as a text colour
- A lighter or darker shade of the accent
- The muted text tokens (--color-text-muted, --color-text-faint)

**Observed violations:**
- FCW Lead Signal panel: secondary paragraph in muted teal on teal background (SCREENSHOT CONFIRMED)
- GMM signal block: "One number to watch" sub-block in lighter teal on teal
- SCEM Lead Signal panel: secondary text in pink-tinted tone on dark red background

**Correct pattern:**
- Panel background: solid `--monitor-accent`
- All text: `#ffffff` or `rgba(255,255,255,0.9)` minimum
- Deemphasised secondary text: `rgba(255,255,255,0.75)` minimum (not accent-derived)

---

## 5. Pending Registry Items

The following monitors were not observed in PED Session 1:
- WDM (democratic-integrity) — audit pending
- AGM (ai-governance) — audit pending
- ERM (environmental-risks) — audit pending

These must be audited in PED Session 2 before any cross-monitor colour encoding work begins.

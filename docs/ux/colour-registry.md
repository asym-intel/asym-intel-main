# docs/ux/colour-registry.md
## Platform Colour-Meaning Registry
**Owner:** Platform Experience Designer
**Created:** 2026-04-03 — PED Session 1
**Status:** v1.0 — initial registry from CSS audit + live page observation (4 of 7 monitors)

This is the single source of truth for what every colour means across all 7 monitors.
No colour may carry contradictory analytical meaning across monitors.
A new colour encoding may not be implemented without first checking this registry.

**Coverage:** GMM, FCW, ESA, SCEM observed. WDM, AGM, ERM pending PED Session 2.

---

## 1. Severity / Regime System (platform-wide)

These colours carry severity meaning across ALL monitors.
Any use of these colours MUST align with the meaning defined here.
Using them for any other purpose (confidence levels, monitor identity, status flags)
creates analytical ambiguity.

| CSS Token | Hex | Meaning | Badge classes |
|---|---|---|---|
| `--critical` | #c1440e | Critical / Rapid Decay / Highest severity | `.severity-badge--critical`, `.severity-badge--rapid-decay` |
| `--high` | #d97706 | High / Elevated / Watchlist | `.severity-badge--high`, `.severity-badge--watchlist` |
| `--moderate` | #2563eb | Moderate / Stable | `.severity-badge--moderate` |
| `--positive` | #059669 | Positive / Recovery / Improving | `.severity-badge--positive`, `.severity-badge--recovery` |
| `--contested` | #6366f1 | Contested / Uncertain | `.severity-badge--contested` |

Each token has a `--{name}-bg` counterpart at 8–10% alpha (light mode), 12–15% (dark mode).
Use `--{name}-bg` as background + `--{name}` as text — always paired, never mixed.

---

## 2. Monitor Accent Colours

Each monitor has a unique accent colour for visual identity only.
Accent colours carry monitor identity meaning — NOT severity, NOT confidence, NOT status.

| Monitor | Slug | Accent Hex | Dark mode accent |
|---|---|---|---|
| WDM | democratic-integrity | #61a5d2 | (inherits via --monitor-accent-dark) |
| GMM | macro-monitor | #22a0aa | (inherits) |
| FCW | fimi-cognitive-warfare | #38bdf8 | (inherits) |
| ESA | european-strategic-autonomy | #5b8db0 | (inherits) |
| AGM | ai-governance | #7a39bb | Purple (Kuja) |
| ERM | environmental-risks | #4caf7d | (inherits) |
| SCEM | conflict-escalation | #dc2626 | (inherits) |

### Permitted accent uses
- Borders, link colours, focus rings
- Light tint backgrounds (via `--monitor-accent-bg` at 10–12% alpha)
- Section nav active state
- Monitor identity chips and labels

### Prohibited accent uses
- Solid panel backgrounds unless ALL text on the panel is white/near-white (see §4)
- Encoding severity or confidence information
- Text colour on any accent-coloured background

---

## 3. Collision Warnings

### ⚠️ SCEM accent = --critical
SCEM accent (#dc2626) is identical to the platform `--critical` severity token.
In cross-monitor contexts (compound signal indicator, cross-monitor landing page),
a red element is ambiguous: SCEM monitor identity, or platform-level CRITICAL severity?

**Current status:** Unresolved — pending Peter decision (decisions.md Q8).
**Interim rule:** In cross-monitor layouts, always pair SCEM red with the monitor label
("Strategic Conflict & Escalation") — never rely on colour alone to identify the monitor.
Never use SCEM accent to communicate severity level independently of the monitor label.

### ✅ AGM colour updated: #7a39bb (Purple/Kuja) — green family collision resolved

AGM accent updated from #3a7d5a (green) to #7a39bb (Purple/Kuja) in April 2026 to distinguish
AI Governance from WDM/ERM green family. AGM/ERM collision risk is now resolved.
Both monitors use green-family accents. In side-by-side cross-monitor contexts they may
be visually indistinguishable, especially in peripheral vision or for colour-blind readers.

**Note:** AGM is now purple (#7a39bb). Previous interim rule for AGM/ERM green collision
landing page, compound signal indicator), always pair accent colour with monitor label.
Never rely on the two greens being distinguishable by colour alone.

### ⚠️ Confidence badge / severity badge collision — ACTIVE
FCW uses `.severity-badge--high` (amber, `--high`) for confidence-level labels (e.g. "CONFIRMED").
This means amber simultaneously means severity HIGH and confidence CONFIRMED.

**Current status:** Unresolved — pending Peter decision (decisions.md Q4).
**Interim rule:** Do not extend this pattern to any additional monitors or any new
confidence-level badges until the collision is resolved with a dedicated confidence
badge class.

---

## 4. Signal Panel Text Rule

**Rule:** When `--monitor-accent` is used as a **solid** panel background (not a tint),
all text on that panel must meet these minimums:

| Text role | Minimum value |
|---|---|
| Primary body text | `#ffffff` or `rgba(255,255,255,0.9)` |
| Secondary / deemphasised text | `rgba(255,255,255,0.72)` |
| Links and CTAs on panel | `rgba(255,255,255,0.85)` |

**Never use on a solid accent background:**
- The accent colour itself (near-collision)
- A lighter or darker shade of the accent
- `--color-text-muted` or `--color-text-faint` (calibrated for page background, not accent)

### Confirmed violations (PED Session 1)

| Monitor | Element | Issue | Status |
|---|---|---|---|
| FCW | Lead Signal panel secondary text ("MF1 alert:...") | Dark teal on mid-teal — est. ~2:1 contrast | ❌ Unimplemented |
| GMM | "One number to watch" sub-block | Lighter teal on dark teal | ❌ Unimplemented |
| GMM | "Read the top story ↓" CTA | Muted teal on dark teal | ❌ Unimplemented |
| SCEM | Lead Signal panel secondary text | Pink-tinted on dark red | ❌ Unimplemented |

WDM, ESA, AGM, ERM signal panels: not yet audited.

---

## 5. Confidence Level Encoding

**Vocabulary (confirmed — from methodology):**
Confirmed / High / Assessed / Possible (descending certainty)

**Visual encoding: NOT YET ESTABLISHED**
Current implementation is a collision with the severity system (see §3).
A dedicated confidence badge class must be designed and approved by Peter before
any new confidence-level badges are implemented.

Candidate approaches (for Peter decision):
- Outline/border style badge vs filled severity badge (distinguishes by form, not colour)
- Separate colour token family not in the severity system
- Icon + label (no colour encoding for confidence)

---

## 6. Pending Registry Items

These monitors were not observed in PED Session 1 and may have undocumented colour usage:

| Monitor | Status |
|---|---|
| WDM (democratic-integrity) | Audit pending — PED Session 2 |
| AGM (ai-governance) | Audit pending — PED Session 2 |
| ERM (environmental-risks) | Audit pending — PED Session 2 |

No new colour encoding may be introduced to these monitors without first completing
the audit and updating this registry.

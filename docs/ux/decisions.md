# docs/ux/decisions.md
## Platform Experience Designer — Accumulated Decisions
**Owner:** Platform Experience Designer
**Created:** April 2026
**Updated:** each session — append, never overwrite

This is the persistent memory of the Platform Experience Designer role.
It accumulates design principles, per-monitor decisions, cross-monitor standards,
open questions, and lessons from what has been tried and didn't work.

A fresh session reads this file before doing anything else. If this file is absent,
run the first-session knowhow dump (see docs/prompts/platform-experience-designer.md)
before any implementation.

---

## Section 1 — Design Principles

*(Populated on first session with Peter — none confirmed yet.)*

---

## Section 2 — Per-Monitor Decisions

*(Populated on first session after live page review — none confirmed yet.)*

---

## Section 3 — Cross-Monitor Standards

**Severity colour conventions (inherited from Blueprint v2.1):**
- CRITICAL / Rapid Decay: red family — `#dc2626` / `var(--color-critical)`
- HIGH / Watchlist: amber family
- MEDIUM / Stable: neutral
- LOW / Recovery: green family

**Confidence level vocabulary (from Domain Analyst methodology):**
- Confirmed / High / Assessed / Possible — these exact words, in this order of certainty
- Never substitute editorial adjectives (Definite, Likely, Suspected)

**Empty state standard:**
- Not yet established — first session priority

**Caption format:**
- Not yet established — first session priority

---

## Section 4 — Open Questions

**Q1: Emotional register calibration**
The platform covers democratic backsliding, cognitive warfare, and escalation risk.
How alarming should the visual language be? Where is the line between "accurately
serious" and "unnecessarily distressing" for the activist citizen audience?
*Needs: session with Peter reviewing live pages.*

**Q2: Empty states — broken vs explained**
Several sections show blank renders while data accumulates (WDM map, SCEM baselines,
chart history lines with 2 data points). These currently look like bugs.
*Needs: agreed pattern for "data accumulating" vs "no data" vs "rendering error".*

**Q3: Cross-monitor journey design**
When a WDM finding is flagged as relevant to FCW, can a reader follow that connection?
Currently: cross_monitor_flags exist in data but no navigation pattern surfaces them.
*Needs: decision on whether cross-monitor linking is in scope for this role or Platform Developer sprint.*

---

## Section 5 — What Has Been Tried

*(Populated as sessions accumulate — none yet.)*

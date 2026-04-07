# Homepage Copy — Signed Off
**Status:** ✅ Signed off by Peter — 7 April 2026
**Used in:** HP-02 (homepage value statement + routing cues)

---

## Platform value statement

Asymmetric Intelligence is a public, methodology-transparent intelligence platform that surfaces pre-consensus structural risks and weekly signals across democracy, conflict, information operations, macroeconomy, AI governance, European strategy, and planetary boundaries.

---

## Routing cues

### Triage
See the monitor dashboards for this week's assessed signals, risk levels, and cross-monitor flags.
**Link:** /monitors/ (or individual monitor dashboard pages)

### This week's analysis
Read the latest weekly briefs and reports for in-depth analytical coverage of the most significant events across each domain.
**Link:** latest weekly brief per monitor

### Structural pipelines
Explore the Living Knowledge pages for slower-moving structures, indices, and scenarios that sit behind the weekly data and deltas.
**Link:** /monitors/{slug}/persistent.html per monitor

### Raw signal
Scan the Chatter feeds for pre-synthesis, high-volume signal — clearly labelled and separate from the multi-stage assessed intelligence.
**Link:** /monitors/{slug}/chatter.html per monitor

---

## Implementation notes (for HP-02)

- Value statement appears once, below the network bar, above the monitor strip.
- Routing cues appear as a 4-item row or 2×2 grid below the featured article stripe.
- Each cue: label (bold) + one sentence + link. No icons needed — text is sufficient.
- Tone: declarative, no exclamation marks, no marketing superlatives.
- "Chatter" capitalised when referring to the named page/section; lowercase in prose ("chatter feeds").
- "Living Knowledge" capitalised — it's a named section type.
- "Dashboard" lowercase in prose ("monitor dashboards") per section-naming-registry.md.
---

## Monitor ordering rule

On the homepage monitor strip and any homepage monitor-card surfaces, monitors are ordered
by expected broad user interest and triage urgency — **not alphabetically**.

**Canonical order:** GMM · SCEM · FCW · AGM · WDM · ESA · ERM

This order applies to:
- The monitor strip (`layouts/partials/monitor-strip.html`)
- Report-card grid on homepage
- Any cross-monitor summary surfaces (e.g. platform status panel)
- Small multiples / confidence distribution row

It does **not** apply to per-monitor pages (each monitor stands alone there).

**Rationale:** GMM and SCEM attract the broadest immediate-triage interest;
FCW and AGM are high-frequency; WDM, ESA, ERM are slower-moving structural monitors.
Order may be revisited as audience data accumulates.

**Signed off:** Peter, 7 April 2026

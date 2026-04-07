# Section Naming Registry
## asym-intel.info — Cross-Monitor Naming and Layout Conventions

**Owner:** Platform Experience Designer  
**Created:** 6 April 2026  
**Status:** ✅ Signed off by Peter — 7 April 2026. Active for Sprint 1 implementation.  
**Nav label amendment:** "Top Items This Issue" nav label shortened to "Top Items" across all monitors. FCW exception: "Top Campaigns". Section headings unchanged.  
**Applies to:** All 7 monitors (dashboard.html + persistent.html)

---

## How to Read This Document

Sections are divided into three tiers:

- **Tier 1 — Universal:** Same name, same location, same layout on every monitor. No variation permitted.
- **Tier 2 — Structural equivalent:** Serves the same structural role across monitors but carries a monitor-specific label. Must follow the naming pattern and use the same layout template.
- **Tier 3 — Domain-specific:** Unique to one or two monitors. No standardisation required, but must use the shared card/table template.

---

## Tier 1 — Universal Sections (Identical Name, All Monitors)

These sections must appear with exactly these names everywhere they occur. Nav label must match section heading exactly.

| Canonical Name | Page | Section ID | What it contains | Current violations known |
|---|---|---|---|---|
| **Lead Signal** | Dashboard | `section-signal` | Single top-line finding this issue. Headline + body. Monitor-accent panel. | GMM uses "Weekly Signal"; FCW may differ |
| **Weekly Brief** | Dashboard + Living Knowledge | `section-weekly-brief` | Narrative paragraph(s) synthesising the issue. Rendered from `weekly_brief` field. | Present on both pages — must have same name |
| **Top Items This Issue** | Dashboard | `section-delta` | Ranked list of 5 intelligence items. Severity-badged. Nav label: "Top Items" (short form). FCW nav: "Top Campaigns". | GMM/ERM/SCEM nav currently shows "Delta Strip" — update in Sprint 1 |
| **Cross-Monitor Flags** | Dashboard + Living Knowledge | `section-cross-monitor` / `section-cross` | Platform-wide compound signals touching this monitor. Rendered from `cross_monitor_flags`. | Nav label confirms as "Cross-Monitor" on WDM; mismatches on GMM/FCW confirmed |
| **Chatter** | Nav tab (own page) | n/a (separate page) | Daily rolling pre-synthesis signals. Must carry persistent "pre-synthesis / unverified" label. Nav tab must say "Chatter" — no substitutes. | Some monitors use "Digest" |

---

## Tier 2 — Structural Equivalents (Pattern-Named)

These sections serve the same structural role (ranked entities by risk level, or cumulative trackers) but the domain noun differs per monitor. The **naming pattern** and **layout template** are standardised; the label is monitor-specific.

### Pattern A — "Severity Ranking" (the ranked bar chart of all entities)

Pattern: **`[Entity Type] Severity Ranking`**

| Monitor | Entity type | Canonical section name |
|---|---|---|
| WDM | Country | Country Severity Ranking |
| SCEM | Conflict | Conflict Severity Ranking |
| FCW | Operation | Operation Severity Ranking |
| ESA | Member State | Member State Severity Ranking |
| AGM | Jurisdiction | Jurisdiction Severity Ranking |
| GMM | Asset Class | Asset Class Risk Ranking |
| ERM | Region | Regional Risk Ranking |

Layout template: horizontal bar chart, sorted descending by score, coloured by monitor tier/severity system, entity name + score + trajectory arrow.

### Pattern B — "Tracker" (the heatmap / entity table across tiers)

Pattern: **`[Entity Type] Tracker`**

| Monitor | Entity type | Canonical section name |
|---|---|---|
| WDM | Country | Country Tracker |
| SCEM | Conflict | Conflict Tracker |
| FCW | Operation | Operation Tracker |
| ESA | Member State | Member State Tracker |
| AGM | Jurisdiction | Jurisdiction Tracker |
| GMM | Asset Class | Asset Class Tracker |
| ERM | Region | Regional Risk Tracker |

Layout template: table with Tier header rows (e.g. "Rapid Decay", "Watchlist", "Recovery" on WDM; equivalent tiers on other monitors), entity rows with severity badge, trajectory arrow, confidence badge, lead signal text, source inline.

### Pattern C — "Top [N] Most [Tier]" (the severity cards / spotlight panel)

Pattern: **`Top [N] Most [Tier Label]`** — where Tier Label is the monitor's highest-risk tier name.

| Monitor | Tier label | Section heading | Nav label |
|---|---|---|---|
| WDM | Rapid Decay | Top 5 Most Severe: Rapid Decay | Top Items |
| SCEM | Active Escalation | Top 5 Most Severe: Active Escalation | Top Items |
| FCW | Active Operations | Top 5 Most Active Operations | Top Campaigns |
| ESA | At Risk | Top 5 At Risk: Member States | Top Items |
| AGM | Regulatory Crisis | Top 5 Most Severe: Regulatory Crisis | Top Items |
| GMM | Tail Risk | Top 5 Tail Risk Assets | Top Items |
| ERM | Critical | Top 5 Most Critical Regions | Top Items |

**Nav label rule:** Use "Top Items" in all right-hand nav entries. Exception: FCW uses "Top Campaigns" (domain noun). Section headings are unabbreviated.

Layout template: horizontal scrollable card strip, flag/icon + entity name + score + arrow + 2-line signal text.

### Pattern D — "Monthly Trend" (the 4-week delta table, Living Knowledge)

This section name is already generic enough to be universal:

**Canonical name: `Monthly Trend`** — on all monitors' Living Knowledge pages.

Layout template: table with Entity | 4-Week Delta | Score | Note columns. Delta badge coloured by direction (critical/positive/moderate).

### Pattern E — "Integrity / Structural Flags" (active flags panel, Dashboard)

This section carries monitor-specific domain meaning, but the pattern is consistent:

Pattern: **`[Domain] Flags`**

| Monitor | Domain | Canonical section name |
|---|---|---|
| WDM | Institutional Integrity | Institutional Integrity Flags |
| SCEM | Friction | Friction Flags |
| FCW | Attribution | Attribution Flags |
| ESA | Sovereignty | Sovereignty Flags |
| AGM | Compliance | Compliance Flags |
| GMM | Systemic Risk | Systemic Risk Flags |
| ERM | Threshold | Threshold Flags |

---

## Tier 3 — Domain-Specific Sections (No Standardisation Required)

These sections are unique to specific monitors. No naming standard needed — but they must use the shared `card` layout template and follow source attribution, confidence badge, and severity badge rules from the platform design system.

| Monitor | Section | Why unique |
|---|---|---|
| WDM | Electoral Watch | Democracy-specific; no equivalent in other monitors |
| WDM | Mimicry Chains | Democracy-specific legislative diffusion tracking |
| WDM | Autocratic Export | Democracy-specific |
| WDM | Digital & Civil Space | Democracy-specific |
| SCEM | F-Flag Matrix | Conflict friction flags; SCEM-specific |
| SCEM | Escalation Scenarios | Conflict-specific |
| FCW | Operation Chains | Information operation attribution; FCW-specific |
| FCW | Attribution Log | FCW-specific |
| GMM | Fed Funds Path | Macro-specific |
| GMM | Macro Scenarios | Macro-specific |
| GMM | Regime Shift Probabilities | GMM-specific |
| AGM | Frontier Model Watch | AGM-specific |
| ERM | Tipping Points | ERM-specific |

---

## Layout Templates — Shared Across All Tiers

Regardless of tier, every section uses one of these four layout primitives. The same CSS classes apply across all monitors.

### Template 1 — Card
Used for: individual findings, flags, friction notes, domain-specific entries.

```
.card
  .card-label     ← flag + entity name + status badge
  .card-title     ← headline
  .card-body      ← summary / analytical text (--text-sm minimum)
  .card-footer    ← lead time / first seen / source (inline, not block)
```

### Template 2 — Table Row
Used for: trackers, rankings, legislative watch, monthly trend.

```
tr.heatmap-row--[severity]
  td  ← flag + entity name
  td  ← severity badge + score
  td  ← trajectory arrow
  td  ← key development + confidence badge + source inline
```

### Template 3 — Delta Item
Used for: Top Items This Issue (delta strip).

```
li.delta-item
  .delta-item__rank
  .delta-item__body
    .delta-item__module    ← entity/country label
    .delta-item__title     ← headline
    .delta-item__one-line  ← summary (≤140 chars)
    severity-badge + tier tag + source inline
```

### Template 4 — Signal Panel
Used for: Lead Signal only.

```
.signal-block
  .signal-block__label     ← "Lead Signal — Issue N"
  p                        ← headline (--text-lg, white)
  p.signal-block__body     ← body text (--text-sm, rgba 255,255,255,0.9)
  .source-link             ← inline, white-family colour
```

---

## Naming Anti-Patterns (Never Use)

These names have been used on some monitors and must be retired:

| Retire | Replace with |
|---|---|
| "Weekly Signal" | "Lead Signal" |
| "Delta Strip" / "Delta Strip — Top Moves This Week" | Section heading: "Top Items This Issue" · Nav label: "Top Items" |
| "Digest" (for daily chatter page) | "Chatter" |
| "KPIs" (as a section heading) | No standalone heading — KPI strip has no visible heading; sidebar nav entry reads "Overview" |
| "Tail Risk Heatmap" (GMM nav, no own heading) | Give section its own heading: "Tail Risk Heatmap" and add nav entry |
| Any F1–F7 code without inline plain-language gloss | Always render as: "F2 — False-flag risk" |

---

## Review Checklist (For Each Monitor Review)

For each monitor, check every visible section against this registry:

- [ ] Tier 1 sections present and named exactly as specified
- [ ] Tier 2 sections follow the naming pattern for their monitor
- [ ] Every Dashboard section has a matching right-hand nav entry (Principle 4)
- [ ] Every nav label matches the section heading exactly, or is an unambiguous abbreviation (Principle 3)
- [ ] "Chatter" tab exists in monitor nav and links to the daily signal layer
- [ ] No section uses a retired name from the anti-patterns list
- [ ] Domain-specific sections (Tier 3) use standard card/table/delta layout templates
- [ ] Encoded labels (F-codes, MATT, severity bands) have inline plain-language context (Principle 6)

---

*This document is a companion to `docs/ux/decisions.md`. It defines naming conventions; `decisions.md` defines design principles. Both documents must be read by the Platform Experience Designer at the start of each session.*
---

## Monitor Nav Tab Order (canonical)

**Signed off:** Peter, 7 April 2026

```
Overview  |  Dashboard  |  Latest Issue  |  Living Knowledge  |  Chatter  |  Methodology  |  Archive / Search
```

Rules:
- This order applies to ALL 7 monitors — do not infer from existing HTML
- Archive / Search shown only where the monitor has those pages
- Overview is the default front door (homepage monitor strip links → Overview)
- No additional tabs may be added without updating this registry

**Do not use:**
- Putting Dashboard first (old pattern)
- Using "About" instead of "Overview"
- Splitting Archive and Search into separate tabs without a design decision


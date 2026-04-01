# SCEM Domain Audit
**Prepared:** 2026-04-01 | **Auditor:** Domain Expert (original SCEM architect)  
**Issue audited:** Issue 1 · Vol 1 · W/E 30 March 2026  
**Pages audited:** dashboard.html, report.html, persistent.html  
**JSON schema version (task spec):** Schema 2.0 (report) / Schema 1.0 (persistent)  
**Note:** JSON files are not publicly accessible; this audit is based on the schema specification provided in the task prompt and the rendered output of all three live pages.

---

## Part 1: Collected But Not Surfaced

The table below maps every top-level JSON field and per-conflict sub-field against what is rendered on each page. "✓ Full" = all sub-fields exposed; "✓ Partial" = some sub-fields exposed; "✗ Absent" = field exists in schema but zero rendering; "— N/A" = field not applicable to that page by design.

### 1.1 Top-Level / Meta Fields

| Field | In JSON Schema | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `meta.week_ending` | ✓ | ✓ Full (header KPI) | ✓ Full (header) | ✓ Full (last updated) |
| `meta.issue_number` | ✓ | ✓ Full | ✓ Full | — N/A |
| `meta.schema_version` | ✓ | ✗ Absent | ✓ Partial (Schema 2.0 in header) | ✓ Partial (Schema 1.0 in header — **version mismatch**) |
| `meta.baseline_status` | ✓ | ✓ Full (banner) | ✓ Full (header note) | ✓ Full (per-conflict) |
| `meta.active_conflict_count` | ✓ | ✓ Full (KPI tile) | ✗ Absent | ✗ Absent |

### 1.2 Lead Signal Fields

| Field | In JSON Schema | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `lead_signal.conflict` | ✓ | ✓ Full (KPI tile label) | ✓ Full (section heading) | ✗ Absent |
| `lead_signal.headline` | ✓ | ✓ Full (lead signal block) | ✓ Full (bold block) | ✗ Absent |
| `lead_signal.indicator` | ✓ | ✓ Partial (in summary text) | ✓ Full (Indicator line) | ✗ Absent |
| `lead_signal.deviation` | ✓ | ✓ Partial (in summary text) | ✓ Full (Deviation line) | ✗ Absent |
| `lead_signal.summary` | ✓ | ✓ Full | ✓ Full | ✗ Absent |
| `lead_signal.source_url` | ✓ | ✗ Absent | ✓ Full ("Primary source →" link) | ✗ Absent |

**Gap:** `lead_signal.source_url` is not surfaced on the dashboard. The dashboard lead signal block carries no citation link, meaning analysts viewing only the dashboard cannot click through to the primary source without opening the report.

### 1.3 Conflict Roster — Per-Conflict Fields

| Field | In JSON Schema | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `conflict` (name) | ✓ | ✓ Full | ✓ Full | ✓ Full |
| `theatre` | ✓ | ✓ Full (card + roster table) | ✓ Full (sub-header) | ✓ Full |
| `trajectory` | ✓ | ✓ Full (card + roster table) | ✓ Full (badge) | ✗ Absent |
| `trajectory_arrow` | ✓ | ✓ Full (↑/→ arrow) | ✓ Full | ✗ Absent |
| `week_number` | ✓ | ✗ Absent | ✗ Absent | ✓ Full (Week N of 13) |
| `baseline_status` | ✓ | ✓ Partial (CONTESTED badge in roster table) | ✓ Full (CONTESTED badge) | ✓ Full (CONTESTED — WEEK N/13) |
| `indicators.I1–I6.level` | ✓ | ✓ Partial (bar chart in Indicator Breakdown) | ✓ Full (table: Level) | ✓ Full (current value tiles) |
| `indicators.I1–I6.baseline` | ✓ | ✗ Absent (bar chart shows level, not baseline) | ✓ Full (table: Baseline) | ✓ Partial (MEDIAN shown as "—" until lock; not the initial baseline value) |
| `indicators.I1–I6.deviation` | ✓ | ✓ Partial (Delta Strip: highest deviation only; Indicator Breakdown: not delta-visualized) | ✓ Full (table: Deviation) | ✗ Absent (current vs. median only) |
| `indicators.I1–I6.band` | ✓ | ✓ Partial (Delta Strip top-5 only; Conflict Roster table: "Highest Band" — but no per-indicator band shown on dashboard) | ✓ Full (table: Band column = CONTESTED) | ✗ Absent |
| `indicators.I1–I6.confidence` | ✓ | ✗ Absent | ✓ Full (Confidence column) | ✗ Absent |
| `indicators.I1–I6.note` | ✓ | ✗ Absent | ✓ Full (Note column) | ✗ Absent |
| `f_flags[]` (flag type) | ✓ | ✓ Full (F-Flag Status Board — aggregate tiles) | ✓ Partial (flags referenced inline in notes only; no dedicated F-flag table per conflict) | ✓ Full (F-Flag Matrix table) |
| `f_flags[]` (detail/rationale) | ✓ | ✗ Absent (dashboard F-flag tiles show flag type + first conflict only; no detail) | ✓ Partial (detail embedded in indicator notes, not structured) | ✓ Full (Detail column) |
| `f_flags[]` (applied date) | ✓ | ✗ Absent | ✗ Absent | ✓ Full |
| `f_flags[]` (status) | ✓ | ✗ Absent | ✗ Absent | ✓ Full (Active/Resolved) |
| `lead_development` | ✓ | ✗ Absent | ✓ Full (bold "Lead Development:" line) | ✗ Absent |
| `summary` (conflict-level) | ✓ | ✗ Absent | ✓ Full (narrative paragraph below indicator table) | ✓ Partial (one-sentence summary only) |
| `source_url` (conflict-level) | ✓ | ✗ Absent | ✗ Absent (sources embedded in notes, not structured) | ✗ Absent |

**Critical gap — `source_url` at conflict level:** Neither the dashboard nor the report renders a structured citation for the conflict's primary source. The report embeds source references inside free-text notes and indicator cells (e.g., "Reuters 26 Jan", "Bloomberg, 31 March") but there is no clickable, structured `source_url` field surfaced at the conflict card level on any page. This is an editorial integrity risk: the data has source provenance in the JSON but it cannot be audited by users.

### 1.4 Roster Watch Fields

| Field | In JSON Schema | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `roster_watch.approaching_inclusion[]` | ✓ | ✗ Absent | ✓ Partial (Ethiopia entry visible in nav, but content not rendered in main body — section appears empty/stub) | ✓ Partial (Ethiopia Northern Theatre listed with criteria met note) |
| `roster_watch.approaching_retirement[]` | ✓ | ✗ Absent | ✗ Absent | ✗ Absent |
| Inclusion criteria threshold text | ✓ | ✗ Absent | ✗ Absent | ✓ Partial (criteria met: "Partial I2") |

**Gap:** `roster_watch.approaching_retirement` has no rendering anywhere. This is analytically significant: users have no visibility into which conflicts are on track for retirement from the roster. The report has a "Roster Watch" section in its navigation but the body content for this section is absent — it renders as blank. This is a **rendering bug**, not a schema gap.

### 1.5 Cross-Monitor Flags

| Field | In JSON Schema | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `cross_monitor_flags[]` | ✓ | ✗ Absent | ✓ Partial (Cross-Monitor section exists in nav but body content absent — same rendering bug) | ✓ Partial (Cross-Monitor section in nav but no content visible in fetched text) |

**Rendering bug:** Both the Report's "Roster Watch" and "Cross-Monitor" sections appear as named navigation entries with no body content. These sections are in the JSON schema and are listed in the sidebar but do not render substantive content on report.html.

### 1.6 Planned / Upcoming Fields (Not Yet in JSON)

| Field | Expected in JSON | Rendered | Notes |
|---|---|---|---|
| `conflict_context` (humanitarian/territorial) | Expected from Sun 5 Apr 2026 | ✗ Absent | Cron prompt updated; no rendering scaffolding yet visible on any page |

### 1.7 Global Escalation Index — Derivation Transparency

| Element | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| Derived formula (RED-band count, AMBER-band count) | Implied from roster bands | ✓ Partial (formula text: "X at RED-band, Y at AMBER-band across Z conflicts") | ✗ Absent | ✗ Absent |
| Per-conflict band contribution | Not structured as field | ✗ Absent | ✗ Absent | ✗ Absent |

**Gap:** The Global Escalation Index on the dashboard currently reads LOW with 0 RED and 0 AMBER conflicts — yet the report text repeatedly states "RED-band threshold MET if baseline locked" for C9 and C10. This contradicts the dashboard display. The issue is that `baseline_status = CONTESTED` suppresses band elevation, but the dashboard does not explain this logic to users. A contested-baseline qualifier on the index display is needed.

---

## Part 2: Recommended Improvements

### Schema/Data Additions (ranked)

**Rank 1 — Escalation Velocity Field** (`escalation_velocity`)  
*Currently missing.* The schema captures indicator deviation at a point in time but has no structured measure of how fast a conflict is moving. A conflict with three indicators at +1 that were all at 0 last week is categorically different from one that has been at +1 for 10 weeks. Without velocity, the monitor cannot distinguish a new breakout from a chronic plateau. Recommended addition:

```json
"escalation_velocity": {
  "direction": "accelerating" | "steady" | "decelerating",
  "week_over_week_delta": +2,   // sum of indicator deviation changes vs. prior week
  "consecutive_escalating_weeks": 3
}
```

This is the single highest-value schema addition: it enables early warning before band thresholds are crossed and directly addresses the monitor's core purpose — detecting escalation signals before mainstream coverage.

**Rank 2 — Composite Escalation Score** (`esc_score`)  
*Currently missing.* Individual I1–I6 deviations are tracked but no aggregate per-conflict score exists. A simple weighted sum (I3 and I2 weighted higher for interstate conflicts; I6 weighted higher for humanitarian conflicts) would allow conflict ranking by escalation severity rather than just by a single highest indicator. This would improve Delta Strip logic, which currently ranks by max single-indicator deviation — a metric easily distorted by one outlier.

```json
"esc_score": {
  "raw": 7,
  "weighted": 6.2,
  "methodology_note": "I3×2, I2×1.5, I1/I4/I5/I6×1.0 — contested baselines use level not deviation"
}
```

**Rank 3 — Ceasefire / Negotiation Status Field** (`negotiation_status`)  
*Currently missing.* The Russia-Ukraine ceasefire/autonomy tracking was moved to ESA (Autonomy Score), but no structured negotiation status exists for other conflicts. This is a major analytical gap: for Gaza, DRC, Sudan, and US-Iran, the ceasefire/negotiation state is the primary variable determining whether the current deviation trajectory continues or reverses. F4 flags partially address this for de-escalation signals, but F-flags are anomaly markers, not status fields. Recommended:

```json
"negotiation_status": {
  "status": "none" | "backchannel" | "formal_talks" | "ceasefire_holding" | "ceasefire_violated",
  "mechanism": "Pakistan quartet intermediary",
  "confidence": "Possible" | "Probable" | "Confirmed",
  "last_updated": "2026-03-31",
  "note": "Iran FM denied negotiations 31 March despite 29 March signals"
}
```

**Rank 4 — External Actor Involvement Field** (`external_actors`)  
*Currently missing.* Several conflicts are materially shaped by third-party actors whose involvement is analytically critical but not structured: Iranian jet fuel to Myanmar, Russia/China sanctions circumvention for DPRK, US troop deployment for C10, Quad mediation non-functionality in Sudan. External actor involvement is currently captured only in free-text notes. Structuring it would enable cross-conflict pattern analysis (e.g., Iran as a conflict-enabler across multiple theatres simultaneously).

```json
"external_actors": [
  {"actor": "Iran", "role": "material_support", "indicator_affected": "I2", "confidence": "Confirmed"},
  {"actor": "Russia", "role": "sanctions_circumvention", "indicator_affected": "I4", "confidence": "Confirmed"}
]
```

**Rank 5 — Territorial Control Change Field** (`territorial_status`)  
*Currently missing; will partially be addressed by upcoming `conflict_context`.* Several active conflicts involve contested or changing territorial control (Gaza IDF 53-58% territory, Israel-Lebanon Litani buffer zone, DRC M23 coltan mines, Sudan RSF Kurmuk), yet this is currently captured only in notes. Structured territorial status would enable I2 escalation assessments to be more rigorous and comparable across conflicts. This should be a sub-field of the incoming `conflict_context` object rather than a standalone top-level field.

**Rank 6 — Source Provenance / Tier Structure at Conflict Level** (`sources[]`)  
*Currently missing as structured field.* Source provenance exists in free-text notes (T1/T2/T3 tier references) but is not machine-readable. A structured `sources[]` array on each conflict would allow: (a) systematic confidence-scoring audit, (b) identification of single-source gaps (F1 triggering), (c) editorial traceability. The existing confidence field (`Confirmed/Probable/Possible`) partially proxies this but the underlying source tier is not queryable.

**Rank 7 — Conflict Phase Field** (`conflict_phase`)  
*Currently missing.* "Escalating" trajectory is a direction, not a phase. Conflicts can be in: latent (Taiwan, Korea), low-intensity, active conventional, active with WMD risk, ceasefire, post-conflict. The phase determines which indicators are most diagnostically relevant and which baselines are appropriate. The current `trajectory` field partially proxies this but conflates direction with phase.

**Rank 8 — Inter-Conflict Linkage Map** (`conflict_linkages[]`)  
*Currently missing.* The US-Iran/Israel-Lebanon/Gaza conflicts are operationally linked (Hormuz closure affects Lebanon's economy; Iran conditioning Lebanon ceasefire on US-Iran deal; Hezbollah I6 linked to Iran air campaign). These linkages are noted in free text but not structured. A linkage map would enable the "ripple escalation" analysis that distinguishes SCEM's analytical value from a simple conflict tracker.

---

### Dashboard Rendering Improvements (ranked)

**Rank 1 — Baseline Deviation Framing on the Bar Chart**  
The recently-added I1–I6 bar chart in "Indicator Breakdown" shows indicator levels (1–5) but **does not show baseline or deviation**. A user looking at Russia-Ukraine I1=5 sees a full bar, which looks maximal — but deviation is 0. A user looking at Sudan I6=5 also sees a full bar, but deviation is +1. The visual is identical for structurally different situations. Fix: add a baseline marker line (or two-tone fill) to each bar so the filled portion above the marker = deviation. Label the marker explicitly "Baseline: 4." This is the most important visual fix because it directly undermines the monitor's core concept if deviation and level look the same.

**Rank 2 — Global Escalation Index — Contested Baseline Disclaimer**  
The index reads "LOW" (0 RED, 0 AMBER) while the report simultaneously states three RED-band thresholds are met for C10 if baselines were locked. This is not explained on the dashboard. Users with only dashboard access will conclude the conflict environment is calm, which is the opposite of the analytical conclusion. Fix: add an inline disclaimer — *"Bands suppressed: baselines CONTESTED until W13. Current levels without baseline: C10 I3 +2, I4 +1, I6 +2."* This is a trust and analytical integrity issue, not merely a cosmetic one.

**Rank 3 — Delta Strip: Show All Conflicting Indicators, Not Just Highest**  
The Delta Strip top-5 shows "Highest indicator deviation: 2 · I6 displacement" for Israel-Lebanon. But C10 (US-Iran) has three indicators at or above the RED-band threshold, which is analytically more significant than a single +2 on one indicator. The strip should display the count of deviating indicators alongside the maximum deviation, e.g., "3 indicators deviating (I3 +2, I4 +1, I6 +2)." The current display understates multi-indicator crises.

**Rank 4 — F-Flag Detail on Dashboard Hover/Expand**  
The dashboard F-Flag Status Board shows F2/F3/F4 as active with the first associated conflict listed. But F4 is active on five separate conflict-indicator pairs, and this is not visible. A user sees "F4 Active / Russia" and misses the F4 flags on Gaza, DRC, Israel-Lebanon, and US-Iran. Fix: make each flag tile expandable or hoverable to show all conflict-indicator instances from the `f_flags[]` array. Alternatively, add a count badge (e.g., "F4 × 5").

**Rank 5 — Source Link on Dashboard Lead Signal**  
`lead_signal.source_url` is in the JSON and is rendered on the report (as "Primary source →") but absent from the dashboard lead signal block. Analysts using the dashboard as their primary view have no path to source verification. Add a source link below the lead signal narrative.

**Rank 6 — Active Conflicts Cards: Show Indicator Deviations Count**  
The Active Conflicts card grid shows conflict name, theatre, trajectory, and CONTESTED badge. It does not show how many indicators are deviating this week. Adding a small indicator — e.g., "4 indicators above baseline" for Sudan — would communicate analytical severity at the card level, before a user drills into Indicator Breakdown.

**Rank 7 — Trajectory Arrow Needs Contextual Anchoring**  
"↑ Escalating" appears on 8 of 10 cards, which creates visual noise without differentiation. "Escalating" from a structural wartime baseline of 5 (Russia-Ukraine, deviation=0) is materially different from "Escalating" with 4 indicators above baseline (Sudan). Consider adding a severity tier to the trajectory label: "↑ Escalating (4 indicators)" or a colour-coded escalation intensity band per card.

**Rank 8 — Persistent Page: Render `approaching_retirement` Section**  
The persistent page renders the Ethiopia approaching_inclusion watch entry but has no `approaching_retirement` section. This is a pure rendering gap — the field exists in the JSON schema. Any conflict nearing retirement criteria (e.g., Gaza/ceasefire holding, Haiti/stability) should have a visible watch note to communicate the analyst's retirement thesis and criteria.

**Rank 9 — Report.html: Fix Roster Watch and Cross-Monitor Section Rendering**  
Both "Roster Watch" and "Cross-Monitor" appear as navigation entries in report.html but render empty content bodies. This is a confirmed rendering bug: these JSON fields (`roster_watch`, `cross_monitor_flags`) are not being injected into the report template. High-priority fix — these sections exist in the persistent page but the report's canonical position for them is empty.

**Rank 10 — Schema Version Consistency**  
The report says "Schema 2.0" while the persistent page says "Schema 1.0". If these are genuinely different schema versions, they need explicit version-specific documentation. If it is a propagation error, it erodes confidence in data integrity. Fix the mismatch and display a unified schema version in the dashboard header.

---

### Methodology Improvements (ranked)

**Rank 1 — The 6-Indicator Framework: Missing I7 — Proxy/Third-Party Warfare**  
I1–I6 covers rhetoric, military posture, nuclear/strategic, economic warfare, diplomatic, and displacement. What is structurally absent is a proxy/third-party warfare indicator (I7). The current Week 1 data repeatedly flags external actor involvement — Iranian jet fuel to Myanmar (I2-adjacent), Iran as a multi-theatre enabler, Russia circumventing DPRK sanctions — but these are absorbed into I2 notes. The US-Iran conflict itself has an I2-adjacent note about Iran attacking US bases across the Gulf while the conflict is classified as a bilateral. Third-party warfare (the IRGC in Syria, Hezbollah in Lebanon, Iran in Myanmar, Russia in Sudan) is now a dominant escalation vector that has no dedicated indicator. Recommend adding I7=proxy_warfare with sub-indicators: (a) state-sponsored external military support, (b) proxy ground forces, (c) mercenary/PMC deployment.

**Rank 2 — Cyber/Information Warfare is Absent from the Framework**  
None of I1–I6 captures offensive cyber operations or information warfare as an escalation signal in structured form. For Russia-Ukraine, PRC-Taiwan, and Korean Peninsula, cyber activity is both an early warning indicator and an escalation mechanism in its own right (e.g., infrastructure attacks preceding kinetic operations). I1=rhetoric partially absorbs information warfare framing but does not capture capability deployment. Recommend either expanding I1 to I1=rhetoric_and_information_warfare with a separate sub-field, or adding I8=cyber_information_warfare. This is particularly relevant for the Taiwan/Korea latent conflicts where cyber is the primary active escalation vector.

**Rank 3 — Baseline Locking at W13 is Methodologically Inconsistent for New Conflicts**  
The W13 baseline locking threshold is appropriate for the original 8 conflicts (which presumably have historical indicator distributions). However, C9 (Israel-Lebanon, conflict re-ignited ~March 2026) and C10 (US-Iran, conflict started ~February 2026) are new hot conflicts being observed at their peak intensity. Their "contested baseline" at W1 is being established during maximum escalation, which will produce abnormally high baselines if allowed to lock at W13 without a reset mechanism for conflict-phase transitions. The methodology needs a conflict phase reset protocol: if a conflict transitions from "latent/cold" to "active/hot" during the observation window, the baseline observation period should restart from the transition date. Currently C10's contested I3 baseline includes W1 observations of Natanz-strike aftermath, which will anchor the "normal" baseline at historically unprecedented levels.

**Rank 4 — Confidence Tiers Need Source-Tier Anchoring**  
The confidence field (`Confirmed/Probable/Possible`) is applied per-indicator but the underlying source-tier system (T1/T2/T3) referenced in notes is not formally linked to confidence thresholds. "Confirmed" appears on Russia-Ukraine I2 with a note citing ISW (T1 adjacent), and on Gaza I2 with a note citing OCHA (T1). But "Confirmed" also appears for DPRK I4 (sanction circumvention via Russia/China), which is a structural inference rather than a sourced event. The confidence taxonomy needs formal definitions: Confirmed = T1 primary source independently corroborated; Probable = T2 source or single T1; Possible = T3 or inference from circumstantial evidence. These definitions should be published in the SCEM methodology note and applied consistently.

**Rank 5 — Roster Additions Likely (Near-Term)**  
Based on current indicator trajectories and the Ethiopia Northern Theatre watch entry:

- **Ethiopia Northern Theatre (Tigray/Amhara/Oromia)** — approaching inclusion. ACLED March 2026 troop movements meet partial I2. Likely crosses dual-indicator threshold if ENDF/TDF engagement escalates beyond March posture. Monitor I2+I6.
- **Pakistan-India (sub-threshold)** — the DPRK SPA "two hostile states" doctrine re-institutionalisation and nuclear posture updates implicitly raise the regional nuclear risk environment; India-Pakistan sub-threshold monitoring should be considered if I3 signals emerge from South Asian context. Not yet on roster.
- **Sahel Fracture (Mali/Niger/Burkina Faso AES bloc)** — Wagner/Africa Corps footprint, French withdrawal, and AES regional fracture from ECOWAS constitute a slow-building multi-indicator environment. Currently below threshold but I4 (economic fracture) and I2 (AES military consolidation) are borderline.

- **Roster retirements (conditional):**
  - **Gaza/Israel-Hamas** — ceasefire is holding at low friction. If Rafah return process continues and I4/I5 deviations persist below +1 for 4+ consecutive weeks, retirement criteria will approach. ESA track (if ceasefire holds) is the most likely exit path. *Caveat: Iran-Gaza crossing closure is a re-escalation risk.*
  - **Haiti Political-Criminal** — not a retirement candidate despite apparent stability. MSS→GSF transition is creating exploitable security gaps; I2/I6 remain above baseline. Monitor for 8+ consecutive weeks of I2 decline before considering retirement.

**Rank 6 — The "CONTESTED" Band is Doing Too Much Work**  
CONTESTED currently functions as both (a) a baseline validity marker and (b) a band level. A RED-band deviation cannot be displayed until baseline locks at W13, which means the monitor will show no RED bands for the entire first quarter of observation for new conflicts — even when those conflicts are at objectively critical indicator levels (C10: I3 nuclear +2, Hormuz closed). This is a structural false negative in the monitor's most important output. Fix: introduce a PROVISIONAL band tier that applies during the CONTESTED period for any indicator deviation ≥ +2, with a clear caveat that it is pre-lock. This would allow the dashboard index to show "PROVISIONAL RED" rather than suppressing the signal entirely.

**Rank 7 — F-Flag Taxonomy Gap: Missing F8 — Indicator Suppression / Access Denied (Active)**  
F6 covers "Data denial / access denied" as a flag type, but currently shows CLEAR. In practice, several conflicts have active indicator suppression: DPRK I6 is explicitly noted as "unmonitorable (no T1 access)" yet is scored at structural zero rather than flagged with F6. Sudan I2 includes hospital strikes with ground-truth gaps. Gaza has a known 4-week OCHA data lag on I6 (noted in the indicator text). These should be triggering F6 flags. F6 = CLEAR is analytically wrong given current data. More broadly, the F-flag taxonomy should be expanded to include: **F8 — Indicator suppression by belligerent** (distinct from F6 general access denial — this is active information warfare against the monitoring function itself, e.g., IRGC jamming, Russian electronic warfare affecting satellite imagery interpretation).

**Rank 8 — Cross-Conflict Spillover Analysis is Absent**  
The monitor tracks 10 conflicts independently. The US-Iran/Israel-Lebanon/Gaza nexus demonstrates that cross-conflict spillover (Hormuz closure affecting Lebanon I4; Iran conditioning ceasefire demands linking C10/C9) is now the dominant analytical challenge. The current schema supports `cross_monitor_flags` but only for links to other SCEM monitors (ESA, etc.), not for within-SCEM conflict linkages. A structured `conflict_linkages[]` field (see Schema Rank 8 above) and a dedicated "Linkage Map" section on the dashboard/report would significantly elevate the monitor's analytical distinctiveness.

---

## Priority Summary

Top 5 actions ranked by value, with effort estimate:

| Rank | Action | Value | Effort | Owner |
|---|---|---|---|---|
| **1** | **Fix dashboard bar chart: add baseline marker to I1–I6 bars** | Critical — the core concept (deviation, not level) is not communicated; every user who reads the dashboard misunderstands the analytical framework | Low — CSS/SVG change to existing bar chart component | Frontend |
| **2** | **Fix report.html rendering bug: Roster Watch and Cross-Monitor sections empty** | High — two complete JSON sections are silently dropped from the canonical intelligence report; analysts reading the report miss all retirement/inclusion signals and all cross-monitor flags | Low — template injection bug; data likely in JSON | Backend/Template |
| **3** | **Add escalation velocity field to JSON schema** | High — without week-over-week delta, the monitor cannot distinguish a new breakout from a stagnant high, which is its primary analytical use case for early warning | Medium — requires prior-week state in cron; delta calculation logic | Data/Cron |
| **4** | **Add PROVISIONAL band tier for CONTESTED-period RED-band deviations (≥+2)** | High — current architecture produces structural false negatives: C10 has three RED-band indicators suppressed by CONTESTED status, making the index read LOW while an active US-Iran war with Hormuz closed is in progress | Medium — schema change + rendering logic + dashboard index recalibration | Data + Frontend |
| **5** | **Add I7 (proxy/third-party warfare) to the indicator framework** | High — proxy warfare is now the dominant escalation vector across 4+ active conflicts (Myanmar, Korea, Sudan, DRC, US-Iran); absorbing it into I2 notes systematically understates the structural escalation drivers the monitor exists to detect | High — requires methodology documentation, historical re-scoring of existing conflicts, cron prompt update | Methodology + Data |

---

*Audit compiled 2026-04-01. All page citations reference live content at https://asym-intel.info/monitors/conflict-escalation/ as of 19:06 CEST.*

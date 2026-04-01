# FCW Domain Audit
**Audited:** Wednesday, 1 April 2026  
**Issue audited:** Issue 2, W/E 2 April 2026  
**Schema version:** 2.0  
**Data source:** https://asym-intel.info/monitors/fimi-cognitive-warfare/data/report-latest.json  
**Pages audited:** dashboard.html · report.html · persistent.html

---

## Part 1: Collected But Not Surfaced

### Overview methodology
The JSON was inspected field-by-field across all top-level arrays. Each field was then cross-referenced against what the three live pages actually render. "Rendered" means the field value is visibly displayed to a user on that page — not merely that the section exists. Fields present in JSON but absent from rendering are the gap.

---

### 1.1 `meta` object

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `meta.issue` | ✓ (2) | ✓ (implied in "Issue 2") | ✓ | ✓ |
| `meta.volume` | ✓ (1) | ✗ not shown | ✗ not shown | ✗ not shown |
| `meta.week_label` | ✓ | ✓ | ✓ | ✗ not shown |
| `meta.published` | ✓ | ✓ | ✓ | ✓ (as "Updated") |
| `meta.slug` | ✓ | ✗ internal only | ✗ internal only | ✗ internal only |
| `meta.publish_time_utc` | ✓ | ✗ not shown | ✗ not shown | ✗ not shown |
| `meta.editor` | ✓ | ✗ not shown | ✗ not shown | ✗ not shown |
| `meta.schema_version` | ✓ | ✓ | ✓ | ✓ |

**Gap:** `meta.volume` is collected but never surfaced anywhere. Minor, but relevant if this becomes a multi-volume publication. `meta.publish_time_utc` is not surfaced; only the date is shown.

---

### 1.2 `signal` object

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `signal.headline` | ✓ | ✓ | ✓ | ✗ not shown |
| `signal.actor` | ✓ ("RU") | ✗ not shown | ✗ not shown | ✗ not shown |
| `signal.confidence` | ✓ ("Confirmed") | ✓ (KPI card) | ✓ (badge on lead signal) | ✗ not shown |
| `signal.f_flags` | ✓ (["F1"]) | ✗ not shown | ✓ (F1 badge) | ✗ not shown |
| `signal.note` | ✓ (MF1 alert text) | ✓ (truncated in lead signal card) | ✓ | ✗ not shown |

**Gap:** `signal.actor` is in JSON but never displayed on any page — the actor behind the lead signal is not labelled. On the dashboard, `signal.f_flags` are absent; they only appear on the report. The persistent page renders none of the signal fields, which is architecturally intentional (it's a living KB, not issue-specific) but means there is no "current issue summary" pointer on persistent.

---

### 1.3 `campaigns[]` array

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `id` | ✓ | ✗ not shown | ✓ (as prefix, e.g. "RU-001") | ✓ |
| `operation_name` | ✓ | ✓ (top 5 only) | ✓ | ✓ |
| `status` | ✓ | ✓ (top 5 only) | ✓ | ✓ |
| `attribution_confidence` | ✓ | ✗ not shown | ✓ (badge) | ✓ (badge) |
| `actor` | ✓ | ✓ (via Actor Threat Board grouping) | ✓ (actor prefix in ID) | ✓ (grouped by actor) |
| `platform` | ✓ | ✗ not shown | ✓ | ✗ not shown |
| `target` | ✓ | ✗ not shown | ✓ | ✗ not shown |
| `summary` | ✓ | ✓ (top 5, abbreviated) | ✓ | ✓ (abbreviated) |
| `last_activity` | ✓ | ✗ not shown | ✓ | ✓ ("Last activity") |
| `f_flags` | ✓ | ✗ not shown | ✓ (inline in summary) | ✗ not shown |
| `changelog` | ✓ | ✗ not shown | ✗ not shown | ✓ (version history) |
| `source_url` | ✓ | ✗ not shown | ✓ ("Source →" link) | ✗ not a direct link per campaign |
| `start_date` | **MISSING** (field recently added, not yet populated — first data expected Apr 9 cron) | ✗ | ✗ | ✗ (timeline Gantt uses `first documented` from persistent, not `start_date`) |

**Gaps:**
- **Dashboard:** `platform`, `target`, `attribution_confidence`, `f_flags`, `last_activity`, `source_url`, `changelog` are all collected but not surfaced. Dashboard shows only top 5 campaigns — the remaining 7 (CN-001, CN-002, AI-NET-001, IR-001, GULF-UAE-001, US-001, IL-001) are **entirely absent** from dashboard view.
- **Report:** `changelog` is collected but not rendered in the report (only in persistent version history). This is a meaningful gap — issue-over-issue changes to a campaign are invisible to report readers.
- **Persistent:** `platform`, `target`, `f_flags`, `source_url` are all in JSON per campaign but not rendered in persistent campaign cards. The persistent timeline Gantt (Campaign Timeline section) is using `first_documented` from the persistent data layer — but once `start_date` is populated in campaigns[], there will be a mismatch unless the Gantt is updated to use the canonical `start_date` field.

---

### 1.4 `actor_tracker[]` array

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `actor` | ✓ | ✓ (Actor Threat Board) | ✓ | ✓ |
| `status` | ✓ | ✓ (dot colour + text) | ✓ (inline text) | ✗ not shown |
| `doctrine` | ✓ | ✗ not shown | ✓ | ✓ |
| `source_url` | ✓ | ✗ not shown | ✓ ("Source →") | ✓ ("Source →") |
| `headline` | ✓ | ✗ not shown | ✓ | ✗ not shown (actor profiles use a different text block) |

**Gaps:**
- Dashboard Actor Threat Board: `doctrine` and `headline` are both in JSON but not displayed. The board shows actor, campaigns count, status, activity level bar, and active/ongoing counts — but not the actor's doctrine or the weekly headline assessment.
- Dashboard also does not show the actor's `status` field as a text label, only as a colour dot — the actual status string ("HIGHLY ACTIVE", "ASSESSED ACTIVE") is not rendered.
- Persistent: `actor_tracker[].headline` is not rendered. Persistent actor profiles use a separate hand-authored text block (doctrine description + primary infrastructure), which is not the same as the `headline` field in JSON. These are diverging.

---

### 1.5 `platform_responses[]` array

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `platform` | ✓ | ✗ not shown | ✓ | ✓ (section header) |
| `action_type` | ✓ | ✗ not shown | ✓ | ✓ |
| `headline` | ✓ | ✗ not shown | ✓ | ✓ |
| `actor` | ✓ | ✗ not shown | ✓ | ✗ not shown |
| `date` | ✓ | ✗ not shown | ✓ | ✗ not shown |
| `source_url` | ✓ | ✗ not shown | ✓ | ✗ not shown (section exists but no per-entry links visible) |

**Gap:** Platform responses are **entirely absent from the dashboard**. For an operational monitor, platform enforcement status is high-signal intelligence — the X enforcement gap (88% of EU-flagged FIMI content remaining) is a critical data point not visible on the primary view. On persistent, `actor`, `date`, and `source_url` are not rendered per entry, reducing the evidentiary traceability of enforcement actions.

---

### 1.6 `attribution_log[]` array

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `id` | ✓ ("ATTR-001") | ✗ | ✗ not shown | ✗ not shown |
| `date` | ✓ | ✗ | ✓ | ✗ not shown |
| `campaign_id` | ✓ | ✗ | ✓ (as label in card header) | ✗ not shown |
| `mf_flags` | ✓ | ✗ | ✓ (inline in note) | ✗ not shown |
| `confidence` | ✓ | ✗ | ✓ (badge) | ✗ not shown |
| `note` | ✓ | ✗ | ✓ | ✗ not shown |
| `source_url` | ✓ | ✗ | ✓ ("Source →") | ✗ not shown |
| `headline` | ✓ | ✗ | ✓ | ✗ not shown |
| `summary` | ✓ | ✗ | ✓ (rendered as the detail text) | ✗ not shown |
| `actor` | ✓ (confusingly set to campaign_id string, e.g. "RU-004") | ✗ | ✗ not rendered separately | ✗ |
| `instrument` | ✓ (set to confidence string, e.g. "High" — appears to be a schema artefact) | ✗ | ✗ | ✗ |

**Gaps:**
- Attribution log is **entirely absent from both dashboard and persistent**. This is the most analytically rich section for users tracking how confidence levels evolve — and it is invisible except on report.html.
- The `id` field (ATTR-001, etc.) is not rendered anywhere, so individual attribution entries cannot be referenced.
- The `actor` field in attribution_log is being populated with the campaign_id string (e.g. "RU-004") rather than the actor code ("RU") — this appears to be a schema population error or a naming collision. The field is semantically ambiguous: it should likely be `actor_code` for the sponsoring actor, distinct from `campaign_id`.
- The `instrument` field is populated with the confidence string ("Assessed", "High") — this appears to be a copy-paste schema error or a field that was repurposed. The field name implies the operational instrument used (e.g. "impersonation website", "financial channel"), not the confidence level.

---

### 1.7 `cognitive_warfare[]` array

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `id` | ✓ ("CW-001") | ✗ | ✓ | ✗ |
| `classification` | ✓ ("COGNITIVE WARFARE") | ✗ | ✓ (section badge) | ✗ |
| `headline` | ✓ | ✗ | ✓ | ✗ |
| `detail` | ✓ | ✗ | ✓ | ✗ |
| `summary` | ✓ (appears to duplicate `significance`) | ✗ | ✗ not rendered separately | ✗ |
| `significance` | ✓ | ✗ | ✗ not rendered | ✗ |
| `source_url` | ✓ | ✗ | ✓ ("Source →") | ✗ |

**Gaps:**
- Cognitive warfare section is **entirely absent from dashboard**. This is a significant intelligence gap for dashboard users — the structural/doctrinal analysis that distinguishes FCW from a simple campaign tracker is not visible at the primary view level.
- `significance` and `summary` appear to contain duplicated or near-identical text (e.g. CW-001: `significance` = "Structural — represents the AI capability transition..." and `summary` = same text). Either this is intentional redundancy (summary for card, significance for tagging) or a schema design error. The `summary` field is not rendered anywhere — if it's meant to be the short-form display version, it needs to be wired up or renamed to avoid confusion.
- Cognitive warfare entries do not appear on persistent.html at all, which means doctrinal/structural CW analysis is ephemeral — it exists only in the weekly report and is lost from the living knowledge base.

---

### 1.8 `cross_monitor_flags` object

| Field | In JSON | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `updated` | ✓ | ✗ | ✓ | ✓ |
| `flags[].id` | ✓ ("CMF-001") | ✗ | ✗ not rendered | ✓ (as section label) |
| `flags[].monitor` | ✓ | ✗ | ✓ | ✓ |
| `flags[].monitor_slug` | ✓ | ✗ internal | ✗ internal | ✗ internal |
| `flags[].headline` | ✓ | ✗ | ✓ | ✓ |
| `flags[].linkage` | ✓ | ✗ | ✓ | ✓ |
| `flags[].classification` | ✓ | ✗ | ✗ not rendered | ✓ |
| `flags[].status` | ✓ | ✗ | ✓ (inline text) | ✓ |
| `flags[].first_flagged` | ✓ | ✗ | ✗ not rendered | ✓ |
| `flags[].updated` | ✓ | ✗ | ✗ not rendered | ✓ |
| `flags[].source_url` | ✓ | ✗ | ✗ not rendered | ✓ ("Monitor →" link) |
| `version_history[]` | ✓ (2 entries) | ✗ | ✗ not rendered | ✗ not rendered |

**Gaps:**
- Cross-monitor flags are **entirely absent from dashboard**. Given that two flags are currently ESCALATED, this is a meaningful gap for users who only check the dashboard.
- `flags[].classification` ("Structural", "Structural — accelerating") is in JSON and shown on persistent but not on report.
- `flags[].first_flagged` and `flags[].updated` are in JSON but not rendered in report.
- `cross_monitor_flags.version_history` is in JSON but not rendered anywhere — the change history for cross-monitor flag escalations is completely invisible to users.
- `flags[].source_url` links to the target monitor's dashboard, not a primary source — rendered as "Monitor →" on persistent but absent from report.

---

### 1.9 Summary: Highest-Value Gaps

| Collected field / section | Not rendered on | Analytical cost of gap |
|---|---|---|
| `campaigns[].f_flags` | Dashboard, Persistent | F-flags signal editorial priority; invisible on primary view |
| `campaigns[].changelog` | Report | Issue-over-issue evolution invisible to report readers |
| `campaigns[].platform` | Dashboard, Persistent | Platform vector is core FIMI intelligence — missing on both views |
| `campaigns[].target` | Dashboard, Persistent | Target is core FIMI intelligence — missing on both views |
| `platform_responses[]` (entire section) | Dashboard | Platform enforcement status absent from primary view |
| `cognitive_warfare[]` (entire section) | Dashboard, Persistent | Structural/doctrinal analysis entirely absent from dashboard; not preserved in living KB |
| `cross_monitor_flags` (ESCALATED flags) | Dashboard | Two ESCALATED flags invisible on primary view |
| `attribution_log[]` (entire section) | Dashboard, Persistent | Attribution evolution invisible outside of report |
| `attribution_log[].instrument` | All | Field has apparent population error (set to confidence string, not instrument type) |
| `attribution_log[].actor` | All | Field appears to store campaign_id rather than actor code — naming/population ambiguity |
| `cognitive_warfare[].significance` | All | Never rendered; duplicates `summary` field — schema redundancy |
| `signal.actor` | All | Actor behind the lead signal never labelled |
| `campaigns[7–12]` (non-top-5) | Dashboard | 7 of 12 tracked campaigns entirely absent from dashboard view |
| `start_date` | All | Field added but not yet populated; persistent timeline will need update when data arrives |

---

## Part 2: Recommended Improvements

### Schema / Data Additions (ranked by value)

**1. Narrative persistence / recurrence tagging** *(High value)*  
Add a `narrative_ids[]` array to each campaign, referencing a top-level `narratives[]` registry. Each narrative entry would carry: `id`, `label` (e.g. "election legitimacy undermining", "NATO collapse narrative", "opposition leader delegitimisation"), `first_observed`, `last_observed`, `actor_spread[]` (which actors use it), and `platform_spread[]`. This enables cross-campaign narrative tracking — the most analytically powerful capability FCW lacks. Currently, the fact that Storm-1516 and SDA are both deploying the "opposition delegitimisation" narrative against Magyar is only visible through manual reading; it cannot be queried, aggregated, or visualised. This is the single highest-value schema addition.

**2. Effectiveness scoring per campaign** *(High value)*  
Add an `effectiveness` object to each campaign with sub-fields: `reach_estimate` (low/medium/high/unknown), `amplification_evidence` (bool + note), `counter_response_triggered` (bool — did it produce a platform takedown, government response, or journalistic rebuttal?), `narrative_penetration` (low/medium/high/unknown — did the narrative enter mainstream media?). This converts FCW from a pure tracking monitor into an impact-assessment monitor. Currently the data describes operations but not their downstream effects.

**3. `start_date` population + timeline Gantt fix** *(High value, immediate)*  
The `start_date` field was added to campaigns schema but is not yet populated. Confirmed for first data on Apr 9 cron. When populated, the persistent.html Campaign Timeline Gantt must be updated to use `campaigns[].start_date` as the canonical bar start point, rather than the `first_documented` field in the persistent layer. These two fields are not synonymous — `first_documented` is the date the monitor first tracked it; `start_date` is the date the operation began. The Doppelganger network (RU-002) illustrates this: `first_documented` in persistent = 2022-09-01 but the actual Gantt bar should reflect the confirmed operation start date. Track `first_documented` separately as a monitor-metadata field.

**4. `attribution_log[].instrument` field — fix population error and populate correctly** *(Medium value, immediate)*  
Currently `instrument` is being set to the confidence string (e.g. "Assessed", "High"). This field should carry the operational instrument/technique — e.g. "impersonation website", "coordinated inauthentic accounts", "financial channel", "AI synthetic video". This is high-value for cross-campaign technique analysis (MITRE ATT&CK-style) and is currently wasted. Rename or repurpose. Similarly, `attribution_log[].actor` should store the actor code (e.g. "RU"), not the campaign_id — the campaign_id is already carried in `campaign_id`.

**5. FIMI Threat Level aggregate field** *(Medium value)*  
Add a top-level `threat_level` object to the JSON alongside `signal`, containing: `level` (BASELINE / ELEVATED / HIGH / CRITICAL), `basis` (brief text explaining the rating), `trend` (STABLE / INCREASING / DECREASING), and `previous_level`. The dashboard already hard-codes "ELEVATED — ACTIVE MULTI-VECTOR OPERATIONS" as what appears to be an editorially determined field, but it is not in the JSON schema — it is either hard-coded in the HTML template or derived from an undocumented field. Making this explicit in the schema allows it to be: (a) tracked over time, (b) used in cross-monitor aggregation, (c) consistently rendered across all three pages.

**6. `cognitive_warfare[]` persistence** *(Medium value)*  
Add CW entries to the persistent data layer with a `first_identified` date and `status` (ACTIVE_DOCTRINE / HISTORICAL / RESOLVED). Currently cognitive warfare analysis is entirely ephemeral — it exists only in the weekly report and is lost from the living knowledge base. Structural CW patterns (e.g. meta-FIMI counter-narrative doctrine, AI-at-scale FIMI) are persistent phenomena that should accumulate in the living KB, not be re-analysed from scratch each issue.

**7. Campaign `linked_campaigns[]` field** *(Medium value)*  
Add a `linked_campaigns[]` array to each campaign entry to make explicit co-targeting relationships. Currently RU-001 carries a changelog note that RU-004 is a "parallel operation targeting same election" — this relationship is buried in a text field and cannot be queried. A `linked_campaigns: ["RU-004"]` on RU-001 (and reciprocally on RU-004) would enable the dashboard to display campaign clusters and the persistent timeline to group co-targeting operations visually.

**8. `platform_responses[]` — add `enforcement_completeness` field** *(Low–Medium value)*  
Add an `enforcement_completeness` field (none / partial / complete) and `assets_actioned` (integer) + `assets_estimated_remaining` (integer or null). Currently entries like "1,700+ assets removed" and "88% of EU-flagged FIMI content remains on X" are narrative strings — not queryable data. This would enable a platform enforcement scorecard view.

**9. Source tier classification** *(Medium value)*  
Add a `source_tier` field to all `source_url`-bearing entries (campaigns, attribution_log, cognitive_warfare). Values: T1 (primary intelligence — government statements, platform transparency reports, court documents), T2 (established research organisations — DFRLab, EEAS, ASPI ICPC, Google TAG), T3 (quality journalism with documented methodology), T4 (secondary/aggregated reporting). This is already implicit in the MF-flag system but not machine-readable per source. It would allow filtering of the attribution log by evidentiary quality and make the analytical standard explicit.

**10. Election / event horizon calendar** *(Low value initially, high value over time)*  
Add a top-level `event_horizon[]` array tracking upcoming elections and high-FIMI-risk events: `event_id`, `date`, `country`, `type` (parliamentary/presidential/referendum), `fimi_risk_level`, `linked_campaigns[]`. This would allow the dashboard to display a forward-looking calendar of FIMI-risk events and the report to contextualise campaigns against an electoral cycle. The Hungary April 12 election is the obvious current use case — it is currently mentioned only in campaign summaries with no structured event data.

---

### Dashboard Rendering Improvements (ranked by value)

**1. Surface all 12 campaigns, not just top 5** *(High value)*  
Seven of twelve tracked campaigns are invisible on the dashboard. Even a condensed two-column grid with ID, name, status badge, attribution confidence, and actor flag would surface the full picture. Currently a dashboard user has no idea that CN-002 (United Front), IR-001 (IRGC), GULF-UAE-001, US-001, or IL-001 exist. The current "Top Campaigns" section implies editorial curation — fine as a featured section — but the remaining campaigns should be accessible in a secondary grid below, not absent entirely.

**2. Add platform enforcement summary widget** *(High value)*  
The platform responses section — currently absent from the dashboard entirely — should appear as a compact widget below the KPI row. A simple table with Platform | Action | Date | Status would surface the X enforcement gap (88% of flagged content remaining) and YouTube inaction on the AI network at the primary view level. These are high-signal intelligence items that currently require navigating to report.html to see.

**3. Add ESCALATED cross-monitor flags alert** *(High value)*  
When any cross-monitor flag has status "Active — ESCALATED", it should render on the dashboard as an alert banner or highlighted card. Currently two flags are ESCALATED (CMF-001, CMF-002) and a dashboard user has no awareness of them. At minimum, a "Cross-Monitor Alerts" widget with the flag headline and target monitor link should appear.

**4. Show campaign platform and target in dashboard cards** *(Medium value)*  
The top-5 campaign cards on the dashboard render name, status badge, and summary — but not platform or target. These are the two most operationally useful fields for quick triage. "TikTok, Telegram" vs "Direct / financial" immediately communicates the attack surface. Add platform and target as compact labels below the summary, matching the report.html card design.

**5. Actor Threat Board: add doctrine label and current headline** *(Medium value)*  
The Actor Threat Board shows actor, campaign count, status dot, activity bar, and active/ongoing count — but not the actor's doctrine or the weekly headline assessment. Adding a one-line doctrine label (e.g. "Active Measures / Reflexive Control") and the `actor_tracker[].headline` field as an expandable or tooltip would make the board analytically meaningful rather than just a count aggregation.

**6. Surface `f_flags` on dashboard campaign cards** *(Medium value)*  
F-flags (F1 = lead signal, F2 = watch, F3 = caution) are the editorial priority signal. They appear on report.html but not on dashboard campaign cards. An F1 badge on RU-001 and RU-004 cards would immediately communicate editorial significance.

**7. Add a Cognitive Warfare panel** *(Medium value)*  
The cognitive_warfare[] section is entirely absent from the dashboard. A compact panel with 2–3 CW headlines and significance labels would surface the doctrinal/structural analysis that distinguishes FCW from a simple campaign list. This is a key differentiator of this monitor's analytical value proposition.

**8. Campaign changelog visible on report** *(Low–Medium value)*  
The `changelog` field exists in campaigns[] and is populated (e.g. "[2026-04-02: New campaign — Storm-1516 confirmed by Gnida project]") but is not rendered in report.html. Adding a "What changed this issue" line in italics beneath each campaign summary would give report readers the ability to immediately identify new developments without re-reading the full summary.

**9. Threat level trend indicator** *(Low value, pending schema fix)*  
Once the `threat_level` field is added to the schema (see Schema recommendation #5), surface the trend arrow (INCREASING / STABLE / DECREASING) alongside the current threat level banner. This requires the schema addition first.

**10. "Last intelligence" staleness indicator** *(Low value)*  
For campaigns where `last_activity` is more than 4 weeks old, add a visual staleness indicator (e.g. grey-out, "last confirmed 6 weeks ago") to help users distinguish live operations from those being maintained on status-unchanged carry-forward. Currently RU-003, CN-001, CN-002, IR-001, GULF-UAE-001, US-001, and IL-001 all have `last_activity` of 2026-03-01 or earlier, which means they are being carried forward on unchanged status without new intelligence — a user cannot distinguish this from a campaign with active new reporting.

---

### Methodology Improvements (ranked by value)

**1. Narrative persistence tracking as first-class methodology** *(Critical value)*  
The current methodology tracks campaigns (actor-attributed operations) and cognitive warfare (doctrinal patterns) — but not narratives as persistent entities that transcend individual campaigns. The most powerful FIMI analysis identifies the same narrative being deployed by different actors across different campaigns and platforms. For example: "Western institutions cannot be trusted to fairly report on election interference" is currently visible as a meta-FIMI pattern in CW-002, but its presence in multiple campaigns (SDA pro-Orbán amplification, SVR Gamechanger plausible deniability seeding, Storm-1516 counter-narrative) is not tracked as a unified narrative. The recommended `narratives[]` registry (Schema #1) enables this — but the methodology should also document how narratives are identified, bounded, and retired.

**2. Cross-platform coherence detection protocol** *(High value)*  
Currently campaigns are tracked per-platform, but cross-platform coordination signals are not systematically assessed. Storm-1516, for example, operates across X, Facebook, Telegram, and fake websites — the fact that content appears synchronously across these platforms is itself an attribution indicator. The methodology should add a `cross_platform_coherence` field to campaigns (with values: NOT_ASSESSED / POSSIBLE / LIKELY / CONFIRMED) and a detection note. The DFRLab AI YouTube network documentation (synchronized pauses/reactivations across 26 channels) is a textbook cross-platform coherence indicator and is noted in the summary but not systematically flagged at the campaign level.

**3. Attribution confidence escalation/de-escalation trigger documentation** *(High value)*  
The methodology page (linked via navigation) should document explicit criteria for when attribution moves between tiers (Possible → Assessed → High → Confirmed, and the reverse). Currently the MF-flag system documents caution conditions, but there is no explicit protocol for what evidence is required to upgrade or downgrade. The ATTR entries in attribution_log are the right mechanism for this, but the instrument field error (see Schema #4) undermines the evidentiary chain. A formal escalation matrix — specifying what constitutes Tier 1/2 evidence for each actor — would strengthen analytical rigour and make the methodology auditable.

**4. Status-unchanged carry-forward policy** *(High value)*  
Seven of twelve campaigns have `last_activity` dates of 2026-03-01, indicating they are being maintained on status-unchanged carry-forward from the inaugural issue. The methodology should define: (a) the maximum number of issues a campaign can be carried forward on unchanged status before being moved to MONITORING / DORMANT, (b) what triggers a status review, and (c) the distinction between ONGOING (operation confirmed still active, just no new intelligence this issue) vs status-unchanged carry-forward (no new intelligence, status not independently verified this cycle). Currently ONGOING is being used in both senses, which degrades the precision of the status taxonomy.

**5. Election-proximate FIMI density scoring** *(High value)*  
The Hungary situation has revealed a need for a systematic methodology for assessing pre-election FIMI density — multiple simultaneous operations targeting the same electoral event. The report notes "highest-density FIMI targeting in Europe Q1 2026" as an editorial judgement, but this should be methodologically defined: a density score that accounts for number of confirmed/assessed operations, attribution confidence levels, days to election, and platform reach estimate. This would make the FCW monitor's election-period assessments comparable across elections (Hungary 2026 vs Germany 2025 vs France 2027) rather than relying on editorial characterisation.

**6. AI-FIMI convergence tracking as structured sub-domain** *(Medium value)*  
The AI-generated YouTube network (AI-NET-001) and the EEAS 47% AI-assisted figure indicate that AI-enabled FIMI is becoming structurally distinct from traditional information operations. The methodology should define AI-FIMI as a tracked sub-domain with specific indicators: use of synthetic media (deepfake/AI anchor), LLM-generated text at scale, automated amplification, AI-generated imagery in fabricated news. CW-001 captures this as a cognitive warfare entry, but it should also feed a structured `ai_fimi_indicators[]` field on relevant campaigns. This would allow the AI Governance Monitor (cross-monitor CMF-003) to receive structured data rather than just a text flag.

**7. Counter-narrative / meta-FIMI tracking** *(Medium value)*  
CW-002 identifies "meta-FIMI" — operations that target the interference reporting itself — as a distinct analytical category. The MF1 flag partially captures this (it flags counter-narratives attempting to delegitimise the story), but the methodology should formalise meta-FIMI as a campaign type in its own right, with its own `is_meta_fimi: bool` flag and `primary_campaign_id` reference. The Hungarian Conservative counter-narrative and the SVR Gamechanger "motivated counter-narrative" from pro-Orbán sources are analytically distinct phenomena — one is a media outlet with motivated editorial stance, the other is potentially state-directed counter-intelligence — and the methodology should distinguish between them.

**8. Source diversification protocol** *(Low–Medium value)*  
Several campaigns (RU-003, CN-002, IR-001, GULF-UAE-001, US-001, IL-001) rely on single-source attribution from the inaugural issue. The methodology should include a source diversification checklist: at minimum two independent Tier 1/2 sources before Confirmed status, one for High. The current methodology documents MF flags for single-source caution (MF3) but does not specify the affirmative criteria for reaching each confidence level. This is the gap that the attribution escalation matrix (Methodology #3) would fill.

---

## Priority Summary

Top 5 actions ranked by analytical value, with implementation effort:

| Rank | Action | Effort | Value |
|---|---|---|---|
| **1** | **Fix `attribution_log[].instrument` and `.actor` field population errors** — these are active schema errors degrading the evidentiary record. `instrument` should carry technique (e.g. "impersonation website"), not confidence; `actor` should carry actor code, not campaign_id. Fix in next cron run. | **Low** | **Critical** |
| **2** | **Add `narrative_ids[]` to campaigns and a top-level `narratives[]` registry** — enables cross-campaign narrative tracking, the highest-value analytical capability FCW currently lacks. Allows querying "which campaigns are running the same narrative" and tracking narrative persistence over time. | **High** | **High** |
| **3** | **Surface platform_responses[], cognitive_warfare[], and ESCALATED cross_monitor_flags on the dashboard** — three entire sections with high analytical value are invisible on the primary view. Minimum viable: a Platform Enforcement widget, a CW panel with 2–3 headlines, and an escalation alert banner. | **Medium** | **High** |
| **4** | **Add `threat_level` object to JSON schema** (level / basis / trend / previous_level) and wire it to the dashboard banner — the "ELEVATED — ACTIVE MULTI-VECTOR OPERATIONS" label currently displayed on the dashboard appears to be editorially set outside the schema. Making this a structured field enables time-series tracking and cross-monitor aggregation. | **Low** | **Medium** |
| **5** | **Migrate `cognitive_warfare[]` entries to persistent layer** with `first_identified` and `status` fields — structural CW patterns (AI-FIMI convergence, meta-FIMI doctrine) are analytically persistent and should accumulate in the living knowledge base rather than being ephemeral per-issue entries. This preserves institutional analytical memory across issues. | **Medium** | **Medium** |

---

*Audit conducted 1 April 2026 by FCW domain analyst. JSON fetched from https://asym-intel.info/monitors/fimi-cognitive-warfare/data/report-latest.json. Live pages audited at dashboard.html, report.html, persistent.html.*

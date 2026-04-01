# WDM Domain Audit
**Issue 3 — W/E 1 April 2026 | Audit conducted: 1 April 2026**
**Auditor:** Domain Expert, World Democracy Monitor / Asymmetric Intelligence
**Source JSON:** `https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json` (48,408 bytes confirmed)
**Persistent page 404 status:** RESOLVED — persistent.html loads correctly as of this audit.

---

## Part 1: Collected But Not Surfaced

The table below maps every JSON field (present or absent) against rendering status on all three live pages. Status codes: **YES** = rendered and populated; **STUB** = section placeholder rendered but empty/no-data message shown; **NO** = absent from page; **PARTIAL** = rendered but incomplete.

| Field / Section | In JSON (Issue 3) | Dashboard | Report | Persistent |
|---|---|---|---|---|
| `meta` (issue, volume, week_label, published, schema_version) | YES | Partial — week_label and published shown; issue number shown on report only | YES (issue/published/schema displayed) | YES (last updated, total issues) |
| `signal.headline` | YES | YES (Lead Signal headline card) | YES | YES (weekly brief intro references it) |
| `signal.body` | YES | YES (Lead Signal body) | YES (blurred teaser + Full Brief link) | NO |
| `signal.source_url` | YES | NO (not linked) | YES (Full Brief link) | NO |
| **`signal.silent_erosion`** | **MISSING** | **NO** | **NO** | **NO** |
| **`signal.history`** (week-over-week trend table) | **MISSING** | **NO** | **NO** | **NO** |
| `heatmap.rapid_decay[]` (15 entries: country, severity_score, severity_arrow, lead_signal, summary, confidence, entry_type, first_seen, last_material_change) | YES | YES — top 5 in table + most-severe cards | YES — full 15-entry table | YES — all entries in persistent tracking table |
| **`heatmap.rapid_decay[*].severity_sub`** (electoral / civil_liberties / judicial sub-scores) | **MISSING from JSON** | **NO** | **NO** | **NO** |
| `heatmap.rapid_decay[*].source_url` | YES (key present, ALL 15 empty string) | NO | NO | NO |
| `heatmap.recovery[]` (5 entries) | YES | NO — recovery not shown on dashboard | YES — full table | YES — persistent tracking table |
| **`heatmap.recovery[*].lead_signal`** | **MISSING** (present on rapid_decay, absent on recovery) | **NO** | **NO** | **NO** |
| **`heatmap.recovery[*].severity_sub`** | **MISSING** | **NO** | **NO** | **NO** |
| `heatmap.recovery[*].source_url` | YES (key present, ALL 5 empty) | NO | NO | NO |
| `heatmap.watchlist[]` (9 entries: country, severity_score, severity_arrow, escalation_trigger, triggers[], threshold_crossed, summary, confidence) | YES | NO — watchlist not shown on dashboard | YES — full table | YES — persistent tracking table |
| **`heatmap.watchlist[*].lead_signal`** | **MISSING** | **NO** | **NO** | **NO** |
| **`heatmap.watchlist[*].severity_sub`** | **MISSING** | **NO** | **NO** | **NO** |
| `heatmap.watchlist[*].source_url` | YES (key present, ALL 9 empty) | NO | NO | NO |
| `intelligence_items[]` (6 entries: rank, country, headline, summary, tier, resilience, severity, source_url) | YES | YES — top 5 shown | YES — all 6 shown | NO |
| **`intelligence_items[*].date`** | **MISSING** | **NO** | **NO** | **NO** |
| `institutional_integrity_flags[]` (7 entries: flag_type, country, headline, summary, severity, lead_time, source, source_url) | YES | NO | YES — all 7 shown | YES — rendered with triggers and escalation trigger |
| `institutional_integrity_flags[*].source_url` | PARTIAL — 3 of 7 populated | NO | PARTIAL | PARTIAL |
| `regional_mimicry_chains[]` (2 chains: chain_id, headline, links[]) | YES | NO | YES — both rendered (headline + links visible) | PARTIAL — headline only, link detail absent |
| **`regional_mimicry_chains[*].mechanism`** | **MISSING** | **NO** | **NO** | **NO** |
| **`regional_mimicry_chains[*].spread_velocity`** | **MISSING** | **NO** | **NO** | **NO** |
| **`regional_mimicry_chains[*].origin`** | **MISSING** | **NO** | **NO** | **NO** |
| `regional_mimicry_chains[*].links[*]` (country, law, year) | YES | NO | YES | NO |
| **`regional_mimicry_chains[*].links[*].status`** (active/enacted/blocked) | **MISSING** | **NO** | **NO** | **NO** |
| `cross_monitor_flags.flags[]` (6 flags: id, title, monitors_involved, status, significance, first_flagged, last_updated, body, action, unchanged_since) | YES | NO | YES — all 6 rendered | NO |
| **`cross_monitor_flags.flags[*].linked_countries`** | **MISSING** | **NO** | **NO** | **NO** |
| `weekly_brief` (6,369 chars) | YES | NO | YES — full text rendered | YES — full text rendered |
| **`monthly_trend`** (rapid_decay_now vs 4w_ago, recovery_now vs 4w_ago) | **MISSING** | **NO** | **NO** | STUB — placeholder text visible |
| **`electoral_watch`** (timeline / environment / positive_transitions) | **MISSING** | **NO** | STUB — "No electoral watch data this issue." | STUB — "Electoral watch data not yet in schema." |
| **`digital_civil`** (restrictions / crackdowns) | **MISSING** | **NO** | STUB — "No digital/civil space entries this issue." | STUB — "Digital & Civil Space data not yet in schema." |
| **`autocratic_export`** (template_laws / financing) | **MISSING** | **NO** | STUB — "No autocratic export entries this issue." | STUB — "Autocratic Export data not yet in schema." |
| **`state_capture`** (broadcaster_capture / judicial_packing) | **MISSING** | **NO** | STUB — "No state/media capture entries this issue." | STUB — "State & Media Capture data not yet in schema." |
| **`institutional_pulse`** (10 entries with resilience flags) | **MISSING** | **NO** | STUB — "No institutional pulse data this issue." | STUB — "Institutional Pulse data not yet in schema." |
| **`legislative_watch`** (11 active bill entries) | **MISSING** | **NO** | STUB — "No legislative watch entries this issue." | STUB — "Legislative Watch data not yet in schema." |
| **`research_360.friction_notes`** (5 active source-conflict notes) | **MISSING** | **NO** | STUB — "No friction notes this issue." | STUB — "Friction notes not yet in schema." |
| **`networks`** (nodes) | **MISSING** | **NO** | **NO** | STUB — "Networks section not yet in schema." |
| `source_url` (top-level) | YES | NO | YES (implied via Full Brief link) | NO |

**Summary counts (Issue 3):**
- Fields present in JSON but not rendered anywhere: `signal.source_url` (dashboard/persistent), `heatmap[*].source_url` (all 29 entries empty), `cross_monitor_flags` (not on dashboard or persistent)
- Fields specified in schema / cron prompt but absent from JSON: `severity_sub`, `signal.silent_erosion`, `signal.history`, `monthly_trend`, `electoral_watch`, `digital_civil`, `autocratic_export`, `state_capture`, `institutional_pulse`, `legislative_watch`, `research_360.friction_notes`, `networks`, `heatmap.recovery[*].lead_signal`, `intelligence_items[*].date`, mimicry chain `mechanism/spread_velocity/origin/links[*].status`
- Category B sections confirmed absent from Issues 1–3, expected from Issue 4 onwards (two-pass commit fix applied 1 April 2026)
- `persistent.html` 404: **RESOLVED** — page renders correctly as of this audit

---

## Part 2: Recommended Improvements

### Schema/Data Additions (ranked by analytical value)

**1. `severity_sub` — sub-dimension scores per heatmap entry [Critical | Effort: Low]**
This is already specified in the cron prompt schema but has never appeared in any of the three issues. Every heatmap entry should carry three sub-scores: `electoral` (0–10), `civil_liberties` (0–10), `judicial` (0–10), each with a trend arrow and brief rationale. This is the single highest-value missing field because:
- It makes the composite severity score interpretable and auditable — researchers can see whether a score of 7 reflects total electoral collapse, total civil society destruction, or an even distribution
- It directly enables the cross-section analysis the methodology promises (V-Dem, Freedom House, and IDEA each map primarily to one of these three dimensions)
- It allows meaningful comparison between structurally different cases (e.g. Iran severity 10 is across all three; US severity 5.5 is primarily judicial + electoral, with civil liberties still partially intact)
- The rendering slots exist; the data just needs to arrive. No new UI work required once the cron outputs it.
**Fix:** Enforce `severity_sub` as a required schema field with validation. If the LLM omits it, the cron should retry or surface a schema error. Document the 1–10 anchors per sub-dimension so the LLM applies them consistently.

**2. `heatmap.recovery[*].lead_signal` — parity with rapid_decay entries [High | Effort: Low]**
Recovery entries lack the `lead_signal` field that is present on every rapid_decay entry. This is asymmetric and analytically important: analysts need the leading indicator driving recovery classification just as much as the one driving decay. Venezuela's `lead_signal` should be "Foro Penal confirmed 621 releases, 500+ still held, revolving-door arrests continue" — this is structurally different from a clean democratic transition and that distinction lives in the lead signal.
**Fix:** Add `lead_signal` as a required field on all three heatmap tiers (rapid_decay, recovery, watchlist) in the cron prompt schema.

**3. `heatmap[*].source_url` — populate or remove [High | Effort: Low]**
All 29 heatmap entries have `source_url` as an empty string. This field was included in the schema but is never populated by the cron. Either: (a) populate it with the most authoritative single source for each country's current classification, or (b) move sourcing to the intelligence_items layer where it already works (6/6 populated). Empty source URLs degrade credibility for researchers and journalists who expect every classification to be traceable to a primary source.
**Fix:** Either populate `source_url` with the authoritative V-Dem/Freedom House/CIVICUS URL per country, or restructure as `sources[]` array allowing 1–3 sources per entry. Enforce non-empty in schema validation.

**4. `signal.silent_erosion` — long-form analytical paragraph [High | Effort: Low]**
A 300–600 word analytical paragraph per issue identifying erosion that is real and measurable but is not generating news coverage — the structural deterioration happening underneath the headline events. This is the methodology's most distinctive value-add over wire services. Currently the `signal` section only has `headline` + `body` (which reads like a news summary). `silent_erosion` should surface things like: the 97% SCOTUS emergency request rate that is not a single news story but a structural pattern; the way Bolivia's clean transfer creates a false positive anchor in regional comparisons; the mechanics of how Benin's overnight constitutional revision passed under a news blackout.
**Fix:** Add `signal.silent_erosion` to cron schema as a required 300–600 word analytical field, distinct from `body` which summarises the week's top stories.

**5. `signal.history` — week-over-week trend table [High | Effort: Low]**
A structured table showing changes since the previous issue: new rapid_decay entries, escalations from watchlist to rapid_decay, de-escalations, new recovery entries, countries exited. Currently this context lives only inside `weekly_brief` as prose. As a structured field, `signal.history` would enable the dashboard and persistent page to render a diff view — "this week: +2 rapid_decay, -1 watchlist, Benin escalated" — which is the most immediately actionable summary for a busy analyst.
**Fix:** Add `signal.history` as a structured array: `[{country, previous_tier, current_tier, direction, reason}]`. Render as a "This Week's Changes" table on both report and persistent.

**6. `monthly_trend` — 4-week comparative KPI block [High | Effort: Low]**
The persistent page already has a stub and the placeholder text explains the dependency on 4 issues of data (which will be reached by Issue 5, week of 13 April). The cron schema should already be building this from Issue 1. The fields needed: `rapid_decay_now`, `rapid_decay_4w_ago`, `recovery_now`, `recovery_4w_ago`, `watchlist_now`, `watchlist_4w_ago`, `net_change_direction`. This renders as a comparison KPI strip on the dashboard and a trend chart on persistent — the most requested feature for analysts tracking aggregate democratic health over time.
**Fix:** Ensure cron is accumulating historical issue counts and computing diffs. Render on dashboard as a second KPI row ("vs 4 weeks ago: Rapid Decay +2, Recovery -1") and on persistent as a trend line with issue markers.

**7. `intelligence_items[*].date`** — event date vs publication date [Medium | Effort: Low]**
Intelligence items have no event date. When item #4 references "the tariff ruling (Feb 20)" this is embedded in prose but not structured. Adding an `event_date` field enables: sorting by recency, filtering stale items from multi-issue persistent view, and cross-referencing with other monitors' event timelines (critical for SCEM and FCW feeds).
**Fix:** Add `event_date` (ISO 8601) to intelligence_items schema. Distinct from `meta.published`.

**8. `regional_mimicry_chains[*]` — mechanism, spread_velocity, origin fields [Medium | Effort: Low]**
The two current chains (Russian Foreign Agent Law, Electoral Restriction Template) have only `chain_id`, `headline`, `links[]`, and `source_url`. Missing:
- `mechanism`: the transmission pathway (direct legislative copying / advisory assistance / cross-party learning / international organisation-mediated)
- `spread_velocity`: how fast the template is spreading (number of adoptions per year)
- `origin`: the originating actor/country/model
- `links[*].status`: whether the law is `enacted`, `pending`, `blocked`, or `repealed`
These fields transform the mimicry chain from a list of facts into an analytical model about how autocratic practices propagate. The `links[*].status` field is especially critical: Bosnia-Herzegovina's law was suspended in May 2025, which makes it an attempted-but-blocked case — analytically very different from enacted cases. This distinction is currently invisible in the data.
**Fix:** Add these four fields to the cron schema for mimicry chains.

**9. `state_capture` broadcaster sub-field — disaggregate from judicial_packing [Medium | Effort: Low]**
When Category B lands in Issue 4, the `state_capture` section bundles `broadcaster_capture` and `judicial_packing` together. These are structurally different forms of capture (media ecosystem vs legal system) and should be tracked separately. Judicial packing is a leading indicator for democratic consolidation; broadcaster capture is a leading indicator for civil society suppression. Bundling them makes cross-country pattern analysis harder.
**Fix:** Keep them as separate sub-sections within `state_capture` or as separate top-level sections. The cron prompt schema already partially disaggregates them — ensure the JSON output preserves that structure.

**10. `cross_monitor_flags.flags[*].linked_countries` — explicit country array [Medium | Effort: Low]**
Cross-monitor flags (cms-001 through cms-006) currently lack a structured list of the WDM-heatmap countries they affect. This field is critical for feeding ESA, SCEM, and AGM: a downstream monitor needs to know which heatmap countries are implicated by cms-003 (AI platform capture as media capture) to properly contextualise its own signals.
**Fix:** Add `linked_countries[]` as a required field on each cross-monitor flag.

---

### Dashboard Rendering Improvements (ranked)

**1. Monthly trend KPI row — add "vs 4 weeks ago" delta line [Critical | Effort: Low]**
The dashboard's current KPI section shows only current-issue counts (29 countries, 15 rapid decay, 9 watchlist, 5 recovery). It should add a second row showing deltas vs. 4 weeks prior. This is the most actionable single-number summary for a democratic health monitor. Without it, the KPI section is a snapshot without context.
Implementation: render `monthly_trend` data as `±N vs 4w ago` beneath each KPI card. If fewer than 4 issues exist, show "tracking since Issue 1."

**2. Recovery and Watchlist sections — add to dashboard [High | Effort: Medium]**
The dashboard shows only `heatmap.rapid_decay` (top 5). Recovery and Watchlist entries are not rendered anywhere on the dashboard. For analysts who need the full picture, this means a required context switch to report.html. The dashboard should render:
- A "Recovery Progress" section (mirroring Most Severe format) showing the 5 recovery countries with their scores and key development
- A "Watchlist Threshold" section showing the 3–5 countries closest to crossing the rapid decay threshold (highest `threshold_crossed` count)
This also makes the colour-coded KPI bar (red/amber/green) legible — currently the green "5 recovery" card is present but no recovery details are visible.

**3. `signal.silent_erosion` — dashboard analytical block [High | Effort: Low]**
Once `silent_erosion` is in the JSON, it should render on the dashboard as a dedicated section beneath the Lead Signal card — a distinct visual treatment (grey background, longer typography, "Structural Signal" label) that separates it from the headline-driven brief. This is the monitor's highest-value analytical differentiator for the target audience (researchers, policy analysts, journalists) who read the dashboard as their primary interface.

**4. Geographic View — severity visualisation improvement [Medium | Effort: High]**
The geographic map is present but appears to render countries without severity gradation visible in the screenshot. The map should use a 5-tier colour scale (deep red 8–10 / red 6–7.9 / amber watchlist / green recovery / grey unmonitored) with country labels on hover showing severity score, trend arrow, and lead signal excerpt. The V-Dem and Freedom House methodologies both use geographic visualisation as a primary communication tool; the WDM map should match that standard.

**5. `heatmap[*].severity_sub` radar chart — per-country detail view [Medium | Effort: High]**
Once severity_sub lands, each country card in the Most Severe section should offer a click-through to a mini radar chart showing electoral / civil_liberties / judicial sub-scores. This allows rapid visual differentiation between structurally similar overall scores with very different component profiles (e.g., Hungary 5 vs. Serbia 4 — similar scores, very different profiles across the three dimensions).

**6. Cross-monitor flags — add to dashboard [Medium | Effort: Low]**
Cross-monitor flags appear on report.html but not dashboard.html. A compact "Cross-Monitor Signals" strip on the dashboard (showing cms-ID, title, monitors_involved, status) would serve the downstream monitors (SCEM, FCW, ESA, AGM) that consult the WDM dashboard as a primary feed. Currently those analysts must navigate to report.html to see these flags.

**7. Intelligence items — add tier filter [Low | Effort: Low]**
The dashboard shows intelligence items as an unfiltered list. A simple tier-based filter (Electoral / Constitutional / Resilience / Transition / Civil Society) would let journalists and researchers quickly surface the category most relevant to their work. The `tier` field is already in the JSON.

---

### Methodology Improvements (ranked)

**1. Severity sub-dimension anchoring — define 1–10 per dimension explicitly [Critical | Effort: Medium]**
The composite severity score (1–10) has no published sub-dimension anchors. The V-Dem methodology publishes explicit coding rules for each indicator; the WDM needs the equivalent. Define three 1–10 scales with anchor descriptions:
- **Electoral** (1 = free, fair, competitive; 10 = no meaningful elections or all candidates state-controlled)
- **Civil Liberties** (1 = full freedoms; 10 = totalitarian suppression of press, assembly, association)
- **Judicial Independence** (1 = independent, fully functional; 10 = judiciary fully captured or non-functional)
Without published anchors, the composite score is not reproducible across time or between LLM runs. Iran 10 and Nicaragua 9.5 look calibrated, but explaining the difference structurally requires these anchors.

**2. Heatmap entry_type taxonomy — clarify 'Episode' vs 'Persistent' vs 'Transient' [High | Effort: Low]**
The `entry_type` field takes values Episode / Persistent / Transient (all three appear in persistent.html tracking). These are not defined anywhere in the methodology documentation. As currently used:
- Episode = a country in active decay with a specific triggering event pattern
- Persistent = a country in chronic long-term deterioration without a specific precipitating episode
- Transient = early warning stage, possibly noise
But this is inferred from the data, not documented. Iraq is classified as `Transient` (severity 6) while Colombia is `Persistent` (severity 4) — this seems inconsistent given Colombia's terror threat trajectory. Formalise the definitions and add a decision tree for classification.

**3. Recovery classification rigour — add reversal risk score [High | Effort: Medium]**
Venezuela is classified as Recovery / Probable at severity 7 — the highest-severity recovery entry. But "Recovery" implies a trajectory toward democratic consolidation; at severity 7, the more accurate framing is "transition under coercion, reversal highly probable." The methodology needs a `reversal_risk` field on recovery entries (Low / Medium / High) to distinguish genuine democratic consolidations (South Korea: Low reversal risk; Bolivia: Low) from coerced or transactional transitions (Venezuela: High). Without this distinction, Recovery is analytically confusing — Venezuela and South Korea appearing in the same tier creates false equivalence.

**4. Watchlist threshold calibration — the `threshold_crossed` count needs weighting [High | Effort: Medium]**
Watchlist entries currently track `threshold_crossed` as a raw count of active triggers (Bangladesh: 3, Israel: 3, India: 4, Mexico: 3, Benin: 4). But all triggers are treated equally — a V-Dem autocratizer designation carries the same weight as a single journalist arrest. The methodology should weight triggers by severity and reversibility:
- **Tier 1 (structural / hard to reverse):** Constitutional changes, judicial packing, electoral redistricting, state broadcaster capture → weight 3
- **Tier 2 (legislative / reversible):** Foreign agent laws, NGO restrictions, emergency powers legislation → weight 2
- **Tier 3 (episodic / potentially reversible):** Press crackdowns, protest suppression, individual prosecutions → weight 1
This produces a weighted escalation score rather than a raw count, making India (4 triggers, 3 of which are Tier 1–2 structural) correctly rank higher risk than Colombia (3 triggers, more episodic). Aligns with V-Dem's approach to indicator weighting.

**5. Regional coverage gaps — Sub-Saharan Africa and Central Asia [High | Effort: Medium]**
The current 29-country heatmap has significant regional gaps:
- **Sub-Saharan Africa:** Only DRC (7), Tanzania (8), Uganda (4.5), Benin (5.5) — major omissions include Ethiopia (ongoing civil war + civil society suppression), Mozambique (contested 2024 election + post-election violence), Sudan (democratic collapse under civil war), Zimbabwe (Mnangagwa consolidation), Cameroon (anglophone crisis + media suppression), and Rwanda (RPF single-party consolidation).
- **Central Asia:** Kazakhstan (7) is the only entry — Tajikistan (effectively authoritarian, no meaningful elections since 1994), Kyrgyzstan (competitive authoritarianism), and Turkmenistan/Uzbekistan (consolidated autocracies relevant as diffusion nodes) are absent.
- **Middle East / MENA:** Only Iran (10) and Iraq (6) — Turkey's ongoing democratic erosion (V-Dem electoral autocracy, journalist imprisonments, 2024 Istanbul mayor case) is absent despite being a NATO member and EMFA-relevant case. Egypt and Tunisia's trajectories are related but only Tunisia is tracked.
These gaps are not just coverage problems — they create selection bias in the regional_mimicry_chains analysis. If you're tracking the Russian Foreign Agent Law chain and missing Ethiopia (which enacted a comparable CSO law in 2009, the template for several African adoptions), the chain is structurally incomplete.

**6. Cross-monitor feed protocol — formalise WDM → SCEM/FCW/ESA/AGM signal format [High | Effort: Medium]**
The cross_monitor_flags section (6 flags currently) is the primary mechanism by which WDM feeds the four downstream monitors. But the current format lacks:
- `priority` (1–5) to allow downstream monitors to triage incoming WDM signals
- `linked_countries[]` to allow downstream monitors to filter by their own country coverage
- `action_required_by` field — which monitor should act on this signal and what specific action
- `confidence` at the flag level (not just at the heatmap entry level)
Without these fields, the downstream monitors consume WDM signals as unstructured text, which defeats the purpose of structured cross-monitor intelligence. The `unchanged_since` field is a good start but needs the other fields to be operationally useful.

**7. Resilience indicator underweighting — three positive signals in 6 intelligence items is correct, but the methodology needs a resilience index [Medium | Effort: High]**
Currently 3 of 6 intelligence items are coded `resilience: True` (Venezuela releases, SCOTUS tariff ruling, Serbia student movement). The heatmap has a recovery tier. But there is no aggregate resilience score or index — no equivalent of the decay severity score on the positive side. A Democratic Resilience Index per country (drawn from: judicial checks recorded, civil society mobilisation, electoral surprises, press freedom improvements) would allow the monitor to track both directions simultaneously. V-Dem's Liberal Component Index and the DEC Resilience Project both provide methodological templates.

**8. Source diversity audit — CIVICUS over-indexation [Medium | Effort: Low]**
Across Issues 1–3, CIVICUS appears in the key development text for approximately 40% of heatmap entries. While CIVICUS Monitor is a high-quality source, this creates two problems:
- **Methodological**: CIVICUS uses its own methodology (CIVICUS Monitor Rating), which can diverge from V-Dem's LDI or Freedom House's Freedom Score. When WDM evidence relies primarily on one source's judgement, the WDM score effectively re-publishes CIVICUS with a different label.
- **Timing**: CIVICUS watchlists are monthly; V-Dem is annual; RSF is annual. The WDM runs weekly. For fresh weekly signal, RSF (press freedom), IPI (journalist safety), and Election Watch (electoral integrity real-time) should be weighted more heavily than annual-cycle sources for in-issue updates.
**Fix:** Source diversity requirement in cron prompt: for each heatmap entry, require at minimum one V-Dem/Freedom House/IDEA source AND one current-week source (RSF, IPI, CIVICUS watchlist, Election Watch, HRW press release). Flag entries with only single-source evidence.

**9. Mimicry chain methodology — transmission vs correlation [Medium | Effort: Medium]**
The current mimicry chain analysis asserts that Hungary's redistricting model connects to the US SAVE America Act and Benin's constitutional revision. This is plausible but the mechanism is asserted, not evidenced. The methodology should require:
- A documented transmission pathway (direct legislative copying: cite the bill text comparison; advisory: cite the consulting relationship; learning: cite the documented reference)
- A counterfactual test: would this law have emerged without the template? (Some "chains" are parallel development from shared authoritarian principles, not transmission)
The distinction matters analytically: a genuine mimicry chain where Orban's advisors are documented to have assisted Benin's constitutional revision is a very different security signal than two governments independently adopting the same logical solution to the same problem. The chain analysis should distinguish these cases.

**10. `research_360.friction_notes` — highest-value currently-missing section for methodology credibility [Medium | Effort: Low]**
Of all the Category B sections expected from Issue 4, `friction_notes` is the most analytically distinctive. The five active source-conflict notes document cases where V-Dem, Freedom House, and CIVICUS give materially different assessments of the same country — and explain why WDM resolves the conflict in a particular direction. This is the section that makes WDM methodologically transparent rather than opaque. Examples of expected friction notes:
- US: V-Dem LDI ranks US at 51st globally; Freedom House still classifies as Free (84/100). WDM resolves toward V-Dem because the LDI captures procedural erosion faster than Freedom House's binary categories.
- Israel: V-Dem, RSF, DEC all show deterioration; Freedom House's score is affected by the Oct 7 context. WDM separates domestic democratic indicators from security-driven constraints.
When friction_notes land in Issue 4, they should be prominently positioned — not buried at the bottom of report.html. They should appear early in the methodology section and be linked from heatmap entries where source conflict exists.

---

## Priority Summary

Top 5 actions ranked by research/policy/journalism value, with effort estimate:

| Rank | Action | Value | Effort | Dependency |
|---|---|---|---|---|
| **1** | **Enforce `severity_sub` output from cron** — add schema validation to require electoral/civil_liberties/judicial sub-scores per heatmap entry. Already specified in cron schema but never appearing. Render on report heatmap table and persistent tracking table immediately. | Critical — makes every severity score interpretable and auditable | **Low** — cron prompt fix + existing render slots | None |
| **2** | **Add `heatmap.recovery[*].lead_signal` + `heatmap.watchlist[*].lead_signal`** — parity with rapid_decay. Single cron prompt fix. Renders immediately in existing table layout. | High — recovery lead signal is analytically distinct from decay signal; analysts need both | **Low** — cron prompt fix only | None |
| **3** | **Populate `heatmap[*].source_url`** — all 29 entries currently have empty string. Add V-Dem/CIVICUS/Freedom House canonical URL per country to cron output. | High — every classification must be traceable to a primary source for researcher/journalist credibility | **Low** — cron prompt instruction update | None |
| **4** | **Add `signal.silent_erosion` field + render on dashboard and report** — the monitor's highest-value analytical differentiator. 300–600 word structural analysis per issue identifying real erosion below the news line. | High — differentiates WDM from wire service summarisation; most distinctive output for policy/journalism audience | **Low** (cron prompt) + **Medium** (dashboard render) | None |
| **5** | **Category B sections live from Issue 4 (already in flight)** — verify `electoral_watch`, `digital_civil`, `autocratic_export`, `state_capture`, `institutional_pulse`, `legislative_watch`, `research_360.friction_notes` all appear and render correctly after the two-pass commit fix. Specifically: verify persistent.html stubs are replaced with live data; verify `friction_notes` is positioned prominently, not buried. | Critical — these are the analytical depth sections that elevate WDM above a heatmap tracker to a full intelligence product | **Low** (already fixed per task context) — verify only | Two-pass commit fix (applied 1 April) |

**Additional near-term actions (Issues 4–6 target):**

- `monthly_trend` computation: persistent page stub is ready; cron needs to accumulate and diff issue counts. Renders as KPI delta row on dashboard. Available at Issue 5 (4-week threshold). **Effort: Low.**
- `signal.history` structured diff table: "This week's changes" — escalations, new entries, exits. **Effort: Low (cron) / Low (render).**
- Regional coverage expansion: Turkey, Ethiopia, Zimbabwe, Sudan minimum. These countries' absence creates selection bias in the mimicry chain analysis. **Effort: Medium (cron scope expansion).**
- Weighted escalation score for watchlist entries: replace raw `threshold_crossed` count with a tier-weighted score. **Effort: Medium (methodology redesign + cron update).**

---

*Audit conducted against: live pages as of 1 April 2026 at ~17:25 CEST; JSON confirmed from `https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json` (48,408 bytes, schema v2.0, Issue 3). Prior audit findings on persistent.html 404 confirmed resolved.*

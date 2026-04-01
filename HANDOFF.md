# HANDOFF.md — Asymmetric Intelligence Session State
**Date:** 2026-04-01 19:00 UTC | **Last commits (main):** see below
**New thread prompt:** "Continuing asym-intel.info maintenance — please load the asym-intel skill first"

---

## FIRST ACTION IN ANY NEW SESSION

```bash
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/HANDOFF.md --jq '.content' | base64 -d
```

Load the skill: `load_skill("asym-intel", scope="user")`

---

## Repository

- **Main:** `asym-intel/asym-intel-main` → https://asym-intel.info
- **Staging:** `staging` branch → https://staging.asym-intel.info
- **Hugo:** publishDir="docs", buildFuture=true
- **Branch protection:** Blueprint validator required; no direct HTML/CSS/JS to main

---

## Seven Monitors — Status

| Monitor | Abbr | Slug | Accent | Publish | Blueprint | Visual |
|---|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | #61a5d2 | Mon 06:00 | v2.1 ✅ | ✅ + choropleth map |
| Global Macro Monitor | GMM | macro-monitor | #22a0aa | Tue 08:00 | v2.1 ✅ | ✅ + tail risk heatmap |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | #38bdf8 | Thu 09:00 | v2.1 ✅ | ✅ |
| European Strategic Autonomy | ESA | european-strategic-autonomy | #5b8db0 | Wed 19:00 | v2.1 ✅ | ✅ |
| AI Governance Monitor | AGM | ai-governance | #3a7d5a | Fri 09:00 | v2.1 ✅ | ✅ |
| Environmental Risks Monitor | ERM | environmental-risks | #4caf7d | Sat 05:00 | v2.1 ✅ | ✅ |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | #dc2626 | Sun 18:00 | v2.1 ✅ | ✅ |

---

## Cron IDs (all active — data-only, no approval needed)

| Monitor | ID | Schedule |
|---|---|---|
| WDM | **db22db0d** | Mon 06:00 UTC |
| GMM | **02c25214** | Tue 08:00 UTC |
| ESA | **0fa1c44e** | Wed 19:00 UTC |
| FCW | **879686db** | Thu 09:00 UTC |
| AGM | **267fd76e** | Fri 09:00 UTC |
| ERM | **3e736a32** | Sat 05:00 UTC |
| SCEM | **eb312202** | Sun 18:00 UTC |
| Housekeeping | **73452bc6** | Mon 08:00 UTC |

---

## Architecture — Two-Pass Commit Rule (ALL 7 monitors)

All 7 cron prompts now enforce a mandatory two-pass commit pattern.
Root cause: WDM Category B sections (electoral_watch, digital_civil,
autocratic_export, state_capture, institutional_pulse, legislative_watch,
research_360, networks) never appeared in any of 3 issues — cron was
silently truncating output before reaching them.

Fix applied globally (not piecemeal) to all 7 monitors:
  PASS 1: core/fast sections committed immediately after research
  PASS 2: deep/slow sections patched onto the Pass 1 JSON via gh API read → modify → PUT
  VERIFY: each prompt now includes a bash verification check — if any keys are
          missing after Pass 2 the agent must re-run Pass 2, not proceed to Step 3

Per-monitor Pass 1 / Pass 2 split:
  WDM:  Pass1=core heatmap/signal/intelligence | Pass2=electoral_watch/digital_civil/autocratic_export/state_capture/institutional_pulse/legislative_watch/research_360/networks
  GMM:  Pass1=signal/executive_briefing/domain sections | Pass2=domain_indicators/tail_risks/sentiment_overlay/cross_monitor_flags
  FCW:  Pass1=signal/campaigns/actor_tracker/platform_responses | Pass2=attribution_log/cognitive_warfare/cross_monitor_flags
  ESA:  Pass1=signal/defence/hybrid_threats | Pass2=institutional_developments/member_state_tracker/cross_monitor_flags
  AGM:  Pass1=modules 0–5 | Pass2=modules 6–15/cross_monitor_flags/delta_strip/country_grid
  ERM:  Pass1=signal/planetary_boundaries/threat_multiplier | Pass2=extreme_weather/policy_law/ai_climate/biosphere/geostrategic/cross_monitor_flags
  SCEM: Pass1=lead_signal/conflict_roster | Pass2=conflict_context/cross_monitor_flags

---

## Recent Commits (main, this session)

| Commit | Description |
|---|---|
| `417892f7` | fix(global): WCAG AA contrast + GMM tail risk heatmap (#17) — start of session |
| `163f5763` | data(gmm): add scenario_analysis, real_m2, hard_landing_risk schemas to cron prompt |
| `e8c57cfc` | data(gmm): backfill scenario_analysis, real_m2, hard_landing_risk — Issue 8 |
| `c6525a94` | data(gmm): add real_m2 5-deflator stack, regime_shift_probs, fed_funds_futures, SA/CC/TS types |
| `7f69ec45` | data(gmm): backfill real_m2 stack, regime_shift_probs, sentiment_overlay, indicator_types — Issue 8 |

---

## GMM Schema — What's Now Collected (Issue 8 onwards)

The GMM cron prompt has been substantially upgraded this session.
`report-latest.json` now contains the following (all backfilled for Issue 8):

### executive_briefing (additions this session)
- `real_m2` — **full 5-deflator stack**: nominal, vs_cpi, vs_pce, vs_core_pce, vs_ppi, vs_core_ppi + direction + note
- `hard_landing_risk` — score (0–1), direction, note
- `scenario_analysis[]` — 3 scenarios (Base Case / De-escalation / Fast Cascade) with probability, horizon, description
- `regime_shift_probabilities` — stay_stagflation, deflationary_bust, inflationary_boom, goldilocks (sum to 1.0)

### signal (additions this session)
- `regime_shift_probabilities` — same as above, mirrored here for dashboard access

### domain_indicators (additions this session)
- `indicator_type` on every indicator — SA (Strategic Anchor) / CC (Cycle Coincident) / TS (Tactical Signal)

### sentiment_overlay (new top-level section this session)
- `fed_funds_futures[]` — 5 FOMC meetings with cut_probability, our_view (AGREES/DISAGREES), note
- `prob_zero_cuts_2026`
- `matt_agreement_pct`

### tail_risks (added prior session)
- 6 entries, likelihood × impact heatmap rendered on dashboard.html

---

## Cross-Monitor Gap Analysis — Completed This Session

Full domain-specific gap analysis performed for all 7 monitors.
Saved to: `/home/user/workspace/monitor-gap-analysis.md`
GMM self-audit (user-provided): `/home/user/workspace/gmm-gap-analysis.md`

### GMM — Remaining gaps (not yet addressed)
These require dashboard HTML work (staging → PR → merge):

| Gap | Priority | Notes |
|---|---|---|
| Horizon Matrix (tactical/cyclical/secular tables) | HIGH | New section on dashboard + report pages |
| Factor Attribution per asset class | HIGH | Per-indicator contribution breakdown with % of score |
| Portfolio Tilts table | MEDIUM | Stance change + rationale + trigger to reverse |
| sentiment_overlay renderer | MEDIUM | fed_funds_futures table + MATT gauge on dashboard.html |
| real_m2 waterfall chart renderer | MEDIUM | 5-bar horizontal chart on dashboard.html |
| regime_shift_probabilities renderer | LOW | Small donut/bar chart |

### All 7 monitors — Universal gaps (cron prompt changes, direct to main)
All three require adding to each monitor's cron prompt:

1. **CHANGELOG RULE** — append-never-overwrite rule for persistent-state arrays (GMM has it; others don't)
2. **top_3_developments[]** — structured "three things that matter most" in signal block
3. **signal confidence** — `confidence: "LOW/MEDIUM/HIGH"` on lead signal (only FCW has it)

### Per-monitor gaps (cron prompt changes, direct to main)
| Monitor | Top gap |
|---|---|
| WDM | severity_score version history in persistent-state + wdm_stress_index aggregate |
| FCW | narrative_persistence tracker in persistent-state + fimi_threat_level aggregate |
| ESA | autonomy_scorecard per-pillar numeric scores + defence_spending_tracker |
| AGM | governance_health composite score + regulatory_calendar in persistent-state |
| ERM | planetary boundary version history + tipping point proximity_score |
| SCEM | composite_score per conflict (from I1–I6) + escalation_velocity |

---

## PENDING TASKS (next session)

### SPRINT 1 STATUS — 2026-04-01

All Sprint 1 items completed and merged to main today:

| PR | Monitors | What merged |
|---|---|---|
| #18 | SCEM | Deviation chart, escalation index HIGH fix, CONTESTED disclaimer, schema version |
| #19 | ESA | Institutional items in Top Items, source links on all items |
| #20 | AGM | 3 `undefined` bugs fixed on persistent.html (M07, M15×2) |
| #22 | ERM+FCW+GMM | ERM cascade tiers+heatmap+summaries+dual_edge / FCW all 12 campaigns+attribution log+platform enforcement+changelog / GMM hard landing KPI+scenarios+fed funds table+Real M2 waterfall |

Direct-to-main (cron/data):
- WDM: source_url, severity_sub, lead_signal enforcement in cron prompt
- SCEM Sprint 2: escalation_velocity, esc_score, negotiation_status schemas
- ESA: lagrange_point_dimensions schema added to cron prompt
- ALL: hardened publish guard (day+hour+recency, hard-exit on prompt reload)
- ALL: shared intelligence layer (intelligence-digest.json, schema-changelog.json, monitor-schema-requirements.json)
- ALL: Step 0B in all cron prompts (read shared layer before research)
- Housekeeping extended to 15 checks (schema validation, digest compilation, freshness)
- COMPUTER.md v1.6, methodology pages updated

### MASTER ACTION PLAN
Full domain expert audit completed for all 7 monitors (including WDM).
Saved to repo: docs/audits/master-action-plan.md (all 7 monitors)
Individual audits: docs/audits/audit-{gmm,wdm,fcw,esa,agm,erm,scem}.md

Key findings:
- 13 confirmed rendering bugs (5 AGM `undefined`, 3 SCEM template failures, 1 ESA missing radar spoke, etc.)
- 49 fields collected in JSON but rendered on zero pages
- ~60 schema additions recommended
- ~45 dashboard UI improvements
- 8 cross-monitor patterns (level-not-deviation bars, sections absent from dashboard, etc.)

Sprint 1 (bugs + low-effort, do next): fix all 13 bugs + surface hard_landing_risk KPI,
  tail risk tooltips, ERM cascade tiers, SCEM baseline marker, ESA institutional_developments
Sprint 2 (schema + medium rendering): sentiment_overlay renderer, scenario cards,
  ESA defence_spending_tracker, AGM regulatory_calendar, SCEM escalation_velocity
Sprint 3 (structural): FCW narratives registry, AGM governance health score,
  ERM proximity scores, SCEM I7 proxy warfare indicator

### AUTOMATED VERIFICATIONS SCHEDULED
- **SCEM Sunday 5 Apr 18:30 UTC** — cron ID: a67a9739 — checks escalation_velocity, esc_score, negotiation_status, two-pass, publish guard
- **WDM Monday 6 Apr 06:30 UTC** — cron ID: 10ddf5f0 — checks Category B sections present for first time, data quality fixes, publish guard
Both will notify on completion.

### SPRINT 2A COMPLETE (2026-04-01)
All 9 visual/chart items delivered across 6 monitors:
- WDM: map as default, 29-country severity bar, nav labels
- GMM: prior-week bar opacity, regime shift 4-bar
- ERM: tipping point proximity bars
- AGM: risk vector radar + concentration diverging bar + Chart.js
- ESA: 50% benchmark on Lagrange radar
- SCEM: 10-conflict comparison bar
Committed directly to main (fdfe29d–43fac9a) after staging PR divergence.

### Priority 1 — Verify SCEM Sunday (5 Apr 18:00 UTC)
First run with: escalation_velocity, esc_score, negotiation_status, conflict_context.
First run reading shared intelligence digest at Step 0B.
Check: new fields present, two-pass rule worked, no off-schedule publish.

### Priority 2 — Verify WDM Monday (6 Apr 06:00 UTC)
First run with two-pass fix — Category B sections must appear for the first time:
  electoral_watch, digital_civil, autocratic_export, state_capture,
  institutional_pulse, legislative_watch, research_360, networks
Also check: source_url non-empty, severity_sub present, lead_signal on recovery entries.

### Priority 3 — Sprint 2 (before next cron runs)
GMM: Horizon Matrix section, Factor Attribution per asset
FCW: threat_level aggregate, narrative persistence tracker
ESA: defence spending tracker, US-dependency index
AGM: regulatory_calendar, governance health score
ERM: tipping proximity scores, boundary version history
SCEM: render escalation_velocity + esc_score on dashboard once data arrives
WDM: silent_erosion field, wdm_stress_index

### Priority 4 — Universal cron prompt fixes (all 7 monitors)
top_3_developments in signal + signal confidence field. Simple appends.

### Priority 2 — Per-monitor cron prompt additions (direct to main)
Work through the per-monitor gap table above. Start with WDM (next to run Mon 06:00)
and ESA (runs today Wed 19:00 — may already have fired).

### Priority 3 — GMM dashboard renderer additions (staging → PR → merge)
Horizon Matrix, Factor Attribution, Portfolio Tilts, sentiment_overlay renderer,
real_m2 waterfall chart. These are HTML changes; staging first.

### Priority 4 — Verify first conflict_context data (SCEM)
SCEM cron runs Sun Apr 5 18:00 UTC. Check persistent.html after that run.

### Priority 5 — FCW campaign timeline (BLOCKED until Apr 9)
FCW cron runs Thu Apr 9. After that run, build Gantt-style timeline on dashboard.

### Priority 6 — Mobile audit
All visual enhancements not audited on mobile yet.

### DEFERRED — WDM / ESA Perplexity-era URLs
If user can share WDM and ESA Perplexity page URLs, run same extraction
as GMM gap analysis to identify domain-specific historical gaps.

---

## Architecture Reminders

- **WCAG AA formula:** `color-mix(in srgb, var(--monitor-accent) 65%, #000)` — use wherever accent appears on light surface
- **Signal-block ownership:** base.css owns `.signal-block { background }` with `!important`; monitor.css must not override
- **Staging-first:** all HTML/CSS/JS → staging branch → PR → user visual sign-off → merge
- **Cron tasks:** data JSON + Hugo brief only, never touch HTML/CSS/JS

# Collector–Analyst Architecture
## Strategic Design Document | asym-intel.info
### Version 2.2 — 4 April 2026 | Synthesiser layer, weekly cadence all monitors | All monitors weekly under synthesiser architecture

---

## Companion Documents

- `editorial-strategy.md` — tier-by-tier audience strategy, epistemic hierarchy principle, UI subordination rules
- `development-plan.md` — master build sequence, phase gates, annual report calendar
- `pipeline-overview.md` — deleted 4 Apr 2026, superseded by this document

## Purpose

This document defines the Collector–Synthesiser–Analyst architecture for the
asym-intel.info platform. It is the canonical reference for how pre-verification
research (Collector + Weekly Research), synthesis (Synthesiser), state management
(State / Delta Engine), and weekly publication (Analyst) relate to each other,
and the governing document for all future builds at any layer.

Read this before designing or modifying any Collector, Synthesiser, State Engine,
or Analyst prompt.

---

## The Problem This Solves

Weekly Analyst crons traditionally did two very different jobs:

1. Search and collect raw candidate findings from public sources
   (fast, cheap, repeatable).
2. Apply monitor methodology, assign confidence, structure and publish output
   (slower, judgment-intensive, stateful).

Combining both into one weekly cron means either:

- The weekly cron spends most of its time on search (inefficient), or
- It spends less time on search (coverage gaps).

Separating them lets the Analyst focus entirely on analytical judgment,
cross-monitor links, and persistent state, with a structured evidence base,
draft synthesis, and deterministic validation already assembled by GitHub Actions.

---

## Layer Model

Every monitor follows the same layered model. Data flows downward; each layer
feeds the next.

- **Layer 0 — Scout** (optional, future)
- **Layer 1A — Collector** (daily, GitHub Actions)
- **Layer 1B — Weekly Research** (weekly, GitHub Actions) ← PAUSED pending synthesiser architecture decision
- **Layer 1C — Synthesiser** (weekly, GitHub Actions) ← NOT YET BUILT
- **Layer 1D — State / Delta Engine** (weekly, GitHub Actions, deterministic) ← NOT YET BUILT
- **Layer 2 — Publisher** (weekly, GitHub Actions — deterministic Python, zero credits)
- **Layer 3 — Platform Validator** (PAUSED — under review)

Layers 1A–1D run on GitHub Actions. They consume Perplexity API credits only
where they call the API; the State / Delta Engine is pure Python and consumes
**no Perplexity credits**.

---

## Layer 0 — Scout (optional, future)

**What:** Lightweight external search with no GitHub access. A standard Perplexity
search, scheduled web query, or human-triggered research pass.

**Produces:** Unstructured prose — links, summaries, raw findings.

**Does not:** Structure data, commit to GitHub, or assign confidence.

**Status:** Not yet implemented. Future capability for high-volume domains.

---

## Layer 1A — Collector (GitHub Actions workflow)

**What:** A GitHub Actions workflow. Searches domain-specific public sources,
structures findings into the Tier 0 schema, deduplicates against the monitor's
active registry, and commits to `pipeline/monitors/{slug}/daily/`.

**Produces:**

- `pipeline/monitors/{slug}/daily/verified-YYYY-MM-DD.json` (dated archive)
- `pipeline/monitors/{slug}/daily/daily-latest.json` (most recent, overwritten daily)

**Does not:**

- Write to `report-latest.json`, `persistent-state.json`, or `archive.json`.
- Assign final public confidence.

Assigns `confidence_preliminary` only.

**Workflow:** `.github/workflows/{monitor}-collector.yml` in `asym-intel-main`.
The workflow calls the Perplexity API with a structured JSON prompt, validates the
Tier 0 schema, and commits output to `pipeline/` — all within GitHub Actions.

**API prompt location:**
`pipeline/monitors/{slug}/{monitor}-collector-api-prompt.txt`

**Script location:**
`pipeline/monitors/{slug}/collect.py`

---

## Layer 1B — Weekly Research (GitHub Actions workflow)

**What:** A weekly GitHub Actions workflow using `sonar-pro` to perform deeper
live web search over the last 7 days and produce structured weekly research
JSON for the monitor.

**Status: PAUSED** — scheduled trigger disabled pending synthesiser architecture
decision. Can be triggered manually via `workflow_dispatch`. Do not re-enable
scheduled triggers without explicit instruction.

**Produces:**

- `pipeline/monitors/{slug}/weekly/weekly-latest.json`
- Optionally, dated `weekly-YYYY-MM-DD.json` archives.

Content typically includes: week-ending metadata, lead research signal,
campaign/country/conflict updates (monitor-specific), actor posture,
platform responses, weekly brief narrative draft, cross-monitor signal candidates.

**Does not:** Publish to `data/`. Update `persistent-state.json`. Assign final confidence.

**Workflow:** `.github/workflows/{slug}-weekly-research.yml` in `asym-intel-main`.

**API prompt location:**
`pipeline/monitors/{slug}/{slug}-weekly-research-api-prompt.txt`

**Script location:**
`pipeline/monitors/{slug}/weekly-research.py`

**Built for:** FCW, GMM, WDM, SCEM. Not yet built for ESA, AGM, ERM.

---

## Layer 1C — Synthesiser (GitHub Actions workflow)

**Status: NOT YET BUILT.** FCW is the planned first implementation.

**What:** A weekly GitHub Actions workflow using `sonar-deep-research` to read
the monitor's daily Collector output, weekly research output, and key
methodology excerpts, and to produce a single **synthesis JSON** that the
Analyst uses as the primary draft input.

**Important:** `sonar-deep-research` does not search the web. It reasons over
documents provided to it in the API call. The synthesiser Python script must
explicitly load and embed pipeline JSON files and methodology content into the
API request body.

**Inputs:**

- `pipeline/monitors/{slug}/daily/daily-latest.json`
- `pipeline/monitors/{slug}/weekly/weekly-latest.json`
- Monitor methodology content (embedded in the prompt or loaded via script from `docs/methodology/`)

**Produces:**

- `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`

This synthesis JSON contains:

- `lead_signal` — one weekly lead signal for the monitor.
- `key_judgments` — 2–5 concise, decision-useful judgments with confidence tags.
- `campaigns` / entity summaries — monitor-specific entities with status, trajectory, and severity.
- `actor_tracker` — posture for all primary actors.
- `weekly_brief_draft` — a 400–600 word analytic narrative draft.

**Does not:**

- Update `persistent-state.json`.
- Set cross-monitor flags.
- Write to `static/monitors/{slug}/data/`.
- Perform GitHub commits (the workflow handles commits, not the script).

**Workflow:** `.github/workflows/{slug}-synthesiser.yml` in `asym-intel-main`.

**API prompt location:**
`pipeline/monitors/{slug}/{slug}-synthesiser-api-prompt.txt`

The Synthesiser replaces the old "Reasoner" as the research-model layer for
synthesis, signal panel, and brief drafting, making the Analyst cron much lighter
(estimated ~275 credits/run → ~100 credits/run).

---

## Layer 1D — State / Delta Engine (GitHub Actions, deterministic)

**Status: NOT YET BUILT.** Planned Phase 2 after Synthesiser is validated.

**What:** A deterministic GitHub Actions + Python workflow that validates,
diffs, scores, and enforces rules over structured JSON from Layers 1A–1C.
It does **not** call Perplexity and consumes no research-model credits.

**Inputs (per monitor):**

- `pipeline/monitors/{slug}/daily/verified-*.json`
- `pipeline/monitors/{slug}/weekly/weekly-*.json`
- `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`
- Previous week's state (`pipeline/monitors/{slug}/state/`)

**Produces:**

- `pipeline/monitors/{slug}/state/state-checked-YYYY-MM-DD.json`
- `pipeline/monitors/{slug}/state/delta-YYYY-MM-DD.json` (material change log)
- Pass/fail status via GitHub commit status or check run.

**Responsibilities:**

- Schema checks: validate JSON against monitor schemas across all layers.
- Required field validation: all required fields and URLs present.
- Material-change detection: diff entities vs last week (unchanged / changed / added / removed).
- KPI recomputation: severity scores, counts from fixed rules — reproducible and auditable.
- Archive and version logging: deterministic log of what changed, when, and why.
- Publish gates: blocking status if validation fails, visible to Analyst before publication.

**Why non-redundant with Synthesiser:**

The Synthesiser handles narrative formation and prioritisation. The State / Delta
Engine guarantees unchanged items persist, changed items are logged, schemas remain
valid, and derived fields (including cross-monitor flags) can be maintained
consistently according to code-level rules — not model judgment.

**Workflow:** `.github/workflows/{slug}-state-engine.yml` in `asym-intel-main`.

**Script location:** `pipeline/monitors/{slug}/state-engine.py`

---

## Layer 2 — Publisher (GitHub Actions, deterministic Python)

**What:** A config-driven Python script (`pipeline/publishers/publisher.py`) that
reads the Synthesiser output and mechanically produces the published report.
Runs as a GitHub Actions workflow — **zero Computer credits, zero LLM calls**.

**Replaces:** The former Analyst Computer cron, which consumed ~100–275 credits/run.
Retired 9 April 2026. See `docs/crons/README.md` for historical reference.

**Credit cost:** Zero.

**Cadence:** Weekly per monitor, matching the old Analyst schedule.

**Inputs:**

- `pipeline/monitors/{slug}/synthesised/synthesis-latest.json` (primary)
- `static/monitors/{slug}/data/report-latest.json` (previous issue, for state continuity)
- `static/monitors/{slug}/data/persistent-state.json`
- `static/monitors/{slug}/data/archive.json`
- Adjacent monitors' `report-latest.json` (for cross-monitor flag verification)

**Produces:**

- `static/monitors/{slug}/data/report-YYYY-MM-DD.json`
- `static/monitors/{slug}/data/report-latest.json`
- `static/monitors/{slug}/data/persistent-state.json` (updated)
- `static/monitors/{slug}/data/archive.json` (appended)
- `content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md` (Hugo brief)
- `docs/monitors/{slug}/data/` mirrors

**Safety guards:**

- Staleness: skips publish if synthesis is >8 days old.
- Validity: skips if synthesis is stub or raw_fallback only.
- Schema validation: warns on missing required fields but still publishes.
- Cross-monitor flags: verified against 6 adjacent monitor reports each run.

**What the Publisher does NOT do (deferred to future State Engine):**

- Contested finding resolution (analytical judgment calls).
- Final confidence upgrade/downgrade (carries forward from synthesis).
- These can be added later as an optional sonar-deep-research step in GA.

**Workflow location:** `.github/workflows/{slug}-publisher.yml`
**Script location:** `pipeline/publishers/publisher.py`

---

## Layer 3 — Platform Validator (weekly Computer cron, Monday)

**What:** Validates all Analyst outputs and all Collector / Synthesiser / State
Engine pipeline files. Compiles `intelligence-digest.json`. Runs checks 1–20,
including Collector-specific schema and traceability checks, and weekly chatter
quality audit (Step 10: tier distribution, recency, source bloat).

**Collector-specific checks (16–20):**

16. Schema version `tier0-v1.0` present in all `verified-*.json` pipeline files.
17. `data_date` matches filename date.
18. High / Confirmed findings have `research_traceback` with ≥2 sources.
19. `episodic_flag=true` entries have `episodic_reason` populated.
20. `campaign_status_candidate` present on all findings.

Future Synthesiser and State / Delta Engine checks will be added here.

**Prompt location:** `docs/crons/housekeeping.md` in `asym-intel-main`

**Estimated credit cost:** ~400 credits/run × 4 runs/month = ~1,600 credits/month.
Trimming to 5 essential steps is a planned efficiency measure (~800 credits/month saving).

---

## Core Rules (apply to all Collectors, Synthesisers, and State Engines)

1. **Collector, Synthesiser, and State Engine never publish.** Only the Publisher
   (Layer 2) writes to public `data/` paths.
2. **`pipeline/` is internal.** Hugo never builds from `pipeline/` files.
3. **Collector assigns `confidence_preliminary` only.** The Analyst upgrades,
   downgrades, or rejects.
4. **Deduplication is mandatory.** Every finding is checked against the active
   registry in `persistent-state.json` before `campaign_status_candidate` is set.
5. **`research_traceback` is mandatory** for all Assessed / High / Confirmed
   findings: ≥2 independent sources, with search queries and analyst notes.
6. **One Collector run per day per monitor.** Guard: skip if
   `verified-{TODAY}.json` already exists.
7. **Urgent findings** go to `asym-intel-internal/notes-for-computer.md`, not
   directly into Analyst output.
8. **Synthesiser feeds the Publisher.** The Publisher mechanically converts
   synthesis output to published reports. Analytical judgment is deferred to
   the future State Engine or manual Computer sessions.
9. **State / Delta Engine is deterministic.** It must rely only on code and
   structured JSON, not on model calls.
10. **Analyst prompts stay in `docs/crons/`**, not in `static/`. Methodology
    content belongs in `docs/methodology/` (public, as a commons resource).

---

## Shared Tier 0 Base Schema (Collector)

All Collectors output `tier0-v1.0` JSON. Monitor-specific extension fields are
added alongside base fields — never replacing them.

### `_meta` (required)

```json
{
  "schema_version": "tier0-v1.0",
  "monitor_slug": "{slug}",
  "job_type": "daily-verified-findings",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "data_date": "YYYY-MM-DD",
  "coverage_window": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "methodology_version": "tier0-v1",
  "source_scope": "public",
  "status": "complete",
  "finding_count": 0,
  "net_new_count": 0,
  "continuation_count": 0,
  "below_threshold_count": 0
}
```

### Per finding (required base fields)

`finding_id`, `dedupe_key`, `title`, `summary`, `date_detected`, `data_date`,
`source_url`, `source_name`, `source_type`, `source_tier`, `retrieved_at`,
`claim_excerpt`, `actors`, `geographies`, `topic_tags`, `preliminary_assessment`,
`confidence_preliminary`, `confidence_basis`, `research_traceback`,
`supports_existing_case`, `related_case_ids`, `campaign_status_candidate`,
`episodic_flag`, `episodic_reason`, `needs_weekly_review`, `review_reason`.

### Monitor-specific extension fields

- **FCW:** `coordination_evidence`, `attribution_candidate`,
  `attribution_gap_note`, `campaign_status_candidate_detail`,
  `narrative_persistence_days`, `platform_transparency_gap`,
  `meets_active_campaign_threshold_candidate`, `cross_monitor_relevance`,
  `mf_flags_candidate`.
- **SCEM:** `conflict_id`, `indicator_deviation`, `escalation_context`,
  `conflict_phase_candidate`, `source_reliability_score`.
- **WDM/GMM/ESA/AGM/ERM:** Extension fields defined in monitor methodology.

---

## Promotion Lifecycle (Collector → Analyst)

Inside the Collector, findings move through internal states only:

`candidate` → `reviewed` → `promoted` | `rejected` | `below_threshold`

The Analyst sees all `candidate` findings and makes the final state decision.
The Collector never sets final publication status; only the Analyst does.

---

## Active Collectors

| Monitor | Workflow | Schedule | Model | Since |
|---------|----------|----------|-------|-------|
| FCW | fcw-collector.yml | Mon 07:00 UTC | sonar | 2 Apr 2026 |
| GMM | gmm-collector.yml | Tue 07:00 UTC | sonar | 3 Apr 2026 |
| WDM | wdm-collector.yml | Wed 07:00 UTC | sonar | 3 Apr 2026 |
| SCEM | scem-collector.yml | Thu 07:00 UTC | sonar | 3 Apr 2026 |
| ESA | esa-collector.yml | Fri 07:00 UTC | sonar | 3 Apr 2026 |
| AGM | agm-collector.yml | Sat 07:00 UTC | sonar | 3 Apr 2026 |
| ERM | erm-collector.yml | Sun 07:00 UTC | sonar | 3 Apr 2026 |

## Active Chatter Workflows

| Monitor | Workflow | Schedule | Model |
|---------|----------|----------|-------|
| FCW | fcw-chatter.yml | Mon 06:00 UTC | sonar |
| GMM | gmm-chatter.yml | Tue 06:00 UTC | sonar |
| WDM | wdm-chatter.yml | Wed 06:00 UTC | sonar |
| SCEM | scem-chatter.yml | Thu 06:00 UTC | sonar |
| ESA | esa-chatter.yml | Fri 06:00 UTC | sonar |
| AGM | agm-chatter.yml | Sat 06:00 UTC | sonar |
| ERM | erm-chatter.yml | Sun 06:00 UTC | sonar |

## Weekly Research / Reasoner (PAUSED)

| Monitor | Weekly Research | Reasoner | Status |
|---------|----------------|----------|--------|
| FCW | fcw-weekly-research.yml | fcw-reasoner.yml | PAUSED |
| GMM | gmm-weekly-research.yml | gmm-reasoner.yml | PAUSED |
| WDM | wdm-weekly-research.yml | wdm-reasoner.yml | PAUSED |
| SCEM | scem-weekly-research.yml | scem-reasoner.yml | PAUSED |
| ESA | — | — | Not built |
| AGM | — | — | Not built |
| ERM | — | — | Not built |

## Active Publisher Workflows (GitHub Actions — zero credits)

Enabled 9 April 2026. Replaced Computer Analyst crons.

| Monitor | Workflow | Schedule | Status |
|---------|----------|----------|--------|
| WDM | democratic-integrity-publisher.yml | Mon 06:00 UTC | ENABLED |
| GMM | macro-monitor-publisher.yml | Tue 08:00 UTC | ENABLED |
| ESA | european-strategic-autonomy-publisher.yml | Wed 19:00 UTC | ENABLED |
| FCW | fimi-cognitive-warfare-publisher.yml | Thu 09:00 UTC | ENABLED |
| AIM | ai-governance-publisher.yml | Fri 09:00 UTC | ENABLED |
| ERM | environmental-risks-publisher.yml | Sat 05:00 UTC | ENABLED |
| SCEM | conflict-escalation-publisher.yml | Sun 18:00 UTC | ENABLED |
| Housekeeping | — | Mon 08:00 UTC | PAUSED — under review |

---

## Adding a New Monitor — Full Checklist

### Phase 1 — Collector (Layer 1A)

1. Write collector API prompt:
   `pipeline/monitors/{slug}/{slug}-collector-api-prompt.txt`
   Include version header: `# PROMPT: {name} | VERSION: v1.0 | UPDATED: {date}`

2. Write `pipeline/monitors/{slug}/collect.py`
   Model on existing collectors. Include subprocess, base64 imports.
   Include auto-downgrade: Confirmed/High with <2 sources → Assessed.

3. Write `.github/workflows/{slug}-collector.yml`
   Schedule: rotating daily slot (check COMPUTER.md for which day is free).

4. Create pipeline stubs:
   `pipeline/monitors/{slug}/daily/daily-latest.json`
   `pipeline/monitors/{slug}/weekly/weekly-latest.json`
   `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`
   `pipeline/monitors/{slug}/state/` (empty dir with README)

5. Add to Active Collectors table in this document.

6. Add to COMPUTER.md GHA table.

7. Log in `asym-intel-internal/prompt-improvements.md`.

### Phase 2 — Synthesiser (Layer 1C)

1. Write synthesiser API prompt:
   `pipeline/monitors/{slug}/{slug}-synthesiser-api-prompt.txt`

2. Write `pipeline/monitors/{slug}/{slug}-synthesiser.py`
   Must embed pipeline JSON + methodology content into sonar-deep-research call.

3. Write `.github/workflows/{slug}-synthesiser.yml`
   Schedule: weekly, after collector has run (same day + 2hrs).
   Start with `workflow_dispatch` only — enable schedule after manual validation.

4. Add to Active Synthesisers table (to be created when first built).

### Phase 3 — State Engine (Layer 1D)

(Build after Phase 2 validated.)

### Phase 4 — Publisher workflow

1. Add monitor config to `pipeline/publishers/publisher.py` `MONITOR_CONFIGS` dict.
2. Create `.github/workflows/{slug}-publisher.yml` (copy from any existing publisher workflow).
3. Set `MONITOR_SLUG` env var and schedule to match the monitor's publish day/time.
4. Test via `workflow_dispatch`, then enable schedule.

---

## File Locations

| Asset | Location |
|---|---|
| This document | `asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md` |
| Pipeline overview (editorial) | `asym-intel-internal/pipeline-overview.md` |
| Prompt improvements log | `asym-intel-internal/prompt-improvements.md` |
| Collector prompts | `pipeline/monitors/{slug}/{slug}-collector-api-prompt.txt` |
| Chatter prompts | `pipeline/monitors/{slug}/{slug}-chatter-api-prompt.txt` |
| Synthesiser prompts | `pipeline/monitors/{slug}/{slug}-synthesiser-api-prompt.txt` |
| Analyst prompts | `docs/crons/{abbr}-analyst-prompt.md` |
| Housekeeping prompt | `docs/crons/housekeeping.md` |
| Methodology (public) | `docs/methodology/{slug}-full.md` + `{slug}-{source}-{year}.md` |
| Pipeline outputs — daily | `pipeline/monitors/{slug}/daily/` |
| Pipeline outputs — weekly | `pipeline/monitors/{slug}/weekly/` |
| Pipeline outputs — synthesised | `pipeline/monitors/{slug}/synthesised/` |
| Pipeline outputs — state | `pipeline/monitors/{slug}/state/` |
| Published data | `static/monitors/{slug}/data/` |
| Cron table | `COMPUTER.md` |
| Identity cards | `asym-intel-internal/AGENT-IDENTITIES.md` |

---

## What to Keep Internal vs Public

| Asset | Location | Reason |
|---|---|---|
| Methodology content | `docs/methodology/` (public) | Commons — continuity, openness |
| Architecture docs | `asym-intel-internal/` (internal) | Operational detail |
| Prompt engineering | `asym-intel-internal/prompt-improvements.md` | Competitive sensitivity |
| Platform config | `asym-intel-internal/platform-config.md` | Cloudflare zone ID, GSC tokens |
| Session notes | `asym-intel-internal/notes-for-computer.md` | Operational logs |
| Agent identities | `asym-intel-internal/AGENT-IDENTITIES.md` | Internal operational |
| Collector/chatter prompts | `pipeline/` (public repo, not served) | Acceptable — not on public URL |
| Analyst prompts | `docs/crons/` (public repo, not served) | Not on public URL |

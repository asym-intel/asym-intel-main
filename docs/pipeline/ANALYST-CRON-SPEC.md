# ANALYST-CRON-SPEC.md

## Platform-First Fix Rule

**Before fixing any bug, gap, or prompt issue — always ask:**

> "Is this specific to one monitor/file, or is it likely present across multiple monitors, workflows, scripts, or pages?"

If the answer is "likely platform-wide" or "I'm not sure":
1. **Audit first** — check all affected monitors/files before touching anything
2. **Fix the spec** — update ANALYST-CRON-SPEC.md or SYNTHESISER-SPEC.md to reflect the correct behaviour
3. **Apply platform-wide** — fix all affected files in one pass, not one at a time as they surface

**Never:**
- Fix one monitor's prompt and leave the same gap in the other 6
- Patch a workflow file without checking if the same pattern exists in all 14 workflow files
- Update a Python script for one monitor without checking the equivalent scripts for all 7

**The cost of reactive patching is high:** each gap found in one monitor that later turns out to affect all 7 means 6 additional session tool calls, 6 additional commits, and 6 additional opportunities for inconsistency. One properly scoped fix costs less than two reactive ones.

**When a gap IS monitor-specific** (e.g. SCEM deviation calculation, WDM living knowledge fields) — document why it's specific before fixing, so future sessions don't audit unnecessarily.


## Canonical Specification — Analyst Cron Prompts
## Asymmetric Intelligence | asym-intel.info
### Version: 1.0 | Date: 2026-04-07
### Governs: All 7 monitor Analyst cron prompts

---

## Purpose

This document is the single source of truth for every Analyst cron prompt across
all seven monitors. When a gap is found in any Analyst cron:

1. Fix this spec first.
2. Then make every monitor prompt conform to it.

One spec update → one conformance pass across all 7 monitors.
Do not patch individual monitor prompts in isolation.

**Companion spec:** `SYNTHESISER-SPEC.md` — governs synthesiser prompts.

**Governing architecture:** `COLLECTOR-ANALYST-ARCHITECTURE.md` (Version 2.2).

---

## 1. Identity and Schedule

### 1.1 What the Analyst Cron IS

The Analyst cron is a **publication agent**, not a research agent.

Under the synthesiser architecture, the Analyst's role is:
- **Methodology** — apply the monitor's framework to confirm, refine, or reject synthesiser output
- **State** — update persistent-state.json with this week's changes
- **Publication** — assemble schema-compliant final JSON and commit to static/

The Analyst does **not** perform primary web search. The Synthesiser (Layer 1C) and
Collector (Layer 1A) have already assembled the evidence base. The Analyst exercises
judgment over that base.

### 1.2 What the Analyst Reads

Pipeline inputs are read-only. Priority order:

1. **Primary:** `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`
   — synthesiser draft (lead signal, key judgments, entity summaries, weekly brief draft)
2. **Secondary:** `pipeline/monitors/{slug}/reasoner/reasoner-latest.json` (if present — legacy layer)
3. **Tertiary:** `pipeline/monitors/{slug}/daily/daily-latest.json` (Collector output)
4. **Supplemental:** `pipeline/monitors/{slug}/weekly/weekly-latest.json` (if present)
5. **State:** `static/monitors/{slug}/data/persistent-state.json`
6. **Continuity:** `static/monitors/{slug}/data/report-latest.json` (prior week)
7. **Shared:** `static/monitors/shared/intelligence-digest.json` and `schema-changelog.json`
8. **Methodology:** `docs/methodology/{slug}-full.md`
9. **Identity/config:** `asym-intel-internal/notes-for-computer.md` (optional), `docs/AGENT-IDENTITIES.md`

If synthesis-latest.json is absent or `null_signal_week: true` with no data,
fall back to direct synthesis from daily + weekly inputs.

### 1.3 What the Analyst Writes

**Published outputs** (written in Two-Pass Commit sequence — see Section 6):

- `static/monitors/{slug}/data/report-latest.json` — current week's public report
- `static/monitors/{slug}/data/report-YYYY-MM-DD.json` — dated archive copy
- `static/monitors/{slug}/data/persistent-state.json` — living state document
- `static/monitors/{slug}/data/archive.json` — append-only historical record
- `content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md` — Hugo brief markdown

The Analyst never writes to `pipeline/` paths. Those are internal only.

### 1.4 Schedule Pattern

One monitor publishes per day, Monday through Sunday:

| Day | Monitor | Slug | Cron ID | Scheduled UTC |
|-----|---------|------|---------|---------------|
| Mon | WDM | `democratic-integrity` | f7bd54e9 | 06:00 |
| Tue | GMM | `macro-monitor` | c94c4134 | 08:00 |
| Wed | ESA | `european-strategic-autonomy` | 0b39626e | 19:00 |
| Thu | FCW | `fimi-cognitive-warfare` | b17522c3 | 09:00 |
| Fri | AGM | `ai-governance` | 5ac62731 | 09:00 |
| Sat | ERM | `environmental-risks` | ce367026 | 05:00 |
| Sun | SCEM | `conflict-escalation` | 8cdb83c8 | 18:00 |

---

## 2. Required Step Structure

Every Analyst cron prompt must contain these steps in this order.
Steps may have monitor-specific sub-tasks but must not be omitted or reordered.

### Step 0A — COMPUTER.md / Urgent Flags (Optional)

Read `asym-intel-internal/notes-for-computer.md` for urgent flags.
This step is **optional** — if the file is inaccessible, log a note and continue.
Do not abort the run on Step 0A failure.

### Step 0B — Architecture and Shared Layer

Read `docs/COLLECTOR-ANALYST-ARCHITECTURE.md`.
Load:
- `static/monitors/shared/intelligence-digest.json`
- `static/monitors/shared/schema-changelog.json`

Command pattern:
```
gh api repos/asymmetric-intelligence/asym-intel-main/contents/docs/COLLECTOR-ANALYST-ARCHITECTURE.md \
  --jq '.content' | base64 -d
```

### Step 0C — Daily Collector Input

Load `pipeline/monitors/{slug}/daily/daily-latest.json`.

Command pattern:
```
gh api repos/asymmetric-intelligence/asym-intel-main/contents/pipeline/monitors/{slug}/daily/daily-latest.json \
  --jq '.content' | base64 -d
```

Note the `finding_count` and `data_date` from `_meta`. Record for `meta.pipeline_inputs`.

### Step 0D — Weekly Research Input (if available)

Load `pipeline/monitors/{slug}/weekly/weekly-latest.json` if present.
If absent, log a note and continue — this input is optional.

### Step 0S — Synthesiser Ingest (Primary Draft)

Load `pipeline/monitors/{slug}/synthesised/synthesis-latest.json`.

This is the **primary draft**. Treat the synthesiser's lead_signal, key_judgments,
entity summaries, weekly_brief_draft, and cross_monitor_candidates as the starting point.

**lead_signal rule (Gap 5):** Confirm or refine the synthesiser's lead_signal.
Do not independently derive a new lead_signal unless the synthesiser output is null
or `null_signal_week: true`. If the synthesiser lead_signal is factually wrong,
correct it with a note. Do not rewrite it without cause.

Record the synthesiser SHA and date for `meta.pipeline_inputs`.

### Step 0P — Persistent State and Prior Report

Load:
- `static/monitors/{slug}/data/persistent-state.json` — living state document
- `static/monitors/{slug}/data/report-latest.json` — prior week's report for state continuity

Check `report-latest.json` for prior `meta.published` date (needed for Publish Guard).

### Step 1 — Methodology Review

Read `docs/methodology/{slug}-full.md`.

Methodology files are public at `docs/methodology/` in `asym-intel-main`.
Apply the methodology to confirm, refine, or reject every synthesiser judgment.

**AGM only:** Also load and apply `asym-intel-internal/ramparts-prompts/ramparts-methodology-digest.md`.

### Step 2 — Monitor-Specific Signal Assessment

This step is **monitor-specific**. Required sub-tasks per monitor:

**GMM:**
- Confirm final stress regime (not `_preliminary`) using ≥2 indicator domain rule
- Update each indicator domain direction and stress level
- Update central_bank_tracker posture
- Update tariff_tracker — add new measures, note retaliation chains

**WDM:**
- Confirm final health_status per country (remove `_preliminary`)
- Confirm/escalate/resolve backsliding_alerts
- Update electoral_calendar_watch — add/remove entries, update fimi_risk
- Flag any V-Dem LDI delta ≥0.05 for immediate send_notification()
- Populate `severity_sub` on every heatmap entry:
  ```json
  "severity_sub": {
    "institutional": 0.0,
    "electoral": 0.0,
    "civil_society": 0.0,
    "media": 0.0
  }
  ```
  Values 0.0–10.0. Set to 0.0 if not relevant — never omit the key.

**SCEM:**
- Confirm final intensity per theatre (remove `escalation_preliminary`)
- Update ACLED event and fatality counts
- Confirm/add/resolve escalation_indicators
- Flag nuclear threshold crossings immediately to send_notification()
- **Deviation calculation (mandatory — do not skip):**
  For every indicator on every conflict in conflict_roster:
  ```
  deviation = level - baseline
  ```
  - `level`: current assessed value (1–5 scale, assigned this week)
  - `baseline`: established pre-conflict/pre-crisis normal (carry from persistent-state; reset only on structural shift)
  - `deviation`: positive = escalation, negative = de-escalation, 0 = at baseline
  - `band` assignment:
    - deviation ≥ +2 → `RED`
    - deviation = +1 → `AMBER`
    - deviation = 0 → `GREEN`
    - deviation ≤ -1 → `GREEN` (add note)
    - `CONTESTED`: only when the level cannot be assessed at all — requires explicit note
  - **Critical rule:** `deviation = 0` with `band = CONTESTED` is a contradiction.
    If level equals baseline and you have sufficient information, band = `GREEN`.

**FCW:**
- Update campaign_roster (active / emerging / dormant)
- Confirm threat_level per campaign
- Update actor_posture for primary actors
- Confirm/add/resolve platform_response entries

**ESA:**
- Update domain_tracker scores (defence / energy / tech / trade / diplomatic)
- Confirm sovereignty_index direction
- Update member_state_alignment map

**AGM:**
- Update capability_tier per lab (frontier model labs only)
- Check regulatory_milestone_status for each tracked jurisdiction
- Update risk_register entries

**ERM:**
- Update planetary_boundary_status per boundary
- Confirm tipping_trajectory direction
- Update compound_risk_matrix

### Step 3 — Cross-Monitor Flags

Review synthesiser `cross_monitor_candidates`.

**Rule:** Confirm, reject, or add flags. Do not invent new cross-monitor flags
without explicit evidence from this week's pipeline data.

Write final `cross_monitor_flags` for the report. Use these exact slugs:

```
fimi-cognitive-warfare    (FCW)
democratic-integrity      (WDM)
conflict-escalation       (SCEM)
european-strategic-autonomy (ESA)
macro-monitor             (GMM)
ai-governance             (AGM)
environmental-risks       (ERM)
```

Cross-monitor flags must appear in both the originating monitor's output and in
the target monitor's output (to be updated on that monitor's publish day).

### Step 4 — Final Report Assembly

Assemble `report-latest.json`. All required fields specified in Section 3.

**Critical reminder (Gap 4 — weekly_brief):**
`weekly_brief` must be written into `report-latest.json` AND into the Hugo markdown file.
The JSON field is what the monitor's report.html page reads.
If `weekly_brief` is absent from the JSON, the brief will not appear on the monitor page
even if the Hugo file exists. Both outputs are mandatory.

**lead_signal (Gap 5):** Confirm from synthesiser — do not independently derive
unless synthesiser output is null.

### Step 5 — Persistent-State Update and Notifications

Update `static/monitors/{slug}/data/persistent-state.json`.

Carry forward all existing fields. Update only fields with new data this week.

For any newly critical finding or highest-severity status change:
1. Call `send_notification()` immediately — this is the real-time alert
2. Append a durable log entry to `asym-intel-internal/notes-for-computer.md` (optional — skip if inaccessible)

Both are required for critical findings. `send_notification()` is the alert;
`notes-for-computer.md` is the durable record.

**WDM living knowledge sections** must be populated every run (see Section 3.3).

### Step 6 — Publish and Commit

Apply **Publish Guard** (Section 5) before writing any file.
If any guard check fails: EXIT. Log the reason. Do not publish.

Apply **Two-Pass Commit Rule** (Section 6) for all file writes.

Commit message format: `data({abbr}): weekly pipeline — Issue [N] W/E YYYY-MM-DD`

Pull before push: `git pull --rebase origin main && git push origin main`

### Step 7 — AGM Only: Ramparts Publication

After completing Steps 1–6, read:
`asym-intel-internal/ramparts-prompts/ramparts-publisher-cron.md`

Follow Ramparts publication steps as specified in that file.
Ramparts is a separate publication target from the main monitor report.

---

## 3. Required Fields in Every report-latest.json

### 3.1 Universal Required Fields

Every monitor's `report-latest.json` must contain:

#### `meta` object

```json
"meta": {
  "issue": 0,
  "volume": 0,
  "week_label": "W/E YYYY-MM-DD",
  "published": "YYYY-MM-DDTHH:MM:SSZ",
  "slug": "{monitor-slug}",
  "schema_version": "2.0",
  "pipeline_inputs": {
    "synthesiser_sha": "string or null",
    "synthesiser_date": "YYYY-MM-DD or null",
    "daily_finding_count": 0,
    "reasoner_sha": "string or null"
  }
}
```

**Gap 3 — pipeline_inputs:** `meta.pipeline_inputs` is **mandatory** on every report.
Record exactly what pipeline data was used. If synthesiser was absent, set
`synthesiser_sha: null` and `synthesiser_date: null`. Never omit the block.

#### `lead_signal` object

```json
"lead_signal": {
  "headline": "string — specific factual statement, max 120 chars",
  "indicator": "string — domain or indicator name",
  "confidence": "Confirmed | High | Assessed | Possible",
  "source_url": "string — primary source URL"
}
```

Derived from synthesiser `lead_signal` (confirmed or refined, not rewritten without cause).

#### `key_judgments` array (3–5 items)

```json
"key_judgments": [
  {
    "id": "kj-001",
    "judgment": "string — specific, decision-useful analytical statement",
    "confidence": "Confirmed | High | Assessed | Possible",
    "supporting_evidence": "string — specific evidence from this week's data",
    "cross_monitor_relevance": "string or null — which other monitors this affects"
  }
]
```

- Minimum 3, maximum 5 judgments per report
- No `_preliminary` markers — these are final values
- `supporting_evidence` must reference specific findings from the pipeline

#### `signal_panel` object

```json
"signal_panel": {
  "headline": "string — dashboard display headline",
  "body": "string — 2–3 sentence summary for dashboard display",
  "level": "string — monitor-specific status label",
  "direction": "Deteriorating | Stable | Improving"
}
```

WDM additionally requires a `history` array (see Section 3.2).

#### `weekly_brief` field (Gap 4)

```json
"weekly_brief": "string — 400–600 words, analytical narrative"
```

**Mandatory in JSON.** Edited from synthesiser `weekly_brief_draft`.
Analyst edits; does not rewrite from scratch without cause.
The Hugo brief markdown file is a **separate, additional output** — both are required.
See Section 7 for Hugo requirements.

#### `cross_monitor_flags` object

```json
"cross_monitor_flags": {
  "updated": "YYYY-MM-DDTHH:MM:SSZ",
  "flags": [
    {
      "target_monitor": "string — full slug",
      "signal": "string",
      "type": "string",
      "confidence": "Confirmed | High | Assessed | Possible",
      "week_added": "YYYY-MM-DD"
    }
  ],
  "version_history": [
    {
      "date": "YYYY-MM-DD",
      "change": "string"
    }
  ]
}
```

### 3.2 Monitor-Specific Required Sections

Each monitor must additionally include:

**GMM:** `stress_regime`, `indicator_domains` (array, 6 domains), `central_bank_tracker`, `tariff_tracker`, `tail_risks`

**WDM:** `global_health_snapshot`, `country_heatmap` (with `severity_sub` on every entry),
`backsliding_alerts`, `electoral_calendar_watch`

`signal_panel` must include `history` array:
```json
"history": [
  {"issue": 1, "date": "YYYY-MM-DD", "rapid_decay": 0, "recovery": 0, "watchlist": 0}
]
```
Carry forward all prior history. Append this week. Max 52 entries (rolling year). Never truncate below 4.

**SCEM:** `global_escalation_snapshot`, `theatre_tracker` (with deviation calc on all indicators),
`escalation_indicators`, `hybrid_warfare_layer`

**FCW:** `campaign_roster`, `actor_posture`, `threat_level`, `platform_response`

**ESA:** `domain_tracker`, `sovereignty_index`, `member_state_alignment`

**AGM:** `capability_tier`, `regulatory_milestone_status`, `risk_register`

**ERM:** `planetary_boundary_status`, `tipping_trajectory`, `compound_risk_matrix`

### 3.3 WDM Living Knowledge Sections in persistent-state.json

The following sections must be populated every WDM run and must not be omitted
(set to `[]` or `{}` if no data — never absent):

- `electoral_watch` — `{timeline: [...], environment: [...], positive_transitions: [...]}`
- `digital_civil` — internet shutdowns, civil society restrictions, press freedom
- `autocratic_export` — documented playbook transfers, legislative mimicry, advisor deployments
- `state_capture` — judiciary packing, media capture, civil service politicisation
- `institutional_pulse` — resilience signals (deterioration and resistance)
- `legislative_watch` — legislation threatening democratic norms
- `research_360.friction_notes` — contested findings, disputed attribution, data gaps
- `networks` — tracked autocratic/interference networks

Schema rule: missing key → "Build 2" placeholder on the page.
`monthly_trend` — do not populate until Issue 8 (4 weeks of data).

---

## 4. GitHub Actions Workflow Requirements

Every GitHub Actions workflow that calls a Python script in the pipeline must
include the following environment variables:

### 4.1 Always Required

```yaml
env:
  PPLX_API_KEY: ${{ secrets.PPLX_API_KEY }}
```

### 4.2 GH_TOKEN (Gap 1)

```yaml
env:
  PPLX_API_KEY: ${{ secrets.PPLX_API_KEY }}
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**GH_TOKEN is required** in the workflow `env` block whenever **any** Python script
in the pipeline uses `subprocess` calls that invoke `gh api`, `gh repo`, or any
`gh` CLI command — including but not limited to:

- `collect.py` — if it reads from `asym-intel-internal` or another internal repo
- `weekly-research.py` — if it fetches methodology or handoff files via `gh api`
- `reasoner.py` — if it reads pipeline files via `gh api`
- `{slug}-synthesiser.py` — if it loads pipeline files via `gh api`

**When to add:** If the script file contains `subprocess` + any string matching
`gh api` or `gh repo`, the workflow must include `GH_TOKEN`.

**Why:** `gh` CLI uses the `GH_TOKEN` environment variable for authentication.
Without it, all `gh api` calls in the subprocess will fail with a 401 error
even if `GITHUB_TOKEN` is available as a secret — it must be explicitly exported
into the environment.

---

## 5. Publish Guard (3 Checks — All Must Pass)

The Publish Guard is **mandatory** before writing any output file.
Apply it at the start of Step 6.

### Check 1: Correct Publish Day

Verify the current UTC day of week matches this monitor's scheduled publish day
(see schedule table in Section 1.4).

**On failure:** EXIT immediately. Log: `"PUBLISH GUARD FAILED: wrong day of week — expected {day}, got {current_day}. Exiting without publish."`

### Check 2: UTC Hour Within ±3 of Scheduled Hour

Verify the current UTC hour is within ±3 hours of the monitor's scheduled UTC hour.

Example: GMM scheduled 08:00 UTC → passes if current UTC hour is 05–11.

**On failure:** EXIT immediately. Log: `"PUBLISH GUARD FAILED: current UTC hour {H} is outside ±3 window of scheduled hour {S}. Exiting without publish."`

### Check 3: report-latest Not Already Dated Today (Gap 6)

Read `meta.published` from the current `static/monitors/{slug}/data/report-latest.json`.
Extract the date portion (YYYY-MM-DD). If it equals today's UTC date: the report has
already been published this cycle.

**On failure:** EXIT immediately. Log: `"PUBLISH GUARD FAILED: report-latest.json already published today ({date}). Exiting without duplicate publish."`

### Guard Failure Response

On any guard failure:
1. Log the specific failure reason (as above)
2. Do NOT write any files
3. Do NOT commit
4. Do NOT send a notification for the publish event
5. Terminate the cron run

A prompt reload is **not** a reason to republish. If the session restarts mid-run,
re-apply the Publish Guard from scratch.

---

## 6. Two-Pass Commit Rule (Gap 7)

The Two-Pass Commit Rule is **mandatory**. Never combine Pass 1 and Pass 2 into
a single commit. This exists to ensure a valid, minimal report exists in the repo
before deep sections are appended — protecting against partial-commit data corruption.

### Pass 1 — Report Files Only

Write and commit **only**:
1. `static/monitors/{slug}/data/report-latest.json` — complete assembled report
2. `static/monitors/{slug}/data/report-YYYY-MM-DD.json` — dated copy (identical content)

Before committing, verify all required top-level keys are present (see Section 3).
If any required key is missing: do not commit. Fix the gap and retry.

Commit message: `data({abbr}): weekly pipeline — Issue [N] W/E YYYY-MM-DD [pass 1]`

```bash
git add static/monitors/{slug}/data/report-latest.json \
        static/monitors/{slug}/data/report-YYYY-MM-DD.json
git commit -m "data({abbr}): weekly pipeline — Issue [N] W/E YYYY-MM-DD [pass 1]"
git pull --rebase origin main && git push origin main
```

If any deep sections need to be patched onto the Pass 1 JSON (due to size limits),
do so via `gh api` PATCH before proceeding to Pass 2.

### Pass 2 — State, Archive, and Hugo Files

Write and commit **only** after Pass 1 is confirmed pushed:
1. `static/monitors/{slug}/data/archive.json` — append this week's entry
2. `static/monitors/{slug}/data/persistent-state.json` — updated living state
3. `content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md` — Hugo brief markdown

Commit message: `data({abbr}): weekly pipeline — Issue [N] W/E YYYY-MM-DD [pass 2]`

```bash
git add static/monitors/{slug}/data/archive.json \
        static/monitors/{slug}/data/persistent-state.json \
        content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md
git commit -m "data({abbr}): weekly pipeline — Issue [N] W/E YYYY-MM-DD [pass 2]"
git pull --rebase origin main && git push origin main
```

### What Never Combines

Do **not** include in Pass 1: archive.json, persistent-state.json, Hugo brief.
Do **not** include in Pass 2: report-latest.json, report-YYYY-MM-DD.json.

---

## 7. Hugo Brief Requirements

### 7.1 Filename Rule (Gap 8 — FE-019)

The Hugo brief filename **must** exactly equal the `date:` frontmatter field:

```
content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md
```

where `YYYY-MM-DD` is the same date string that appears in the frontmatter `date:` field.

**Example:**
- Filename: `content/monitors/macro-monitor/2026-04-07-weekly-brief.md`
- Frontmatter: `date: "2026-04-07"`

**Violation:** FE-019 — filename date mismatch causes Hugo to render the wrong brief
on the weekly brief page, or to fail to render it at all.

### 7.2 Required Frontmatter Fields

```yaml
---
title: "{Monitor Full Name} — Weekly Brief W/E YYYY-MM-DD"
date: "YYYY-MM-DD"
slug: "{monitor-slug}"
issue: N
schema_version: "2.0"
draft: false
---
```

All six fields are required. `draft: false` must be explicit (not omitted, which
defaults to true in some Hugo configs).

### 7.3 Minimum Length

The Hugo brief body must be **400–600 words**.

This content must be the same as — or edited from — the `weekly_brief` field in
`report-latest.json`. Do not produce significantly different text in the two outputs.

### 7.4 Relationship to JSON weekly_brief

The Hugo file and the JSON field serve different consumers:
- `report-latest.json → weekly_brief` is read by the monitor's `report.html` page
- `content/monitors/{slug}/YYYY-MM-DD-weekly-brief.md` is read by the brief page (`/briefs/`)

Both are **required every publish cycle**. Producing one without the other is
a FE-019 / display gap.

---

## 8. Collector and Weekly Research — API Prompt Requirements

Although these are not Analyst outputs, Analyst prompt authors are responsible for
understanding what their pipeline inputs require so that gaps are caught.

### 8.1 search_recency_filter (Gap 2)

**Collector API prompts** (daily, `sonar` model):
```json
"search_recency_filter": "week"
```

**Weekly research API prompts** (`sonar-pro` model):
```json
"search_recency_filter": "month"
```

These filters must be present in every API call object. Omitting them causes the
Perplexity API to return results from the full index with no recency weighting,
producing stale findings in the daily pipeline.

---

## 9. Conformance Checklist

Use this checklist to audit any Analyst cron prompt against this spec.
Answer YES or NO for each item. Any NO is a gap requiring correction.

### Identity and Inputs

- [ ] Prompt describes Analyst as a publication agent, not a research agent
- [ ] Prompt reads synthesiser output as primary draft (Step 0S)
- [ ] Prompt reads persistent-state.json and prior report-latest.json (Step 0P)
- [ ] Prompt loads COLLECTOR-ANALYST-ARCHITECTURE.md (Step 0B)
- [ ] Prompt reads monitor methodology from `docs/methodology/{slug}-full.md`

### Step Structure

- [ ] Step 0A present (notes-for-computer.md, optional/non-blocking)
- [ ] Step 0B present (architecture + shared layer)
- [ ] Step 0C present (daily-latest.json)
- [ ] Step 0D present (weekly-latest.json, optional)
- [ ] Step 0S present (synthesis-latest.json, primary draft)
- [ ] Step 0P present (persistent-state + prior report)
- [ ] Step 1 present (methodology review)
- [ ] Step 2 present (monitor-specific signal assessment)
- [ ] Step 3 present (cross-monitor flags — confirm from synthesiser, do not invent)
- [ ] Step 4 present (final report assembly)
- [ ] Step 5 present (persistent-state update + notifications)
- [ ] Step 6 present (Publish Guard + Two-Pass Commit)
- [ ] AGM only: Step 7 present (Ramparts publication)

### Required JSON Fields

- [ ] `meta.pipeline_inputs` present with synthesiser_sha, synthesiser_date, daily_finding_count, reasoner_sha (Gap 3)
- [ ] `meta.schema_version` = "2.0"
- [ ] `lead_signal` present with headline, indicator/domain, confidence, source_url
- [ ] `key_judgments` array with 3–5 items, each with judgment, confidence, supporting_evidence, cross_monitor_relevance
- [ ] `signal_panel` present with headline, body, level, direction
- [ ] `weekly_brief` present in JSON (400–600 words) (Gap 4)
- [ ] `cross_monitor_flags` present with updated timestamp, flags array, version_history

### lead_signal Rule

- [ ] Prompt specifies: confirm/refine synthesiser lead_signal; do not independently derive unless synthesiser output is null (Gap 5)

### Publish Guard

- [ ] Check 1: correct day of week
- [ ] Check 2: UTC hour within ±3 of scheduled hour
- [ ] Check 3: report-latest not already dated today (Gap 6)
- [ ] Failure response: EXIT, log reason, do not publish

### Two-Pass Commit Rule

- [ ] Pass 1 files: report-latest.json + report-YYYY-MM-DD.json only (Gap 7)
- [ ] Pass 2 files: archive.json + persistent-state.json + Hugo brief only (Gap 7)
- [ ] Passes are never combined
- [ ] Commit message format matches spec

### Hugo Brief

- [ ] Filename = `YYYY-MM-DD-weekly-brief.md` where date matches frontmatter `date:` field (Gap 8 — FE-019)
- [ ] Frontmatter includes: title, date, slug, issue, schema_version, draft: false
- [ ] Brief body is 400–600 words

### GitHub Actions (for workflow authors)

- [ ] `PPLX_API_KEY` in workflow env
- [ ] `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in workflow env if any script uses `subprocess` + `gh api` (Gap 1)

### Monitor-Specific

- [ ] **GMM:** stress_regime (final, no _preliminary), 6 indicator_domains, central_bank_tracker, tariff_tracker, tail_risks
- [ ] **WDM:** severity_sub on every heatmap entry; signal_panel.history array; living knowledge sections in persistent-state
- [ ] **SCEM:** deviation calculation on every indicator (level, baseline, deviation, band); CONTESTED band has explicit note
- [ ] **FCW:** campaign_roster, actor_posture, threat_level, platform_response
- [ ] **ESA:** domain_tracker, sovereignty_index, member_state_alignment
- [ ] **AGM:** capability_tier, regulatory_milestone_status, risk_register; Ramparts Step 7
- [ ] **ERM:** planetary_boundary_status, tipping_trajectory, compound_risk_matrix

---

## Appendix A — Known Gaps Fixed (Session 2026-04-07)

These gaps were identified and fixed during the session of 2026-04-07. Each is
explicitly addressed in this spec as noted.

| Gap | Description | Spec Section |
|-----|-------------|-------------|
| Gap 1 | GH_TOKEN in workflow env | Section 4.2 |
| Gap 2 | search_recency_filter in collector/weekly-research API calls | Section 8.1 |
| Gap 3 | meta.pipeline_inputs mandatory in every report-latest.json | Section 3.1 |
| Gap 4 | weekly_brief must be in JSON AND Hugo brief (both mandatory) | Sections 3.1, 4 (Step 4), 7.4 |
| Gap 5 | lead_signal confirmed from synthesiser; not independently derived unless null | Sections 2 (Step 0S, Step 4), 3.1 |
| Gap 6 | Publish Guard: 3 checks — day, UTC hour ±3, not already published today | Section 5 |
| Gap 7 | Two-Pass Commit Rule — Pass 1: report files only; Pass 2: state+archive+Hugo | Section 6 |
| Gap 8 | Hugo brief filename must equal frontmatter date field (FE-019 rule) | Section 7.1 |

---

*End of ANALYST-CRON-SPEC.md — Version 1.0 | 2026-04-07*

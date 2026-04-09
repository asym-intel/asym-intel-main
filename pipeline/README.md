# pipeline/monitors/

## What this directory is

Internal pipeline storage for the asym-intel.info intelligence architecture.
Never served publicly — Hugo's `publishDir = docs` only builds from `static/`,
`content/`, and `assets/`. Everything in `pipeline/` is repo-internal only.

## Architecture

```
Layer 1A — Collector (daily, GitHub Actions, sonar)
  Searches public sources → structures into Tier 0 JSON → commits to pipeline/

Layer 1B — Weekly Research (weekly, GitHub Actions, sonar-pro)
  Deeper web search → weekly research JSON → commits to pipeline/

Layer 1C — Reasoner (weekly, GitHub Actions, sonar-deep-research)
  Reasons over pipeline docs → analytical conclusions → commits to pipeline/

Layer 1D — Synthesiser (weekly, GitHub Actions, sonar-deep-research)
  Combines all inputs → synthesis-latest.json → commits to pipeline/

Layer 2 — Publisher (weekly, GitHub Actions, deterministic Python)
  Reads synthesis-latest.json → publishes to static/ and content/
  Script: pipeline/publishers/publisher.py
  Zero LLM calls, zero credits.
```

## Directory structure

```
pipeline/
  monitors/
    {slug}/
      daily/
        README.md               — monitor-specific notes
        daily-latest.json       — most recent Collector run (overwritten daily)
        verified-YYYY-MM-DD.json — dated archive (one per day, never deleted)
      weekly/
        weekly-latest.json      — most recent weekly research (overwritten weekly)
      reasoner/
        reasoner-latest.json    — most recent reasoner output
      synthesised/
        synthesis-latest.json   — most recent synthesis (feeds the Publisher)
  publishers/
    publisher.py                — generic config-driven publisher (all 7 monitors)
  synthesisers/
    synth_utils.py              — shared synthesiser utilities
```

## Monitors with active pipelines

All 7 monitors have active Collector, Chatter, and Publisher workflows.
See `ops/cron-schedule.md` in asym-intel-internal for full schedule.

## Rules

- Collectors write ONLY to `pipeline/` — never to `static/monitors/{slug}/data/`
- `daily-latest.json` is overwritten on each run
- `verified-YYYY-MM-DD.json` files are permanent — never delete
- All Collector files conform to `tier0-v1.0` schema
- `confidence_preliminary` only — never final public confidence levels
- The Publisher (Layer 2) is the only automated process that writes to `data/`

## Adding a new monitor

See `docs/COLLECTOR-ANALYST-ARCHITECTURE.md` for the full step-by-step checklist.

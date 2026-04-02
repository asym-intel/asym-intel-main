# pipeline/monitors/

## What this directory is

Internal pipeline storage for the Collector layer of the asym-intel.info
three-layer intelligence architecture. Never served publicly — Hugo's
`publishDir = docs` only builds from `static/`, `content/`, and `assets/`.
Everything in `pipeline/` is repo-internal only.

## Architecture

```
Layer 1 — Collector (daily Computer cron)
  Searches public sources → structures into Tier 0 JSON → commits here

Layer 2 — Analyst (weekly Computer cron)
  Reads pipeline/{slug}/daily/daily-latest.json at Step 0C
  Applies monitor methodology → assigns final confidence → publishes to data/
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
```

## Monitors with active Collectors

| Monitor | Slug | Collector cron | Schedule |
|---------|------|---------------|----------|
| FCW | fimi-cognitive-warfare | 6d67ba71 | Daily 08:00 UTC |

## Rules

- Collectors write ONLY to `pipeline/` — never to `static/monitors/{slug}/data/`
- `daily-latest.json` is overwritten on each run
- `verified-YYYY-MM-DD.json` files are permanent — never delete
- All files conform to `tier0-v1.0` schema
- `confidence_preliminary` only — never final public confidence levels
- The Analyst (weekly cron) is the only agent that writes to `data/`

## Adding a new monitor

See `asym-intel-internal/prompts/README.md` for the full step-by-step guide.

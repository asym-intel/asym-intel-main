# WDM Daily Collector Output

**Monitor:** World Democracy Monitor (democratic-integrity)
**Layer:** Tier 0 — Daily Pre-Verification (GitHub Actions)
**Model:** sonar (fast daily search)
**Schedule:** Daily 07:00 UTC

## Files

- `daily-latest.json` — most recent collector run (overwritten daily)
- `verified-YYYY-MM-DD.json` — dated archive of each run

## Purpose

Pre-verified candidate findings for the WDM Analyst cron.
Contains democratic erosion indicators, institutional integrity events,
and electoral watch items identified from public sources.

The WDM Analyst reads this at Step 0C each Monday before applying
the full scoring methodology and publishing.

## Schema

`tier0-v1.0` — see `asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md`

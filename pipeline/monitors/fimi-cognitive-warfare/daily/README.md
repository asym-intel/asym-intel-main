# pipeline/monitors/fimi-cognitive-warfare/daily/

## What this is

Tier 0 pre-verification feeder output for the FCW (FIMI & Cognitive Warfare) monitor.

The FCW Daily Feeder runs every day at 08:00 UTC. It searches public FIMI sources
(Meta CIB, Google TAG, MSTIC, EEAS STRATCOM, Stanford IO, DFRLab, ASPI ICPC),
structures candidate findings against the Tier 0 schema, and writes here.

This is pipeline infrastructure — not published intelligence. The weekly FCW cron
reads this at Step 0C, applies FCW methodology, assigns final confidence, and
decides what enters the public report.

## Files

- `daily-latest.json` — most recent feeder run output (overwritten daily)
- `verified-YYYY-MM-DD.json` — dated archive files (one per day, append-only)

## What this is NOT

- Not public output. Never served on asym-intel.info.
- Not a substitute for the weekly FCW cron's methodology review.
- Not a source of final confidence levels (feeder assigns `confidence_preliminary` only).
- Not a changelog of published findings (see `data/archive.json` for that).

## Schema

All files conform to `tier0-v1.0` schema.
See `docs/prompts/tier0-schema.md` for the canonical field definitions.

## Who reads this

- FCW Weekly Cron (Thu 09:00 UTC) — Step 0C
- Housekeeping Cron (Mon 08:00 UTC) — validates schema and freshness

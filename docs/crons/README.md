# docs/crons/ — Retired Analyst Cron Prompts

## Status: RETIRED — 9 April 2026

The analyst cron prompts in this directory are **no longer active**. Weekly report
publication is now handled by `pipeline/publishers/publisher.py`, a deterministic
Python script running as GitHub Actions workflows — zero Computer credits.

See `.github/workflows/*-publisher.yml` for the active publisher workflows.
See `pipeline/publishers/publisher.py` for the publisher script.
See `ops/cron-schedule.md` in asym-intel-internal for the full schedule.

**Do NOT recreate Computer crons from these prompts.** The publisher workflows
replace them entirely.

---

## Historical reference

These prompts were used by Computer `schedule_cron` tasks created 4 April 2026.
Each cron was a slim pointer that read its prompt from this directory and executed
as a full Computer session, consuming ~100 credits/run.

### Retired Analyst Cron IDs (do not recreate)

| Monitor | Cron ID | Was | Replaced by |
|---------|---------|-----|-------------|
| WDM | adad85f6 | Mon 06:00 UTC | democratic-integrity-publisher.yml |
| GMM | 6efe51b0 | Tue 08:00 UTC | macro-monitor-publisher.yml |
| ESA | 72398be9 | Wed 19:00 UTC | european-strategic-autonomy-publisher.yml |
| FCW | 478f4080 | Thu 09:00 UTC | fimi-cognitive-warfare-publisher.yml |
| AGM | b53d2f93 | Fri 09:00 UTC | ai-governance-publisher.yml |
| ERM | 0aaf2bd7 | Sat 05:00 UTC | environmental-risks-publisher.yml |
| SCEM | 743bbe21 | Sun 18:00 UTC | conflict-escalation-publisher.yml |
| Housekeeping | c725855f | Mon 08:00 UTC | PAUSED — under review |

### Earlier retired IDs (4 April 2026 — do not recreate)

f7bd54e9, c94c4134, 0b39626e, b17522c3, 5ac62731, ce367026, 8cdb83c8, 7e058f57,
aec126c5, f78e0c2c, a67a9739, 10ddf5f0, 631c0fa0

---

## Prompt files (archived, not active)

| File | Monitor | Notes |
|------|---------|-------|
| wdm-slimmed-analyst-cron.md | WDM | Archived |
| agm-slimmed-analyst-cron.md | AGM | Archived |
| erm-slimmed-analyst-cron.md | ERM | Archived |
| esa-slimmed-analyst-cron.md | ESA | Archived |
| scem-slimmed-analyst-cron.md | SCEM | Archived |
| housekeeping.md | Platform | PAUSED — review Monday |
| annual-calibration-reminder.md | Platform | Unchanged |
| gsc-quarterly-audit.md | Platform | Unchanged |
| staging-guard.md | Platform | Migrated to GA workflow |

GMM and FCW analyst prompts were in asym-intel-internal (IP-protected). Also archived.

---

## What to keep internal vs public

Analyst prompts remain in this directory as historical reference. They are not
served on the public URL (Hugo doesn't build from `docs/crons/`). No action needed.

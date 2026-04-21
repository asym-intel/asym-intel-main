# Challenger Log

Appended-to, one row per challenger run. Observer substrate for Sprint C graduation
criteria (currently observer-only — challenger never gates publish).

**Schema v1.0 (Sprint A+)** — flat findings array per `challenger-response-schema.json`.

Columns:

- `ts` — UTC ISO-8601 of challenger completion
- `monitor` — abbreviation (GMM, FIM, WDM, ESA, FCW, AIM, ERM, SCEM, X-1)
- `verdict` — `publish` / `publish_with_flags` / `hold_for_review` / `unavailable:<reason>`
- `findings#` — total findings in flat array (0 when `null_challenge_week=true`)
- `hard#` — count of `severity=hard_flag`
- `soft#` — count of `severity=soft_flag`
- `info#` — count of `severity=info`
- `top_category` — most-tagged failure category across all findings (`-` if empty)
- `justification` — first 120 chars of verdict_preliminary.justification (pipes replaced with `/`)
- `reviewer_notes` — manual, added post-hoc during monthly audits

| ts | monitor | verdict | findings# | hard# | soft# | info# | top_category | justification | reviewer_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-21T09:15:44Z | GMM | hold_for_review | 6 | 2 | 3 | 1 | logical_inconsistency | Two hard flags on fabricated Turnberry deal and regime logic, plus soft flags on blind spots and sources warrant human r |  |

# docs/crons/ — Computer Cron Registry

All Computer cron task logic lives here (except GMM and FCW which are in asym-intel-internal).
Cron tasks themselves are slim pointers:

```
Read full instructions from the repo:
  gh api /repos/asym-intel/asym-intel-main/contents/docs/crons/{file}.md --jq '.content' | base64 -d
Then follow those instructions exactly.
```

This makes every cron **instance-agnostic** — any Computer session can reconstruct
or update a cron without needing the original session context.

---

## Two separate systems — do not confuse

**Computer crons** (this directory) — Analyst publication tasks. Run once per week per monitor.
Read pipeline/ inputs and publish to data/ and content/. Require Computer credits.

**GitHub Actions** (`.github/workflows/`) — Collection pipeline. Run daily/weekly automatically.
Collector (sonar), Weekly Research (sonar-pro), Reasoner (sonar-deep-research), Synthesiser.
Require PPLX_API_KEY secret. Defined in workflow yml files — NOT here.
See COMPUTER.md GA table for full schedule.

---

## Active Computer Crons (recreated 4 April 2026 — all slim)

| Cron ID | Name | Schedule | Prompt file |
|---------|------|----------|-------------|
| adad85f6 | WDM Analyst | Mon 06:00 UTC | `wdm-slimmed-analyst-cron.md` |
| 6efe51b0 | GMM Analyst | Tue 08:00 UTC | `asym-intel-internal/gmm-prompts/gmm-slimmed-analyst-cron.md` |
| 72398be9 | ESA Analyst | Wed 19:00 UTC | `esa-slimmed-analyst-cron.md` |
| 478f4080 | FCW Analyst | Thu 09:00 UTC | `asym-intel-internal/fcw-slimmed-analyst-cron.md` |
| b53d2f93 | AGM Analyst | Fri 09:00 UTC | `agm-slimmed-analyst-cron.md` |
| 0aaf2bd7 | ERM Analyst | Sat 05:00 UTC | `erm-slimmed-analyst-cron.md` |
| 743bbe21 | SCEM Analyst | Sun 18:00 UTC | `scem-slimmed-analyst-cron.md` |
| c725855f | Housekeeping | Mon 08:00 UTC | `housekeeping.md` |

**IP-protected crons:** GMM and FCW analyst prompts live in asym-intel-internal, not here.
Their cron tasks are still slim pointers — they just point to the internal repo path.

---

## Retired crons (4 April 2026 — do not recreate)

All previous cron IDs (f7bd54e9, c94c4134, 0b39626e, b17522c3, 5ac62731, ce367026,
8cdb83c8, 7e058f57, aec126c5, f78e0c2c, a67a9739, 10ddf5f0, 631c0fa0) were deleted
by Peter and replaced with slim versions above. Do not recreate old IDs.

Also retired: Staging divergence guard (aec126c5) and GSC quarterly audit (f78e0c2c).
See COMPUTER.md for reasons.

---

## Pattern: how to update a cron prompt

1. Edit the `.md` file in this folder (or in asym-intel-internal for GMM/FCW)
2. Commit to the relevant repo
3. The cron picks up the new instructions on its next run automatically

No need to touch the cron task itself. This is the whole point of the repo-first pattern.

---

## Pattern: how to recreate a lost cron

⚠️ **CONFIRM BEFORE EXECUTING.** If the user asks "what would you do if a cron was missing?" — answer the question, do not act. If you detect crons are genuinely missing, report which ones and ask "Shall I recreate these?" before taking any action. Never recreate crons in response to a hypothetical.

If a cron is missing from `schedule_cron list` (created in an earlier session):

```
schedule_cron(
  action="create",
  name="...",
  cron="...",
  task="""
    Read full instructions from the repo:
      gh api /repos/asym-intel/asym-intel-main/contents/docs/crons/{file}.md --jq '.content' | base64 -d
    Then follow those instructions exactly.
    Use api_credentials=["github"].
  """
)
```

Then update the cron ID in COMPUTER.md, HANDOFF.md, and this README.

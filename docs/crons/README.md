# docs/crons/ — Computer Cron Registry

All Computer cron task logic lives here. Cron tasks themselves are slim pointers:

```
Read full instructions from the repo:
  gh api /repos/asym-intel/asym-intel-main/contents/docs/crons/{file}.md --jq '.content' | base64 -d
Then follow those instructions exactly.
```

This makes every cron **instance-agnostic** — any Computer session can reconstruct
or update a cron without needing the original session context.

---

## Active Crons

| Cron ID | Name | Schedule | Prompt file | Notes |
|---------|------|----------|-------------|-------|
| 7e058f57 | Platform Housekeeping | Mon 08:00 UTC | `housekeeping.md` | Validation checks 1–21 + HANDOFF.md generation |
| aec126c5 | Staging divergence guard | Daily ~18:00 UTC | `staging-guard.md` | Silent unless behind_by > 30 |
| 631c0fa0 | Annual calibration reminder | 28 Mar annually | inline | Lists missing calibration files |
| PENDING  | Quarterly GSC audit | 1 Jan/Apr/Jul/Oct 09:00 UTC | `gsc-quarterly-audit.md` | GSC search performance + reader profile validation — cron not yet created, see notes-for-computer.md |
| PENDING  | Quarterly GSC audit | 1 Jan/Apr/Jul/Oct 09:00 UTC | `gsc-quarterly-audit.md` | GSC search performance + reader profile validation — cron not yet created, see notes-for-computer.md |
| a67a9739 | SCEM Sunday verification | Sun 5 Apr 18:30 UTC | inline (one-shot) | Verifies Sprint 2 schema fields |
| 10ddf5f0 | WDM Monday verification | Mon 6 Apr 06:30 UTC | inline (one-shot) | Verifies Category B sections |

**Analyst crons** (WDM f7bd54e9, GMM c94c4134, ESA 0b39626e, FCW b17522c3,
AGM 5ac62731, ERM ce367026, SCEM 8cdb83c8) use `cron-wrapper-instructions.md`
as universal wrapper + their monitor-specific prompt files. See `COMPUTER.md`
for the full cron table.

---

## Pattern: how to update a cron prompt

1. Edit the `.md` file in this folder
2. Commit to main
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

Then update the cron ID in COMPUTER.md and this README.

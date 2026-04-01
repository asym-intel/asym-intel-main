# CRON WRAPPER — All Asymmetric Intelligence Monitors

## How to configure any monitor cron task

The cron schedule should contain ONLY this:

---
Read your full instructions from the repo before doing anything:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{SLUG}/cron-prompt.md \
  --jq '.content' | base64 -d
```

Then follow those instructions exactly. The repo file is the canonical
source of truth. Ignore any instructions baked into this cron schedule.

Use api_credentials=["github"] for all GitHub operations.
```
---

Replace {SLUG} with the monitor slug:
  SCEM: conflict-escalation      → scem-cron-prompt.md
  ERM:  environmental-risks      → erm-cron-prompt.md
  WDM:  democratic-integrity     → wdm-cron-prompt.md  (to be created)
  GMM:  macro-monitor            → gmm-cron-prompt.md  (to be created)
  FCW:  fimi-cognitive-warfare   → fcw-cron-prompt.md  (to be created)
  ESA:  european-strategic-autonomy → esa-cron-prompt.md (to be created)
  AGM:  ai-governance            → agm-cron-prompt.md  (to be created)

## Why this pattern
- Blueprint changes propagate instantly to all cron runs
- No need to update 7 cron schedules when architecture changes
- Cron violations (like touching HTML) are caught at the prompt level
- Prompt files are version-controlled and auditable

# CRON WRAPPER — All Asymmetric Intelligence Monitors
# Blueprint v2.1 — Updated 1 April 2026

## How to configure any monitor cron task

The cron schedule should contain ONLY this:

---
Read your full instructions from the repo before doing anything:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{SLUG}/{ABBR}-cron-prompt.md \
  --jq '.content' | base64 -d
```

Then follow those instructions exactly. The repo file is the canonical
source of truth. Ignore any instructions baked into this cron schedule.

Use api_credentials=["github"] for all GitHub operations.

---

## Monitor slugs and prompt paths

| Monitor | Abbr | Slug | Cron Prompt |
|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | wdm-cron-prompt.md |
| Global Macro Monitor | GMM | macro-monitor | gmm-cron-prompt.md |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | fcw-cron-prompt.md |
| European Strategic Autonomy | ESA | european-strategic-autonomy | esa-cron-prompt.md |
| AI Governance Monitor | AGM | ai-governance | agm-cron-prompt.md |
| Environmental Risks Monitor | ERM | environmental-risks | erm-cron-prompt.md |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | scem-cron-prompt.md |

## Housekeeping cron (fc210493)

Runs every Monday at 08:00 UTC (after all Monday publishes). Reads its
prompt from:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/housekeeping-cron-prompt.md \
  --jq '.content' | base64 -d
```

Performs 9 structural checks across all 7 monitors. Notifies only on WARN/FAIL.

## Why this pattern

- Blueprint changes propagate instantly to all cron runs
- No need to update 7 cron schedules when architecture changes
- Cron violations (like touching HTML) are caught at the prompt level
- Prompt files are version-controlled and auditable
- The housekeeping cron catches structural drift before it reaches users

## Critical rules (all crons)

1. CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER.
2. Only write: report-latest.json, report-{DATE}.json, archive.json,
   persistent-state.json, and one Hugo brief markdown file.
3. Always use today's UTC date. Never future dates.
4. schema_version: "2.0" in all JSON files.
5. Load persistent-state.json BEFORE researching.

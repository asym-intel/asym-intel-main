# CRON WRAPPER — All Asymmetric Intelligence Monitors
# Blueprint v2.1 — Updated 1 April 2026
# ══════════════════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — READ THIS BEFORE ANYTHING ELSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every cron agent MUST begin by fetching the working agreement:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d
```

Then fetch your monitor-specific prompt and follow it exactly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNIVERSAL CRON RULES — APPLY TO ALL 7 MONITORS, NO EXCEPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 1 — FILE SCOPE: You may write EXACTLY these files and nothing else:
  ✅ static/monitors/{slug}/data/report-latest.json
  ✅ static/monitors/{slug}/data/report-{PUBLISH_DATE}.json
  ✅ static/monitors/{slug}/data/archive.json          (APPEND ONLY — never truncate)
  ✅ static/monitors/{slug}/data/persistent-state.json (SURGICAL UPDATES — never replace wholesale)
  ✅ content/monitors/{slug}/{PUBLISH_DATE}-weekly-brief.md

  ❌ NEVER write *.html, *.css, *.js, *.yml, *.toml, or any file outside data/ and content/
  ❌ NEVER write to static/monitors/shared/
  ❌ NEVER modify any other monitor's files
  ❌ NEVER create new files outside the above list

RULE 2 — DATE: Always use today's actual UTC date.
  PUBLISH_DATE=$(date -u +%Y-%m-%d)
  Never use a future date. Hugo silently skips future-dated pages (buildFuture=true is set,
  but the validator will FAIL the build if a future date is detected).

RULE 3 — JSON SCHEMA: Every JSON file must contain:
  "schema_version": "2.0"   in the meta object
  Named semantic keys only — never module_0, module_1, etc.

RULE 4 — PERSISTENT STATE: Load before researching. Update surgically.
  - Read persistent-state.json FIRST, before any research begins
  - Carry forward all entities unless new primary-source evidence justifies change
  - Every change MUST include a version_history entry with date, change, reason, prior_value
  - Never delete version_history entries — only append

RULE 5 — ARCHIVE: Append only. Never overwrite or truncate archive.json.
  Read current archive, append this issue's index entry, write back.
  The archive is the permanent record — data loss here cannot be recovered.

RULE 6 — SINGLE COMMIT: All 4 data files in one git commit.
  Commit message format: "data({abbr}): weekly JSON pipeline — Issue {N} W/E {DATE}"
  The Hugo brief is committed separately (or included in the same commit — either is fine).

RULE 7 — DAY GUARD: Check the day before running.
  IF today is not your scheduled day → run a health check only, then exit silently.
  IF today IS your scheduled day AND current UTC hour >= scheduled time → proceed.
  IF unsure → do NOT run. Exit silently.

RULE 8 — SIGNAL FIELD: Always an object, never a string.
  "signal": { "headline": "...", "body": "...", "source_url": "..." }

RULE 9 — VALIDATION BEFORE COMMIT: Before git push, verify:
  - All 4 JSON files are valid JSON (python3 -c "import json; json.load(open(...))")
  - published date matches today's UTC date
  - schema_version is "2.0"
  - persistent-state.json is larger than its previous version (never shrunk)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO CONFIGURE ANY MONITOR CRON TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Computer cron schedule should contain ONLY this:

---
Read the working agreement and your full instructions from the repo:

```bash
# Step 0: Working agreement (always first)
gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md \
  --jq '.content' | base64 -d

# Step 1: Your monitor-specific prompt
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{SLUG}/{ABBR}-cron-prompt.md \
  --jq '.content' | base64 -d
```

Follow both exactly. The repo files are the canonical source of truth.
Use api_credentials=["github"] for all GitHub operations.
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONITOR SLUGS AND PROMPT PATHS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Monitor | Abbr | Slug | Cron Prompt | Day | UTC |
|---|---|---|---|---|---|
| World Democracy Monitor | WDM | democratic-integrity | wdm-cron-prompt.md | Monday | 06:00 |
| Global Macro Monitor | GMM | macro-monitor | gmm-cron-prompt.md | Monday | 08:00 |
| FIMI & Cognitive Warfare | FCW | fimi-cognitive-warfare | fcw-cron-prompt.md | Thursday | 09:00 |
| European Strategic Autonomy | ESA | european-strategic-autonomy | esa-cron-prompt.md | Wednesday | 19:00 |
| AI Governance Monitor | AGM | ai-governance | agm-cron-prompt.md | Friday | 09:00 |
| Environmental Risks Monitor | ERM | environmental-risks | erm-cron-prompt.md | Saturday | 05:00 |
| Strategic Conflict & Escalation | SCEM | conflict-escalation | scem-cron-prompt.md | Sunday | 18:00 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOUSEKEEPING CRON (73452bc6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Runs every Monday at 08:00 UTC (after all Monday publishes).
Reads: static/monitors/housekeeping-cron-prompt.md
Performs 12 structural checks. Notifies only on WARN/FAIL. Silent on all-OK.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS PATTERN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- COMPUTER.md + cron-wrapper = working agreement that travels with every agent
- Blueprint changes propagate instantly to all cron runs via repo-read pattern
- Validator catches violations before they reach production
- Prompt files are version-controlled, auditable, and fixable without touching Computer schedules

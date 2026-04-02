# FCW COLLECTOR — Architecture Reference
# Updated: 2 April 2026
#
# STATUS: The FCW daily Collector now runs as a GitHub Actions workflow,
# NOT as a Computer cron. This stub is retained for historical reference only.
#
# CURRENT ARCHITECTURE (as of 2 April 2026):
#
#   Layer 1 — Collector (GitHub Actions)
#   Workflow: .github/workflows/fcw-collector.yml
#   Schedule: Daily 07:00 UTC
#   Canonical prompt: asym-intel-internal/prompts/FCW-COLLECTOR-PROMPT-v1.md
#
#   gh api /repos/asym-intel/asym-intel-internal/contents/prompts/FCW-COLLECTOR-PROMPT-v1.md \
#     --jq '.content' | base64 -d
#
#   Layer 2 — Analyst (Computer cron b17522c3)
#   Schedule: Thursday 09:00 UTC
#   Prompt: static/monitors/fimi-cognitive-warfare/fcw-cron-prompt.md
#
# HISTORY:
#   This file previously referenced FCW-DAILY-FEEDER-PROMPT-v4.md, which was
#   planned but never created. The "daily feeder" concept was superseded by the
#   GitHub Actions Collector architecture (March/April 2026). The prompt was
#   renamed from FCW-DAILY-FEEDER-PROMPT to FCW-COLLECTOR-PROMPT-v1.md.
#
# Do not create FCW-DAILY-FEEDER-PROMPT-v4.md — it is obsolete.
# Do not create a Computer cron for the FCW Collector — it runs in GitHub Actions.

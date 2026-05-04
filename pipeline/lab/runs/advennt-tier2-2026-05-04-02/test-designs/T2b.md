---
test_id: T2b
role: periodic-collection
monitor: advennt
provider: anthropic-agents
model: claude-sonnet-4-6
target_week_start: 2026-04-06
target_week_end: 2026-05-04
prompt_file: pipeline/lab/runs/advennt-tier2-2026-05-04-01/inputs/prompt-merged-T1.txt
prompt_sha: 2127cdc3b022bd554d32721c637351b4ce41a264f08ade2855e49225c1fc2003
max_tokens: 32768
collection_mode: periodic-additive
reference_date: 2026-05-04
routing_source: pipeline/engine/model_routing.yml

doctrine_question: >
  Given the T2 wall-clock ceiling was silently halved by
  anthropic_agents_client.py's hardcoded 1800s default (provider_config
  path had no carrier in role_defaults.yaml v3.0), does K5a stock DR
  complete the 7-jurisdiction merged collection within a correctly
  plumbed 3600s ceiling?

scoreboard_columns: "label,role,monitor,model,provider,tokens_input,tokens_output,server_tool_uses,runtime_seconds,parsed_ok,jurisdictions_returned,signals_total,avg_signals_per_jurisdiction,cost_total,max_wall_s_resolved"

evidence_artefacts: "raw/test-T2b-raw-response.json,outputs/test-T2b-parsed.json,raw/test-T2b-resolved-config.json"

pass_threshold: >
  parsed_ok=true AND stop_reason=end_turn AND jurisdictions_returned=7 AND
  max_wall_s_resolved=3600 (logged at dispatch time from the adapter, not
  inferred from design file). If max_wall_s_resolved != 3600, test
  invalidates as plumbing-bug not DR-capability-bug.

scoreboard_count_fields:
  developments_count: signals
  candidates_count: gaps_this_run

provider_config_override:
  max_wall_s: 3600
  poll_interval_s: 10.0
  keep_resources: false
  agent_name: advennt-t2b-dr-tier2
  session_title: advennt-collector-tier2-dr-retry-2026-05-04
---

# Test T2b — T2 re-run with correctly plumbed max_wall_s=3600

## Doctrine anchors

KH-LAB-003 (provider_overlays carrier — the fix that makes this test valid).
AD-2026-05-04-CM (role_defaults.yaml v3.0 overlay model).

Findings from T2 diagnostic:
  1. anthropic_agents_client.py L205 hardcodes max_wall_s default=1800.
  2. role_defaults.yaml v3.0 has no provider_config carrier under any role.
  3. T2.md's max_wall_s: 3600 was structurally invisible to runner + adapter.

## Pre-run plumbing fix (blocker)

PR lab-plumbing-CP-1 must be merged. Specifically:
1. role_defaults.yaml — provider_overlays.anthropic-agents block under
   periodic-collection carrying max_wall_s: 3600.
2. runner.py — layer 4 projecting provider_overlays into provider_config.
3. anthropic_agents_client.py — log max_wall_s_resolved to provider_extras.

FIRST CHECK: raw/test-T2b-resolved-config.json must show
max_wall_s_resolved=3600 before interpreting any other result.

## Hypothesis

At 7-jurisdiction merged scope, K5a DR needs >1800s and <=3600s to
complete. T2's actual elapsed was capped at 1800s — we don't yet know
whether completion would have occurred at 2400s, 3000s, or 3600s.

## Test design

Identical to T2 in every variable except the plumbing fix. Prompt SHA
matches T1/T2 exactly to isolate the wall-clock variable.

## Success criteria

1. max_wall_s_resolved == 3600 in resolved-config.json. (If not, STOP.)
2. stop_reason: end_turn AND parsed_ok: true AND jurisdictions_returned=7.
3. runtime_seconds reported (informs future max_wall_s tuning).

## Failure modes

- runtime ≈ 3600 AND timeout → scope is binding constraint; T3a-A mandatory.
- runtime < 1800 AND end_turn → T2's failure was NOT wall-clock; investigate.
- max_wall_s_resolved != 3600 → plumbing PR didn't land correctly.

## Expected cost shape

$2–5 focused, $8–15 if DR is thorough. Same envelope as T2.

## Follow-on

Pass (runtime < 2700s): DR viable at 7-jurisdiction scope.
Pass (runtime 2700–3600s): DR marginal; T3a-A mandatory for production.
Fail (timeout at 3600s): T3a-A (scope reduction) or T2c (prompt override).

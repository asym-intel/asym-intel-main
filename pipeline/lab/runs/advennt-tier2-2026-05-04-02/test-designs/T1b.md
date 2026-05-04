---
test_id: T1b
role: periodic-collection
monitor: advennt
provider: anthropic
model: claude-sonnet-4-6
target_week_start: 2026-04-06
target_week_end: 2026-05-04
prompt_file: pipeline/lab/runs/advennt-tier2-2026-05-04-02/inputs/prompt-merged-T1b.txt
prompt_sha: <compute at authoring — must differ from T1 by the added directive>
max_tokens: 16384
collection_mode: periodic-additive
reference_date: 2026-05-04
routing_source: pipeline/engine/model_routing.yml

doctrine_question: >
  Does the Messages API dispatch path honour tool_choice with
  web_search_20260209 as a server-side tool, and does forced web_search
  invocation produce live-source signals at 7-jurisdiction merged scope
  that T1 parametric-recall did not?

scoreboard_columns: "label,role,monitor,model,provider,tokens_input,tokens_output,server_tool_uses,runtime_seconds,parsed_ok,jurisdictions_returned,signals_total,avg_signals_per_jurisdiction,search_invocations,live_url_resolution_rate"

evidence_artefacts: "raw/test-T1b-raw-response.json,raw/test-T1b-request-payload.json,outputs/test-T1b-parsed.json"

pass_threshold: >
  parsed_ok=true AND stop_reason=end_turn AND jurisdictions_returned=7 AND
  server_tool_uses>=1 AND signals_total>=22. Diagnostic bar: request
  payload MUST include tools array with web_search_20260209; if absent,
  test invalidates as harness-bug not model-bug.

scoreboard_count_fields:
  developments_count: signals
  candidates_count: gaps_this_run

provider_config_override:
  tool_choice:
    type: tool
    name: web_search
---

# Test T1b — Messages API + forced web_search_20260209, 7 jurisdictions

## Doctrine anchor

T1 showed server_tool_uses=None with no evidence whether `tools` was in
the request; T1b is the paired diagnostic + forced-invocation test.
See CLIENT-BETA-001 in engine-knowhow-inbox.md re: residual beta injection.

## Prerequisite — harness request logging

PR lab-plumbing-CP-1 must be merged. T1b requires the Messages API
client to dump `request_payload` into raw. Without this, a tool_use=0
outcome is ambiguous between (a) tool_choice not honoured, (b) tools
absent from payload, (c) model chose parametric path.

## Hypothesis

With tools=[{web_search_20260209, max_uses=5}] in the request AND
tool_choice={type:tool, name:web_search} AND an explicit prompt
directive, Sonnet 4.6 will invoke web_search at least once on the
first turn, then continue autonomously for up to 5 uses, producing
signals with live URLs — distinct from T1's parametric-recall URLs.

## Prompt delta vs T1

Add as the final paragraph before the schema block:

> "You MUST call the web_search tool before composing your JSON response.
> Do not rely on parametric knowledge of regulatory developments — every
> signal must be grounded in a web_search result from the current window.
> If a jurisdiction returns no search results, set its signals array to []
> and populate gaps_this_run with the search queries attempted."

## Success criteria

1. Diagnostic (MUST): request_payload.json contains `tools` array with
   web_search_20260209 AND `tool_choice: {type:tool, name:web_search}`.
2. Forced invocation: server_tool_uses >= 1.
3. Autonomous continuation: server_tool_uses >= 3 across full run.
4. Schema: jurisdictions_returned=7, all blocks populated.
5. Comparative: live URL resolution rate >= 60% (sample-check 10 signals).

## Failure modes

- tools absent from payload → harness bug; T1b invalidates. Fix adapter.
- tools present, tool_choice present, server_tool_uses=0 → SDK version issue.
- server_tool_uses=1 then stops → raise max_uses or strengthen directive.
- Input tokens > 200k → reduce max_uses to 3, or move to T1c (tier-1 only).

## Expected cost shape

T1 floor: $0.29 (parametric). T1b with 15–25 searches: ~$2–4.

## Follow-on

Pass → T1c (tier-1 only GB/MT/GI scope) with forced-search posture.
Fail (diagnostic) → fix harness, re-run T1b.
Fail (model) → Advennt production tier-2 moves to managed-agents path (T2b).

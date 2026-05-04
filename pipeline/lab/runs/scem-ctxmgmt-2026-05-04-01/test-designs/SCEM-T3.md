---
test_id: SCEM-T3
role: periodic-collection
monitor: conflict-escalation
provider: anthropic
model: claude-sonnet-4-6
target_week_start: 2026-04-27
target_week_end: 2026-05-03
prompt_file: pipeline/monitors/conflict-escalation/weekly-research-prompt.txt
prompt_sha: d633bef58ee82639026b8fb2c0cb1a47d149be40713bbe87f20eee6414f1ff33
max_tokens: 16384
collection_mode: periodic-additive
reference_date: 2026-05-04
routing_source: pipeline/engine/model_routing.yml

doctrine_question: >
  Does the context-management-2025-06-27 beta, which auto-clears old
  tool_result blocks between turns at a 50k trigger, resolve the 8-theatre
  SCEM weekly-research failure pattern (900s silent stall + 369k token
  overflow at web_search_max_uses=3)? Specifically: does the beta prevent
  inter-turn accumulation without breaking schema compliance or signed
  thinking blocks?

scoreboard_columns: "label,role,monitor,model,provider,tokens_input,tokens_output,server_tool_uses,runtime_seconds,parsed_ok,theatres_covered,signals_total,avg_signals_per_theatre,context_compaction_events,max_turn_input_tokens"

evidence_artefacts: "raw/test-SCEM-T3-raw-response.json,raw/test-SCEM-T3-request-payload.json,raw/test-SCEM-T3-resolved-config.json,outputs/test-SCEM-T3-parsed.json"

pass_threshold: >
  parsed_ok=true AND stop_reason=end_turn AND theatres_covered>=6 (out of
  8; Sudan/Myanmar/DRC structural gap tolerated) AND
  max_turn_input_tokens<=180000 (headroom preserved) AND
  context_compaction_events>=1 (beta observably fired).

scoreboard_count_fields:
  developments_count: conflict_updates
  candidates_count: open_findings

provider_config_override:
  tool_choice:
    type: auto    # NOT forced — SCEM prompt is directive enough
  beta_headers:
    - context-management-2025-06-27

experimental_flags:
  enable_context_management: true
  enable_count_tokens_preflight: true
---

# Test SCEM-T3 — context-management beta at 8-theatre scope

## Doctrine anchors

KH-WS-004 (web_search iterative tool-use timeout — 900s lab overlay).
KH-WS-005 (context-management beta prescription for SCEM scope).
Incident 2026-05-04 SCEM overflow:
  - 3 searches, 369,599 input tokens, prose output instead of JSON
  - Root cause: tool_result density, not tool_use count
  - Prior fix (max_uses 20→3) insufficient for this failure mode

## Hypothesis

Anthropic's context-management-2025-06-27 beta auto-clears tool_result
blocks from prior turns when cumulative input tokens exceed the beta's
internal 50k trigger, preserving only the reasoning/thinking block
signatures and the most recent turn's tool_results. At 8-theatre
iterative-search scope this should:

(a) prevent the 369k accumulation observed in the original SCEM failure,
(b) allow the model to continue searching through all 8 theatres rather
    than silently stalling mid-loop at ~900s, and
(c) preserve structural fidelity (keyed JSON output, not prose
    continuation) because thinking blocks remain signed and intact.

## Test design — scope_axes

strategy: full-scope (no theatre splitting)
axes: theatre — 8 active/watch theatres per SCEM prompt
  (Russia-Ukraine, Gaza, Sudan, Myanmar, DRC, Iran, Haiti, Sahel)
tool: web_search_20260209
max_uses: 3 (engine standard — NOT the variable under test)
beta: context-management-2025-06-27 (the variable under test)
output_structure: SCEM weekly-research-v1.0 schema (unmodified)

## Key variables vs SCEM baseline failure

| Variable | Baseline (2026-05-04 fail) | SCEM-T3 |
|---|---|---|
| Model | claude-sonnet-4-5 (prod) | claude-sonnet-4-6 (upgrade) |
| Tool version | web_search_20250305 | web_search_20260209 |
| Beta headers | none | context-management-2025-06-27 |
| max_uses | 3 | 3 (held constant) |
| Prompt | identical SHA d633bef5 | identical SHA d633bef5 |

Two variables change together (model + tool version) because
web_search_20260209 requires Sonnet 4.6. The isolating comparison is
SCEM-T3 vs SCEM-T3-control (below), not SCEM-T3 vs baseline-fail.

## Per-turn token instrumentation required

Harness must log `usage.input_tokens` after every tool_use round-trip,
written as a `turn_telemetry` array in raw/test-SCEM-T3-raw-response.json:

```json
"turn_telemetry": [
  {"turn": 1, "input_tokens": 4523, "output_tokens": 892,
   "tool_uses_so_far": 0, "compaction_fired": false},
  {"turn": 2, "input_tokens": 48211, "output_tokens": 1104,
   "tool_uses_so_far": 1, "compaction_fired": false},
  {"turn": 3, "input_tokens": 31892, "output_tokens": 1340,
   "tool_uses_so_far": 2, "compaction_fired": true}
]
```

`compaction_fired: true` when input_tokens_this_turn < input_tokens_prior_turn
+ last_tool_result_size, i.e. the beta observably reduced context.

## Success criteria

1. stop_reason: end_turn AND parsed_ok: true.
2. theatres_covered >= 6.
3. No single turn's input_tokens exceeds 180,000.
4. At least one `compaction_fired: true` event in turn_telemetry.
5. Total server_tool_uses >= 3.

## Failure modes

- Silent stall at 900s again → beta did not prevent inter-turn
  accumulation. Escalate to SCEM-T4 (4+4 theatre split).
- `compaction_fired` never true → beta header sent but not honoured.
  Verify request_payload.json contains the header.
- Prose output instead of JSON → thinking-block signature break.
  Escalate to Anthropic support with request_payload.json + turn_telemetry.
- theatres_covered < 6 → compaction may be too aggressive. Check
  Anthropic docs for compaction trigger threshold tuning.

## Expected cost shape

SCEM-T3 with Sonnet 4.6 + web_search_20260209: ~$1.50–2.30 per run.
If cost > $3 despite theatres_covered<8: economics favour SCEM-T4.

## Prerequisite

PR lab-plumbing-CP-1 must be merged before dispatch.

## Follow-on decision tree

Pass (all criteria): KH-WS-005 → "validated". Fleet propagation sprint.
Pass (cost > $3): Compare vs SCEM-T4 on economics.
Fail (silent stall): SCEM-T4 mandatory.
Fail (prose/signature break): Beta adoption blocked; escalate Anthropic.

## Control variant

See SCEM-T3-control.md in this directory — runs immediately after T3.

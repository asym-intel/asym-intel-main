---
test_id: SCEM-T3-control
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
  With context-management beta OFF and web_search_max_uses forced to 1,
  does SCEM's 8-theatre prompt still overflow or stall? If it passes
  cleanly: the SCEM failure mode is INTER-turn accumulation and
  context-management is the correct fix. If it still fails: the failure
  is INTRA-turn density and context-management cannot save it —
  scope-splitting (SCEM-T4) becomes mandatory regardless of beta.

scoreboard_columns: "label,role,monitor,model,provider,tokens_input,tokens_output,server_tool_uses,runtime_seconds,parsed_ok,theatres_covered,signals_total,single_turn_input_tokens"

evidence_artefacts: "raw/test-SCEM-T3-control-raw-response.json,raw/test-SCEM-T3-control-request-payload.json,outputs/test-SCEM-T3-control-parsed.json"

pass_threshold: >
  DIAGNOSTIC — pass/fail asymmetry is the whole point.
  "Pass" (parsed_ok + stop_reason=end_turn + single_turn_input_tokens<180k):
    → Inter-turn accumulation confirmed as failure mechanism.
    → SCEM-T3 result interpretation: beta is the right fix.
  "Fail" (overflow / stall / prose output):
    → Intra-turn density confirmed as additional failure mechanism.
    → SCEM-T4 scope-split mandatory for production regardless of beta.

scoreboard_count_fields:
  developments_count: conflict_updates
  candidates_count: open_findings

provider_config_override:
  tool_choice:
    type: auto
  max_uses: 1
  # NO beta_headers — control variant MUST NOT enable context-management.

experimental_flags:
  enable_context_management: false
  enable_count_tokens_preflight: true
---

# Test SCEM-T3-control — intra-turn vs inter-turn density isolation

## Doctrine anchor

Paired control for SCEM-T3. context-management beta clears old tool_results
BETWEEN turns. It cannot rescue a single turn whose tool_result alone
exceeds cap. Running max_uses=1 bounds the test to exactly one tool
invocation and isolates intra-turn token cost.

## Hypothesis

If SCEM's failure is purely inter-turn (accumulated tool_results across
3 search uses), then max_uses=1 eliminates the accumulation vector and
the run should complete cleanly — single_turn_input_tokens should be
prompt (~3.5k) + one tool_result (~5k-50k) = well under any cap.

If SCEM's failure is partly intra-turn (one search returning dense
theatre data), max_uses=1 still fails or warns, proving that
context-management alone cannot solve SCEM at 8-theatre scope.

## Test design

Identical to SCEM-T3 except:
- `beta_headers: []` (no context-management)
- `provider_config_override.max_uses: 1` (single search cap)
- `allowed_domains`: unchanged

## Result interpretation matrix (paired with SCEM-T3)

| T3 result | T3-control result | Interpretation | Next step |
|---|---|---|---|
| Pass | Pass (Result A/B) | Beta works; inter-turn confirmed | Promote to fleet |
| Pass | Fail (Result D) | Beta compensates for both modes | Verify turn_telemetry; fleet-promote cautiously |
| Fail | Pass (Result A/B) | Beta doesn't help; unexpected | Diagnose |
| Fail | Fail (Result D) | Intra-turn density dominates | SCEM-T4 mandatory |

## Cost ceiling

$1 hard abort. At max_uses=1 this run is inherently cheap.

## Result shapes

- Result A: parsed_ok=true, runtime<300s, single_turn_input_tokens<50k
  → Clean pass. Inter-turn is the accumulation vector.
- Result B: parsed_ok=true but theatres_covered<4
  → Model didn't overflow but single search insufficient for coverage.
  Inter-turn still the accumulation vector; SCEM-T3 should work.
- Result C: stop_reason=pause_turn or continuation-prose
  → Model wanted more searches. Re-run with max_uses=2 to narrow.
- Result D: overflow/stall even at max_uses=1
  → Intra-turn density is a real failure mechanism. SCEM-T4 mandatory.

## Why this pair is worth the extra $1

Without the control, a SCEM-T3 fail is ambiguous:
- Was beta off by default?
- Was header not honoured?
- Was intra-turn density the problem all along?

Combined with request_payload logging (PR lab-plumbing-CP-1) which
eliminates the first two ambiguities, we get an unambiguous diagnostic
for ~$3.50 total across the pair.

## Prerequisite

PR lab-plumbing-CP-1 must be merged. Run immediately after SCEM-T3.

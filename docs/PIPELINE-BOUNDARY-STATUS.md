# Pipeline boundary — status as of 2026-05-05

This document records the state of the provider-call boundary inside the `pipeline/` directory as of the close of Sprint CS-min (2026-05-05). It is intended for a fresh architect or operator opening the repo cold and asking: "what does the engine boundary mean, and what sits outside it?" The doc is a snapshot, not a maintained registry. Future sprints update it in place when the underlying state changes; until then it is the canonical answer.

## Canonical engine surface

`pipeline/engine/**` is the only sanctioned surface for direct provider calls, enforced by `tools/no_direct_provider_calls.py` (introduced in Sprint CS-min, BRIEF CS-2, PR #270). The gate scans every Python file under `pipeline/engine/` and fails CI if any file outside that directory makes a direct provider call; the full rule set lives in `tools/no_direct_provider_calls.py`.

## Why the boundary is narrow

During CS-2's first-pass scan, the audit found that the 43 pre-engine `pipeline/**` files belong to at least three distinct populations that were not separable without more time and signal than Sprint CS-min had. Some files carry explicit "preserved for direct invocation" headers — they are legacy entry points retained on purpose so lab/debug workflows keep working. Others are active, scheduled production workflows (e.g. `collect.py` instances across eight monitors, `cross-monitor-synthesiser.py`, and `financial-integrity-synthesiser.py`, the last of which was manually dispatched on 2026-05-05). A third group may be dead residue (e.g. seven of the eight per-monitor `<abbr>-chatter.py` files appear superseded by `pipeline/chatter/unified-chatter.py`). Because the sprint could not safely tell these populations apart within scope, it did not attempt to classify, shim, or remove any of the 43 files. The narrow gate avoids forcing a classification before the audit happens.

## Files outside the gate (deferred audit)

The following 43 files were surfaced during CS-2's first-pass scan. None have been classified; the status column reflects that.

| path | category | status |
|------|----------|--------|
| `pipeline/monitors/ai-governance/agm-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/ai-governance/agm-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/ai-governance/collect.py` | collect | unclassified |
| `pipeline/monitors/ai-governance/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/conflict-escalation/collect.py` | collect | unclassified |
| `pipeline/monitors/conflict-escalation/daily/scem-daily-test.py` | daily test script | unclassified |
| `pipeline/monitors/conflict-escalation/scem-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/conflict-escalation/scem-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/conflict-escalation/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/democratic-integrity/collect.py` | collect | unclassified |
| `pipeline/monitors/democratic-integrity/wdm-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/democratic-integrity/wdm-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/democratic-integrity/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/environmental-risks/collect.py` | collect | unclassified |
| `pipeline/monitors/environmental-risks/erm-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/environmental-risks/erm-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/environmental-risks/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/european-strategic-autonomy/collect.py` | collect | unclassified |
| `pipeline/monitors/european-strategic-autonomy/esa-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/european-strategic-autonomy/esa-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/european-strategic-autonomy/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/fimi-cognitive-warfare/collect.py` | collect | unclassified |
| `pipeline/monitors/fimi-cognitive-warfare/fcw-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/fimi-cognitive-warfare/fcw-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/fimi-cognitive-warfare/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/financial-integrity/collect.py` | collect | unclassified |
| `pipeline/monitors/financial-integrity/fim-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/financial-integrity/fim-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/financial-integrity/weekly-research.py` | weekly-research | unclassified |
| `pipeline/monitors/macro-monitor/collect.py` | collect | unclassified |
| `pipeline/monitors/macro-monitor/gmm-chatter.py` | chatter (per-monitor) | unclassified |
| `pipeline/monitors/macro-monitor/gmm-reasoner.py` | reasoner | unclassified |
| `pipeline/monitors/macro-monitor/gmm-weekly-test.py` | daily test script | unclassified |
| `pipeline/monitors/macro-monitor/weekly-research.py` | weekly-research | unclassified |
| `pipeline/synthesisers/cross-monitor/cross-monitor-synthesiser.py` | synthesiser (cross-monitor) | unclassified |
| `pipeline/synthesisers/erm/environmental-risks-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/esa/european-strategic-autonomy-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/fcw/fcw-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/fim/financial-integrity-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/gmm/macro-monitor-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/scem/conflict-escalation-synthesiser.py` | synthesiser (per-monitor) | unclassified |
| `pipeline/synthesisers/test_synth_utils_v2.py` | synth test fixture | unclassified |
| `pipeline/synthesisers/wdm/democratic-integrity-synthesiser.py` | synthesiser (per-monitor) | unclassified |

Classification is deferred to the housekeeping audit (see `ops/HOUSEKEEPING-INBOX.md`, entry dated 2026-05-05).

## Open question: chatter routing

`pipeline/chatter/unified-chatter.py` currently issues `requests.post` calls to `https://api.perplexity.ai/chat/completions` directly, using `os.environ["PPLX_API_KEY"]`. This file is **excluded from the gate's scope** for Sprint CS-min — the gate covers only `pipeline/engine/**`, and `unified-chatter.py` was a deliberate out-of-scope exclusion. The open question is: should chatter route through the engine, or is chatter its own first-class surface alongside the engine? Forcing an answer in Sprint CS-min would have expanded scope beyond what the sprint could hold safely; the question is logged in the operational housekeeping inbox for the follow-up audit.

## Why the sprint paused here

Sprint CS-min stopped at the gate-and-doc deliverable because the audit revealed the engine cutover left behind a population of files whose status the sprint could not safely classify in the time available. Some of those files are legacy entry points retained on purpose — labelled in their own file headers as "preserved for direct invocation" — and some are scheduled or manually-dispatched production workflows. Removing or shimming them without a classification step risked breaking lab/debug tooling or active workflows. The conservative response was to give the gate a narrow remit it can hold honestly, document the boundary in this file, log the audit follow-up in `ops/HOUSEKEEPING-INBOX.md`, and stop. A future sprint will pick up the audit and decide per-file.

## How to extend the boundary

- **Add a directory to scope.** Edit `_SCAN_DIRS` in `tools/no_direct_provider_calls.py`. Keep the change small; one directory per sprint.
- **Add a single file to scope.** Edit `_SCAN_FILES` in the same file.
- **Migrate a pre-engine file to the engine.** That is *not* a gate change; it is a code change in `pipeline/engine/**` that adds a new dispatch entry point, plus deletion (or re-purposing) of the pre-engine file. The gate then covers the migration automatically.

## Provenance

- Authority: `AD-2026-05-05-CS`
- Companion: `BRIEF CS-2` (PR #270 on `asym-intel-main`)
- Audit follow-up: `ops/HOUSEKEEPING-INBOX.md` entries dated `2026-05-05`
- Boundary as of: `2026-05-05`

# Engine contract — how Asymmetric Intelligence runs its pipelines

**Version:** 1.0 — 21 April 2026
**Status:** Public credibility document. Summarises the technical contract every monitor's weekly pipeline adheres to, without reproducing internal engine code.
**Audience:** Analysts, journalists, peers, and evaluators who want to understand what Asymmetric Intelligence does and does not do when producing its weekly monitor briefs.

---

## What this document is for

Asymmetric Intelligence publishes seven weekly monitors (WDM, GMM, FCW, ESA, AGM, ERM, SCEM). Each is produced by a pipeline that calls large language models against published methodology. Because that pipeline is not a black box to us, it should not be a black box to readers either.

This document commits us, in public, to the engineering rules every monitor follows. These rules are enforced in code and in continuous integration on every commit. Where the underlying implementation is proprietary (engine-level code, lab extractor logic), the rule itself is still public here, so a reader can hold us to it.

**What you can verify from public artifacts:**

- What each monitor claims to cover → [`docs/methodology/{slug}-full.md`](https://github.com/asym-intel/asym-intel-main/tree/main/docs/methodology)
- What went wrong on any given week → [`pipeline/incidents/`](https://github.com/asym-intel/asym-intel-main/tree/main/pipeline/incidents)
- What structure every output conforms to → [`pipeline/schema-registry.json`](https://github.com/asym-intel/asym-intel-main/blob/main/pipeline/schema-registry.json)
- That outputs match their schema → published weekly reports in [`data/`](https://github.com/asym-intel/asym-intel-main/tree/main/data)

**What is not public:**

- The exact prompts sent to the model (competitive scope)
- The engine code that assembles and sends those prompts (competitive technique)
- Annual calibration values (updated each January; prior years retained internally)

---

## Engine principles

Every weekly-research pipeline — across all monitors — adheres to the following principles. These are engine-level rules, meaning a single engine change propagates to every monitor at once; no monitor can drift.

### 1. Prompts are versioned and dated

Every production prompt carries a version string and a last-updated date. When a rule changes at the engine level, every monitor inherits the change simultaneously. We do not run unversioned prompts.

### 2. We do not tell the model what it does not know

We explicitly avoid priming the model with "your knowledge cutoff is X" language. Our models have live web search; that is the tool we instruct them to use for any fact they do not already know. This is an engine-level rule because reasoning models can refuse tasks when primed with cutoff language.

### 3. We forbid code fences in model output

Our output contract forbids markdown code fences around the JSON response. This is not cosmetic: fences add tokens, break parsers, and drift across model versions.

### 4. We allow "thinking" blocks, and strip them deterministically

Reasoning models emit an internal "thinking" trace before the answer. We allow this block but strip it before storage and publication. The stripping rule is uniform across monitors and enforced in the engine.

### 5. The domain body of every prompt is monitor-specific; the framing is not

Each monitor's domain prompt — its role statement, its indicator taxonomy, its source tiers, its schema — is tailored to that monitor. The *framing* — how we instruct the model on working mode, output contract, retrieval discipline — is shared across all monitors. One framing change, applied once, reaches every monitor.

### 6. Citations are required; fabrication is forbidden

Every finding must cite a retrievable source URL from the monitor's declared tier list or from a credible corroborating source. If retrieval failed for a tier, the monitor's `research_coverage` field must say so. We do not accept the model refusing the task in lieu of admitting retrieval failure, and we do not accept invented citations.

### 7. Timeouts are explicit and uniform

Every weekly-research call has an explicit `(connect, read)` timeout tuple, set at the engine level from a single configuration file. No monitor can silently inherit a different timeout.

### 8. We maintain a laboratory for prompt and extractor work

Changes to prompt structure, output extractors, or model selection are tested in a laboratory environment before reaching production. The laboratory runs against the same engine the production pipeline uses, with production prompts as its baseline. A prompt or extractor does not reach production until its lab performance is documented.

### 9. Incidents are published

When a weekly run fails, partially succeeds, or produces output that did not meet schema, we log it to [`pipeline/incidents/`](https://github.com/asym-intel/asym-intel-main/tree/main/pipeline/incidents). We do not retroactively edit published reports; we publish a successor report with a link to the incident.

### 10. Schema is a public contract

Every monitor's output conforms to the versioned JSON schema at [`pipeline/schema-registry.json`](https://github.com/asym-intel/asym-intel-main/blob/main/pipeline/schema-registry.json). Schema evolution is additive within a major version. Breaking changes require a major version bump and a migration note in the incident log.

---

## What each weekly brief you read is produced by

A reader of any monitor brief — say, the [AI Governance weekly](https://asym-intel.info/monitors/ai-governance/) — is reading output produced by:

1. **A versioned prompt** built from a monitor-specific domain body plus an engine-level framing block.
2. **Annual calibration** — indicator-specific thresholds updated each January, held in an internal calibration file, injected at runtime and stamped into the output.
3. **A deep-research model call** with live web search, bounded by an explicit timeout tuple, returning structured JSON.
4. **Deterministic post-processing** — thinking-block stripping, JSON extraction with a fallback repair step, schema validation.
5. **An adversarial challenger pass** (for monitors where this is enabled) that runs a second model against the first model's output, looking for findings the synthesiser missed or over-claimed. The challenger's output is published alongside the primary brief, not folded silently into it.
6. **A deterministic publisher** that writes the report JSON, builds the Hugo brief page, and updates the monitor's index.

Steps 1, 3, and 4 are engine-level and uniform. Step 2 is monitor-specific and uses internal calibration files. Steps 5 and 6 are uniform and their outputs are public.

---

## What changed recently

Credibility documents that do not have a change log become wallpaper. Material changes to this contract will be appended here.

| Date | Change |
|---|---|
| 2026-04-21 | Initial version. Committed as part of the engine-templating migration. |

---

## Corrections and challenges

If you have spotted something in our published output that contradicts a rule in this document, or if you believe a rule should exist but does not, the right place to raise it is via a GitHub issue on [asym-intel/asym-intel-main](https://github.com/asym-intel/asym-intel-main/issues). We respond to every substantive challenge in the public issue tracker.

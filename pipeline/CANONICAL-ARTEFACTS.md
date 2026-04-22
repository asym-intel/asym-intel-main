# Canonical Artefacts Manifest

**Version:** 1.0 — 22 April 2026
**Status:** Authoritative. Single source of truth for cross-repo paired files between `asym-intel-internal` and `asym-intel-main`.
**Scope filed by:** [SCOPE-2026-04-22-002](scopes/canonical-parity-preflight-scope.md) — canonical parity preflight.
**Enforced by:** `tools/preflight_parity.py` (PARITY-001 byte-identicality + PARITY-002 pair-existence). Blocking on every push/PR on both repos.

---

## Why this file exists

Per **ENGINE-RULES §5** and `ops/PIPELINE-UPGRADE-TO-COMMON-SPEC-KNOWHOW.md`, canonical artefacts on `asym-intel-internal` are the source of truth. `asym-intel-main` carries byte-lifted copies. This has been treated as a **per-sprint discipline** ("remember to update internal first") and silently failed for newer artefact types — see SCOPE-002 Class E motivating event (commit `d968fdf` closed the instance; this manifest + preflight closes the class).

**Canonical parity is a cross-repo invariant, not a discipline.** This file + `tools/preflight_parity.py` make that invariant executable (per FE learning L-9: every rule has a validator or it isn't a rule).

---

## Parity categories

Every paired file falls into exactly one category.

| Category | Meaning | PARITY-001 (md5) | PARITY-002 (existence) |
|---|---|---|---|
| `byte-identical` | Canonical authored on internal; lifted byte-exact to main. md5 must match. | ✅ Checked | ✅ Checked |
| `structurally-derived` | Main copy is generated from canonical via a deterministic transform (e.g. template + value injection). md5 will differ by design. | ❌ Skipped | ✅ Checked |
| `canonical-only` | Lives only on internal. No live counterpart. (Domain docs, instructions, ops state.) | ❌ Skipped | ❌ Skipped |
| `pre-canonical` | Monitor has not yet been canonical-sprinted. Live side may lead canonical side. Exempt until canonical sprint lands. | ❌ Skipped | ❌ Skipped |
| `known-drift` | Time-limited allow-list entry. Canonical and live currently differ by known cause; expires at a dated milestone. Never applies to newly-landed drift. | ❌ Skipped (until expiry) | ✅ Checked |

**Category assignment rule:** if you touch a canonical artefact, the category of every paired row it belongs to must be correct at PR merge time. New `known-drift` rows require an AD entry.

---

## Byte-identical pairs (21 rows — all checked every run)

Baseline md5s captured 2026-04-22 on internal HEAD `HEAD~A` / main HEAD `HEAD~B` (recorded at preflight first-install). Preflight recomputes on every run.

| Monitor | Slot | Canonical (internal) | Live (main) |
|---|---|---|---|
| WDM | synth-prompt | `pipeline/monitors/democratic-integrity/synthesiser-prompt.txt` | `pipeline/synthesisers/wdm/democratic-integrity-synthesiser-api-prompt.txt` |
| WDM | reasoner-prompt | `pipeline/monitors/democratic-integrity/reasoner-prompt.txt` | `pipeline/monitors/democratic-integrity/wdm-reasoner-api-prompt.txt` |
| WDM | weekly-research-prompt | `pipeline/monitors/democratic-integrity/weekly-research-prompt.txt` | `pipeline/monitors/democratic-integrity/wdm-weekly-research-api-prompt.txt` |
| WDM | synth-schema | `pipeline/monitors/democratic-integrity/synthesiser-schema.json` | `pipeline/synthesisers/wdm/wdm-response-schema.json` |
| GMM | synth-prompt | `pipeline/monitors/macro-monitor/synthesiser-prompt.txt` | `pipeline/synthesisers/gmm/macro-monitor-synthesiser-api-prompt.txt` |
| GMM | reasoner-prompt | `pipeline/monitors/macro-monitor/reasoner-prompt.txt` | `pipeline/monitors/macro-monitor/gmm-reasoner-api-prompt.txt` |
| GMM | weekly-research-prompt | `pipeline/monitors/macro-monitor/weekly-research-prompt.txt` | `pipeline/monitors/macro-monitor/gmm-weekly-research-api-prompt.txt` |
| ESA | synth-prompt | `pipeline/monitors/european-strategic-autonomy/synthesiser-prompt.txt` | `pipeline/synthesisers/esa/european-strategic-autonomy-synthesiser-api-prompt.txt` |
| ESA | reasoner-prompt | `pipeline/monitors/european-strategic-autonomy/reasoner-prompt.txt` | `pipeline/monitors/european-strategic-autonomy/esa-reasoner-api-prompt.txt` |
| ESA | weekly-research-prompt | `pipeline/monitors/european-strategic-autonomy/weekly-research-prompt.txt` | `pipeline/monitors/european-strategic-autonomy/esa-weekly-research-api-prompt.txt` |
| ESA | synth-schema | `pipeline/monitors/european-strategic-autonomy/synthesiser-schema.json` | `pipeline/synthesisers/esa/esa-response-schema.json` |
| FCW | synth-prompt | `pipeline/monitors/fimi-cognitive-warfare/synthesiser-prompt.txt` | `pipeline/synthesisers/fcw/fcw-synthesiser-api-prompt.txt` |
| FCW | reasoner-prompt | `pipeline/monitors/fimi-cognitive-warfare/reasoner-prompt.txt` | `pipeline/monitors/fimi-cognitive-warfare/fcw-reasoner-api-prompt.txt` |
| FCW | weekly-research-prompt | `pipeline/monitors/fimi-cognitive-warfare/weekly-research-prompt.txt` | `pipeline/monitors/fimi-cognitive-warfare/fcw-weekly-research-api-prompt.txt` |
| AGM | synth-prompt | `pipeline/monitors/ai-governance/synthesiser-prompt.txt` | `pipeline/synthesisers/agm/ai-governance-synthesiser-api-prompt.txt` |
| AGM | reasoner-prompt | `pipeline/monitors/ai-governance/reasoner-prompt.txt` | `pipeline/monitors/ai-governance/agm-reasoner-api-prompt.txt` |
| AGM | weekly-research-prompt | `pipeline/monitors/ai-governance/weekly-research-prompt.txt` | `pipeline/monitors/ai-governance/agm-weekly-research-api-prompt.txt` |
| AGM | synth-schema | `pipeline/monitors/ai-governance/synthesiser-schema.json` | `pipeline/synthesisers/agm/agm-response-schema.json` |
| ERM | synth-prompt | `pipeline/monitors/environmental-risks/synthesiser-prompt.txt` | `pipeline/synthesisers/erm/environmental-risks-synthesiser-api-prompt.txt` |
| ERM | reasoner-prompt | `pipeline/monitors/environmental-risks/reasoner-prompt.txt` | `pipeline/monitors/environmental-risks/erm-reasoner-api-prompt.txt` |
| ERM | weekly-research-prompt | `pipeline/monitors/environmental-risks/weekly-research-prompt.txt` | `pipeline/monitors/environmental-risks/erm-weekly-research-api-prompt.txt` |
| ERM | synth-schema | `pipeline/monitors/environmental-risks/synthesiser-schema.json` | `pipeline/synthesisers/erm/erm-response-schema.json` |
| SCEM | synth-prompt | `pipeline/monitors/conflict-escalation/synthesiser-prompt.txt` | `pipeline/synthesisers/scem/conflict-escalation-synthesiser-api-prompt.txt` |
| SCEM | reasoner-prompt | `pipeline/monitors/conflict-escalation/reasoner-prompt.txt` | `pipeline/monitors/conflict-escalation/scem-reasoner-api-prompt.txt` |
| SCEM | weekly-research-prompt | `pipeline/monitors/conflict-escalation/weekly-research-prompt.txt` | `pipeline/monitors/conflict-escalation/scem-weekly-research-api-prompt.txt` |
| SCEM | synth-schema | `pipeline/monitors/conflict-escalation/synthesiser-schema.json` | `pipeline/synthesisers/scem/scem-response-schema.json` |

Row count: **26** (21 prompts + 5 schemas; FCW and GMM schemas classified elsewhere — see below).

---

## Canonical-only rows (36 rows — exempt from both checks)

These live exclusively on internal. No live counterpart exists or is expected. Preflight does not touch them.

### Domain docs + reasoner instructions (present only where canonical sprint has landed)

| Monitor | Slot | Canonical (internal) |
|---|---|---|
| WDM | synth-domain | `pipeline/monitors/democratic-integrity/synthesiser-domain.md` |
| WDM | weekly-research-domain | `pipeline/monitors/democratic-integrity/weekly-research-domain.md` |
| WDM | reasoner-instructions | `pipeline/monitors/democratic-integrity/reasoner-instructions.md` |
| WDM | reasoner-schema | `pipeline/monitors/democratic-integrity/reasoner-schema.json` |
| GMM | synth-domain | `pipeline/monitors/macro-monitor/synthesiser-domain.md` |
| GMM | weekly-research-domain | `pipeline/monitors/macro-monitor/weekly-research-domain.md` |
| GMM | weekly-research-schema | `pipeline/monitors/macro-monitor/weekly-research-schema.json` |
| GMM | reasoner-instructions | `pipeline/monitors/macro-monitor/reasoner-instructions.md` |
| GMM | reasoner-schema | `pipeline/monitors/macro-monitor/reasoner-schema.json` |
| GMM | methodology-guardrails | `pipeline/monitors/macro-monitor/methodology-guardrails.md` |
| ERM | synth-domain | `pipeline/monitors/environmental-risks/synthesiser-domain.md` |
| ERM | weekly-research-domain | `pipeline/monitors/environmental-risks/weekly-research-domain.md` |
| ERM | reasoner-instructions | `pipeline/monitors/environmental-risks/reasoner-instructions.md` |
| ERM | reasoner-schema | `pipeline/monitors/environmental-risks/reasoner-schema.json` |
| AGM | methodology-guardrails | `pipeline/monitors/ai-governance/methodology-guardrails.md` |
| FCW | synth-schema | `pipeline/monitors/fimi-cognitive-warfare/synthesiser-schema.json` |
| FIM | methodology-guardrails | `pipeline/monitors/financial-integrity/methodology-guardrails.md` |

### Per-monitor metadata (canonical-only today; migration to structurally-derived pending)

| Monitor | Slot | Canonical (internal) |
|---|---|---|
| WDM | metadata | `pipeline/monitors/democratic-integrity/metadata.yml` |
| GMM | metadata | `pipeline/monitors/macro-monitor/metadata.yml` |
| ESA | metadata | `pipeline/monitors/european-strategic-autonomy/metadata.yml` |
| FCW | metadata | `pipeline/monitors/fimi-cognitive-warfare/metadata.yml` |
| AGM | metadata | `pipeline/monitors/ai-governance/metadata.yml` |
| ERM | metadata | `pipeline/monitors/environmental-risks/metadata.yml` |
| SCEM | metadata | `pipeline/monitors/conflict-escalation/metadata.yml` |
| FIM | metadata | `pipeline/monitors/financial-integrity/metadata.yml` |

Row count: **25**.

---

## Pre-canonical rows (FIM) — 4 rows, exempt until canonical sprint

FIM has not yet been canonical-sprinted. Live artefacts exist and run (daily chatter + collector); canonical counterparts are empty. This is the reverse direction of the Class E gap (live leads canonical) and must not block parity CI. Exempt from PARITY-001 and PARITY-002 until FIM canonical sprint lands. At that point, these rows flip to `byte-identical` in the manifest.

| Abbr | Slot | Canonical path (empty today) | Live path |
|---|---|---|---|
| FIM | synth-prompt | `pipeline/monitors/financial-integrity/synthesiser-prompt.txt` | `pipeline/synthesisers/fim/financial-integrity-synthesiser-api-prompt.txt` |
| FIM | reasoner-prompt | `pipeline/monitors/financial-integrity/reasoner-prompt.txt` | `pipeline/monitors/financial-integrity/fim-reasoner-api-prompt.txt` |
| FIM | weekly-research-prompt | `pipeline/monitors/financial-integrity/weekly-research-prompt.txt` | `pipeline/monitors/financial-integrity/fim-weekly-research-api-prompt.txt` |
| FIM | synth-schema | `pipeline/monitors/financial-integrity/synthesiser-schema.json` | `pipeline/synthesisers/fim/fim-response-schema.json` |

**Flip trigger:** FIM canonical sprint landing PR. Author changes category `pre-canonical` → `byte-identical` in the same PR that authors the canonical side, enforced by scope-doc checklist.

---

## Known-drift rows (time-limited allow-list)

Time-limited entries. Each must cite the root cause and the expiry milestone. PARITY-001 logs these as "drift (allow-listed, expires \<milestone\>)" but does not fail. PARITY-002 still enforces existence.

| Monitor | Slot | Canonical | Live | Cause | Expiry |
|---|---|---|---|---|---|
| GMM | synth-schema | `pipeline/monitors/macro-monitor/synthesiser-schema.json` | `pipeline/synthesisers/gmm/gmm-response-schema.json` | Canonical authored independently before live schema was fully migrated to match. Baseline md5s diverged at manifest creation: canonical `0f5d9bb1…`, live `a91750a1…`. | GMM canonical sprint (H-6 on `ops/fe-readiness-tracker.md`). |

Row count: **1**.

**Allow-list hygiene:** A new known-drift row requires an architectural decision entry (AD) and an explicit expiry milestone. If an expiry passes without the row being resolved or re-justified, `tools/preflight_parity.py` fails. Allow-list is not a retirement home.

---

## Manifest self-reference

| Artefact | Canonical (internal) | Live (main) | Category |
|---|---|---|---|
| This file | `ops/CANONICAL-ARTEFACTS.md` | `pipeline/CANONICAL-ARTEFACTS.md` | `byte-identical` |

---

## How preflight consumes this file

`tools/preflight_parity.py` parses this file's tables by markdown structure:

1. Locate the `## Byte-identical pairs` heading, scan rows under it. Each row = one check.
2. Locate `## Canonical-only rows` — exempted from both PARITY-001 and PARITY-002.
3. Locate `## Pre-canonical rows (FIM)` — exempted from both.
4. Locate `## Known-drift rows` — exempted from PARITY-001 (md5); still checked by PARITY-002 (existence).

**PARITY-001 (md5 identicality):** for each byte-identical row, fail if `md5(canonical_path) != md5(live_path)`. Report both paths + both md5s.
**PARITY-002 (pair existence):** for each byte-identical + known-drift row, fail if only one of `canonical_path` / `live_path` exists.

Preflight runs in both repos. See `tools/preflight_parity.py` for the dual-context detection.

---

## Change log

- **2026-04-22 — v1.0 created.** Filed from SCOPE-2026-04-22-002 Class A. Baseline: 26 byte-identical + 25 canonical-only + 4 pre-canonical (FIM) + 1 known-drift (GMM synth-schema) = 56 rows total. 21/21 prompt pairs byte-identical at creation; 5/7 synth-schema pairs byte-identical, 1 canonical-only (FCW), 1 known-drift (GMM). Computer's manifest-authoring pass captured baseline md5s for every byte-identical row on clean `HEAD` of both repos.

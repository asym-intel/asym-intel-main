# Canonical Artefacts Manifest

**Version:** 1.4 — 22 April 2026
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
| GMM | synth-schema | `pipeline/monitors/macro-monitor/synthesiser-schema.json` | `pipeline/synthesisers/gmm/gmm-response-schema.json` |
| GMM | methodology-guardrails | `pipeline/monitors/macro-monitor/methodology-guardrails.md` | `pipeline/monitors/macro-monitor/methodology-guardrails.md` |
| ESA | synth-prompt | `pipeline/monitors/european-strategic-autonomy/synthesiser-prompt.txt` | `pipeline/synthesisers/esa/european-strategic-autonomy-synthesiser-api-prompt.txt` |
| ESA | reasoner-prompt | `pipeline/monitors/european-strategic-autonomy/reasoner-prompt.txt` | `pipeline/monitors/european-strategic-autonomy/esa-reasoner-api-prompt.txt` |
| ESA | weekly-research-prompt | `pipeline/monitors/european-strategic-autonomy/weekly-research-prompt.txt` | `pipeline/monitors/european-strategic-autonomy/esa-weekly-research-api-prompt.txt` |
| ESA | synth-schema | `pipeline/monitors/european-strategic-autonomy/synthesiser-schema.json` | `pipeline/synthesisers/esa/esa-response-schema.json` |
| FCW | synth-prompt | `pipeline/monitors/fimi-cognitive-warfare/synthesiser-prompt.txt` | `pipeline/synthesisers/fcw/fcw-synthesiser-api-prompt.txt` |
| FCW | reasoner-prompt | `pipeline/monitors/fimi-cognitive-warfare/reasoner-prompt.txt` | `pipeline/monitors/fimi-cognitive-warfare/fcw-reasoner-api-prompt.txt` |
| FCW | weekly-research-prompt | `pipeline/monitors/fimi-cognitive-warfare/weekly-research-prompt.txt` | `pipeline/monitors/fimi-cognitive-warfare/fcw-weekly-research-api-prompt.txt` |
| FCW | synth-schema | `pipeline/monitors/fimi-cognitive-warfare/synthesiser-schema.json` | `pipeline/synthesisers/fcw/fcw-response-schema.json` |
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

Row count: **29** (21 prompts + 7 schemas + 1 methodology-guardrails). FCW synth-schema promoted from canonical-only to byte-identical as part of v1.3 FCW canonical sprint (AD-22j) — response-schema authored byte-exact on main at the same time.

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
| ERM | synth-domain | `pipeline/monitors/environmental-risks/synthesiser-domain.md` |
| ERM | weekly-research-domain | `pipeline/monitors/environmental-risks/weekly-research-domain.md` |
| ERM | reasoner-instructions | `pipeline/monitors/environmental-risks/reasoner-instructions.md` |
| ERM | reasoner-schema | `pipeline/monitors/environmental-risks/reasoner-schema.json` |
| ESA | synth-domain | `pipeline/monitors/european-strategic-autonomy/synthesiser-domain.md` |
| ESA | weekly-research-domain | `pipeline/monitors/european-strategic-autonomy/weekly-research-domain.md` |
| ESA | reasoner-instructions | `pipeline/monitors/european-strategic-autonomy/reasoner-instructions.md` |
| ESA | reasoner-schema | `pipeline/monitors/european-strategic-autonomy/reasoner-schema.json` |
| FCW | synth-domain | `pipeline/monitors/fimi-cognitive-warfare/synthesiser-domain.md` |
| FCW | weekly-research-domain | `pipeline/monitors/fimi-cognitive-warfare/weekly-research-domain.md` |
| FCW | reasoner-instructions | `pipeline/monitors/fimi-cognitive-warfare/reasoner-instructions.md` |
| FCW | reasoner-schema | `pipeline/monitors/fimi-cognitive-warfare/reasoner-schema.json` |
| AGM | synth-domain | `pipeline/monitors/ai-governance/synthesiser-domain.md` |
| AGM | weekly-research-domain | `pipeline/monitors/ai-governance/weekly-research-domain.md` |
| AGM | reasoner-instructions | `pipeline/monitors/ai-governance/reasoner-instructions.md` |
| AGM | reasoner-schema | `pipeline/monitors/ai-governance/reasoner-schema.json` |
| AGM | methodology-guardrails | `pipeline/monitors/ai-governance/methodology-guardrails.md` |
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

Row count: **36**.

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

_No active known-drift entries. Table restored when a new drift row is authored with an AD and expiry._

Row count: **0**.

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
- **2026-04-22 — v1.4 AGM canonical sprint (Leg A — canonical files landed).** AGM advanced from 4/8 to 8/8 canonical files with the addition of `synthesiser-domain.md`, `weekly-research-domain.md`, `reasoner-instructions.md` and `reasoner-schema.json` at `pipeline/monitors/ai-governance/`. Canonical-only row count increased from 32 → 36 (+4 new AGM rows). Byte-identical row count unchanged at 29 — AGM synth-schema was already correctly classified as byte-identical in v1.3 (md5 `91497308d199a9384970508f82f7ccb7`, 14933 bytes), verified against main repo on 2026-04-22; the handover's proposed promotion was a no-op. AGM is a governance-landscape monitor with no actor axis and no MF-flag application; primary axes are capability tier T1-T4 (frontier|advanced|deployment|commoditised), regulatory framework (EU_AI_Act|US_EO_NIST|UK_voluntary|China_regs|International), deployment tier (frontier|production|open_weights|other), and governance mechanism (binding_legislation|executive_action|standards_frameworks|industry_self_governance|judicial_action|institutional_capacity). Confidence canon deliberately retains dual-scale: synth and reasoner emit cross-monitor 4-tier `Confirmed|High|Assessed|Possible` while `methodology-guardrails.md` keeps the AGM-specific challenger scale `Confirmed|Probable|Uncertain|Speculative` — these address different consumers (downstream pipeline vs. internal challenger review) and are NOT collapsed (AD-22l). Source hierarchy remains AGM-specific 3-tier T1-T3 (do not expand); `reasoner-schema.json` `source_tier` enum includes T4 as no-op for cross-monitor interop but AGM never emits it. Cross-monitor routing: AGM emits to `fcw|scem|wdm|esa|gmm|erm` (full mesh minus self). Direction unified to canonical `Worsening|Stable|Improving`. Rule-3 Chinese-lab press-release discipline formalised (single-lab benchmark claims cap at Assessed; `needs_independent_eval` flag surfaced to reasoner). Rule-5 durability flag mandatory on every regulatory finding (`durable|revocable|non-binding`) with reasoner Gate 5 capping revocable-instrument milestone promotions at High confidence. Advances H-2 on `ops/fe-readiness-tracker.md` from 5/7 → 6/7 (SCEM is the remaining outlier with real `sonar-pro/16384` config — a genuine config case, not a docstring drift). Config lift (AGM `sonar-pro/16384` header docstring drift → true `sonar-deep-research/32768` defaults) follows in Leg B1 paired-merge under AD-22e, along with paired docstring-normalisation fix on the synth-prompt `# MODEL:` line on internal. Class-level finding: GMM header docstring carries the same `sonar-pro` vs. `sonar-deep-research` drift (inherited before pipeline standardisation); logged to `engine-knowhow-inbox.md` for a separate GMM-docstring-fix cleanup. New totals: 29 byte-identical + 36 canonical-only + 4 pre-canonical (FIM) + 0 known-drift = 69 rows.
- **2026-04-22 — v1.3 FCW canonical sprint (Leg A — canonical files landed).** FCW advanced from 4/8 to 8/8 canonical files with the addition of `synthesiser-domain.md`, `weekly-research-domain.md`, `reasoner-instructions.md` and `reasoner-schema.json` at `pipeline/monitors/fimi-cognitive-warfare/`. FCW synth-schema promoted from `canonical-only` to `byte-identical` at the same time — response-schema authored byte-exact on main under Leg B1 paired-merge (AD-22e, AD-22j). Canonical-only row count increased from 28 → 32 (+4 new FCW rows; −1 FCW synth-schema promoted away). Byte-identical row count increased from 28 → 29 (+1 FCW synth-schema promoted in). FCW is the suite's parent monitor for multi-actor FIMI attribution — `cross_monitor_candidates[]` swept to full-mesh six-target scope (wdm|scem|esa|gmm|agm|erm), retiring the legacy four-target scope; `confidence_preliminary` swept to canonical 4-tier `Confirmed|High|Assessed|Possible` on `cross_monitor_candidates[]` (AD-22h canon extension to FCW); actor canon formalised as six primary actors (RU|CN|IR|GULF|US|IL) plus COMMERCIAL with `client_attribution: attributed|unattributed` sub-dimension plus UNKNOWN pre-attribution tier — no context-actor tier on FCW (methodology §Actor Inclusion Criteria commits to all six as equal-standard); direction unified to `Worsening|Stable|Improving`. MF-flag application discipline formalised in reasoner Gate 2 with MF2 aggressive-downgrade on content-alignment-only attribution claims. Advances H-2 on `ops/fe-readiness-tracker.md` from 4/7 → 5/7. New totals: 29 byte-identical + 32 canonical-only + 4 pre-canonical (FIM) + 0 known-drift = 65 rows.
- **2026-04-22 — v1.2 ESA canonical sprint (Leg A — canonical files landed).** ESA advanced from 4/8 to 8/8 canonical files with the addition of `synthesiser-domain.md`, `weekly-research-domain.md`, `reasoner-instructions.md` and `reasoner-schema.json` at `pipeline/monitors/european-strategic-autonomy/`. Canonical-only row count increased from 24 → 28. Reasoner body and `cross_monitor_candidates` swept to four-tier confidence canon `Confirmed|High|Assessed|Possible`; actors aligned to four-actor canon `RU|CN|US|IL` with Turkey/Gulf/Belarus/Iran demoted to a separate `context_actors` posture-flag tier; direction unified to `Worsening|Stable|Improving`; stress to four-tier `Green|Amber|Red|Crisis`. Dual-axis domain model preserved and documented in `reasoner-instructions.md` — 6-domain ECFR taxonomy (security-defence, economy-tech, climate-energy, migration, democracy-rule-of-law, external-action) is used for the synthesiser brief surface, while the 5-domain persistent-state axis (defence, energy, tech, trade, diplomatic) remains the scoring axis for the reasoner's per-domain stress and direction fields. This is an additive landing: no live counterparts affected, no parity class flipped. Config lift (sonar-pro/16384 → sonar-deep-research/32768) follows in Leg B1 paired-merge under AD-22e. Advances H-2 on `ops/fe-readiness-tracker.md` from 3/7 → 4/7. New totals: 28 byte-identical + 28 canonical-only + 4 pre-canonical (FIM) + 0 known-drift = 60 rows.
- **2026-04-22 — v1.1 GMM canonical sprint (Phase A1).** Retired the only known-drift row. GMM synth-schema flipped `known-drift` → `byte-identical` after canonical alignment of vocabulary with live JSON Schema: direction unified to `Worsening|Stable|Improving`; asset_outlook.conviction split to four distinct enum values `HIGH|MEDIUM|LOW|BIFURCATED`; confidence_preliminary unified to four-tier `Confirmed|High|Assessed|Possible` on lead_signal, key_judgments and cross_monitor_candidates; stress_level extended to four-tier `Green|Amber|Red|Crisis` on indicator_domains and credit_stress; tail_risks.direction retained as `Increasing|Stable|Decreasing` (risk magnitude, semantically distinct). Schema and synth prompt swept together under paused-cron conditions so both sides agree. Separately, GMM methodology-guardrails reclassified `canonical-only` → `byte-identical` after audit confirmed it already exists at the same path on both repos with md5 `b4cfa56cd3c04a50f56bf0ec7c2c5588` (12727 bytes). New totals: 28 byte-identical + 24 canonical-only + 4 pre-canonical (FIM) + 0 known-drift = 56 rows. Closes H-6 on `ops/fe-readiness-tracker.md`. Preflight now checks 29 paired rows (28 byte-identical + 1 manifest self-reference), with 28 exempt.

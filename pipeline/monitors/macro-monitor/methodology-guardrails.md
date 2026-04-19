# GMM Methodology Guardrails — Challenger Reference

**Monitor:** Global Macro Monitor (GMM)
**Slug:** `macro-monitor`
**Consumed by:** `pipeline/challengers/run_challenger.py` as `{{GUARDRAIL_BLOCK}}`
**Last updated:** 2026-04-19
**Primary methodology source:** `docs/methodology/macro-monitor-full.md` (v2.0, 2026-03-30)

This file is monitor-specific methodological context for the adversarial challenger. It codifies the source hierarchy, domains, flags, blind spots, documented false-positive patterns, and house rules the challenger must cite when flagging claims in a weekly GMM brief. The cross-monitor Confidence Tier Standard v1.0 (Confirmed / High / Assessed / Possible) is defined in the challenger skeleton; this file defines what counts as T1/T2/T3/T4 **for GMM specifically**.

---

## 1. Source Hierarchy (GMM)

Four tiers. When the challenger verifies a brief claim against its cited source, it must classify the source into one of these tiers.

### Tier 1 — Supranational institutional and primary central bank

FOMC / Federal Reserve statements, ECB, BoE, BoJ, PBOC, RBI official publications. IMF (WEO, GFSR, COFER), BIS (quarterly review, working papers, effective exchange rate data), World Bank (GEP, IDS). US Treasury (TIC data, quarterly refunding), CBO scoring reports. These are the evidentiary gold standard for macro claims. Always cited first; always linked to the specific document, data release, or minute.

### Tier 2 — Official national statistics and regulator releases

BLS (employment, CPI, PPI), BEA (GDP, trade, personal income), Fed H.6 / H.8 / SLOOS, St. Louis Fed FRED series (STLFSI4 et al), Chicago Fed NFCI, FDIC, FINRA margin statistics, SEC filings, ESMA, FCA, JFSA, PBOC monthly data, OECD, Eurostat. National central bank subsidiary data series. The workhorse tier for indicator values.

### Tier 3 — Established financial press and standing data providers

Bloomberg, Reuters, FT, WSJ, Nikkei, Handelsblatt wire reporting with named reporters and on-the-record sources. Trepp (CRE delinquency), Cass Freight Index, FactSet consensus, CBOE data, Windward / Kpler shipping data, ICE / LSEG data series. University of Michigan consumer surveys. Strong for pattern confirmation; should be cross-checked against a T1-T2 source before a "Confirmed" confidence label is used.

### Tier 4 — Sell-side research and policy think tanks

Goldman Sachs Global Investment Research, Morgan Stanley, JPM, Deutsche Bank research notes. PIIE, Brookings, Atlantic Council, RAND, IIF research (as opposed to IIF Global Debt Monitor which is T1-adjacent), Baker Botts tariff tracker, CSIS, ECFR, Chatham House. Useful for framework and interpretation; insufficient alone to support "Confirmed" or "High" confidence on a factual claim.

**Unranked (cite but do not rely on):** X/Twitter posts, anonymous blog posts, LLM-generated summaries of primary sources, press releases without underlying data.

### Tier verification rule

If the brief cites a source the challenger cannot place in tiers 1-4, the challenger records `source_tier: unknown` and flags the finding under category `source_unverifiable` or `source_misattribution` depending on whether the source itself can be found via web search.

---

## 2. Six Indicator Domains

Every GMM claim about "stress" or "deterioration" must map to at least one of these domains. A claim that doesn't is out of scope for GMM.

| # | Domain | Slug | Core indicators (subset) |
|---|--------|------|-------------------------|
| 1 | Debt and Sovereign | `domain_1_debt_sovereign` | US debt/deficit, Japan JGB yields, EM sovereign spreads, custody migration, gold/reserve ratio |
| 2 | Banking and Credit | `domain_2_banking_credit` | Fed SLOOS, CRE/CMBS delinquency, G-SIB capital, private credit / NBFI |
| 3 | Market Structure | `domain_3_market_structure` | VIX term structure, Treasury market liquidity, margin debt, FX swap basis, M2 money supply |
| 4 | Real Economy | `domain_4_real_economy` | ISM PMI, jobless claims, Cass Freight, consumer confidence, earnings revisions |
| 5 | Composite Indices | `domain_5_composite_indices` | STLFSI, NFCI, IIF global debt, 0DTE volume ratio |
| 6 | Amplifiers | `domain_6_amplifiers` | Trump tariffs, oil supply shock, dollar weaponisation, AI infrastructure debt |

**Stress regime conjunctivity rule:** A stress regime upgrade (GREEN→AMBER, AMBER→RED, RED→CRISIS) requires corroborating evidence across **at least two domains**. A single domain moving cannot justify a regime change. If the brief's `stress_regime_preliminary.regime_delta` is non-Stable, the challenger must verify that evidence exists in `indicator_domains` across two or more distinct domains.

---

## 3. Flag and Direction Semantics

The challenger must not re-validate scoring arithmetic — the synthesiser enforces that mechanically. But the challenger must verify that **flag assignments reflect evidence** and **direction labels match source-reported trajectory**.

**Flag rules:**
- 🔴 WARNING (-1.0) — in or approaching crisis territory per the indicator-specific threshold in `docs/methodology/macro-monitor-full.md`
- 🟡 ELEVATED (-0.3) — above normal baseline, direction of concern but not critical
- 🟢 GREEN (+1.0) — within normal range

**Direction rules:**
- DETERIORATING (×1.1) — source shows worsening trajectory vs prior reading
- IMPROVING (×0.9) — source shows improvement
- STABLE or BIFURCATED (×1.0) — flat, or split between sub-components

**Aggregate-vs-sub-component rule:** If an indicator has both an aggregate reading and sub-component readings (e.g. EM aggregate spread vs Fragile Five), the scoring engine uses the aggregate flag. Sub-component flags belong in narrative commentary only. Flag the finding if the brief uses a sub-component flag in a scoring context.

---

## 4. Blind Spot Rules (automated — must be present when trigger holds)

These are deterministic rules the synthesiser is required to apply. The challenger must verify the rule was applied, not re-derive it.

### Blind Spot 1 — Earnings Suppression
**Trigger:** `earnings_revisions` flag = GREEN
**Required effect:** Tech asset class `blind_spot_warning` must contain a statement that the GREEN reading may be suppressed by buyback distortion (~$1.1T annually in share repurchases) and GAAP-to-non-GAAP adjustments.
**Finding category if missing:** `logical_inconsistency` (trigger held, rule not applied)

### Blind Spot 2 — Nominal M2 Mirage
**Trigger:** `m2_money_supply` flag = ELEVATED AND direction = DETERIORATING
**Required effect:** Crypto asset class `blind_spot_warning` must note nominal M2 expansion is thinning in real terms; Real M2 may turn negative; nominal M2 narrative support for Crypto is deteriorating.
**Finding category if missing:** `logical_inconsistency`

---

## 5. Documented False-Positive Corrections (mandatory overrides)

Four conditional overrides that the synthesiser is required to apply. The challenger verifies application.

1. **Government bonds in systemic crisis** — if `system_average < -0.70`, the Bonds asset class outlook must be overridden to UNCERTAIN and the flight-to-quality dynamic must be noted. The model correctly identifies systemic stress but bonds are the flight-to-quality beneficiary in extreme stress; mechanical scoring would be directionally wrong.

2. **Tech in fiscal/monetary expansion** — when explicit government intervention is designed to backstop a specific asset class (TARP, BTFP, CHIPS Act etc.), the intervention must be flagged as a potential false-positive generator in Tech commentary.

3. **Crypto in banking distrust** — if the banking-domain aggregate score < -0.50, note that BTC may rally as a banking alternative despite the mechanical score.

4. **Energy commodity vs equity divergence** — note that the energy score reflects commodity stress, not producer equity performance.

The challenger flags a `logical_inconsistency` finding if a trigger condition holds and the corresponding override is absent from the brief.

---

## 6. Known Failure Modes the Challenger Should Probe

### 6.1 Hormuz-flip false positive
`oil_supply_shock` is currently driven by Hormuz / shipping-lane risk. If Hormuz de-escalates between runs, the indicator can flip 🔴→🟢 and drive a large positive score delta that is a false signal of recovery — the underlying geopolitical fragility has not resolved, only the shipping manifestation. Always verify `current_driver` field and cross-check against shipping data (Windward / Kpler) and OPEC+ posture.

### 6.2 Earnings suppression concealment
Consensus forward-EPS estimates from FactSet routinely mask buyback distortion and SBC exclusion. A GREEN `earnings_revisions` reading without accompanying `blind_spot_warning` is almost always a finding.

### 6.3 Nominal vs real M2 confusion
Nominal M2 growth cited without adjacent reference to real M2 (nominal minus CPI/PCE/Core PCE) is a finding. Narrative that leans on M2 expansion as a crypto tailwind while real M2 is flat or negative is overstated.

### 6.4 Fragile Five aggregation
EM sovereign distress cited as aggregate when the narrative is actually about Fragile Five countries specifically. The brief must be explicit about which cohort it is referring to.

### 6.5 MATT framework drift
The Market Agreement to Our Themes (MATT) scores 0-10 are inherently judgemental and drift-prone. Check whether this week's MATT scores are traceable to specific IB research coverage cited in `positioning_overlay.contrarian_corner` or similar fields. Unsupported MATT shifts are a `source_unverifiable` finding.

### 6.6 Scenario probability drift without cause
`scenario_framework[].probability_delta` must be justified by a specific event or data release. Probability shifts without a named trigger are `logical_inconsistency` findings.

### 6.7 Persistent-state overreach
GMM `persistent-state.json` carries forward baselines and alerts across weeks. Claims attributed to persistent-state that are not present in the current week's synthesis are `logical_inconsistency` findings.

---

## 7. House Rules

- **No apostrophes in JSON string values.** Use "does not" not "doesn't", "this weeks" not "this week's". The synthesiser enforces this; the challenger must also enforce it in its own output.
- **All sources require a URL when one exists.** A source cited without a URL retrievable via web search is a `source_unverifiable` finding unless the source is a FOMC minute, SEC filing, or other identifiable document with a canonical reference.
- **Dates in ISO-8601** (YYYY-MM-DD). Relative dates ("last week", "earlier this month") in factual claims are `logical_inconsistency` findings — the brief's cadence makes absolute dates mandatory.
- **Confidence labels are reserved.** Only Confirmed / High / Assessed / Possible for signals. Only High / Assessed / Possible for key_judgments. Any other label (likely, probable, possible, certain, definitely) in a confidence position is a `logical_inconsistency` finding.

---

## 8. What The Challenger Should NOT Do

- Do not re-validate the schema (the synthesiser validates against `pipeline/synthesisers/gmm/gmm-response-schema.json`).
- Do not re-compute scoring arithmetic (weighted sums, system_average, probability_sum) — these are mechanical and already enforced.
- Do not second-guess the methodology itself — the challenger's job is to check whether the **brief** adheres to the methodology, not whether the **methodology** is right.
- Do not propose methodology amendments in findings. If a recurring issue points to a methodology gap, raise that separately in `notes-for-computer.md`, not inside a per-week challenger output.

---

## 9. Open Methodology Gaps (awareness only)

These are known gaps in GMM methodology v2.0. The challenger should be aware of them but treat them as context, not as findings against the brief:

- **Source tier taxonomy was not formally documented in `macro-monitor-full.md` prior to this guardrails file.** This file codifies the tiers for challenger use. Pending: lift into the canonical methodology doc.
- **No formal falsifier definitions per indicator.** Each indicator has a "What to look for" field in the methodology, but no explicit "what would prove this read wrong" clause. Until that lands, challenger judgements about confidence overstatement lean on the cross-monitor Confidence Tier Standard defaults.
- **Cross-monitor cascade tracking is aspirational.** GMM emits `cross_monitor_candidates` but the end-to-end cascade audit is deferred per `docs/audits/master-action-plan.md`.

---

*Version: guardrails-v1.0 | Monitor: macro-monitor | Author: Computer | Reference methodology: v2.0 (2026-03-30)*

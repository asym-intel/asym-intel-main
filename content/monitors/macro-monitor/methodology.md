---
title: "Methodology — Asym Intel Macro Monitor"
description: "Full methodology for the Asym Intel Macro Monitor: 24 indicators across 6 domains, 8-asset-class scoring engine, conviction model, Tactical Alerts, Blind Spot Rules, and weekly update protocol. Version 2.0, effective 25 March 2026."
date: 2026-03-18
monitor: "macro-monitor"
type: "methodology"
draft: false
---

**Methodology Version: 2.0** — Effective 25 March 2026. Introduces: direction multipliers, Metals formula update (no VIX), two-tier Tactical Alert thresholds (0.45 / 0.60).

---

## 1. Data Collection

The monitor tracks **24 indicators** across six domains, each sourced from a named primary publisher. Data is gathered weekly; each indicator receives a three-level flag relative to its documented crisis threshold.

| Domain | Indicators | Primary Sources |
|---|---|---|
| §I Debt & Sovereign | US debt/deficit, JGB yields, EM distress, custody migration, gold-reserve ratio | BPC, CBO, YCharts, World Gold Council, IIF |
| §II Banking & Credit | SLOOS, CRE delinquency, G-SIB capital, private credit/NBFI | Federal Reserve, Trepp, S&P Global, BPI |
| §III Market Structure | VIX term structure, Treasury liquidity, margin debt, FX swap basis, M2/Real M2 | CBOE, TBAC, FINRA, Reuters, Fed H.6 |
| §IV Real Economy | ISM PMI, jobless claims, Cass Freight, consumer confidence, earnings revisions | ISM, BLS, Cass, University of Michigan, FactSet |
| §V Composite Indices | STLFSI, NFCI, IIF Global Debt Monitor, 0DTE volume ratio | St. Louis Fed, Chicago Fed, IIF, CBOE |
| §VI Amplifiers | Trump tariffs, oil/supply shock, dollar weaponisation, AI infra debt | Baker Botts, Windward/Kpler, BIS, Futurum |

---

## 1a. Source Hierarchy and Precedence Rules

The Macro Monitor applies a five-tier source hierarchy to all indicator
flags and narrative items. When tiers conflict, the precedence rules below
govern which source sets the flag.

| Tier | Category | Named Sources | Rule |
|---|---|---|---|
| **T1** | **Primary Institutional Data** | Federal Reserve (SLOOS, H.6, FOMC minutes), ECB Statistical Data Warehouse, BIS Statistics, IMF World Economic Outlook, CBO Budget and Economic Outlook, OBR Economic and Fiscal Outlook, Eurostat, FDIC, EBA, SEC primary filings | **Always use.** Link directly to the primary release. Never cite analysis of a T1 release when the release itself is accessible. T1 data sets the flag; all other tiers interpret it. |
| **T2** | **Named Financial Data Providers** | Bloomberg Terminal consensus data, Refinitiv/LSEG, Kpler commodity flows, S&P Global Market Intelligence, Trepp (CRE delinquency), FINRA (margin debt), CBOE (VIX, options flow), ICE BofA indices, MarineTraffic (Hormuz/chokepoint), IIF Global Debt Monitor | Use when T1 does not publish the specific metric in real-time. Note where T2 data diverges from T1 official figures — the gap is itself a signal. |
| **T3** | **Named Research Institutions** | BIS Working Papers, Federal Reserve Bank regional research (NY, SF, Chicago, Dallas), NBER working papers, IIF research, Peterson Institute, Brookings Economic Studies, PIIE | Used for structural analysis, leading indicator interpretation, and signal framing. Not used as primary source for indicator flags unless T1/T2 do not cover the metric. |
| **T4** | **Named Specialist Media and Analysis** | FT Alphaville, Bloomberg Opinion (identified named economists), WSJ Markets (named reporters), Project Syndicate (named economists), Politico Economy, Eurointelligence, Heterodox Academy economic commentary | Used for forward intelligence and early signals. Attribution lag between T4 analysis and T1/T2 confirmation is tracked as a signal — a T4 thesis confirmed weeks later by T1 data strengthens that analyst's tier weighting. |
| **T5** | **General Financial Press** | Reuters markets, AP business, general financial press without named economists or primary data | Last resort. Never used to establish a flag. Used only for event timeline verification alongside T1/T2 primary data. Always flagged as T5 in citations. |

**Conflict Rule:** When T1 and T2 data diverge — for example, official
BLS unemployment vs. ADP private payrolls estimate, or official CPI vs.
MIT Billion Prices Project — both figures are cited, the gap is quantified
(e.g. "+0.3pp above official"), and the direction and magnitude of the gap
is treated as an analytical signal in its own right. Persistent divergence
between T1 official data and T2 market-derived data often precedes
revision of the official data series and is tracked accordingly.

**Revision Risk Flag:** Where a T1 data series has a documented history
of material revision (e.g. non-farm payrolls, GDP advance estimates),
the initial release is flagged with a revision-risk note. The flag is
cleared or updated when the revision is published.


## 2. Flag Assignment

Each indicator is assigned one of three flags based on its reading relative to its documented crisis threshold and direction of travel:

| Flag | Score | Meaning |
|---|---|---|
| 🔴 WARNING | −1.0 | In or approaching crisis territory; direction deteriorating |
| 🟡 ELEVATED | −0.3 | Above normal baseline; direction of concern but not critical |
| 🟢 GREEN | +1.0 | Within normal range; supportive or neutral |

**Dual-flag rule:** Where an indicator shows both an aggregate and a sub-component flag (e.g. EM aggregate 🟡 and Fragile Five 🔴), the scoring engine uses the **aggregate flag**. Sub-component flags appear in the prose narrative only.

**Metals note (v2.0):** Metals are driven by monetary credibility and reserve diversification — `gold_reserve_ratio_em` (0.40), `us_debt_deficit` (0.25), `oil_supply_shock` (0.15), `dollar_weaponization` (0.20). VIX is no longer an input to the Metals score.

**Source-neutral oil indicator:** `oil_supply_shock` is named for the economic effect (price level × active disruption), not the geopolitical cause. A *Current Driver* note records the active cause each week. The formula weight never changes.

---

## 3. Scoring Formula

For each of the 8 asset classes, a score **S** is computed as:

```
S = Σ ( indicator_score_i × weight_i × direction_multiplier_i )
```

Scores are capped between −1.0 and +1.0. Weights sum to 1.0 per asset class. **Weights are fixed — only the flags change week to week.**

### Direction Multipliers (v2.0)

| Direction | Multiplier |
|---|---|
| DETERIORATING | × 1.1 |
| IMPROVING | × 0.9 |
| STABLE or BIFURCATED | × 1.0 |

### Example — Real Estate

| Indicator | Flag | Score | Weight | Contribution |
|---|---|---|---|---|
| `cre_delinquency` | 🔴 | −1.0 | × 0.40 | = −0.40 |
| `private_credit_nbfi` | 🔴 | −1.0 | × 0.30 | = −0.30 |
| `fed_sloos` | 🟢 | +1.0 | × 0.15 | = +0.15 |
| `gsib_capital` | 🟡 | −0.3 | × 0.15 | = −0.045 |
| **Total S** | | | | **= −0.595 → −0.59** |

---

## 4. Outlook Labels

| Score Range | Outlook |
|---|---|
| +0.50 to +1.00 | BULLISH |
| +0.10 to +0.49 | MILD POSITIVE |
| −0.09 to +0.09 | NEUTRAL |
| −0.10 to −0.49 | MILD NEGATIVE |
| −0.50 to −1.00 | BEARISH |

---

## 5. Conviction

Conviction measures how much the component indicators agree with each other for a given asset class.

**Method:** Count the formula flags. Find the percentage in the single largest group (all-red, all-yellow, or all-green).

| Dominant Group % | Conviction |
|---|---|
| > 80% | HIGH |
| 50–80% | MEDIUM |
| No group reaches 50% | LOW — BIFURCATED |

HIGH CONVICTION means the indicators pull strongly in one direction — the outlook label is more reliable. BIFURCATED means genuinely mixed inputs; the score reflects offsetting forces, not absence of signal.

---

## 6. Tactical Alerts

Two alert tiers trigger on week-on-week score changes:

| Tier | Condition | Meaning |
|---|---|---|
| 👁 WATCH | \|Δ\| ≥ 0.45 | Meaningful shift; monitor closely |
| ⚡ CRITICAL | \|Δ\| ≥ 0.60 | Regime shift signal; act on positioning |

A CRITICAL delta requires at least one major indicator to flip between 🔴 and 🟢, or multiple simultaneous shifts — a genuine regime change, not data noise.

*Baseline: 24 March 2026. Tactical Alerts begin Week of 31 March 2026.*

---

## 7. Blind Spot Rules

Two automated checks run every week regardless of scores:

**Rule 1 — Earnings Suppression:** If `earnings_revisions` is 🟢, a warning is appended to Tech: *Score may be suppressed by buyback distortion and non-GAAP adjustments.*

**Rule 2 — Nominal M2 Mirage:** If `m2_money_supply` is 🟡 AND Direction = Deteriorating, a warning is appended to Crypto: *Nominal M2 expansion is thinning in real terms. Forward Real M2 may turn negative by Q3 2026.*

Blind spot warnings affect commentary only. The underlying score uses the mechanical flag value without discretionary adjustment.

---

## 8. Weekly Update Protocol

1. Pull live data for all 24 indicators from primary sources
2. Assign flags (🔴 / 🟡 / 🟢) vs. crisis threshold and direction of travel
3. Run scoring engine — apply fixed weights and direction multipliers
4. Compare to prior week — produce Tactical Alerts for |Δ| ≥ 0.45 and |Δ| ≥ 0.60
5. Apply blind spot rules automatically
6. Update `oil_supply_shock` Current Driver note
7. Update Sentiment & Positioning Overlay (§IX)
8. Update 360° Intelligence section (§XI)
9. Redeploy dashboard to permanent URL

*Formula weights, outlook thresholds, conviction thresholds, and Tactical Alert triggers are fixed parameters. Changes require a versioned methodology update.*

---


## 9. Cross-Monitor Signals

The Macro Monitor feeds signals to other monitors in the Asymmetric Intelligence network when a macro development has documented cross-domain impact.

| Target Monitor | Trigger |
|---|---|
| [European Geopolitical & Hybrid Threat Monitor](https://asym-intel.info/monitors/european-strategic-autonomy/dashboard.html) | Economic coercion instruments, sanctions architecture failures, or European financial sovereignty developments |
| [World Democracy Monitor](https://asym-intel.info/monitors/democratic-integrity/dashboard.html) | Economic dependency or financial coercion documented as a mechanism of democratic erosion or state capture |
| [Strategic Conflict & Escalation Monitor](https://asym-intel.info/monitors/conflict-escalation/dashboard.html) | Economic warfare signals (sanctions evasion, trade weaponisation, debt-trap leverage) escalating toward kinetic conflict risk |
| [Global Environmental Risks Monitor](https://asym-intel.info/monitors/environmental-risks/dashboard.html) | Climate finance mechanism failures, carbon market structural stress, or resource-sector credit events |
| [Global FIMI Monitor](https://asym-intel.info/monitors/fimi-cognitive-warfare/dashboard.html) | Coordinated financial disinformation campaigns or market manipulation attributed to state actors |
| [AI Governance Monitor](https://asym-intel.info/monitors/ai-governance/dashboard.html) | AI infrastructure investment flows, compute sovereignty developments, or AI-sector systemic financial risk |

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 24 Mar 2026 | Initial release. 24 indicators, 8 asset classes, fixed weights. Alert delta threshold ±0.60. |
| 2.0 | 25 Mar 2026 | Direction multipliers (×1.1/×0.9). Metals formula: VIX removed. Two-tier alerts: WATCH ≥0.45, CRITICAL ≥0.60. |

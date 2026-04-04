# Asym Intel Macro Monitor — Full Internal Methodology
**Classification:** Internal — not for publication  
**Version:** 2.0  
**Last updated:** 2026-03-30
**Maintained by:** Peter Howitt, Ramparts.gi  
**Public summary at:** https://asym-intel.info/monitors/macro-monitor/methodology/ (§XIV of dashboard)

---

## I. Purpose and Analytical Position

The Asym Intel Macro Monitor is a weekly geopolitical risk and financial stress product, not a financial advisory service. Its analytical position: track the 24 indicators that institutional finance and mainstream economics tend to lag on, and surface the structural divergences between consensus narratives and hard data before they become consensus.

The monitor's distinctive contribution is the systematic detection of what it calls "Blind Spots" — indicators that read as benign (🟢) but are structurally suppressed by artificial mechanisms (buyback distortion, nominal-vs-real confusion, government demand substitution). These are tracked and flagged separately from the scoring engine.

**Update cadence:** Weekly. Every Monday (or agreed weekly day), pull all 24 indicators, rerun scoring engine, publish dashboard.

---

## II. Full Prompt Guidance — Weekly Research Sequence

### Step 1 — Pull the 24 Indicators (45–60 min)
For each indicator, retrieve the most current published reading from its primary source. The table below documents: indicator name, primary source URL, and what to look for.

**Domain: Debt & Sovereign (§I)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| US Debt/Deficit | CBO / Bipartisan Policy Center | https://bipartisanpolicy.org/ | Current federal debt total; current FY deficit |
| Japan JGB Yields | Trading Economics / BoJ | https://tradingeconomics.com/japan/30-year-bond-yield | 30yr JGB yield (primary); also check 10yr |
| EM Sovereign (aggregate) | IMF / EMBI data | https://www.imf.org/ | EMBI GD spread; note any Fragile Five country individual spread data |
| Custody Migration | US Treasury TIC | https://ticdata.treasury.gov/ | Total foreign holdings; Japan and China share specifically |
| Gold/Reserve Ratio (EM) | World Gold Council | https://www.gold.org/ | EM central bank gold reserves as % of total; note if gold has surpassed Treasuries in any major CB |

**Domain: Banking & Credit (§II)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| SLOOS Credit Standards | Federal Reserve | https://www.federalreserve.gov/data/sloos.htm | Net % tightening C&I loans; net % tightening CRE loans |
| CRE CMBS Delinquency | Trepp / S&P Global | https://www.trepp.com/ | CMBS office delinquency rate (primary); retail and multifamily secondary |
| G-SIB Capital | Federal Reserve | https://www.federalreserve.gov/ | Any new capital requirement changes; CDS spreads for major G-SIBs |
| Private Credit/NBFI | Reuters / Bloomberg / IMF | https://www.reuters.com/ | Any new stress signals in private credit; NBFI cross-border flows |

**Domain: Market Structure (§III)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| VIX Term Structure | CBOE | https://www.cboe.com/tradable_products/vix/ | Current VIX spot; VIX futures curve (contango/backwardation) |
| Treasury Liquidity | TBAC / Treasury | https://home.treasury.gov/ | SOFR vs. IORB spread; bid-offer spreads in on-the-run Treasuries; basis trade overhang signals |
| Margin Debt | FINRA | https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics | Total FINRA member margin debit balances |
| FX Swap Basis | Reuters / Bloomberg | https://www.reuters.com/ | EUR/USD cross-currency basis swap (3-month) |
| M2 / Real Net Liquidity | Federal Reserve H.6 | https://www.federalreserve.gov/releases/h6/current/ | Nominal M2 YoY growth; compute Real M2 = Nominal M2 growth minus CPI/PCE/Core PCE |

**Domain: Real Economy (§IV)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| ISM Manufacturing PMI | ISM | https://www.ismworld.org/ | Manufacturing PMI; new orders; prices paid (for stagflation signal) |
| Jobless Claims | BLS / DOL | https://www.bls.gov/ | Weekly initial claims; 4-week moving average; note divergence from payrolls |
| Cass Freight Index | Cass Information Systems | https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes/ | Freight shipments index (primary); expenditures secondary |
| Consumer Confidence | University of Michigan | http://www.sca.isr.umich.edu/ | UMich Index of Consumer Sentiment (ICS); current conditions vs. expectations |
| Earnings Revisions | FactSet | https://www.factset.com/ | Forward 12-month EPS estimate; revision breadth (% analysts revising up vs. down) |

**Domain: Composite Indices (§V)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| STLFSI | St. Louis Fed | https://fred.stlouisfed.org/series/STLFSI4 | Current week STLFSI4; note week-on-week change and trajectory |
| NFCI | Chicago Fed | https://www.chicagofed.org/research/data/nfci/current-data | Current week NFCI; risk, credit, and leverage subindices |
| IIF Global Debt Monitor | IIF | https://www.iif.com/ | Total global debt (quarterly); debt/GDP ratio |
| 0DTE Volume Ratio | CBOE / CME | https://www.cboe.com/ | 0DTE as % of total SPX option volume |

**Domain: Amplifiers (§VI)**

| Indicator | Source | URL | What to retrieve |
|-----------|--------|-----|-----------------|
| Trump Tariffs | Baker Botts Tracker / PIIE | https://www.piie.com/research/piie-charts/2019/us-china-trade-war-tariffs-date-chart | Effective tariff rate; any new tariff announcements |
| Oil/Supply Shock | Windward / Kpler / Goldman Sachs | https://www.windward.ai/ | Brent crude price; active supply disruption status; shipping route data (Hormuz/Red Sea) |
| Dollar Weaponisation | World Gold Council / IMF | https://www.imf.org/en/Data | USD reserve share (from COFER data); trend direction |
| AI Infrastructure Debt | Goldman Sachs / Morgan Stanley / Futurum | https://www.goldmansachs.com/ | Big Five hyperscaler capex plans; any new debt issuance announcements |

### Step 2 — Assign Flags (15–20 min)
For each of the 24 indicators, assign:
- Flag: 🔴 WARNING / 🟡 ELEVATED / 🟢 GREEN
- Direction: DETERIORATING / STABLE / BIFURCATED / IMPROVING

**Flag assignment rules:**
- 🔴 WARNING (score −1.0): In or approaching crisis territory; direction deteriorating. The threshold for "crisis territory" is documented in the Indicator Scorecard for each indicator (the "Threshold" column).
- 🟡 ELEVATED (score −0.3): Above normal baseline; direction of concern but not critical
- 🟢 GREEN (score +1.0): Within normal range; supportive or neutral

**Direction multiplier rules (applied during scoring, not flag assignment):**
- DETERIORATING: ×1.1
- IMPROVING: ×0.9
- STABLE or BIFURCATED: ×1.0

**Sub-component vs. aggregate rule:** Where an indicator has both an aggregate and a sub-component flag (e.g. EM aggregate 🟡 but Fragile Five 🔴), the scoring engine always uses the aggregate flag. Sub-component flags appear in narrative commentary but not in formulas.

### Step 3 — Run Scoring Engine (20–30 min)
For each of the 8 asset classes, compute: S = Σ (indicator_score_i × weight_i × direction_multiplier_i)

**Complete asset class weight tables:**

**METALS (Gold / Silver) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| gold_reserve_ratio_em | Current flag | 0.40 | Per direction |
| us_debt_deficit | Current flag | 0.25 | Per direction |
| oil_supply_shock | Current flag | 0.15 | Per direction |
| dollar_weaponization | Current flag | 0.20 | Per direction |

*Note: VIX is NOT an input to Metals score as of v2.0. Do not revert.*

**ENERGY (Oil / Gas) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| oil_supply_shock | Current flag | 0.50 | Per direction |
| trump_tariffs | Current flag | 0.20 | Per direction |
| cass_freight | Current flag | 0.15 | Per direction |
| ism_pmi | Current flag | 0.15 | Per direction |

**BONDS (Sovereign / Long-Duration) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| japan_jgb_yields | Current flag | 0.25 | Per direction |
| us_debt_deficit | Current flag | 0.30 | Per direction |
| treasury_market_liquidity | Current flag | 0.20 | Per direction |
| stlfsi | Current flag | 0.15 | Per direction |
| ism_pmi | Current flag | 0.10 | Per direction |

**CRYPTO (Bitcoin / Digital Assets) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| m2_money_supply | Current flag | 0.40 | Per direction |
| margin_debt | Current flag | 0.15 | Per direction |
| us_debt_deficit | Current flag | 0.20 | Per direction |
| dollar_weaponization | Current flag | 0.15 | Per direction |
| zero_dte_volume | Current flag | 0.10 | Per direction |

**TECH (Hyperscalers / AI) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| ai_infra_debt | Current flag | 0.30 | Per direction |
| earnings_revisions | Current flag | 0.25 | Per direction |
| trump_tariffs | Current flag | 0.20 | Per direction |
| private_credit_nbfi | Current flag | 0.15 | Per direction |
| margin_debt | Current flag | 0.10 | Per direction |

**CONSUMER STAPLES (Defensives) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| consumer_confidence | Current flag | 0.40 | Per direction |
| trump_tariffs | Current flag | 0.20 | Per direction |
| cass_freight | Current flag | 0.15 | Per direction |
| jobless_claims | Current flag | 0.25 | Per direction |

**EM EQUITIES — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| trump_tariffs | Current flag | 0.30 | Per direction |
| oil_supply_shock | Current flag | 0.20 | Per direction |
| em_sovereign_distress | Current flag | 0.30 | Per direction |
| fx_swap_basis | Current flag | 0.20 | Per direction |

**REAL ESTATE (CRE / REITs) — Full formula:**
| Indicator | Flag | Weight | Direction multiplier |
|-----------|------|--------|---------------------|
| cre_delinquency | Current flag | 0.40 | Per direction |
| private_credit_nbfi | Current flag | 0.30 | Per direction |
| fed_sloos | Current flag | 0.15 | Per direction |
| gsib_capital | Current flag | 0.15 | Per direction |

**Outcome labels:**
| Score range | Outlook label |
|------------|--------------|
| +0.50 to +1.00 | BULLISH |
| +0.10 to +0.49 | MILD POSITIVE |
| −0.09 to +0.09 | NEUTRAL |
| −0.10 to −0.49 | MILD NEGATIVE |
| −0.50 to −1.00 | BEARISH |

**Caps:** Individual asset class scores are capped at −1.0 (floor) and +1.0 (ceiling) after applying direction multipliers.

### Step 4 — Compare to Prior Week and Trigger Alerts (5 min)
For each asset class, compute delta vs. prior week score.

**Alert tiers:**
- **👁 WATCH** (amber): |Δ| ≥ 0.45 — meaningful shift; monitor closely
- **⚡ CRITICAL** (red): |Δ| ≥ 0.60 — regime shift signal; act on positioning

**Alert output format (for each triggered alert):**
Previous score → Current score · Delta (↑ or ↓) · Which indicator(s) moved · Three most affected related asset classes to watch.

**Important:** The first week of each new edition is a baseline week. No Tactical Alerts are produced in the baseline week. Comparisons begin the following week.

### Step 5 — Apply Blind Spot Rules (5 min)
Two automated checks every week regardless of scores:

**Rule 1 — Earnings Suppression:**
If `earnings_revisions` flag = 🟢, append to Tech asset class commentary:
> ⚠️ Score may be suppressed by buyback distortion ($1.1T+ annually in share repurchases) and GAAP-to-non-GAAP adjustments (stock-based compensation excluded). Watch Q2 guidance season as potential detonation point.

**Rule 2 — Nominal M2 Mirage:**
If `m2_money_supply` flag = 🟡 AND Direction = "Deteriorating", append to Crypto asset class commentary:
> ⚠️ Nominal M2 expansion is thinning in real terms. Forward Real M2 may turn negative by Q3 2026 on current inflation pipeline (PPI 4.0% + tariff pass-through). Nominal M2 narrative support for Crypto is deteriorating.

**Important:** Blind spot warnings affect commentary only. Scores use mechanical flag values unchanged.

### Step 6 — Update Conviction Levels (5 min)
For each asset class, compute conviction:
- Count flags in the formula
- Find the % in the single largest group (all-red, all-yellow, or all-green)
- > 80% dominant group = HIGH CONVICTION
- 50%–80% = MEDIUM CONVICTION
- No group reaches 50% = LOW — BIFURCATED

### Step 7 — Update Positioning Overlay (§IX) (15–20 min)
- **Fed Funds Futures**: Pull current implied policy path from CME FedWatch or Bloomberg
- **BofA Global Fund Manager Survey**: Updated monthly (mid-month); check for new release
- **MATT Framework**: Update "Market Pricing" and "MATT Score" for each tracked theme based on current consensus positioning

### Step 8 — Update Intelligence Section (§XI) (20–30 min)
- **Contrarian Corner**: Check major IB research for views that diverge from the monitor's assessment. Document internally consistent contrarian views — do not dismiss; assess the scenario under which the contrarian view is correct.
- **Alpha Signal Extraction**: Check for underappreciated signals in the data that are not yet consensus:
  - CDX credit default swap indices (CDX.NA.IG, CDX.NA.HY) vs. S&P 500 divergence
  - Windward/Kpler maritime intelligence for Hormuz or Red Sea activity
  - Fed funds futures pricing vs. macro data divergence
  - Macquarie and non-consensus IB calls

### Step 9 — Update Current Driver Note for oil_supply_shock (2 min)
The `oil_supply_shock` indicator is named for the economic effect (price + disruption), not the cause. Each week, update the "Current Driver" note: what is actively causing the oil supply shock this week? (Iran/Hormuz, OPEC+ decision, Russian export disruption, etc.)

### Step 10 — Update Portfolio and Trade Recommendations (§XII) (15–20 min)
Review model portfolio tilts for any stance changes warranted by the new indicator data. For each stance change, document: rationale, and trigger to reverse.

### Step 11 — Update Archive Table (2 min)
Add one row to the Previous Reports table: edition number, date, overall stress level, most significant flag changes from prior week, report link.

---

## III. Conviction Model — Internal Detail

**What conviction measures:** How internally consistent the formula indicators are — how much they agree with each other.

**Bifurcated signals require qualitative judgement:** A BIFURCATED score means genuinely mixed inputs. The score is driven by offsetting forces. Do not present the outlook label as a definitive view; present it as the net result of conflicting signals and document which signals are conflicting.

**Practical bifurcation example:** Tech (as of March 2026) — earnings_revisions 🟢 (+0.25) significantly offsets the bearish signals. The score of −0.33 is not a clean bearish picture; it is the result of one large positive offsetting several negatives. The qualitative commentary should reflect this structure.

---

## IV. System Average and Overall Stress Level

The System Average (displayed in dashboard header) is the simple arithmetic mean of all 8 asset class scores.

**Overall Stress Level labels:**
| System Average | Overall Stress Level |
|----------------|---------------------|
| > 0 | LOW STRESS |
| −0.10 to 0 | NORMAL |
| −0.20 to −0.10 | ELEVATED |
| −0.35 to −0.20 | ELEVATED → HIGH |
| −0.50 to −0.35 | HIGH |
| < −0.50 | CRITICAL |

**Current baseline (March 2026):** System Average −0.55, classified as ELEVATED → HIGH (transitional label used when trajectory is toward the next tier).

**Historical context:**
| Period | System Average | Model signal | Actual outcome |
|--------|---------------|-------------|---------------|
| Non-recessionary average | +0.10 | Neutral to bullish | Normal market conditions |
| Pre-crisis median | −0.40 | BEARISH | Pre-crisis |
| SVB March 2023 | −0.60 | BEARISH | Banking −28% |
| 2022 Bond Crash | −0.74 | BEARISH | Bonds −20%, Crypto −65% |
| COVID 2020 | −0.70 | BEARISH | S&P −34% in 33 days |
| GFC 2008 | −0.79 | BEARISH | S&P −57% |
| Current Mar 2026 | −0.55 | BEARISH | TBD |

---

## V. Indicator Types — Classification

Three indicator types (displayed in scorecard):

| Type | Label | Role |
|------|-------|------|
| Strategic Anchor (SA) | Structural, slow-moving; secular regime signal | US Debt/GDP, Japan JGB, G-SIB Capital, Private Credit/NBFI, Gold Reserve Ratio, IIF Global Debt, AI Infra Debt |
| Cycle Coincident (CC) | Cyclical; moves with credit cycle and real economy | M2, ISM PMI, Jobless Claims, Cass Freight, Consumer Confidence, Earnings Revisions, STLFSI, NFCI, Trump Tariffs, Dollar Weaponisation |
| Tactical Signal (TS) | High-frequency; fast-moving; actionable | VIX, Treasury Liquidity, Margin Debt, FX Swap Basis, Oil Supply Shock, 0DTE Volume |

**Why this matters internally:** When SA indicators deteriorate, it signals a secular regime shift that may persist for years. When CC and TS indicators deteriorate simultaneously with SA deterioration, the severity is compounded. When CC/TS deteriorate but SA remains stable, this is more likely a cyclical drawdown than a structural regime shift.

---

## VI. The MATT Framework — Internal Calibration

**MATT = Market Agreement to Our Themes**

For each of our tracked warning themes, MATT Score measures how much the market has already priced it in (0–10, where 10 = fully priced, 0 = not priced at all).

**MATT Score assignment protocol:**
- 0–2 (Very Low): Theme is not discussed in mainstream IB research; institutional positioning shows no awareness; no relevant sector/asset pricing
- 3–4 (Low): Theme is acknowledged but consensus treats it as low probability; positioning partially reflects it in one but not multiple asset classes
- 5–6 (Medium): Consensus acknowledges the theme; partial pricing in relevant assets; mainstream IB coverage present but not dominant
- 7–8 (High): Theme is consensus view; majority of IB research covers it; relevant assets pricing in significant probability
- 9–10 (Fully priced): Theme is the mainstream narrative; positioning fully reflects it; limited upside to being correct — signal value is diminished

**Key insight from MATT framework:** A high MATT score means less actionable alpha from the theme — the market has already moved. A low MATT score means the theme is underpriced. The most actionable scenarios are MATT 1–3 on themes where our evidence is strong (red/amber flags).

---

## VII. Scenario Framework — Internal Probability Maintenance

Three scenarios maintained weekly with explicit probability weights:

| Scenario | Current weight | Description |
|----------|---------------|-------------|
| Base Case — Slow Burn | 55% | Grinding deterioration; no clean cascade trigger; most dangerous for risk management because it never trips stop-losses cleanly |
| De-escalation | 25% | Hormuz de-escalation + tariff retreat + AI productivity materialising; bull case |
| Fast Cascade | 20% | Hormuz closure 30+ days OR private credit redemption gate event triggers NBFI cascade |

**Probability update rule:** Probabilities are updated when a specific event materially changes the relative likelihood. Document: which scenario's probability changed, why, and by how much.

---

## VIII. Known Failure Modes

### Documented false positives (hit rate analysis)
The model has a documented false positive rate of 4/32 asset-event combinations = 12.5%. Both patterns represent structural model limitations:

1. **Government bonds in systemic crisis** (GFC 2008): Model correctly identifies systemic stress but bonds are the flight-to-quality beneficiary. The model is wrong about bonds' directional performance in extreme systemic stress. Correction: in any scenario where System Average < −0.70, override the Bonds directional outlook to UNCERTAIN and note the flight-to-quality dynamic.

2. **Tech in fiscal/monetary expansion** (COVID 2020 H2): Narrative-driven rallies powered by unprecedented fiscal and monetary stimulus can override fundamental stress signals. Correction: when government intervention is explicitly designed to backstop a specific asset class (TARP for banks, BTFP for banking sector, CHIPS Act for semiconductor demand), flag the intervention as a potential false positive generator.

3. **Crypto in banking distrust scenario** (SVB 2023): Bitcoin rallied as an alternative to failing banks — the model was bearish on crypto but the banking distrust thesis drove a rally. Correction: add a "Banking Distrust Modifier" note when banking sector score is < −0.50: "In severe banking stress, Crypto may rally as a banking system alternative — monitor BTC/banking sector correlation for sign change."

4. **Energy sector equities vs. energy commodity** (2022): The model is built around commodity/economic metrics, which can diverge from equity performance in the energy sector (commodity volatile, equity sector gains from producer profits). Correction: note explicitly that "Energy score reflects oil market stress; integrated oil producer equities may diverge."

### Over-indexing tendencies
1. **US-centric indicators**: 18 of 24 indicators are US-focused. European and Asian stress may be under-captured. EM sovereign distress and JGB yields partially correct for this, but structural European banking stress, EU sovereign stress, or Asian currency crises may not register quickly.
2. **Short-term triggers over structural anchors**: The most visible weekly movements are in Tactical Signal indicators. Resist over-updating on fast-moving TS indicators while letting SA indicators drift without attention.
3. **Hormuz/geopolitical premium**: The oil_supply_shock indicator is currently driven by Hormuz risk. If/when Hormuz de-escalates, the indicator would flip to 🟢, which could produce a large positive score delta (potential false positive for recovery). Monitor the indicator-specific current driver note carefully.

### Under-indexing tendencies
1. **Private credit cascade**: The $3T private credit market is opaque by design. NBFI stress signals are documented but the full scale of interconnections is unknown. The model flags the risk but the timing of any crystallisation is unknown.
2. **Tail risk aggregation**: The model scores asset classes individually. It does not capture cross-asset correlation breakdown scenarios (e.g. when gold, bonds, and equities all fall simultaneously as in some historical crises). The Crisis Probability Dashboard (§VIII) partially addresses this but the scoring formula cannot fully capture tail risk.

---

## IX. IP Notes — Analytical Distinctives

1. **The 24-indicator weighted sum formula with direction multipliers**: The specific selection of 24 indicators, their domain classification, the flag score values (−1.0/−0.3/+1.0), the asset-class-specific weight tables, and the direction multiplier (×1.1/×0.9/×1.0) constitute an original financial stress scoring instrument. The weight tables above are internal-only.

2. **The MATT Framework**: The systematic measurement of market-consensus agreement with each of the monitor's tracked themes is an original concept. No comparable publicly documented methodology exists in financial research.

3. **The Blind Spot Rules as automated flags**: The two automated checks (earnings suppression and nominal M2 mirage) that run regardless of scores are an original epistemic mechanism for preventing the model from producing false green signals in specific structural situations.

4. **The System Average stress level labels**: The specific thresholds and labels (ELEVATED → HIGH as a transitional label, CRITICAL below −0.50) and their calibration against historical crisis benchmarks constitute a proprietary stress classification system.

5. **Conviction calculation methodology**: The dominant-group-percentage approach to conviction (how much the formula indicators agree with each other) is an original approach to quantifying signal quality within a weighted sum framework.

6. **Indicator type classification (SA/CC/TS)**: The three-type classification of indicators as Strategic Anchors, Cycle Coincident, or Tactical Signals — with implications for how to interpret score changes — is an original analytical framework.

---

## X. Changelog Placeholder

See `/home/user/workspace/asym-intel-internal/changelogs/CHANGELOG.md` for version history.

| Version | Date | Changes |
|---------|------|---------|
| 1.0 (public) | 2026-03-24 | Initial dashboard published. 24 indicators, 8 asset classes. First baseline week (no Tactical Alerts). Metals formula updated to remove VIX. Two-tier alert system introduced (WATCH 0.45 / CRITICAL 0.60). |
| 1.0 (internal) | 2026-03-30 | Internal methodology document created. Full formula tables documented. Weekly research sequence with primary source URLs. MATT framework calibration. Blind Spot rules. Known failure modes. IP notes. |

---

*Internal document. Not for publication or distribution outside Ramparts.gi. Classification: Internal.*

---

## XI. Scoring Engine — Full v2.0 Specification

*Source of truth for the automated weekly pipeline. Last updated: 2026-03-30.*

### Flag Scores
| Flag | Base Score |
|---|---|
| 🔴 WARNING | −1.0 |
| 🟡 ELEVATED | −0.3 |
| 🟢 GREEN | +1.0 |

### Direction Multipliers
| Direction | Multiplier |
|---|---|
| DETERIORATING | × 1.1 |
| IMPROVING | × 0.9 |
| STABLE or BIFURCATED | × 1.0 |

Scores capped −1.0 to +1.0 after multiplier application.

### Formula Weights (FIXED — do not adjust without versioned update)

| Asset Class | Indicator | Weight |
|---|---|---|
| **METALS** | gold_reserve_ratio_em | 0.40 |
| | us_debt_deficit | 0.25 |
| | oil_supply_shock | 0.15 |
| | dollar_weaponization | 0.20 |
| **ENERGY** | oil_supply_shock | 0.50 |
| | trump_tariffs | 0.20 |
| | ism_pmi | 0.15 |
| | cass_freight | 0.15 |
| **BONDS** | us_debt_deficit | 0.30 |
| | japan_jgb_yields | 0.25 |
| | treasury_market_liquidity | 0.20 |
| | ism_pmi | 0.10 |
| | stlfsi | 0.15 |
| **CRYPTO** | m2_money_supply | 0.40 |
| | us_debt_deficit | 0.20 |
| | margin_debt | 0.15 |
| | dollar_weaponization | 0.15 |
| | zero_dte_volume | 0.10 |
| **TECH** | ai_infra_debt | 0.30 |
| | earnings_revisions | 0.25 |
| | trump_tariffs | 0.20 |
| | margin_debt | 0.10 |
| | private_credit_nbfi | 0.15 |
| **CONSUMER STAPLES** | consumer_confidence | 0.40 |
| | jobless_claims | 0.25 |
| | trump_tariffs | 0.20 |
| | cass_freight | 0.15 |
| **EM EQUITIES** | em_sovereign_distress | 0.30 |
| | trump_tariffs | 0.30 |
| | fx_swap_basis | 0.20 |
| | oil_supply_shock | 0.20 |
| **REAL ESTATE** | cre_delinquency | 0.40 |
| | private_credit_nbfi | 0.30 |
| | fed_sloos | 0.15 |
| | gsib_capital | 0.15 |

### Outlook Bands
| Score | Label |
|---|---|
| ≥ +0.50 | BULLISH |
| +0.10 to +0.49 | MILD POSITIVE |
| −0.09 to +0.09 | NEUTRAL |
| −0.50 to −0.10 | MILD NEGATIVE |
| ≤ −0.51 | BEARISH |

### Tactical Alert Thresholds
| Tier | Condition |
|---|---|
| WATCH | \|Δ\| ≥ 0.45 |
| CRITICAL | \|Δ\| ≥ 0.60 |

### Blind Spot Rules (Automated)
- **Rule 1 — Earnings Suppression:** if `earnings_revisions` = 🟢 → append warning to Tech score
- **Rule 2 — Nominal M2 Mirage:** if `m2_money_supply` = 🟡 AND Direction = Deteriorating → append warning to Crypto score

### Version History
| Version | Date | Changes |
|---|---|---|
| 1.0 | 24 Mar 2026 | Initial release |
| 2.0 | 25 Mar 2026 | Direction multipliers; Metals formula (no VIX); two-tier alerts (0.45/0.60) |

---

## CURRENT ARCHITECTURE — Global Macro Monitor (updated 2026-04-01)

> This section was added 2026-04-01 to reflect the current production architecture.
> The publication workflow described in earlier sections references the legacy Perplexity
> deploy_website() pipeline. The current pipeline is GitHub/Hugo via asym-intel/asym-intel-main.

### Two-Pass Commit Rule (MANDATORY — all 7 monitors)

All cron outputs are written in two separate git commits to prevent silent truncation of
large JSON payloads. Never combine into one commit.

**PASS 1** — Core/fast sections: committed immediately after research completes.
**PASS 2** — Deep/slow sections: patched onto the Pass 1 JSON via:
  `gh api /repos/asym-intel/asym-intel-main/contents/[path] --jq '.content' | base64 -d`
  → modify in Python → PUT back

After Pass 2, verify ALL required top-level keys are present before proceeding to Step 3.
If any key is missing, re-run Pass 2 — do not proceed to notify.

### Publish Guard (MANDATORY — all 7 monitors)

Before writing any JSON, verify:
1. Today is the correct publish day (day-of-week check)
2. Current UTC hour is within ±3 of the scheduled publish hour
3. The existing report-latest.json does NOT already contain today's date in meta.published

If any check fails: EXIT. Do not publish. Log the reason.
"A prompt reload is NOT a reason to publish."

### Shared Intelligence Layer — Step 0B (MANDATORY — all 7 monitors)

After loading own persistent-state, BEFORE starting research:

```bash
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/intelligence-digest.json \
  --jq '.content' | base64 -d
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/schema-changelog.json \
  --jq '.content' | base64 -d
```

Filter intelligence-digest.json for flags relevant to this monitor's domain.
Check schema-changelog.json for any new required fields added since last run.

### Current Pipeline (GitHub/Hugo — replaces legacy deploy_website)

```bash
PUBLISH_DATE=$(date +%Y-%m-%d)
# ⚠️ Filename MUST equal PUBLISH_DATE — see anti-pattern FE-019
MONITOR_SLUG="macro-monitor"
REPO=/tmp/asym-intel-main

cd /tmp && rm -rf asym-intel-main
gh repo clone asym-intel/asym-intel-main asym-intel-main -- --depth=1 --quiet
cd $REPO
git config user.email "monitor-bot@asym-intel.info"
git config user.name "Monitor Bot"

# Data files (Pass 1 then Pass 2 — see Two-Pass Rule above)
# PASS 1: write core JSON
# PASS 2: patch deep sections

# Hugo brief (⚠️ filename = PUBLISH_DATE — not tomorrow or yesterday)
cat > content/monitors/macro-monitor/${PUBLISH_DATE}-weekly-brief.md << MDEOF
---
title: "Global Macro Monitor — W/E {DATE}"
date: ${PUBLISH_DATE}T08:00:00Z
summary: "[lead signal summary]"
draft: false
monitor: "macro-monitor"
---
MDEOF

git add static/monitors/macro-monitor/data/
git add content/monitors/macro-monitor/
git commit -m "data(GMM): weekly pipeline — Issue [N] W/E ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main
```

### Schema Version

All JSON files must contain `"schema_version": "2.0"` at top level.
No future dates. No direct HTML/CSS/JS writes from cron tasks — data only.

### Monitor Accent & URLs

- Accent: #22a0aa
- Dashboard: https://asym-intel.info/monitors/macro-monitor/dashboard.html
- Data: https://asym-intel.info/monitors/macro-monitor/data/report-latest.json
- Internal spec: asym-intel/asym-intel-internal/methodology/macro-monitor-full.md

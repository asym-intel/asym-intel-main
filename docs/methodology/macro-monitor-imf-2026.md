# Global Macro Monitor — Enhancement Addendum
**Version:** 1.0  
**Date:** 2026-04-02  
**Status:** Internal — read after `macro-monitor-full-3.md` and before weekly research  
**Cron ID:** 02c25214 | Schedule: Tuesday 0800 UTC  
**Slug:** macro-monitor

---

## 1. Purpose of This Addendum

This addendum supplements `macro-monitor-full-3.md` with calibrations specific to the 2026 macro environment. As of April 2026, three structural changes have materially altered the GMM's operating conditions:

1. **Trump Tariff Escalation Phase** — The April 2, 2026 "Liberation Day" tariff package has raised the effective US tariff rate to its highest level since the 1930s. This activates a specific protocol within the GMM framework (§2).
2. **US-EU Strategic Decoupling** — The transatlantic economic relationship is undergoing a structural shift that the existing indicator set partially but not fully captures (§3).
3. **AI Capex as Macro Variable** — Hyperscaler AI infrastructure spending has reached a scale where it materially affects corporate earnings, sovereign fiscal positions (data centre incentives), and energy grid planning. It requires an explicit treatment within the GMM framework (§4).

This addendum does not alter indicator weights or the MATT framework. It adds protocol upgrades for the current environment and corrects known sources of analytical drift.

**Read order at session start:**
1. `AGENT-IDENTITIES.md` → GMM identity card
2. `macro-monitor-full-3.md` → full methodology
3. This addendum → protocol upgrades
4. `persistent-state.json` → convictionhistory, assetclassbaseline, blindspotoverrides
5. `intelligence-digest.json` → FCW MF1 flags before scoring sentimentoverlay; ESA flags for EUR assets; SCEM escalation for commodity signals

---

## 2. Tariff Shock Cascade Protocol

### 2.1 Activation Conditions

The Tariff Shock Cascade Protocol is **active** when the effective US tariff rate (weighted average across all imports) exceeds 15% AND the US has tariff disputes active with two or more of: EU, China, Canada, Mexico, Japan, South Korea simultaneously.

**As of April 2026:** Protocol is active. The April 2, 2026 tariff package has activated it.

### 2.2 Indicator Scoring Under Active Protocol

Under an active tariff shock, the following indicator re-weighting applies:

**Upgrade from TS to CC (temporary, duration: until tariff level stabilises for 8+ consecutive weeks):**
- Global trade volume indicators (WTO merchandise trade volumes)
- Corporate earnings guidance revisions in export-sensitive sectors
- PMI export orders sub-index divergence (US vs. non-US)

**New standing check (run every issue while protocol is active):**
- **Effective tariff rate tracker:** Source: USTR, Peterson Institute PIIE real-time tariff tracker. Report the current weighted average effective rate and the week-on-week change.
- **Retaliation schedule tracker:** Which trading partners have announced, enacted, or escalated retaliatory measures? Source: respective trade ministries, WTO dispute filings.
- **Sector exposure mapping:** Which of the 8 GMM asset classes are most exposed to the current week's tariff state?

| Asset class | Current tariff exposure | Signal direction |
|---|---|---|
| Tech | Software/services exempted so far; hardware vulnerable | Monitor for digital services tax retaliation |
| Consumer Staples | Agricultural tariffs bilateral with China | Commodity input cost pressure |
| Energy | Oil/LNG: US exporters benefit vs. foreign competitors; EU energy input costs | Net ambiguous — assess direction weekly |
| Metals | Steel/aluminium Section 232 tariffs active | Inflationary input cost to manufacturing |
| EM Equities | Export-oriented EMs (Vietnam, Mexico, Bangladesh) most exposed | Monitor for capital outflow and currency pressure |
| Bonds | Tariff-driven inflation expectations affect rate path | TS indicator — do not over-upgrade |
| Real Estate | Secondary effect via construction material costs | Lagged — monitor quarterly, not weekly |
| Crypto | No direct tariff exposure; risk-off environment feeds safe-haven narrative | TS indicator — apply false-positive caution |

### 2.3 Tariff Escalation Ladder — Tracking Structure

Track the tariff situation as an escalation ladder (analogous to SCEM's I1-I6 framework):

| Rung | Description | Current status |
|---|---|---|
| T1 | Announced but not yet enacted | Note but do not score |
| T2 | Enacted, retaliatory response not yet | Score as CC — trade uncertainty elevated |
| T3 | Enacted + active retaliation by ≥1 major partner | Score as CC-SA border — structural trade disruption |
| T4 | Multi-partner retaliation + WTO dispute filing | Score as SA — structural trade system stress |
| T5 | WTO DSB panel convened or US withdrawal signalled | Score as SA — potential trade system rupture |

**As of April 2026:** Assessment based on current public information — assess rung from available sources at session time and record in the `tradepolicy` field of the issue.

### 2.4 Tariff False Positive Discipline

The tariff environment creates specific false positive risks for GMM indicators:

- **VIX spikes driven by tariff news** are almost always TS. Apply `episodicflag: true` unless the spike is sustained 3+ weeks with corroborating credit spread widening.
- **Earnings guidance revisions** on tariff exposure are CC indicators, not SA. They reflect the current level of tariffs, not a structural change to the economic model.
- **Currency moves** (EUR/USD, CNY/USD, MXN/USD) driven by tariff news are TS unless the move represents a managed currency response (e.g., PBOC CNY guidance band widening) — that would be CC.
- **Dollar strength** on tariff risk-off is expected and documented. Do not treat dollar appreciation during a tariff shock as a new financial conditions tightening signal — it is embedded in the tariff regime.

---

## 3. US-EU Decoupling Framework

### 3.1 Structural Nature of the Shift

The transatlantic relationship has entered a phase of *active economic coercion*, not just policy divergence. This is analytically distinct from:
- **Normal policy divergence** (Fed/ECB different rate paths)
- **Trade disputes** (Boeing/Airbus, steel tariffs 2018-style)
- **Active economic coercion** (tariffs combined with security conditionality, platform governance pressure, dollar weaponisation, and intelligence sharing as leverage)

The third category is the 2026 situation. It has SA-level implications, not TS-level.

### 3.2 New Standing Indicators (Supplement Existing Framework)

Add the following as informal supplementary indicators (not numbered, do not replace existing 24 — these are analytical overlays):

**US-EU Decoupling Index (qualitative, assessed weekly):**
Composite of:
- Active tariff/trade disputes: US vs. EU specifically
- Technology export restrictions with EU impact
- NATO financial commitment reliability (US defence spending and Article 5 posture)
- USD/EUR clearing and SWIFT access signals
- Big Tech compliance/DSA enforcement pressure

Report as: `decouplingdirection: Accelerating | Stable | De-escalating` with a one-sentence evidence basis.

**EUR Reserve Currency Trajectory:**
- Source: ECB monthly bulletin, IMF COFER data (quarterly lag), BIS quarterly review
- Metric: EUR share of global FX reserves (rolling 4-quarter average)
- Signal: EUR share declining while USD share holds = decoupling reinforcing dollar hegemony; EUR share rising = European financial autonomy progressing

**EU Capital Markets Union Progress:**
- Source: ESMA quarterly securities markets risk outlook, ECB Capital Markets Union tracker
- Signal: CMU depth affects whether the EU can finance its own defence and infrastructure needs without US capital markets access

### 3.3 Asset Class Implications of US-EU Decoupling

| Asset class | US-EU decoupling implication | GMM scoring guidance |
|---|---|---|
| Bonds (EU) | ECB potentially forced to hold rates lower than warranted to support defence spending | CC signal — structural fiscal pressure |
| EUR/USD | Tariff war + divergent growth trajectories → EUR weakness | TS indicator — episodic unless sustained 8+ weeks |
| Metals | European steel/aluminium exposed to US Section 232 + retaliation cycles | CC signal during active tariff protocol |
| Tech (EU-listed) | DSA compliance costs + potential US Big Tech market access restrictions | Watch — not yet SA |
| Energy (EU) | US LNG dependency replacing Russian dependency — see §ESA/P2 | SA signal — structural dependency shift |
| EM Equities | Europe-heavy EM (Eastern Europe, Turkey) exposed to EU growth drag | Secondary effect — monitor quarterly |

---

## 4. AI Capex as Macro Variable

### 4.1 Scale Calibration

As of 2026, the five major US hyperscalers (Microsoft, Google, Amazon, Meta, Apple) have combined AI infrastructure capex planned at approximately $300-400bn annually. This is macroeconomically significant:
- Roughly equivalent to the annual defence spending of the entire EU
- Larger than the GDP of most individual EU member states
- A meaningful share of total US private fixed investment

This scale means that AI infrastructure spend is now a **macro indicator**, not just a sector-level data point.

### 4.2 How to Score in Existing Framework

Map AI capex signals to existing indicators as follows:

| AI capex signal | Existing GMM indicator | Scoring guidance |
|---|---|---|
| Hyperscaler capex guidance (quarterly earnings) | Domain III: Market Structure / Corporate investment | CC — reflects medium-term investment cycle |
| AI data centre energy demand growth | Domain V: Real Economy energy component | SA — structural grid capacity constraint |
| AI-driven semiconductor demand (NVIDIA/TSMC orders) | Domain III: Market Structure | CC — leading indicator for tech sector CapEx cycle |
| AI capex debt (hyperscaler borrowing for infrastructure) | Domain II: Banking Credit / Corporate debt | SA — large-scale debt issuance at elevated rates |
| Sovereign AI infrastructure incentives (EU/US government subsidies) | Domain I: Sovereign Fiscal | CC — affects fiscal baseline |

**Standalone AI Capex Watch field in JSON:**
```json
"aicapexwatch": {
  "hyperscalercombinedcapexqoq": "string — QoQ change from latest earnings",
  "direction": "Accelerating | Stable | Decelerating",
  "gridconstraintrisk": "Low | Medium | High",
  "crossmonitorflag": "boolean — flag to ERM and AGM if grid constraint risk is High"
}
```

### 4.3 Energy Wall Integration (Cross-Monitor with AGM/ERM)

When AI capex signals grid constraint risk (High):
- Cross-flag to AGM (Energy Wall forensic filter)
- Cross-flag to ERM (planetary boundary — energy systems)
- In GMM: score energy sector asset class with an annotation noting the demand-driven structural component vs. supply/price-driven component

---

## 5. Source Upgrades — 2026 Standing Checks

Add the following to GMM's standing weekly checklist:

| Source | URL | Signal type | Tier |
|---|---|---|---|
| PIIE Real-Time Tariff Tracker | `piie.com/research/piie-charts` | Effective US tariff rate | Tier 2 |
| IMF World Economic Outlook | `imf.org/en/Publications/WEO` | Global growth, fiscal forecasts (April + October editions) | Tier 1 |
| BIS Quarterly Review | `bis.org/publ/qtrpdf` | Global credit, EM capital flows, dollar hegemony | Tier 1 |
| ECB Economic Bulletin | `ecb.europa.eu/pub/economic-bulletin` | EUR conditions, bank lending survey | Tier 1 |
| CME FedWatch | `cmegroup.com/trading/interest-rates/countdown-to-fomc` | Fed rate path probability | Tier 2 — named source required |
| COFER (IMF) | `imf.org/external/np/sta/cofer` | Reserve currency shares (quarterly lag) | Tier 1 |
| ESMA Risk Dashboard | `esma.europa.eu/sites/default/files/library` | EU market risk indicators | Tier 1 |
| SemiAnalysis | `semianalysis.com` | AI chip supply chain, compute infrastructure signals | Tier 3 — verify with Tier 1/2 |
| Datacenter Dynamics | `datacenterdynamics.com` | AI infrastructure investment signals | Tier 3 — verify with Tier 1/2 |

### 5.1 IMF WEO April 2026 Integration Protocol

The IMF WEO April 2026 edition is expected in mid-April 2026. When published:
- Update all SA indicators that reference global growth forecasts
- Check whether IMF has revised the fragile frontier sovereign list — any new addition is a Tier 1 sovereign risk signal
- Check whether IMF downgraded US growth prospects — if yes, assess spillover to EU via the decoupling framework (§3)
- Check whether IMF's global trade volume forecast has shifted in response to tariff escalation
- Cross-flag to SCEM if IMF has flagged new commodity price stress in conflict-adjacent regions
- Do NOT treat WEO release as a regime-change trigger on its own — it is an SA indicator update that may confirm or modify existing conviction history, not reset it

---

## 6. MATT Framework — 2026 Recalibration Notes

The MATT (Market Agreement to Our Themes) framework measures the gap between the GMM's analytical assessment and what markets are currently pricing. Apply the following recalibration notes:

### 6.1 Currently Over-Priced Themes (Markets Ahead of Fundamentals)

These are areas where current market pricing appears to have run ahead of the underlying structural signals — meaning MATT divergence is currently *market over-pricing*:

- **US soft landing persistence** — markets pricing resilient US growth despite tariff headwinds and inverted services PMI trend. SA indicators suggest more stress than market pricing reflects.
- **AI productivity dividend priced in** — equity markets (especially US tech) pricing in productivity gains from AI that are not yet visible in aggregate productivity data.
- **Dollar reserve currency stability** — market pricing of USD assets as safe haven during tariff war may not fully reflect the long-term reserve currency diversification that tariff weaponisation incentivises.

### 6.2 Currently Under-Priced Themes (GMM Sees More Risk)

These are areas where the GMM's structural analysis suggests more risk than current market pricing reflects — MATT divergence is *GMM sees more risk*:

- **EM sovereign contagion from tariff war** — export-oriented EM sovereigns (Vietnam, Bangladesh, Cambodia, Mexico) face structural growth shocks that credit spreads have not yet fully reflected.
- **European fiscal capacity constraint for defence** — markets pricing European defence spending as additive to fiscal baseline, not as a constraint on other spending or a sovereign risk factor.
- **AI energy demand as structural input cost shock** — industrial users and grid operators have not priced the medium-term electricity demand growth from AI data centres into capex and pricing models.

### 6.3 Sentiment Overlay — FCW MF1 Flag Protocol

**Mandatory:** Before scoring the `sentimentoverlay` section, read `intelligence-digest.json` for any FCW MF1 flag (Meta-FIMI — the interference story itself may be a target of manipulation).

When FCW carries an MF1 flag relevant to a market:
- Add a note to `sentimentoverlay`: *"FCW active MF1 flag on [topic] — market sentiment in this domain may be distorted by information operations. Treat as TS signal with explicit caveat."*
- Do not suppress the sentiment reading — annotate it

---

## 7. Known Blind Spot Additions

The existing four blind spots (Government Bonds in systemic crisis, Tech in fiscal expansion, Crypto in banking distrust, Energy equity vs. commodity divergence) remain active. Add:

**BLIND SPOT 5: TARIFF-DRIVEN EARNINGS BEATS**  
During tariff escalation phases, companies with US domestic revenue and limited import exposure may report earnings beats purely because their cost base is insulated from tariff effects while revenue benefits from reduced import competition. This creates a false earnings quality signal — beat driven by tariff shelter, not underlying operational improvement. Apply when scoring the Tech and Consumer Staples asset classes during active tariff protocol.

**BLIND SPOT 6: EUROPEAN DEFENCE SPENDING AS GROWTH SIGNAL**  
European defence spending increases are being priced by some market participants as a Keynesian stimulus (government spending → growth). This conflates the composition of spending with its macroeconomic effect. Defence spending on imported platforms (F-35s, US ordnance) has limited European growth multiplier. ESA/EDIP-funded European defence procurement has higher multiplier. Disaggregate before scoring as macro positive.

---

## 8. Persistent State — Schema Additions

Add the following fields to `persistent-state.json` to support 2026 protocol upgrades:

```json
{
  "tariffescalationprotocol": {
    "active": "boolean",
    "activationdate": "YYYY-MM-DD",
    "currentrung": "integer 1-5",
    "effectivetariffrate": "float — current weighted average",
    "priorweekrate": "float",
    "activeretaliators": ["array of country codes"],
    "wtofilings": "integer — number of active WTO dispute filings"
  },
  "usdecouplingindex": {
    "direction": "Accelerating | Stable | De-escalating",
    "activedomains": ["array — Trade | Technology | Security | Finance | Platform"],
    "mattdivergence": "string — Markets Ahead | GMM Sees More Risk | Aligned"
  },
  "aicapexwatch": {
    "hyperscalercombinedcapexqoq": "string",
    "direction": "Accelerating | Stable | Decelerating",
    "gridconstraintrisk": "Low | Medium | High",
    "crossmonitorflag": "boolean"
  },
  "imfweostatus": {
    "lastversion": "string — e.g. October 2025",
    "nextexpected": "YYYY-MM-DD",
    "integrationcomplete": "boolean"
  }
}
```

---

## 9. Cross-Monitor Signal Routing Additions

Supplement the signal routing rules in `macro-monitor-full-3.md`:

| Trigger | Route to | Action |
|---|---|---|
| Tariff escalation rung ≥ T3 | ESA, SCEM | Joint crossmonitorflag — ESA: assess EU fiscal capacity constraint; SCEM: assess commodity disruption |
| EM sovereign spreads widen ≥ 150bps week-on-week | SCEM | Flag: macro stress as conflict-risk multiplier in affected region |
| AI capex watch: grid constraint risk = High | ERM, AGM | Joint crossmonitorflag — ERM: planetary boundary stress; AGM: Energy Wall forensic filter |
| EUR/USD sustained below 1.02 for 3+ consecutive weeks | ESA | Flag: EUR weakness as European financial autonomy signal |
| US-EU decoupling index direction = Accelerating for 2+ consecutive issues | ESA, WDM | Joint crossmonitorflag — strategic and political context for financial decoupling |
| IMF WEO downgrade to major sovereign | SCEM, WDM | Flag if sovereign is in SCEM active conflict roster or WDM tracker |

---

## 10. GMM-Specific Failure Mode Additions

Supplement those in `AGENT-IDENTITIES.md`:

**TARIFF HEADLINE OVERREACTION**  
Tariff announcements generate headlines, VIX spikes, and analyst commentary every week during an active escalation phase. Most individual announcements are TS events. The regime-level question is whether the structural trade architecture is changing (SA). Score the architecture, not the individual announcement.

**EUROPEAN FISCAL OPTIMISM BIAS**  
ReArm Europe, European defence bonds, NextGenEU extensions — European institutional capacity to announce fiscal instruments consistently exceeds its capacity to disburse them. The lead time between announcement and economic effect is typically 18-36 months. Do not score announced European fiscal instruments as current macro support — score disbursement velocity.

**EM HOMOGENISATION**  
The "EM Equities" asset class in the GMM framework aggregates fundamentally different sovereigns. A tariff shock affecting Vietnamese export manufacturers is not the same as a tariff shock affecting Brazilian commodity exporters. When EM Equities is the most material asset class in a given issue, disaggregate at least three sub-regions before scoring.

**GOLD AS SAFE HAVEN — FALSE STABILITY**  
Gold at elevated levels is often interpreted as a stable safe haven signal. It may instead reflect active central bank buying by sovereigns diversifying out of USD reserves — which is a structural dollar de-anchoring signal, not a safe haven signal. When gold is elevated, check BIS central bank reserve data before concluding safe-haven demand.

---

*End of GMM Enhancement Addendum v1.0*

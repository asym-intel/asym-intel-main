# V-Dem 2026 Calibration Addendum
## World Democracy Monitor — Annual Baseline Reset

**File:** `methodology/democratic-integrity-vdem-2026.md`
**Version:** 1.0
**Effective date:** 2026-03-28 (V-Dem Dataset v16 release)
**Next calibration:** March 2027 (V-Dem Dataset v17)
**Commits to:** `asym-intel/asym-intel-internal`

---

This document is read alongside `democratic-integrity-full.md`. It does not replace the
core methodology. It provides the annual V-Dem calibration layer: updated global baselines,
ERT episode flags, indicator-to-dimension mappings, and the V-Dem Watchlist 2026 as WDM
inputs. The WDM cron reads this file at Step 0B alongside `persistent-state.json`.

---

## 1. Purpose and Reading Order

The WDM operates as a real-time institutional radar sitting 6–18 months ahead of annual
index updates. V-Dem is a **lagging calibration source, not a leading signal source** — it
confirms or challenges the trajectories the WDM has been tracking in real time. The annual
V-Dem release therefore serves three functions in the WDM workflow:

1. **Baseline reset** — recalibrate each country's LDI anchor score against which weekly
   severity scoring is measured (Dimension A: LDI Trajectory)
2. **ERT episode flags** — update which countries are in formally identified autocratisation
   or democratisation episodes, calibrating the WDM's status thresholds
3. **Indicator audit** — compare the WDM's Dimension B (Institutional Breadth) assessments
   against V-Dem's top-declining-indicators list; flag any pillars the WDM under-weighted

**V-Dem lag rule (mandatory):** V-Dem Dataset v16 covers data through end-2025. It is
the best available annual calibration. It is NOT current intelligence about 2026 conditions.
Treat V-Dem LDI scores as the structural baseline; treat weekly Tier 1–3 monitoring as the
current-conditions layer. Never update a severity score downward solely because V-Dem
improved a country's score — check whether the structural conditions V-Dem measures have
actually changed since v16 was coded.

---

## 2. Global Context — 2026 Calibration Frame

The V-Dem 2026 report (Dataset v16, covering through 2025) provides the following
calibration frame for the WDM's analytical environment:

| Metric | 2025 Value | Change vs. 2024 |
|--------|-----------|-----------------|
| Global democracy level (population-weighted LDI) | Back to 1978 levels | Continued decline |
| Number of liberal democracies | 31 countries | Down from 45 in 2009 |
| Number of autocracies | 92 | First time > democracies (87) since Cold War |
| Share of population in autocracies | 74% (6 billion) | +3pp vs. prior year |
| Countries in active autocratisation episodes | 44 | Record high (ERT v16) |
| Countries in active democratisation episodes | 18 | 15-year stagnation |
| New autocratisers identified in 2025 | 10 | Includes 5 European states |
| Share of population in liberal democracies | 7% (600 million) | Lowest in 50+ years |

**WDM calibration implication:** The 2026 reference frame is structurally more pessimistic
than the prior year. Country severity scores calibrated against the 2025 global average
should be reviewed against the 2024 baseline, not the 2023 one. The threshold for what
constitutes "stable" has narrowed: a country holding its LDI score flat in this environment
is resisting a structural global current, not merely persisting.

---

## 3. USA Downgrade — Special Calibration Entry

The 2026 V-Dem report designates the USA's 2025 decline as the most significant
single-country event in the dataset. This has WDM-specific implications.

### V-Dem Assessment (Dataset v16)
- **LDI score:** 0.57 (down from 0.75 in 2024) — largest single-year LDI decline in US history
- **EDI score:** 0.74 (down from 0.84) — driven by media freedom and legislative constraint collapse
- **Regime classification:** Electoral Democracy (downgraded from Liberal Democracy for
  first time in 50+ years)
- **ERT status:** Active autocratisation episode — onset identified as 2025
- **Most affected component:** Legislative Constraints on the Executive — lost one-third of
  its value in 2025, reaching lowest point in over 100 years
- **Stable components:** Suffrage, Elected Officials, Clean Elections Index (election-year
  only; 2026 midterms not yet assessed)

### WDM Scoring Calibration — USA

| WDM Dimension | V-Dem Evidence | Calibrated Value |
|---------------|---------------|-----------------|
| **A — LDI Trajectory** | 0.75 → 0.57 (−0.18 in one year; exceeds 2.5× the average annual decline of comparable autocratisers) | 2.5 (Collapse-speed) |
| **B — Institutional Breadth** | Legislature (investigative capacity), Judiciary (independence signals), Press (freedom of expression, self-censorship, media bias all declining), Civil Society (CSO repression worsening), Civil Service (Schedule F, DOGE) = 5 of 6 pillars | 2.0 (5 pillars) |
| **C — Repression Severity** | Administrative harassment (USAID, universities, law firms, inspectors general); no mass arrests or killings documented by V-Dem v16 | 0.5 (Harassment/administrative) |
| **D — Resilience (inverted)** | Courts partially functioning (multiple injunctions); civil society mobilisation (No Kings Day, 7 million); press still operating; BUT legislative co-optation advancing | 1.0 (Moderate resilience) |

**Calibrated WDM severity score (USA):** A(2.5) + B(2.0) + C(0.5) − D(1.0) = **4.0**
**Status:** Rapid Decay (meets 2-pillar minimum; 5 pillars confirmed)
**V-Dem confirmation flag:** `vdemConfirmed: true` — this is the rare case where V-Dem's
annual score provides corroborating Tier 2 evidence for an existing WDM Rapid Decay
designation.

**Electoral watch note:** V-Dem's Clean Elections Index did not change in 2025 (evaluated
in election years only). V-Dem flags significant concerns about the 2026 midterms: federal
assertion of control over state election processes, DOJ lawsuits against 24 states, FBI action
in Fulton County, and 40% turnover among US election officials since 2020. Set
`electoralwatch.environment` to HIGH RISK for the 2026 US midterms (November 2026).

---

## 4. New European Autocratisers — 2025 ERT Identifications

V-Dem Dataset v16 identifies **five new European autocratisers** in 2025. All five are
within or adjacent to the WDM's coverage geography. Their ERT episode onset flags and
WDM calibration notes follow.

### 4.1 United Kingdom
- **V-Dem status:** Electoral Democracy, active autocratisation episode (new 2025)
- **Primary V-Dem drivers:** Freedom of academic and cultural expression (declining),
  media self-censorship (worsening), freedom of discussion
- **WDM calibration note:** UK was on WDM Watch List. V-Dem v16 confirmation upgrades
  evidentiary basis to Tier 2. Promote to Rapid Decay only if WDM Dimension B confirms
  ≥2 institutional pillars under structural (not episodic) attack. Contrast: media freedom
  concerns are real; legislature and judiciary remain partially independent. Hold at Watch
  List with elevated confidence unless weekly monitoring confirms pillar deterioration.

### 4.2 Italy
- **V-Dem status:** Liberal Democracy (−), active autocratisation episode (new 2025)
- **Primary V-Dem drivers:** Executive respect for constitution, deliberation quality
- **WDM calibration note:** Italy is on WDM Watch List. The Liberal Democracy (−)
  classification means Italy is in the grey zone — V-Dem's confidence intervals place it
  potentially at Electoral Democracy. Apply WDM's Contested Band methodology: hold
  for 2 consecutive weeks of corroborating Tier 1–3 evidence before promoting.

### 4.3 Slovakia
- **V-Dem status:** Electoral Democracy, active autocratisation episode (new 2025)
- **Primary V-Dem drivers:** Media censorship, CSO repression, executive-judiciary tension
- **WDM calibration note:** V-Dem confirmation provides Tier 2 corroboration for weekly
  signals. Slovakia's Fico government's trajectory is now formally episodic in V-Dem terms.
  Calibrate Dimension A at 1.5–2.0 (Steep decline) and review Dimension B against
  documented pillar attacks.

### 4.4 Slovenia
- **V-Dem status:** Electoral Democracy, active autocratisation episode (new 2025)
- **Primary V-Dem drivers:** Government censorship of media (noted as a top offender),
  media self-censorship — listed alongside Hong Kong and Vietnam as top decliners
- **WDM calibration note:** Slovenia also appears in the Shadow FIMI Report addendum
  (March 2026) as an active FIMI target. Cross-reference with FCW intelligence-digest.
  If FCW has an active campaign flag for Slovenia, apply `fimilink: true` to relevant
  WDM legislative watch entries.

### 4.5 Croatia
- **V-Dem status:** Electoral Democracy, active autocratisation episode (new 2025)
- **Primary V-Dem drivers:** Electoral quality concerns, deliberation quality
- **WDM calibration note:** Croatia's EU membership makes this a Rule of Law mechanism
  signal. Cross-reference with ESA monitor for EU institutional response signals.

---

## 5. ERT Methodology Integration

### What the ERT Is (and What It Is Not for the WDM)

The Episodes of Regime Transformation (ERT) methodology identifies autocratisation and
democratisation episodes by detecting cumulative change of ≥0.1 on V-Dem's Electoral
Democracy Index (EDI) within a defined window, using a conservative threshold to avoid
false positives.

**For the WDM, the ERT provides:**
- Formal confirmation that a country is in a structural episode (upgrades evidentiary weight
  of Tier 2)
- Episode start dates (useful for contextualising WDM severity score history)
- Episode classification: Stand-Alone (new decline from non-episode) vs. Bell-Turn
  (reversal from prior trend)

**The ERT does NOT provide:**
- Weekly or monthly granularity (annual data only)
- Leading indicators (it identifies episodes once they have accumulated ≥0.1 change)
- Prediction of continuation or reversal

**WDM rule:** An active ERT autocratisation flag is Tier 2 corroborating evidence for a
WDM Watch List promotion. It is not independently sufficient for Rapid Decay designation —
the WDM's real-time Dimension B (institutional breadth) assessment still determines status.

### Stand-Alone vs. Bell-Turn in WDM Context

| ERT Type | V-Dem Definition | WDM Implication |
|----------|-----------------|-----------------|
| **Stand-Alone autocratisation** | Country not previously in an episode begins declining | New onset — watch for acceleration in first 18 months (research shows first electoral cycle is decisive) |
| **Bell-Turn autocratisation** | Country reverses from a democratisation episode | Prior democratisation gains are being unwound — assess which specific gains are reverting |
| **U-Turn democratisation** | Country reverses from an autocratisation episode | Recovery designation candidate; monitor for consolidation or reversal back |
| **Stand-Alone democratisation** | Country with no prior episode begins improving | New democratiser — apply Recovery designation with 2-week confirmation |

**Current Bell-Turn cases in WDM coverage (V-Dem v16):** Argentina, Mexico
**Current U-Turn cases in WDM coverage (V-Dem v16):** Poland, Brazil, South Korea (potential)

---

## 6. V-Dem Indicator Mapping to WDM Dimensions

V-Dem's top-20 declining indicators (2015–2025) should inform which Dimension B pillars
the WDM flags as under attack. The mapping below translates V-Dem's indicator taxonomy
into the WDM's six-pillar Dimension B framework.

### Pillar Mapping

| WDM Pillar | V-Dem Indicators (Top-20 Declining, 2015–2025) | Signal Frequency |
|-----------|-----------------------------------------------|-----------------|
| **Press** | Government censorship effort — media (44 countries declining); Media self-censorship (39); Media bias (34); Harassment of journalists (34); Print/broadcast media perspectives (30); Print/broadcast media critical (31) | **Highest — 6 of top 20** |
| **Civil Society** | CSO repression (39 countries declining); CSO entry and exit control (37); Engaged society (34) | **Second highest — 3 of top 20** |
| **Legislature** | Legislative constraints on executive (21 declining); Legislature investigates in practice (31) | **2 of top 20** |
| **Judiciary** | Transparent laws with predictable enforcement (29); Rule of Law (22) | **2 of top 20** |
| **Elections** | EMB autonomy (28); Election free and fair (31) | **2 of top 20** |
| **Civil Service / Executive** | Executive respects constitution (28); Range of consultation at elite levels (37); Reasoned justification (28); Freedom from torture (33) | **4 of top 20** |

**WDM calibration implication:** Press and Civil Society are the two most globally active
attack surfaces in the current autocratisation wave. When these two pillars are under attack,
the WDM's Dimension B should reflect this — a country where only press and civil society
are under attack scores B=1.0 (2–3 pillars). When legislature and judiciary follow, score
escalates to B=2.0–2.5. This matches V-Dem's documented sequencing: freedom of
expression is "often the first domino to fall."

### The Deliberation Indicator

V-Dem's Deliberation index (declining in 26 countries) has no direct WDM pillar
equivalent. Map it to the **Civil Service** pillar as "executive-opposition dialogue quality."
When deliberation scores fall, mark the Civil Service pillar as under attack
(policy reasoning replaced by executive fiat) even before formal civil service
independence measures are legislated away.

---

## 7. V-Dem Watchlist 2026 — WDM Input

V-Dem Watchlist 2026 identifies countries that have reached ≥75% of the ERT threshold
(≥0.075 change on EDI) without formally entering an episode. These are **near-miss
autocratisers** — the WDM's equivalent of Watch List entries approaching Rapid Decay.

### Watchlist Autocratisers (dark red — ≥0.075 threshold)

| Country | WDM Coverage? | WDM Current Status | Action |
|---------|--------------|-------------------|--------|
| Bulgaria | Yes (EU member) | Check persistent-state | Add to WDM Watch List if not already present; ERT near-miss is promotion trigger |
| Cyprus | Yes (EU member) | Check persistent-state | As above — Cyprus on V-Dem Watchlist for second consecutive year |
| Namibia | Sub-Saharan Africa scope | Check persistent-state | Add if not tracked; Scout requirement per §5 Geographic Scouting |
| Portugal | Yes (EU member) | Check persistent-state | **New this year** — unexpected; Tier 2 flag; add to WDM Watch List |
| Russia | Yes | Rapid Decay (confirmed) | Already in Rapid Decay; V-Dem Watchlist is residual signal — note that V-Dem ERT considers Russia's primary autocratisation episode concluded (regime consolidated) |
| Sierra Leone | West Africa scope | Check persistent-state | V-Dem near-miss for second consecutive year; promote from near-miss to Watch List |
| Sudan | Africa scope | Check persistent-state | Likely already Rapid Decay given conflict context; verify against SCEM crossmonitor flags |
| Vanuatu | Out of primary scope | N/A | Note for context; second-largest single-year LDI drop in 2025 after USA |

### Watchlist Democratisers (potential U-turns — ≥0.075 threshold)

| Country | WDM Coverage? | WDM Current Status | Action |
|---------|--------------|-------------------|--------|
| Chad | Africa scope | Check persistent-state | Military coup reversal — fragile; apply Bell-Turn caution |
| Gabon | Africa scope | Check persistent-state | As above — civilian government re-installed post-coup |
| South Korea | Yes | Recovery (current) | Closest to qualifying as democratiser; confirm Recovery status; monitor Constitutional Court role |

---

## 8. Regional Calibration Notes

### Western Europe and North America

V-Dem 2026 records the most notable regional LDI decline of any region, driven by USA
(343M population weight) plus ongoing episodes in Italy (59M) and UK (70M). The
**region's population-weighted LDI is now at its lowest level in over 50 years.**

WDM implication: Western European country severity scores should not be benchmarked
against their own historical norms in isolation — they are deteriorating within a regional
context that is itself deteriorating. A country holding its score flat while neighbours decline
is demonstrating active resilience (Dimension D credit) not merely stability.

### Eastern Europe

Poland and Romania are V-Dem U-Turn democratisers (episodes of democratic recovery
after prior autocratisation). Both are in the WDM Recovery category. V-Dem v16
corroborates this.

Hungary and Serbia remain active autocratisation episodes. V-Dem v16 corroborates WDM
Rapid Decay designations for both.

Ukraine is listed as an active autocratisation episode. WDM should maintain Ukraine with
cross-monitor flags from SCEM (conflict-driven democratic regression) — the V-Dem
decline reflects wartime executive concentration of power, not ideological autocratisation.
Notate this distinction in the `analyticalconcern` field.

### Latin America

Argentina and Mexico are Bell-Turn autocratisers (reversing prior democratisation gains).
V-Dem v16 confirms what WDM weekly monitoring has been tracking. Brazil remains an
Electoral Democracy and U-Turn democratiser, but the bell-turn risks in the region are
shifting the population-weighted regional average back toward decline.

### Sub-Saharan Africa

V-Dem identifies a resurgence of military coups in the Sahel (Chad, Burkina Faso, Mali,
Niger) and autocratic deepening in CAR, Mozambique, and Togo. WDM's Sub-Saharan
Africa scouting requirement (§5 of core methodology) is confirmed as necessary by V-Dem
v16 data. These countries have genuine V-Dem-documented declines that are
under-represented in English-language Tier 3–4 sources.

---

## 9. Dimension A Calibration Table — 2025 LDI Anchors

V-Dem Dataset v16 provides the updated LDI baseline for Dimension A scoring. Dimension A
measures the LDI Trajectory: the rate of change from this anchor. The table below provides
calibrated anchors for WDM-covered countries where V-Dem v16 records material change.

**Reading:** The `anchor` is the 2025 LDI score. The `trajectory` is the annual change
(2024→2025). Use both to set Dimension A: the anchor contextualises the level; the
trajectory sets the rate-of-change score.

| Country | 2025 LDI | 2024→2025 Change | ERT Status | Dimension A Value |
|---------|---------|-----------------|-----------|------------------|
| USA | 0.57 | −0.18 | Active autocratisation | 2.5 (collapse-speed) |
| Hungary | ~0.28 | Continued decline | Active autocratisation | 2.0–2.5 |
| Italy | ~0.72 | Gradual decline | Active autocratisation (new) | 1.0–1.5 |
| UK | ~0.74 | Gradual decline | Active autocratisation (new) | 1.0 |
| Slovakia | ~0.60 | Moderate decline | Active autocratisation (new) | 1.5 |
| Slovenia | ~0.65 | Gradual-moderate decline | Active autocratisation (new) | 1.0–1.5 |
| Croatia | ~0.65 | Gradual decline | Active autocratisation (new) | 1.0 |
| Poland | ~0.72 | Improving | Active democratisation (U-Turn) | 0 (stable/improving) |
| South Korea | ~0.80 | Improving | Near-miss democratiser | 0 (stable) |
| Romania | ~0.60 | Improving | Active democratisation (U-Turn) | 0 |
| Brazil | ~0.62 | Stable | U-Turn consolidating | 0 |
| Argentina | ~0.55 | Declining | Active autocratisation | 1.5–2.0 |
| India | ~0.30 | Continued decline | Active autocratisation | 2.0 |
| Israel | ~0.48 | Continued decline | Active autocratisation | 1.5–2.0 |

**Note:** Approximate LDI values are derived from V-Dem Report 2026 figures and
contextual analysis. Exact country-year scores are available in V-Dem Dataset v16
at v-dem.net. Replace approximate values with exact v16 figures when loading
persistent-state for the first Monday brief following this calibration.

---

## 10. V-Dem Lag Handling — The 12–18 Month Window

V-Dem data is coded through end-2025 but published in March 2026. The WDM's function
is to detect conditions **6–18 months before annual indices register them**. This creates a
specific relationship:

- When a V-Dem score confirms what the WDM has already been tracking: **Tier 2
  corroboration** — log the confirmation in the changelog, upgrade affected entries
  from Probable to Confirmed where appropriate.
- When a V-Dem score reveals a deterioration the WDM did not track: **Gap audit** —
  investigate why the signal was missed; add the V-Dem-identified indicators to the
  weekly scouting checklist for that country.
- When a V-Dem score shows improvement that the WDM's weekly tracking did not pick up:
  **Do not downgrade** until weekly monitoring confirms the structural conditions
  V-Dem measured have actually continued to improve into 2026.

**V-Dem V16 lag note (mandatory in all brief references):** V-Dem Dataset v16 covers
through end-2025. Any reference to V-Dem data in the weekly brief must note that it
reflects conditions through December 2025, not current conditions. For countries where
significant 2026 events have occurred (e.g., elections, constitutional changes, mass
protests), explicitly note the V-Dem coverage gap and weight current-intelligence sources
accordingly.

---

## 11. Revised Source Hierarchy Entry — V-Dem

The existing WDM source hierarchy (§4 of core methodology) lists V-Dem at Tier 2
(Quantitative Indices). The following clarifications apply following the v16 release:

**V-Dem LDI and EDI scores (annual):**
- Use for: Dimension A baseline anchor, ERT episode flag, regime classification
- Do NOT use for: current-conditions scoring (12–18 month lag), event-driven updates
- Citation format: "V-Dem Dataset v16 (through 2025), LDI [score], ERT status [active/concluded]"

**V-Dem ERT episode flags:**
- Use as: Tier 2 corroborating evidence for Watch List promotion
- Weight: Equivalent to a Freedom House downgrade in the same direction
- Caveat: ERT is conservative (high false-negative rate for recent onset) — absence of ERT
  flag does not mean absence of autocratisation

**V-Dem Democracy Report 2026 (narrative/analytical content):**
- Use as: Tier 5 (analytical framework, conceptual framing)
- Do NOT use as: primary evidence for specific country claims — always trace to the
  underlying v16 dataset scores

**V-Dem Watchlist 2026:**
- Use as: Tier 2 early-warning input for WDM Watch List additions
- Update cadence: Annual (published with Democracy Report each March)

---

## 12. Integration Checklist — First Monday Brief Post-Calibration

When publishing the first WDM brief after loading this calibration document:

- [ ] Replace all Dimension A anchors for countries listed in §9 with v16 LDI values
- [ ] Add ERT episode flags to `heatmap` entries for the 5 new European autocratisers
      (Croatia, Italy, Slovakia, Slovenia, UK) — field: `vdemERT: "active-2025"`
- [ ] Add USA `vdemConfirmed: true` and update LDI anchor in persistent-state
- [ ] Review WDM Watch List against V-Dem Watchlist 2026 (§7) — add Bulgaria, Cyprus,
      Namibia, Portugal, Sierra Leone if not already present
- [ ] Confirm South Korea, Poland, Romania in Recovery category against U-Turn
      democratisation ERT status
- [ ] Set `electoralwatch.environment` to HIGH RISK for USA 2026 midterms
- [ ] Add V-Dem Slovenia signal to FCW crossmonitorflag check (FIMI link per Shadow
      FIMI Report addendum, March 2026)
- [ ] In the weekly brief, include a "V-Dem 2026 Calibration" item (§9 of brief format:
      "V-Dem quantitative scores what the numbers reveal this week") noting the
      global context frame from §2 of this document
- [ ] Log all baseline changes in persistent-state changelog with source:
      "V-Dem Dataset v16 / Democracy Report 2026 (March 2026)"

---

*This document supersedes no prior methodology. It is additive. Core methodology,
scoring rubric, source hierarchy, and publication workflow remain as specified in
`democratic-integrity-full.md` (v2.0, 2026-03-31).*

*Commit to: `asym-intel/asym-intel-internal/methodology/democratic-integrity-vdem-2026.md`*
*Also reference in: `democratic-integrity-full.md` §4 (Source Hierarchy), Tier 2 entry for V-Dem*

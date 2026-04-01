# BEFORE STARTING — READ THE WORKING AGREEMENT:
# gh api /repos/asym-intel/asym-intel-main/contents/COMPUTER.md --jq '.content' | base64 -d
# This contains architecture rules, deployment constraints, and file scope limits.

# TASK: Global Macro Monitor (GMM)
# VERSION: 2.0 — Blueprint v2.0 compliant
# CADENCE: Weekly — every Monday at 08:00 UTC
# PUBLISH TO: https://asym-intel.info/monitors/macro-monitor/

# ══════════════════════════════════════════════════════════════
# STEP 0 — PUBLISH GUARD (MUST RUN FIRST — DO NOT SKIP)
# ══════════════════════════════════════════════════════════════
#
# This block MUST be the first thing executed. Run it before
# reading any further instructions. If it exits, stop completely.
#
# Two conditions must BOTH be true to proceed:
#   1. Today is the correct publish day (Tuesday)
#   2. This monitor has not published in the last 6 days
#
# If either condition fails → EXIT IMMEDIATELY. Do not research.
# Do not write any files. Do not send any notification.
# A prompt reload is NOT a reason to publish.

```bash
set -e

# Check 1: correct day of week
EXPECTED_DAY="Tuesday"
TODAY_DAY=$(date -u +%A)
if [ "$TODAY_DAY" != "$EXPECTED_DAY" ]; then
  echo "GUARD: Wrong day. Today=$TODAY_DAY, expected=$EXPECTED_DAY. Exiting."
  exit 0
fi

# Check 2: UTC hour >= scheduled hour (avoid running before scheduled time)
EXPECTED_HOUR=08
TODAY_HOUR=$(date -u +%H | sed 's/^0//')
if [ "${TODAY_HOUR:-0}" -lt "$EXPECTED_HOUR" ]; then
  echo "GUARD: Too early. UTC hour=$TODAY_HOUR, scheduled=$EXPECTED_HOUR. Exiting."
  exit 0
fi

# Check 3: not published within the last 6 days
LAST_PUB=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/macro-monitor/data/report-latest.json \
  --jq '.content' | base64 -d | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d.get('meta',{{}}).get('published','2000-01-01')[:10])")
DAYS_AGO=$(python3 -c "
from datetime import date
last = date.fromisoformat('$LAST_PUB')
today = date.today()
print((today - last).days)
")
echo "GUARD: Last published $LAST_PUB ($DAYS_AGO days ago)"
if [ "$DAYS_AGO" -lt 6 ]; then
  echo "GUARD: Published $DAYS_AGO days ago — too recent. Minimum interval is 6 days. Exiting."
  exit 0
fi

echo "GUARD: All checks passed. Proceeding with publish pipeline."
```

If the bash block above exits with code 0 after printing "GUARD: ... Exiting" → STOP HERE.
Do not proceed. Do not perform any research or writes.
Only continue if the final line printed is "GUARD: All checks passed."

━━━━
SCHEMA — FLAG DEFINITIONS (include in meta block):
    "flag_definitions": {
      "f_flags": {
        "F1": "Counter-narrative active — a motivated source is contesting this claim",
        "F2": "Attribution contested — not independently corroborated",
        "F3": "Single source — treat as Assessed until corroborated"
      }
    },

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES (read first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CRON TASKS NEVER TOUCH HTML, CSS, OR JS FILES. EVER.
   Write ONLY: data/report-latest.json, data/report-{DATE}.json,
   data/archive.json, data/persistent-state.json + 1 Hugo brief.

2. LOAD PERSISTENT STATE FIRST. 3. NAMED SEMANTIC KEYS ONLY.
4. schema_version: "2.0" in all JSON files.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the analyst for the Global Macro Monitor (GMM).
Financial crisis early-warning: debt dynamics, credit stress,
systemic risk, market structure. Named-source 5-tier hierarchy
(§1a). Feed macro signals to SCEM, ERM, ESA, AGM.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0 — Load persistent state:
  gh repo clone asym-intel/asym-intel-main /tmp/asym-intel-main -- --depth=1 --quiet
  cat /tmp/asym-intel-main/static/monitors/macro-monitor/data/persistent-state.json
  cat /tmp/asym-intel-main/static/monitors/macro-monitor/data/report-latest.json

STEP 1 — Research: BIS, IMF WEO/GFSR, World Bank, Federal Reserve,
  ECB, Bloomberg (T1), FT/Reuters/WSJ (T2). Named sources only.

STEP 2 — Write 4 JSON files (single git commit):
  report-latest.json schema:
  { "meta": {..., "schema_version": "2.0", "methodology_url": "https://asym-intel.info/monitors/macro-monitor/methodology/"},
    "signal": {}, "debt_dynamics": [], "credit_stress": [],
    "systemic_risk": [], "asset_outlook": [], "safe_haven": [],
    "cross_monitor_flags": {}, "source_url": "..." }
  
  persistent-state.json — update these fields every issue:
    conviction_history: APPEND new entry {date, system_average, conviction, regime, regime_conviction, rationale}
    asset_class_baseline: for each asset UPDATE current_score/flag/direction AND APPEND version_history entry {date, change, reason, prior_value}
    active_tactical_alerts: replace list with currently active alerts only
    oil_supply_shock_driver: update current_driver, note, last_updated; append version_history if driver changes
    blind_spot_overrides: update active flag and version_history only if status changes
    NOTE: conviction_history and asset_class_baseline.version_history are the live trend data
    displayed on persistent.html charts — always append, never overwrite history.
  
CHANGELOG RULE — persistent array items:
Each item carries a "changelog" string. When updating an existing item, append:
  "changelog": "[existing history] | [YYYY-MM-DD: description of change]"
When creating a new item, set:
  "changelog": "[YYYY-MM-DD: New entry]"
Never delete changelog history.

Commit: "data(gmm): weekly JSON pipeline — Issue [N] W/E [DATE]"

STEP 3 — Hugo brief:
  content/monitors/macro-monitor/[DATE]-weekly-brief.md
  title: "Global Macro Monitor — W/E [DD Month YYYY]"
  date: [DATE]T08:00:00Z | monitor: "macro-monitor"

STEP 4 — Notify. Dashboard: https://asym-intel.info/monitors/macro-monitor/dashboard.html

Cron: 0 8 * * 1 (every Monday at 08:00 UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAIL RISK HEATMAP — add to report-latest.json each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add a "tail_risks" array to report-latest.json. Each entry is a named
macro tail risk event that an investor should track this week.

SCHEMA per item:
{
  "id":         "snake_case_unique_id",
  "label":      "Short event name (≤4 words)",
  "likelihood": 0.0–1.0,   // see sourcing rule below
  "impact":     0.0–1.0,   // see sourcing rule below
  "direction":  "Increasing" | "Stable" | "Decreasing",
  "note":       "One sentence: what triggers this, why it matters now"
}

SOURCING RULES (always follow these — do not use gut estimates):

likelihood (x-axis):
  Source directly from the probability estimates you write in the
  Horizon Matrix / tactical section of the report narrative.
  e.g. "60% probability oil stays $90+ for 30 days" → likelihood: 0.60
  e.g. "35% chance of VIX re-spike" → likelihood: 0.35
  If no explicit probability exists, assign band midpoints:
    LOW probability (<33%)    → 0.20
    MEDIUM probability (33–66%) → 0.50
    HIGH probability (>66%)   → 0.75
  Always note the sourcing in "note".

impact (y-axis) — FORMALISED METHOD:
  Step 1: List asset classes materially affected (score change ≥0.15 if scenario triggers)
  Step 2: Count affected asset classes (max 8)
  Step 3: Estimate average score change across affected classes (0.0–1.0)
  Step 4: impact = (count / 8) × average_score_change × 1.5, capped at 1.0
  Example: Hormuz closure affects 6 asset classes avg 0.80 change →
           impact = (6/8) × 0.80 × 1.5 = 0.90

QUANTITY: 5–8 tail risks per issue. Cover a mix of near-term (≤4 weeks)
and medium-term (1–3 month) horizons. Label each as "near" or "medium"
in the "note" field prefix: "[Near]" or "[Medium]".

EXAMPLE OUTPUT:
"tail_risks": [
  {
    "id": "private_credit_cascade",
    "label": "Private Credit Cascade",
    "likelihood": 0.55,
    "impact": 0.85,
    "direction": "Increasing",
    "note": "[Near] Gate events at Ares/Apollo signal retail outflow pressure that could trigger CLO and IG credit contagion simultaneously."
  },
  {
    "id": "jgb_yield_spiral",
    "label": "JGB Yield Spiral",
    "likelihood": 0.25,
    "impact": 0.90,
    "direction": "Stable",
    "note": "[Medium] BoJ forced to choose between FX defence and yield cap; no modern precedent for orderly resolution."
  }
]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENARIO ANALYSIS — add to executive_briefing each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add a "scenario_analysis" array to executive_briefing every issue.
Always produce exactly 3 scenarios: Base Case, De-escalation, Fast Cascade.
Probabilities must sum to 1.0 (±0.01 allowed for rounding).

SCHEMA per scenario:
{
  "label":       "Base Case" | "De-escalation" | "Fast Cascade",
  "name":        "Short evocative name (2–4 words)",
  "probability": 0.0–1.0,    // analyst estimate; must sum to 1.0 across 3
  "horizon":     "e.g. 3 months",
  "description": "2–3 sentences: what triggers it, key market impact, asset class direction"
}

SOURCING RULES:
- Base Case: the most likely path given current macro regime and data.
  Use the probability from base_case_probability (keep both in sync).
- De-escalation: policy pivot, trade deal, or resolution that relieves stress.
  Lower probability than Base Case in STAGFLATION / RISK-OFF regimes.
- Fast Cascade: tail scenario — rapid credit, liquidity, or political shock.
  Probability reflects analyst conviction; do not artificially inflate.
- All probabilities sourced from your Horizon Matrix estimates.
- Set base_case_label and base_case_probability as before (kept for
  backward compat), but scenario_analysis is the authoritative source.

EXAMPLE:
"scenario_analysis": [
  {
    "label": "Base Case",
    "name": "Slow Burn",
    "probability": 0.55,
    "horizon": "3 months",
    "description": "Tariff shock absorbed gradually; Fed on hold; credit stress contained to private markets; S&P range-bound -10% to +5%; stagflation regime persists."
  },
  {
    "label": "De-escalation",
    "name": "Policy Pivot",
    "probability": 0.20,
    "horizon": "6–8 weeks",
    "description": "Trade deal framework or Fed pivot signal triggers relief rally; credit spreads compress; regime transitions toward RISK-ON; equities +8–15%."
  },
  {
    "label": "Fast Cascade",
    "name": "Credit Contagion",
    "probability": 0.25,
    "horizon": "4–6 weeks",
    "description": "Private credit gate events escalate to CLO and IG contagion; VIX spikes above 40; hard landing surges; Fed forced to emergency cut; equities -20%+."
  }
]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL M2 & HARD LANDING RISK — add to executive_briefing each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add "real_m2" and "hard_landing_risk" to executive_briefing every issue.

REAL M2 SCHEMA:
{
  "value":     float,          // Real M2 YoY % change (nominal M2 minus Core PCE)
  "direction": "Improving" | "Stable" | "Deteriorating",
  "note":      "One sentence: current reading, trend, and what it signals"
}

Source: Federal Reserve H.6 (M2), BLS/BEA Core PCE. Calculate as:
  real_m2 = nominal_m2_yoy_growth - core_pce_yoy
If data unavailable, note in the "note" field and use previous issue value.

HARD LANDING RISK SCHEMA:
{
  "score":     0.0–1.0,       // analyst probability of hard landing in next 12 months
  "direction": "Improving" | "Stable" | "Increasing",
  "note":      "One sentence: key drivers of the current score"
}

Hard landing defined as: GDP growth < -1.0% for 2+ consecutive quarters
within the next 12 months. Score sources: BIS, IMF WEO probability tables,
your own composite of leading indicators (yield curve, credit spreads,
consumer confidence, unemployment claims). Do not fabricate; if anchoring
to a published probability, cite it in the note.

EXAMPLE:
"real_m2": {
  "value": 1.78,
  "direction": "Deteriorating",
  "note": "Real M2 vs. Core PCE +1.78% and narrowing — nominal M2 (+4.88%) masks the compression in real liquidity growth."
},
"hard_landing_risk": {
  "score": 0.38,
  "direction": "Increasing",
  "note": "Private credit gate events, consumer confidence below GFC trough, and tariff shock raise hard landing probability above baseline; consistent with IMF April WEO downside scenario."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL M2 — FIVE-DEFLATOR STACK (update executive_briefing each issue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The real_m2 field must include ALL FIVE deflators, not just Core PCE.
This produces the waterfall chart showing progressive liquidity erosion.

SCHEMA (replace the single-value real_m2 from prior schema):
{
  "nominal":      float,   // Nominal M2 YoY % (Fed H.6)
  "vs_cpi":       float,   // nominal minus CPI YoY
  "vs_pce":       float,   // nominal minus PCE YoY
  "vs_core_pce":  float,   // nominal minus Core PCE YoY  ← primary reference
  "vs_ppi":       float,   // nominal minus PPI YoY
  "vs_core_ppi":  float,   // nominal minus Core PPI YoY  ← tightest measure
  "direction":    "Improving" | "Stable" | "Deteriorating",
  "note":         "One sentence on the spread and what it signals"
}

Source: Fed H.6 (M2), BLS CPI, BEA PCE, BLS PPI. Calculate each as:
  real_m2_vs_X = nominal_m2_yoy - X_yoy
Direction is based on vs_core_pce trend vs. prior week.
If a deflator is unavailable, use prior week's value and note it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGIME SHIFT PROBABILITIES — add to signal each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add "regime_shift_probabilities" to the signal block each issue.
The four regimes are fixed; only the probabilities change.
They must sum to 1.0 (±0.01 for rounding).

SCHEMA:
"regime_shift_probabilities": {
  "stay_stagflation":    float,  // probability current regime persists 3 months
  "deflationary_bust":   float,  // credit/demand collapse → disinflation + recession
  "inflationary_boom":   float,  // demand re-accelerates, inflation entrenched
  "goldilocks":          float   // soft landing: inflation falls, growth holds
}

Source: analyst judgement anchored to scenario_analysis probabilities.
stay_stagflation should equal or approximate base_case_probability.
Also copy into executive_briefing.regime_shift_probabilities for the dashboard.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FED FUNDS FUTURES — add to sentiment_overlay each issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add a "sentiment_overlay" top-level key to report-latest.json.
Include the next 5 FOMC meetings with implied cut probabilities
and your view vs. market consensus.

SCHEMA:
"sentiment_overlay": {
  "fed_funds_futures": [
    {
      "meeting":          "Apr 28–29",          // display label
      "meeting_date":     "2026-04-29",          // ISO date of decision day
      "weeks_ahead":      4,                     // weeks from publish date
      "cut_probability":  0.02,                  // from CME FedWatch (0.0–1.0)
      "our_view":         "AGREES" | "DISAGREES",
      "note":             "One sentence analyst rationale"
    }
    // ... 5 meetings total
  ],
  "prob_zero_cuts_2026": float,   // cumulative: probability of no cuts this year
  "matt_agreement_pct":  float,   // % of analyst flags market is pricing (0–1)
  "source_url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
}

Source: CME FedWatch for cut_probability. Analyst judgement for our_view.
AGREES = market pricing consistent with your framework.
DISAGREES = market is mispricing — note which direction.
Update all 5 meetings every issue; remove meetings that have passed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INDICATOR TYPE BADGES — add to every domain indicator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every indicator object in domain_indicators must include:
  "indicator_type": "SA" | "CC" | "TS"

Definitions:
  SA = Strategic Anchor    — structural, multi-year horizon, slow-moving
  CC = Cycle Coincident    — tracks the business/credit cycle, months horizon
  TS = Tactical Signal     — fast-moving, weeks horizon, for positioning

CANONICAL MAPPING (fixed — do not change week to week):
  Domain 1 — Debt & Sovereign:
    us_debt_deficit:           SA
    japan_jgb_yields:          SA
    em_sovereign_distress:     SA
    custody_migration:         SA
    gold_reserve_ratio:        SA

  Domain 2 — Banking & Credit:
    fed_sloos:                 TS
    cre_delinquency:           CC
    gsib_capital_cds:          SA
    private_credit_nbfi:       SA

  Domain 3 — Market Structure:
    vix_term_structure:        TS
    treasury_market_liquidity: TS
    margin_debt:               TS
    dollar_funding_fx_basis:   TS
    m2_real_net_liquidity:     CC

  Domain 4 — Real Economy:
    ism_manufacturing_pmi:     CC
    jobless_claims:            CC
    cass_freight_index:        CC
    consumer_confidence:       CC
    corporate_earnings_revisions: CC

  Domain 5 — Composite Indices:
    stlfsi4:                   CC
    chicago_fed_nfci:          CC
    iif_global_debt_monitor:   SA
    zero_dte_option_volume:    TS

  Domain 6 — Amplifiers:
    trump_tariff_escalation:   SA
    oil_supply_shock:          TS
    dollar_weaponisation:      SA
    ai_infrastructure_debt:    SA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TWO-PASS COMMIT RULE — MANDATORY FOR EVERY RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  The JSON for this monitor is too large to produce safely in one pass.
You MUST write it in two separate git commits. Never combine into one.

PASS 1 — Core sections (commit first, immediately after research):
  meta, signal, executive_briefing, debt_dynamics, credit_stress, systemic_risk, asset_outlook, safe_haven, source_url

  Commit: "data(gmm): Issue [N] W/E [DATE] — core sections"

PASS 2 — Deep sections (commit second, by patching the Pass 1 file):
  domain_indicators, tail_risks, sentiment_overlay, cross_monitor_flags

  Method:
  ```bash
  # 1. Download the Pass 1 JSON
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/macro-monitor/data/report-latest.json \
    --jq '.content' | base64 -d > /tmp/gmm-report.json

  # 2. Add the Pass 2 sections to /tmp/gmm-report.json using Python/jq

  # 3. Push it back (replace the file with the patched version)
  SHA=$(gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/macro-monitor/data/report-latest.json --jq '.sha')
  CONTENT=$(base64 -w 0 /tmp/gmm-report.json)
  gh api --method PUT /repos/asym-intel/asym-intel-main/contents/static/monitors/macro-monitor/data/report-latest.json \
    --field message="data(gmm): Issue [N] W/E [DATE] — deep sections" \
    --field content="$CONTENT" --field sha="$SHA" --field branch="main"
  ```

  Do the same two-pass write for report-{DATE}.json.

VERIFICATION — run after Pass 2 before proceeding to Step 3:
  ```bash
  gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/macro-monitor/data/report-latest.json \
    --jq '.content' | base64 -d | python3 -c \
    "import json,sys; d=json.load(sys.stdin); missing=[k for k in ['domain_indicators', 'tail_risks', 'sentiment_overlay'] if k not in d]; print('MISSING:',missing) if missing else print('ALL SECTIONS PRESENT ✓')"
  ```
  If MISSING is non-empty — do NOT proceed to Step 3. Re-run Pass 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0B — READ SHARED INTELLIGENCE LAYER (before research)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After loading your own persistent-state.json, read these two shared files:

```bash
# Cross-monitor intelligence digest (compiled weekly by housekeeping cron)
# Filters for flags relevant to GMM (either targeting or sourced from this monitor)
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/intelligence-digest.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
abbr='gmm'
flags=[f for f in d.get('flags',[])
       if abbr in [x.lower() for x in f.get('target_monitors',[])]
       or f.get('source_monitor','')==abbr]
print(f'Relevant cross-monitor flags: {{len(flags)}} of {{d.get("total_flags",0)}} total')
for f in flags:
    print(f'  [{f["source_monitor"].upper()}→{abbr.upper()}] {f["title"][:80]}')
    if f.get('body'): print(f'    {f["body"][:120]}')
"

# Schema changelog — confirm what you must produce this issue
gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/shared/schema-changelog.json \
  --jq '.content' | base64 -d | python3 -c "
import json,sys
d=json.load(sys.stdin)
entries=[e for e in d.get('entries',[]) if e.get('monitor') in ['GMM','ALL']]
print(f'Schema requirements for GMM ({len(entries)} entries):')
for e in entries:
    print(f'  [{e["id"]}] {e["field"]}: required from {e.get("required_from_issue","launch")}')
"
```

Use cross-monitor flags to incorporate adjacent signals into your analysis
and update your own cross_monitor_flags where new linkages are found.
Use schema changelog to verify your output includes all required fields.

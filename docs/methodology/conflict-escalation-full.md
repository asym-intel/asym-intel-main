# Strategic Conflict & Escalation Monitor — Full Internal Methodology
## INTERNAL / PRIVATE REPO — asym-intel/asym-intel-internal
## methodology/conflict-escalation-full.md

Version: 1.0
Date: 2026-03-30
Monitor slug: conflict-escalation
Public URL: https://asym-intel.info/monitors/conflict-escalation/
Dashboard: https://asym-intel.info/monitors/conflict-escalation/dashboard.html
Public methodology: https://asym-intel.info/monitors/conflict-escalation/methodology/
Cron schedule: Weekly — Friday 18:00 UTC (7pm Gibraltar summer time)

---

## INTERNAL NOTES — NOT FOR PUBLICATION

### Conflict roster (current)
Maintain the following fields per conflict in the internal tracking file:
- Conflict ID (slug)
- Entry date
- Entry trigger (which criteria met)
- Structural break dates and descriptions
- Baseline window start date
- Baseline recalculation due date (next 3-month cycle)
- Current status (Active / Dormant Watch)
- Retirement date (if applicable)

### Baseline recalculation log
Each quarter, record:
- Date of recalculation
- Conflicts affected
- Any baselines reset due to structural break override
- Analyst name/identifier

### Source reliability log
Maintain a running note on sources that have been identified as:
- Consistently ahead on T1/T2 verification
- Consistently late (data lag patterns)
- Flagged for suspected F1–F4 disinformation patterns
- Withdrawn from use and reason

### Deviation audit trail
For any Red-band entry, record:
- Indicator and actor
- Level scored
- Baseline used
- Deviation computed
- Confidence label applied
- Sources used for scoring
- F1–F4 flags if applicable
- Analyst sign-off

### Contested baseline registry
All conflicts and indicators currently operating under Contested Baseline flag:
- Conflict ID
- Indicator(s) flagged
- Date flag applied
- Number of observations to date
- Projected date of flag removal (at current observation rate)

---

## SCORING RUBRICS (EXTENDED — not in public methodology)

### I1 Rhetoric Intensity — extended notes
- Distinguish between state-media amplification (may be F1/F3 tactic) and official government-to-government statements
- For authoritarian states where state media and official government voice are indistinct, treat both as Tier 3 requiring corroboration
- Multilingual source monitoring required: Russian-language, Arabic-language, and Mandarin-language sources frequently carry material before English-language translation
- AI triage: use velocity detection across multilingual sources to flag spikes; do not score from AI output directly

### I2 Military Posture — extended notes
- Primary secondary sources for satellite-derived analysis: Middlebury Institute CNS (nuclear/missile), CSIS iDeas Lab, UNOSAT, Planet Labs public releases, Sentinel Hub EO Browser change detection outputs (where publicly released), Bellingcat geolocation verification
- Do not cite commercial satellite providers' proprietary analysis unless independently corroborated
- Distinguish between exercise (routine baseline) and deployment (potentially anomalous) using historical exercise calendar data
- NATO exercise calendar is publicly available and should be checked before scoring any posture change involving NATO members or partners

### I3 Nuclear & Strategic — extended notes
- Doctrine Shift flag is separate from Level scoring. A formal doctrine change (e.g., lowering nuclear threshold in official doctrine) is coded as Doctrine Shift regardless of whether rhetoric Level changes
- IAEA safeguards reporting is T1 for civilian nuclear programmes; INF-type military nuclear monitoring has no equivalent T1 source — score accordingly
- DPRK: nearly all satellite analysis must be treated as T2 (secondary OSINT) given access constraints; treat Confirmed confidence as rarely achievable for DPRK posture scores
- Israel: ambiguity doctrine means I3 baseline is structurally near zero for public signalling; any public signalling should be treated as highly anomalous regardless of absolute level

### I4 Economic Warfare — extended notes
- OFAC, HM Treasury, EU Official Journal are T1 for sanctions confirmation
- Energy cutoffs: IEA, ACER (EU energy regulator), national grid operators are T1
- Asset freezes involving financial system access: SWIFT notifications, correspondent banking alerts via credible financial journalism (FT, Bloomberg) = T2
- Trade restriction data: WTO dispute filings and national customs authority announcements = T1; secondary reporting = T2

### I5 Diplomatic Channel Status — extended notes
- Back-channel activity is almost never independently verifiable; treat any report of back-channel talks as Unverified unless two independent T2 sources confirm
- Ambassador recall vs. expulsion: recall is actor-initiated (may be signalling); expulsion is host-country-initiated (higher escalation indicator). Code differently.
- Multilateral forum participation: UNSC walkouts, OSCE meeting boycotts are T1 verifiable and carry high indicator weight

### I6 Displacement Velocity — extended notes
- UNHCR Operational Data Portal: primary T1 source for registered refugees and asylum data
- OCHA ReliefWeb and Humanitarian Data Exchange: T1 for IDP data and humanitarian situation reports
- IOM Displacement Tracking Matrix: T1 for displacement tracking in specific crisis zones
- Data date annotation is mandatory — always record the as-of date of the data, not the report publication date
- When data dates are more than 3 weeks behind the scoring week, note this explicitly in the scoring table and narrative
- Rapid-onset displacement (conflict-triggered) should be distinguished from slow-onset (climate/economic) in the narrative even if both feed the same I6 score

---

## PUBLISH STEP (COMPLETE — for cron task reference)

```bash
PUBLISH_DATE=$(date +%Y-%m-%d)
WEEK_ENDING=$(date +"%d %B %Y")
MONITOR_SLUG="conflict-escalation"
WORKSPACE="/home/user/workspace/conflict-monitor"

# ── PUBLIC REPO ──────────────────────────────────────────────────────────────
cd /tmp && rm -rf asym-intel-publish
gh repo clone asym-intel/asym-intel-main asym-intel-publish
cd asym-intel-publish
git config user.email "monitor-bot@asym-intel.info"
git config user.name "Monitor Bot"

# Dashboard
cp ${WORKSPACE}/dashboard.html static/monitors/${MONITOR_SLUG}/dashboard.html

# Methodology (Hugo markdown)
cp ${WORKSPACE}/methodology.md content/monitors/${MONITOR_SLUG}/methodology.md

# Weekly brief (Hugo markdown)
cp ${WORKSPACE}/brief-${PUBLISH_DATE}.md content/monitors/${MONITOR_SLUG}/${PUBLISH_DATE}-brief.md

git add static/monitors/${MONITOR_SLUG}/dashboard.html
git add content/monitors/${MONITOR_SLUG}/methodology.md
git add content/monitors/${MONITOR_SLUG}/${PUBLISH_DATE}-brief.md
git commit -m "content: conflict-escalation dashboard and brief ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main

echo "✓ Dashboard: https://asym-intel.info/monitors/${MONITOR_SLUG}/dashboard.html"
echo "✓ Methodology: https://asym-intel.info/monitors/${MONITOR_SLUG}/methodology/"
echo "✓ Brief: https://asym-intel.info/monitors/${MONITOR_SLUG}/${PUBLISH_DATE}-brief/"

# ── INTERNAL / PRIVATE REPO ──────────────────────────────────────────────────
cd /tmp && rm -rf asym-intel-internal
gh repo clone asym-intel/asym-intel-internal asym-intel-internal
cd asym-intel-internal
git config user.email "monitor-bot@asym-intel.info"
git config user.name "Monitor Bot"

cp ${WORKSPACE}/methodology-internal.md methodology/${MONITOR_SLUG}-full.md

git add methodology/${MONITOR_SLUG}-full.md
git commit -m "methodology: conflict-escalation internal update ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main

echo "✓ Internal methodology: asym-intel/asym-intel-internal/methodology/${MONITOR_SLUG}-full.md"
```

---

## CROSS-MONITOR SIGNAL ROUTING (internal reference)

When the weekly scoring produces any of the following, route as noted:

| Signal | Route to | How |
|---|---|---|
| F1–F4 flag on any indicator | FIMI monitor task (next run) | Include in cross-monitor signals section of brief |
| Red-band I1/I2 for Russia, China, Iran, Gulf, US, Israel | FIMI monitor | Flag actor + conflict context |
| Red-band any indicator for European theatre conflict | ESA Wednesday run | Flag in brief cross-monitor section |
| I6 spike with climate/water driver noted | GERP Saturday run | Cross-tag in brief |
| I4 Red-band (economic warfare) | Macro Monitor | Note in macro cross-signals |
| Any Red-band within 90 days of scheduled election in affected state | Democracy Monitor | Flag |

---

## CURRENT ARCHITECTURE — Strategic Conflict & Escalation Monitor (updated 2026-04-01)

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
MONITOR_SLUG="conflict-escalation"
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
cat > content/monitors/conflict-escalation/${PUBLISH_DATE}-weekly-brief.md << MDEOF
---
title: "FIMI & Cognitive Warfare Monitor — W/E {DATE}"
date: ${PUBLISH_DATE}T18:00:00Z
summary: "[lead signal summary]"
draft: false
monitor: "conflict-escalation"
---
MDEOF

git add static/monitors/conflict-escalation/data/
git add content/monitors/conflict-escalation/
git commit -m "data(SCEM): weekly pipeline — Issue [N] W/E ${PUBLISH_DATE}"
git pull --rebase origin main
git push origin main
```

### Schema Version

All JSON files must contain `"schema_version": "2.0"` at top level.
No future dates. No direct HTML/CSS/JS writes from cron tasks — data only.

### Monitor Accent & URLs

- Accent: #dc2626
- Dashboard: https://asym-intel.info/monitors/conflict-escalation/dashboard.html
- Data: https://asym-intel.info/monitors/conflict-escalation/data/report-latest.json
- Internal spec: asym-intel/asym-intel-internal/methodology/conflict-escalation-full.md

---

## ANALYTICAL UPGRADES — ACLED 2026 + I1-I6 Analytical Upgrades (added 2 April 2026)

### FM-SCEM-01: Drone Normalisation — Theatre-Specific Baselines

FPV drone and Shahed-136 operations are now BASELINE in Ukraine/Russia and Gaza — do not score above I2 Level 2 for routine drone exchange. The relevant I2 escalation signal is: (a) range extension reaching previously non-targeted urban centres, (b) swarm doctrine (coordinated multi-vector simultaneous attack), or (c) cross-border drone incursion into a third-party state. Store drone baseline per theatre in persistent-state under each conflict's indicatorBaselines.I2.

### FM-SCEM-02: AI-Generated Rhetoric — I1 Inflation Risk

AI-generated propaganda now mimics official government rhetoric at scale. Before scoring any I1 item sourced from social media or unofficial channels, explicitly note: 'AI generation check: does source have verifiable institutional origin?' State media and official government voice are indistinct for authoritarian actors (RU, CN, DPRK, Iran, Myanmar junta) — treat both as T3 requiring T1/T2 corroboration. Any I1 spike of ≥2 levels in a single week requires dual-source confirmation before committing to persistent-state. Add aiGenerationCheck: true field to I1 scoring entries where applied.

### FM-SCEM-03: Russia I3 Doctrine Shift as Persistent Baseline

Russia's November 2024 nuclear doctrine formally lowered the threshold for nuclear use. This is a CONFIRMED DOCTRINE SHIFT — already coded as doctrineshiftconfirmed: true in persistent-state. Do not re-code it as new each week. Subsequent Medvedev/MFA rhetoric referencing the doctrine is EPISODIC — flag with episodic: true, do not increment I3 score. Only score new I3 event when: (a) second formal doctrine document issued; (b) nuclear-capable delivery system moved to alert status (confirmed by Middlebury CNS or CSIS iDeas Lab); (c) IAEA safeguards access formally suspended.

### FM-SCEM-04: US I5 Channel De-weighting (2026)

US withdrawal from 66+ multilateral institutions means US participation in multilateral forums is no longer a reliable I5 positive indicator in 2026. Weight European, Gulf, and African Union mediation channels more heavily than US bilateral channels in Gaza, Ukraine, and Sudan theatres. Document weighting rationale in narrative.


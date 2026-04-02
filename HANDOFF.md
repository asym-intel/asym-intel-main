# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 session wrap (~16:35 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions -- Next Session

1. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC):
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"

2. **FCW Thursday pipeline validation** (Thu 10 Apr 09:00 UTC):
   First full run with Steps 0C/0D/0E. Verify report published and pipeline read correctly.

3. **Sprint 3 Group A** (8 rendering items, all data confirmed present):
   FCW: all 12 campaigns on dashboard, attribution_log field fixes
   GMM: hard_landing_risk KPI, regime_shift_probabilities chart, sentiment_overlay table
   WDM: weekly_brief on dashboard
   SCEM: roster_watch + cross_monitor_flags sections on report.html

4. **SCEM verification cron** fires Sun 5 Apr 18:30 UTC (auto -- no action needed)
   **WDM verification cron** fires Mon 6 Apr 06:30 UTC (auto -- no action needed)

5. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## GitHub Actions Pipeline Status

| Monitor | Collector | Weekly Research | Reasoner | Analyst Steps 0C/0D/0E |
|---------|-----------|-----------------|----------|------------------------|
| FCW | Daily 07:00 UTC | Wed 18:00 UTC | Wed 20:00 UTC | Wired (Thu Analyst) |
| GMM | Daily 06:00 UTC | Mon 18:00 UTC | Mon 20:00 UTC | Wired (Tue Analyst) |
| SCEM | Daily 06:00 UTC | Sat 18:00 UTC | Sat 20:00 UTC | Wired (Sun Analyst) |
| WDM | Not yet built | Not yet built | Not yet built | Not yet |
| ESA | Not yet built | Not yet built | Not yet built | Not yet |
| AGM | Not yet built | Not yet built | Not yet built | Not yet |
| ERM | Not yet built | Not yet built | Not yet built | Not yet |

CRITICAL: Never create Computer crons for monitor pipelines -- they run in GitHub Actions.

---

## Annual Calibration Status -- ALL 7 COMPLETE

| Monitor | File | Key additions |
|---------|------|---------------|
| WDM | democratic-integrity-vdem-2026.md | V-Dem v16 LDI anchors, ERT flags |
| ERM | environmental-risks-copernicus-2026.md | Planetary boundaries, 1.5C baseline, tipping systems |
| SCEM | conflict-escalation-acled-2026.md | Drone baselines, doctrine shift, Q2 recalcs |
| AGM | ai-governance-euaiact-2026.md | Standards Vacuum ACTIVE, GPAI table |
| ESA | european-strategic-autonomy-ecfr-2026.md | US coercion protocol, Lagrange 2026 |
| GMM | macro-monitor-imf-2026.md | Tariff Shock Protocol ACTIVE, decoupling index |
| FCW | fimi-cognitive-warfare-eeas-2026.md | AI-FIMI protocol, X/Twitter degraded, DISARM v1.5 |

---

## Monitor Publication Status

| Monitor | Last Published | Pipeline | Calibration |
|---------|---------------|----------|-------------|
| WDM | 2026-04-01 | Not built | V-Dem v16 applied |
| GMM | 2026-04-01 | Live | IMF 2026 applied |
| FCW | 2026-04-01 | Live | EEAS 2026 applied |
| ESA | 2026-04-01 | Not built | ECFR 2026 applied |
| AGM | 2026-04-01 | Not built | EU AI Act 2026 applied |
| ERM | 2026-03-29 | Not built | Copernicus 2025 applied |
| SCEM | 2026-03-30 | Live | ACLED 2026 applied |

---

## Chatter Feature

Full spec at: /home/user/workspace/chatter-design.md
Decision: deploy Chatter alongside pipeline rollout per monitor (not separate sprint).
Dashboard tab + GitHub Actions workflow + public JSON per monitor.
Cost: ~$0.73/monitor/year (sonar daily).

---

## Architecture Notes (stable)

- FCW/GMM/SCEM: GitHub Actions Collector (sonar daily) + Weekly Research (sonar-pro) + Reasoner (sonar-deep-research)
- pipeline/ is internal only -- Hugo never builds from it
- sonar-deep-research does NOT search the web -- reasoning over docs you provide only
- Staging required for all monitor HTML/CSS/JS changes
- Two-pass commit mandatory for all 7 Analyst crons
- Annual calibration: {slug}-{index}-{YEAR}.md -- auto-discovered at Step 0B+
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval

---

## Sprint Backlog

Full programme: docs/audits/sprint-programme.md

Sprint 3 Group A (next session, ~2-3 hours):
  FCW/GMM/SCEM/WDM rendering items -- all data confirmed present

Sprint 3 Groups B+C: GMM charts, ESA cards, SCEM bugs, cross-monitor widget

Sprint 4: Schema additions (24 items, cron prompt changes required first)

Sprint 5: Architectural (design sessions required)

# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 (session wrap)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Sprint 3 Group A** (8 items, all data confirmed present, ~2-3 hours):
   FCW: all 12 campaigns on dashboard, attribution_log field fixes
   GMM: hard_landing_risk KPI card, regime_shift_probabilities chart, sentiment_overlay table
   WDM: weekly_brief on dashboard
   SCEM: roster_watch section + cross_monitor_flags section on report.html

2. **FCW Thursday pipeline validation** (Thu 10 Apr 09:00 UTC):
   First full run with Steps 0C/0D/0E. Verify it reads pipeline/ correctly and publishes.
   Check: gh api .../fimi-cognitive-warfare/data/report-latest.json | meta.published

3. **Remaining calibration files** (GMM/ESA/FCW not yet done):
   GMM: macro-monitor-imf-2026.md (IMF WEO April 2026 due soon)
   ESA: european-strategic-autonomy-ecfr-2026.md
   FCW: fimi-cognitive-warfare-eeas-2026.md

4. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Monitor Publication Status

| Monitor | Last Published | Calibration Applied |
|---------|---------------|---------------------|
| WDM | 2026-04-01 | V-Dem v16 (2026-04-02) |
| GMM | 2026-04-01 | None yet |
| FCW | 2026-04-01 | 5 methodology gaps (2026-04-02) |
| ESA | 2026-04-01 | None yet |
| AGM | 2026-04-01 | EU AI Act 2026 (2026-04-02) |
| ERM | 2026-03-29 | Copernicus 2025 (2026-04-02) |
| SCEM | 2026-03-30 | ACLED 2026 (2026-04-02) |

---

## FCW Pipeline (GitHub Actions -- NOT Computer crons)

```
Daily 07:00 UTC (sonar)          pipeline/daily/
Wed 18:00 UTC (sonar-pro)        pipeline/weekly/
Wed 20:00 UTC (sonar-deep-research) pipeline/reasoner/

FCW Analyst Thu 09:00 UTC (879686db)
  Step 0C: daily Collector
  Step 0D: weekly research
  Step 0E: Reasoner
  Step 1: methodology application (not raw research)
```

First full pipeline run: Thu 10 Apr 09:00 UTC.
Do NOT deploy pipeline to other monitors until this validates.

---

## Annual Calibration Convention

Files: asym-intel-internal/methodology/{slug}-{index}-{YEAR}.md
Auto-discovered by Step 0B+ in each cron prompt.

Active files (2026):
  democratic-integrity-vdem-2026.md (WDM)
  environmental-risks-copernicus-2026.md (ERM)
  conflict-escalation-acled-2026.md (SCEM)
  ai-governance-euaiact-2026.md (AGM)

Missing (create next session): GMM, ESA, FCW

---

## COMPUTER.md Version

## Version 2.3 — 2 April 2026

---

## Stable Architecture Notes

- FCW pipeline: GitHub Actions (NOT Computer crons). Never recreate as Computer cron.
- sonar = live web search | sonar-pro = deeper live search | sonar-deep-research = reasoning over docs you provide (no web search)
- pipeline/ is internal only -- Hugo never builds from it
- Staging required for all monitor HTML/CSS/JS changes
- Two-pass commit mandatory for all 7 Analyst crons
- 'wrap' = session checkpoint trigger (same as 'merge' for HTML)
- notes-for-computer.md: log significant decisions immediately during session

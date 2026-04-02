# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 end-of-day wrap (~17:30 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Sprint 3 Groups B+C** — no blockers, pure rendering work, can start immediately:
   GMM: scenario cards, Real M2 waterfall, tail risk tooltips, regime_shift chart
   ESA: Lagrange 6th radar spoke, institutional_developments cards
   AGM: digest.html nav link, M06 arXiv section, risk vector heat grid
   ERM: cascade tier breakdown, reverse cascade check, M03 three-layer rendering
   WDM: silent_erosion section, signal.history trend, severity_sub render
   SCEM: indicator deviation chart fix, GEI CONTESTED disclaimer
   ALL: source links pass, cross-monitor flags widget

2. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC — tomorrow):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

3. **Sprint 2B items** — slot in as crons fire this week:
   - WDM Category B sections render on report.html (after Mon 6 Apr WDM run)
   - ESA defence spending bar chart (after Wed 8 Apr ESA run)
   - FCW campaign Gantt — start_date field needed (after Thu 9 Apr FCW run)

4. **Verification crons fire automatically** — no action needed:
   - SCEM: Sun 5 Apr 18:30 UTC (cron a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (cron 10ddf5f0)

5. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Completed Today (2 April 2026)

- **Sprint 3 Group A merged to main** — FCW (12 campaigns + instrument column), FCW Chatter page,
  GMM (Fed Funds KPI + Sentiment Overlay), WDM (weekly_brief + sidebar nav),
  SCEM (roster_watch section), shared base.css FE-020 fixes
- **FE-020 corrected** — inline renderMarkdown is canonical (not AsymRenderer); ARCHITECTURE.md updated
- **DQ-001 logged** — SCEM roster_watch dedup rule in ARCHITECTURE.md
- **Full cron migration** — all 9 crons now slim repo pointers to docs/crons/
- **docs/crons/ registry created** — housekeeping.md, staging-guard.md, annual-calibration-reminder.md + README
- **Staging divergence guard live** (aec126c5, daily ~18:00 UTC)
- **ARCHITECTURE.md** now in asym-intel skill Step 0 (item 4) — mandatory before HTML/CSS/JS work

---

## Cron Table (current — all slim repo pointers)

| Layer | Name | Cron ID | Schedule | Prompt |
|---|---|---|---|---|
| Analyst | WDM | d22b7778 | Mon 06:00 UTC | wdm-cron-prompt.md |
| Analyst | GMM | 9983df74 | Tue 08:00 UTC | gmm-cron-prompt.md |
| Analyst | ESA | 26f24020 | Wed 19:00 UTC | esa-cron-prompt.md |
| Analyst | FCW | 1d51ae99 | Thu 09:00 UTC | fcw-cron-prompt.md |
| Analyst | AGM | 743fe004 | Fri 09:00 UTC | agm-cron-prompt.md |
| Analyst | ERM | 1ec0d995 | Sat 05:00 UTC | erm-cron-prompt.md |
| Analyst | SCEM | 40a62a34 | Sun 18:00 UTC | scem-cron-prompt.md |
| Housekeeping | Platform Housekeeping | 7e058f57 | Mon 08:00 UTC | docs/crons/housekeeping.md |
| Guard | Staging divergence guard | aec126c5 | Daily ~18:00 UTC | docs/crons/staging-guard.md |
| Calibration | Annual calibration reminder | e6668dce | 28 Mar annually | docs/crons/annual-calibration-reminder.md |
| Verification | SCEM verification | a67a9739 | Sun 5 Apr 18:30 UTC (one-shot) | inline |
| Verification | WDM verification | 10ddf5f0 | Mon 6 Apr 06:30 UTC (one-shot) | inline |

---

## GitHub Actions Pipeline Status

| Monitor | Collector | Weekly Research | Reasoner | Analyst Steps 0C/0D/0E |
|---------|-----------|-----------------|----------|------------------------|
| FCW | Daily 07:00 UTC | Wed 18:00 UTC | Wed 20:00 UTC | Wired (Thu Analyst) |
| GMM | Daily 06:00 UTC | Mon 18:00 UTC | Mon 20:00 UTC | Wired (Tue Analyst) |
| SCEM | Daily 06:00 UTC | Sat 18:00 UTC | Sat 20:00 UTC | Wired (Sun Analyst) |
| WDM | Not yet built | — | — | Not yet |
| ESA | Not yet built | — | — | Not yet |
| AGM | Not yet built | — | — | Not yet |
| ERM | Not yet built | — | — | Not yet |

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

## Architecture Notes (stable)

- All crons are slim repo pointers — edit .md file in docs/crons/ or static/monitors/{slug}/, commit, done
- To recreate a lost cron: see docs/crons/README.md for exact pattern
- ARCHITECTURE.md — mandatory read before any HTML/CSS/JS work; update when new patterns found
- FE-020 canonical fix: inline renderMarkdown (report.html pattern), NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- Staging guard: fires daily, notifies if behind_by > 30. Merge via direct file apply (not PR at high divergence)
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval

---

## Sprint Backlog

Full programme: docs/audits/sprint-programme.md

Sprint 3 Groups B+C: next session (no blockers)
Sprint 2B: this week as crons fire (data-gated)
Sprint 4: schema additions — after Sprint 3
Sprint 5: architectural — design sessions required

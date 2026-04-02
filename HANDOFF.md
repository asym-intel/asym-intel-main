# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 end-of-session wrap (~18:25 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Sprint 3 Groups B+C — items NOT yet done (data not in schema yet — Sprint 4):**
   - WDM: silent_erosion, signal.history trend, severity_sub (fields not in JSON)
   - SCEM: GEI CONTESTED disclaimer, indicator deviation chart fix (fields not in JSON)
   - ESA: Lagrange 6th spoke (already has 6 — confirmed working, item closed)
   - ALL: source links systematic pass (still pending)

2. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

3. **Sprint 2B data-gated items** (slot in as crons fire):
   - WDM Category B sections (Mon 6 Apr)
   - ESA defence spending bar (Wed 8 Apr)
   - FCW campaign Gantt (Thu 9 Apr)

4. **Housekeeping cleanup:**
   - Remove `static/monitors/housekeeping-cron-prompt.md` duplicate (moved to docs/crons/)
   - Update `static/monitors/shared/anti-patterns.json` with FE-020 through FE-025

5. **Verification crons fire automatically:**
   - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

6. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Completed This Session (2 April 2026)

**Sprint 3 Group A** (earlier today, merged):
FCW 12 campaigns + Chatter, GMM Fed Funds/Sentiment, WDM weekly_brief, SCEM roster_watch

**Sprint 3 Groups B+C** (merged ~18:25 CEST):
- ALL 6 dashboards: Cross-Monitor Flags section + sidebar nav + renderCrossMonitor
- GMM: score-history sidebar anchor fix
- AGM: Digest + Methodology + Search in top nav
- ERM: reverse_cascade_check rendered in cascade cells
- ESA: duplicate radar removed from dashboard, sidebar links to persistent.html
- ESA persistent: Lagrange radar enlarged +40% (canvas 543×543, fonts 14/15px, centred)

**Architecture additions (all in ARCHITECTURE.md):**
- FE-021: cross-monitor section outside </main>
- FE-022: render call after .catch block
- FE-023: sidebar nav link omission
- FE-024: escHtml scope error outside DOMContentLoaded
- FE-025: empty file from bash associative array encoding
- Pre-staging checklist added (7 checks)
- platform-developer.md: during-session documentation mandate added

**Cron infrastructure** (earlier today):
- All 9 crons migrated to slim repo pointers
- docs/crons/ registry created
- Staging divergence guard live (aec126c5)
- Robustness testing: 3 failure modes found and fixed in COMPUTER.md

---

## Cron Table (current — all slim repo pointers)

| Layer | Name | ID | Schedule |
|---|---|---|---|
| Analyst | WDM | d22b7778 | Mon 06:00 UTC |
| Analyst | GMM | 9983df74 | Tue 08:00 UTC |
| Analyst | ESA | 26f24020 | Wed 19:00 UTC |
| Analyst | FCW | 1d51ae99 | Thu 09:00 UTC |
| Analyst | AGM | 743fe004 | Fri 09:00 UTC |
| Analyst | ERM | 1ec0d995 | Sat 05:00 UTC |
| Analyst | SCEM | 40a62a34 | Sun 18:00 UTC |
| Housekeeping | Platform Housekeeping | 7e058f57 | Mon 08:00 UTC |
| Guard | Staging divergence guard | aec126c5 | Daily ~18:00 UTC |
| Calibration | Annual calibration reminder | e6668dce | 28 Mar annually |
| Verification | SCEM verify | a67a9739 | Sun 5 Apr 18:30 (one-shot) |
| Verification | WDM verify | 10ddf5f0 | Mon 6 Apr 06:30 (one-shot) |

---

## What's Next (in order)

1. Sprint 3 remaining items (source links pass, WDM/SCEM schema-gated items)
2. Sprint 2B as crons fire this week
3. Pipeline outsourcing review → WDM/ESA/AGM/ERM pipelines
4. Sprint 4 — schema additions
5. Sprint 5 — architectural (design sessions required)

---

## Architecture Notes (stable)

- All crons slim repo pointers — edit .md in docs/crons/ or static/monitors/{slug}/, commit, done
- ARCHITECTURE.md mandatory before any HTML/CSS/JS work — FE-021 through FE-025 all documented
- FE-020: inline renderMarkdown (report.html pattern), NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- Staging reset to main after every direct-file merge
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval

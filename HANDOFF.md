# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 end-of-session wrap (~19:00 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

2. **Sprint 3 remaining items (schema-gated — Sprint 4):**
   - WDM: silent_erosion, signal.history trend, severity_sub (fields not in JSON)
   - SCEM: GEI CONTESTED disclaimer, indicator deviation chart fix (fields not in JSON)

3. **Sprint 2B data-gated items** (slot in as crons fire):
   - WDM Category B sections (Mon 6 Apr)
   - ESA defence spending bar (Wed 8 Apr)
   - FCW campaign Gantt (Thu 9 Apr)

4. **Verification crons fire automatically:**
   - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

5. **Source link labels — migrate inline "Source →" strings:**
   AsymRenderer.sourceLabel(url) is now available. Individual dashboard inline Source → strings not yet using it — migrate as dashboards are touched (not urgent).

6. **eghtm-full.md filename rename** (low priority):
   Content updated to ESA but filename in asym-intel-internal is still eghtm-full.md. Cron prompts don't reference it by filename so safe to defer.

7. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Completed This Session (2 April 2026 evening)

**Housekeeping cleanup:**
- Deleted static/monitors/housekeeping-cron-prompt.md duplicate (bde2e1a3)
- anti-patterns.json v1.1 — FE-021 through FE-025 added; FE-020 corrected to inline renderMarkdown pattern

**Source links systematic pass:**
- ERM tipping cells, SCEM roster rows, WDM heatmap table + map popup — source_url wired
- AsymRenderer.sourceLabel(url) added to renderer.js — 80+ domain mappings, exposed on public API

**Nav brand strip — all 59 monitor HTML pages:**
" Monitor" removed from monitor-nav__brand <span> across all 7 monitors × 8-9 pages

**EGHTM → ESA rename — 21 files:**
Main repo + internal repo; SCEM flag_id updated; methodology content patched

**ESA dashboard bugs fixed (direct to main):**
- Lagrange radar section + nav link + 110 lines Chart.js removed
- Cross-monitor FE-022 scope bug fixed: renderCrossMonitor moved into report-latest .then() where d is in scope

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

1. Sprint 3 remaining (source links migration, WDM/SCEM schema-gated items)
2. Sprint 2B as crons fire this week
3. Pipeline outsourcing review → WDM/ESA/AGM/ERM pipelines (after FCW Thu 10 Apr validates)
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
- AsymRenderer.sourceLabel(url) available for domain-aware source link labels

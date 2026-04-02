# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 end-of-day wrap (~21:14 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

2. **Verify FCW schedule self-report on next run** (Thu 9 Apr 09:00 UTC) — confirm it logs "✓ On schedule" not a late-invocation warning. First full 0C/0D/0E pipeline test.

3. **Sprint 3 remainder — doable now, no blockers (~2.5 hrs):**
   - GMM: tail risk note tooltips (20 min)
   - GMM: scenario cards (30 min)
   - AGM: M06 arXiv stub section in report.html (20 min)
   - AGM: risk vector heat grid in report.html (30 min)
   - ALL: inline `Source →` → `AsymRenderer.sourceLabel()` migration (opportunistic)

4. **Sprint 2B data-gated renders (fires this week):**
   - WDM Category B sections verify (Mon 6 Apr after cron)
   - ESA defence spending bar (Wed 8 Apr after cron)
   - FCW campaign Gantt (Thu 9 Apr after cron)

5. **Verification crons fire automatically:**
   - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

6. **After FCW Thu 9 Apr validates:** begin WDM pipeline build (outsourcing review first)

7. **Sprint 3 schema-gated (Sprint 4 — blocked):**
   - WDM: silent_erosion, signal.history, severity_sub
   - SCEM: GEI CONTESTED disclaimer, indicator deviation chart fix

8. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Completed This Session (2 April 2026 — full day)

**Morning (Sprint 3A + infrastructure):**
- All analyst crons migrated to slim repo pointers (docs/crons/ registry)
- 7/7 annual calibration files created and wired
- FCW + GMM + SCEM GitHub Actions pipelines live
- Staging divergence guard live
- Sprint 3A merged: FCW campaigns + Chatter, GMM Fed Funds/Sentiment, WDM weekly_brief, SCEM roster_watch
- Sprint 3B merged: Cross-monitor flags all 6 dashboards, AGM nav, ERM reverse_cascade, ESA radar +40%

**Afternoon/Evening:**
- Housekeeping: duplicate prompt deleted; anti-patterns.json v1.1 (FE-021–025)
- Source links pass: ERM tipping cells, SCEM roster rows, WDM heatmap + popup
- AsymRenderer.sourceLabel(url) — 80+ domain map in renderer.js
- Nav brand: " Monitor" stripped from all 59 monitor HTML pages
- EGHTM → ESA rename — 21 files across both repos
- ESA dashboard: Lagrange radar removed; cross-monitor FE-022 scope bug fixed
- docs/ROADMAP.md created — single source of truth for all planned work
- COMPUTER.md v2.7 — ROADMAP in Step 0, governance wiring rule, all 7 correct cron IDs
- Skill v1.3 — ROADMAP in Step 0, correct cron IDs, GMM/SCEM pipelines added
- platform-developer.md + domain-analyst-template.md — governance file wiring rule added
- Three new role prompts: platform-security-expert.md, seo-discoverability-expert.md, platform-auditor.md
- ROLES.md updated — prompt refs added; Platform Auditor role added

**Late evening — cron infrastructure fix:**
- All 7 analyst crons were pointing to FCW prompt (migration bug) — all recreated as correct slim pointers
- Schedule self-report block added to all 7 cron prompts (detects late/wrong-day invocation)
- All 7 correct IDs confirmed and committed to COMPUTER.md v2.7

---

## Cron Table (confirmed correct — all slim repo pointers)

| Layer | Name | ID | Schedule |
|---|---|---|---|
| Analyst | WDM | f7bd54e9 | Mon 06:00 UTC |
| Analyst | GMM | c94c4134 | Tue 08:00 UTC |
| Analyst | ESA | 0b39626e | Wed 19:00 UTC |
| Analyst | FCW | b17522c3 | Thu 09:00 UTC |
| Analyst | AGM | 5ac62731 | Fri 09:00 UTC |
| Analyst | ERM | ce367026 | Sat 05:00 UTC |
| Analyst | SCEM | 8cdb83c8 | Sun 18:00 UTC |
| Housekeeping | Platform Housekeeping | 7e058f57 | Mon 08:00 UTC |
| Guard | Staging divergence guard | aec126c5 | Daily ~18:00 UTC |
| Calibration | Annual calibration reminder | e6668dce | 28 Mar annually |
| Verification | SCEM verify | a67a9739 | Sun 5 Apr 18:30 (one-shot) |
| Verification | WDM verify | 10ddf5f0 | Mon 6 Apr 06:30 (one-shot) |

## GitHub Actions Pipelines (external — NOT Computer crons)

| Monitor | Workflow | Schedule | Model |
|---|---|---|---|
| FCW | fcw-collector.yml | Daily 07:00 UTC | sonar |
| FCW | fcw-weekly-research.yml | Wed 18:00 UTC | sonar-pro |
| FCW | fcw-reasoner.yml | Wed 20:00 UTC | sonar-deep-research |
| GMM | gmm-collector.yml | Daily 06:00 UTC | sonar |
| GMM | gmm-weekly-research.yml | Mon 18:00 UTC | sonar-pro |
| GMM | gmm-reasoner.yml | Mon 20:00 UTC | sonar-deep-research |
| SCEM | scem-collector.yml | Daily 06:00 UTC | sonar |
| SCEM | scem-weekly-research.yml | Sat 18:00 UTC | sonar-pro |
| SCEM | scem-reasoner.yml | Sat 20:00 UTC | sonar-deep-research |

---

## What's Next (in order)

1. GMM Collector verify (Fri 3 Apr)
2. Sprint 3 remainder — GMM tooltips/scenarios, AGM M06/risk grid (~2.5 hrs)
3. Sprint 2B as crons fire this week
4. WDM pipeline (after FCW Thu 9 Apr validates)
5. Sprint 4 schema sprint — one monitor per session, ~2 hrs each
6. ESA/AGM/ERM pipelines (sequential after WDM)
7. Sprint 5 — design sessions required before any build

---

## Architecture Notes (stable)

- All crons slim repo pointers — edit .md in docs/crons/ or static/monitors/{slug}/, commit, done
- ARCHITECTURE.md mandatory before any HTML/CSS/JS work
- FE-020: inline renderMarkdown (report.html pattern), NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- Staging reset to main after every direct-file merge
- AsymRenderer.sourceLabel(url) available for domain-aware source link labels
- ROADMAP.md is the single source of truth for all planned work — update at every wrap
- Governance file wiring rule: new persistent files → Step 0 in COMPUTER.md + skill + notes. Canonical test in docs/prompts/platform-developer.md.
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval

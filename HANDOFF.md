# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 session wrap (~21:30 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

2. **Check FCW schedule self-report** (Thu 9 Apr 09:00 UTC) — first full 0C/0D/0E test after today's FCW validation.

3. **FCW schedule discrepancy** — FCW cron b17522c3 was firing at 18:00 UTC not 09:00 UTC. Recreated during today's session. Verify next Thursday run fires at 09:00 UTC.

4. **Sprint 3 remainder — doable now, no blockers (~2.5 hrs):**
   - GMM: tail risk note tooltips (20 min)
   - GMM: scenario cards (30 min)
   - AGM: M06 arXiv stub section in report.html (20 min)
   - AGM: risk vector heat grid in report.html (30 min)
   - ALL: inline `Source →` → `AsymRenderer.sourceLabel()` migration (opportunistic)

5. **Sprint 2B data-gated renders (fires this week):**
   - WDM Category B sections verify (Mon 6 Apr after cron)
   - ESA defence spending bar (Wed 8 Apr after cron)
   - FCW campaign Gantt (Thu 9 Apr after cron)

6. **Verification crons fire automatically:**
   - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

7. **WDM Analyst first full pipeline run: Mon 7 Apr 06:00 UTC**
   Steps 0C/0D/0E now wired. First run will load weekly research (Sun 18:00 UTC)
   and Reasoner (Sun 20:00 UTC) output before methodology.

8. **COMPUTER.md GitHub Actions table**: WDM added (v2.8). 12 workflows now active.

9. **Next pipeline builds** (sequential, after WDM validates Mon 7 Apr):
   ESA → AGM → ERM (one per session, ~1.5 hrs each following WDM pattern)

10. **Sprint 4 schema sprint** — still blocked:
    - WDM: silent_erosion, signal.history, severity_sub
    - SCEM: GEI CONTESTED disclaimer, indicator deviation chart fix

11. **User actions pending:**
    - GSC domain property: DNS TXT record for asym-intel.info
    - Cloudflare: enable Bot Fight Mode + Page Shield
    - Fortiguard recategorisation: News and Media / Research

---

## Completed This Session (2 April 2026 — full day + evening)

**Morning-afternoon (see previous wraps for detail):**
- All analyst crons migrated to slim repo pointers (docs/crons/ registry)
- 7/7 annual calibration files created and wired
- FCW + GMM + SCEM GitHub Actions pipelines live
- Sprint 3 Groups A+B+C merged
- Housekeeping dedup, anti-patterns v1.1, source links pass
- EGHTM → ESA rename (21 files), ESA dashboard bugs fixed
- COMPUTER.md v2.7, Skill v1.3, ROADMAP.md, governance infrastructure

**Evening (this session):**
- WDM pipeline built — 3 GitHub Actions workflows committed to asym-intel-main:
  - wdm-collector.yml (daily 07:00 UTC, sonar)
  - wdm-weekly-research.yml (Sun 18:00 UTC, sonar-pro)
  - wdm-reasoner.yml (Sun 20:00 UTC, sonar-deep-research)
- Pipeline files: collect.py, weekly-research.py, wdm-reasoner.py
- API prompts: wdm-collector-api-prompt.txt, wdm-weekly-research-api-prompt.txt
- Directory stubs: daily/, weekly/, reasoner/ with READMEs + stub JSONs
- WDM Analyst cron prompt: Steps 0C/0D/0E wired + Step 1 pipeline-aware
- COMPUTER.md v2.8 — WDM added to GitHub Actions table (12 total)
- notes-for-computer.md — WDM pipeline session logged

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

## GitHub Actions Pipelines (external — NOT Computer crons) — 12 active

| Monitor | Workflow | Schedule | Model |
|---|---|---|---|
| WDM | wdm-collector.yml | Daily 07:00 UTC | sonar |
| WDM | wdm-weekly-research.yml | Sun 18:00 UTC | sonar-pro |
| WDM | wdm-reasoner.yml | Sun 20:00 UTC | sonar-deep-research |
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

1. Verify WDM Collector first run (Thu 3 Apr 07:00 UTC)
2. Sprint 3 remainder — GMM tooltips/scenarios, AGM M06/risk grid (~2.5 hrs)
3. Sprint 2B as crons fire this week
4. WDM Analyst first full pipeline run (Mon 7 Apr 06:00 UTC) — verify 0C/0D/0E
5. ESA pipeline (after WDM validates)
6. AGM, ERM pipelines (sequential)
7. Sprint 4 schema sprint — one monitor per session

---

## Architecture Notes (stable)

- All crons slim repo pointers — edit .md in docs/crons/ or static/monitors/{slug}/, commit, done
- ARCHITECTURE.md mandatory before any HTML/CSS/JS work
- FE-020: inline renderMarkdown (report.html pattern), NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- Staging reset to main after every direct-file merge
- AsymRenderer.sourceLabel(url) available for domain-aware source link labels
- ROADMAP.md is the single source of truth for all planned work — update at every wrap
- Governance file wiring rule: new persistent files → Step 0 in COMPUTER.md + skill + notes
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval
- WDM pipeline: FCW pattern applied exactly — outsourcing review checklist followed

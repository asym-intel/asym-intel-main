# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-02 end-of-day wrap (~20:13 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

1. **Verify FCW cron schedule** — FCW fired at 18:00 UTC today (20:00 CEST), not 09:00 UTC as documented in COMPUTER.md. Likely the cron was created at 18:00 UTC during today's migration and COMPUTER.md was set to 09:00 UTC incorrectly. Check actual schedule on cron `1d51ae99` and correct whichever is wrong. Update COMPUTER.md cron table to match.

2. **Check GMM Collector first run** (Fri 3 Apr 06:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/macro-monitor/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

3. **Sprint 3 remainder — doable now, no blockers (~2.5 hrs):**
   - GMM: tail risk note tooltips (20 min)
   - GMM: scenario cards (30 min)
   - AGM: M06 arXiv stub section in report.html (20 min)
   - AGM: risk vector heat grid in report.html (30 min)
   - ALL: inline `Source →` → `AsymRenderer.sourceLabel()` migration (opportunistic as pages are touched)

4. **Sprint 2B data-gated renders (fires this week):**
   - WDM Category B sections verify (Mon 6 Apr after cron)
   - ESA defence spending bar (Wed 8 Apr after cron)
   - FCW campaign Gantt (Thu 9 Apr after cron)

5. **Verification crons fire automatically:**
   - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
   - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

6. **After FCW Thu 9 Apr validates:** begin WDM pipeline build (outsourcing review first per COMPUTER.md)

7. **Sprint 3 schema-gated items (Sprint 4 — blocked):**
   - WDM: silent_erosion, signal.history, severity_sub
   - SCEM: GEI CONTESTED disclaimer, indicator deviation chart fix

8. **User actions pending:**
   - GSC domain property: DNS TXT record for asym-intel.info
   - Cloudflare: enable Bot Fight Mode + Page Shield
   - Fortiguard recategorisation: News and Media / Research

---

## Completed This Session (2 April 2026 — full day)

**Morning session (Sprint 3A + infrastructure):**
- All 9 crons migrated to slim repo pointers (docs/crons/ registry)
- 7/7 annual calibration files created and wired (Step 0B+ auto-discovery)
- FCW + GMM + SCEM GitHub Actions pipelines live (Collector/Weekly/Reasoner)
- Staging divergence guard live (aec126c5)
- Sprint 3A merged: FCW 12 campaigns + Chatter, GMM Fed Funds/Sentiment, WDM weekly_brief, SCEM roster_watch
- Sprint 3B merged: Cross-monitor flags all 6 dashboards, AGM nav, ERM reverse_cascade, ESA radar +40%, GMM sidebar fix

**Evening session:**
- Housekeeping: duplicate housekeeping-cron-prompt.md deleted
- anti-patterns.json v1.1 — FE-021 through FE-025 added
- Source links systematic pass — ERM tipping cells, SCEM roster rows, WDM heatmap + popup wired
- `AsymRenderer.sourceLabel(url)` — 80+ domain map added to renderer.js, exposed on public API
- Nav brand — " Monitor" stripped from all 59 monitor HTML pages across 7 monitors
- EGHTM → ESA rename — 21 files across both repos
- ESA dashboard — Lagrange radar section removed; cross-monitor FE-022 scope bug fixed
- `docs/ROADMAP.md` created — single source of truth for all planned work
- COMPUTER.md v2.6 — ROADMAP in Step 0, governance file wiring rule, canonical test reference
- Skill v1.3 — ROADMAP in Step 0, cron IDs corrected, GMM/SCEM pipelines added
- `platform-developer.md` — Step 5 (wire new governance files) added
- `domain-analyst-template.md` — governance file wiring rule added
- Three new role prompts created:
  - `docs/prompts/platform-security-expert.md` v1.0
  - `docs/prompts/seo-discoverability-expert.md` v1.0
  - `docs/prompts/platform-auditor.md` v1.0 (quarterly audit role — replaces ADMIN concept)
- `docs/ROLES.md` updated — prompt file refs added to Security/SEO; Platform Auditor role added
- `docs/ROADMAP.md` updated — specialist roles in Ongoing/Evergreen; first-run setup note

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

- All crons slim repo pointers — edit .md in docs/crons/, commit, done
- ARCHITECTURE.md mandatory before any HTML/CSS/JS work
- FE-020: inline renderMarkdown (report.html pattern), NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- Staging reset to main after every direct-file merge
- AsymRenderer.sourceLabel(url) available for domain-aware source link labels
- 'wrap' = session checkpoint | 'merge' = HTML deployment approval
- ROADMAP.md is the single source of truth for all planned work — update at every wrap
- Governance file wiring rule: new persistent files must be wired into Step 0 in COMPUTER.md, skill, and notes-for-computer.md. Canonical test in docs/prompts/platform-developer.md.

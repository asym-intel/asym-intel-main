# HANDOFF.md — Asymmetric Intelligence
**Generated:** 2026-04-03 session wrap (~01:16 CEST) — full day + evening session
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

### Peter — action required

1. **Branch protection on main** — HIGH security finding (SEC-009)
   GitHub repo settings → Branches → require CI to pass, include administrators

2. **Integrity manifest GA workflow approval** — draft at `docs/security/drafts/generate-integrity-manifest.yml`
   Review and move to `.github/workflows/` when ready

3. **Cloudflare security headers** — HSTS max-age 31536000 + X-Frame-Options + CSP + Referrer-Policy
   Via Cloudflare Transform Rules (spec in docs/prompts/platform-security-expert.md)

4. **Cloudflare Zone ID + Account ID** → add to `asym-intel-internal/platform-config.md`
   (Cloudflare dashboard → asym-intel.info overview → Zone ID in right sidebar)

5. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

### Computer — next session work queue (start fresh session)

6. **PED first session** — Peter's RTF observations are the brief (Prompt-B-PED.rtf)
   - docs/ux/decisions.md full population (Sections 1–4)
   - docs/ux/colour-registry.md creation
   - 5-page progressive disclosure audit
   - Gap list → notes-for-computer.md for Platform Developer
   - Split into two subagents: observe first → write second (session limit lesson)

7. **JSON-LD structured data** — HIGH SEO finding, blocks AI search
   Platform Developer session: layouts/partials/head.html + layouts/_default/single.html
   Spec: docs/seo/ai-search-audit-2026-Q2.md Section 5

8. **docs/benchmarks/** — first-session knowhow for Security/SEO/Platform Developer

9. **Sprint 3 remainder** (no blockers, ~2.5 hrs):
   - GMM: tail risk note tooltips + scenario cards
   - AGM: M06 arXiv stub + risk vector heat grid

10. **Sprint 2B data-gated** (fires this week):
    - WDM Category B verify (Mon 6 Apr)
    - ESA defence spending bar (Wed 8 Apr)
    - FCW campaign Gantt (Thu 9 Apr)

11. **Next pipeline builds** (after WDM validates Mon 7 Apr): ESA → AGM → ERM

---

## Completed This Session (2–3 April 2026 — full day)

### Three-session benchmark (Sessions 1–3)
- Platform Developer: FCW dashboard divergence investigated + fixed · FCW stub corrected · repo-audit committed
- Security Expert (first-ever): docs/security/ created · secrets rotation · third-party audit with SRI hashes · integrity manifest spec · platform-status.md
- SEO Expert (first-ever): docs/SEO.md + ai-search-audit-2026-Q2.md · robots.txt fixed · 0/3 AI search queries cited (baseline)

### HIGH findings resolved this session
- ✅ **SEC-010** SRI hashes — PR #29 merged, all 7 dashboards
- ✅ **SEC-008** integrity-manifest.json — live on main, all 7 monitors hashed
- ✅ **SEO-010** WDM meta description — "democratic backsliding" + V-Dem + Freedom House added
- ✅ **FCW dashboard** — legacy 140k replaced with modern 37k shared-library version on main
- ✅ **SEO methodology dates** — all 7 pages corrected from 2020-01-01 to actual dates
- ✅ **FCW stub files** — both corrected, GA architecture documented

### Governance improvements
- COMPUTER.md v3.1 — wrap step 0 (incomplete work check), subagent sizing rules, cancelled-subagent pitfall
- Skill v1.6 — matching updates
- platform-config.md — created in asym-intel-internal (Zone ID placeholder for Peter)
- docs/audits/repo-audit-2026-04-02.md — committed

### Still open (HIGH — requires Peter)
- ⚠️ Branch protection on main (SEC-009) — Peter action
- ⚠️ Cloudflare headers — Peter action
- ⚠️ Integrity manifest workflow approval — Peter action
- ⚠️ Cloudflare Zone ID in platform-config.md — Peter action

---

## Cron Table (confirmed correct)

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
| Quarterly | GSC audit | f78e0c2c | 1 Jan/Apr/Jul/Oct 09:00 UTC |

## GitHub Actions (12 active)

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

## Architecture Notes (stable)

- COMPUTER.md v3.1 — wrap step 0, subagent sizing table, cancelled-subagent pitfall #16
- Subagent rule: browse 5+ pages AND write docs → two subagents (observe then write)
- Subagent rule: >90min session → defer complex multi-subagent work to fresh session
- All crons slim repo pointers — edit .md in docs/crons/ or static/monitors/{slug}/, commit, done
- FE-020: inline renderMarkdown for narrative fields, NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- platform-config.md in asym-intel-internal — canonical home for Zone IDs, account IDs

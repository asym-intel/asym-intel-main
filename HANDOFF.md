# HANDOFF.md - Asymmetric Intelligence
**Generated:** 2026-04-03 session wrap (~00:30 CEST) — three-session benchmark complete
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

## Immediate Actions — Next Session

### Peter — action required before next Computer session

1. **FCW dashboard PR #28 — visual sign-off needed**
   PR staging → main is open: https://github.com/asym-intel/asym-intel-main/pull/28
   Browse the staging preview and confirm FCW dashboard renders correctly (modern Blueprint v2.1 shared-library version). Once confirmed, merge.

2. **Branch protection on main — HIGH security finding**
   Enable branch protection on `asym-intel-main` → main:
   - Require status checks to pass (CI build.yml)
   - Include administrators (must apply to owner too, not just collaborators)
   GitHub repo settings → Branches → Add rule for `main`

3. **HSTS max-age — update Cloudflare Transform Rule**
   Current: max-age=15552000 (180 days). Required: max-age=31536000 (365 days).

4. **Add security headers via Cloudflare Transform Rules**
   X-Frame-Options: DENY
   Content-Security-Policy: (spec in docs/prompts/platform-security-expert.md)
   Referrer-Policy: strict-origin-when-cross-origin

5. **GSC property verification** ✅ Confirmed — TXT record live in public DNS (`google-site-verification=3ig4MTYb8s0zrWYRlo5JskGc5SNFa8PwHmFuZ4xC5X0`). No action needed.

6. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

### Computer — platform work queue (in order)

7. **PR #28 merge** — after Peter confirms visual sign-off above, merge and reset staging to main.

8. **SRI hashes on Chart.js CDN tags** — HIGH security finding
   Platform Developer session: add `integrity=` + `crossorigin=anonymous` to all 7 monitor dashboard Chart.js `<script>` tags. Standardise to v4.4.7.
   SRI hash for 4.4.7: `sha384-vsrfeLOOY6KuIYKDlmVH5UiBmgIdB1oEf7p01YgWHuqmOHfZr374+odEv96n9tNC`
   Full hashes for 4.4.4 and 4.4.0 in docs/security/third-party-audit.md.

9. **JSON-LD structured data** — HIGH SEO finding, blocks AI search visibility
   Platform Developer: implement in layouts/partials/head.html and layouts/_default/single.html.
   Full spec: docs/seo/ai-search-audit-2026-Q2.md Section 5.
   Types needed: Dataset, NewsArticle, FAQPage, BreadcrumbList.

10. **WDM meta description fix** — HIGH SEO finding
    One front-matter update to content/monitors/democratic-integrity/_index.md.
    Proposed: "Weekly early-warning intelligence on democratic backsliding, institutional erosion, and state capture — tracking V-Dem and Freedom House signals before annual indices catch up."

11. **Methodology page lastmod dates** — MEDIUM SEO finding
    All 7 methodology pages carry lastmod 2020-01-01. Set correct dates in Hugo front-matter.

12. **integrity-manifest.json** — HIGH security finding
    New GitHub Actions workflow generate-integrity-manifest.yml (Mon 09:00 UTC, after Housekeeping).
    Full spec: docs/security/integrity-manifest-spec.md.
    Requires Peter approval as a new workflow.

13. **Automated pipeline failure notifications** — MEDIUM security finding
    All 14 GA workflows (FCW/GMM/SCEM/WDM Collector/Research/Reasoner) need `if: failure()` notification step.

14. **Sprint 3 remainder — doable now, no blockers (~2.5 hrs):**
    - GMM: tail risk note tooltips (20 min)
    - GMM: scenario cards (30 min)
    - AGM: M06 arXiv stub section in report.html (20 min)
    - AGM: risk vector heat grid in report.html (30 min)

15. **Sprint 2B data-gated (fires this week):**
    - WDM Category B sections verify (Mon 6 Apr after cron)
    - ESA defence spending bar (Wed 8 Apr after cron)
    - FCW campaign Gantt (Thu 9 Apr after cron)

16. **Verification crons fire automatically:**
    - SCEM: Sun 5 Apr 18:30 UTC (a67a9739)
    - WDM: Mon 6 Apr 06:30 UTC (10ddf5f0)

17. **WDM Analyst first full pipeline run: Mon 7 Apr 06:00 UTC**

18. **Next pipeline builds** (sequential, after WDM validates Mon 7 Apr):
    ESA → AGM → ERM

---

## Completed — Three-Session Benchmark (2–3 April 2026)

### Session 1 — Platform Developer

- **FCW dashboard.html divergence investigated and fixed (staging)**
  static/ (139k, legacy embedded CSS) vs docs/ (37k, modern shared library) — root cause identified: shared-library migration was never applied to static/. Maintenance cron was writing into legacy file. Staging branch updated with modern version. PR #28 open.
- **FCW-DAILY-FEEDER-PROMPT-v4.md missing — resolved**
  Both fcw-daily-feeder-cron.md stubs updated. No active cron was broken. GA workflow is canonical. Commits: fc489ff2, 00835ff2.
- **Repo audit committed** to docs/audits/repo-audit-2026-04-02.md (commit afcecdce, 14,012 bytes). 2 CRITICAL, 2 HIGH, 3 MEDIUM, 2 LOW findings documented.
- **platform-dev-findings.md** saved to workspace for Session 2/3 reference.

### Session 2 — Platform Security Expert (first-ever session)

- **docs/security/ created** — all four required files committed to main:
  - docs/security/secrets-rotation-schedule.md (7.4 KB, commit 44cbd432)
  - docs/security/third-party-audit.md (10.4 KB, commit 375fe577) — SRI hashes computed for all Chart.js versions in use
  - docs/security/integrity-manifest-spec.md (8.7 KB, commit e3ba824d)
  - docs/security/platform-status.md (7.9 KB, commit 37e07da9) — quarterly checklist results
- **Findings:** 0 CRITICAL, 3 HIGH, 3 MEDIUM, 3 LOW
- **Positive:** Pipeline at /pipeline/ returns 404 ✅ · Single owner on both repos ✅ · No secrets in logs ✅ · No Chart.js CVEs ✅
- **security-findings.md** saved to workspace for Session 3 reference.

### Session 3 — SEO & Discoverability Expert (first-ever session)

- **docs/seo/ created** — three files committed to main:
  - docs/SEO.md (23.9 KB, commit 317303c0) — strategy + quarterly findings
  - docs/seo/ai-search-audit-2026-Q2.md (14.9 KB, commit 3ed50a7e) — AI search baseline
  - docs/seo/gsc-monthly-audit.md (6.2 KB, commit 23d9a435) — stub, pending GSC connection
- **docs/robots.txt updated** (commit d8e56930) — Disallow: /pipeline/ and /*.json added (Security LOW finding resolved)
- **Findings:** 3 HIGH, 5 MEDIUM, 2 LOW
- **AI search baseline:** 0 of 3 benchmark queries cite asym-intel.info. Primary driver: no structured data on any page.
- **notes-for-computer.md** updated in asym-intel-internal with all three sessions' findings.

---

## Specialist Sessions — Status Update

| Session | Status | Key output |
|---------|--------|------------|
| Platform Security Expert | ✅ First session complete | docs/security/ created, 3 HIGH findings documented |
| SEO & Discoverability Expert | ✅ First session complete | docs/SEO.md + AI search baseline, 3 HIGH findings |
| Platform Experience Designer | 📋 Next specialist session | Peter's reader observations + colour-registry.md |
| Intelligence Surface Analyst | 📋 After PED | Five-audience gap test |

---

## Completed Previously (2 April 2026)

**Morning-afternoon:** All analyst crons migrated to slim repo pointers · 7/7 annual calibration files · FCW + GMM + SCEM GitHub Actions pipelines · Sprint 3A+B+C merged · Housekeeping dedup · EGHTM → ESA rename (21 files) · COMPUTER.md v2.7 · Skill v1.3 · ROADMAP.md · governance infrastructure

**Evening:** WDM pipeline built (3 GA workflows) · COMPUTER.md v2.8

**Late evening:** ROLES.md v1.2/v1.3 · role enhancement addenda v1.0 · all 6 role prompts updated · MISSION.md v1.2 · docs/security/platform-status.md + docs/ux/decisions.md created · governance mirror deleted from asym-intel-internal

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
| Quarterly | GSC audit | f78e0c2c | 1 Jan/Apr/Jul/Oct 09:00 UTC |

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

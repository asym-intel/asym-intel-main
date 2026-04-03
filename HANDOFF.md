# HANDOFF.md — Asymmetric Intelligence
**Generated:** 2026-04-03 session wrap (~02:10 CEST) — full evening session
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

> **Ready-to-paste prompt for next session:** `docs/prompts/next-session.md`

## Immediate Actions — Next Session

### Peter — action required

1. **PR #30 — nav fix** — visual check on FCW report.html + AGM report.html then merge
   https://github.com/asym-intel/asym-intel-main/pull/30

2. **Branch protection on main** (SEC-009 HIGH) — GitHub repo settings → Branches

3. **Integrity manifest workflow** — move `docs/security/drafts/generate-integrity-manifest.yml` → `.github/workflows/`

4. **Cloudflare security headers** — HSTS 31536000 + X-Frame-Options + CSP + Referrer-Policy

5. **Cloudflare Zone ID + Account ID** → `asym-intel-internal/platform-config.md`

6. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

7. **GSC property verification** — https://search.google.com/search-console/

### Computer — next session work queue

8. **PED first session** — Peter's reader observations are the brief (notes-for-computer.md, search "Prompt-B-PED")
   Split into two subagents: observe first → write second. See next-session.md for full prompt.

9. **Sprint 3 remainder** — GMM tail risk tooltips + scenario cards; AGM M06 arXiv stub + risk vector heat grid

10. **Sprint 2B data-gated** — WDM Category B (Mon 6 Apr), ESA defence bar (Wed 8 Apr), FCW Gantt (Thu 9 Apr)

---

## Completed This Session (2–3 April 2026 — evening)

### JSON-LD structured data (SEO HIGH — resolved)
- ✅ `layouts/partials/head.html` — BreadcrumbList + Dataset (monitor section pages)
- ✅ `layouts/_default/single.html` — NewsArticle (upgraded from Article) + isAccessibleForFree + license + isPartOf
- ✅ Hugo minifier double-escaping fixed — `printf+safeHTML` wrapping entire script tag
- ✅ Verified clean in docs/ built output

### Housekeeping Option B
- ✅ `housekeeping-cron-prompt.md` copied to `static/monitors/`
- ✅ `lastmod` added to about.md, search.md, subscribe.md
- ℹ️ `content/tags/_index.md` does not exist — site uses `content/topics/` (no action)

### Nav inconsistency fix — FCW + AGM (PR #30 open)
- ✅ Principle identified: hardcoded nav per page → new pages not propagated to all siblings
- ✅ All 7 monitors audited — only FCW and AGM affected
- 🔄 PR #30 staged: FCW report+overview (Chatter added), AGM report+overview (Digest added)
- ⚠️ Awaiting Peter visual sign-off before merge

### Governance
- ✅ PED prompt v1.1 — Example-as-Instance Rule + PED-007 failure mode
- ✅ FE-026 — Hugo minifier JSON-LD pattern in ARCHITECTURE.md + anti-patterns.json
- ✅ GitHub Pages `build_type: workflow` — Jekyll runner disabled permanently
- ✅ notes-for-computer.md — Jekyll fix + nav audit + PED rule all logged

### Still open (HIGH — Peter action)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ Cloudflare headers
- ⚠️ Integrity manifest workflow approval
- ⚠️ Cloudflare Zone ID in platform-config.md

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

## GitHub Actions (12 active — unchanged)

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

- COMPUTER.md v3.2 — wrap step 0, memoryless-instance rule, subagent sizing table
- **FE-026** — Hugo `--minify` escapes JSON-LD inside script tags. Use `printf+safeHTML` for entire tag. See ARCHITECTURE.md.
- **Nav pattern** — monitor nav is hardcoded per page. Adding a new page requires updating all siblings manually. Structural fix queued Sprint 5.
- GitHub Pages `build_type: workflow` — Jekyll runner permanently disabled
- platform-config.md in asym-intel-internal — canonical home for Zone IDs, account IDs

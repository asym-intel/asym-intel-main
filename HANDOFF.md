# HANDOFF.md — Asymmetric Intelligence
**Generated:** 2026-04-03 session wrap (~02:00 CEST)
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

> **Ready-to-paste prompt for next session:** `docs/prompts/next-session.md`
> This file is always kept current — read it instead of reconstructing the prompt from this file.

## Immediate Actions — Next Session

### Peter — action required

1. **Branch protection on main** — HIGH security finding (SEC-009)
   GitHub repo settings → Branches → require CI to pass, include administrators

2. **Integrity manifest GA workflow approval** — draft at `docs/security/drafts/generate-integrity-manifest.yml`
   Review and move to `.github/workflows/` when ready

3. **Cloudflare security headers** — HSTS max-age 31536000 + X-Frame-Options + CSP + Referrer-Policy
   Via Cloudflare Transform Rules (spec in docs/prompts/platform-security-expert.md)

4. **Cloudflare Zone ID + Account ID** → add to `asym-intel-internal/platform-config.md`

5. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
   ```
   gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
   ```

6. **GSC property verification** — https://search.google.com/search-console/ (DNS TXT done 2 April — confirm in-console)

### Computer — next session work queue

7. **PED first session** — Peter's reader observations are the brief (in notes-for-computer.md, Prompt-B-PED)
   - docs/ux/decisions.md full population (Sections 1–4)
   - docs/ux/colour-registry.md creation (PED-004 prerequisite)
   - 5-page progressive disclosure audit
   - Gap list → notes-for-computer.md for Platform Developer
   - Split into two subagents: observe first → write second
   - Note: Example-as-Instance Rule (PED-007) now in PED prompt v1.1 — first session applies it

8. **Sprint 3 remainder** (no blockers):
   - GMM: tail risk note tooltips + scenario cards
   - AGM: M06 arXiv stub + risk vector heat grid

9. **Sprint 2B data-gated** (fires this week):
   - WDM Category B verify (Mon 6 Apr)
   - ESA defence spending bar (Wed 8 Apr)
   - FCW campaign Gantt (Thu 9 Apr)

10. **Next pipeline builds** (after WDM validates Mon 7 Apr): ESA → AGM → ERM

---

## Completed This Session (2–3 April 2026 — evening session)

### JSON-LD structured data — SEO HIGH finding resolved
- ✅ `layouts/partials/head.html` — BreadcrumbList (all non-home pages) + Dataset (monitor section pages)
- ✅ `layouts/_default/single.html` — Article → NewsArticle upgrade + isAccessibleForFree + license + author + isPartOf
- ✅ Hugo minifier double-escaping bug fixed — printf+safeHTML pattern for all script[type=application/ld+json] tags
- ✅ Verified clean in built docs/ output: headline, description, BreadcrumbList, Dataset all correct

**Pattern established (add to ARCHITECTURE.md / anti-patterns):**
Hugo `--minify` escapes content inside `<script>` tags. For JSON-LD, use:
`{{ printf \`<script type="application/ld+json">%s</script>\` ($dict | jsonify) | safeHTML }}`
NOT `<script type="application/ld+json">{{ $dict | jsonify | safeHTML }}</script>`

### Housekeeping Option B
- ✅ `housekeeping-cron-prompt.md` copied to `static/monitors/` (was only in docs/ — source/output broken)
- ✅ `lastmod: 2026-04-01T00:00:00Z` added to about.md, search.md, subscribe.md (3 of 4 utility pages)
- ℹ️ `content/tags/_index.md` does not exist — site uses `content/topics/` instead (no action needed)

### PED prompt governance
- ✅ `platform-experience-designer.md` v1.1 — Example-as-Instance Rule + PED-007 failure mode added
- Rule: Peter's UX examples are instances of principles; PED must extract principle, audit all 7 monitors, spec at principle level

### Jekyll Pages runner
- ✅ GitHub Pages `build_type` switched from `legacy` → `workflow`
- Jekyll auto-builder no longer fires on push — permanent red build eliminated
- Hugo build.yml remains the only build pipeline; Cloudflare serving unaffected

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

## Architecture Notes

- COMPUTER.md v3.2 — wrap step 0, memoryless-instance rule, subagent sizing table
- FE-020: inline renderMarkdown for narrative fields, NOT AsymRenderer.renderMarkdown
- DQ-001: SCEM roster_watch must not contain conflicts already in conflict_roster
- **NEW — Hugo minifier JSON-LD pattern:** use printf+safeHTML for entire script tag (not safeHTML on jsonify output alone)
- platform-config.md in asym-intel-internal — canonical home for Zone IDs, account IDs
- GitHub Pages build_type: workflow (Jekyll runner permanently disabled)

# HANDOFF.md — Asymmetric Intelligence
**Generated:** 2026-04-03 session wrap (~03:00 CEST) — PED Session 1 full
**Next auto-generation:** Monday 7 April 08:00 UTC (Housekeeping)

---

> **Ready-to-paste prompt for next session:** `docs/prompts/next-session.md`

## Immediate Actions — Next Session

### Peter — action required

1. **PR #31 — visual sign-off needed** — FCW contrast + SCEM nav + GMM nav
   https://github.com/asym-intel/asym-intel-main/pull/31
   Check:
   - FCW dashboard: secondary signal text ("MF1 alert:...") readable on teal panel
   - SCEM dashboard: "Conflict Overview" nav entry present; "Friction Flags" label clear
   - GMM dashboard: updated nav labels match sections on scroll
   Merge when satisfied.

2. **PED Q4 — confidence badge encoding** — review decisions.md Section 4 Q4
   FCW "CONFIRMED" badge uses severity colour (amber). Need: approve separate visual
   class before any confidence badge implementation proceeds.

3. **PED Q6 — homepage hero image** — in scope this sprint or later?

4. **PED Q7 — homepage chatter feed** — PED spec or Platform Developer feature?

5. **PED Q8 — SCEM accent = --critical** — intentional or resolve?

6. **Branch protection on main** (SEC-009 HIGH) — GitHub repo settings → Branches

7. **Integrity manifest workflow** — move `docs/security/drafts/generate-integrity-manifest.yml` → `.github/workflows/`

8. **Cloudflare security headers** — HSTS + X-Frame-Options + CSP + Referrer-Policy

9. **Cloudflare Zone ID + Account ID** → `asym-intel-internal/platform-config.md`

10. **GSC property verification** — https://search.google.com/search-console/

11. **Verify WDM Collector first run** (Thu 3 Apr 07:00 UTC):
    ```
    gh api /repos/asym-intel/asym-intel-main/contents/pipeline/monitors/democratic-integrity/daily/daily-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_meta'])"
    ```

### Computer — next session work queue

12. **PED Sprint 2** — after Peter answers Q4/Q6/Q7/Q8:
    - AGM + ERM dashboard audit (last 2 monitors unreviewed)
    - ESA mobile viewport test (#section-delta font — Peter's observation, unconfirmed at desktop)
    - Signal panel contrast fix on GMM + SCEM (extend Principle 5 fix)
    - SCEM F-flag matrix integrated labels (show meaning inline in tile)
    - Severity badge font size floor (0.6rem → --text-xs in base.css)

13. **Sprint 3 remainder** — GMM tail risk tooltips + scenario cards; AGM M06 arXiv stub + risk vector heat grid

14. **Sprint 2B data-gated** — WDM Category B (Mon 6 Apr), ESA defence bar (Wed 8 Apr), FCW Gantt (Thu 9 Apr)

---

## Completed This Session (2–3 April 2026 — full evening + PED session)

### PED Session 1 — first ever (complete)

**Governance files:**
- ✅ `docs/ux/decisions.md` — fully populated (8 principles, 4-monitor findings, 8 open Qs)
- ✅ `docs/ux/colour-registry.md` — created (severity system, accents, 3 collision warnings)
- ✅ `docs/ROADMAP.md` — PED Sprint 1 complete, Sprint 2 queued
- ✅ `notes-for-computer.md` — INCOMPLETE WORK TRACKER section added

**Monitor fixes staged (PR #31 — awaiting Peter sign-off):**
- ✅ FCW: signal panel secondary text contrast fix (rgba white on teal)
- ✅ SCEM: Conflict Overview nav entry added + Friction Flags label
- ✅ GMM: 4 nav labels aligned to section headings

**Monitor fixes live (merged to main):**
- ✅ Homepage: "Read →" / "Read briefing →" CTAs removed (commits 48e64d4, 9e9673a)

**Audits complete:**
- ✅ WDM dashboard — PASS on contrast, attribution, 60-second test. Minor mismatches noted.
- ✅ GMM, FCW, ESA, SCEM — audited. Findings in decisions.md Section 2.
- ⚠️ AGM, ERM — not yet audited. PED Sprint 2.

### JSON-LD + housekeeping (earlier in session)
- ✅ BreadcrumbList + Dataset + NewsArticle structured data live
- ✅ FE-026 pattern in ARCHITECTURE.md + anti-patterns.json
- ✅ housekeeping-cron-prompt.md to static/monitors/
- ✅ lastmod on about.md, search.md, subscribe.md
- ✅ Jekyll Pages runner disabled (build_type: workflow)
- ✅ Nav fix PR #30 merged — FCW Chatter + AGM Digest

### Still open (HIGH — Peter action)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ Cloudflare headers
- ⚠️ Integrity manifest workflow approval
- ⚠️ Cloudflare Zone ID in platform-config.md
- ⚠️ PR #31 visual sign-off

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
- **FE-026** — Hugo `--minify` escapes JSON-LD inside script tags. Use `printf+safeHTML` for entire tag.
- **Nav pattern** — monitor nav is hardcoded per page. Structural fix queued Sprint 5.
- **Principle 5** — solid accent-background panels: all text must be white/near-white. See colour-registry.md §4.
- **decisions.md** — PED persistent memory. 8 principles, examples, open questions. Read before any UX work.
- GitHub Pages `build_type: workflow` — Jekyll runner permanently disabled
- platform-config.md in asym-intel-internal — canonical home for Zone IDs, account IDs

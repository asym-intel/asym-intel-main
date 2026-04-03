# HANDOFF.md — Asymmetric Intelligence Platform
**Updated:** 2026-04-03 final wrap (~11:03 CEST)

## Platform Status
- Site: ✅ Live at asym-intel.info
- Build: ✅ build.yml with deploy-pages job (fixed today)
- Staging: ✅ Clean (ahead_by: 0, behind_by: 78 — expected after reset)
- CF Cache: ✅ Purged multiple times today

## Cron IDs (all verified)
| Monitor | Cron ID | Schedule |
|---|---|---|
| WDM | f7bd54e9 | Mon 06:00 UTC |
| GMM | c94c4134 | Tue 08:00 UTC |
| ESA | 0b39626e | Wed 19:00 UTC |
| FCW | b17522c3 | Thu 09:00 UTC |
| AGM | 5ac62731 | Fri 09:00 UTC |
| ERM | ce367026 | Sat 05:00 UTC |
| SCEM | 8cdb83c8 | Sun 18:00 UTC |
| Housekeeping | 7e058f57 | Mon 08:00 UTC |

## GitHub Actions Pipelines
**Daily Collectors (06:00/07:00 UTC):** All 7 ✅
**Chatter (06:00 UTC):** All 7 ✅ — FCW/GMM/WDM/SCEM/ESA/ERM 10 items; AGM 1 item (correct — quality filter active)
**Weekly research + Reasoner:** FCW/GMM/SCEM ✅ | ESA/AGM/ERM ❌ not yet built

## Shared Modules (nav.js v1.3 + new today)
| Module | File | Function |
|---|---|---|
| Monitor registry | nav.js MONITOR_REGISTRY | Single source for accent, SVG, name, abbr |
| Nav injection | nav.js injectMonitorNav() | Canonical 9-link nav from URL |
| Brand injection | nav.js injectMonitorBrand() | Logo + name + --monitor-accent |
| Theme toggle | nav.js injectThemeToggle() | Idempotent |
| Footer | nav.js injectMonitorFooter() | Canonical footer |
| Chatter renderer | shared/js/chatter.js | All chatter pages — derives slug from URL |
| Search engine | shared/js/search.js | All search pages — full-text across issues |
| Source labels | renderer.js sourceLabel/sourceLink | 80+ domain map, inline attribution |

## Prompt Quality Infrastructure (new today)
- Version headers on all 17 prompt files
- `asym-intel-internal/prompt-improvements.md` — running quality log
- Housekeeping Step 10 — weekly chatter quality audit (tier%, recency, source bloat)
- AGM blocked domain list: dwealth.news, p3adaptive.com, atlan.com etc.

## Open — Needs next session
1. ESA/AGM/ERM weekly-research + reasoner workflows
2. PED Sprint 2 (Q4/Q6/Q7/Q8 decisions gating it — see decisions.md)
3. ~3 unmatched Source → patterns in FCW/WDM/SCEM dashboards (minor)
4. GMM/ESA annual calibration files (imf-2026, ecfr-2026)
5. Sprint 4 schema items (WDM/SCEM schema-gated renders)
6. AGM chatter — consider 2-3x/week cadence vs daily (low-frequency domain)

## Open — Peter action required
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ GSC property verification (DNS TXT record)

## Deployment reminder
After ANY shared JS/CSS change:
1. Verify live: `curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"`
2. If stale: workflow_dispatch build.yml → `cloudflare_api_key-purge-all-files` (Zone: cc419b7519eba04ef0dc6a7b851930c7)
3. Screenshot a dashboard — confirm no "Failed to load data."

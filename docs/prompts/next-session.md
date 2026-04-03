# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 post-renderer-fix wrap

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: ESA/AGM/ERM pipelines + PED Sprint 2 ---

VERIFY LIVE BEFORE STARTING:
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/renderer.js | node --check /dev/stdin && echo OK
→ Must return OK. If not: check notes-for-computer.md for renderer.js bug pattern.

curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Should show v1.3.

Screenshot https://asym-intel.info/monitors/macro-monitor/dashboard.html
→ Must NOT show "Failed to load dashboard data" or "AsymRenderer is not defined".

Priority queue:

1. ESA/AGM/ERM weekly-research + reasoner workflows
   Pattern: .github/workflows/fcw-weekly-research.yml + fcw-reasoner.yml
   Apply to: european-strategic-autonomy, ai-governance, environmental-risks
   Also update their analyst cron prompts with Steps 0C/0D/0E

2. PED Sprint 2 — surface Peter's open decisions FIRST
   Read docs/ux/decisions.md Section 4 — Q4, Q6, Q7, Q8 need answers before any build.
   If decisions available: run sprint (AGM+ERM audit, ESA mobile test, signal contrast, badge font)

3. Source → pattern cleanup (minor)
   FCW dashboard (1), WDM dashboard (1), SCEM dashboard (1)
   grep "Source →" in static/monitors/{slug}/dashboard.html

4. GMM/ESA annual calibration files

EFFICIENCY REMINDER (COMPUTER.md v3.4):
- Batch 3+ tasks per session. Step 0 loading is fixed overhead — amortise it.
- Housekeeping notifies on any issue. Silence = healthy. Don't open a session to verify health.

DEPLOYMENT REMINDER:
After any shared JS/CSS change → node --check on the file → commit → verify live → CF purge.
CF Zone ID: cc419b7519eba04ef0dc6a7b851930c7
```

## Previous session completed
- ✅ renderer.js syntax bug fixed (sourceLink single-quote escaping — broke all dashboards)
- ✅ CI validator CHECK 17 added — node --check on all shared JS files (commit 480d46cc)
- ✅ Efficiency sprint: staging guard + GSC audit crons deleted, Housekeeping slimmed
- ✅ COMPUTER.md v3.4 — min session size rule
- ✅ docs/monitors/_shared/ artefact deleted

## Peter action required
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC DNS TXT record verification
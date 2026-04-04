# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-04 | Version: post-architecture-alignment

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and
asym-intel-internal/COLLECTOR-ANALYST-ARCHITECTURE.md before starting.

--- VERIFY LIVE BEFORE ANY WORK ---
1. curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
   → Must show v1.3
2. Screenshot https://asym-intel.info/monitors/democratic-integrity/dashboard.html
   → Must NOT show "Failed to load data." or "Loading..."
3. Screenshot https://asym-intel.info/monitors/fimi-cognitive-warfare/chatter.html
   → Must show items (not "Loading today's signals...")
If any fail: see ARCHITECTURE.md deployment runbook + CF purge Zone cc419b7519eba04ef0dc6a7b851930c7

--- ARCHITECTURE STATUS ---
All monitors: weekly cadence (quarterly idea superseded — synthesiser makes weekly affordable).
All 7 Analyst crons: active, weekly, unchanged.
Weekly-research + Reasoner (FCW/GMM/WDM/SCEM): PAUSED — being replaced by Synthesiser layer.
Synthesiser (Layer 1C): NOT YET BUILT — Peter drafting FCW files.

--- FIRST TASK: Review Peter's FCW synthesiser draft ---
Peter is drafting these files:
  1. pipeline/monitors/fimi-cognitive-warfare/fcw-synthesiser-api-prompt.txt
  2. pipeline/monitors/fimi-cognitive-warfare/fcw-synthesiser.py
  3. pipeline/monitors/fimi-cognitive-warfare/synthesised/synthesis-latest.json (stub)
  4. .github/workflows/fcw-synthesiser.yml
  5. Slim FCW Analyst cron task description (plain text → Computer converts to schedule_cron call)

When Peter sends them:
- Review each file against COLLECTOR-ANALYST-ARCHITECTURE.md v2.1
- Check fcw-synthesiser.py embeds pipeline JSON into sonar-deep-research call correctly
- Check synthesiser-api-prompt.txt instructs model NOT to web search (sonar-deep-research = docs only)
- Validate synthesiser output schema matches report-latest.json structure minus cross_monitor_flags + persistent_state_delta
- Commit, trigger workflow_dispatch, verify synthesis-latest.json output
- Then build slim Analyst cron, delete old FCW cron (b17522c3), test end-to-end

--- THEN: Roll pattern to remaining 6 monitors ---
GMM, WDM, SCEM, ESA, AGM, ERM — same 5 files each.
ESA/AGM/ERM also need weekly-research workflows built (currently have no Layer 1B).

--- OTHER QUEUED WORK ---
- PED Sprint 2: Q4/Q6/Q7/Q8 decisions in decisions.md gate this — surface first
- Housekeeping: trim to 5 essential steps (~800 credits/month saving)
- Signal refresh (Option B): weekly sonar-pro for all 7 monitors — keeps dashboard live
- Source → minor cleanup: FCW/WDM/SCEM dashboards (3 patterns, non-blocking)

--- DEPLOYMENT REMINDER ---
After any shared JS/CSS change:
1. Verify live (Cache-Control: no-store)
2. If stale: workflow_dispatch build.yml
3. CF purge-all-files (Zone: cc419b7519eba04ef0dc6a7b851930c7)
4. Screenshot a dashboard — confirm no "Failed to load data."
```

## Current platform state

- Site: ✅ asym-intel.info live, all dashboards rendering
- nav.js: ✅ v1.3 — MONITOR_REGISTRY, 4 injection functions
- Chatter: ✅ 7/7 monitors, rotating daily, shared/js/chatter.js
- Search: ✅ 7/7 monitors, shared/js/search.js
- Collectors: ✅ 7/7 rotating daily (Mon–Sun 07:00 UTC)
- Weekly-research: ⏸ PAUSED (4 built, 3 not built)
- Reasoner: ⏸ PAUSED (4 built, 3 not built)
- Synthesiser: ❌ Not built — Peter drafting FCW
- Analyst crons: ✅ 7/7 weekly, current architecture (pre-synthesiser)
- Housekeeping: ✅ Weekly Monday

## Peter action required
- ⚠️ FCW synthesiser files (drafting) — this unlocks the new architecture
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC property verification (DNS TXT)

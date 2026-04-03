# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 efficiency sprint wrap (~11:30 CEST)

> **Bootloader:** Say "Computer: asym-intel.info" to the next instance.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: ESA/AGM/ERM pipelines + PED Sprint 2 ---

VERIFY LIVE BEFORE STARTING:
curl -s -H "Cache-Control: no-store" https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Should show v1.3. If not: workflow_dispatch build.yml → CF purge-all-files.

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
   grep "Source →" in each static/monitors/{slug}/dashboard.html, fix inline

4. GMM/ESA annual calibration files
   macro-monitor-imf-2026.md (IMF WEO April 2026 data)
   european-strategic-autonomy-ecfr-2026.md

EFFICIENCY REMINDER (new rule in COMPUTER.md v3.4):
- Batch 3+ tasks per session. Step 0 loading is fixed overhead — amortise it.
- Housekeeping notifies on any issue. Silence = healthy. Don't open a session to verify health.

DEPLOYMENT REMINDER:
After any shared JS/CSS change → verify live (Cache-Control: no-store) → if stale: workflow_dispatch + CF purge-all.
CF Zone ID: cc419b7519eba04ef0dc6a7b851930c7
```

## Previous session completed (efficiency sprint — 3 Apr)
- ✅ Staging guard cron deleted (aec126c5)
- ✅ GSC audit cron deleted (f78e0c2c) — recreate after GSC DNS TXT verified
- ✅ Housekeeping slimmed — HTML structural checks stripped, ~50% fewer steps
- ✅ COMPUTER.md v3.4 — min session size rule added
- ✅ docs/monitors/_shared/ artefact deleted
- ✅ CRON-001 docs/ copies fixed for AGM/WDM/FCW/GMM

## Peter action required
- ⚠️ Q4/Q6/Q7/Q8 in decisions.md (gates PED Sprint 2)
- ⚠️ Branch protection on main (SEC-009)
- ⚠️ GSC DNS TXT record verification
# HANDOFF.md — Asymmetric Intelligence
**Last updated:** Thursday, 2 April 2026, ~12:00 CEST
**Session:** Major architecture session — FCW pipeline built end-to-end

---

## Immediate Actions for Next Session

1. **Check FCW Thursday Analyst run** (Thu 3 Apr 09:00 UTC) — first run with Steps 0C/0D/0E. Verify it reads pipeline/ correctly and publishes a valid report. Check: `gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/fimi-cognitive-warfare/data/report-latest.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('meta',{}).get('published',''))"` 

2. **Deploy pipeline to other 6 monitors** — but ONLY after FCW Thursday run validates the pattern. Use pipeline/PIPELINE-BUILD-PATTERN.md as the step-by-step guide. Priority order: SCEM (natural second pilot — conflict data), WDM (29-country research load), AGM (16-module load).

3. **Google Search Console** — submit domain property verification (DNS TXT record) and then submit both sitemaps: asym-intel.info/sitemap.xml and compossible.asym-intel.info/sitemap.xml

4. **Fortiguard recategorisation** — submit asym-intel.info at fortiguard.com/webfilter as "News and Media / Research". Gibraltar network filter (octopus.gi) is likely Fortinet-based.

5. **Sprint 3** — next rendering/schema session. Full backlog at docs/audits/sprint-programme.md. 34 low-effort items across all 7 monitors.

---

## Repository State

### asym-intel-main (public)
- COMPUTER.md: v2.3
- Hugo site: live at asym-intel.info (SSL: Full Strict ✅)
- FCW GitHub Actions pipeline: 3 workflows live and tested
- pipeline/monitors/fimi-cognitive-warfare/: daily/ + weekly/ + reasoner/ directories
- docs/: MISSION.md, ROLES.md, prompts/, audits/sprint-programme.md
- content/mission.md: Mission & Principles published at /mission/

### asym-intel-internal (private)
- AGENT-IDENTITIES.md: v2.3 — includes FCW Collector identity card
- COLLECTOR-ANALYST-ARCHITECTURE.md: canonical strategy document
- notes-for-computer.md: session summary 2 April 2026
- prompts/README.md: architecture reference
- prompts/FCW-COLLECTOR-PROMPT-v1.1: 5 methodology gaps applied
- methodology/fimi-cognitive-warfare-full.md: 5 gaps committed (34242 chars)

---

## FCW Pipeline Architecture (DO NOT recreate as Computer crons)

```
GitHub Actions (daily 07:00 UTC, sonar)         → pipeline/daily/
GitHub Actions (Wed 18:00 UTC, sonar-pro)        → pipeline/weekly/
GitHub Actions (Wed 20:00 UTC, sonar-deep-research) → pipeline/reasoner/

FCW Analyst cron 879686db (Thu 09:00 UTC)
  Step 0C: reads pipeline/daily/daily-latest.json
  Step 0D: reads pipeline/weekly/weekly-latest.json
  Step 0E: reads pipeline/reasoner/reasoner-latest.json
  Step 1: applies FCW methodology (not raw research)
  Publishes → data/report-latest.json
```

**Model selection (critical):**
- `sonar` — live web search, fast, daily use
- `sonar-pro` — live web search, deeper, weekly use
- `sonar-deep-research` — reasons over documents YOU provide, NO web search. Use only for Reasoner workflows where you pass structured JSON as context.

---

## FCW Methodology Updates (5 Gaps — 2 April 2026)

Applied to methodology/fimi-cognitive-warfare-full.md AND FCW-COLLECTOR-PROMPT-v1.1:

1. **Private Emanation sub-category** — state-subsidised infrastructure actors (Musk/Thiel/Palantir scale) between state and commercial operator. Attribution form: "private emanation of state A's security apparatus." Different logic from contractor/client framework.

2. **Legislative capture threshold** — disclosed-but-astroturfed lobbying can meet FIMI criteria via DISARM T0059+T0046. Coordination+manipulation threshold applies alongside disclosure test. BLOOM/CSDDD reference case.

3. **Distributed coordination architecture** — no-single-director ≠ no coordination. Deliberate architectural feature of sophisticated operations. Demonstrate synchronisation pattern, not command node.

4. **Spyware-as-targeting-infrastructure** — Pegasus-FIMI loop. Spyware harvests targeting data → informs FIMI precision targeting. Tracked as `hybrid_type: targeting_infrastructure` in Attribution Log. Distinct from hack-and-leak.

5. **EEAS asymmetry as documented political choice** — EP PEGA Committee documented US/Israeli operations meeting DISARM criteria are not entered by political design, not evidentiary threshold. Reading protocol: "EEAS FIMI Explorer: no entry — reflects institutional perimeter by political design."

---

## Cron Schedule (Computer)

| Cron ID | Name | Schedule | Notes |
|---|---|---|---|
| db22db0d | WDM Analyst | Mon 06:00 UTC | Two-pass commit, Step 0B/0C |
| 02c25214 | GMM Analyst | Tue 08:00 UTC | |
| 0fa1c44e | ESA Analyst | Wed 19:00 UTC | |
| 879686db | FCW Analyst | Thu 09:00 UTC | Steps 0C/0D/0E wired to pipeline |
| 267fd76e | AGM Analyst | Fri 09:00 UTC | |
| 3e736a32 | ERM Analyst | Sat 05:00 UTC | |
| eb312202 | SCEM Analyst | Sun 18:00 UTC | |
| 73452bc6 | Platform Validator | Mon 08:00 UTC | Checks 1–20 incl. pipeline |
| a67a9739 | SCEM verification | Sun 5 Apr 18:30 UTC | One-shot |
| 10ddf5f0 | WDM verification | Mon 6 Apr 06:30 UTC | One-shot |

---

## SEO / Site Health

- Sitemap: xmlns:xhtml removed on asym-intel.info and compossible.asym-intel.info ✅
- Cloudflare SSL: changed to Full (Strict) ✅
- Cloudflare Bot Fight Mode: to enable
- Cloudflare Page Shield: to enable
- Recategorisation: submit to Fortiguard (priority), Cloudflare radar, Cisco Umbrella, Symantec
- GSC domain property: user action required (DNS TXT record)

---

## Sprint Backlog

Full sprint programme at docs/audits/sprint-programme.md

**Sprint 2B** (data-gated, this week):
- SCEM verification cron fires Sun 5 Apr 18:30 UTC
- WDM verification cron fires Mon 6 Apr 06:30 UTC
- WDM Category B sections first appear Mon 6 Apr — verify render
- ESA defence spending bar after Wed 8 Apr cron
- FCW Campaign Gantt after Thu 9 Apr (start_date data)

**Sprint 3** (next session, 34 items, all low-effort):
- AGM digest.html, SCEM report sections, ESA 6th radar spoke
- FCW all 12 campaigns, GMM hard_landing_risk KPI, WDM weekly_brief
- ERM cascade tiers, source links everywhere, cross-monitor widget all dashboards

**Sprint 4** (schema sprint): 24 new fields requiring cron prompt changes first
**Sprint 5** (architectural): design sessions required before building

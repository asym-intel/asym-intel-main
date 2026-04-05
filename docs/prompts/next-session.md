# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-05 morning wrap (~07:45 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Prompt

```
Load asym-intel skill. Read COMPUTER.md, HANDOFF.md, notes-for-computer.md,
docs/ARCHITECTURE.md, and docs/ROADMAP.md before starting.

--- VERIFY LIVE FIRST ---
curl -s https://asym-intel.info/monitors/shared/js/nav.js | grep "nav.js  v"
→ Must show v1.4
Screenshot any dashboard → must render, no "Failed to load data"

--- TASK 1: ENABLE SYNTHESISER SCHEDULES ---
All 7 synthesisers pass. Uncomment the schedule: lines in each .yml workflow:
  FCW: Wed 22:00 UTC | GMM: Mon 20:00 UTC | WDM: Sun 21:00 UTC
  SCEM: Sat 10:00 UTC | ESA: Wed 09:00 UTC | AGM: Thu 22:00 UTC | ERM: Fri 20:00 UTC
Commit all 7 in a single commit.

--- TASK 2: MONITOR FIRST SLIM ANALYST RUNS ---
SCEM fires Sun 5 Apr 18:00 UTC. WDM fires Mon 6 Apr 06:00 UTC.
Housekeeping Mon 6 Apr 08:00 UTC. GMM Tue 7 Apr 08:00 UTC.
Check that each loads its prompt from repo and publishes successfully.
If SCEM has already fired, verify its output.

--- TASK 3: SCEM VISUAL SPRINT 2 ---
Read asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md
Next components: NEW-02 (Confidence Quality Summary Bar), NEW-03 (Deviation Heatmap PNG).
Use tiered deployment — NEW-02 is LOW risk (additive JS-AUTO), deploy direct to main.

--- TASK 4: HOMEPAGE NETWORK GRAPH ---
Priority 2 from network integration plan.
Add a section in layouts/index.html embedding whitespace.asym-intel.info via iframe.
Hugo layout change → goes to main directly.

--- THEN ---
- PED Sprint 2: Q4/Q6/Q7/Q8
- Analytics: Plausible vs Fathom
```

## Key facts for this session
- All 8 slim crons live (see HANDOFF.md for IDs)
- Tiered deployment rules: LOW risk → main directly (see COMPUTER.md)
- synth_utils.py shared JSON repair module at pipeline/synthesisers/synth_utils.py
- SYNTH_MODEL env var override available on all 7 scripts
- GMM workflow fetches prompt + methodology + addendum from internal repo
- Leverage Signal skill: "Computer: Signal" for commercial GMM thread
- ERG (Energy & Resource Geopolitics) confirmed as abbreviation for new monitor

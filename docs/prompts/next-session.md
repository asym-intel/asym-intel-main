# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-05 wrap (~09:00 BST)

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

--- VERIFY SYNTHESISER SCHEDULES COMMITTED ---
gh api /repos/asym-intel/asym-intel-main/commits --jq '.[0] | {sha:.sha[:8],msg:.commit.message[:60]}'
→ Must show commit 3ee1ff7c "feat: enable scheduled triggers on all 7 synthesiser workflows"

--- TASK 1: VERIFY FIRST SYNTHESISER RUNS ---
SCEM synthesiser fired Sun 5 Apr 10:00 UTC — check pipeline/monitors/conflict-escalation/ for output.
SCEM Analyst fires Sun 5 Apr 18:00 UTC — check data/report-latest.json after that.
WDM synthesiser fires Sun 5 Apr 21:00 UTC, Analyst Mon 6 Apr 06:00 UTC.
GMM synthesiser fires Mon 6 Apr 20:00 UTC, Analyst Tue 7 Apr 08:00 UTC.
For each: confirm synthesiser produced valid JSON → Analyst published successfully.

--- TASK 2: SCEM VISUAL SPRINT 2 ---
Read asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md
Next components: NEW-02 (Confidence Quality Summary Bar), NEW-03 (Deviation Heatmap PNG).
NEW-02 is LOW risk (additive JS-AUTO) → deploy direct to main.

--- TASK 3: HOMEPAGE NETWORK GRAPH ---
Add a section in layouts/index.html embedding whitespace.asym-intel.info via iframe.
Hugo layout change → goes to main directly.

--- THEN ---
- PED Sprint 2: Q4/Q6/Q7/Q8 (Peter decisions needed — check if provided)
- Analytics provider: Plausible vs Fathom (Peter decision pending)
- Commercial docs: update "Leverage Signal" / signal.asym-intel.info →
  "Asymmetric Investor" + confirmed subdomain (Peter to confirm subdomain name)
```

## Key facts for this session
- All 8 slim Analyst crons live (see HANDOFF.md for IDs)
- All 7 synthesiser schedules now LIVE (commit 3ee1ff7c, 5 Apr 2026)
- Tiered deployment rules: LOW risk → main directly (see COMPUTER.md)
- synth_utils.py shared JSON repair at pipeline/synthesisers/synth_utils.py
- SYNTH_MODEL env var override available on all 7 scripts
- Commercial brand: "Asymmetric Investor" (subdomain TBC) — update internal docs when confirmed
- ERG monitor: methodology stub to be created in Q3 2026; no build until GMM migrates commercially

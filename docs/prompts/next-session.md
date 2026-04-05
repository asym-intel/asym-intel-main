# Next Computer Session — Ready-to-Paste Prompt
**Updated:** 2026-04-05 evening wrap (~17:20 BST)

> **Bootloader:** "Computer: asym-intel.info"

---

## Session start checklist
Load asym-intel + asym-intel-charts skills. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, docs/ROADMAP.md.

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging --jq '{ahead_by:.ahead_by}'
gh api /repos/asym-intel/asym-intel-main/commits?per_page=5 --jq '[.[] | {sha:.sha[:8],msg:.commit.message[:60]}]'
```

## Verify fixes live
- https://asym-intel.info/monitors/ai-governance/dashboard.html — Lead Signal, Model Frontier, Energy Wall, Concentration Index must all show real data (not "Could not load")
- https://asym-intel.info/monitors/macro-monitor/dashboard.html — "Fed Funds & Sentiment Overlay" must show Chart.js line chart

---

## Priority queue

### TASK 1 — Verify synthesiser pipeline
- SCEM: synthesiser 10:00 UTC, Analyst 18:00 UTC — check data/report-latest.json
- WDM: synthesiser 21:00 UTC Sun → check Mon morning
- GMM: synthesiser Mon 20:00 UTC, Analyst Tue 08:00 UTC

### TASK 2 — SCEM Visual Sprint 2
NEW-02: Confidence Quality Summary Bar (LOW risk → main direct)
NEW-03: Deviation Heatmap PNG
Read: asym-intel-internal/visuals/scem-visual-recommendations-2026-04-05.md

### TASK 3 — Homepage network graph
layouts/index.html Hugo layout change → main directly.

### TASK 4 — Per-monitor search.html chatter indexing (search.js v1.1)
MEDIUM risk → staging + screenshot before merge.

### THEN
- PED Sprint 2: Q4/Q6/Q7/Q8 (Peter decisions needed)
- Analytics: Plausible vs Fathom (Peter pending)
- Asymmetric Investor commercial entry point (Peter to revert)

---

## Critical rules added this session
- **esc() scope on AGM:** esc() must be at module scope (not inside DOMContentLoaded)
  Any render function outside the closure that calls esc() will throw ReferenceError,
  silently caught by .catch(), wiping Lead Signal/Risk Vector/Model Frontier.
  Rule: check this on ANY monitor when adding render functions outside DOMContentLoaded.
- **Cloudflare Zone ID:** cc419b7519eba04ef0dc6a7b851930c7 (asym-intel.info)
  Add to platform-config.md if still placeholder.
- **sourceLink canonical:** AsymRenderer.sourceLink(url) — no esc(), no guard (FE-027)
- **Signal block body:** class="signal-block__body" — never --color-text-muted inside .signal-block
- **Staging clean:** ahead_by 0

## Session summary (5 Apr 2026 — full day)
- All 7 synthesiser schedules live
- Full data surfacing across all 7 monitors (PR #39, PR #40)
- FE-027 sourceLink canonical pattern — all 7 reports + renderer.js
- Signal block contrast fixed — 4 pages
- /search/ chatter indexing — all 7 monitors
- GMM: domain indicators, tail risks, sentiment overlay chart
- AGM: delta strip, energy wall, arxiv, country watch, concentration, revolving door
- AGM crash (esc scope) fixed
- Asymmetric Investor brand confirmed: investor.asym-intel.info

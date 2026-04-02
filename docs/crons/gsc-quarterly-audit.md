# Quarterly GSC Audit — Computer Admin Cron
## Prompt file: docs/crons/gsc-quarterly-audit.md

This cron runs quarterly (1 April, 1 July, 1 October, 1 January) and
sends Peter a structured summary of asym-intel.info search performance
from Google Search Console via the Cloudflare and Google connectors.

---

## STEP 0 — Read context

```bash
gh api /repos/asym-intel/asym-intel-main/contents/docs/MISSION.md \
  --jq '.content' | base64 -d | grep -A 80 "## Reader Profiles"
```

Read the Reader Profiles section only. This is the audience model you are
auditing against — the question is whether GSC data validates or challenges
the assumed profiles.

---

## STEP 1 — Collect GSC data

Use the Google Search Console connector (or search_web with site:asym-intel.info
as a fallback if GSC connector is unavailable) to collect for the past 90 days:

1. **Top 20 queries** driving impressions to asym-intel.info
2. **Top 20 pages** by clicks
3. **Top 20 queries** by click-through rate (CTR)
4. **Country breakdown** — top 10 countries by impressions
5. **Device breakdown** — desktop vs mobile vs tablet %
6. **Average position** for the platform's core topic queries:
   - "democratic backsliding monitor"
   - "FIMI detection"
   - "AI governance tracker"
   - "European strategic autonomy"
   - "conflict escalation monitor"
   - "macrofinancial risk"
   - "environmental risk monitor"

If GSC connector is unavailable: note this clearly and use
search_web to check current ranking for the 7 core queries above.
Report what was available and what was not.

---

## STEP 2 — Analyse against reader profiles

For each reader profile in MISSION.md §Reader Profiles, assess:

- Which queries suggest this audience is arriving?
- Which monitor pages are they landing on?
- Is the landing page appropriate for what the query implies they need?
- Any queries where intent clearly does not match what the page delivers?

Flag explicitly:
- Queries with high impressions but very low CTR (title/description mismatch)
- Queries suggesting activist citizen audience (non-expert phrasing)
- Queries suggesting OSINT/professional audience (technical phrasing)
- Any monitor that appears to have zero organic discovery (no queries at all)

---

## STEP 3 — Write the audit report

Save to: `docs/seo/gsc-quarterly-YYYY-QN.md`
(e.g. `gsc-quarterly-2026-Q2.md` for April–June 2026)

Also overwrite: `docs/seo/gsc-latest-audit.md` (always the most recent)

Report structure:
```
# GSC Quarterly Audit — YYYY QN
**Period:** YYYY-MM-DD to YYYY-MM-DD
**Generated:** YYYY-MM-DD

## Summary (3-4 sentences)
Key findings. What changed since last quarter. Biggest gap between
expected and actual discovery.

## Top Queries (table: query | impressions | clicks | CTR | avg position)

## Top Pages (table: page | clicks | impressions | CTR)

## Core Topic Rankings (table: query | position | delta from last quarter)

## Reader Profile Evidence
### OSINT / professional audience
### Journalist / policy audience
### Activist citizen audience
(What the data says about each, or "no signal yet")

## Monitor Discovery Gaps
Which monitors have weak or absent organic discovery. Recommended actions.

## Recommendations for SEO Expert
Prioritised list. Each with: what to do, which page(s), estimated impact.
Max 5 items — prioritise ruthlessly.

## Reader Profile Notes for MISSION.md
Any evidence that suggests the assumed profiles should be updated.
Flag to Peter if a profile revision is warranted.
```

---

## STEP 4 — Notify Peter

Send an in-app notification:

Title: "Quarterly GSC audit ready — asym-intel.info"
Body: 2-3 sentence summary of the most significant finding.
Include: link to the saved report file or repo path.

---

## STEP 5 — Update docs/seo/gsc-latest-audit.md in repo

Commit the audit report to asym-intel-main:
```bash
# Save report to docs/seo/gsc-quarterly-YYYY-QN.md
# Also overwrite docs/seo/gsc-latest-audit.md
git commit -m "seo(audit): quarterly GSC review — YYYY QN"
```

The SEO & Discoverability Expert reads `docs/seo/gsc-latest-audit.md`
at Step 0 of any SEO session. Keeping it current means every SEO session
starts from the latest real data, not assumptions.

---

## Notes

- This cron does NOT make any changes to the site. It only reads and reports.
- Implementation of recommendations is a separate SEO Expert session triggered by Peter.
- If this is the first run and no previous audit exists, note that and
  establish the baseline — all metrics are "Q0 baseline, no delta available."
- The reader profile sections should be brief and honest: "data too thin
  to draw conclusions" is a valid finding for the first 1-2 quarters.

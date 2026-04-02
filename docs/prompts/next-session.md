# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap
**Rule:** This file is overwritten at every wrap. It always contains the
highest-priority prompt for the immediately next Computer Admin session.
It is never left stale. A fresh instance reading this file gets the correct
starting point without needing to reconstruct it from HANDOFF.md.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- SESSION: Platform Experience Designer (first-ever) ---

Peter's reader observations are the brief. They are in
notes-for-computer.md (search for "Prompt-B-PED" or "PED session").
Key observations summarised:
- Homepage: "Read →" redundant beside hyperlinked title — wasted space
- "Source →" labels should be inline hyperlinks on the item itself
- Small font sitewide (e.g. ESA dashboard #section-delta)
- Nav label / section title mismatches (GMM: nav says KPI, section says Tail Risk Heatmap)
- Hard-to-read signal text blocks (GMM report, FCW dashboard #section-signal)
- SCEM flag matrix — value unclear to non-specialist reader
- SCEM sections with no right-hand nav entry (Conflict Overview — All Active Roster)
- Homepage: consider visual image (cf. whitespace.asym-intel.info)
- Homepage: consolidated chatter feed (top 5 daily chatters) as OSINT surface

Run the full first-session PED benchmark:

1. Knowhow dump — visit 5 live monitor pages, populate
   docs/ux/decisions.md Sections 1-4 from observations
   + Peter's notes above
2. Create docs/ux/colour-registry.md — every severity and
   confidence colour across all 7 monitors; flag collisions (PED-004).
   Must be committed before any implementation is proposed.
3. Progressive disclosure audit — Layer 1 test (10-second
   activist-citizen test) for each of the 5 pages visited
4. Prioritised gap list — top 5 changes by activist-citizen
   impact, each as a precise implementation spec passed to
   Platform Developer via notes-for-computer.md

MANDATORY SUBAGENT RULE (COMPUTER.md v3.2):
Split into TWO subagents — not one.
  Subagent 1 (observe): browse the 5 pages + read shared/css/base.css
  and per-monitor monitor.css files for colour tokens. Save findings
  to /home/user/workspace/ped-observations.md.
  Subagent 2 (write): read ped-observations.md + Peter's notes above,
  then commit docs/ux/decisions.md and docs/ux/colour-registry.md,
  update notes-for-computer.md with gap specs, update HANDOFF + ROADMAP.

Do not implement anything. Design, document, and specify only.

--- AFTER PED: JSON-LD structured data ---

Platform Developer session immediately after PED wraps.
Implement Schema.org structured data in Hugo layouts:
- layouts/partials/head.html — Dataset + BreadcrumbList for monitor pages
- layouts/_default/single.html — upgrade Article to NewsArticle
Full spec: docs/seo/ai-search-audit-2026-Q2.md Section 5
Goes direct to main (Hugo source, not static HTML — no staging needed).

Wrap covering both tasks at the end.
```

---

## What this session completed (do not re-do)

- ✅ FCW dashboard — modern shared-library version on main (was legacy 140k)
- ✅ SRI hashes — PR #29 merged, all 7 dashboards, SEC-010 closed
- ✅ integrity-manifest.json — live on main, all 7 monitors hashed
- ✅ WDM meta description — "democratic backsliding" + V-Dem + Freedom House
- ✅ All 7 methodology page dates — corrected from 2020-01-01 to actual dates
- ✅ docs/security/ — created and accurate (third-party-audit, platform-status, rotation-schedule)
- ✅ docs/SEO.md + docs/seo/ — created, robots.txt fixed
- ✅ COMPUTER.md v3.2 — wrap step 0, memoryless-instance rule, subagent sizing
- ✅ platform-config.md in asym-intel-internal (Zone ID placeholder for Peter)

## Still open — Peter action required before or during next session

- ⚠️ Branch protection on main (SEC-009 HIGH) — GitHub repo settings → Branches
- ⚠️ Integrity manifest workflow approval — docs/security/drafts/generate-integrity-manifest.yml → .github/workflows/
- ⚠️ Cloudflare: HSTS max-age 31536000 + X-Frame-Options + CSP + Referrer-Policy
- ⚠️ Cloudflare Zone ID + Account ID → asym-intel-internal/platform-config.md

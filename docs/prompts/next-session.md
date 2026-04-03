# Next Computer Admin Session — Ready-to-Paste Prompt
**Updated:** 2026-04-03 session wrap (~02:10 CEST)
**Rule:** This file is overwritten at every wrap. Always current.

---

## Prompt

```
Load the asym-intel skill first. Read COMPUTER.md, HANDOFF.md,
notes-for-computer.md, docs/ARCHITECTURE.md, and docs/ROADMAP.md
before starting.

--- FIRST: merge PR #30 if Peter has signed off ---

Check: https://github.com/asym-intel/asym-intel-main/pull/30
FCW report + overview (Chatter added), AGM report + overview (Digest added).
If Peter has approved, merge and reset staging to main before any other work.

--- SESSION: Platform Experience Designer (first-ever) ---

Peter's reader observations are the brief. They are in
notes-for-computer.md (search "Prompt-B-PED").
Key observations:
- Homepage: "Read →" redundant beside hyperlinked title — wasted space
- "Source →" labels should be inline hyperlinks on the item itself
- Small font sitewide (e.g. ESA dashboard #section-delta)
- Nav label / section title mismatches (GMM: nav says KPI, section says Tail Risk Heatmap)
- Hard-to-read signal text blocks (GMM report, FCW dashboard #section-signal)
- SCEM flag matrix — value unclear to non-specialist reader
- SCEM sections with no right-hand nav entry (Conflict Overview, All Active Roster)
- Homepage: consider visual image (cf. whitespace.asym-intel.info)
- Homepage: consolidated chatter feed (top 5 daily chatters) as OSINT surface

PED-007 RULE (in prompt v1.1): Each observation is an INSTANCE of a PRINCIPLE.
Extract the principle, audit all 7 monitors for all instances, spec at
the principle level — not just the named example.

MANDATORY: Two subagents.
  Subagent 1 (observe): browse 5 live pages + read CSS colour tokens.
  Save to /home/user/workspace/ped-observations.md.
  Subagent 2 (write): read observations + Peter's notes, then commit
  docs/ux/decisions.md, docs/ux/colour-registry.md,
  update notes-for-computer.md with gap specs, update HANDOFF + ROADMAP.

Do not implement anything. Design, document, specify only.

Wrap at the end.
```

---

## What this session completed (do not re-do)

- ✅ JSON-LD — BreadcrumbList + Dataset + NewsArticle live and verified clean
- ✅ FE-026 — Hugo minifier JSON-LD pattern in ARCHITECTURE.md + anti-patterns.json
- ✅ housekeeping-cron-prompt.md to static/monitors/
- ✅ lastmod on about.md, search.md, subscribe.md
- ✅ PED prompt v1.1 — Example-as-Instance Rule + PED-007
- ✅ Jekyll Pages runner disabled (build_type: workflow)
- ✅ Nav audit — FCW + AGM fixed in PR #30 (awaiting Peter sign-off)
- ✅ All prior session work (SRI hashes, integrity manifest, SEO, FCW dashboard)

## Open — Peter action required

- ⚠️ PR #30 visual sign-off + merge
- ⚠️ Branch protection on main (SEC-009 HIGH)
- ⚠️ Integrity manifest workflow approval
- ⚠️ Cloudflare headers + Zone ID
- ⚠️ GSC property verification

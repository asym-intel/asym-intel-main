# Asymmetric Intelligence — Role Enhancement Addenda
**Version:** 1.0  
**Date:** 2026-04-02  
**Status:** Internal — read after ROLES.md, supplements existing role cards  
**Applies to:** Six platform roles. Does not modify Domain Analyst (×7) or Computer role cards.

---

## How to Use This Document

Each section below is an **enhancement addendum** to the corresponding role card in ROLES.md. It does not replace the existing card — it adds mission-aligned precision that the base card leaves under-specified.

**Read order:** MISSION.md → ROLES.md (base role card) → this addendum (your role section) → session startup sequence.

The enhancements derive from a systematic cross-reference of ROLES-02-April.md against MISSION-1-2.md. Every addition traces to a specific gap between what the mission demands and what the role card currently specifies.

---

# ENHANCEMENT 1: SEO & DISCOVERABILITY EXPERT

**Enhancement level:** Significant  
**Priority:** High — search is the platform's primary discovery mechanism. If output is not findable, the public commons is not serving its public.  
**Mission anchor:** *"The platform does no marketing. Search is the primary discovery mechanism."*

---

## 1.1 Search Intent Matrix — Five Reader Profiles

The existing role card treats SEO as a metadata standards problem. The mission defines five reader profiles with fundamentally different search behaviours. The SEO role must map search intent per audience per monitor.

### How Each Audience Searches

| Reader profile | Search behaviour | Example query (WDM domain) | Example query (AGM domain) |
|---|---|---|---|
| **OSINT practitioner** | Named-source, data-specific, methodological | `V-Dem liberal democracy index Hungary 2026` | `EU AI Act harmonised standards CEN-CENELEC JTC21 status` |
| **Lawyer / policy expert** | Structural-trajectory, compliance-focused, citable | `Hungary rule of law Article 7 proceedings current status` | `EU AI Act high-risk system compliance timeline 2026` |
| **Journalist** | Pattern-seeking, event-triggered, verification-oriented | `Hungary democratic backsliding pattern evidence` | `AI governance gap between regulation and enforcement` |
| **Activist citizen** | Natural language, concern-driven, exploratory | `is democracy declining in Europe` | `is AI dangerous who regulates it` |
| **Politician / civil society** | Positional, cherry-pick-resistant, citable in debate | `independent assessment Hungary democratic institutions` | `AI Act implementation status independent analysis` |

### Operational Rule

For every monitor's landing page and latest-issue page, verify that the title tag, meta description, H1, and first paragraph contain language that would match at least **three of the five search intent types**. If only one profile's search intent is served (typically the OSINT practitioner), the metadata is under-optimised for the mission.

### Per-Monitor Keyword Strategy (Standing Reference)

| Monitor | Primary keyword cluster | Secondary cluster | Long-tail opportunity |
|---|---|---|---|
| WDM | democratic backsliding, institutional erosion, democracy index | judicial independence, electoral integrity, authoritarian diffusion | `[country] democracy score 2026` |
| SCEM | conflict escalation, early warning, geopolitical risk | civilian displacement, ceasefire monitoring, escalation indicators | `[region] conflict risk assessment` |
| ESA | European strategic autonomy, EU defence, digital sovereignty | ReArm Europe, NATO European pillar, EU-US decoupling | `European defence industrial base progress` |
| GMM | macro financial risk, global recession risk, systemic stress | credit conditions, sovereign debt, tariff economic impact | `US tariff impact on [asset class/region]` |
| FCW | foreign information manipulation, FIMI, disinformation | cognitive warfare, election interference, state-sponsored | `[country] disinformation campaign evidence` |
| ERM | environmental risk, climate tipping points, planetary boundaries | food security, biodiversity loss, climate migration | `[region] climate risk structural assessment` |
| AGM | AI governance, AI regulation, AI safety | EU AI Act, frontier model risk, AI ethics accountability | `AI regulation tracker [jurisdiction] 2026` |

Update this table quarterly when GSC query data reveals actual search patterns.

---

## 1.2 AI Search Engine Optimisation

Google AI Overviews, Perplexity, ChatGPT Search, and Bing Copilot are now significant discovery channels for the OSINT/policy audience. The platform's structured methodology, explicit confidence levels, and machine-parseable JSON make it unusually well-suited for AI-search citation — but only if the content is structured for machine comprehension.

### Requirements

**Structured methodology pages.** Each monitor's methodology section should be a standalone page (or clearly delineated section) with:
- Named confidence levels and their definitions (machine-readable)
- Source hierarchy with explicit tier labels
- Scoring methodology in declarative sentences, not narrative prose
- Update frequency stated explicitly ("Published weekly, every [day]")

**Clean vocabulary for AI extraction.** AI search engines extract entities and claims. Use consistent, extractable phrasing:
- ✅ `"Hungary's WDM severity score is 7.2 (Amber-High), based on V-Dem EDI decline and judicial independence erosion."`
- ❌ `"Hungary continues to present concerning signals across multiple dimensions of democratic health."`
- The first is citable and extractable. The second is analytically vague and AI-search engines will skip it for a more specific source.

**FAQ schema for common queries.** Add `FAQPage` JSON-LD on monitor landing pages for the 3–5 most common questions each monitor answers:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How is democratic backsliding measured?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The World Democracy Monitor uses a severity scoring formula ABC+2.5D..."
      }
    }
  ]
}
```

**Last-updated timestamps in machine-readable format.** Every monitor page should include:
```html
<time datetime="2026-04-01T06:00:00Z" itemprop="dateModified">1 April 2026</time>
```
AI search engines use this to assess freshness. A weekly monitor without machine-readable dates loses its timeliness advantage.

---

## 1.3 Schema.org Dataset Markup

The platform publishes structured JSON data files that are substantively **datasets**. Adding `Dataset` markup makes them discoverable in Google Dataset Search — directly serving the OSINT practitioner and academic researcher.

```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "World Democracy Monitor — Weekly Severity Scores",
  "description": "Weekly institutional health severity scores for 29 countries, covering electoral integrity, judicial independence, civil society space, and accountability mechanisms.",
  "url": "https://asym-intel.info/monitors/democratic-integrity/data/",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "creator": {
    "@type": "Organization",
    "name": "Asymmetric Intelligence",
    "url": "https://asym-intel.info"
  },
  "temporalCoverage": "2025-11/..",
  "spatialCoverage": "Global — 29 countries",
  "distribution": {
    "@type": "DataDownload",
    "encodingFormat": "application/json",
    "contentUrl": "https://asym-intel.info/monitors/democratic-integrity/data/report-latest.json"
  },
  "measurementTechnique": "Composite severity scoring (ABC+2.5D) from V-Dem, Freedom House, OSCE/ODIHR, and UN Special Rapporteur data",
  "variableMeasured": [
    "Electoral integrity (A)",
    "Institutional independence (B)", 
    "Civil society and media freedom (C)",
    "Accountability mechanisms (D)"
  ]
}
```

Apply equivalent Dataset markup to all 7 monitors where structured data files are publicly accessible. This is high-value, low-effort SEO work.

---

## 1.4 Citability Infrastructure

The mission defines success as analytical citation before consensus. Citation requires infrastructure.

### Requirements (SEO role owns specification; Platform Developer implements)

**Stable, human-readable URLs for specific findings.**
- Monitor landing: `asym-intel.info/monitors/democratic-integrity/`
- Specific issue: `asym-intel.info/monitors/democratic-integrity/2026-04-01/`
- Specific module anchor: `asym-intel.info/monitors/democratic-integrity/2026-04-01/#module-3`

**Recommended citation format on each page.** A visible "Cite this" element (expandable, not intrusive):
```
Asymmetric Intelligence, "World Democracy Monitor — Issue 22" (1 April 2026), 
https://asym-intel.info/monitors/democratic-integrity/2026-04-01/
```

**Date-stamped versioning.** If a published finding is corrected after publication, the correction should be visible with a timestamp. This protects both the platform's credibility and the researcher who cited the original.

**Permanent archive URLs.** The archive indexing policy (noindex after 3 months, redirect after 6) must NOT break citation URLs. A researcher who cited a finding in April 2026 must still be able to reach that exact page in April 2028. Implement noindex while keeping the page live and accessible via direct URL. Never 404 a cited page.

**Absolute constraint — citation URL permanence overrides all archive policy.** If any archive policy (noindex, redirect, cache expiry, CDN purge) would result in a citation URL returning 404, redirecting away from its original content, or rendering without its original data, that policy must be modified. The credibility of every researcher who has cited the platform depends on URL permanence. This constraint is not subject to performance or storage trade-offs.

---

## 1.5 Failure Modes — Additions

**SEO-008: AI-SEARCH INVISIBILITY**
The platform's structured data and explicit methodology make it ideal for AI-search citation. If competitors with less rigorous methodology appear in AI Overviews instead, the SEO strategy has failed.

**Quarterly AI search audit procedure:**
1. For each of the 7 monitors, search the primary keyword (e.g. "democratic backsliding monitor", "FIMI cognitive warfare tracker") in: Google (check for AI Overview), Perplexity, ChatGPT Search
2. Screenshot results — is asym-intel.info cited?
3. If not cited: identify which source IS cited and why (structured data, domain authority, content extractability)
4. Document findings in `docs/seo/ai-search-audit-YYYY-QX.md`
5. If a competitor with less rigorous methodology consistently outranks asym-intel in AI search, this is a HIGH finding — diagnose root cause (missing FAQ schema, poor extractability, freshness signals) and produce a specific remediation recommendation

**SEO-009: CITABILITY URL BREAKAGE**
A researcher cites a specific issue URL. Six months later, the archive policy redirects it. The citation is now broken. This directly undermines the mission's success criterion. Rule: archive pages may be noindexed but must never return 404 or redirect away from the cited content.

**SEO-010: SINGLE-PROFILE METADATA OPTIMISATION**
Metadata is written for the OSINT practitioner (technical, source-specific) while the activist citizen (natural language, concern-driven) finds nothing in the SERP snippet that tells them this page answers their question. Apply the three-of-five test to every meta description.

---

# ENHANCEMENT 2: PLATFORM EXPERIENCE DESIGNER

**Enhancement level:** Significant  
**Priority:** High — reader experience is the mission's delivery surface. Intelligence that cannot be parsed by the reader it was built for has failed.  
**Mission anchor:** *"Legibility for non-experts is a design goal. It is not a licence to simplify confidence levels into binary good/bad judgments."*

---

## 2.1 Five-Profile Progressive Disclosure Framework

The ISA applies a two-audience test. The PED needs an operational design framework for resolving the tensions between all five reader profiles simultaneously.

### The Progressive Disclosure Principle

Design for the activist citizen's first 10 seconds. Reward the OSINT practitioner's deep dive. Serve the journalist's citation need. Protect the politician from cherry-pick accusation. Give the lawyer structural trajectory.

**Layer 1 — Orientation (0–10 seconds).** What the activist citizen sees first.
- Signal summary: one sentence, plain language, stating direction (improving/stable/deteriorating)
- Severity/regime visual: colour-coded, immediately legible without domain knowledge
- "What does this mean?" — a single expandable sentence translating the analytical finding into plain consequence

**Layer 2 — Structural Picture (10–60 seconds).** What the journalist and lawyer need.
- Module-level findings with trajectory indicators (arrows, sparklines)
- Source count and confidence level visible but not dominant
- Cross-monitor links where signals compound ("See also: ESA member state capture")

**Layer 3 — Analytical Depth (60+ seconds).** What the OSINT practitioner demands.
- Full source attribution with tier labels
- Confidence level methodology visible
- Asymmetric signal callouts with technical detail
- Historical severity/score charts with date-stamped data points
- Raw data access (link to JSON)

**Layer 4 — Citation Layer (on demand).** What the politician and lawyer need to take away.
- "Cite this" element with formatted citation
- Permalink to specific finding
- PDF/print-friendly view with full sourcing intact
- Date-stamped methodology version reference

### Design Rule

Every page must be readable at Layer 1 without scrolling past the fold on mobile. Every page must reward reaching Layer 3 with information not available at Layer 1. If Layer 1 and Layer 3 contain the same information at different verbosity levels, the progressive disclosure has failed — it's just repetition.

---

## 2.2 Confidence-Level Visual Language Protocol

The visual distinction between confidence levels is analytically loaded. A subtle colour difference between Assessed and High (FCW) could mislead a reader more than a wrong finding. The PED owns the visual encoding; the methodology owns the definition. The interface between them requires explicit governance.

### Confidence-Level Visual Encoding Standards

| Domain | Levels | Visual encoding rule |
|---|---|---|
| FCW attribution | Confirmed / High / Assessed / Possible | Four visually distinct states — never rely on colour alone. Use colour + icon + label. |
| WDM severity | Numeric score + band (Green/Amber/Red/Rapid Decay) | Bands must be perceptually equidistant. Amber-to-Red transition must be the most visually dramatic. |
| GMM regime | Green/Amber/Orange/Red + MATT score | Regime label and MATT divergence are separate visual elements — never combine into one colour. |
| SCEM escalation | Watch / Elevated / High / Critical | Escalation levels must read as a sequence, not just as colours. Use progressive visual weight (thin→thick border, small→large icon). |
| AGM risk | Module-specific indicators | Asymmetric signal callouts must be visually distinct from standard findings. |

### Platform-Wide Colour-Meaning Registry (Create in Session 1 Before Any Implementation)

Before implementing any visual encoding for confidence levels or severity, the PED must create and commit `docs/ux/colour-registry.md`. This file is the single source of truth for what every colour means across all 7 monitors. Format:

```markdown
| Hex / CSS var | Name | Meaning | Monitors using | Cannot be used for |
|---|---|---|---|---|
| #dc2626 / --color-critical | Signal Red | CRITICAL severity, Rapid Decay | WDM, SCEM | Any non-severity purpose |
| var(--monitor-accent) | Monitor accent | Monitor identity colour | All 7 (different per monitor) | Severity encoding |
```

**Rule:** No colour may carry contradictory analytical meaning across monitors. If amber means "Assessed" in FCW and "Elevated" in SCEM, that is a collision — document it and resolve it before it reaches any reader. The registry is the tool for detecting and preventing these collisions.

Commit the registry before the first visual change is staged. The registry is `docs/ux/`-owned, committed directly to main (documentation), updated any time a new colour encoding is introduced.

### Escalation Rule for Confidence-Presentation Decisions

The PED may make independent design decisions about:
- Typography, spacing, layout of confidence indicators
- Icon selection and size
- Animation/transition when confidence levels change

The PED must escalate to Peter before implementing:
- Any change to the severity colour system (the specific hex values associated with severity bands)
- Any change to confidence level vocabulary (the words Confirmed/High/Assessed/Possible)
- Any visual encoding that could be read as implying a confidence level the methodology does not assign
- Any simplification that reduces the number of visible confidence levels (e.g., collapsing Assessed and Possible into one visual state)

---

## 2.3 Cross-Monitor Reader Journeys

The intelligence digest routes signals between monitors for agents. But the reader following a compound signal across monitors has no designed pathway. This is the platform's most distinctive structural advantage — and it's currently invisible.

### Design Specification

**In-context cross-links.** When a finding references another monitor's domain (e.g., WDM entry on Hungary mentioning FIMI campaign), the reference should be a visible, styled link — not just a text mention. Format:

```
[Cross-monitor signal] → FCW: Active FIMI campaign targeting Hungarian media (High confidence)
```

Clicking navigates to the specific FCW module entry.

**Compound signal callout.** When two or more monitors flag the same country/actor/event in the same publication week, surface a compound signal indicator visible on both monitor pages:

```
⟐ Compound Signal: Hungary flagged by WDM (severity ↑), FCW (FIMI campaign, High), 
  ESA (bilateral capture risk). See cross-monitor view.
```

**Cross-monitor landing page.** A single page (or section of the homepage) that shows all active cross-monitor flags for the current week. This is the "so what?" page — the place where compound signals become visible as systemic patterns rather than isolated domain findings.

### Priority

This is the highest-impact PED enhancement. The individual monitors already exist. The cross-monitor synthesis is the platform's analytical edge. Making it visible to readers is a design problem, not an analytical one.

---

## 2.4 Recovery Signal Presentation Parity

MISSION.md states: *"A democracy monitor that only tracks decay is analytically incomplete."* The PED must audit and ensure that recovery signals receive equal visual weight to deterioration signals.

### The Problem

Deterioration has a natural visual vocabulary: red, amber, warning icons, upward-pointing severity arrows. Recovery has no equivalent visual vocabulary on most analytical platforms. The result: a platform that tracks both directions but *looks like* it only tracks bad news.

### Design Requirements

- Recovery signals use a dedicated visual treatment — not just "green" (which reads as "normal/nothing to see") but an active improvement indicator (e.g., a specific icon, a positive-trajectory sparkline, a labelled "Improving" badge)
- Recovery signals appear in the same visual hierarchy as deterioration signals — not buried below the fold or in a "good news" sidebar
- The signal summary (Layer 1) states recovery where it exists with the same prominence as deterioration
- The severity colour system includes a "Measurable Improvement" state that is visually as salient as "Rapid Decay"

### Anti-Pattern

A page where all visual emphasis (colour, size, position) goes to deteriorating entries while stable or improving entries are grey/muted text at the bottom. This fails the mission — it tells the activist citizen that the world is only getting worse, which is not what the data says.

---

## 2.5 Failure Modes — Additions

**PED-004: CONFIDENCE-LEVEL VISUAL COLLISION**
Two different monitors use the same colour for different confidence meanings (e.g., amber = "Assessed" in FCW, amber = "Elevated" in SCEM). The reader who visits both monitors in one session will conflate the meanings. Maintain a platform-wide colour-meaning registry and ensure no colour carries contradictory analytical meaning across monitors.

**PED-005: PROGRESSIVE DISCLOSURE COLLAPSE**
Layer 1 (orientation) contains so much detail that it reads like Layer 3 (analytical depth). The activist citizen bounces because the page looks like a research database, not an answer to their question. Test: can a non-specialist understand the top-of-page signal in 10 seconds without scrolling?

**PED-006: CROSS-MONITOR JOURNEY DEAD END**
A cross-monitor link points to a monitor page but not to the specific finding. The reader lands on the FCW homepage and has to hunt for the Hungary FIMI entry. All cross-monitor links must deep-link to the specific module section, not to the monitor landing page.

---

# ENHANCEMENT 3: INTELLIGENCE SURFACE ANALYST

**Enhancement level:** Moderate  
**Priority:** Medium  
**Mission anchor:** *"A gap that fails only the activist citizen is still a gap."*

---

## 3.1 Five-Audience Gap Test (Replaces Two-Audience Test)

Upgrade the ISA's audit framework from two audiences to five. For every gap identified, explicitly state which reader profiles are affected.

### The Five-Profile Gap Test

For every surface element audited, ask:

1. **OSINT practitioner:** Can they find the raw signal, trace it to source, and calibrate their own confidence? If not → **Depth Gap**.
2. **Lawyer / policy expert:** Can they identify the structural trajectory and cite it in professional work? If not → **Trajectory Gap**.
3. **Journalist:** Can they verify the finding independently and use it as structural context for a story? If not → **Verification Gap**.
4. **Activist citizen:** Can they understand what the finding means for the thing they care about without prior OSINT literacy? If not → **Orientation Gap**.
5. **Politician / civil society:** Can they use the finding in public argument without exposure to cherry-picking accusations? If not → **Robustness Gap**.

### Gap Classification

| Gap type | Severity | Owner |
|---|---|---|
| Depth Gap | Medium — affects power users, not mission-critical | PED (Layer 3 design) |
| Trajectory Gap | High — directly affects professional utility | PED (Layer 2 design) + Domain Analyst (narrative clarity) |
| Verification Gap | High — undermines citability | SEO (source links) + Domain Analyst (source attribution) |
| Orientation Gap | Critical — fails the hardest and most important audience | PED (Layer 1 design) |
| Robustness Gap | High — affects political utility and platform credibility | Domain Analyst (methodology transparency) + PED (methodology visibility) |

---

## 3.2 Asymmetric Signal Visibility Audit

The platform's distinctive value is asymmetric signals. The ISA must audit whether this value is surfaceable to readers who don't already know to look for it.

### Audit Checklist (Add to Quarterly Audit)

- Can a first-time visitor identify within 30 seconds what makes this platform different from a news aggregator?
- Are asymmetric signal callouts visually distinct from standard findings?
- Does the asymmetric signal include a plain-language explanation of *why* it's non-obvious?
- Can the activist citizen understand an asymmetric signal without reading the methodology page first?
- Is the `technicalfriction` field (AGM, ESA) rendered in a way that communicates "this is the insight you came here for"?

### Output Format

For each finding, classify:
- **Visible and clear:** The asymmetric value is surfaced and readable by ≥3 reader profiles
- **Visible but opaque:** The callout exists but its significance is not self-explanatory
- **Buried:** The asymmetric signal is in the data but not visually distinguished from routine findings
- **Absent:** The data contains an asymmetric implication that is not surfaced at all

---

## 3.3 Recovery Signal Parity Audit

Add to every quarterly audit cycle:

- Count the number of deterioration indicators with dedicated visual treatment (red, amber, warning icons, upward severity arrows)
- Count the number of recovery indicators with dedicated visual treatment
- If the ratio is >3:1 in favour of deterioration, flag as a **Presentation Bias Gap**
- Audit specifically: does the WDM heatmap show improvement with the same visual salience as decay? Does the GMM regime label for de-escalation carry the same visual weight as the escalation label?

---

# ENHANCEMENT 4: PLATFORM SECURITY EXPERT

**Enhancement level:** Moderate  
**Priority:** Medium  
**Mission anchor:** *"The emerging threat tier — as the platform becomes known — subtle data integrity attacks, reputation attacks, targeted availability attacks from actors whose activities the platform monitors."*

---

## 4.1 Counter-FIMI Self-Defence Protocol

This platform monitors state-sponsored FIMI, democratic backsliding, and conflict escalation. The actors whose activities are monitored have a direct operational interest in undermining the platform's credibility. The existing role card identifies this threat; this addendum specifies the response.

### Output Integrity Verification (SHA-256 Manifest)

**Purpose:** Enable any third party to verify that a published finding is authentic and unmodified.

**Implementation:**
1. At publication time, generate a SHA-256 hash of every `report-latest.json` file across all 7 monitors
2. Publish the manifest as `integrity-manifest.json` at a stable URL:
```json
{
  "generated": "2026-04-01T06:00:00Z",
  "monitors": {
    "democratic-integrity": {
      "file": "report-2026-04-01.json",
      "sha256": "a1b2c3d4e5f6..."
    },
    "macro-monitor": {
      "file": "report-2026-04-01.json",
      "sha256": "f6e5d4c3b2a1..."
    }
  }
}
```
3. The manifest itself is committed to GitHub (providing an independent timestamp via git history)
4. If a fabricated screenshot claims asym-intel published a specific finding, the manifest + git history proves the actual output

**Response protocol for reputation attacks:**
1. Identify the fabricated claim
2. Reference the integrity manifest for the relevant date
3. Provide the git commit hash showing the actual published content
4. Document the incident in `docs/security/incidents/` with the fabricated claim and the verified truth
5. If the attack appears coordinated, flag to FCW via `notes-for-computer.md` — it may itself be a FIMI signal

### Canary Statement

Publish a standing canary statement on the About page:
> *"Asymmetric Intelligence has never been subject to a government order to modify, suppress, or alter any published finding. This statement is updated quarterly. Last updated: [date]."*

If the statement is ever removed without explanation, its absence is the signal.

---

## 4.2 Single-Owner Account Security Protocol

Peter is the sole publisher and final decision authority. His GitHub account is the platform's single point of failure.

### Requirements

| Control | Status | Audit frequency |
|---|---|---|
| GitHub 2FA (hardware key preferred) | Verify enabled | Quarterly |
| Recovery codes stored offline (not in cloud) | Verify with Peter | Annually |
| GitHub session token review (active sessions) | Review and revoke stale | Monthly |
| Email account security (recovery email for GitHub) | Verify 2FA on email | Quarterly |
| Cloudflare account 2FA | Verify enabled | Quarterly |
| GSC account access review | Verify sole owner | Quarterly |
| API key rotation for all cron agent credentials | Per rotation schedule | Per schedule |

### Succession Planning

Document and maintain (in a sealed, offline-only document held by Peter):
- Full list of accounts and services the platform depends on
- Recovery procedures for each
- Designated emergency contact who could take over publication if Peter is incapacitated
- This is not paranoia — it is the minimum for a platform that aspires to be a permanent public commons

---

## 4.3 CDN Compromise Response Playbook

**Trigger:** Any CDN the platform depends on (Chart.js, Leaflet, Fontshare, Google Fonts) reports a compromise, serves unexpected content, or fails SRI hash verification.

**Immediate response (within 1 hour of discovery):**
1. Replace CDN `<script>` / `<link>` tags with pinned local copies of the last-known-good version (maintain these in `static/fallback/`)
2. Verify the replacement renders correctly on desktop and mobile
3. Deploy via staging → main (expedited review — security exception to normal PR process, but visual sign-off still required)
4. Notify Peter via `notes-for-computer.md` with URGENT flag

**Within 24 hours:**
1. Document the incident in `docs/security/incidents/`
2. Assess whether any user was served compromised content (check Cloudflare analytics for the affected time window)
3. Evaluate whether to return to CDN (after vendor confirms resolution) or permanently self-host

**Preventive measure:** Maintain a `/static/fallback/` directory containing pinned, version-locked copies of all CDN dependencies. Update these copies quarterly. Verify SRI hashes match.

---

## 4.4 Failure Modes — Additions

**SEC-008: FABRICATED OUTPUT ATTACK**
Someone publishes a screenshot claiming asym-intel rated a country differently than it did. Without an integrity manifest, there is no efficient way to prove otherwise. The SHA-256 manifest is the defence. Build it before it's needed.

**SEC-009: SINGLE-OWNER COMPROMISE**
Peter's GitHub account is phished or session-hijacked. The attacker pushes a modified `report-latest.json` to main. Without branch protection rules requiring a CI check, the modification goes live immediately. Ensure: branch protection on main requires passing CI validation, even for the repository owner.

**SEC-010: DEPENDENCY PINNING DRIFT**
SRI hashes are set once and never updated. The CDN updates to a new version. The SRI check fails silently (browser blocks the script), and the page breaks. Monitor for SRI failures in Cloudflare Page Shield or browser error reporting.

---

# ENHANCEMENT 5: PLATFORM AUDITOR

**Enhancement level:** Moderate  
**Priority:** Lower  
**Mission anchor:** *"Is what is written in COMPUTER.md, HANDOFF.md, and the methodology files actually true?"*

---

## 5.1 Cross-Monitor Signal Integrity Audit

Add to the quarterly audit programme (Q3 focus, but spot-check quarterly):

### Audit Procedure

1. Extract all `crossmonitorflags` from the most recent issue of each of the 7 monitors
2. For each flag with a `targetmonitor` field, verify:
   - Did the target monitor's next issue acknowledge the flag?
   - Was the flag reflected in the target monitor's scoring or narrative?
   - If the flag was not acted on, is there a documented reason (e.g., flag was below the target monitor's materiality threshold)?
3. For each routing rule documented in the methodology files and enhancement addenda:
   - Has the trigger condition occurred in the last quarter?
   - If yes, was the flag generated?
   - If the trigger condition has not occurred, is the routing rule still relevant?

### Output Format

```markdown
## Cross-Monitor Signal Audit — Q2 2026

### Signals Sent
| Source | Target | Flag | Date | Received? | Acted On? | Notes |
|---|---|---|---|---|---|---|
| WDM | ESA | Hungary severity ↑ | 2026-03-24 | ✅ | ✅ | ESA updated P5 score |
| GMM | ESA | EUR weakness sustained 3 weeks | 2026-04-01 | ✅ | ❌ | ESA noted but did not score — document why |
| FCW | WDM | FIMI campaign in Georgia | 2026-03-17 | ❌ | — | Signal lost — investigate |

### Signals Expected but Not Generated
| Routing Rule | Trigger Condition | Occurred? | Flag Generated? |
|---|---|---|---|
| GMM→SCEM: Orange-band + energy region escalation | Not occurred in Q2 | N/A | N/A |
| WDM→FCW: Rapid Decay + FIMI campaign | Occurred 2026-03-17 | ❌ | **Gap — WDM did not generate flag** |
```

### Escalation

- Any signal that was sent but not received → investigate the `intelligence-digest.json` pipeline
- Any signal that should have been generated but was not → flag to the source monitor's Domain Analyst via `notes-for-computer.md`
- Systemic pattern (≥3 lost signals in a quarter) → escalate to Computer and Peter

---

## 5.2 Schema Version Drift Detection

When one monitor's cron prompt expects a field that the shared renderer doesn't handle, the result is a silent rendering failure — data exists in JSON but is invisible on the page.

### Audit Procedure (Quarterly)

1. Extract the full key set from each monitor's `report-latest.json`
2. Cross-reference against the corresponding `render` function in `renderer.js`
3. Flag any key that:
   - Exists in JSON but has no rendering path → **Invisible Data**
   - Exists in the renderer but not in JSON → **Orphaned Renderer** (dead code)
   - Has changed type (string → array, number → object) without a `schema-changelog.json` entry → **Undocumented Schema Change**
4. Cross-reference `schema-changelog.json` against actual JSON structures — are all documented changes reflected in the live schema?

### Output Format

```markdown
## Schema Drift Audit — Q2 2026

### Invisible Data (JSON key exists, no renderer)
| Monitor | Key | First appeared | Impact |
|---|---|---|---|
| AGM | module9.technicalfriction | 2026-04-04 | High — analytical value not reaching reader |

### Orphaned Renderers (renderer expects key, JSON missing)
| Monitor | Expected key | Last seen in JSON | Impact |
|---|---|---|---|
| GMM | signal.aicapexwatch | Never | Low — new field, cron not yet producing it |

### Undocumented Changes
| Monitor | Key | Old type | New type | schema-changelog entry? |
|---|---|---|---|---|
| None found | — | — | — | — |
```

---

## 5.3 Failure Modes — Additions

**AUDIT-003: DOCUMENTATION-REALITY DIVERGENCE**
The most insidious audit finding: COMPUTER.md says "all PRs require staging review" but git history shows direct-to-main merges in the last quarter. The Auditor must check process documentation against actual behaviour, not just against other documentation.

**AUDIT-004: ROUTING RULE ACCUMULATION**
Each enhancement addendum adds cross-monitor routing rules. Over time, the total number of routing rules may exceed what any single agent can realistically check in a session. The Auditor should count active routing rules quarterly. If the count exceeds 30, propose consolidation or tiering (mandatory vs. advisory routes).

---

# ENHANCEMENT 6: PLATFORM DEVELOPER

**Enhancement level:** Minor  
**Priority:** Lower  
**Mission anchor:** *"All output is free. All methodology is published. The platform does not offer paid access."* — a public commons must be accessible to all users, including those using assistive technology.

---

## 6.1 Accessibility Audit Process

The platform's public commons mission means accessibility is a structural requirement, not a nice-to-have. A democracy monitor that cannot be read by a visually impaired policy researcher has failed its public purpose.

### WCAG 2.2 AA Compliance Checklist (Run Quarterly, All 7 Monitor Pages + Homepage)

**Perceivable:**
- [ ] All images have meaningful `alt` text (decorative images: `alt=""`)
- [ ] Colour is never the sole means of conveying information (confidence levels use colour + icon + label)
- [ ] Text contrast meets 4.5:1 for body, 3:1 for large text — including on monitor-accent backgrounds
- [ ] Charts have text alternatives (data table or `aria-label` with key values)
- [ ] Font size never below 12px; body text at 16px minimum

**Operable:**
- [ ] All interactive elements reachable via Tab key in logical order
- [ ] Focus indicators visible on all interactive elements (not just browser default)
- [ ] Skip-to-content link as first focusable element on every page
- [ ] No keyboard traps (modals, dropdowns all dismissable via Escape)
- [ ] Touch targets ≥44×44px on mobile

**Understandable:**
- [ ] Page language declared (`<html lang="en">`)
- [ ] Heading hierarchy: one `<h1>` per page, `<h2>`→`<h3>` in order, no skipped levels
- [ ] Form inputs have associated `<label>` elements
- [ ] Error messages are specific and adjacent to the error

**Robust:**
- [ ] Semantic HTML throughout (`<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`)
- [ ] ARIA landmarks for major page regions
- [ ] Valid HTML (no duplicate IDs, proper nesting)
- [ ] Screen reader tested (VoiceOver on macOS, or NVDA) on at least 2 monitor pages per quarter

### Automated + Manual Split

- **Automated (every deploy):** axe-core or Lighthouse accessibility audit in CI pipeline. Target: zero critical violations.
- **Manual (quarterly):** Screen reader walkthrough of 2 monitor pages. Keyboard-only navigation test of all 7 monitor landing pages. Colour contrast spot-check on all severity/confidence visual encodings.

### Chart Accessibility

Charts are the platform's primary visual communication tool. They must be accessible:
- Every chart has a text summary (`aria-label` or adjacent `<p>`) stating the key finding the chart communicates
- Data tables are available as an alternative to every chart (expandable, not default-visible)
- Chart colours meet contrast requirements against the background
- Hover/tooltip information is accessible via keyboard focus, not only mouse

---

## 6.2 Failure Modes — Addition

**FE-026: ACCESSIBILITY REGRESSION**
A CSS change to the shared library inadvertently reduces contrast below WCAG AA on a monitor-accent background. The CI pipeline doesn't catch it because the Lighthouse check runs against one page, not all 7 monitor accent colours. Fix: run contrast validation against all 7 `--monitor-accent` values in CI pipeline, not just the default.

---

*End of Role Enhancement Addenda v1.0*

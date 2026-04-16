
## 2026-04-16 — CRITICAL: Source hallucination propagated to publication

**Monitor:** ESA | **Stage:** weekly-research → reasoner → synthesiser → publisher
**Severity:** Critical — fabricated claim published as lead signal

Weekly research (sonar-deep-research) fabricated a Euractiv URL and claim: "EU Commission awarded first ReArm Europe EDIP contracts worth €500M to Rheinmetall and Nexter." The URL does not exist. The claim conflates March 2024 ASAP with March 2026 EDIP. No such contract exists.

**Root cause:** No pipeline stage validates source URL reachability or cross-checks claim dates against actual source publication dates. The LLM hallucinated a plausible-sounding URL and claim, and every downstream stage trusted it.

**Impact:** Published as ESA lead signal W/E 16 April 2026. Google search for the claim returns only 2024 results — reputational risk if readers fact-check.

**Fix required:** ENGINE-RULES.md Section 13 documents 5 required fixes (R1-R5): URL reachability checks, date cross-validation, reasoner source trust boundary, publisher source gate, platform-wide implementation. These are class-level fixes affecting all 8 monitors.

**Logged to:** pipeline/incidents/ via incident_log.py

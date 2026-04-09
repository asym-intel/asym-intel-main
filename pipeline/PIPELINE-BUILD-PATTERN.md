> **Partially superseded — 9 April 2026.** The "Computer Analyst cron" references
> in this document are now historical. Publication is handled by
> `pipeline/publishers/publisher.py` (zero credits, GitHub Actions).
> The Collector and Weekly Research build patterns are still current.
> See `ops/cron-schedule.md` in asym-intel-internal for the canonical schedule.

# GitHub Actions Pipeline Build Pattern
## Reusable guide for adding Collector + Weekly Research to any monitor
### Version 1.0 — 2 April 2026 | asym-intel.info

---

## What this pattern does

Moves the research workload out of the Computer Analyst cron and into GitHub Actions,
which calls the Perplexity API directly. The Analyst cron becomes a pure methodology
engine — it receives pre-researched structured JSON and applies scoring, confidence
assignment, schema construction, and publication.

```
GitHub Actions (daily, sonar)          → pipeline/{slug}/daily/
GitHub Actions (daily, sonar)                    → pipeline/{slug}/daily/
GitHub Actions (weekly Wed 18:00, sonar-pro)      → pipeline/{slug}/weekly/
GitHub Actions (weekly Wed 20:00, sonar-deep-research) → pipeline/{slug}/reasoner/

Computer Analyst cron (weekly, publish day)
  Step 0C: reads daily Collector output
  Step 0D: reads weekly research output
  Step 0E: reads Reasoner analytical conclusions
  Applies methodology → publishes
```

---

## Cost profile

| Layer | Model | Cadence | Est. cost/month |
|-------|-------|---------|----------------|
| Daily Collector | sonar | Daily | ~$0.02 |
| Weekly Research | sonar-pro | Weekly | ~$0.05 |
| Reasoner | sonar-deep-research | Weekly (day before Analyst) | ~$0.05 |
| Computer Analyst | n/a | Weekly | Computer credits |
| **Total per monitor** | | | **~$0.12/month + Computer** |

---

## Files needed per monitor

```
asym-intel-main/
  .github/workflows/
    {slug}-collector.yml         ← daily Perplexity call (sonar)
    {slug}-weekly-research.yml   ← weekly Perplexity call (sonar-pro)
    {slug}-reasoner.yml          ← weekly reasoning call (sonar-deep-research)
  pipeline/monitors/{slug}/
    collect.py                   ← daily collection script
    weekly-research.py           ← weekly research script
    fcw-collector-api-prompt.txt       ← daily Collector prompt (JSON output)
    {slug}-weekly-research-api-prompt.txt ← weekly research prompt (JSON output)
    fcw-reasoner.py                        ← Reasoner script (no prompt file needed — prompt is inline)
    daily/
      README.md
      daily-latest.json          ← stub (overwritten daily)
    weekly/
      README.md
      weekly-latest.json         ← stub (overwritten weekly)
    reasoner/
      reasoner-latest.json       ← stub (overwritten weekly)

asym-intel-internal/prompts/
  {MONITOR}-COLLECTOR-PROMPT-v1.md   ← identity card (not used by GitHub Actions)
```

---

## Step-by-step build guide

### Step 1 — Define what moves to GitHub Actions vs stays in Analyst

**Moves to daily Collector (sonar):**
- Ongoing monitoring of source feeds
- Finding new events/developments/operations
- Deduplicating against active registry
- Producing candidate findings with confidence_preliminary

**Moves to weekly research (sonar-pro — live web search with deeper synthesis):**
- Deep synthesis across all sources for the past 7 days
- Actor posture analysis
- Campaign updates and new campaigns
- Platform enforcement actions
- Weekly brief narrative
- Cross-monitor signal identification

**Stays in Analyst cron (always):**
- Publish guard (day/hour/recency checks)
- persistent-state.json load
- intelligence-digest.json read
- Step 0C (daily Collector review)
- Step 0D (weekly research review)
- MF-flag application and analytical judgment
- Final confidence assignment
- Schema construction + two-pass commit
- Hugo brief filing
- Notification

### Step 2 — Write the daily Collector API prompt

File: `pipeline/monitors/{slug}/{slug}-collector-api-prompt.txt`

Requirements:
- Instruct model to output ONLY valid JSON (no markdown, no code fences)
- Include the full Tier 0 base schema as a template
- Define monitor-specific source list and source tiers
- Define inclusion threshold (4 conditions or monitor equivalent)
- Define confidence_preliminary levels with explicit evidentiary thresholds
- Include monitor-specific extension fields after base fields
- Instruction: "Return ONLY valid JSON matching this exact schema"

### Step 3 — Write collect.py

Copy from `pipeline/monitors/fimi-cognitive-warfare/collect.py` and adapt:
- Change `OUT_DIR` path to `pipeline/monitors/{slug}/daily`
- Change schema validation to match monitor-specific required fields
- Keep the JSON strip logic (model may wrap in code fences despite instructions)
- Keep the guard check (skip if today's file exists)
- Keep the schema_version check (`tier0-v1.0`)
- Adapt `_meta.monitor_slug` check
- Add monitor-specific validation rules if needed

### Step 4 — Write fcw-collector.yml (daily workflow)

Copy from `.github/workflows/fcw-collector.yml` and adapt:
- Change workflow name
- Change script path in `run:` step
- Keep schedule as `"0 7 * * *"` (07:00 UTC daily)
- Keep `PPLX_API_KEY` secret reference (same secret for all monitors)
- Change commit message prefix

### Step 5 — Write the weekly research API prompt

File: `pipeline/monitors/{slug}/{slug}-weekly-research-api-prompt.txt`

Requirements:
- Instruct model to output ONLY valid JSON
- Include full weekly research schema as template
- Define monitor-specific source list
- Define what "new this week" means for this domain
- Include weekly_brief_narrative field (400-600 words)
- Include cross_monitor_signals for adjacent monitors
- Instruction: "Return ONLY valid JSON"

Monitor-specific source lists:
| Monitor | Primary sources |
|---------|----------------|
| FCW | Meta CIB, Google TAG, MSTIC, EEAS, Stanford IO, DFRLab, ASPI |
| WDM | V-Dem, CIVICUS, Freedom House, OSCE ODIHR, Venice Commission, RSF |
| SCEM | ACLED, UCDP, ISW, UN OCHA, IISS, ICJ, SIPRI |
| AGM | arXiv, Nature, AISI, NIST, IEEE, DeepMind/OpenAI blogs, METR |
| ESA | EEAS, NATO, ECFR, Bruegel, European Parliament, Ifo |
| ERM | IPCC, Science/Nature, UNEP, WRI, Global Carbon Project, Copernicus |
| GMM | Fed, ECB, BIS, IMF, Bloomberg/Reuters data, FRED |

### Step 6 — Write weekly-research.py

Copy from `pipeline/monitors/fimi-cognitive-warfare/weekly-research.py` and adapt:
- Change `OUT_DIR` path
- Change schema_version check (`weekly-research-v1.0`)
- Change `_meta.monitor_slug`
- Adapt required fields validation for monitor schema
- Adapt the summary print statement

### Step 7 — Write weekly research workflow

Copy from `.github/workflows/fcw-weekly-research.yml` and adapt:
- Change workflow name
- Change schedule — run day before Analyst publish:

| Monitor | Analyst day | Research workflow schedule |
|---------|------------|---------------------------|
| WDM | Monday 06:00 UTC | Sunday 18:00 UTC: `"0 18 * * 0"` |
| GMM | Tuesday 08:00 UTC | Monday 18:00 UTC: `"0 18 * * 1"` |
| ESA | Wednesday 19:00 UTC | Wednesday 06:00 UTC: `"0 6 * * 3"` |
| FCW | Thursday 09:00 UTC | Wednesday 18:00 UTC: `"0 18 * * 3"` ✅ |
| AGM | Friday 09:00 UTC | Thursday 18:00 UTC: `"0 18 * * 4"` |
| ERM | Saturday 05:00 UTC | Friday 18:00 UTC: `"0 18 * * 5"` |
| SCEM | Sunday 18:00 UTC | Saturday 18:00 UTC: `"0 18 * * 6"` |

### Step 8 — Add Step 0D to the Analyst cron prompt

After Step 0C (daily Collector review), add Step 0D:

```bash
WEEKLY_PATH="pipeline/monitors/{slug}/weekly"
WEEKLY=$(gh api /repos/asym-intel/asym-intel-main/contents/${WEEKLY_PATH}/weekly-latest.json \
  --jq '.content' | base64 -d 2>/dev/null || echo "")

if [ -z "$WEEKLY" ]; then
  echo "STEP 0D: No weekly research found. Proceeding with research-only mode."
else
  echo "$WEEKLY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
meta = d.get('_meta', {})
lead = d.get('lead_signal', {})
campaigns = d.get('campaigns', [])
print(f'Weekly research week_ending: {meta.get(\"week_ending\",\"unknown\")}')
print(f'Lead: [{lead.get(\"confidence_preliminary\")}] {lead.get(\"headline\",\"\")[:80]}')
print(f'Campaigns: {len(campaigns)} | Actor entries: {len(d.get(\"actor_tracker\",[]))}')
print(f'Platform responses: {len(d.get(\"platform_responses\",[]))}')
print()
print('USE THIS RESEARCH as the basis for your report. Apply FCW methodology:')
print('- Confirm/adjust confidence levels using your own source checks')
print('- Apply MF-flags to all findings')
print('- Update persistent campaign registry based on campaigns array')
print('- Use weekly_brief_narrative as the starting draft for the Hugo brief')
"
fi
```

Then replace Step 1 (research) with:

```
STEP 1 — Apply methodology to weekly research output (Step 0D):
  If weekly research was loaded: use it as primary source material.
  Apply MF1-MF4 flags to all findings.
  Confirm or adjust confidence_preliminary → assign final confidence.
  If weekly research was NOT loaded: conduct research directly (fallback).
  In either case: cross-check against daily Collector candidates (Step 0C).
```

### Step 8B — Write the Reasoner (optional but recommended for complex monitors)

The Reasoner uses `sonar-deep-research` to reason over the accumulated structured data
from persistent-state + Collector + weekly research. It does NOT search the web — it
reasons over documents you feed it.

Copy `pipeline/monitors/fimi-cognitive-warfare/fcw-reasoner.py` and adapt:
- Change `OUT_DIR` and file paths
- Adapt the context extraction (what sections to pull from persistent-state)
- Adapt the prompt's analytical tasks for the monitor domain:
  - FCW: attribution chain analysis, campaign linkage detection
  - WDM: country deterioration pattern analysis, mimicry chain detection
  - SCEM: conflict trajectory modelling, I1-I6 deviation pattern reasoning
  - AGM: capability-governance lag analysis across 16 modules
- Keep the context size limit (40,000 chars) and truncation logic
- Keep the `import re` at the top

Schedule: 2 hours after weekly research (same Wednesday, before Thursday Analyst):
  FCW:  Wed 20:00 UTC  `"0 20 * * 3"`
  WDM:  Sun 20:00 UTC  `"0 20 * * 0"`
  SCEM: Sat 20:00 UTC  `"0 20 * * 6"`

Add Step 0E to the Analyst cron after Step 0D — same pattern as Step 0D but reads
`pipeline/{slug}/reasoner/reasoner-latest.json`.

### Step 9 — Create pipeline directory stubs

```bash
# Create weekly/ directory stub
echo '{
  "_meta": {"schema_version": "weekly-research-v1.0", "monitor_slug": "{slug}",
            "status": "stub", "note": "Stub — first real content after first workflow run"}
}' > pipeline/monitors/{slug}/weekly/weekly-latest.json
```

### Step 10 — Commit and verify

1. Commit all files to `asym-intel-main`
2. Add `PPLX_API_KEY` to repo secrets (already done for FCW)
3. Trigger manual run from GitHub Actions tab
4. Check output JSON in `pipeline/monitors/{slug}/`
5. Verify schema validation passed in workflow logs
6. Check Analyst cron reads Step 0D correctly on next run

---

## Known issues + solutions

**Model wraps JSON in code fences despite instructions**
→ `collect.py` / `weekly-research.py` strip fences automatically. Already handled.

**sonar-pro is the correct weekly model, NOT sonar-deep-research.**
sonar-deep-research is a reasoning model — it cannot browse live URLs.
sonar-pro does live web search with deeper synthesis. Always use sonar-pro for weekly research.

**Schema validation fails on first run**
→ Check `pipeline/monitors/{slug}/debug-YYYY-MM-DD.json` for raw model output.
→ Adjust prompt if model is consistently producing a different structure.
→ Run workflow manually from Actions tab after fixing.

**Analyst cron Step 0D has no weekly research (first week)**
→ "STEP 0D: No weekly research found" is expected first run. Analyst falls back to direct research.

**week_ending date wrong**
→ `weekly-research.py` calculates next Saturday from today. Correct for all weekdays.

---

## Lessons learned (FCW pilot — 2 April 2026)

1. **sonar (not sonar-pro) is sufficient for daily Collector.** Fast, cheap, produces valid JSON reliably.
2. **Zero findings is a valid and correct result.** Daily threshold filtering works — 4 background reports excluded correctly on first run.
3. **JSON stripping is necessary.** Model occasionally wraps output in code fences despite explicit instruction. The strip logic in collect.py handles this.
4. **GitHub Actions completes in ~20 seconds** for sonar daily calls. sonar-deep-research will take 60-120 seconds — set timeout to 300s.
5. **One PPLX_API_KEY secret covers all monitors.** No per-monitor secrets needed.
6. **sonar-deep-research IS correct for the Reasoner.** Feed it structured JSON as
   context in the prompt — it reasons over that data without searching the web.
   The Reasoner prompt includes the actual JSON inline; the model reasons over it.
   Empty input (no campaigns, no findings) → Reasoner correctly returns empty output
   with a clear explanation. This is correct behaviour, not a failure.
7. **sonar-deep-research is NOT for live web search.** It refused to generate FIMI intelligence
   because it cannot browse live URLs — it is a reasoning/synthesis model for documents you
   provide, not an OSINT collection tool. Use `sonar-pro` for weekly research workflows.
   Model selection: `sonar` for daily (fast, cheap), `sonar-pro` for weekly (deeper search).
6. **Analyst cron Step 0D is a fallback not a dependency.** If weekly research fails, Analyst runs in research-only mode. Never let research layer failure block publication.

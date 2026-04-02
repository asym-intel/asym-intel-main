# Annual Calibration Files Reminder — `631c0fa0`

**Schedule:** 28 March annually (09:00 UTC)  
**Purpose:** Remind Peter to create annual calibration files for all 7 monitors before the new methodology year begins.

## What to do

Use `api_credentials=["github"]`.

### Step 1 — Check which files already exist

```bash
gh api /repos/asym-intel/asym-intel-internal/contents/methodology \
  --jq '[.[] | .name]'
```

Derive current year from system date:
```bash
YEAR=$(date -u +%Y)
```

### Step 2 — Compare against expected files

Expected files (naming convention: `{slug}-{index}-{YEAR}.md`):

| File | Monitor | Source | Typical publish |
|------|---------|--------|-----------------|
| `democratic-integrity-vdem-{YEAR}.md` | WDM | [v-dem.net](https://v-dem.net) | March |
| `environmental-risks-copernicus-{YEAR}.md` | ERM | [climate.copernicus.eu](https://climate.copernicus.eu) | Early year |
| `conflict-escalation-acled-{YEAR}.md` | SCEM | [acleddata.com](https://acleddata.com) | December prev year |
| `ai-governance-euaiact-{YEAR}.md` | AGM | [artificialintelligenceact.eu](https://artificialintelligenceact.eu) | Ongoing |
| `macro-monitor-imf-{YEAR}.md` | GMM | [imf.org/weo](https://imf.org/en/Publications/WEO) | April |
| `european-strategic-autonomy-ecfr-{YEAR}.md` | ESA | [ecfr.eu](https://ecfr.eu) | Early year |
| `fimi-cognitive-warfare-eeas-{YEAR}.md` | FCW | [euvsdisinfo.eu](https://euvsdisinfo.eu) | Annual |

### Step 3 — Notify with missing files

**If all 7 exist:** Send a notification confirming all calibration files are present for {YEAR}.

**If any are missing:**

**Title:** `Annual calibration files due — {MONTH} {YEAR}`

**Body:**
- List each missing file with its expected filename and source URL
- Note: "These files are self-discovered by cron agents at Step 0B+ — once committed to `asym-intel-internal/methodology/` with the correct name, all 7 Analyst crons pick them up automatically on their next run."
- Note: "The IMF WEO calibration (GMM) typically publishes in April — may not be available yet at the 28 March trigger date."

## Notes

- Files are auto-discovered by all 7 Analyst crons at Step 0B+ using the convention `{slug}-{index}-{YEAR}.md`
- No manual wiring needed once committed with the correct filename
- This reminder fires before IMF WEO publishes (April) — GMM file being absent on 28 March is expected
- If the reminder fires and all files already exist, send a brief confirmation notification rather than silently exiting

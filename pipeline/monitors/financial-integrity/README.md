# Financial Integrity Monitor — Pipeline

**Monitor:** FIM (Financial Integrity Monitor)
**Slug:** `financial-integrity`
**Accent:** `#8b0000`
**Methodology:** `asym-intel-internal/methodology/drafts/fim-methodology-full-v2.md`
**Entity set:** `asym-intel-internal/methodology/fim-entity-set.md`

## Pipeline Files

| File | Purpose |
|---|---|
| `fim-collector-api-prompt.txt` | Collector prompt — daily financial integrity findings |
| `fim-chatter-api-prompt.txt` | Standalone chatter prompt (fallback — normal chatter via unified) |
| `collect.py` | Collector Python script — calls Perplexity, validates, writes output |
| `fim-chatter.py` | Standalone chatter Python script (emergency re-run only) |
| `daily/` | Daily collector output (daily-latest.json + dated verified files) |

## GA Workflows

| Workflow | Schedule | Notes |
|---|---|---|
| `fim-collector.yml` | Daily 07:35 UTC (via CF Worker) | Tier 0 daily collection |
| `fim-chatter.yml` | Manual only | Standalone fallback — normal chatter via unified-chatter.yml |

## Entity Set Summary

- **Layer 1:** 24 jurisdictions (7 Tier A daily, 5 Tier B daily, 7 Tier C rotating, 5 Tier D rotating)
- **Layer 2:** 6 actor categories (state-linked, professional enablers, TBML, dark infrastructure, digital-asset, conflict/terrorism/proliferation)
- **Layer 3:** 5 standing trackers (Russian sanctions evasion, EU AML/AMLA, FATF grey list, BO registry, crypto integrity)
- **Layer 4:** Tiered source anchors (FATF, OFAC, OFSI, FinCEN, OCCRP, ICIJ, Global Witness, FT, Bloomberg, Reuters)

## Three-Pillar Coverage

AML + CTF + CPF — all three FATF pillars scanned explicitly.

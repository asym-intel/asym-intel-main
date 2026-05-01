# fe-commons

Canonical shared FE primitives for Class B consumer-surface repos.

**Authority:** AD-2026-04-30-BK + AD-2026-04-30-BM
**Contract:** `asym-intel-internal:docs/design-system/L3-patterns/fe-implementation-contract.md`
**Consumption mechanism:** build-time copy via `actions/checkout` sparse-checkout (see §5 of the contract)

## Contents

| File | Purpose |
|---|---|
| `tokens.css` | Class B dark-palette token scale. Consumed by advennt, investor, payments-gi. Per-class value overrides go in per-project CSS; do not fork this file. |

## Adding a primitive

1. Confirm it matches a §2 forbidden pattern (formatters, hydration helpers, empty-state components, etc.)
2. Confirm it generalises to ≥2 Class B consumers
3. Add the file here; update this README
4. Author an AD entry if the addition changes the contract boundary

## Drift detection

`commons-drift-lint.yml` reusable workflow (live, observe-mode until 2026-05-14). Per-project repos opt in via:

```yaml
jobs:
  commons-drift:
    uses: asym-intel/asym-intel-main/.github/workflows/commons-drift-lint.yml@main
    secrets:
      ASYM_INTEL_PIPELINE: ${{ secrets.ASYM_INTEL_PIPELINE }}
```
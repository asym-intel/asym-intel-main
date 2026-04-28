# Persistent-State Routing Contract

**Status:** Doctrine — enforced by `tools/preflight.py` (contract-coverage + no-shadow checks)
**Introduced:** Sprint 4 §0, AD-2026-04-24
**Owner:** Shared across all 7 monitors

## Why this exists

Sprint 4 §0 audit surfaced a **class-of-issue** across persistent-state data:

- Persistent-state JSON files accumulate keys (baselines, calibration logs, 2026 methodology anchors) that are never routed to a reader-visible surface.
- Local render helpers in `static/monitors/{slug}/persistent.html` shadow the shared library (`assets/js/renderer.js`), causing silent divergence — an instance fix to one monitor does not reach its siblings.
- New persistent-state keys added by the weekly publisher or by editorial can go unrendered indefinitely because nothing enforces coverage.

This contract makes every top-level persistent-state key **declarable** against one of four routes, and makes unlisted keys a CI failure.

## The four routes

| Route | Meaning | Surface |
|---|---|---|
| **Living Knowledge** | Reader-visible on the monitor's Living Knowledge (`persistent.html`) page | `static/monitors/{slug}/persistent.html` |
| **Dashboard** | Reader-visible on the monitor dashboard | `static/monitors/{slug}/dashboard.html` |
| **Both** | Rendered on both pages | both HTML files |
| **Archive-only** | Intentionally not rendered; retained in JSON for audit, replay, methodology anchoring. Must carry a `reason`. | n/a |

## Declaring routes

Each monitor has a `routes` block in this doc. Every top-level key in `data/monitors/{slug}/persistent-state.json` **must** appear in the block. `schema_version`, `generated_at`, `monitor`, and `last_updated` are exempt meta keys.

The preflight check reads this file, parses each monitor's routes block, and fails if any persistent-state top-level key is not listed.

## Renderer source-of-truth

When the route is Living Knowledge, Dashboard, or Both:

- **Must** use a shared renderer on `window.AsymPersistent` or `window.AsymSections`.
- **Must not** define local `renderEntityList`, `renderEntityObj`, `renderEntityCard`, `renderVersionHistory` (monitor-specific sibling-alternatives like ERM's 3-arg `renderVersionHistory` are explicitly grandfathered by name in the shadow-check).
- New section-level renderers (e.g. per-domain panels a monitor uniquely needs) belong in `assets/js/renderer.js` under the `AsymSections` namespace — not in the monitor HTML.

When the route is Archive-only:

- No renderer is attached. The `reason` documents intent — e.g. "methodology anchor retained for calibration replay; future render deferred to Sprint 4 §2".

## Monitor routes

### WDM — democratic-integrity

```yaml
routes:
  heatmap_countries: Living Knowledge     # renderCountryHeatmap
  mimicry_chains: Living Knowledge        # AsymSections.renderMimicryChains
  institutional_integrity_active_flags: Living Knowledge  # card grid
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog (ref impl for others)
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  structural_facts: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  windowed_events: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### GMM — macro-monitor

```yaml
routes:
  asset_class_baseline: Living Knowledge  # AsymSections.renderAssetClassBaseline
  active_tactical_alerts: Both            # dashboard alerts ribbon + LK panel
  oil_supply_shock_driver: Living Knowledge
  blind_spot_overrides: Living Knowledge
  conviction_history: Living Knowledge    # renderConvictionSparkline
  tariff_escalation_protocol: Living Knowledge
  us_decoupling_index: Living Knowledge
  ai_capex_watch: Living Knowledge
  imf_weo_status: Living Knowledge
  blind_spots: Living Knowledge
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog (ref impl for others)
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  standing_supply_shock_drivers: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  regime_classification: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  us_fiscal_sustainability: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  recession_indicators: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### FCW — fimi-cognitive-warfare

```yaml
routes:
  active_campaigns: Living Knowledge
  actor_profiles: Living Knowledge
  platform_enforcement_tracker: Living Knowledge
  ai_fimi_calibration_2026: Living Knowledge
  platform_transparency_2026: Living Knowledge
  disarm_version: Living Knowledge
  campaign_baselines_2026: Living Knowledge
  calibration_log: Living Knowledge       # inline (planned migration to AsymSections — Sprint 4 §1)
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  infrastructure_registry: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  regulatory_framework: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### ESA — european-strategic-autonomy

```yaml
routes:
  kpi_state: Living Knowledge
  active_elections: Both
  state_capture_cases: Living Knowledge
  active_actor_campaigns: Living Knowledge
  eu_legislation_tracker: Living Knowledge
  timeline_events: Living Knowledge
  lagrange_scoring_2026: Living Knowledge
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog — LANDING §0
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  capability_domains: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  capability_programmes: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  capability_stocks: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  dependencies: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  partner_taxonomy: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  strategic_compass_milestones: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  trade_instruments: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  enlargement_cfsp: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### AGM — ai-governance

```yaml
routes:
  module_7_risk_vectors: Living Knowledge     # renderEntityList (shared AsymPersistent, post §0)
  module_9_eu_ai_act_tracker: Living Knowledge  # renderEuActTrackerVisual
  module_14_concentration_index: Living Knowledge  # renderConcentrationVisual
  module_15_aisi_pipeline: Living Knowledge
  module_5_standards_vacuum: Living Knowledge
  module_5_ciyuan: Living Knowledge
  ongoing_lab_postures: Living Knowledge
  cross_monitor_flags: Both
  eu_ai_act_tracker: Living Knowledge
  gpai_compliance: Living Knowledge
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog — LANDING §0
  # Methodology anchors — future sprint renders as collapsed panels above each module
  risk_vectors_2026_baseline: Archive-only
    reason: "Methodology-dated baseline snapshot. Planned render as 'Methodology anchor' collapsed panel above module_7 in Sprint 4 §1+."
  concentration_index_2026: Archive-only
    reason: "Methodology anchor for module_14. Deferred render — §1+."
  aisi_status_2026: Archive-only
    reason: "Methodology anchor for module_15. Deferred render — §1+."
  last_issue: Archive-only
    reason: "Publisher metadata for replay cross-reference. Read by build tools, not reader-facing."
  country_grid_status: Archive-only
    reason: "Jurisdiction grid — planned new section on persistent.html via AsymSections.renderJurisdictionsGrid in Sprint 4 §1+."
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### ERM — environmental-risks

```yaml
routes:
  planetary_boundary_status: Living Knowledge
  tipping_system_flags: Living Knowledge
  standing_trackers: Living Knowledge
  active_attribution_gap_cases: Living Knowledge
  regional_cascade_chains: Living Knowledge
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog — LANDING §0
  # Methodology anchors & duplicate-shape keys
  planetary_boundaries_calibration: Archive-only
    reason: "Methodology anchor for planetary_boundary_status. Sprint 4 §1+."
  copernicus_2025_baselines: Archive-only
    reason: "Baseline snapshot from Copernicus 2025 data release. Calibration replay only."
  tipping_systems: Archive-only
    reason: "Methodology anchor for tipping_system_flags. Sprint 4 §1+."
  attribution_gap_standing_flags: Archive-only
    reason: "Standing-flag methodology register. Deferred render — §1+."
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  climate_physics_anchors: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  regulatory_regimes: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  carbon_markets: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  corporate_disclosure: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  climate_litigation: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  active_disruption_events: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  energy_transition_stocks_flows: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  supply_chain_choke_points: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  nature_biodiversity: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

### SCEM — conflict-escalation

```yaml
routes:
  conflict_baselines: Living Knowledge
  f_flag_history: Living Knowledge
  roster_status: Living Knowledge
  roster_watch: Living Knowledge
  cross_monitor_flags: Both
  calibration_log: Living Knowledge       # AsymSections.renderCalibrationLog — LANDING §0
  source_hierarchy_2026: Archive-only
    reason: "Methodology anchor — Tier-1/2/3 source hierarchy snapshot. Deferred render — §1+."
  i5_calibration_2026: Archive-only
    reason: "I5 methodology calibration baseline. Deferred render — §1+."
  # DR baseline 2026-04-28 — held modules (Sprint AV BRIEF #2)
  conflict_pair_registry: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  order_of_battle: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  treaty_posture: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  escalation_thresholds: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  active_escalation_events: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  mediation_deescalation_architecture: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  alliance_security_architectures: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
  gaps_register: Archive-only
    reason: "Held reservoir per Sprint AV BRIEF #2 (DR baseline 2026-04-28). Render-surfacing deferred to post-pipeline-stable sprint."
```

## Grandfathered exemptions (Sprint 4 §1 burn-down)

The shadow-renderer check (`PSR-002`) exempts these monitor-local definitions pending shared-lib migration:

| Monitor | Function | Reason | Planned fix |
|---|---|---|---|
| ERM | `renderVersionHistory(history, toggleId, historyId)` | 3-arg sibling API used inside ERM's boundary/threshold/grid/cascade renderers — not a shared-lib shadow. | Keep as sibling; rename to `erm.renderVersionHistoryInline` in §1 for clarity. |
| AGM | `renderEntityList(arr, fields)` | Field-whitelist signature; shared-lib API is `(items, containerId, opts)`. | Add `opts.fieldWhitelist` to `AsymPersistent.renderEntityList`, migrate AGM call sites, delete local. §1. |
| AGM | `renderEntityObj(obj)` | No shared-lib equivalent. | Add `AsymPersistent.renderEntityObj(obj, containerId)` in §1, migrate AGM call sites, delete local. |

## Change protocol

- Adding a new key to `persistent-state.json`: the PR **must** also update this file with the route. CI fails otherwise.
- Changing a key's route (Archive-only → Living Knowledge, etc.): update this file in the same PR as the render wiring.
- Removing a key: remove the route entry.

## References

- AD-2026-04-24 — *Render-layer root-cause fix + routing contract* (supersedes AD-2026-04-18c)
- AD-2026-04-18b — *Single-Role Boot Governance* (ENGINE-RULES §24)
- `assets/js/renderer.js` — shared `AsymPersistent` and `AsymSections` namespaces
- `tools/preflight.py` — contract-coverage + no-shadow checks

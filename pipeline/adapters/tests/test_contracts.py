"""Adapter contract tests.

Run with: pytest -q pipeline/adapters/tests/test_contracts.py
Or standalone:  python -m pipeline.adapters.tests.test_contracts

Goals:
  1. Registry returns a usable adapter instance for (monitor, target).
  2. Adapter rejects an unknown canonical schema_version (fail-loud).
  3. Adapter output is JSON-serialisable.
  4. Every emitted module/item carries the keys the Ramparts renderer
     reads, with string fallbacks — nothing should stringify as 'undefined'.
  5. §27-L: persistent-state merge semantics honour Invariant L:
     - empty/absent synth → persistent carried forward untouched
     - partial synth → field-update + unchanged_since stamping
     - malformed synth → PersistentMergeError (fail-loud)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # .../adapter/
sys.path.insert(0, str(ROOT))

import pytest

from pipeline.adapters import get, CanonicalSchemaError  # noqa: E402
from pipeline.adapters.base import PersistentMergeError  # noqa: E402
from pipeline.adapters import ramparts_aim  # noqa: F401, E402  (triggers @register)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---- Required item shapes, keyed by (module, list_key) ----
# We assert each emitted item carries these keys AND each value is a
# plain JSON scalar/list/dict — never None/undefined-ish.
REQUIRED_ITEM_KEYS: dict[tuple[str, str], set[str]] = {
    ("module_1", "mainstream"): {
        "rank", "headline", "date", "body",
        "asymmetric", "source_label", "source_url",
    },
    ("module_1", "underweighted"): {
        "rank", "headline", "date", "body",
        "asymmetric", "source_label", "source_url",
    },
    ("module_3", "funding_rounds"): {
        "company", "amount", "valuation", "date", "lead", "focus",
        "asymmetric", "source_label", "source_url",
        "cursor_curve", "cursor_note", "persistence", "confidence",
    },
    ("module_3", "strategic_deals"): {
        "name", "type", "date", "detail", "source_label", "source_url",
    },
    ("module_4", "sectors"): {
        "name", "status", "headline", "detail",
        "asymmetric", "source_label", "source_url",
    },
    ("module_6", "threshold_events"): {
        "flag", "title", "date", "domain", "lab", "model",
        "capability", "reliability", "partnerships", "programme",
        "asymmetric", "source_label", "source_url",
    },
    ("module_6", "programme_updates"): {
        "title", "date", "domain", "lab", "detail",
        "source_label", "source_url",
    },
    ("module_6", "arxiv_highlights"): {
        "id", "title", "domain", "note", "url",
    },
    ("module_7", "vectors"): {
        "name", "color", "level", "headline", "detail",
        "asymmetric", "source_label", "source_url", "additional_items",
    },
    ("module_8", "items"): {
        "title", "date", "jurisdiction", "category", "body",
        "ihl_friction", "asymmetric", "source_label", "source_url",
    },
    ("module_9", "new_developments"): {
        "jurisdiction", "flag", "instrument", "date", "issuer",
        "domain", "obligations", "enforcement", "asymmetric",
        "source_label", "source_url",
    },
    ("module_11", "items"): {
        "title", "date", "jurisdiction", "category", "body",
        "accountability_friction", "asymmetric",
        "source_label", "source_url",
    },
}


def _load_fixture(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def adapter():
    return get("ai-governance", "ramparts-wp")


@pytest.fixture(params=["commons-aim-2026-04-10.json", "commons-aim-2026-04-17.json"])
def shaped(adapter, request):
    canonical = _load_fixture(request.param)
    out = adapter.transform(canonical)
    return out


def test_registry_returns_instance(adapter):
    assert adapter is not None
    assert adapter.monitor == "ai-governance"
    assert adapter.target == "ramparts-wp"
    assert adapter.emits_schema_version == "ramparts-v2"


def test_unknown_schema_rejected(adapter):
    canonical = {"meta": {"schema_version": "9.9"}}
    with pytest.raises(CanonicalSchemaError):
        adapter.transform(canonical)


def test_output_is_json_serialisable(shaped):
    json.dumps(shaped)  # must not raise


def test_required_item_keys_present(shaped):
    missing: list[str] = []
    for (module_key, list_key), required in REQUIRED_ITEM_KEYS.items():
        module = shaped.get(module_key) or {}
        items = module.get(list_key) or []
        if not isinstance(items, list):
            missing.append(f"{module_key}.{list_key} is not a list ({type(items).__name__})")
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                missing.append(f"{module_key}.{list_key}[{i}] is not a dict ({type(item).__name__})")
                continue
            for k in required:
                if k not in item:
                    missing.append(f"{module_key}.{list_key}[{i}] missing key '{k}'")
    assert not missing, "Contract failures:\n  " + "\n  ".join(missing)


def test_no_none_values_in_scalar_fields(shaped):
    """Scalar fields that feed the renderer must be strings or ints,
    never None/null — otherwise they stringify to 'undefined' in JS."""
    offenders: list[str] = []
    for (module_key, list_key), required in REQUIRED_ITEM_KEYS.items():
        module = shaped.get(module_key) or {}
        items = module.get(list_key) or []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            for k, v in item.items():
                if v is None:
                    offenders.append(f"{module_key}.{list_key}[{i}].{k} is None")
    assert not offenders, "None fields:\n  " + "\n  ".join(offenders)


def test_meta_carries_emitted_schema_version(shaped):
    assert shaped.get("meta", {}).get("schema_version") == "ramparts-v2"


# ---------------------------------------------------------------------------
# §27-L — Persistent-state merge contract tests
# ---------------------------------------------------------------------------
#
# These tests use a minimal synthetic canonical + persistent pair so they
# are isolated from real fixture drift. They cover the three rules that
# can silently break Ramparts Issue 4-style pages:
#
#   (L.a) empty synth for a persistent-backed module → carry forward
#   (L.b) partial synth → field-update + unchanged_since stamping
#   (L.c) contradictory synth shape → PersistentMergeError (fail-loud)
#
# Module 7 vectors is the canonical example (match_key='vector') and is
# exercised in all three tests. Other persistent-backed modules share the
# same _merge_persistent_list helper so one merge-level test per rule is
# sufficient to cover Invariant L compliance.


def _minimal_canonical(module_7_override: object = "__unset__") -> dict:
    """Build a minimal schema-2.0 canonical report. By default module_7 is
    absent (simulates empty synth). Pass explicit value to override.
    """
    canonical = {
        "meta": {
            "schema_version": "2.0",
            "published": "2026-04-17",
            "week_label": "Week 16 — 17 April 2026",
            "volume": 1,
            "issue": 4,
            "slug": "2026-04-17",
        },
        # Absence of other modules is fine — adapter tolerates missing modules.
    }
    if module_7_override != "__unset__":
        canonical["module_7"] = module_7_override  # type: ignore[assignment]
    return canonical


def _minimal_persistent() -> dict:
    """Build a persistent-state with one module_7 vector already tracked."""
    return {
        "module_7_risk_vectors": [
            {
                "vector": "compute_concentration",
                "name": "Compute Concentration",
                "color": "red",
                "level": "ELEVATED",
                "headline": "Top-3 labs hold >70% of frontier training compute.",
                "detail": "Persistent tracker detail.",
                "asymmetric": "Persistent asymmetric.",
                "source_label": "Persistent source",
                "source_url": "https://example.org/persistent",
                "additional_items": [],
                "unchanged_since": "2026-04-03",
                "last_updated": "2026-04-03",
            }
        ],
    }


def test_L_a_empty_synth_carries_persistent_forward(adapter):
    """Rule 2: absent/empty synth for module 7 → persistent vector is rendered
    unchanged, NOT cleared. Without §27-L this is the Issue 4 bug."""
    canonical = _minimal_canonical()  # no module_7
    persistent = _minimal_persistent()

    shaped = adapter.transform(canonical, persistent=persistent)

    vectors = shaped.get("module_7", {}).get("vectors", [])
    assert len(vectors) >= 1, "module_7.vectors must carry persistent floor when synth is empty"
    compute = next((v for v in vectors if v.get("name") == "Compute Concentration"), None)
    assert compute is not None, "Persistent 'Compute Concentration' vector was dropped"
    # unchanged_since must be preserved from persistent, NOT re-stamped to this week
    assert compute.get("unchanged_since") == "2026-04-03", (
        "Empty synth must NOT restamp unchanged_since — carried items keep their prior date."
    )


def test_L_b_partial_synth_field_updates_and_stamps(adapter):
    """Rule 3+4: a synth item matching a persistent vector by match_key updates
    the fields provided AND stamps unchanged_since=publish_date. Non-overlapping
    persistent entries are preserved. Shape mapping in _module_7 collapses
    `vector` (match_key) to `name`, so we identify the merged item via `name`.
    """
    canonical = _minimal_canonical({
        "vectors": [
            {
                "vector": "compute_concentration",
                "rating": "HIGH",  # adapter maps rating → color+level
                "summary": "NVIDIA allocates 80% of H-series to three customers.",
                # other fields omitted — must NOT overwrite persistent values with None
            }
        ]
    })
    persistent = _minimal_persistent()

    shaped = adapter.transform(canonical, persistent=persistent)

    vectors = shaped.get("module_7", {}).get("vectors", [])
    compute = next((v for v in vectors if v.get("name") == "Compute Concentration"), None)
    assert compute is not None, "matched vector disappeared after merge"

    # Synth provided `summary` which → headline via field-fallback. Persistent's
    # prior headline must be overwritten by the synth value.
    assert "80%" in compute.get("headline", ""), (
        "field-update failed: synth 'summary' should overwrite persistent 'headline'"
    )
    # Fields absent in synth → preserved from persistent. The adapter's _shape
    # prefers the merged dict's keys, so persistent-only fields (asymmetric,
    # detail, source_url) must survive unchanged.
    assert compute.get("asymmetric") == "Persistent asymmetric.", (
        "persistent-only field lost after partial synth merge"
    )
    assert compute.get("detail") == "Persistent tracker detail.", (
        "persistent 'detail' lost after partial synth merge"
    )
    # unchanged_since stamped to publish_date
    assert compute.get("unchanged_since") == "2026-04-17", (
        "partial synth must stamp unchanged_since to this week's publish_date"
    )


def test_L_c_contradictory_synth_shape_raises(adapter):
    """Rule 5: a synth field arriving with the wrong shape (dict where list is
    expected) MUST raise PersistentMergeError — we refuse to silently overwrite
    a persistent tracker with garbled data."""
    canonical = _minimal_canonical({
        "vectors": {"oops": "this should have been a list"},  # malformed
    })
    persistent = _minimal_persistent()

    with pytest.raises(PersistentMergeError):
        adapter.transform(canonical, persistent=persistent)


def test_L_default_persistent_arg_is_backward_compatible(adapter):
    """transform(canonical) without persistent= must still work for callers
    that haven't migrated. Persistent-backed modules just render whatever
    the canonical provides (possibly empty)."""
    canonical = _minimal_canonical()
    # Must not raise; must return a dict with a module_7 key (empty vectors is fine).
    shaped = adapter.transform(canonical)
    assert isinstance(shaped, dict)
    assert "module_7" in shaped


# ---------------------------------------------------------------------------
# Module 9 — EU AI Act layered-system + country_grid renderer contract
# ---------------------------------------------------------------------------
#
# Regression tests for the Issue 4 M9 'undefined' bug (April 2026). The
# Ramparts renderer reads a specific key-set from each layer and each
# country_grid row; emitting the wrong keys renders literal 'undefined'
# strings in the DOM. These tests lock the contract.


# Field-names the renderer's renderM8_LawGuidance function reads on each
# eu_ai_act_layered.layers[] entry.
M9_LAYER_REQUIRED_KEYS: set[str] = {
    "layer", "instrument", "status", "status_class",
    "timeline", "week_update", "source_url",
}

# Field-names the renderer reads on each country_grid[] row.
COUNTRY_GRID_REQUIRED_KEYS: set[str] = {
    "jurisdiction", "status_icon", "binding_law", "key_guidance",
    "last_updated", "change_flag",
}

# Allowed values of status_class (renderer switches on these three buckets).
STATUS_CLASS_ALLOWED: set[str] = {"active", "gap", ""}


def _persistent_with_eu_ai_act(shape: str = "both") -> dict:
    """Build a persistent-state with EU AI Act layer data.

    shape='A'    → only eu_ai_act_tracker.layers (dict shape)
    shape='B'    → only module_9_eu_ai_act_tracker.layers (list shape)
    shape='both' → both present (Shape B should win by adapter priority)
    """
    state: dict = {}
    if shape in ("A", "both"):
        state["eu_ai_act_tracker"] = {
            "standards_vacuum_flag": "ACTIVE",
            "last_updated": "2026-04-10",
            "layers": {
                "layer_1_text": {"status": "confirmed", "note": "OJ L 2024/1689"},
                "layer_3_harmonised_standards": {
                    "status": "standards_vacuum_active",
                    "note": "No OJ citation; CEN-CENELEC JTC21 Stage 40",
                    "last_updated": "2026-04-05",
                },
            },
        }
    if shape in ("B", "both"):
        state["module_9_eu_ai_act_tracker"] = {
            "current_days_to_deadline": 104,
            "standards_vacuum_active": True,
            "layers": [
                {
                    "layer": 1,
                    "name": "AI Act Text",
                    "status": "Active",
                    "note": "Regulation in force.",
                    "unchanged_since": "2026-03-30",
                },
                {
                    "layer": 3,
                    "name": "Harmonised Standards (CEN-CENELEC JTC21)",
                    "status": "Delayed",
                    "note": "Standards expected Q4 2026.",
                    "unchanged_since": "2026-03-30",
                },
            ],
        }
    return state


def test_M9_layers_carry_renderer_keys(adapter):
    """Every emitted eu_ai_act_layered.layers[] entry must carry the exact
    key-set the Ramparts M9 renderer reads. Missing keys render as 'undefined'
    in the DOM — this is the Issue 4 regression class."""
    canonical = _minimal_canonical()
    persistent = _persistent_with_eu_ai_act(shape="B")
    shaped = adapter.transform(canonical, persistent=persistent)
    layers = shaped.get("module_9", {}).get("eu_ai_act_layered", {}).get("layers", [])
    assert layers, "expected layers to be built from persistent state"
    for i, layer in enumerate(layers):
        assert isinstance(layer, dict), f"layer {i} is not a dict"
        missing = M9_LAYER_REQUIRED_KEYS - set(layer.keys())
        assert not missing, f"layer {i} missing renderer keys: {missing}"
        # None values would stringify to 'undefined' in the template literal.
        for k in M9_LAYER_REQUIRED_KEYS:
            assert layer[k] is not None, f"layer {i}.{k} is None"
            assert not isinstance(layer[k], (list, dict)), (
                f"layer {i}.{k} must be a scalar, got {type(layer[k]).__name__}"
            )


def test_M9_layers_status_class_is_bucketed(adapter):
    """status_class must be one of 'active' / 'gap' / '' — the three buckets
    the renderer switches on for pill colour."""
    canonical = _minimal_canonical()
    persistent = _persistent_with_eu_ai_act(shape="both")
    shaped = adapter.transform(canonical, persistent=persistent)
    layers = shaped.get("module_9", {}).get("eu_ai_act_layered", {}).get("layers", [])
    for layer in layers:
        assert layer["status_class"] in STATUS_CLASS_ALLOWED, (
            f"status_class={layer['status_class']!r} not in {STATUS_CLASS_ALLOWED}"
        )


def test_M9_layers_prefer_shape_B_when_both_present(adapter):
    """When both Shape A and Shape B persistent shapes are present, Shape B
    wins (richer: carries `name`, `unchanged_since`, prose status)."""
    canonical = _minimal_canonical()
    persistent = _persistent_with_eu_ai_act(shape="both")
    shaped = adapter.transform(canonical, persistent=persistent)
    layers = shaped.get("module_9", {}).get("eu_ai_act_layered", {}).get("layers", [])
    # Shape B has 2 layers; Shape A has 2 layers. Shape B's layer 1 has
    # name='AI Act Text' — the `layer` field should contain it.
    layer_displays = [layer["layer"] for layer in layers]
    assert any("AI Act Text" in disp for disp in layer_displays), (
        f"expected Shape B names in layer field, got {layer_displays}"
    )


def test_M9_layers_shape_A_key_humanised(adapter):
    """Shape A has only dict keys like 'layer_3_harmonised_standards'. The
    adapter must humanise this into a readable 'Layer 3 — Harmonised Standards'
    string so the renderer displays it correctly."""
    canonical = _minimal_canonical()
    persistent = _persistent_with_eu_ai_act(shape="A")
    shaped = adapter.transform(canonical, persistent=persistent)
    layers = shaped.get("module_9", {}).get("eu_ai_act_layered", {}).get("layers", [])
    assert layers, "expected Shape A to produce layers"
    displays = [layer["layer"] for layer in layers]
    # Must start with 'Layer N —' prefix and carry a humanised trailer.
    assert all(disp.startswith("Layer ") for disp in displays), (
        f"Shape A key humanisation failed, got {displays}"
    )
    # 'standards_vacuum_active' status should be bucketed as 'gap'.
    vacuum_layer = next(
        (l for l in layers if "Harmonised" in l["layer"]), None
    )
    assert vacuum_layer is not None, "harmonised_standards layer not found"
    assert vacuum_layer["status_class"] == "gap"


def test_M9_malformed_canonical_layers_raises(adapter):
    """If canonical module_9.eu_ai_act_layered.layers is a non-list, fail-loud
    with PersistentMergeError — do not silently render garbage."""
    canonical = _minimal_canonical()
    canonical["module_9"] = {
        "eu_ai_act_layered": {"layers": "this should have been a list"}
    }
    with pytest.raises(PersistentMergeError):
        adapter.transform(canonical, persistent={})


def test_M9_malformed_persistent_layers_raises(adapter):
    """If persistent eu_ai_act_tracker.layers is not dict/list, fail-loud."""
    canonical = _minimal_canonical()
    persistent = {
        "eu_ai_act_tracker": {"layers": "garbage"},
    }
    with pytest.raises(PersistentMergeError):
        adapter.transform(canonical, persistent=persistent)


def test_M9_empty_persistent_yields_empty_layers(adapter):
    """No persistent EU AI Act data + empty canonical → layers: []. Must NOT
    raise and must NOT emit undefineds."""
    canonical = _minimal_canonical()
    shaped = adapter.transform(canonical, persistent={})
    layered = shaped.get("module_9", {}).get("eu_ai_act_layered", {})
    assert layered.get("layers") == []


# ---------------------------------------------------------------------------
# country_grid — §27-L persistent-backed
# ---------------------------------------------------------------------------


def _persistent_with_country_grid() -> dict:
    return {
        "country_grid_status": {
            "last_updated": "2026-04-10",
            "jurisdictions": [
                {
                    "jurisdiction": "EU",
                    "binding_law": "AI Act (curated persistent text)",
                    "status_icon": "\U0001f7e1",
                    "last_updated": "2026-04-01",
                },
                {
                    "jurisdiction": "UK",
                    "binding_law": "No binding AI law; AISI monitoring",
                    "status_icon": "\U0001f7e0",
                    "last_updated": "2026-04-01",
                },
            ],
        }
    }


def test_country_grid_empty_synth_carries_persistent(adapter):
    """Rule 2: empty canonical country_grid → persistent baseline rendered."""
    canonical = _minimal_canonical()  # no country_grid key
    persistent = _persistent_with_country_grid()
    shaped = adapter.transform(canonical, persistent=persistent)
    grid = shaped.get("country_grid", [])
    assert len(grid) >= 2, f"expected persistent floor in country_grid, got {len(grid)}"
    juris = {row["jurisdiction"] for row in grid}
    assert "EU" in juris and "UK" in juris


def test_country_grid_row_has_renderer_keys(adapter):
    canonical = _minimal_canonical()
    persistent = _persistent_with_country_grid()
    shaped = adapter.transform(canonical, persistent=persistent)
    grid = shaped.get("country_grid", [])
    for i, row in enumerate(grid):
        missing = COUNTRY_GRID_REQUIRED_KEYS - set(row.keys())
        assert not missing, f"country_grid row {i} missing keys: {missing}"
        for k in COUNTRY_GRID_REQUIRED_KEYS:
            assert row[k] is not None, f"country_grid row {i}.{k} is None"


def test_country_grid_persistent_binding_law_preserved(adapter):
    """Persistent `binding_law` is curated text. Synth `signal` (news items)
    must NOT overwrite persistent binding_law for existing jurisdictions.
    This is the second half of the Issue 4 M9 bug — synth was writing
    news headlines into what should have been a stable baseline column.
    """
    canonical = _minimal_canonical()
    canonical["country_grid"] = [
        {
            "jurisdiction": "EU",
            "signal": "OpenAI closes $852B round (this is news, not law)",
            "change_flag": "\u26a0\ufe0f",
        }
    ]
    persistent = _persistent_with_country_grid()
    shaped = adapter.transform(canonical, persistent=persistent)
    grid = shaped.get("country_grid", [])
    eu_row = next((r for r in grid if r["jurisdiction"] == "EU"), None)
    assert eu_row is not None
    # Persistent curated binding_law must survive the merge.
    assert "curated" in eu_row["binding_law"], (
        f"synth 'signal' overwrote persistent binding_law: {eu_row['binding_law']!r}"
    )
    # But change_flag from synth should have been applied.
    assert eu_row["change_flag"] == "\u26a0\ufe0f"


def test_country_grid_synth_adds_new_jurisdiction(adapter):
    """A synth-only jurisdiction (not in persistent) gets appended with its
    `signal` used as the binding_law seed."""
    canonical = _minimal_canonical()
    canonical["country_grid"] = [
        {
            "jurisdiction": "Japan",
            "signal": "METI soft-law guidelines; no binding framework",
            "status_icon": "\U0001f7e0",
        }
    ]
    persistent = _persistent_with_country_grid()
    shaped = adapter.transform(canonical, persistent=persistent)
    grid = shaped.get("country_grid", [])
    jp = next((r for r in grid if r["jurisdiction"] == "Japan"), None)
    assert jp is not None, "Japan not appended from synth"
    assert "METI" in jp["binding_law"], "signal not seeded as binding_law"


def test_country_grid_malformed_raises(adapter):
    """Rule 5: synth country_grid as dict (not list) → PersistentMergeError."""
    canonical = _minimal_canonical()
    canonical["country_grid"] = {"oops": "should be list"}
    persistent = _persistent_with_country_grid()
    with pytest.raises(PersistentMergeError):
        adapter.transform(canonical, persistent=persistent)


if __name__ == "__main__":
    # Allow running without pytest for quick checks.
    sys.exit(pytest.main([__file__, "-v"]))

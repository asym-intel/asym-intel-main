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


if __name__ == "__main__":
    # Allow running without pytest for quick checks.
    sys.exit(pytest.main([__file__, "-v"]))

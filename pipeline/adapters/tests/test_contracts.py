"""Adapter contract tests.

Run with: pytest -q pipeline/adapters/tests/test_contracts.py
Or standalone:  python -m pipeline.adapters.tests.test_contracts

Goals:
  1. Registry returns a usable adapter instance for (monitor, target).
  2. Adapter rejects an unknown canonical schema_version (fail-loud).
  3. Adapter output is JSON-serialisable.
  4. Every emitted module/item carries the keys the Ramparts renderer
     reads, with string fallbacks — nothing should stringify as 'undefined'.
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


if __name__ == "__main__":
    # Allow running without pytest for quick checks.
    sys.exit(pytest.main([__file__, "-v"]))

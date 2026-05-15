"""
pipeline/engine/test_prompt_state_injection.py

pytest harness for render_stored_state_inventory.

Runs the 7 built-in tests from the module's _tests() function plus
structural assertions about the public API surface.

Sprint-7 Phase 1 — BRIEF §4 acceptance criterion C1: pytest passes ≥5 unit tests.
"""

import pathlib
import sys

# Ensure pipeline/engine is importable from both CI and local contexts
_ENGINE_DIR = pathlib.Path(__file__).resolve().parent
_PIPELINE_DIR = _ENGINE_DIR.parent
_REPO_ROOT = _PIPELINE_DIR.parent
for _p in [str(_ENGINE_DIR), str(_PIPELINE_DIR), str(_REPO_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pipeline.engine.prompt_state_injection import (
    render_stored_state_inventory,
    _tests,
)


def test_all_builtin():
    """Run all 7 built-in unit tests from prompt_state_injection._tests()."""
    _tests()


def test_public_api_returns_string():
    """render_stored_state_inventory always returns a str."""
    import tempfile, json
    with tempfile.TemporaryDirectory() as tmpdir:
        td = pathlib.Path(tmpdir)
        schema = {"arrays": {"x": {"key_field": "id", "key_constraint": {"pattern": "^X-\\d{3}$"}}}}
        (td / "s.json").write_text(json.dumps(schema))
        (td / "p.json").write_text(json.dumps({"x": [{"id": "X-001"}]}))
        result = render_stored_state_inventory("t", "test", td / "p.json", td / "s.json")
        assert isinstance(result, str)
        assert len(result) > 0


def test_header_always_present():
    """Header block is always present regardless of content."""
    import tempfile, json
    with tempfile.TemporaryDirectory() as tmpdir:
        td = pathlib.Path(tmpdir)
        (td / "s.json").write_text(json.dumps({"arrays": {}}))
        (td / "p.json").write_text(json.dumps({}))
        result = render_stored_state_inventory("t", "test", td / "p.json", td / "s.json")
        assert "## STORED-STATE INVENTORY" in result


def test_deterministic():
    """Same inputs always produce identical output."""
    import tempfile, json
    with tempfile.TemporaryDirectory() as tmpdir:
        td = pathlib.Path(tmpdir)
        schema = {"arrays": {"arr": {"key_field": "id", "key_constraint": {"pattern": "^A-\\d{3}$"}}}}
        state = {"arr": [{"id": "A-002"}, {"id": "A-001"}]}
        (td / "s.json").write_text(json.dumps(schema))
        (td / "p.json").write_text(json.dumps(state))
        r1 = render_stored_state_inventory("t", "mon", td / "p.json", td / "s.json")
        r2 = render_stored_state_inventory("t", "mon", td / "p.json", td / "s.json")
        assert r1 == r2, "Output must be deterministic"


def test_no_side_effects(tmp_path):
    """Function does not write any files."""
    import json
    schema = {"arrays": {"arr": {"key_field": "id", "key_constraint": {"pattern": "^B-\\d{3}$"}}}}
    state = {"arr": [{"id": "B-001"}]}
    (tmp_path / "s.json").write_text(json.dumps(schema))
    (tmp_path / "p.json").write_text(json.dumps(state))
    files_before = set(tmp_path.iterdir())
    render_stored_state_inventory("t", "mon", tmp_path / "p.json", tmp_path / "s.json")
    files_after = set(tmp_path.iterdir())
    assert files_before == files_after, "Function must not create or modify files"

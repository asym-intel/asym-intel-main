#!/usr/bin/env python3
"""
pipeline/engine/prompt_state_injection.py

Engine helper: render a STORED-STATE INVENTORY block for prompt injection.

Consumed by Phase 2a/b/c Executors who wire it into ESA, GMM, and SCEM
interpreter synthesiser runners. The rendered block is prepended to the
interpreter prompt so the LLM can reuse existing stored identifiers and
mint new ones using the schema-declared pattern — preventing key-scheme
divergence (the Class A `apply_failed_disjoint_key_scheme` defect).

Public API
----------
render_stored_state_inventory(
    abbr:                  str,
    monitor_slug:          str,
    persistent_state_path: pathlib.Path,
    arrays_schema_path:    pathlib.Path,
) -> str

Returns a markdown block of shape:

    ## STORED-STATE INVENTORY (read before emitting any patch identifiers)

    You MUST reuse existing identifiers from this inventory when proposing
    updates to existing items. Only mint NEW identifiers (using the
    documented pattern) when proposing genuinely new items.

    ### eu_legislation_tracker  (key_field: id, pattern: ^LEG-\\d{3}$)
    Stored identifiers: LEG-001, LEG-002, ..., LEG-012
    Next available: LEG-013

    ### state_capture_cases  (key_field: country, constraint: ISO-3166-1 alpha-2 enum)
    Stored identifiers: HU, GE, SK, RS, CZ, AT, CY
    Add new entries using the ISO-3166-1 alpha-2 code only.

Authority
---------
Sprint-7 Phase 1 — BRIEF-SPRINT-7-INTERPRETER-PROMPT-STATE-INJECTION §4 Phase 1.
Acceptance criteria C1: this module exists with the API above; pytest passes ≥5 unit tests.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any, Optional

__all__ = ["render_stored_state_inventory"]

_HEADER = """\
## STORED-STATE INVENTORY (read before emitting any patch identifiers)

You MUST reuse existing identifiers from this inventory when proposing \
updates to existing items. Only mint NEW identifiers (using the documented \
pattern) when proposing genuinely new items.\
"""

_NO_ARRAYS_NOTE = (
    "\n\n_(No array declarations found in persistent-state schema — "
    "no identifier constraints to enforce.)_"
)

_EMPTY_STATE_NOTE_FMT = (
    "\n\n_(persistent-state file not found or empty for {monitor_slug} — "
    "mint new identifiers using the schema patterns below.)_"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_stored_state_inventory(
    abbr: str,
    monitor_slug: str,
    persistent_state_path: pathlib.Path,
    arrays_schema_path: pathlib.Path,
) -> str:
    """Render a deterministic markdown block to prepend to an interpreter prompt.

    Gives the LLM a tabular view of the currently stored array keys plus
    the schema-locked key_constraint pattern, preventing key-scheme
    divergence (the Class A `apply_failed_disjoint_key_scheme` defect).

    Parameters
    ----------
    abbr:
        Short monitor abbreviation, e.g. ``"esa"``, ``"gmm"``, ``"scem"``.
        Used for log messages only — does not affect output.
    monitor_slug:
        Human-readable monitor slug for error messages, e.g.
        ``"european-strategic-autonomy"``.
    persistent_state_path:
        Absolute path to the monitor's ``persistent-state.json``.
        Graceful: returns an empty-inventory block if the file is missing.
    arrays_schema_path:
        Absolute path to the monitor's ``persistent-state-schema.json``.
        Graceful: returns an inventory with no pattern hints if missing.

    Returns
    -------
    str
        A single markdown string (no side effects, deterministic).
        Always begins with ``## STORED-STATE INVENTORY …``.
    """
    arrays_schema = _load_arrays_schema(arrays_schema_path)
    persistent_state = _load_persistent_state(persistent_state_path)

    if not arrays_schema:
        return _HEADER + _NO_ARRAYS_NOTE

    sections: list[str] = []

    if persistent_state is None:
        # State file missing: note + pattern hints only
        header_note = _EMPTY_STATE_NOTE_FMT.format(monitor_slug=monitor_slug)
        for array_key, decl in arrays_schema.items():
            sections.append(_render_section(array_key, decl, stored_values=[]))
        return _HEADER + header_note + "\n\n" + "\n\n".join(sections)

    for array_key, decl in arrays_schema.items():
        stored_values = _resolve_stored_values(
            persistent_state, array_key, decl.get("key_field", "id")
        )
        sections.append(_render_section(array_key, decl, stored_values))

    body = "\n\n".join(sections) if sections else "(no arrays declared)"
    return _HEADER + "\n\n" + body


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_arrays_schema(path: pathlib.Path) -> dict[str, Any]:
    """Load the ``arrays`` block from the persistent-state schema.

    Returns an empty dict if the file is missing or malformed.
    """
    p = pathlib.Path(path)
    if not p.exists():
        _warn(f"arrays_schema_path not found: {p}")
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _warn(f"Could not parse arrays_schema at {p}: {exc}")
        return {}
    arrays_block = raw.get("arrays", {})
    if not isinstance(arrays_block, dict):
        _warn(f"'arrays' block is not a dict in {p}")
        return {}
    return arrays_block


def _load_persistent_state(path: pathlib.Path) -> Optional[dict[str, Any]]:
    """Load persistent-state JSON.

    Returns None if the file is missing (graceful); raises nothing.
    Returns an empty dict if the file exists but is malformed.
    """
    p = pathlib.Path(path)
    if not p.exists():
        _warn(f"persistent_state_path not found: {p}")
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _warn(f"Could not parse persistent_state at {p}: {exc}")
        return {}
    if not isinstance(raw, dict):
        _warn(f"persistent_state root is not a dict in {p}")
        return {}
    return raw


def _resolve_stored_values(
    state: dict[str, Any],
    array_key: str,
    key_field: str,
) -> list[str]:
    """Extract existing key-field values from a persistent-state array.

    Handles two state shapes:
    - Top-level array: ``state[array_key]`` is a list of dicts.
    - Nested path with ``'.'``: ``state["module_13"]["items"]`` via
      ``array_key = "module_13.items"``.
    - Nested dict of actor → list: used by ``active_actor_campaigns``
      in ESA where items are keyed by actor under a top-level dict.

    Returns a sorted list of unique string values of ``key_field``.
    """
    target = _resolve_path(state, array_key)

    if target is None:
        return []

    items: list[dict[str, Any]] = []

    if isinstance(target, list):
        items = [i for i in target if isinstance(i, dict)]
    elif isinstance(target, dict):
        # Dict of actor → list-of-items  (e.g. ESA active_actor_campaigns)
        for v in target.values():
            if isinstance(v, list):
                items.extend(i for i in v if isinstance(i, dict))
            elif isinstance(v, dict):
                # Actor block may contain a 'campaigns' sub-list
                nested = v.get("campaigns") or v.get("items") or []
                if isinstance(nested, list):
                    items.extend(i for i in nested if isinstance(i, dict))

    values: list[str] = []
    for item in items:
        val = item.get(key_field)
        if val is not None:
            values.append(str(val))

    # Sort: prefer numeric-suffix sort for ``XX-NNN``-style IDs
    return sorted(set(values), key=_sort_key)


def _resolve_path(obj: Any, dotted_key: str) -> Any:
    """Walk a dotted path through nested dicts, returning None if missing."""
    parts = dotted_key.split(".")
    current = obj
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    return current


def _render_section(
    array_key: str,
    decl: dict[str, Any],
    stored_values: list[str],
) -> str:
    """Render one ``###`` section for a single array declaration."""
    key_field = decl.get("key_field", "id")
    constraint = decl.get("key_constraint", {})
    pattern = constraint.get("pattern")
    enum = constraint.get("enum")

    # --- Header line ---
    if pattern:
        constraint_hint = f"pattern: {pattern}"
    elif enum:
        constraint_hint = f"ISO-3166-1 alpha-2 enum" if _is_iso_enum(enum) else f"enum: {', '.join(str(e) for e in enum[:6])}{'…' if len(enum) > 6 else ''}"
    else:
        constraint_hint = "no constraint declared"

    header = f"### {array_key}  (key_field: {key_field}, {constraint_hint})"

    # --- Stored identifiers line ---
    if stored_values:
        ids_str = ", ".join(stored_values)
        stored_line = f"Stored identifiers: {ids_str}"
    else:
        stored_line = "Stored identifiers: (none)"

    # --- Next-available / enum hint ---
    if pattern and stored_values:
        next_id = _compute_next_id(pattern, stored_values)
        if next_id:
            action_line = f"Next available: {next_id}"
        else:
            action_line = f"Mint new identifiers using pattern: {pattern}"
    elif pattern and not stored_values:
        action_line = f"Mint first identifier using pattern: {pattern}"
    elif enum:
        action_line = (
            "Add new entries using the ISO-3166-1 alpha-2 code only."
            if _is_iso_enum(enum)
            else f"Valid values: {', '.join(str(e) for e in enum)}"
        )
    else:
        action_line = f"Mint new identifiers using key_field: {key_field}"

    return "\n".join([header, stored_line, action_line])


def _compute_next_id(pattern: str, stored_values: list[str]) -> Optional[str]:
    """Compute the next-available identifier for integer-suffixed patterns.

    Handles patterns of the shape ``^PREFIX-\\d{N}$`` (one prefix segment
    separated by a hyphen before the numeric suffix), e.g.
    ``^LEG-\\d{3}$`` → next of [LEG-001, LEG-002] is ``LEG-003``.

    Returns None if the pattern is not integer-suffixed or if no stored
    values match the pattern.  Date-like patterns (``\\d{4}-\\d{2}-\\d{2}``)
    are explicitly excluded — date sequences are append-only by calendar and
    computing "next date" is not meaningful here.
    """
    # Exclude ISO-date-like patterns: two or more fixed-width digit groups
    # separated by hyphens (YYYY-MM-DD shape)
    if re.search(r"\\d\{\d+\}.*-.*\\d\{\d+\}", pattern):
        return None

    # Extract a numeric-suffix format: PREFIX-NNN where N is digit-run
    suffix_match = re.search(r"\\d\{(\d+)\}", pattern)
    if not suffix_match:
        # No fixed-width digit group → can't compute next
        # Try variable-length digit run: \\d+
        if r"\d+" not in pattern and r"\d{" not in pattern:
            return None
        # Determine prefix from stored values
        suffix_match_var = True
        zero_pad = None
    else:
        zero_pad = int(suffix_match.group(1))
        suffix_match_var = False

    # Find the prefix by looking at the first stored value that matches
    # the pattern structure: everything before the trailing digit block
    compiled = None
    try:
        # Compile the original regex for validation
        compiled = re.compile(pattern)
    except re.error:
        return None

    # Extract numeric suffix from each stored value
    nums: list[int] = []
    prefix_seen: Optional[str] = None

    for val in stored_values:
        if not compiled.fullmatch(val):
            continue
        # Find the last sequence of digits in the value
        m = re.search(r"(\D*?)(\d+)$", val)
        if m:
            if prefix_seen is None:
                prefix_seen = m.group(1)
            if m.group(1) == prefix_seen:
                nums.append(int(m.group(2)))

    if not nums or prefix_seen is None:
        return None

    next_num = max(nums) + 1
    if zero_pad is not None:
        return f"{prefix_seen}{str(next_num).zfill(zero_pad)}"
    else:
        return f"{prefix_seen}{next_num}"


def _is_iso_enum(enum: list) -> bool:
    """Heuristic: enum looks like ISO-3166-1 alpha-2 if ≥20 entries of 2 uppercase letters."""
    if len(enum) < 20:
        return False
    two_char = sum(1 for e in enum if isinstance(e, str) and len(e) == 2 and e.isupper())
    return two_char >= 20


def _sort_key(val: str):
    """Sort key that places numeric-suffix IDs in numeric order."""
    m = re.search(r"^(.*?)(\d+)$", val)
    if m:
        return (m.group(1), int(m.group(2)))
    return (val, 0)


def _warn(msg: str) -> None:
    print(f"[prompt_state_injection] WARN: {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Unit tests (run with pytest or python3 -m pytest)
# ---------------------------------------------------------------------------

def _tests():
    """In-module test suite — ≥5 tests as required by BRIEF §4 Phase 1.

    These tests are also picked up by pytest via the test file
    ``pipeline/engine/test_prompt_state_injection.py`` which imports this
    module and calls ``run_tests()``.
    """
    import tempfile, os

    def write_json(path, obj):
        pathlib.Path(path).write_text(json.dumps(obj), encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmpdir:
        td = pathlib.Path(tmpdir)

        # ------------------------------------------------------------------
        # Test 1: empty persistent-state → empty inventory block
        # ------------------------------------------------------------------
        schema_1 = {
            "arrays": {
                "my_array": {
                    "key_field": "id",
                    "key_constraint": {"pattern": "^ITEM-\\d{3}$"},
                }
            }
        }
        state_1 = {}
        sp1 = td / "schema1.json";  write_json(sp1, schema_1)
        ps1 = td / "state1.json";   write_json(ps1, state_1)
        result1 = render_stored_state_inventory("t1", "test-monitor-1", ps1, sp1)
        assert "## STORED-STATE INVENTORY" in result1, "Test 1: header missing"
        assert "Stored identifiers: (none)" in result1, "Test 1: should report no stored IDs"
        assert "Mint first identifier" in result1, "Test 1: should hint first identifier"
        print("  TEST 1 PASS: empty persistent-state → empty inventory")

        # ------------------------------------------------------------------
        # Test 2: populated persistent-state + pattern → stored keys + next-available
        # ------------------------------------------------------------------
        schema_2 = {
            "arrays": {
                "eu_legislation_tracker": {
                    "key_field": "id",
                    "key_constraint": {"pattern": "^LEG-\\d{3}$"},
                }
            }
        }
        state_2 = {
            "eu_legislation_tracker": [
                {"id": "LEG-001", "title": "AI Act"},
                {"id": "LEG-003", "title": "DSA"},
                {"id": "LEG-002", "title": "DMA"},
            ]
        }
        sp2 = td / "schema2.json";  write_json(sp2, schema_2)
        ps2 = td / "state2.json";   write_json(ps2, state_2)
        result2 = render_stored_state_inventory("t2", "test-monitor-2", ps2, sp2)
        assert "LEG-001" in result2 and "LEG-002" in result2 and "LEG-003" in result2, \
            "Test 2: stored IDs not rendered"
        assert "LEG-004" in result2, f"Test 2: next-available LEG-004 missing; got: {result2}"
        assert "pattern: ^LEG-\\d{3}$" in result2, "Test 2: pattern hint missing"
        print("  TEST 2 PASS: populated state + pattern → stored keys + next-available")

        # ------------------------------------------------------------------
        # Test 3: missing schema file → graceful inventory without pattern hint
        # ------------------------------------------------------------------
        ps3 = td / "state3.json";   write_json(ps3, {"my_array": [{"id": "X-001"}]})
        result3 = render_stored_state_inventory("t3", "test-monitor-3", ps3, td / "nonexistent.json")
        assert "## STORED-STATE INVENTORY" in result3, "Test 3: header missing"
        assert "No array declarations" in result3, "Test 3: should report no array declarations"
        print("  TEST 3 PASS: missing schema → graceful inventory without pattern hint")

        # ------------------------------------------------------------------
        # Test 4: enum-constraint array (ISO-3166-1 alpha-2) → enum listed
        # ------------------------------------------------------------------
        eu_enum = [
            "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
            "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
            "NL", "PL", "PT", "RO", "SE", "SI", "SK", "GB", "UA"
        ]
        schema_4 = {
            "arrays": {
                "state_capture_cases": {
                    "key_field": "country",
                    "key_constraint": {"enum": eu_enum},
                }
            }
        }
        state_4 = {
            "state_capture_cases": [
                {"country": "HU", "score": 8},
                {"country": "PL", "score": 5},
            ]
        }
        sp4 = td / "schema4.json";  write_json(sp4, schema_4)
        ps4 = td / "state4.json";   write_json(ps4, state_4)
        result4 = render_stored_state_inventory("t4", "test-monitor-4", ps4, sp4)
        assert "HU" in result4 and "PL" in result4, "Test 4: stored country codes missing"
        assert "ISO-3166-1 alpha-2" in result4, "Test 4: ISO enum hint missing"
        print("  TEST 4 PASS: enum-constraint array → ISO hint rendered")

        # ------------------------------------------------------------------
        # Test 5: mixed-shape inventory across 3+ arrays → all rendered
        # ------------------------------------------------------------------
        schema_5 = {
            "arrays": {
                "legislation": {
                    "key_field": "id",
                    "key_constraint": {"pattern": "^LEG-\\d{3}$"},
                },
                "countries": {
                    "key_field": "country",
                    "key_constraint": {"enum": ["AT", "BE", "BG", "CY", "CZ", "DE",
                                               "DK", "EE", "ES", "FI", "FR", "GR",
                                               "HR", "HU", "IE", "IT", "LT", "LU",
                                               "LV", "MT", "NL", "PL"]},
                },
                "alerts": {
                    "key_field": "alert_id",
                    "key_constraint": {"pattern": "^ALERT-\\d{3}$"},
                },
            }
        }
        state_5 = {
            "legislation": [{"id": "LEG-001"}, {"id": "LEG-002"}],
            "countries": [{"country": "HU"}, {"country": "DE"}],
            "alerts": [{"alert_id": "ALERT-001"}, {"alert_id": "ALERT-002"}],
        }
        sp5 = td / "schema5.json";  write_json(sp5, schema_5)
        ps5 = td / "state5.json";   write_json(ps5, state_5)
        result5 = render_stored_state_inventory("t5", "test-monitor-5", ps5, sp5)
        assert "### legislation" in result5, "Test 5: legislation section missing"
        assert "### countries" in result5, "Test 5: countries section missing"
        assert "### alerts" in result5, "Test 5: alerts section missing"
        assert "LEG-003" in result5, "Test 5: next-available LEG-003 missing"
        assert "ALERT-003" in result5, "Test 5: next-available ALERT-003 missing"
        print("  TEST 5 PASS: mixed inventory across 3 arrays → all rendered")

        # ------------------------------------------------------------------
        # Test 6: missing persistent-state file → graceful with pattern hints
        # ------------------------------------------------------------------
        schema_6 = {
            "arrays": {
                "gaps_register": {
                    "key_field": "gap_id",
                    "key_constraint": {"pattern": "^GAP-\\d{3}$"},
                }
            }
        }
        sp6 = td / "schema6.json";  write_json(sp6, schema_6)
        result6 = render_stored_state_inventory("t6", "test-monitor-6",
                                                 td / "missing_state.json", sp6)
        assert "## STORED-STATE INVENTORY" in result6, "Test 6: header missing"
        assert "persistent-state file not found" in result6, "Test 6: missing-state note missing"
        assert "### gaps_register" in result6, "Test 6: array section missing despite missing state"
        print("  TEST 6 PASS: missing persistent-state → graceful with pattern hints")

        # ------------------------------------------------------------------
        # Test 7: nested dict of actor → list (ESA active_actor_campaigns shape)
        # ------------------------------------------------------------------
        schema_7 = {
            "arrays": {
                "active_actor_campaigns": {
                    "key_field": "id",
                    "key_constraint": {"pattern": "^[A-Z]{2,3}-\\d{3}$"},
                }
            }
        }
        state_7 = {
            "active_actor_campaigns": {
                "RU": [{"id": "RU-001", "name": "InfoOp"}, {"id": "RU-002", "name": "Cyber"}],
                "CN": [{"id": "CN-001", "name": "BRI"}],
                "US": [{"id": "US-001", "name": "SandA"}],
            }
        }
        sp7 = td / "schema7.json";  write_json(sp7, schema_7)
        ps7 = td / "state7.json";   write_json(ps7, state_7)
        result7 = render_stored_state_inventory("t7", "test-monitor-7", ps7, sp7)
        assert "RU-001" in result7, "Test 7: RU-001 missing"
        assert "CN-001" in result7, "Test 7: CN-001 missing"
        assert "US-001" in result7, "Test 7: US-001 missing"
        print("  TEST 7 PASS: nested actor-dict → all campaign IDs extracted")

    print("\nAll tests passed.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="render_stored_state_inventory CLI smoke test")
    parser.add_argument("--run-tests", action="store_true", help="Run built-in unit tests")
    parser.add_argument("--persistent-state", type=pathlib.Path)
    parser.add_argument("--arrays-schema",    type=pathlib.Path)
    parser.add_argument("--abbr",             default="cli")
    parser.add_argument("--monitor-slug",     default="cli-monitor")
    args = parser.parse_args()

    if args.run_tests:
        _tests()
    elif args.persistent_state and args.arrays_schema:
        print(render_stored_state_inventory(
            abbr=args.abbr,
            monitor_slug=args.monitor_slug,
            persistent_state_path=args.persistent_state,
            arrays_schema_path=args.arrays_schema,
        ))
    else:
        parser.print_help()

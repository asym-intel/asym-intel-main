"""
Regression tests for the AIM (`ai-governance`) `module_2` (Model Frontier)
persistent-state scaffold.

Context (root cause):
- Methodology is canonical (interpreter-prompt v2.4 Rule 4): module_2.models[]
  is the Model Frontier registry. Interpreter emits patches against it.
- Baseline 2026-04-28 (`baseline_run_id agm-2026-04-28`) omitted module_2.
- Curator surfaced the gap as AGM-GAP-002 in `gaps_register` (2026-04-28).
- AIM 2026-05-05 force-replay (`apply-debug-2026-05-05.json`) failed with
  `applier_rejection_reason: target_missing:module_2`, blocking publication
  with `hold_reason: patch_apply_failed`.

This test pins the scaffold added 2026-05-05 so a future schema-cleanup
sweep cannot silently drop it and re-introduce the blocker.

The scaffold lives in `static/monitors/ai-governance/data/persistent-state.json`.
"""

from __future__ import annotations

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PERSISTENT_STATE_PATH = (
    REPO_ROOT
    / "static"
    / "monitors"
    / "ai-governance"
    / "data"
    / "persistent-state.json"
)
APPLY_LATEST_PATH = (
    REPO_ROOT
    / "pipeline"
    / "monitors"
    / "ai-governance"
    / "applied"
    / "apply-latest.json"
)


def _load_state() -> dict:
    return json.loads(PERSISTENT_STATE_PATH.read_text(encoding="utf-8"))


# ── Scaffold presence ──────────────────────────────────────────────────────


def test_module_2_top_level_key_present():
    state = _load_state()
    assert "module_2" in state, (
        "module_2 must remain a top-level key in persistent-state.json. "
        "Removing it re-opens AIM applier `target_missing:module_2`."
    )


def test_module_2_has_models_array():
    state = _load_state()
    models = state["module_2"].get("models")
    assert isinstance(models, list), (
        "module_2.models must be a list (per interpreter-schema v1.0). "
        "Engine path-resolver indexes module_2.models[<lab>/<name>] as "
        "list-of-objects."
    )


def test_module_2_in_required_modules():
    state = _load_state()
    required = state["_meta"].get("required_modules") or []
    assert "module_2" in required, (
        "module_2 must be listed in _meta.required_modules so module-level "
        "absence audits (check_module_provenance) recognise it."
    )


def test_module_2_has_scaffold_provenance():
    """Scaffold entry must record why it was bootstrapped, so a future
    operator can trace it back to the methodology gap closure."""
    state = _load_state()
    m2 = state["module_2"]
    assert "scaffold_basis" in m2 and "AGM-GAP-002" in m2["scaffold_basis"]
    vh = m2.get("version_history") or []
    assert vh, "module_2.version_history must be non-empty (engine appends here)."
    first = vh[0]
    assert first.get("change") == "scaffold_create"
    assert first.get("patch_id") == "scaffold-module_2-2026-05-05"


def test_gaps_register_agm_gap_002_resolved():
    state = _load_state()
    gaps = state.get("gaps_register") or []
    target = next((g for g in gaps if g.get("gap_id") == "AGM-GAP-002"), None)
    assert target is not None, "AGM-GAP-002 must remain in gaps_register"
    assert target.get("status") == "resolved"
    assert target.get("date_resolved") == "2026-05-05"
    assert "module_2" in (target.get("resolution") or "")


# ── Reproducer for the original target_missing failure ─────────────────────


def test_reproduces_failing_target_kb_path_resolution():
    """
    Reproduce the AIM applier path-resolution against the seeded entry.

    The Interpreter emitted patch `_unstamped_0` with
    `target_kb_path: "module_2.models[OpenAI/GPT-5.5]"`. Pre-scaffold, the
    applier's `_resolve_path` fails at the first segment with
    `target_missing:module_2`. Post-scaffold, the path resolves and the
    OpenAI/GPT-5.5 entry is locatable by the engine's identity-match
    (`lab + "/" + name` per AGM module_2 convention).

    We don't import the engine here (it lives in asym-intel-internal); we
    re-implement the minimum identity-match to assert reachability.
    """
    state = _load_state()
    models = state["module_2"]["models"]

    target_id = "OpenAI/GPT-5.5"

    # Mirror the engine's `_identity_match` rule for module_2.models:
    # `entry["lab"] + "/" + entry["name"]` must equal the bracket payload.
    def _identity_match(entry: dict, payload: str) -> bool:
        if not isinstance(entry, dict):
            return False
        lab = entry.get("lab") or ""
        name = entry.get("name") or ""
        return f"{lab}/{name}" == payload

    matches = [m for m in models if _identity_match(m, target_id)]
    assert len(matches) == 1, (
        f"Expected exactly one module_2.models entry to match "
        f"'{target_id}'; got {len(matches)}. The 2026-05-05 scaffold seeds "
        f"this entry from interpret-latest.json so the AIM force-replay "
        f"clears `target_missing:module_2`."
    )
    entry = matches[0]
    assert entry.get("tier") == 1
    assert entry.get("released") == "2026-04-23"


# ── Scaffold is consistent with the live interpret artefact ───────────────


def test_scaffold_seed_matches_interpret_latest():
    """
    The scaffold seed for OpenAI/GPT-5.5 was lifted verbatim from
    `interpret-latest.json` module_2.models[0] (cycle agm-2026-05-05). This
    test asserts that the structural body the methodology emitted matches
    what's now persistent — so the next force-replay's patch update against
    `module_2.models[OpenAI/GPT-5.5]` is a no-op identity overwrite rather
    than a state mutation.
    """
    state = _load_state()
    interpret_latest_path = (
        REPO_ROOT
        / "pipeline"
        / "monitors"
        / "ai-governance"
        / "synthesised"
        / "interpret-latest.json"
    )
    interpret = json.loads(interpret_latest_path.read_text(encoding="utf-8"))
    interp_models = (interpret.get("module_2") or {}).get("models") or []
    interp_target = next(
        (m for m in interp_models if m.get("lab") == "OpenAI" and m.get("name") == "GPT-5.5"),
        None,
    )
    assert interp_target is not None, (
        "interpret-latest.json must still carry the OpenAI/GPT-5.5 model "
        "entry — if the methodology drops it, this test should be updated "
        "alongside removing the persistent-state scaffold seed."
    )

    persistent_target = next(
        (m for m in state["module_2"]["models"]
         if m.get("lab") == "OpenAI" and m.get("name") == "GPT-5.5"),
        None,
    )
    assert persistent_target is not None

    # Compare the methodology-defined body fields. We deliberately omit
    # operator-only fields the scaffold added (`first_seen_in_state`,
    # `scaffold_seed`).
    body_keys = ("name", "lab", "tier", "released", "headline", "asymmetric", "flag")
    for k in body_keys:
        assert persistent_target.get(k) == interp_target.get(k), (
            f"module_2.models[OpenAI/GPT-5.5].{k} drifted from "
            f"interpret-latest.json — scaffold seed must mirror interpreter."
        )


# ── Failure-mode regression: apply-latest still records the original bug ──


def test_apply_latest_documents_pre_fix_failure():
    """
    Sanity check: the pre-fix `apply-latest.json` (cycle 2026-05-05) records
    `target_missing:module_2` for `_unstamped_0`. This is the artefact this
    PR fixes. We assert it stays visible until a post-fix force-replay
    overwrites apply-latest.json — so the next replay is the *proof* the
    scaffold cleared the blocker, not a silent overwrite.
    """
    if not APPLY_LATEST_PATH.exists():
        return  # apply artefacts may be absent in some CI fixtures
    apply_latest = json.loads(APPLY_LATEST_PATH.read_text(encoding="utf-8"))
    failed = apply_latest.get("patches_apply_failed") or []
    if not failed:
        # Post-replay state — the fix has been validated end-to-end.
        return
    # Pre-replay state — the failure entry should be the documented one.
    module_2_failures = [
        f for f in failed
        if (f.get("target_kb_path") or "").startswith("module_2.")
    ]
    if module_2_failures:
        assert module_2_failures[0].get("applier_rejection_reason") == "target_missing:module_2", (
            "Pre-fix apply-latest.json must record the documented "
            "target_missing:module_2 failure. If the reason has changed, "
            "re-evaluate the root-cause analysis in this PR."
        )

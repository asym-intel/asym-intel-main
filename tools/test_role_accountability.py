"""
Tests for tools/role_accountability.py — role-accountability diagnostic for
commons monitor weekly cycles.

Pure in-memory + tmp_path fixtures. No network, no LLM calls, no real
publish/applier path. Each test seeds a minimal but realistic stage set and
asserts the classifier picks the correct first_failed_role + likely_fix_type.

Cases:
  1. Module with content → PASS / pass / none
  2. Empty module + null_cycle + provenance → PASS / data_absence / data_absence
  3. Empty module + material_change + manifest extractions + 0 claims
     → FAIL / interpreter_failure / prompt
  4. Empty module + non-empty structured_claims but none mapping to module
     → FAIL / allocator_failure / schema
  5. Missing reasoner-latest → FAIL / plumbing / plumbing
  6. apply-latest sha1 drift → FAIL / plumbing / plumbing
  7. Composer drop: interpret has content, claim_trace explicitly maps other
     module but not this one → FAIL / composer_failure / composer
  8. CLI text output + exit code on a tmp repo with one monitor
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from role_accountability import (  # noqa: E402
    classify_module,
    diagnose_cycle,
    main,
)


def _seed_monitor(repo_root: pathlib.Path,
                  slug: str,
                  *,
                  weekly: dict | None = None,
                  reasoner: dict | None = None,
                  interpret: dict | None = None,
                  review: dict | None = None,
                  compose: dict | None = None,
                  apply_artefact: dict | None = None,
                  ) -> pathlib.Path:
    """Write a minimal monitor stage set under repo_root."""
    base = repo_root / "pipeline" / "monitors" / slug
    (base / "weekly").mkdir(parents=True, exist_ok=True)
    (base / "reasoner").mkdir(parents=True, exist_ok=True)
    (base / "synthesised").mkdir(parents=True, exist_ok=True)
    (base / "applied").mkdir(parents=True, exist_ok=True)

    def _write(path: pathlib.Path, body: dict | None) -> None:
        if body is None:
            return
        path.write_text(json.dumps(body, indent=2), encoding="utf-8")

    _write(base / "weekly" / "weekly-latest.json", weekly)
    _write(base / "reasoner" / "reasoner-latest.json", reasoner)
    _write(base / "synthesised" / "interpret-latest.json", interpret)
    _write(base / "synthesised" / "review-latest.json", review)
    _write(base / "synthesised" / "compose-latest.json", compose)
    _write(base / "applied" / "apply-latest.json", apply_artefact)
    return base


def _fake_minimal_stages(slug: str = "test-monitor") -> dict:
    """Realistic-shaped stage payloads with no module rows yet.

    Keys match `_seed_monitor` kwargs: apply_artefact (not apply).
    """
    return {
        "weekly": {
            "_meta": {"monitor_slug": slug, "week_ending": "2026-05-02"},
            "weekly_developments": [{"id": "d1", "headline": "..."}],
            "open_findings": [],
        },
        "reasoner": {
            "_meta": {"monitor_slug": slug},
            "regulatory_milestone_updates": [{"id": "rm1"}],
            "risk_pattern_detections": [],
        },
        "interpret": {
            "_meta": {
                "schema_version": "test-interpret-v1.0",
                "monitor_slug": slug,
                "week_ending": "2026-05-02",
                "null_signal_week": False,
                "cycle_disposition": "material_change",
                "triple_extraction_manifest": {
                    "deterministic_extractions": 0,
                    "llm_fallback_extractions": 0,
                },
            },
            "structured_claims": [],
        },
        "review": {
            "_meta": {"monitor_slug": slug},
            "verdict": "publish-with-flags",
            "checks": [],
        },
        "compose": {
            "_meta": {"monitor_slug": slug},
            "weekly_brief_draft": "...",
            "claim_trace": [],
        },
        "apply_artefact": {
            "_meta": {"monitor_slug": slug},
            "inputs": {},
            # Default to held — most failure-class fixtures want the
            # classifier to attribute upstream, not flag publisher_failure.
            # Tests that exercise publisher-failed-open override this.
            "publication": {"ready_to_publish": False,
                             "hold_reason": "test_default_hold"},
        },
    }


# ── Case 1: populated module passes ────────────────────────────────────────

def test_populated_module_passes(tmp_path):
    s = _fake_minimal_stages()
    s["interpret"]["module_0"] = {
        "title": "Lead Signal",
        "body": "Real content with substance.",
    }
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    [m0] = cv.modules
    assert m0.status == "PASS"
    assert m0.first_failed_role == "pass"
    assert m0.likely_fix_type == "none"


# ── Case 2: explicit data_absence passes ───────────────────────────────────

def test_empty_with_null_cycle_provenance_is_data_absence(tmp_path):
    s = _fake_minimal_stages()
    s["interpret"]["_meta"]["cycle_disposition"] = "null_cycle"
    s["interpret"]["_meta"]["null_signal_week"] = True
    s["interpret"]["module_3"] = {
        "title": "Module 3",
        "items": [],
        "null_signal": True,
        "empty_reason": "no_material_content",
    }
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    [m3] = cv.modules
    assert m3.status == "PASS"
    assert m3.first_failed_role == "data_absence"
    assert m3.likely_fix_type == "data_absence"


# ── Case 3: AGM-signature interpreter drop ────────────────────────────────

def test_interpreter_drops_claims_in_material_cycle(tmp_path):
    """The AIM 2026-05-03 signature: manifest claims 50 extractions, but
    structured_claims[] is empty and modules are empty."""
    s = _fake_minimal_stages()
    s["interpret"]["_meta"]["triple_extraction_manifest"] = {
        "deterministic_extractions": 42,
        "llm_fallback_extractions": 8,
    }
    s["interpret"]["module_1"] = {
        "title": "Capability tier",
        "models": [],
        "null_signal": True,
        "empty_reason": "interpreter_no_signal",
    }
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    [m1] = cv.modules
    assert m1.status == "FAIL"
    assert m1.first_failed_role == "interpreter_failure"
    assert m1.likely_fix_type == "prompt"
    assert m1.confidence == "high"
    # Evidence must point at the manifest/claim-count contradiction.
    assert any("triple_extraction_manifest" in e for e in m1.evidence)
    assert any("structured_claims" in e for e in m1.evidence)


# ── Case 4: claims emitted but none reach this module ─────────────────────

def test_allocator_failure_when_claims_skip_module(tmp_path):
    s = _fake_minimal_stages()
    s["interpret"]["structured_claims"] = [
        {"claim_id": "c1", "module_key": "module_0", "evidence_id": "e1"},
        {"claim_id": "c2", "module_key": "module_0", "evidence_id": "e2"},
    ]
    s["interpret"]["module_0"] = {"title": "M0", "body": "content"}
    s["interpret"]["module_5"] = {"title": "M5", "items": []}
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    by_key = {m.module_key: m for m in cv.modules}
    assert by_key["module_0"].status == "PASS"
    m5 = by_key["module_5"]
    assert m5.status == "FAIL"
    assert m5.first_failed_role == "allocator_failure"
    assert m5.likely_fix_type == "schema"


# ── Case 5: missing reasoner-latest is plumbing ───────────────────────────

def test_missing_stage_reports_plumbing(tmp_path):
    s = _fake_minimal_stages()
    s["interpret"]["module_0"] = {"title": "x", "items": []}
    s["reasoner"] = None  # do not seed the reasoner stage at all
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    assert cv.plumbing_issues
    [m0] = cv.modules
    assert m0.status == "FAIL"
    assert m0.first_failed_role == "plumbing"
    assert m0.likely_fix_type == "plumbing"


# ── Case 6: apply-recorded sha1 drifts from on-disk interpret ─────────────

def test_sha1_drift_reports_plumbing(tmp_path):
    s = _fake_minimal_stages()
    s["interpret"]["module_0"] = {"title": "x", "body": "content"}
    base = _seed_monitor(tmp_path, "test-monitor", **s)

    # Compute the *real* sha1 of interpret-latest after seeding.
    interp_path = base / "synthesised" / "interpret-latest.json"
    real = hashlib.sha1(interp_path.read_bytes()).hexdigest()

    # Rewrite apply-latest with a DELIBERATELY WRONG sha1 to simulate the
    # applier having seen an older copy of interpret-latest.
    apply_path = base / "applied" / "apply-latest.json"
    apply_data = json.loads(apply_path.read_text())
    apply_data["inputs"] = {
        "interpret": {
            "path": "pipeline/monitors/test-monitor/synthesised/interpret-latest.json",
            "content_sha1": "0" * 40,
            "schema_version": "test-interpret-v1.0",
        },
    }
    apply_path.write_text(json.dumps(apply_data, indent=2))

    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    assert any("content_sha1 drift" in p for p in cv.plumbing_issues)
    assert real != "0" * 40  # sanity
    [m0] = cv.modules
    assert m0.first_failed_role == "plumbing"


# ── Case 7: composer drops a populated module ─────────────────────────────

def test_composer_drops_populated_module(tmp_path):
    """Composer schema with explicit module references in claim_trace —
    interpret has populated module but compose trace omits it."""
    s = _fake_minimal_stages()
    s["interpret"]["module_0"] = {"title": "M0", "body": "kept by composer"}
    s["interpret"]["module_1"] = {"title": "M1", "body": "DROPPED by composer"}
    s["compose"]["claim_trace"] = [
        {"module": "module_0", "trace_type": "structural"},
    ]
    _seed_monitor(tmp_path, "test-monitor", **s)
    cv = diagnose_cycle("test-monitor", repo_root=tmp_path)
    by = {m.module_key: m for m in cv.modules}
    assert by["module_0"].status == "PASS"
    m1 = by["module_1"]
    assert m1.status == "FAIL"
    assert m1.first_failed_role == "composer_failure"
    assert m1.likely_fix_type == "composer"


# ── Case 8: CLI text output + exit code ───────────────────────────────────

def test_cli_text_and_exit_code(tmp_path, capsys):
    s = _fake_minimal_stages()
    s["interpret"]["module_0"] = {"title": "x", "body": "content"}
    _seed_monitor(tmp_path, "test-monitor", **s)
    rc = main([
        "--monitor", "test-monitor",
        "--repo-root", str(tmp_path),
    ])
    assert rc == 0  # all-PASS
    out = capsys.readouterr().out
    assert "test-monitor" in out
    assert "module_0" in out
    assert "PASS" in out


def test_cli_json_emits_structured_record(tmp_path, capsys):
    s = _fake_minimal_stages()
    # Force interpreter_failure shape.
    s["interpret"]["_meta"]["triple_extraction_manifest"] = {
        "deterministic_extractions": 50,
        "llm_fallback_extractions": 0,
    }
    s["interpret"]["module_2"] = {"title": "x", "items": []}
    _seed_monitor(tmp_path, "test-monitor", **s)
    rc = main([
        "--monitor", "test-monitor",
        "--repo-root", str(tmp_path),
        "--json",
    ])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    [cycle] = payload["cycles"]
    [mod] = cycle["modules"]
    assert mod["module_key"] == "module_2"
    assert mod["first_failed_role"] == "interpreter_failure"
    assert mod["likely_fix_type"] == "prompt"


# ── Pure-function level: classify_module on hand-rolled inputs ────────────

def test_classify_module_publisher_failure_when_unprovenanced_published(tmp_path):
    """Publication marked ready_to_publish=True with empty unprovenanced
    module → publisher_failure (publisher gate failed open)."""
    interpret = {
        "_meta": {
            "monitor_slug": "x",
            "cycle_disposition": "material_change",
            "null_signal_week": False,
            "triple_extraction_manifest": {
                "deterministic_extractions": 0,
                "llm_fallback_extractions": 0,
            },
        },
        "structured_claims": [],
        "module_4": {"title": "M4", "items": []},  # empty + no provenance
    }
    apply_artefact = {"publication": {"ready_to_publish": True}}
    review = {"verdict": "publish-with-flags", "checks": []}
    verdict = classify_module(
        "module_4",
        interpret=interpret,
        review=review,
        compose={},
        apply_artefact=apply_artefact,
        weekly={},
        reasoner={"risk_pattern_detections": [{"id": "p1"}]},
        plumbing_issues=[],
    )
    assert verdict.first_failed_role == "publisher_failure"
    assert verdict.likely_fix_type == "publisher"


def test_classify_module_held_publication_attributes_upstream(tmp_path):
    """If publication is correctly held (ready_to_publish=False) on an
    empty unprovenanced module in a material cycle and no manifest
    extractions exist, attribution falls upstream to the reasoner —
    the publisher itself is doing its job, the interpreter had nothing to
    work with, and the reasoner had patterns."""
    interpret = {
        "_meta": {
            "monitor_slug": "x",
            "cycle_disposition": "material_change",
            "null_signal_week": False,
            "triple_extraction_manifest": {
                "deterministic_extractions": 0,
                "llm_fallback_extractions": 0,
            },
        },
        "structured_claims": [],
        "module_4": {"title": "M4", "items": []},
    }
    apply_artefact = {"publication": {"ready_to_publish": False,
                                       "hold_reason": "review_verdict:hold-for-review"}}
    review = {"verdict": "hold-for-review", "checks": []}
    verdict = classify_module(
        "module_4",
        interpret=interpret,
        review=review,
        compose={},
        apply_artefact=apply_artefact,
        weekly={},
        reasoner={"risk_pattern_detections": [{"id": "p1"}]},
        plumbing_issues=[],
    )
    assert verdict.status == "FAIL"
    assert verdict.first_failed_role == "reasoner_failure"
    assert verdict.likely_fix_type == "prompt"


def test_classify_module_collector_failure_when_reasoner_thin(tmp_path):
    """Material cycle, no manifest extractions, reasoner produces no
    pattern signals → collector_failure (likely under-collection)."""
    interpret = {
        "_meta": {
            "monitor_slug": "x",
            "cycle_disposition": "material_change",
            "null_signal_week": False,
            "triple_extraction_manifest": {
                "deterministic_extractions": 0,
                "llm_fallback_extractions": 0,
            },
        },
        "structured_claims": [],
        "module_4": {"title": "M4", "items": []},
    }
    apply_artefact = {"publication": {"ready_to_publish": False,
                                       "hold_reason": "test"}}
    verdict = classify_module(
        "module_4",
        interpret=interpret,
        review={"verdict": "hold-for-review", "checks": []},
        compose={},
        apply_artefact=apply_artefact,
        weekly={"weekly_developments": []},
        reasoner={},  # no pattern buckets at all → reasoner_is_thin
        plumbing_issues=[],
    )
    assert verdict.first_failed_role == "collector_failure"
    assert verdict.likely_fix_type == "prompt"

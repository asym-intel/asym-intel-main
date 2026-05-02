"""
Tests for publisher upstream publication-eligibility gate.

The gate reads pipeline/monitors/{slug}/applied/apply-latest.json and refuses
to publish when the upstream apply/review verdict says the cycle is not
ready (ready_to_publish=false, or hold-for-review/REJECT review verdict).

Live evidence motivating the fix: AIM apply-2026-05-02.json had
ready_to_publish=false / hold_reason="review_verdict:hold-for-review", but
publisher run 25256774146 still wrote static/monitors/ai-governance/data/
report-latest.json. This stage-contract break is what the gate closes.

Cases covered:
  1. ready_to_publish=false             → block, critical incident.
  2. ready_to_publish absent + review verdict hold-for-review → block.
  3. ready_to_publish absent + review verdict REJECT (legacy) → block.
  4. ready_to_publish=true              → permit, no incident.
  5. apply-latest.json absent           → permit, info incident
     (legacy monitors not yet on the apply pipeline).
  6. apply-latest.json malformed JSON   → permit, warning incident.
  7. apply-latest.json missing publication block → permit, warning incident.
  8. publish-with-flags + ready=true    → permit (matches AIM 2026-05-01).
  9. Real AIM 2026-05-02 fixture shape  → blocks (regression guard).

No network. Uses tmp_path for the apply artefact.
"""

import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from publisher import (  # noqa: E402
    load_publication_eligibility,
    check_publication_eligibility,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _write_apply(tmp_path: pathlib.Path, slug: str, payload) -> pathlib.Path:
    """Write `payload` (dict or raw string) to applied/apply-latest.json under tmp_path."""
    apply_dir = tmp_path / "pipeline" / "monitors" / slug / "applied"
    apply_dir.mkdir(parents=True, exist_ok=True)
    apply_path = apply_dir / "apply-latest.json"
    if isinstance(payload, str):
        apply_path.write_text(payload)
    else:
        apply_path.write_text(json.dumps(payload))
    return apply_path


class _IncidentRecorder:
    """Captures log_incident kwargs for assertions."""

    def __init__(self):
        self.calls = []

    def __call__(self, **kw):
        self.calls.append(kw)


# ── ready_to_publish=false → block ─────────────────────────────────────────


def test_ready_to_publish_false_blocks(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is True
    assert eligibility["decision"] == "block"
    assert eligibility["ready_to_publish"] is False
    assert eligibility["hold_reason"] == "review_verdict:hold-for-review"
    assert len(log.calls) == 1
    incident = log.calls[0]
    assert incident["incident_type"] == "publisher_skip"
    assert incident["severity"] == "critical"
    assert "ready_to_publish=false" in incident["detail"]


def test_block_incident_carries_hold_reason_for_machine_readability(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    })
    log = _IncidentRecorder()
    check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    detail = log.calls[0]["detail"]
    # The hold_reason and review_verdict must appear in the incident detail
    # so downstream incident analysers can categorise without re-loading the
    # apply artefact.
    assert "review_verdict:hold-for-review" in detail
    assert "hold-for-review" in detail


# ── review verdict alone is enough to block ────────────────────────────────


def test_hold_for_review_verdict_blocks_when_ready_flag_absent(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            # ready_to_publish deliberately omitted
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is True
    assert eligibility["decision"] == "block"
    assert log.calls[0]["incident_type"] == "publisher_skip"
    assert log.calls[0]["severity"] == "critical"


def test_legacy_reject_verdict_blocks_when_ready_flag_absent(tmp_path):
    """Legacy verdict_legacy=REJECT must also block (defence in depth)."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {},
        "inputs": {"review": {"verdict": "REJECT"}},
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is True
    assert eligibility["decision"] == "block"


# ── ready_to_publish=true → permit ─────────────────────────────────────────


def test_ready_to_publish_true_permits(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
        },
        "inputs": {"review": {"verdict": "APPROVE"}},
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["decision"] == "publish"
    # No incident in the happy path.
    assert log.calls == []


def test_publish_with_flags_verdict_permits_when_ready_flag_true(tmp_path):
    """publish-with-flags + ready_to_publish=true must publish (AIM 2026-05-01)."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
        },
        "inputs": {"review": {"verdict": "publish-with-flags"}},
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["decision"] == "publish"
    assert log.calls == []


# ── Missing/malformed apply artefact → permit, but log ─────────────────────


def test_missing_apply_artefact_permits_with_info_incident(tmp_path):
    """Legacy monitors not on the apply pipeline must still publish.

    Documented behaviour: when apply-latest.json is absent the gate logs a
    guard_skip / info incident and permits publish. This is the
    least-disruptive choice for monitors that have not been migrated to the
    apply stage yet (5 of 8 monitors at the time of writing). The incident
    gives ops a single place to find which monitors lack the gate.
    """
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "macro-monitor", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["apply_present"] is False
    assert eligibility["decision"] == "publish_no_apply"
    assert len(log.calls) == 1
    incident = log.calls[0]
    assert incident["incident_type"] == "guard_skip"
    assert incident["severity"] == "info"
    assert "apply-latest.json absent" in incident["detail"]


def test_malformed_apply_artefact_permits_with_warning_incident(tmp_path):
    """Malformed apply JSON shouldn't regress monitors mid-rollout."""
    _write_apply(tmp_path, "ai-governance", "{not valid json")
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["malformed"] is True
    assert eligibility["decision"] == "publish_malformed"
    assert log.calls[0]["severity"] == "warning"
    assert log.calls[0]["incident_type"] == "quality_failure"


def test_missing_publication_block_permits_with_warning(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "inputs": {"review": {"verdict": "APPROVE"}},
        # publication intentionally absent
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["malformed"] is True
    assert eligibility["decision"] == "publish_malformed"


def test_apply_artefact_not_an_object_permits_with_warning(tmp_path):
    _write_apply(tmp_path, "ai-governance", ["this", "is", "an", "array"])
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is False
    assert eligibility["malformed"] is True


# ── load_publication_eligibility unit ──────────────────────────────────────


def test_load_extracts_review_verdict_when_present(tmp_path):
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": False,
                        "hold_reason": "review_verdict:hold-for-review"},
        "inputs": {"review": {"verdict": "hold-for-review",
                              "verdict_legacy": "REJECT"}},
    })
    e = load_publication_eligibility("ai-governance", tmp_path)
    assert e["apply_present"] is True
    assert e["ready_to_publish"] is False
    assert e["hold_reason"] == "review_verdict:hold-for-review"
    assert e["review_verdict"] == "hold-for-review"
    assert e["malformed"] is False


def test_load_returns_apply_path_even_when_absent(tmp_path):
    e = load_publication_eligibility("ai-governance", tmp_path)
    assert e["apply_path"].name == "apply-latest.json"
    assert e["apply_present"] is False


# ── Regression guard against the original incident (AIM 2026-05-02) ────────


def test_regression_guard_real_aim_2026_05_02_shape_blocks(tmp_path):
    """Exact shape from pipeline/monitors/ai-governance/applied/apply-2026-05-02.json
    (the artefact that did not stop publisher run 25256774146).
    """
    _write_apply(tmp_path, "ai-governance", {
        "_meta": {
            "schema_version": "aim-apply-v1.0",
            "monitor_slug": "ai-governance",
            "applied_at": "2026-05-02T08:00:05Z",
            "cycle_disposition": "material_change",
        },
        "cycle_id": "agm-2026-05-02",
        "inputs": {
            "review": {
                "path": "pipeline/monitors/ai-governance/synthesised/review-latest.json",
                "schema_version": "aim-review-v1.0",
                "verdict": "hold-for-review",
                "verdict_legacy": "REJECT",
                "verdict_reason": "hard-invariant FAIL: ['R1']",
            },
        },
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
            "publisher_artefacts": {
                "report_latest_path": "static/monitors/ai-governance/data/report-latest.json",
            },
        },
    })
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path, log_incident_fn=log,
    )
    assert block is True, (
        "AIM 2026-05-02 apply artefact MUST block publish — this is the "
        "exact stage-contract break the gate exists to prevent."
    )
    assert eligibility["decision"] == "block"
    assert log.calls[0]["severity"] == "critical"


# ── Default log_incident is optional ───────────────────────────────────────


def test_check_works_without_log_incident_callback(tmp_path):
    """Caller may omit log_incident_fn entirely (graceful fallback)."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": False, "hold_reason": "x"},
        "inputs": {"review": {"verdict": "hold-for-review"}},
    })
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
    )
    assert block is True
    assert eligibility["decision"] == "block"

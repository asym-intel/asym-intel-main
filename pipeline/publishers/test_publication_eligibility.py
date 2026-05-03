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


def _write_apply(tmp_path: pathlib.Path, slug: str, payload, filename: str = "apply-latest.json") -> pathlib.Path:
    """Write `payload` (dict or raw string) to applied/{filename} under tmp_path.

    `filename` lets tests place a dated artefact (apply-YYYY-MM-DD.json)
    next to apply-latest.json to exercise the date-keyed gate.
    """
    apply_dir = tmp_path / "pipeline" / "monitors" / slug / "applied"
    apply_dir.mkdir(parents=True, exist_ok=True)
    apply_path = apply_dir / filename
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


# ── Date-keyed eligibility (backfill / PUBLISH_DATE) ───────────────────────
#
# Backfill scenario: a publisher re-run with PUBLISH_DATE=YYYY-MM-DD must
# gate against apply-{YYYY-MM-DD}.json, not apply-latest.json. Without this,
# a backfill of an older held cycle can mis-decide based on a newer cycle's
# permitted verdict (or vice versa).


def test_publish_date_selects_dated_artefact_when_present(tmp_path):
    """PUBLISH_DATE=YYYY-MM-DD must read apply-YYYY-MM-DD.json, not apply-latest.json."""
    # apply-latest reflects a NEWER cycle that PERMITS publish.
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-latest.json")
    # apply-2026-04-23 reflects an OLDER cycle that BLOCKS publish.
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }, filename="apply-2026-04-23.json")
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
        log_incident_fn=log,
        publish_date="2026-04-23",
    )
    # Must block on the dated artefact, NOT permit on the latest.
    assert block is True, (
        "PUBLISH_DATE=2026-04-23 must gate against apply-2026-04-23.json "
        "(blocking) — not apply-latest.json (permitting). The dated artefact "
        "is the correct cycle's verdict."
    )
    assert eligibility["decision"] == "block"
    assert eligibility["apply_path"].name == "apply-2026-04-23.json"
    assert eligibility["dated_lookup_used"] is True
    # Incident detail mentions the dated artefact, not apply-latest.
    detail = log.calls[0]["detail"]
    assert "apply-2026-04-23.json" in detail
    assert "apply-latest.json" not in detail


def test_publish_date_inverse_dated_permits_when_latest_blocks(tmp_path):
    """Mirror case: dated permits, latest blocks → must publish."""
    # apply-latest reflects a NEWER cycle that BLOCKS publish.
    _write_apply(tmp_path, "ai-governance", {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }, filename="apply-latest.json")
    # apply-2026-04-23 reflects an OLDER cycle that PERMITS publish.
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-2026-04-23.json")
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
        log_incident_fn=log,
        publish_date="2026-04-23",
    )
    assert block is False
    assert eligibility["decision"] == "publish"
    assert eligibility["apply_path"].name == "apply-2026-04-23.json"


def test_publish_date_dated_missing_with_latest_present_blocks(tmp_path):
    """Backfill gap: monitor IS on the apply pipeline (apply-latest.json
    present) but no apply ran for the requested date. The gate must refuse
    rather than fall back to apply-latest (which is a different cycle).
    """
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-latest.json")
    # No apply-2026-04-23.json written.
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
        log_incident_fn=log,
        publish_date="2026-04-23",
    )
    assert block is True
    assert eligibility["decision"] == "block"
    assert eligibility["apply_present"] is False
    assert eligibility["dated_lookup_used"] is True
    assert eligibility["latest_present"] is True
    incident = log.calls[0]
    assert incident["incident_type"] == "apply_date_missing"
    assert incident["severity"] == "critical"
    assert "apply-2026-04-23.json" in incident["detail"]


def test_publish_date_dated_missing_legacy_monitor_still_permits(tmp_path):
    """Legacy monitor (no apply pipeline) must still publish on backfill.

    When neither the dated apply nor apply-latest.json exists, the monitor
    is not on the apply pipeline — that's the legacy case PR #186 designed
    permit for. PUBLISH_DATE must not regress that.
    """
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "macro-monitor", tmp_path,
        log_incident_fn=log,
        publish_date="2026-04-23",
    )
    assert block is False
    assert eligibility["decision"] == "publish_no_apply"
    assert eligibility["apply_present"] is False
    assert eligibility["latest_present"] is False
    assert log.calls[0]["incident_type"] == "guard_skip"
    assert log.calls[0]["severity"] == "info"


def test_no_publish_date_uses_apply_latest(tmp_path):
    """Live (today) path: publish_date=None must read apply-latest.json.

    Backward-compat with PR #186: when PUBLISH_DATE isn't set, the gate
    behaves exactly as before. A dated artefact next to apply-latest must
    NOT be picked up.
    """
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-latest.json")
    # A misleading dated artefact that would block — must be ignored.
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": False, "hold_reason": "x"},
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }, filename="apply-2026-04-23.json")
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
        publish_date=None,
    )
    assert block is False
    assert eligibility["decision"] == "publish"
    assert eligibility["apply_path"].name == "apply-latest.json"
    assert eligibility["dated_lookup_used"] is False


def test_load_with_publish_date_reads_dated_artefact(tmp_path):
    """Unit-level: load_publication_eligibility honours publish_date."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": False,
                        "hold_reason": "review_verdict:hold-for-review"},
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }, filename="apply-2026-05-02.json")
    e = load_publication_eligibility(
        "ai-governance", tmp_path, publish_date="2026-05-02",
    )
    assert e["apply_path"].name == "apply-2026-05-02.json"
    assert e["apply_present"] is True
    assert e["ready_to_publish"] is False
    assert e["review_verdict"] == "hold-for-review"
    assert e["dated_lookup_used"] is True


def test_load_with_publish_date_missing_dated_reports_latest_present(tmp_path):
    """Loader exposes latest_present so the policy layer can distinguish
    'legacy monitor' from 'backfill gap'."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-latest.json")
    e = load_publication_eligibility(
        "ai-governance", tmp_path, publish_date="2026-04-23",
    )
    assert e["apply_present"] is False
    assert e["dated_lookup_used"] is True
    assert e["latest_present"] is True


def test_publish_date_works_for_non_aim_monitor(tmp_path):
    """Date-keyed gate must work for any commons monitor, not just AIM.

    The gate is class-level: every monitor that uses publisher.py needs
    backfills to gate against the dated artefact. Verify with a different
    slug.
    """
    _write_apply(tmp_path, "environmental-risks", {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }, filename="apply-2026-04-26.json")
    _write_apply(tmp_path, "environmental-risks", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "APPROVE"}},
    }, filename="apply-latest.json")
    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "environmental-risks", tmp_path,
        log_incident_fn=log,
        publish_date="2026-04-26",
    )
    assert block is True
    assert eligibility["apply_path"].name == "apply-2026-04-26.json"
    assert eligibility["decision"] == "block"


# ── Regression guard: AIM 2026-05-02 backfill scenario ─────────────────────


def test_regression_aim_2026_05_02_backfill_not_masked_by_newer_permit(tmp_path):
    """The class of bug this PR fixes: a backfill of AIM 2026-05-02 (held)
    must block even if apply-latest.json has been replaced by a later
    cycle that permitted publish.

    Without date-keyed gating, the publisher would mis-publish the held
    2026-05-02 cycle because apply-latest now points at, say, 2026-05-09
    with ready_to_publish=true.
    """
    # Held cycle (the one we are backfilling).
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
                "verdict": "hold-for-review",
                "verdict_legacy": "REJECT",
                "verdict_reason": "hard-invariant FAIL: ['R1']",
            },
        },
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
    }, filename="apply-2026-05-02.json")
    # apply-latest now reflects a hypothetical later, permitted cycle.
    _write_apply(tmp_path, "ai-governance", {
        "_meta": {"applied_at": "2026-05-09T08:00:05Z"},
        "cycle_id": "agm-2026-05-09",
        "inputs": {"review": {"verdict": "APPROVE"}},
        "publication": {"ready_to_publish": True, "hold_reason": None},
    }, filename="apply-latest.json")

    log = _IncidentRecorder()
    block, eligibility = check_publication_eligibility(
        "ai-governance", tmp_path,
        log_incident_fn=log,
        publish_date="2026-05-02",
    )
    assert block is True, (
        "Backfill of held AIM 2026-05-02 must block — the gate must read "
        "apply-2026-05-02.json (held), not apply-latest.json (permitted)."
    )
    assert eligibility["apply_path"].name == "apply-2026-05-02.json"
    assert eligibility["decision"] == "block"
    assert log.calls[0]["severity"] == "critical"

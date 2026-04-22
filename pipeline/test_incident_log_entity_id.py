"""Coverage for log_incident() entity_id kwarg (fan-out contract).

The engine's fan-out stage bases in asym-intel-internal
(pipeline/engine/reasoner_base.py, synth_base.py, weekly_research_base.py)
call log_incident(..., entity_id=entity_id) when a per-entity run raises
during fan-out iteration — see SPEC-ADVENNT-ENGINE-MIGRATION v1.2 §3.2
and AD-2026-04-21z (Wave 0.2) for the contract.

Before this coverage existed, the engine/main cross-repo contract drifted:
engine fanout bases (3c719e7) added entity_id= passing without a matching
main signature update. The 3 TestFanOutPartialFailure tests in -internal
surfaced the drift only when gh auth was available to _cross_repo, making
outcomes environmentally non-deterministic (AD-2026-04-22a Tension log).

These tests pin the contract from main's side: entity_id is accepted,
recorded on the incident, and omitted when None to preserve byte-identical
records for non-fan-out monitors.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from incident_log import log_incident


def test_entity_id_accepted_and_recorded(tmp_path):
    """log_incident accepts entity_id kwarg and records it on the incident."""
    result = log_incident(
        monitor="advennt",
        stage="reasoner",
        incident_type="fanout_entity_error",
        severity="error",
        detail="GI: simulated failure",
        entity_id="GI",
        repo_root=tmp_path,
    )

    assert result["entity_id"] == "GI"

    # Verify it persists to disk
    log_file = tmp_path / "pipeline" / "incidents" / "incidents.jsonl"
    assert log_file.exists()
    row = json.loads(log_file.read_text().strip().split("\n")[0])
    assert row["entity_id"] == "GI"
    assert row["monitor"] == "advennt"
    assert row["stage"] == "reasoner"


def test_entity_id_omitted_when_none(tmp_path):
    """When entity_id is None (non-fan-out monitor), the field is NOT written.

    Byte-identical to pre-v1.2 behaviour for the 8 existing non-fan-out
    monitors (WDM/GMM/ESA/FCW/AGM/ERM/SCEM/FIM).
    """
    result = log_incident(
        monitor="macro-monitor",
        stage="reasoner",
        incident_type="api_failure",
        severity="error",
        detail="sonar-pro timeout",
        repo_root=tmp_path,
    )

    assert "entity_id" not in result

    log_file = tmp_path / "pipeline" / "incidents" / "incidents.jsonl"
    row = json.loads(log_file.read_text().strip().split("\n")[0])
    assert "entity_id" not in row


def test_entity_id_kwarg_only(tmp_path):
    """entity_id must be passed as a kwarg (signature is keyword-only)."""
    # All incident-log args are keyword-only (leading `*` in signature).
    # Positional call should fail — this locks that in so nobody later
    # accidentally relaxes the signature.
    import pytest
    with pytest.raises(TypeError):
        log_incident(
            "advennt", "reasoner", "fanout_entity_error",  # positional
            repo_root=tmp_path,
        )

"""Schema v1.1 backward-compat tests for prompt_exchange_log.py.

Five tests covering the v1.0 → v1.1 additive bump:
  1. v1.0 rows remain readable after the v1.1 upgrade.
  2. v1.1 rows written with no optional args still have safe defaults.
  3. Lab call path writes source=lab + runtime + lab_run_id correctly.
  4. Core invariant: log_exchange NEVER raises, even on bad paths.
  5. The engagement-signature diagnostic (tokens + runtime_seconds)
     round-trips through write → read intact.

Per SPEC-AI-ENGINE-LABORATORY v0.3.2 §B (schema v1.1).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prompt_exchange_log import log_exchange, read_exchanges


def test_v10_row_readable_after_v11_upgrade(tmp_path):
    """A pre-existing v1.0 row must still parse with the v1.1 reader."""
    log_file = tmp_path / "pipeline" / "incidents" / "prompt-exchanges.jsonl"
    log_file.parent.mkdir(parents=True)
    # Hand-craft a v1.0 shape row (no schema_version, no engine/source)
    v10_row = {
        "ts": "2026-04-18T09:00:00Z",
        "monitor": "macro-monitor",
        "stage": "weekly-research",
        "model": "sonar-pro",
        "prompt_file": "some/path.txt",
        "prompt_hash": "abcdef1234567890",
        "prompt_chars": 500,
        "outcome": "success",
        "response_chars": 2000,
        "raw_response": "{...}",
        "run_id": "12345",
    }
    log_file.write_text(json.dumps(v10_row) + "\n")
    records = read_exchanges(repo_root=tmp_path)
    assert len(records) == 1
    assert records[0]["monitor"] == "macro-monitor"
    assert "schema_version" not in records[0]  # v1.0 row never had it
    assert "engine" not in records[0]          # v1.0 row never had it


def test_v11_row_defaults_correct(tmp_path):
    """A v1.1 row written with no optional new args still has safe defaults."""
    record = log_exchange(
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-pro",
        prompt_text="test prompt",
        raw_response='{"ok": true}',
        parsed_ok=True,
        repo_root=tmp_path,
    )
    assert record["schema_version"] == "1.1"
    assert record["engine"] == "asym-intel"
    assert record["source"] == "cron"
    assert "lab_run_id" not in record       # None → omitted
    assert "runtime_seconds" not in record  # None → omitted


def test_v11_lab_source_with_runtime(tmp_path):
    """Lab call path writes source=lab + runtime + lab_run_id."""
    record = log_exchange(
        monitor="ai-governance",
        stage="synthesiser",
        model="sonar-deep-research",
        prompt_text="test prompt",
        raw_response='{"ok": true}',
        parsed_ok=True,
        source="lab",
        lab_run_id="lab-20260422-001",
        extractor="think-aware",
        contract="engine-default",
        runtime_seconds=132.4,
        tokens=10900,
        repo_root=tmp_path,
    )
    assert record["source"] == "lab"
    assert record["lab_run_id"] == "lab-20260422-001"
    assert record["extractor"] == "think-aware"
    assert record["contract"] == "engine-default"
    assert record["runtime_seconds"] == 132.4
    assert record["tokens"] == 10900


def test_log_never_raises_even_on_bad_path():
    """Core invariant: logging failures never propagate."""
    # Pass a file path that cannot be created (not writable)
    bogus = pathlib.Path("/nonexistent/readonly/volume")
    record = log_exchange(
        monitor="x", stage="y", model="z",
        prompt_text="p", raw_response="r", parsed_ok=True,
        repo_root=bogus,
    )
    # Should return empty dict, not raise
    assert isinstance(record, dict)


def test_engagement_signature_round_trip(tmp_path):
    """The diagnostic playbook needs tokens+runtime to classify. Round-trip
    both through write → read and confirm they survive.
    Per SPEC-AI-ENGINE-LABORATORY §1.2 engagement-signature playbook:
      - >10k tokens + >100s runtime → likely parser-dropped real work.
    """
    log_exchange(
        monitor="ai-governance", stage="synthesiser", model="sonar-deep-research",
        prompt_text="p", raw_response='{"ok":true}', parsed_ok=True,
        tokens=10900, runtime_seconds=130.2, source="lab",
        lab_run_id="lab-signature-test", repo_root=tmp_path,
    )
    records = read_exchanges(repo_root=tmp_path)
    assert len(records) == 1
    r = records[0]
    # The engagement signature fields both present on the same row
    assert r["tokens"] == 10900
    assert r["runtime_seconds"] == 130.2
    # >10k tokens + >100s runtime classifies as "parser class" per playbook
    assert r["tokens"] > 10000 and r["runtime_seconds"] > 100

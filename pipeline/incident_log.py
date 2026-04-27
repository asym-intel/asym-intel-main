"""
Pipeline Incident Log — Engine-Level Shared Utility

Append-only JSONL logger for pipeline failures, quality issues, and no-shows.
Any pipeline script (collector, research, reasoner, synthesiser, publisher)
imports this and calls log_incident() at the point of failure.

Location: pipeline/incident_log.py (asym-intel-main)
Import:   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[N]))
          from incident_log import log_incident

Schema version: 1.0 (16 April 2026)

This is an ENGINE-LEVEL utility. All sites using the asym engine's
prompt→pipeline→publish pattern MUST use this for failure logging.
See ENGINE-RULES.md for integration requirements.
"""

import json
import os
import pathlib
import datetime

# ── Configuration ─────────────────────────────────────────────────

# Default output: repo-root/pipeline/incidents/incidents.jsonl
# Each pipeline script resolves REPO_ROOT from its own location or env var.
_DEFAULT_REPO_ROOT = pathlib.Path(
    os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[1])
)
INCIDENTS_DIR = _DEFAULT_REPO_ROOT / "pipeline" / "incidents"
INCIDENTS_FILE = INCIDENTS_DIR / "incidents.jsonl"

# ── Incident types ────────────────────────────────────────────────

INCIDENT_TYPES = {
    "api_failure":       "API call failed after all retries",
    "empty_response":    "API returned empty or non-JSON response",
    "json_parse_error":  "Response could not be parsed as valid JSON",
    "json_repaired":     "Response required JSON repair before parsing",
    "schema_violation":  "Output failed schema validation",
    "quality_failure":   "Output is structurally valid but substantively empty/stub",
    "stale_input":       "Input data too old for this pipeline stage",
    "publisher_skip":    "Publisher declined to publish (stale, stub, or failed gate)",
    "no_show":           "Expected pipeline run did not fire",
    "guard_skip":        "Run skipped by dedup guard (already ran today)",
    "prompt_refusal":    "Model refused the prompt (identity/safety filter)",
    "timeout":           "API call or workflow timed out",
    "input_missing":     "Required input file not found",
}

# ── Severity levels ───────────────────────────────────────────────

SEVERITIES = {
    "info":     "Logged for audit trail, no action needed (e.g. guard_skip, json_repaired)",
    "warning":  "Degraded output, pipeline continued (e.g. schema warnings, stale input used)",
    "error":    "Stage failed, pipeline halted at this point (e.g. api_failure, json_parse_error)",
    "critical": "Data integrity risk (e.g. publisher_skip due to roster drop, governance file wipe)",
}


def log_incident(
    *,
    monitor: str,
    stage: str,
    incident_type: str,
    severity: str = "error",
    detail: str = "",
    errors: list = None,
    warnings: list = None,
    run_id: str = None,
    raw_snippet: str = None,
    repo_root: pathlib.Path = None,
    entity_id: str = None,
) -> dict:
    """Append a single incident line to the JSONL log.

    Args:
        monitor:       Monitor slug or product name (e.g. "european-strategic-autonomy", "advennt")
        stage:         Pipeline stage (collector, weekly-research, reasoner, synthesiser, publisher, watchdog)
        incident_type: One of INCIDENT_TYPES keys
        severity:      One of: info, warning, error, critical
        detail:        Human-readable description of what happened
        errors:        List of validation error strings (from schema checks)
        warnings:      List of validation warning strings
        run_id:        GitHub Actions run ID (from GITHUB_RUN_ID env var if not provided)
        raw_snippet:   First 500 chars of raw LLM output (for debugging prompt failures)
        repo_root:     Override repo root path (defaults to auto-detected)
        entity_id:     Fan-out entity identifier (e.g. jurisdiction code "GI", "CA-ON")
                       for monitors with top-level fan_out (SPEC-ADVENNT-ENGINE-MIGRATION
                       v1.2 §3.2, asym-intel-internal engine fanout bases
                       reasoner_base/synth_base/weekly_research_base). Omitted from the
                       JSONL record when None, so non-fan-out monitors write
                       byte-identical records to pre-v1.2.

    Returns:
        The incident dict that was written (for testing/chaining).

    Side effects:
        Appends one JSON line to pipeline/incidents/incidents.jsonl
        Creates the directory if it doesn't exist.
        NEVER raises — all errors are caught and printed to stderr.
        A logging failure must NEVER take down a pipeline stage.
    """
    try:
        # Resolve output path
        root = repo_root or _DEFAULT_REPO_ROOT
        incidents_dir = root / "pipeline" / "incidents"
        incidents_file = incidents_dir / "incidents.jsonl"

        # Build incident record
        incident = {
            "ts": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "monitor": monitor,
            "stage": stage,
            "type": incident_type,
            "severity": severity,
            "detail": detail,
        }

        # Optional fields — only include if present
        if errors:
            incident["errors"] = errors
        if warnings:
            incident["warnings"] = warnings
        if entity_id:
            incident["entity_id"] = entity_id

        # Run ID: explicit or from GA environment
        incident["run_id"] = run_id or os.environ.get("GITHUB_RUN_ID", "local")

        # Workflow name from GA environment
        workflow = os.environ.get("GITHUB_WORKFLOW", "")
        if workflow:
            incident["workflow"] = workflow

        if raw_snippet:
            incident["raw_snippet"] = raw_snippet[:500]

        # Write
        incidents_dir.mkdir(parents=True, exist_ok=True)
        with open(incidents_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(incident, ensure_ascii=False) + "\n")

        # Also print to stdout for GA logs
        severity_icon = {"info": "ℹ", "warning": "⚠", "error": "✗", "critical": "🚨"}.get(
            severity, "?"
        )
        print(
            f"INCIDENT {severity_icon} [{severity.upper()}] {monitor}/{stage}: "
            f"{incident_type} — {detail}"
        )

        return incident

    except Exception as e:
        # NEVER let logging take down the pipeline
        print(f"WARNING: incident_log.log_incident failed: {e}")
        return {}


def read_incidents(
    repo_root: pathlib.Path = None,
    since: str = None,
    monitor: str = None,
    severity: str = None,
) -> list:
    """Read incidents from the JSONL log with optional filters.

    Args:
        repo_root: Override repo root path
        since:     ISO date string — only return incidents on or after this date
        monitor:   Filter by monitor slug
        severity:  Filter by severity level

    Returns:
        List of incident dicts, newest first.
    """
    root = repo_root or _DEFAULT_REPO_ROOT
    incidents_file = root / "pipeline" / "incidents" / "incidents.jsonl"

    if not incidents_file.exists():
        return []

    incidents = []
    for line in incidents_file.read_text(encoding="utf-8").strip().split("\n"):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if since and record.get("ts", "") < since:
            continue
        if monitor and record.get("monitor") != monitor:
            continue
        if severity and record.get("severity") != severity:
            continue

        incidents.append(record)

    return list(reversed(incidents))  # newest first


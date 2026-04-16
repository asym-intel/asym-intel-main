"""
Prompt Exchange Logger — Engine-Level Shared Utility

Append-only JSONL logger that records every LLM API call: the prompt sent,
the raw response received, and the outcome (success / parse_error / refusal).

This builds the archive of what works and what fails, BEFORE any parsing
changes are made. Every pipeline script that calls an LLM should log via
log_exchange() immediately after receiving the API response.

Location: pipeline/shared/prompt_exchange_log.py (asym-intel-main)
Import:   sys.path.insert(0, str(repo_root / "pipeline" / "shared"))
          from prompt_exchange_log import log_exchange

Output:   pipeline/incidents/prompt-exchanges.jsonl

Schema version: 1.0 (16 April 2026)
"""

import hashlib
import json
import os
import pathlib
import datetime

# ── Configuration ─────────────────────────────────────────────────

_DEFAULT_REPO_ROOT = pathlib.Path(
    os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[2])
)

OUTCOMES = {
    "success":        "Response parsed as valid JSON",
    "json_repaired":  "Response required cleanup (fence strip / brace extract) before parsing",
    "parse_error":    "Response could not be parsed as JSON even after cleanup",
    "refusal":        "Model refused the prompt (identity/safety/capability filter)",
    "empty":          "Response was empty or whitespace-only",
    "api_error":      "API call itself failed (HTTP error, timeout)",
}


def _prompt_fingerprint(prompt_text: str) -> str:
    """SHA-256 of the prompt template (before variable substitution).

    For tracking which prompt version produced which outcomes.
    We hash the full text — cheap and deterministic.
    """
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:16]


def _detect_refusal(raw: str) -> bool:
    """Detect common patterns where the model refuses the prompt
    instead of returning JSON data."""
    if not raw:
        return False
    # Check first 300 chars for refusal signatures
    head = raw[:300].lower()
    refusal_signals = [
        "i appreciate",
        "i cannot",
        "i can't",
        "i need to clarify",
        "i am perplexity",
        "i am a search assistant",
        "i'm not able to",
        "i don't have access",
        "i cannot fulfill",
        "as an ai",
        "i'm unable to",
        "this request is outside",
    ]
    return any(signal in head for signal in refusal_signals)


def _classify_outcome(raw: str, parsed_ok: bool) -> str:
    """Classify the exchange outcome from the raw response."""
    if not raw or not raw.strip():
        return "empty"
    if _detect_refusal(raw):
        return "refusal"
    if parsed_ok:
        # Check if cleanup was needed
        clean = raw.strip()
        try:
            json.loads(clean)
            return "success"
        except json.JSONDecodeError:
            return "json_repaired"
    return "parse_error"


def log_exchange(
    *,
    monitor: str,
    stage: str,
    model: str,
    prompt_text: str,
    prompt_file: str = "",
    raw_response: str,
    parsed_ok: bool,
    outcome: str = None,
    tokens: int = None,
    citations: int = None,
    item_count: int = None,
    repo_root: pathlib.Path = None,
) -> dict:
    """Log a single LLM API exchange to the JSONL archive.

    Call this IMMEDIATELY after receiving the API response,
    BEFORE any parsing or validation logic runs.

    Args:
        monitor:       Monitor slug (e.g. "fimi-cognitive-warfare")
        stage:         Pipeline stage (chatter, collector, weekly-research, synthesiser, reasoner)
        model:         Model name used (e.g. "sonar", "sonar-pro")
        prompt_text:   The full prompt sent (after variable substitution)
        prompt_file:   Path to the prompt template file (for traceability)
        raw_response:  The full raw LLM response text
        parsed_ok:     Whether the response was successfully parsed as JSON
        outcome:       Override auto-classification (one of OUTCOMES keys)
        tokens:        Total tokens used (from API response)
        citations:     Number of citations returned
        item_count:    Number of items in parsed output (if successful)
        repo_root:     Override repo root path

    Returns:
        The exchange record dict.

    Side effects:
        Appends one JSON line to pipeline/incidents/prompt-exchanges.jsonl
        NEVER raises — logging failure must not take down the pipeline.
    """
    try:
        root = repo_root or _DEFAULT_REPO_ROOT
        log_dir = root / "pipeline" / "incidents"
        log_file = log_dir / "prompt-exchanges.jsonl"

        # Auto-classify if not overridden
        if outcome is None:
            outcome = _classify_outcome(raw_response, parsed_ok)

        record = {
            "ts": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "monitor": monitor,
            "stage": stage,
            "model": model,
            "prompt_file": prompt_file,
            "prompt_hash": _prompt_fingerprint(prompt_text),
            "prompt_chars": len(prompt_text),
            "outcome": outcome,
            "response_chars": len(raw_response) if raw_response else 0,
            "raw_response": raw_response,
        }

        # Optional fields
        if tokens is not None:
            record["tokens"] = tokens
        if citations is not None:
            record["citations"] = citations
        if item_count is not None:
            record["item_count"] = item_count

        # Run context from GA
        run_id = os.environ.get("GITHUB_RUN_ID", "local")
        record["run_id"] = run_id
        workflow = os.environ.get("GITHUB_WORKFLOW", "")
        if workflow:
            record["workflow"] = workflow

        # Write
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        outcome_icon = {
            "success": "✅", "json_repaired": "🔧",
            "parse_error": "❌", "refusal": "🚫",
            "empty": "⚪", "api_error": "💥",
        }.get(outcome, "?")
        print(f"EXCHANGE {outcome_icon} {monitor}/{stage}: {outcome} "
              f"(prompt={record['prompt_chars']}ch, response={record['response_chars']}ch)")

        return record

    except Exception as e:
        # NEVER let logging take down the pipeline
        print(f"WARNING: prompt_exchange_log.log_exchange failed: {e}")
        return {}


def read_exchanges(
    repo_root: pathlib.Path = None,
    since: str = None,
    monitor: str = None,
    outcome: str = None,
) -> list:
    """Read exchanges from the JSONL log with optional filters.

    Returns list of exchange dicts, newest first.
    """
    root = repo_root or _DEFAULT_REPO_ROOT
    log_file = root / "pipeline" / "incidents" / "prompt-exchanges.jsonl"

    if not log_file.exists():
        return []

    exchanges = []
    for line in log_file.read_text(encoding="utf-8").strip().split("\n"):
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
        if outcome and record.get("outcome") != outcome:
            continue

        exchanges.append(record)

    return list(reversed(exchanges))  # newest first

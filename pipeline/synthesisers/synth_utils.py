"""
Shared utilities for all Asymmetric Intelligence synthesiser scripts.
Place at: pipeline/synthesisers/synth_utils.py
Import:   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
          from synth_utils import parse_llm_json

v2 additions (21 Apr 2026, SPEC-AI-ENGINE-LABORATORY v0.3.2 PR 2):
  - parse_llm_json gains optional `think_aware` flag that strips
    `<think>...</think>` blocks before JSON extraction. Required for
    sonar-deep-research, which wraps JSON in a reasoning block that
    the standard extractor drops.
  - new `call_synth_api` helper wraps requests.post with wall-clock
    timing and routes through prompt_exchange_log.log_exchange so every
    synthesiser call is observable in prompt-exchanges.jsonl. Callers
    opt in — existing 9 synth scripts remain unchanged until wired in
    a follow-up PR.

Back-compat: all existing callers using `parse_llm_json(raw, tag)`
continue to work unchanged.
"""

import json
import pathlib
import re
import sys
import time


_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_think_blocks(raw: str) -> str:
    """Remove `<think>...</think>` wrapper blocks from an LLM response.

    Perplexity sonar-deep-research emits reasoning inside a `<think>`
    block before the JSON output. The standard JSON extractor in
    `parse_llm_json` does not handle the wrapper and drops the run.
    This helper strips the wrapper so the existing brace-matching
    extractor can proceed.

    Implementation is intentionally mechanical — a regex against a
    publicly-known wrapper format. Extractor-selection logic (when to
    use think-aware by model/stage) lives in
    `ops/PROMPTS-KNOWHOW-perplexity.md` in asym-intel-internal, not here.
    """
    if not raw:
        return raw
    return _THINK_BLOCK_RE.sub("", raw)


def repair_json(raw: str) -> str:
    """Multi-pass JSON repair for LLM output.

    Handles:
      1. Smart/curly quotes → straight quotes
      2. Unescaped apostrophes inside string values → \\u0027
      3. Control characters inside strings (tabs, newlines) → escaped
      4. Trailing commas before } or ]
      5. Truncated response — attempts to close open braces/brackets
    """
    # ── Pass 0: normalise smart quotes ──────────────────────────────────
    raw = raw.replace("\u201c", '"').replace("\u201d", '"')   # "" → ""
    raw = raw.replace("\u2018", "'").replace("\u2019", "'")   # '' → ''
    raw = raw.replace("\u2013", "-").replace("\u2014", "--")  # –— → --

    # ── Pass 1: walk char-by-char, fix in-string issues ─────────────────
    repaired = []
    in_string = False
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == '\\' and in_string:
            # Escape sequence — pass through, but validate next char
            repaired.append(c)
            i += 1
            if i < len(raw):
                nc = raw[i]
                # Valid JSON escapes: " \ / b f n r t uXXXX
                if nc in ('"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'):
                    repaired.append(nc)
                else:
                    # Invalid escape like \' or \S — escape the backslash
                    repaired.append('\\')
                    repaired.append(nc)
        elif c == '"':
            in_string = not in_string
            repaired.append(c)
        elif in_string:
            if c == "'":
                repaired.append('\\u0027')
            elif c == '\n':
                repaired.append('\\n')
            elif c == '\r':
                repaired.append('\\r')
            elif c == '\t':
                repaired.append('\\t')
            elif ord(c) < 0x20:
                # Other control characters
                repaired.append(f'\\u{ord(c):04x}')
            else:
                repaired.append(c)
        else:
            repaired.append(c)
        i += 1

    result = ''.join(repaired)

    # ── Pass 2: trailing commas ─────────────────────────────────────────
    result = re.sub(r',\s*([}\]])', r'\1', result)

    # ── Pass 3: truncation recovery ─────────────────────────────────────
    # If the response was cut off mid-string or mid-object, try to close it
    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        pass

    # Try closing unclosed strings and braces
    # Count open braces/brackets
    open_braces = 0
    open_brackets = 0
    in_str = False
    for ci in result:
        if ci == '\\' and in_str:
            continue
        elif ci == '"':
            in_str = not in_str
        elif not in_str:
            if ci == '{':
                open_braces += 1
            elif ci == '}':
                open_braces -= 1
            elif ci == '[':
                open_brackets += 1
            elif ci == ']':
                open_brackets -= 1

    # If we're still inside a string, close it
    if in_str:
        result += ' [truncated]"'

    # Close any open brackets/braces
    result += ']' * max(0, open_brackets)
    result += '}' * max(0, open_braces)

    # Remove any trailing comma before the closing braces we just added
    result = re.sub(r',\s*([}\]])', r'\1', result)

    return result


def parse_llm_json(raw: str, monitor_tag: str = "SYNTH", *, think_aware: bool = False) -> tuple:
    """Parse LLM JSON output with multi-stage repair.

    Returns (parsed_dict, was_repaired: bool).
    Raises json.JSONDecodeError only if all repair attempts fail.

    Args:
        raw:           Raw LLM response text.
        monitor_tag:   Short tag used in diagnostic prints (e.g. "GMM").
        think_aware:   If True, strip `<think>...</think>` wrapper blocks
                       before JSON extraction. Required for Perplexity
                       `sonar-deep-research`. Defaults to False so all
                       existing callers remain unchanged.

    Usage:
        # Standard (all existing callers):
        synthesis, repaired = parse_llm_json(raw, "GMM")

        # Think-aware (sonar-deep-research and similar):
        synthesis, repaired = parse_llm_json(raw, "AIG", think_aware=True)
    """
    # Optional: strip `<think>...</think>` reasoning wrapper first
    if think_aware:
        raw = _strip_think_blocks(raw)

    # Strip markdown fences
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    # Extract outermost JSON object
    brace_start = raw.find("{")
    brace_end = raw.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        raw = raw[brace_start:brace_end + 1]

    # Attempt 1: direct parse
    try:
        return json.loads(raw), False
    except json.JSONDecodeError:
        pass

    # Attempt 2: repaired parse
    repaired = repair_json(raw)
    try:
        return json.loads(repaired), True
    except json.JSONDecodeError as e:
        print(f"[{monitor_tag}] repair_json failed: {e}")

    # Attempt 3: aggressive — strip all control chars, re-repair
    aggressive = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', raw)
    repaired2 = repair_json(aggressive)
    try:
        return json.loads(repaired2), True
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"All repair attempts failed: {e.msg}", e.doc[:200], e.pos
        )


# ─── call_synth_api helper (SPEC-AI-ENGINE-LABORATORY v0.3.2 PR 2) ───────────
#
# Wraps the Perplexity API POST with:
#   1. Wall-clock timing (runtime_seconds for Schema v1.1)
#   2. 429 rate-limit backoff (60s default — same pattern as existing scripts)
#   3. parse_llm_json invocation (with optional think_aware extractor)
#   4. log_exchange emission into pipeline/incidents/prompt-exchanges.jsonl
#
# Callers opt in. Existing 9 synth scripts remain unchanged until wired in a
# follow-up PR. First live caller will be the lab runner (PR 3) invoking this
# helper against AIG synth for the 5a/5b/5c/5d discovery grid.


def _load_log_exchange():
    """Lazy-import log_exchange from pipeline/shared/prompt_exchange_log.

    Lazy to keep synth_utils importable in environments where pipeline/shared/
    is not on sys.path (e.g. unit tests that only exercise parse_llm_json).
    Returns a no-op stub if the import fails, so call_synth_api never takes
    down the synthesiser because the logger module moved.
    """
    try:
        repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
        shared = repo_root / "pipeline" / "shared"
        if str(shared) not in sys.path:
            sys.path.insert(0, str(shared))
        from prompt_exchange_log import log_exchange  # type: ignore
        return log_exchange
    except Exception:  # noqa: BLE001 — never let import take down the pipeline
        def _noop(**_kw):
            return {}
        return _noop


def call_synth_api(
    *,
    url: str,
    headers: dict,
    body: dict,
    monitor: str,
    stage: str,
    model: str,
    prompt_text: str,
    prompt_file: str = "",
    extractor: str = "standard",
    contract: str = None,
    source: str = "cron",
    lab_run_id: str = None,
    engine: str = "asym-intel",
    prompt_body_sha: str = None,
    timeout: int = 300,
    rate_limit_backoff: int = 60,
) -> tuple:
    """Call the Perplexity API, parse the response, log the exchange.

    Single entry point for synth-stage API calls so every call lands in
    `prompt-exchanges.jsonl` with Schema v1.1 fields filled.

    Args:
        url, headers, body:  requests.post arguments (unchanged from callers).
        monitor:             Monitor slug (e.g. "ai-governance").
        stage:               Pipeline stage — "synthesiser" for MVP scope.
        model:               Model name used (e.g. "sonar-deep-research").
        prompt_text:         The full rendered prompt sent to the model.
        prompt_file:         Path to the prompt template (traceability).
        extractor:           Extraction strategy — "standard" | "think-aware".
                             Determines think_aware flag passed to parse_llm_json.
        contract:            Prompt contract layer (None | "engine-default" | ...).
        source:              "cron" | "lab" — distinguishes production from lab runs.
        lab_run_id:          Set by lab runner; joins to pipeline/lab/run-log.jsonl.
        engine:              "asym-intel" | "advennt".
        prompt_body_sha:     Domain body SHA (vs final-assembled prompt SHA).
        timeout:             requests timeout seconds.
        rate_limit_backoff:  Seconds to wait on HTTP 429 before retry.

    Returns:
        (parsed_or_none, meta) where:
          - parsed_or_none: dict from parse_llm_json on success, None on failure
          - meta: dict with keys:
              raw              — full raw response text (may be "")
              http_status      — final HTTP status (int) or None if connection failed
              runtime_seconds  — wall-clock duration of the API call(s)
              was_repaired     — bool from parse_llm_json, False if parse failed
              parsed_ok        — bool
              error            — str | None  (exception message if any)
              exchange_record  — dict returned by log_exchange
              tokens           — int | None  (usage.total_tokens if present)
              citations        — int | None  (len(resp['citations']) if present)

    Never raises. On any failure, returns (None, meta) with error populated.
    """
    import requests  # local import — only needed when this helper is called

    log_exchange = _load_log_exchange()

    think_aware = (extractor == "think-aware")
    raw = ""
    http_status = None
    tokens = None
    citations = None
    error_msg = None

    t0 = time.time()
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        http_status = resp.status_code
        if resp.status_code == 429:
            print(f"[{monitor}] 429 rate limit — waiting {rate_limit_backoff}s")
            time.sleep(rate_limit_backoff)
            resp = requests.post(url, headers=headers, json=body, timeout=timeout)
            http_status = resp.status_code
        resp.raise_for_status()

        data = resp.json()
        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
        raw = raw.strip()

        usage = data.get("usage") or {}
        tokens = usage.get("total_tokens")
        if isinstance(data.get("citations"), list):
            citations = len(data["citations"])
    except Exception as e:  # noqa: BLE001
        error_msg = f"{type(e).__name__}: {e}"
    runtime_seconds = time.time() - t0

    parsed = None
    was_repaired = False
    parsed_ok = False
    if raw and error_msg is None:
        try:
            parsed, was_repaired = parse_llm_json(
                raw, monitor_tag=monitor, think_aware=think_aware
            )
            parsed_ok = True
        except json.JSONDecodeError as e:
            error_msg = f"JSONDecodeError: {e}"

    # Log the exchange — never raises
    exchange_record = log_exchange(
        monitor=monitor,
        stage=stage,
        model=model,
        prompt_text=prompt_text,
        prompt_file=prompt_file,
        raw_response=raw,
        parsed_ok=parsed_ok,
        tokens=tokens,
        citations=citations,
        item_count=None,  # synth-specific count semantics — caller can derive
        engine=engine,
        source=source,
        lab_run_id=lab_run_id,
        extractor=extractor,
        contract=contract,
        prompt_body_sha=prompt_body_sha,
        runtime_seconds=runtime_seconds,
    )

    meta = {
        "raw": raw,
        "http_status": http_status,
        "runtime_seconds": runtime_seconds,
        "was_repaired": was_repaired,
        "parsed_ok": parsed_ok,
        "error": error_msg,
        "exchange_record": exchange_record,
        "tokens": tokens,
        "citations": citations,
    }
    return parsed, meta

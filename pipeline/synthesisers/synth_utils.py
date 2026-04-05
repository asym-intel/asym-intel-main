"""
Shared utilities for all Asymmetric Intelligence synthesiser scripts.
Place at: pipeline/synthesisers/synth_utils.py
Import:   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
          from synth_utils import parse_llm_json
"""

import json, re


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


def parse_llm_json(raw: str, monitor_tag: str = "SYNTH") -> tuple:
    """Parse LLM JSON output with multi-stage repair.

    Returns (parsed_dict, was_repaired: bool).
    Raises json.JSONDecodeError only if all repair attempts fail.

    Usage:
        try:
            synthesis, repaired = parse_llm_json(raw, "GMM")
            if repaired:
                print(f"[GMM] JSON repaired successfully")
        except json.JSONDecodeError as e:
            # All repair attempts failed
            ...
    """
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

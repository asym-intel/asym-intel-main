#!/usr/bin/env python3
"""
Pre-Publication Adversarial Challenger — engine-wide runner

Per SCOPE-2026-04-17-003 and data-integrity-roadmap Layer 3.

Runs AFTER synthesis, BEFORE publisher. Observer-only (Sprint A/B) — never gates
publish. Emits `_challenge` block attached to the monitor's persistent-state.json.

Inputs (env):
  MONITOR_SLUG   — e.g. "financial-integrity", "macro-monitor", "cross-monitor"
  PPLX_API_KEY   — Perplexity API key
  REPO_ROOT      — optional override (defaults to repo root discovered from file)

File conventions:
  Synthesis input:   pipeline/monitors/{slug}/synthesised/synthesis-latest.json
                     (fallback: pipeline/synthesisers/{abbr}/... if that's the canonical location)
  Guardrails:        pipeline/monitors/{slug}/methodology-guardrails.md
  Prior briefs (for overfit detection):
                     content/monitors/{slug}/*.md  — most recent 2
  Output:            static/monitors/{slug}/data/persistent-state.json._challenge
                     ops/challenger-log.md (append one row)

Failure modes (never block the cascade):
  — no synthesis    → _challenge: {status: "no_synthesis"}  exit 0
  — no guardrails   → _challenge: {status: "no_guardrails"} exit 0
  — API error       → _challenge: {status: "unavailable", reason: ...} exit 0
  — JSON parse fail → _challenge: {status: "parse_error", raw_snippet: ...} exit 0

Model: sonar-pro with web search enabled (required — see SCOPE-003).
"""
import datetime
import hashlib
import json
import os
import pathlib
import sys
import time
from collections import Counter

import requests

# ── Pipeline incident logging (engine-level, graceful fallback) ──────────────
try:
    _il_root = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[2]))
    sys.path.insert(0, str(_il_root / "pipeline"))
    from incident_log import log_incident  # type: ignore
except ImportError:
    def log_incident(**kw): pass


REPO_ROOT = pathlib.Path(os.environ.get("REPO_ROOT", pathlib.Path(__file__).resolve().parents[2]))
MONITOR_SLUG = os.environ.get("MONITOR_SLUG", "").strip()

API_KEY = os.environ.get("PPLX_API_KEY", "").strip()
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL = os.environ.get("CHALLENGER_MODEL") or "sonar-pro"

CHALLENGER_DIR = REPO_ROOT / "pipeline" / "challengers"
SKELETON_PROMPT = CHALLENGER_DIR / "challenger-skeleton-prompt.txt"
RESPONSE_SCHEMA = CHALLENGER_DIR / "challenger-response-schema.json"

# Public-methodology → abbreviation map (used for guardrail discovery and log label)
SLUG_ABBR = {
    "financial-integrity": "FIM",
    "macro-monitor": "GMM",
    "democratic-integrity": "WDM",
    "european-strategic-autonomy": "ESA",
    "fimi-cognitive-warfare": "FCW",
    "ai-governance": "AIM",
    "environmental-risks": "ERM",
    "conflict-escalation": "SCEM",
    "cross-monitor": "X-1",
}


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str):
    print(f"[challenger:{MONITOR_SLUG}] {msg}", flush=True)


def write_challenge_block(challenge: dict, duration_ms: int = 0) -> None:
    """Write _challenge onto static/monitors/{slug}/data/persistent-state.json.

    Also mirrors to docs/ (generated output tree) so the Hugo build sees it.
    """
    challenge["challenger_model"] = challenge.get("challenger_model", MODEL)
    challenge["ts"] = challenge.get("ts", now_iso())
    challenge["duration_ms"] = duration_ms
    challenge["schema_version"] = "1.0"

    for tree in ("static", "docs"):
        ps_path = REPO_ROOT / tree / "monitors" / MONITOR_SLUG / "data" / "persistent-state.json"
        if not ps_path.exists():
            # First run — nothing to attach to. Skip quietly; log below covers it.
            log(f"persistent-state.json not found at {ps_path} — skipping write (tree={tree})")
            continue
        try:
            state = json.loads(ps_path.read_text(encoding="utf-8"))
            state["_challenge"] = challenge
            ps_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
            log(f"wrote _challenge to {ps_path}")
        except Exception as e:
            log(f"WARNING: could not write _challenge to {ps_path}: {e}")


def append_challenger_log(verdict: str, justification: str, flag_counts: dict) -> None:
    """Append one row to ops/challenger-log.md. Observer substrate for Sprint C graduation.

    flag_counts keys (all optional, default 0):
      findings, hard, soft, info, top_category
    """
    log_path = REPO_ROOT / "ops" / "challenger-log.md"
    if not log_path.exists():
        log(f"challenger-log.md missing — skipping append (expected during first run or fresh repo)")
        return
    abbr = SLUG_ABBR.get(MONITOR_SLUG, MONITOR_SLUG.upper())
    row = (
        f"| {now_iso()} | {abbr} | {verdict} | "
        f"{flag_counts.get('findings', 0)} | "
        f"{flag_counts.get('hard', 0)} | "
        f"{flag_counts.get('soft', 0)} | "
        f"{flag_counts.get('info', 0)} | "
        f"{flag_counts.get('top_category', '-')} | "
        f"{justification[:120].replace('|', '/')} |  |\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(row)
        log(f"appended row to {log_path}")
    except Exception as e:
        log(f"WARNING: could not append to challenger log: {e}")


def emit_status(status: str, reason: str = "") -> None:
    """Emit a non-verdict _challenge block (degradation path). Always exit 0."""
    block = {
        "status": status,
        "verdict": "unavailable",
        "justification": reason or status,
        "challenger_model": MODEL,
    }
    write_challenge_block(block)
    append_challenger_log(
        verdict=f"unavailable:{status}",
        justification=reason or status,
        flag_counts={},
    )
    log(f"emitted degradation status: {status} — {reason}")
    sys.exit(0)


def load_prior_briefs(slug: str, limit: int = 2) -> list[tuple[str, str]]:
    """Return [(filename, content)] of most recent `limit` published briefs."""
    brief_dir = REPO_ROOT / "content" / "monitors" / slug
    if not brief_dir.is_dir():
        return []
    briefs = sorted(
        [p for p in brief_dir.glob("*-weekly-brief.md") if p.is_file()],
        key=lambda p: p.name,
        reverse=True,
    )[:limit]
    out = []
    for p in briefs:
        try:
            txt = p.read_text(encoding="utf-8")
            out.append((p.name, txt[:8000]))
        except Exception:
            pass
    return out


def main() -> None:
    if not MONITOR_SLUG:
        print("ERROR: MONITOR_SLUG env var not set", file=sys.stderr)
        sys.exit(1)
    if not API_KEY:
        emit_status("unavailable", "PPLX_API_KEY not set")

    # ── Load skeleton prompt ────────────────────────────────────────────────
    if not SKELETON_PROMPT.exists():
        emit_status("unavailable", f"skeleton prompt missing at {SKELETON_PROMPT}")
    skeleton = SKELETON_PROMPT.read_text(encoding="utf-8")

    # ── Load guardrails (monitor-specific) ──────────────────────────────────
    guardrail_path = REPO_ROOT / "pipeline" / "monitors" / MONITOR_SLUG / "methodology-guardrails.md"
    if not guardrail_path.exists():
        emit_status("no_guardrails", f"guardrail file missing at {guardrail_path}")
    guardrails = guardrail_path.read_text(encoding="utf-8")

    # ── Load synthesis (latest) ─────────────────────────────────────────────
    # Two candidate locations per current pipeline convention
    synth_candidates = [
        REPO_ROOT / "pipeline" / "monitors" / MONITOR_SLUG / "synthesised" / "synthesis-latest.json",
    ]
    synthesis = None
    synth_source = None
    for p in synth_candidates:
        if p.exists():
            try:
                synthesis = json.loads(p.read_text(encoding="utf-8"))
                synth_source = str(p.relative_to(REPO_ROOT))
                break
            except Exception as e:
                log(f"WARNING: could not parse {p}: {e}")
    if synthesis is None:
        emit_status("no_synthesis", "synthesis-latest.json not found or unreadable")

    # ── Load prior briefs for overfit detection ────────────────────────────
    prior = load_prior_briefs(MONITOR_SLUG, limit=2)

    # ── Assemble user message ───────────────────────────────────────────────
    monitor_name = synthesis.get("_meta", {}).get("monitor_slug", MONITOR_SLUG)
    user_parts = [
        skeleton
            .replace("{{MONITOR_NAME}}", monitor_name)
            .replace("{{GUARDRAIL_BLOCK}}", guardrails[:12000]),
        f"## SYNTHESIS UNDER REVIEW (source: {synth_source})\n\n"
        + json.dumps(synthesis, indent=2, ensure_ascii=False)[:32000],
    ]
    for name, txt in prior:
        user_parts.append(f"## PRIOR BRIEF FOR OVERFIT COMPARISON: {name}\n\n{txt}")

    user_msg = "\n\n---\n\n".join(user_parts)
    if len(user_msg) > 80000:
        log(f"user_msg truncated {len(user_msg)} → 80000")
        user_msg = user_msg[:80000]

    system_msg = (
        "You are an adversarial epistemic auditor. You are paid to find weaknesses "
        "in the attached synthesis. A null_challenge_week is acceptable only if you "
        "have genuinely tried to break the brief across the full failure taxonomy "
        "and the guardrail block. Use web search to verify claims and to search "
        "for counter-evidence. Respond with a single valid JSON object matching "
        "the response_format schema — flat findings array with per-finding severity "
        "and categories. No markdown fences. No explanatory text outside the JSON."
    )

    prompt_hash = hashlib.sha256((skeleton + guardrails).encode("utf-8")).hexdigest()[:16]

    # ── Load response schema for structured output ─────────────────────────
    response_schema = None
    if RESPONSE_SCHEMA.exists():
        try:
            response_schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"WARNING: response schema unreadable: {e}")

    request_body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 8000,
        "temperature": 0.1,
    }
    if response_schema:
        request_body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"schema": response_schema},
        }
        log("using structured output (response_format)")

    # ── Call sonar-pro ──────────────────────────────────────────────────────
    t0 = time.time()
    try:
        log(f"calling {MODEL} (guardrails={len(guardrails)}B, synth={len(json.dumps(synthesis))}B)")
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=request_body,
            timeout=300,
        )
        if resp.status_code == 429:
            log("429 — waiting 60s and retrying once")
            time.sleep(60)
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=request_body,
                timeout=300,
            )
        resp.raise_for_status()
    except Exception as e:
        log_incident(monitor=MONITOR_SLUG, stage="challenger",
                     incident_type="api_error", severity="warning",
                     detail=f"sonar-pro call failed: {e}")
        emit_status("unavailable", f"sonar-pro call failed: {e}")
        return  # unreachable; for type checker

    duration_ms = int((time.time() - t0) * 1000)
    raw = resp.json()["choices"][0]["message"]["content"].strip()

    # ── Parse challenger verdict ────────────────────────────────────────────
    try:
        verdict_obj = json.loads(raw)
    except json.JSONDecodeError as e:
        log_incident(monitor=MONITOR_SLUG, stage="challenger",
                     incident_type="json_parse_error", severity="warning",
                     detail=f"{e}", raw_snippet=raw[:500])
        log(f"JSON parse error: {e}")
        block = {
            "status": "parse_error",
            "verdict": "unavailable",
            "justification": f"challenger returned invalid JSON: {e}",
            "raw_snippet": raw[:500],
            "challenger_model": MODEL,
            "challenger_prompt_hash": prompt_hash,
        }
        write_challenge_block(block, duration_ms=duration_ms)
        append_challenger_log("unavailable:parse_error", str(e), {})
        sys.exit(0)

    # ── Assemble _challenge block per v1.0 flat-findings schema ─────────────
    findings = verdict_obj.get("findings", []) or []
    if not isinstance(findings, list):
        findings = []

    # Count by severity
    sev_counter = Counter()
    cat_counter = Counter()
    for f in findings:
        if not isinstance(f, dict):
            continue
        sev = f.get("severity", "info")
        sev_counter[sev] += 1
        for c in (f.get("categories") or []):
            cat_counter[c] += 1

    hard = sev_counter.get("hard_flag", 0)
    soft = sev_counter.get("soft_flag", 0)
    info = sev_counter.get("info", 0)
    top_category = cat_counter.most_common(1)[0][0] if cat_counter else "-"

    # Verdict — prefer new verdict_preliminary.overall, fall back to legacy fields
    vp = verdict_obj.get("verdict_preliminary") or {}
    verdict = (
        vp.get("overall")
        or verdict_obj.get("verdict")
        or verdict_obj.get("overall_verdict", {}).get("verdict")
        or "publish"
    )
    justification = (
        vp.get("justification")
        or verdict_obj.get("justification")
        or verdict_obj.get("overall_verdict", {}).get("justification")
        or ""
    )

    flag_counts = {
        "findings": len(findings),
        "hard": hard,
        "soft": soft,
        "info": info,
        "top_category": top_category,
    }

    challenge = {
        "challenger_schema_version": "1.0",
        "challenger_model": MODEL,
        "challenger_prompt_hash": prompt_hash,
        "ts": now_iso(),
        "duration_ms": duration_ms,
        "verdict": verdict,
        "justification": justification,
        "null_challenge_week": bool(verdict_obj.get("null_challenge_week", False)),
        "null_challenge_reason": verdict_obj.get("null_challenge_reason"),
        "flag_counts": flag_counts,
        "findings": findings,
        "status": "ok",
    }

    write_challenge_block(challenge, duration_ms=duration_ms)

    append_challenger_log(
        verdict=verdict,
        justification=justification,
        flag_counts=flag_counts,
    )
    log(f"verdict={verdict} duration_ms={duration_ms} flag_counts={flag_counts}")


if __name__ == "__main__":
    main()

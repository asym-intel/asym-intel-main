"""
Token Intensity Monitor — asym-intel.info
Version 2.0 · April 2026

Calculates TIM, manages cascade state machine, and writes to a
SEPARATE ops-metrics file (not persistent-state.json) to keep
epistemic state clean from operational telemetry.

Integration point: Called by Collector/Synthesiser/Analyst workflows
after each Perplexity API call. Layer 1D State Engine reads the
ops-metrics output deterministically.
"""
import json
import os
import statistics
from datetime import datetime
from enum import Enum


class CascadeState(Enum):
    """Governed state machine for research-loop detection."""
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    CASCADE_DETECTED = "CASCADE_DETECTED"
    MITIGATED = "MITIGATED"


# ── Thresholds ──────────────────────────────────────────────
TIM_HIGH = 0.8          # Deep synthesis / possible loop
TIM_LOW = 0.2           # Surface-level skimming risk
SPIKE_FACTOR = 1.5      # 50% above 4-week average
CITATION_LOOP = 30      # High citations with low diversity
HISTORY_WINDOW = 12     # Weeks of history to retain
BMR_WINDOW = 4          # Weeks for Basal Metabolic Rate calc
INTENSITY_DIVISOR = 2000 # Token-to-intensity normalisation


def load_ops_metrics(ops_metrics_path: str) -> dict:
    """Load ops-metrics.json for the monitor. Create if missing."""
    if os.path.exists(ops_metrics_path):
        with open(ops_metrics_path, "r") as f:
            return json.load(f)
    return {"usage_history": [], "cascade_state": CascadeState.NORMAL.value}


def save_ops_metrics(ops_metrics_path: str, data: dict) -> None:
    """Persist ops-metrics.json — deterministic, no model calls."""
    os.makedirs(os.path.dirname(ops_metrics_path), exist_ok=True)
    with open(ops_metrics_path, "w") as f:
        json.dump(data, f, indent=2)


def calculate_tim(prompt_tokens: int, completion_tokens: int) -> float:
    """Token Intensity Metric = completion / prompt. Guarded against div/0."""
    if prompt_tokens <= 0:
        return 0.0
    return round(completion_tokens / prompt_tokens, 3)


def compute_analytical_intensity(total_tokens: int) -> int:
    """Bounded 1-10 public intensity score derived from raw token count."""
    return min(10, max(1, round(total_tokens / INTENSITY_DIVISOR)))


def detect_spike(total_tokens: int, history: list) -> bool:
    """True if current run exceeds 150% of the BMR_WINDOW-week average."""
    recent = [h["total_tokens"] for h in history[-BMR_WINDOW:]]
    if len(recent) < BMR_WINDOW:
        return False
    avg = statistics.mean(recent)
    return total_tokens > (avg * SPIKE_FACTOR)


def detect_citation_loop(citations: int, unique_domains: int) -> bool:
    """Detect Reverse Cascade: many citations but low source diversity."""
    if citations >= CITATION_LOOP and unique_domains > 0:
        diversity_ratio = unique_domains / citations
        return diversity_ratio < 0.3
    return False


def advance_cascade_state(
    current_state: str,
    spike_detected: bool,
    citation_loop: bool,
    tim_score: float,
    mitigation_action: str | None = None,
) -> str:
    """
    State machine transitions:
      NORMAL      → ELEVATED      (spike OR high TIM)
      ELEVATED    → CASCADE_DETECTED (spike AND citation loop)
      CASCADE_DETECTED → MITIGATED (mitigation action taken)
      MITIGATED   → NORMAL        (next clean run)
      Any state   → NORMAL        (no alerts for two consecutive runs)
    """
    state = CascadeState(current_state)

    if state == CascadeState.NORMAL:
        if spike_detected or tim_score > TIM_HIGH:
            return CascadeState.ELEVATED.value
        return CascadeState.NORMAL.value

    elif state == CascadeState.ELEVATED:
        if spike_detected and citation_loop:
            return CascadeState.CASCADE_DETECTED.value
        if not spike_detected and tim_score <= TIM_HIGH:
            return CascadeState.NORMAL.value
        return CascadeState.ELEVATED.value

    elif state == CascadeState.CASCADE_DETECTED:
        if mitigation_action:
            return CascadeState.MITIGATED.value
        return CascadeState.CASCADE_DETECTED.value

    elif state == CascadeState.MITIGATED:
        if not spike_detected and tim_score <= TIM_HIGH:
            return CascadeState.NORMAL.value
        return CascadeState.MITIGATED.value

    return CascadeState.NORMAL.value


def monitor_metabolic_load(
    monitor_slug: str,
    current_usage: dict,
    ops_metrics_path: str,
    mitigation_action: str | None = None,
) -> dict:
    """
    Main entry point. Called after each Sonar API run.

    Args:
        monitor_slug:     e.g. "environmental-risks"
        current_usage:    dict with prompt_tokens, completion_tokens,
                          citations, unique_domains (optional)
        ops_metrics_path: path to pipeline/monitors/{slug}/ops/ops-metrics.json
        mitigation_action: optional string if a loop-break was triggered

    Returns:
        log_entry dict with TIM, intensity, cascade state, and alerts.
    """
    ops = load_ops_metrics(ops_metrics_path)
    history = ops.get("usage_history", [])
    prev_cascade = ops.get("cascade_state", CascadeState.NORMAL.value)

    p_tokens = current_usage.get("prompt_tokens", 1)
    c_tokens = current_usage.get("completion_tokens", 0)
    total = p_tokens + c_tokens
    citations = current_usage.get("citations", 0)
    unique_domains = current_usage.get("unique_domains", citations)

    tim_score = calculate_tim(p_tokens, c_tokens)
    intensity = compute_analytical_intensity(total)
    spike = detect_spike(total, history)
    cit_loop = detect_citation_loop(citations, unique_domains)

    new_cascade = advance_cascade_state(
        prev_cascade, spike, cit_loop, tim_score, mitigation_action
    )

    # Build alerts list
    alerts = []
    if tim_score < TIM_LOW:
        alerts.append("SURFACE_SKIM_WARNING")
    if tim_score > TIM_HIGH:
        alerts.append("HIGH_INTENSITY")
    if spike:
        alerts.append("SPIKE_DETECTED")
    if cit_loop:
        alerts.append("CITATION_LOOP")

    log_entry = {
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "monitor_slug": monitor_slug,
        "prompt_tokens": p_tokens,
        "completion_tokens": c_tokens,
        "total_tokens": total,
        "tim_score": tim_score,
        "analytical_intensity": intensity,
        "citations": citations,
        "unique_domains": unique_domains,
        "spike_detected": spike,
        "cascade_state": new_cascade,
        "alerts": alerts,
    }

    # Update history (rolling window)
    history.append(log_entry)
    history = history[-HISTORY_WINDOW:]

    ops["usage_history"] = history
    ops["cascade_state"] = new_cascade
    ops["last_updated"] = log_entry["date"]

    save_ops_metrics(ops_metrics_path, ops)
    return log_entry


# ── Example usage ───────────────────────────────────────────
if __name__ == "__main__":
    usage = {
        "prompt_tokens": 1200,
        "completion_tokens": 8000,
        "citations": 25,
        "unique_domains": 8,
    }
    result = monitor_metabolic_load(
        "environmental-risks",
        usage,
        "pipeline/monitors/environmental-risks/ops/ops-metrics.json",
    )
    print(json.dumps(result, indent=2))
    if result["cascade_state"] != "NORMAL":
        print(f"\n⚠️  {result['monitor_slug']}: {result['cascade_state']}")
        print(f"   TIM={result['tim_score']}  Intensity={result['analytical_intensity']}")

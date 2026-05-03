#!/usr/bin/env python3
"""
role_accountability.py — diagnostic for commons monitor weekly cycles.

Given the artefacts of a single monitor weekly cycle (collector → reasoner →
interpreter → reviewer → composer → applier → publisher), classify per-module
status by **first failed role**. The aim is to separate plumbing failures from
role failures and point at the cheapest likely fix:

    prompt | model | schema | contract | allocator | reviewer
          | composer | publisher | plumbing | data_absence

Diagnostic only. Does not weaken any gate, does not rerun any LLM, does not
mutate artefacts. Reads what the pipeline already wrote on disk.

## Role accountability model

A weekly cycle for one monitor is a chain of stages, each with a *role*:

  collector    — fetch raw evidence relevant to the monitor's modules
  reasoner     — turn raw evidence into pattern signals
  interpreter  — emit structured_claims (one row per claim, with evidence_id,
                 confidence, source, module mapping) AND populate per-module
                 buckets in the interpret artefact
  allocator    — claims must land in their declared module bucket and the
                 module's schema must accept them (combined with interpreter)
  reviewer     — block defective interpret artefacts (R1..R8 checks)
  composer     — convert structured_claims + module buckets into the
                 reader-facing draft without dropping modules
  applier      — apply patches to persistent state, set publication readiness
  publisher    — refuse to publish modules that are silently empty

`plumbing` is orthogonal: a stage's output exists locally but the next stage
cannot see it (path mismatch, repo-divergence, missing latest pointer).

## Per-module classification

For each `module_<n>` we walk the chain and stop at the first failure:

  PASS                       — module reaches publisher with content
  data_absence (PASS)        — module is empty but provenance is explicit
                               (null_signal=True, empty_reason set, and the
                               cycle disposition / collector tells a
                               consistent story)
  collector_failure          — relevant evidence missing from weekly artefact
  reasoner_failure           — collector saw evidence but reasoner emitted
                               nothing routed to this module
  interpreter_failure        — reasoner had signals; interpret artefact
                               module is empty AND structured_claims[] is
                               empty (claims dropped)
  allocator_failure          — structured_claims[] non-empty but no claim
                               maps to this module / module schema rejected
  reviewer_failure           — module would have been valid but a too-strict
                               or too-loose reviewer check blocks the cycle
  composer_failure           — module was populated in interpret/apply but
                               compose-latest dropped it
  publisher_failure          — module empty without provenance reaches
                               publisher (publisher correctly blocks)
  plumbing                   — earlier stage's `*-latest.json` is missing or
                               its content_sha1 doesn't match the next
                               stage's recorded input

`likely_fix_type` is reported alongside `first_failed_role`. A role failure
maps to one of {prompt, model, schema, contract, allocator, reviewer,
composer, publisher, plumbing, data_absence} — see classify_module().

## Output

A flat list of records (one per (monitor, module)) plus a cycle-level
summary. Text or JSON. Nothing is written to disk except by the caller; this
file only emits to stdout.

## Out of scope

- Does not run the LLMs.
- Does not patch any artefact.
- Does not weaken or replace any reviewer or publisher gate.
- Module-shape catalogue is *minimal* and inferred from artefact contents
  (modules list themselves). If a monitor adds a new module type the tool
  treats it generically.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Reuse the publisher's pure helpers — single source of truth for what
# "module body is empty" and "has provenance" mean at the publisher gate.
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "publishers"))
try:
    from publisher import (  # type: ignore
        _module_body_is_empty,
        _find_unprovenanced_empty_modules,
    )
except Exception:  # pragma: no cover — fallback if publisher import fails
    def _module_body_is_empty(module: dict) -> bool:
        if not isinstance(module, dict):
            return False
        meta_keys = {"title", "null_signal", "empty_reason", "fallback_message",
                     "absence_basis"}
        body = {k: v for k, v in module.items() if k not in meta_keys}
        if not body:
            return True
        for v in body.values():
            if isinstance(v, list) and v:
                return False
            if isinstance(v, dict) and v:
                return False
            if isinstance(v, str) and v.strip():
                return False
        return True

    def _find_unprovenanced_empty_modules(report: dict) -> list[str]:
        bad = []
        for k, v in (report or {}).items():
            if not k.startswith("module_") or not isinstance(v, dict):
                continue
            if not _module_body_is_empty(v):
                continue
            if v.get("null_signal") is True and v.get("empty_reason"):
                continue
            bad.append(k)
        return bad


COMMONS_SLUGS = (
    "ai-governance",
    "democratic-integrity",
    "macro-monitor",
    "fimi-cognitive-warfare",
    "european-strategic-autonomy",
    "environmental-risks",
    "conflict-escalation",
)

# Maps role failure -> the cheapest likely fix surface to investigate.
# "likely" not "definitely": a reviewer FAIL might be a real defect upstream;
# a composer drop might be a schema mismatch. The classifier emits the
# first-line surface; analysts override based on advisory_notes etc.
LIKELY_FIX_FOR_ROLE = {
    "collector_failure": "prompt",
    "reasoner_failure": "prompt",
    "interpreter_failure": "prompt",
    "allocator_failure": "schema",
    "reviewer_failure": "reviewer",
    "composer_failure": "composer",
    "publisher_failure": "publisher",
    "plumbing": "plumbing",
    "data_absence": "data_absence",
    "pass": "none",
}

# Confidence scale: how certain the classifier is the assigned role is the
# first failure. "high" = directly inferred from explicit artefact fields;
# "medium" = inferred from cross-stage comparison; "low" = best guess when
# stages disagree or are partially missing.
CONFIDENCE = ("high", "medium", "low")


@dataclass
class StageRef:
    """Pointer to one stage's latest artefact for a monitor cycle."""
    name: str            # e.g. "interpret"
    path: Path           # absolute path to the latest file
    exists: bool
    data: dict | None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.exists and self.error == "" and self.data is not None


@dataclass
class ModuleVerdict:
    """One row of the role-accountability matrix."""
    monitor_slug: str
    module_key: str
    status: str                    # PASS | FAIL
    first_failed_role: str         # see role list above
    likely_fix_type: str
    confidence: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class CycleVerdict:
    monitor_slug: str
    week_ending: str
    cycle_disposition: str
    publication_ready: bool
    hold_reason: str
    plumbing_issues: list[str]
    review_verdict: str
    review_failed_checks: list[str]
    structured_claim_count: int
    triple_extraction_manifest: dict
    modules: list[ModuleVerdict]


# ──────────────────────────────────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────────────────────────────────

# Stage path layout for the commons monitor weekly pipeline.
# Anchored at pipeline/monitors/<slug>/.
STAGE_PATHS = {
    "weekly":    "weekly/weekly-latest.json",
    "reasoner":  "reasoner/reasoner-latest.json",
    "interpret": "synthesised/interpret-latest.json",
    "review":    "synthesised/review-latest.json",
    "compose":   "synthesised/compose-latest.json",
    "apply":     "applied/apply-latest.json",
}


def _load_stage(monitor_root: Path, name: str) -> StageRef:
    """Load one stage's `*-latest.json`. Records errors instead of raising."""
    rel = STAGE_PATHS[name]
    path = monitor_root / rel
    if not path.exists():
        return StageRef(name=name, path=path, exists=False, data=None,
                        error="missing")
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        return StageRef(name=name, path=path, exists=True, data=None,
                        error=f"json_parse_error: {e}")
    except OSError as e:  # pragma: no cover
        return StageRef(name=name, path=path, exists=True, data=None,
                        error=f"os_error: {e}")
    if not isinstance(data, dict):
        return StageRef(name=name, path=path, exists=True, data=None,
                        error="root_not_object")
    return StageRef(name=name, path=path, exists=True, data=data)


def load_cycle(monitor_slug: str,
               repo_root: Path = REPO_ROOT) -> dict[str, StageRef]:
    """Load every stage artefact for one commons monitor's latest cycle."""
    monitor_root = repo_root / "pipeline" / "monitors" / monitor_slug
    return {name: _load_stage(monitor_root, name) for name in STAGE_PATHS}


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def _module_keys(report: dict) -> list[str]:
    """Top-level `module_<n>` keys in numeric order, preserving any padding."""
    keys = [k for k in (report or {}) if k.startswith("module_")]
    def _num(k: str) -> int:
        try:
            return int(k.split("_", 1)[1])
        except ValueError:
            return 1_000_000
    return sorted(keys, key=_num)


def _claim_to_module(claim: dict) -> str | None:
    """Best-effort: extract the module key a structured_claim points at.

    The interpreter spec has gone through several iterations. Accept any of:
      claim["module_key"]    e.g. "module_3"
      claim["target_module"] e.g. "module_3"
      claim["module"]        e.g. 3 or "module_3"
      claim["module_index"]  e.g. 3

    Returns canonical "module_<n>" or None when no mapping is encoded.
    """
    if not isinstance(claim, dict):
        return None
    for k in ("module_key", "target_module", "module"):
        v = claim.get(k)
        if isinstance(v, str) and v.startswith("module_"):
            return v
        if isinstance(v, int):
            return f"module_{v}"
    idx = claim.get("module_index")
    if isinstance(idx, int):
        return f"module_{idx}"
    return None


def _claim_counts_per_module(claims: list) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in claims or []:
        mk = _claim_to_module(c)
        if mk:
            counts[mk] = counts.get(mk, 0) + 1
    return counts


def _review_failed_checks(review: dict | None) -> list[str]:
    if not isinstance(review, dict):
        return []
    return [c.get("check_id") or c.get("id") or "?"
            for c in review.get("checks", [])
            if (c.get("result") or c.get("outcome")) == "FAIL"]


def _content_sha1_recorded(apply_artefact: dict | None,
                            stage_name: str) -> str | None:
    """The applier records the content_sha1 of upstream stage inputs.

    Returns the recorded sha1 string for `stage_name` (e.g. "interpret",
    "review") or None when unavailable.
    """
    if not isinstance(apply_artefact, dict):
        return None
    inputs = apply_artefact.get("inputs") or {}
    s = inputs.get(stage_name)
    if isinstance(s, dict):
        return s.get("content_sha1")
    return None


def _detect_plumbing(stages: dict[str, StageRef]) -> list[str]:
    """Cross-stage plumbing checks. Returns a list of human-readable issues."""
    issues: list[str] = []

    # 1. Each stage's latest pointer must exist (or plumbing/data_absence).
    for name in ("weekly", "reasoner", "interpret", "review", "compose",
                 "apply"):
        s = stages.get(name)
        if s is None or not s.exists:
            issues.append(f"{name}-latest missing at {s.path if s else name}")
            continue
        if s.error:
            issues.append(f"{name}-latest unreadable: {s.error}")

    # 2. apply-latest records content_sha1 for interpret + review; if those
    #    don't match the sha1 the on-disk file produces today, the applier
    #    saw a different artefact than we are diagnosing -> plumbing.
    apply = stages.get("apply")
    if apply and apply.ok:
        for upstream in ("interpret", "review"):
            recorded = _content_sha1_recorded(apply.data, upstream)
            up = stages.get(upstream)
            if recorded and up and up.ok:
                # Compute today's sha1 of the file the applier *named*.
                try:
                    import hashlib
                    h = hashlib.sha1(up.path.read_bytes()).hexdigest()
                    if h != recorded:
                        issues.append(
                            f"{upstream}-latest content_sha1 drift: "
                            f"applier saw {recorded[:8]}, disk has {h[:8]}"
                        )
                except OSError:  # pragma: no cover
                    pass
    return issues


# ──────────────────────────────────────────────────────────────────────────
# Per-module classifier
# ──────────────────────────────────────────────────────────────────────────

def classify_module(
    module_key: str,
    *,
    interpret: dict,
    review: dict | None,
    compose: dict | None,
    apply_artefact: dict | None,
    weekly: dict | None,
    reasoner: dict | None,
    plumbing_issues: list[str],
) -> ModuleVerdict:
    """Decide first_failed_role + likely_fix_type for one module.

    Resolution order (stop at first hit):
      1. plumbing          — any stage missing/sha-drifting
      2. publisher_failure — module empty + unprovenanced AND publication
                              would have proceeded (publication.ready_to_publish
                              true). When the publisher itself is correctly
                              blocking on this same condition, we attribute to
                              the *upstream* role that produced the
                              unprovenanced empty.
      3. composer_failure  — interpret module non-empty but compose dropped it
      4. reviewer_failure  — review verdict blocks but the only failing checks
                              are over-strict for a benign condition
                              (`reviewer_overblock` heuristic, low confidence)
      5. allocator_failure — structured_claims[] non-empty but zero claims map
                              to this module while module body is empty
      6. interpreter_failure — module empty + cycle is material_change AND
                                triple_extraction_manifest claims extractions
                                AND structured_claims[] is empty (claims
                                dropped between manifest and emission)
      7. reasoner_failure  — reasoner emitted nothing for any pattern
                              touching this module's domain
      8. collector_failure — weekly artefact lacks evidence relevant to
                              this module's domain
      9. data_absence (PASS) — module empty but provenance is explicit and
                                cycle disposition is null_cycle/partial_cycle
                                or null_signal_week=True
     10. PASS               — module has content
    """
    interpret = interpret or {}
    module = interpret.get(module_key, {})
    review = review or {}
    apply_artefact = apply_artefact or {}
    compose = compose or {}

    interp_meta = interpret.get("_meta") or {}
    cycle_disposition = (interp_meta.get("cycle_disposition") or "").lower()
    null_signal_week = bool(interp_meta.get("null_signal_week"))
    triple_manifest = interp_meta.get("triple_extraction_manifest") or {}
    det_n = int(triple_manifest.get("deterministic_extractions") or 0)
    llm_n = int(triple_manifest.get("llm_fallback_extractions") or 0)
    manifest_total = det_n + llm_n

    structured_claims = interpret.get("structured_claims") or []
    claim_count = len(structured_claims)
    claim_per_module = _claim_counts_per_module(structured_claims)

    # ── 1. plumbing
    if plumbing_issues:
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="plumbing",
            likely_fix_type="plumbing",
            confidence="high",
            evidence=plumbing_issues[:3],
        )

    # Has content?
    body_empty = _module_body_is_empty(module) if isinstance(module, dict) else True
    has_provenance = (
        isinstance(module, dict)
        and module.get("null_signal") is True
        and bool(module.get("empty_reason"))
    )

    if not body_empty:
        # ── 3. composer_failure: module had content in interpret but compose
        #      dropped it. The composer artefact is reader-facing so we look
        #      at compose["weekly_brief_draft"] and `claim_trace` for any
        #      reference to the module key. Conservative: only flag when the
        #      compose draft exists and explicitly omits this module.
        composer_dropped = _composer_dropped_module(compose, module_key)
        if composer_dropped:
            return ModuleVerdict(
                monitor_slug=interp_meta.get("monitor_slug", "?"),
                module_key=module_key,
                status="FAIL",
                first_failed_role="composer_failure",
                likely_fix_type="composer",
                confidence="medium",
                evidence=[
                    "interpret module has content; compose draft has no "
                    "matching section",
                    f"compose schema: {sorted((compose or {}).keys())[:6]}",
                ],
            )
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="PASS",
            first_failed_role="pass",
            likely_fix_type="none",
            confidence="high",
            evidence=["module body has content"],
        )

    # body is empty from here on.

    # ── 9. data_absence
    if has_provenance and (
        cycle_disposition in {"null_cycle", "partial_cycle"}
        or null_signal_week
    ):
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="PASS",
            first_failed_role="data_absence",
            likely_fix_type="data_absence",
            confidence="high",
            evidence=[
                f"empty_reason={module.get('empty_reason')}",
                f"cycle_disposition={cycle_disposition or 'unset'}",
                f"null_signal_week={null_signal_week}",
            ],
        )

    # ── 2. publisher_failure (defense-in-depth attribution).
    # If the module is empty + unprovenanced AND publication actually went
    # ahead, the publisher gate failed open. When publication held precisely
    # *because* of this condition, the publisher is doing its job and the
    # attribution shifts upstream (to interpreter/allocator below).
    publication = (apply_artefact.get("publication") or {})
    ready_to_publish = bool(publication.get("ready_to_publish"))
    if (not has_provenance) and ready_to_publish:
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="publisher_failure",
            likely_fix_type="publisher",
            confidence="high",
            evidence=[
                "empty unprovenanced module reached published artefact",
                f"publication.ready_to_publish={ready_to_publish}",
            ],
        )

    # ── 6. interpreter_failure: claims dropped between extraction and
    #      structured_claims[]. This is the AGM 2026-05-03 signature.
    if (
        manifest_total > 0
        and claim_count == 0
        and cycle_disposition == "material_change"
    ):
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="interpreter_failure",
            likely_fix_type="prompt",
            confidence="high",
            evidence=[
                f"triple_extraction_manifest claims {manifest_total} "
                f"extractions (det={det_n}, llm={llm_n})",
                "structured_claims[] is empty",
                f"cycle_disposition={cycle_disposition}",
            ],
        )

    # ── 5. allocator_failure: claims emitted but none reach this module.
    if claim_count > 0 and claim_per_module.get(module_key, 0) == 0:
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="allocator_failure",
            likely_fix_type="schema",
            confidence="medium",
            evidence=[
                f"structured_claims has {claim_count} claims; "
                f"0 mapped to {module_key}",
                "module body empty + cycle is material",
            ],
        )

    # ── 4. reviewer over-block: review FAILED only on checks that don't
    #      contradict an empty-with-no-content interpretation. Conservative
    #      heuristic, low confidence — analyst overrides expected.
    if _reviewer_overblocks(review, claim_count, manifest_total):
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="reviewer_failure",
            likely_fix_type="reviewer",
            confidence="low",
            evidence=[
                f"review verdict: {review.get('verdict')}",
                f"failed checks: {_review_failed_checks(review)}",
            ],
        )

    # ── 7/8. reasoner_failure / collector_failure: cycle is material but no
    #          extraction signal at all. Without a per-module domain
    #          taxonomy we can only emit a coarse signal.
    if cycle_disposition == "material_change" and manifest_total == 0:
        # When the module also lacks the empty_reason stamp, the contract
        # break rides on top of whichever upstream stage came up empty —
        # we still attribute the *first* failure (collector or reasoner).
        if reasoner_is_thin(reasoner):
            return ModuleVerdict(
                monitor_slug=interp_meta.get("monitor_slug", "?"),
                module_key=module_key,
                status="FAIL",
                first_failed_role="collector_failure",
                likely_fix_type="prompt",
                confidence="medium",
                evidence=[
                    "material cycle but reasoner_is_thin",
                    f"weekly_developments={len((weekly or {}).get('weekly_developments') or [])}",
                ],
            )
        return ModuleVerdict(
            monitor_slug=interp_meta.get("monitor_slug", "?"),
            module_key=module_key,
            status="FAIL",
            first_failed_role="reasoner_failure",
            likely_fix_type="prompt",
            confidence="medium",
            evidence=[
                "material cycle, collector populated, "
                "but interpreter has no extractions",
            ],
        )

    # ── Fallback: empty module without a recognised upstream cause.
    # Most likely the interpreter forgot to stamp empty_reason on a
    # legitimately empty module — a contract violation. Includes empty
    # modules in null/partial cycles where provenance was simply omitted.
    return ModuleVerdict(
        monitor_slug=interp_meta.get("monitor_slug", "?"),
        module_key=module_key,
        status="FAIL",
        first_failed_role="interpreter_failure",
        likely_fix_type="contract",
        confidence="medium",
        evidence=[
            "module empty, no provenance, no recognised upstream cause",
            f"cycle_disposition={cycle_disposition or 'unset'}",
        ],
    )


def _composer_dropped_module(compose: dict, module_key: str) -> bool:
    """True when interpret has content but compose has no matching section.

    The composer's reader-facing draft is prose (`weekly_brief_draft`) plus
    `claim_trace`. The current AGM composer schema (aim-compose-v1.0) does
    NOT encode per-module keys in the trace — it traces by `brief_offset_*`
    + `trace_type`, so absence of a `module_*` substring is not evidence of
    a drop. We therefore only flag composer-drop when the trace explicitly
    encodes module references and this module key is missing.

    Conservative by design: false-negative >> false-positive here.
    """
    if not isinstance(compose, dict):
        return False
    trace = compose.get("claim_trace")
    if isinstance(trace, dict):
        # dict-shaped trace: {module_key: ...}. If schema uses this shape and
        # this key is absent, the composer dropped it.
        if any(k.startswith("module_") for k in trace.keys()):
            return module_key not in trace
        return False
    if isinstance(trace, list):
        # list-shaped trace: only flag when at least one entry encodes a
        # `module` field — i.e. the schema does carry per-module references.
        encodes_module = any(
            isinstance(e, dict) and "module" in e for e in trace
        )
        if not encodes_module:
            return False
        return not any(
            isinstance(e, dict) and e.get("module") == module_key
            for e in trace
        )
    return False


def _reviewer_overblocks(review: dict | None,
                          claim_count: int,
                          manifest_total: int) -> bool:
    """Heuristic: did the reviewer fail in a way that looks too strict?

    Concretely: the reviewer fails on R6 (manifest != claims) and R8
    (structured_claims empty in material cycle) when the interpreter
    *itself* dropped claims. Those are correct calls — not over-blocks.
    Return True only when the reviewer fails on something that has no
    upstream cause we can find. This is intentionally conservative: most
    runs return False.
    """
    if not isinstance(review, dict):
        return False
    failed = _review_failed_checks(review)
    if not failed:
        return False
    # If R6/R8 fail and the manifest/claims signature points to interpreter
    # drop, it's an interpreter failure (handled earlier), not over-block.
    if "R6" in failed or "R8" in failed:
        if manifest_total > 0 and claim_count == 0:
            return False
    # No further over-block heuristics in v1 — return False to favour
    # placing blame upstream where evidence supports it.
    return False


def reasoner_is_thin(reasoner: dict | None) -> bool:
    """True when reasoner emitted no pattern signals across all buckets."""
    if not isinstance(reasoner, dict):
        return True
    buckets = (
        "capability_tier_reviews",
        "regulatory_milestone_updates",
        "risk_pattern_detections",
        "lab_posture_changes",
        "contested_findings",
    )
    return all(not (reasoner.get(b) or []) for b in buckets)


# ──────────────────────────────────────────────────────────────────────────
# Cycle aggregation
# ──────────────────────────────────────────────────────────────────────────

def diagnose_cycle(monitor_slug: str,
                   repo_root: Path = REPO_ROOT) -> CycleVerdict:
    stages = load_cycle(monitor_slug, repo_root)
    interpret = stages["interpret"].data or {}
    review = stages["review"].data
    compose = stages["compose"].data
    apply_artefact = stages["apply"].data
    weekly = stages["weekly"].data
    reasoner = stages["reasoner"].data

    plumbing_issues = _detect_plumbing(stages)

    interp_meta = interpret.get("_meta") or {}
    apply_pub = (apply_artefact or {}).get("publication") or {}

    module_keys = _module_keys(interpret)
    verdicts = [
        classify_module(
            mk,
            interpret=interpret,
            review=review,
            compose=compose,
            apply_artefact=apply_artefact,
            weekly=weekly,
            reasoner=reasoner,
            plumbing_issues=plumbing_issues,
        )
        for mk in module_keys
    ]

    return CycleVerdict(
        monitor_slug=monitor_slug,
        week_ending=interp_meta.get("week_ending", "?"),
        cycle_disposition=interp_meta.get("cycle_disposition", "?"),
        publication_ready=bool(apply_pub.get("ready_to_publish")),
        hold_reason=str(apply_pub.get("hold_reason") or ""),
        plumbing_issues=plumbing_issues,
        review_verdict=str((review or {}).get("verdict") or "?"),
        review_failed_checks=_review_failed_checks(review),
        structured_claim_count=len(interpret.get("structured_claims") or []),
        triple_extraction_manifest=interp_meta.get(
            "triple_extraction_manifest") or {},
        modules=verdicts,
    )


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def _format_text(cycles: list[CycleVerdict]) -> str:
    out: list[str] = []
    for cv in cycles:
        out.append(f"## {cv.monitor_slug}  week_ending={cv.week_ending}  "
                   f"disposition={cv.cycle_disposition}")
        out.append(f"   publication_ready={cv.publication_ready}  "
                   f"hold_reason={cv.hold_reason or '-'}")
        out.append(f"   review_verdict={cv.review_verdict}  "
                   f"failed_checks={cv.review_failed_checks or '-'}")
        out.append(f"   structured_claims={cv.structured_claim_count}  "
                   f"manifest={cv.triple_extraction_manifest or '-'}")
        if cv.plumbing_issues:
            out.append(f"   plumbing: {cv.plumbing_issues}")
        out.append("")
        out.append(f"   {'module':10}  {'status':5}  "
                   f"{'first_failed_role':22}  {'likely_fix':12}  "
                   f"{'conf':6}  evidence")
        for mv in cv.modules:
            ev = "; ".join(mv.evidence)[:80]
            out.append(
                f"   {mv.module_key:10}  {mv.status:5}  "
                f"{mv.first_failed_role:22}  {mv.likely_fix_type:12}  "
                f"{mv.confidence:6}  {ev}"
            )
        out.append("")
    return "\n".join(out)


def _format_json(cycles: list[CycleVerdict]) -> str:
    return json.dumps(
        {"cycles": [asdict(cv) for cv in cycles]},
        indent=2,
        sort_keys=True,
        default=str,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Role-accountability diagnostic for commons monitor "
                    "weekly cycles. Classifies each module by first failed "
                    "role + likely fix type."
    )
    parser.add_argument(
        "--monitor",
        action="append",
        default=[],
        metavar="SLUG",
        help="Monitor slug (e.g. ai-governance). May be passed multiple "
             "times. Default: every commons slug.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repo root (default: this checkout).",
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    slugs = args.monitor or list(COMMONS_SLUGS)
    repo_root = Path(args.repo_root)

    cycles = [diagnose_cycle(slug, repo_root) for slug in slugs]

    if args.json:
        print(_format_json(cycles))
    else:
        print(_format_text(cycles))

    # Exit code: 0 iff every module either PASS or data_absence (PASS).
    any_fail = any(
        mv.status == "FAIL"
        for cv in cycles
        for mv in cv.modules
    )
    return 1 if any_fail else 0


__all__ = [
    "COMMONS_SLUGS",
    "CycleVerdict",
    "ModuleVerdict",
    "StageRef",
    "classify_module",
    "diagnose_cycle",
    "load_cycle",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())

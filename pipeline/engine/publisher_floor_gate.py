#!/usr/bin/env python3
"""
pipeline/engine/publisher_floor_gate.py

Publish-floor gate for the commons-monitor Publisher Bot.

Called BEFORE the markdown-commit step. Validates a candidate brief against
four floor rules. On failure: raises PublishFloorGateError (aborting the
commit) and writes a structured failure record to
  pipeline/monitors/<monitor>/applied/publish-blocked-<date>.json

Floor rules (all must pass to permit commit):
  1. body_bytes >= configured floor (default 800). Body = stripped of
     frontmatter + whitespace.
  2. patches_actually_applied >= 1 in the apply-debug artefact.
  3. No sentinel pattern: single non-whitespace char, ^[A-Z]\\s*$,
     Jinja2 residue, repeated bare bullets.
  4. body contains >=1 citation marker ([1], [slug], etc.) OR
     frontmatter brief_sources has >=1 URL.

Config: pipeline/engine/publisher_floor_config.json
  {
    "default_body_bytes_floor": 800,
    "overrides": {
      "<monitor-slug>": { "body_bytes_floor": 400 }
    }
  }

Usage:
  from pipeline.engine.publisher_floor_gate import run_floor_gate

  run_floor_gate(
      brief_md_path  = Path("content/monitors/esa/2026-05-14-weekly-brief.md"),
      apply_debug_path = Path("pipeline/monitors/esa/applied/apply-debug-2026-05-14.json"),
      monitor_slug   = "european-strategic-autonomy",
      publish_date   = "2026-05-14",
      repo_root      = Path("."),
  )

  # Silent return = pass. Raises PublishFloorGateError on fail.

Self-check:
  python3 pipeline/engine/publisher_floor_gate.py --self-check

Sprint BX-9-PUBLISH-FLOOR-GATE (AD-2026-05-14-SPRINT-3-BX-READER-IMPACT-BATCH).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ── Exceptions ─────────────────────────────────────────────────────────────

class PublishFloorGateError(RuntimeError):
    """Raised when the publish-floor gate fires.  Abort the commit."""

    def __init__(self, reason: str, details: dict | None = None):
        super().__init__(reason)
        self.reason = reason
        self.details = details or {}


# ── Sentinel patterns ───────────────────────────────────────────────────────

_SENTINEL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("single-char",          re.compile(r"^\S$")),
    ("single-alpha-upper",   re.compile(r"^[A-Z]\s*$", re.MULTILINE)),
    ("jinja2-if-residue",    re.compile(r"\{%\s*if\s+", re.IGNORECASE)),
    ("jinja2-endif-residue", re.compile(r"\{%\s*endif\s*%\}", re.IGNORECASE)),
    ("bare-bullet-sentinel", re.compile(r"(?m)^-\s*$")),
]

# Citation marker patterns (per BRIEF §3.1 rule 4)
_CITATION_RE = re.compile(
    r"\[(?:[0-9]+|[a-zA-Z][a-zA-Z0-9_\-]{2,})\]"  # [1] or [slug_name]
)

# Frontmatter block extractor
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


# ── Config loader ───────────────────────────────────────────────────────────

def _load_config(repo_root: Path) -> dict:
    config_path = repo_root / "pipeline" / "engine" / "publisher_floor_config.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise PublishFloorGateError(
                f"publisher_floor_config.json unreadable: {exc}"
            )
    # Config absence is a gate failure — fail closed.
    raise PublishFloorGateError(
        f"publisher_floor_config.json not found at {config_path}. "
        "Floor gate requires explicit config — fail closed."
    )


def _body_bytes_floor(config: dict, monitor_slug: str) -> int:
    overrides = config.get("overrides") or {}
    mon_override = overrides.get(monitor_slug) or {}
    if "body_bytes_floor" in mon_override:
        return int(mon_override["body_bytes_floor"])
    return int(config.get("default_body_bytes_floor", 800))


# ── Frontmatter / body split ────────────────────────────────────────────────

def _split_frontmatter(md_text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body_text). Body has leading whitespace stripped."""
    m = _FRONTMATTER_RE.match(md_text)
    if m:
        fm = m.group(1)
        body = md_text[m.end():].strip()
        return fm, body
    return "", md_text.strip()


def _extract_brief_sources_urls(frontmatter_block: str) -> list[str]:
    """Cheap YAML parse: extract url: values from brief_sources block."""
    urls = []
    in_brief_sources = False
    for line in frontmatter_block.splitlines():
        if re.match(r"^brief_sources\s*:", line):
            in_brief_sources = True
            continue
        if in_brief_sources:
            # End of list block
            if line and not line.startswith(" ") and not line.startswith("-"):
                in_brief_sources = False
                continue
            url_m = re.search(r'url:\s*["\']?(https?://[^\s"\']+)["\']?', line)
            if url_m:
                urls.append(url_m.group(1))
    return urls


# ── Rule checks ─────────────────────────────────────────────────────────────

def _check_body_length(body: str, floor: int) -> tuple[bool, str]:
    nb = len(body.encode("utf-8"))
    if nb >= floor:
        return True, ""
    return False, f"body_bytes({nb})<{floor}"


def _check_patches_applied(apply_debug: dict) -> tuple[bool, str]:
    # patches_actually_applied can be list or int
    val = apply_debug.get("patches_actually_applied", [])
    count = len(val) if isinstance(val, list) else int(val)
    if count >= 1:
        return True, ""
    return False, f"patches_actually_applied({count})<1"


def _check_sentinel(body: str) -> tuple[bool, str, str | None]:
    """Returns (passed, reason, pattern_name)."""
    for name, pat in _SENTINEL_PATTERNS:
        if pat.search(body):
            return False, f"sentinel_detected:{name}", name
    return True, "", None


def _check_citation(body: str, frontmatter_block: str) -> tuple[bool, str]:
    if _CITATION_RE.search(body):
        return True, ""
    urls = _extract_brief_sources_urls(frontmatter_block)
    if urls:
        return True, ""
    return False, "no_citation_marker_and_no_brief_sources_url"


# ── Failure record writer ───────────────────────────────────────────────────

def _write_blocked_record(
    repo_root: Path,
    monitor_slug: str,
    publish_date: str,
    reason: str,
    rule_failures: list[str],
    apply_debug: dict | None,
) -> Path:
    record_dir = repo_root / "pipeline" / "monitors" / monitor_slug / "applied"
    record_dir.mkdir(parents=True, exist_ok=True)
    record_path = record_dir / f"publish-blocked-{publish_date}.json"
    record = {
        "schema_version": "publish-blocked-v1.0",
        "monitor_slug": monitor_slug,
        "publish_date": publish_date,
        "blocked_at": datetime.now(timezone.utc).isoformat(),
        "floor_failure_reason": reason,
        "rule_failures": rule_failures,
        "apply_debug_summary": {
            "patches_actually_applied": (
                len(apply_debug.get("patches_actually_applied", []))
                if apply_debug and isinstance(apply_debug.get("patches_actually_applied"), list)
                else apply_debug.get("patches_actually_applied") if apply_debug else None
            ),
            "week_ending": apply_debug.get("week_ending") if apply_debug else None,
        } if apply_debug else None,
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record_path


# ── Public API ──────────────────────────────────────────────────────────────

def check_floor_gate(
    brief_md_text: str,
    apply_debug: dict,
    monitor_slug: str,
    repo_root: Path,
) -> dict:
    """Run all four floor rules. Returns a result dict (does not raise).

    Result keys:
      passed              bool
      floor_failure_reason  str or None
      rule_failures       list[str]
      body_bytes          int
      sentinel_detected   bool
      sentinel_pattern    str or None
      patches_actually_applied  int
      citation_count      int
    """
    config = _load_config(repo_root)
    floor = _body_bytes_floor(config, monitor_slug)

    fm_block, body = _split_frontmatter(brief_md_text)
    body_bytes = len(body.encode("utf-8"))
    citation_count = len(_CITATION_RE.findall(body))

    rule_failures: list[str] = []

    # Rule 1: body length
    r1_ok, r1_msg = _check_body_length(body, floor)
    if not r1_ok:
        rule_failures.append(r1_msg)

    # Rule 2: patches applied
    r2_ok, r2_msg = _check_patches_applied(apply_debug)
    if not r2_ok:
        rule_failures.append(r2_msg)

    # Rule 3: sentinel
    r3_ok, r3_msg, sentinel_name = _check_sentinel(body)
    if not r3_ok:
        rule_failures.append(r3_msg)

    # Rule 4: citation
    r4_ok, r4_msg = _check_citation(body, fm_block)
    if not r4_ok:
        rule_failures.append(r4_msg)

    passed = len(rule_failures) == 0
    patches_val = apply_debug.get("patches_actually_applied", [])
    patches_count = len(patches_val) if isinstance(patches_val, list) else int(patches_val)

    return {
        "passed": passed,
        "floor_failure_reason": " AND ".join(rule_failures) if rule_failures else None,
        "rule_failures": rule_failures,
        "body_bytes": body_bytes,
        "sentinel_detected": not r3_ok,
        "sentinel_pattern": (f"single-char:{body}" if sentinel_name == "single-char" and len(body) <= 3
                             else sentinel_name),
        "patches_actually_applied": patches_count,
        "citation_count": citation_count,
    }


def run_floor_gate(
    brief_md_path: Path,
    apply_debug_path: Path,
    monitor_slug: str,
    publish_date: str,
    repo_root: Path,
) -> dict:
    """Load brief + apply-debug and run the floor gate.

    Silent return = pass.
    Raises PublishFloorGateError on failure (also writes blocked record).
    Returns result dict on pass.
    """
    # Load brief
    if not brief_md_path.exists():
        raise PublishFloorGateError(f"Brief not found: {brief_md_path}")
    brief_md_text = brief_md_path.read_text(encoding="utf-8")

    # Load apply-debug (required for rule 2)
    apply_debug: dict = {}
    if apply_debug_path.exists():
        try:
            apply_debug = json.loads(apply_debug_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise PublishFloorGateError(f"apply-debug unreadable: {exc}")
    else:
        # No apply-debug → patches_actually_applied=0 → rule 2 fires
        apply_debug = {"patches_actually_applied": 0}

    result = check_floor_gate(brief_md_text, apply_debug, monitor_slug, repo_root)

    if not result["passed"]:
        blocked_path = _write_blocked_record(
            repo_root=repo_root,
            monitor_slug=monitor_slug,
            publish_date=publish_date,
            reason=result["floor_failure_reason"],
            rule_failures=result["rule_failures"],
            apply_debug=apply_debug,
        )
        print(
            f"  ✗ PUBLISH FLOOR GATE FIRED [{monitor_slug} {publish_date}]\n"
            f"    Reason: {result['floor_failure_reason']}\n"
            f"    Blocked record: {blocked_path}",
            file=sys.stderr,
        )
        raise PublishFloorGateError(
            result["floor_failure_reason"],
            details=result,
        )

    print(f"  ✓ publish floor gate passed [{monitor_slug} {publish_date}] "
          f"body_bytes={result['body_bytes']} patches={result['patches_actually_applied']}")
    return result


# ── Self-check ──────────────────────────────────────────────────────────────

def _self_check() -> None:
    """Smoke-test the gate logic with synthetic inputs. Called via --self-check."""
    import tempfile, os

    print("publisher_floor_gate self-check...")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        # Write config
        config_dir = td_path / "pipeline" / "engine"
        config_dir.mkdir(parents=True)
        (config_dir / "publisher_floor_config.json").write_text(json.dumps({
            "default_body_bytes_floor": 800,
            "overrides": {},
        }))

        good_body = "## Lead Signal\n\nThe EU Council adopted the " + "European Chips Act implementation roadmap. " * 30 + "\n\n[1] https://example.com"
        good_md = f"---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: test\nbrief_sources:\n  - url: \"https://example.com\"\n---\n\n{good_body}"
        good_apply = {"patches_actually_applied": [{"patch_id": "p1"}]}

        result = check_floor_gate(good_md, good_apply, "test-monitor", td_path)
        assert result["passed"], f"Self-check FAIL (should pass): {result}"
        print("  ✓ valid brief passes gate")

        # Sentinel "A" case
        sentinel_md = "---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: test\n---\n\nA"
        result2 = check_floor_gate(sentinel_md, {"patches_actually_applied": 0}, "test-monitor", td_path)
        assert not result2["passed"], "Self-check FAIL (sentinel should be caught)"
        assert result2["sentinel_detected"], "Sentinel should be detected"
        assert result2["patches_actually_applied"] == 0
        print("  ✓ sentinel 'A' + zero patches correctly fires gate")

    print("publisher_floor_gate self-check PASSED")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--self-check", action="store_true")
    p.add_argument("--brief", type=Path, help="Path to brief MD")
    p.add_argument("--apply-debug", type=Path, help="Path to apply-debug JSON")
    p.add_argument("--monitor", type=str)
    p.add_argument("--date", type=str, default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    p.add_argument("--repo-root", type=Path, default=Path("."))
    args = p.parse_args()

    if args.self_check:
        _self_check()
        sys.exit(0)

    if not (args.brief and args.apply_debug and args.monitor):
        print("Usage: publisher_floor_gate.py --brief <path> --apply-debug <path> --monitor <slug> [--date YYYY-MM-DD] [--repo-root <path>]")
        sys.exit(1)

    try:
        run_floor_gate(args.brief, args.apply_debug, args.monitor, args.date, args.repo_root)
        sys.exit(0)
    except PublishFloorGateError as e:
        print(f"GATE FIRED: {e}", file=sys.stderr)
        sys.exit(1)

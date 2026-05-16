"""
tools/test_preflight_wf_script_hyphen.py — smoke fixture for the W7a regex reshape.

Tests the WF-SCRIPT checkout_paths extractor in tools/preflight.py against
the class of workflows that caused 4 skip-list workarounds: those where an
actions/checkout step contains a hyphenated field value (e.g.
`repository: asym-intel/asym-intel-internal`) between `uses:` and `path:`.

Root cause cured: the previous `[^-]*?` quantifier excluded the hyphen
character and stopped at the first `-` in a hyphenated value, leaving
checkout_paths empty. The cure uses `(?!\\n\\s*-\\s)[\\s\\S]` (negative
lookahead sentinel) to allow hyphens within field values while bounding the
scan to the current YAML list-item block.

Four cases:
  1. Checkout step with repository: asym-intel/asym-intel-internal + path: internal
     → extractor must return 'internal'; script under 'internal/' must be skipped.
  2. Checkout step with repository: asym-intel/asym-intel-main (no path:)
     → no path extracted; script existence check runs normally.
  3. Checkout step with no repository field + path: foo
     → extractor must return 'foo'; script under 'foo/' must be skipped.
  4. Workflow with TWO checkout steps — one with hyphenated repo + path, one plain
     → both paths extracted correctly; scripts under each prefix skipped.

Approach: monkey-patch preflight.REPO_ROOT to a tmp_path tree; write synthetic
workflow YAML; invoke check_workflows; inspect Results. Same pattern as
tools/test_preflight_wf_script.py (BRIEF gate-cure-pr338 §3.3).

Authority: W7a WF-SCRIPT regex reshape (fleet-20260516T093336Z).
AD-2026-05-13-CI-GATE-CALIBRATION-DOCTRINE: cure is in the gate.
"""

import sys
import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers (mirrors tools/test_preflight_wf_script.py pattern)
# ---------------------------------------------------------------------------

def _load_preflight(tmp_root: Path):
    """Import (or reimport) preflight with REPO_ROOT patched to tmp_root."""
    if "preflight" in sys.modules:
        del sys.modules["preflight"]

    tools_dir = Path(__file__).resolve().parent
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    import preflight as pf
    pf.REPO_ROOT = tmp_root
    return pf


def _make_wf_dir(tmp_root: Path) -> Path:
    wf_dir = tmp_root / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    return wf_dir


def _run(tmp_root: Path, wf_yaml: str, extra_files: list[str] | None = None):
    """Write a workflow YAML, optionally create extra files, run check_workflows."""
    wf_dir = _make_wf_dir(tmp_root)
    wf_file = wf_dir / "test-hyphen-workflow.yml"
    wf_file.write_text(textwrap.dedent(wf_yaml))

    if extra_files:
        for rel in extra_files:
            target = tmp_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# placeholder\n")

    pf = _load_preflight(tmp_root)
    r = pf.Results()
    pf.check_workflows(r)

    ok_details = [d for (_, d) in r.passed]
    fail_details = [d for (_, d) in r.failed]
    return r, ok_details, fail_details


# ---------------------------------------------------------------------------
# Case 1: checkout with repository: asym-intel/asym-intel-internal + path: internal
# The classic W7a trigger: hyphenated field value between uses: and path:
# ---------------------------------------------------------------------------

def test_case1_hyphenated_repo_with_path(tmp_path):
    """
    Case 1: checkout step has repository: asym-intel/asym-intel-internal and path: internal.
    The extractor must successfully extract 'internal' despite the hyphens in the
    repository field value. The script under internal/ must be skipped (sibling-checkout).
    
    This is the pattern that caused engine-preflight.yml, engine-runtime-audit.yml,
    cf-speed-setup.yml, and _reusable-applier.yml (W6P-c PR #360) to be skip-listed
    or fail the gate.
    """
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v6

              - name: Checkout asym-intel-internal
                uses: actions/checkout@v6
                with:
                  repository: asym-intel/asym-intel-internal
                  token: ${{ secrets.ASYM_ENGINE_PUBLISHER }}
                  path: internal
                  sparse-checkout: |
                    tools/check_applier_manifest_contradiction.py

              - name: Check manifest contradiction
                run: python3 internal/tools/check_applier_manifest_contradiction.py
        """
    r, ok, fail = _run(tmp_path, yaml)

    # The script under internal/ must be skipped (sibling-checkout ok), not failed
    assert any("sibling-checkout" in d and "internal/" in d for d in ok), (
        f"Case 1 FAIL: expected sibling-checkout ok for internal/...; ok={ok} fail={fail}"
    )
    assert not any("does not exist" in d and "internal/" in d for d in fail), (
        f"Case 1 FAIL: internal/... path was falsely flagged as missing; fail={fail}"
    )


# ---------------------------------------------------------------------------
# Case 2: checkout with repository: asym-intel/asym-intel-main but NO path:
# No path extracted; normal existence check runs.
# ---------------------------------------------------------------------------

def test_case2_hyphenated_repo_no_path(tmp_path):
    """
    Case 2: checkout step has repository: asym-intel/asym-intel-main but no path: field.
    No sibling-checkout path should be extracted; scripts are existence-checked normally.
    A missing script must still be reported as a failure (no false-skip).
    """
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout main repo
                uses: actions/checkout@v6
                with:
                  repository: asym-intel/asym-intel-main
                  token: ${{ secrets.GITHUB_TOKEN }}

              - run: python3 tools/missing-script.py
        """
    r, ok, fail = _run(tmp_path, yaml)

    # Script must be checked for existence (no path: was given, so no sibling-skip)
    assert any("missing-script.py" in d and "does not exist" in d for d in fail), (
        f"Case 2 FAIL: expected failure for missing script when no path: field; ok={ok} fail={fail}"
    )
    assert not any("sibling-checkout" in d for d in ok if "missing-script" in d), (
        f"Case 2 FAIL: missing-script was falsely skipped as sibling-checkout; ok={ok}"
    )


# ---------------------------------------------------------------------------
# Case 3: checkout with no repository field + path: foo
# Same as original case 5 in test_preflight_wf_script.py but named explicitly.
# ---------------------------------------------------------------------------

def test_case3_no_repository_field_with_path(tmp_path):
    """
    Case 3: checkout step has no repository: field, only path: foo.
    The extractor must return 'foo'; scripts under foo/ must be skipped.
    """
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout repo into foo
                uses: actions/checkout@v6
                with:
                  path: foo

              - run: python3 foo/tools/script.py
        """
    r, ok, fail = _run(tmp_path, yaml)

    assert any("sibling-checkout" in d and "foo/" in d for d in ok), (
        f"Case 3 FAIL: expected sibling-checkout ok for foo/...; ok={ok} fail={fail}"
    )
    assert not any("does not exist" in d and "foo/" in d for d in fail), (
        f"Case 3 FAIL: foo/... path was falsely flagged as missing; fail={fail}"
    )


# ---------------------------------------------------------------------------
# Case 4: workflow with TWO checkout steps — one with hyphenated repo + path,
# one without path. Both paths extracted correctly.
# ---------------------------------------------------------------------------

def test_case4_two_checkout_steps_mixed(tmp_path):
    """
    Case 4: workflow has two checkout steps:
      (a) plain checkout with no path (default checkout of current repo)
      (b) checkout of asym-intel/asym-intel-internal with path: internal (hyphenated)
    
    Expected:
      - 'internal' extracted as sibling-checkout path → internal/tools/x.py skipped
      - tools/local.py NOT skipped → existence-checked; must exist to pass
    """
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout main
                uses: actions/checkout@v6

              - name: Checkout internal
                uses: actions/checkout@v6
                with:
                  repository: asym-intel/asym-intel-internal
                  token: ${{ secrets.ASYM_ENGINE_PUBLISHER }}
                  path: internal

              - run: python3 internal/tools/x.py
              - run: python3 tools/local.py
        """

    # Create tools/local.py so its existence check passes
    r, ok, fail = _run(tmp_path, yaml, extra_files=["tools/local.py"])

    # internal/tools/x.py → sibling-checkout skip
    assert any("sibling-checkout" in d and "internal/" in d for d in ok), (
        f"Case 4 FAIL: expected sibling-checkout ok for internal/...; ok={ok} fail={fail}"
    )
    assert not any("does not exist" in d and "internal/" in d for d in fail), (
        f"Case 4 FAIL: internal/... falsely flagged as missing; fail={fail}"
    )

    # tools/local.py → normal existence check (it exists, so must be ok)
    assert any("tools/local.py exists" in d for d in ok), (
        f"Case 4 FAIL: tools/local.py existence check not ok; ok={ok} fail={fail}"
    )

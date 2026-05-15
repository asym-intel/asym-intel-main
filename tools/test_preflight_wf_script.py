"""
tools/test_preflight_wf_script.py — pytest fixture for the WF-SCRIPT check in preflight.py.

7 cases per BRIEF gate-cure-pr338 §3.3:
  1. Plain script in repo root → ok
  2. Plain script that doesn't exist → fail
  3. _internal/script.py → ok (legacy runtime-checkout message)
  4. actions/checkout + path: main + python3 main/tools/x.py → ok (sibling-checkout)
     REGRESSION TEST for PR #338 false alarm
  5. actions/checkout + path: internal + python3 internal/tools/y.py → ok (sibling-checkout)
  6. actions/checkout with NO path: field + python3 tools/z.py (missing) → fail
  7. path: main present BUT python3 some-other-dir/x.py (leading dir not a checkout-path) → fail

Approach: import preflight, monkey-patch preflight.REPO_ROOT to a tmp_path
tree, write synthetic workflow YAML files, invoke check_workflows, inspect
Results. This keeps preflight.py untouched (§3.2 is the only allowed edit).
"""

import importlib
import sys
import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_preflight(tmp_root: Path):
    """
    Import (or reimport) preflight with REPO_ROOT patched to tmp_root.
    Returns the module with REPO_ROOT already patched.
    """
    # Force a clean import each time so REPO_ROOT is re-evaluated via our patch.
    if "preflight" in sys.modules:
        del sys.modules["preflight"]

    # tools/ directory in the REAL repo — needed so `import preflight` works.
    tools_dir = Path(__file__).resolve().parent
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    import preflight as pf
    # Patch the module-level REPO_ROOT so check_workflows sees our tmp tree.
    pf.REPO_ROOT = tmp_root
    return pf


def _make_wf_dir(tmp_root: Path) -> Path:
    wf_dir = tmp_root / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    return wf_dir


def _run(tmp_root: Path, wf_yaml: str, extra_files: list[str] | None = None):
    """
    Write a single workflow YAML, optionally create extra files (repo-root relative),
    run check_workflows, return (results, ok_details, fail_details).
    """
    wf_dir = _make_wf_dir(tmp_root)
    wf_file = wf_dir / "test-workflow.yml"
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
# Case 1 — plain script in repo root → ok
# ---------------------------------------------------------------------------

def test_plain_script_exists(tmp_path):
    """Case 1: workflow references tools/real.py which exists → WF-SCRIPT ok."""
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v6
              - run: python3 tools/real.py
        """
    r, ok, fail = _run(tmp_path, yaml, extra_files=["tools/real.py"])
    assert any("tools/real.py exists" in d for d in ok), f"Expected ok for real.py; ok={ok} fail={fail}"
    assert not fail, f"Expected no failures; fail={fail}"


# ---------------------------------------------------------------------------
# Case 2 — plain script that doesn't exist → fail
# ---------------------------------------------------------------------------

def test_plain_script_missing(tmp_path):
    """Case 2: workflow references tools/missing.py which does NOT exist → WF-SCRIPT fail."""
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v6
              - run: python3 tools/missing.py
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("tools/missing.py" in d and "does not exist" in d for d in fail), \
        f"Expected fail for missing.py; ok={ok} fail={fail}"


# ---------------------------------------------------------------------------
# Case 3 — _internal/ prefix → ok with legacy message
# ---------------------------------------------------------------------------

def test_internal_prefix_skip(tmp_path):
    """Case 3: _internal/script.py → ok (legacy runtime-checkout pattern)."""
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v6
              - run: python3 _internal/tools/gate.py
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("runtime checkout from internal repo" in d for d in ok), \
        f"Expected legacy-skip ok; ok={ok} fail={fail}"
    assert not fail, f"Expected no failures; fail={fail}"


# ---------------------------------------------------------------------------
# Case 4 — REGRESSION TEST: path: main + python3 main/tools/x.py → ok (sibling)
# ---------------------------------------------------------------------------

def test_sibling_checkout_path_main(tmp_path):
    """
    Case 4 (REGRESSION for PR #338):
    Workflow uses actions/checkout@v6 with path: main AND python3 main/tools/x.py.
    main/tools/x.py does NOT exist under REPO_ROOT.
    The scanner must recognise 'main' as a sibling-checkout path and skip the
    existence check, emitting ok with sibling-checkout message.
    """
    yaml = """\
        on: push
        jobs:
          coverage:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout main repo
                uses: actions/checkout@v6
                with:
                  path: main
              - name: Checkout internal repo
                uses: actions/checkout@v6
                with:
                  repository: asym-intel/asym-intel-internal
                  token: ${{ secrets.ASYM_ENGINE_PUBLISHER }}
                  path: internal
              - name: Run gate
                run: |
                  python3 main/tools/check_persistent_state_schema_coverage.py \\
                    --repo-root main \\
                    --meta-schema internal/policy/contracts/meta-schema.json
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("sibling-checkout" in d and "main/" in d for d in ok), \
        f"Expected sibling-checkout ok for main/tools/...; ok={ok} fail={fail}"
    assert not any("does not exist" in d for d in fail), \
        f"Sibling-checkout path falsely flagged as missing; fail={fail}"


# ---------------------------------------------------------------------------
# Case 5 — path: internal + python3 internal/tools/y.py → ok (sibling)
# ---------------------------------------------------------------------------

def test_sibling_checkout_path_internal(tmp_path):
    """Case 5: path: internal and python3 internal/tools/y.py → ok (sibling-checkout)."""
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout main
                uses: actions/checkout@v6
                with:
                  path: main
              - name: Checkout internal
                uses: actions/checkout@v6
                with:
                  path: internal
              - run: python3 internal/tools/y.py
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("sibling-checkout" in d and "internal/" in d for d in ok), \
        f"Expected sibling-checkout ok for internal/tools/y.py; ok={ok} fail={fail}"
    assert not any("does not exist" in d for d in fail), \
        f"Sibling-checkout path falsely flagged; fail={fail}"


# ---------------------------------------------------------------------------
# Case 6 — no path: field on checkout + python3 tools/z.py (missing) → fail
# ---------------------------------------------------------------------------

def test_no_path_field_existence_still_checked(tmp_path):
    """
    Case 6: actions/checkout with NO path: field. tools/z.py does not exist.
    No false-skip should occur — the scanner must still check local existence.
    """
    yaml = """\
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v6
              - run: python3 tools/z.py
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("tools/z.py" in d and "does not exist" in d for d in fail), \
        f"Expected fail when no path: field and script missing; ok={ok} fail={fail}"


# ---------------------------------------------------------------------------
# Case 7 — path: main BUT python3 some-other-dir/x.py → fail (no over-permissive skip)
# ---------------------------------------------------------------------------

def test_path_main_but_unrelated_leading_dir(tmp_path):
    """
    Case 7: path: main is a checkout-path, but the script reference starts with
    'some-other-dir/' — not a known checkout-path. Must still fail if file absent.
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
                  path: main
              - run: python3 some-other-dir/x.py
        """
    r, ok, fail = _run(tmp_path, yaml)
    assert any("some-other-dir/x.py" in d and "does not exist" in d for d in fail), \
        f"Expected fail for unrelated leading dir; ok={ok} fail={fail}"
    # 'main' checkout-path must not cause 'some-other-dir/...' to be skipped
    assert not any("sibling-checkout" in d and "some-other-dir" in d for d in ok), \
        f"Over-permissive skip detected; ok={ok}"

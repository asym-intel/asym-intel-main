#!/usr/bin/env python3
"""Fixture suite for tools/lint_reusable_input_uniformity.py.

Runs BEFORE the live scan in the workflow (PREFLIGHT-KNOWHOW §2 pattern,
mirrored from tools/test_preflight_parity.py). If the parser regresses,
this fails first with a clear test name.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import dedent


SCRIPT = Path(__file__).parent / "lint_reusable_input_uniformity.py"

UNIFORM_FIXTURE = {
    "_reusable-alpha.yml": dedent(
        """\
        name: alpha
        on:
          workflow_call:
            inputs:
              slug:
                type: string
                required: true
              force:
                type: boolean
                default: false
        """
    ),
    "_reusable-beta.yml": dedent(
        """\
        name: beta
        on:
          workflow_call:
            inputs:
              slug:
                type: string
                required: true
              force:
                type: boolean
                default: false
        """
    ),
}

DRIFT_FIXTURE = {
    "_reusable-alpha.yml": dedent(
        """\
        name: alpha
        on:
          workflow_call:
            inputs:
              force:
                type: boolean
                default: false
        """
    ),
    "_reusable-beta.yml": dedent(
        """\
        name: beta
        on:
          workflow_call:
            inputs:
              force:
                type: string
                default: 'false'
        """
    ),
}

SOLO_INPUT_FIXTURE = {
    "_reusable-alpha.yml": dedent(
        """\
        name: alpha
        on:
          workflow_call:
            inputs:
              only_here:
                type: string
                required: false
        """
    ),
    "_reusable-beta.yml": dedent(
        """\
        name: beta
        on:
          workflow_call:
            inputs:
              also_only_here:
                type: boolean
                default: false
        """
    ),
}


def run_lint(fixture: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        workflows = Path(tmp) / ".github" / "workflows"
        workflows.mkdir(parents=True)
        for name, body in fixture.items():
            (workflows / name).write_text(body)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), tmp],
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout + proc.stderr


def assert_eq(label: str, got, want) -> None:
    if got != want:
        print(f"FAIL {label}: got {got!r}, want {want!r}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    rc, out = run_lint(UNIFORM_FIXTURE)
    assert_eq("uniform: exit 0", rc, 0)
    if "OK:" not in out:
        print(f"FAIL uniform: expected 'OK:' in output, got:\n{out}", file=sys.stderr)
        return 1
    if "INPUT-TYPE-DRIFT" in out:
        print(f"FAIL uniform: unexpected drift header in output:\n{out}", file=sys.stderr)
        return 1

    rc, out = run_lint(DRIFT_FIXTURE)
    assert_eq("drift: exit 1", rc, 1)
    if "INPUT-TYPE-DRIFT:" not in out:
        print(f"FAIL drift: expected 'INPUT-TYPE-DRIFT:' marker, got:\n{out}", file=sys.stderr)
        return 1
    if "input 'force'" not in out:
        print(f"FAIL drift: expected \"input 'force'\" line, got:\n{out}", file=sys.stderr)
        return 1
    if "type 'boolean'" not in out or "type 'string'" not in out:
        print(f"FAIL drift: expected both 'boolean' and 'string' in report, got:\n{out}", file=sys.stderr)
        return 1

    rc, out = run_lint(SOLO_INPUT_FIXTURE)
    assert_eq("solo inputs: exit 0 (each input appears only once across the corpus)", rc, 0)

    print("All fixture cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

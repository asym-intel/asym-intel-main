#!/usr/bin/env python3
"""
preflight_ui_shim.py — asym-intel-main shim for engine-tools/preflight_ui.py.

Fetches preflight_ui.py from asym-intel-internal via the ENGINE_INTERNAL_READ_TOKEN
secret, caches it in .engine-tools-cache/ (gitignored), and execs it against the
current repo with --site asym-intel.info.

Per the 2026-04-19 parity audit shim-dispatch pattern.
Authorising decision: AD-2026-04-19-02 (SPEC-ENGINE-UI-FLOOR).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / ".engine-tools-cache"
CACHED_SCRIPT = CACHE_DIR / "preflight_ui.py"

REPO = "asym-intel/asym-intel-internal"
REMOTE_PATH = "engine-tools/preflight_ui.py"
SITE = "asym-intel.info"


def _fetch_script() -> None:
    """Pull preflight_ui.py from asym-intel-internal into local cache."""
    CACHE_DIR.mkdir(exist_ok=True)

    token = os.environ.get("ENGINE_INTERNAL_READ_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print(
            "preflight_ui_shim: ENGINE_INTERNAL_READ_TOKEN not set; "
            "falling back to gh cli auth",
            file=sys.stderr,
        )

    cmd = [
        "gh", "api",
        f"/repos/{REPO}/contents/{REMOTE_PATH}",
        "--jq", ".content",
    ]
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(
            f"preflight_ui_shim: failed to fetch {REMOTE_PATH}: {result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)

    import base64
    content = base64.b64decode(result.stdout.strip()).decode("utf-8")
    CACHED_SCRIPT.write_text(content, encoding="utf-8")


def main() -> int:
    _fetch_script()

    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(CACHED_SCRIPT), str(repo_root), "--site", SITE],
        env=os.environ.copy(),
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

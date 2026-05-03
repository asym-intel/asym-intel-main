#!/usr/bin/env python3
"""
Pipeline-triggers manifest loader + expected-fire enumerator.

Reads `asym-intel-internal:ops/pipeline-triggers.yml` (the canonical pipeline
trigger manifest, manifest_version 1.0.0) and exposes:

  - load_manifest(token=None) -> dict
        Fetch + parse the manifest. In-memory cached for the producer run.

  - iter_expected_fires(manifest, window_start, window_end) -> list[dict]
        Expand every active trigger source into the concrete (workflow, datetime)
        pairs that should have fired between `window_start` and `window_end`
        (both inclusive, both timezone-aware UTC).

This helper is consumed by `compute_trigger_health()` in
`update-pipeline-status.py` to populate the `_trigger_health` block in
`pipeline-status.json` (schema v4.0).

Scope (Sprint BH BH.2 BRIEF):
  IN:  cf_dispatcher_schedule.active_crons[] (with non-empty dispatches[])
       github_native_schedules[] (without state: disabled_manually)
  OUT: workflow_run_chains, observers, orphan_workflows, inactive_branches,
       observers without a manifest cron: field, github_workflow_dispatch,
       repository_dispatch.

DOW convention:
  - cf_dispatcher_schedule.active_crons[].dow uses Cloudflare-Quartz indexing:
        0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
  - github_native_schedules[].cron field 5 uses standard cron indexing:
        0,7=Sun, 1=Mon, ..., 6=Sat
  - Python `datetime.weekday()` returns 0=Mon..6=Sun.
  We normalise everything to a Python-weekday set internally.

Tolerance for actual-vs-expected match is set in the consumer
(`compute_trigger_health()` in update-pipeline-status.py), not here. This module
only enumerates expected fires.

Sprint authority: AD-2026-04-30-BH §BH.2; BH.2 BRIEF.
"""

import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# yaml is a hard dependency. The producer already runs on a runner with PyYAML
# installed (used by other ops scripts). If absent we fail loudly rather than
# silently degrading the trigger-health signal.
try:
    import yaml
except ImportError as exc:  # pragma: no cover — surfaced at runtime in CI
    raise ImportError(
        "PyYAML is required by ops/_pipeline_triggers_loader.py "
        "(reads ops/pipeline-triggers.yml from asym-intel-internal). "
        "Install with `pip install pyyaml`."
    ) from exc


INTERNAL_REPO = "asym-intel/asym-intel-internal"
MAIN_REPO = "asym-intel/asym-intel-main"
MANIFEST_PATH = "ops/pipeline-triggers.yml"

# Manifest DOW (Quartz: 0=Sun..6=Sat) -> Python weekday (0=Mon..6=Sun)
_QUARTZ_TO_PY = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}

# Standard cron DOW (0,7=Sun, 1=Mon..6=Sat) -> Python weekday (0=Mon..6=Sun)
_CRON_TO_PY = {0: 6, 7: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}


# ─── Manifest fetch ─────────────────────────────────────────────

_MANIFEST_CACHE = {"data": None, "sha": None}


def _gh_api_raw(endpoint, token=None):
    """Call gh api and return stdout. Mirrors gh_api() in the producer."""
    cmd = ["gh", "api", endpoint]
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(
            f"  WARNING: gh api {endpoint} failed: {result.stderr[:200]}",
            file=sys.stderr,
        )
        return None
    return result.stdout


def load_manifest(token=None, force=False):
    """Fetch + parse asym-intel-internal:ops/pipeline-triggers.yml.

    Cached in-memory for the producer's runtime so multiple calls don't repeat
    the API hit. Pass force=True in tests to bypass the cache.

    Returns the parsed dict, or None on fetch/parse failure.
    """
    if not force and _MANIFEST_CACHE["data"] is not None:
        return _MANIFEST_CACHE["data"]

    # Prefer GH_TOKEN (PAT for cross-repo reads); fall back to GITHUB_TOKEN.
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    raw = _gh_api_raw(f"/repos/{INTERNAL_REPO}/contents/{MANIFEST_PATH}", token=token)
    if not raw:
        return None

    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        return None

    content_b64 = envelope.get("content", "")
    if not content_b64:
        return None

    try:
        yaml_text = base64.b64decode(content_b64).decode("utf-8")
        manifest = yaml.safe_load(yaml_text)
    except (ValueError, UnicodeDecodeError, yaml.YAMLError):
        return None

    if not isinstance(manifest, dict):
        return None

    _MANIFEST_CACHE["data"] = manifest
    # Capture the contents-envelope `sha` (git blob SHA of the manifest at
    # read time). Useful for drift detection on the consumer side: the
    # `manifest_version` field inside the YAML is editable and only bumped
    # by intent; the blob SHA changes on every byte-level edit and is the
    # right key for "did the manifest I read match what I read last time".
    _MANIFEST_CACHE["sha"] = envelope.get("sha")
    return manifest


def manifest_sha():
    """Return the git blob SHA of the manifest as last loaded.

    Returns None if `load_manifest` has not yet been called or the last
    fetch did not return a sha (degraded path). Always reflects the most
    recent successful load.
    """
    return _MANIFEST_CACHE.get("sha")


# ─── Cron parsing ───────────────────────────────────────────────


def _parse_cron_field(field, lo, hi):
    """Expand a cron field ('*', '5', '0,30', '1-5') into a sorted set of ints.

    Returns set() if unparseable.
    """
    field = (field or "").strip()
    if not field or field == "*":
        return set(range(lo, hi + 1))
    out = set()
    for part in field.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                a, b = part.split("-", 1)
                a_i, b_i = int(a), int(b)
                for v in range(min(a_i, b_i), max(a_i, b_i) + 1):
                    if lo <= v <= hi:
                        out.add(v)
            except ValueError:
                continue
        else:
            try:
                v = int(part)
                if lo <= v <= hi:
                    out.add(v)
            except ValueError:
                continue
    return out


def _parse_github_cron(cron_str):
    """Parse a 5-field cron string ('m h dom mon dow') into sets.

    Returns dict with sets: {minutes, hours, doms, months, dows_python}, or
    None on parse failure. We only care about minute, hour, and dow for
    matching — dom/mon are kept for completeness but assumed permissive in
    every manifest cron we ship.
    """
    if not cron_str:
        return None
    fields = cron_str.split()
    if len(fields) != 5:
        return None
    minutes = _parse_cron_field(fields[0], 0, 59)
    hours = _parse_cron_field(fields[1], 0, 23)
    doms = _parse_cron_field(fields[2], 1, 31)
    months = _parse_cron_field(fields[3], 1, 12)
    dows_raw = _parse_cron_field(fields[4], 0, 7)
    if not (minutes and hours and doms and months):
        return None
    dows_python = {_CRON_TO_PY[d] for d in dows_raw if d in _CRON_TO_PY}
    if not dows_python:
        # All-DOW cron ('*' parsed as 0..7 — already mapped above).
        dows_python = set(range(7))
    return {
        "minutes": minutes,
        "hours": hours,
        "doms": doms,
        "months": months,
        "dows_python": dows_python,
    }


# ─── Expected-fire enumeration ──────────────────────────────────


def _iter_window_dates(window_start, window_end):
    """Yield each UTC calendar date between window_start and window_end inclusive."""
    cur = window_start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = window_end.replace(hour=0, minute=0, second=0, microsecond=0)
    while cur <= end:
        yield cur
        cur = cur + timedelta(days=1)


def _expand_cf_dispatcher(manifest, window_start, window_end):
    """Yield ExpectedFire records from cf_dispatcher_schedule.active_crons[]."""
    cf = (manifest or {}).get("cf_dispatcher_schedule") or {}
    active = cf.get("active_crons") or []
    for entry in active:
        dispatches = entry.get("dispatches") or []
        if not dispatches:
            # AGM Friday publisher no-op marker (BRIEF: dispatches: [] => skip).
            continue
        manifest_dow = entry.get("dow")
        if manifest_dow not in _QUARTZ_TO_PY:
            continue
        py_dow = _QUARTZ_TO_PY[manifest_dow]
        cron_str = entry.get("cron") or ""
        monitor = entry.get("monitor")
        utc_times = entry.get("utc_times") or []
        # Walk window dates; emit one ExpectedFire per matching dispatch on
        # each date whose Python weekday matches.
        for day in _iter_window_dates(window_start, window_end):
            if day.weekday() != py_dow:
                continue
            for dispatch in dispatches:
                t = dispatch.get("time") or ""
                wf = dispatch.get("workflow") or ""
                if not t or not wf:
                    continue
                m = re.match(r"^(\d{1,2}):(\d{2})$", t)
                if not m:
                    continue
                hh, mm = int(m.group(1)), int(m.group(2))
                expected_dt = day.replace(hour=hh, minute=mm, second=0,
                                          microsecond=0, tzinfo=timezone.utc)
                if expected_dt < window_start or expected_dt > window_end:
                    continue
                yield {
                    "trigger_id": f"cf:{cron_str}:{t}:{wf}",
                    "source_kind": "cf_dispatcher",
                    "workflow": wf,
                    "repo": MAIN_REPO,
                    "cron": cron_str,
                    "utc_time": t,
                    "dow": manifest_dow,
                    "monitor": monitor,
                    "expected_at": expected_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }


def _normalise_repo(repo):
    """Normalise a manifest `repo:` value to fully-qualified `{owner}/{repo}` form.

    The manifest historically uses bare names like `"asym-intel-main"` for
    github_native entries (which are unambiguous in human reading). The
    GitHub API requires `{owner}/{repo}`; without normalisation the actual-runs
    fetch returns an empty list and every expected fire is incorrectly logged
    as missed. Sprint BH BRIEF #2 acceptance #5 fix-forward.
    """
    if not repo:
        return MAIN_REPO
    if "/" in repo:
        return repo
    # Bare repo name — prepend the canonical owner. asym-intel/* is the only
    # owner the manifest references; if a future repo lives under a different
    # owner the manifest entry must already use fully-qualified form.
    return f"asym-intel/{repo}"


def _expand_github_native(manifest, window_start, window_end):
    """Yield ExpectedFire records from github_native_schedules[]."""
    natives = (manifest or {}).get("github_native_schedules") or []
    for entry in natives:
        if entry.get("state") == "disabled_manually":
            continue
        wf = entry.get("workflow") or ""
        repo = _normalise_repo(entry.get("repo"))
        # Each entry has either `cron:` (single) or `crons:` (list).
        crons = entry.get("crons") or ([entry["cron"]] if entry.get("cron") else [])
        for cron_str in crons:
            parsed = _parse_github_cron(cron_str)
            if not parsed:
                continue
            for day in _iter_window_dates(window_start, window_end):
                if day.weekday() not in parsed["dows_python"]:
                    continue
                for hh in sorted(parsed["hours"]):
                    for mm in sorted(parsed["minutes"]):
                        expected_dt = day.replace(hour=hh, minute=mm, second=0,
                                                  microsecond=0, tzinfo=timezone.utc)
                        if expected_dt < window_start or expected_dt > window_end:
                            continue
                        yield {
                            "trigger_id": f"gh:{repo}:{wf}:{cron_str}:{hh:02d}:{mm:02d}",
                            "source_kind": "github_native",
                            "workflow": wf,
                            "repo": repo,
                            "cron": cron_str,
                            "utc_time": f"{hh:02d}:{mm:02d}",
                            "dow": None,
                            "monitor": None,
                            "expected_at": expected_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        }


def iter_expected_fires(manifest, window_start, window_end):
    """Return a list of ExpectedFire records in [window_start, window_end].

    Both window bounds are timezone-aware UTC datetimes. Returns [] if the
    manifest is missing or empty.
    """
    if not manifest:
        return []
    out = []
    out.extend(_expand_cf_dispatcher(manifest, window_start, window_end))
    out.extend(_expand_github_native(manifest, window_start, window_end))
    # Sort by expected_at then trigger_id for stable output.
    out.sort(key=lambda r: (r["expected_at"], r["trigger_id"]))
    return out


# ─── Self-test (scope item 6′) ─────────────────────────────────
#
# No ops/tests/ infrastructure exists in asym-intel-main at this SHA.
# Per BH.2 BRIEF scope item 6′, the smoke test ships as a __main__ self-test
# in this helper module. Run with:
#     python3 ops/_pipeline_triggers_loader.py
# Exits 0 on pass, 1 on fail. Does NOT hit GitHub — uses an inline synthetic
# manifest so it can run on any developer machine.


def _self_test():
    """In-process assertion suite for the loader. Returns (passed, failed) counts."""
    passed = 0
    failed = 0

    def _check(name, cond, detail=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name} — {detail}")

    # Synthetic manifest: 1 cf_dispatcher entry on Mon, 1 with empty dispatches
    # (must be skipped), and 1 github_native cron firing 3× daily.
    synth = {
        "cf_dispatcher_schedule": {
            "active_crons": [
                {
                    "cron": "0,30 8 * * MON",
                    "utc_times": ["08:00", "08:30"],
                    "dow": 1,  # Quartz Monday
                    "monitor": "wdm",
                    "dispatches": [
                        {"time": "08:00", "workflow": "wdm-weekly-research.yml"},
                        {"time": "08:30", "workflow": "wdm-reasoner.yml"},
                    ],
                },
                {
                    "cron": "30 9 * * FRI",
                    "utc_times": ["09:30"],
                    "dow": 5,  # Quartz Friday
                    "monitor": "agm",
                    "dispatches": [],  # AGM no-op marker — must be skipped
                },
            ],
        },
        "github_native_schedules": [
            {
                "workflow": "update-pipeline-status.yml",
                "repo": "asym-intel/asym-intel-main",
                "crons": ["0 8 * * *", "0 14 * * *", "0 23 * * *"],
            },
            {
                "workflow": "pipeline-watchdog.yml",
                "repo": "asym-intel/asym-intel-main",
                "state": "disabled_manually",
                "cron": "0 6 * * 1",  # Must NOT emit (disabled)
            },
        ],
    }

    # Window: Mon 2026-04-27 00:00Z .. Sun 2026-05-03 23:59:59Z (full week).
    ws = datetime(2026, 4, 27, 0, 0, 0, tzinfo=timezone.utc)
    we = datetime(2026, 5, 3, 23, 59, 59, tzinfo=timezone.utc)
    fires = iter_expected_fires(synth, ws, we)

    # Test 1: WDM cf entry should emit 2 fires (Mon 08:00 + Mon 08:30) on
    # 2026-04-27 only (the only Monday in the window).
    cf_fires = [f for f in fires if f["source_kind"] == "cf_dispatcher"]
    _check(
        "cf_dispatcher emits 2 WDM fires on Mon 2026-04-27",
        len(cf_fires) == 2
        and all(f["expected_at"].startswith("2026-04-27T08:") for f in cf_fires)
        and {f["workflow"] for f in cf_fires} == {
            "wdm-weekly-research.yml", "wdm-reasoner.yml"
        },
        detail=f"got {len(cf_fires)}: {[(f['workflow'], f['expected_at']) for f in cf_fires]}",
    )

    # Test 2: AGM no-op-marker entry (dispatches: []) must NOT emit anything.
    agm_fires = [f for f in fires if (f.get("monitor") == "agm")]
    _check(
        "AGM no-op marker (empty dispatches) emits zero fires",
        len(agm_fires) == 0,
        detail=f"got {len(agm_fires)}: {agm_fires}",
    )

    # Test 3: github_native update-pipeline-status emits 7 days × 3 crons = 21
    # fires; pipeline-watchdog emits 0 (disabled).
    gh_fires = [f for f in fires if f["source_kind"] == "github_native"]
    ups_fires = [f for f in gh_fires if f["workflow"] == "update-pipeline-status.yml"]
    pw_fires = [f for f in gh_fires if f["workflow"] == "pipeline-watchdog.yml"]
    _check(
        "github_native update-pipeline-status emits 21 fires (7 days × 3 crons)",
        len(ups_fires) == 21,
        detail=f"got {len(ups_fires)}",
    )
    _check(
        "pipeline-watchdog (state: disabled_manually) emits zero fires",
        len(pw_fires) == 0,
        detail=f"got {len(pw_fires)}",
    )

    # Test 4: Acceptance #4 — comparator-side detection. Simulated by removing
    # one expected fire from the manifest mid-window; the expected list must
    # then be missing the 08:30 entry. Verifies the loader is the source of
    # truth (downstream comparator's missed_fires logic relies on this).
    synth_skipped = {
        "cf_dispatcher_schedule": {
            "active_crons": [
                {
                    "cron": "0 8 * * MON",
                    "utc_times": ["08:00"],
                    "dow": 1,
                    "monitor": "wdm",
                    "dispatches": [
                        {"time": "08:00", "workflow": "wdm-weekly-research.yml"},
                    ],
                },
            ],
        },
    }
    fires_skipped = iter_expected_fires(synth_skipped, ws, we)
    _check(
        "Removing wdm-reasoner from manifest drops it from expected list",
        len(fires_skipped) == 1
        and fires_skipped[0]["workflow"] == "wdm-weekly-research.yml",
        detail=f"got {fires_skipped}",
    )

    # Test 5: cron parsing — single-day '0 6 * * 1' = Mon 06:00 only.
    parsed = _parse_github_cron("0 6 * * 1")
    _check(
        "cron '0 6 * * 1' parses to Mon (Python weekday 0)",
        parsed and parsed["dows_python"] == {0}
        and parsed["hours"] == {6} and parsed["minutes"] == {0},
        detail=f"got {parsed}",
    )

    # Test 6: cron parsing — '0 8,14,23 * * *' => 3 hours, all days.
    parsed2 = _parse_github_cron("0 8,14,23 * * *")
    _check(
        "cron '0 8,14,23 * * *' parses to 3 hours, all days",
        parsed2 and parsed2["hours"] == {8, 14, 23}
        and parsed2["dows_python"] == set(range(7)),
        detail=f"got {parsed2}",
    )

    # Test 7: empty manifest returns []
    _check("empty manifest returns []", iter_expected_fires({}, ws, we) == [])
    _check("None manifest returns []", iter_expected_fires(None, ws, we) == [])

    # Test 8: Quartz DOW conversion
    _check("Quartz Sun (0) -> Python Sun (6)", _QUARTZ_TO_PY[0] == 6)
    _check("Quartz Mon (1) -> Python Mon (0)", _QUARTZ_TO_PY[1] == 0)
    _check("Quartz Sat (6) -> Python Sat (5)", _QUARTZ_TO_PY[6] == 5)

    # Test 9: repo normalisation — BRIEF #2 acceptance #5 fix-forward.
    # The canonical manifest uses bare names like 'asym-intel-main' for
    # github_native entries; the actual-runs fetch needs `{owner}/{repo}`.
    _check(
        "_normalise_repo bare 'asym-intel-main' -> 'asym-intel/asym-intel-main'",
        _normalise_repo("asym-intel-main") == "asym-intel/asym-intel-main",
        detail=f"got {_normalise_repo('asym-intel-main')}",
    )
    _check(
        "_normalise_repo passes already-qualified form unchanged",
        _normalise_repo("asym-intel/asym-intel-main") == "asym-intel/asym-intel-main",
    )
    _check(
        "_normalise_repo None -> MAIN_REPO",
        _normalise_repo(None) == MAIN_REPO,
    )
    _check(
        "_normalise_repo empty string -> MAIN_REPO",
        _normalise_repo("") == MAIN_REPO,
    )

    # Test 10: github_native expand normalises bare-repo entries (the bug
    # that caused 23 false-missed fires in the first post-merge run).
    synth_bare = {
        "github_native_schedules": [
            {
                "workflow": "update-pipeline-status.yml",
                "repo": "asym-intel-main",  # bare — must be normalised
                "cron": "0 8 * * *",
            },
        ],
    }
    bare_fires = iter_expected_fires(synth_bare, ws, we)
    _check(
        "github_native bare-repo entry emits fires with qualified repo",
        len(bare_fires) == 7  # 7 days × 1 cron
        and all(f["repo"] == "asym-intel/asym-intel-main" for f in bare_fires),
        detail=f"got {[(f['repo'], f['expected_at']) for f in bare_fires]}",
    )

    return passed, failed


if __name__ == "__main__":
    print("Running ops/_pipeline_triggers_loader.py self-test")
    p, f = _self_test()
    print(f"\n{p} passed, {f} failed")
    sys.exit(0 if f == 0 else 1)

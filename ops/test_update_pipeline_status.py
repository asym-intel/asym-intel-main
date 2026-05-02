#!/usr/bin/env python3
"""Tests for ops/update-pipeline-status.py — derive_public_rollup() + Phase B canon names.

Run:
    python3 ops/test_update_pipeline_status.py
or:
    pytest ops/test_update_pipeline_status.py -v

Sprint AZ BRIEF #1: assert that the producer's derive_public_rollup() function
correctly maps full-fidelity internal status to schema v3.0 simplified output,
and that the per-monitor + engine roll-up colour rules behave as specified.

Sprint BU BU.4: schema bumped 4.0 → 4.1; ADVENNT added as 9th monitor;
_full_fidelity_status() fixture expanded to 9 monitors; test_schema_v4_shape
updated for new count + slug list + version string.

Sprint BH BRIEF #2 amendment: schema bumped 3.0 → 4.0; public rollup now
propagates the optional `_trigger_health` block from internal full-fidelity
status. New tests verify (a) v4.0 shape, (b) `_trigger_health` round-trip,
(c) other internal-only keys (`_verification`, `_incidents`, `_meta`) remain
stripped from the public surface.
"""
import importlib.util
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


# Load the producer module dynamically (filename has dashes — not importable normally)
_producer_path = Path(__file__).resolve().parent / "update-pipeline-status.py"
_spec = importlib.util.spec_from_file_location("update_pipeline_status", _producer_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

derive_public_rollup = _module.derive_public_rollup
_classify_station = _module._classify_station
_classify_monitor = _module._classify_monitor
_match_expected_to_actual = _module._match_expected_to_actual
_tolerance_late_for = _module._tolerance_late_for
_parse_producer_issue_body = _module._parse_producer_issue_body
_resolve_cross_repo_failure_alerts = _module._resolve_cross_repo_failure_alerts
_PRODUCER_POLL_BODY_MARKER = _module._PRODUCER_POLL_BODY_MARKER
TRIGGER_TOLERANCE_LATE_CF = _module.TRIGGER_TOLERANCE_LATE_CF
TRIGGER_TOLERANCE_LATE_GH_NATIVE = _module.TRIGGER_TOLERANCE_LATE_GH_NATIVE
TRIGGER_TOLERANCE_EARLY = _module.TRIGGER_TOLERANCE_EARLY


# ─── Fixture builders ─────────────────────────────────────────────────────

NOW = datetime(2026, 4, 28, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _ok_station(days_ago=1):
    ts = _iso(NOW - timedelta(days=days_ago))
    return {"last_run": ts, "last_conclusion": "success", "last_success": ts}


def _failed_station(days_ago=1):
    return {
        "last_run": _iso(NOW - timedelta(days=days_ago)),
        "last_conclusion": "failure",
        "last_success": _iso(NOW - timedelta(days=days_ago + 5)),
    }


def _stale_station(days_ago=15):
    ts = _iso(NOW - timedelta(days=days_ago))
    return {"last_run": ts, "last_conclusion": "success", "last_success": ts}


def _never_station():
    return {"last_run": None, "last_conclusion": "never", "last_success": None}


def _all_green_monitor(slug="WDM"):
    return {
        "accent": "#000",
        "day": "Mon",
        "cron_time": "Mon 06:00 UTC",
        "stations": {
            stage: _ok_station() for stage in
            ["collector", "chatter", "weekly-research", "interpret", "review",
             "compose", "apply", "curate", "published", "dashboard"]
        },
    }


def _full_fidelity_status(monitor_overrides=None):
    """Build a full-fidelity status dict for all 9 monitors, optionally overriding some.

    Sprint BU BU.4: added ADVENNT as 9th monitor. The default entry is all-green
    so cross-monitor tests (engine roll-up colour rules) are not perturbed by
    ADVENNT's presence. Tests that exercise ADVENNT-specific behaviour should
    override it explicitly.
    """
    overrides = monitor_overrides or {}
    status = {}
    for slug in ["WDM", "GMM", "ESA", "FCW", "AIM", "ERM", "SCEM", "FIM", "ADVENNT"]:
        status[slug] = overrides.get(slug, _all_green_monitor(slug))
    status["_meta"] = {"generated": _iso(NOW), "generator": "test"}
    return status


# ─── Schema-shape tests ───────────────────────────────────────────────────

def test_schema_v4_shape():
    """Schema v4.0 (Sprint BH BRIEF #2): adds optional `_trigger_health` block
    propagated from internal full-fidelity status. Other shape rules unchanged."""
    out = derive_public_rollup(_full_fidelity_status())
    # Sprint BU BU.4: schema bumped 4.0 → 4.1 (ADVENNT as 9th monitor)
    assert out["schema_version"] == "4.1", f"expected 4.1 (BU.4 bump), got {out['schema_version']}"
    assert "generated_at" in out
    assert "engine" in out and "status" in out["engine"] and "last_updated" in out["engine"]
    assert "monitors" in out and isinstance(out["monitors"], list)
    assert len(out["monitors"]) == 9, f"expected 9 monitors (BU.4: +ADVENNT), got {len(out['monitors'])}: {[m['slug'] for m in out['monitors']]}"
    slugs = [m["slug"] for m in out["monitors"]]
    assert slugs == ["WDM", "GMM", "ESA", "FCW", "AIM", "ERM", "SCEM", "FIM", "ADVENNT"]
    for m in out["monitors"]:
        assert set(m.keys()) == {"slug", "status", "last_updated"}
        assert m["status"] in ("green", "amber", "red")


def test_schema_v4_trigger_health_propagation():
    """Sprint BH BRIEF #2 acceptance #3: when internal status has a `_trigger_health`
    block, derive_public_rollup() must propagate it to the public rollup unchanged.
    When absent, the key must also be absent on the public side (no synthetic injection)."""
    # Case 1: internal has _trigger_health → public must have it
    internal = _full_fidelity_status()
    internal["_trigger_health"] = {
        "schema_version": "1.0",
        "window_days": 7,
        "manifest_loaded": True,
        "expected_fires": 43,
        "matched_fires": 41,
        "missed_fires": [
            {"trigger_id": "github_native::update-pipeline-status.yml",
             "expected_at": "2026-04-29T08:00:00Z"},
        ],
        "last_fire_was_on_time": True,
    }
    out = derive_public_rollup(internal)
    assert "_trigger_health" in out, "_trigger_health must propagate from internal to public"
    assert out["_trigger_health"] == internal["_trigger_health"], \
        "_trigger_health must propagate unchanged (no field stripping)"
    # Case 2: internal lacks _trigger_health (degraded mode) → public must also lack it
    internal_no_health = _full_fidelity_status()
    out_no_health = derive_public_rollup(internal_no_health)
    assert "_trigger_health" not in out_no_health, \
        "public rollup must not synthesise _trigger_health when internal omits it"


def test_schema_v4_internal_only_keys_excluded():
    """Public rollup must keep _trigger_health (v4.0) but exclude other internal-only
    keys: _meta, _verification, _incidents stay internal-only by construction."""
    internal = _full_fidelity_status()
    internal["_trigger_health"] = {"schema_version": "1.0", "manifest_loaded": True}
    internal["_verification"] = {"checked_at": _iso(NOW)}
    internal["_incidents"] = [{"id": "INC-001"}]
    out = derive_public_rollup(internal)
    assert "_trigger_health" in out, "_trigger_health must propagate (v4.0)"
    assert "_verification" not in out, "_verification must remain internal-only"
    assert "_incidents" not in out, "_incidents must remain internal-only"
    # _meta in input is engine metadata; output uses generated_at — neither should
    # leak the internal _meta block.
    assert "_meta" not in out, "_meta must remain internal-only"


def test_schema_v4_no_methodology_keys():
    """The output must not contain any per-station, model, or stage-name keys."""
    out = derive_public_rollup(_full_fidelity_status())
    out_text = str(out)
    forbidden = ["interpret", "compose", "apply", "curate", "reasoner",
                 "synthesiser", "chatter", "weekly-research", "cascade",
                 "challenger", "dispatcher", "sonar"]
    for term in forbidden:
        assert term not in out_text.lower(), f"forbidden term {term!r} leaked into rollup output"


# ─── Roll-up rule tests ───────────────────────────────────────────────────

def test_all_green_engine_green():
    out = derive_public_rollup(_full_fidelity_status())
    # FIM is treated as amber (non-canonical track) when all stations are green-equivalent
    # Actually: when all stations have valid recent successes, FIM rolls up green too.
    # Let's verify the test: with all 8 monitors as _all_green_monitor, no station is "never".
    assert out["engine"]["status"] == "green", f"engine={out['engine']['status']}, monitors={out['monitors']}"


def test_one_red_engine_red():
    monitors = {"GMM": {
        **_all_green_monitor("GMM"),
        "stations": {**_all_green_monitor("GMM")["stations"], "compose": _failed_station()},
    }}
    out = derive_public_rollup(_full_fidelity_status(monitors))
    gmm = next(m for m in out["monitors"] if m["slug"] == "GMM")
    assert gmm["status"] == "red"
    assert out["engine"]["status"] == "red"


def test_one_amber_engine_amber():
    monitors = {"ESA": {
        **_all_green_monitor("ESA"),
        "stations": {**_all_green_monitor("ESA")["stations"], "review": _stale_station(days_ago=15)},
    }}
    out = derive_public_rollup(_full_fidelity_status(monitors))
    esa = next(m for m in out["monitors"] if m["slug"] == "ESA")
    assert esa["status"] == "amber"
    assert out["engine"]["status"] == "amber"


def test_red_dominates_amber():
    monitors = {
        "GMM": {**_all_green_monitor("GMM"),
                "stations": {**_all_green_monitor("GMM")["stations"], "interpret": _failed_station()}},
        "ESA": {**_all_green_monitor("ESA"),
                "stations": {**_all_green_monitor("ESA")["stations"], "review": _stale_station(15)}},
    }
    out = derive_public_rollup(_full_fidelity_status(monitors))
    assert out["engine"]["status"] == "red"


def test_fim_never_is_amber_not_red():
    """FIM is on a non-canonical track until financial-integrity ships. Never-state stations should be amber, not red."""
    fim = {
        "accent": "#e6a817", "day": "Tue", "cron_time": "Tue 16:00 UTC",
        "stations": {stage: _never_station() for stage in
                     ["collector", "chatter", "weekly-research", "interpret",
                      "review", "compose", "apply", "curate", "published", "dashboard"]},
    }
    out = derive_public_rollup(_full_fidelity_status({"FIM": fim}))
    fim_out = next(m for m in out["monitors"] if m["slug"] == "FIM")
    assert fim_out["status"] == "amber", f"expected FIM amber (non-canonical never), got {fim_out['status']}"
    # Engine should be amber (no reds, but FIM amber)
    assert out["engine"]["status"] == "amber"


def test_canonical_monitor_never_is_red():
    """A canonical monitor (e.g. WDM) with a never-state station IS red — real gap."""
    wdm = {
        **_all_green_monitor("WDM"),
        "stations": {**_all_green_monitor("WDM")["stations"], "compose": _never_station()},
    }
    out = derive_public_rollup(_full_fidelity_status({"WDM": wdm}))
    wdm_out = next(m for m in out["monitors"] if m["slug"] == "WDM")
    assert wdm_out["status"] == "red", f"expected canonical never to be red, got {wdm_out['status']}"


def test_last_updated_is_max_across_stations():
    fresh = _iso(NOW - timedelta(hours=1))
    older = _iso(NOW - timedelta(days=3))
    monitor = _all_green_monitor("GMM")
    monitor["stations"]["interpret"]["last_run"] = fresh
    monitor["stations"]["compose"]["last_run"] = older
    out = derive_public_rollup(_full_fidelity_status({"GMM": monitor}))
    gmm = next(m for m in out["monitors"] if m["slug"] == "GMM")
    assert gmm["last_updated"] == fresh


def test_classify_station_failure_red():
    assert _classify_station(_failed_station(), now=NOW) == "red"


def test_classify_station_recent_success_green():
    assert _classify_station(_ok_station(days_ago=1), now=NOW) == "green"


def test_classify_station_stale_amber():
    assert _classify_station(_stale_station(days_ago=15), now=NOW) == "amber"


def test_classify_station_very_stale_red():
    assert _classify_station(_stale_station(days_ago=30), now=NOW) == "red"


# ─── Trigger-health tolerance split tests (Sprint BH BJ fix-forward 2) ───
#
# After PR #153 + #154 shipped a unified +5min late tolerance, live producer
# fires showed the comparator marking 39 of 43 expected GA scheduled-cron fires
# as missed — because GA's observed scheduled-cron p95 latency is 30-90 minutes
# (well-documented community behaviour). The fix splits tolerance per
# source_kind: cf_dispatcher keeps +5min (Worker dispatch <60s), github_native
# moves to +60min. AD-2026-04-30-BJ records the empirical evidence and the
# process learning (live-fire verification before merge-confirmation).

def test_tolerance_late_for_cf_dispatcher_is_5min():
    assert _tolerance_late_for("cf_dispatcher") == timedelta(minutes=5)
    assert TRIGGER_TOLERANCE_LATE_CF == timedelta(minutes=5)


def test_tolerance_late_for_github_native_is_60min():
    assert _tolerance_late_for("github_native") == timedelta(minutes=60)
    assert TRIGGER_TOLERANCE_LATE_GH_NATIVE == timedelta(minutes=60)


def test_tolerance_late_for_unknown_falls_back_to_max():
    # Fail-open: unknown/None source_kind uses the wider tolerance so schema
    # drift can’t cause spurious-missed reports.
    assert _tolerance_late_for(None) == timedelta(minutes=60)
    assert _tolerance_late_for("") == timedelta(minutes=60)
    assert _tolerance_late_for("some_future_kind") == timedelta(minutes=60)


def _expected_fire(source_kind, expected_at, workflow="x.yml", repo="r/r"):
    return {
        "trigger_id": f"{source_kind}::{workflow}",
        "source_kind": source_kind,
        "workflow": workflow,
        "repo": repo,
        "cron": "0 8 * * *",
        "expected_at": expected_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "monitor": "WDM",
    }


def _actual_run(started, workflow="x.yml", repo="r/r"):
    return {
        "workflow": workflow,
        "repo": repo,
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_started_dt": started,
        "conclusion": "success",
        "event": "schedule",
        "run_number": 1,
        "html_url": "https://example/test",
    }


def test_match_cf_dispatcher_within_5min_late_matches():
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    expected = _expected_fire("cf_dispatcher", expected_at)
    # 4 minutes late — inside cf tolerance.
    actual = _actual_run(expected_at + timedelta(minutes=4))
    assert _match_expected_to_actual(expected, [actual]) is actual


def test_match_cf_dispatcher_30min_late_does_not_match():
    """cf_dispatcher must keep the tight 5min tolerance — the wider gh_native
    tolerance must NOT leak into cf matching."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    expected = _expected_fire("cf_dispatcher", expected_at)
    actual = _actual_run(expected_at + timedelta(minutes=30))
    assert _match_expected_to_actual(expected, [actual]) is None


def test_match_github_native_30min_late_matches():
    """GA scheduled-cron typically fires 30-60min late; must count as on-time."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    expected = _expected_fire("github_native", expected_at)
    actual = _actual_run(expected_at + timedelta(minutes=30))
    assert _match_expected_to_actual(expected, [actual]) is actual


def test_match_github_native_60min_late_matches():
    """Boundary: 60min late is at the tolerance edge — must still match."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    expected = _expected_fire("github_native", expected_at)
    actual = _actual_run(expected_at + timedelta(minutes=60))
    assert _match_expected_to_actual(expected, [actual]) is actual


def test_match_github_native_61min_late_does_not_match():
    """Beyond +60min, even GA fires count as missed."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    expected = _expected_fire("github_native", expected_at)
    actual = _actual_run(expected_at + timedelta(minutes=61))
    assert _match_expected_to_actual(expected, [actual]) is None


def test_match_early_tolerance_unchanged_per_source_kind():
    """Early tolerance is 2min for both source_kinds."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    for sk in ("cf_dispatcher", "github_native"):
        expected = _expected_fire(sk, expected_at)
        # 1 min early — should match
        early_ok = _actual_run(expected_at - timedelta(minutes=1))
        assert _match_expected_to_actual(expected, [early_ok]) is early_ok
        # 3 min early — must not match
        early_too_far = _actual_run(expected_at - timedelta(minutes=3))
        assert _match_expected_to_actual(expected, [early_too_far]) is None


def test_match_window_orientation_natural():
    """Regression guard for AD-2026-04-30-BJ §fix-forward 2: the comparator
    window must be [expected - TOL_EARLY, expected + TOL_LATE]. PR #153
    shipped the arithmetic inverted; this test enforces the corrected
    orientation so future refactors can't silently re-invert. A fire that is
    later-than-expected by less than TOL_LATE must match; a fire that is
    earlier-than-expected by more than TOL_EARLY must NOT match (the wider
    LATE tolerance must NOT leak into the early-side bound)."""
    expected_at = datetime(2026, 4, 30, 8, 0, 0, tzinfo=timezone.utc)
    # github_native, +30min: must match (post-expected, inside +60min LATE).
    e1 = _expected_fire("github_native", expected_at)
    a1 = _actual_run(expected_at + timedelta(minutes=30))
    assert _match_expected_to_actual(e1, [a1]) is a1
    # github_native, -30min: must NOT match. If LATE leaked into the
    # early-side bound (the PR #153 bug), this would falsely match.
    a2 = _actual_run(expected_at - timedelta(minutes=30))
    assert _match_expected_to_actual(e1, [a2]) is None


def test_tolerance_block_serialises_both_source_kinds():
    """compute_trigger_health() must emit both late tolerances in the
    serialised tolerance dict so consumers can see the per-kind values."""
    # Force degraded mode — we don’t need a manifest to inspect the base
    # tolerance dict shape.
    compute_trigger_health = _module.compute_trigger_health
    _orig_avail = _module._TRIGGER_LOADER_AVAILABLE
    _module._TRIGGER_LOADER_AVAILABLE = False
    try:
        out = compute_trigger_health(window_days=7, now=NOW)
    finally:
        _module._TRIGGER_LOADER_AVAILABLE = _orig_avail
    tol = out["tolerance"]
    assert tol["late_minutes_cf_dispatcher"] == 5
    assert tol["late_minutes_github_native"] == 60
    assert tol["early_minutes"] == 2
    # Old key must be gone (schema change documented in AD-BJ).
    assert "late_minutes" not in tol


# ─── Cross-repo failure-issue lifecycle tests ─────────────────────────────
#
# Regression coverage for asym-intel-main#173/#174: producer auto-opens cross-
# repo failure issues but never auto-closed them on recovery. Tests confirm
# the new resolve path closes only producer-poll issues whose station has
# returned to success on the CURRENT producer run.


def _producer_issue(*, number, abbr, station, created_at, body_extra=""):
    """Build a fixture issue dict matching the GitHub /issues API shape that
    _resolve_cross_repo_failure_alerts() consumes."""
    body = (
        f"**Monitor:** {abbr} (asym-intel/advennt)\n"
        f"**Station:** {station}\n"
        f"**Workflow:** publisher.yml\n"
        f"**Last run:** 2026-05-02T08:33:01Z\n"
        f"**Detected by:** {_PRODUCER_POLL_BODY_MARKER}\n"
        f"\nClose when resolved.{body_extra}"
    )
    return {
        "number": number,
        "title": f"🔴 Pipeline failure: {abbr} {station} (publisher.yml)",
        "state": "open",
        "created_at": created_at,
        "body": body,
        "labels": [{"name": "pipeline-failure"}],
    }


def test_parse_producer_issue_body_extracts_monitor_and_station():
    body = (
        "**Monitor:** ADVENNT (asym-intel/advennt)\n"
        "**Station:** published\n"
        "**Workflow:** publisher.yml\n"
        f"**Detected by:** {_PRODUCER_POLL_BODY_MARKER}\n"
    )
    abbr, station = _parse_producer_issue_body(body)
    assert abbr == "ADVENNT"
    assert station == "published"


def test_parse_producer_issue_body_rejects_non_producer():
    """Issues without the producer-poll marker must NOT be parsed — they may
    be manually-filed pipeline-failure issues we must never auto-close."""
    body = "**Monitor:** ADVENNT\n**Station:** published\nManually filed.\n"
    abbr, station = _parse_producer_issue_body(body)
    assert abbr is None and station is None


class _FakeRun:
    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = ""


def _patch_subprocess(call_log, *, comment_rc=0, close_rc=0):
    """Replace _module.subprocess.run with a recorder that returns success."""
    def fake_run(cmd, *args, **kwargs):
        call_log.append(cmd)
        if any("comments" in p for p in cmd):
            return _FakeRun(returncode=comment_rc)
        return _FakeRun(returncode=close_rc)
    return fake_run


def test_resolve_closes_when_station_recovered():
    """The lifecycle gap behind #173/#174: when current run shows success and
    last_run > issue.created_at, the resolver must close the issue."""
    issue = _producer_issue(
        number=173, abbr="ADVENNT", station="published",
        created_at="2026-05-02T09:15:03Z",
    )
    # Current status: publisher succeeded at 11:10 (after the 09:15 issue).
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T11:10:29Z",
                    "last_conclusion": "success",
                    "last_success": "2026-05-02T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(
            status, issues=[issue],
            now=datetime(2026, 5, 2, 14, 0, tzinfo=timezone.utc),
        )
    finally:
        _module.subprocess.run = orig
    assert closed == [173], f"expected #173 closed, got {closed}"
    # Two API calls: comment + PATCH state=closed
    assert len(calls) == 2
    assert any("comments" in p for p in calls[0])
    assert any("state=closed" in p for p in calls[1])


def test_resolve_skips_when_station_still_failing():
    """Active failure must NOT be auto-closed — that would mask the alert."""
    issue = _producer_issue(
        number=173, abbr="ADVENNT", station="published",
        created_at="2026-05-02T09:15:03Z",
    )
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T10:00:00Z",
                    "last_conclusion": "failure",
                    "last_success": "2026-05-01T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[issue])
    finally:
        _module.subprocess.run = orig
    assert closed == []
    assert calls == [], "no API calls expected when station is still failing"


def test_resolve_skips_when_success_predates_issue():
    """If last_run on the current snapshot is OLDER than the issue's created_at,
    the success is stale evidence — don't close yet."""
    issue = _producer_issue(
        number=173, abbr="ADVENNT", station="published",
        created_at="2026-05-02T09:15:03Z",
    )
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-01T08:00:00Z",  # before the issue
                    "last_conclusion": "success",
                    "last_success": "2026-05-01T08:00:00Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[issue])
    finally:
        _module.subprocess.run = orig
    assert closed == []


def test_resolve_skips_running_status():
    """`running`/`queued` is NOT recovery — don't close mid-flight."""
    issue = _producer_issue(
        number=174, abbr="ADVENNT", station="dashboard",
        created_at="2026-05-02T09:15:03Z",
    )
    status = {
        "ADVENNT": {
            "stations": {
                "dashboard": {
                    "last_run": "2026-05-02T11:10:29Z",
                    "last_conclusion": "running",
                    "last_success": "2026-05-01T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[issue])
    finally:
        _module.subprocess.run = orig
    assert closed == []


def test_resolve_skips_non_producer_issue():
    """Issues without the producer-poll marker (e.g. manually-filed) must be
    left alone, even if labelled `pipeline-failure`."""
    manual = {
        "number": 999,
        "title": "🔴 Pipeline failure: ADVENNT published",
        "state": "open",
        "created_at": "2026-05-02T09:15:03Z",
        "body": "Filed manually by operator. ADVENNT published is broken.",
        "labels": [{"name": "pipeline-failure"}],
    }
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T11:10:29Z",
                    "last_conclusion": "success",
                    "last_success": "2026-05-02T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[manual])
    finally:
        _module.subprocess.run = orig
    assert closed == []
    assert calls == []


def test_resolve_skips_commons_monitor():
    """Commons monitors are owned by pipeline-failure-alert.yml, not the
    producer-poll path. Even if a producer-style body somehow names a commons
    monitor, the resolver must not act on it."""
    fake = _producer_issue(
        number=200, abbr="WDM", station="published",
        created_at="2026-05-02T09:00:00Z",
    )
    status = {
        "WDM": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T11:00:00Z",
                    "last_conclusion": "success",
                    "last_success": "2026-05-02T11:00:00Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[fake])
    finally:
        _module.subprocess.run = orig
    assert closed == []


def test_resolve_closes_label_less_producer_issue():
    """Regression for #173/#174: real producer-poll issues lack the
    `pipeline-failure` label because the open-path's `--field labels[]=...`
    invocation didn't always set it. The resolver must still find and close
    them via body-marker matching, since the body-marker is the authoritative
    provenance signal."""
    issue = _producer_issue(
        number=173, abbr="ADVENNT", station="published",
        created_at="2026-05-02T09:15:03Z",
    )
    issue["labels"] = []  # the actual on-prod shape for #173/#174
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T11:10:29Z",
                    "last_conclusion": "success",
                    "last_success": "2026-05-02T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls)
    try:
        closed = _resolve_cross_repo_failure_alerts(
            status, issues=[issue],
            now=datetime(2026, 5, 2, 14, 0, tzinfo=timezone.utc),
        )
    finally:
        _module.subprocess.run = orig
    assert closed == [173], f"expected #173 closed, got {closed}"


def test_emit_creates_issue_with_labels_array():
    """Regression for #173/#174 root cause: the open path must send `labels`
    as a real JSON array, not as a string `--field`. We verify by capturing
    the payload sent through stdin and asserting the JSON shape includes
    `labels: ["pipeline-failure"]`."""
    _emit = _module._emit_cross_repo_failure_alerts
    # Bypass the existing-titles check by injecting a fresh status with a
    # recent failure on a cross-repo monitor.
    now_iso = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": now_iso,
                    "last_conclusion": "failure",
                    "last_success": None,
                },
            },
        },
    }
    captured = {}

    def fake_gh_api(endpoint, token=None):
        # _list_open_pipeline_failure_issues() returns []
        return "[]"

    def fake_run(cmd, *args, **kwargs):
        captured["cmd"] = cmd
        captured["input"] = kwargs.get("input")
        return _FakeRun(returncode=0)

    orig_gh, orig_run = _module.gh_api, _module.subprocess.run
    _module.gh_api = fake_gh_api
    _module.subprocess.run = fake_run
    try:
        _emit(status)
    finally:
        _module.gh_api = orig_gh
        _module.subprocess.run = orig_run

    assert "input" in captured and captured["input"], (
        "expected JSON payload piped via --input -"
    )
    import json as _json
    payload = _json.loads(captured["input"])
    assert payload.get("labels") == ["pipeline-failure"], (
        f"labels must be a JSON array, got {payload.get('labels')!r}"
    )
    assert "--input" in captured["cmd"], (
        "open path must use `--input -` (gh-documented array form), "
        "not legacy `--field labels[]=...`"
    )


def test_list_open_pipeline_failure_issues_filters_pull_requests():
    """The /issues endpoint returns PRs too; the helper must strip them so
    the resolver doesn't try to body-parse a PR description."""
    _list = _module._list_open_pipeline_failure_issues
    fake_payload = _json_dumps_for_test([
        {"number": 1, "title": "issue", "body": "x"},
        {"number": 2, "title": "PR", "body": "y", "pull_request": {"url": "..."}},
    ])

    def fake_gh_api(endpoint, token=None):
        return fake_payload

    orig = _module.gh_api
    _module.gh_api = fake_gh_api
    try:
        out = _list()
    finally:
        _module.gh_api = orig
    nums = [i.get("number") for i in out]
    assert nums == [1], f"PRs must be stripped, got {nums}"


def _json_dumps_for_test(obj):
    import json as _json
    return _json.dumps(obj)


def test_resolve_does_not_close_if_comment_fails():
    """If posting the recovery comment fails, the issue must stay open — no
    silent close that would erase the audit trail."""
    issue = _producer_issue(
        number=173, abbr="ADVENNT", station="published",
        created_at="2026-05-02T09:15:03Z",
    )
    status = {
        "ADVENNT": {
            "stations": {
                "published": {
                    "last_run": "2026-05-02T11:10:29Z",
                    "last_conclusion": "success",
                    "last_success": "2026-05-02T11:10:29Z",
                },
            },
        },
    }
    calls = []
    orig = _module.subprocess.run
    _module.subprocess.run = _patch_subprocess(calls, comment_rc=1)
    try:
        closed = _resolve_cross_repo_failure_alerts(status, issues=[issue])
    finally:
        _module.subprocess.run = orig
    assert closed == []
    # Comment was attempted, close was NOT.
    assert len(calls) == 1
    assert any("comments" in p for p in calls[0])


# ─── Test runner (no pytest required) ──────────────────────────────────────

def main():
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}\n    {e}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {fn.__name__} (error)\n    {type(e).__name__}: {e}")
    print()
    if failed:
        print(f"FAIL: {failed}/{len(fns)} test(s) failed")
        return 1
    print(f"PASS: {len(fns)} test(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

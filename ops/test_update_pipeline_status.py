#!/usr/bin/env python3
"""Tests for ops/update-pipeline-status.py — derive_public_rollup() + Phase B canon names.

Run:
    python3 ops/test_update_pipeline_status.py
or:
    pytest ops/test_update_pipeline_status.py -v

Sprint AZ BRIEF #1: assert that the producer's derive_public_rollup() function
correctly maps full-fidelity internal status to schema v3.0 simplified output,
and that the per-monitor + engine roll-up colour rules behave as specified.

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
    """Build a full-fidelity status dict for all 8 monitors, optionally overriding some."""
    overrides = monitor_overrides or {}
    status = {}
    for slug in ["WDM", "GMM", "ESA", "FCW", "AIM", "ERM", "SCEM", "FIM"]:
        status[slug] = overrides.get(slug, _all_green_monitor(slug))
    status["_meta"] = {"generated": _iso(NOW), "generator": "test"}
    return status


# ─── Schema-shape tests ───────────────────────────────────────────────────

def test_schema_v4_shape():
    """Schema v4.0 (Sprint BH BRIEF #2): adds optional `_trigger_health` block
    propagated from internal full-fidelity status. Other shape rules unchanged."""
    out = derive_public_rollup(_full_fidelity_status())
    assert out["schema_version"] == "4.0"
    assert "generated_at" in out
    assert "engine" in out and "status" in out["engine"] and "last_updated" in out["engine"]
    assert "monitors" in out and isinstance(out["monitors"], list)
    assert len(out["monitors"]) == 8
    slugs = [m["slug"] for m in out["monitors"]]
    assert slugs == ["WDM", "GMM", "ESA", "FCW", "AIM", "ERM", "SCEM", "FIM"]
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

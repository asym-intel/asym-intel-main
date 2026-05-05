"""
Tests for publisher applier-driven date contract.

Until 2026-05-05 the publisher derived meta.slug, meta.week_label,
report.source_url and the weekly-brief filename from runtime UTC
date (or PUBLISH_DATE override). The applier, however, locks each
cycle to a `week_ending` and writes paths the publisher is expected
to honour (publication.publisher_artefacts.weekly_brief_path /
report_latest_path). Live diagnosis 2026-05-05: WDM/GMM/ESA/FCW/ERM/
SCEM applier-readiness reached for week_ending=2026-05-09 but
publisher still wrote 2026-05-05 labels/paths (incl. SCEM Issue 10).

These tests cover:
  - load_publication_eligibility surfaces week_ending and
    publisher_artefacts when present on the apply artefact.
  - resolve_publication_targets prefers applier week_ending over
    runtime/PUBLISH_DATE date and threads it through publish_date.
  - Backwards compatibility: legacy apply artefacts without the
    contract fields are unaffected (runtime date retained).
  - Real SCEM 2026-05-05 fixture shape: would have caught the live
    bug — runtime=2026-05-05 → resolved publish_date=2026-05-09.
  - Malformed week_ending on the contract falls back gracefully.
  - Brief filename date can come from publisher_artefacts when
    week_ending is absent (defensive double-source).

No network. Uses tmp_path for the apply artefact.
"""

import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from publisher import (  # noqa: E402
    load_publication_eligibility,
    resolve_publication_targets,
    _date_from_brief_path,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _write_apply(tmp_path: pathlib.Path, slug: str, payload, filename: str = "apply-latest.json") -> pathlib.Path:
    apply_dir = tmp_path / "pipeline" / "monitors" / slug / "applied"
    apply_dir.mkdir(parents=True, exist_ok=True)
    apply_path = apply_dir / filename
    apply_path.write_text(json.dumps(payload))
    return apply_path


# ── load_publication_eligibility surfaces the contract ────────────────────


def test_load_surfaces_week_ending_when_present(tmp_path):
    _write_apply(tmp_path, "macro-monitor", {
        "week_ending": "2026-05-09",
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    })
    e = load_publication_eligibility("macro-monitor", tmp_path)
    assert e["week_ending"] == "2026-05-09"
    # Existing fields still populated.
    assert e["ready_to_publish"] is True
    assert e["malformed"] is False


def test_load_surfaces_publisher_artefacts_when_present(tmp_path):
    _write_apply(tmp_path, "conflict-escalation", {
        "week_ending": "2026-05-09",
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
            "publisher_artefacts": {
                "weekly_brief_path": "content/monitors/conflict-escalation/2026-05-09-weekly-brief.md",
                "report_latest_path": "static/monitors/conflict-escalation/data/report-latest.json",
            },
        },
        "inputs": {"review": {"verdict": "publish"}},
    })
    e = load_publication_eligibility("conflict-escalation", tmp_path)
    assert e["publisher_artefacts"]["weekly_brief_path"].endswith(
        "2026-05-09-weekly-brief.md"
    )
    assert e["publisher_artefacts"]["report_latest_path"].endswith(
        "report-latest.json"
    )


def test_load_handles_legacy_apply_without_contract_fields(tmp_path):
    """Legacy apply artefacts (no week_ending, no publisher_artefacts) must
    still load cleanly with the contract fields set to None."""
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    })
    e = load_publication_eligibility("ai-governance", tmp_path)
    assert e["week_ending"] is None
    assert e["publisher_artefacts"] is None
    assert e["malformed"] is False
    assert e["ready_to_publish"] is True


def test_load_ignores_non_string_week_ending(tmp_path):
    """If week_ending is malformed (e.g. None or numeric) the loader
    must not crash; it should leave eligibility.week_ending=None."""
    _write_apply(tmp_path, "macro-monitor", {
        "week_ending": 20260509,  # numeric — invalid shape
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    })
    e = load_publication_eligibility("macro-monitor", tmp_path)
    assert e["week_ending"] is None


# ── resolve_publication_targets behaviour ─────────────────────────────────


def test_resolve_prefers_applier_week_ending_over_runtime():
    eligibility = {
        "week_ending": "2026-05-09",
        "publisher_artefacts": {
            "weekly_brief_path": "content/monitors/macro-monitor/2026-05-09-weekly-brief.md",
            "report_latest_path": "static/monitors/macro-monitor/data/report-latest.json",
        },
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-09"
    assert t["brief_filename_date"] == "2026-05-09"
    assert t["source"] == "applier_week_ending"
    assert t["contract_present"] is True


def test_resolve_falls_back_to_runtime_when_no_contract():
    """Backwards compat: legacy apply artefact without the contract
    keeps runtime date unchanged."""
    eligibility = {"week_ending": None, "publisher_artefacts": None}
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-05"
    assert t["brief_filename_date"] == "2026-05-05"
    assert t["source"] == "runtime"
    assert t["contract_present"] is False


def test_resolve_uses_brief_path_date_when_week_ending_absent():
    """Defensive double-source: if week_ending is missing but
    publisher_artefacts.weekly_brief_path embeds a date, use it."""
    eligibility = {
        "week_ending": None,
        "publisher_artefacts": {
            "weekly_brief_path": "content/monitors/macro-monitor/2026-05-09-weekly-brief.md",
            "report_latest_path": "static/monitors/macro-monitor/data/report-latest.json",
        },
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-09"
    assert t["brief_filename_date"] == "2026-05-09"
    assert t["source"] == "applier_brief_path"
    assert t["contract_present"] is True


def test_resolve_handles_malformed_week_ending_gracefully():
    """Malformed week_ending must not crash; resolver falls back to
    runtime date and the caller logs a warning incident."""
    eligibility = {
        "week_ending": "not-a-date",
        "publisher_artefacts": None,
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-05"
    assert t["source"] == "runtime"
    assert t["contract_present"] is True  # contract was structurally present


def test_resolve_handles_empty_eligibility():
    """When no apply artefact exists at all (legacy monitor), resolver
    must not raise — runtime date wins."""
    t = resolve_publication_targets({}, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-05"
    assert t["source"] == "runtime"
    assert t["contract_present"] is False


def test_resolve_brief_filename_date_can_diverge_from_publish_date_only_when_week_ending_missing():
    """When week_ending is set, both publish_date and brief_filename_date
    follow it. The brief path date is only used as a fallback source."""
    # week_ending wins outright when present; brief_path is consistent.
    eligibility = {
        "week_ending": "2026-05-09",
        "publisher_artefacts": {
            "weekly_brief_path": "content/monitors/x/2026-05-09-weekly-brief.md",
            "report_latest_path": "static/monitors/x/data/report-latest.json",
        },
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    assert t["publish_date"] == t["brief_filename_date"] == "2026-05-09"


# ── _date_from_brief_path helper ───────────────────────────────────────────


def test_date_from_brief_path_extracts_date():
    assert _date_from_brief_path(
        "content/monitors/macro-monitor/2026-05-09-weekly-brief.md"
    ) == "2026-05-09"


def test_date_from_brief_path_returns_none_for_unknown_shape():
    assert _date_from_brief_path("some/other/path.md") is None
    assert _date_from_brief_path(None) is None
    assert _date_from_brief_path(12345) is None
    assert _date_from_brief_path("") is None


# ── Regression guard: real fixture shapes from 2026-05-05 ──────────────────


def _scem_2026_05_05_fixture():
    """Real shape from pipeline/monitors/conflict-escalation/applied/
    apply-latest.json on 2026-05-05 (the artefact whose contract was
    ignored by the SCEM publisher dispatch that committed Issue 10
    with stale 2026-05-05 labels).
    """
    return {
        "_meta": {
            "schema_version": "aim-apply-v1.0",
            "monitor_slug": "conflict-escalation",
            "applied_at": "2026-05-05T18:01:00Z",
            "cycle_disposition": "material_change",
        },
        "cycle_id": "scem-2026-05-05",
        "methodology_version": "conflict-escalation-methodology-2026-Q2",
        "week_ending": "2026-05-09",
        "week_ending_source": "interpret._meta.week_ending",
        "inputs": {"review": {"verdict": "publish"}},
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
            "publisher_artefacts": {
                "weekly_brief_path": "content/monitors/conflict-escalation/2026-05-09-weekly-brief.md",
                "report_latest_path": "static/monitors/conflict-escalation/data/report-latest.json",
            },
        },
    }


def test_regression_scem_2026_05_05_resolves_to_applier_week_ending(tmp_path):
    """Live regression guard: SCEM apply-latest on 2026-05-05 carries
    week_ending=2026-05-09 + publisher_artefacts pointing at
    2026-05-09-weekly-brief.md. The resolver must promote 2026-05-09
    over the runtime 2026-05-05 — exactly the behaviour the manual
    SCEM Issue 10 dispatch lacked.
    """
    _write_apply(tmp_path, "conflict-escalation", _scem_2026_05_05_fixture())
    e = load_publication_eligibility("conflict-escalation", tmp_path)
    assert e["week_ending"] == "2026-05-09"
    assert e["publisher_artefacts"] is not None

    t = resolve_publication_targets(e, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-09"
    assert t["brief_filename_date"] == "2026-05-09"
    assert t["source"] == "applier_week_ending"
    assert t["contract_present"] is True


def test_regression_macro_monitor_2026_05_05_resolves_to_applier_week_ending(tmp_path):
    """Class-wide check: same fix must apply to GMM (and by symmetry
    WDM/ESA/FCW/ERM)."""
    _write_apply(tmp_path, "macro-monitor", {
        "_meta": {"schema_version": "aim-apply-v1.0",
                  "monitor_slug": "macro-monitor",
                  "applied_at": "2026-05-05T00:03:05Z"},
        "cycle_id": "gmm-2026-05-05",
        "week_ending": "2026-05-09",
        "inputs": {"review": {"verdict": "publish"}},
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
            "publisher_artefacts": {
                "weekly_brief_path": "content/monitors/macro-monitor/2026-05-09-weekly-brief.md",
                "report_latest_path": "static/monitors/macro-monitor/data/report-latest.json",
            },
        },
    })
    e = load_publication_eligibility("macro-monitor", tmp_path)
    t = resolve_publication_targets(e, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-09"
    assert t["source"] == "applier_week_ending"


def test_legacy_apply_without_contract_still_publishes_on_runtime_date(tmp_path):
    """A legacy applier output (no week_ending / no publisher_artefacts)
    must not regress the publisher — it stays on the runtime/PUBLISH_DATE
    date the way it did before the contract was introduced.
    """
    _write_apply(tmp_path, "ai-governance", {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    })
    e = load_publication_eligibility("ai-governance", tmp_path)
    t = resolve_publication_targets(e, runtime_date="2026-05-05")
    assert t["publish_date"] == "2026-05-05"
    assert t["source"] == "runtime"
    assert t["contract_present"] is False


# ── End-to-end-ish: report meta carries applier week_ending ────────────────
#
# This test imports build_meta directly and asserts the publisher's
# meta object would carry the applier week_ending once the resolver has
# run. This is the unit test that would have caught the SCEM Issue 10
# defect: meta.slug / meta.week_label / meta.published all key off
# `publish_date`, so verifying they reflect 2026-05-09 (not the runtime
# 2026-05-05) closes the contract.


def test_build_meta_uses_resolved_publish_date_for_slug_and_week_label():
    from publisher import build_meta, MONITOR_CONFIGS

    eligibility = {
        "week_ending": "2026-05-09",
        "publisher_artefacts": {
            "weekly_brief_path": "content/monitors/conflict-escalation/2026-05-09-weekly-brief.md",
            "report_latest_path": "static/monitors/conflict-escalation/data/report-latest.json",
        },
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    publish_date = t["publish_date"]

    config = MONITOR_CONFIGS["conflict-escalation"]
    meta = build_meta(prev_report={}, synthesis={}, publish_date=publish_date, config=config)

    # The contract: meta.slug / meta.week_label / meta.published all
    # follow the applier week_ending, not runtime 2026-05-05.
    assert meta["slug"] == "2026-05-09"
    assert meta["week_label"] == "W/E 9 May 2026"
    assert meta["published"].startswith("2026-05-09")


def test_source_url_uses_resolved_publish_date():
    """Verify the source_url construction (line in main()) would emit
    /monitors/<slug>/2026-05-09-weekly-brief/ rather than 2026-05-05.

    We re-implement the one-liner inline because main() is monolithic;
    the construction is `f"{SITE_URL}/monitors/{slug}/{publish_date}-weekly-brief/"`.
    The unit assertion is that `publish_date` is 2026-05-09, which is
    what tied the original bug together.
    """
    from publisher import SITE_URL
    eligibility = {
        "week_ending": "2026-05-09",
        "publisher_artefacts": None,
    }
    t = resolve_publication_targets(eligibility, runtime_date="2026-05-05")
    source_url = f"{SITE_URL}/monitors/conflict-escalation/{t['publish_date']}-weekly-brief/"
    assert "2026-05-09-weekly-brief" in source_url
    assert "2026-05-05" not in source_url

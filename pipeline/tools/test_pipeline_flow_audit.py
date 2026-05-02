"""
Tests for pipeline_flow_audit.py — the BRIEF 1 pipeline-flow data-quality
audit harness.

Coverage:

  • Emptiness primitives match the publisher contract (placeholder objects,
    [{}] arrays, literal "null" sentinel, str "").
  • Interpretation row classifies AIM 2026-05-02 module_3 / module_6 as
    silent-empty (absent_unknown, interpreter break) — the live failure mode.
  • Publish row honors module-level null_signal provenance when present
    (post-#185 expected behavior) and flags bare-empty modules without it.
  • Apply-stage block detection: ready_to_publish=false plus a present
    published report flips on the apply_block_not_honored note (the #186
    contract guard).
  • module_2 trace is `present` everywhere a module body exists.
  • first_break_stage is the earliest non-present, non-absent_explained stage.
  • All-indexed-monitor summary smoke test: returns one summary per monitor
    in the registry, with the AIM 2026-05-02 silent-empty modules surfaced.

The tests use synthetic fixtures written into tmp_path, and one regression
test against the live AIM 2026-05-02 artifacts already in the repo.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from pipeline_flow_audit import (  # noqa: E402
    STATE_ABSENT_EXPLAINED,
    STATE_ABSENT_UNKNOWN,
    STATE_BLOCKED,
    STATE_MISSING_ARTIFACT,
    STATE_PRESENT,
    _has_literal_null_string,
    _has_placeholder_array,
    _is_empty_value,
    _meaningful_leaf_count,
    _module_body_is_empty,
    audit_all_indexed,
    audit_consumer,
    rows_to_csv,
    rows_to_json,
    summarise_consumer,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _write_json(path: pathlib.Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _make_consumer_artifacts(
    tmp_repo: pathlib.Path,
    slug: str,
    *,
    report_date: str,
    interpret: dict,
    review: dict | None = None,
    apply_doc: dict | None = None,
    published: dict | None = None,
    weekly: dict | None = None,
) -> None:
    base = tmp_repo / "pipeline" / "monitors" / slug
    static = tmp_repo / "static" / "monitors" / slug / "data"
    if weekly is not None:
        _write_json(base / "weekly" / f"weekly-{report_date}.json", weekly)
    _write_json(base / "synthesised" / f"interpret-{report_date}.json", interpret)
    if review is not None:
        _write_json(base / "synthesised" / f"review-{report_date}.json", review)
    if apply_doc is not None:
        _write_json(base / "applied" / f"apply-{report_date}.json", apply_doc)
    if published is not None:
        _write_json(static / f"report-{report_date}.json", published)


# ── Emptiness primitives ───────────────────────────────────────────────────


def test_is_empty_value_handles_placeholder_and_null_string():
    assert _is_empty_value(None) is True
    assert _is_empty_value("") is True
    assert _is_empty_value("null") is True
    assert _is_empty_value("NULL") is True
    assert _is_empty_value("Null  ") is True
    assert _is_empty_value({}) is True
    assert _is_empty_value([]) is True
    assert _is_empty_value([{}]) is True
    assert _is_empty_value([{"a": ""}, {}]) is True
    assert _is_empty_value("hello") is False
    assert _is_empty_value([{"a": "x"}]) is False


def test_module_body_is_empty_excludes_meta_keys():
    # AIM 2026-05-02 module_3 shape (placeholder arrays + title)
    m3 = {
        "title": "Investment and M&A",
        "funding_rounds": [{}],
        "strategic_deals": [{}],
        "energy_wall": [{}],
    }
    assert _module_body_is_empty(m3) is True
    # Already-stamped absence module is still 'empty body'
    m_stamped = {
        "title": "Investment and M&A",
        "funding_rounds": [],
        "null_signal": True,
        "empty_reason": "no_material_content",
        "fallback_message": "...",
    }
    assert _module_body_is_empty(m_stamped) is True
    # Module with one real entry is not empty
    m2 = {"title": "Models", "models": [{"name": "GPT-5.5"}]}
    assert _module_body_is_empty(m2) is False


def test_meaningful_leaf_count_ignores_placeholders():
    assert _meaningful_leaf_count([{}]) == 0
    assert _meaningful_leaf_count("null") == 0
    assert _meaningful_leaf_count({"a": [{"b": "x"}, {}]}) == 1
    assert _meaningful_leaf_count(
        [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    ) == 3


def test_placeholder_array_and_null_string_detectors():
    m_ph = {"title": "X", "items": [{}]}
    assert _has_placeholder_array(m_ph) is True
    m_no = {"title": "X", "items": [{"a": 1}]}
    assert _has_placeholder_array(m_no) is False
    m_null = {"title": "X", "digest_note": "null", "items": []}
    assert _has_literal_null_string(m_null) is True


# ── Synthetic fixture: AIM 2026-05-02 silent-empty modules ────────────────


@pytest.fixture
def aim_2026_05_02_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """Synthetic repo reproducing the AIM 2026-05-02 failure mode.

    interpret:    module_2 populated, module_3 / module_6 placeholder-only.
    review:       hold-for-review (R1 hard-invariant fail).
    apply:        ready_to_publish=False, hold_reason=review_verdict:hold-for-review.
    publish:      report-* exists with bare-empty module_3/6 — the live break.
    """
    interpret = {
        "_meta": {
            "monitor_slug": "ai-governance",
            "week_ending": "2026-05-02",
            "cycle_disposition": "material_change",
            "null_signal_week": False,
        },
        "module_2": {
            "title": "Models",
            "models": [
                {"name": "GPT-5.5", "lab": "OpenAI", "tier": 1},
                {"name": "Other", "lab": "Anthropic", "tier": 1},
            ],
        },
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [{}],
            "strategic_deals": [{}],
            "energy_wall": [{}],
        },
        "module_6": {
            "title": "AI in Science",
            "threshold_events": [{}],
            "programme_updates": [{}],
            "arxiv_highlights": [{}],
        },
        "module_9": {
            "title": "Law and Litigation",
            "digest_note": "null",
            "law_highlights": [{}],
        },
    }
    review = {
        "verdict": "hold-for-review",
        "verdict_reason": "hard-invariant FAIL: ['R1']",
        "checks": [{"check_id": "R1", "result": "FAIL"}],
    }
    apply_doc = {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }
    # Published report: same shape, [{}] normalised to [] by the prior publish run.
    published = {
        "module_2": {
            "title": "Models",
            "models": [
                {"name": "GPT-5.5", "lab": "OpenAI", "tier": 1},
                {"name": "Other", "lab": "Anthropic", "tier": 1},
            ],
        },
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "strategic_deals": [],
            "energy_wall": [],
        },
        "module_6": {
            "title": "AI in Science",
            "threshold_events": [],
            "programme_updates": [],
            "arxiv_highlights": [],
        },
        "module_9": {
            "title": "Law and Litigation",
            "digest_note": "null",
            "law_highlights": [],
        },
    }
    weekly = {
        "_meta": {"week_ending": "2026-05-02"},
        "weekly_developments": [
            {"id": "AGM-2026-05-02-002", "kind": "partnership"},
        ],
    }
    _make_consumer_artifacts(
        tmp_path, "ai-governance",
        report_date="2026-05-02",
        interpret=interpret,
        review=review,
        apply_doc=apply_doc,
        published=published,
        weekly=weekly,
    )
    return tmp_path


# ── Failed-module trace: module_3 ──────────────────────────────────────────


def test_module_3_silent_empty_at_interpret(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_3"],
    )
    by_stage = {r.stage: r for r in rows}
    interp = by_stage["interpretation"]
    assert interp.state == STATE_ABSENT_UNKNOWN
    assert interp.absence_basis == "interpreter_silent_empty"
    assert interp.meaningful_leaf_count == 0
    assert "bare_empty_module_no_provenance" in interp.notes
    # material_change cycle + empty module → suspected classification drift.
    assert "suspected_classification_drift" in interp.notes
    # Placeholder [{}] arrays must be detected.
    assert "placeholder_array_detected" in interp.notes


def test_module_3_first_break_is_interpretation(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_3"],
    )
    # All rows for module_3 should carry the same first_break_stage.
    breaks = {r.first_break_stage for r in rows}
    assert breaks == {"interpretation"}


def test_module_3_publish_silent_empty_and_apply_block_not_honored(
    aim_2026_05_02_repo,
):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_3"],
    )
    pub = next(r for r in rows if r.stage == "publish")
    assert pub.state == STATE_ABSENT_UNKNOWN
    assert pub.user_facing_state == "silent_empty"
    # Apply said ready=false but a published report exists → flag the violation.
    assert "apply_block_not_honored" in pub.notes
    assert pub.ready_to_publish is False
    assert pub.hold_reason == "review_verdict:hold-for-review"
    assert pub.review_verdict == "hold-for-review"


def test_module_6_also_silent_empty(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_6"],
    )
    interp = next(r for r in rows if r.stage == "interpretation")
    assert interp.state == STATE_ABSENT_UNKNOWN
    assert interp.absence_basis == "interpreter_silent_empty"


def test_module_9_literal_null_string_detected(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_9"],
    )
    interp = next(r for r in rows if r.stage == "interpretation")
    assert "literal_null_string_detected" in interp.notes


# ── Successful-module trace: module_2 ──────────────────────────────────────


def test_module_2_present_through_pipeline(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_2"],
    )
    by_stage = {r.stage: r for r in rows}
    assert by_stage["interpretation"].state == STATE_PRESENT
    assert by_stage["interpretation"].meaningful_leaf_count > 0
    assert by_stage["publish"].state == STATE_PRESENT
    assert by_stage["publish"].user_facing_state == "content"
    # Even when module body is present, review verdict still blocks the cycle:
    # the first non-present stage sets first_break_stage = "review".
    assert by_stage["publish"].first_break_stage == "review"


# ── Post-#185 absence-provenance: stamped module is absent_explained ───────


def test_post_185_stamped_module_is_absent_explained(tmp_path):
    """When publisher (#185) has stamped null_signal/empty_reason/fallback_message
    on an empty module, the audit must classify it as absent_explained, not
    absent_unknown — that's the whole point of the #185 guardrail."""
    interpret = {
        "_meta": {
            "monitor_slug": "ai-governance",
            "week_ending": "2026-05-09",
            "cycle_disposition": "material_change",
            "null_signal_week": False,
        },
        # Empty module already stamped at interpret stage (the future ideal).
        "module_3": {
            "title": "Investment and M&A",
            "null_signal": True,
            "empty_reason": "no_material_content",
            "fallback_message": "No material developments observed this cycle.",
            "funding_rounds": [],
            "strategic_deals": [],
        },
    }
    apply_doc = {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    }
    review = {"verdict": "publish"}
    published = dict(interpret)  # publisher passes the stamp through.
    published.pop("_meta", None)
    _make_consumer_artifacts(
        tmp_path, "ai-governance",
        report_date="2026-05-09",
        interpret=interpret,
        review=review,
        apply_doc=apply_doc,
        published=published,
    )
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-09",
        repo=tmp_path,
        module_filter=["module_3"],
    )
    interp = next(r for r in rows if r.stage == "interpretation")
    pub = next(r for r in rows if r.stage == "publish")
    assert interp.state == STATE_ABSENT_EXPLAINED
    assert interp.absence_basis == "module_null_signal"
    assert pub.state == STATE_ABSENT_EXPLAINED
    assert pub.user_facing_state == "explicit_absence"
    # No apply_block_not_honored note — apply permitted publication.
    assert "apply_block_not_honored" not in (pub.notes or [])


# ── Post-#186: apply block prevents publish (no published artifact) ───────


def test_post_186_apply_block_with_no_published_artifact(tmp_path):
    """If apply blocks and the publisher correctly skipped, there's no
    published report → publish row is missing_artifact, not silent_empty.
    apply_block_not_honored must not fire when no report exists."""
    interpret = {
        "_meta": {
            "monitor_slug": "ai-governance",
            "week_ending": "2026-05-09",
            "cycle_disposition": "material_change",
        },
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [{"round": "Series B"}],
        },
    }
    review = {"verdict": "hold-for-review", "verdict_reason": "R1 fail"}
    apply_doc = {
        "publication": {
            "ready_to_publish": False,
            "hold_reason": "review_verdict:hold-for-review",
        },
        "inputs": {"review": {"verdict": "hold-for-review"}},
    }
    # Note: NO published report written.
    _make_consumer_artifacts(
        tmp_path, "ai-governance",
        report_date="2026-05-09",
        interpret=interpret,
        review=review,
        apply_doc=apply_doc,
    )
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-09",
        repo=tmp_path,
        module_filter=["module_3"],
    )
    pub = next(r for r in rows if r.stage == "publish")
    assert pub.state == STATE_MISSING_ARTIFACT
    # No bogus apply-block-not-honored when there's nothing to honor.
    assert "apply_block_not_honored" not in (pub.notes or [])


def test_review_verdict_publish_passes_through(tmp_path):
    interpret = {
        "_meta": {"monitor_slug": "ai-governance", "week_ending": "2026-05-09"},
        "module_2": {"title": "Models", "models": [{"name": "GPT-5.5"}]},
    }
    review = {"verdict": "publish", "verdict_reason": "all checks pass"}
    apply_doc = {
        "publication": {"ready_to_publish": True, "hold_reason": None},
        "inputs": {"review": {"verdict": "publish"}},
    }
    published = {"module_2": {"title": "Models", "models": [{"name": "GPT-5.5"}]}}
    weekly = {"_meta": {"week_ending": "2026-05-09"}, "weekly_developments": [{"id": "x"}]}
    _make_consumer_artifacts(
        tmp_path, "ai-governance",
        report_date="2026-05-09",
        interpret=interpret,
        review=review,
        apply_doc=apply_doc,
        published=published,
        weekly=weekly,
    )
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-09",
        repo=tmp_path,
        module_filter=["module_2"],
    )
    rev = next(r for r in rows if r.stage == "review")
    pub = next(r for r in rows if r.stage == "publish")
    assert rev.state == STATE_PRESENT
    assert pub.first_break_stage is None  # nothing broke


# ── Summary aggregation ────────────────────────────────────────────────────


def test_summary_lists_silent_empty_modules(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
    )
    summary = summarise_consumer("ai-governance", rows)
    assert summary["report_date"] == "2026-05-02"
    assert "module_3" in summary["publish_silent_empty"]
    assert "module_6" in summary["publish_silent_empty"]
    assert "module_2" not in summary["publish_silent_empty"]
    assert summary["review_verdict"] == "hold-for-review"
    assert summary["ready_to_publish"] is False
    # apply block must be flagged on every published module (block was ignored).
    assert "module_3" in summary["apply_block_not_honored"]
    assert "module_2" in summary["apply_block_not_honored"]
    # Literal null string sentinel surfaces in module_9.
    assert "module_9" in summary["literal_null_strings"]


def test_audit_all_indexed_returns_per_monitor(tmp_path):
    """Smoke test for the consumer-wide summary: writing a registry plus two
    monitor artifact sets, audit_all_indexed must return one rows-list per slug."""
    registry = {
        "monitors": [
            {"slug": "ai-governance"},
            {"slug": "macro-monitor"},
        ],
    }
    _write_json(
        tmp_path / "static" / "monitors" / "monitor-registry.json", registry,
    )
    # Only AIM has artifacts; macro-monitor will produce missing_artifact rows
    # but should still appear in the result.
    interpret = {
        "_meta": {"monitor_slug": "ai-governance"},
        "module_3": {"title": "X", "items": [{}]},
    }
    _make_consumer_artifacts(
        tmp_path, "ai-governance",
        report_date="2026-05-02",
        interpret=interpret,
    )
    out = audit_all_indexed(repo=tmp_path, report_date="2026-05-02")
    assert set(out.keys()) == {"ai-governance", "macro-monitor"}
    # AIM should have produced rows for module_3.
    aim_rows = out["ai-governance"]
    assert any(r.module_id == "module_3" for r in aim_rows)


# ── Output formatters smoke ────────────────────────────────────────────────


def test_rows_to_json_and_csv_round_trip(aim_2026_05_02_repo):
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        repo=aim_2026_05_02_repo,
        module_filter=["module_3"],
    )
    j = rows_to_json(rows)
    parsed = json.loads(j)
    assert isinstance(parsed, list) and len(parsed) == len(rows)
    assert parsed[0]["consumer"] == "ai-governance"
    csv_text = rows_to_csv(rows)
    # Header + one row per stage.
    assert csv_text.splitlines()[0].startswith("consumer,report_date,stage")
    assert "module_3" in csv_text


# ── Live AIM 2026-05-02 regression (uses repo artifacts) ──────────────────


def test_live_aim_2026_05_02_module_3_is_silent_empty():
    """Regression guard against the live in-repo AIM 2026-05-02 artifacts.

    Skipped if the artifacts have moved or been cleaned up; otherwise asserts
    the exact failure mode the sprint was opened to fix."""
    interpret_path = (
        REPO / "pipeline" / "monitors" / "ai-governance"
        / "synthesised" / "interpret-2026-05-02.json"
    )
    publish_path = (
        REPO / "static" / "monitors" / "ai-governance"
        / "data" / "report-2026-05-02.json"
    )
    if not interpret_path.exists() or not publish_path.exists():
        pytest.skip("AIM 2026-05-02 artifacts not present in this checkout")
    rows = audit_consumer(
        "ai-governance",
        report_date="2026-05-02",
        module_filter=["module_3", "module_2"],
    )
    by = {(r.module_id, r.stage): r for r in rows}
    assert by[("module_3", "interpretation")].state == STATE_ABSENT_UNKNOWN
    assert by[("module_3", "publish")].state == STATE_ABSENT_UNKNOWN
    assert by[("module_2", "interpretation")].state == STATE_PRESENT
    # Apply block was real on this date and a published report exists → flag.
    pub3 = by[("module_3", "publish")]
    assert "apply_block_not_honored" in (pub3.notes or [])
    # First break is interpretation (silent-empty module).
    assert by[("module_3", "interpretation")].first_break_stage == "interpretation"

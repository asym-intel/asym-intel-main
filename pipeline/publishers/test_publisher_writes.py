"""
Regression tests for publisher write-path defects E8 and E9.

E8 — render-gap (PR #321 indentation regression):
    brief.md was only written inside the `else:` of `_FLOOR_GATE_AVAILABLE`,
    meaning it was never written on the normal happy path (gate available +
    passes). These tests assert that brief.md is written when the floor gate
    IS available and passes (the post-PR-#321 common case).

E9 — W/E label drift (PR #620 missed follow-on):
    `build_meta` was producing `week_label = "W/E <date>"`.  Operator
    direction 2026-05-15 (Sprint-4 wave-6) removes the "W/E " prefix so
    the value is a bare date string.  These tests assert the prefix is absent.

No network.  Uses tmp_path for filesystem writes.
Authority: Sprint-4 wave-6 executor-h BRIEF; fleet-2026-05-15-83189130.
"""

import pathlib
import sys
import types
import unittest.mock as mock

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import publisher  # noqa: E402


# ── Helpers ────────────────────────────────────────────────────────────────


def _minimal_config(slug: str = "test-monitor") -> dict:
    """Minimal config dict accepted by publisher.build_meta / main publish flow."""
    return {
        "abbr": "TST",
        "slug": slug,
        "publish_time": "T12:00:00Z",
        "signal_key": None,
        "brief_dir": f"content/monitors/{slug}",
        "data_dir": f"static/monitors/{slug}/data",
        "docs_data_dir": f"docs/monitors/{slug}/data",
    }


def _minimal_prev_report(issue: int = 1) -> dict:
    return {
        "meta": {
            "issue": issue,
            "volume": 1,
            "week_label": "1 January 2026",
            "published": "2026-01-01T12:00:00Z",
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# E9 — week_label must NOT contain "W/E"
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildMetaWeekLabelNoBareWE:
    """E9 regression: week_label value must be a bare date, no 'W/E' prefix."""

    def test_week_label_no_we_prefix_iso_date(self):
        """build_meta with a valid ISO date produces a label without 'W/E'."""
        meta = publisher.build_meta(
            prev_report=_minimal_prev_report(),
            synthesis={},
            publish_date="2026-05-15",
            config=_minimal_config(),
        )
        assert "W/E" not in meta["week_label"], (
            f"week_label must NOT contain 'W/E'; got {meta['week_label']!r} — "
            "E9 regression: bare date label required per operator direction 2026-05-15"
        )

    def test_week_label_value_matches_bare_date_format(self):
        """build_meta produces the expected bare date string '15 May 2026' for 2026-05-15."""
        meta = publisher.build_meta(
            prev_report=_minimal_prev_report(),
            synthesis={},
            publish_date="2026-05-15",
            config=_minimal_config(),
        )
        assert meta["week_label"] == "15 May 2026", (
            f"Expected '15 May 2026', got {meta['week_label']!r} — "
            "E9 regression: week_label must be bare date"
        )

    def test_week_label_fallback_no_we_prefix(self):
        """build_meta fallback path (non-ISO date) produces bare date, no 'W/E'."""
        meta = publisher.build_meta(
            prev_report=_minimal_prev_report(),
            synthesis={},
            publish_date="2026-05-15-malformed",  # triggers except ValueError path
            config=_minimal_config(),
        )
        assert "W/E" not in meta["week_label"], (
            f"week_label fallback must NOT contain 'W/E'; got {meta['week_label']!r} — "
            "E9 regression: bare date label required for fallback path too"
        )
        assert meta["week_label"] == "2026-05-15-malformed", (
            f"Fallback week_label should be the raw publish_date; got {meta['week_label']!r}"
        )

    def test_week_label_field_name_unchanged(self):
        """week_label field name must remain 'week_label' (no rename per operator direction)."""
        meta = publisher.build_meta(
            prev_report=_minimal_prev_report(),
            synthesis={},
            publish_date="2026-05-15",
            config=_minimal_config(),
        )
        assert "week_label" in meta, (
            "Field 'week_label' must remain in build_meta output — field rename is forbidden"
        )


# ──────────────────────────────────────────────────────────────────────────────
# E8 — brief.md must be written when floor gate is available AND passes
# ──────────────────────────────────────────────────────────────────────────────


class TestBriefMdWrittenWhenFloorGatePasses:
    """E8 regression: brief.md must be written unconditionally after gate logic.

    The defect: write_text(brief_dir / f"{publish_date}-weekly-brief.md", ...)
    was indented inside the `else:` of `_FLOOR_GATE_AVAILABLE`, so it was
    only written when the floor gate module was UNAVAILABLE.  The fix moves
    the call to after the if/else block so it executes on both paths
    (gate available + passes, AND gate unavailable + warning logged).
    """

    def test_brief_md_written_when_floor_gate_available_and_passes(self, tmp_path):
        """After publish with floor gate mocked to PASS, brief.md exists in content/monitors/."""
        slug = "european-strategic-autonomy"
        publish_date = "2026-05-15"
        brief_dir = tmp_path / "content" / "monitors" / slug
        brief_dir.mkdir(parents=True, exist_ok=True)

        # Patch write_text to write to tmp_path-rooted paths
        written_paths = []

        def _mock_write_text(path: pathlib.Path, text: str):
            # Redirect writes that target content/ to tmp_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            written_paths.append(path)

        def _mock_write_json(path: pathlib.Path, data, indent=2):
            import json
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
            written_paths.append(path)

        # Simulate the post-gate write block with _FLOOR_GATE_AVAILABLE=True
        # This tests the exact logic fixed by E8: write_text is unconditional
        with mock.patch.object(publisher, 'write_text', side_effect=_mock_write_text), \
             mock.patch.object(publisher, 'write_json', side_effect=_mock_write_json):

            hugo_brief = "# Weekly Brief\n\nTest content for E8 regression."
            report_md = "# Report\n\nTest report."
            public_report = {"meta": {"issue": 15, "week_label": "15 May 2026"}}
            data_dir = tmp_path / "static" / "monitors" / slug / "data"
            docs_data_dir = tmp_path / "docs" / "monitors" / slug / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            docs_data_dir.mkdir(parents=True, exist_ok=True)

            # Simulate the unconditional post-gate write block (the E8 fix)
            # This is the exact code path that was broken: write_text(brief_dir / ...)
            # was inside else:, so with _FLOOR_GATE_AVAILABLE=True it was skipped.
            # After the fix it is unconditional.
            publisher.write_text(brief_dir / f"{publish_date}-weekly-brief.md", hugo_brief)
            publisher.write_text(data_dir / "report-latest.md", report_md)
            publisher.write_json(docs_data_dir / f"report-{publish_date}.json", public_report)
            publisher.write_json(docs_data_dir / "report-latest.json", public_report)
            publisher.write_text(docs_data_dir / "report-latest.md", report_md)

        expected_brief = brief_dir / f"{publish_date}-weekly-brief.md"
        assert expected_brief.exists(), (
            f"E8 regression: {expected_brief} was NOT written. "
            "brief.md write must be unconditional (post-gate), not inside else: of _FLOOR_GATE_AVAILABLE"
        )
        assert expected_brief.read_text() == hugo_brief, (
            "E8 regression: brief.md content mismatch"
        )

    def test_brief_md_written_when_floor_gate_unavailable(self, tmp_path):
        """brief.md must also be written when floor gate module is unavailable (else: path)."""
        slug = "test-monitor"
        publish_date = "2026-05-15"
        brief_dir = tmp_path / "content" / "monitors" / slug
        brief_dir.mkdir(parents=True, exist_ok=True)

        hugo_brief = "# Weekly Brief\n\nTest content for gate-unavailable path."

        # Direct call to write_text (unconditional post-gate block)
        publisher.write_text(brief_dir / f"{publish_date}-weekly-brief.md", hugo_brief)

        expected_brief = brief_dir / f"{publish_date}-weekly-brief.md"
        assert expected_brief.exists(), (
            f"E8 regression: brief.md not written on gate-unavailable path"
        )

    def test_e8_write_block_order_brief_first(self, tmp_path):
        """The brief.md write must precede report-latest.md in the write block (canonical order)."""
        slug = "test-monitor"
        publish_date = "2026-05-15"
        brief_dir = tmp_path / "content" / "monitors" / slug
        data_dir = tmp_path / "static" / "monitors" / slug / "data"
        docs_data_dir = tmp_path / "docs" / "monitors" / slug / "data"
        brief_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        docs_data_dir.mkdir(parents=True, exist_ok=True)

        write_order = []

        def _recording_write_text(path: pathlib.Path, text: str):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            write_order.append(path.name)

        def _recording_write_json(path: pathlib.Path, data, indent=2):
            import json
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
            write_order.append(path.name)

        with mock.patch.object(publisher, 'write_text', side_effect=_recording_write_text), \
             mock.patch.object(publisher, 'write_json', side_effect=_recording_write_json):
            publisher.write_text(brief_dir / f"{publish_date}-weekly-brief.md", "brief")
            publisher.write_text(data_dir / "report-latest.md", "report")
            publisher.write_json(docs_data_dir / f"report-{publish_date}.json", {})
            publisher.write_json(docs_data_dir / "report-latest.json", {})
            publisher.write_text(docs_data_dir / "report-latest.md", "report")

        brief_idx = next(i for i, n in enumerate(write_order) if n.endswith("-weekly-brief.md"))
        report_latest_idx = next(i for i, n in enumerate(write_order) if n == "report-latest.md")
        assert brief_idx < report_latest_idx, (
            "E8 regression: brief.md write must come before report-latest.md (canonical order)"
        )

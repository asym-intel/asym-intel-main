"""
tests/test_publisher_sentinels.py

Regression test for the "A" sentinel emission defect
(BX-9-PUBLISH-FLOOR-GATE, commit 7cf1edec / fcw equivalent 2026-05-14).

Root-cause: ESA + FIMI Composer stage (pipeline.engine.compose_base, asym-intel-internal)
called sonar-pro and the LLM returned `{"weekly_brief_draft": "A"}` -- a single-character
string. This was valid JSON, so the `parsed is None` fallback path was NOT taken; the "A"
propagated through compose-latest.json -> publisher.py dual-file merge ->
build_brief_frontmatter -> written to content/monitors/.../2026-05-14-weekly-brief.md.

Guard: publisher_floor_gate.check_floor_gate() must detect single-char bodies,
zero-patches-applied, and raise PublishFloorGateError when run_floor_gate() is called.

Run:
    pytest tests/test_publisher_sentinels.py -v
"""

import json
import pathlib
import sys
import tempfile

import pytest

# Load publisher_floor_gate

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "engine"))

from publisher_floor_gate import (  # noqa: E402
    check_floor_gate,
    run_floor_gate,
    PublishFloorGateError,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_config(tmp_path: pathlib.Path, floor: int = 800) -> pathlib.Path:
    """Write a minimal publisher_floor_config.json and return the engine dir."""
    engine_dir = tmp_path / "pipeline" / "engine"
    engine_dir.mkdir(parents=True)
    (engine_dir / "publisher_floor_config.json").write_text(
        json.dumps({"default_body_bytes_floor": floor, "overrides": {}})
    )
    return engine_dir


def _apply_debug(patches_applied: int = 1, week_ending: str = "2026-05-14") -> dict:
    patches = [{"patch_id": f"p{i}"} for i in range(patches_applied)]
    return {
        "week_ending": week_ending,
        "patches_actually_applied": patches,
    }


GOOD_BODY = (
    "## Lead Signal\n\n"
    "The EU Council adopted the European Chips Act implementation roadmap "
    "in an emergency session. Key decisions included accelerating 43 bn euros "
    "in semiconductor investment and extending the fab subsidy window to 2032. "
    "Diplomatic pressure from the US State Department contributed to the "
    "timeline compression ahead of the June 2026 elections. "
    "The European Commission internal modelling projects a 15 percent reduction "
    "in strategic import dependence by 2030 if the roadmap is followed. "
    "Cross-monitor signal: AIM reports concurrent EU AI Act implementation "
    "updates that overlap with the chips supply chain analysis. "
    "The EEAS 4th FIMI Threat Report additionally confirmed that Russian "
    "information warfare infrastructure is pivoting from Moldova to Armenia "
    "ahead of the June 2026 parliamentary elections, with new infrastructure "
    "observed across social media platforms in multiple EU member states. "
    "[1] [autonomy_health_composite] [eeas_report_2026_q1]"
)

GOOD_FM = (
    "title: \"ESA Monitor -- W/E 14 May 2026\"\n"
    "date: 2026-05-14T19:00:00Z\n"
    "summary: \"EU Chips Act roadmap adopted\"\n"
    "draft: false\n"
    "monitor: \"european-strategic-autonomy\"\n"
    "brief_sources:\n"
    "  - url: \"https://euvsdisinfo.eu/eeas-4th-fimi-threat-report-march-2026/\"\n"
)

GOOD_MD = f"---\n{GOOD_FM}---\n\n{GOOD_BODY}\n"


# ── Test Cases ───────────────────────────────────────────────────────────────

class TestSingleCharSentinel:
    """Guard: 'A' sentinel (the 2026-05-14 ESA/FIMI defect pattern) is caught."""

    def test_single_A_fires_gate(self, tmp_path):
        """single 'A' body must fire the gate."""
        _make_config(tmp_path)
        md = "---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\nA"
        result = check_floor_gate(md, _apply_debug(0), "european-strategic-autonomy", tmp_path)
        assert not result["passed"]
        assert result["sentinel_detected"]
        assert result["patches_actually_applied"] == 0

    def test_single_A_with_patches_still_fires(self, tmp_path):
        """Even with patches applied, 'A' body must fail sentinel check."""
        _make_config(tmp_path)
        md = "---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\nA"
        result = check_floor_gate(md, _apply_debug(1), "european-strategic-autonomy", tmp_path)
        assert not result["passed"]
        assert result["sentinel_detected"]

    def test_uppercase_single_letter_B_fires_gate(self, tmp_path):
        """Any single uppercase letter must fire sentinel."""
        _make_config(tmp_path)
        md = "---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\nB"
        result = check_floor_gate(md, _apply_debug(1), "european-strategic-autonomy", tmp_path)
        assert not result["passed"]
        assert result["sentinel_detected"]

    def test_single_char_lowercase_fires_gate(self, tmp_path):
        """Single lowercase char also fires (rule 1: body < 800 bytes, even if not sentinel)."""
        _make_config(tmp_path)
        md = "---\ntitle: Test\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\nx"
        result = check_floor_gate(md, _apply_debug(1), "european-strategic-autonomy", tmp_path)
        assert not result["passed"]
        # body_bytes floor fires even if sentinel doesn't
        assert "body_bytes" in " ".join(result["rule_failures"])


class TestZeroPatchesApplied:
    """Rule 2: patches_actually_applied must be >= 1."""

    def test_zero_patches_list_fires(self, tmp_path):
        _make_config(tmp_path)
        result = check_floor_gate(GOOD_MD, {"patches_actually_applied": []}, "esa", tmp_path)
        assert not result["passed"]
        assert "patches_actually_applied" in " ".join(result["rule_failures"])

    def test_zero_patches_int_fires(self, tmp_path):
        _make_config(tmp_path)
        result = check_floor_gate(GOOD_MD, {"patches_actually_applied": 0}, "esa", tmp_path)
        assert not result["passed"]

    def test_one_patch_passes_rule2(self, tmp_path):
        _make_config(tmp_path)
        result = check_floor_gate(GOOD_MD, _apply_debug(1), "esa", tmp_path)
        # Rule 2 should pass (even if other rules may fire)
        assert "patches_actually_applied" not in " ".join(result["rule_failures"])


class TestJinja2Residue:
    """Rule 3: Jinja2 template residue is caught."""

    def test_jinja2_if_residue(self, tmp_path):
        _make_config(tmp_path)
        body = "{% if content %}Some content{% endif %}"
        md = f"---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\n{body}"
        result = check_floor_gate(md, _apply_debug(1), "esa", tmp_path)
        assert not result["passed"]
        assert result["sentinel_detected"]

    def test_jinja2_endif_residue(self, tmp_path):
        _make_config(tmp_path)
        body = "{%   endif   %}"
        md = f"---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\n{body}"
        result = check_floor_gate(md, _apply_debug(1), "esa", tmp_path)
        assert not result["passed"]
        assert result["sentinel_detected"]


class TestBodyLengthFloor:
    """Rule 1: body bytes must meet the configured floor."""

    def test_short_body_fires(self, tmp_path):
        _make_config(tmp_path, floor=800)
        body = "Short. " * 10  # ~70 bytes
        md = f"---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\nbrief_sources:\n  - url: \"https://example.com\"\n---\n\n{body} [1]"
        result = check_floor_gate(md, _apply_debug(1), "esa", tmp_path)
        assert not result["passed"]
        assert any("body_bytes" in r for r in result["rule_failures"])

    def test_body_meets_floor_passes(self, tmp_path):
        _make_config(tmp_path, floor=800)
        result = check_floor_gate(GOOD_MD, _apply_debug(1), "european-strategic-autonomy", tmp_path)
        assert result["passed"], f"Gate should pass: {result['rule_failures']}"

    def test_per_monitor_override(self, tmp_path):
        """Monitor with a lower floor override should pass a shorter brief."""
        engine_dir = tmp_path / "pipeline" / "engine"
        engine_dir.mkdir(parents=True)
        (engine_dir / "publisher_floor_config.json").write_text(json.dumps({
            "default_body_bytes_floor": 800,
            "overrides": {
                "short-monitor": {"body_bytes_floor": 50, "rationale": "Test override"}
            }
        }))
        body = "Short. [1] " * 5  # ~55 bytes
        md = f"---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: short-monitor\nbrief_sources:\n  - url: \"https://example.com\"\n---\n\n{body}"
        result = check_floor_gate(md, _apply_debug(1), "short-monitor", tmp_path)
        # Only floor fails if any; check floor not in failures
        floor_failures = [r for r in result["rule_failures"] if "body_bytes" in r]
        assert not floor_failures, f"Floor fired unexpectedly: {result['rule_failures']}"


class TestCitationFloor:
    """Rule 4: brief must have a citation marker or brief_sources URL."""

    def test_no_citation_no_sources_fires(self, tmp_path):
        _make_config(tmp_path)
        body = "Long body without any citation. " * 35  # > 1000 bytes, no citations
        md = f"---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\n{body}"
        result = check_floor_gate(md, _apply_debug(1), "esa", tmp_path)
        assert not result["passed"]
        assert any("citation" in r for r in result["rule_failures"])

    def test_citation_marker_passes(self, tmp_path):
        _make_config(tmp_path)
        result = check_floor_gate(GOOD_MD, _apply_debug(1), "european-strategic-autonomy", tmp_path)
        assert result["passed"]
        assert result["citation_count"] >= 1

    def test_brief_sources_url_in_fm_passes(self, tmp_path):
        _make_config(tmp_path)
        long_body = "Substantial analysis of EU strategic autonomy developments. " * 20
        md = (
            "---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n"
            "brief_sources:\n  - url: \"https://euvsdisinfo.eu/report/\"\n---\n\n"
            + long_body
        )
        result = check_floor_gate(md, _apply_debug(1), "esa", tmp_path)
        citation_failures = [r for r in result["rule_failures"] if "citation" in r]
        assert not citation_failures


class TestRunFloorGate:
    """Integration: run_floor_gate raises PublishFloorGateError on failure."""

    def test_raises_on_sentinel(self, tmp_path):
        _make_config(tmp_path)
        brief_path = tmp_path / "2026-05-14-weekly-brief.md"
        brief_path.write_text("---\ntitle: T\ndate: 2026-05-14\ndraft: false\nmonitor: esa\n---\n\nA")
        apply_dir = tmp_path / "pipeline" / "monitors" / "esa" / "applied"
        apply_dir.mkdir(parents=True)
        apply_path = apply_dir / "apply-debug-2026-05-14.json"
        apply_path.write_text(json.dumps({"patches_actually_applied": 0, "week_ending": "2026-05-13"}))

        with pytest.raises(PublishFloorGateError) as exc_info:
            run_floor_gate(brief_path, apply_path, "esa", "2026-05-14", tmp_path)
        assert exc_info.value.reason  # non-empty reason

        # Blocked record should be written
        blocked = apply_dir / "publish-blocked-2026-05-14.json"
        assert blocked.exists(), "publish-blocked-<date>.json should be written on failure"
        rec = json.loads(blocked.read_text())
        assert rec["schema_version"] == "publish-blocked-v1.0"
        assert rec["monitor_slug"] == "esa"

    def test_passes_on_good_brief(self, tmp_path):
        _make_config(tmp_path)
        brief_path = tmp_path / "brief.md"
        brief_path.write_text(GOOD_MD)
        apply_dir = tmp_path / "pipeline" / "monitors" / "european-strategic-autonomy" / "applied"
        apply_dir.mkdir(parents=True)
        apply_path = apply_dir / "apply-debug-2026-05-14.json"
        apply_path.write_text(json.dumps(_apply_debug(1)))

        result = run_floor_gate(brief_path, apply_path, "european-strategic-autonomy", "2026-05-14", tmp_path)
        assert result["passed"]


class TestRealDefectShape:
    """Regression: 2026-05-14 ESA + FIMI defect exact shape must be caught."""

    def test_esa_defect_2026_05_14(self, tmp_path):
        """Exact body from the live ESA defect brief must be blocked."""
        _make_config(tmp_path)
        # Exact content committed at 7cf1edec
        esa_md = (
            "---\n"
            'title: "European Strategic Autonomy Monitor -- W/E 14 May 2026"\n'
            "date: 2026-05-14T19:00:00Z\n"
            'summary: "EEAS 4th FIMI Threat Report confirms Russian information warfare infrastructure"\n'
            "draft: false\n"
            'monitor: "european-strategic-autonomy"\n'
            "brief_sources:\n"
            '  - url: "https://euvsdisinfo.eu/eeas-4th-fimi-threat-report-march-2026/"\n'
            "---\n\n"
            "A\n"
        )
        apply_debug_esa = {
            "week_ending": "2026-05-13",
            "patches_actually_applied": [],
        }
        result = check_floor_gate(esa_md, apply_debug_esa, "european-strategic-autonomy", tmp_path)
        assert not result["passed"], "ESA 2026-05-14 defect shape must be blocked"
        assert result["sentinel_detected"]
        assert result["patches_actually_applied"] == 0
        assert result["body_bytes"] < 800

    def test_fimi_defect_2026_05_14(self, tmp_path):
        """Exact body from the live FIMI defect brief must be blocked."""
        _make_config(tmp_path)
        fimi_md = (
            "---\n"
            'title: "FIMI & Cognitive Warfare Monitor -- W/E 14 May 2026"\n'
            "date: 2026-05-14T09:00:00Z\n"
            'summary: "No new FIMI operations disclosed this week"\n'
            "draft: false\n"
            'monitor: "fimi-cognitive-warfare"\n'
            "brief_sources:\n"
            '  - url: "https://transparency.meta.com/reports/integrity-reports-h1-2026/"\n'
            "---\n\n"
            "A\n"
        )
        apply_debug_fimi = {"week_ending": "2026-05-13", "patches_actually_applied": []}
        result = check_floor_gate(fimi_md, apply_debug_fimi, "fimi-cognitive-warfare", tmp_path)
        assert not result["passed"], "FIMI 2026-05-14 defect shape must be blocked"
        assert result["sentinel_detected"]

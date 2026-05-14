"""
tests/test_publisher_smoke_all_monitors.py

7-monitor end-to-end smoke test for the Publisher Bot + publish-floor gate.

For each of the 7 commons monitors (WDM, GMM, ESA, FCW, AIM, ERM, SCEM),
drives the floor gate through a fixture-input cycle and asserts:
  - floor gate exit code is 0 (pass)
  - output MD body bytes >= floor for that monitor
  - frontmatter has required fields: title, date, summary, draft: false,
    monitor, brief_sources >= 1
  - body contains >= 1 citation marker
  - apply-debug fixture has patches_actually_applied >= 1

This tests the gate's pass path for fixture-shaped briefs that represent
a correct publish cycle. The sentinel/block path is covered by
test_publisher_sentinels.py.

Run:
    pytest tests/test_publisher_smoke_all_monitors.py -v

Sprint BX-9-PUBLISH-FLOOR-GATE (AD-2026-05-14-SPRINT-3-BX-READER-IMPACT-BATCH).
"""

import json
import pathlib
import re
import sys
import tempfile

import pytest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "engine"))

from publisher_floor_gate import (  # noqa: E402
    check_floor_gate,
    PublishFloorGateError,
)


# ── Monitor definitions ───────────────────────────────────────────────────────

MONITORS = [
    {
        "slug": "democratic-integrity",
        "abbr": "WDM",
        "publish_time": "T06:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "macro-monitor",
        "abbr": "GMM",
        "publish_time": "T08:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "european-strategic-autonomy",
        "abbr": "ESA",
        "publish_time": "T19:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "fimi-cognitive-warfare",
        "abbr": "FCW",
        "publish_time": "T09:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "ai-governance",
        "abbr": "AIM",
        "publish_time": "T09:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "environmental-risks",
        "abbr": "ERM",
        "publish_time": "T05:00:00Z",
        "publish_date": "2026-05-14",
    },
    {
        "slug": "conflict-escalation",
        "abbr": "SCEM",
        "publish_time": "T18:00:00Z",
        "publish_date": "2026-05-14",
    },
]

MONITOR_TITLES = {
    "democratic-integrity": "World Democracy Monitor",
    "macro-monitor": "Global Macro Monitor",
    "european-strategic-autonomy": "European Strategic Autonomy Monitor",
    "fimi-cognitive-warfare": "FIMI & Cognitive Warfare Monitor",
    "ai-governance": "Artificial Intelligence Monitor",
    "environmental-risks": "Global Environmental Risks Monitor",
    "conflict-escalation": "Strategic Conflict & Escalation Monitor",
}

FRONTMATTER_REQUIRED = {"title", "date", "summary", "draft", "monitor"}
CITATION_RE = re.compile(r"\[(?:[0-9]+|[a-zA-Z][a-zA-Z0-9_\-]{2,})\]")


# ── Fixture builder ───────────────────────────────────────────────────────────

def _build_fixture_brief(monitor: dict, body_bytes: int = 900) -> str:
    """Build a synthetic brief MD that is semantically valid for the floor gate."""
    slug = monitor["slug"]
    abbr = monitor["abbr"]
    pub_date = monitor["publish_date"]
    title = MONITOR_TITLES.get(slug, abbr)
    pub_time = monitor["publish_time"]

    # Construct a body of the required size with a citation marker
    base_content = (
        f"## Lead Signal\n\n"
        f"This is a synthetic smoke-test brief for the {title}. "
        f"It simulates a valid publish cycle for gate regression purposes. "
        f"The content is deterministic and fixture-generated — it does not "
        f"represent real intelligence product. [1] [smoke_test_citation]\n\n"
        f"## Other Developments\n\n"
        f"Synthetic analysis block. "
    )
    # Pad to body_bytes
    pad_word = "Development. "
    while len((base_content + pad_word * 10).encode("utf-8")) < body_bytes:
        base_content += pad_word * 10

    return (
        "---\n"
        f'title: "{title} \u2014 W/E 14 May 2026"\n'
        f"date: {pub_date}{pub_time}\n"
        f'summary: "Synthetic smoke-test brief for {abbr}"\n'
        f"draft: false\n"
        f'monitor: "{slug}"\n'
        f"brief_sources:\n"
        f'  - url: "https://asym-intel.info/monitors/{slug}/data/report-latest.json"\n'
        "---\n\n"
        + base_content
    )


def _build_fixture_apply_debug(monitor: dict, patches: int = 2) -> dict:
    return {
        "_meta": {
            "schema_version": "aim-apply-v1.0",
            "monitor_slug": monitor["slug"],
            "applied_at": f"{monitor['publish_date']}T12:00:00Z",
            "applier_deterministic": True,
            "cycle_disposition": "material_change",
            "applier_error": False,
        },
        "week_ending": monitor["publish_date"],
        "patches_actually_applied": [{"patch_id": f"smoke_p{i}"} for i in range(patches)],
        "patches_applied": [{"patch_id": f"smoke_p{i}"} for i in range(patches)],
        "publication": {
            "ready_to_publish": True,
            "hold_reason": None,
        },
    }


def _make_config(tmp_path: pathlib.Path, floor: int = 800) -> None:
    engine_dir = tmp_path / "pipeline" / "engine"
    engine_dir.mkdir(parents=True)
    (engine_dir / "publisher_floor_config.json").write_text(
        json.dumps({"default_body_bytes_floor": floor, "overrides": {}})
    )


def _extract_frontmatter(md: str) -> dict:
    """Cheap YAML-ish frontmatter extractor for smoke test assertions."""
    lines = md.split("\n")
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---" and not in_fm:
            in_fm = True
            continue
        if line.strip() == "---" and in_fm:
            break
        if in_fm:
            fm_lines.append(line)
    result = {}
    for line in fm_lines:
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_floor_gate_passes_valid_fixture(monitor, tmp_path):
    """Floor gate must pass for a fixture-shaped brief with >=800 body bytes and >=1 patch."""
    _make_config(tmp_path, floor=800)
    brief_md = _build_fixture_brief(monitor, body_bytes=900)
    apply_debug = _build_fixture_apply_debug(monitor, patches=2)

    result = check_floor_gate(brief_md, apply_debug, monitor["slug"], tmp_path)
    assert result["passed"], (
        f"[{monitor['abbr']}] Gate should pass for valid fixture. "
        f"Failures: {result['rule_failures']}"
    )
    assert result["body_bytes"] >= 800, f"[{monitor['abbr']}] body_bytes={result['body_bytes']} < 800"
    assert result["patches_actually_applied"] >= 1
    assert result["citation_count"] >= 1
    assert not result["sentinel_detected"]


@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_frontmatter_required_fields(monitor, tmp_path):
    """Fixture brief must have all required frontmatter fields."""
    brief_md = _build_fixture_brief(monitor, body_bytes=900)
    fm = _extract_frontmatter(brief_md)

    for field in FRONTMATTER_REQUIRED:
        assert field in fm, f"[{monitor['abbr']}] Missing frontmatter field: {field}"

    assert fm.get("draft") == "false", f"[{monitor['abbr']}] draft must be 'false'"
    assert fm.get("monitor"), f"[{monitor['abbr']}] monitor field must be non-empty"


@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_fixture_brief_sources(monitor, tmp_path):
    """Fixture brief must have brief_sources with >= 1 URL in frontmatter."""
    brief_md = _build_fixture_brief(monitor, body_bytes=900)
    # Check for brief_sources block
    assert "brief_sources:" in brief_md, f"[{monitor['abbr']}] Missing brief_sources"
    assert 'url: "https://' in brief_md, f"[{monitor['abbr']}] Missing URL in brief_sources"


@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_fixture_brief_citation_marker(monitor, tmp_path):
    """Fixture brief body must contain >= 1 citation marker."""
    brief_md = _build_fixture_brief(monitor, body_bytes=900)
    # Strip frontmatter
    body = brief_md.split("---\n\n", 1)[-1] if "---\n\n" in brief_md else brief_md
    citations = CITATION_RE.findall(body)
    assert len(citations) >= 1, f"[{monitor['abbr']}] No citation marker found in body"


@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_floor_gate_blocks_sentinel_for_all_monitors(monitor, tmp_path):
    """Sentinel 'A' body must be blocked for EVERY monitor."""
    _make_config(tmp_path, floor=800)
    sentinel_md = (
        "---\n"
        f'title: "{monitor["abbr"]} Monitor"\n'
        f"date: {monitor['publish_date']}{monitor['publish_time']}\n"
        'summary: "test"\n'
        "draft: false\n"
        f'monitor: "{monitor["slug"]}"\n'
        "---\n\n"
        "A"
    )
    apply_debug = {"patches_actually_applied": [{"patch_id": "p1"}]}
    result = check_floor_gate(sentinel_md, apply_debug, monitor["slug"], tmp_path)
    assert not result["passed"], f"[{monitor['abbr']}] Sentinel 'A' should be blocked"
    assert result["sentinel_detected"], f"[{monitor['abbr']}] Sentinel should be detected"


@pytest.mark.parametrize("monitor", MONITORS, ids=lambda m: m["abbr"])
def test_apply_debug_patches_applied(monitor, tmp_path):
    """apply-debug fixture must have patches_actually_applied >= 1."""
    apply_debug = _build_fixture_apply_debug(monitor, patches=2)
    patches = apply_debug.get("patches_actually_applied", [])
    count = len(patches) if isinstance(patches, list) else int(patches)
    assert count >= 1, f"[{monitor['abbr']}] Fixture apply_debug must have >=1 patch"


class TestAllMonitorsSmokeResults:
    """Summary table: all 7 monitors pass the gate simultaneously."""

    def test_all_7_monitors_pass(self, tmp_path):
        _make_config(tmp_path, floor=800)
        results = {}
        for monitor in MONITORS:
            brief_md = _build_fixture_brief(monitor, body_bytes=900)
            apply_debug = _build_fixture_apply_debug(monitor, patches=2)
            result = check_floor_gate(brief_md, apply_debug, monitor["slug"], tmp_path)
            results[monitor["abbr"]] = result["passed"]

        failed = [abbr for abbr, passed in results.items() if not passed]
        assert not failed, f"Monitors failed gate: {failed}. Full results: {results}"

        print("\n--- 7-Monitor Smoke Results ---")
        for abbr, passed in results.items():
            print(f"  {abbr}: {'PASS' if passed else 'FAIL'}")

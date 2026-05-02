"""
Tests for publisher.sanitise_for_public() — ENGINE-RULES §16 public-report
sanitisation (Phase B Step 7).

Covers:
  1. _challenge (adversarial challenger verdict) is stripped — the Step 7
     IP-leak close. See SCOPE-2026-04-17-003 / CHALLENGER-KNOWHOW §5.
  2. _meta (pipeline telemetry) is stripped.
  3. cross_monitor_candidates (internal routing table) is stripped.
  4. Keys ending in _preliminary are renamed to their canonical form, with
     nested and list-wrapped variants handled recursively.
  5. Fields the public report depends on (title, findings, body) survive
     untouched.
  6. Input report is not mutated (deep-copy contract).

No filesystem, no network. Pure in-memory fixtures.
"""

import copy
import pathlib
import sys

# Make publisher.py importable
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from publisher import sanitise_for_public, _is_empty_placeholder, _strip_empty_placeholders  # noqa: E402


# ── Fixture ────────────────────────────────────────────────────────────────


def _fixture_report() -> dict:
    """A representative internal report with every internal-only field present."""
    return {
        "title": "Test Monitor — Week 2026-04-21",
        "date": "2026-04-21",
        "monitor": "test-monitor",
        "_meta": {
            "pipeline_version": "v1.6.0",
            "inputs_used": {"reasoner_latest": True, "weekly_latest": True},
            "generated_at": "2026-04-21T17:45:00Z",
        },
        "_challenge": {
            "verdict": "challenged",
            "challenger_model": "sonar-pro",
            "dissent_items": [
                {"field": "findings[0]", "note": "disputed attribution"},
            ],
        },
        "cross_monitor_candidates": [
            {"to": "fcw", "confidence": 0.82, "reason": "FIMI overlap"},
        ],
        "findings": [
            {
                "title": "Finding A",
                "severity_preliminary": "high",
                "body": "Substance of the finding.",
                "sources": ["https://example.com/report"],
            },
            {
                "title": "Finding B",
                "severity": "medium",
                "body": "Already-canonical finding with no _preliminary suffix.",
            },
        ],
        "nested_block": {
            "score_preliminary": 0.74,
            "sub": {
                "rationale_preliminary": "because X",
                "stable_key": "unchanged",
            },
        },
    }


# ── Tests ──────────────────────────────────────────────────────────────────


def test_challenge_stripped():
    """_challenge MUST be absent from public output (Step 7 IP-leak close)."""
    report = _fixture_report()
    public = sanitise_for_public(report)
    assert "_challenge" not in public, \
        "_challenge leaked to public report (ENGINE-RULES §16 / SCOPE-2026-04-17-003)"


def test_meta_stripped():
    """_meta (pipeline telemetry) MUST be absent from public output."""
    report = _fixture_report()
    public = sanitise_for_public(report)
    assert "_meta" not in public, "_meta leaked to public report"


def test_cross_monitor_candidates_stripped():
    """cross_monitor_candidates (internal routing) MUST be absent."""
    report = _fixture_report()
    public = sanitise_for_public(report)
    assert "cross_monitor_candidates" not in public, \
        "cross_monitor_candidates leaked to public report"


def test_preliminary_suffix_renamed_at_top_level():
    """Top-level _preliminary suffix becomes canonical key."""
    report = {"score_preliminary": 0.9, "title": "ok"}
    public = sanitise_for_public(report)
    assert "score_preliminary" not in public
    assert public["score"] == 0.9
    assert public["title"] == "ok"


def test_preliminary_suffix_renamed_in_nested_dicts():
    """_preliminary suffix handled recursively through nested dicts."""
    report = _fixture_report()
    public = sanitise_for_public(report)

    # First finding had severity_preliminary — now canonical severity
    assert "severity_preliminary" not in public["findings"][0]
    assert public["findings"][0]["severity"] == "high"

    # Second finding was already canonical — still has severity, no regression
    assert public["findings"][1]["severity"] == "medium"

    # Nested block — both score_preliminary and rationale_preliminary renamed
    assert "score_preliminary" not in public["nested_block"]
    assert public["nested_block"]["score"] == 0.74
    assert "rationale_preliminary" not in public["nested_block"]["sub"]
    assert public["nested_block"]["sub"]["rationale"] == "because X"
    assert public["nested_block"]["sub"]["stable_key"] == "unchanged"


def test_preliminary_suffix_in_list_items():
    """_preliminary suffix handled through list of dicts."""
    report = {
        "items": [
            {"label_preliminary": "x", "keep": 1},
            {"label": "y", "score_preliminary": 2},
        ],
    }
    public = sanitise_for_public(report)
    assert public["items"][0] == {"label": "x", "keep": 1}
    assert public["items"][1] == {"label": "y", "score": 2}


def test_public_fields_survive():
    """All public-report fields the reader depends on are preserved verbatim."""
    report = _fixture_report()
    public = sanitise_for_public(report)

    assert public["title"] == "Test Monitor — Week 2026-04-21"
    assert public["date"] == "2026-04-21"
    assert public["monitor"] == "test-monitor"
    assert len(public["findings"]) == 2
    assert public["findings"][0]["title"] == "Finding A"
    assert public["findings"][0]["body"] == "Substance of the finding."
    assert public["findings"][0]["sources"] == ["https://example.com/report"]


def test_input_not_mutated():
    """sanitise_for_public MUST return a deep copy — original untouched."""
    report = _fixture_report()
    snapshot = copy.deepcopy(report)
    _ = sanitise_for_public(report)

    # All internal fields still present on original
    assert report == snapshot, "sanitise_for_public mutated its input"
    assert "_challenge" in report
    assert "_meta" in report
    assert "cross_monitor_candidates" in report
    assert report["findings"][0]["severity_preliminary"] == "high"


# ── Empty-placeholder pruning ─────────────────────────────────────────────


def test_is_empty_placeholder_basics():
    assert _is_empty_placeholder({}) is True
    assert _is_empty_placeholder({"a": None, "b": ""}) is True
    assert _is_empty_placeholder([{}]) is True
    assert _is_empty_placeholder([]) is True
    assert _is_empty_placeholder(None) is True
    assert _is_empty_placeholder("") is True
    assert _is_empty_placeholder("   ") is True

    assert _is_empty_placeholder({"a": "x"}) is False
    assert _is_empty_placeholder([{"a": "x"}]) is False
    assert _is_empty_placeholder("x") is False
    assert _is_empty_placeholder(0) is False
    assert _is_empty_placeholder(False) is False


def test_strip_empty_placeholders_drops_aim_module_3_pattern():
    """AIM module_3 ships [{}] for funding_rounds when the LLM has nothing —
    publisher must drop those before public write."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [{}],
            "strategic_deals": [{}],
            "energy_wall": [{}],
        },
    }
    cleaned = _strip_empty_placeholders(report)
    assert cleaned["module_3"]["title"] == "Investment and M&A"
    assert cleaned["module_3"]["funding_rounds"] == []
    assert cleaned["module_3"]["strategic_deals"] == []
    assert cleaned["module_3"]["energy_wall"] == []


def test_strip_empty_placeholders_preserves_real_entries():
    report = {
        "module_3": {
            "funding_rounds": [
                {},
                {"company": "Acme", "amount": "$100M"},
                {"company": "", "amount": ""},  # all-empty values
                {"company": "Beta"},
            ],
        },
    }
    cleaned = _strip_empty_placeholders(report)
    rounds = cleaned["module_3"]["funding_rounds"]
    assert len(rounds) == 2
    assert rounds[0]["company"] == "Acme"
    assert rounds[1]["company"] == "Beta"


def test_sanitise_for_public_strips_empty_module_arrays():
    """End-to-end: an AIM-shaped report with [{}] placeholders comes out clean."""
    report = {
        "title": "AIM Issue 12",
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [{}],
            "strategic_deals": [{}],
            "energy_wall": [{}],
        },
        "module_5": {"european": [{}], "china": [{}]},
        "module_6": {
            "threshold_events": [{}],
            "programme_updates": [{}],
            "arxiv_highlights": [{}],
        },
    }
    public = sanitise_for_public(report)
    assert public["module_3"]["funding_rounds"] == []
    assert public["module_3"]["strategic_deals"] == []
    assert public["module_3"]["energy_wall"] == []
    assert public["module_5"]["european"] == []
    assert public["module_5"]["china"] == []
    assert public["module_6"]["threshold_events"] == []
    assert public["module_6"]["programme_updates"] == []
    assert public["module_6"]["arxiv_highlights"] == []


def test_strip_does_not_collapse_zero_or_false():
    """Numbers and booleans count as content even when falsy — protect them."""
    report = {"items": [{"score": 0, "active": False}]}
    cleaned = _strip_empty_placeholders(report)
    assert cleaned == {"items": [{"score": 0, "active": False}]}


if __name__ == "__main__":
    # Run as script for quick sanity: python test_sanitise_for_public.py
    import traceback
    tests = [
        (name, obj) for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            failed += 1
        except Exception:
            print(f"ERROR {name}:")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)

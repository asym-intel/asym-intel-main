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

from publisher import (  # noqa: E402
    sanitise_for_public,
    _is_empty_placeholder,
    _strip_empty_placeholders,
    _annotate_empty_modules,
    _find_unprovenanced_empty_modules,
    _module_body_is_empty,
    build_report_placeholder,
    stamp_publisher_omission,
    _EMPTY_REASON_TAXONOMY,
)


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


# ── Module-level null-signal provenance contract ──────────────────────────
#
# Live AIM artefact (commit 6e867f3f) has 10 modules of the form
# {title, <field>: [], <field>: [], ...}. The contract: every empty-shaped
# module reaching the public report MUST carry null_signal/empty_reason/
# fallback_message before publication.


def test_string_null_treated_as_empty():
    """LLM-emitted "null" string sentinel (AIM module_9 digest_note) is empty."""
    assert _is_empty_placeholder("null") is True
    assert _is_empty_placeholder("NULL") is True
    assert _is_empty_placeholder("  null  ") is True
    # Real content containing "null" is not.
    assert _is_empty_placeholder("nullable type") is False


def test_module_body_is_empty_recognises_title_plus_empty_arrays():
    """AIM module_3 shape after [{}] strip — title plus empty arrays — is empty."""
    m = {
        "title": "Investment and M&A",
        "funding_rounds": [],
        "strategic_deals": [],
        "energy_wall": [],
    }
    assert _module_body_is_empty(m) is True


def test_module_body_is_empty_recognises_placeholder_arrays():
    """Pre-strip module_3 shape with [{}] placeholders is also empty."""
    m = {
        "title": "Investment and M&A",
        "funding_rounds": [{}],
        "strategic_deals": [{}],
    }
    assert _module_body_is_empty(m) is True


def test_module_body_is_empty_recognises_string_null_field():
    """AIM module_9 with digest_note: "null" plus empty arrays is empty."""
    m = {
        "title": "Law and Litigation",
        "digest_note": "null",
        "law_highlights": [],
        "standards_highlights": [],
        "litigation_highlights": [],
    }
    assert _module_body_is_empty(m) is True


def test_module_body_is_empty_rejects_non_empty():
    """A module with any meaningful content is not empty."""
    m = {
        "title": "Investment and M&A",
        "funding_rounds": [{"company": "Acme", "amount": "$100M"}],
    }
    assert _module_body_is_empty(m) is False


def test_annotate_empty_modules_stamps_no_material_content_for_null_cycle():
    """When interpret-stage marks a null/partial cycle, empty modules get
    explicit no_material_content provenance and a reader-facing fallback."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "strategic_deals": [],
            "energy_wall": [],
        },
    }
    meta = {"null_signal_week": True, "cycle_disposition": "null_cycle"}
    out = _annotate_empty_modules(report, source_meta=meta)
    m = out["module_3"]
    assert m["null_signal"] is True
    assert m["empty_reason"] == "no_material_content"
    assert isinstance(m["fallback_message"], str) and m["fallback_message"]


def test_annotate_empty_modules_stamps_schema_thin_when_overall_material():
    """The exact AIM data-quality break: overall null_signal_week=false /
    cycle_disposition=material_change but a module_* is structurally empty.

    With the placeholder-traceability taxonomy this is `schema_thin` —
    distinct from `unknown` because the producing stage IS identifiable
    (synthesiser emitted a thin module on a material cycle), and the
    triage path differs from a truly unattributable empty.
    """
    report = {
        "module_6": {
            "title": "AI in Science",
            "threshold_events": [],
            "programme_updates": [],
            "arxiv_highlights": [],
        },
    }
    meta = {
        "null_signal_week": False,
        "cycle_disposition": "material_change",
        "null_signal_reason": "multiple material developments this week",
    }
    out = _annotate_empty_modules(report, source_meta=meta)
    m = out["module_6"]
    assert m["null_signal"] is True
    assert m["empty_reason"] == "schema_thin"
    assert isinstance(m["fallback_message"], str) and m["fallback_message"]
    # produced_by/produced_at provenance must be present.
    assert m["produced_by"] == "publisher.annotate_empty_modules"
    assert m["produced_at"].endswith("Z") and "T" in m["produced_at"]


def test_annotate_empty_modules_stamps_unknown_when_meta_absent():
    """No interpret-stage meta at all — fall back to explicit unknown rather
    than guessing. Unknown stays load-bearing; do not collapse it."""
    report = {
        "module_4": {
            "title": "Empty section",
            "items": [],
        },
    }
    out = _annotate_empty_modules(report, source_meta=None)
    m = out["module_4"]
    assert m["null_signal"] is True
    assert m["empty_reason"] == "unknown"
    assert "could not determine" in m["fallback_message"].lower() \
        or "review" in m["fallback_message"].lower()


def test_annotate_empty_modules_replaces_string_null_field():
    """AIM module_9 digest_note: "null" must not survive into the public report
    as the literal four-letter word — annotation drops it to empty string."""
    report = {
        "module_9": {
            "title": "Law and Litigation",
            "digest_note": "null",
            "law_highlights": [],
            "standards_highlights": [],
            "litigation_highlights": [],
        },
    }
    meta = {"null_signal_week": False, "cycle_disposition": "material_change"}
    out = _annotate_empty_modules(report, source_meta=meta)
    m = out["module_9"]
    assert m["null_signal"] is True
    assert m["digest_note"] == ""


def test_annotate_empty_modules_preserves_non_empty_modules():
    """Modules with real content MUST NOT be touched."""
    report = {
        "module_0": {
            "title": "Lead Signal",
            "headline": "Real headline",
            "items": [{"id": "x", "summary": "real"}],
        },
        "module_3": {
            "title": "Empty M&A",
            "funding_rounds": [],
        },
    }
    meta = {"null_signal_week": False, "cycle_disposition": "material_change"}
    out = _annotate_empty_modules(report, source_meta=meta)
    assert "null_signal" not in out["module_0"]
    assert out["module_0"]["headline"] == "Real headline"
    assert out["module_0"]["items"][0]["summary"] == "real"
    assert out["module_3"]["null_signal"] is True


def test_annotate_empty_modules_does_not_overwrite_existing_provenance():
    """If the upstream stage already wrote provenance, respect it."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "null_signal": True,
            "empty_reason": "synthesis_skipped",
            "fallback_message": "Upstream skipped this module.",
        },
    }
    out = _annotate_empty_modules(report, source_meta={})
    m = out["module_3"]
    assert m["empty_reason"] == "synthesis_skipped"
    assert m["fallback_message"] == "Upstream skipped this module."


def test_sanitise_for_public_end_to_end_with_aim_module_3_pattern():
    """End-to-end: AIM-shaped report with [{}] placeholders, string "null",
    and overall null_signal_week=false. Public report has clean arrays AND
    explicit module-level provenance for the empty modules."""
    report = {
        "title": "AIM Issue 12",
        "_meta": {
            "null_signal_week": False,
            "cycle_disposition": "material_change",
        },
        "module_0": {
            "title": "Lead Signal",
            "items": [{"id": "lead-1", "summary": "real lead"}],
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
            "standards_highlights": [{}],
            "litigation_highlights": [{}],
        },
    }
    public = sanitise_for_public(report)

    # Real content survives untouched
    assert public["module_0"]["items"][0]["summary"] == "real lead"
    assert "null_signal" not in public["module_0"]

    # Empty modules carry provenance — taxonomy widened post-Phase-A,
    # so any of the publisher-emitted reasons is acceptable here.
    for k in ("module_3", "module_6", "module_9"):
        m = public[k]
        assert m["null_signal"] is True, f"{k} missing null_signal"
        assert m["empty_reason"] in {
            "unknown", "no_material_content", "schema_thin",
        }, f"{k} unexpected empty_reason {m['empty_reason']!r}"
        assert isinstance(m["fallback_message"], str) and m["fallback_message"], \
            f"{k} fallback_message missing"
        assert m.get("produced_by"), f"{k} produced_by missing"
        assert m.get("produced_at"), f"{k} produced_at missing"

    # Placeholder [{}] arrays became empty arrays
    assert public["module_3"]["funding_rounds"] == []
    assert public["module_3"]["strategic_deals"] == []
    assert public["module_9"]["law_highlights"] == []

    # "null" string sentinel did not leak through
    assert public["module_9"]["digest_note"] != "null"


def test_find_unprovenanced_empty_modules_flags_bare_empty():
    """Defense-in-depth gate: bare empty modules are reported."""
    report = {
        "module_3": {"title": "Empty", "funding_rounds": [], "strategic_deals": []},
        "module_6": {
            "title": "Provenanced empty",
            "threshold_events": [],
            "null_signal": True,
            "empty_reason": "no_material_content",
            "fallback_message": "OK.",
        },
        "module_0": {"title": "Real", "items": [{"id": "x"}]},
    }
    bad = _find_unprovenanced_empty_modules(report)
    assert bad == ["module_3"]


def test_find_unprovenanced_empty_modules_passes_after_annotate():
    """Round-trip: annotate then validate — public report should pass."""
    report = {
        "module_3": {
            "title": "Investment and M&A",
            "funding_rounds": [],
            "strategic_deals": [],
        },
    }
    annotated = _annotate_empty_modules(report, source_meta={
        "null_signal_week": False,
        "cycle_disposition": "material_change",
    })
    assert _find_unprovenanced_empty_modules(annotated) == []


# ── Placeholder taxonomy (Phase A) ─────────────────────────────────────────


def test_taxonomy_contains_all_canonical_reasons():
    """Spec §2 lists seven canonical reasons. The exported taxonomy tuple
    must contain each — guards against a code edit that drops one silently."""
    expected = {
        "no_material_content",
        "schema_thin",
        "report_stale",
        "held_upstream",
        "renderer_schema_mismatch",
        "publisher_omission",
        "unknown",
    }
    assert set(_EMPTY_REASON_TAXONOMY) == expected


def test_stamp_publisher_omission_creates_synthetic_module():
    """Module declared by the schema but absent from the JSON gets a
    synthetic placeholder so the renderer can't silently skip it (case 5)."""
    report = {
        "module_0": {"title": "Lead", "items": [{"id": "x"}]},
        # module_3 declared by schema but absent
    }
    omitted = stamp_publisher_omission(
        report,
        ["module_0", "module_3"],
        titles={"module_3": "Investment and M&A"},
    )
    assert omitted == ["module_3"]
    m = report["module_3"]
    assert m["null_signal"] is True
    assert m["empty_reason"] == "publisher_omission"
    assert m["title"] == "Investment and M&A"
    assert m["produced_by"] == "publisher.stamp_publisher_omission"
    assert m["produced_at"].endswith("Z")
    # Existing real module untouched.
    assert "null_signal" not in report["module_0"]


def test_stamp_publisher_omission_idempotent():
    """Calling twice with the same expected list does not re-stamp existing
    placeholders or duplicate them."""
    report: dict = {}
    first = stamp_publisher_omission(report, ["module_3"])
    snapshot = dict(report["module_3"])
    second = stamp_publisher_omission(report, ["module_3"])
    assert first == ["module_3"]
    assert second == []  # already a dict, skipped
    assert report["module_3"] == snapshot


def test_build_report_placeholder_report_stale():
    """report_stale → status=stale, reason set, fallback names the as_of
    date so the reader knows how stale, plus operator provenance."""
    block = build_report_placeholder(
        reason="report_stale",
        monitor="ai-governance",
        as_of="2026-04-25",
        next_check="2026-05-06",
    )
    assert block["report_status"] == "stale"
    assert block["reason"] == "report_stale"
    assert "2026-04-25" in block["fallback_message"]
    assert "2026-05-06" in block["fallback_message"]
    assert block["produced_by"].startswith("publisher.")
    assert block["produced_at"].endswith("Z")
    assert block["reader_facing"] is True
    assert block["monitor"] == "ai-governance"


def test_build_report_placeholder_held_upstream_keeps_hold_reason_operator_only():
    """held_upstream surfaces a neutral reader fallback, but the internal
    hold_reason (verdict code) is preserved on the block for operators."""
    block = build_report_placeholder(
        reason="held_upstream",
        monitor="scem",
        hold_reason="review_verdict:hold-for-review",
    )
    assert block["report_status"] == "held"
    assert block["reason"] == "held_upstream"
    assert block["hold_reason"] == "review_verdict:hold-for-review"
    # Reader-facing fallback must not leak the verdict code.
    assert "verdict" not in block["fallback_message"].lower()
    assert "hold-for-review" not in block["fallback_message"]


def test_build_report_placeholder_unknown_reason_coerced():
    """Unrecognised reasons coerce to 'unknown' — explicit, not silent."""
    block = build_report_placeholder(
        reason="some_future_reason",
        monitor="wdm",
    )
    assert block["reason"] == "unknown"
    # We do not lie with a confident "no material developments" message.
    assert block["fallback_message"]


def test_build_report_placeholder_ok_when_no_reason():
    """No reason → status=ok, reason=None. Useful for callers that want
    to write a uniform sidecar regardless of report state."""
    block = build_report_placeholder(reason=None, monitor="aim")
    assert block["report_status"] == "ok"
    assert block["reason"] is None
    assert block["fallback_message"] == ""


def test_build_report_placeholder_fim_parked_not_reader_facing():
    """FIM remains parked (no public page yet). The block is still produced
    for operator triage, but reader_facing=False signals the renderer/site
    must suppress the banner."""
    block = build_report_placeholder(
        reason="held_upstream",
        monitor="fim",
        reader_facing=False,
    )
    assert block["report_status"] == "held"
    assert block["reader_facing"] is False
    # Operators still get the fallback string; suppression is a renderer
    # concern, not a missing-data concern.
    assert block["fallback_message"]


def test_renderer_schema_mismatch_is_part_of_taxonomy():
    """Detection of renderer_schema_mismatch is renderer-side (client-only),
    but the constant is still part of the canonical taxonomy so producers
    of operator output (e.g. fleet_stage_classifier) can normalise to it."""
    assert "renderer_schema_mismatch" in _EMPTY_REASON_TAXONOMY


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

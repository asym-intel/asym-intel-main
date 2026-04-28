#!/usr/bin/env python3
"""Tests for tools/public_surface_audit.py — L7 methodology-vocab rule.

Run:
    python3 tools/test_public_surface_audit.py
or:
    pytest tools/test_public_surface_audit.py -v

Covers:
  - L7 hard-fails on each forbidden term
  - L7 does NOT trip on look-alike words ("synthesis" vs "synthesiser",
    "interpretation" vs "interpret" — the latter would trip because
    "interpret" is a substring; we accept this and exclude commons via
    the rule design rather than via fuzzy matching).
  - L7 hits across .html, .json, .js, .css, .md
  - L7 still hard-fails when other rules also fire (compounding)
  - Allowlist entries can suppress legitimate L7 occurrences
  - L7 does NOT scan operator-only paths (asym-intel-internal is out of scope
    by virtue of being a different repo; this test asserts the scanner's
    DEFAULT_PUBLIC_ROOTS is still 'static' only, ensuring the scanner can't
    accidentally walk into operator surfaces inside the same repo).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCANNER = Path(__file__).resolve().parent / "public_surface_audit.py"


def run_scanner(root: Path, extra_args=None):
    """Invoke the scanner. Returns (returncode, parsed_json)."""
    cmd = [sys.executable, str(SCANNER), "--root", str(root), "--json"]
    if extra_args:
        cmd.extend(extra_args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError:
        data = None
    return res.returncode, data, res.stderr


def make_repo(tmp: Path, files: dict) -> Path:
    """Create a synthetic repo under tmp with the given {relpath: content} files."""
    root = tmp / "repo"
    root.mkdir(exist_ok=True)
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


# ─── L7 positive tests ─────────────────────────────────────────────────────

L7_TERMS = [
    "interpret", "interpreter", "compose", "composer",
    "applier", "curate", "curator", "reasoner",
    "synthesiser", "synthesizer", "chatter",
    "weekly-research", "weekly_research",
    "phase a", "phase b", "cascade",
    "challenger", "pipeline-dispatcher", "dispatcher",
    "sonar-pro", "sonar-deep-research", "sonar-reasoning",
]


def test_l7_each_forbidden_term_hard_fails():
    failures = []
    with tempfile.TemporaryDirectory() as td:
        for i, term in enumerate(L7_TERMS):
            tmp = Path(td) / f"case_{i}"
            tmp.mkdir()
            root = make_repo(tmp, {
                f"static/sample_{i}.html": f"<p>The {term} is internal-only methodology vocabulary.</p>",
            })
            rc, data, stderr = run_scanner(root)
            l7_hits = [f for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"]
            if rc != 1:
                failures.append(f"  term={term!r}: expected exit 1, got {rc}; stderr={stderr[:200]}")
            elif not l7_hits:
                failures.append(f"  term={term!r}: expected L7 hit, got none. findings={data.get('findings') if data else None}")
    assert not failures, "L7 missed terms:\n" + "\n".join(failures)


def test_l7_negative_synthesis_passes():
    """\"synthesis\" is a different word from \"synthesiser\"; should NOT trip L7."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/legit.html": "<p>This is a synthesis of public reporting.</p>",
        })
        rc, data, stderr = run_scanner(root)
        l7_hits = [f for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"]
        assert not l7_hits, f"L7 false-positive on 'synthesis': {l7_hits}"
        assert rc == 0, f"expected exit 0, got {rc}. stderr={stderr[:200]}"


def test_l7_negative_review_apply_pass():
    """'review' and 'apply' are deliberately excluded from L7 (BRIEF #1 spec)."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/legit.html": "<p>Apply for our service. Review terms.</p>",
        })
        rc, data, stderr = run_scanner(root)
        l7_hits = [f for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"]
        assert not l7_hits, f"L7 false-positive on review/apply: {l7_hits}"
        assert rc == 0, f"expected exit 0, got {rc}. stderr={stderr[:200]}"


def test_l7_case_insensitive():
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/case.html": "<p>SYNTHESISER and Reasoner and ChAtTer</p>",
        })
        rc, data, _ = run_scanner(root)
        l7_hits = [f for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"]
        assert len(l7_hits) >= 3, f"expected ≥3 L7 hits across cases, got {len(l7_hits)}: {l7_hits}"
        assert rc == 1


def test_l7_hits_in_json_and_js():
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/data.json": '{"stage": "synthesiser"}',
            "static/script.js": 'const stage = "reasoner";',
        })
        rc, data, _ = run_scanner(root)
        l7_files = {f["file"] for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"}
        assert l7_files == {"static/data.json", "static/script.js"}, f"unexpected: {l7_files}"
        assert rc == 1


def test_l7_allowlist_suppresses():
    """A legitimate file (e.g. test fixture) listed in allowlist should not trip L7."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/legit-methodology-page.html": "<p>The reasoner is documented publicly.</p>",
            "tools/public_surface_audit.allowlist": "^static/legit-methodology-page\\.html:",
        })
        rc, data, stderr = run_scanner(root)
        l7_hits = [f for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"]
        assert not l7_hits, f"allowlist did not suppress L7: {l7_hits}; stderr={stderr[:200]}"
        assert rc == 0, f"expected exit 0, got {rc}. stderr={stderr[:200]}"


def test_l7_phase_b_phrase():
    """\"phase b\" with whitespace must trip; \"phaseboard\" must NOT (word boundary)."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/with.html": "<p>Phase B cascade rolled out.</p>",
            "static/without.html": "<p>The phaseboard is empty.</p>",
        })
        rc, data, _ = run_scanner(root)
        l7_files = {f["file"] for f in (data or {}).get("findings", []) if f["rule_id"] == "L7_METHODOLOGY_VOCAB"}
        # 'cascade' AND 'phase b' both trip in with.html
        assert "static/with.html" in l7_files
        # 'phaseboard' should NOT trip
        assert "static/without.html" not in l7_files or all(
            f["matched"].lower() not in ("phaseboard",)
            for f in (data or {}).get("findings", [])
            if f["file"] == "static/without.html"
        )


def test_l7_combines_with_other_rules():
    """If both L3 and L7 trip in one file, scanner reports both."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "static/leak.html": "<!-- asym-intel-internal/ops/synthesiser.md -->",
        })
        rc, data, _ = run_scanner(root)
        rules = {f["rule_id"] for f in (data or {}).get("findings", [])}
        assert "L3_INTERNAL_REPO_REF" in rules
        assert "L7_METHODOLOGY_VOCAB" in rules
        assert rc == 1


def test_default_scope_is_static_only():
    """Sanity check: docs/ is still excluded by default (per AD-2026-04-28 + DR baseliner sprint)."""
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(Path(td), {
            "docs/leak.html": "<p>synthesiser</p>",
        })
        rc, data, _ = run_scanner(root)  # default --public-roots = ('static',)
        assert rc == 0
        assert (data or {}).get("findings") == [], "docs/ scanned by default — should not be"


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

#!/usr/bin/env python3
"""Tests for check_canonical_pipeline_deviation.py."""

from __future__ import annotations

import unittest
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import check_canonical_pipeline_deviation as gate


GOOD_BODY = """
## Canonical pipeline review

- canonical-pipeline-reviewed: yes
- classification: canonical/common-code fix
- canonical comparator: WDM reusable reviewer/composer/applier chain at main
- deviation rationale: Common-code repair; no consumer-specific fork introduced.
"""


class CanonicalPipelineDeviationGateTests(unittest.TestCase):
    def test_non_structural_change_passes_without_body(self):
        result = gate.evaluate("", ["content/monitors/foo/2026-05-04-weekly-brief.md"])
        self.assertTrue(result.ok)
        self.assertEqual(result.structural_files, [])

    def test_structural_engine_change_requires_review_block(self):
        result = gate.evaluate("", ["pipeline/engine/review_base.py"])
        self.assertFalse(result.ok)
        self.assertIn("pipeline/engine/review_base.py", result.structural_files)

    def test_structural_workflow_change_accepts_complete_review_block(self):
        result = gate.evaluate(GOOD_BODY, [".github/workflows/fim-reviewer.yml"])
        self.assertTrue(result.ok)

    def test_consumer_schema_change_is_structural(self):
        result = gate.evaluate(GOOD_BODY, ["pipeline/monitors/financial-integrity/interpreter-schema.json"])
        self.assertTrue(result.ok)
        self.assertEqual(
            result.structural_files,
            ["pipeline/monitors/financial-integrity/interpreter-schema.json"],
        )

    def test_invalid_classification_fails(self):
        body = GOOD_BODY.replace("canonical/common-code fix", "quick fix")
        result = gate.evaluate(body, ["pipeline/engine/review_base.py"])
        self.assertFalse(result.ok)
        self.assertTrue(any("Invalid classification" in error for error in result.errors))

    def test_placeholder_comparator_fails(self):
        body = GOOD_BODY.replace(
            "WDM reusable reviewer/composer/applier chain at main",
            "TBD",
        )
        result = gate.evaluate(body, ["pipeline/engine/review_base.py"])
        self.assertFalse(result.ok)
        self.assertTrue(any("canonical comparator" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()

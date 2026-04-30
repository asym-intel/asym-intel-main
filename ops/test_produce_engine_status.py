#!/usr/bin/env python3
"""
ops/test_produce_engine_status.py

Regression tests for `ops/produce_engine_status.py:derive_status`.

Per AD-2026-04-30-BP, this script is a thin reader of the canonical
classifier's output (`engine.status` and `monitors[].status` in the public
roll-up `static/ops/pipeline-status.json`). These tests assert the read
contract: identity-pass on `engine.status`, count of `monitors[].status`
buckets, and KV-value shape preservation.

The "single canonical classifier" invariant: `derive_status` MUST NOT
re-classify; it MUST take `engine` from `engine.status` exactly as the
canonical classifier wrote it.

Run:
  python3 -m unittest ops/test_produce_engine_status.py

Or via the existing CI runner that already invokes ops/test_*.py.
"""

import json
import os
import sys
import unittest

# Path setup so we can import the sibling script as a module.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "produce_engine_status",
    os.path.join(THIS_DIR, "produce_engine_status.py"),
)
produce_engine_status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(produce_engine_status)
derive_status = produce_engine_status.derive_status


def _roll_up(engine_status, last_updated, monitors):
    """Build a v4.0-shaped public roll-up fixture."""
    return {
        "schema_version": "4.0",
        "generated_at": last_updated,
        "engine": {"status": engine_status, "last_updated": last_updated},
        "monitors": [
            {"slug": slug, "status": status, "last_updated": last_updated}
            for slug, status in monitors
        ],
        "_trigger_health": {},
    }


class TestDeriveStatus(unittest.TestCase):

    def test_engine_passes_through_from_canonical_classifier(self):
        """engine.status is taken from engine.status verbatim — no re-classification."""
        # Canonical classifier said "amber" — derive_status must not re-derive
        # something else from monitors[].status. (Even if the monitors list is
        # empty, engine pass-through holds.)
        data = _roll_up("amber", "2026-04-30T19:00:00Z", [])
        out = derive_status(data)
        self.assertEqual(out["engine"], "amber")
        self.assertEqual(out["last_updated"], "2026-04-30T19:00:00Z")

    def test_monitor_status_counts(self):
        data = _roll_up("red", "2026-04-30T19:00:00Z", [
            ("WDM",  "red"),
            ("GMM",  "red"),
            ("FCW",  "amber"),
            ("ESA",  "green"),
            ("AGM",  "green"),
            ("ERM",  "green"),
            ("SCEM", "green"),
        ])
        out = derive_status(data)
        self.assertEqual(out["red_count"], 2)
        self.assertEqual(out["amber_count"], 1)
        self.assertEqual(out["green_count"], 4)

    def test_kv_value_shape_preserved(self):
        """Output must contain exactly the five keys the consumer expects."""
        data = _roll_up("green", "2026-04-30T19:00:00Z", [
            ("WDM", "green"),
        ])
        out = derive_status(data)
        self.assertEqual(
            set(out.keys()),
            {"engine", "last_updated", "red_count", "amber_count", "green_count"},
        )

    def test_no_re_classification_when_engine_disagrees_with_monitors(self):
        """If the canonical classifier says 'red' but monitors[].status is
        all-green (e.g. due to a staleness rule the canonical classifier
        applies that derive_status does not know about), derive_status MUST
        report engine='red' and counts from monitors. Re-classifying would
        violate the AD-BP invariant."""
        data = _roll_up("red", "2026-04-30T19:00:00Z", [
            ("WDM", "green"),
            ("GMM", "green"),
        ])
        out = derive_status(data)
        self.assertEqual(out["engine"], "red")  # NOT recomputed from monitors
        self.assertEqual(out["green_count"], 2)
        self.assertEqual(out["red_count"], 0)

    def test_unknown_monitor_status_not_counted(self):
        """Non-{red,amber,green} statuses (e.g. FIM-non-canonical states) are
        intentionally not bucketed; the canonical engine.status already
        accounts for them at roll-up time."""
        data = _roll_up("green", "2026-04-30T19:00:00Z", [
            ("WDM", "green"),
            ("FIM", "paused"),  # hypothetical non-canonical state
        ])
        out = derive_status(data)
        self.assertEqual(out["green_count"], 1)
        self.assertEqual(out["red_count"], 0)
        self.assertEqual(out["amber_count"], 0)

    def test_missing_engine_block_yields_unknown(self):
        data = {"schema_version": "4.0", "monitors": []}
        out = derive_status(data)
        self.assertEqual(out["engine"], "unknown")
        self.assertIsNone(out["last_updated"])

    def test_kv_serialisation_is_compact(self):
        """Sanity-check: the JSON the script PUTs to KV is compact (no spaces)."""
        data = _roll_up("green", "2026-04-30T19:00:00Z", [("WDM", "green")])
        out = derive_status(data)
        payload = json.dumps(out, separators=(",", ":"))
        self.assertNotIn(", ", payload)
        self.assertNotIn(": ", payload)


if __name__ == "__main__":
    unittest.main()

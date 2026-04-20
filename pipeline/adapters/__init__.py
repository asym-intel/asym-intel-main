"""
Front-end adapters for asym-intel canonical monitor reports.

Architecture (see docs/architecture/thin-frontend-pattern.md):

    [Canonical monitor report JSON]   (one per monitor, schema-versioned)
                  │
                  ▼
    [Adapter]    ─ declarative field mapping
                  │   - expects a specific canonical schema version
                  │   - emits a specific target renderer shape
                  ▼
    [Target renderer]  (thin commons / rich commercial / WP / PDF / email)
                  │
                  ▼
    [Distribution target]

Each adapter is a pure function: canonical report → shaped report.
No I/O. No network. Testable in isolation with fixtures.

Registry: every adapter registers a (monitor, target) key and declares
the canonical schema version it accepts. The registry exists so that
contract tests, CI, and preflight can enumerate adapters and verify
invariants.
"""

from .base import Adapter, AdapterError, CanonicalSchemaError
from .registry import register, get, list_adapters

__all__ = [
    "Adapter",
    "AdapterError",
    "CanonicalSchemaError",
    "register",
    "get",
    "list_adapters",
]

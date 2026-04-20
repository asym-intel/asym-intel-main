"""
Adapter base class and shared errors.

An Adapter is a pure function from a canonical monitor report JSON to
a shaped report JSON for a specific front-end renderer.

Subclasses MUST set:

    monitor:                   str  (e.g. "ai-governance")
    target:                    str  (e.g. "ramparts-wp")
    accepts_schema_versions:   tuple[str, ...]  (e.g. ("2.0",))
    emits_schema_version:      str  (e.g. "ramparts-v2")

and MUST implement:

    def transform(self, canonical: dict) -> dict

Subclasses SHOULD call `self._assert_canonical_schema(canonical)` first
inside transform() to fail loudly on drift.
"""

from __future__ import annotations

from typing import Any


class AdapterError(Exception):
    """Raised when an adapter cannot produce a valid shaped report."""


class CanonicalSchemaError(AdapterError):
    """Raised when the canonical report does not match the schema version(s)
    this adapter accepts. Fail-loud replacement for silent field-mismatch bugs.
    """


class Adapter:
    # Subclasses MUST override.
    monitor: str = ""
    target: str = ""
    accepts_schema_versions: tuple[str, ...] = ()
    emits_schema_version: str = ""

    # ---- public ----

    def transform(self, canonical: dict) -> dict:
        """Pure function. Take canonical report dict → shaped report dict."""
        raise NotImplementedError

    # ---- helpers available to subclasses ----

    def _assert_canonical_schema(self, canonical: dict) -> None:
        """Fail loudly if the canonical report's schema_version is not in
        this adapter's accepted set. Prevents silent field-mismatch bugs
        when the canonical schema drifts."""
        meta = canonical.get("meta", {}) or {}
        schema_version = meta.get("schema_version")
        if schema_version is None:
            raise CanonicalSchemaError(
                f"[{self.__class__.__name__}] canonical report missing meta.schema_version; "
                f"adapter accepts {self.accepts_schema_versions}"
            )
        if schema_version not in self.accepts_schema_versions:
            raise CanonicalSchemaError(
                f"[{self.__class__.__name__}] canonical schema_version='{schema_version}' "
                f"not in accepted set {self.accepts_schema_versions}. "
                f"Either (a) bump the canonical schema with a migration, "
                f"or (b) update this adapter to accept the new version."
            )

    @staticmethod
    def _first(*values: Any, default: Any = "") -> Any:
        """Return the first value that is truthy (non-empty string, non-None, non-empty list)."""
        for v in values:
            if v is None:
                continue
            if isinstance(v, str) and not v.strip():
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            return v
        return default

    @staticmethod
    def _get(obj: Any, *keys: str, default: Any = "") -> Any:
        """Safe chained get for dict-of-dicts. `_get(d, "a", "b")` ≈ d.get('a', {}).get('b', default)."""
        cur: Any = obj
        for k in keys:
            if not isinstance(cur, dict):
                return default
            cur = cur.get(k)
            if cur is None:
                return default
        return cur

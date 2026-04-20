"""
Adapter base class and shared errors.

An Adapter is a pure function from a canonical monitor report JSON plus an
optional persistent-state JSON to a shaped report JSON for a specific front-end
renderer.

Subclasses MUST set:

    monitor:                   str  (e.g. "ai-governance")
    target:                    str  (e.g. "ramparts-wp")
    accepts_schema_versions:   tuple[str, ...]  (e.g. ("2.0",))
    emits_schema_version:      str  (e.g. "ramparts-v2")

and MUST implement:

    def transform(self, canonical: dict, persistent: dict | None = None) -> dict

Subclasses SHOULD call `self._assert_canonical_schema(canonical)` first
inside transform() to fail loudly on drift.

ENGINE-RULES §27 Invariant L — Persistent-state merge semantics
---------------------------------------------------------------
When the adapter's monitor has a `persistent-state.json` tracker, `persistent`
is the authoritative floor of the rendered output. Per-module rules:

    1. Baseline is always persistent-state.
    2. This week's synthesis *updates* the persistent-state record, never
       replaces it wholesale. Empty synthesis for a persistent-backed module
       means "no update this week", NOT "clear the tracker".
    3. Every carried entry surfaces `unchanged_since: YYYY-MM-DD` so readers
       see what is fresh vs carried.
    4. Partial synthesis = partial update (match on a §27-F monotone invariant
       key; non-overlapping entries are preserved).
    5. Fail loud on contradiction (malformed synth shape), not on absence.

The helpers below (`_merge_persistent_list`, `_index_by_key`) implement the
default semantics so adapters don't re-roll them per module.
"""

from __future__ import annotations

import copy
from typing import Any


class AdapterError(Exception):
    """Raised when an adapter cannot produce a valid shaped report."""


class CanonicalSchemaError(AdapterError):
    """Raised when the canonical report does not match the schema version(s)
    this adapter accepts. Fail-loud replacement for silent field-mismatch bugs.
    """


class PersistentMergeError(AdapterError):
    """Raised when synthesis provides a persistent-backed field with a
    malformed shape. Fail-loud replacement for silent data loss when a
    garbled synth could otherwise overwrite a rich tracker with junk
    (§27-L rule 5)."""


class Adapter:
    # Subclasses MUST override.
    monitor: str = ""
    target: str = ""
    accepts_schema_versions: tuple[str, ...] = ()
    emits_schema_version: str = ""

    # ---- public ----

    def transform(self, canonical: dict, persistent: dict | None = None) -> dict:
        """Pure function. Take canonical report dict (+ optional persistent-state
        dict) → shaped report dict."""
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

    # ---- §27-L persistent-state merge helpers ----

    @staticmethod
    def _index_by_key(items: list, key: str) -> dict[str, int]:
        """Build {match_value: list_index} index for a list of dicts.
        Items missing `key` or with non-hashable values are skipped.
        Later duplicates overwrite earlier (last-wins, matches _merge_list)."""
        out: dict[str, int] = {}
        if not isinstance(items, list):
            return out
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            v = it.get(key)
            if v is None:
                continue
            try:
                out[str(v)] = i
            except Exception:
                continue
        return out

    def _merge_persistent_list(
        self,
        persistent_list: list,
        synth_list: list | None,
        match_key: str,
        publish_date: str,
        field_name: str = "<unnamed>",
    ) -> list:
        """Merge a weekly synthesis list into a persistent-state list per §27-L.

        Semantics:
          - persistent_list is the floor. Always returned (possibly mutated).
          - If synth_list is None or [], persistent_list is returned untouched
            (rule 2: empty synth = no update).
          - If synth_list is not a list, raise PersistentMergeError (rule 5).
          - For each item in synth_list that has a matching item in
            persistent_list (by match_key), field-update the persistent item
            with the synth fields and stamp `unchanged_since = publish_date`
            (rule 3 — "this is fresh this week").
          - For each item in synth_list that has no match, APPEND it with
            `unchanged_since = publish_date`.
          - Carried items (no synth match) keep their prior `unchanged_since`.

        Returns a deep copy — callers receive a fresh list they can mutate.
        """
        base = copy.deepcopy(persistent_list) if isinstance(persistent_list, list) else []

        if synth_list is None:
            # Quiet week — stamp carried items so they have a date if missing,
            # but never overwrite an existing unchanged_since.
            for it in base:
                if isinstance(it, dict):
                    it.setdefault("unchanged_since", it.get("last_updated", publish_date))
            return base

        if not isinstance(synth_list, list):
            raise PersistentMergeError(
                f"[{self.__class__.__name__}] synthesis field '{field_name}' expected list, "
                f"got {type(synth_list).__name__} — refusing to merge into persistent tracker."
            )

        if not synth_list:
            # Explicit empty list is still "no update" per rule 2.
            for it in base:
                if isinstance(it, dict):
                    it.setdefault("unchanged_since", it.get("last_updated", publish_date))
            return base

        idx = self._index_by_key(base, match_key)
        for synth_item in synth_list:
            if not isinstance(synth_item, dict):
                continue
            mv = synth_item.get(match_key)
            if mv is not None and str(mv) in idx:
                # Field-update existing persistent item
                target = base[idx[str(mv)]]
                for k, v in synth_item.items():
                    if v is None:
                        continue
                    target[k] = v
                target["unchanged_since"] = publish_date
                target["last_updated"] = publish_date
            else:
                # New entry this week
                new_it = copy.deepcopy(synth_item)
                new_it.setdefault("unchanged_since", publish_date)
                new_it.setdefault("last_updated", publish_date)
                base.append(new_it)
                if mv is not None:
                    idx[str(mv)] = len(base) - 1

        # Stamp any still-unstamped carried items (cold-start compatibility).
        for it in base:
            if isinstance(it, dict):
                it.setdefault("unchanged_since", it.get("last_updated", publish_date))
        return base

    def _merge_persistent_dict(
        self,
        persistent_dict: dict,
        synth_dict: dict | None,
        publish_date: str,
        field_name: str = "<unnamed>",
    ) -> dict:
        """Field-level merge of a synth dict into a persistent tracker dict.

        Returns deep copy of persistent_dict with non-None synth fields applied
        on top. Empty / None synth_dict returns persistent_dict untouched.
        Non-dict synth raises PersistentMergeError (rule 5).
        """
        base = copy.deepcopy(persistent_dict) if isinstance(persistent_dict, dict) else {}
        if synth_dict is None or synth_dict == {}:
            return base
        if not isinstance(synth_dict, dict):
            raise PersistentMergeError(
                f"[{self.__class__.__name__}] synthesis field '{field_name}' expected dict, "
                f"got {type(synth_dict).__name__} — refusing to merge into persistent tracker."
            )
        touched = False
        for k, v in synth_dict.items():
            if v is None or (isinstance(v, (list, dict, str)) and not v):
                continue
            base[k] = v
            touched = True
        if touched:
            base["last_updated"] = publish_date
        return base

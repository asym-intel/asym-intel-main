"""
monitor_urls.py — Python resolver for the canonical monitor registry.

Single source of truth: static/monitors/monitor-registry.json
ENGINE-RULES §17: URLs to engine assets MUST come from this resolver,
never from string concatenation.

Usage:
    from pipeline.shared.monitor_urls import monitor_url, all_monitors

    print(monitor_url("WDM"))
    # https://asym-intel.info/monitors/democratic-integrity/

    for m in all_monitors():
        print(m["abbr"], m["url"])

All lookups are case-insensitive on abbr. Slug lookups require exact match.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Registry lives in static/monitors relative to repo root.
_REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "static"
    / "monitors"
    / "monitor-registry.json"
)


@lru_cache(maxsize=1)
def _load_registry() -> dict[str, Any]:
    """Load and cache the registry JSON. Raises FileNotFoundError if missing."""
    with open(_REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("schema_version") != "2.0":
        raise ValueError(
            f"monitor-registry.json schema_version mismatch: "
            f"expected '2.0', got {data.get('schema_version')!r}"
        )
    return data


def all_monitors() -> list[dict[str, Any]]:
    """Return the full list of monitor entries, in registry order."""
    return list(_load_registry()["monitors"])


def _find(key: str, value: str) -> dict[str, Any]:
    for m in _load_registry()["monitors"]:
        if m.get(key) == value:
            return m
    raise KeyError(f"No monitor with {key}={value!r}")


def monitor_by_abbr(abbr: str) -> dict[str, Any]:
    """Look up a monitor by abbreviation (case-insensitive)."""
    up = abbr.upper()
    return _find("abbr", up)


def monitor_by_slug(slug: str) -> dict[str, Any]:
    """Look up a monitor by slug (exact match)."""
    return _find("slug", slug)


def monitor_url(abbr: str) -> str:
    """Canonical public URL for a monitor, e.g. 'WDM' -> '.../monitors/democratic-integrity/'."""
    return monitor_by_abbr(abbr)["url"]


def monitor_slug(abbr: str) -> str:
    """Slug for a monitor abbreviation."""
    return monitor_by_abbr(abbr)["slug"]


def monitor_name(abbr: str) -> str:
    """Full name for a monitor."""
    return monitor_by_abbr(abbr)["name"]


def monitor_accent(abbr: str) -> str:
    """Primary accent hex colour for a monitor."""
    return monitor_by_abbr(abbr)["accent"]


def monitor_svg_url(abbr: str) -> str:
    """Public URL of the monitor glyph SVG."""
    return monitor_by_abbr(abbr)["svg_url"]


def all_abbrs() -> list[str]:
    """All monitor abbreviations, in registry order."""
    return [m["abbr"] for m in all_monitors()]


def all_slugs() -> list[str]:
    """All monitor slugs, in registry order."""
    return [m["slug"] for m in all_monitors()]


# Convenience: eagerly load on import so missing-file errors surface early.
_load_registry()

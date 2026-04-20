"""
Adapter registry. Every concrete adapter self-registers on import.

Lookup key is (monitor, target). Example:
    (
        "ai-governance",
        "ramparts-wp",
    )
"""

from __future__ import annotations

from typing import Any

_REGISTRY: dict[tuple[str, str], type] = {}


def register(cls: type) -> type:
    """Class decorator that registers an Adapter subclass."""
    if not cls.monitor or not cls.target:
        raise ValueError(
            f"Adapter {cls.__name__} must set class attrs `monitor` and `target`"
        )
    key = (cls.monitor, cls.target)
    if key in _REGISTRY:
        raise ValueError(f"Adapter already registered for {key}: {_REGISTRY[key].__name__}")
    _REGISTRY[key] = cls
    return cls


def get(monitor: str, target: str) -> Any:
    """Return an instance of the registered adapter for (monitor, target)."""
    key = (monitor, target)
    if key not in _REGISTRY:
        raise KeyError(
            f"No adapter registered for monitor='{monitor}' target='{target}'. "
            f"Known: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[key]()


def list_adapters() -> list[tuple[str, str, type]]:
    """Enumerate all registered adapters. Used by preflight and docs."""
    return [(m, t, cls) for (m, t), cls in sorted(_REGISTRY.items())]

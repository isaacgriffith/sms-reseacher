"""Unit tests for researcher_mcp.core.registry.

Covers:
- register() adds a source under the given index key.
- get() returns the registered source or None.
- get_enabled() with None returns all sources.
- get_enabled() with a list returns only the specified (registered) sources.
- registered_indices() returns all keys in registration order.
- set_registry / get_registry module-level helpers.
"""

from __future__ import annotations

import pytest

from researcher_mcp.core.registry import SourceRegistry, get_registry, set_registry
from researcher_mcp.sources.base import PaperRecord


class _FakeSource:
    """Minimal DatabaseSource-compatible object for testing."""

    def __init__(self, name: str) -> None:
        self.name = name

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[PaperRecord]:
        """Return an empty list (stub)."""
        return []

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Return None (stub)."""
        return None


class TestSourceRegistryRegisterAndGet:
    """Tests for register() and get()."""

    def test_get_registered_source(self) -> None:
        """get() returns the source registered under the given key."""
        registry = SourceRegistry()
        src = _FakeSource("ss")
        registry.register("semantic_scholar", src)
        assert registry.get("semantic_scholar") is src

    def test_get_unregistered_source_returns_none(self) -> None:
        """get() returns None for an unknown index key."""
        registry = SourceRegistry()
        assert registry.get("nonexistent") is None

    def test_register_overwrites_existing(self) -> None:
        """Registering the same key again replaces the old source."""
        registry = SourceRegistry()
        src1 = _FakeSource("first")
        src2 = _FakeSource("second")
        registry.register("ieee_xplore", src1)
        registry.register("ieee_xplore", src2)
        assert registry.get("ieee_xplore") is src2

    def test_register_multiple_keys(self) -> None:
        """Multiple sources can be registered under different keys."""
        registry = SourceRegistry()
        sources = {
            "ieee_xplore": _FakeSource("ieee"),
            "scopus": _FakeSource("scopus"),
            "semantic_scholar": _FakeSource("ss"),
        }
        for key, src in sources.items():
            registry.register(key, src)
        for key, src in sources.items():
            assert registry.get(key) is src


class TestSourceRegistryGetEnabled:
    """Tests for get_enabled()."""

    def test_get_enabled_none_returns_all(self) -> None:
        """get_enabled(None) returns all registered (index, source) pairs."""
        registry = SourceRegistry()
        src_a = _FakeSource("a")
        src_b = _FakeSource("b")
        registry.register("alpha", src_a)
        registry.register("beta", src_b)
        result = registry.get_enabled(None)
        assert len(result) == 2
        assert ("alpha", src_a) in result
        assert ("beta", src_b) in result

    def test_get_enabled_with_list_filters(self) -> None:
        """get_enabled(list) returns only the specified indices that exist."""
        registry = SourceRegistry()
        src_a = _FakeSource("a")
        src_b = _FakeSource("b")
        src_c = _FakeSource("c")
        registry.register("alpha", src_a)
        registry.register("beta", src_b)
        registry.register("gamma", src_c)
        result = registry.get_enabled(["alpha", "gamma"])
        assert len(result) == 2
        indices = [idx for idx, _ in result]
        assert "alpha" in indices
        assert "gamma" in indices
        assert "beta" not in indices

    def test_get_enabled_skips_unregistered_indices(self) -> None:
        """Indices in the list that are not registered are silently skipped."""
        registry = SourceRegistry()
        src = _FakeSource("s")
        registry.register("real", src)
        result = registry.get_enabled(["real", "ghost", "phantom"])
        assert len(result) == 1
        assert result[0][0] == "real"

    def test_get_enabled_empty_list_returns_empty(self) -> None:
        """get_enabled([]) returns an empty list even if sources are registered."""
        registry = SourceRegistry()
        registry.register("alpha", _FakeSource("a"))
        result = registry.get_enabled([])
        assert result == []

    def test_get_enabled_empty_registry_returns_empty(self) -> None:
        """get_enabled on an empty registry always returns an empty list."""
        registry = SourceRegistry()
        assert registry.get_enabled(None) == []
        assert registry.get_enabled(["any"]) == []


class TestSourceRegistryRegisteredIndices:
    """Tests for registered_indices()."""

    def test_returns_keys_in_registration_order(self) -> None:
        """registered_indices() returns keys in the order they were registered."""
        registry = SourceRegistry()
        for key in ["z_key", "a_key", "m_key"]:
            registry.register(key, _FakeSource(key))
        assert registry.registered_indices() == ["z_key", "a_key", "m_key"]

    def test_empty_registry_returns_empty_list(self) -> None:
        """registered_indices() on a fresh registry returns []."""
        assert SourceRegistry().registered_indices() == []


class TestModuleLevelRegistryHelpers:
    """Tests for set_registry / get_registry module-level helpers."""

    def test_get_registry_raises_before_set(self) -> None:
        """get_registry() raises RuntimeError when no registry has been set."""
        import researcher_mcp.core.registry as reg_module

        original = reg_module._default_registry
        reg_module._default_registry = None
        try:
            with pytest.raises(RuntimeError, match="not been initialised"):
                get_registry()
        finally:
            reg_module._default_registry = original

    def test_set_and_get_registry(self) -> None:
        """set_registry() followed by get_registry() returns the same instance."""
        import researcher_mcp.core.registry as reg_module

        original = reg_module._default_registry
        try:
            new_registry = SourceRegistry()
            set_registry(new_registry)
            assert get_registry() is new_registry
        finally:
            reg_module._default_registry = original

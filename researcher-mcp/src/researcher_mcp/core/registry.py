"""Source registry mapping database index identifiers to source adapter instances.

The :class:`SourceRegistry` is the single point of indirection between the
fan-out search logic and individual database source adapters.  Adding a new
database integration requires only registering a new source instance here —
the fan-out in ``tools/search.py`` needs no changes (OCP).
"""

from __future__ import annotations

from researcher_mcp.sources.base import DatabaseSource


class SourceRegistry:
    """Maps database index identifiers to :class:`DatabaseSource` instances.

    Sources can be registered globally (enabled for all searches) or marked as
    enabled/disabled per-call by passing an explicit ``indices`` allowlist to
    :meth:`get_enabled`.

    Attributes:
        _sources: Internal mapping from index identifier to source instance.
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._sources: dict[str, DatabaseSource] = {}

    def register(self, index: str, source: DatabaseSource) -> None:
        """Register a source adapter under the given index identifier.

        Args:
            index: String key identifying the database index (e.g.
                ``"semantic_scholar"``).  Should match a :class:`DatabaseIndex`
                enum value from ``db.models.search_integrations``.
            source: A :class:`DatabaseSource` protocol-compliant instance.
        """
        self._sources[index] = source

    def get(self, index: str) -> DatabaseSource | None:
        """Return the source registered for ``index``, or None if absent.

        Args:
            index: The database index identifier to look up.

        Returns:
            The registered :class:`DatabaseSource`, or None.
        """
        return self._sources.get(index)

    def get_enabled(self, indices: list[str] | None = None) -> list[tuple[str, DatabaseSource]]:
        """Return (index, source) pairs for the specified indices.

        If ``indices`` is None, returns all registered sources.  Any index in
        ``indices`` that is not registered is silently skipped.

        Args:
            indices: Optional list of index identifiers to include.  Pass None
                to include every registered source.

        Returns:
            List of ``(index_identifier, source_instance)`` tuples, ordered by
            registration order.
        """
        if indices is None:
            return list(self._sources.items())
        return [
            (idx, src)
            for idx in indices
            if (src := self._sources.get(idx)) is not None
        ]

    def registered_indices(self) -> list[str]:
        """Return all registered index identifiers in registration order.

        Returns:
            List of index identifier strings.
        """
        return list(self._sources.keys())


# Module-level default registry populated by server.py at startup.
_default_registry: SourceRegistry | None = None


def get_registry() -> SourceRegistry:
    """Return the module-level default :class:`SourceRegistry`.

    Raises:
        RuntimeError: If the registry has not been initialised via
            :func:`set_registry` before this function is called.

    Returns:
        The default :class:`SourceRegistry` instance.
    """
    if _default_registry is None:
        raise RuntimeError(
            "SourceRegistry has not been initialised. "
            "Call set_registry() during server startup."
        )
    return _default_registry


def set_registry(registry: SourceRegistry) -> None:
    """Set the module-level default registry.

    Args:
        registry: A configured :class:`SourceRegistry` instance to use as the
            global default.
    """
    global _default_registry  # noqa: PLW0603
    _default_registry = registry

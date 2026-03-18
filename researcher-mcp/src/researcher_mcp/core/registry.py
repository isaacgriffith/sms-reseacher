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
        return [(idx, src) for idx in indices if (src := self._sources.get(idx)) is not None]

    def registered_indices(self) -> list[str]:
        """Return all registered index identifiers in registration order.

        Returns:
            List of index identifier strings.

        """
        return list(self._sources.keys())


# Module-level default registry populated by build_default_registry() at startup.
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
            "SourceRegistry has not been initialised. Call set_registry() during server startup."
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


def build_default_registry() -> SourceRegistry:
    """Create and return a :class:`SourceRegistry` pre-populated with all sources.

    Sources are instantiated from :class:`~researcher_mcp.core.config.ResearcherSettings`
    credentials.  This function should be called once during server startup and
    the result passed to :func:`set_registry`.

    Returns:
        A fully populated :class:`SourceRegistry` with all configured source
        adapters registered under their respective ``DatabaseIndex`` string values.

    """
    from researcher_mcp.core.config import get_settings  # noqa: PLC0415
    from researcher_mcp.core.http_client import make_retry_client  # noqa: PLC0415
    from researcher_mcp.sources.acm import ACMSource  # noqa: PLC0415
    from researcher_mcp.sources.google_scholar import GoogleScholarSource  # noqa: PLC0415
    from researcher_mcp.sources.ieee import IEEESource  # noqa: PLC0415
    from researcher_mcp.sources.inspec import InspecSource  # noqa: PLC0415
    from researcher_mcp.sources.science_direct import ScienceDirectSource  # noqa: PLC0415
    from researcher_mcp.sources.scopus import ScopusSource  # noqa: PLC0415
    from researcher_mcp.sources.semantic_scholar import SemanticScholarSource  # noqa: PLC0415
    from researcher_mcp.sources.springer import SpringerSource  # noqa: PLC0415
    from researcher_mcp.sources.wos import WoSSource  # noqa: PLC0415

    settings = get_settings()
    client = make_retry_client()

    registry = SourceRegistry()
    registry.register(
        "ieee_xplore",
        IEEESource(client, api_key=settings.ieee_xplore_api_key),
    )
    registry.register("acm_dl", ACMSource(client))
    registry.register(
        "scopus",
        ScopusSource(api_key=settings.elsevier_api_key, inst_token=settings.elsevier_inst_token),
    )
    registry.register(
        "web_of_science",
        WoSSource(client, api_key=settings.wos_api_key),
    )
    registry.register(
        "inspec",
        InspecSource(
            client,
            api_key=settings.elsevier_api_key,
            inst_token=settings.elsevier_inst_token,
        ),
    )
    registry.register(
        "science_direct",
        ScienceDirectSource(
            api_key=settings.elsevier_api_key,
            inst_token=settings.elsevier_inst_token,
        ),
    )
    registry.register(
        "springer_link",
        SpringerSource(api_key=settings.springer_api_key),
    )
    registry.register(
        "google_scholar",
        GoogleScholarSource(proxy_url=settings.scholarly_proxy_url),
    )
    registry.register(
        "semantic_scholar",
        SemanticScholarSource(client, rpm=settings.semantic_scholar_rpm),  # type: ignore[arg-type]
    )
    return registry

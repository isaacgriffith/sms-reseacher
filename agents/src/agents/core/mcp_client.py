"""MCP client connecting agents to researcher-mcp via HTTP/SSE."""

from __future__ import annotations

from typing import Any

import httpx

from agents.core.config import AgentSettings, get_agent_settings


class MCPClient:
    """Lightweight HTTP client for discovering and calling MCP tools.

    Connects to the ``researcher-mcp`` FastMCP server at
    ``RESEARCHER_MCP_URL`` via HTTP/SSE, discovers available tools,
    and converts them to the LiteLLM function-call format so they can
    be passed as the ``tools`` parameter to LLM completion calls.

    This is a simplified stub implementation for the MVP harness.  Full
    streaming SSE handling is added in the researcher-mcp integration
    feature.

    Args:
        settings: Optional :class:`AgentSettings` override.

    """

    def __init__(self, settings: AgentSettings | None = None) -> None:
        """Initialise the MCP client.

        Args:
            settings: Optional settings override; defaults to
                :func:`get_agent_settings`.

        """
        self._settings = settings or get_agent_settings()
        self._base_url = self._settings.researcher_mcp_url.removesuffix("/sse")

    async def list_tools(self) -> list[dict[str, Any]]:
        """Discover tools exposed by the MCP server.

        Calls ``GET {base_url}/tools/list`` and returns the raw tool
        list from the server's JSON response.

        Returns:
            A list of MCP tool definition dicts, each with at minimum
            ``name``, ``description``, and ``inputSchema`` keys.

        Raises:
            httpx.HTTPError: If the server is unreachable or returns
                a non-2xx status.

        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self._base_url}/tools/list", timeout=10.0)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return list(data.get("tools", []))

    def to_litellm_tools(self, mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert MCP tool definitions to LiteLLM function-call format.

        Transforms each MCP tool's ``name``, ``description``, and
        ``inputSchema`` into the OpenAI-compatible ``{"type": "function",
        "function": {...}}`` structure expected by
        :meth:`~agents.core.llm_client.LLMClient.complete`.

        Args:
            mcp_tools: Raw tool list returned by :meth:`list_tools`.

        Returns:
            A list of LiteLLM-format tool dicts ready to pass as
            the ``tools`` kwarg in a completion call.

        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                },
            }
            for tool in mcp_tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a single MCP tool by name.

        Args:
            tool_name: The MCP tool name (e.g. ``search_papers``).
            arguments: The tool's input arguments matching its
                ``inputSchema``.

        Returns:
            The tool's JSON response dict.

        Raises:
            httpx.HTTPError: If the request fails.

        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/tools/call",
                json={"name": tool_name, "arguments": arguments},
                timeout=30.0,
            )
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result

"""Build public server cards from the registered MCP tools."""

from typing import Any


def registered_tool_cards(mcp: Any) -> list[dict[str, str]]:
    """Return a stable public view of the registered tools."""
    tools = sorted(mcp._tool_manager.list_tools(), key=lambda tool: tool.name)
    return [{"name": tool.name, "description": tool.description or ""} for tool in tools]

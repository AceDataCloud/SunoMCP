"""Server-card tools must match the MCP registry exactly."""

from pathlib import Path

import tools  # noqa: F401, I001
from core.server import mcp
from core.server_card import registered_tool_cards


def test_server_card_tools_match_registered_tools():
    registered = {tool.name for tool in mcp._tool_manager.list_tools()}
    advertised = {tool["name"] for tool in registered_tool_cards(mcp)}

    assert advertised == registered
    assert len(advertised) == len(registered_tool_cards(mcp))


def test_http_server_card_uses_registered_tools():
    source = (Path(__file__).parents[1] / "main.py").read_text()

    assert '"tools": registered_tool_cards(mcp)' in source

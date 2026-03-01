"""Tools module for MCP Suno server."""

# Import all tools to register them with the MCP server
from tools import (
    audio_tools,
    info_tools,
    lyrics_tools,
    media_tools,
    persona_tools,
    style_tools,
    task_tools,
)

__all__ = [
    "audio_tools",
    "lyrics_tools",
    "persona_tools",
    "media_tools",
    "style_tools",
    "task_tools",
    "info_tools",
]

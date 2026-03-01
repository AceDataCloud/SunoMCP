"""MCP Server initialization."""

import logging

from mcp.server.fastmcp import FastMCP

from core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(settings.server_name, host="0.0.0.0")

logger.info(f"Initialized MCP server: {settings.server_name}")

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

# Build FastMCP kwargs, enabling OAuth when MCP_SERVER_URL is configured
mcp_kwargs: dict = {"host": "0.0.0.0"}
oauth_provider = None

if settings.server_url:
    from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
    from pydantic import AnyHttpUrl

    from core.oauth import AceDataCloudOAuthProvider

    oauth_provider = AceDataCloudOAuthProvider()
    mcp_kwargs["auth_server_provider"] = oauth_provider
    mcp_kwargs["auth"] = AuthSettings(
        issuer_url=AnyHttpUrl(settings.server_url),
        resource_server_url=AnyHttpUrl(settings.server_url),
        client_registration_options=ClientRegistrationOptions(enabled=True),
        revocation_options=RevocationOptions(enabled=True),
    )
    logger.info(f"OAuth enabled: issuer_url={settings.server_url}")

# Initialize FastMCP server
mcp = FastMCP(settings.server_name, **mcp_kwargs)

logger.info(f"Initialized MCP server: {settings.server_name}")

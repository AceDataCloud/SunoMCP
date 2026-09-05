#!/usr/bin/env python3
"""
MCP Suno Server - AI Music Generation via AceDataCloud API.

A Model Context Protocol (MCP) server that provides tools for generating
AI music using Suno through the AceDataCloud platform.
"""

import argparse
import logging
import sys
from importlib import metadata

from dotenv import load_dotenv

# Load environment variables before importing other modules
load_dotenv()

from core.config import settings
from core.server import mcp
from core.server_card import registered_tool_cards

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def safe_print(text: str) -> None:
    """Print to stderr safely, handling encoding issues."""
    if not sys.stderr.isatty():
        logger.debug(f"[MCP Suno] {text}")
        return

    try:
        print(text, file=sys.stderr)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode(), file=sys.stderr)


def get_version() -> str:
    """Get the package version."""
    try:
        return metadata.version("mcp-suno")
    except metadata.PackageNotFoundError:
        return "dev"


def main() -> None:
    """Run the MCP Suno server."""
    parser = argparse.ArgumentParser(
        description="MCP Suno Server - AI Music Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-suno                    # Run with stdio transport (default)
  mcp-suno --transport http   # Run with HTTP transport
  mcp-suno --version          # Show version

Environment Variables:
  ACEDATACLOUD_API_TOKEN          API token from AceDataCloud (required)
  SUNO_DEFAULT_MODEL         Default model (default: chirp-v5-5)
  SUNO_REQUEST_TIMEOUT       Request timeout in seconds (default: 1800)
  LOG_LEVEL                  Logging level (default: INFO)
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mcp-suno {get_version()}",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)",
    )
    args = parser.parse_args()

    # Print startup banner
    safe_print("")
    safe_print("=" * 50)
    safe_print("  MCP Suno Server - AI Music Generation")
    safe_print("=" * 50)
    safe_print("")
    safe_print(f"  Version:   {get_version()}")
    safe_print(f"  Transport: {args.transport}")
    safe_print(f"  Model:     {settings.default_model}")
    safe_print(f"  Log Level: {settings.log_level}")
    safe_print("")

    # Validate configuration
    if not settings.is_configured and args.transport != "http":
        safe_print("  [ERROR] ACEDATACLOUD_API_TOKEN not configured!")
        safe_print("  Get your token from https://platform.acedata.cloud")
        safe_print("")
        sys.exit(1)

    if args.transport == "http":
        safe_print("  [OK] HTTP mode - tokens from request headers")
    else:
        safe_print("  [OK] API token configured")
    safe_print("")

    # Import tools and prompts to register them
    safe_print("  Loading tools and prompts...")
    import prompts  # noqa: F401, I001
    import tools  # noqa: F401

    safe_print("  [OK] Tools and prompts loaded")
    safe_print("")
    safe_print("  Available tools:")
    safe_print("    - suno_generate_music")
    safe_print("    - suno_generate_custom_music")
    safe_print("    - suno_extend_music")
    safe_print("    - suno_cover_music")
    safe_print("    - suno_concat_music")
    safe_print("    - suno_generate_with_persona")
    safe_print("    - suno_generate_with_persona_vox")
    safe_print("    - suno_generate_lyrics")
    safe_print("    - suno_create_persona")
    safe_print("    - suno_create_voice")
    safe_print("    - suno_list_personas")
    safe_print("    - suno_delete_persona")
    safe_print("    - suno_create_custom_model")
    safe_print("    - suno_get_custom_model")
    safe_print("    - suno_list_custom_models")
    safe_print("    - suno_generate_with_custom_model")
    safe_print("    - suno_delete_custom_model")
    safe_print("    - suno_all_stems_music")
    safe_print("    - suno_underpainting")
    safe_print("    - suno_overpainting")
    safe_print("    - suno_samples_music")
    safe_print("    - suno_get_task")
    safe_print("    - suno_get_tasks_batch")
    safe_print("    - suno_list_models")
    safe_print("    - suno_list_actions")
    safe_print("    - suno_get_lyric_format_guide")
    safe_print("")
    safe_print("  Available prompts:")
    safe_print("    - suno_music_generation_guide")
    safe_print("    - suno_workflow_examples")
    safe_print("    - suno_style_suggestions")
    safe_print("")
    safe_print("=" * 50)
    safe_print("  Ready for MCP connections")
    safe_print("=" * 50)
    safe_print("")

    # Run the server
    try:
        if args.transport == "http":
            import contextlib

            import uvicorn
            from starlette.applications import Starlette
            from starlette.requests import Request
            from starlette.responses import JSONResponse, RedirectResponse
            from starlette.routing import BaseRoute, Mount, Route

            from core.server import oauth_provider

            async def health(_request: Request) -> JSONResponse:
                return JSONResponse({"status": "ok"})

            async def favicon(_request: Request) -> RedirectResponse:
                return RedirectResponse("https://cdn.acedata.cloud/l3ffw7.jpg", status_code=301)

            async def server_card(_request: Request) -> JSONResponse:
                """MCP Server Card for Smithery and other registries."""
                return JSONResponse(
                    {
                        "serverInfo": {"name": "MCP Suno", "version": get_version()},
                        "authentication": {"required": True, "schemes": ["bearer"]},
                        "tools": registered_tool_cards(mcp),
                        "prompts": [
                            {
                                "name": "suno_music_generation_guide",
                                "description": "Guide for music generation",
                            },
                            {"name": "suno_workflow_examples", "description": "Example workflows"},
                            {
                                "name": "suno_style_suggestions",
                                "description": "Style suggestions for generation",
                            },
                        ],
                        "resources": [],
                    }
                )

            @contextlib.asynccontextmanager
            async def lifespan(_app: Starlette):  # type: ignore[no-untyped-def]
                async with mcp.session_manager.run():
                    yield

            mcp.settings.stateless_http = True
            mcp.settings.json_response = True
            mcp.settings.streamable_http_path = "/mcp"

            # Build routes
            routes: list[BaseRoute] = [
                Route("/health", health),
                Route("/favicon.ico", favicon),
                Route("/.well-known/mcp/server-card.json", server_card),
            ]

            # Add OAuth callback route if OAuth is enabled
            if oauth_provider:
                routes.append(Route("/oauth/callback", oauth_provider.handle_callback))

            # Mount legacy SSE transport (/sse + /messages) alongside Streamable HTTP (/mcp)
            # so SSE-only clients (e.g. OOBE Synapse SDK) and modern Streamable HTTP
            # clients are both supported on the same endpoint.
            for sse_route in mcp.sse_app().routes:
                routes.append(sse_route)
            routes.append(Mount("/", app=mcp.streamable_http_app()))

            app = Starlette(routes=routes, lifespan=lifespan)
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            mcp.run(transport="stdio")
    except KeyboardInterrupt:
        safe_print("\nShutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

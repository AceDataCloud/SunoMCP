# Suno MCP

AI Music Generation with Suno - Generate songs, lyrics, covers, and more via Ace Data Cloud API

This extension provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for VS Code, enabling AI assistants like GitHub Copilot to interact with Suno AI directly.

## Features

- **21 tools** available for AI assistants
- Zero-install: Uses `uvx` for automatic package management
- Works with GitHub Copilot, Claude, and other MCP-compatible AI assistants

## Prerequisites

1. **Python 3.10+** with `uvx` (from [uv](https://github.com/astral-sh/uv)) installed
2. **Ace Data Cloud API Token** — Get one at [platform.acedata.cloud](https://platform.acedata.cloud)

## Setup

1. Install this extension from the VS Code Marketplace
2. When prompted, enter your Ace Data Cloud API token
3. The MCP server will be available to AI assistants automatically

You can also manually configure the token in your VS Code settings (`.vscode/mcp.json`):

```json
{
  "servers": {
    "suno": {
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": {
        "ACEDATACLOUD_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Links

- [PyPI Package](https://pypi.org/project/mcp-suno/)
- [Source Code](https://github.com/AceDataCloud/SunoMCP)
- [Ace Data Cloud Platform](https://platform.acedata.cloud)
- [API Documentation](https://docs.acedata.cloud)

## License

MIT

# Suno MCP — JetBrains Plugin

AI Music Generation with [Suno](https://suno.com) via [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for JetBrains IDEs.

<!-- Plugin description -->
This plugin helps you set up the MCP Suno server with JetBrains AI Assistant.
Once configured, AI Assistant can generate songs, lyrics, covers, remixes, and more
using Suno AI — all powered by [Ace Data Cloud](https://platform.acedata.cloud?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_platform).

**35 AI Music Tools** — Generate, extend, cover, remix, mashup, stems, lyrics, and more.
<!-- Plugin description end -->

## Quick Start

1. Install this plugin from the [JetBrains Marketplace](https://plugins.jetbrains.com/plugin/com.acedatacloud.mcp.suno)
2. Open **Settings → Tools → Suno MCP**
3. Enter your [Ace Data Cloud](https://platform.acedata.cloud?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_platform) API token
4. Click **Copy Config** (STDIO or HTTP)
5. Paste into **Settings → Tools → AI Assistant → Model Context Protocol (MCP)**

### STDIO Mode (Local)

Runs the MCP server locally. Requires [uv](https://github.com/astral-sh/uv) installed.

```json
{
  "mcpServers": {
    "suno": {
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": {
        "ACEDATACLOUD_API_TOKEN": "your-token"
      }
    }
  }
}
```

### HTTP Mode (Remote)

Connects to the hosted MCP server at `suno.mcp.acedata.cloud`. No local install needed.

```json
{
  "mcpServers": {
    "suno": {
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

## Links

- [Ace Data Cloud Platform](https://platform.acedata.cloud?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_platform)
- [Documentation](https://platform.acedata.cloud/documents/suno-mcp?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_quick_start)
- [PyPI Package](https://pypi.org/project/mcp-suno/)
- [Source Code](https://github.com/AceDataCloud/SunoMCP)

## License

MIT

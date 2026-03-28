# MCP Suno

<!-- mcp-name: io.github.AceDataCloud/mcp-suno -->

[![PyPI version](https://img.shields.io/pypi/v/mcp-suno.svg)](https://pypi.org/project/mcp-suno/)
[![PyPI downloads](https://img.shields.io/pypi/dm/mcp-suno.svg)](https://pypi.org/project/mcp-suno/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for AI music generation using [Suno](https://suno.ai) through the [AceDataCloud API](https://platform.acedata.cloud).

Generate AI music, lyrics, and manage audio projects directly from Claude, VS Code, or any MCP-compatible client.

## Features

- **Music Generation** - Create AI-generated songs from text prompts
- **Custom Lyrics & Style** - Full control over lyrics, title, and music style
- **Song Extension** - Continue existing songs from any timestamp
- **Cover/Remix** - Create cover versions with different styles
- **Lyrics Generation** - Generate structured lyrics from descriptions
- **Persona Management** - Save and reuse voice styles
- **Task Tracking** - Monitor generation progress and retrieve results

## Quick Start

### 1. Get Your API Token

1. Sign up at [AceDataCloud Platform](https://platform.acedata.cloud)
2. Go to the [API documentation page](https://platform.acedata.cloud/documents/4da95d9d-7722-4a72-857d-bf6be86036e9)
3. Click **"Acquire"** to get your API token
4. Copy the token for use below

### 2. Use the Hosted Server (Recommended)

AceDataCloud hosts a managed MCP server — **no local installation required**.

**Endpoint:** `https://suno.mcp.acedata.cloud/mcp`

All requests require a Bearer token. Use the API token from Step 1.

#### Claude.ai

Connect directly on [Claude.ai](https://claude.ai) with OAuth — **no API token needed**:

1. Go to Claude.ai **Settings → Integrations → Add More**
2. Enter the server URL: `https://suno.mcp.acedata.cloud/mcp`
3. Complete the OAuth login flow
4. Start using the tools in your conversation

#### Claude Desktop

Add to your config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### Cursor / Windsurf

Add to your MCP config (`.cursor/mcp.json` or `.windsurf/mcp.json`):

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### VS Code (Copilot)

Add to your VS Code MCP config (`.vscode/mcp.json`):

```json
{
  "servers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

Or install the [Ace Data Cloud MCP extension](https://marketplace.visualstudio.com/items?itemName=acedatacloud.acedatacloud-mcp) for VS Code, which bundles all 11 MCP servers with one-click setup.

#### JetBrains IDEs

1. Go to **Settings → Tools → AI Assistant → Model Context Protocol (MCP)**
2. Click **Add** → **HTTP**
3. Paste:

```json
{
  "mcpServers": {
    "suno": {
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```


#### Claude Code

Claude Code supports MCP servers natively:

```bash
claude mcp add suno --transport http https://suno.mcp.acedata.cloud/mcp \
  -h "Authorization: Bearer YOUR_API_TOKEN"
```

Or add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### Cline

Add to Cline's MCP settings (`.cline/mcp_settings.json`):

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### Amazon Q Developer

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### Roo Code

Add to Roo Code MCP settings:

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

#### Continue.dev

Add to `.continue/config.yaml`:

```yaml
mcpServers:
  - name: suno
    type: streamable-http
    url: https://suno.mcp.acedata.cloud/mcp
    headers:
      Authorization: "Bearer YOUR_API_TOKEN"
```

#### Zed

Add to Zed's settings (`~/.config/zed/settings.json`):

```json
{
  "language_models": {
    "mcp_servers": {
      "suno": {
        "url": "https://suno.mcp.acedata.cloud/mcp",
        "headers": {
          "Authorization": "Bearer YOUR_API_TOKEN"
        }
      }
    }
  }
}
```

#### cURL Test

```bash
# Health check (no auth required)
curl https://suno.mcp.acedata.cloud/health

# MCP initialize
curl -X POST https://suno.mcp.acedata.cloud/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

### 3. Or Run Locally (Alternative)

If you prefer to run the server on your own machine:

```bash
# Install from PyPI
pip install mcp-suno
# or
uvx mcp-suno

# Set your API token
export ACEDATACLOUD_API_TOKEN="your_token_here"

# Run (stdio mode for Claude Desktop / local clients)
mcp-suno

# Run (HTTP mode for remote access)
mcp-suno --transport http --port 8000
```

#### Claude Desktop (Local)

```json
{
  "mcpServers": {
    "suno": {
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": {
        "ACEDATACLOUD_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Docker (Self-Hosting)

```bash
docker pull ghcr.io/acedatacloud/mcp-suno:latest
docker run -p 8000:8000 ghcr.io/acedatacloud/mcp-suno:latest
```

Clients connect with their own Bearer token — the server extracts the token from each request's `Authorization` header.

## Available Tools

### Music Generation

| Tool                    | Description                                                |
| ----------------------- | ---------------------------------------------------------- |
| `generate_music`        | Generate music from a text prompt (Inspiration Mode)       |
| `generate_custom_music` | Generate with custom lyrics, title, and style              |
| `extend_music`          | Extend an existing song from a timestamp                   |
| `cover_music`           | Create a cover/remix version                               |
| `concat_music`          | Merge extended segments into complete audio                |
| `generate_with_persona` | Generate using a saved voice style                         |
| `remaster_music`        | Remaster an existing song to improve audio quality         |
| `stems_music`           | Separate a song into individual stems (vocals/instruments) |
| `replace_section`       | Replace a specific time range with new generated content   |
| `upload_extend`         | Extend uploaded audio with new AI-generated content        |
| `upload_cover`          | Create an AI cover of uploaded audio                       |
| `mashup_music`          | Create a mashup by blending multiple songs together        |

### Lyrics

| Tool              | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `generate_lyrics` | Generate song lyrics from a prompt                         |
| `mashup_lyrics`   | Generate mashup lyrics by combining two sets of lyrics     |
| `optimize_style`  | Optimize a style description for better generation results |

### Media Conversion

| Tool             | Description                                       |
| ---------------- | ------------------------------------------------- |
| `get_mp4`        | Get an MP4 video version of a generated song      |
| `get_wav`        | Get lossless WAV format of a generated song       |
| `get_midi`       | Get MIDI data extracted from a generated song     |
| `get_timing`     | Get timing and subtitle data for a generated song |
| `extract_vocals` | Extract the vocal track from a generated song     |

### Persona

| Tool             | Description                  |
| ---------------- | ---------------------------- |
| `create_persona` | Save a voice style for reuse |

### Upload

| Tool           | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| `upload_audio` | Upload an external audio file for use in subsequent operations |

### Tasks

| Tool              | Description                  |
| ----------------- | ---------------------------- |
| `get_task`        | Query a single task status   |
| `get_tasks_batch` | Query multiple tasks at once |

### Information

| Tool                     | Description                 |
| ------------------------ | --------------------------- |
| `list_models`            | List available Suno models  |
| `list_actions`           | List available API actions  |
| `get_lyric_format_guide` | Get lyrics formatting guide |

## Usage Examples

### Generate Music from Prompt

```
User: Create a happy birthday song

Claude: I'll generate a birthday song for you.
[Calls generate_music with prompt="A happy birthday celebration song"]
```

### Generate with Custom Lyrics

```
User: Create a rock song with these lyrics:
[Verse]
Thunder in the night
Electric soul ignite
[Chorus]
We are the storm

Claude: I'll create a rock song with your lyrics.
[Calls generate_custom_music with lyrics, title="Storm", style="rock, powerful"]
```

### Extend a Song

```
User: Continue this song from the 2-minute mark with a bridge section

Claude: I'll extend the song with a bridge.
[Calls extend_music with audio_id, continue_at=120, lyric="[Bridge]..."]
```

## Available Models

| Model             | Version | Max Duration | Features             |
| ----------------- | ------- | ------------ | -------------------- |
| `chirp-v5-5`      | V5.5    | 8 minutes    | Latest, best quality |
| `chirp-v5`        | V5      | 8 minutes    | High quality         |
| `chirp-v4-5-plus` | V4.5+   | 8 minutes    | Enhanced quality     |
| `chirp-v4-5`      | V4.5    | 4 minutes    | Vocal gender control |
| `chirp-v4`        | V4      | 150 seconds  | Stable               |
| `chirp-v3-5`      | V3.5    | 120 seconds  | Fast                 |
| `chirp-v3-0`      | V3      | 120 seconds  | Legacy               |

**Vocal Gender Control** (v4.5+ only):

- `f` - Female vocals
- `m` - Male vocals

## Configuration

### Environment Variables

| Variable                    | Description                  | Default                     |
| --------------------------- | ---------------------------- | --------------------------- |
| `ACEDATACLOUD_API_TOKEN`    | API token from AceDataCloud  | **Required**                |
| `ACEDATACLOUD_API_BASE_URL` | API base URL                 | `https://api.acedata.cloud` |
| `ACEDATACLOUD_OAUTH_CLIENT_ID`  | OAuth client ID (hosted mode) | —                           |
| `ACEDATACLOUD_PLATFORM_BASE_URL` | Platform base URL            | `https://platform.acedata.cloud` |
| `SUNO_DEFAULT_MODEL`        | Default model for generation | `chirp-v5-5`                |
| `SUNO_REQUEST_TIMEOUT`      | Request timeout in seconds   | `1800`                      |
| `LOG_LEVEL`                 | Logging level                | `INFO`                      |

### Command Line Options

```bash
mcp-suno --help

Options:
  --version          Show version
  --transport        Transport mode: stdio (default) or http
  --port             Port for HTTP transport (default: 8000)
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/AceDataCloud/mcp-suno.git
cd mcp-suno

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev,test]"
```

### Run Tests

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=core --cov=tools

# Run integration tests (requires API token)
pytest tests/test_integration.py -m integration
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy core tools
```

### Build & Publish

```bash
# Install build dependencies
pip install -e ".[release]"

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Project Structure

```
MCPSuno/
├── core/                   # Core modules
│   ├── __init__.py
│   ├── client.py          # HTTP client for Suno API
│   ├── config.py          # Configuration management
│   ├── exceptions.py      # Custom exceptions
│   ├── server.py          # MCP server initialization
│   └── utils.py           # Utility functions
├── tools/                  # MCP tool definitions
│   ├── __init__.py
│   ├── audio_tools.py     # Audio generation tools
│   ├── info_tools.py      # Information tools
│   ├── lyrics_tools.py    # Lyrics generation tools
│   ├── media_tools.py     # Media conversion tools
│   ├── persona_tools.py   # Persona management tools
│   └── task_tools.py      # Task query tools
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── test_client.py
│   ├── test_config.py
│   ├── test_integration.py
│   └── test_utils.py
├── deploy/                 # Deployment configs
│   └── production/
│       ├── deployment.yaml
│       ├── ingress.yaml
│       └── service.yaml
├── .env.example           # Environment template
├── .gitignore
├── CHANGELOG.md
├── Dockerfile             # Docker image for HTTP mode
├── docker-compose.yaml    # Docker Compose config
├── LICENSE
├── main.py                # Entry point
├── pyproject.toml         # Project configuration
└── README.md
```

## API Reference

This server wraps the [AceDataCloud Suno API](https://platform.acedata.cloud/documents/4da95d9d-7722-4a72-857d-bf6be86036e9):

- [Suno Audios API](https://platform.acedata.cloud/documents/4da95d9d-7722-4a72-857d-bf6be86036e9) - Music generation
- [Suno Lyrics API](https://platform.acedata.cloud/documents/514d82dc-f7ab-4638-9f21-8b9275916b08) - Lyrics generation
- [Suno Tasks API](https://platform.acedata.cloud/documents/b0dd9823-0e01-4c75-af83-5a6e2e05bfed) - Task queries
- [Suno Persona API](https://platform.acedata.cloud/documents/78bb6c62-6ce0-490f-a7df-e89d80ec0583) - Persona management

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [AceDataCloud Platform](https://platform.acedata.cloud)
- [Suno Official](https://suno.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

Made with love by [AceDataCloud](https://platform.acedata.cloud)

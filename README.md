# MCP Suno

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

### 1. Get API Token

Get your API token from [AceDataCloud Platform](https://platform.acedata.cloud):

1. Sign up or log in
2. Navigate to [Suno Audios API](https://platform.acedata.cloud/documents/4da95d9d-7722-4a72-857d-bf6be86036e9)
3. Click "Acquire" to get your token

### 2. Install

```bash
# Clone the repository
git clone https://github.com/AceDataCloud/mcp-suno.git
cd mcp-suno

# Install with pip
pip install -e .

# Or with uv (recommended)
uv pip install -e .
```

### 3. Configure

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API token
echo "ACEDATACLOUD_API_TOKEN=your_token_here" > .env
```

### 4. Run

```bash
# Run the server
mcp-suno

# Or with Python directly
python main.py
```

## Claude Desktop Integration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "suno": {
      "command": "mcp-suno",
      "env": {
        "ACEDATACLOUD_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Or if using uv:

```json
{
  "mcpServers": {
    "suno": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-suno", "mcp-suno"],
      "env": {
        "ACEDATACLOUD_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## Remote HTTP Mode (Hosted)

AceDataCloud hosts a managed MCP server that you can connect to directly — **no local installation required**.

**Endpoint**: `https://suno.mcp.acedata.cloud/mcp`

All requests require a Bearer token in the `Authorization` header. Get your token from [AceDataCloud Platform](https://platform.acedata.cloud).

### Claude Desktop (Remote)

```json
{
  "mcpServers": {
    "suno": {
      "type": "streamable-http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer your_api_token_here"
      }
    }
  }
}
```

### Cursor / VS Code

In your MCP client settings, add:

- **Type**: `streamable-http`
- **URL**: `https://suno.mcp.acedata.cloud/mcp`
- **Headers**: `Authorization: Bearer your_api_token_here`

### cURL Test

```bash
# Health check (no auth required)
curl https://suno.mcp.acedata.cloud/health

# MCP initialize (requires Bearer token)
curl -X POST https://suno.mcp.acedata.cloud/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer your_api_token_here" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

### Self-Hosting with Docker

```bash
docker pull ghcr.io/acedatacloud/mcp-suno:latest
docker run -p 8000:8000 ghcr.io/acedatacloud/mcp-suno:latest
```

Clients connect with their own Bearer token — the server extracts the token from each request's `Authorization` header and uses it for upstream API calls.

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
| `chirp-v5`        | V5      | 8 minutes    | Latest, best quality |
| `chirp-v4-5-plus` | V4.5+   | 8 minutes    | Enhanced quality     |
| `chirp-v4-5`      | V4.5    | 4 minutes    | Vocal gender control |
| `chirp-v4`        | V4      | 150 seconds  | Stable               |
| `chirp-v3-5`      | V3.5    | 120 seconds  | Fast                 |
| `chirp-v3`        | V3      | 120 seconds  | Legacy               |

**Vocal Gender Control** (v4.5+ only):

- `f` - Female vocals
- `m` - Male vocals

## Configuration

### Environment Variables

| Variable                    | Description                  | Default                     |
| --------------------------- | ---------------------------- | --------------------------- |
| `ACEDATACLOUD_API_TOKEN`    | API token from AceDataCloud  | **Required**                |
| `ACEDATACLOUD_API_BASE_URL` | API base URL                 | `https://api.acedata.cloud` |
| `SUNO_DEFAULT_MODEL`        | Default model for generation | `chirp-v4-5`                |
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

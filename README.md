# Suno by Ace Data Cloud

[简体中文安装与首用指南](https://github.com/AceDataCloud/SunoMCP/blob/main/readme/README_zh_Hans.md)

<!-- mcp-name: io.github.AceDataCloud/mcp-suno -->

[![PyPI version](https://img.shields.io/pypi/v/mcp-suno.svg)](https://pypi.org/project/mcp-suno/)
[![PyPI downloads](https://img.shields.io/pypi/dm/mcp-suno.svg)](https://pypi.org/project/mcp-suno/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for AI music generation using [Suno](https://suno.ai) through the [AceDataCloud API](https://platform.acedata.cloud?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_platform).

Generate AI music, lyrics, and manage audio projects directly from Claude, VS Code, or any MCP-compatible client.

## Use Suno in Glama

Find the Ace-provided [Suno source listing](https://glama.ai/mcp/servers/AceDataCloud/SunoMCP) or [remote connector](https://glama.ai/mcp/connectors/io.github.AceDataCloud/mcp-suno). Follow the [Glama installation, API Token and first-use guide](https://github.com/AceDataCloud/SunoMCP/blob/main/readme/GLAMA.md). Public discovery and a successful personal connection are separate checks; generation uses your Ace account balance.

## Suno in goose

Use the independent **Suno by Ace Data Cloud** native goose plugin: [install and API Token guide](goose/README.md) · [简体中文](goose/README_zh_Hans.md). It reuses this MCP server and does not imply goose Marketplace or default-provider inclusion.

## Find the Suno integration in the official MCP Registry

Open [Suno in the official MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.AceDataCloud%2Fmcp-suno), expand the matching `io.github.AceDataCloud` entry, and use its **Packages** or **Remotes** installation information in a client that consumes MCP catalogs. This is the Suno integration provided by Ace Data Cloud; it is not an endorsement by the model vendor. The Registry is a directory, not the app that runs a tool.

Search for `mcp-suno` (or `io.github.AceDataCloud/mcp-suno`) to locate the exact entry. The official Registry search currently matches server names; spaces in a display title do not create extra search aliases. If your client does not consume the catalog, use the client-specific connection instructions below and check **Applications → General application** for your token, service permissions, balance and current price. Keep the original task ID when checking asynchronous results.


## Features

- **Music Generation** - Create AI-generated songs from text prompts
- **Custom Lyrics & Style** - Full control over lyrics, title, and music style
- **Song Extension** - Continue existing songs from any timestamp
- **Cover/Remix** - Create cover versions with different styles
- **Lyrics Generation** - Generate structured lyrics from descriptions
- **Persona Management** - Save and reuse voice styles
- **Custom Music Models** - Create and reuse app-owned custom music models
- **Task Tracking** - Monitor generation progress and retrieve results

## Tool Reference

| Tool | Description |
|------|-------------|
| `suno_generate_music` | Generate AI music from a text prompt using Suno's Inspiration Mode. |
| `suno_generate_custom_music` | Generate AI music with full control over lyrics, title, and style (Custom Mode). |
| `suno_extend_music` | Extend an existing song from a specific timestamp with new lyrics. |
| `suno_cover_music` | Create a cover or remix version of an existing song in a different style. |
| `suno_concat_music` | Concatenate extended song segments into a single complete audio file. |
| `suno_generate_with_persona` | Generate music using a saved artist persona for consistent vocal style. |
| `suno_remaster_music` | Remaster an existing song; v5/v5.5 require a variation category. |
| `suno_stems_music` | Separate a song into individual stems (vocals and instruments). |
| `suno_replace_section` | Replace a specific time range in a song with new generated content. |
| `suno_upload_extend` | Extend an uploaded audio (your own music) with new AI-generated content. |
| `suno_upload_cover` | Create an AI cover of an uploaded audio (your own music). |
| `suno_mashup_music` | Blend exactly two songs using a required creative-direction prompt. |
| `suno_all_stems_music` | Return two distinct 12-stem candidate sets, labeled `stem_set` 1 and 2 in task results. |
| `suno_generate_lyrics` | Generate song lyrics from a text prompt. |
| `suno_get_mp4` | Get an MP4 video version of a generated song. |
| `suno_get_timing` | Get timing and subtitle data for a generated song. |
| `suno_extract_vocals` | Extract a required vocal interval shorter than 30 seconds. |
| `suno_get_wav` | Get the lossless WAV format of a generated song. |
| `suno_get_mp3` | Get the compressed MP3 format of a generated song. |
| `suno_get_midi` | Get MIDI data extracted from a generated song. |
| `suno_create_persona` | Create a new artist persona from an existing audio's vocal style. |
| `suno_create_custom_model` | Create a reusable custom music model from 6 to 24 authorized audio URLs. |
| `suno_get_custom_model` | Retrieve one custom music model by ID. |
| `suno_list_custom_models` | List custom music models for the current Suno application. |
| `suno_generate_with_custom_model` | Generate a song using a ready custom music model. |
| `suno_delete_custom_model` | Archive a custom music model so it can no longer be used. |
| `suno_optimize_style` | Optimize a music style description for better generation results. |
| `suno_mashup_lyrics` | Generate mashup lyrics by combining two sets of lyrics. |
| `suno_upload_audio` | Upload external audio in standard or enhanced mode for subsequent operations. |
| `suno_get_task` | Query the status and result of a music generation task. |
| `suno_get_tasks_batch` | Query multiple music generation tasks at once. |
| `suno_list_models` | List all available Suno models and their capabilities. |
| `suno_list_actions` | List all available Suno API actions and corresponding tools. |
| `suno_get_lyric_format_guide` | Get guidance on formatting lyrics for Suno music generation. |

## Connect in minutes

The hosted server is `https://suno.mcp.acedata.cloud/mcp`. Choose **one** authentication route before following a client example:

| Route | Use it when | What you provide |
|---|---|---|
| Browser sign-in (OAuth) | Your MCP client supports remote OAuth; use DCR if the client requires automatic registration | The server URL; sign in to AceDataCloud and approve access in the browser. No key needs to be pasted into the MCP config. |
| API token | Your client cannot complete the remote OAuth flow, or you need an explicit credential for an integration | An AceDataCloud API token in the client's Bearer header. Keep it in a user-level secret store or environment variable. |
| Local stdio | You want the MCP process to run on your machine | Install `mcp-suno` and pass `ACEDATACLOUD_API_TOKEN` to that process. |

The hosted server always receives a Bearer token: with OAuth, the client obtains and sends it after sign-in; with API-token setup, you supply it. **DCR is client registration, not a separate AceDataCloud API key.** After consent, the hosted service currently reuses or creates an API credential for your account; it may fail if the account cannot obtain one. Some clients offer a published client identity or manual client ID; those are client-specific alternatives, not a second API-token requirement. Browser sign-in does not remove the need for an AceDataCloud account. Music generation uses your AceDataCloud account and may incur usage charges. Review [current Suno pricing and limits](https://platform.acedata.cloud/documents/suno-audios?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-audios) before generating.

### Browser sign-in: hosted server

Use this path for clients with remote MCP OAuth support. Add **only the URL** first; do not also set an `Authorization` header. If a client cannot complete discovery or registration, use the API-token route below.

#### Claude and Claude Desktop chat

Use Claude's **remote custom connector** in `Customize → Connectors → Add custom connector` (or your organization's connector settings). Enter the hosted URL, choose sign-in, and select **Register automatically** for the OAuth client if Claude asks. Complete the AceDataCloud login and consent flow, then enable the connector in your conversation. Claude Desktop's `claude_desktop_config.json` is for **local** MCP processes; it is not where Claude's remote custom connectors are installed. [Claude's connector guide](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

#### Claude Code

```bash
claude mcp add --transport http --scope user suno https://suno.mcp.acedata.cloud/mcp
claude mcp login suno
```

In Claude Code, `/mcp` shows the connection and available tools. For project scope, merge `{"mcpServers":{"suno":{"type":"http","url":"https://suno.mcp.acedata.cloud/mcp"}}}` into `<project>/.mcp.json`; keep existing entries when merging. Claude Code and Claude Desktop chat have separate MCP configuration. [Claude Code MCP guide](https://code.claude.com/docs/en/mcp).

#### Cursor

In Cursor's MCP settings, add a remote server with the hosted URL and complete the OAuth prompt. For project scope, merge this into `<project>/.cursor/mcp.json`; for your own machines, use `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "suno": {
      "url": "https://suno.mcp.acedata.cloud/mcp"
    }
  }
}
```

The URL-only project config contains no token. Do not commit a project config if you later add a real token. [Cursor MCP guide](https://cursor.com/docs/mcp).

#### VS Code with GitHub Copilot

Run **MCP: Add Server**, choose HTTP, and enter the hosted URL. Save to the user profile for personal use or to a workspace config for a team; approve the server and complete sign-in when prompted. New workspace configs use `<project>/.mcp.json`; VS Code also reads its `.vscode/mcp.json` format. This is the VS Code format for a local workspace:

```json
{
  "servers": {
    "suno": {
      "type": "http",
      "url": "https://suno.mcp.acedata.cloud/mcp"
    }
  }
}
```

Run **MCP: List Servers** to check connection and tool loading. [VS Code MCP setup](https://code.visualstudio.com/docs/agent-customization/mcp-servers) and [configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

#### Codex CLI or Codex app

```bash
codex mcp add suno --url https://suno.mcp.acedata.cloud/mcp
codex mcp login suno
```

Codex keeps user MCP settings in `~/.codex/config.toml` and can show the server in `/mcp`. [Official Codex MCP guide](https://developers.openai.com/codex/mcp/).

### API token: hosted server

<!-- BEGIN TOKEN ONBOARDING -->
1. Open [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_api_key). Sign in, or register an account first.
2. Find **General application**. If it has not been created, choose **Initialize General Application**. A general key can use the services available to your account; a dedicated application's key is limited to its service. Check the required service/model access and [current pricing](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_models).
3. Copy the **API Key** from the application card, or open **Keys / Manage Keys → Create** to create a separate key for this integration. Give it a recognizable name so you can revoke or rotate it independently.
4. When creating a key, review **Expiration Time**, **Set Usage Limitation**, and **Allowed APIs**. Enable only the restrictions you need, allow the operations you will call, then click **Create** and copy the token from the key list. Task lookup does not grant permission to submit a generation. Confirm the application's balance can cover your first request; any trial allowance is whatever your account currently displays.
5. Copy only the token value, without quotation marks, spaces, or `Bearer `. An API Key / API Token field expects this raw value; only a manually configured HTTP `Authorization` header needs the `Bearer ` prefix. A `platform-...` account-management token cannot replace a generation API key.

![Copy an application API key or open Manage Keys](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/2522b2f57210597af2db866445319334a1677a23/_assets/tutorial/get-api-key-en.png)

![Create a separately named key with optional restrictions](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/2522b2f57210597af2db866445319334a1677a23/_assets/tutorial/create-api-key-en.png)

Save the key in the client's credential store or the environment variable shown below. Never put it in a prompt, shared workflow, screenshot, or Git commit. If authentication fails, check the full copied value, application/service access, expiration, usage limit, and balance before creating another key.
<!-- END TOKEN ONBOARDING -->

Use this route when you need a fixed credential or your client does not complete OAuth. An invalid fixed header does not automatically fall back to browser sign-in.

For **Claude Code**, set the variable in the environment that starts Claude Code, then add the server. The shell expands the token when you add the server, so treat the saved user-level MCP config as a secret; use browser sign-in above if you do not want a key in client config:

```bash
export ACEDATACLOUD_API_TOKEN='YOUR_API_TOKEN'
claude mcp add --transport http --scope user suno https://suno.mcp.acedata.cloud/mcp \
  --header "Authorization: Bearer $ACEDATACLOUD_API_TOKEN"
```

For a shared project config, put only the variable reference in `<project>/.mcp.json` and keep the token in each user's environment. Unlike the CLI example above, Claude Code expands `${ACEDATACLOUD_API_TOKEN}` when it reads `.mcp.json`. Merge this entry with existing servers:

```json
{
  "mcpServers": {
    "suno": {
      "type": "http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer ${ACEDATACLOUD_API_TOKEN}"
      }
    }
  }
}
```

For **Cursor**, use its `${env:ACEDATACLOUD_API_TOKEN}` syntax in a user-level `~/.cursor/mcp.json` (or an uncommitted project config):

```json
{
  "mcpServers": {
    "suno": {
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer ${env:ACEDATACLOUD_API_TOKEN}"
      }
    }
  }
}
```

For **VS Code**, prefer a user-profile MCP config and a masked input instead of putting the token in the JSON. Merge these fields into the file opened by **MCP: Open User Configuration**:

```json
{
  "inputs": [
    {"id": "acedata-suno-token", "type": "promptString", "description": "AceDataCloud API token", "password": true}
  ],
  "servers": {
    "suno": {
      "type": "http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {"Authorization": "Bearer ${input:acedata-suno-token}"}
    }
  }
}
```

This interactive input is specific to VS Code's user/workspace format; do not copy it into `.mcp.json` for Agent Host. VS Code prompts once and stores the value securely for later use. [VS Code configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

Other clients use different schemas. For **Cline**, open **MCP Servers → Configure → Configure MCP Servers** (Cline CLI: `~/.cline/data/settings/cline_mcp_settings.json`) and use `type: "streamableHttp"` under `mcpServers`; [Cline's guide](https://docs.cline.bot/mcp/mcp-overview) has the full shape. For **JetBrains AI Assistant**, go to **Settings → Tools → AI Assistant → Model Context Protocol (MCP)** and add a remote server using the hosted URL; check its connection status and use the API-token route if your version does not complete OAuth. [JetBrains' guide](https://www.jetbrains.com/help/ai-assistant/mcp.html). For **Zed**, use `context_servers` with the hosted URL in its settings; omitting `Authorization` starts its OAuth flow. [Zed's guide](https://zed.dev/docs/ai/mcp).

### Local stdio server

Local mode needs an API token. Use it when your client only supports local processes or you want the MCP process on your machine; it still calls the AceDataCloud API and does not run Suno locally.

```bash
# Install once, then run the local stdio server
python -m pip install mcp-suno
export ACEDATACLOUD_API_TOKEN='YOUR_API_TOKEN'
mcp-suno
```

For Claude Desktop's **local** MCP configuration, merge this into the file opened by its developer settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS). This is a local `uvx` process; it is separate from the remote custom connector above:

```json
{
  "mcpServers": {
    "suno": {
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": {
        "ACEDATACLOUD_API_TOKEN": "YOUR_API_TOKEN"
      }
    }
  }
}
```

Keep this user-level file private. On Windows, set `$env:ACEDATACLOUD_API_TOKEN = 'YOUR_API_TOKEN'` in the shell that starts local clients. `uvx` requires [uv](https://docs.astral.sh/uv/) on `PATH`; `mcp-suno` requires the package installed in the environment from which the client launches it.

For self-hosted HTTP, run `mcp-suno --transport http --port 8000` or build this repository's Dockerfile and run the resulting image. Clients must send their own Bearer tokens; expose the service only with suitable network and TLS controls.

### Check the connection before generating

1. `https://suno.mcp.acedata.cloud/health` returning `{"status":"ok"}` checks reachability only, not authentication.
2. Use the client's MCP server list to confirm Suno tools appear. `suno_list_models` and `suno_list_actions` return static reference data; they confirm tool loading, **not** that your downstream API credential or balance works.
3. When ready, ask the client to call `suno_generate_music` with a short prompt. Save the returned task ID, then call `suno_get_task` until it completes. This is the first end-to-end API check and can be billed. Check the current [Suno service limits and pricing](https://platform.acedata.cloud/documents/suno-audios?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-audios) before this step.

If you see **401**, check whether the client completed OAuth or sent a valid token, and do not configure both paths at once. If OAuth redirects but fails, retry from the same client session; if the account cannot create or retrieve a credential, resolve that in AceDataCloud Platform. A tool list can load while an API call fails for balance, permissions, or service availability, so check the returned error rather than assuming the connection failed.

## Use the tools

Tool names in the client include the `suno_` prefix. Start with `suno_list_models` or `suno_list_actions` to confirm the connection. For generation, use `suno_generate_music` for a prompt or `suno_generate_custom_music` for your own lyrics and style. Advanced operations, media conversion, personas, and custom models are listed in the [tool reference](#tool-reference) and exposed by the MCP server.

Generation and edits return a **task ID**, not a finished song. Query `suno_get_task` (or `suno_get_tasks_batch` for multiple IDs) until the task reports success and final media URLs. An intermediate audio URL may be only a preview; a failed task should stop polling. Do not repeat the generation call to check progress, because it may submit and bill another task.

Example request to your MCP client:

> Use `suno_generate_music` to create a short upbeat acoustic birthday song. Give me the task ID, check it with `suno_get_task`, and share the final audio only after the task completes.

For custom lyrics:

> Use `suno_generate_custom_music` with title “Storm”, style “energetic rock”, and these lyrics: `[Verse] Thunder in the night [Chorus] We are the storm`. Then follow the returned task ID to completion.

`negative_tags` excludes styles or genres only in custom mode (`custom=true`). The API currently sets no fixed character limit for this field, but overly long content may still fail; keep the description concise.

For covers, extensions and stem separation, use the returned audio `id` as `audio_id`. A downloadable audio file does **not** guarantee that its ID remains available for further processing.

### Processing errors

The audio API documents these HTTP 500 errors:

| Code | Meaning |
| --- | --- |
| `api_error` with message `the account may have been offline` | The audio API reports that the account may have been offline. |
| `suno_processing_unavailable` | Music processing is unavailable. |
| `suno_model_unavailable` | The selected model is unavailable for this operation. |
| `suno_processing_failed` | Music processing returned no audio. |

Stop on terminal failure, retain any returned `task_id` and `trace_id`, and contact support with those IDs. Do not blindly resubmit, switch models, or treat an existing download URL as proof that another processing request will work.

## Available Models

| Model             | Version | Max Duration | Features             |
| ----------------- | ------- | ------------ | -------------------- |
| `chirp-v6`        | V6      | API-defined  | Current v6 model     |
| `chirp-v6-wild`   | V6 Wild | API-defined  | v6 Wild model        |
| `chirp-v6-mini`   | V6 Mini | API-defined  | v6 Mini model        |
| `chirp-v5-5`      | V5.5    | 8 minutes    | Previous model name  |
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
| `ACEDATACLOUD_API_TOKEN`    | Local stdio token; hosted requests provide it via OAuth or Bearer header | Required for local stdio |
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
git clone https://github.com/AceDataCloud/SunoMCP.git
cd SunoMCP

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
SunoMCP/
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
│   ├── custom_model_tools.py # Custom music model tools
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

This server wraps the [AceDataCloud Suno API](https://platform.acedata.cloud/documents/suno-audios?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-audios):

- [Suno Audios API](https://platform.acedata.cloud/documents/suno-audios?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-audios) - Music generation
- [Suno Lyrics API](https://platform.acedata.cloud/documents/suno-lyrics?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-lyrics) - Lyrics generation
- [Suno Tasks API](https://platform.acedata.cloud/documents/suno-tasks?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-tasks) - Task queries
- [Suno Persona API](https://platform.acedata.cloud/documents/suno-persona?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_documents_suno-persona) - Persona management

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## Documentation

<!-- canonical-documentation -->
[Documentation](https://platform.acedata.cloud/documents/suno-mcp?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_quick_start)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [AceDataCloud Platform](https://platform.acedata.cloud?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_platform)
- [Suno Official](https://suno.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

Made with love by [AceDataCloud](https://platform.acedata.cloud?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_platform)

## Cline setup / Cline 图文接入

[Suno by Ace Data Cloud — English guide](https://github.com/AceDataCloud/MCPs/blob/4a2fb4e17d322bc22c5742ab3a5bd48b24ec5bdc/suno/docs/cline.md) · [完整中文图文步骤](https://github.com/AceDataCloud/MCPs/blob/4a2fb4e17d322bc22c5742ab3a5bd48b24ec5bdc/suno/docs/cline.md#中文步骤). The Cline marketplace submission is pending review as of 2026-10-18; the guide labels the manual fallback separately. / Cline 官方目录投稿仍待审核，手动接入不等于已上架。

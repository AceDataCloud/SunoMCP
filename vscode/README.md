# Suno MCP

AI music generation with Suno — songs, lyrics, covers, stems, and more.

[![VS Code Marketplace](https://img.shields.io/badge/VS%20Code-Marketplace-blue?logo=visualstudiocode&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=acedatacloud.mcp-suno) [![PyPI](https://img.shields.io/pypi/v/mcp-suno.svg?label=PyPI)](https://pypi.org/project/mcp-suno/) [![Hosted MCP](https://img.shields.io/badge/hosted-mcp-blue)](https://suno.mcp.acedata.cloud/mcp)

Connect VS Code's AI agents to Suno through Ace Data Cloud. Generate songs from text prompts, write custom lyrics with full musical control, extend tracks, remix or cover, separate stems, export MP4/WAV/MIDI — all from chat.

This extension registers the **suno** MCP server with VS Code so GitHub
Copilot and any other agent that speaks the [Model Context Protocol](https://modelcontextprotocol.io/)
can call it directly from chat.

---

## Quick Start

1. **Install this extension.** VS Code registers the `suno` MCP server automatically.
2. **Get an API key** from [Ace Data Cloud](https://platform.acedata.cloud/console/applications) (Applications → API Key). New accounts include free trial credit.
3. **Open Copilot Chat** in agent mode and ask for a music task — the extension prompts for the API key the first time and stores it in the OS keychain via VS Code's `SecretStorage`.

You can rotate or remove the API key any time from the command palette:

- **Suno MCP: Set Ace Data Cloud API Key**
- **Suno MCP: Clear Ace Data Cloud API Key**

> The default config talks to the **hosted streamable-HTTP endpoint** at
> `https://suno.mcp.acedata.cloud/mcp` — no Python, no `uvx`, no local install needed.

## VS Code Setup Guide

For screenshots, token setup, project-level and user-level `mcp.json`, and Copilot Agent Mode examples, see:

- [Suno MCP VS Code guide](https://platform.acedata.cloud/documents/promotion_article_mcp_suno_vscode)
- [All Ace Data Cloud MCP servers in VS Code](https://platform.acedata.cloud/documents/promotion_article_mcp_all_vscode)

### Example prompts

- "Generate a lofi hip-hop track about late-night coding. Use suno."
- "Write lyrics for a punk song about deadline pressure, then turn them into a song."
- "Cover the song with task id <id> in a jazz piano style."

---

## Tool Reference

**35 tools** available via this server.

| Tool | Description |
| --- | --- |
| `suno_generate_music` | Generate AI music from a text prompt using Suno's Inspiration Mode. |
| `suno_generate_custom_music` | Generate AI music with full control over lyrics, title, and style (Custom Mode). |
| `suno_extend_music` | Extend an existing song from a specific timestamp with new lyrics. |
| `suno_cover_music` | Create a cover or remix version of an existing song in a different style. |
| `suno_concat_music` | Concatenate extended song segments into a single complete audio file. |
| `suno_generate_with_persona` | Generate music using a saved artist persona for consistent vocal style. |
| `suno_generate_with_persona_vox` | Generate music with stronger vocal consistency from a saved persona. |
| `suno_remaster_music` | Remaster an existing song to improve audio quality. |
| `suno_stems_music` | Separate a song into individual stems (vocals and instruments). |
| `suno_all_stems_music` | Separate a song into vocals, bass, drums, and other instrument stems. |
| `suno_replace_section` | Replace a specific time range in a song with new generated content. |
| `suno_upload_extend` | Extend an uploaded audio (your own music) with new AI-generated content. |
| `suno_upload_cover` | Create an AI cover of an uploaded audio (your own music). |
| `suno_mashup_music` | Create a musical mashup by blending multiple songs together. |
| `suno_generate_lyrics` | Generate song lyrics from a text prompt. |
| `suno_get_mp4` | Get an MP4 video version of a generated song. |
| `suno_get_timing` | Get timing and subtitle data for a generated song. |
| `suno_extract_vocals` | Extract the vocal track from a generated song (stem separation). |
| `suno_get_wav` | Get the lossless WAV format of a generated song. |
| `suno_get_midi` | Get MIDI data extracted from a generated song. |
| `suno_create_persona` | Create a new artist persona from an existing audio's vocal style. |
| `suno_create_voice` | Create a custom voice persona from an external audio URL. |
| `suno_list_personas` | List saved artist personas and voice IDs. |
| `suno_delete_persona` | Delete a saved artist persona. |
| `suno_optimize_style` | Optimize a music style description for better generation results. |
| `suno_mashup_lyrics` | Generate mashup lyrics by combining two sets of lyrics. |
| `suno_upload_audio` | Upload an external audio file to Suno for use in subsequent operations. |
| `suno_underpainting` | Add AI-generated accompaniment under uploaded vocals. |
| `suno_overpainting` | Add AI-generated vocals over uploaded instrumental audio. |
| `suno_samples_music` | Add AI-generated samples to uploaded audio. |
| `suno_get_task` | Query the status and result of a music generation task. |
| `suno_get_tasks_batch` | Query multiple music generation tasks at once. |
| `suno_list_models` | List all available Suno models and their capabilities. |
| `suno_list_actions` | List all available Suno API actions and corresponding tools. |
| `suno_get_lyric_format_guide` | Get guidance on formatting lyrics for Suno music generation. |

## Supported Models

`v3.5`, `v4`, `v4.5`, `v5`

## Pricing

From $0.05 per song. New users get free trial credit at sign-up. See full pricing at [https://docs.acedata.cloud](https://docs.acedata.cloud).

---

## Configuration

This extension implements the `mcpServerDefinitionProviders` contribution point
and registers a single hosted server with VS Code:

```text
Provider id : acedatacloud.suno
Server label: Suno MCP
Server URL  : https://suno.mcp.acedata.cloud/mcp
Transport   : Streamable HTTP
Auth        : Bearer API key from VS Code SecretStorage (or $ACEDATACLOUD_API_TOKEN)
```

You don't need to edit `mcp.json` — the extension handles registration and
token handling automatically. If you'd rather configure things by hand, the
sections below show equivalent `mcp.json` snippets you can use **instead of**
this extension.

### Alternative: manual `mcp.json` (hosted)

```jsonc
{
  "servers": {
    "suno": {
      "type": "http",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": { "Authorization": "Bearer ${input:acedatacloud_api_token}" }
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "acedatacloud_api_token",
      "description": "Ace Data Cloud API key",
      "password": true
    }
  ]
}
```

### Alternative: local stdio (no network roundtrip)

For offline dev, air-gapped environments, or pinning to a specific PyPI
version, install [`uv`](https://docs.astral.sh/uv/) and use:

```jsonc
{
  "servers": {
    "suno": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": { "ACEDATACLOUD_API_TOKEN": "${input:acedatacloud_api_token}" }
    }
  }
}
```

`uvx` will download and run the latest [`mcp-suno`](https://pypi.org/project/mcp-suno/) on demand.

---

## Links

- **Hosted endpoint:** https://suno.mcp.acedata.cloud/mcp
- **PyPI package:** [`mcp-suno`](https://pypi.org/project/mcp-suno/)
- **Source repository:** https://github.com/AceDataCloud/SunoMCP
- **Ace Data Cloud platform:** https://platform.acedata.cloud
- **MCP documentation:** https://docs.acedata.cloud

## License

MIT — see [LICENSE](LICENSE).

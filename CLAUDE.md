# SunoMCP

MCP (Model Context Protocol) server for Suno AI music generation via AceDataCloud API.

## Project Structure

```
core/
  config.py     — Settings dataclass (API token, base URL)
  server.py     — FastMCP server singleton
  client.py     — httpx async HTTP client
  types.py      — Literal types (SunoModel, VocalGender, etc.)
  exceptions.py — Error classes (AuthError, APIError, TimeoutError)
  utils.py      — Formatting helpers
tools/
  audio_tools.py   — generate, custom, extend, cover, remaster, concat
  lyrics_tools.py  — generate lyrics, mashup
  media_tools.py   — MP4, WAV, MIDI, timing, vocal separation
  persona_tools.py — save/manage voice personas
  style_tools.py   — optimize style descriptions
  task_tools.py    — query task status, wait for completion
  info_tools.py    — list models, capabilities
prompts/           — LLM guidance prompts
tests/             — pytest-asyncio + respx tests
```

## Sync from Docs

When invoked by the sync workflow, the Docs repo is checked out at `_docs/`. Your job:

1. **Source of truth** — `_docs/openapi/suno.json` is the OpenAPI spec for the Suno API.
2. **Compare models** — The `SunoModel` Literal in `core/types.py` must match the spec's model enum. Add/remove as needed.
3. **Compare parameters** — Each `@mcp.tool()` function's parameters should match the corresponding OpenAPI endpoint.
4. **Update defaults** — If a new model becomes the recommended default, update `DEFAULT_MODEL` in `core/types.py`.
5. **Update README** — Keep the model table and feature list current.
6. **Add tests** — For new tools or parameters, add test cases in `tests/`.
7. **PR title** — Use format: `sync: <description> [auto-sync]`

## Development

```bash
pip install -e ".[dev]"
pytest --cov=core --cov=tools
ruff check .
```

# MCPSuno

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

When working on an auto-sync issue (labeled `auto-sync`), follow these rules:

1. **Compare models** — The `SunoModel` Literal in `core/types.py` must match the model enum from the Docs OpenAPI spec. Add/remove model values as needed.
2. **Compare parameters** — Each `@mcp.tool()` function's parameters should include all parameters from the corresponding OpenAPI endpoint. Use the Docs OpenAPI spec as source of truth.
3. **Update defaults** — If a new model becomes the recommended default, update `DEFAULT_MODEL` in `core/types.py`.
4. **Update README** — Keep the model table and feature list current.
5. **Add tests** — For new tools or parameters, add test cases in `tests/`.
6. **PR title** — Use format: `sync: <description> [auto-sync]`

## Development

```bash
pip install -e ".[dev]"
pytest --cov=core --cov=tools
ruff check .
```

# Copilot Instructions for SunoMCP

## Sync from Docs

When working on a sync task (issue labeled `auto-sync`), follow these rules:

1. **Source of truth** — Clone/checkout `AceDataCloud/Docs` and read `openapi/suno.json` (the Suno API OpenAPI spec).
2. **Compare models** — The `SunoModel` Literal in `core/types.py` must exactly match the model enum from the OpenAPI spec. Add missing models, remove deprecated ones.
3. **Compare endpoints** — Each endpoint in the spec should have a corresponding `@mcp.tool()` function in `tools/`. Add tools for new endpoints if needed.
4. **Compare parameters** — Each tool function's parameters should match the corresponding OpenAPI endpoint's request body schema.
5. **Update defaults** — If a new model becomes the recommended default, update `DEFAULT_MODEL` in `core/types.py`.
6. **Update README** — Keep the model table and feature list in `README.md` current.
7. **Add tests** — For new tools or parameters, add test cases in `tests/`.
8. **PR title** — Use format: `sync: <description> [auto-sync]`
9. **No changes needed** — If everything is already in sync, close the issue with a comment.

## Project Structure

```
core/
  config.py     — Settings dataclass (API token, base URL)
  server.py     — FastMCP server singleton
  client.py     — httpx async HTTP client
  types.py      — Literal types (SunoModel, VocalGender, etc.)
  exceptions.py — Error classes
  utils.py      — Formatting helpers
tools/           — @mcp.tool() decorated async functions
prompts/         — LLM guidance prompts
tests/           — pytest-asyncio + respx tests
```

## Development

```bash
pip install -e ".[dev]"
pytest --cov=core --cov=tools
ruff check .
```

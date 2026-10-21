---
name: suno-music
description: Use Suno through Ace Data Cloud in goose for Suno music, lyrics and covers. Use the installed service MCP tools; query the original task ID after generation. This plugin is maintained by Ace Data Cloud, not the service brand's official plugin.
license: MIT
---

# Suno by Ace Data Cloud

Use the MCP tools installed by this plugin. Match tools by their suffix because goose namespaces them with `suno-by-acedatacloud`.

- Read `../../README.md` for installation and credential setup. The service API key belongs in `ACEDATACLOUD_API_TOKEN` in the environment that starts goose; never ask the user to paste it into chat.
- A free connection/reference check uses `suno_list_models`. Static reference success is not a paid generation or a billing result.
- For an explicitly requested generation/edit, inspect the installed tool schema first. Use `suno_generate_music`, `suno_generate_custom_music` as applicable. Do not invent model defaults or silently substitute another model/service.
- For custom generation, use `negative_tags` only to exclude styles or genres in custom mode (`custom=true`). There is currently no fixed API character limit for this field, but overly long content may fail; keep it concise rather than imposing an invented limit.
- For covers, extensions or stem separation, pass the audio `id` as `audio_id`. A downloadable file does not prove the ID is still available for processing.
- Confirm current account access, balance and price; preserve any user spending cap. Do not generate merely to test installation or check progress.
- After one submission, retain the returned task ID. Use `suno_get_task` to query that same ID, with the exact ID argument name from the schema. A pending result is not success; stop at terminal failure and preserve upstream meaning. Do not submit another generation to poll.
- On HTTP 500 `api_error` with message `the account may have been offline`, or on `suno_processing_unavailable`, `suno_model_unavailable` or `suno_processing_failed`, stop on terminal failure, retain any returned `task_id` and `trace_id`, and contact support with those IDs. Do not blindly retry, silently switch models, or use a download URL as evidence that processing is available.
- Report complete only with an explicit successful terminal status and returned media URLs. Never fabricate audio/image/video URLs or claim a unique billing record without checking the account's actual usage.

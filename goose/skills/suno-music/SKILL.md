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
- Use `negative_tags` to exclude styles or genres in custom generation or `suno_replace_section`. There is currently no fixed API character limit for this field, but overly long content may fail; keep it concise rather than imposing an invented limit.
- For `suno_extend_music` or `suno_upload_extend`, supply a positive `continue_at` in seconds and preserve fractional values such as `30.792`. New lyrics only affect content after that boundary; use generation or a cover to reinterpret the whole song. For replacement, require `0 <= replace_section_start < replace_section_end`; for `suno_samples_music`, require `samples_end > samples_start >= 0` (start defaults to 0). End times must not exceed the source duration.
- `persona_id` is a voice ID, not an audio ID. Artist-consistency tools require it; extensions do not use an extra persona. For `suno_generate_inspo`, provide 1–4 authorized public reference audio URLs, use `instrumental=true` for no lyrics, or `custom=true` with `lyric_prompt` and no lyrics to generate lyrics automatically. Inspo voice selection depends on the service channel; do not promise it always applies. `duration` is a generation-only target, not a guaranteed finished length.
- For covers, extensions or stem separation, pass the audio `id` as `audio_id`. A downloadable file does not prove the ID is still available for processing.
- For a specified-voice cover, pass `persona_id` to `suno_cover_music` or `suno_upload_cover`. For a private voice created by `suno_create_voice`, first call `suno_upload_audio` with the source `audio_url`, `mode: "standard"` and that `persona_id`; then call `suno_upload_cover` with the returned `data.audio_id` and the same `persona_id`. Do not reuse an older unassociated audio ID or use enhanced upload. Keep voice creation, upload and cover on the same service channel. No extra `vocal_gender` is needed, and a gender preference cannot replace the voice ID.
- Before a cover or extension, use `suno_check_audio_availability` with the audio UUID from the completed song, not its task ID. This authenticated precheck is synchronous and currently costs no Credits; do not poll its returned task ID. Success only reports `data.available=true` for the current channel at check time and does not guarantee later processing. HTTP 503 `availability_unknown` or another error means the check could not confirm availability, not `false`; retain support identifiers and stop rather than blindly retrying or submitting a paid operation to test availability.
- Confirm current account access, balance and price; preserve any user spending cap. Do not generate merely to test installation or check progress.
- After one submission, retain the returned task ID. Use `suno_get_task` to query that same ID, with the exact ID argument name from the schema. A pending result is not success; stop at terminal failure and preserve upstream meaning. Do not submit another generation to poll.
- On HTTP 500 `api_error` with message `the account may have been offline`, or on `suno_processing_unavailable`, `suno_model_unavailable` or `suno_processing_failed`, stop on terminal failure, retain any returned `task_id` and `trace_id`, and contact support with those IDs. Do not blindly retry, silently switch models, or use a download URL as evidence that processing is available.
- For `suno_all_stems_music`, wait for the full task to reach successful completion; a playable URL during processing does not prove that all stems are ready.
- Report complete only with an explicit successful terminal status and returned media URLs. Never fabricate audio/image/video URLs or claim a unique billing record without checking the account's actual usage.

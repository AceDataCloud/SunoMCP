"""Informational tools for Suno API."""

from core.server import mcp


@mcp.tool()
async def suno_list_models() -> str:
    """List all available Suno models and their capabilities.

    Shows all available model versions with their limits, features, and
    recommended use cases. Use this to understand which model to choose
    for your music generation.

    Model comparison:
    - chirp-v5-5: Latest, highest quality, 8-minute max duration
    - chirp-v5: High quality, 8-minute max duration
    - chirp-v4-5-plus: High quality with 8-minute duration
    - chirp-v4-5: Recommended balance of quality and speed, 4-minute duration
    - chirp-v4: Good quality, 150 seconds max
    - chirp-v3-5/v3: Legacy models, 120 seconds max

    Returns:
        Table of all models with their version, limits, and features.
    """
    # Last updated: 2026-04-05
    return """Available Suno Models:

| Model           | Version | Prompt Limit | Lyric Limit  | Style Limit | Max Duration |
|-----------------|---------|--------------|--------------|-------------|--------------|
| chirp-v5-5      | V5.5    | 200 chars    | 5000 chars   | 1000 chars  | 8 minutes    |
| chirp-v5        | V5      | 200 chars    | 5000 chars   | 1000 chars  | 8 minutes    |
| chirp-v4-5-plus | V4.5+   | 200 chars    | 5000 chars   | 1000 chars  | 8 minutes    |
| chirp-v4-5      | V4.5    | 200 chars    | 5000 chars   | 1000 chars  | 4 minutes    |
| chirp-v4        | V4      | 200 chars    | 3000 chars   | 200 chars   | 150 seconds  |
| chirp-v3-5      | V3.5    | 200 chars    | 3000 chars   | 200 chars   | 120 seconds  |
| chirp-v3-0      | V3      | 200 chars    | 3000 chars   | 200 chars   | 120 seconds  |

Recommended: chirp-v5-5 for best quality, chirp-v4-5 for a reliable alternative.

Features by Version:
- V4.5+: Vocal gender control ('f' for female, 'm' for male)
- V5/V5.5: High quality model with 8-minute songs
"""


@mcp.tool()
async def suno_list_actions() -> str:
    """List all available Suno API actions and corresponding tools.

    Reference guide for what each action does and which tool to use.
    Helpful for understanding the full capabilities of the Suno MCP.

    Returns:
        Categorized list of all actions and their corresponding tools.
    """
    # Last updated: 2026-04-27
    return """Available Suno Actions and Tools:

Music Generation:
- suno_generate_music: Create music from a simple text prompt (Inspiration Mode)
- suno_generate_custom_music: Create music with custom lyrics and style (Custom Mode)
- suno_extend_music: Continue an existing song from a specific timestamp
- suno_cover_music: Create a cover/remix version of a song
- suno_concat_music: Merge extended song segments into complete audio
- suno_remaster_music: Remaster a song to improve audio quality
- suno_replace_section: Replace a specific time range with new content
- suno_mashup_music: Blend multiple songs together musically

Upload-based Operations (for your own music):
- suno_upload_audio: Upload external audio for use in Suno
- suno_upload_extend: Extend uploaded audio with new AI content
- suno_upload_cover: Create an AI cover of uploaded audio
- suno_underpainting: Add AI-generated accompaniment to uploaded vocal audio
- suno_overpainting: Add AI-generated vocals to uploaded instrumental audio
- suno_samples_music: Add AI-generated samples to uploaded audio

Stems & Extraction:
- suno_stems_music: Separate a song into vocal and instrumental stems
- suno_all_stems_music: Separate a song into all individual stems (vocals, bass, drums, etc.)
- suno_extract_vocals: Extract only the vocal track from a song

Media Conversion:
- suno_get_mp4: Get MP4 video version of a song
- suno_get_wav: Get lossless WAV format of a song
- suno_get_midi: Get MIDI data from a song
- suno_get_timing: Get word-level timing/subtitle data

Persona (Voice Style):
- suno_create_persona: Save a voice style from a Suno-generated audio for reuse
- suno_create_voice: Create a voice persona from an external audio URL
- suno_list_personas: List all saved voice personas for a user
- suno_delete_persona: Delete a saved voice persona
- suno_generate_with_persona: Generate with a saved voice style
- suno_generate_with_persona_vox: Generate with a saved voice style using VOX consistency mode

Lyrics:
- suno_generate_lyrics: Generate song lyrics from a prompt
- suno_optimize_style: Optimize a style description for better results
- suno_mashup_lyrics: Combine two sets of lyrics into a mashup

Task Management:
- suno_get_task: Check status of a single generation
- suno_get_tasks_batch: Check status of multiple generations

Information:
- suno_list_models: Show available models and their capabilities
- suno_list_actions: Show this action reference (you are here)
- suno_get_lyric_format_guide: Show how to format lyrics

Workflow Examples:
1. Quick song: suno_generate_music → suno_get_task
2. Custom song: suno_generate_lyrics → suno_generate_custom_music → suno_get_task
3. Long song: suno_generate_music → suno_extend_music (repeat) → suno_concat_music
4. Consistent voice: suno_generate_music → suno_create_persona → suno_generate_with_persona
5. Custom voice from URL: suno_create_voice → suno_generate_with_persona
6. Your own music: suno_upload_audio → suno_upload_extend or suno_upload_cover
7. Add accompaniment: suno_upload_audio → suno_underpainting
8. Add vocals: suno_upload_audio → suno_overpainting
9. Full stems: suno_all_stems_music → use stems for further production
10. Remix: suno_stems_music → use stems for further production
11. Fix section: suno_replace_section → suno_get_task
"""


@mcp.tool()
async def suno_get_lyric_format_guide() -> str:
    """Get guidance on formatting lyrics for Suno music generation.

    Shows how to structure lyrics with section markers for best results.
    Following this format helps Suno understand the song structure and
    generate appropriate melodies for each section.

    Returns:
        Complete guide with section markers, examples, and tips.
    """
    # Last updated: 2026-04-05
    return """Lyric Format Guide for Suno:

Section Markers (use square brackets):
- [Verse] or [Verse 1], [Verse 2]: Main storytelling sections
- [Chorus]: Repeated catchy section (the hook)
- [Pre-Chorus]: Build-up before chorus
- [Bridge]: Contrasting section, usually near the end
- [Outro]: Ending section
- [Intro]: Opening instrumental or vocals

Example Structure:
```
[Verse 1]
First verse lyrics here
Setting up the story

[Pre-Chorus]
Building anticipation
Leading to the hook

[Chorus]
The main hook goes here
Most memorable part
Repeat this section

[Verse 2]
Second verse continues
The narrative unfolds

[Chorus]
The main hook goes here
Most memorable part
Repeat this section

[Bridge]
Something different here
A twist or climax

[Chorus]
The main hook goes here
Most memorable part
Final repetition

[Outro]
Winding down
Fade out
```

Tips for Best Results:
- Keep lines concise (4-8 words) for better singing flow
- Use simple, clear language that's easy to sing
- Include rhymes for catchiness (especially in chorus)
- Leave some creative freedom for the AI
- Use consistent line lengths within sections
- End verses with a lead-in to the chorus
"""

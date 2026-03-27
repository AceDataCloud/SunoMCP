"""Prompt templates for Suno MCP server.

MCP Prompts provide guidance to LLMs on when and how to use the available tools.
These are exposed via the MCP protocol and help LLMs make better decisions.
"""

from core.server import mcp


@mcp.prompt()
def suno_music_generation_guide() -> str:
    """Guide for choosing the right Suno tool for music generation."""
    return """# Suno Music Generation Guide

When the user wants to generate music, choose the appropriate tool based on their needs:

## Quick Generation (Inspiration Mode)
**Tool:** `suno_generate_music`
**Use when:**
- User gives a simple description: "make me a birthday song"
- User wants Suno to handle lyrics and arrangement
- Quick, low-effort music creation

**Example:** "Create an upbeat pop song about summer"
→ Call `suno_generate_music` with prompt="An upbeat pop song about summer, fun, beach vibes, catchy melody"

## Custom Generation (Full Control)
**Tool:** `suno_generate_custom_music`
**Use when:**
- User provides specific lyrics
- User wants control over title and style
- User specifies vocal gender preference

**Example:** "Here are my lyrics: [Verse] Walking in the rain..."
→ Call `suno_generate_custom_music` with the provided lyrics, a title, and appropriate style

## Extending Songs
**Tool:** `suno_extend_music`
**Use when:**
- User wants to make a song longer
- User wants to add more sections to an existing song
- Building a multi-part composition

**After extending:** Use `suno_concat_music` to merge all segments into one file.

## Creating Covers
**Tool:** `suno_cover_music`
**Use when:**
- User wants a different version of an existing song
- "Make it jazz", "acoustic version", "remix"

## Generating Lyrics Only
**Tool:** `suno_generate_lyrics`
**Use when:**
- User wants lyrics without music yet
- User wants to review/edit lyrics before generating music

## Checking Status
**Tool:** `suno_get_task`
**Use when:**
- Generation takes time and user wants to check if it's ready
- User asks "is my song done?"
- A generation tool returned only a task_id and you need the final audio URLs

## Important Notes:
1. Music generation is async in MCP - generation tools should return quickly with a task_id
2. After any generate/extend/cover/remaster/stems/media conversion call, use `suno_get_task` to poll for the final result
2. Default model is chirp-v4-5 (good balance of quality and speed)
3. For longest songs (8 min), use chirp-v5-5 or chirp-v4-5-plus
4. Vocal gender only works on v4.5+ models
"""


@mcp.prompt()
def suno_workflow_examples() -> str:
    """Common workflow examples for Suno music generation."""
    return """# Suno Workflow Examples

## Workflow 1: Quick Song Generation
1. User: "Make me a rock song about freedom"
2. Call `suno_generate_music(prompt="Rock song about freedom, electric guitars, powerful drums, anthemic")`
3. Return the task_id from the submission response
4. Poll with `suno_get_task(task_id)` until the task finishes and audio URLs appear

## Workflow 2: Custom Song with User's Lyrics
1. User provides lyrics
2. Ask for title and style preferences if not provided
3. Call `suno_generate_custom_music(lyric=user_lyrics, title="...", style="...")`
4. Poll with `suno_get_task(task_id)` for the completed audio

## Workflow 3: Creating a Long Song (>4 minutes)
1. Generate initial song with `suno_generate_music`
2. Get the audio_id from the result
3. Call `suno_extend_music(audio_id, new_lyrics, continue_at=song_duration)`
4. Repeat step 3 as needed
5. Call `suno_concat_music(last_audio_id)` to merge all segments

## Workflow 4: Consistent Voice Across Songs
1. Generate a song the user likes
2. Call `suno_create_persona(audio_id, name="My Voice")`
3. For future songs, use `suno_generate_with_persona(audio_id, persona_id, prompt)`

## Workflow 5: Cover/Remix
1. User has a song_id they want to remix
2. User describes the new style
3. Call `suno_cover_music(audio_id, prompt="jazz version", style="smooth jazz, saxophone")`
4. Poll with `suno_get_task(task_id)` for the completed cover

## Tips:
- Always be descriptive in prompts - include genre, mood, instruments, tempo
- Use style_negative to exclude unwanted elements
- For v4.5+ models, offer vocal_gender option for custom songs
"""


@mcp.prompt()
def suno_style_suggestions() -> str:
    """Style and prompt writing suggestions for Suno."""
    return """# Suno Style Prompt Guide

## Effective Prompt Writing

Good prompts include:
- **Genre:** pop, rock, jazz, classical, electronic, hip-hop, country, R&B, metal, folk
- **Mood:** happy, sad, energetic, calm, dark, uplifting, romantic, aggressive
- **Instruments:** guitar, piano, drums, synthesizer, violin, saxophone, bass
- **Tempo:** slow, mid-tempo, fast, upbeat, ballad
- **Era/Style:** 80s, 90s, modern, vintage, retro, futuristic

## Example Prompts by Genre

**Pop:**
"Catchy pop song, upbeat, synth hooks, danceable, modern production"

**Rock:**
"Hard rock anthem, electric guitars, powerful drums, stadium rock feel"

**Jazz:**
"Smooth jazz, saxophone solo, walking bass, brushed drums, late night vibe"

**Electronic:**
"EDM banger, heavy bass drops, synth arpeggios, festival energy"

**Classical:**
"Orchestral piece, strings, dramatic, cinematic, emotional crescendo"

**Folk:**
"Acoustic folk, fingerpicking guitar, gentle vocals, storytelling"

**Hip-Hop:**
"Trap beat, 808 bass, hi-hats, confident flow, modern hip-hop"

## Style Negative Examples

Use style_negative to exclude:
- "autotune, robotic" - for natural vocals
- "heavy metal, screaming" - for softer songs
- "electronic, synth" - for acoustic sound
- "slow, ballad" - for upbeat songs

## Lyric Section Tips

Each section has a purpose:
- **[Intro]:** Set the mood, can be instrumental
- **[Verse]:** Tell the story, build narrative
- **[Pre-Chorus]:** Build tension before the hook
- **[Chorus]:** The catchiest, most memorable part
- **[Bridge]:** Contrast, often emotional peak
- **[Outro]:** Wind down, resolve the song
"""

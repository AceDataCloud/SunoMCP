"""Audio generation tools for Suno API."""

from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.types import DEFAULT_MODEL, SunoModel, VocalGender
from core.utils import format_audio_result


@mcp.tool()
async def suno_generate_music(
    prompt: Annotated[
        str,
        Field(
            description="Description of the music to generate. Be descriptive about genre, mood, instruments, and theme. Examples: 'A happy birthday song with acoustic guitar', 'Epic orchestral battle music with dramatic choir', 'Chill lo-fi hip hop beat for studying'"
        ),
    ],
    model: Annotated[
        SunoModel,
        Field(
            description="Suno model version. 'chirp-v4-5' is recommended for most use cases. 'chirp-v5-5' offers best quality with 8-minute max duration. Older models (v3, v3-5, v4) have shorter duration limits."
        ),
    ] = DEFAULT_MODEL,
    instrumental: Annotated[
        bool,
        Field(
            description="If true, generate instrumental music without vocals. Default is false (with vocals)."
        ),
    ] = False,
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the audio is generated."
        ),
    ] = None,
) -> str:
    """Generate AI music from a text prompt using Suno's Inspiration Mode.

    This is the simplest way to create music - just describe what you want and Suno
    will automatically generate appropriate lyrics, melody, style, and arrangement.

    Use this when:
    - You want quick music generation with minimal input
    - You don't have specific lyrics in mind
    - You want Suno to be creative with the arrangement

    For full control over lyrics and style, use suno_generate_custom_music instead.

    Returns:
        Task ID and generated audio information including URLs, title, lyrics, and duration.
    """
    result = await client.generate_audio(
        action="generate",
        prompt=prompt,
        model=model,
        instrumental=instrumental,
        callback_url=callback_url,
    )
    return format_audio_result(result)


@mcp.tool()
async def suno_generate_custom_music(
    lyric: Annotated[
        str,
        Field(
            description="Song lyrics with section markers. Use [Verse], [Chorus], [Pre-Chorus], [Bridge], [Outro], [Intro] to structure the song. Example:\n[Verse 1]\nWalking down the empty street\nRain is falling at my feet\n\n[Chorus]\nBut I keep moving on\nUntil the break of dawn"
        ),
    ],
    title: Annotated[
        str,
        Field(description="Title of the song. Keep it concise and memorable."),
    ],
    style: Annotated[
        str,
        Field(
            description="Music style description. Be specific about genre, mood, tempo, and instruments. Examples: 'upbeat pop rock, energetic drums, electric guitar', 'acoustic folk, gentle, fingerpicking', 'dark electronic, synthwave, 80s retro'"
        ),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(
            description="Suno model version. 'chirp-v4-5' or 'chirp-v5-5' recommended for best quality."
        ),
    ] = DEFAULT_MODEL,
    instrumental: Annotated[
        bool,
        Field(
            description="If true, generate instrumental version (lyrics will be ignored). Default is false."
        ),
    ] = False,
    style_negative: Annotated[
        str,
        Field(
            description="Styles to explicitly exclude from the generation. Examples: 'heavy metal, screaming', 'autotune, electronic'"
        ),
    ] = "",
    vocal_gender: Annotated[
        VocalGender,
        Field(
            description="Preferred vocal gender. 'f' for female, 'm' for male, empty string for AI to decide. Only works with v4.5+ models."
        ),
    ] = "",
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the audio is generated."
        ),
    ] = None,
) -> str:
    """Generate AI music with full control over lyrics, title, and style (Custom Mode).

    This gives you complete creative control over the song. You provide the lyrics
    with section markers, and Suno generates the melody and arrangement.

    Use this when:
    - You have specific lyrics you want to use
    - You want precise control over the music style
    - You need a specific song title
    - You want to specify vocal gender (v4.5+ models)

    For quick generation without writing lyrics, use suno_generate_music instead.

    Returns:
        Task ID and generated audio information including URLs, title, lyrics, and duration.
    """
    payload = {
        "action": "generate",
        "custom": True,
        "lyric": lyric,
        "title": title,
        "model": model,
        "instrumental": instrumental,
        "callback_url": callback_url,
    }

    if style:
        payload["style"] = style
    if style_negative:
        payload["style_negative"] = style_negative
    if vocal_gender and vocal_gender in ("f", "m"):
        payload["vocal_gender"] = vocal_gender

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_extend_music(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the audio to extend. This is the 'id' field from a previous generation result."
        ),
    ],
    lyric: Annotated[
        str,
        Field(
            description="Lyrics for the extended section. Use section markers like [Verse], [Chorus], [Bridge], [Outro]. The extension will continue from where the original song left off."
        ),
    ],
    continue_at: Annotated[
        float,
        Field(
            description="Timestamp in seconds where to start the extension. For example, 120.5 means continue from 2 minutes and 0.5 seconds into the song."
        ),
    ],
    style: Annotated[
        str,
        Field(
            description="Music style for the extension. Leave empty to maintain the original style, or specify to change the style mid-song."
        ),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(description="Model version to use for the extension."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the extension is complete."
        ),
    ] = None,
) -> str:
    """Extend an existing song from a specific timestamp with new lyrics.

    This allows you to continue a previously generated song, adding new sections
    like additional verses, a bridge, or an outro.

    Use this when:
    - A generated song is too short and you want to add more
    - You want to add a bridge or outro to an existing song
    - You're building a longer song piece by piece

    After extending multiple times, use suno_concat_music to merge all segments.

    Returns:
        Task ID and the extended audio information.
    """
    payload = {
        "action": "extend",
        "audio_id": audio_id,
        "lyric": lyric,
        "continue_at": continue_at,
        "custom": True,
        "model": model,
        "callback_url": callback_url,
    }

    if style:
        payload["style"] = style

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_cover_music(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the audio to create a cover of. This is the 'id' field from a previous generation."
        ),
    ],
    prompt: Annotated[
        str,
        Field(
            description="Description of how you want the cover to sound. Examples: 'acoustic unplugged version', 'jazz lounge style', '80s synthwave remix'"
        ),
    ] = "",
    style: Annotated[
        str,
        Field(
            description="Target music style for the cover. Examples: 'jazz, smooth, saxophone', 'acoustic folk, gentle guitar', 'electronic dance, high energy'"
        ),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(description="Model version to use for the cover."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the cover is complete."
        ),
    ] = None,
) -> str:
    """Create a cover or remix version of an existing song in a different style.

    This generates a new version of a song with a different arrangement, genre,
    or mood while keeping the core melody and lyrics.

    Use this when:
    - You want to hear a song in a different genre
    - You want an acoustic/unplugged version of an electronic song
    - You want to remix a song with a different vibe

    Returns:
        Task ID and the cover audio information.
    """
    payload = {
        "action": "cover",
        "audio_id": audio_id,
        "model": model,
        "callback_url": callback_url,
    }

    if prompt:
        payload["prompt"] = prompt
    if style:
        payload["style"] = style

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_concat_music(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the LAST segment of an extended song chain. Suno will automatically find and merge all connected segments."
        ),
    ],
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the concatenation is complete."
        ),
    ] = None,
) -> str:
    """Concatenate extended song segments into a single complete audio file.

    After extending a song multiple times with suno_extend_music, use this tool
    to merge all the segments into one continuous audio file.

    Use this when:
    - You've extended a song one or more times
    - You want a single audio file instead of multiple segments
    - You're ready to finalize a long-form composition

    Returns:
        Task ID and the concatenated audio information with the full song.
    """
    result = await client.generate_audio(
        action="concat",
        audio_id=audio_id,
        callback_url=callback_url,
    )
    return format_audio_result(result)


@mcp.tool()
async def suno_generate_with_persona(
    audio_id: Annotated[
        str,
        Field(description="ID of a reference audio to base the generation on."),
    ],
    persona_id: Annotated[
        str,
        Field(
            description="ID of the persona to use. Get this from suno_create_persona tool. The persona defines the vocal style and characteristics."
        ),
    ],
    prompt: Annotated[
        str,
        Field(
            description="Description of the music to generate. The persona's voice will be applied to this new song."
        ),
    ],
    model: Annotated[
        SunoModel,
        Field(description="Model version to use."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(
            description="Webhook callback URL for asynchronous notifications. When provided, the API will call this URL when the audio is generated."
        ),
    ] = None,
) -> str:
    """Generate music using a saved artist persona for consistent vocal style.

    This allows you to maintain a consistent voice/singing style across multiple
    songs by using a previously saved persona.

    Use this when:
    - You want multiple songs with the same vocal style
    - You're creating an album or series with consistent vocals
    - You found a voice you like and want to reuse it

    First create a persona with suno_create_persona, then use its ID here.

    Returns:
        Task ID and generated audio information with the persona's voice applied.
    """
    result = await client.generate_audio(
        action="artist_consistency",
        audio_id=audio_id,
        persona_id=persona_id,
        prompt=prompt,
        model=model,
        callback_url=callback_url,
    )
    return format_audio_result(result)


@mcp.tool()
async def suno_remaster_music(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the audio to remaster. This is the 'id' field from a previous generation."
        ),
    ],
    model: Annotated[
        SunoModel,
        Field(
            description="Model version to use for remastering. Newer models produce better results."
        ),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Remaster an existing song to improve audio quality.

    Takes a previously generated song and applies audio remastering to enhance
    clarity, dynamics, and overall sound quality.

    Use this when:
    - You want to improve the audio quality of a generated song
    - You want a song generated with an older model to sound better
    - You need a polished, production-ready version

    Returns:
        Task ID and the remastered audio information.
    """
    result = await client.generate_audio(
        action="remaster",
        audio_id=audio_id,
        model=model,
        callback_url=callback_url,
    )
    return format_audio_result(result)


@mcp.tool()
async def suno_stems_music(
    audio_id: Annotated[
        str,
        Field(description="ID of the audio to separate into stems."),
    ],
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Separate a song into individual stems (vocals and instruments).

    Splits the audio into separate tracks for vocals and instrumentals,
    useful for remixing, karaoke, or isolating specific parts.

    Use this when:
    - You want to separate vocals from instrumentals
    - You need individual stem tracks for mixing
    - You want to create a karaoke version

    Returns:
        Task ID and stem separation results with individual track URLs.
    """
    result = await client.generate_audio(
        action="stems",
        audio_id=audio_id,
        callback_url=callback_url,
    )
    return format_audio_result(result)


@mcp.tool()
async def suno_replace_section(
    audio_id: Annotated[
        str,
        Field(description="ID of the audio to replace a section in."),
    ],
    replace_section_start: Annotated[
        float,
        Field(description="Start time in seconds of the section to replace."),
    ],
    replace_section_end: Annotated[
        float,
        Field(description="End time in seconds of the section to replace."),
    ],
    lyric: Annotated[
        str | None,
        Field(
            description="New lyrics for the replaced section. Use section markers like [Verse], [Chorus]."
        ),
    ] = None,
    style: Annotated[
        str,
        Field(description="Music style for the replaced section."),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(description="Model version to use."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Replace a specific time range in a song with new generated content.

    Re-generates a portion of a song between the specified start and end times,
    keeping the rest of the song unchanged. Great for fixing sections you don't like.

    Use this when:
    - A specific section of a song needs improvement
    - You want to change lyrics in the middle of a song
    - You want to replace a verse or chorus with something different

    Returns:
        Task ID and the updated audio information.
    """
    payload: dict = {
        "action": "replace_section",
        "audio_id": audio_id,
        "replace_section_start": replace_section_start,
        "replace_section_end": replace_section_end,
        "model": model,
        "callback_url": callback_url,
    }

    if lyric:
        payload["lyric"] = lyric
        payload["custom"] = True
    if style:
        payload["style"] = style

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_upload_extend(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the uploaded audio to extend. Must be an audio uploaded via suno_upload_audio."
        ),
    ],
    lyric: Annotated[
        str,
        Field(description="Lyrics for the extension section."),
    ],
    continue_at: Annotated[
        float,
        Field(description="Timestamp in seconds where to start the extension."),
    ],
    style: Annotated[
        str,
        Field(description="Music style for the extension."),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(description="Model version to use."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Extend an uploaded audio (your own music) with new AI-generated content.

    Similar to suno_extend_music but works with audio you uploaded via
    suno_upload_audio. Allows you to add new sections to your own music.

    Use this when:
    - You uploaded your own music and want to extend it
    - You want to add AI-generated sections to your existing recordings

    Returns:
        Task ID and the extended audio information.
    """
    payload: dict = {
        "action": "upload_extend",
        "audio_id": audio_id,
        "lyric": lyric,
        "continue_at": continue_at,
        "custom": True,
        "model": model,
        "callback_url": callback_url,
    }

    if style:
        payload["style"] = style

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_upload_cover(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the uploaded audio to create a cover of. Must be an audio uploaded via suno_upload_audio."
        ),
    ],
    style: Annotated[
        str,
        Field(description="Target music style for the cover."),
    ] = "",
    model: Annotated[
        SunoModel,
        Field(description="Model version to use."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Create an AI cover of an uploaded audio (your own music).

    Similar to suno_cover_music but works with audio you uploaded via
    suno_upload_audio. Re-arranges your music in a different style.

    Use this when:
    - You uploaded your own music and want a cover in a different style
    - You want to hear your song re-interpreted by AI

    Returns:
        Task ID and the cover audio information.
    """
    payload: dict = {
        "action": "upload_cover",
        "audio_id": audio_id,
        "model": model,
        "callback_url": callback_url,
    }

    if style:
        payload["style"] = style

    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_mashup_music(
    mashup_audio_ids: Annotated[
        list[str],
        Field(description="List of audio IDs to mashup together. Provide 2 or more song IDs."),
    ],
    model: Annotated[
        SunoModel,
        Field(description="Model version to use."),
    ] = DEFAULT_MODEL,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Create a musical mashup by blending multiple songs together.

    Combines elements from multiple generated songs into a single cohesive
    mashup track. Different from lyrics mashup - this blends the actual audio.

    Use this when:
    - You want to blend two or more songs together musically
    - You're creating a DJ-style mashup
    - You want to combine melodies from different songs

    Returns:
        Task ID and the mashup audio information.
    """
    result = await client.generate_audio(
        action="mashup",
        mashup_audio_ids=mashup_audio_ids,
        model=model,
        callback_url=callback_url,
    )
    return format_audio_result(result)

"""Style and mashup tools for Suno API."""

import json
from typing import Annotated, Any, Literal

from pydantic import Field

from core.client import client
from core.server import mcp


@mcp.tool()
async def suno_optimize_style(
    prompt: Annotated[
        str,
        Field(
            description="Style prompt words that need to be optimized. Examples: 'rock guitar', 'jazz smooth', 'electronic dance party'"
        ),
    ],
) -> str:
    """Optimize a music style description for better generation results.

    Takes a rough style description and refines it into an optimized style
    prompt that Suno can better understand and produce higher quality music for.

    Use this when:
    - You have a vague style idea and want to refine it
    - You want better style prompts for suno_generate_custom_music
    - You need suggestions for style terms

    Returns:
        Optimized style description ready for use in music generation.
    """
    result = await client.get_style(prompt=prompt)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_mashup_lyrics(
    lyrics_a: Annotated[
        str,
        Field(
            description="The first set of lyrics to combine. Can be full song lyrics with section markers."
        ),
    ],
    lyrics_b: Annotated[
        str,
        Field(
            description="The second set of lyrics to combine. Can be full song lyrics with section markers."
        ),
    ],
) -> str:
    """Generate mashup lyrics by combining two sets of lyrics.

    Takes two different song lyrics and intelligently combines them into
    a cohesive mashup. Great for creating unique lyrical combinations.

    Use this when:
    - You want to blend two songs' lyrics together
    - You're creating a mashup or medley
    - You want creative lyrical combinations from two sources

    Returns:
        Combined mashup lyrics ready for use in music generation.
    """
    result = await client.mashup_lyrics(lyrics_a=lyrics_a, lyrics_b=lyrics_b)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_upload_audio(
    audio_url: Annotated[
        str,
        Field(
            description="Public URL of the audio file. Enhanced mode requires HTTPS and audio you own or are authorized to use."
        ),
    ],
    mode: Annotated[
        Literal["standard", "enhanced"],
        Field(
            description="Upload mode. standard preserves normal upload behavior; enhanced handles some authorized audio that standard mode cannot process, costs 1.87 Credits on success, and runs asynchronously."
        ),
    ] = "standard",
    name: Annotated[
        str | None,
        Field(description="Audio name, required for enhanced mode and limited to 100 characters."),
    ] = None,
    callback_url: Annotated[
        str | None,
        Field(description="Optional HTTPS webhook URL for the enhanced upload result."),
    ] = None,
) -> str:
    """Upload external audio for use in subsequent operations.

    Use standard mode for normal uploads. Use enhanced mode only when standard
    upload cannot process authorized audio; it returns a task_id for suno_get_task.
    Enhanced audio IDs support Cover, Samples, and Mashup.
    """
    if mode == "enhanced" and not name:
        raise ValueError("name is required when mode=enhanced")
    payload: dict[str, Any] = {"audio_url": audio_url}
    if mode == "enhanced":
        payload["mode"] = mode
    if name:
        payload["name"] = name
    if callback_url:
        payload["callback_url"] = callback_url
    result = await client.upload_audio(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_create_voice(
    audio_url: Annotated[
        str,
        Field(
            description="Publicly accessible URL of the audio file to create a voice from. Must be MP3 or WAV format, at least 10 seconds long, containing clear vocals from a single speaker without background noise or music."
        ),
    ],
    name: Annotated[
        str | None,
        Field(description="Optional name for the custom voice persona."),
    ] = None,
    description: Annotated[
        str | None,
        Field(description="Description of the custom voice persona (optional)."),
    ] = None,
) -> str:
    """Create a custom voice persona from an external audio URL.

    Creates a voice persona directly from a publicly accessible audio URL
    (MP3 or WAV format). The audio must contain clear vocals from a single
    speaker and be at least 10 seconds long.

    This is different from suno_create_persona which creates a persona from
    a previously generated Suno audio. Use this to create a persona from
    your own voice recordings or external audio files.

    Use this when:
    - You have an external audio file with clear vocals
    - You want to create a voice persona from your own recordings
    - You want to use a specific real-world voice as a persona

    Returns:
        Persona ID that can be used with suno_generate_with_persona tool.
    """
    payload: dict = {
        "audio_url": audio_url,
    }
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description

    result = await client.create_voice(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)

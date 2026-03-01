"""Style and mashup tools for Suno API."""

import json
from typing import Annotated

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
            description="Public URL of the audio file to upload. The URL must be directly accessible (CDN link, cloud storage URL, etc.)."
        ),
    ],
) -> str:
    """Upload an external audio file to Suno for use in subsequent operations.

    Uploads audio from a URL so it can be used with actions like upload_extend
    and upload_cover, which allow you to extend or create covers of your own music.

    Use this when:
    - You have your own music you want to extend/cover with Suno
    - You want to use an external audio as a base for Suno operations
    - You need to import audio into Suno's system

    After uploading, use the returned audio_id with suno_upload_extend or
    suno_upload_cover actions.

    Returns:
        Upload result with audio ID for use in subsequent operations.
    """
    result = await client.upload_audio(audio_url=audio_url)
    return json.dumps(result, ensure_ascii=False, indent=2)

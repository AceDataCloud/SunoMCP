"""Lyrics generation tools for Suno API."""

from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.types import DEFAULT_LYRICS_MODEL, LyricsModel
from core.utils import format_lyrics_result


@mcp.tool()
async def suno_generate_lyrics(
    prompt: Annotated[
        str,
        Field(
            description="Description of the lyrics you want. Include theme, mood, genre, and any specific elements. Examples: 'A romantic ballad about lost love and rainy nights', 'An upbeat pop song about summer vacation', 'A motivational hip-hop track about overcoming obstacles'"
        ),
    ],
    model: Annotated[
        LyricsModel,
        Field(
            description="Model version for lyrics generation. 'default' works well for most lyrics. 'remi-v1' offers an alternative style."
        ),
    ] = DEFAULT_LYRICS_MODEL,
) -> str:
    """Generate song lyrics from a text prompt.

    Creates structured lyrics with proper song sections (Verse, Chorus, Bridge, etc.)
    based on your description. The generated lyrics are formatted and ready to use
    with suno_generate_custom_music.

    Use this when:
    - You need lyrics but don't want to write them yourself
    - You want AI-generated lyrics for a specific theme or mood
    - You need properly structured lyrics with section markers

    The output includes section markers like [Verse], [Chorus], [Bridge] that
    Suno's music generation understands.

    Returns:
        Generated lyrics with title, status, and formatted text with section markers.
    """
    result = await client.generate_lyrics(
        prompt=prompt,
        model=model,
    )
    return format_lyrics_result(result)

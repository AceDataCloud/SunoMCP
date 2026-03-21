"""Media conversion and extraction tools for Suno API."""

import json
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_audio_result


@mcp.tool()
async def suno_get_mp4(
    audio_id: Annotated[
        str,
        Field(
            description="The song ID to get the MP4 video for. This is the 'id' field from a previous audio generation result."
        ),
    ],
) -> str:
    """Get an MP4 video version of a generated song.

    Converts a generated audio into an MP4 video file with visualizations.
    Useful for sharing on social media or video platforms.

    Use this when:
    - You want a video version of a generated song
    - You need to share the song on video platforms
    - You want a visual representation of the audio

    Returns:
        Task ID and MP4 video information.
    """
    result = await client.get_mp4(audio_id=audio_id)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_timing(
    audio_id: Annotated[
        str,
        Field(description="The song ID to get timing/subtitle data for."),
    ],
) -> str:
    """Get timing and subtitle data for a generated song.

    Returns word-level timing information that can be used for
    synchronized lyrics display, karaoke, or subtitle generation.

    Use this when:
    - You need synchronized lyrics/subtitles
    - You want to create karaoke-style displays
    - You need word-level timing for video editing

    Returns:
        Timing data with word-level timestamps.
    """
    result = await client.get_timing(audio_id=audio_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_extract_vocals(
    audio_id: Annotated[
        str,
        Field(description="The song ID to extract vocals from."),
    ],
    vocal_start: Annotated[
        float | None,
        Field(description="Start time in seconds for the vocal extraction range."),
    ] = None,
    vocal_end: Annotated[
        float | None,
        Field(description="End time in seconds for the vocal extraction range."),
    ] = None,
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Extract the vocal track from a generated song (stem separation).

    Isolates the vocals from a song, removing instrumental background.
    Useful for remixing, creating acapella versions, or persona creation.

    Use this when:
    - You want an isolated vocal track
    - You need vocals for a remix or mashup
    - You want to create a persona from specific vocal segments

    Returns:
        Task ID and extracted vocal audio information.
    """
    payload: dict = {"audio_id": audio_id}
    if vocal_start is not None:
        payload["vocal_start"] = vocal_start
    if vocal_end is not None:
        payload["vocal_end"] = vocal_end
    if callback_url:
        payload["callback_url"] = callback_url

    result = await client.get_vox(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_wav(
    audio_id: Annotated[
        str,
        Field(description="The song ID to get the WAV format for."),
    ],
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Get the lossless WAV format of a generated song.

    Converts the song to high-quality uncompressed WAV format.
    WAV files are larger but have no quality loss compared to MP3.

    Use this when:
    - You need a lossless audio format for production
    - You want the highest quality audio output
    - You need uncompressed audio for further processing

    Returns:
        Task ID and WAV audio information.
    """
    payload: dict = {"audio_id": audio_id}
    if callback_url:
        payload["callback_url"] = callback_url

    result = await client.get_wav(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_midi(
    audio_id: Annotated[
        str,
        Field(description="The song ID to get MIDI data for."),
    ],
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for asynchronous notifications."),
    ] = None,
) -> str:
    """Get MIDI data extracted from a generated song.

    Converts the song's melodic and rhythmic information into MIDI format,
    which can be used in digital audio workstations (DAWs) for further editing.

    Use this when:
    - You want to edit the melody in a DAW
    - You need note-level data from the song
    - You want to recreate the song with different instruments

    Returns:
        Task ID and MIDI data information.
    """
    payload: dict = {"audio_id": audio_id}
    if callback_url:
        payload["callback_url"] = callback_url

    result = await client.get_midi(**payload)
    return format_audio_result(result)

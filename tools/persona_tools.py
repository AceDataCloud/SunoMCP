"""Persona management tools for Suno API."""

import json
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_persona_result


@mcp.tool()
async def suno_create_persona(
    audio_id: Annotated[
        str,
        Field(
            description="ID of the audio to use as the persona reference. This should be a previously generated song whose vocal style you want to save and reuse."
        ),
    ],
    name: Annotated[
        str,
        Field(
            description="Name for this persona. Use a descriptive name that helps you remember the voice style. Examples: 'My Rock Voice', 'Soft Female Singer', 'Deep Male Baritone', 'Energetic Pop Vocalist'"
        ),
    ],
    vox_audio_id: Annotated[
        str | None,
        Field(
            description="Optional audio ID used to generate a new singer's style by combining with the main audio. Useful for creating hybrid vocal personas."
        ),
    ] = None,
    vocal_start: Annotated[
        float | None,
        Field(
            description="Start time in seconds of the vocal segment to use from the audio. Useful for isolating a specific vocal section."
        ),
    ] = None,
    vocal_end: Annotated[
        float | None,
        Field(description="End time in seconds of the vocal segment to use from the audio."),
    ] = None,
    description: Annotated[
        str | None,
        Field(
            description="Description of the singer's style. Examples: 'Warm and breathy female voice with jazz influences', 'Powerful male rock vocalist with raspy tone'"
        ),
    ] = None,
) -> str:
    """Create a new artist persona from an existing audio's vocal style.

    This saves the vocal characteristics from a generated song so you can reuse
    that same voice style in future generations. Great for maintaining consistency
    across multiple songs.

    Use this when:
    - You generated a song and love the voice
    - You want to create multiple songs with the same vocalist
    - You're building an album with consistent vocal style
    - You want to save a unique voice for future use

    After creating a persona, use suno_generate_with_persona with the returned
    persona_id to generate new songs with that voice.

    Returns:
        Persona ID that can be used with suno_generate_with_persona tool.
    """
    payload: dict = {
        "audio_id": audio_id,
        "name": name,
    }

    if vox_audio_id:
        payload["vox_audio_id"] = vox_audio_id
    if vocal_start is not None:
        payload["vocal_start"] = vocal_start
    if vocal_end is not None:
        payload["vocal_end"] = vocal_end
    if description:
        payload["description"] = description

    result = await client.create_persona(**payload)
    return format_persona_result(result)


@mcp.tool()
async def suno_list_personas(
    user_id: Annotated[
        str,
        Field(description="The user ID to list personas for."),
    ],
    limit: Annotated[
        int,
        Field(description="Maximum number of personas to return. Default is 50."),
    ] = 50,
    offset: Annotated[
        int,
        Field(description="Number of personas to skip for pagination. Default is 0."),
    ] = 0,
) -> str:
    """List all saved artist personas for a user.

    Returns all personas previously created with suno_create_persona or
    suno_create_voice for the given user.

    Use this when:
    - You want to see all available voice personas
    - You need to find a persona ID to use in music generation
    - You want to manage your saved vocal styles

    Returns:
        List of personas with their IDs, names, and descriptions.
    """
    result = await client.list_personas(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_delete_persona(
    persona_id: Annotated[
        str,
        Field(description="The persona ID to delete."),
    ],
    user_id: Annotated[
        str | None,
        Field(description="The user ID for ownership verification (optional)."),
    ] = None,
) -> str:
    """Delete a saved artist persona.

    Permanently removes a previously created persona. This action cannot be undone.

    Use this when:
    - You want to remove an unused voice persona
    - You need to clean up old personas
    - You want to delete a persona you no longer need

    Returns:
        Confirmation of the deletion.
    """
    payload: dict = {"persona_id": persona_id}
    if user_id:
        payload["user_id"] = user_id

    result = await client.delete_persona(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)

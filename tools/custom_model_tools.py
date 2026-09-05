"""Custom music model tools for Suno API."""

import json
from typing import Annotated, Literal

from pydantic import Field

from core.client import client
from core.server import mcp


@mcp.tool()
async def suno_create_custom_model(
    name: Annotated[
        str,
        Field(description="Name for the custom music model."),
    ],
    audio_urls: Annotated[
        list[str],
        Field(
            min_length=6,
            max_length=24,
            description="6 to 24 authorized audio URLs used to train the custom music model.",
        ),
    ],
    callback_url: Annotated[
        str | None,
        Field(description="Webhook callback URL for custom model creation status."),
    ] = None,
    idempotency_key: Annotated[
        str | None,
        Field(description="Optional Idempotency-Key header value for safe retries."),
    ] = None,
) -> str:
    """Create a reusable custom music model from authorized audio examples.

    This is a paid, long-running operation. Call it only after the user confirms
    the source files and the 5.6-Credit list price.
    """
    payload: dict = {
        "action": "create",
        "name": name,
        "audio_urls": audio_urls,
    }
    if callback_url:
        payload["callback_url"] = callback_url

    result = await client.custom_models(idempotency_key=idempotency_key, **payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_get_custom_model(
    model_id: Annotated[
        str,
        Field(description="ID of the custom music model to retrieve.", alias="id"),
    ],
) -> str:
    """Retrieve a single custom music model by ID."""
    result = await client.custom_models(action="retrieve", id=model_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_list_custom_models(
    limit: Annotated[
        int,
        Field(description="Maximum number of custom models to return."),
    ] = 20,
    offset: Annotated[
        int,
        Field(description="Number of custom models to skip for pagination."),
    ] = 0,
    status: Annotated[
        Literal["queued", "uploading", "training", "ready", "failed", "archived"] | None,
        Field(description="Optional status filter for custom models."),
    ] = None,
) -> str:
    """List custom music models for the current Suno application."""
    payload: dict = {
        "action": "retrieve_batch",
        "limit": limit,
        "offset": offset,
    }
    if status:
        payload["status"] = status

    result = await client.custom_models(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_generate_with_custom_model(
    model_id: Annotated[
        str,
        Field(description="Ready custom music model ID to generate with.", alias="id"),
    ],
    title: Annotated[
        str,
        Field(description="Title for the generated song."),
    ],
    lyric: Annotated[
        str,
        Field(description="Lyrics for the generated song."),
    ],
    style: Annotated[
        str,
        Field(description="Music style for the generated song."),
    ],
) -> str:
    """Generate a song using a ready custom music model.

    The initial response only accepts the async task. Poll it until success or
    failure; this operation never falls back to another model.
    """
    result = await client.custom_models(
        action="generate",
        id=model_id,
        title=title,
        lyric=lyric,
        style=style,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_archive_custom_model(
    model_id: Annotated[
        str,
        Field(description="ID of the custom music model to archive.", alias="id"),
    ],
) -> str:
    """Archive a custom music model so it can no longer be used.

    Archiving does not guarantee that model capacity is released.
    """
    result = await client.custom_models(action="delete", id=model_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

"""Task query tools for Suno API."""

import asyncio
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_task_result


@mcp.tool()
async def suno_get_task(
    task_id: Annotated[
        str,
        Field(
            description="The task ID returned from a generation request. This is the 'task_id' field from any suno_generate_*, suno_extend_*, suno_cover_*, or suno_concat_* tool response."
        ),
    ],
) -> str:
    """Query the status and result of a music generation task.

    Use this to check if a generation is complete and retrieve the resulting
    audio URLs, titles, lyrics, and other metadata.

    Use this when:
    - You want to check if a generation has completed
    - You need to retrieve audio URLs from a previous generation
    - You want to get the full details of a generated song

    Task states:
    - 'pending': Generation is still in progress — KEEP POLLING
    - 'processing': Generation is being processed — KEEP POLLING
    - 'complete': Generation finished successfully — this is the ONLY state that means done
    - 'failed': Generation failed (check error message)

    CRITICAL: During the 'pending' state, the response may already contain intermediate
    audio_url values (e.g. URLs from audiopipe.suno.ai). These are STREAMING PREVIEW URLs,
    NOT final results. You MUST check the 'state' field — only present the results to the
    user when state is 'complete' and success is true. Do NOT stop polling just because
    audio_url is non-empty.

    Returns:
        Task status and generated audio information including URLs, title, lyrics, and task timing metadata.
    """
    result = await client.query_task(
        id=task_id,
        action="retrieve",
    )
    # Throttle polling: sleep 5s for incomplete tasks so LLM clients
    # don't burn through poll attempts in seconds.
    response = result.get("response", {})
    is_complete = response.get("success", False)
    is_failed = response.get("success") is False or str(result.get("state", "")).lower() in {
        "failed",
        "error",
        "cancelled",
        "canceled",
    }
    if not is_complete and not is_failed:
        await asyncio.sleep(5)
    return format_task_result(result)


@mcp.tool()
async def suno_get_tasks_batch(
    task_ids: Annotated[
        list[str],
        Field(description="List of task IDs to query. Maximum recommended batch size is 50 tasks."),
    ],
) -> str:
    """Query multiple music generation tasks at once.

    Efficiently check the status of multiple tasks in a single request.
    More efficient than calling suno_get_task multiple times.

    Use this when:
    - You have multiple pending generations to check
    - You want to get status of several songs at once
    - You're tracking a batch of generations

    CRITICAL: Same as suno_get_task — only consider a task complete when its state
    is 'complete' and success is true. Intermediate audio_url values during 'pending'
    state are streaming previews, NOT final results.

    Returns:
        Status and audio information for all queried tasks.
    """
    result = await client.query_task(
        ids=task_ids,
        action="retrieve_batch",
    )

    if "error" in result:
        error = result.get("error", {})
        return f"Error: {error.get('code', 'unknown')} - {error.get('message', 'Unknown error')}"

    lines = [f"Total Tasks: {result.get('count', 0)}", ""]

    for item in result.get("items", []):
        response_info = item.get("response", {})
        state = item.get("state", "")
        success = response_info.get("success", False)
        is_failed = response_info.get("success") is False or str(state).lower() in {
            "failed",
            "error",
            "cancelled",
            "canceled",
        }
        effective_state = state or ("failed" if is_failed else "pending")
        lines.extend(
            [
                f"=== Task: {item.get('id', 'N/A')} ===",
                f"State: {effective_state}",
                f"Created At: {item.get('created_at', 'N/A')}",
                f"Success: {success}",
            ]
        )

        if state == "complete" and success:
            for audio in response_info.get("data", []):
                lines.append(
                    f"  - {audio.get('title', 'Untitled')}: {audio.get('audio_url', 'N/A')}"
                )
        elif is_failed:
            lines.append(f"  Error: {response_info.get('error', 'Unknown error')}")
        else:
            lines.append(
                f"  ⏳ Still {effective_state} — keep polling. Any audio_url values are intermediate previews."
            )

        lines.append("")

    return "\n".join(lines)

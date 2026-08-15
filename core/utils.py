"""Utility functions for MCP Suno server."""

import json
from typing import Any


def _with_submission_guidance(
    data: dict[str, Any], poll_tool: str, batch_poll_tool: str | None = None
) -> dict[str, Any]:
    """Attach MCP polling guidance to async submission responses."""
    payload = dict(data)
    task_id = payload.get("task_id")
    if not task_id:
        return payload

    payload["mcp_async_submission"] = {
        "task_id": task_id,
        "poll_tool": poll_tool,
        "batch_poll_tool": batch_poll_tool,
        "recommended_action": "poll",
        "should_poll": True,
        "terminal_state_reached": False,
        "polling_interval_seconds": 15,
        "max_poll_attempts": 100,
        "expected_wait_seconds": 600,
        "next_step": (
            f'Call {poll_tool}(task_id="{task_id}") to poll until the task completes '
            f"and the final media URLs are available. "
            f"IMPORTANT: Media generation typically takes 1-5 minutes. "
            f"Wait at least 15 seconds between each poll. "
            f"Keep polling for up to 100 attempts. Do NOT stop early — the task is still running."
        ),
    }
    return payload


def _with_task_guidance(
    data: dict[str, Any], poll_tool: str, batch_poll_tool: str | None = None
) -> dict[str, Any]:
    """Attach MCP polling guidance to task lookup responses."""
    payload = dict(data)
    task_id = payload.get("id") or payload.get("task_id")
    if not task_id:
        return payload

    # Determine task state for explicit guidance
    state = payload.get("state", "")
    response = payload.get("response", {})
    success = response.get("success", False) if isinstance(response, dict) else False
    response_failed = isinstance(response, dict) and response.get("success") is False

    if success:
        payload["mcp_task_polling"] = {
            "task_id": task_id,
            "state": "complete",
            "is_complete": True,
            "is_failed": False,
            "should_poll": False,
            "terminal_state_reached": True,
            "recommended_action": "stop",
            "note": "Task is complete. The audio URLs are final and ready to present to the user.",
        }
    else:
        is_failed = response_failed or str(state).lower() in {
            "failed",
            "error",
            "cancelled",
            "canceled",
        }
        effective_state = state or ("failed" if is_failed else "pending")
        payload["mcp_task_polling"] = {
            "task_id": task_id,
            "poll_tool": poll_tool,
            "batch_poll_tool": batch_poll_tool,
            "state": effective_state,
            "is_complete": False,
            "is_failed": is_failed,
            "should_poll": not is_failed,
            "terminal_state_reached": is_failed,
            "recommended_action": "stop" if is_failed else "poll",
            "polling_interval_seconds": 15,
            "max_poll_attempts": 100,
            "next_step": (
                "Task failed. Inspect response.error for details and do not poll again."
                if is_failed
                else (
                    f'Task is NOT complete yet (state: "{effective_state}"). '
                    f'IMPORTANT: Only state="complete" with success=true means the task is finished. '
                    f"Ignore any intermediate audio_url values — these are streaming previews, NOT final results. "
                    f'Wait 15 seconds, then call {poll_tool}(task_id="{task_id}") again. '
                    f"Media generation typically takes 1-5 minutes. Keep polling for up to 100 attempts."
                )
            ),
        }
    return payload


def format_audio_result(data: dict[str, Any]) -> str:
    """Format audio generation result as JSON.

    Args:
        data: API response dictionary

    Returns:
        JSON string representation of the result
    """
    return json.dumps(
        _with_submission_guidance(data, "suno_get_task", "suno_get_tasks_batch"),
        ensure_ascii=False,
        indent=2,
    )


def format_lyrics_result(data: dict[str, Any]) -> str:
    """Format lyrics generation result as JSON.

    Args:
        data: API response dictionary

    Returns:
        JSON string representation of the result
    """
    return json.dumps(
        _with_submission_guidance(data, "suno_get_task", "suno_get_tasks_batch"),
        ensure_ascii=False,
        indent=2,
    )


def format_task_result(data: dict[str, Any]) -> str:
    """Format task query result as JSON.

    Args:
        data: API response dictionary

    Returns:
        JSON string representation of the result
    """
    return json.dumps(
        _with_task_guidance(data, "suno_get_task", "suno_get_tasks_batch"),
        ensure_ascii=False,
        indent=2,
    )


def format_persona_result(data: dict[str, Any]) -> str:
    """Format persona creation result as JSON.

    Args:
        data: API response dictionary

    Returns:
        JSON string representation of the result
    """
    return json.dumps(
        _with_submission_guidance(data, "suno_get_task", "suno_get_tasks_batch"),
        ensure_ascii=False,
        indent=2,
    )

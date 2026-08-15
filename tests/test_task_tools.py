"""Unit tests for task tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.task_tools import suno_get_task, suno_get_tasks_batch


class TestGetTaskTool:
    @pytest.mark.asyncio
    async def test_success_response_without_state_does_not_sleep(self):
        task = {
            "id": "complete-task",
            "state": "",
            "response": {"success": True, "data": [{"id": "audio-1"}]},
        }
        with (
            patch("tools.task_tools.client.query_task", new=AsyncMock(return_value=task)),
            patch("tools.task_tools.asyncio.sleep", new=AsyncMock()) as mock_sleep,
        ):
            result = await suno_get_task(task_id="complete-task")

        mock_sleep.assert_not_awaited()
        assert '"state": "complete"' in result
        assert '"should_poll": false' in result

    @pytest.mark.asyncio
    async def test_failed_response_does_not_sleep(self):
        task = {
            "id": "failed-task",
            "state": "",
            "response": {
                "success": False,
                "error": {"code": "bad_request", "message": "prompt is required"},
            },
        }
        with (
            patch("tools.task_tools.client.query_task", new=AsyncMock(return_value=task)),
            patch("tools.task_tools.asyncio.sleep", new=AsyncMock()) as mock_sleep,
        ):
            result = await suno_get_task(task_id="failed-task")

        mock_sleep.assert_not_awaited()
        assert '"state": "failed"' in result
        assert '"should_poll": false' in result

    @pytest.mark.asyncio
    async def test_batch_marks_response_success_as_complete(self):
        response = {
            "count": 1,
            "items": [
                {
                    "id": "complete-task",
                    "state": "",
                    "response": {
                        "success": True,
                        "data": [{"title": "Done", "audio_url": "https://example.com/a.mp3"}],
                    },
                }
            ],
        }
        with patch(
            "tools.task_tools.client.query_task",
            new=AsyncMock(return_value=response),
        ):
            result = await suno_get_tasks_batch(task_ids=["complete-task"])

        assert "State: complete" in result
        assert "Done: https://example.com/a.mp3" in result
        assert "keep polling" not in result

    @pytest.mark.asyncio
    async def test_batch_marks_response_error_as_failed(self):
        response = {
            "count": 1,
            "items": [
                {
                    "id": "failed-task",
                    "state": "",
                    "response": {
                        "success": False,
                        "error": {"code": "bad_request", "message": "prompt is required"},
                    },
                }
            ],
        }
        with patch(
            "tools.task_tools.client.query_task",
            new=AsyncMock(return_value=response),
        ):
            result = await suno_get_tasks_batch(task_ids=["failed-task"])

        assert "State: failed" in result
        assert "bad_request" in result
        assert "keep polling" not in result

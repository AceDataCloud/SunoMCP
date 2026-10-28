"""Unit tests for media tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from core.exceptions import SunoAPIError
from core.server import mcp
from tools.info_tools import suno_list_actions
from tools.media_tools import suno_extract_vocals, suno_get_mp3


class TestAudioAvailabilityTool:
    @pytest.mark.asyncio
    async def test_schema_and_dispatch(self, mock_availability_response):
        tool = next(
            tool for tool in await mcp.list_tools() if tool.name == "suno_check_audio_availability"
        )
        schema = tool.inputSchema
        assert schema["required"] == ["audio_id"]
        assert set(schema["properties"]) == {"audio_id"}
        assert schema["properties"]["audio_id"]["type"] == "string"
        assert schema["properties"]["audio_id"]["format"] == "uuid"
        audio_id = mock_availability_response["data"]["id"]
        with patch(
            "tools.media_tools.client.check_audio_availability",
            new=AsyncMock(return_value=mock_availability_response),
        ) as request:
            result = await mcp.call_tool("suno_check_audio_availability", {"audio_id": audio_id})

        request.assert_awaited_once_with(audio_id=audio_id)
        content, _ = result
        assert json.loads(content[0].text) == mock_availability_response
        assert "suno_check_audio_availability" in await suno_list_actions()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arguments", [{}, {"audio_id": ""}, {"audio_id": "not-a-uuid"}])
    async def test_rejects_invalid_audio_id_without_request(self, arguments):
        with (
            patch("tools.media_tools.client.check_audio_availability", new=AsyncMock()) as request,
            pytest.raises(ToolError),
        ):
            await mcp.call_tool("suno_check_audio_availability", arguments)
        request.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_unknown_availability_is_error_not_false(self, mock_availability_response):
        error = SunoAPIError(
            message="Availability unknown",
            code="availability_unknown",
            status_code=503,
            task_id=mock_availability_response["task_id"],
            trace_id=mock_availability_response["trace_id"],
        )
        with (
            patch(
                "tools.media_tools.client.check_audio_availability",
                new=AsyncMock(side_effect=error),
            ) as request,
            pytest.raises(ToolError, match="availability_unknown") as exc_info,
        ):
            await mcp.call_tool(
                "suno_check_audio_availability",
                {"audio_id": mock_availability_response["data"]["id"]},
            )
        assert mock_availability_response["task_id"] in str(exc_info.value)
        assert mock_availability_response["trace_id"] in str(exc_info.value)
        request.assert_awaited_once()


class TestExtractVocalsTool:
    @pytest.mark.asyncio
    async def test_forwards_short_interval(self, mock_audio_response):
        with patch(
            "tools.media_tools.client.get_vox",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_vox:
            await suno_extract_vocals(
                audio_id="audio-1",
                vocal_start=1,
                vocal_end=20,
            )

        assert mock_vox.await_args.kwargs == {
            "audio_id": "audio-1",
            "vocal_start": 1,
            "vocal_end": 20,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start,end", [(20, 20), (20, 10), (0, 30), (1, 31)])
    async def test_rejects_invalid_or_long_interval(self, start, end):
        with pytest.raises(ValueError, match="shorter than 30 seconds"):
            await suno_extract_vocals(
                audio_id="audio-1",
                vocal_start=start,
                vocal_end=end,
            )


class TestGetMp3Tool:
    @pytest.mark.asyncio
    async def test_forwards_audio_id_without_callback(self, mock_audio_response):
        with patch(
            "tools.media_tools.client.get_mp3",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_mp3:
            await suno_get_mp3(audio_id="audio-1")

        assert mock_mp3.await_args.kwargs == {"audio_id": "audio-1"}

    @pytest.mark.asyncio
    async def test_forwards_callback_when_provided(self, mock_audio_response):
        callback = "https://example.com/callback"
        with patch(
            "tools.media_tools.client.get_mp3",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_mp3:
            await suno_get_mp3(audio_id="audio-1", callback_url=callback)

        assert mock_mp3.await_args.kwargs == {
            "audio_id": "audio-1",
            "callback_url": callback,
        }

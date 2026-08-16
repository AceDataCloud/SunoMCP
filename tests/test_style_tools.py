"""Unit tests for style tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.style_tools import suno_create_voice


class TestCreateVoiceTool:
    @pytest.mark.asyncio
    async def test_name_is_optional(self):
        with patch(
            "tools.style_tools.client.create_voice",
            new=AsyncMock(return_value={"success": True}),
        ) as mock_create_voice:
            await suno_create_voice(audio_url="https://example.com/voice.mp3")

        assert mock_create_voice.await_args.kwargs == {
            "audio_url": "https://example.com/voice.mp3",
        }

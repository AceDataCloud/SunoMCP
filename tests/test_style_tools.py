"""Unit tests for style tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.style_tools import suno_create_voice, suno_upload_audio


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


class TestUploadTool:
    @pytest.mark.asyncio
    async def test_standard_mode_is_default(self):
        with patch(
            "tools.style_tools.client.upload_audio",
            new=AsyncMock(return_value={"data": {"audio_id": "audio-1"}}),
        ) as mock_upload:
            await suno_upload_audio(audio_url="https://example.com/audio.mp3")

        assert mock_upload.await_args.kwargs == {"audio_url": "https://example.com/audio.mp3"}

    @pytest.mark.asyncio
    async def test_enhanced_mode_forwards_name_and_callback(self):
        with patch(
            "tools.style_tools.client.upload_audio",
            new=AsyncMock(return_value={"task_id": "task-1"}),
        ) as mock_upload:
            result = await suno_upload_audio(
                audio_url="https://example.com/audio.mp3",
                mode="enhanced",
                name="My Song",
                callback_url="https://example.com/webhook",
            )

        assert '"task_id": "task-1"' in result
        assert mock_upload.await_args.kwargs == {
            "audio_url": "https://example.com/audio.mp3",
            "mode": "enhanced",
            "name": "My Song",
            "callback_url": "https://example.com/webhook",
        }

    @pytest.mark.asyncio
    async def test_enhanced_mode_requires_name(self):
        with pytest.raises(ValueError, match="name is required"):
            await suno_upload_audio(
                audio_url="https://example.com/audio.mp3",
                mode="enhanced",
            )

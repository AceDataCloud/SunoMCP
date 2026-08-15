"""Unit tests for media tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.media_tools import suno_extract_vocals


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

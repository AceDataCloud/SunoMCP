"""Unit tests for audio tools (mocked client, no network)."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.audio_tools import (
    suno_generate_custom_music,
    suno_generate_inspo,
    suno_mashup_music,
    suno_remaster_music,
    suno_replace_section,
)


class TestInspoTool:
    """Tests for the suno_generate_inspo tool."""

    @pytest.mark.asyncio
    async def test_inspo_builds_expected_payload(self, mock_audio_response):
        """Inspo tool should send action=inspo with audio_urls and optional params."""
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            result = await suno_generate_inspo(
                audio_urls=["https://cdn1.suno.ai/ref.mp3"],
                prompt="warm acoustic folk",
                style="acoustic, folk, warm",
                title="Inspo Demo",
                model="chirp-v5",
                audio_weight=0.6,
            )

        mock_generate.assert_awaited_once()
        payload = mock_generate.await_args.kwargs
        assert payload["action"] == "inspo"
        assert payload["audio_urls"] == ["https://cdn1.suno.ai/ref.mp3"]
        assert payload["model"] == "chirp-v5"
        assert payload["audio_weight"] == 0.6
        assert payload["style"] == "acoustic, folk, warm"
        assert "test-task-123" in result

    @pytest.mark.asyncio
    async def test_inspo_omits_unset_optional_params(self, mock_audio_response):
        """Optional params left empty should not be sent in the payload."""
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_inspo(audio_urls=["https://cdn1.suno.ai/ref.mp3"])

        payload = mock_generate.await_args.kwargs
        assert payload["action"] == "inspo"
        assert "audio_weight" not in payload
        assert "style" not in payload
        assert "prompt" not in payload


class TestRemasterTool:
    @pytest.mark.asyncio
    async def test_remaster_forwards_variation_category(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_remaster_music(
                audio_id="audio-1",
                variation_category="subtle",
                model="chirp-v5-5",
            )

        assert mock_generate.await_args.kwargs == {
            "action": "remaster",
            "audio_id": "audio-1",
            "variation_category": "subtle",
            "model": "chirp-v5-5",
            "callback_url": None,
        }


class TestMashupTool:
    @pytest.mark.asyncio
    async def test_mashup_forwards_creative_direction(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_mashup_music(
                mashup_audio_ids=["audio-1", "audio-2"],
                prompt="Blend both melodies into one arrangement",
                style="warm acoustic pop",
                title="Merged Currents",
                instrumental=True,
            )

        payload = mock_generate.await_args.kwargs
        assert payload["action"] == "mashup"
        assert payload["mashup_audio_ids"] == ["audio-1", "audio-2"]
        assert payload["prompt"] == "Blend both melodies into one arrangement"
        assert payload["style"] == "warm acoustic pop"
        assert payload["title"] == "Merged Currents"
        assert payload["instrumental"] is True


class TestCustomNegativeTags:
    """Tests for excluded styles on custom generation."""

    @pytest.mark.asyncio
    async def test_negative_tags_are_forwarded(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(
                lyric="[Verse]\nhello",
                negative_tags="metal, distortion",
            )

        payload = mock_generate.await_args.kwargs
        assert payload["negative_tags"] == "metal, distortion"
        assert "style_negative" not in payload

    @pytest.mark.asyncio
    async def test_empty_negative_tags_are_omitted(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(lyric="[Verse]\nhello")

        assert "negative_tags" not in mock_generate.await_args.kwargs


class TestCustomLyricPrompt:
    """Tests for auto-lyrics prompt on custom generation."""

    @pytest.mark.asyncio
    async def test_lyric_prompt_string_is_forwarded(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(lyric="", lyric_prompt="A song about winter")

        assert mock_generate.await_args.kwargs["lyric_prompt"] == "A song about winter"

    @pytest.mark.asyncio
    async def test_empty_lyric_prompt_is_forwarded(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(lyric="", lyric_prompt="")

        assert mock_generate.await_args.kwargs["lyric_prompt"] == ""


class TestCustomDuration:
    """Tests for the duration parameter on custom generation."""

    @pytest.mark.asyncio
    async def test_duration_is_forwarded(self, mock_audio_response):
        """A requested duration should reach the API payload."""
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(
                lyric="[Verse]\nhello",
                title="Duration Demo",
                model="chirp-v5-5",
                duration=330,
            )

        payload = mock_generate.await_args.kwargs
        assert payload["action"] == "generate"
        assert payload["custom"] is True
        assert payload["duration"] == 330

    @pytest.mark.asyncio
    async def test_duration_omitted_when_unset(self, mock_audio_response):
        """Leaving duration unset must not send the key at all."""
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(
                lyric="[Verse]\nhello",
                title="No Duration",
                model="chirp-v5-5",
            )

        assert "duration" not in mock_generate.await_args.kwargs

    @pytest.mark.asyncio
    async def test_duration_is_not_range_or_model_gated(self, mock_audio_response):
        """Any value on any model is forwarded as-is; the API owns the rules."""
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_generate_custom_music(
                lyric="[Verse]\nhello",
                title="Long Take",
                model="chirp-v4",
                duration=900,
            )

        assert mock_generate.await_args.kwargs["duration"] == 900


class TestReplaceSectionResultMode:
    @pytest.mark.asyncio
    async def test_explicit_result_mode_is_forwarded(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_replace_section(
                audio_id="audio-1",
                replace_section_start=10,
                replace_section_end=20,
                result_mode="candidates",
            )

        assert mock_generate.await_args.kwargs["replace_section_result_mode"] == "candidates"

    @pytest.mark.asyncio
    async def test_default_result_mode_requests_two_full_songs(self, mock_audio_response):
        with patch(
            "tools.audio_tools.client.generate_audio",
            new=AsyncMock(return_value=mock_audio_response),
        ) as mock_generate:
            await suno_replace_section(
                audio_id="audio-1",
                replace_section_start=10,
                replace_section_end=20,
            )

        assert mock_generate.await_args.kwargs["replace_section_result_mode"] == "full_song"

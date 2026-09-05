"""Unit tests for custom model tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tools.custom_model_tools import (
    suno_archive_custom_model,
    suno_create_custom_model,
    suno_generate_with_custom_model,
    suno_get_custom_model,
    suno_list_custom_models,
)


class TestCustomModelTools:
    @pytest.mark.asyncio
    async def test_create_custom_model_forwards_payload_and_idempotency_key(self):
        with patch(
            "tools.custom_model_tools.client.custom_models",
            new=AsyncMock(return_value={"id": "model-1", "task_id": "task-1"}),
        ) as mock_custom_models:
            result = await suno_create_custom_model(
                name="My Indie Model",
                audio_urls=[
                    "https://example.com/song-01.mp3",
                    "https://example.com/song-02.mp3",
                    "https://example.com/song-03.mp3",
                    "https://example.com/song-04.mp3",
                    "https://example.com/song-05.mp3",
                    "https://example.com/song-06.mp3",
                ],
                callback_url="https://example.com/webhook",
                idempotency_key="retry-key",
            )

        assert '"task_id": "task-1"' in result
        assert mock_custom_models.await_args.kwargs == {
            "idempotency_key": "retry-key",
            "action": "create",
            "name": "My Indie Model",
            "audio_urls": [
                "https://example.com/song-01.mp3",
                "https://example.com/song-02.mp3",
                "https://example.com/song-03.mp3",
                "https://example.com/song-04.mp3",
                "https://example.com/song-05.mp3",
                "https://example.com/song-06.mp3",
            ],
            "callback_url": "https://example.com/webhook",
        }

    @pytest.mark.asyncio
    async def test_get_custom_model_uses_retrieve_action(self):
        with patch(
            "tools.custom_model_tools.client.custom_models",
            new=AsyncMock(return_value={"id": "model-1"}),
        ) as mock_custom_models:
            await suno_get_custom_model(model_id="model-1")

        assert mock_custom_models.await_args.kwargs == {
            "action": "retrieve",
            "id": "model-1",
        }

    @pytest.mark.asyncio
    async def test_list_custom_models_forwards_pagination_and_status(self):
        with patch(
            "tools.custom_model_tools.client.custom_models",
            new=AsyncMock(return_value={"items": []}),
        ) as mock_custom_models:
            await suno_list_custom_models(limit=10, offset=20, status="ready")

        assert mock_custom_models.await_args.kwargs == {
            "action": "retrieve_batch",
            "limit": 10,
            "offset": 20,
            "status": "ready",
        }

    @pytest.mark.asyncio
    async def test_generate_with_custom_model_uses_generate_action(self):
        with patch(
            "tools.custom_model_tools.client.custom_models",
            new=AsyncMock(return_value={"task_id": "task-1"}),
        ) as mock_custom_models:
            await suno_generate_with_custom_model(
                model_id="model-1",
                title="Neon Rain",
                lyric="[Verse]\nCity lights",
                style="indie rock",
            )

        assert mock_custom_models.await_args.kwargs == {
            "action": "generate",
            "id": "model-1",
            "title": "Neon Rain",
            "lyric": "[Verse]\nCity lights",
            "style": "indie rock",
        }

    @pytest.mark.asyncio
    async def test_archive_custom_model_uses_delete_action(self):
        with patch(
            "tools.custom_model_tools.client.custom_models",
            new=AsyncMock(return_value={"success": True}),
        ) as mock_custom_models:
            await suno_archive_custom_model(model_id="model-1")

        assert mock_custom_models.await_args.kwargs == {
            "action": "delete",
            "id": "model-1",
        }

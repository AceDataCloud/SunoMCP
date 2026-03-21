"""Unit tests for utility functions."""

import json

from core.utils import (
    format_audio_result,
    format_lyrics_result,
    format_persona_result,
    format_task_result,
)


class TestFormatAudioResult:
    """Tests for format_audio_result function."""

    def test_format_success(self, mock_audio_response):
        """Test formatting successful audio response."""
        result = format_audio_result(mock_audio_response)
        data = json.loads(result)
        assert data["success"] is True
        assert data["task_id"] == "test-task-123"
        assert data["trace_id"] == "test-trace-456"
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "Test Song"
        assert data["data"][0]["duration"] == 120.5
        assert data["data"][0]["state"] == "succeeded"
        assert "audio_url" in data["data"][0]
        assert data["mcp_async_submission"]["poll_tool"] == "suno_get_task"

    def test_format_error(self, mock_error_response):
        """Test formatting error response."""
        result = format_audio_result(mock_error_response)
        data = json.loads(result)
        assert data["success"] is False
        assert data["error"]["code"] == "invalid_request"

    def test_format_empty_data(self):
        """Test formatting response with no audio data."""
        response = {"success": True, "task_id": "123", "data": []}
        result = format_audio_result(response)
        data = json.loads(result)
        assert data["task_id"] == "123"
        assert data["data"] == []


class TestFormatLyricsResult:
    """Tests for format_lyrics_result function."""

    def test_format_success(self, mock_lyrics_response):
        """Test formatting successful lyrics response."""
        result = format_lyrics_result(mock_lyrics_response)
        data = json.loads(result)
        assert data["success"] is True
        assert data["task_id"] == "lyrics-task-123"
        assert data["data"]["title"] == "Test Song Title"
        assert data["data"]["status"] == "complete"
        assert "Generated lyrics here" in data["data"]["text"]

    def test_format_error(self, mock_error_response):
        """Test formatting error response."""
        result = format_lyrics_result(mock_error_response)
        data = json.loads(result)
        assert data["success"] is False


class TestFormatTaskResult:
    """Tests for format_task_result function."""

    def test_format_success(self, mock_task_response):
        """Test formatting successful task response."""
        result = format_task_result(mock_task_response)
        data = json.loads(result)
        assert data["id"] == "task-123"
        assert data["request"]["action"] == "generate"
        assert data["response"]["success"] is True
        assert data["response"]["data"][0]["title"] == "Test Song"
        assert data["mcp_task_polling"]["poll_tool"] == "suno_get_task"

    def test_format_error(self):
        """Test formatting error response."""
        error_response = {"error": {"code": "not_found", "message": "Task not found"}}
        result = format_task_result(error_response)
        data = json.loads(result)
        assert data["error"]["code"] == "not_found"


class TestFormatPersonaResult:
    """Tests for format_persona_result function."""

    def test_format_success(self, mock_persona_response):
        """Test formatting successful persona response."""
        result = format_persona_result(mock_persona_response)
        data = json.loads(result)
        assert data["success"] is True
        assert data["data"]["persona_id"] == "persona-id-456"

    def test_format_error(self, mock_error_response):
        """Test formatting error response."""
        result = format_persona_result(mock_error_response)
        data = json.loads(result)
        assert data["success"] is False

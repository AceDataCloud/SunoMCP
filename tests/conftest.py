"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file BEFORE any other imports
from dotenv import load_dotenv

load_dotenv(dotenv_path=project_root / ".env")

# Set default log level for tests
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture
def api_token():
    """Get API token from environment for integration tests."""
    token = os.environ.get("ACEDATACLOUD_API_TOKEN", "")
    if not token:
        pytest.skip("ACEDATACLOUD_API_TOKEN not configured for integration tests")
    return token


@pytest.fixture
def mock_audio_response():
    """Mock successful audio generation response."""
    return {
        "success": True,
        "task_id": "test-task-123",
        "trace_id": "test-trace-456",
        "data": [
            {
                "id": "audio-id-1",
                "title": "Test Song",
                "style": "pop, upbeat",
                "duration": 120.5,
                "state": "succeeded",
                "model": "chirp-v4-5",
                "audio_url": "https://cdn1.suno.ai/test-audio.mp3",
                "video_url": "https://cdn1.suno.ai/test-video.mp4",
                "image_url": "https://cdn2.suno.ai/test-image.jpeg",
                "lyric": "[Verse]\nTest lyrics here\n[Chorus]\nTest chorus here",
                "created_at": "2025-01-21T00:00:00.000Z",
            }
        ],
    }


@pytest.fixture
def mock_availability_response():
    return {
        "success": True,
        "task_id": "11111111-1111-4111-8111-111111111111",
        "trace_id": "22222222-2222-4222-8222-222222222222",
        "data": {"id": "33333333-3333-4333-8333-333333333333", "available": True},
    }


@pytest.fixture
def mock_lyrics_response():
    """Mock successful lyrics generation response."""
    return {
        "success": True,
        "task_id": "lyrics-task-123",
        "data": {
            "title": "Test Song Title",
            "text": "[Verse]\nGenerated lyrics here\n[Chorus]\nCatchy chorus",
            "status": "complete",
        },
    }


@pytest.fixture
def mock_task_response():
    """Mock task query response."""
    return {
        "id": "task-123",
        "created_at": 1705788000.0,
        "request": {
            "action": "generate",
            "prompt": "A test song",
        },
        "response": {
            "success": True,
            "task_id": "task-123",
            "data": [
                {
                    "id": "audio-id-1",
                    "title": "Test Song",
                    "duration": 120.5,
                    "audio_url": "https://cdn1.suno.ai/test.mp3",
                }
            ],
        },
    }


@pytest.fixture
def mock_persona_response():
    """Mock persona creation response."""
    return {
        "success": True,
        "task_id": "persona-task-123",
        "data": {
            "persona_id": "persona-id-456",
        },
    }


@pytest.fixture
def mock_error_response():
    """Mock error response."""
    return {
        "success": False,
        "error": {
            "code": "invalid_request",
            "message": "Invalid parameters provided",
        },
    }

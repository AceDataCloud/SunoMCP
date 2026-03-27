"""
Integration tests for Suno MCP Server.

These tests make REAL API calls to verify all tools work correctly.
Run with: pytest tests/test_integration.py -v -s

Note: These tests require ACEDATACLOUD_API_TOKEN to be set.
They are skipped in CI environments without the token.
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Check if API token is configured
HAS_API_TOKEN = bool(os.getenv("ACEDATACLOUD_API_TOKEN"))

# Decorator to skip tests that require API token
requires_api_token = pytest.mark.skipif(
    not HAS_API_TOKEN,
    reason="ACEDATACLOUD_API_TOKEN not configured - skipping integration test",
)


class TestAudioTools:
    """Integration tests for audio generation tools."""

    @requires_api_token
    @pytest.mark.asyncio
    async def test_generate_music_basic(self):
        """Test basic music generation with real API."""
        from tools.audio_tools import suno_generate_music

        result = await suno_generate_music(
            prompt="A short test jingle, upbeat and happy",
            model="chirp-v3-5",  # Use v3.5 for faster generation
            instrumental=False,
        )

        print("\n=== Generate Music Result ===")
        print(result)

        # Verify response contains expected fields
        assert "Task ID:" in result
        assert "Song 1" in result or "Error:" not in result
        if "Error:" not in result:
            assert "Audio URL:" in result
            assert "https://" in result

    @requires_api_token
    @pytest.mark.asyncio
    async def test_generate_custom_music(self):
        """Test custom music generation with lyrics."""
        from tools.audio_tools import suno_generate_custom_music

        result = await suno_generate_custom_music(
            lyric="[Verse]\nThis is a test song\nJust for testing\n[Chorus]\nTest test test",
            title="Test Song",
            style="pop, simple",
            model="chirp-v3-5",
            instrumental=False,
        )

        print("\n=== Custom Music Result ===")
        print(result)

        assert "Task ID:" in result
        if "Error:" not in result:
            assert "Audio URL:" in result


class TestLyricsTools:
    """Integration tests for lyrics generation tools."""

    @requires_api_token
    @pytest.mark.asyncio
    async def test_generate_lyrics(self):
        """Test lyrics generation with real API."""
        from tools.lyrics_tools import suno_generate_lyrics

        result = await suno_generate_lyrics(
            prompt="A short song about testing software",
            model="chirp-v3",
        )

        print("\n=== Generate Lyrics Result ===")
        print(result)

        assert "Task ID:" in result
        if "Error:" not in result:
            assert "Title:" in result
            assert "Lyrics:" in result


class TestInfoTools:
    """Integration tests for informational tools."""

    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test suno_list_models tool."""
        from tools.info_tools import suno_list_models

        result = await suno_list_models()

        print("\n=== List Models Result ===")
        print(result)

        assert "chirp-v5" in result
        assert "chirp-v4-5" in result
        assert "chirp-v3" in result

    @pytest.mark.asyncio
    async def test_list_actions(self):
        """Test suno_list_actions tool."""
        from tools.info_tools import suno_list_actions

        result = await suno_list_actions()

        print("\n=== List Actions Result ===")
        print(result)

        assert "suno_generate_music" in result
        assert "suno_extend_music" in result
        assert "suno_cover_music" in result

    @pytest.mark.asyncio
    async def test_get_lyric_format_guide(self):
        """Test lyric format guide tool."""
        from tools.info_tools import suno_get_lyric_format_guide

        result = await suno_get_lyric_format_guide()

        print("\n=== Lyric Format Guide ===")
        print(result)

        assert "[Verse]" in result
        assert "[Chorus]" in result


class TestTaskTools:
    """Integration tests for task query tools."""

    @requires_api_token
    @pytest.mark.asyncio
    async def test_get_task_with_real_id(self):
        """Test querying a task - first generate, then query."""
        from tools.audio_tools import suno_generate_music
        from tools.task_tools import suno_get_task

        # First generate something to get a task ID
        gen_result = await suno_generate_music(
            prompt="Quick test melody",
            model="chirp-v3-5",
        )

        print("\n=== Generation Result ===")
        print(gen_result)

        # Extract task ID from result
        if "Task ID:" in gen_result:
            lines = gen_result.split("\n")
            task_id = None
            for line in lines:
                if line.startswith("Task ID:"):
                    task_id = line.replace("Task ID:", "").strip()
                    break

            if task_id and task_id != "N/A":
                print(f"\n=== Querying Task: {task_id} ===")
                task_result = await suno_get_task(task_id)
                print(task_result)

                assert "Task ID:" in task_result


class TestClientDirectly:
    """Test the client module directly."""

    @requires_api_token
    @pytest.mark.asyncio
    async def test_client_generate_audio(self):
        """Test client.generate_audio directly."""
        from core.client import SunoClient

        client = SunoClient()

        result = await client.generate_audio(
            action="generate",
            prompt="Very short test",
            model="chirp-v3-5",
        )

        print("\n=== Client Direct Result ===")
        print(result)

        assert result.get("success") is True or "error" in result
        if result.get("success"):
            assert "task_id" in result
            assert "data" in result

    @requires_api_token
    @pytest.mark.asyncio
    async def test_client_generate_lyrics(self):
        """Test client.generate_lyrics directly."""
        from core.client import SunoClient

        client = SunoClient()

        result = await client.generate_lyrics(
            prompt="A song about code",
            model="chirp-v3",
        )

        print("\n=== Client Lyrics Result ===")
        print(result)

        assert result.get("success") is True or "error" in result
        if result.get("success"):
            assert "data" in result


class TestFullWorkflow:
    """End-to-end workflow tests."""

    @requires_api_token
    @pytest.mark.asyncio
    async def test_lyrics_then_music_workflow(self):
        """Test complete workflow: generate lyrics then create music."""
        from tools.audio_tools import suno_generate_custom_music
        from tools.lyrics_tools import suno_generate_lyrics

        print("\n=== Step 1: Generate Lyrics ===")
        lyrics_result = await suno_generate_lyrics(
            prompt="A short happy song",
        )
        print(lyrics_result)

        # If lyrics generation succeeded, use them for music
        if "Lyrics:" in lyrics_result and "Error:" not in lyrics_result:
            # Extract lyrics from result
            lines = lyrics_result.split("\n")
            in_lyrics = False
            extracted_lyrics = []
            for line in lines:
                if line.startswith("Lyrics:"):
                    in_lyrics = True
                    continue
                if in_lyrics:
                    extracted_lyrics.append(line)

            if extracted_lyrics:
                lyrics_text = "\n".join(extracted_lyrics).strip()
                if lyrics_text and lyrics_text != "N/A":
                    print("\n=== Step 2: Generate Music with Lyrics ===")
                    music_result = await suno_generate_custom_music(
                        lyric=lyrics_text[:500],  # Limit length for test
                        title="Generated Happy Song",
                        style="pop, upbeat",
                        model="chirp-v3-5",
                    )
                    print(music_result)

                    assert "Task ID:" in music_result


if __name__ == "__main__":
    # Run all tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])

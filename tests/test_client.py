"""Unit tests for HTTP client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from core.client import SunoClient
from core.exceptions import SunoAPIError, SunoAuthError, SunoTimeoutError


@pytest.fixture
def client():
    """Create a client instance for testing."""
    return SunoClient(api_token="test-token", base_url="https://api.test.com")


class TestSunoClient:
    """Tests for SunoClient class."""

    def test_init_with_params(self):
        """Test client initialization with explicit parameters."""
        client = SunoClient(api_token="my-token", base_url="https://custom.api.com")
        assert client.api_token == "my-token"
        assert client.base_url == "https://custom.api.com"

    def test_get_headers(self, client):
        """Test that headers are correctly generated."""
        headers = client._get_headers()
        assert headers["accept"] == "application/json"
        assert headers["authorization"] == "Bearer test-token"
        assert headers["content-type"] == "application/json"

    def test_get_headers_no_token(self):
        """Test that missing token raises auth error."""
        client = SunoClient(api_token="", base_url="https://api.test.com")
        with pytest.raises(SunoAuthError, match="not configured"):
            client._get_headers()

    def test_with_async_callback_injects_default_callback(self, client):
        """Test async submission injects an internal callback when missing."""
        payload = client._with_async_callback({"action": "generate"})
        assert payload["callback_url"] == "https://api.acedata.cloud/health"

    def test_with_async_callback_preserves_explicit_callback(self, client):
        """Test async submission preserves a user-provided callback."""
        payload = client._with_async_callback(
            {"action": "generate", "callback_url": "https://example.com/webhook"}
        )
        assert payload["callback_url"] == "https://example.com/webhook"

    @pytest.mark.asyncio
    async def test_request_success(self, client, mock_audio_response):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_audio_response

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_instance

            result = await client.request("/suno/audios", {"action": "generate"})
            assert result == mock_audio_response

    @pytest.mark.asyncio
    async def test_request_auth_error_401(self, client):
        """Test 401 response raises auth error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_instance

            with pytest.raises(SunoAuthError, match="Invalid API token"):
                await client.request("/suno/audios", {})

    @pytest.mark.asyncio
    async def test_request_timeout(self, client):
        """Test timeout raises timeout error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.TimeoutException("Timeout")
            mock_client.return_value.__aenter__.return_value = mock_instance

            with pytest.raises(SunoTimeoutError, match="timed out"):
                await client.request("/suno/audios", {})

    @pytest.mark.asyncio
    async def test_request_http_error(self, client):
        """Test HTTP error raises API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_instance

            with pytest.raises(SunoAPIError) as exc_info:
                await client.request("/suno/audios", {})

            assert exc_info.value.status_code == 500

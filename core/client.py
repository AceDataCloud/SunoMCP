"""HTTP client for Suno API."""

import contextvars
import json
from typing import Any

import httpx
from loguru import logger

from core.config import settings
from core.exceptions import SunoAPIError, SunoAuthError, SunoTimeoutError

# Force upstream async mode in MCP so tool calls return quickly with a task_id.
_ASYNC_CALLBACK_URL = "https://api.acedata.cloud/health"

# Context variable for per-request API token (used in HTTP/remote mode)
_request_api_token: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "_request_api_token", default=None
)


def set_request_api_token(token: str | None) -> None:
    """Set the API token for the current request context (HTTP mode)."""
    _request_api_token.set(token)


def get_request_api_token() -> str | None:
    """Get the API token from the current request context."""
    return _request_api_token.get()


class SunoClient:
    """Async HTTP client for AceDataCloud Suno API."""

    def __init__(self, api_token: str | None = None, base_url: str | None = None):
        """Initialize the Suno API client.

        Args:
            api_token: API token for authentication. If not provided, uses settings.
            base_url: Base URL for the API. If not provided, uses settings.
        """
        self.api_token = api_token if api_token is not None else settings.api_token
        self.base_url = base_url or settings.api_base_url
        self.timeout = settings.request_timeout

        logger.info(f"SunoClient initialized with base_url: {self.base_url}")
        logger.debug(f"API token configured: {'Yes' if self.api_token else 'No'}")
        logger.debug(f"Request timeout: {self.timeout}s")

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        token = get_request_api_token() or self.api_token
        if not token:
            logger.error("API token not configured!")
            raise SunoAuthError("API token not configured")

        return {
            "accept": "application/json",
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
        }

    def _with_async_callback(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Ensure long-running media operations are submitted asynchronously."""
        request_payload = dict(payload)
        if not request_payload.get("callback_url"):
            request_payload["callback_url"] = _ASYNC_CALLBACK_URL
        return request_payload

    async def request(
        self,
        endpoint: str,
        payload: dict[str, Any],
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the Suno API.

        Args:
            endpoint: API endpoint path (e.g., "/suno/audios")
            payload: Request body as dictionary
            timeout: Optional timeout override

        Returns:
            API response as dictionary

        Raises:
            SunoAuthError: If authentication fails
            SunoAPIError: If the API request fails
            SunoTimeoutError: If the request times out
        """
        url = f"{self.base_url}{endpoint}"
        request_timeout = timeout or self.timeout

        logger.info(f"🚀 POST {url}")
        logger.debug(f"Request payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        logger.debug(f"Timeout: {request_timeout}s")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=request_timeout,
                )

                logger.info(f"📥 Response status: {response.status_code}")

                if response.status_code == 401:
                    logger.error("❌ Authentication failed: Invalid API token")
                    raise SunoAuthError("Invalid API token")

                if response.status_code == 403:
                    logger.error("❌ Access denied: Check API permissions")
                    raise SunoAuthError("Access denied. Check your API permissions.")

                response.raise_for_status()

                result = response.json()
                logger.success(f"✅ Request successful! Task ID: {result.get('task_id', 'N/A')}")

                # Log summary of response
                if result.get("success"):
                    data = result.get("data", [])
                    if isinstance(data, list):
                        logger.info(f"📊 Returned {len(data)} item(s)")
                        for i, item in enumerate(data, 1):
                            if "audio_url" in item:
                                logger.info(
                                    f"   Song {i}: {item.get('title', 'Untitled')} - {item.get('duration', 0):.1f}s"
                                )
                            elif "text" in item:
                                logger.info(f"   Lyrics {i}: {item.get('title', 'Untitled')}")
                else:
                    logger.warning(f"⚠️ API returned success=false: {result.get('error', {})}")

                return result  # type: ignore[no-any-return]

            except httpx.TimeoutException as e:
                logger.error(f"⏰ Request timeout after {request_timeout}s: {e}")
                raise SunoTimeoutError(
                    f"Request to {endpoint} timed out after {request_timeout}s"
                ) from e

            except SunoAuthError:
                raise

            except httpx.HTTPStatusError as e:
                logger.error(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
                raise SunoAPIError(
                    message=e.response.text,
                    code=f"http_{e.response.status_code}",
                    status_code=e.response.status_code,
                ) from e

            except Exception as e:
                logger.error(f"❌ Request error: {e}")
                raise SunoAPIError(message=str(e)) from e

    # Convenience methods for specific endpoints
    async def generate_audio(self, **kwargs: Any) -> dict[str, Any]:
        """Generate audio using the audios endpoint."""
        logger.info(f"🎵 Generating audio with action: {kwargs.get('action', 'generate')}")
        return await self.request("/suno/audios", self._with_async_callback(kwargs))

    async def generate_lyrics(self, **kwargs: Any) -> dict[str, Any]:
        """Generate lyrics using the lyrics endpoint."""
        logger.info(f"📝 Generating lyrics with prompt: {kwargs.get('prompt', '')[:50]}...")
        return await self.request("/suno/lyrics", kwargs)

    async def create_persona(self, **kwargs: Any) -> dict[str, Any]:
        """Create a persona using the persona endpoint."""
        logger.info(f"👤 Creating persona: {kwargs.get('name', 'unnamed')}")
        return await self.request("/suno/persona", kwargs)

    async def get_mp4(self, **kwargs: Any) -> dict[str, Any]:
        """Get MP4 video for a song."""
        logger.info(f"🎥 Getting MP4 for audio: {kwargs.get('audio_id', '')}")
        return await self.request("/suno/mp4", self._with_async_callback(kwargs))

    async def get_timing(self, **kwargs: Any) -> dict[str, Any]:
        """Get timing/subtitle data for a song."""
        logger.info(f"⏱️ Getting timing for audio: {kwargs.get('audio_id', '')}")
        return await self.request("/suno/timing", kwargs)

    async def get_vox(self, **kwargs: Any) -> dict[str, Any]:
        """Extract vocals from a song."""
        logger.info(f"🎙️ Extracting vocals for audio: {kwargs.get('audio_id', '')}")
        return await self.request("/suno/vox", self._with_async_callback(kwargs))

    async def get_wav(self, **kwargs: Any) -> dict[str, Any]:
        """Get WAV format of a song."""
        logger.info(f"🔊 Getting WAV for audio: {kwargs.get('audio_id', '')}")
        return await self.request("/suno/wav", self._with_async_callback(kwargs))

    async def get_midi(self, **kwargs: Any) -> dict[str, Any]:
        """Get MIDI data of a song."""
        logger.info(f"🎹 Getting MIDI for audio: {kwargs.get('audio_id', '')}")
        return await self.request("/suno/midi", self._with_async_callback(kwargs))

    async def get_style(self, **kwargs: Any) -> dict[str, Any]:
        """Optimize a style prompt."""
        logger.info(f"🎨 Getting style for prompt: {kwargs.get('prompt', '')[:50]}...")
        return await self.request("/suno/style", kwargs)

    async def mashup_lyrics(self, **kwargs: Any) -> dict[str, Any]:
        """Generate mashup lyrics from two sets of lyrics."""
        logger.info("🔀 Generating mashup lyrics")
        return await self.request("/suno/mashup-lyrics", kwargs)

    async def upload_audio(self, **kwargs: Any) -> dict[str, Any]:
        """Upload audio from a URL."""
        logger.info(f"📤 Uploading audio: {kwargs.get('audio_url', '')[:50]}...")
        return await self.request("/suno/upload", kwargs)

    async def query_task(self, **kwargs: Any) -> dict[str, Any]:
        """Query task status using the tasks endpoint."""
        task_id = kwargs.get("id") or kwargs.get("ids", [])
        logger.info(f"🔍 Querying task(s): {task_id}")
        return await self.request("/suno/tasks", kwargs)


# Global client instance
client = SunoClient()

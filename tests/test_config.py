"""Unit tests for core configuration module."""

import os
from unittest.mock import patch

import pytest


def test_settings_default_values():
    """Test that settings have sensible defaults."""
    with patch.dict(os.environ, {"ACEDATACLOUD_API_TOKEN": "test"}, clear=False):
        from core.config import Settings

        settings = Settings()
        assert settings.api_base_url == "https://api.acedata.cloud"
        assert settings.default_model == "chirp-v5-5"
        assert settings.request_timeout == 1800.0
        assert settings.server_name == "suno"
        assert settings.transport == "stdio"


def test_settings_from_environment():
    """Test that settings are loaded from environment variables."""
    env_vars = {
        "ACEDATACLOUD_API_TOKEN": "my-token",
        "ACEDATACLOUD_API_BASE_URL": "https://custom.api.com",
        "SUNO_DEFAULT_MODEL": "chirp-v5",
        "SUNO_REQUEST_TIMEOUT": "300",
        "MCP_SERVER_NAME": "my-suno",
        "LOG_LEVEL": "DEBUG",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        from core.config import Settings

        settings = Settings()
        assert settings.api_token == "my-token"
        assert settings.api_base_url == "https://custom.api.com"
        assert settings.default_model == "chirp-v5"
        assert settings.request_timeout == 300.0
        assert settings.server_name == "my-suno"
        assert settings.log_level == "DEBUG"


def test_settings_is_configured():
    """Test the is_configured property."""
    from core.config import Settings

    with patch.dict(os.environ, {"ACEDATACLOUD_API_TOKEN": ""}, clear=False):
        settings = Settings()
        assert not settings.is_configured

    with patch.dict(os.environ, {"ACEDATACLOUD_API_TOKEN": "valid-token"}, clear=False):
        settings = Settings()
        assert settings.is_configured


def test_settings_validate_missing_token():
    """Test that validation fails without API token."""
    from core.config import Settings

    with patch.dict(os.environ, {"ACEDATACLOUD_API_TOKEN": ""}, clear=False):
        settings = Settings()
        with pytest.raises(ValueError, match="ACEDATACLOUD_API_TOKEN"):
            settings.validate()

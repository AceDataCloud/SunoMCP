"""Tests for hosted MCP OAuth behavior."""

import pytest


def test_normalize_scopes_defaults_to_mcp_access():
    from core.oauth import MCP_ACCESS_SCOPE, _normalize_scopes

    assert _normalize_scopes(None) == [MCP_ACCESS_SCOPE]
    assert _normalize_scopes([]) == [MCP_ACCESS_SCOPE]


@pytest.mark.asyncio
async def test_direct_api_token_gets_mcp_access_scope(monkeypatch):
    from core import oauth

    captured = {}
    monkeypatch.setattr(
        oauth, "set_request_api_token", lambda token: captured.setdefault("token", token)
    )

    provider = oauth.AceDataCloudOAuthProvider()
    access_token = await provider.load_access_token("test-api-token")

    assert captured["token"] == "test-api-token"
    assert access_token.scopes == [oauth.MCP_ACCESS_SCOPE]

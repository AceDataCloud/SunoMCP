# Generated from shared/oauth_state.py by scripts/sync_oauth.py; do not edit.

"""Shared, encrypted OAuth state for hosted MCP replicas.

The source is copied into each standalone MCP package by sync_oauth.py.
Redis is required in production; local single-process development can use
the in-memory fallback when MCP_OAUTH_REDIS_URL is unset.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time

from cryptography.fernet import Fernet
from mcp.server.auth.provider import AuthorizationCode, OAuthClientInformationFull
from redis.asyncio import Redis

STATE_TTL_SECONDS = 600


class OAuthStateStore:
    def __init__(
        self,
        server_name: str,
        redis_client: Redis | None = None,
        state_key: str = "",
    ) -> None:
        self._prefix = f"mcp:oauth:{hashlib.sha256(server_name.encode()).hexdigest()[:24]}"
        redis_url = os.getenv("MCP_OAUTH_REDIS_URL", "")
        self._redis = redis_client
        if self._redis is None and redis_url:
            self._redis = Redis.from_url(
                redis_url,
                password=os.getenv("MCP_OAUTH_REDIS_PASSWORD") or None,
                decode_responses=True,
            )
        self._cipher = None
        if self._redis is not None:
            key = state_key or os.getenv("MCP_OAUTH_STATE_KEY", "")
            if not key:
                raise ValueError("MCP_OAUTH_STATE_KEY is required with shared OAuth state")
            self._cipher = Fernet(base64.urlsafe_b64encode(bytes.fromhex(key)))

        self.clients: dict[str, OAuthClientInformationFull] = {}
        self.pending: dict[str, dict] = {}
        self.codes: dict[str, tuple[AuthorizationCode, str]] = {}
        self.revoked: set[str] = set()

    def _key(self, kind: str, value: str) -> str:
        return f"{self._prefix}:{kind}:{value}"

    def _seal(self, value: str) -> str:
        assert self._cipher is not None
        return self._cipher.encrypt(value.encode()).decode()

    def _unseal(self, value: str | bytes) -> str:
        assert self._cipher is not None
        return self._cipher.decrypt(value).decode()

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        if self._redis is None:
            return self.clients.get(client_id)
        raw = await self._redis.get(self._key("client", client_id))
        return OAuthClientInformationFull.model_validate_json(self._unseal(raw)) if raw else None

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        client_id = client_info.client_id
        if not client_id:
            raise ValueError("OAuth client_id is required")
        if self._redis is None:
            self.clients[client_id] = client_info
        else:
            await self._redis.set(
                self._key("client", client_id), self._seal(client_info.model_dump_json())
            )

    async def put_pending(self, state: str, value: dict) -> None:
        if self._redis is None:
            self.pending[state] = value
        else:
            await self._redis.set(
                self._key("pending", state),
                self._seal(json.dumps(value)),
                ex=STATE_TTL_SECONDS,
            )

    async def take_pending(self, state: str) -> dict | None:
        if self._redis is None:
            return self.pending.pop(state, None)
        raw = await self._redis.getdel(self._key("pending", state))
        return json.loads(self._unseal(raw)) if raw else None

    async def put_code(self, code: AuthorizationCode, token: str) -> None:
        if self._redis is None:
            self.codes[code.code] = (code, token)
        else:
            payload = {"authorization_code": code.model_dump(mode="json"), "token": token}
            ttl = max(1, int(code.expires_at - time.time()))
            await self._redis.set(
                self._key("code", code.code),
                self._seal(json.dumps(payload)),
                ex=ttl,
            )

    def _parse_code(self, raw: str | bytes | None) -> tuple[AuthorizationCode, str] | None:
        if not raw:
            return None
        payload = json.loads(self._unseal(raw))
        return AuthorizationCode.model_validate(payload["authorization_code"]), payload["token"]

    async def get_code(self, code: str) -> tuple[AuthorizationCode, str] | None:
        if self._redis is None:
            return self.codes.get(code)
        return self._parse_code(await self._redis.get(self._key("code", code)))

    async def take_code(self, code: str) -> tuple[AuthorizationCode, str] | None:
        if self._redis is None:
            return self.codes.pop(code, None)
        return self._parse_code(await self._redis.getdel(self._key("code", code)))

    async def delete_code(self, code: str) -> None:
        if self._redis is None:
            self.codes.pop(code, None)
        else:
            await self._redis.delete(self._key("code", code))

    def _revoked_key(self, token: str) -> str:
        return self._key("revoked", hashlib.sha256(token.encode()).hexdigest())

    async def is_revoked(self, token: str) -> bool:
        if self._redis is None:
            return token in self.revoked
        return bool(await self._redis.exists(self._revoked_key(token)))

    async def revoke(self, token: str) -> None:
        if self._redis is None:
            self.revoked.add(token)
        else:
            await self._redis.set(self._revoked_key(token), "1")

    async def clear_revoked(self, token: str) -> None:
        if self._redis is None:
            self.revoked.discard(token)
        else:
            await self._redis.delete(self._revoked_key(token))

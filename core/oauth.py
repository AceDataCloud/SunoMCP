"""OAuth 2.1 provider for AceDataCloud MCP servers.

Implements the MCP SDK's OAuthAuthorizationServerProvider interface,
delegating user authentication to AceDataCloud's OAuth 2.0 Authorization Server.

Flow:
1. Claude.ai redirects user to /authorize
2. MCP server redirects to auth.acedata.cloud/oauth2/authorize (consent page)
3. User logs in (if needed), sees consent page, approves
4. auth.acedata.cloud issues an authorization code, redirects to /oauth/callback
5. MCP server exchanges code for JWT + refresh_token via POST /oauth2/token (with PKCE)
6. MCP server uses JWT to fetch/create user's API credential
7. Issues the credential token as the OAuth access_token
8. On refresh: calls auth.acedata.cloud with stored refresh_token → new JWT → re-fetch credential
"""

import base64
import hashlib
import json
import secrets
import time
from urllib.parse import urlencode

import httpx
from loguru import logger
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthClientInformationFull,
    OAuthToken,
    RefreshToken,
)
from pydantic import AnyUrl
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from core.client import set_request_api_token
from core.config import settings

MCP_ACCESS_SCOPE = "mcp:access"


def _normalize_scopes(scopes: list[str] | None) -> list[str]:
    return scopes or [MCP_ACCESS_SCOPE]


class AceDataCloudOAuthProvider:
    """OAuth provider that delegates authentication to AceDataCloud platform.

    Refresh tokens are backed by auth.acedata.cloud — pod restarts don't break
    refresh because the real refresh_token lives at the authorization server.
    """

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[
            str, tuple[AuthorizationCode, str, str | None]
        ] = {}  # code → (AuthCode, api_token, auth_refresh_token)
        self._access_tokens: dict[str, AccessToken] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}
        # Maps MCP refresh_token → auth.acedata.cloud refresh_token (the real one)
        self._auth_refresh_tokens: dict[str, str] = {}
        self._pending_auth: dict[str, dict] = {}  # mcp_state → {client_id, params}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        client = self._clients.get(client_id)
        if client:
            return client
        # After pod restart, registered clients are forgotten. Synthesize so
        # token/refresh calls don't get a hard 401 — real auth is via
        # auth.acedata.cloud refresh_token validation.
        synthetic = OAuthClientInformationFull(
            client_id=client_id,
            redirect_uris=[AnyUrl("https://auth.acedata.cloud/user/connections")],
            token_endpoint_auth_method="none",
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
        )
        self._clients[client_id] = synthetic
        logger.debug(f"Synthesized client record for {client_id} (post-restart)")
        return synthetic

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        client_id = client_info.client_id
        assert client_id is not None
        self._clients[client_id] = client_info
        logger.info(f"Registered OAuth client: {client_id}")

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Redirect user to AceDataCloud OAuth 2.0 consent page."""
        mcp_state = secrets.token_urlsafe(32)

        # Generate PKCE pair for auth.acedata.cloud token exchange
        code_verifier = secrets.token_urlsafe(48)
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        auth_code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

        self._pending_auth[mcp_state] = {
            "client_id": client.client_id,
            "redirect_uri": str(params.redirect_uri),
            "state": params.state,
            "code_challenge": params.code_challenge,
            "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
            "scopes": _normalize_scopes(params.scopes),
            "resource": params.resource,
            "auth_code_verifier": code_verifier,
        }

        callback_url = f"{settings.server_url}/oauth/callback"

        # Request offline_access so auth.acedata.cloud returns a refresh_token
        auth_params = {
            "client_id": settings.oauth_client_id,
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "profile platform offline_access",
            "state": mcp_state,
            "code_challenge": auth_code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{settings.auth_base_url}/oauth2/authorize?{urlencode(auth_params)}"
        logger.info(f"OAuth authorize: redirecting to consent page (mcp_state={mcp_state})")
        return auth_url

    async def handle_callback(self, request: Request) -> RedirectResponse | JSONResponse:
        """Handle the callback from AceDataCloud OAuth 2.0 after user consent."""
        mcp_state = request.query_params.get("state")
        adc_code = request.query_params.get("code")

        if not mcp_state or not adc_code:
            logger.error(f"handle_callback: missing state={mcp_state} or code={adc_code}")
            return JSONResponse({"error": "Missing state or code parameter"}, status_code=400)

        pending = self._pending_auth.pop(mcp_state, None)
        if not pending:
            logger.error(f"handle_callback: state {mcp_state} not found in pending_auth")
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)

        try:
            # Exchange code for JWT + refresh_token from auth.acedata.cloud
            code_verifier = pending.get("auth_code_verifier", "")
            token_data = await self._exchange_code_for_tokens(adc_code, code_verifier)
            if not token_data:
                return JSONResponse(
                    {"error": "Failed to exchange authorization code"}, status_code=502
                )

            jwt_token = token_data["access_token"]
            auth_refresh = token_data.get("refresh_token")  # from auth.acedata.cloud

            # Fetch user's API credential using the JWT
            api_token = await self._get_user_credential(jwt_token)
            if not api_token:
                return JSONResponse(
                    {
                        "error": "No API credential found. Please create an API key at "
                        "https://platform.acedata.cloud first."
                    },
                    status_code=403,
                )

            # Create MCP authorization code (carries both api_token and auth_refresh)
            auth_code_str = secrets.token_urlsafe(48)
            auth_code = AuthorizationCode(
                code=auth_code_str,
                scopes=_normalize_scopes(pending.get("scopes")),
                expires_at=time.time() + 600,
                client_id=pending["client_id"],
                code_challenge=pending["code_challenge"],
                redirect_uri=pending["redirect_uri"],
                redirect_uri_provided_explicitly=pending["redirect_uri_provided_explicitly"],
                resource=pending.get("resource"),
            )
            self._auth_codes[auth_code_str] = (auth_code, api_token, auth_refresh)

            # Redirect back to Claude with the MCP auth code
            redirect_uri = pending["redirect_uri"]
            params = {"code": auth_code_str}
            if pending.get("state"):
                params["state"] = pending["state"]

            separator = "&" if "?" in redirect_uri else "?"
            redirect_url = f"{redirect_uri}{separator}{urlencode(params)}"
            logger.info("OAuth callback: issuing auth code, redirecting to client")
            return RedirectResponse(url=redirect_url, status_code=302)

        except Exception:
            logger.exception("OAuth callback error")
            return JSONResponse({"error": "Internal server error"}, status_code=500)

    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,  # noqa: ARG002
        authorization_code: str,
    ) -> AuthorizationCode | None:
        data = self._auth_codes.get(authorization_code)
        if not data:
            return None
        auth_code = data[0]
        if auth_code.expires_at < time.time():
            self._auth_codes.pop(authorization_code, None)
            return None
        return auth_code

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        data = self._auth_codes.pop(authorization_code.code, None)
        if not data:
            raise ValueError("Authorization code not found or already used")
        _, api_token, auth_refresh = data

        client_id = client.client_id or ""

        # Store access token
        self._access_tokens[api_token] = AccessToken(
            token=api_token,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
            expires_at=None,
        )

        # Issue MCP refresh_token backed by auth.acedata.cloud's refresh_token
        mcp_refresh_str = secrets.token_urlsafe(48)
        self._refresh_tokens[mcp_refresh_str] = RefreshToken(
            token=mcp_refresh_str,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
        )
        if auth_refresh:
            self._auth_refresh_tokens[mcp_refresh_str] = auth_refresh

        logger.info(
            f"OAuth token exchange: issued access token for client {client_id} "
            f"(auth_refresh={'yes' if auth_refresh else 'no'})"
        )
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
            scope=" ".join(_normalize_scopes(authorization_code.scopes)),
            refresh_token=mcp_refresh_str if auth_refresh else None,
        )

    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str,
    ) -> RefreshToken | None:
        stored = self._refresh_tokens.get(refresh_token)
        if stored:
            return stored
        # After pod restart, in-memory refresh tokens are lost. Synthesize so
        # exchange_refresh_token can attempt auth.acedata.cloud refresh.
        return RefreshToken(
            token=refresh_token,
            client_id=client.client_id or "",
            scopes=[MCP_ACCESS_SCOPE],
        )

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        """Refresh by calling auth.acedata.cloud with the stored auth refresh_token."""
        client_id = client.client_id or ""
        old_mcp_refresh = refresh_token.token

        # Get the auth.acedata.cloud refresh_token mapped to this MCP refresh
        auth_refresh = self._auth_refresh_tokens.pop(old_mcp_refresh, None)
        self._refresh_tokens.pop(old_mcp_refresh, None)

        if not auth_refresh:
            # Post-restart: no mapping. Fall back to in-memory access_token if available.
            for token, at in self._access_tokens.items():
                if at.client_id == client_id:
                    new_mcp_refresh = secrets.token_urlsafe(48)
                    self._refresh_tokens[new_mcp_refresh] = RefreshToken(
                        token=new_mcp_refresh,
                        client_id=client_id,
                        scopes=_normalize_scopes(scopes or refresh_token.scopes),
                    )
                    return OAuthToken(
                        access_token=token,
                        token_type="Bearer",
                        scope=" ".join(_normalize_scopes(scopes or refresh_token.scopes)),
                        refresh_token=new_mcp_refresh,
                    )
            from mcp.server.auth.provider import TokenError

            raise TokenError(
                error="invalid_grant",
                error_description="Refresh token expired, please re-authorize",
            )

        # Call auth.acedata.cloud to refresh the JWT
        token_data = await self._refresh_auth_token(auth_refresh)
        if not token_data:
            from mcp.server.auth.provider import TokenError

            raise TokenError(
                error="invalid_grant",
                error_description="auth.acedata.cloud refresh failed, please re-authorize",
            )

        new_jwt = token_data["access_token"]
        new_auth_refresh = token_data.get("refresh_token", auth_refresh)

        # Use new JWT to fetch/verify the user's API credential
        api_token = await self._get_user_credential(new_jwt)
        if not api_token:
            from mcp.server.auth.provider import TokenError

            raise TokenError(
                error="invalid_grant",
                error_description="Failed to fetch API credential after refresh",
            )

        # Remove old access_token for this client, store new one
        for token, at in list(self._access_tokens.items()):
            if at.client_id == client_id:
                del self._access_tokens[token]
        self._access_tokens[api_token] = AccessToken(
            token=api_token,
            client_id=client_id,
            scopes=_normalize_scopes(scopes or refresh_token.scopes),
            expires_at=None,
        )

        # Issue new MCP refresh_token mapped to the new auth refresh_token
        new_mcp_refresh = secrets.token_urlsafe(48)
        self._refresh_tokens[new_mcp_refresh] = RefreshToken(
            token=new_mcp_refresh,
            client_id=client_id,
            scopes=_normalize_scopes(scopes or refresh_token.scopes),
        )
        self._auth_refresh_tokens[new_mcp_refresh] = new_auth_refresh

        logger.info(f"OAuth refresh: issued new access token for client {client_id}")
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
            scope=" ".join(_normalize_scopes(scopes or refresh_token.scopes)),
            refresh_token=new_mcp_refresh,
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        """Validate an access token.

        Accepts both OAuth-issued tokens and direct API credential tokens.
        Direct tokens are accepted since the real validation happens at api.acedata.cloud.
        """
        if token in self._access_tokens:
            access_token = self._access_tokens[token]
            if access_token.expires_at and time.time() > access_token.expires_at:
                self._access_tokens.pop(token, None)
                return None
            set_request_api_token(token)
            return access_token

        # Accept direct API credential tokens (for VS Code, Cursor, etc.)
        set_request_api_token(token)
        return AccessToken(token=token, client_id="direct", scopes=[MCP_ACCESS_SCOPE])

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self._access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshToken):
            self._auth_refresh_tokens.pop(token.token, None)
            self._refresh_tokens.pop(token.token, None)
        logger.info(f"Revoked token: {token.token[:8]}...")

    # --- Internal helpers ---

    @staticmethod
    def _decode_jwt_payload(token: str) -> dict[str, str] | None:
        """Decode JWT payload without verification (for debug logging only)."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            result: dict[str, str] = json.loads(payload_bytes)
            return result
        except Exception as e:
            logger.debug(f"Failed to decode JWT payload: {e}")
            return None

    async def _exchange_code_for_tokens(
        self, code: str, code_verifier: str
    ) -> dict[str, str] | None:
        """Exchange authorization code for JWT + refresh_token from auth.acedata.cloud."""
        callback_url = f"{settings.server_url}/oauth/callback"
        token_url = f"{settings.auth_base_url}/oauth2/token"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": settings.oauth_client_id,
                        "redirect_uri": callback_url,
                        "code_verifier": code_verifier,
                    },
                )
                if response.status_code == 200:
                    data: dict[str, str] = response.json()
                    if data.get("access_token"):
                        claims = self._decode_jwt_payload(data["access_token"])
                        if claims:
                            logger.debug(
                                f"JWT claims: user_id={claims.get('user_id')}, "
                                f"exp={claims.get('exp')}, scope={claims.get('scope')}"
                            )
                        logger.info(
                            f"Token exchange OK (refresh_token={'yes' if data.get('refresh_token') else 'no'})"
                        )
                        return data
                    logger.error(f"Token exchange 200 but no access_token: {list(data.keys())}")
                else:
                    logger.error(
                        f"OAuth token exchange failed: {response.status_code} {response.text[:200]}"
                    )
        except Exception:
            logger.exception("OAuth token exchange error")
        return None

    async def _refresh_auth_token(self, auth_refresh_token: str) -> dict[str, str] | None:
        """Call auth.acedata.cloud to refresh the JWT using the auth refresh_token."""
        token_url = f"{settings.auth_base_url}/oauth2/token"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": auth_refresh_token,
                        "client_id": settings.oauth_client_id,
                    },
                )
                if response.status_code == 200:
                    data: dict[str, str] = response.json()
                    if data.get("access_token"):
                        logger.info("auth.acedata.cloud refresh OK, new JWT issued")
                        return data
                    logger.error(f"Auth refresh 200 but no access_token: {list(data.keys())}")
                else:
                    logger.warning(
                        f"auth.acedata.cloud refresh failed: {response.status_code} "
                        f"{response.text[:200]}"
                    )
        except Exception:
            logger.exception("auth.acedata.cloud refresh error")
        return None

    async def _get_user_credential(self, jwt_token: str) -> str | None:
        """Fetch or auto-create user's API credential token from PlatformBackend.

        Flow:
        1. List existing credentials → return first token if found
        2. List Global Usage applications → use first if found
        3. If no application, create one (POST /api/v1/applications/)
        4. Create credential under that application (POST /api/v1/credentials/)
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}
        logger.debug(
            f"_get_user_credential: platform_base_url={settings.platform_base_url}, "
            f"jwt_token={jwt_token[:32]}..."
        )

        # Decode JWT to extract user_id (needed for filtering API queries)
        claims = self._decode_jwt_payload(jwt_token)
        user_id: str | None = None
        if claims:
            user_id = claims.get("user_id")
            logger.debug(
                f"_get_user_credential JWT: user_id={user_id}, "
                f"scope={claims.get('scope')}, "
                f"permissions={claims.get('permissions')}, "
                f"token_type={claims.get('token_type')}, "
                f"exp={claims.get('exp')}"
            )
        else:
            logger.warning("_get_user_credential: could not decode JWT for debug")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Step 1: Check for existing credentials
                creds_url = f"{settings.platform_base_url}/api/v1/credentials/"
                creds_params: dict[str, str] = {}
                if user_id:
                    creds_params["user_id"] = user_id
                logger.debug(f"Step 1: GET {creds_url} params={creds_params}")
                response = await client.get(creds_url, headers=headers, params=creds_params)
                logger.debug(
                    f"Step 1 response: status={response.status_code}, body={response.text[:1000]}"
                )

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", data) if isinstance(data, dict) else data
                    logger.debug(
                        f"Step 1 parsed: type(data)={type(data).__name__}, "
                        f"type(results)={type(results).__name__}, "
                        f"count={len(results) if isinstance(results, list) else 'N/A'}"
                    )
                    if isinstance(results, list):
                        for i, cred in enumerate(results):
                            logger.debug(
                                f"Step 1 credential[{i}]: "
                                f"id={cred.get('id')}, "
                                f"token={'present' if cred.get('token') else 'MISSING'}, "
                                f"type={cred.get('type')}, "
                                f"keys={list(cred.keys())}"
                            )
                            cred_token: str | None = cred.get("token")
                            if cred_token:
                                logger.info(
                                    f"Found existing credential token "
                                    f"(id={cred.get('id')}, token={cred_token[:12]}...)"
                                )
                                return cred_token
                        logger.debug(
                            f"Step 1: iterated {len(results)} credentials, none had a token"
                        )
                    else:
                        logger.warning(f"Step 1: results is not a list: {type(results).__name__}")
                else:
                    logger.error(
                        f"Step 1 FAILED: credentials list returned "
                        f"status={response.status_code}, body={response.text[:500]}"
                    )

                # Step 2: No credentials found — auto-provision
                logger.info("No credentials found, auto-provisioning Application + Credential")

                # Step 2a: Find or create a Global Usage application
                apps_url = f"{settings.platform_base_url}/api/v1/applications/"
                apps_params: dict[str, str] = {
                    "limit": "10",
                    "ordering": "-created_at",
                    "type": "Usage",
                    "scope": "Global",
                }
                if user_id:
                    apps_params["user_id"] = user_id
                logger.debug(f"Step 2a: GET {apps_url} params={apps_params}")
                app_resp = await client.get(apps_url, params=apps_params, headers=headers)
                logger.debug(
                    f"Step 2a response: status={app_resp.status_code}, body={app_resp.text[:1000]}"
                )

                application_id: str | None = None
                if app_resp.status_code == 200:
                    app_data = app_resp.json()
                    items = app_data.get("items", app_data.get("results", []))
                    logger.debug(
                        f"Step 2a parsed: "
                        f"data_keys={list(app_data.keys()) if isinstance(app_data, dict) else 'not-dict'}, "
                        f"items_count={len(items) if isinstance(items, list) else 'N/A'}"
                    )
                    if isinstance(items, list) and items:
                        app = items[0]
                        application_id = app.get("id")
                        logger.debug(
                            f"Step 2a: using app id={application_id}, "
                            f"type={app.get('type')}, "
                            f"scope={app.get('scope')}, "
                            f"remaining_amount={app.get('remaining_amount')}, "
                            f"keys={list(app.keys())}"
                        )
                        # Check if the app already has a credential
                        app_creds = app.get("credentials", [])
                        logger.debug(
                            f"Step 2a: app.credentials count="
                            f"{len(app_creds) if isinstance(app_creds, list) else 'not-list'}"
                        )
                        if isinstance(app_creds, list) and app_creds:
                            logger.debug(f"Step 2a: first credential in app: {app_creds[0]}")
                            existing_token: str | None = app_creds[0].get("token")
                            if isinstance(existing_token, str) and existing_token:
                                logger.info(
                                    f"Found credential in existing application "
                                    f"(app_id={application_id}, token={existing_token[:12]}...)"
                                )
                                return existing_token
                            logger.debug("Step 2a: credential in app has no token field or empty")
                    else:
                        logger.debug("Step 2a: no Global Usage applications found")
                else:
                    logger.error(
                        f"Step 2a FAILED: applications list returned "
                        f"status={app_resp.status_code}, body={app_resp.text[:500]}"
                    )

                if not application_id:
                    # Create a new Global Usage application
                    create_payload = {"type": "Usage", "scope": "Global"}
                    logger.debug(f"Step 2a-create: POST {apps_url} json={create_payload}")
                    create_app_resp = await client.post(
                        apps_url,
                        headers={**headers, "Content-Type": "application/json"},
                        json=create_payload,
                    )
                    logger.debug(
                        f"Step 2a-create response: status={create_app_resp.status_code}, "
                        f"body={create_app_resp.text[:1000]}"
                    )
                    if create_app_resp.status_code in (200, 201):
                        new_app = create_app_resp.json()
                        application_id = new_app.get("id")
                        logger.info(f"Created Global Application: {application_id}")
                    else:
                        logger.error(
                            f"Failed to create application: "
                            f"{create_app_resp.status_code} {create_app_resp.text}"
                        )
                        return None

                # Step 2b: Create a credential under the application
                cred_create_url = f"{settings.platform_base_url}/api/v1/credentials/"
                cred_create_payload = {"application_id": application_id}
                logger.debug(f"Step 2b: POST {cred_create_url} json={cred_create_payload}")
                cred_resp = await client.post(
                    cred_create_url,
                    headers={**headers, "Content-Type": "application/json"},
                    json=cred_create_payload,
                )
                logger.debug(
                    f"Step 2b response: status={cred_resp.status_code}, "
                    f"body={cred_resp.text[:1000]}"
                )
                if cred_resp.status_code in (200, 201):
                    cred_data = cred_resp.json()
                    logger.debug(
                        f"Step 2b parsed: type={type(cred_data).__name__}, "
                        f"keys={list(cred_data.keys()) if isinstance(cred_data, dict) else 'not-dict'}"
                    )
                    new_token: str | None = (
                        cred_data.get("token") if isinstance(cred_data, dict) else None
                    )
                    if isinstance(new_token, str) and new_token:
                        logger.info(
                            f"Auto-provisioned new credential token (token={new_token[:12]}...)"
                        )
                        return new_token
                    logger.error(f"Credential created but no token in response: {cred_data}")
                else:
                    logger.error(
                        f"Failed to create credential: {cred_resp.status_code} {cred_resp.text}"
                    )
        except Exception:
            logger.exception("Credential fetch/provision error")

        logger.error("_get_user_credential: returning None — all steps failed")
        return None

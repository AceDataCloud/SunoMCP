"""OAuth 2.1 provider for AceDataCloud MCP servers.

Implements the MCP SDK's OAuthAuthorizationServerProvider interface,
delegating user authentication to AceDataCloud's OAuth 2.0 Authorization Server.

Flow:
1. Claude.ai redirects user to /authorize
2. MCP server redirects to auth.acedata.cloud/oauth2/authorize (consent page)
3. User logs in (if needed), sees consent page, approves
4. auth.acedata.cloud issues an authorization code, redirects to /oauth/callback
5. MCP server exchanges code for JWT via POST /oauth2/token (with PKCE)
6. MCP server uses JWT to fetch/create user's API credential
7. Issues the credential token as the OAuth access_token
8. Claude uses this token for all subsequent MCP requests
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
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from core.client import set_request_api_token
from core.config import settings

MCP_ACCESS_SCOPE = "mcp:access"


def _normalize_scopes(scopes: list[str] | None) -> list[str]:
    return scopes or [MCP_ACCESS_SCOPE]


class AceDataCloudOAuthProvider:
    """OAuth provider that delegates authentication to AceDataCloud platform.

    In-memory storage is used for auth state (suitable for single-replica K8s deployment).
    """

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[
            str, tuple[AuthorizationCode, str]
        ] = {}  # code → (AuthCode, api_token)
        self._access_tokens: dict[str, AccessToken] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}
        self._pending_auth: dict[str, dict] = {}  # mcp_state → {client_id, params}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        client_id = client_info.client_id
        assert client_id is not None
        self._clients[client_id] = client_info
        logger.info(f"Registered OAuth client: {client_id}")

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Redirect user to AceDataCloud OAuth 2.0 consent page."""
        # Generate state key for tracking this auth flow
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

        # Build callback URL
        callback_url = f"{settings.server_url}/oauth/callback"

        # Build OAuth 2.0 authorize URL
        auth_params = {
            "client_id": settings.oauth_client_id,
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "profile platform",
            "state": mcp_state,
            "code_challenge": auth_code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{settings.auth_base_url}/oauth2/authorize?{urlencode(auth_params)}"
        logger.info(f"OAuth authorize: redirecting to consent page (mcp_state={mcp_state})")
        return auth_url

    async def handle_callback(self, request: Request) -> RedirectResponse | JSONResponse:
        """Handle the callback from AceDataCloud OAuth 2.0 after user consent.

        This is called as a Starlette route handler, not part of the SDK interface.
        """
        mcp_state = request.query_params.get("state")
        adc_code = request.query_params.get("code")

        logger.debug(
            f"handle_callback: state={mcp_state}, code={adc_code[:16] if adc_code else None}, "
            f"pending_auth_keys={list(self._pending_auth.keys())}"
        )

        if not mcp_state or not adc_code:
            logger.error(f"handle_callback: missing state={mcp_state} or code={adc_code}")
            return JSONResponse({"error": "Missing state or code parameter"}, status_code=400)

        pending = self._pending_auth.pop(mcp_state, None)
        if not pending:
            logger.error(
                f"handle_callback: state {mcp_state} not found in pending_auth. "
                f"Available states: {list(self._pending_auth.keys())}"
            )
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)

        try:
            # Exchange AceDataCloud OAuth 2.0 code for JWT (with PKCE)
            code_verifier = pending.get("auth_code_verifier", "")
            logger.debug(
                f"handle_callback: exchanging code for JWT, pending_keys={list(pending.keys())}"
            )
            jwt_token = await self._exchange_code_for_jwt(adc_code, code_verifier)
            logger.debug(
                f"handle_callback: JWT exchange returned "
                f"{'token=' + jwt_token[:32] + '...' if jwt_token else 'None'}"
            )
            if not jwt_token:
                logger.error("handle_callback: JWT exchange failed, returning 502")
                return JSONResponse(
                    {"error": "Failed to exchange authorization code"}, status_code=502
                )

            # Fetch user's API credential token from PlatformBackend
            logger.debug("handle_callback: fetching user credential...")
            api_token = await self._get_user_credential(jwt_token)
            logger.debug(
                f"handle_callback: _get_user_credential returned "
                f"{'token=' + api_token[:12] + '...' if api_token else 'None'}"
            )
            if not api_token:
                logger.error("handle_callback: credential fetch returned None, returning 403")
                return JSONResponse(
                    {
                        "error": "No API credential found. Please create an API key at "
                        "https://platform.acedata.cloud first."
                    },
                    status_code=403,
                )

            # Create MCP authorization code
            auth_code_str = secrets.token_urlsafe(48)
            auth_code = AuthorizationCode(
                code=auth_code_str,
                scopes=_normalize_scopes(pending.get("scopes")),
                expires_at=time.time() + 600,  # 10 minutes
                client_id=pending["client_id"],
                code_challenge=pending["code_challenge"],
                redirect_uri=pending["redirect_uri"],
                redirect_uri_provided_explicitly=pending["redirect_uri_provided_explicitly"],
                resource=pending.get("resource"),
            )
            self._auth_codes[auth_code_str] = (auth_code, api_token)

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
        auth_code, _ = data
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
        _, api_token = data

        client_id = client.client_id or ""

        # Store access token mapping
        self._access_tokens[api_token] = AccessToken(
            token=api_token,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
            expires_at=None,  # API credential tokens don't expire by time
        )

        # Generate refresh token
        refresh_token_str = secrets.token_urlsafe(48)
        self._refresh_tokens[refresh_token_str] = RefreshToken(
            token=refresh_token_str,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
        )

        logger.info(f"OAuth token exchange: issued access token for client {client_id}")
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
            scope=" ".join(_normalize_scopes(authorization_code.scopes)),
            refresh_token=refresh_token_str,
        )

    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,  # noqa: ARG002
        refresh_token: str,
    ) -> RefreshToken | None:
        return self._refresh_tokens.get(refresh_token)

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        # For refresh, we reuse the same API credential token
        # Find the associated access token
        self._refresh_tokens.pop(refresh_token.token, None)

        # The original access_token (API credential) is still valid
        # Just issue a new refresh token
        client_id = client.client_id or ""
        new_refresh = secrets.token_urlsafe(48)
        self._refresh_tokens[new_refresh] = RefreshToken(
            token=new_refresh,
            client_id=client_id,
            scopes=_normalize_scopes(scopes or refresh_token.scopes),
        )

        # Find the access token for this client
        for token, at in self._access_tokens.items():
            if at.client_id == client.client_id:
                return OAuthToken(
                    access_token=token,
                    token_type="Bearer",
                    scope=" ".join(_normalize_scopes(scopes or refresh_token.scopes)),
                    refresh_token=new_refresh,
                )

        raise ValueError("No access token found for refresh")

    async def load_access_token(self, token: str) -> AccessToken | None:
        """Validate an access token.

        Accepts both OAuth-issued tokens and direct API credential tokens.
        Direct tokens are accepted since the real validation happens at api.acedata.cloud.
        """
        # Check OAuth-issued tokens first
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
            self._refresh_tokens.pop(token.token, None)
        logger.info(f"Revoked token: {token.token[:8]}...")

    # --- Internal helpers ---

    @staticmethod
    def _decode_jwt_payload(token: str) -> dict | None:
        """Decode JWT payload without verification (for debug logging only)."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                logger.debug(f"JWT has {len(parts)} parts, expected 3")
                return None
            payload_b64 = parts[1]
            # Add padding
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload: dict = json.loads(payload_bytes)
            return payload
        except Exception as e:
            logger.debug(f"Failed to decode JWT payload: {e}")
            return None

    async def _exchange_code_for_jwt(self, code: str, code_verifier: str) -> str | None:
        """Exchange AceDataCloud OAuth 2.0 authorization code for JWT."""
        callback_url = f"{settings.server_url}/oauth/callback"
        token_url = f"{settings.auth_base_url}/oauth2/token"
        logger.debug(
            f"Exchanging code for JWT: token_url={token_url}, "
            f"client_id={settings.oauth_client_id}, "
            f"redirect_uri={callback_url}, "
            f"code={code[:16]}..., "
            f"code_verifier={code_verifier[:16]}..."
        )
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
                logger.debug(
                    f"Token exchange response: status={response.status_code}, "
                    f"body={response.text[:500]}"
                )
                if response.status_code == 200:
                    data = response.json()
                    access_token: str | None = data.get("access_token")
                    if access_token:
                        # Decode and log JWT claims for debugging
                        claims = self._decode_jwt_payload(access_token)
                        if claims:
                            logger.debug(
                                f"JWT claims: user_id={claims.get('user_id')}, "
                                f"scope={claims.get('scope')}, "
                                f"permissions={claims.get('permissions')}, "
                                f"is_superuser={claims.get('is_superuser')}, "
                                f"is_verified={claims.get('is_verified')}, "
                                f"exp={claims.get('exp')}, "
                                f"iat={claims.get('iat')}, "
                                f"token_type={claims.get('token_type')}, "
                                f"all_keys={list(claims.keys())}"
                            )
                        else:
                            logger.warning("Could not decode JWT payload for debug")
                    else:
                        logger.error(
                            f"Token exchange 200 but no access_token in response. "
                            f"Keys: {list(data.keys())}"
                        )
                    return access_token
                logger.error(f"OAuth token exchange failed: {response.status_code} {response.text}")
        except Exception:
            logger.exception("OAuth token exchange error")
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

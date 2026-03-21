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
            "scopes": params.scopes,
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
            "scope": "profile",
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

        if not mcp_state or not adc_code:
            return JSONResponse({"error": "Missing state or code parameter"}, status_code=400)

        pending = self._pending_auth.pop(mcp_state, None)
        if not pending:
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)

        try:
            # Exchange AceDataCloud OAuth 2.0 code for JWT (with PKCE)
            code_verifier = pending.get("auth_code_verifier", "")
            jwt_token = await self._exchange_code_for_jwt(adc_code, code_verifier)
            if not jwt_token:
                return JSONResponse(
                    {"error": "Failed to exchange authorization code"}, status_code=502
                )

            # Fetch user's API credential token from PlatformBackend
            api_token = await self._get_user_credential(jwt_token)
            if not api_token:
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
                scopes=pending.get("scopes") or [],
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
            scopes=authorization_code.scopes,
            expires_at=None,  # API credential tokens don't expire by time
        )

        # Generate refresh token
        refresh_token_str = secrets.token_urlsafe(48)
        self._refresh_tokens[refresh_token_str] = RefreshToken(
            token=refresh_token_str,
            client_id=client_id,
            scopes=authorization_code.scopes,
        )

        logger.info(f"OAuth token exchange: issued access token for client {client_id}")
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
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
            scopes=scopes or refresh_token.scopes,
        )

        # Find the access token for this client
        for token, at in self._access_tokens.items():
            if at.client_id == client.client_id:
                return OAuthToken(
                    access_token=token,
                    token_type="Bearer",
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
        return AccessToken(token=token, client_id="direct", scopes=[])

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self._access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshToken):
            self._refresh_tokens.pop(token.token, None)
        logger.info(f"Revoked token: {token.token[:8]}...")

    # --- Internal helpers ---

    async def _exchange_code_for_jwt(self, code: str, code_verifier: str) -> str | None:
        """Exchange AceDataCloud OAuth 2.0 authorization code for JWT."""
        callback_url = f"{settings.server_url}/oauth/callback"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{settings.auth_base_url}/oauth2/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": settings.oauth_client_id,
                        "redirect_uri": callback_url,
                        "code_verifier": code_verifier,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    access_token: str | None = data.get("access_token")
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
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Step 1: Check for existing credentials
                response = await client.get(
                    f"{settings.platform_base_url}/api/v1/credentials/",
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", data) if isinstance(data, dict) else data
                    if isinstance(results, list):
                        for cred in results:
                            cred_token: str | None = cred.get("token")
                            if cred_token:
                                logger.info("Found existing user credential token")
                                return cred_token

                # Step 2: No credentials found — auto-provision
                logger.info("No credentials found, auto-provisioning Application + Credential")

                # Step 2a: Find or create a Global Usage application
                app_resp = await client.get(
                    f"{settings.platform_base_url}/api/v1/applications/",
                    params={
                        "limit": "10",
                        "ordering": "-created_at",
                        "type": "Usage",
                        "scope": "Global",
                    },
                    headers=headers,
                )
                application_id: str | None = None
                if app_resp.status_code == 200:
                    app_data = app_resp.json()
                    items = app_data.get("items", app_data.get("results", []))
                    if isinstance(items, list) and items:
                        app = items[0]
                        application_id = app.get("id")
                        # Check if the app already has a credential
                        app_creds = app.get("credentials", [])
                        if isinstance(app_creds, list) and app_creds:
                            existing_token: str | None = app_creds[0].get("token")
                            if isinstance(existing_token, str) and existing_token:
                                logger.info("Found credential in existing application")
                                return existing_token

                if not application_id:
                    # Create a new Global Usage application
                    create_app_resp = await client.post(
                        f"{settings.platform_base_url}/api/v1/applications/",
                        headers={**headers, "Content-Type": "application/json"},
                        json={"type": "Usage", "scope": "Global"},
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
                cred_resp = await client.post(
                    f"{settings.platform_base_url}/api/v1/credentials/",
                    headers={**headers, "Content-Type": "application/json"},
                    json={"application_id": application_id},
                )
                if cred_resp.status_code in (200, 201):
                    cred_data = cred_resp.json()
                    new_token: str | None = (
                        cred_data.get("token") if isinstance(cred_data, dict) else None
                    )
                    if isinstance(new_token, str) and new_token:
                        logger.info("Auto-provisioned new credential token")
                        return new_token
                    logger.error("Credential created but no token in response")
                else:
                    logger.error(
                        f"Failed to create credential: {cred_resp.status_code} {cred_resp.text}"
                    )
        except Exception:
            logger.exception("Credential fetch/provision error")
        return None

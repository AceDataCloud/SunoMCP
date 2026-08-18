"""OAuth 2.1 provider for AceDataCloud MCP servers.

Implements the MCP SDK's OAuthAuthorizationServerProvider interface,
delegating user authentication to AceDataCloud's OAuth 2.0 Authorization Server.

Flow:
1. Claude.ai redirects user to /authorize
2. MCP server redirects to auth.acedata.cloud/oauth2/authorize (consent page)
3. User logs in (if needed), sees consent page, approves
4. auth.acedata.cloud issues an authorization code, redirects to /oauth/callback
5. MCP server exchanges code for a JWT via POST /oauth2/token (with PKCE)
6. MCP server uses the JWT to fetch/create the user's API credential
7. Issues the durable credential token as the OAuth access_token — the credential
   does not expire, so there is no refresh flow and restarts never force re-auth
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

    The access token is the user's durable, non-expiring api.acedata.cloud
    credential. There is no refresh flow — the credential never expires, so pod
    restarts/redeploys never force re-authorization.
    """

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[
            str, tuple[AuthorizationCode, str]
        ] = {}  # code → (AuthCode, api_token)
        self._access_tokens: dict[str, AccessToken] = {}
        self._pending_auth: dict[str, dict] = {}  # mcp_state → {client_id, params}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        client = self._clients.get(client_id)
        if client:
            return client
        # After pod restart, registered clients are forgotten. Synthesize so
        # token calls don't get a hard 401 — the access token is a durable
        # api.acedata.cloud credential validated upstream.
        synthetic = OAuthClientInformationFull(
            client_id=client_id,
            redirect_uris=[AnyUrl("https://auth.acedata.cloud/user/connections")],
            token_endpoint_auth_method="none",
            grant_types=["authorization_code"],
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

        # Only need profile + platform to fetch the user's durable credential.
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
        _, api_token = data

        client_id = client.client_id or ""

        # The access token is the user's durable, non-expiring credential.
        self._access_tokens[api_token] = AccessToken(
            token=api_token,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
            expires_at=None,
        )

        logger.info(f"OAuth token exchange: issued durable credential for client {client_id}")
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
            scope=" ".join(_normalize_scopes(authorization_code.scopes)),
        )

    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,  # noqa: ARG002
        refresh_token: str,  # noqa: ARG002
    ) -> RefreshToken | None:
        # No refresh flow — the access token is a durable, non-expiring credential.
        return None

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,  # noqa: ARG002
        refresh_token: RefreshToken,  # noqa: ARG002
        scopes: list[str],  # noqa: ARG002
    ) -> OAuthToken:
        from mcp.server.auth.provider import TokenError

        # Tokens never expire, so there is nothing to refresh. An old client that
        # still holds a pre-migration refresh_token gets a clean re-auth prompt.
        raise TokenError(
            error="invalid_grant",
            error_description="This server issues non-expiring tokens; refresh is not supported.",
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

    async def _get_user_credential(self, jwt_token: str) -> str | None:
        """Get or create this Hosted MCP's dedicated Global Credential."""
        headers = {"Authorization": f"Bearer {jwt_token}"}
        claims = self._decode_jwt_payload(jwt_token)
        user_id = str(claims.get("user_id")) if claims and claims.get("user_id") else None

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                apps_url = f"{settings.platform_base_url}/api/v1/applications/"
                apps_params: dict[str, str] = {
                    "limit": "10",
                    "ordering": "-created_at",
                    "type": "Usage",
                    "scope": "Global",
                }
                if user_id:
                    apps_params["user_id"] = user_id
                app_resp = await client.get(apps_url, params=apps_params, headers=headers)

                application_id: str | None = None
                if app_resp.status_code == 200:
                    app_data = app_resp.json()
                    items = app_data.get("items", app_data.get("results", []))
                    if isinstance(items, list) and items:
                        application_id = items[0].get("id")

                if not application_id:
                    create_app_resp = await client.post(
                        apps_url,
                        headers={**headers, "Content-Type": "application/json"},
                        json={"type": "Usage", "scope": "Global"},
                    )
                    if create_app_resp.status_code not in (200, 201):
                        logger.error(
                            "Failed to create Global Application: "
                            f"{create_app_resp.status_code} {create_app_resp.text[:500]}"
                        )
                        return None
                    application_id = create_app_resp.json().get("id")

                if not application_id:
                    return None

                # Query for existing shared "OAuth MCP" credential first
                cred_list_resp = await client.get(
                    f"{settings.platform_base_url}/api/v1/credentials/",
                    params={"application_id": application_id, "name": "OAuth MCP"},
                    headers=headers,
                )
                existing_creds = []
                if cred_list_resp.status_code == 200:
                    cred_data = cred_list_resp.json()
                    existing_creds = cred_data.get("items", cred_data.get("results", []))

                # Reuse existing credential if found
                if existing_creds and isinstance(existing_creds, list):
                    data = existing_creds[0]
                    token = data.get("token") if isinstance(data, dict) else None
                    if isinstance(token, str) and token:
                        logger.info(f"Reusing existing OAuth MCP Credential (id={data.get('id')})")
                        return token

                # Create new credential only if not found
                cred_resp = await client.post(
                    f"{settings.platform_base_url}/api/v1/credentials/",
                    headers={**headers, "Content-Type": "application/json"},
                    json={
                        "application_id": application_id,
                        "name": "OAuth MCP",
                    },
                )
                if cred_resp.status_code not in (200, 201):
                    logger.error(
                        "Failed to create OAuth MCP Credential: "
                        f"{cred_resp.status_code} {cred_resp.text[:500]}"
                    )
                    return None
                data = cred_resp.json()
                token = data.get("token") if isinstance(data, dict) else None
                if isinstance(token, str) and token:
                    logger.info(f"Created new OAuth MCP Credential (id={data.get('id')})")
                    return token
                logger.error("OAuth MCP Credential response did not contain a token")
        except Exception:
            logger.exception("Managed MCP Credential provisioning failed")
        return None

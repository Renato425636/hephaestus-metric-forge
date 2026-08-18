"""OAuth2 Client Credentials (Auth0, M2M) JWT validation.

The API only validates tokens — it never issues them. Token issuance is the
client's responsibility via `POST https://{AUTH0_DOMAIN}/oauth/token`.

Validation: RS256 signature against Auth0's public JWKS, plus `aud`, `iss`,
`exp` checks. The JWKS is cached with a TTL; a `kid` that isn't in the cache
(e.g. because Auth0 rotated signing keys) is treated as a cache-miss and
triggers a single refetch rather than an immediate failure.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

JWKS_TTL_SECONDS = 3600

# auto_error=False: FastAPI's HTTPBearer otherwise raises 403 on a missing
# Authorization header. An absent/invalid credential is a 401 (unauthenticated),
# so the check is done explicitly in get_current_token below.
_bearer_scheme = HTTPBearer(auto_error=False)


def _auth0_domain() -> str:
    domain = os.environ.get("AUTH0_DOMAIN")
    if not domain:
        raise RuntimeError("AUTH0_DOMAIN environment variable is not set")
    return domain


def _auth0_audience() -> str:
    audience = os.environ.get("AUTH0_AUDIENCE")
    if not audience:
        raise RuntimeError("AUTH0_AUDIENCE environment variable is not set")
    return audience


class JWKSCache:
    """TTL cache over an Auth0 tenant's JWKS, keyed by `kid`."""

    def __init__(self, ttl_seconds: int = JWKS_TTL_SECONDS) -> None:
        self._ttl_seconds = ttl_seconds
        self._keys: dict[str, dict[str, Any]] = {}
        self._fetched_at: float = 0.0

    def _is_stale(self) -> bool:
        return (time.time() - self._fetched_at) > self._ttl_seconds

    def _fetch(self) -> None:
        url = f"https://{_auth0_domain()}/.well-known/jwks.json"
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        jwks = response.json()
        self._keys = {key["kid"]: key for key in jwks["keys"]}
        self._fetched_at = time.time()

    def get_key(self, kid: str) -> dict[str, Any]:
        if not self._keys or self._is_stale():
            self._fetch()
        if kid not in self._keys:
            # Cache-miss, not a hard error: Auth0 may have rotated signing keys.
            self._fetch()
        if kid not in self._keys:
            raise KeyError(f"kid '{kid}' not found in JWKS")
        return self._keys[kid]

    def invalidate(self) -> None:
        self._keys = {}
        self._fetched_at = 0.0


_jwks_cache = JWKSCache()


def _decode_token(token: str) -> dict[str, Any]:
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token header"
        ) from exc

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token missing kid")

    try:
        signing_key = _jwks_cache.get_key(kid)
    except (KeyError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=_auth0_audience(),
            issuer=f"https://{_auth0_domain()}/",
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token: {exc}"
        ) from exc

    return payload


async def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """FastAPI dependency: validates the bearer JWT, returns its claims."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await asyncio.to_thread(_decode_token, credentials.credentials)

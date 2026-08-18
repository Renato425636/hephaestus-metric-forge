from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt

import app.auth as auth_module

AUDIENCE = "https://metrics-api.test"
DOMAIN = "test-tenant.auth0.com"
ISSUER = f"https://{DOMAIN}/"


def _generate_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def _jwk_for(public_pem: str, kid: str) -> dict[str, Any]:
    key_dict: dict[str, Any] = jwk.construct(public_pem, algorithm="RS256").to_dict()
    key_dict["kid"] = kid
    key_dict["use"] = "sig"
    key_dict["alg"] = "RS256"
    return key_dict


def _make_token(private_pem: str, kid: str, **claim_overrides: Any) -> str:
    claims = {
        "sub": "test-client@clients",
        "aud": AUDIENCE,
        "iss": ISSUER,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    claims.update(claim_overrides)
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": kid})


PRIVATE_PEM, PUBLIC_PEM = _generate_keypair()
OTHER_PRIVATE_PEM, OTHER_PUBLIC_PEM = _generate_keypair()
KID = "primary-kid"
OTHER_KID = "rotated-kid"


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("AUTH0_DOMAIN", DOMAIN)
    monkeypatch.setenv("AUTH0_AUDIENCE", AUDIENCE)
    auth_module._jwks_cache.invalidate()
    yield
    auth_module._jwks_cache.invalidate()


def _patch_jwks(monkeypatch: pytest.MonkeyPatch, keys: list[dict[str, Any]]) -> list[str]:
    """Patches httpx.get for JWKS fetches; returns a list recording each fetch call."""
    calls: list[str] = []

    def _fake_get(url: str, timeout: float = 5.0) -> _FakeResponse:
        calls.append(url)
        return _FakeResponse({"keys": keys})

    monkeypatch.setattr(auth_module.httpx, "get", _fake_get)
    return calls


def test_decode_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_jwks(monkeypatch, [_jwk_for(PUBLIC_PEM, KID)])
    token = _make_token(PRIVATE_PEM, KID)

    payload = auth_module._decode_token(token)

    assert payload["sub"] == "test-client@clients"
    assert payload["aud"] == AUDIENCE


def test_decode_expired_token_raises_401(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_jwks(monkeypatch, [_jwk_for(PUBLIC_PEM, KID)])
    token = _make_token(PRIVATE_PEM, KID, exp=int(time.time()) - 60)

    with pytest.raises(Exception) as exc_info:
        auth_module._decode_token(token)
    assert exc_info.value.status_code == 401  # type: ignore[attr-defined]


def test_decode_wrong_audience_raises_401(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_jwks(monkeypatch, [_jwk_for(PUBLIC_PEM, KID)])
    token = _make_token(PRIVATE_PEM, KID, aud="https://someone-else.test")

    with pytest.raises(Exception) as exc_info:
        auth_module._decode_token(token)
    assert exc_info.value.status_code == 401  # type: ignore[attr-defined]


def test_decode_wrong_issuer_raises_401(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_jwks(monkeypatch, [_jwk_for(PUBLIC_PEM, KID)])
    token = _make_token(PRIVATE_PEM, KID, iss="https://not-the-tenant.auth0.com/")

    with pytest.raises(Exception) as exc_info:
        auth_module._decode_token(token)
    assert exc_info.value.status_code == 401  # type: ignore[attr-defined]


def test_decode_tampered_signature_raises_401(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_jwks(monkeypatch, [_jwk_for(PUBLIC_PEM, KID)])
    # Token signed with a *different* private key than the one published in JWKS.
    token = _make_token(OTHER_PRIVATE_PEM, KID)

    with pytest.raises(Exception) as exc_info:
        auth_module._decode_token(token)
    assert exc_info.value.status_code == 401  # type: ignore[attr-defined]


def test_kid_rotation_triggers_cache_miss_refetch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulates Auth0 rotating signing keys mid-session: cache has the old kid,
    token is signed with a new kid published on the *next* fetch — must refetch
    rather than fail outright."""
    calls: list[str] = []
    served_keys = [_jwk_for(PUBLIC_PEM, KID)]

    def _fake_get(url: str, timeout: float = 5.0) -> _FakeResponse:
        calls.append(url)
        return _FakeResponse({"keys": served_keys})

    monkeypatch.setattr(auth_module.httpx, "get", _fake_get)

    # Prime the cache with only the old kid.
    auth_module._jwks_cache.get_key(KID)
    assert len(calls) == 1

    # Auth0 rotates: new key now served, old kid gone.
    served_keys.clear()
    served_keys.append(_jwk_for(OTHER_PUBLIC_PEM, OTHER_KID))

    token = _make_token(OTHER_PRIVATE_PEM, OTHER_KID)
    payload = auth_module._decode_token(token)

    assert payload["sub"] == "test-client@clients"
    assert len(calls) == 2  # cache-miss on OTHER_KID triggered exactly one refetch


def test_missing_authorization_header_returns_401(client_without_auth_override: Any) -> None:
    response = client_without_auth_override.get("/functions")
    assert response.status_code == 401


@pytest.fixture()
def client_without_auth_override() -> Iterator[Any]:
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_jwks_fetch_http_error_is_401(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_get(url: str, timeout: float = 5.0) -> _FakeResponse:
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(auth_module.httpx, "get", _raise_get)
    token = _make_token(PRIVATE_PEM, KID)

    with pytest.raises(Exception) as exc_info:
        auth_module._decode_token(token)
    assert exc_info.value.status_code == 401  # type: ignore[attr-defined]

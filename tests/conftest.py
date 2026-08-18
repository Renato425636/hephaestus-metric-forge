from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("AUTH0_DOMAIN", "test-tenant.auth0.com")
os.environ.setdefault("AUTH0_AUDIENCE", "https://metrics-api.test")

from app.auth import get_current_token  # noqa: E402
from app.main import app  # noqa: E402


def _fake_token_payload() -> dict[str, Any]:
    return {"sub": "test-client@clients", "aud": os.environ["AUTH0_AUDIENCE"]}


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Authenticated TestClient: bypasses real JWT validation for endpoint tests.

    Auth logic itself is exercised separately (and for real) in test_auth.py.
    """
    app.dependency_overrides[get_current_token] = _fake_token_payload
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_token, None)


@pytest.fixture()
def unauthenticated_client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client

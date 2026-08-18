"""Contract-level tests for the `functions` resource: catalog shape, routing,
and generic error handling that isn't specific to any one function.

Per-item behavior (happy path, dtype/param validation, edge cases) lives in
the `tests/test_functions_*.py` category files, one per catalog category.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

_EXPECTED_FUNCTION_NAMES = {
    "dedupe",
    "drop_nulls",
    "fill_nulls",
    "trim_whitespace",
    "normalize_case",
    "groupby_agg",
    "pivot",
    "melt",
    "cast_dtype",
    "bucketize",
    "normalize",
}


def test_list_functions_catalog(client: TestClient) -> None:
    response = client.get("/functions")
    assert response.status_code == 200
    body = response.json()
    names = {item["name"] for item in body}
    assert names >= _EXPECTED_FUNCTION_NAMES
    for item in body:
        assert "applicable_dtypes" in item


def test_unknown_function_returns_404(client: TestClient) -> None:
    payload = {"data": [{"x": 1}], "columns": ["x"], "params": {}}
    response = client.post("/functions/does_not_exist", json=payload)
    assert response.status_code == 404


def test_missing_column_is_per_item_error(client: TestClient) -> None:
    payload = {"data": [{"x": 1}], "columns": ["missing_col"], "params": {}}
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results[0]["error"] is not None
    assert "not found in data" in results[0]["error"]


def test_functions_endpoint_requires_auth(unauthenticated_client: TestClient) -> None:
    response = unauthenticated_client.get("/functions")
    assert response.status_code == 401

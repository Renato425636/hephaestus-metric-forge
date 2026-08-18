from __future__ import annotations

import json

from fastapi.testclient import TestClient


def test_list_functions_catalog(client: TestClient) -> None:
    response = client.get("/functions")
    assert response.status_code == 200
    body = response.json()
    names = {item["name"] for item in body}
    assert {"dedupe", "groupby", "normalize"} <= names
    for item in body:
        assert "applicable_dtypes" in item


def test_dedupe_counts_duplicates(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 3}, {"id": 3}],
        "columns": ["id"],
        "params": {},
    }
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results == [{"column": "id", "function": "dedupe", "value": 2, "error": None}]


def test_groupby_default_counts_groups(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a"}, {"category": "a"}, {"category": "b"}],
        "columns": ["category"],
        "params": {},
    }
    response = client.post("/functions/groupby", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results[0]["value"] == 2
    assert results[0]["error"] is None


def test_normalize_minmax(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 0.0}, {"amount": 5.0}, {"amount": 10.0}],
        "columns": ["amount"],
        "params": {"method": "minmax"},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results[0]["error"] is None
    normalized = json.loads(results[0]["value"])
    assert normalized == [0.0, 0.5, 1.0]


def test_normalize_on_string_column_is_not_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"name": "alice"}, {"name": "bob"}],
        "columns": ["name"],
        "params": {},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results[0]["value"] is None
    assert "not applicable" in results[0]["error"]


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

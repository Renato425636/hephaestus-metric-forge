from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_metrics_catalog(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    entries = [item for item in body if item["name"] == "balance"]
    contexts = {item["context"] for item in entries}
    assert {"default", "banking"} <= contexts


def test_balance_default_context_is_plain_sum(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert results == [{"column": "amount", "function": "balance", "value": 150.0, "error": None}]


def test_strategy_dispatch_differs_by_context(client: TestClient) -> None:
    base_payload = {
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
    }

    default_response = client.post("/metrics", json={**base_payload, "context": "default"})
    banking_response = client.post(
        "/metrics",
        json={**base_payload, "context": "banking", "params": {"balance": {"reserve_ratio": 0.2}}},
    )

    default_value = default_response.json()[0]["value"]
    banking_value = banking_response.json()[0]["value"]

    assert default_value == 150.0
    assert banking_value == 120.0  # 150 * (1 - 0.2)
    assert default_value != banking_value


def test_unregistered_context_falls_back_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 10.0}, {"amount": 20.0}],
        "columns": ["amount"],
        "functions": ["average"],
        "context": "some_context_never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 15.0


def test_unknown_metric_name_and_context_is_per_item_error(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 10.0}],
        "columns": ["amount"],
        "functions": ["not_a_real_metric"],
        "context": "nonexistent",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_numeric_metric_on_string_column_is_not_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"name": "alice"}, {"name": "bob"}],
        "columns": ["name"],
        "functions": ["balance"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_metrics_endpoint_requires_auth(unauthenticated_client: TestClient) -> None:
    response = unauthenticated_client.post(
        "/metrics",
        json={"data": [{"x": 1}], "columns": ["x"], "functions": ["balance"]},
    )
    assert response.status_code == 401

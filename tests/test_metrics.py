"""Contract-level tests for the `metrics` resource: catalog shape, routing,
and generic error handling that isn't specific to any one metric.

Per-item behavior (happy path, context divergence/fallback, dtype/param
validation) lives in the `tests/test_metrics_*.py` category files.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

_EXPECTED_METRIC_CONTEXTS = {
    "balance": {"default", "retail", "banking"},
    "net_revenue": {"default", "tax_adjusted"},
    "outlier_iqr": {"default", "strict", "lenient"},
    "null_rate": {"default"},
    "cardinality": {"default"},
    "duplicate_rate": {"default"},
    "mean": {"default"},
    "median": {"default"},
    "stddev": {"default"},
    "percentile": {"default"},
}


def test_list_metrics_catalog(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()

    contexts_by_name: dict[str, set[str]] = {}
    for item in body:
        contexts_by_name.setdefault(item["name"], set()).add(item["context"])

    for name, expected_contexts in _EXPECTED_METRIC_CONTEXTS.items():
        assert expected_contexts <= contexts_by_name.get(name, set()), name


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


def test_missing_column_is_per_item_error_for_every_function(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 10.0}],
        "columns": ["missing_col"],
        "functions": ["mean", "balance"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    for result in results:
        assert result["error"] is not None
        assert "not found in data" in result["error"]


def test_metrics_endpoint_requires_auth(unauthenticated_client: TestClient) -> None:
    response = unauthenticated_client.post(
        "/metrics",
        json={"data": [{"x": 1}], "columns": ["x"], "functions": ["balance"]},
    )
    assert response.status_code == 401

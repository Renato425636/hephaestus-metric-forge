"""`metrics` in the financial-domain category: balance, net_revenue.

Both are the catalog's canonical example of real context divergence — the
formula itself changes, not just a cosmetic label.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# balance
# ---------------------------------------------------------------------------


def test_balance_default_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 150.0


def test_balance_retail_matches_default(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "retail",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 150.0


def test_balance_invalid_dtype(client: TestClient) -> None:
    payload = {
        "data": [{"name": "alice"}],
        "columns": ["name"],
        "functions": ["balance"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_balance_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 100.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "banking",
        "params": {"balance": {"pending_ratio": "not_a_float"}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_balance_edge_case_null_values_are_ignored_in_sum(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 10.0}, {"amount": None}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 10.0


def test_balance_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 100.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "some_context_never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 100.0


def test_balance_context_divergence_banking_vs_default(client: TestClient) -> None:
    base_payload = {
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
    }

    default_response = client.post("/metrics", json={**base_payload, "context": "default"})
    banking_response = client.post(
        "/metrics",
        json={
            **base_payload,
            "context": "banking",
            "params": {"balance": {"pending_ratio": 0.2}},
        },
    )

    default_value = default_response.json()[0]["value"]
    banking_value = banking_response.json()[0]["value"]

    assert default_value == 150.0
    assert banking_value == 120.0  # round(150 * (1 - 0.2), 2)
    assert default_value != banking_value


def test_balance_banking_rounds_to_two_decimals(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 33.333}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "banking",
        "params": {"balance": {"pending_ratio": 0.1}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    # 33.333 * 0.9 = 29.9997 -> rounds to 30.0 (banker's rounding)
    assert response.json()[0]["value"] == 30.0


# ---------------------------------------------------------------------------
# net_revenue
# ---------------------------------------------------------------------------


def test_net_revenue_default_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"revenue": 200.0}, {"revenue": 100.0}],
        "columns": ["revenue"],
        "functions": ["net_revenue"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 300.0


def test_net_revenue_invalid_dtype(client: TestClient) -> None:
    payload = {
        "data": [{"name": "alice"}],
        "columns": ["name"],
        "functions": ["net_revenue"],
        "context": "default",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_net_revenue_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"revenue": 100.0}],
        "columns": ["revenue"],
        "functions": ["net_revenue"],
        "context": "tax_adjusted",
        "params": {"net_revenue": {"tax_rate": "not_a_float"}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_net_revenue_edge_case_zero_tax_rate_matches_default(client: TestClient) -> None:
    payload = {
        "data": [{"revenue": 200.0}],
        "columns": ["revenue"],
        "functions": ["net_revenue"],
        "context": "tax_adjusted",
        "params": {"net_revenue": {"tax_rate": 0.0}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 200.0


def test_net_revenue_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"revenue": 200.0}],
        "columns": ["revenue"],
        "functions": ["net_revenue"],
        "context": "some_context_never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 200.0


def test_net_revenue_context_divergence_tax_adjusted_vs_default(client: TestClient) -> None:
    base_payload = {
        "data": [{"revenue": 200.0}, {"revenue": 100.0}],
        "columns": ["revenue"],
        "functions": ["net_revenue"],
    }

    default_response = client.post("/metrics", json={**base_payload, "context": "default"})
    adjusted_response = client.post(
        "/metrics",
        json={
            **base_payload,
            "context": "tax_adjusted",
            "params": {"net_revenue": {"tax_rate": 0.25}},
        },
    )

    default_value = default_response.json()[0]["value"]
    adjusted_value = adjusted_response.json()[0]["value"]

    assert default_value == 300.0
    assert adjusted_value == 225.0  # 300 * (1 - 0.25)
    assert default_value != adjusted_value

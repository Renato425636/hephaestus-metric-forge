"""`metrics` in the descriptive-stats category: mean, median, stddev,
percentile."""

from __future__ import annotations

import math

import pytest
from fastapi.testclient import TestClient

_DATA = [{"x": v} for v in [1.0, 2.0, 3.0, 4.0, 10.0]]

# ---------------------------------------------------------------------------
# mean
# ---------------------------------------------------------------------------


def test_mean_happy_path(client: TestClient) -> None:
    payload = {"data": _DATA, "columns": ["x"], "functions": ["mean"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 4.0


def test_mean_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}], "columns": ["name"], "functions": ["mean"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_mean_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": _DATA,
        "columns": ["x"],
        "functions": ["mean"],
        "context": "context_that_was_never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 4.0


def test_mean_edge_case_single_value(client: TestClient) -> None:
    payload = {"data": [{"x": 7.0}], "columns": ["x"], "functions": ["mean"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 7.0


# ---------------------------------------------------------------------------
# median
# ---------------------------------------------------------------------------


def test_median_happy_path(client: TestClient) -> None:
    payload = {"data": _DATA, "columns": ["x"], "functions": ["median"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 3.0


def test_median_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}], "columns": ["name"], "functions": ["median"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_median_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": _DATA,
        "columns": ["x"],
        "functions": ["median"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 3.0


def test_median_edge_case_single_value(client: TestClient) -> None:
    payload = {"data": [{"x": 7.0}], "columns": ["x"], "functions": ["median"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 7.0


# ---------------------------------------------------------------------------
# stddev
# ---------------------------------------------------------------------------


def test_stddev_happy_path(client: TestClient) -> None:
    payload = {"data": [{"x": 2.0}, {"x": 4.0}], "columns": ["x"], "functions": ["stddev"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    # sample stddev (ddof=1) of [2.0, 4.0] is sqrt(2)
    assert result["value"] == pytest.approx(math.sqrt(2))


def test_stddev_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}], "columns": ["name"], "functions": ["stddev"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_stddev_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"x": 2.0}, {"x": 4.0}],
        "columns": ["x"],
        "functions": ["stddev"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_stddev_edge_case_single_value_is_zero_not_null(client: TestClient) -> None:
    payload = {"data": [{"x": 7.0}], "columns": ["x"], "functions": ["stddev"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 0.0


# ---------------------------------------------------------------------------
# percentile
# ---------------------------------------------------------------------------


def test_percentile_happy_path_p50_matches_median(client: TestClient) -> None:
    payload = {
        "data": _DATA,
        "columns": ["x"],
        "functions": ["percentile"],
        "params": {"percentile": {"p": 50.0}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 3.0


def test_percentile_defaults_to_p50(client: TestClient) -> None:
    payload = {"data": _DATA, "columns": ["x"], "functions": ["percentile"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 3.0


def test_percentile_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}], "columns": ["name"], "functions": ["percentile"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_percentile_invalid_params_out_of_range(client: TestClient) -> None:
    payload = {
        "data": _DATA,
        "columns": ["x"],
        "functions": ["percentile"],
        "params": {"percentile": {"p": 150.0}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_percentile_edge_case_p0_and_p100_are_min_and_max(client: TestClient) -> None:
    p0_response = client.post(
        "/metrics",
        json={
            "data": _DATA,
            "columns": ["x"],
            "functions": ["percentile"],
            "params": {"percentile": {"p": 0.0}},
        },
    )
    p100_response = client.post(
        "/metrics",
        json={
            "data": _DATA,
            "columns": ["x"],
            "functions": ["percentile"],
            "params": {"percentile": {"p": 100.0}},
        },
    )
    assert p0_response.json()[0]["value"] == 1.0
    assert p100_response.json()[0]["value"] == 10.0

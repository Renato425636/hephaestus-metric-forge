"""`functions` in the dtype-transformation category: cast_dtype, bucketize."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# cast_dtype
# ---------------------------------------------------------------------------


def test_cast_dtype_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1}, {"amount": 2}],
        "columns": ["amount"],
        "params": {"target_dtype": "Float64"},
    }
    response = client.post("/functions/cast_dtype", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == "Float64"


def test_cast_dtype_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}],
        "columns": ["label"],
        "params": {"target_dtype": "Utf8"},
    }
    response = client.post("/functions/cast_dtype", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_cast_dtype_invalid_params_unknown_target(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1}],
        "columns": ["amount"],
        "params": {"target_dtype": "NotARealDtype"},
    }
    response = client.post("/functions/cast_dtype", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "unsupported target_dtype" in result["error"]


def test_cast_dtype_edge_case_incompatible_value(client: TestClient) -> None:
    payload = {
        "data": [{"label": "not-a-number"}],
        "columns": ["label"],
        "params": {"target_dtype": "Int64"},
    }
    response = client.post("/functions/cast_dtype", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


# ---------------------------------------------------------------------------
# bucketize
# ---------------------------------------------------------------------------


def test_bucketize_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}, {"amount": 5.0}, {"amount": 15.0}, {"amount": 25.0}],
        "columns": ["amount"],
        "params": {"bins": [10.0, 20.0], "labels": ["low", "mid", "high"]},
    }
    response = client.post("/functions/bucketize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    histogram = json.loads(result["value"])
    assert histogram == {"low": 2, "mid": 1, "high": 1}


def test_bucketize_invalid_dtype(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}],
        "columns": ["label"],
        "params": {"bins": [1.0, 2.0]},
    }
    response = client.post("/functions/bucketize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_bucketize_invalid_params_missing_bins(client: TestClient) -> None:
    payload = {"data": [{"amount": 1.0}], "columns": ["amount"], "params": {}}
    response = client.post("/functions/bucketize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_bucketize_edge_case_mismatched_labels_length(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 5.0}],
        "columns": ["amount"],
        "params": {"bins": [10.0, 20.0], "labels": ["only_one"]},
    }
    response = client.post("/functions/bucketize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------


def test_normalize_happy_path_minmax(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 0.0}, {"amount": 5.0}, {"amount": 10.0}],
        "columns": ["amount"],
        "params": {"method": "minmax"},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert json.loads(result["value"]) == [0.0, 0.5, 1.0]


def test_normalize_happy_path_zscore(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 2.0}, {"amount": 4.0}],
        "columns": ["amount"],
        "params": {"method": "zscore"},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    normalized = json.loads(result["value"])
    # sample stddev (ddof=1) of [2, 4] is sqrt(2), so z-scores are +/- 1/sqrt(2)
    assert normalized == pytest.approx([-0.7071067811865475, 0.7071067811865475])


def test_normalize_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}, {"name": "bob"}], "columns": ["name"], "params": {}}
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_normalize_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}, {"amount": 2.0}],
        "columns": ["amount"],
        "params": {"method": "not_a_real_method"},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "unsupported method" in result["error"]


def test_normalize_edge_case_constant_column_minmax(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 5.0}, {"amount": 5.0}],
        "columns": ["amount"],
        "params": {"method": "minmax"},
    }
    response = client.post("/functions/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    # span is 0 -> falls back to (series - min) instead of dividing by zero
    assert json.loads(result["value"]) == [0.0, 0.0]

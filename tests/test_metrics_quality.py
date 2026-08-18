"""`metrics` in the data-quality category: null_rate, cardinality,
duplicate_rate, outlier_iqr (default/strict/lenient)."""

from __future__ import annotations

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# null_rate
# ---------------------------------------------------------------------------


def test_null_rate_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"x": 1}, {"x": None}, {"x": None}, {"x": 4}],
        "columns": ["x"],
        "functions": ["null_rate"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 0.5


def test_null_rate_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}, {"label": None}],
        "columns": ["label"],
        "functions": ["null_rate"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_null_rate_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"x": 1}, {"x": None}],
        "columns": ["x"],
        "functions": ["null_rate"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 0.5


def test_null_rate_edge_case_no_nulls(client: TestClient) -> None:
    payload = {"data": [{"x": 1}, {"x": 2}], "columns": ["x"], "functions": ["null_rate"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0.0


# ---------------------------------------------------------------------------
# cardinality
# ---------------------------------------------------------------------------


def test_cardinality_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a"}, {"category": "a"}, {"category": "b"}],
        "columns": ["category"],
        "functions": ["cardinality"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 2


def test_cardinality_all_dtypes_applicable(client: TestClient) -> None:
    payload = {"data": [{"x": 1}, {"x": 2}], "columns": ["x"], "functions": ["cardinality"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_cardinality_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a"}, {"category": "b"}],
        "columns": ["category"],
        "functions": ["cardinality"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 2


def test_cardinality_edge_case_single_value(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a"}, {"category": "a"}],
        "columns": ["category"],
        "functions": ["cardinality"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 1


# ---------------------------------------------------------------------------
# duplicate_rate
# ---------------------------------------------------------------------------


def test_duplicate_rate_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 3}],
        "columns": ["id"],
        "functions": ["duplicate_rate"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 0.25  # (4 - 3) / 4


def test_duplicate_rate_all_dtypes_applicable(client: TestClient) -> None:
    payload = {"data": [{"label": "a"}], "columns": ["label"], "functions": ["duplicate_rate"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_duplicate_rate_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 1}],
        "columns": ["id"],
        "functions": ["duplicate_rate"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0.5


def test_duplicate_rate_edge_case_all_unique(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 2}],
        "columns": ["id"],
        "functions": ["duplicate_rate"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0.0


# ---------------------------------------------------------------------------
# outlier_iqr
# ---------------------------------------------------------------------------

_OUTLIER_DATA = [{"x": v} for v in [10.0, 11.0, 12.0, 13.0, 14.0, 100.0]]


def test_outlier_iqr_default_happy_path(client: TestClient) -> None:
    payload = {"data": _OUTLIER_DATA, "columns": ["x"], "functions": ["outlier_iqr"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1  # the 100.0 outlier


def test_outlier_iqr_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"name": "alice"}], "columns": ["name"], "functions": ["outlier_iqr"]}
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_outlier_iqr_invalid_params(client: TestClient) -> None:
    payload = {
        "data": _OUTLIER_DATA,
        "columns": ["x"],
        "functions": ["outlier_iqr"],
        "params": {"outlier_iqr": {"k": "not_a_float"}},
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_outlier_iqr_edge_case_empty_after_dropping_nulls(client: TestClient) -> None:
    payload = {
        "data": [{"x": None}, {"x": None}],
        "columns": ["x"],
        "functions": ["outlier_iqr"],
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None  # dtype is Null -> "not applicable", not a crash


def test_outlier_iqr_context_divergence_strict_vs_lenient(client: TestClient) -> None:
    # A mild outlier (20.0): tight fences (k=1.0/1.5) flag it, the k=3.0
    # lenient fence is wide enough to absorb it — genuine per-context divergence.
    borderline_data = [{"x": v} for v in [10.0, 11.0, 12.0, 13.0, 14.0, 20.0]]

    strict_response = client.post(
        "/metrics",
        json={
            "data": borderline_data,
            "columns": ["x"],
            "functions": ["outlier_iqr"],
            "context": "strict",
        },
    )
    lenient_response = client.post(
        "/metrics",
        json={
            "data": borderline_data,
            "columns": ["x"],
            "functions": ["outlier_iqr"],
            "context": "lenient",
        },
    )

    strict_value = strict_response.json()[0]["value"]
    lenient_value = lenient_response.json()[0]["value"]

    assert strict_value == 1
    assert lenient_value == 0
    assert strict_value != lenient_value


def test_outlier_iqr_context_fallback_to_default(client: TestClient) -> None:
    payload = {
        "data": _OUTLIER_DATA,
        "columns": ["x"],
        "functions": ["outlier_iqr"],
        "context": "never_registered",
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1  # falls back to default (k=1.5), same as test above

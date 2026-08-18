"""`functions` in the reshape/aggregation category: groupby_agg, pivot, melt."""

from __future__ import annotations

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# groupby_agg
# ---------------------------------------------------------------------------


def test_groupby_agg_happy_path_sum(client: TestClient) -> None:
    payload = {
        "data": [
            {"category": "a", "qty": 1},
            {"category": "a", "qty": 2},
            {"category": "b", "qty": 3},
        ],
        "columns": ["qty"],
        "params": {"by": ["category"], "agg": {"qty": "sum"}},
    }
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 6.0  # 1+2+3, roll-up of both groups' sums


def test_groupby_agg_count_sums_back_to_row_count(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a"}, {"category": "a"}, {"category": "b"}],
        "columns": ["category"],
        "params": {"by": ["category"]},  # agg defaults to "count" per column
    }
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 3.0


def test_groupby_agg_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}, {"label": "b"}],
        "columns": ["label"],
        "params": {"by": ["label"]},
    }
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_groupby_agg_invalid_params_missing_by(client: TestClient) -> None:
    payload = {"data": [{"qty": 1}], "columns": ["qty"], "params": {}}
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_groupby_agg_invalid_agg_name(client: TestClient) -> None:
    payload = {
        "data": [{"category": "a", "qty": 1}],
        "columns": ["qty"],
        "params": {"by": ["category"], "agg": {"qty": "not_a_real_agg"}},
    }
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "unsupported agg" in result["error"]


def test_groupby_agg_edge_case_single_group(client: TestClient) -> None:
    payload = {
        "data": [{"category": "only", "qty": 5}, {"category": "only", "qty": 5}],
        "columns": ["qty"],
        "params": {"by": ["category"], "agg": {"qty": "mean"}},
    }
    response = client.post("/functions/groupby_agg", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 5.0


# ---------------------------------------------------------------------------
# pivot
# ---------------------------------------------------------------------------


def test_pivot_happy_path(client: TestClient) -> None:
    payload = {
        "data": [
            {"region": "west", "sku": "a", "qty": 1},
            {"region": "west", "sku": "b", "qty": 2},
            {"region": "east", "sku": "a", "qty": 3},
        ],
        "columns": ["qty"],
        "params": {"index": "region", "on": "sku", "agg": "sum"},
    }
    response = client.post("/functions/pivot", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 2  # skus a, b -> 2 value columns


def test_pivot_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"region": "west", "sku": "a", "label": "x"}],
        "columns": ["label"],
        "params": {"index": "region", "on": "sku"},
    }
    response = client.post("/functions/pivot", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_pivot_invalid_params_missing_required_field(client: TestClient) -> None:
    payload = {
        "data": [{"region": "west", "sku": "a", "qty": 1}],
        "columns": ["qty"],
        "params": {"index": "region"},  # missing required "on"
    }
    response = client.post("/functions/pivot", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_pivot_edge_case_unknown_index_column(client: TestClient) -> None:
    payload = {
        "data": [{"region": "west", "sku": "a", "qty": 1}],
        "columns": ["qty"],
        "params": {"index": "does_not_exist", "on": "sku"},
    }
    response = client.post("/functions/pivot", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


# ---------------------------------------------------------------------------
# melt
# ---------------------------------------------------------------------------


def test_melt_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1, "a": 10, "b": 100}, {"id": 2, "a": 20, "b": 200}],
        "columns": ["a"],
        "params": {"id_vars": ["id"], "value_vars": ["a", "b"]},
    }
    response = client.post("/functions/melt", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 4  # 2 id rows * 2 value_vars


def test_melt_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1, "label": "x"}],
        "columns": ["label"],
        "params": {"id_vars": ["id"]},
    }
    response = client.post("/functions/melt", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_melt_invalid_params_missing_id_vars(client: TestClient) -> None:
    payload = {"data": [{"id": 1, "a": 10}], "columns": ["a"], "params": {}}
    response = client.post("/functions/melt", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_melt_edge_case_value_vars_defaults_to_remaining_columns(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1, "a": 10, "b": 100}],
        "columns": ["a"],
        "params": {"id_vars": ["id"]},
    }
    response = client.post("/functions/melt", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 2  # 1 id row * (a, b) value_vars

"""`functions` in the cleaning category: dedupe, drop_nulls, fill_nulls,
trim_whitespace, normalize_case.

Every item follows the same coverage template: happy path, invalid dtype
(skipped with a note when the function accepts `applicable_dtypes=["any"]`,
since no dtype can be "invalid" for it), invalid params, and edge cases.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# dedupe
# ---------------------------------------------------------------------------


def test_dedupe_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 3}, {"id": 3}],
        "columns": ["id"],
        "params": {},
    }
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 2


def test_dedupe_all_dtypes_applicable(client: TestClient) -> None:
    """dedupe declares applicable_dtypes=["any"] — no dtype is ever rejected."""
    payload = {
        "data": [{"label": "a"}, {"label": "a"}, {"label": "b"}],
        "columns": ["label"],
        "params": {},
    }
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1


def test_dedupe_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"id": 1}, {"id": 2}],
        "columns": ["id"],
        "params": {"keep": "middle"},  # not "first"/"last"
    }
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_dedupe_edge_case_empty_data(client: TestClient) -> None:
    payload = {"data": [], "columns": ["id"], "params": {}}
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is not None  # column 'id' doesn't exist on an empty frame


def test_dedupe_edge_case_all_unique(client: TestClient) -> None:
    payload = {"data": [{"id": 1}, {"id": 2}, {"id": 3}], "columns": ["id"], "params": {}}
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0


def test_dedupe_subset_param_across_multiple_columns(client: TestClient) -> None:
    payload = {
        "data": [
            {"region": "west", "sku": "a"},
            {"region": "west", "sku": "a"},
            {"region": "east", "sku": "a"},
        ],
        "columns": ["region"],
        "params": {"subset": ["region", "sku"]},
    }
    response = client.post("/functions/dedupe", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1


# ---------------------------------------------------------------------------
# drop_nulls
# ---------------------------------------------------------------------------


def test_drop_nulls_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}, {"amount": None}, {"amount": 3.0}],
        "columns": ["amount"],
        "params": {},
    }
    response = client.post("/functions/drop_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1


def test_drop_nulls_all_dtypes_applicable(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}, {"label": None}],
        "columns": ["label"],
        "params": {},
    }
    response = client.post("/functions/drop_nulls", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["error"] is None


def test_drop_nulls_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}],
        "columns": ["amount"],
        "params": {"subset": "not_a_list"},
    }
    response = client.post("/functions/drop_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_drop_nulls_edge_case_no_nulls(client: TestClient) -> None:
    payload = {"data": [{"amount": 1.0}, {"amount": 2.0}], "columns": ["amount"], "params": {}}
    response = client.post("/functions/drop_nulls", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0


def test_drop_nulls_edge_case_all_nulls(client: TestClient) -> None:
    payload = {"data": [{"amount": None}, {"amount": None}], "columns": ["amount"], "params": {}}
    response = client.post("/functions/drop_nulls", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 2


# ---------------------------------------------------------------------------
# fill_nulls
# ---------------------------------------------------------------------------


def test_fill_nulls_happy_path_constant(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}, {"amount": None}, {"amount": None}],
        "columns": ["amount"],
        "params": {"strategy": "constant", "value": 0.0},
    }
    response = client.post("/functions/fill_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 2


def test_fill_nulls_mean_strategy_on_string_column_is_rejected(client: TestClient) -> None:
    payload = {
        "data": [{"label": "a"}, {"label": None}],
        "columns": ["label"],
        "params": {"strategy": "mean"},
    }
    response = client.post("/functions/fill_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "numeric" in result["error"]


def test_fill_nulls_invalid_params(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}],
        "columns": ["amount"],
        "params": {"strategy": "not_a_real_strategy"},
    }
    response = client.post("/functions/fill_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_fill_nulls_constant_without_value_is_an_error(client: TestClient) -> None:
    payload = {
        "data": [{"amount": None}],
        "columns": ["amount"],
        "params": {"strategy": "constant"},
    }
    response = client.post("/functions/fill_nulls", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "value" in result["error"]


def test_fill_nulls_edge_case_no_nulls(client: TestClient) -> None:
    payload = {
        "data": [{"amount": 1.0}, {"amount": 2.0}],
        "columns": ["amount"],
        "params": {"strategy": "forward"},
    }
    response = client.post("/functions/fill_nulls", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0


# ---------------------------------------------------------------------------
# trim_whitespace
# ---------------------------------------------------------------------------


def test_trim_whitespace_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"name": "  alice  "}, {"name": "bob"}],
        "columns": ["name"],
        "params": {},
    }
    response = client.post("/functions/trim_whitespace", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 1


def test_trim_whitespace_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"amount": 1.0}], "columns": ["amount"], "params": {}}
    response = client.post("/functions/trim_whitespace", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_trim_whitespace_invalid_params(client: TestClient) -> None:
    payload = {"data": [{"name": "a"}], "columns": ["name"], "params": {"mode": "diagonal"}}
    response = client.post("/functions/trim_whitespace", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_trim_whitespace_edge_case_null_values_are_unchanged(client: TestClient) -> None:
    payload = {"data": [{"name": None}, {"name": "clean"}], "columns": ["name"], "params": {}}
    response = client.post("/functions/trim_whitespace", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0


# ---------------------------------------------------------------------------
# normalize_case
# ---------------------------------------------------------------------------


def test_normalize_case_happy_path(client: TestClient) -> None:
    payload = {
        "data": [{"name": "Alice"}, {"name": "bob"}],
        "columns": ["name"],
        "params": {"mode": "upper"},
    }
    response = client.post("/functions/normalize_case", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["error"] is None
    assert result["value"] == 2


def test_normalize_case_invalid_dtype(client: TestClient) -> None:
    payload = {"data": [{"amount": 1.0}], "columns": ["amount"], "params": {}}
    response = client.post("/functions/normalize_case", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert "not applicable" in result["error"]


def test_normalize_case_invalid_params(client: TestClient) -> None:
    payload = {"data": [{"name": "a"}], "columns": ["name"], "params": {"mode": "sideways"}}
    response = client.post("/functions/normalize_case", json=payload)
    assert response.status_code == 200
    result = response.json()[0]
    assert result["value"] is None
    assert result["error"] is not None


def test_normalize_case_edge_case_already_normalized(client: TestClient) -> None:
    payload = {
        "data": [{"name": "alice"}, {"name": "bob"}],
        "columns": ["name"],
        "params": {"mode": "lower"},
    }
    response = client.post("/functions/normalize_case", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["value"] == 0

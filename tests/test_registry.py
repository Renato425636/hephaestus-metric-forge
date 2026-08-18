from __future__ import annotations

from typing import Any

import polars as pl
import pytest

from app.models import FunctionSpec, MetricSpec
from app.registry import (
    dtype_category,
    is_applicable,
    register_function,
    register_metric,
    resolve_function_strategy,
    resolve_metric_strategy,
)


def test_register_and_resolve_function() -> None:
    spec = FunctionSpec(name="_test_fn_registry", applicable_dtypes=["any"], param_schema=None)

    @register_function(spec)
    def _strategy(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
        return 42

    fn, resolved_spec = resolve_function_strategy("_test_fn_registry")
    assert resolved_spec is spec
    assert fn(pl.DataFrame(), "x", {}) == 42


def test_resolve_unknown_function_raises() -> None:
    with pytest.raises(KeyError):
        resolve_function_strategy("_definitely_not_registered")


def test_register_and_resolve_metric_exact_context() -> None:
    spec = MetricSpec(name="_test_metric_ctx", applicable_dtypes=["numeric"], param_schema=None)

    @register_metric(spec, context="special")
    def _strategy(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
        return 1

    fn, resolved_spec = resolve_metric_strategy("_test_metric_ctx", "special")
    assert resolved_spec is spec
    assert fn(pl.DataFrame(), "x", {}) == 1


def test_resolve_metric_falls_back_to_default_context() -> None:
    spec = MetricSpec(
        name="_test_metric_fallback", applicable_dtypes=["numeric"], param_schema=None
    )

    @register_metric(spec, context="default")
    def _strategy(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
        return 7

    fn, _ = resolve_metric_strategy("_test_metric_fallback", "context_that_was_never_registered")
    assert fn(pl.DataFrame(), "x", {}) == 7


def test_resolve_metric_unknown_name_raises() -> None:
    with pytest.raises(KeyError):
        resolve_metric_strategy("_definitely_not_a_metric", "default")


@pytest.mark.parametrize(
    ("dtype", "expected"),
    [
        (pl.Int64, "numeric"),
        (pl.Float64, "numeric"),
        (pl.Utf8, "string"),
        (pl.Boolean, "other"),
        (pl.Date, "other"),
    ],
)
def test_dtype_category(dtype: pl.DataType, expected: str) -> None:
    assert dtype_category(dtype) == expected


def test_is_applicable() -> None:
    assert is_applicable("numeric", ["numeric", "string"])
    assert not is_applicable("string", ["numeric"])
    assert is_applicable("other", ["any"])

"""Strategy Pattern registries for `functions` (1D key) and `metrics` (2D key).

Resolution is a plain dict lookup against strategies registered ahead of time via
decorators — no inheritance, no abstract base classes, no object construction
(hence "Strategy", not "Factory"). Adding a new function or metric means adding a
new decorated callable; routing and validation code never changes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import polars as pl

from app.models import FunctionSpec, MetricSpec

FunctionCallable = Callable[[pl.DataFrame, str, dict[str, Any]], Any]
MetricCallable = Callable[[pl.DataFrame, str, dict[str, Any]], Any]

_FUNCTIONS_REGISTRY: dict[str, tuple[FunctionCallable, FunctionSpec]] = {}
_METRICS_REGISTRY: dict[tuple[str, str], tuple[MetricCallable, MetricSpec]] = {}


def register_function(spec: FunctionSpec) -> Callable[[FunctionCallable], FunctionCallable]:
    def decorator(fn: FunctionCallable) -> FunctionCallable:
        _FUNCTIONS_REGISTRY[spec.name] = (fn, spec)
        return fn

    return decorator


def resolve_function_strategy(name: str) -> tuple[FunctionCallable, FunctionSpec]:
    if name not in _FUNCTIONS_REGISTRY:
        raise KeyError(f"function '{name}' not found")
    return _FUNCTIONS_REGISTRY[name]


def register_metric(
    spec: MetricSpec, context: str = "default"
) -> Callable[[MetricCallable], MetricCallable]:
    def decorator(fn: MetricCallable) -> MetricCallable:
        _METRICS_REGISTRY[(spec.name, context)] = (fn, spec)
        return fn

    return decorator


def resolve_metric_strategy(
    metric_name: str, context: str = "default"
) -> tuple[MetricCallable, MetricSpec]:
    key = (metric_name, context)
    if key not in _METRICS_REGISTRY:
        key = (metric_name, "default")  # fallback: unknown/missing context -> default
    if key not in _METRICS_REGISTRY:
        raise KeyError(f"metric '{metric_name}' not found for context '{context}' or default")
    return _METRICS_REGISTRY[key]


def list_functions() -> list[FunctionSpec]:
    return [spec for _, spec in _FUNCTIONS_REGISTRY.values()]


def list_metrics() -> list[tuple[str, MetricSpec]]:
    """Returns (context, spec) pairs — one per registered (metric_name, context)."""
    return [(context, spec) for (_, context), (_, spec) in _METRICS_REGISTRY.items()]


def dtype_category(dtype: pl.DataType) -> str:
    if dtype.is_numeric():
        return "numeric"
    if dtype == pl.Utf8:
        return "string"
    return "other"


def is_applicable(category: str, applicable_dtypes: list[str]) -> bool:
    return "any" in applicable_dtypes or category in applicable_dtypes

"""`average` — only registered for the `default` context.

Requesting it under an unregistered context (e.g. `banking`) exercises the
resolver's fallback-to-default behavior in `resolve_metric_strategy`.
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="average", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def average_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    # Dtype is narrowed to "numeric" via applicable_dtypes before this strategy
    # runs; polars' aggregation stubs stay dtype-generic, so mypy needs a hint.
    mean = cast(float | None, df[column].mean())
    return mean if mean is not None else 0.0

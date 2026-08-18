"""`mean` — arithmetic average of a numeric column.

Single `default` context: this is the catalog's reference case for the
resolver's fallback-to-default behavior — requesting `mean` under any
unregistered context still resolves here via
[`resolve_metric_strategy`][app.registry.resolve_metric_strategy].
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="mean", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def mean_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    value = cast(float | None, df[column].mean())
    return value if value is not None else 0.0

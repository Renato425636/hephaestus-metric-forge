"""`median` — 50th percentile of a numeric column. Single `default` context:
standard descriptive statistic, domain-independent."""

from __future__ import annotations

from typing import Any, cast

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="median", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def median_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    value = cast(float | None, df[column].median())
    return value if value is not None else 0.0

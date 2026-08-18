"""`stddev` — sample standard deviation (ddof=1) of a numeric column. Single
`default` context: standard descriptive statistic, domain-independent.

A column with fewer than 2 non-null values has an undefined sample stddev;
that returns `0.0` here rather than `null`/`NaN`, keeping the scalar
`value` contract simple for callers.
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="stddev", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def stddev_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    value = cast(float | None, df[column].std())
    return value if value is not None else 0.0

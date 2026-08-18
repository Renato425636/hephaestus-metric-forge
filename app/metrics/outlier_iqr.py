"""`outlier_iqr` — count of values outside the Tukey IQR fence
`[Q1 - k*IQR, Q3 + k*IQR]`.

The three registered contexts genuinely diverge (not just cosmetically):
different default `k` values shift how many values get flagged as outliers
for the *same* input data.

- `default` — `k=1.5`, the standard Tukey fence.
- `strict`  — `k=1.0`, a tighter fence: flags *more* values as outliers.
- `lenient` — `k=3.0`, a looser fence: flags *fewer* values as outliers.

`params.k` overrides the context's default `k` when provided, for callers
who want the count/context semantics but a custom threshold.
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl
from pydantic import BaseModel

from app.models import MetricSpec
from app.registry import register_metric


class OutlierIqrParams(BaseModel):
    k: float | None = None


_SPEC = MetricSpec(name="outlier_iqr", applicable_dtypes=["numeric"], param_schema=OutlierIqrParams)


def _count_outliers(df: pl.DataFrame, column: str, k: float) -> int:
    series = df[column].cast(pl.Float64).drop_nulls()
    if series.len() == 0:
        return 0

    q1 = cast(float, series.quantile(0.25))
    q3 = cast(float, series.quantile(0.75))
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr

    return int(((series < lower) | (series > upper)).sum())


@register_metric(_SPEC, context="default")
def outlier_iqr_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = OutlierIqrParams.model_validate(params)
    return _count_outliers(df, column, parsed.k if parsed.k is not None else 1.5)


@register_metric(_SPEC, context="strict")
def outlier_iqr_strict(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = OutlierIqrParams.model_validate(params)
    return _count_outliers(df, column, parsed.k if parsed.k is not None else 1.0)


@register_metric(_SPEC, context="lenient")
def outlier_iqr_lenient(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = OutlierIqrParams.model_validate(params)
    return _count_outliers(df, column, parsed.k if parsed.k is not None else 3.0)

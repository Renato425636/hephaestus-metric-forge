"""`null_rate` — fraction of null values in a column (0.0–1.0). Single
`default` context: this is a structural data-quality signal, not something
that meaningfully diverges by domain."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="null_rate", applicable_dtypes=["any"], param_schema=None),
    context="default",
)
def null_rate_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    if df.height == 0:
        return 0.0
    return df[column].null_count() / df.height

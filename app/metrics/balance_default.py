"""`balance` in the default (generic) context: plain sum of the column."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="balance", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def balance_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    return float(df[column].sum())

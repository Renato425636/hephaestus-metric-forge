"""`cardinality` — count of distinct values in a column. Single `default`
context: structural data-quality signal, domain-independent."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="cardinality", applicable_dtypes=["any"], param_schema=None),
    context="default",
)
def cardinality_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    return df[column].n_unique()

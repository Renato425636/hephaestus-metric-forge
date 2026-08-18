"""`duplicate_rate` — fraction of rows that are duplicates on a column
(`(height - n_unique) / height`). Single `default` context: structural
data-quality signal, domain-independent."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="duplicate_rate", applicable_dtypes=["any"], param_schema=None),
    context="default",
)
def duplicate_rate_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    if df.height == 0:
        return 0.0
    unique = df[column].n_unique()
    return (df.height - unique) / df.height

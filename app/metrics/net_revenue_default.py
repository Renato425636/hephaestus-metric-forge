"""`net_revenue` — context-dependent revenue calculation.

- `default`: gross sum of the column, no deductions.
- `tax_adjusted` (see `net_revenue_tax_adjusted.py`): applies `tax_rate` to
  each transaction *before* summing.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric


@register_metric(
    MetricSpec(name="net_revenue", applicable_dtypes=["numeric"], param_schema=None),
    context="default",
)
def net_revenue_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    return float(df[column].sum())

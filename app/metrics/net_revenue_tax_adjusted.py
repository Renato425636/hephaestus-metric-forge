"""`net_revenue` in the `tax_adjusted` context.

Diverges from `default` (see `net_revenue_default.py`) by deducting
`params.tax_rate` from *each* transaction before summing, rather than
taxing the aggregate — sums post-tax amounts directly.
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl
from pydantic import BaseModel

from app.models import MetricSpec
from app.registry import register_metric


class TaxAdjustedParams(BaseModel):
    tax_rate: float = 0.15


@register_metric(
    MetricSpec(name="net_revenue", applicable_dtypes=["numeric"], param_schema=TaxAdjustedParams),
    context="tax_adjusted",
)
def net_revenue_tax_adjusted(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    parsed = TaxAdjustedParams.model_validate(params)
    after_tax = df[column].cast(pl.Float64) * (1 - parsed.tax_rate)
    total = cast(float | None, after_tax.sum())
    return total if total is not None else 0.0

"""`balance` in the `banking` context: sum less a fractional reserve requirement.

Deliberately different math from the default context so strategy dispatch is
observable end-to-end (same metric name, different context, different value).
"""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import MetricSpec
from app.registry import register_metric


class ReserveRatioParams(BaseModel):
    reserve_ratio: float = 0.1  # fraction held back as reserve, e.g. 0.1 = 10%


@register_metric(
    MetricSpec(name="balance", applicable_dtypes=["numeric"], param_schema=ReserveRatioParams),
    context="banking",
)
def balance_banking(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    parsed = ReserveRatioParams.model_validate(params)
    total = float(df[column].sum())
    return total * (1 - parsed.reserve_ratio)

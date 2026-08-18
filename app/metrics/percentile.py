"""`percentile` — arbitrary percentile (`params.p`, 0-100) of a numeric
column. Single `default` context: standard descriptive statistic,
domain-independent."""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel, Field

from app.models import MetricSpec
from app.registry import register_metric


class PercentileParams(BaseModel):
    p: float = Field(default=50.0, ge=0.0, le=100.0)


@register_metric(
    MetricSpec(name="percentile", applicable_dtypes=["numeric"], param_schema=PercentileParams),
    context="default",
)
def percentile_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    parsed = PercentileParams.model_validate(params)
    value = df[column].quantile(parsed.p / 100.0)
    return value if value is not None else 0.0

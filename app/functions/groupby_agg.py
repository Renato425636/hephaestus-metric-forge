"""`groupby_agg` — groups the whole dataset by `params.by`, aggregates the
requested column per `params.agg`, and returns the sum of that aggregate
across all resulting groups.

The per-group breakdown isn't representable in the scalar `value` contract,
so this returns a single roll-up number: enough to confirm the grouping/agg
combination ran correctly (e.g. `agg="count"` sums back to `df.height`).
"""

from __future__ import annotations

from typing import Any, cast

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function

_SUPPORTED_AGGS = {"count", "sum", "mean", "min", "max"}


class GroupByAggParams(BaseModel):
    by: list[str]
    agg: dict[str, str] = {}


@register_function(
    FunctionSpec(name="groupby_agg", applicable_dtypes=["any"], param_schema=GroupByAggParams)
)
def groupby_agg(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    parsed = GroupByAggParams.model_validate(params)
    agg_name = parsed.agg.get(column, "count")

    if agg_name not in _SUPPORTED_AGGS:
        raise ValueError(
            f"unsupported agg '{agg_name}' for column '{column}', "
            f"expected one of {sorted(_SUPPORTED_AGGS)}"
        )

    if agg_name == "count":
        expr = pl.len().alias("agg")
    else:
        expr = getattr(pl.col(column), agg_name)().alias("agg")
    grouped = df.group_by(parsed.by).agg(expr)
    total = cast(float | int | None, grouped["agg"].sum())
    return float(total) if total is not None else 0.0

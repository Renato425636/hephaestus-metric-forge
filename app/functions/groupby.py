"""`groupby` — groups rows by `column`, optionally aggregating another column."""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function

_SUPPORTED_AGGS = {"count", "sum", "mean"}


class GroupByParams(BaseModel):
    agg_column: str | None = None
    agg: str = "count"


@register_function(
    FunctionSpec(name="groupby", applicable_dtypes=["any"], param_schema=GroupByParams)
)
def groupby(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int | float:
    parsed = GroupByParams.model_validate(params)

    if parsed.agg not in _SUPPORTED_AGGS:
        raise ValueError(
            f"unsupported agg '{parsed.agg}', expected one of {sorted(_SUPPORTED_AGGS)}"
        )

    if parsed.agg == "count" or parsed.agg_column is None:
        return int(df.select(pl.col(column)).n_unique())

    grouped = df.group_by(column).agg(getattr(pl.col(parsed.agg_column), parsed.agg)().alias("agg"))
    return float(grouped["agg"].sum())

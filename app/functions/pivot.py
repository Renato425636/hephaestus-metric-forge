"""`pivot` — reshapes long to wide by `params.on`, indexed by `params.index`,
with cell values from `params.values` (defaults to the requested column).

Returns the number of resulting value columns (i.e. the cardinality of
`params.on`) rather than the pivoted table itself, since `value` is scalar.
"""

from __future__ import annotations

from typing import Any, Literal

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class PivotParams(BaseModel):
    index: str
    on: str
    values: str | None = None
    agg: Literal["first", "sum", "mean", "count"] = "first"


# Public API keeps the friendlier "count"; polars' own literal spells it "len".
_AGG_MAP: dict[str, Literal["first", "sum", "mean", "len"]] = {
    "first": "first",
    "sum": "sum",
    "mean": "mean",
    "count": "len",
}


@register_function(FunctionSpec(name="pivot", applicable_dtypes=["any"], param_schema=PivotParams))
def pivot(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = PivotParams.model_validate(params)
    values_col = parsed.values if parsed.values is not None else column

    pivoted = df.pivot(
        on=parsed.on,
        index=parsed.index,
        values=values_col,
        aggregate_function=_AGG_MAP[parsed.agg],
    )
    return pivoted.width - 1  # exclude the index column

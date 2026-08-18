"""`fill_nulls` — count of nulls that would be filled in a column.

`strategy="mean"|"median"` requires a numeric column (validated at runtime,
since `applicable_dtypes=["any"]` also has to admit `"forward"`/`"constant"`
on string/other columns). `strategy="constant"` requires a non-null `value`.
"""

from __future__ import annotations

from typing import Any, Literal

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import dtype_category, register_function


class FillNullsParams(BaseModel):
    strategy: Literal["mean", "median", "forward", "constant"] = "constant"
    value: Any | None = None


@register_function(
    FunctionSpec(name="fill_nulls", applicable_dtypes=["any"], param_schema=FillNullsParams)
)
def fill_nulls(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = FillNullsParams.model_validate(params)
    series = df[column]
    null_count: int = series.null_count()

    if parsed.strategy == "constant":
        if parsed.value is None:
            raise ValueError("strategy 'constant' requires a non-null 'value' param")
        series.fill_null(parsed.value)
    elif parsed.strategy == "forward":
        series.fill_null(strategy="forward")
    else:
        if dtype_category(series.dtype) != "numeric":
            raise ValueError(f"strategy '{parsed.strategy}' requires a numeric column")
        if parsed.strategy == "mean":
            series.fill_null(strategy="mean")
        else:
            # polars' fill_null strategy=... doesn't support "median" natively.
            series.fill_null(series.median())

    return null_count

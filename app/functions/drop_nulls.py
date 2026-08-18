"""`drop_nulls` — count of rows that would be dropped for having a null in
`params.subset` (defaults to just the requested column)."""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class DropNullsParams(BaseModel):
    subset: list[str] | None = None


@register_function(
    FunctionSpec(name="drop_nulls", applicable_dtypes=["any"], param_schema=DropNullsParams)
)
def drop_nulls(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = DropNullsParams.model_validate(params)
    subset = parsed.subset if parsed.subset else [column]
    remaining = df.drop_nulls(subset=subset).height
    return df.height - remaining

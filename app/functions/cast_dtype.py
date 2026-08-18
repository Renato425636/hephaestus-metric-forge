"""`cast_dtype` — casts a column to `params.target_dtype`, strictly (any value
that doesn't convert raises, surfaced as a per-item error by the router).

Returns the resulting dtype name on success, confirming the cast applied.
"""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function

_DTYPE_MAP: dict[str, type[pl.DataType]] = {
    "Int32": pl.Int32,
    "Int64": pl.Int64,
    "Float32": pl.Float32,
    "Float64": pl.Float64,
    "Utf8": pl.Utf8,
    "Boolean": pl.Boolean,
}


class CastDtypeParams(BaseModel):
    target_dtype: str


@register_function(
    FunctionSpec(name="cast_dtype", applicable_dtypes=["any"], param_schema=CastDtypeParams)
)
def cast_dtype(df: pl.DataFrame, column: str, params: dict[str, Any]) -> str:
    parsed = CastDtypeParams.model_validate(params)

    if parsed.target_dtype not in _DTYPE_MAP:
        raise ValueError(
            f"unsupported target_dtype '{parsed.target_dtype}', expected one of "
            f"{sorted(_DTYPE_MAP)}"
        )

    target = _DTYPE_MAP[parsed.target_dtype]
    casted = df[column].cast(target, strict=True)
    return str(casted.dtype)

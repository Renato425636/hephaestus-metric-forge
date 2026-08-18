"""`normalize` — min-max or z-score normalization of a numeric column.

Returns a JSON-encoded list of normalized values (as `str`), since the API
contract's `value` field is scalar-only (`float | int | str | None`).
"""

from __future__ import annotations

import json
from typing import Any, cast

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class NormalizeParams(BaseModel):
    method: str = "minmax"  # "minmax" | "zscore"


@register_function(
    FunctionSpec(name="normalize", applicable_dtypes=["numeric"], param_schema=NormalizeParams)
)
def normalize(df: pl.DataFrame, column: str, params: dict[str, Any]) -> str:
    parsed = NormalizeParams.model_validate(params)
    series = df[column].cast(pl.Float64)

    if parsed.method == "zscore":
        # Series is dtype-narrowed via applicable_dtypes=["numeric"] before this
        # strategy runs; polars' aggregation stubs stay dtype-generic, so mypy
        # needs an explicit narrowing here.
        mean = cast(float | None, series.mean())
        std = cast(float | None, series.std())
        result = (series - mean) / std if std else series - mean
    elif parsed.method == "minmax":
        min_v = cast(float | None, series.min())
        max_v = cast(float | None, series.max())
        span = None if min_v is None or max_v is None else max_v - min_v
        result = (series - min_v) / span if span else series - min_v
    else:
        raise ValueError(f"unsupported method '{parsed.method}', expected 'minmax' or 'zscore'")

    return json.dumps(result.to_list())

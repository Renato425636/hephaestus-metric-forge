"""`bucketize` — bins a numeric column via `params.bins` breakpoints (and
optional `params.labels`), returning a JSON-encoded histogram (`{label: count}`).

Non-scalar result, so — like `normalize` — it's serialized as a `str`.
"""

from __future__ import annotations

import json
from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class BucketizeParams(BaseModel):
    bins: list[float]
    labels: list[str] | None = None


@register_function(
    FunctionSpec(name="bucketize", applicable_dtypes=["numeric"], param_schema=BucketizeParams)
)
def bucketize(df: pl.DataFrame, column: str, params: dict[str, Any]) -> str:
    parsed = BucketizeParams.model_validate(params)
    series = df[column].cast(pl.Float64)
    bucketed = series.cut(breaks=parsed.bins, labels=parsed.labels)

    counts = bucketed.value_counts()
    label_col, count_col = counts.columns
    labels = counts[label_col].cast(pl.Utf8).to_list()
    values = counts[count_col].to_list()
    return json.dumps(dict(zip(labels, values, strict=True)))

"""`dedupe` — count of duplicate rows removable for a given column."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import FunctionSpec
from app.registry import register_function


@register_function(FunctionSpec(name="dedupe", applicable_dtypes=["any"], param_schema=None))
def dedupe(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    total = df.height
    unique = df[column].n_unique()
    return total - unique

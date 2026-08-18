"""`dedupe` — count of duplicate rows removable for a given column.

Duplicates are identified over `params.subset` (defaults to just the column
the request is iterating on). `params.keep` picks which occurrence Polars
would retain (`"first"` or `"last"`) — it doesn't change the *count* returned
here, but is validated and threaded through so callers building an actual
deduplication pipeline on top of this API get consistent semantics.
"""

from __future__ import annotations

from typing import Any, Literal

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class DedupeParams(BaseModel):
    subset: list[str] | None = None
    keep: Literal["first", "last"] = "first"


@register_function(
    FunctionSpec(name="dedupe", applicable_dtypes=["any"], param_schema=DedupeParams)
)
def dedupe(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = DedupeParams.model_validate(params)
    subset = parsed.subset if parsed.subset else [column]
    deduped_height = df.unique(subset=subset, keep=parsed.keep).height
    return df.height - deduped_height

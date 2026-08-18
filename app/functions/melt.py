"""`melt` — unpivots wide to long: `params.id_vars` stay as identifier
columns, `params.value_vars` (defaults to every other column) get stacked
into `variable`/`value` rows.

Returns the resulting long-format row count (`len(id rows) * len(value_vars)`).
"""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class MeltParams(BaseModel):
    id_vars: list[str]
    value_vars: list[str] | None = None


@register_function(FunctionSpec(name="melt", applicable_dtypes=["any"], param_schema=MeltParams))
def melt(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = MeltParams.model_validate(params)
    melted = df.unpivot(index=parsed.id_vars, on=parsed.value_vars)
    return melted.height

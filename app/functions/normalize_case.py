"""`normalize_case` — count of string values that would change under the
requested case transformation."""

from __future__ import annotations

from typing import Any, Literal, cast

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class NormalizeCaseParams(BaseModel):
    mode: Literal["lower", "upper", "title"] = "lower"


@register_function(
    FunctionSpec(
        name="normalize_case", applicable_dtypes=["string"], param_schema=NormalizeCaseParams
    )
)
def normalize_case(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = NormalizeCaseParams.model_validate(params)
    original = df[column]

    if parsed.mode == "lower":
        transformed = original.str.to_lowercase()
    elif parsed.mode == "upper":
        transformed = original.str.to_uppercase()
    else:
        transformed = original.str.to_titlecase()

    return cast(int, original.ne_missing(transformed).sum())

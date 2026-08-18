"""`trim_whitespace` — count of string values with leading/trailing whitespace
that would be removed."""

from __future__ import annotations

from typing import Any, Literal, cast

import polars as pl
from pydantic import BaseModel

from app.models import FunctionSpec
from app.registry import register_function


class TrimWhitespaceParams(BaseModel):
    mode: Literal["both", "left", "right"] = "both"


@register_function(
    FunctionSpec(
        name="trim_whitespace", applicable_dtypes=["string"], param_schema=TrimWhitespaceParams
    )
)
def trim_whitespace(df: pl.DataFrame, column: str, params: dict[str, Any]) -> int:
    parsed = TrimWhitespaceParams.model_validate(params)
    original = df[column]

    if parsed.mode == "both":
        trimmed = original.str.strip_chars()
    elif parsed.mode == "left":
        trimmed = original.str.strip_chars_start()
    else:
        trimmed = original.str.strip_chars_end()

    return cast(int, original.ne_missing(trimmed).sum())

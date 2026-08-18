"""`balance` in the `banking` context.

Diverges from `default`/`retail` (see `balance_default.py`) in two concrete
ways: it excludes `params.pending_ratio` of the raw sum (funds floated /
not yet cleared aren't available balance), and it rounds to 2 decimal
places using round-half-to-even — Python's built-in `round()` already
implements banker's rounding, which is the convention most regulatory
balance-reporting rules expect (avoids systematic upward bias from
always-round-up schemes).
"""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.models import MetricSpec
from app.registry import register_metric


class BankingBalanceParams(BaseModel):
    pending_ratio: float = 0.05  # fraction of the total considered pending / not yet cleared


@register_metric(
    MetricSpec(name="balance", applicable_dtypes=["numeric"], param_schema=BankingBalanceParams),
    context="banking",
)
def balance_banking(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    parsed = BankingBalanceParams.model_validate(params)
    total = float(df[column].sum())
    available = total * (1 - parsed.pending_ratio)
    return round(available, 2)

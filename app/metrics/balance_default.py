"""`balance` — context-dependent balance calculation.

- `default` / `retail`: plain sum of the column at face value, no
  adjustments. Registered under both context keys since they're the same
  formula — "retail" is the domain-meaningful name, "default" keeps the
  registry's universal fallback working for callers who pass an
  unrecognized context.
- `banking` (see `balance_banking.py`): excludes a pending/float fraction
  and applies regulatory rounding — genuinely different math, not a
  cosmetic variant. See that module's docstring for the formula.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import MetricSpec
from app.registry import register_metric

_SPEC = MetricSpec(name="balance", applicable_dtypes=["numeric"], param_schema=None)


@register_metric(_SPEC, context="retail")
@register_metric(_SPEC, context="default")
def balance_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    return float(df[column].sum())

"""Importing this package registers every `metrics` strategy as a side effect."""

from app.metrics import average_default as _average_default  # noqa: F401
from app.metrics import balance_banking as _balance_banking  # noqa: F401
from app.metrics import balance_default as _balance_default  # noqa: F401

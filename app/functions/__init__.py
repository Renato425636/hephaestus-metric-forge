"""Importing this package registers every `functions` strategy as a side effect."""

from app.functions import dedupe as _dedupe  # noqa: F401
from app.functions import groupby as _groupby  # noqa: F401
from app.functions import normalize as _normalize  # noqa: F401

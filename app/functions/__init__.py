"""Importing this package registers every `functions` strategy as a side effect."""

from app.functions import bucketize as _bucketize  # noqa: F401
from app.functions import cast_dtype as _cast_dtype  # noqa: F401
from app.functions import dedupe as _dedupe  # noqa: F401
from app.functions import drop_nulls as _drop_nulls  # noqa: F401
from app.functions import fill_nulls as _fill_nulls  # noqa: F401
from app.functions import groupby_agg as _groupby_agg  # noqa: F401
from app.functions import melt as _melt  # noqa: F401
from app.functions import normalize as _normalize  # noqa: F401
from app.functions import normalize_case as _normalize_case  # noqa: F401
from app.functions import pivot as _pivot  # noqa: F401
from app.functions import trim_whitespace as _trim_whitespace  # noqa: F401

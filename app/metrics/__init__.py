"""Importing this package registers every `metrics` strategy as a side effect."""

from app.metrics import balance_banking as _balance_banking  # noqa: F401
from app.metrics import balance_default as _balance_default  # noqa: F401
from app.metrics import cardinality as _cardinality  # noqa: F401
from app.metrics import duplicate_rate as _duplicate_rate  # noqa: F401
from app.metrics import mean as _mean  # noqa: F401
from app.metrics import median as _median  # noqa: F401
from app.metrics import net_revenue_default as _net_revenue_default  # noqa: F401
from app.metrics import net_revenue_tax_adjusted as _net_revenue_tax_adjusted  # noqa: F401
from app.metrics import null_rate as _null_rate  # noqa: F401
from app.metrics import outlier_iqr as _outlier_iqr  # noqa: F401
from app.metrics import percentile as _percentile  # noqa: F401
from app.metrics import stddev as _stddev  # noqa: F401

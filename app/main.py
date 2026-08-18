"""FastAPI app assembly.

Importing `app.functions`/`app.metrics` registers every strategy (decorator
side effects) before the routers that depend on the registries are wired up.
"""

from __future__ import annotations

from fastapi import FastAPI

from app import functions as _functions  # noqa: F401
from app import metrics as _metrics  # noqa: F401
from app.routers.functions import router as functions_router
from app.routers.metrics import router as metrics_router

app = FastAPI(title="Metrics Function Library API", version="1.0.0")

app.include_router(functions_router)
app.include_router(metrics_router)

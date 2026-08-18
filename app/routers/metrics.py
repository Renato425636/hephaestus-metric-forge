"""`GET /metrics` catalog and `POST /metrics` execution."""

from __future__ import annotations

import asyncio
from typing import Any

import polars as pl
from fastapi import APIRouter, Depends

from app.auth import get_current_token
from app.models import MetricCatalogEntry, MetricResult, MetricsRequest
from app.registry import dtype_category, is_applicable, list_metrics, resolve_metric_strategy

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=list[MetricCatalogEntry])
async def list_metrics_catalog(
    _: dict[str, Any] = Depends(get_current_token),
) -> list[MetricCatalogEntry]:
    return [
        MetricCatalogEntry(
            name=spec.name,
            context=context,
            applicable_dtypes=spec.applicable_dtypes,
            param_schema=spec.param_schema.model_json_schema() if spec.param_schema else None,
        )
        for context, spec in list_metrics()
    ]


def _compute_metrics_sync(req: MetricsRequest) -> list[MetricResult]:
    df = pl.DataFrame(req.data, infer_schema_length=None)
    results: list[MetricResult] = []

    for column in req.columns:
        if column not in df.columns:
            error = f"column '{column}' not found in data"
            for fn_name in req.functions:
                results.append(MetricResult(column=column, function=fn_name, error=error))
            continue

        for fn_name in req.functions:
            try:
                fn, spec = resolve_metric_strategy(fn_name, req.context)
            except KeyError as exc:
                results.append(MetricResult(column=column, function=fn_name, error=str(exc)))
                continue

            category = dtype_category(df[column].dtype)
            if not is_applicable(category, spec.applicable_dtypes):
                error = (
                    f"metric '{fn_name}' not applicable to dtype '{category}' of column '{column}'"
                )
                results.append(MetricResult(column=column, function=fn_name, error=error))
                continue

            params = req.params.get(fn_name, {})
            try:
                value = fn(df, column, params)
                results.append(MetricResult(column=column, function=fn_name, value=value))
            except Exception as exc:  # noqa: BLE001 - surfaced per-item, request must not fail wholesale
                results.append(MetricResult(column=column, function=fn_name, error=str(exc)))

    return results


@router.post("/metrics", response_model=list[MetricResult])
async def compute_metrics(
    req: MetricsRequest,
    _: dict[str, Any] = Depends(get_current_token),
) -> list[MetricResult]:
    return await asyncio.to_thread(_compute_metrics_sync, req)

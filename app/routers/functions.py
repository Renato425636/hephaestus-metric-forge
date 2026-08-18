"""`GET /functions` catalog and `POST /functions/{name}` execution."""

from __future__ import annotations

import asyncio
from typing import Any

import polars as pl
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_token
from app.models import FunctionCatalogEntry, FunctionRequest, FunctionResult
from app.registry import dtype_category, is_applicable, list_functions, resolve_function_strategy

router = APIRouter(tags=["functions"])


@router.get("/functions", response_model=list[FunctionCatalogEntry])
async def list_functions_catalog(
    _: dict[str, Any] = Depends(get_current_token),
) -> list[FunctionCatalogEntry]:
    return [
        FunctionCatalogEntry(
            name=spec.name,
            applicable_dtypes=spec.applicable_dtypes,
            param_schema=spec.param_schema.model_json_schema() if spec.param_schema else None,
        )
        for spec in list_functions()
    ]


def _compute_function_sync(name: str, req: FunctionRequest) -> list[FunctionResult]:
    fn, spec = resolve_function_strategy(name)  # raises KeyError -> 404 below

    df = pl.DataFrame(req.data, infer_schema_length=None)
    results: list[FunctionResult] = []

    for column in req.columns:
        if column not in df.columns:
            results.append(
                FunctionResult(
                    column=column, function=name, error=f"column '{column}' not found in data"
                )
            )
            continue

        category = dtype_category(df[column].dtype)
        if not is_applicable(category, spec.applicable_dtypes):
            error = f"function '{name}' not applicable to dtype '{category}' of column '{column}'"
            results.append(FunctionResult(column=column, function=name, error=error))
            continue

        try:
            value = fn(df, column, req.params)
            results.append(FunctionResult(column=column, function=name, value=value))
        except Exception as exc:  # noqa: BLE001 - surfaced per-item, request must not fail wholesale
            results.append(FunctionResult(column=column, function=name, error=str(exc)))

    return results


@router.post("/functions/{name}", response_model=list[FunctionResult])
async def run_function(
    name: str,
    req: FunctionRequest,
    _: dict[str, Any] = Depends(get_current_token),
) -> list[FunctionResult]:
    try:
        return await asyncio.to_thread(_compute_function_sync, name, req)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

"""Pydantic v2 schemas for the metrics/functions API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

ResultValue = float | int | str | None


class MetricsRequest(BaseModel):
    data: list[dict[str, Any]]
    columns: list[str]
    functions: list[str]
    context: str = "default"
    params: dict[str, dict[str, Any]] = {}


class MetricResult(BaseModel):
    column: str
    function: str
    value: ResultValue = None
    error: str | None = None


class FunctionRequest(BaseModel):
    data: list[dict[str, Any]]
    columns: list[str]
    params: dict[str, Any] = {}


class FunctionResult(BaseModel):
    column: str
    function: str
    value: ResultValue = None
    error: str | None = None


class FunctionSpec(BaseModel):
    """Registration-time spec for a `functions` strategy. Not returned as-is over the wire."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    applicable_dtypes: list[str]
    param_schema: type[BaseModel] | None = None


class MetricSpec(BaseModel):
    """Registration-time spec for a `metrics` strategy. Not returned as-is over the wire."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    applicable_dtypes: list[str]
    param_schema: type[BaseModel] | None = None


class FunctionCatalogEntry(BaseModel):
    """JSON-serializable catalog entry for `GET /functions`."""

    name: str
    applicable_dtypes: list[str]
    param_schema: dict[str, Any] | None = None


class MetricCatalogEntry(BaseModel):
    """JSON-serializable catalog entry for `GET /metrics`."""

    name: str
    context: str
    applicable_dtypes: list[str]
    param_schema: dict[str, Any] | None = None

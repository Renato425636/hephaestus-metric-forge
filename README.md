<p align="center">
  <img src="docs/assets/banner.svg" alt="Hephaestus Metric Forge" width="100%">
</p>

# Hephaestus Metric Forge

Stateless REST API for computing metrics and generic transformations over
tabular data. No upload, no persistence, no `dataset_id` — data travels
inline in the request and results come back in the same call.

**Stack:** FastAPI · Polars · Pydantic v2 · Auth0 (OAuth2 Client Credentials)

## What this is

Two distinct resources, both dispatched through a **Strategy Pattern**
registry (plain dict lookup, no class hierarchy):

- **`functions`** — atomic, domain-independent transformations (`dedupe`,
  `groupby_agg`, `normalize`, `cast_dtype`, ...). Looked up by name alone.
- **`metrics`** — domain-contextual calculations. The *same* metric name can
  mean a different formula depending on `context` — e.g. `balance` in
  `retail` vs `banking`. Looked up by `(name, context)`, with fallback to
  `default` when the requested context isn't registered.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_AUDIENCE="https://metrics-api"

uvicorn app.main:app --reload
```

```bash
curl -X POST "http://localhost:8000/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 100.0}, {"amount": 50.0}],
    "columns": ["amount"],
    "functions": ["balance"],
    "context": "banking"
  }'
```

Full docs (getting started, architecture, and a reference page per
function/metric): see [`docs/`](docs/index.md), or run `mkdocs serve` after
`pip install -e ".[docs]"`.

## Development

```bash
pytest --cov=app --cov-report=term-missing   # 127 tests, 97% coverage
ruff check app tests
mypy --strict app
```

## Docker

```bash
docker build -t hephaestus-metric-forge .
docker run -p 8000:8000 \
  -e AUTH0_DOMAIN="your-tenant.auth0.com" \
  -e AUTH0_AUDIENCE="https://metrics-api" \
  hephaestus-metric-forge
```

## Postman

`postman/collection.json` + `postman/environment.json` cover the full auth
+ functions + metrics flow — works against `localhost` or a deployed URL,
no hardcoded hosts.

## Catalog

11 `functions` (cleaning, reshape, dtype transforms) and 10 `metrics`
(financial, data-quality, descriptive stats) — full list with parameters
and examples in [`docs/reference/`](docs/reference/functions/dedupe.md).
`balance` and `outlier_iqr` are the canonical examples of real
context-dependent dispatch (different formula per context, not a cosmetic
variant) — see [Context Resolution](docs/concepts/context-resolution.md).

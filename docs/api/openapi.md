# API Reference (OpenAPI)

FastAPI generates a full OpenAPI 3.1 schema from the route definitions and
Pydantic models directly — there's nothing hand-maintained to fall out of
sync here.

## Interactive docs

When the API is running:

- **Swagger UI**: `$BASE_URL/docs` — try requests directly in the browser
  (paste a bearer token via the "Authorize" button).
- **ReDoc**: `$BASE_URL/redoc` — read-only, better for skimming the whole
  schema at once.
- **Raw schema**: `$BASE_URL/openapi.json`

## Endpoints at a glance

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/functions` | Bearer JWT | List the `functions` catalog |
| `POST` | `/functions/{name}` | Bearer JWT | Run one function over inline data |
| `GET` | `/metrics` | Bearer JWT | List the `metrics` catalog (name + context + dtypes + param schema) |
| `POST` | `/metrics` | Bearer JWT | Run one or more metrics, under one context, over inline data |

Request/response shapes are documented per-item in
[Functions reference](../reference/functions/dedupe.md) and
[Metrics reference](../reference/metrics/balance.md); the raw Pydantic
models (`MetricsRequest`, `MetricResult`, `FunctionRequest`,
`FunctionResult`) are in `app/models.py` and show up in the interactive
docs with full field-level detail.

## Embedding the live schema

To pull the schema into a static page instead of linking to a running
instance, fetch and embed it at doc-build time, e.g.:

```bash
curl -s "$BASE_URL/openapi.json" -o docs/api/openapi.json
```

This is left as a manual/CI step rather than wired into `mkdocs build` here
— see the changelog for what's deliberately out of scope in this pass.

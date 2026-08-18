# Hephaestus Metric Forge

Stateless REST API for computing metrics and generic transformations over
tabular data, built on **FastAPI** + **Polars**. No upload, no persistence,
no `dataset_id` — data travels inline in the request and results come back
in the same call.

[![tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen)]()
[![mypy](https://img.shields.io/badge/mypy-strict-blue)]()
[![ruff](https://img.shields.io/badge/lint-ruff-46a3ff)]()

## What this is

Two distinct resources:

- **`functions`** — atomic, domain-independent transformations (`dedupe`,
  `groupby_agg`, `normalize`, ...). Looked up by name alone.
- **`metrics`** — domain-contextual calculations. The *same* metric name can
  mean a different formula depending on `context` (e.g. `balance` in
  `retail` vs `banking`). Looked up by `(name, context)`, with fallback to
  `default` when the requested context isn't registered.

Both are resolved via a **Strategy Pattern registry** — a plain dict lookup
against pre-registered callables, not a class hierarchy. See
[Architecture](concepts/architecture.md) for the full picture.

## Quickstart

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 100.0}, {"amount": 50.0}],
    "columns": ["amount"],
    "functions": ["balance"],
    "context": "banking"
  }'
```

Full walkthrough (including how to obtain `$ACCESS_TOKEN`) in
[Getting Started](getting-started/quickstart.md).

## Where to go next

- New to the API? Start at [Installation](getting-started/installation.md).
- Want the mental model before the how-to? Read [Concepts](concepts/architecture.md).
- Looking for a specific function or metric? Jump straight to [Reference](reference/functions/dedupe.md).

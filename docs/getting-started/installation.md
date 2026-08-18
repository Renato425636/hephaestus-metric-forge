# Installation

## Requirements

- Python 3.12+
- (optional, for containerized runs) Docker

## Local install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs the API (FastAPI, Polars, Pydantic v2, `python-jose`) plus the
dev toolchain (`pytest`, `ruff`, `mypy`).

## Environment variables

The API validates — never issues — Auth0 M2M JWTs (see
[Authentication](authentication.md)). Two variables are required before the
app can start handling authenticated requests:

| Variable | Description |
|---|---|
| `AUTH0_DOMAIN` | Your Auth0 tenant domain, e.g. `your-tenant.auth0.com` |
| `AUTH0_AUDIENCE` | The API identifier registered in Auth0 |

```bash
export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_AUDIENCE="https://metrics-api"
```

## Run locally

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`. Interactive docs (Swagger UI) at
`http://localhost:8000/docs`.

## Run via Docker

```bash
docker build -t hephaestus-metric-forge .
docker run -p 8000:8000 \
  -e AUTH0_DOMAIN="your-tenant.auth0.com" \
  -e AUTH0_AUDIENCE="https://metrics-api" \
  hephaestus-metric-forge
```

The image runs `gunicorn` with `uvicorn.workers.UvicornWorker` (2 workers) —
tuned for horizontal scaling on Cloud Run rather than a single fat instance.

## Run the test suite

```bash
pytest --cov=app --cov-report=term-missing
ruff check app tests
mypy --strict app
```

## Build the docs locally

```bash
pip install mkdocs mkdocs-material "mkdocstrings[python]"
mkdocs serve
```

Docs are then live-reloaded at `http://localhost:8000` (or the next free
port, if 8000 is already taken by the API itself).

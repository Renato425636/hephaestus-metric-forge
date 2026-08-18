# Quickstart

An end-to-end request: get a token, then call `/metrics`.

## curl

```bash
export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_AUDIENCE="https://metrics-api"
export BASE_URL="http://localhost:8000"

ACCESS_TOKEN=$(curl -s -X POST "https://$AUTH0_DOMAIN/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "'"$AUTH0_CLIENT_ID"'",
    "client_secret": "'"$AUTH0_CLIENT_SECRET"'",
    "audience": "'"$AUTH0_AUDIENCE"'"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 100.0}, {"amount": 50.0}],
    "columns": ["amount"],
    "functions": ["balance"],
    "context": "banking",
    "params": {"balance": {"pending_ratio": 0.1}}
  }'
```

Response:

```json
[
  {"column": "amount", "function": "balance", "value": 135.0, "error": null}
]
```

Swap `"context": "banking"` for `"context": "default"` (or drop the field —
`"default"` is the default) and the same request returns `150.0` — same
data, different formula. See [Context Resolution](../concepts/context-resolution.md)
for why.

## Python

```python
import httpx

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "..."  # see Authentication

response = httpx.post(
    f"{BASE_URL}/metrics",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    json={
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "banking",
        "params": {"balance": {"pending_ratio": 0.1}},
    },
)
response.raise_for_status()
print(response.json())
```

## A `functions` call for comparison

`functions` don't take a `context` — same request shape, minus that field,
against `/functions/{name}`:

```bash
curl -X POST "$BASE_URL/functions/dedupe" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"id": 1}, {"id": 1}, {"id": 2}],
    "columns": ["id"],
    "params": {}
  }'
```

## Next steps

- Browse the full catalog: [Functions reference](../reference/functions/dedupe.md) · [Metrics reference](../reference/metrics/balance.md)
- Understand *why* the API is shaped this way: [Architecture](../concepts/architecture.md)

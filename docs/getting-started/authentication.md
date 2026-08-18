# Authentication

The API is secured with **OAuth2 Client Credentials** (the M2M flow), backed
by Auth0. Every endpoint under `/functions` and `/metrics` requires a valid
bearer JWT.

## Who does what

- **Auth0** issues the token. The API never issues or mints tokens itself.
- **This API** only *validates* the token: RS256 signature against Auth0's
  published JWKS, plus `aud`, `iss`, and `exp` checks.

This split matters operationally: rotating client secrets, revoking a
client, or changing token TTLs are all Auth0-side operations — the API
doesn't need to be redeployed for any of them.

## 1. Obtain a token

```bash
curl -X POST "https://$AUTH0_DOMAIN/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "'"$AUTH0_CLIENT_ID"'",
    "client_secret": "'"$AUTH0_CLIENT_SECRET"'",
    "audience": "'"$AUTH0_AUDIENCE"'"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

## 2. Call the API

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

## Python

```python
import httpx

token_response = httpx.post(
    f"https://{AUTH0_DOMAIN}/oauth/token",
    json={
        "grant_type": "client_credentials",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": AUTH0_AUDIENCE,
    },
)
access_token = token_response.json()["access_token"]

response = httpx.post(
    f"{BASE_URL}/metrics",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "data": [{"amount": 100.0}, {"amount": 50.0}],
        "columns": ["amount"],
        "functions": ["balance"],
        "context": "banking",
    },
)
```

## What happens on the server side

1. JWT header is parsed (unverified) to read `kid`.
2. The matching signing key is looked up in a TTL-cached copy of Auth0's
   JWKS (`https://{AUTH0_DOMAIN}/.well-known/jwks.json`).
3. If the `kid` isn't in the cache — e.g. because Auth0 rotated its signing
   keys — that's treated as a cache-miss, not an error: the JWKS is
   refetched once before failing.
4. The token is verified: RS256 signature, `aud == AUTH0_AUDIENCE`,
   `iss == https://{AUTH0_DOMAIN}/`, and `exp` in the future.
5. Any failure — missing token, bad signature, wrong audience/issuer,
   expired token — returns `401 Unauthorized`.

## Postman

The bundled [`postman/collection.json`](https://github.com) runs the token
request first and stores `access_token` in the environment via a test
script; every other request reads `{{access_token}}` from there. See
`postman/environment.json` for the variables you need to fill in
(`auth0_domain`, `auth0_client_id`, `auth0_client_secret`, `auth0_audience`).

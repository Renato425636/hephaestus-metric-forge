# Changelog

## Unreleased

### Added — catalog expansion

**`functions`** (11 total): `dedupe`, `drop_nulls`, `fill_nulls`,
`trim_whitespace`, `normalize_case`, `groupby_agg`, `pivot`, `melt`,
`cast_dtype`, `bucketize`, `normalize`.

**`metrics`** (10 names, 15 `(name, context)` registrations):

- `balance` — `default`, `retail`, `banking`
- `net_revenue` — `default`, `tax_adjusted`
- `outlier_iqr` — `default`, `strict`, `lenient`
- `null_rate`, `cardinality`, `duplicate_rate` — `default`
- `mean`, `median`, `stddev`, `percentile` — `default`

Every item shipped with a unit test module (happy path, dtype/param
validation, edge cases, and — for multi-context metrics — context
divergence + fallback) and a `docs/reference/` page.

### Changed

- `dedupe` gained `subset`/`keep` params (previously param-less,
  single-column only).
- `groupby` (single-column, `agg_column`/`agg` params) was replaced by
  `groupby_agg` (`by: list[str]`, `agg: dict[str, str]`) to match the
  planned catalog shape — multi-column grouping, one agg per column.
- `average` (context: `default`) was renamed to `mean` — same formula, name
  now matches the rest of the descriptive-stats set (`median`, `stddev`,
  `percentile`).
- `balance`'s banking-context params renamed `reserve_ratio` →
  `pending_ratio`, and the formula now also applies regulatory rounding
  (round-half-to-even, 2 decimals) — see [`balance`](reference/metrics/balance.md).
  `balance` is now also registered under `context="retail"` (identical
  formula to `default`) to match the domain-facing name used in the spec.

### Documentation

- Added a full MkDocs site (Material theme + `mkdocstrings`): getting
  started, concepts (architecture, functions-vs-metrics, context
  resolution — with a Mermaid request-flow diagram), and one reference page
  per function/metric.

## Previous: initial implementation

FastAPI + Polars + Pydantic v2 base: Strategy Pattern registries (1D
`functions`, 2D `metrics`), Auth0 M2M JWT validation with JWKS
caching/rotation handling, `asyncio.to_thread`-offloaded computation,
Docker multi-stage build, Postman collection.

## Out of scope (tracked, not forgotten)

- Rate limiting (token bucket per client).
- Custom `anyio.CapacityLimiter` for bounding concurrent thread usage.
- Persistence, upload, `dataset_id` — the API stays stateless by design.
- Multi-step stateful transformation pipelines.
- MkDocs site deployment (GitHub Pages or similar) and docs versioning
  (`mike`) — hosting decision deferred to a future pass.
- CI/CD (GitHub Actions) — handled in a separate pass.

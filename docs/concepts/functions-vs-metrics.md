# Functions vs Metrics

Two resources, two different registry shapes, because they answer two
different questions.

| | `functions` | `metrics` |
|---|---|---|
| Question answered | "Transform/summarize this column" | "What's this domain-specific number for this column?" |
| Registry key | `name` (1D) | `(name, context)` (2D) |
| Same name, different logic? | No — one implementation per name | Yes, by design — that's the whole point |
| Unknown name | `404` at the route (`POST /functions/{name}`) | Per-item `error` in the result (batch endpoint, name is in the body) |
| Endpoint shape | `POST /functions/{name}` — one function per call | `POST /metrics` — a list of `functions` + one shared `context` per call |
| Examples | `dedupe`, `groupby_agg`, `normalize`, `cast_dtype` | `balance`, `null_rate`, `outlier_iqr` |

## Why `functions` don't need a context dimension

A `function` is domain-independent by construction: `dedupe` counts
duplicates the same way whether the data is retail transactions or sensor
readings. There's exactly one correct implementation per name, so the
registry only needs `name` as a key, and `resolve_function_strategy(name)`
either finds it or doesn't — no fallback to reason about.

## Why `metrics` need `(name, context)`

A `metric` name describes *what* you're asking for, not *how* to compute
it — and the "how" can legitimately differ by domain. `balance` in a
`retail` context is a plain sum; in a `banking` context it also excludes
pending/floated funds and applies regulatory rounding (see
[`balance`](../reference/metrics/balance.md)). Same question, genuinely
different formula, same name on purpose — that's what the two-dimensional
key is for.

This is also why `metrics` requests carry `context` and `functions` (a
*list* of metric names) rather than a single function name in the URL:
you're usually asking "give me these N metrics, all interpreted under this
one domain" in a single call.

## Where this shows up in the code

```python
# functions/ — 1D registry
_FUNCTIONS_REGISTRY: dict[str, tuple[Callable, FunctionSpec]]

# metrics/ — 2D registry
_METRICS_REGISTRY: dict[tuple[str, str], tuple[Callable, MetricSpec]]
```

Both are populated the same way — a decorator at import time — and both are
resolved with a plain dict lookup. The only structural difference is the
key shape, and that shape is a direct consequence of the question each
resource answers.

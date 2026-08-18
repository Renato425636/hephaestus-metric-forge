# Context Resolution

How `(metric_name, context)` turns into a specific function call — and what
happens when the requested context doesn't exist.

## The resolver

```python
def resolve_metric_strategy(metric_name: str, context: str = "default") -> tuple[MetricCallable, MetricSpec]:
    key = (metric_name, context)
    if key not in _METRICS_REGISTRY:
        key = (metric_name, "default")  # fallback: unknown/missing context -> default
    if key not in _METRICS_REGISTRY:
        raise KeyError(f"metric '{metric_name}' not found for context '{context}' or default")
    return _METRICS_REGISTRY[key]
```

Three outcomes, in order:

1. **Exact match** — `(metric_name, context)` is registered. Use it.
2. **Fallback match** — it isn't, but `(metric_name, "default")` is.
   Silently use the default-context implementation instead.
3. **No match at all** — neither key is registered. Raise `KeyError`,
   which the caller (the `/metrics` route) turns into a per-item `error` in
   the response rather than failing the whole request.

## Why fallback instead of a hard 404

A client asking for `mean` under `context="banking"` almost certainly wants
*the mean*, not a banking-specific formula that doesn't exist — `mean` only
has a `default` registration (see [`mean`](../reference/metrics/mean.md)).
Silently falling back keeps the API usable when a caller passes a context
that's meaningful for *some* metrics in a batch request but not others,
without forcing every metric author to register a redundant `default` alias
by hand for metrics that have no real per-context divergence.

The tradeoff: a typo in `context` (e.g. `"bnaking"`) won't error — it just
silently resolves to `default`. That's a deliberate choice for this API
(favor availability over strictness on an optional dispatch key), not an
oversight.

## Naming note

The resolver is named `resolve_metric_strategy` — not, say,
`metrics_context_general`. An earlier internal draft used a name like that
and it was actively misleading: it read as if `"general"` were itself a
registered context, when the function is the generic *resolver* that
happens to fall back to the literal string `"default"`. The current name
says what the function does (resolve a strategy) without implying anything
about which contexts exist.

## What "registering a metric" actually populates

```python
@register_metric(
    MetricSpec(name="balance", applicable_dtypes=["numeric"], param_schema=None),
    context="retail",
)
def balance_default(df: pl.DataFrame, column: str, params: dict[str, Any]) -> float:
    ...
```

adds one entry: `_METRICS_REGISTRY[("balance", "retail")] = (balance_default, spec)`.
[`balance`](../reference/metrics/balance.md) stacks two such decorators on
the same function to register it under both `"default"` and `"retail"` —
same formula, two valid names for it — while `"banking"` points at a
different function entirely. The registry doesn't care whether two keys
point at the same callable or different ones; it's just a dict.

## Applies to `functions` too — sort of

`functions` don't have a context dimension (see
[Functions vs Metrics](functions-vs-metrics.md)), so there's no fallback to
speak of: `resolve_function_strategy(name)` either finds the name or raises
`KeyError`, which the `/functions/{name}` route turns into a `404` rather
than a per-item error, since the name is part of the URL rather than the
request body.

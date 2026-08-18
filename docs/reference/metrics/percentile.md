# `percentile`

**Categoria:** Estatística descritiva
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.percentile.percentile_default
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `PercentileParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `p` | `float` (0–100) | Não | `50.0` | Percentil desejado, na escala 0–100 |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"x": 1.0}, {"x": 2.0}, {"x": 3.0}, {"x": 4.0}, {"x": 10.0}],
    "columns": ["x"],
    "functions": ["percentile"],
    "params": {"percentile": {"p": 90.0}}
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "percentile", "value": 10.0, "error": null}
]
```

## Divergência por contexto

Não aplicável — `percentile` só tem o contexto `default`. Estatística descritiva padrão, sem variação por domínio; o parâmetro `p` controla o percentil, não o contexto.

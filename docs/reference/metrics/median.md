# `median`

**Categoria:** Estatística descritiva
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.median.median_default
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

Sem parâmetros (`param_schema: None`).

## Exemplo de request

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"x": 1.0}, {"x": 2.0}, {"x": 3.0}, {"x": 4.0}, {"x": 10.0}],
    "columns": ["x"],
    "functions": ["median"]
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "median", "value": 3.0, "error": null}
]
```

## Divergência por contexto

Não aplicável — `median` só tem o contexto `default`. Estatística descritiva padrão, sem variação por domínio.

# `mean`

**Categoria:** Estatística descritiva
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.mean.mean_default
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
    "functions": ["mean"]
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "mean", "value": 4.0, "error": null}
]
```

## Divergência por contexto

Não aplicável — `mean` só tem o contexto `default`. É a referência do catálogo para o [fallback de contexto](../../concepts/context-resolution.md): pedir `mean` sob qualquer `context` não registrado ainda resolve aqui.

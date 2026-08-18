# `null_rate`

**Categoria:** Qualidade de dados
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.null_rate.null_rate_default
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
    "data": [{"x": 1}, {"x": null}, {"x": null}, {"x": 4}],
    "columns": ["x"],
    "functions": ["null_rate"]
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "null_rate", "value": 0.5, "error": null}
]
```

## Divergência por contexto

Não aplicável — `null_rate` só tem o contexto `default`. É um sinal estrutural de qualidade de dados, sem variação por domínio; qualquer `context` desconhecido cai no `default` via [fallback](../../concepts/context-resolution.md).

# `duplicate_rate`

**Categoria:** Qualidade de dados
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.duplicate_rate.duplicate_rate_default
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
    "data": [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 3}],
    "columns": ["id"],
    "functions": ["duplicate_rate"]
  }'
```

## Exemplo de response

```json
[
  {"column": "id", "function": "duplicate_rate", "value": 0.25, "error": null}
]
```

## Divergência por contexto

Não aplicável — `duplicate_rate` só tem o contexto `default`. Sinal estrutural de qualidade de dados, sem variação por domínio.

# `cardinality`

**Categoria:** Qualidade de dados
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.cardinality.cardinality_default
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
    "data": [{"category": "a"}, {"category": "a"}, {"category": "b"}],
    "columns": ["category"],
    "functions": ["cardinality"]
  }'
```

## Exemplo de response

```json
[
  {"column": "category", "function": "cardinality", "value": 2, "error": null}
]
```

## Divergência por contexto

Não aplicável — `cardinality` só tem o contexto `default`. Sinal estrutural de qualidade de dados, sem variação por domínio.

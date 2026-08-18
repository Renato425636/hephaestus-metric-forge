# `stddev`

**Categoria:** Estatística descritiva
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`

## Descrição

::: app.metrics.stddev.stddev_default
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
    "data": [{"x": 2.0}, {"x": 4.0}],
    "columns": ["x"],
    "functions": ["stddev"]
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "stddev", "value": 1.4142135623730951, "error": null}
]
```

Colunas com menos de 2 valores não-nulos têm desvio padrão amostral indefinido; a API retorna `0.0` em vez de `null`/`NaN` para manter o contrato `value` sempre escalar e previsível.

## Divergência por contexto

Não aplicável — `stddev` só tem o contexto `default`. Estatística descritiva padrão (ddof=1), sem variação por domínio.

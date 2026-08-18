# `groupby_agg`

**Categoria:** Agregação/reshape
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.groupby_agg.groupby_agg
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `GroupByAggParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `by` | `list[str]` | Sim | — | Colunas de agrupamento |
| `agg` | `dict[str, str]` | Não | `{}` | Mapa `coluna -> agregação` (`count`, `sum`, `mean`, `min`, `max`); colunas ausentes usam `"count"` |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/groupby_agg" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"category": "a", "qty": 1},
      {"category": "a", "qty": 2},
      {"category": "b", "qty": 3}
    ],
    "columns": ["qty"],
    "params": {"by": ["category"], "agg": {"qty": "sum"}}
  }'
```

## Exemplo de response

```json
[
  {"column": "qty", "function": "groupby_agg", "value": 6.0, "error": null}
]
```

## Divergência por contexto

Não aplicável — `groupby_agg` é uma `function`, não uma `metric`.

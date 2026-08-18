# `pivot`

**Categoria:** Agregação/reshape
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.pivot.pivot
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `PivotParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `index` | `str` | Sim | — | Coluna que vira o índice do resultado |
| `on` | `str` | Sim | — | Coluna cujos valores viram novas colunas |
| `values` | `str \| None` | Não | coluna requisitada | Coluna de origem dos valores das células |
| `agg` | `"first" \| "sum" \| "mean" \| "count"` | Não | `"first"` | Agregação usada quando há múltiplas linhas por célula |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/pivot" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"region": "west", "sku": "a", "qty": 1},
      {"region": "west", "sku": "b", "qty": 2},
      {"region": "east", "sku": "a", "qty": 3}
    ],
    "columns": ["qty"],
    "params": {"index": "region", "on": "sku", "agg": "sum"}
  }'
```

## Exemplo de response

```json
[
  {"column": "qty", "function": "pivot", "value": 2, "error": null}
]
```

## Divergência por contexto

Não aplicável — `pivot` é uma `function`, não uma `metric`.

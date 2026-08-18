# `drop_nulls`

**Categoria:** Limpeza
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto (ver [Functions vs Metrics](../../concepts/functions-vs-metrics.md))

## Descrição

::: app.functions.drop_nulls.drop_nulls
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `DropNullsParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `subset` | `list[str] \| None` | Não | `None` (usa apenas a coluna requisitada) | Colunas cuja nulidade conta para o descarte da linha |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/drop_nulls" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 1.0}, {"amount": null}, {"amount": 3.0}],
    "columns": ["amount"],
    "params": {}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "drop_nulls", "value": 1, "error": null}
]
```

## Divergência por contexto

Não aplicável — `drop_nulls` é uma `function`, não uma `metric`.

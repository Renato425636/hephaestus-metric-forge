# `fill_nulls`

**Categoria:** Limpeza
**Dtypes aplicáveis:** `any` (com validação em runtime: `strategy="mean"|"median"` exige coluna `numeric`)
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.fill_nulls.fill_nulls
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `FillNullsParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `strategy` | `"mean" \| "median" \| "forward" \| "constant"` | Não | `"constant"` | Estratégia de preenchimento |
| `value` | `Any \| None` | Sim, se `strategy="constant"` | `None` | Valor usado quando `strategy="constant"` |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/fill_nulls" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 1.0}, {"amount": null}, {"amount": null}],
    "columns": ["amount"],
    "params": {"strategy": "constant", "value": 0.0}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "fill_nulls", "value": 2, "error": null}
]
```

Aplicar `strategy="mean"` em uma coluna `string` retorna erro por item (não falha o request):

```json
[
  {"column": "label", "function": "fill_nulls", "value": null, "error": "strategy 'mean' requires a numeric column"}
]
```

## Divergência por contexto

Não aplicável — `fill_nulls` é uma `function`, não uma `metric`.

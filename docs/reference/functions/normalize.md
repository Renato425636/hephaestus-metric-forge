# `normalize`

**Categoria:** Transformação de tipo
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.normalize.normalize
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `NormalizeParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `method` | `"minmax" \| "zscore"` | Não | `"minmax"` | Técnica de normalização |

O resultado não é escalar (é a série inteira normalizada), então o contrato `value: str` carrega a lista serializada em JSON.

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/normalize" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 0.0}, {"amount": 5.0}, {"amount": 10.0}],
    "columns": ["amount"],
    "params": {"method": "minmax"}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "normalize", "value": "[0.0, 0.5, 1.0]", "error": null}
]
```

## Divergência por contexto

Não aplicável — `normalize` é uma `function`, não uma `metric`.

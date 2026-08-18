# `normalize_case`

**Categoria:** Limpeza
**Dtypes aplicáveis:** `string`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.normalize_case.normalize_case
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `NormalizeCaseParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `mode` | `"lower" \| "upper" \| "title"` | Não | `"lower"` | Transformação de caixa aplicada |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/normalize_case" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"name": "Alice"}, {"name": "bob"}],
    "columns": ["name"],
    "params": {"mode": "upper"}
  }'
```

## Exemplo de response

```json
[
  {"column": "name", "function": "normalize_case", "value": 2, "error": null}
]
```

## Divergência por contexto

Não aplicável — `normalize_case` é uma `function`, não uma `metric`.

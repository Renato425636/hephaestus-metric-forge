# `trim_whitespace`

**Categoria:** Limpeza
**Dtypes aplicáveis:** `string`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.trim_whitespace.trim_whitespace
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `TrimWhitespaceParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `mode` | `"both" \| "left" \| "right"` | Não | `"both"` | Lado(s) da string a partir do qual o whitespace é removido |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/trim_whitespace" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"name": "  alice  "}, {"name": "bob"}],
    "columns": ["name"],
    "params": {}
  }'
```

## Exemplo de response

```json
[
  {"column": "name", "function": "trim_whitespace", "value": 1, "error": null}
]
```

## Divergência por contexto

Não aplicável — `trim_whitespace` é uma `function`, não uma `metric`.

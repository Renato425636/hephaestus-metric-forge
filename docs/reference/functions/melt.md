# `melt`

**Categoria:** Agregação/reshape
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.melt.melt
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `MeltParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `id_vars` | `list[str]` | Sim | — | Colunas identificadoras mantidas como estão |
| `value_vars` | `list[str] \| None` | Não | Todas as colunas fora de `id_vars` | Colunas empilhadas em `variable`/`value` |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/melt" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 1, "a": 10, "b": 100},
      {"id": 2, "a": 20, "b": 200}
    ],
    "columns": ["a"],
    "params": {"id_vars": ["id"], "value_vars": ["a", "b"]}
  }'
```

## Exemplo de response

```json
[
  {"column": "a", "function": "melt", "value": 4, "error": null}
]
```

## Divergência por contexto

Não aplicável — `melt` é uma `function`, não uma `metric`.

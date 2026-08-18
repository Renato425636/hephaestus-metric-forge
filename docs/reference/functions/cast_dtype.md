# `cast_dtype`

**Categoria:** Transformação de tipo
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.cast_dtype.cast_dtype
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `CastDtypeParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `target_dtype` | `str` | Sim | — | Um de `Int32`, `Int64`, `Float32`, `Float64`, `Utf8`, `Boolean` |

Cast é **estrito**: um valor que não converte (ex.: `"abc"` → `Int64`) vira erro por item, não exceção do request inteiro.

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/cast_dtype" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 1}, {"amount": 2}],
    "columns": ["amount"],
    "params": {"target_dtype": "Float64"}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "cast_dtype", "value": "Float64", "error": null}
]
```

## Divergência por contexto

Não aplicável — `cast_dtype` é uma `function`, não uma `metric`.

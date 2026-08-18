# `dedupe`

**Categoria:** Limpeza
**Dtypes aplicáveis:** `any`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto (ver [Functions vs Metrics](../../concepts/functions-vs-metrics.md))

## Descrição

::: app.functions.dedupe.dedupe
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `DedupeParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `subset` | `list[str] \| None` | Não | `None` (usa apenas a coluna requisitada) | Colunas consideradas ao identificar duplicatas |
| `keep` | `"first" \| "last"` | Não | `"first"` | Qual ocorrência a operação de deduplicação preservaria |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/dedupe" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 3}, {"id": 3}],
    "columns": ["id"],
    "params": {}
  }'
```

## Exemplo de response

```json
[
  {"column": "id", "function": "dedupe", "value": 2, "error": null}
]
```

## Divergência por contexto

Não aplicável — `dedupe` é uma `function` (registry de 1 dimensão), não uma `metric`. O resultado depende apenas de `subset`/`keep`, não de contexto de domínio.

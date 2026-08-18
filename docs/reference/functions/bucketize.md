# `bucketize`

**Categoria:** Transformação de tipo
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** n/a — `functions` não têm dimensão de contexto

## Descrição

::: app.functions.bucketize.bucketize
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `BucketizeParams`

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `bins` | `list[float]` | Sim | — | Pontos de corte (breakpoints) dos buckets |
| `labels` | `list[str] \| None` | Não | Rótulos de intervalo gerados automaticamente | Deve ter `len(bins) + 1` itens quando informado |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/functions/bucketize" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 1.0}, {"amount": 5.0}, {"amount": 15.0}, {"amount": 25.0}],
    "columns": ["amount"],
    "params": {"bins": [10.0, 20.0], "labels": ["low", "mid", "high"]}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "bucketize", "value": "{\"low\": 2, \"mid\": 1, \"high\": 1}", "error": null}
]
```

## Divergência por contexto

Não aplicável — `bucketize` é uma `function`, não uma `metric`.

# `net_revenue`

**Categoria:** Domínio financeiro
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`, `tax_adjusted`

## Descrição

::: app.metrics.net_revenue_default.net_revenue_default
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

::: app.metrics.net_revenue_tax_adjusted.net_revenue_tax_adjusted
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

| Contexto | `param_schema` | Parâmetro | Tipo | Default | Descrição |
|---|---|---|---|---|---|
| `default` | `None` | — | — | — | Sem parâmetros |
| `tax_adjusted` | `TaxAdjustedParams` | `tax_rate` | `float` | `0.15` | Alíquota deduzida de cada transação antes da soma |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"revenue": 200.0}, {"revenue": 100.0}],
    "columns": ["revenue"],
    "functions": ["net_revenue"],
    "context": "tax_adjusted",
    "params": {"net_revenue": {"tax_rate": 0.25}}
  }'
```

## Exemplo de response

```json
[
  {"column": "revenue", "function": "net_revenue", "value": 225.0, "error": null}
]
```

## Divergência por contexto

| Contexto | Fórmula/lógica | Quando usar |
|---|---|---|
| `default` | `sum(column)` — receita bruta, sem deduções | Fallback universal; relatórios de receita bruta |
| `tax_adjusted` | `sum(column * (1 - tax_rate))` — deduz a alíquota por transação antes de somar | Receita líquida de imposto, quando o dado de origem é bruto |

Mesmo dado (`[200.0, 100.0]`), contextos diferentes: `default` → `300.0`; `tax_adjusted` com `tax_rate=0.25` → `225.0`.

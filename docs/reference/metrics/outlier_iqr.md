# `outlier_iqr`

**Categoria:** Qualidade de dados
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`, `strict`, `lenient`

## Descrição

`outlier_iqr` conta valores fora da cerca de Tukey `[Q1 - k*IQR, Q3 + k*IQR]`. Os três contextos usam `k` diferentes — divergência real, não cosmética: o mesmo dado produz contagens de outlier diferentes por contexto.

::: app.metrics.outlier_iqr.outlier_iqr_default
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

::: app.metrics.outlier_iqr.outlier_iqr_strict
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

::: app.metrics.outlier_iqr.outlier_iqr_lenient
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

`param_schema`: `OutlierIqrParams` (igual nos três contextos)

| Nome | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `k` | `float \| None` | Não | Depende do contexto (ver tabela abaixo) | Sobrescreve o `k` padrão do contexto quando informado |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"x": 10.0}, {"x": 11.0}, {"x": 12.0}, {"x": 13.0}, {"x": 14.0}, {"x": 20.0}],
    "columns": ["x"],
    "functions": ["outlier_iqr"],
    "context": "strict"
  }'
```

## Exemplo de response

```json
[
  {"column": "x", "function": "outlier_iqr", "value": 1, "error": null}
]
```

## Divergência por contexto

| Contexto | Fórmula/lógica | Quando usar |
|---|---|---|
| `default` | `k=1.5` (cerca de Tukey padrão) | Uso geral, sem indicação específica de sensibilidade |
| `strict` | `k=1.0` (cerca mais apertada → sinaliza **mais** outliers) | Auditoria/compliance, onde falsos negativos custam mais |
| `lenient` | `k=3.0` (cerca mais larga → sinaliza **menos** outliers) | Dados naturalmente dispersos, onde falsos positivos atrapalham |

Para `x = [10, 11, 12, 13, 14, 20]`: `strict` → `1` outlier; `lenient` → `0` outliers (mesma cerca inferior/superior, `k` diferente).

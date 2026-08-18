# `balance`

**Categoria:** Domínio financeiro
**Dtypes aplicáveis:** `numeric`
**Contextos disponíveis:** `default`, `retail` (mesma fórmula de `default`), `banking`

## Descrição

`balance` é o exemplo canônico de divergência real de fórmula por contexto neste catálogo: `banking` não é uma variação cosmética de `default`/`retail`, é um cálculo diferente (float/pending deduction + arredondamento regulatório).

::: app.metrics.balance_default.balance_default
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

::: app.metrics.balance_banking.balance_banking
    options:
      show_source: true
      heading_level: 3
      show_root_heading: false
      show_root_toc_entry: false

## Parâmetros

| Contexto | `param_schema` | Parâmetro | Tipo | Default | Descrição |
|---|---|---|---|---|---|
| `default` / `retail` | `None` | — | — | — | Sem parâmetros |
| `banking` | `BankingBalanceParams` | `pending_ratio` | `float` | `0.05` | Fração do total considerada pendente/não compensada |

## Exemplo de request

```bash
curl -X POST "$BASE_URL/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"amount": 100.0}, {"amount": 50.0}],
    "columns": ["amount"],
    "functions": ["balance"],
    "context": "banking",
    "params": {"balance": {"pending_ratio": 0.2}}
  }'
```

## Exemplo de response

```json
[
  {"column": "amount", "function": "balance", "value": 120.0, "error": null}
]
```

## Divergência por contexto

| Contexto | Fórmula/lógica | Quando usar |
|---|---|---|
| `default` | `sum(column)` — soma simples, sem ajustes | Fallback universal; qualquer contexto não registrado cai aqui |
| `retail` | Idêntico a `default` | Nome explícito de domínio para varejo, onde toda transação vale seu valor de face |
| `banking` | `round(sum(column) * (1 - pending_ratio), 2)` — exclui fração pendente/não compensada e arredonda (round-half-to-even) | Saldo disponível bancário, onde fundos em compensação não contam e o arredondamento regulatório é exigido |

Mesmo dado (`[100.0, 50.0]`), contextos diferentes: `default`/`retail` → `150.0`; `banking` com `pending_ratio=0.2` → `120.0`.

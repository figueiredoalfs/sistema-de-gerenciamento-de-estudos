# Módulo: Desempenho

## Propósito
Calcula e expõe métricas de desempenho do aluno: taxa de acerto por subtópico, evolução mensal por área e ranking de pontos fracos. Os dados são calculados sobre a tabela `respostas_questoes` em tempo real.

## Arquivos principais
- `app/routers/desempenho.py` — endpoints de desempenho global
- `app/routers/respostas.py` — registro de respostas + desempenho por subtópico
- `app/models/resposta_questao.py` — model `RespostaQuestao`
- `frontend/src/pages/Desempenho.jsx` — página de métricas
- `frontend/src/api/desempenho.js` — chamadas de API

## Endpoints
```
POST /questoes/{questao_id}/responder   → registra uma resposta
GET  /desempenho/subtopicos             → desempenho por subtópico (ordenado por pior)
GET  /desempenho                        → visão geral + por área
GET  /desempenho/evolucao               → evolução mensal por área
```

## Fluxo de dados

### Registro de resposta
```
POST /questoes/{id}/responder
  body: {alternativa_escolhida, tempo_segundos}
  → valida alternativa contra questao.alternativas_json
  → RespostaQuestao(correta=bool, subtopico_id, aluno_id)
  → commit
  → retorna {correta, alternativa_correta, explicacao?}
```

### Desempenho por subtópico
```
GET /desempenho/subtopicos
  → SELECT subtopico_id,
           COUNT(id) AS respondidas,
           SUM(CAST(correta AS INTEGER)) AS acertos   ← PostgreSQL compat
    FROM respostas_questoes
    WHERE aluno_id = ?
    GROUP BY subtopico_id
    ORDER BY (acertos/respondidas) ASC
```

## Model RespostaQuestao
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `aluno_id` | FK | Quem respondeu |
| `questao_id` | FK | Questão respondida |
| `subtopico_id` | FK | Subtópico da questão |
| `correta` | Boolean | Acertou? |
| `alternativa_escolhida` | String(1) | Letra escolhida |
| `tempo_segundos` | Integer | Tempo de resposta |
| `respondida_em` | DateTime | Timestamp |

## Dependências externas
- `Questao` — valida alternativa, puxa subtopico_id
- `Topico` — nome do subtópico no response
- `Aluno` — filtro por usuário

## Regras de negócio críticas
- **`func.sum(correta)` em PostgreSQL exige CAST**: `func.sum(sa.cast(correta, sa.Integer))`
  - SQLite armazena Boolean como 0/1 → sum funciona direto
  - PostgreSQL tem BOOLEAN nativo → sum() retorna NULL sem cast
- Respostas são **imutáveis** — não há update/delete de respostas registradas
- `correta` é calculado no backend, nunca aceito do cliente

## Pontos de atenção
- Query de subtópicos ordena por taxa de acerto ASC (piores primeiro) — não alterar sem revisar UI
- `tempo_segundos` pode ser NULL se o cliente não enviar
- Para grandes volumes de respostas, considerar índice em `(aluno_id, subtopico_id)`

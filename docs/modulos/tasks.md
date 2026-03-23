# Módulo: Tasks (Study Tasks)

## Propósito
Gerencia as tarefas de estudo individuais do aluno. Cada tarefa é um item de estudo tipado (diagnóstico, teoria, revisão, questionário, simulado, reforço) associado a um tópico e a uma Meta. O dashboard exibe as tasks do dia; o TaskView executa questões dentro da task.

## Arquivos principais
- `app/routers/study_tasks.py` — CRUD de tasks
- `app/models/study_task.py` — model `StudyTask`
- `frontend/src/pages/Dashboard.jsx` — lista tasks do dia
- `frontend/src/pages/TaskView.jsx` — execução de uma task
- `frontend/src/hooks/useTasks.js` — fetch + estado das tasks
- `frontend/src/components/dashboard/` — TaskCard, TaskHero, VerticalTimeline, WeeklyProgressBar
- `frontend/src/components/task/` — QuestionFlow, VideoList, PdfPanel

## Tipos de task
| Tipo | Descrição |
|------|-----------|
| `diagnostico` | Avaliação inicial — gera proficiência base |
| `teoria` | Estudo de conteúdo (vídeos/PDF) |
| `revisao` | Revisão espaçada (FSRS) |
| `questionario` | Sequência de questões |
| `simulado` | Simulado completo |
| `reforco` | Reforço em tópicos fracos |

## Fluxo de dados

### Dashboard
```
GET /tasks/today
  → retorna tasks do dia (limite configurável, status pending/in_progress)
  → frontend exibe em VerticalTimeline + TaskHero
```

### Execução
```
GET /tasks/{id}/questoes   → lista questões da task (questoes_json)
PATCH /tasks/{id}/status   → atualiza status (pending→in_progress→completed)
  → se diagnostico completo: recalcula proficiências
  → se última task da meta: encerra Meta automaticamente
```

### Criação (via metas)
```
Tasks são criadas pelo módulo de metas (gerarMeta), nunca diretamente pelo aluno
POST /tasks é interno/admin
```

## Dependências externas
- `Meta` — toda task pertence a uma meta (`meta_id`)
- `Topico` — `materia_id`, `topico_id`, `subtopico_id`
- `RespostaQuestao` — registradas via `POST /questoes/{id}/responder`
- `PerfilEstudo` — define carga semanal

## Regras de negócio críticas
- Ordem das tasks importa: `order_in_week` determina sequência na semana
- `questoes_json` é um array de IDs (string) — parse via `json.loads`
- Mudança de status é **unidirecional**: não voltar de `completed` para anterior
- Task de diagnóstico completa → dispara recálculo de proficiência no subtópico

## Pontos de atenção
- `GET /tasks/today` tem limite para evitar sobrecarga — não retorna todas as tasks da meta
- `week_number` é relativo à meta, não ao calendário
- FSRS fields (`stability`, `difficulty`, `due_date`) estão no model mas o algoritmo está em `ALGORITMO.md`

# Módulo: Metas

## Propósito
Gerencia os ciclos pedagógicos semanais (Metas). Cada Meta é um container de tasks com quota semanal. O módulo gera tasks automaticamente com base no plano base do aluno, proficiência FSRS e disponibilidade (horas/dia × dias/semana). Meta 00 é o diagnóstico inicial; Meta 01+ são semanas de estudo.

## Arquivos principais
- `app/routers/metas.py` — endpoints de meta
- `app/models/meta.py` — model `Meta`
- `app/routers/cronograma_semanal.py` — cronograma semanal (se existir)
- `app/models/cronograma.py` — model de cronograma (pré-prova / revisão final)
- `app/models/plano_base.py` — template de plano por área
- `frontend/src/api/metas.js` — chamadas de API
- `frontend/src/components/dashboard/DiagnosticBanner.jsx` — banner de diagnóstico

## Endpoints
```
POST /metas/iniciar-diagnostico   → cria Meta 00 (diagnóstico)
POST /metas/gerar                 → gera nova meta semanal com tasks
GET  /metas                       → lista todas as metas do aluno
GET  /metas/active                → meta ativa com progresso
GET  /metas/{id}                  → detalhes de uma meta
PATCH /metas/{id}/encerrar        → encerra meta manualmente
```

## Fluxo de geração de meta
```
POST /metas/gerar
  → verifica se há meta aberta (bloqueia se sim)
  → lê PerfilEstudo (horas_por_dia, dias_por_semana, area, experiencia)
  → lê PlanoBase da área
  → consulta proficiências FSRS dos subtópicos
  → prioriza subtópicos com menor proficiência / mais atrasados
  → cria StudyTasks tipadas (teoria, revisao, questionario…)
  → cria Meta com numero_semana = última + 1
  → retorna Meta com tasks embutidas
```

## Model Meta
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `numero_semana` | Integer | Sequência (0 = diagnóstico) |
| `tarefas_total` | Integer | Tasks geradas |
| `tarefas_concluidas` | Integer | Tasks completadas |
| `status` | String | `aberta` / `encerrada` |
| `aluno_id` | FK | Dono da meta |

## Dependências externas
- `StudyTask` — tasks criadas dentro da meta
- `PerfilEstudo` — parâmetros de carga
- `PlanoBase` — template de conteúdo por área
- `Topico` — hierarquia de conteúdo
- `Proficiencia` — scores FSRS por subtópico

## Regras de negócio críticas
- **Só pode haver 1 meta aberta por vez** — verificar antes de gerar
- Meta 00 é criada no onboarding — não criar manualmente para alunos iniciantes
- `tarefas_concluidas` é incrementado quando task muda para `completed` (via tasks router)
- Meta auto-encerra quando `tarefas_concluidas == tarefas_total`
- O PlanoBase define a ordem e os tipos de task — não alterar sem revisar o plano

## Pontos de atenção
- A geração de meta chama IA (Gemini) para alguns casos — pode dar timeout
- `cronograma_semanal.py` gerencia o calendário de sessões, separado das metas
- `horas_por_dia × dias_por_semana` define a carga total que o engine deve respeitar

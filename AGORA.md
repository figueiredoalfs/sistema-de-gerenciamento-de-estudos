# AGORA.md — Skolai: Planejamento completo
> Fonte única de verdade. Substitui IMPLEMENTATION_GUIDE.md.
> Atualizado: 16/03/2026.

---

## Visão do produto

Plataforma de estudos para concursos públicos com 3 perfis:
- **Aluno** — trilha de estudo personalizada, análise de desempenho, revisões
- **Admin** — gestão de conteúdo (questões, tópicos, usuários)
- **Mentor** — acompanhamento de alunos mentorados

Stack: FastAPI (backend) + React/Vite/Tailwind (frontend) + SQLite(dev)/PostgreSQL(prod) + Gemini Flash (IA)
**Streamlit: abandonar completamente. Tudo em React.**

---

## Estado real do backend hoje

### O que está implementado e funciona
- Auth completo: registro, login JWT, /auth/me, alterar senha
- Onboarding: cria/atualiza aluno, upsert PerfilEstudo, chama gerar_plano_inicial
- Engine pedagógica: gera Meta com tasks priorizadas por estado do subtópico
- Tasks: CRUD, GET /tasks/today, PATCH status, dispara lógica pós-diagnóstico
- Metas: gerar, listar, active, encerrar
- Desempenho: por matéria, evolução mensal
- Questões: endpoints admin para criar/editar, listar por subtópico
- Conteúdo: explicações por subtópico, vídeos com cache, PDF gerado por IA

### Ponto crítico: banco de questões vazio
A engine pedagógica gera tasks mas `questoes_json = null`.
Sem questões, os fluxos de questionário, simulado e reforço não funcionam.
**Importar questões é o desbloqueador de 80% das features.**

### Dois sistemas de sessão coexistindo (legado)
- `Sessao` — sistema antigo, usado por `priorizacao.py` (agenda legacy)
- `StudyTask` — sistema novo, usado pela engine pedagógica
O React usa apenas StudyTask. Sessao/priorizacao.py são legado.

---

## Estado real do frontend hoje

### O que existe em React
```
Login.jsx         ✅ funcionando
Onboarding.jsx    ✅ funcionando (4 steps)
Dashboard.jsx     ⚠️ renderiza, TaskCard não expande
useTasks.js       ✅ busca tasks + meta em paralelo
AuthContext.jsx   ✅ login, logout, refreshUser
api/              ✅ auth, tasks, metas, onboarding
```

### O que não existe em React ainda
- Análise de desempenho
- Banco de questões (admin)
- Gestão de usuários (admin)
- Gestão de tópicos/subtópicos (admin)
- Fluxo de revisões
- Painel do mentor
- Expansão do TaskCard por tipo

### Streamlit — deletar
```
app.py, api_client.py, database.py, style.py
config_app.py, config_fontes.py, config_materias.py
migrar_dados.py, telas/
```

---

## Contratos de API confirmados

| Endpoint | Response relevante |
|---|---|
| POST /auth/login | { access_token, role, nome } |
| GET /auth/me | AlunoResponse: { id, nome, email, role, area, horas_por_dia, dias_por_semana, nivel_desafio, ativo, diagnostico_pendente } |
| POST /onboarding | { aluno_id, perfil_estudo_id, funcionalidades, tasks_geradas } |
| GET /tasks/today | { daily_limit, tasks: [...] } |
| PATCH /tasks/{id}/status | task atualizada; se diagnostico→completed dispara engine |
| GET /metas | { metas: [{ id, status, numero_semana, tasks_meta, tasks_concluidas }] } |
| GET /metas/active | meta com status='aberta' |
| POST /metas/gerar | meta criada com tasks |
| GET /desempenho | por matéria |
| GET /desempenho/evolucao | mensal |

**Regra:** contrato quebrado → corrigir backend. Nunca adaptar frontend.

---

## TASK LIST

### FASE 0 — Desbloqueador crítico

#### TASK 0.1 — Importação de questões (Admin)
⬜ PENDING
**Por que primeiro:** sem questões no banco, questionario/simulado/reforco não funcionam.
Toda a engine pedagógica fica travada.

Backend (já existe POST /questoes admin):
- Confirmar que o endpoint aceita array de questões
- Cada questão: { subtopico_id, enunciado, alternativas[5], gabarito, fonte, nivel }
- Validar e salvar em lote

Frontend (React — nova página admin):
- Tela de upload JSON/CSV
- Preview das questões antes de importar
- Feedback de quantas foram importadas com sucesso
- Formato esperado documentado na tela

**Fluxo externo (fora do sistema):**
Admin usa IA externa (ChatGPT/Claude) para converter PDF do Tec Concursos
em JSON estruturado → importa pelo painel.

---

### FASE 1 — Fluxo do aluno funcionando de ponta a ponta

#### TASK 1.1 — Confirmar /auth/me retorna `area`
⬜ PENDING
AlunoResponse já tem campo `area` no schema.
Testar com servidor rodando:
```bash
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN" | python3 -m json.tool
```
OnboardingGuard verifica `user.area` — se não vier, loop infinito.

---

#### TASK 1.2 — Expansão do TaskCard por tipo
⬜ PENDING
Estado atual: card mostra badge mas não expande, comportamento igual para todos os tipos.

Card fechado: numero_cronograma + subject_nome + subtopic_nome + badge tipo + status

Card expandido por tipo:

**teoria:**
- Descrição do que fazer
- [ Vídeo Aula ] → GET /task-conteudo/{task_code}/videos
- [ Gerar PDF ] → POST /task-conteudo/{task_code}/gerar-pdf
- [ Iniciar Questões ] → abre 5 questões de validação obrigatórias
- Só finaliza após responder as questões

**revisao:**
- Igual a teoria, 10 questões de validação

**reforco:**
- Igual a teoria, 10-15 questões

**questionario:**
- [ Iniciar ] → exibe questoes_json em sequência
- Conclui automaticamente ao terminar

**simulado:**
- Igual a questionario com timer

**diagnostico:**
- [ Iniciar ] → exibe questões diagnósticas
- Ao concluir dispara engine pedagógica automaticamente

---

#### TASK 1.3 — Tela de resolução de questões
⬜ PENDING
Componente QuestionFlow reutilizado por todos os tipos de task que têm questões.

Props: questoes[], onComplete(resultado)
- Exibe uma questão por vez
- Alternativas clicáveis com feedback visual após resposta
- Progresso: "Questão 3 de 10"
- Ao finalizar: chama onComplete com { acertos, total, percentual }
- Resultado atualiza status da task via PATCH /tasks/{id}/status

---

#### TASK 1.4 — Sistema de vídeos
⬜ PENDING
Backend já tem task_conteudo e task_video implementados.
Frontend precisa:
- Ao clicar "Vídeo Aula": GET /task-conteudo/{task_code}/videos
- Se existirem: exibir lista com thumbnail + título + avaliação
- Se não existirem: POST /task-conteudo/{task_code}/videos/buscar (IA busca YouTube)
- Botão "Ver mais vídeos" → busca novos
- Avaliação 1-5 estrelas por vídeo → POST /task-videos/{id}/avaliar

---

#### TASK 1.5 — Geração de PDF
⬜ PENDING
Backend já tem endpoint de geração.
Frontend precisa:
- Ao clicar "Gerar PDF": POST /task-conteudo/{task_code}/gerar-pdf
- Loading com mensagem "Gerando conteúdo..." (pode levar ~15s)
- Exibir conteúdo gerado em modal ou área expandida
- Se já existir cache: GET /task-conteudo/{task_code} retorna direto

---

### FASE 2 — Análise de desempenho (Aluno)

#### TASK 2.1 — Página de desempenho
⬜ PENDING
Nova rota React: /desempenho

Seções:
- KPIs gerais: total questões, % acerto geral, matéria mais forte, matéria mais fraca
- Desempenho por matéria: tabela ou cards com % acerto + total questões
- Evolução mensal: gráfico de linha por matéria (GET /desempenho/evolucao)

Endpoints: GET /desempenho, GET /desempenho/evolucao

---

#### TASK 2.2 — Lançamento manual de bateria
⬜ PENDING
Aluno pode registrar resultado de questões feitas fora do sistema
(ex: Qconcursos, TEC, prova anterior).

Nova rota React: /lancar-bateria
- Selecionar matéria + subtópico
- Informar acertos/total/fonte
- POST /bateria
- Atualiza desempenho automaticamente

---

### FASE 3 — Painel Admin

#### TASK 3.1 — Layout do painel admin
⬜ PENDING
Nova rota React: /admin (protegida por role === 'administrador')
Sidebar separada do painel do aluno.
Páginas: Questões | Tópicos | Usuários | Importar

---

#### TASK 3.2 — Gestão de questões
⬜ PENDING
- Listar questões com filtro por matéria/subtópico
- Editar questão individual (PATCH /questoes/{id})
- Deletar questão
- Ver questões por subtópico

---

#### TASK 3.3 — Importação em lote (TASK 0.1 revisitada com UI completa)
⬜ PENDING
- Upload de arquivo JSON ou CSV
- Preview com tabela das questões detectadas
- Validação: destacar questões com campos faltando
- Importar com feedback de progresso
- Histórico de importações

Formato JSON esperado:
```json
[{
  "subtopico": "Atos Administrativos",
  "materia": "Direito Administrativo",
  "enunciado": "...",
  "alternativas": ["A)...", "B)...", "C)...", "D)...", "E)..."],
  "gabarito": "C",
  "nivel": "medio",
  "fonte": "CESPE 2023"
}]
```

---

#### TASK 3.4 — Gestão de tópicos e subtópicos
⬜ PENDING
- Listar hierarquia: matéria → tópico → subtópico
- Adicionar/editar/remover subtópico
- Ajustar peso_edital por subtópico
- Ver quantas questões cada subtópico tem

---

#### TASK 3.5 — Gestão de usuários
⬜ PENDING
- Listar alunos com filtros
- Ver perfil detalhado de cada aluno
- Ativar/desativar aluno
- Atribuir mentor
- Ver progresso e última atividade

---

### FASE 4 — Painel do Mentor

#### TASK 4.1 — Visão dos alunos mentorados
⬜ PENDING
Nova rota React: /mentor (protegida por role === 'mentor')
- Lista dos alunos mentorados
- Card por aluno: nome, área, % progresso meta atual, última atividade
- Clicar no aluno → ver detalhes de desempenho

---

#### TASK 4.2 — Detalhes do aluno mentorado
⬜ PENDING
- Desempenho por matéria
- Tasks concluídas na semana
- Histórico de metas
- Pontos fortes e fracos identificados pela engine

---

### FASE 5 — Limpeza e deploy

#### TASK 5.1 — Deletar Streamlit
⬜ PENDING
```bash
rm app.py api_client.py database.py style.py
rm config_app.py config_fontes.py config_materias.py migrar_dados.py
rm -rf telas/
rm IMPLEMENTATION_GUIDE.md
```

---

#### TASK 5.2 — Remover routers inativos do backend
⬜ PENDING
Confirmar quais routers o React não usa e remover do main.py:
agenda.py, cronograma_semanal.py, conhecimento.py,
admin_stats.py, explicacoes.py (verificar se React vai usar)

**Atenção:** routers que serão usados nas fases 2-4 não deletar.

---

#### TASK 5.3 — CORS restrito
⬜ PENDING
Antes do deploy, substituir `allow_origins=["*"]` por:
```python
allow_origins=[
    "http://localhost:5173",
    "https://seu-dominio.railway.app",
]
```

---

#### TASK 5.4 — Deploy Railway
⬜ PENDING
1. Variáveis: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
2. `railway run alembic upgrade head`
3. Testar fluxo completo online
4. Configurar domínio

---

## Regras fixas

1. Streamlit: deletar. Tudo em React.
2. Contrato quebrado → corrigir backend, nunca adaptar frontend
3. Uma task por vez
4. Testar endpoint antes de implementar o frontend correspondente
5. Sem questões no banco → TASK 0.1 primeiro
6. Código morto só deletar na FASE 5
7. SQLite em dev, PostgreSQL no Railway

# AGORA.md — Skolai
> Cada task = backend + frontend + testável no navegador.
> Só marcar como concluída quando funcionar de ponta a ponta.
> Atualizado: 16/03/2026 | 10/21 concluídas

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev)/PostgreSQL(prod) + Gemini Flash
- Frontend: React 18 + Vite + Tailwind + React Router v6
- Roles: administrador / mentor / estudante
- Streamlit: abandonado — deletar na FASE-5

## Progresso por fase
- ✅ FASE-0: Banco de questões (2/2)
- ✅ FASE-1: Fluxo do aluno (5/5)
- ✅ FASE-2: Desempenho (3/3)
- ⬜ FASE-3: Painel admin base (0/4) ← atual
- ⬜ FASE-3.5: PlanoBase + progressão pedagógica (0/4)
- ⬜ FASE-4: Painel mentor (0/1)
- ⬜ FASE-5: Limpeza + deploy (0/2)

---

## Regra de implementação
1. Backend primeiro — testar no /docs antes de tocar no frontend
2. Frontend consome o endpoint confirmado
3. Só concluir quando funcionar no navegador de ponta a ponta
4. Contrato quebrado → corrigir backend, nunca adaptar frontend

---

## FASE-3 — Painel Admin

### TASK 3.1 — Layout admin + gestão de questões
⬜ PENDING

**Testa assim:** login como administrador → acessa /admin → vê sidebar
própria → filtra questões por matéria → edita uma → deleta outra.

**Backend:**
- GET /admin/questoes?materia=X&subtopico=Y&page=1 (protegido role=administrador)
- PATCH /admin/questoes/{id} — editar campos da questão
- DELETE /admin/questoes/{id} — deletar com confirmação

**Frontend:**
- Rota /admin protegida por role === 'administrador'
- Sidebar própria separada da sidebar do aluno:
  Questões | Importar | Tópicos | Usuários | Configurações
- Página Questões: tabela com filtros por matéria/subtópico,
  editar inline ou modal, deletar com confirmação
- Contador de questões por subtópico visível

---

### TASK 3.2 — Importação em lote com UI completa
⬜ PENDING

**Testa assim:** admin → /admin/importar → drag-and-drop de JSON →
preview aparece → confirma → "X questões importadas, Y erros".

**Backend:**
- POST /admin/questoes/importar: aceita array, resolve subtopico por nome,
  valida, salva em lote
- Retorna: { importadas: N, erros: [{ linha, motivo }] }

**Frontend (página /admin/importar):**
- Upload drag-and-drop JSON ou CSV
- Preview em tabela antes de confirmar importação
- Linhas com erro destacadas visualmente
- Barra de progresso durante importação
- Resultado: "X importadas, Y com erro" + lista de erros detalhada

**Formato JSON documentado na tela:**
```json
[{
  "materia": "Direito Administrativo",
  "subtopico": "Atos Administrativos",
  "enunciado": "...",
  "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
  "gabarito": "C",
  "nivel": "medio",
  "fonte": "CESPE 2023"
}]
```

---

### TASK 3.3 — Gestão de tópicos e subtópicos
⬜ PENDING

**Testa assim:** admin → /admin/topicos → expande Direito Administrativo
→ edita peso_edital de Atos Administrativos → vê contador de questões.

**Backend:**
- GET /admin/topicos/hierarquia — árvore completa com contadores de questões
- POST /admin/subtopicos — criar subtópico dentro de um tópico
- PATCH /admin/subtopicos/{id} — editar nome e peso_edital
- DELETE /admin/subtopicos/{id} — só se não tiver questões vinculadas

**Frontend (página /admin/topicos):**
- Árvore expansível: matéria → tópico → subtópico
- Cada subtópico: nome, peso_edital (editável inline), nº de questões
- Botão adicionar subtópico dentro de cada tópico
- Deletar desabilitado se subtópico tiver questões vinculadas

---

### TASK 3.4 — Gestão de usuários
⬜ PENDING

**Testa assim:** admin → /admin/usuarios → filtra por área fiscal →
desativa um aluno → atribui mentor → vê confirmação.

**Backend:**
- GET /admin/usuarios?area=X&role=Y&ativo=true — listar com filtros
- PATCH /admin/usuarios/{id} — ativar/desativar, atribuir mentor_id
- GET /admin/usuarios/{id}/progresso — meta atual + tasks + desempenho geral

**Frontend (página /admin/usuarios):**
- Tabela: nome, email, área, role, ativo, última atividade
- Filtros: área, role, status ativo/inativo
- Ações por linha: toggle ativar/desativar, atribuir mentor, ver progresso
- Modal de progresso: meta atual, tasks concluídas, % acerto geral

---

## FASE-3.5 — PlanoBase + Progressão Pedagógica

> Base científica: Cognitive Load Theory (Sweller 1988) + Spiral Curriculum
> (Bruner) + Expertise Reversal Effect (Kalyuga 2003).
> Introduzir 3-5 matérias iniciais e expandir conforme desempenho é mais
> eficaz do que expor todas as matérias de uma vez.

### TASK 3.5.1 — Área fiscal como única ativa no onboarding
⬜ PENDING

**Testa assim:** onboarding tela 1 → somente "Fiscal" é clicável →
as outras áreas aparecem com cadeado e texto "Em desenvolvimento".

**Frontend (StepArea.jsx):**
- Área "Fiscal" → selecionável normalmente
- Demais áreas (Jurídica, Policial, TI, Saúde) → aparência bloqueada:
  opacity reduzida, cadeado no canto, tooltip "Em desenvolvimento"
  cursor not-allowed, não dispara onChange

**Backend:** nenhuma mudança necessária.

---

### TASK 3.5.2 — Model PlanoBase + geração via IA
⬜ PENDING

**Testa assim:** novo aluno faz onboarding → sistema busca PlanoBase
fiscal/iniciante → não existe → IA gera em background → salva no banco
→ admin recebe notificação → próximo aluno do mesmo perfil usa o plano
cacheado sem chamar a IA.

**Backend — novo model PlanoBase:**
```
id, area, perfil (iniciante/intermediario/avancado)
versao (int, começa em 1)
gerado_por_ia (bool)
revisado_admin (bool, default false)
ativo (bool, default true)
fases_json: [
  {
    numero: 1,
    nome: "Fundação",
    criterio_avanco: "media_acerto >= 0.65",
    materias: ["Lingua Portuguesa", "Raciocinio Logico", "Matematica"]
  },
  {
    numero: 2,
    nome: "Núcleo Jurídico",
    criterio_avanco: "media_acerto >= 0.70",
    materias_novas: ["Direito Constitucional", "Direito Administrativo"],
    materias_continuam: "todas"
  },
  ...
]
ordem_subtopicos_json: {
  "Direito Administrativo": ["Princípios", "Poderes", "Atos", ...]
}
created_at, updated_at
```

**Lógica de busca/geração em plano_inicial.py:**
1. Busca PlanoBase ativo para area + perfil
2. Se existe e revisado_admin=true → usa direto
3. Se existe mas revisado_admin=false → usa + admin já foi notificado
4. Se não existe → gera via IA (Gemini) + salva + cria notificação admin

**Prompt para IA:**
"Gere um plano progressivo para concursos fiscais brasileiros com perfil
[iniciante/intermediario/avancado]. Retorne JSON com fases de introdução
de matérias, critérios de avanço baseados em % de acerto, e ordem
pedagógica dos subtópicos por matéria. Considere carga cognitiva:
máximo 3-5 matérias na fase 1, expandindo gradualmente."

---

### TASK 3.5.3 — Lógica de avanço de fase
⬜ PENDING

**Testa assim:** aluno com dados de teste atinge 65% em todas as
matérias da fase 1 → sistema detecta → adiciona matérias da fase 2
automaticamente → aluno vê novas matérias no dashboard.

**Backend — novo service avancar_fase.py:**
- Roda após cada meta encerrada (hook em engine_pedagogica.py)
- Calcula média de acerto por matéria ativa do aluno
- Compara com criterio_avanco da fase atual do aluno
- Se atingido:
  - Registra fase_atual no Aluno ou PerfilEstudo
  - Adiciona novas matérias ao ciclo ativo do aluno
  - Cria notificação para o aluno: "Você avançou para a Fase 2!"
- Não retrocede fase automaticamente (só admin pode)

**Novo campo em Aluno ou PerfilEstudo:**
- fase_plano_atual (int, default 1)
- plano_base_id (FK para PlanoBase)

---

### TASK 3.5.4 — Dashboard admin — notificação e revisão do PlanoBase
⬜ PENDING

**Testa assim:** após IA gerar PlanoBase → admin loga → vê banner
de notificação → clica em revisar → edita critério de avanço da fase 2
→ salva → escolhe "aplicar só para novos alunos" → confirma.

**Backend:**
- Model Notificacao: { id, tipo, titulo, descricao, lida, payload_json }
- GET /admin/notificacoes — lista não lidas
- PATCH /admin/notificacoes/{id}/lida
- GET /admin/plano-base/{id} — detalhe do plano
- PATCH /admin/plano-base/{id} — editar fases e critérios
- POST /admin/plano-base/{id}/aplicar — body: { escopo: "novos" | "todos" }

**Frontend (dashboard admin + página /admin/configuracoes):**
- Banner no topo do dashboard admin quando há notificações não lidas
- "IA gerou um PlanoBase para Fiscal/Iniciante. [Revisar]"
- Página de revisão: editor visual das fases
  - Editar nome da fase
  - Editar critério de avanço (slider de % ou campo numérico)
  - Reordenar matérias por fase (drag-and-drop)
  - Editar ordem dos subtópicos por matéria
- Botão salvar → modal: "Aplicar para: Novos alunos / Todos os alunos"

---

## FASE-4 — Painel do Mentor

### TASK 4.1 — Lista e detalhe dos alunos mentorados
⬜ PENDING

**Testa assim:** login como mentor → acessa /mentor → vê lista de alunos
→ clica num aluno → vê desempenho por matéria e tasks desta semana.

**Backend:**
- GET /mentor/alunos — alunos onde mentor_id = current_user.id
- GET /mentor/alunos/{id}/resumo — desempenho + meta atual + tasks semana
  + histórico de metas + pontos fortes (>80%) e fracos (<60%)
- Protegido por role=mentor

**Frontend:**
- Rota /mentor protegida por role === 'mentor'
- Lista: nome, área, fase do plano, % meta atual, última atividade
- Detalhe por aluno:
  - Desempenho por matéria (% acerto com indicador visual)
  - Tasks concluídas na semana atual
  - Histórico de metas (últimas 4 semanas)
  - Seção "Pontos fortes" e "Precisa de atenção"

---

## FASE-5 — Limpeza e Deploy

### TASK 5.1 — Deletar Streamlit + routers inativos
⬜ PENDING
**Só executar quando todas as fases anteriores estiverem estáveis.**

```bash
rm app.py api_client.py database.py style.py
rm config_app.py config_fontes.py config_materias.py migrar_dados.py
rm -rf telas/
rm IMPLEMENTATION_GUIDE.md
```
Remover do main.py os routers que o React não usa.

---

### TASK 5.2 — Deploy Railway
⬜ PENDING

1. Restringir CORS:
```python
allow_origins=["http://localhost:5173", "https://dominio.railway.app"]
```
2. Variáveis Railway: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
3. `railway run alembic upgrade head`
4. Testar fluxo completo online

---

## Rotas React completas

| Rota | Página | Role |
|---|---|---|
| /login | Login | público |
| /onboarding | Onboarding | autenticado sem area |
| / | Dashboard | estudante |
| /desempenho | Desempenho | estudante |
| /lancar-bateria | LancarBateria | estudante |
| /admin | AdminDashboard | administrador |
| /admin/questoes | AdminQuestoes | administrador |
| /admin/importar | AdminImportar | administrador |
| /admin/topicos | AdminTopicos | administrador |
| /admin/usuarios | AdminUsuarios | administrador |
| /admin/configuracoes | AdminConfiguracoes | administrador |
| /mentor | MentorDashboard | mentor |
| /mentor/aluno/:id | MentorAlunoDetalhe | mentor |

---

## Regras fixas
1. Contrato quebrado → corrigir backend, nunca adaptar frontend
2. Uma task por vez
3. Testar endpoint no /docs antes de implementar o frontend
4. Código morto só deletar na FASE-5
5. SQLite em dev, PostgreSQL no Railway
6. PlanoBase: nunca gerar duplicata — sempre buscar antes de gerar
7. Área fiscal: única ativa. Outras bloqueadas com "Em desenvolvimento"

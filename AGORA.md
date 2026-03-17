# AGORA.md — Skolai
> Cada task = backend + frontend + testável no navegador.
> Só marcar como concluída quando funcionar de ponta a ponta.
> Atualizado: 16/03/2026.

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev)/PostgreSQL(prod) + Gemini Flash
- Frontend: React 18 + Vite + Tailwind + React Router v6
- Roles: administrador / mentor / estudante
- Streamlit: abandonado — deletar na FASE 5

## Progresso
- 8/20 tasks concluídas
- Em andamento: evolução mensal (gráfico de linha)
- Proxy Vite `/dev` configurado ✅
- Meta gerada automaticamente no onboarding ✅

---

## Regra de implementação
1. Backend primeiro — testar no /docs antes de tocar no frontend
2. Frontend consome o endpoint confirmado
3. Só concluir quando funcionar no navegador de ponta a ponta
4. Contrato quebrado → corrigir backend, nunca adaptar frontend

---

## FASE 2 — Análise de desempenho (em andamento)

### TASK 2.2 — Evolução mensal
🟡 EM ANDAMENTO

**Testa assim:** acessa /desempenho → aba ou seção "Evolução" →
gráfico de linha aparece com dados por matéria ao longo dos meses.

**Backend:** GET /desempenho/evolucao
Retorna: [ { mes, ano, materia, percentual } ]

**Frontend:**
- Gráfico de linha com Recharts ou similar
- Eixo X: meses | Eixo Y: % acerto | Linha por matéria
- Estado vazio: "Nenhum dado ainda — lance suas primeiras baterias"

---

### TASK 2.3 — Lançamento manual de bateria
⬜ PENDING

**O que entrega:** aluno registra resultado de questões feitas fora
do sistema (Qconcursos, TEC, prova anterior) e o desempenho atualiza.

**Testa assim:** acessa /lancar-bateria → preenche matéria, subtópico,
acertos, total, fonte → salva → vai em /desempenho → vê o novo dado.

**Backend:**
- POST /bateria: { materia, subtopico, acertos, total, fonte }
- Confirmar que atualiza SubtopicoEstado e dispara recálculo de desempenho
- GET /topicos/hierarquia para popular os selects de matéria/subtópico

**Frontend (rota /lancar-bateria):**
- Select de matéria → carrega subtópicos do backend
- Campos: acertos (número), total (número), fonte (select com opções)
- Fontes disponíveis: qconcursos, tec, prova_anterior_mesma_banca,
  prova_anterior_outra_banca, simulado, manual
- Submit → feedback de sucesso → opção de lançar outra
- Link para /desempenho para ver o impacto

---

## FASE 3 — Painel Admin

### TASK 3.1 — Layout + gestão de questões
⬜ PENDING

**O que entrega:** admin acessa /admin, vê sidebar própria e consegue
listar, filtrar, editar e deletar questões do banco.

**Testa assim:** login como admin → acessa /admin → vê lista de questões
com filtros → edita uma questão → salva → vê a alteração.

**Backend:**
- GET /questoes?materia=X&subtopico=Y&page=1 — listar com filtros
- PATCH /questoes/{id} — editar questão
- DELETE /questoes/{id} — deletar com confirmação
- Todos protegidos por role=administrador

**Frontend:**
- Rota /admin protegida por role === 'administrador'
- Sidebar separada: Questões | Importar | Tópicos | Usuários
- Página Questões: tabela com filtros, editar inline ou modal, deletar
- Contador de questões por subtópico

---

### TASK 3.2 — Importação em lote com UI completa
⬜ PENDING

**O que entrega:** admin importa questões via JSON ou CSV com
preview, validação visual e feedback de resultado.

**Testa assim:** admin → /admin/importar → faz upload de JSON →
vê preview das questões → confirma → vê "X questões importadas".

**Backend:**
- POST /questoes/importar: aceita array, valida, salva em lote
- Retorna: { importadas: N, erros: [{ linha, motivo }] }
- Resolver subtopico por nome (não só por ID) para facilitar o JSON

**Frontend (página /admin/importar):**
- Upload drag-and-drop de JSON ou CSV
- Preview em tabela antes de confirmar
- Destaque visual nas linhas com erro de validação
- Barra de progresso durante importação
- Resultado: "X importadas, Y com erro" + lista de erros

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

**O que entrega:** admin visualiza e edita a hierarquia de conteúdo
sem precisar mexer no banco diretamente.

**Testa assim:** admin → /admin/topicos → vê árvore matéria→tópico→subtópico
→ edita peso_edital de um subtópico → vê contador de questões atualizado.

**Backend:**
- GET /admin/topicos/hierarquia — árvore completa com contadores
- POST /admin/subtopicos — criar subtópico
- PATCH /admin/subtopicos/{id} — editar nome e peso_edital
- DELETE /admin/subtopicos/{id} — só se não tiver questões vinculadas

**Frontend (página /admin/topicos):**
- Árvore expansível: matéria → tópico → subtópico
- Cada subtópico mostra: nome, peso_edital, nº de questões
- Editar inline o peso_edital
- Adicionar subtópico dentro de um tópico
- Deletar subtópico (desabilitado se tiver questões)

---

### TASK 3.4 — Gestão de usuários
⬜ PENDING

**O que entrega:** admin gerencia alunos, ativa/desativa contas
e atribui mentores.

**Testa assim:** admin → /admin/usuarios → filtra por área →
desativa um aluno → atribui mentor → vê confirmação.

**Backend:**
- GET /admin/usuarios?area=X&role=Y — listar com filtros
- PATCH /admin/usuarios/{id} — ativar/desativar, atribuir mentor
- GET /admin/usuarios/{id}/progresso — resumo de atividade

**Frontend (página /admin/usuarios):**
- Tabela com: nome, email, área, role, ativo, última atividade
- Filtros: área, role, status (ativo/inativo)
- Ações por linha: ativar/desativar, atribuir mentor, ver progresso
- Modal de progresso: meta atual, tasks concluídas, desempenho geral

---

## FASE 4 — Painel do Mentor

### TASK 4.1 — Visão e detalhes dos alunos mentorados
⬜ PENDING

**O que entrega:** mentor acessa /mentor e acompanha o progresso
de cada aluno mentorado com dados reais.

**Testa assim:** login como mentor → acessa /mentor → vê lista de alunos
→ clica em um → vê desempenho por matéria e tasks da semana.

**Backend:**
- GET /mentor/alunos — lista alunos onde mentor_id = current_user.id
- GET /mentor/alunos/{id}/resumo — desempenho + meta atual + tasks semana
- Protegido por role=mentor

**Frontend:**
- Rota /mentor protegida por role === 'mentor'
- Lista de alunos: nome, área, % meta atual, última atividade
- Página de detalhe por aluno:
  - Desempenho por matéria (% acerto)
  - Tasks concluídas na semana atual
  - Histórico de metas (semanas anteriores)
  - Pontos fortes (> 80%) e fracos (< 60%)

---

## FASE 5 — Limpeza e deploy

### TASK 5.1 — Deletar Streamlit + routers inativos
⬜ PENDING

**Executar apenas quando todas as fases anteriores estiverem estáveis.**

```bash
# Streamlit
rm app.py api_client.py database.py style.py
rm config_app.py config_fontes.py config_materias.py migrar_dados.py
rm -rf telas/
rm IMPLEMENTATION_GUIDE.md

# Verificar quais routers o React não usa mais
# Remover imports correspondentes do main.py
```

---

### TASK 5.2 — Deploy Railway
⬜ PENDING

1. Restringir CORS:
```python
allow_origins=["http://localhost:5173", "https://dominio.railway.app"]
```
2. Configurar variáveis no Railway: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
3. `railway run alembic upgrade head`
4. Testar fluxo completo: login → onboarding → dashboard → task → desempenho

---

## Rotas React mapeadas

| Rota | Componente | Role |
|---|---|---|
| /login | Login.jsx | público |
| /onboarding | Onboarding.jsx | autenticado sem area |
| / | Dashboard.jsx | estudante |
| /desempenho | Desempenho.jsx | estudante |
| /lancar-bateria | LancarBateria.jsx | estudante |
| /admin | AdminLayout.jsx | administrador |
| /admin/questoes | AdminQuestoes.jsx | administrador |
| /admin/importar | AdminImportar.jsx | administrador |
| /admin/topicos | AdminTopicos.jsx | administrador |
| /admin/usuarios | AdminUsuarios.jsx | administrador |
| /mentor | MentorDashboard.jsx | mentor |
| /mentor/aluno/:id | MentorAlunoDetalhe.jsx | mentor |


# AGORA.md — Skolai
> Cada task = backend + frontend + testável no navegador.
> Só marcar como concluída quando funcionar de ponta a ponta.
> Atualizado: 20/03/2026 | 10/21 concluídas

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
- ⬜ FASE-6: Backlog priorizado (0/14)

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
Botão "Sugerir Subtópico" chama NLP Mapper e retorna sugestão para o admin confirmar.

**Backend:**
- GET /admin/questoes?materia=X&subtopico=Y&page=1
- PATCH /admin/questoes/{id} — editar campos incluindo subtopico_id
- DELETE /admin/questoes/{id}
- POST /admin/questoes/{id}/sugerir-subtopico — chama NLP Mapper com
  enunciado da questão + lista de subtópicos → retorna sugestão
  (IA só chamada quando admin clica — não automático)

**Frontend:**
- Rota /admin protegida por role === 'administrador'
- Sidebar: Questões | Importar | Tópicos | Usuários | Reportes | Configurações
- Tabela com filtros, editar inline/modal, deletar com confirmação
- Campo subtópico editável + botão "Sugerir" que chama a IA
- Contador de questões por subtópico

---

### TASK 3.2 — Importação em lote (JSON + PDF TEC Concursos)
⬜ PENDING

**Testa assim:** admin → /admin/importar → upload de PDF do TEC →
sistema extrai questões → preview → confirma → "X importadas".
Ou upload de JSON manualmente formatado.

**Backend:**
- POST /admin/questoes/importar-json — array de questões
- POST /admin/questoes/importar-pdf — envia PDF para Gemini Flash extrair
  questões estruturadas (custo < $0.01 por PDF de 200 questões)
  Gemini extrai: banca, tipo (MC/CE), enunciado, alternativas, gabarito,
  matéria, subtópico sugerido
- Retorna: { importadas: N, erros: [{ linha, motivo }] }

**Frontend:**
- Upload drag-and-drop: aceita JSON ou PDF
- Preview em tabela antes de confirmar
- Linhas com subtópico não mapeado sinalizadas para revisão
- Barra de progresso + resultado detalhado

**Formato JSON:**
```json
[{
  "materia": "Direito Administrativo",
  "subtopico": "Atos Administrativos",
  "enunciado": "...",
  "alternativas": ["A)...", "B)...", "C)...", "D)...", "E)..."],
  "gabarito": "C",
  "nivel": "medio",
  "fonte": "CESPE 2023"
}]
```

---

### TASK 3.3 — Gestão de tópicos e subtópicos
⬜ PENDING

**Testa assim:** admin → /admin/topicos → expande Direito Administrativo
→ edita peso_edital → vê contador de questões → adiciona subtópico.

**Backend:**
- GET /admin/topicos/hierarquia — árvore com contadores
- POST/PATCH/DELETE /admin/subtopicos

**Frontend:**
- Árvore expansível: matéria → tópico → subtópico
- peso_edital editável inline
- Deletar desabilitado se tiver questões vinculadas

---

### TASK 3.4 — Gestão de usuários + edição de dados
⬜ PENDING

**Testa assim:** admin → /admin/usuarios → edita dados de um aluno →
desativa → atribui mentor → vê progresso.

**Backend:**
- GET /admin/usuarios?area=X&role=Y&ativo=true
- PATCH /admin/usuarios/{id} — editar nome, email, área, role,
  horas_por_dia, dias_por_semana, nivel_desafio, mentor_id, ativo
- POST /admin/usuarios/{id}/reset-senha — gera senha temporária
- GET /admin/usuarios/{id}/progresso

**Frontend:**
- Tabela: nome, email, área, role, ativo, última atividade
- Modal de edição completa dos campos do aluno
- Redefinição de senha como ação separada
- Modal de progresso: meta atual, tasks, % acerto

---

## FASE-3.5 — PlanoBase + Progressão Pedagógica

### TASK 3.5.1 — Onboarding: áreas + seleção de matérias
⬜ PENDING

**Testa assim:** onboarding → somente Fiscal e CFOE/EAOF são clicáveis →
outras áreas mostram "Em desenvolvimento" → ao avançar, aluno pode
escolher "Sistema decide" ou "Escolher matérias" → se escolher, seleciona
da lista com checkboxes.

**Frontend (StepArea.jsx + novo StepMaterias.jsx):**
- Áreas ativas: Fiscal, CFOE/EAOF
- Demais áreas: bloqueadas com cadeado + tooltip "Em desenvolvimento"
- Nova tela após área: "Como montar seu plano?"
  - "Deixar o sistema decidir" — IA usa todas as matérias da área
  - "Escolher minhas matérias" — exibe lista com checkboxes (mín. 3)
- IA ainda decide a ordem de introdução das matérias selecionadas

**Backend:**
- Salvar `materias_selecionadas` em PerfilEstudo
- plano_inicial.py respeita a seleção ao montar o PlanoBase

---

### TASK 3.5.2 — Model PlanoBase + geração via IA
⬜ PENDING

**Testa assim:** novo aluno faz onboarding → IA gera PlanoBase →
salva no banco → próximo aluno do mesmo perfil usa o cache.

**Backend — model PlanoBase:**
```
id, area, perfil, versao, gerado_por_ia, revisado_admin, ativo
fases_json: [{ numero, nome, criterio_avanco, materias, materias_novas }]
ordem_subtopicos_json: { "Materia": ["subtopico1", ...] }
```

**Lógica:**
1. Busca PlanoBase ativo para area + perfil
2. Existe → usa
3. Não existe → Gemini gera + salva + notifica admin
Nunca gera duplicata.

---

### TASK 3.5.3 — Lógica de avanço de fase + diagnóstico obrigatório
⬜ PENDING

**Testa assim:** aluno com `experiencia=tempo_de_estudo` → diagnóstico
(Meta 00) é obrigatório antes de acessar o dashboard normal.
Aluno atinge 65% nas matérias da fase 1 → sistema adiciona fase 2 automaticamente.

**Backend:**
- Diagnóstico obrigatório para `experiencia != iniciante`
- Remover banner de aviso — bloquear dashboard até Meta 00 concluída
- service avancar_fase.py: roda após cada meta encerrada
- Novos campos em PerfilEstudo: fase_plano_atual, plano_base_id

**Metas numeradas:**
- Meta de diagnóstico = Meta 00
- Metas regulares começam em Meta 01 e incrementam sequencialmente
- Metas finalizadas permanecem acessíveis ao aluno (não somem)

---

### TASK 3.5.4 — Dashboard admin: notificações + revisão PlanoBase
⬜ PENDING

**Testa assim:** IA gera PlanoBase → admin vê banner → clica revisar
→ edita critérios → salva → escolhe "novos alunos" ou "todos".

**Backend:**
- Model Notificacao
- GET /admin/notificacoes
- PATCH /admin/plano-base/{id}
- POST /admin/plano-base/{id}/aplicar { escopo: "novos"|"todos" }

**Frontend:**
- Banner de notificações no dashboard admin
- Editor visual de fases (drag-and-drop matérias, slider critério)

---

## FASE-4 — Painel do Mentor

### TASK 4.1 — Lista e detalhe dos alunos mentorados
⬜ PENDING

**Backend:**
- GET /mentor/alunos
- GET /mentor/alunos/{id}/resumo

**Frontend:**
- Rota /mentor: lista com progresso e última atividade
- Detalhe: desempenho, tasks da semana, histórico metas, fortes/fracos

---

## FASE-5 — Limpeza e Deploy

### TASK 5.1 — Segurança antes do deploy
⬜ PENDING

**Implementar:**
- Confirmação de email no cadastro (Resend ou SendGrid)
- Recuperação de senha com token temporário de uso único (1h)
- Rate limiting no /auth/login: 5 tentativas / 10 min por IP (slowapi)
- Access token curto (1h) + refresh token (30 dias)
- Logs de segurança: logins falhados, acessos admin, 401/403

**Verificar:**
- `senha_hash` nunca aparece em nenhum response
- Todos os endpoints admin retornam 403 (não 404) para role errado
- Validação Pydantic em todos os routers
- dev.db no .gitignore
- Nenhuma chave hardcoded fora do .env
- Histórico git sem chaves expostas

---

### TASK 5.2 — Deletar Streamlit + routers inativos
⬜ PENDING

```bash
rm app.py api_client.py database.py style.py
rm config_app.py config_fontes.py config_materias.py migrar_dados.py
rm -rf telas/ && rm IMPLEMENTATION_GUIDE.md
```

---

### TASK 5.3 — Deploy Railway
⬜ PENDING

1. CORS restrito para domínios reais
2. Variáveis: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
3. `railway run alembic upgrade head`
4. Testar fluxo completo online

---

## FASE-6 — Backlog priorizado

> Items confirmados para implementar. Ordenados por dependência e impacto.
> Formalizar em tasks detalhadas quando FASE-5 estiver concluída.

### B-01 — Correções imediatas (bugs)
⬜ PENDING

- Bug: botão de reset do painel DEV não aparece/funciona
- Bug: lançamento de bateria não está funcionando
- Bug: geração do PlanoBase via IA retorna "A IA não retornou fases válidas"
- Fontes do lançamento de bateria → substituir por bancas reais:
  CESPE/CEBRASPE, FCC, FGV, VUNESP, AOCP, IDECAN, IBFC, QUADRIX,
  IADES, UPENET, Outra banca, Simulado próprio

---

### B-02 — Personalização por funcionalidades do onboarding
⬜ PENDING

Aluno vê só o que selecionou: sidebar, botões PDF/Vídeo e QuestionFlow
condicionais baseados em `funcionalidades_json` do PerfilEstudo.
Requer GET /auth/me retornar `funcionalidades` (join com PerfilEstudo).
Hook `useFuncionalidades()` no frontend.
Painel (/) aparece sempre independente da seleção.

---

### B-03 — Índice de Prontidão (IP)
⬜ PENDING

```
IP = Σ(accuracy_rate × peso_edital × fator_decay × fator_cobertura)
     / Σ(peso_edital) × 100

fator_decay = exp(-decay_rate × dias_sem_revisar)
fator_cobertura: nunca=0 / só teoria=0.5 / teoria+exercicios=1.0
```

Novo service `indice_prontidao.py`.
Alimenta: Mapa de Calor do Edital (B-05), Projeção de Prontidão (B-04),
painel do mentor e dashboard admin.

---

### B-04 — Dashboard de desempenho — novos gráficos
⬜ PENDING

Adicionar em ordem de prioridade (dados já existem no backend):
- Radar de matérias (teia/aranha com % acerto)
- Velocidade de domínio por matéria (barras: dominado/revisão/estudo/não iniciado)
- Volume semanal de questões (barras últimas 8 semanas)
- Heatmap de consistência (calendário estilo GitHub)
- Projeção de prontidão (semanas para atingir limiar — depende do IP B-03)
- Taxa de acerto por tipo de questão (depende do Mapa de Lacunas B-06)

---

### B-05 — Mapa de Calor do Edital
⬜ PENDING

Grade visual cruzando `peso_edital` × `accuracy_rate` por subtópico.
Cores: vermelho (peso alto + domínio baixo) → verde (peso alto + domínio alto).
Responde: "onde devo estudar agora?"
Backend já tem todos os dados. Depende do IP (B-03).
Para pré-edital sem PDF: usa pesos do PlanoBase.

---

### B-06 — Mapa de Lacunas
⬜ PENDING

Diagnóstico contínuo de padrões de erro por subtópico.

**Dados internos:** salvar alternativa escolhida em RespostaQuestao
(hoje só salva acertou/errou). Com isso detectar: confusão de conceito
específica, erro em exceções vs regra geral, erro em aplicação vs conceito.

**Dados externos (Caderno de Questões):**
- Renomear "Lançar bateria" para "Caderno de Questões"
- Campos: matéria, subtópico, acertos, total, banca
- Aparece no Mapa de Lacunas como dado de menor granularidade

**Visibilidade:**
- Lista de subtópicos por resistência ao aprendizado
- Status: travado / melhorando / resolvido
- Padrão detectado após 5+ erros no mesmo subtópico
- Ciclo: lacuna detectada → reforço direcionado → resolvida

---

### B-07 — Questões de validação geradas por IA
⬜ PENDING

Pool por subtópico com threshold:
- < 10 questões → IA gera em background (Celery), não bloqueia aluno
- ≥ 10 questões → sorteia 5 do pool sem chamar IA
- ≥ 30 questões → pool maduro, IA nunca mais chamada para esse subtópico

Registrar questões respondidas por aluno para priorizar não vistas.
`origem=quiz_ia` — usadas só em questionários de validação.

---

### B-08 — Progressão de dificuldade dentro das tasks
⬜ PENDING

Usar campo `nivel` (básico/médio/difícil) nas questões para selecionar
dificuldade conforme `exposure_count` do subtópico:
- exposure_count = 1 → básico/médio
- exposure_count = 2 → médio/difícil
- exposure_count >= 3 → difícil, estilo prova real

Ajuste no `quiz_generator`. Cronograma não cresce.

---

### B-09 — Sistema de reporte de conteúdo IA
⬜ PENDING

Botão discreto de reporte em todo conteúdo gerado por IA
(PDF, vídeos, questões geradas, explicações).

Tipos: conteúdo incorreto, gabarito errado, vídeo fora do tema, outro.
Reporte vinculado ao task_code ou questao_id.

Painel admin — seção Reportes:
- Conteúdo reportado + motivo + quantos alunos reportaram
- Ações: corrigir manualmente, regenerar via IA, ignorar
- Itens com mais de 3 reportes sobem automaticamente

---

### B-10 — Painel financeiro no admin
⬜ PENDING

**Gastos com IA (automático):**
Interceptar chamadas no ai_provider.py, registrar tokens consumidos,
calcular custo por tipo (PDF, vídeo, questões, PlanoBase, edital).
Mostrar: total mensal, por tipo, por aluno, projeção.

**Infraestrutura (manual):**
Admin insere fatura mensal do Railway e outros custos fixos.

**Receita (para quando for pago):**
Campos de plano no Aluno. MRR quando ativo.

---

### B-11 — Fluxo pós-edital via upload de PDF
⬜ PENDING

Upload do PDF do edital no onboarding quando `fase_estudo = pos_edital`.
Gemini extrai: órgão, cargo, banca, data prova, matérias, pesos, nº questões,
conteúdo programático.
NLP Mapper faz correspondência semântica com subtópicos do banco.
Aluno confirma dados extraídos. Admin valida mapeamento.
PlanoBase pós-edital: todas as matérias ativas desde o início,
priorizadas por peso × urgência (dias restantes).
Remover opção pós-edital do onboarding enquanto não implementado.

---

### B-12 — Mapa de Concursos
⬜ PENDING

**Calendário visual:**
Datas de provas abertas na área do aluno.
Destaque: inscrições abertas vs encerradas vs prazo próximo.
Clique: detalhes + link do edital. Botão "Me avise".

**Mapa geográfico:**
Mapa do Brasil com marcadores por estado/status.
Filtros: área, banca, faixa salarial.

**Fonte:** scraping Celery em PCI Concursos + alimentação manual admin.
Admin pode adicionar/editar concursos manualmente.

---

### B-13 — Horas líquidas de estudo
⬜ PENDING

Campo `duracao_real_min` já existe em StudyTask.
Ao finalizar task: campo numérico ou slider "Quanto tempo você estudou?"
Mostrar no dashboard: horas reais vs planejadas na semana,
média diária, evolução semanal.

---

### B-14 — Segurança avançada pós-deploy
⬜ PENDING

Após estabilizar em produção:
- Monitoramento com Sentry (erros em produção)
- Backup automático do banco PostgreSQL
- Alertas de custo de IA por email quando ultrapassar threshold
- Auditoria de acessos admin (log de quem alterou o quê)

---

## Rotas React completas

| Rota | Página | Role |
|---|---|---|
| /login | Login | público |
| /onboarding | Onboarding | autenticado sem area |
| / | Dashboard | estudante |
| /desempenho | Desempenho | estudante |
| /caderno-questoes | CadernoQuestoes | estudante |
| /mapa-lacunas | MapaLacunas | estudante |
| /mapa-concursos | MapaConcursos | estudante |
| /admin | AdminDashboard | administrador |
| /admin/questoes | AdminQuestoes | administrador |
| /admin/importar | AdminImportar | administrador |
| /admin/topicos | AdminTopicos | administrador |
| /admin/usuarios | AdminUsuarios | administrador |
| /admin/reportes | AdminReportes | administrador |
| /admin/financeiro | AdminFinanceiro | administrador |
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
7. Áreas ativas: Fiscal e CFOE/EAOF. Outras bloqueadas.
8. IA só chamada por ação explícita — nunca automatizar 100% sem supervisão
9. Todo conteúdo IA exibido ao aluno deve ter opção de reporte

# AGORA.md — Skolai
> Cada task = backend + frontend + testável no navegador.
> Só marcar como concluída quando funcionar de ponta a ponta.
> Atualizado: 21/03/2026 | 20/43 concluídas

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev)/PostgreSQL(prod) + Gemini Flash
- Frontend: React 18 + Vite + Tailwind + React Router v6
- Roles: administrador / mentor / estudante

## Progresso por fase
- ✅ FASE-0: Banco de questões (2/2)
- ✅ FASE-1: Fluxo do aluno (5/5)
- ✅ FASE-2: Desempenho (3/3)
- ✅ FASE-3: Painel admin base (4/4)
- ✅ FASE-3.5: PlanoBase + progressão pedagógica (4/4)
- ✅ FASE-4: Painel mentor (1/1)
- ⬜ FASE-5: Deploy (1/3) ← próxima
- ⬜ FASE-6: Backlog priorizado (0/21)

---

## Regras de implementação
1. Backend primeiro — testar no /docs antes de tocar no frontend
2. Frontend consome o endpoint confirmado
3. Só concluir quando funcionar no navegador de ponta a ponta
4. Contrato quebrado → corrigir backend, nunca adaptar frontend
5. IA só chamada por ação explícita — nunca automatizar 100% sem supervisão
6. Todo conteúdo IA exibido ao aluno deve ter opção de reporte
7. PlanoBase: nunca gerar duplicata — sempre buscar antes de gerar
8. Plano de estudo opera sobre subtópicos por área, não matérias genéricas
9. Áreas ativas: Fiscal, EAOF-COM, EAOF-SVM, CFOE-COM. Outras bloqueadas.
10. Código morto só deletar na FASE-5

---

## FASE-3 — Painel Admin

### TASK 3.1 — Layout admin + gestão de questões ✅ DONE
### TASK 3.2 — Importação em lote: JSON + PDF TEC Concursos ✅ DONE

---

### TASK 3.3 — Gestão de tópicos, subtópicos e configuração por área
⬜ PENDING

**Testa assim:** admin → /admin/topicos → expande Direito Tributário →
configura peso=0.12 e complexidade=alta para área fiscal →
vê contador de questões por subtópico.

**Backend:**
- GET /admin/topicos/hierarquia — árvore com contadores de questões
- POST/PATCH/DELETE /admin/subtopicos
- Novo model SubtopicoArea: { subtopico_id, area, peso, complexidade }
  complexidade: baixa/media/alta
  Define: nível das questões selecionadas + limiar de domínio por área
  baixa=70% / media=75% / alta=80%
- PATCH /admin/subtopicos/{id}/area — configurar peso e complexidade
- Campo prerequisitos_json em Topico nivel=2: lista de subtopico_ids
  que devem ser dominados antes

**Frontend (página /admin/topicos):**
- Árvore expansível: matéria → tópico → subtópico
- Por subtópico: nome, nº questões, peso e complexidade por área (editável)
- Selector de área para alternar a configuração exibida
- Botão adicionar subtópico dentro de um tópico
- Deletar desabilitado se subtópico tiver questões vinculadas

---

### TASK 3.4 — Gestão de usuários + edição de dados
⬜ PENDING

**Testa assim:** admin → /admin/usuarios → edita dados de um aluno →
desativa → atribui mentor → vê progresso.

**Backend:**
- GET /admin/usuarios?area=X&role=Y&ativo=true
- PATCH /admin/usuarios/{id} — editar: nome, email, área, role,
  horas_por_dia, dias_por_semana, nivel_desafio, mentor_id, ativo
- POST /admin/usuarios/{id}/reset-senha — gera senha temporária
- GET /admin/usuarios/{id}/progresso

**Frontend:**
- Tabela: nome, email, área, role, ativo, última atividade
- Modal de edição completa dos campos do aluno
- Redefinição de senha como ação separada (não no mesmo form)
- Modal de progresso: meta atual, tasks concluídas, % acerto geral

---

## FASE-3.5 — PlanoBase + Progressão Pedagógica

> Base científica: Cognitive Load Theory (Sweller) + Spiral Curriculum (Bruner)
> Plano opera sobre subtópicos, não matérias.
> Subtópico tem peso e complexidade configurados por área.

### TASK 3.5.1 — Onboarding: áreas ativas + perfil de uso + seleção de subtópicos
⬜ PENDING

**Testa assim:** onboarding → Fiscal e áreas militares clicáveis →
outras bloqueadas → aluno escolhe perfil de uso → opcionalmente
seleciona matérias específicas.

**Áreas ativas no onboarding:**
- Fiscal (SEFAZ, Receita Federal, TCE, TCU)
- EAOF-COM (BET/BEI/BCO — Comunicações)
- EAOF-SVM (SEM — Serviços de Manutenção)
- CFOE-COM (BET/BEI/BCO — Comunicações, nível oficial)
- Demais: bloqueadas com cadeado + "Em desenvolvimento"

**Perfil de uso (novo step no onboarding):**
Pergunta: "Como você vai usar o Skolai?"
- Cronograma de estudo — sistema monta e gerencia meu plano
- Análise de desempenho — acompanhar acertos e erros
- Geração de conteúdo — PDFs e vídeos por subtópico
- Geração de questões — praticar com questões

Se cronograma NÃO selecionado:
  Pergunta adicional: "Você já tem um plano externo?"
  (mentor, outra plataforma, plano próprio)

Interface adapta-se silenciosamente à combinação escolhida.
Salvar: funcionalidades_json + tem_plano_externo em PerfilEstudo.

**Seleção de matérias (opcional):**
- "Deixar o sistema decidir" — IA usa todos os subtópicos da área
- "Escolher minhas matérias" — lista com checkboxes (mín. 3 matérias)
- IA ainda decide a ordem pedagógica dos subtópicos selecionados

**Backend:**
- Salvar funcionalidades_json, tem_plano_externo, materias_selecionadas
  em PerfilEstudo

---

### TASK 3.5.2 — Model PlanoBase + geração via IA por subtópico
⬜ PENDING

**Testa assim:** novo aluno onboarding área fiscal → sistema busca
PlanoBase fiscal/iniciante → não existe → IA gera baseado em subtópicos
tagueados para fiscal → salva → admin notificado → próximo aluno usa cache.

**Backend — model PlanoBase:**
```
id, area, perfil (iniciante/intermediario/avancado)
versao, gerado_por_ia, revisado_admin, ativo
fases_json: [{
  numero, nome, criterio_avanco,
  subtopicos: [subtopico_id, ...],  ← não mais matérias
  subtopicos_novos: [subtopico_id, ...]
}]
created_at, updated_at
```

**Lógica de geração:**
1. Busca SubtopicoArea para a área do aluno
2. IA recebe lista de subtópicos com peso, complexidade e pré-requisitos
3. IA retorna ordem pedagógica respeitando:
   - Pré-requisitos entre subtópicos
   - Máx. 15-20 subtópicos na fase 1 (carga cognitiva)
   - Peso na área (subtópicos mais pesados com mais atenção)
   - Complexidade (subtópicos baixa antes de alta)
4. Salva PlanoBase + notifica admin
5. Nunca gera duplicata — sempre busca antes

**Critérios de avanço por área:**
- Fiscal: fase1=65% / fase2=70% / fase3=75% / fase4=80%
- Militar (COM/SVM): mesma lógica, ajustada pela complexidade

---

### TASK 3.5.3 — Lógica de avanço de fase + diagnóstico + metas
⬜ PENDING

**Testa assim:** aluno não-iniciante → Meta 00 obrigatória, dashboard
bloqueado até concluir → atinge critério da fase 1 → fase 2 desbloqueada
automaticamente → notificação "Você avançou para a Fase 2!".

**Backend:**
- Diagnóstico obrigatório para experiencia != iniciante
- Dashboard bloqueado até Meta 00 concluída (não só banner)
- service avancar_fase.py: roda após cada meta encerrada
  Calcula média por subtópico ativo × peso_edital
  Se atingiu criterio_avanco: adiciona subtópicos da fase seguinte
- Novo campo em PerfilEstudo: fase_plano_atual, plano_base_id

**Numeração de metas:**
- Meta de diagnóstico = Meta 00
- Metas regulares: Meta 01, 02, 03...
- Metas finalizadas: permanecem acessíveis ao aluno para consulta

---

### TASK 3.5.4 — Dashboard admin: notificações + revisão PlanoBase
⬜ PENDING

**Testa assim:** IA gera PlanoBase → admin vê banner → clica revisar →
edita critério de avanço → salva → escolhe "novos alunos" ou "todos".

**Backend:**
- Model Notificacao: { id, tipo, titulo, descricao, lida, payload_json }
- GET /admin/notificacoes
- PATCH /admin/notificacoes/{id}/lida
- GET /admin/plano-base/{id}
- PATCH /admin/plano-base/{id} — editar fases e critérios
- POST /admin/plano-base/{id}/aplicar { escopo: "novos"|"todos" }

**Frontend:**
- Banner no topo do dashboard admin para notificações não lidas
- Editor visual de fases: drag-and-drop subtópicos, slider critério
- Modal ao salvar: "Aplicar para novos alunos / Todos os alunos"

---

## FASE-4 — Painel do Mentor

### TASK 4.1 — Lista e detalhe dos alunos mentorados
⬜ PENDING

**Backend:**
- GET /mentor/alunos
- GET /mentor/alunos/{id}/resumo

**Frontend:**
- Rota /mentor protegida por role === 'mentor'
- Lista: nome, área, fase do plano, % meta atual, última atividade
- Detalhe: desempenho por subtópico, tasks da semana,
  histórico metas, pontos fortes (>80%) e fracos (<60%)

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
- senha_hash nunca aparece em nenhum response
- Todos endpoints admin retornam 403 (não 404) para role errado
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
Remover do main.py os routers que o React não usa.

---

### TASK 5.3 — Deploy Railway
⬜ PENDING

1. CORS restrito para domínios reais
2. Variáveis: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
3. railway run alembic upgrade head
4. Testar fluxo completo online

---

## FASE-6 — Backlog priorizado

> Implementar após FASE-5. Formalizar em tasks detalhadas conforme avança.

### B-01 — Correções de bugs imediatos
⬜ PENDING
- Bug: botão reset painel DEV não aparece/funciona
- Bug: lançamento de bateria — lista de matérias não carrega
- Bug: geração PlanoBase via IA retorna "fases inválidas"
- Bug: task não gera conteúdo via IA (PDF/vídeo)
- Bug: Meta 00 não aparece para alunos não-iniciantes
- Bug: banner diagnóstico pendente persiste após conclusão
- Fontes lançamento bateria → bancas reais:
  CESPE/CEBRASPE, FCC, FGV, VUNESP, AOCP, IDECAN, IBFC,
  QUADRIX, IADES, UPENET, Outra banca, Simulado próprio

---

### B-02 — Telas do aluno: perfil, caderno, dashboard
⬜ PENDING

**Perfil do usuário (nova rota /perfil):**
- Editar: nome, email, disponibilidade (horas/dia, dias/semana)
- Alterar senha: campo senha atual + nova + confirmação
- Ver área e experiência cadastradas
- Opção de refazer o onboarding

**Caderno de Questões (renomear /lancar-bateria):**
- Renomear para "Caderno de Questões" em toda a interface
- Select matéria → carrega subtópicos corretamente
- Campos: acertos, total, banca (lista de bancas reais)
- Após salvar: feedback de sucesso + opção de lançar outra

**Dashboard — melhorias:**
- Tasks expandem e geram conteúdo via IA corretamente
- Metas finalizadas acessíveis ao aluno

---

### B-03 — Personalização por funcionalidades do onboarding
⬜ PENDING

Sidebar e componentes condicionais baseados em funcionalidades_json.
GET /auth/me retornar funcionalidades (join com PerfilEstudo).
Hook useFuncionalidades() no frontend.
Interface adapta silenciosamente — sem mostrar "perfil" ao aluno:
- Com cronograma: dashboard com tasks é a tela principal
- Sem cronograma + plano externo: Caderno de Questões é o centro
- Painel (/) sempre visível independente da seleção

---

### B-04 — Índice de Prontidão (IP)
⬜ PENDING

```
IP = Σ(accuracy_rate × peso_area × fator_decay × fator_cobertura)
     / Σ(peso_area) × 100

fator_decay = exp(-decay_rate × dias_sem_revisar)
fator_cobertura: nunca=0 / só teoria=0.5 / teoria+questoes=1.0
```

Novo service indice_prontidao.py.
Alimenta: Mapa de Calor (B-06), Projeção de Prontidão (B-05),
painel mentor, dashboard admin.

---

### B-05 — Dashboard de desempenho — novos gráficos
⬜ PENDING

Em ordem de prioridade (dados já existem no backend):
- Radar de matérias (teia/aranha com % acerto)
- Velocidade de domínio (barras: dominado/revisão/estudo/não iniciado)
- Volume semanal de questões (últimas 8 semanas)
- Heatmap de consistência (calendário estilo GitHub)
- Projeção de prontidão (depende do IP B-04)
- Taxa de acerto por tipo de questão (depende do B-07)

---

### B-06 — Mapa de Calor do Edital
⬜ PENDING

Grade visual cruzando peso_area × accuracy_rate por subtópico.
Cores: vermelho (peso alto + domínio baixo) → verde (dominado).
Responde: "onde devo estudar agora?"
Depende do IP (B-04).
Para pré-edital: usa pesos do PlanoBase.

---

### B-07 — Mapa de Lacunas
⬜ PENDING

Diagnóstico contínuo de padrões de erro por subtópico.

Dados internos: salvar alternativa escolhida em RespostaQuestao.
Com isso detectar confusão de conceito específica após 5+ erros.

Dados externos: Caderno de Questões alimenta o mapa com menor
granularidade (sabe que errou, não sabe como).

Visibilidade: lista por resistência ao aprendizado.
Status: travado / melhorando / resolvido.
Ciclo fechado: lacuna → reforço direcionado → resolvida.

---

### B-08 — Base de conhecimento por upload de fontes
⬜ PENDING

Admin faz upload de PDFs (legislações, manuais, doutrinas, materiais
de estudo) sem precisar organizar por subtópico antes.

Sistema processa automaticamente:
- Extrai texto via pdfplumber
- Divide em chunks por seção (RAG)
- IA mapeia cada chunk para subtópicos relevantes do banco
- Indexa para busca semântica

Ao gerar conteúdo ou questão para um subtópico:
Prioridade: 1. chunks das fontes upadas → 2. legislação oficial
→ 3. conhecimento geral da IA (fallback)

Para vídeos do YouTube:
- Sistema busca transcrição automática via API
- Se indisponível: salva metadados (título, canal, URL) para recomendação
- Admin pode adicionar links com anotação do conteúdo coberto

Fontes do NotebookLM do admin: exportar os PDFs originais e upar.
A IA gera fundamentada no material já validado para concurso.

Nova rota admin: /admin/fontes
- Listar fontes upadas por área/subtópico
- Upload + vínculo automático por área
- Status de processamento (pendente/indexado)
- Deletar fonte

Reativa SVE como área viável — regulamentos internos da FAB
(ICA 83-1, ICA 85-16, ICA 87-7, SISPNR) upados pelo admin
resolvem o problema de conteúdo não indexado na internet.

---

### B-09 — Questões geradas por IA (fallback + validação)
⬜ PENDING

Quando banco insuficiente para um subtópico ou aluno esgotou questões:
IA gera em background (Celery) e salva com board="IA".

Pool por subtópico:
- < 10 questões → IA gera lote de 10 em background
- ≥ 10 questões → sorteia sem chamar IA
- ≥ 30 questões → pool maduro, IA nunca mais chamada

Geração em lote: 10 questões por chamada para economizar tokens.
Registrar questões respondidas por aluno para priorizar não vistas.
Aviso de origem obrigatório: "Questão gerada por IA —
gabarito pode conter imprecisões" no enunciado e no gabarito.

---

### B-10 — Progressão de dificuldade dentro das tasks
⬜ PENDING

Usar campo nivel (básico/médio/difícil) por exposure_count:
- exposure_count = 1 → básico/médio
- exposure_count = 2 → médio/difícil
- exposure_count >= 3 → difícil, estilo prova real

Ajuste no quiz_generator. Cronograma não cresce.

---

### B-11 — Sistema de reporte de conteúdo IA
⬜ PENDING

Botão discreto em todo conteúdo gerado por IA:
PDF, vídeos, questões geradas, explicações pós-gabarito.

Tipos: conteúdo incorreto, gabarito errado, vídeo fora do tema, outro.
Vinculado ao task_code ou questao_id.

Painel admin /admin/reportes:
- Conteúdo + motivo + nº de alunos que reportaram
- Ações: corrigir manualmente, regenerar via IA, ignorar
- Itens com 3+ reportes sobem automaticamente

---

### B-12 — Painel financeiro (duas fases)
⬜ PENDING

**B-12a — Controle de custos pré-beta (implementar antes do deploy):**
Interceptar chamadas em ai_provider.py → registrar em log_ia:
tipo, tokens_input, tokens_output, custo_estimado, aluno_id.
Dashboard admin /admin/financeiro:
- Custo total do mês por tipo de geração
- Custo por aluno beta (ranking de consumo)
- Projeção mensal
- Custos fixos manuais (Railway, domínio)

**B-12b — Monetização pós-beta (após dados reais de consumo):**
Usar dados do B-12a para precificar os planos.
Model Plano com limites configuráveis pelo admin.
Middleware de verificação por feature.
Gateway de pagamento (Pagar.me ou Stripe).
Tela de upgrade para o aluno com comparativo de planos.
MRR, churn, margem por aluno no painel admin.

---

### B-13 — Fluxo pós-edital via upload de PDF
⬜ PENDING

Upload PDF do edital no onboarding quando fase_estudo = pos_edital.
Gemini extrai: órgão, cargo, banca, data prova, subtópicos, pesos.
NLP Mapper cruza com SubtopicoArea da área do aluno.
Aluno confirma dados. Admin valida mapeamento antes de ativar.
PlanoBase pós-edital: todos os subtópicos do edital ativos desde o início,
priorizados por peso × urgência (dias restantes).
Remover opção pós-edital do onboarding até implementado.

---

### B-14 — Chat com IA contextualizado
⬜ PENDING

Chat integrado com contexto automático do aluno:
subtópico atual, matéria, fase de estudo, erros recentes do Mapa de Lacunas.

Dois pontos de acesso:
- Dentro da task: "Tirar dúvida sobre este tema"
- Ícone flutuante global disponível em qualquer tela

Limitação por plano: número de mensagens por período.
Internamente registrar tokens em log_ia para controle de custo.
Aviso progressivo ao se aproximar do limite.

Contexto injetado automaticamente (invisível ao aluno):
subtópico + matéria + fase + erros recentes.

---

### B-15 — Mapa de Concursos
⬜ PENDING

Calendário visual: datas de provas na área do aluno.
Destaque: inscrições abertas / encerradas / prazo próximo.
Clique: detalhes + link edital. Botão "Me avise".

Mapa geográfico: marcadores por estado e status.
Filtros: área, banca, faixa salarial.

Fonte: scraping Celery + alimentação manual admin.

---

### B-16 — Horas líquidas de estudo
⬜ PENDING

duracao_real_min já existe em StudyTask.
Ao finalizar task: campo numérico "Quanto tempo você estudou?"
Dashboard: horas reais vs planejadas, média diária, evolução semanal.

---

### B-17 — Upload de PDF de prova pelo aluno (meio do beta)
⬜ PENDING

Aluno faz upload de PDF com questões (provas antigas, apostilas).
IA extrai — mesmo pipeline do admin.
Questões entram na fila de revisão do admin com identificação do aluno.
Pendente: disponível só para o aluno que enviou.
Após aprovação admin: entra no banco compartilhado.

---

### B-18 — Áreas militares — subtópicos e banco
⬜ PENDING

Criar no banco os subtópicos para EAOF-COM, EAOF-SVM e CFOE-COM.

**COM (EAOF e CFOE — banco unificado):**
- Eletricidade Básica: Lei de Ohm, Circuitos CC, CA, Transformadores...
- Eletrônica Digital: Portas Lógicas, Álgebra de Boole, Flip-Flop...
- Princípios de Telecomunicações: Ondas de Rádio, Antenas, Transmissão...
- Regulamentos de Telecom EAOF: MCA 102-7
- Regulamentos Militares (comum EAOF): Estatuto, CPM, CPPM, RDAER, RISAER

**SVM (EAOF):**
- Suprimento e Logística: Armazenagem, Material SSS, Gestão de Estoques
- Transporte de Superfície: Viaturas, Combustíveis, Gerenciamento
- Código de Trânsito: capítulos do edital
- Meio Ambiente: CONAMA 273/00, CONAMA 362/05
- Contratações: Lei 14.133 (já existe), Manual COMAER
- Corrosão: Eletroquímica, Formas, Revestimentos

Upar legislações FAB como fontes (B-08) para SVM e futuramente SVE.
GIT, MAT e Inglês já existem no banco — servem para todos.

---

### B-19 — Segurança avançada pós-deploy
⬜ PENDING

- Monitoramento com Sentry
- Backup automático PostgreSQL
- Alertas de custo de IA por email ao ultrapassar threshold
- Auditoria de acessos admin (log de quem alterou o quê)

---

### B-20 — Aviso de origem nas questões
⬜ PENDING

Toda questão exibida ao aluno deve indicar origem:
- Banca real: mostrar banca + ano
- Gerada por IA: "Questão gerada por IA — gabarito pode conter imprecisões"
- Contribuída por aluno (futuro): "Enviada por usuário"

Aviso aparece no enunciado E no feedback pós-resposta.
Conecta com sistema de reporte (B-11).

---

### B-21 — Arquitetura pedagógica por subtópico e área
⬜ PENDING

Consolidar a mudança de matéria → subtópico como unidade do plano.

Campo area em Topico (nivel=0) corrigir: deve armazenar
"fiscal"/"eaof_com"/"eaof_svm"/"cfoe_com", não o nome da matéria.
Script de migração: setar area corretamente para as 57 matérias.

SubtopicoArea ativo para todas as áreas ativas.
plano_inicial.py e engine_pedagogica.py operar sobre SubtopicoArea.
PlanoBase gerado com subtopicos_ids, não nomes de matéria.

---

## Rotas React completas

| Rota | Página | Role |
|---|---|---|
| /login | Login | público |
| /onboarding | Onboarding | autenticado sem area |
| / | Dashboard | estudante |
| /desempenho | Desempenho | estudante |
| /perfil | Perfil | estudante |
| /caderno-questoes | CadernoQuestoes | estudante |
| /mapa-lacunas | MapaLacunas | estudante |
| /mapa-concursos | MapaConcursos | estudante |
| /admin | AdminDashboard | administrador |
| /admin/questoes | AdminQuestoes | administrador |
| /admin/importar | AdminImportar | administrador |
| /admin/fontes | AdminFontes | administrador |
| /admin/topicos | AdminTopicos | administrador |
| /admin/usuarios | AdminUsuarios | administrador |
| /admin/reportes | AdminReportes | administrador |
| /admin/financeiro | AdminFinanceiro | administrador |
| /admin/configuracoes | AdminConfiguracoes | administrador |
| /mentor | MentorDashboard | mentor |
| /mentor/aluno/:id | MentorAlunoDetalhe | mentor |


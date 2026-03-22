# AGORA.md — Skolai
> Cada task = backend + frontend + testável no navegador.
> Só marcar como concluída quando funcionar de ponta a ponta.
> Atualizado: 22/03/2026 | 22/46 concluídas | www.skolai.com.br no ar

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev)/PostgreSQL(prod) + Gemini 1.5 Flash
- Frontend: React 18 + Vite + Tailwind + React Router v6 + Caddy
- Roles: administrador / mentor / estudante
- Deploy: Railway — Frontend (Dockerfile+Caddy) + Backend + PostgreSQL

## Progresso
- ✅ FASE-0: Banco de questões (2/2)
- ✅ FASE-1: Fluxo do aluno (5/5)
- ✅ FASE-2: Desempenho (3/3)
- ✅ FASE-3: Painel admin base (4/4)
- ✅ FASE-3.5: PlanoBase + progressão pedagógica (4/4)
- ✅ FASE-4: Painel mentor (1/1)
- ✅ FASE-5: Segurança + deploy (3/3)
- ⬜ FASE-6: Backlog priorizado (0/24) ← atual

---

## Infraestrutura Railway — NÃO alterar sem necessidade

### Serviços
| Serviço | URL | Status |
|---|---|---|
| Frontend | www.skolai.com.br | Online |
| Backend | domínio Railway interno | Online |
| PostgreSQL | gerado pelo Railway | Online |

### Variáveis de ambiente — Backend
- DATABASE_URL — PostgreSQL Railway (automático)
- SECRET_KEY — chave JWT
- GEMINI_API_KEY — API Gemini
- ALLOWED_ORIGINS — https://www.skolai.com.br
- ADMIN_EMAIL, ADMIN_NOME, ADMIN_SENHA

### Variáveis de ambiente — Frontend
- VITE_API_URL — URL pública do backend
- PORT = 80

### Arquivos críticos — não modificar
- `frontend/Dockerfile` — build 2 estágios: node:18-alpine + caddy:2-alpine
- `frontend/.dockerignore` — sem isso node_modules Windows quebra o build
- `frontend/Caddyfile` — try_files obrigatório para React Router funcionar
- `frontend/railway.toml` — builder = "dockerfile" (não nixpacks)
- Ferramentas de build em `dependencies` (não devDependencies)

### O que NÃO fazer
- Não voltar para nixpacks — quebra build por NODE_ENV=production
- Não deletar .dockerignore do frontend
- Não remover PORT=80 das variáveis do frontend
- Não mover vite/tailwind para devDependencies sem testar em Docker limpo
- Não remover try_files do Caddyfile
- Não alterar DATABASE_URL manualmente — Railway gerencia automaticamente
- Não commitar .env, dev.db ou sisfig.db — estão no .gitignore, manter assim
- Não remover o fix postgres:// → postgresql:// em config.py (database_url_compat)
- Não alterar ALLOWED_ORIGINS para "*" em produção — manter restrito
- Não usar gemini-2.5-flash — caro demais, usar gemini-1.5-flash-8b ou gemini-1.5-flash

### Fluxo obrigatório ao mudar o schema do banco
Qualquer nova tabela ou coluna criada localmente exige:
```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head                          # testa local
git add alembic/versions/
git commit && git push                        # Railway faz deploy
railway run alembic upgrade head              # aplica no PostgreSQL
```
Sem esse último passo o backend sobe mas quebra ao acessar a nova tabela.

---

## Regras de implementação
1. Backend primeiro — testar no /docs antes de tocar no frontend
2. Frontend consome o endpoint confirmado
3. Só concluir quando funcionar no navegador de ponta a ponta
4. Contrato quebrado → corrigir backend, nunca adaptar frontend
5. IA só chamada por ação explícita — nunca em loop automático
6. Todo conteúdo IA exibido ao aluno deve ter opção de reporte
7. PlanoBase opera sobre subtópicos por área, não matérias
8. Modelo de IA padrão: gemini-1.5-flash-8b (tarefas simples)
   gemini-1.5-flash (tarefas complexas como PlanoBase e PDF)
9. Áreas ativas: Fiscal, EAOF-COM, EAOF-SVM, CFOE-COM. Outras bloqueadas.

---

## FASE-6 — Backlog priorizado

> Ordenado por impacto no beta test.
> B-00 é o primeiro passo — banco de produção está vazio.

---

### B-00 — Migrar dados do dev.db para o PostgreSQL do Railway
⬜ PENDING — FAZER ANTES DE QUALQUER OUTRA COISA

**Por que primeiro:** o banco de produção está vazio. Matérias, subtópicos,
questões importadas e dados de teste estão só no dev.db local.
Sem isso o site não tem conteúdo nenhum.

**O que precisa migrar:**
- 57 matérias e subtópicos (hierarquia completa)
- Questões importadas
- Ciclos configurados por área
- SubtopicoArea (peso e complexidade por área)
- Alunos de teste (opcional — podem se cadastrar pelo site)

**Como fazer:**
Pedir ao Claude Code para criar `scripts/migrar_dev_para_railway.py`:
- Lê todos os dados do dev.db via SQLAlchemy
- Insere no PostgreSQL do Railway respeitando ordem de dependências
  (matérias antes de tópicos, tópicos antes de subtópicos, etc.)
- Ignora duplicatas (upsert) para poder rodar mais de uma vez com segurança

```bash
railway run python scripts/migrar_dev_para_railway.py
```

**Verificar depois:**
- Acessar /admin/topicos no site → matérias aparecem
- Acessar /admin/questoes → questões aparecem

---

### B-01 — Correções de bugs imediatos
⬜ PENDING

**Testa assim:** aluno consegue usar o sistema de ponta a ponta sem
erros visíveis no fluxo principal.

- Bug: task não gera conteúdo via IA (botões PDF e vídeo não funcionam)
- Bug: lançamento de bateria não carrega lista de matérias
- Bug: geração do PlanoBase retorna "A IA não retornou fases válidas"
  → corrigir prompt para retornar apenas fases[], ordem_subtopicos{},
    prerequisitos{} — critérios de avanço são fixos no código
- Bug: botão de reset do painel DEV não aparece/funciona
- Bug: Meta 00 não aparece para alunos não-iniciantes
- Bug: banner de diagnóstico continua aparecendo após concluído
- Fontes do lançamento de bateria → trocar para bancas reais:
  CESPE/CEBRASPE, FCC, FGV, VUNESP, AOCP, IDECAN, IBFC,
  QUADRIX, IADES, UPENET, Outra banca, Simulado próprio
- Modelo de IA: trocar gemini-2.5-flash → gemini-1.5-flash-8b
  em ai_provider.py e verificar se está hardcoded em outros arquivos

---

### B-02 — Telas do aluno funcionando de fato
⬜ PENDING

**Testa assim:** aluno loga → tem perfil editável → consegue registrar
sessão no caderno de questões → task gera conteúdo real.

**Perfil do usuário (não existe ainda):**
- Nova rota /perfil
- Editar: nome, email, senha (atual + nova + confirmação)
- Editar disponibilidade: horas/dia, dias/semana
- Ver área e experiência cadastradas
- Opção de refazer o onboarding

**Caderno de Questões (lançamento de bateria renomeado):**
- Renomear rota /lancar-bateria → /caderno-questoes
- Corrigir carregamento da lista de matérias e subtópicos
- Campos: matéria, subtópico, acertos, total, banca (lista de bancas reais)
- Feedback de sucesso + opção de registrar outra sessão
- Histórico de sessões registradas

**Tasks com conteúdo:**
- Botão PDF: chamar POST /task-conteudo/{task_code}/gerar-pdf
  com loading "Gerando conteúdo..." (~15s)
- Botão Vídeo: GET /task-conteudo/{task_code}/videos
- Aviso discreto de origem em todo conteúdo gerado por IA:
  "Conteúdo gerado por IA — pode conter imprecisões"
- Botão de reporte junto ao aviso

---

### B-03 — Personalização por funcionalidades do onboarding
⬜ PENDING

**Testa assim:** aluno que selecionou só cronograma_estudo → sidebar
mostra só Painel e Agenda. Aluno sem cronograma → Caderno de Questões
vira tela principal.

**Backend:**
- GET /auth/me retornar funcionalidades (join com PerfilEstudo)
- Salvar tem_plano_externo (bool) em PerfilEstudo

**Frontend:**
- Hook useFuncionalidades() lendo user.funcionalidades
- Sidebar condicional por funcionalidade ativa
- Dashboard reorganiza conforme combinação selecionada:
  - com cronograma → tasks do dia em destaque
  - sem cronograma + plano externo → Caderno de Questões em destaque
- Botões PDF/Vídeo só se geracao_conteudo ativo
- QuestionFlow só se geracao_questoes ativo
- Painel (/) aparece sempre

---

### B-04 — Índice de Prontidão (IP)
⬜ PENDING

```
IP = Σ(accuracy_rate × peso_area × fator_decay × fator_cobertura)
     / Σ(peso_area) × 100

fator_decay = exp(-decay_rate × dias_sem_revisar)
fator_cobertura: nunca=0 / só teoria=0.5 / teoria+exercicios=1.0
```

Novo service `indice_prontidao.py`.
Alimenta: B-05 (Mapa de Calor), B-06 (gráficos desempenho),
painel mentor e dashboard admin.

---

### B-05 — Dashboard desempenho — novos gráficos
⬜ PENDING

Adicionar em ordem de prioridade:
- Radar de matérias (teia com % acerto por matéria)
- Velocidade de domínio (barras: dominado/revisão/estudo/não iniciado)
- Volume semanal de questões (barras últimas 8 semanas)
- Heatmap de consistência (calendário estilo GitHub)
- Projeção de prontidão (semanas para atingir limiar — depende B-04)
- Taxa de acerto por tipo de questão (depende B-07)

---

### B-06 — Mapa de Calor do Edital
⬜ PENDING

Grade visual cruzando peso_area × accuracy_rate por subtópico.
Cores: vermelho (peso alto + domínio baixo) → verde (dominado).
Responde: "onde devo estudar agora?"
Para pré-edital sem PDF: usa pesos do PlanoBase.
Depende do IP (B-04).

---

### B-07 — Mapa de Lacunas
⬜ PENDING

Diagnóstico contínuo de padrões de erro por subtópico.

Salvar alternativa escolhida em RespostaQuestao (hoje só acertou/errou).
Com isso detectar: confusão de conceito, erro em exceções vs regra,
erro em aplicação vs conceito puro.

Visibilidade para o aluno:
- Lista de subtópicos por resistência ao aprendizado
- Status: travado / melhorando / resolvido
- Padrão detectado após 5+ erros no mesmo subtópico
- Ciclo: lacuna → reforço direcionado → resolvida

Caderno de Questões alimenta o mapa como dado de menor granularidade.

---

### B-08 — Base de conhecimento por upload de fontes
⬜ PENDING

Admin upa PDFs brutos (leis, manuais, doutrinas, legislações FAB).
Sistema processa automaticamente:
- Extrai texto via pdfplumber
- Divide em chunks por seção
- IA mapeia cada chunk para subtópicos relevantes
- Indexa para busca semântica (RAG)

Para vídeos do YouTube:
- Transcrição automática via API YouTube se disponível
- Fallback: metadados (título, canal, URL) para recomendação

Prioridade ao gerar conteúdo:
```
1. Chunks de fontes upadas para aquele subtópico
2. Legislação oficial upada
3. Conhecimento geral da IA (fallback)
```

Nova rota: /admin/fontes
Nova sidebar admin: Questões | Importar | Fontes | Tópicos | Usuários |
                    Reportes | Financeiro | Configurações

---

### B-09 — Questões geradas por IA (fallback + pool)
⬜ PENDING

Quando não há questões suficientes no banco para um subtópico:
```
1. Questões do banco não vistas pelo aluno (origem banca real)
2. Questões do banco já vistas (repetição controlada)
3. IA gera em background (Celery) → salva com board="IA"
```

Pool por subtópico:
- < 10 questões → IA gera lote de 10 em background
- ≥ 10 questões → sorteia sem chamar IA
- ≥ 30 questões → pool maduro, IA nunca mais chamada

Aviso obrigatório nas questões geradas por IA:
"Questão gerada por IA — gabarito pode conter imprecisões"
Botão de reporte junto ao aviso.

Registrar questões respondidas por aluno para evitar repetição.

---

### B-10 — Progressão de dificuldade dentro das tasks
⬜ PENDING

Usar campo nivel (básico/médio/difícil) nas questões para selecionar
dificuldade conforme exposure_count do subtópico:
- exposure_count = 1 → básico/médio
- exposure_count = 2 → médio/difícil
- exposure_count >= 3 → difícil, estilo prova real da área

Ajuste no quiz_generator. Cronograma não cresce.

---

### B-11 — Sistema de reporte de conteúdo IA
⬜ PENDING

Botão discreto em todo conteúdo gerado por IA.
Tipos: conteúdo incorreto, gabarito errado, vídeo fora do tema, outro.
Reporte vinculado ao task_code ou questao_id.

Painel admin → Reportes:
- Conteúdo + motivo + quantos alunos reportaram
- Ações: corrigir, regenerar via IA, ignorar
- Itens com 3+ reportes sobem automaticamente

---

### B-12 — Painel financeiro
⬜ PENDING

**B-12a — Controle de custos pré-beta (implementar agora):**
- Interceptar todas as chamadas em ai_provider.py
- Registrar em log_ia: tipo, tokens_input, tokens_output,
  custo_estimado, aluno_id, created_at
- Dashboard admin: custo total mês, por tipo, por aluno,
  projeção, custos fixos manuais (Railway, domínio)

**B-12b — Seleção de modelo por tipo de operação (implementar agora):**
- Tabela configuracoes_sistema no banco
- Admin configura modelo por tipo de operação:
  geração questões, PDF, sugestão subtópico, PlanoBase, chat, extração PDF
- Modelos disponíveis: gemini-1.5-flash-8b | gemini-1.5-flash | gemini-1.5-pro
- ai_provider.py consulta a configuração antes de cada chamada

**B-12c — Monetização pós-beta:**
- Definir planos baseado nos dados do B-12a
- Model Plano com limites configuráveis
- Gateway de pagamento (Pagar.me ou Stripe)
- Tela de upgrade para o aluno
- MRR, churn, margem por aluno

---

### B-13 — Fluxo pós-edital via upload de PDF
⬜ PENDING

Upload do PDF do edital no onboarding (fase_estudo = pos_edital).
Gemini extrai: órgão, cargo, banca, data prova, subtópicos, pesos.
NLP Mapper faz correspondência com subtópicos do banco.
Aluno confirma. Admin valida mapeamento antes de ativar.
PlanoBase pós-edital: todos os subtópicos do edital ativos,
priorizados por peso × urgência (dias restantes).
Remover opção pós-edital do onboarding enquanto não implementado.

---

### B-14 — Chat com IA contextualizado
⬜ PENDING

Contexto automático injetado (invisível ao aluno):
subtópico atual, matéria, fase, erros recentes do Mapa de Lacunas.

Dois pontos de acesso:
- Dentro da task expandida: "Tirar dúvida sobre este tema"
- Ícone flutuante global em qualquer tela

Limite por plano (número de mensagens por período).
Aviso de uso: "X de Y perguntas usadas esta semana".
Registrar consumo de tokens em log_ia.

---

### B-15 — Mapa de Concursos
⬜ PENDING

Calendário visual com datas de provas na área do aluno.
Mapa geográfico do Brasil com marcadores por estado/status.
Filtros: área, banca, faixa salarial.
Botão "Me avise" por concurso.
Fonte: scraping Celery (PCI Concursos) + alimentação manual admin.

---

### B-16 — Horas líquidas de estudo
⬜ PENDING

duracao_real_min já existe em StudyTask.
Ao finalizar task: campo "Quanto tempo você estudou?" (slider ou número).
Dashboard: horas reais vs planejadas na semana, média diária,
evolução semanal.

---

### B-17 — Ordem de aparição dos subtópicos
⬜ PENDING

Campo ordem (inteiro) em cada subtópico dentro da matéria.
Engine usa esse campo para sequenciar as tasks do aluno.

Admin configura via /admin/topicos:
- Drag-and-drop para reordenar subtópicos dentro de cada tópico
- Botão "Sugerir ordem pedagógica" por matéria — IA ordena todos
  os subtópicos de uma vez, admin confirma ou ajusta
- Para pós-edital: ordem importada do edital automaticamente

prerequisitos_json complementa a ordem — sistema não libera subtópico
sem os pré-requisitos concluídos.

---

### B-18 — Áreas militares — subtópicos e banco
⬜ PENDING

Criar no banco os subtópicos para COM e SVM:

COM (serve EAOF e CFOE):
  Eletricidade Básica → Lei de Ohm, Circuitos CC, CA, Transformadores
  Eletrônica Digital → Portas Lógicas, Circuitos, Flip-Flop, Conversores
  Princípios de Telecomunicações → Ondas, Transmissão, Antenas, Sistemas Digitais
  Regulamentos Militares → Estatuto, CPM, CPPM, RDAER, RISAER (só EAOF)
  Telecomunicações COMAER → MCA 102-7 (só EAOF)

SVM (EAOF):
  Suprimento e Logística → Armazenagem, Material SSS, Gestão de Estoques
  Transporte de Superfície → Viaturas, Combustíveis, Gerenciamento
  Legislação de Trânsito → CTB capítulos do edital
  Meio Ambiente → CONAMA 273/00, CONAMA 362/05
  Contratações Públicas → Lei 14.133, Manual COMAER
  Corrosão → Eletroquímica, Formas de Corrosão, Revestimentos

Upar legislações FAB como fontes (B-08) vinculadas a esses subtópicos.
GIT, MAT e Inglês já existem no banco — servem para todas as especialidades.

---

### B-19 — Arquitetura pedagógica por subtópico e área
⬜ PENDING

Corrigir campo area em Topico — hoje armazena nome da matéria
em vez de "fiscal", "eaof", "cfoe".
SubtopicoArea (já existe) com peso e complexidade por área.
plano_inicial.py e engine_pedagogica.py operar sobre subtópicos
tagueados pela área, não sobre matérias.

Complexidade por área define:
- Nível das questões selecionadas
- Profundidade do conteúdo gerado
- Limiar de domínio: baixa=70% / média=75% / alta=80%

---

### B-20 — Aviso de origem nas questões
⬜ PENDING

Indicação discreta de origem em toda questão exibida:
- Banca real (CESPE, FGV, etc): mostrar banca + ano
- Gerada por IA: "Questão gerada por IA — gabarito pode conter imprecisões"
- Contribuição de aluno (quando implementado): "Enviada por usuário"

Aparece no enunciado e no feedback pós-resposta.
Conecta com sistema de reporte (B-11).

---

### B-21 — Upload de PDF de prova pelo aluno
⬜ PENDING (meio do beta)

Aluno upa PDF de prova antiga, apostila ou caderno escaneado.
IA extrai questões — mesmo pipeline do admin.
Questões entram na fila de revisão do admin com identificação do aluno.
Enquanto pendente: disponíveis só para o aluno que enviou.
Após aprovação admin: entram no banco compartilhado.

---


### B-22 — Segurança avançada pós-deploy
⬜ PENDING

- Monitoramento com Sentry (erros em produção)
- Backup automático do PostgreSQL Railway → Google Drive via GitHub Actions
  (você tem Google One — espaço não é problema)
  Workflow: todo dia às 3h → pg_dump → upload para pasta "Backups Skolai" no Drive
  Retenção: 30 dias (deleta backups antigos automaticamente)
  Secrets necessários: RAILWAY_DATABASE_URL, GDRIVE_CREDENTIALS, GDRIVE_FOLDER_ID
- Alertas de custo de IA por email quando ultrapassar threshold configurável
- Auditoria de acessos admin (log de quem alterou o quê e quando)

---

### B-23 — Confirmação de email e recuperação de senha
⬜ PENDING

Ficou pendente da FASE-5 (foi marcado como concluído parcialmente).
- Confirmação de email no cadastro (Resend ou SendGrid)
- Recuperação de senha com token temporário de uso único (1h)
- Email de boas-vindas após confirmação

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
| /perfil | Perfil | estudante |
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

---

## Critérios pedagógicos fixos no código

```python
CRITERIOS_AVANCO = {1: 0.65, 2: 0.70, 3: 0.75, 4: 0.80, 5: 0.85}
MAX_MATERIAS_FASE_1 = 4
MAX_MATERIAS_NOVAS_POR_FASE = 3
LIMIAR_DOMINIO = {"baixa": 0.70, "media": 0.75, "alta": 0.80}
```

A IA do PlanoBase retorna APENAS:
- fases[]: quais matérias entram em cada fase e em que ordem
- ordem_subtopicos{}: sequência pedagógica dos subtópicos por matéria
- prerequisitos{}: dependências diretas entre subtópicos

NUNCA gera critérios de avanço, limiares ou configurações pedagógicas.


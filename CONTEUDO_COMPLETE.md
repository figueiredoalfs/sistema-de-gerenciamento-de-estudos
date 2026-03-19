# SKOLAI — Plataforma de Gestão de Estudos para Concursos Públicos
**Documentação Completa do Software**

---

## 📋 ÍNDICE
1. [Visão Geral](#visão-geral)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Estrutura de Diretórios](#estrutura-de-diretórios)
5. [Models (Banco de Dados)](#models-banco-de-dados)
6. [Routers (API)](#routers-api)
7. [Services (Lógica de Negócio)](#services-lógica-de-negócio)
8. [Módulos Especializados](#módulos-especializados)
9. [Funcionalidades Principais](#funcionalidades-principais)
10. [Fluxos de Usuário](#fluxos-de-usuário)
11. [Padrões e Regras](#padrões-e-regras)
12. [Status do Projeto](#status-do-projeto)
13. [Como Rodar](#como-rodar)
14. [Dependências](#dependências)

---

## VISÃO GERAL

**SKOLAI** é uma plataforma web de gestão de estudos para candidatos a concursos públicos brasileiros. Combina:

- **Cronograma Adaptativo**: Agendamento inteligente baseado em disponibilidade do aluno
- **Análise de Desempenho**: Acompanhamento de evolução com relatórios detalhados
- **Geração de Conteúdo com IA**: Explicações, flashcards e exemplos gerados dinamicamente
- **Baterias de Questões**: Banco de questões organizado por matéria e subtópico
- **Painel Administrativo**: Gestão de usuários, tópicos e questões

### Objetivo Beta
Criar MVP com funcionalidades essenciais simples e escaláveis, sem complexidade desnecessária.

---

## STACK TECNOLÓGICO

### Backend
- **Framework**: FastAPI 0.115.0
- **ORM**: SQLAlchemy 2.0.35
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Auth**: JWT + bcrypt (python-jose)
- **Task Queue**: Celery 5.4.0 (modo eager local)
- **IA**: Google Generative AI (Gemini Flash) + Anthropic
- **PDF**: reportlab, pdfplumber
- **Validação**: Pydantic 2.9.2

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS 3
- **Roteamento**: React Router v6
- **HTTP Client**: axios

### Infraestrutura
- **Migrations**: Alembic 1.13.3
- **Servidor**: Uvicorn 0.30.6
- **Deploy**: Railway

---

## ARQUITETURA DO SISTEMA

### Princípios Arquiteturais

1. **Modular**: Cada funcionalidade em módulo separado
2. **Camadas Lógicas**:
   - **Camada BD**: Models, migrations
   - **Camada API**: Routers, schemas, services
   - **Camada CONFIG**: Configuração, documentação
3. **Separação de Responsabilidades**:
   - **Routers**: Recebem request, validam, delegam a services
   - **Services**: Implementam lógica de negócio
   - **Models**: Representam entidades, sem lógica complexa

### Estrutura Modular

```
app/
├── core/
│   ├── database.py      (Configuração SQLAlchemy)
│   ├── security.py      (JWT, hash)
│   ├── ai_provider.py   (Interface IA)
│   └── config.py
├── models/              (SQLAlchemy ORM)
├── routers/             (Endpoints da API)
├── services/            (Lógica de negócio)
├── schemas/             (Pydantic request/response)
├── scripts/             (Seed, migrations)
└── modules/             (Funcionalidades especializadas)
```

---

## ESTRUTURA DE DIRETÓRIOS

```
sistema-de-gerenciamento-de-estudos/
├── app/
│   ├── __init__.py
│   ├── main.py                 (FastAPI app)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ai_provider.py      (Camada de IA)
│   │   ├── config.py           (Variáveis de configuração)
│   │   ├── database.py         (SQLAlchemy setup)
│   │   └── security.py         (Auth JWT + hash)
│   ├── models/                 (SQLAlchemy models)
│   │   ├── aluno.py
│   │   ├── ciclo_materia.py
│   │   ├── config_sistema.py
│   │   ├── cronograma.py
│   │   ├── erro_critico.py
│   │   ├── exam.py
│   │   ├── explicacao_subtopico.py
│   │   ├── meta.py
│   │   ├── meta_semanal.py
│   │   ├── padrao_cognitivo.py
│   │   ├── perfil_estudo.py
│   │   ├── plano_base.py
│   │   ├── proficiencia.py
│   │   ├── questao.py
│   │   ├── questao_banco.py
│   │   ├── question_attempt.py
│   │   ├── question_subtopic.py
│   │   ├── resposta_questao.py
│   │   ├── sessao.py
│   │   ├── simulado.py
│   │   ├── study_session.py
│   │   ├── study_task.py
│   │   ├── subject.py
│   │   ├── subtopico_estado.py
│   │   ├── task_conteudo.py
│   │   ├── task_video.py
│   │   ├── task_video_avaliacao.py
│   │   ├── topic.py
│   │   ├── topico.py
│   │   ├── topic_progress.py
│   │   └── __init__.py
│   ├── routers/                (Endpoints API)
│   │   ├── admin_ciclos.py
│   │   ├── admin_importar_questoes.py
│   │   ├── admin_plano_base.py
│   │   ├── admin_stats.py
│   │   ├── admin_topicos.py
│   │   ├── agenda.py
│   │   ├── auth.py
│   │   ├── bateria.py
│   │   ├── conhecimento.py
│   │   ├── cronograma_semanal.py
│   │   ├── desempenho.py
│   │   ├── erro_critico.py
│   │   ├── explicacoes.py
│   │   ├── metas.py
│   │   ├── onboarding.py
│   │   ├── questoes.py
│   │   ├── respostas.py
│   │   ├── study_tasks.py
│   │   ├── task_conteudo.py
│   │   ├── usuarios.py
│   │   └── __init__.py
│   ├── services/               (Lógica de negócio)
│   │   ├── avancar_fase.py
│   │   ├── decay.py
│   │   ├── desempenho_diagnostico.py
│   │   ├── engine_pedagogica.py
│   │   ├── explicacao_subtopico.py
│   │   ├── gerador_cronograma.py
│   │   ├── gerar_plano_base.py
│   │   ├── plano_inicial.py
│   │   ├── plano_pos_diagnostico.py
│   │   ├── priorizacao.py
│   │   ├── questao_ia.py
│   │   ├── sugestao_subtopicos.py
│   │   ├── task_conteudo_service.py
│   │   └── __init__.py
│   ├── schemas/                (Pydantic schemas)
│   │   ├── aluno.py
│   │   ├── meta.py
│   │   ├── questao.py
│   │   ├── resposta_questao.py
│   │   ├── study_task.py
│   │   └── ...
│   ├── scripts/                (Seed, utilitários)
│   │   ├── seed_admin.py
│   │   ├── seed_ciclos.py
│   │   └── seed_topicos.py
│   ├── modules/                (Funcionalidades especializadas)
│   │   ├── conteudo/
│   │   │   ├── router.py       (Geração de conteúdo)
│   │   │   └── service.py
│   │   └── onboarding/
│   │       ├── router.py       (Fluxo de primeiro acesso)
│   │       └── service.py
│   └── workers/                (Background jobs)
│
├── alembic/                    (Database migrations)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── (migration files)
│
├── frontend/                   (React + Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/              (Páginas principais)
│   │   │   ├── Onboarding.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TaskView.jsx
│   │   │   ├── Desempenho.jsx
│   │   │   ├── AdminPlanoBase.jsx
│   │   │   └── ...
│   │   ├── components/         (Componentes React)
│   │   │   ├── task/
│   │   │   ├── onboarding/
│   │   │   ├── admin/
│   │   │   ├── layout/
│   │   │   └── ...
│   │   ├── api/                (Clientes HTTP)
│   │   │   ├── client.js
│   │   │   ├── admin.js
│   │   │   ├── tasks.js
│   │   │   ├── conteudo.js
│   │   │   └── ...
│   │   ├── styles/
│   │   └── hooks/              (Custom React hooks)
│   └── public/
│
├── docs/                       (Documentação técnica)
│   ├── ALGORITMO.md            (Engine pedagógica)
│   ├── IA.md                   (Estratégia de IA)
│   ├── MODELS.md               (Schema do banco)
│   ├── ONBOARDING.md           (Fluxo de onboarding)
│   ├── PEDAG.md                (Pedagogia)
│   ├── REGRAS.md               (Regras de negócio)
│   └── SESSOES.md              (Espécies de session)
│
├── README.md
├── PROJECT_RULES.md            (Regras de desenvolvimento)
├── IMPLEMENTATION_GUIDE.md     (Lista de tasks)
├── AGORA.md                    (Status atual)
├── CAMADAS.md                  (Camadas do sistema)
├── CLAUDE_PROMPT.MD            (Instruções para IA)
├── SESSAO.md                   (Notas de sessão)
├── STATUS.json                 (Progress tracking)
├── requirements.txt            (Dependências Python)
├── alembic.ini                 (Config Alembic)
├── Procfile                    (Deploy Railway)
├── railway.toml                (Config Railway)
└── .env (exemplo)
```

---

## MODELS (Banco de Dados)

### Core

#### Aluno
Representa um estudante na plataforma.
```python
- id: UUID
- email: str (unique)
- password_hash: str
- nome: str
- role: str (enum: 'estudante', 'mentor', 'administrador')
- ativo: bool
- data_criacao: datetime
- mentor_id: UUID (opcional, FK para outro Aluno)
```

#### PerfilEstudo
Perfil de aprendizagem do aluno.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- area: str (enum: 'fiscal', 'juridica', 'policial', 'ti', 'saude')
- fase: str (enum: 'pre_edital', 'pos_edital')
- experiencia: str (enum: 'iniciante', 'alguns_meses', 'mais_tempo')
- horas_por_dia: float
- dias_por_semana: int
- funcionalidades: JSON
- plano_base_id: UUID (FK PlanoBase)
- data_criacao: datetime
```

### Baterias & Questões

#### Subject (Matéria)
Matérias do concurso (Direito Constituicional, Português, etc).
```python
- id: UUID
- nome: str
- area: str
- peso_edital: float
- descricao: str (opcional)
- ativo: bool
```

#### Topic (Tópico)
Tópicos principais dentro de uma matéria.
```python
- id: UUID
- subject_id: UUID (FK Subject)
- nome: str
- nivel: int (1=matéria, 2=tópico, 3=subtópico)
- peso_edital: float
- ativo: bool
- descricao: str (opcional)
```

#### Topico (Subtópico)
Nível granular de estudo.
```python
- id: UUID
- topic_id: UUID (FK Topic)
- nome: str
- peso_edital: float
- ativo: bool
- ordem: int
```

#### QuestãoBanco
Banco de questões da plataforma.
```python
- id: UUID
- subject_id: UUID (FK Subject)
- subtopico_id: UUID (FK Topico, opcional)
- enunciado: str
- alternativas: JSON (list[str])
- gabarito: str (A-E)
- nivel: str (facil, medio, dificil)
- fonte: str (CESPE, FCC, etc)
- comentario: str (opcional)
- revisado_admin: bool
- criado_por: UUID (FK Aluno, admin que criou)
- data_criacao: datetime
```

#### QuestionSubtopic
Relacionamento muitos-para-muitos entre questões e subtópicos.
```python
- questao_id: UUID (FK)
- subtopico_id: UUID (FK)
```

#### QuestionAttempt
Registro de tentativas de responder questões.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- questao_id: UUID (FK QuestãoBanco)
- resposta_selecionada: str
- acertou: bool
- tempo_resposta: int (segundos)
- tentativa_numero: int
- data_tentativa: datetime
```

### Tarefas de Estudo

#### StudyTask
Tarefa de estudo gerada pelo sistema.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- subject_id: UUID (FK Subject)
- topic_id: UUID (FK Topic)
- subtopic_id: UUID (FK Topico)
- tipo: str (theory, reforco, exercises, exam_sim)
- descricao: str
- status: str (pendente, em_andamento, concluida)
- progresso_percentual: float
- prioridade: str (alta, media, baixa)
- meta_id: UUID (FK Meta)
- week_number: int
- order_in_week: int
- data_prevista: date
- data_conclusao: date (opcional)
- task_code: str (único)
- criada_em: datetime
```

#### TaskConteudo
Conteúdo gerado (PDFs, explicações) para uma task.
```python
- id: UUID
- task_code: str (FK StudyTask)
- tipo: str (theory, reforco, exercises)
- objetivo: str (gerado com IA)
- instrucoes: str (gerado com IA)
- conteudo_pdf: str (markdown ou HTML)
- estrutura_json: JSON (componentes da estrutura)
- criado_em: datetime
```

#### TaskVideo
Videos recomendados para uma task.
```python
- id: UUID
- task_code: str (FK StudyTask)
- titulo: str
- url: str
- duracao_minutos: int
- fonte: str (YouTube, etc)
- relevancia_score: float
- criado_em: datetime
```

#### TaskVideoAvaliacao
Avaliação do aluno sobre a qualidade de um video.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- video_id: UUID (FK TaskVideo)
- nota: int (1-5)
- comentario: str (opcional)
- data_avaliacao: datetime
```

### Cronograma & Metas

#### Meta
Meta de estudo do aluno (semanal).
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- numero_meta: int
- data_inicio: date
- data_fim: date
- status: str (planejada, em_andamento, concluida)
- tasks_meta: relationship(StudyTask)
- criada_em: datetime
```

#### Cronograma
Agendamento semanal de tarefas.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- semana_numero: int
- tasks_agendadas: JSON
- criado_em: datetime
```

### Desempenho

#### Sessão
Sessão de estudo do aluno.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- task_id: UUID (FK StudyTask)
- data_inicio: datetime
- data_fim: datetime (opcional)
- tempo_total_segundos: int
- questoes_respondidas: int
- taxa_acerto: float
- notas_aluno: str (opcional)
- status: str (em_andamento, concluida)
```

#### Proficiência
Nível de domínio em cada subtópico.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- subtopico_id: UUID (FK Topico)
- nivel: float (0-10)
- ultima_atualizacao: datetime
- fonte_calculo: str (questoes, diagnostico, etc)
```

#### ErroCrítico
Erros frequentes do aluno.
```python
- id: UUID
- aluno_id: UUID (FK Aluno)
- subtopico_id: UUID (FK Topico)
- questoes_acertadas: int
- questoes_erradas: int
- percentual_erro: float
- flagged_como_critico: bool
- data_atualizacao: datetime
```

### Admin

#### PlanoBase
Base pedagógica personalizada para cada area/perfil.
```python
- id: UUID
- area: str
- perfil: str (iniciante, intermediario, avancado)
- fases: JSON (estrutura de fases)
- gerado_por_ia: bool
- revisado_admin: bool
- versao: int
- proxima_versao_draft: JSON (rascunho)
- criado_em: datetime
- atualizado_em: datetime
```

---

## ROUTERS (API)

### Autenticação

#### POST /auth/register
Criar novo usuário.
```
Request:
  - email: str
  - password: str
  - nome: str

Response:
  - aluno_id: UUID
  - email: str
  - token: str
```

#### POST /auth/login
Fazer login e obter JWT.
```
Request:
  - email: str
  - password: str

Response:
  - token: str
  - aluno_id: UUID
  - role: str
```

#### GET /auth/me
Dados do usuário autenticado.
```
Response:
  - id: UUID
  - email: str
  - nome: str
  - role: str
```

### Onboarding

#### POST /onboarding
Primeiro fluxo: cria perfil de estudo.
```
Request:
  - area: str
  - fase: str
  - experiencia: str
  - horas_por_dia: float
  - dias_por_semana: int
  - funcionalidades: list[str]

Response:
  - aluno_id: UUID
  - perfil_estudo_id: UUID
  - funcionalidades: list[str]
  - tasks_geradas: list[StudyTaskResponse]
```

### Tarefas de Estudo

#### GET /study-tasks
Listar tasks do aluno.
```
Query params:
  - status: str (opcional)
  - tipo: str (opcional)
  - page: int

Response: list[StudyTaskResponse]
```

#### GET /study-tasks/{id}
Detalhes de uma task específica.
```
Response: StudyTaskResponse (com progresso)
```

#### PATCH /study-tasks/{id}
Atualizar status/progresso de uma task.
```
Request:
  - status: str
  - progresso_percentual: float

Response: StudyTaskResponse
```

#### POST /study-tasks/{id}/concluir
Marcar task como concluída.
```
Response: { sucesso: bool, mensagem: str }
```

### Conteúdo

#### GET /task-conteudo/{task_code}
Obter conteúdo gerado para uma task.
```
Response:
  - objetivo: str
  - instrucoes: str
  - conteudo_pdf: str
  - estrutura: JSON
```

#### POST /task-conteudo/{task_code}/gerar-pdf
Gerar PDF/conteúdo com IA.
```
Response:
  - conteudo_pdf: str
  - gerado_em: datetime
```

#### GET /task-conteudo/{task_code}/videos
Listar videos recomendados.
```
Response: list[TaskVideoResponse]
```

#### POST /task-conteudo/{task_code}/videos/buscar
Buscar novos videos com IA.
```
Response: { videos_adicionados: int }
```

#### POST /task-videos/{video_id}/avaliar
Avaliar qualidade de um video.
```
Request:
  - nota: int (1-5)
  - comentario: str (opcional)

Response: { sucesso: bool }
```

### Módulo Conteúdo (IA)

#### POST /conteudo/resumo
Gerar resumo com IA.
```
Request:
  - topico: str

Response:
  - topico: str
  - resumo: str
```

#### POST /conteudo/flashcards
Gerar flashcards com IA.
```
Request:
  - topico: str

Response:
  - topico: str
  - flashcards: list[{ pergunta, resposta }]
```

#### POST /conteudo/exemplo
Gerar exemplo prático com IA.
```
Request:
  - topico: str

Response:
  - topico: str
  - exemplo: str
```

### Questões

#### GET /questoes
Listar questões (alunos veem seu banco personalizado).
```
Query params:
  - materia_id: UUID (opcional)
  - subtopico_id: UUID (opcional)
  - nivel: str (opcional)
  - page: int

Response: Paginated[QuestãoResponse]
```

#### GET /questoes/{id}
Detalhes de uma questão.
```
Response: QuestãoResponse
```

#### POST /questoes/{id}/responder
Registrar resposta a uma questão.
```
Request:
  - resposta_selecionada: str (A-E)

Response:
  - acertou: bool
  - gabarito: str
  - comentario: str
```

### Desempenho

#### GET /desempenho
Resumo de desempenho do aluno.
```
Response:
  - taxa_acerto_geral: float
  - questoes_respondidas: int
  - tempo_estudo_total: int
  - desempenho_por_materia: dict
  - erros_criticos: list[ErrosCriticosResponse]
  - evolucao_mensal: list[{ mes, taxa_acerto }]
```

#### GET /desempenho/{materia_id}
Desempenho detalhado por matéria.
```
Response:
  - materia: str
  - taxa_acerto: float
  - questoes_respondidas: int
  - subtopicos: list[{
      nome: str,
      taxa_acerto: float,
      flag_critico: bool
    }]
```

### Agenda

#### GET /agenda
Tarefas priorizadas para hoje/semana.
```
Query params:
  - data: date (opcional)

Response:
  - sessoes_hoje: list[AgendaItemResponse]
  - sessoes_semana: list[AgendaItemResponse]
  - prioridade_calculo: str (descrição do algoritmo usado)
```

### Metas

#### GET /metas
Histórico de metas do aluno.
```
Response: list[MetaResponse]
```

#### GET /metas/{id}
Detalhes de uma meta.
```
Response: MetaResponse (com tasks associadas)
```

#### POST /metas
Gerar nova meta.
```
Request: { }

Response: MetaResponse
```

### Admin - Questões

#### GET /admin/questoes
Listar questões (admin).
```
Query params:
  - materia_id: UUID
  - subtopico_id: UUID
  - page: int

Response: Paginated[QuestãoAdminResponse]
```

#### PATCH /admin/questoes/{id}
Editar questão.
```
Request:
  - enunciado: str
  - alternativas: list[str]
  - gabarito: str
  - nivel: str
  - comentario: str

Response: QuestãoAdminResponse
```

#### DELETE /admin/questoes/{id}
Deletar questão.
```
Response: { sucesso: bool }
```

#### POST /admin/questoes/importar
Importar questões em lote.
```
Request:
  - questoes: list[{
      materia: str,
      subtopico: str,
      enunciado: str,
      alternativas: list[str],
      gabarito: str,
      nivel: str,
      fonte: str
    }]

Response:
  - importadas: int
  - erros: list[{ linha, motivo }]
```

### Admin - Tópicos

#### GET /admin/topicos/hierarquia
Árvore completa de matérias/tópicos/subtópicos.
```
Response:
  - materias: list[{
      id: UUID,
      nome: str,
      topicos: list[{
        id: UUID,
        nome: str,
        subtopicos: list[{
          id: UUID,
          nome: str,
          peso_edital: float,
          num_questoes: int
        }]
      }]
    }]
```

#### POST /admin/subtopicos
Criar subtópico.
```
Request:
  - topic_id: UUID
  - nome: str
  - peso_edital: float

Response: SubtopicoResponse
```

#### PATCH /admin/subtopicos/{id}
Editar subtópico.
```
Request:
  - nome: str
  - peso_edital: float

Response: SubtopicoResponse
```

#### DELETE /admin/subtopicos/{id}
Deletar subtópico (só se sem questões).
```
Response: { sucesso: bool }
```

### Admin - Usuários

#### GET /admin/usuarios
Listar usuários.
```
Query params:
  - area: str (opcional)
  - role: str (opcional)
  - ativo: bool (opcional)
  - page: int

Response: Paginated[UsuarioAdminResponse]
```

#### PATCH /admin/usuarios/{id}
Editar usuário (ativar/desativar, atribuir mentor).
```
Request:
  - ativo: bool
  - mentor_id: UUID (opcional)

Response: UsuarioAdminResponse
```

#### GET /admin/usuarios/{id}/progresso
Ver progresso de um aluno.
```
Response:
  - meta_atual: MetaResponse
  - tasks_concluidas: int
  - taxa_acerto_geral: float
  - desempenho_por_materia: dict
```

### Admin - PlanoBase

#### GET /admin/plano-base
Listar planos base.
```
Query params:
  - area: str (opcional)
  - perfil: str (opcional)
  - pendente_revisao: bool (opcional)

Response: Paginated[PlanoBa Response]
```

#### POST /admin/plano-base/gerar
Gerar novo plano base com IA.
```
Request:
  - area: str
  - perfil: str

Response:
  - id: UUID
  - status: str (draft, em_revisao, aprovado)
```

#### PATCH /admin/plano-base/{id}
Editar/revisar plano base.
```
Request:
  - fases: JSON
  - revisado_admin: bool

Response: PlanoBaseResponse
```

#### POST /admin/plano-base/{id}/aprovar
Aprovar plano base.
```
Response: { sucesso: bool }
```

#### DELETE /admin/plano-base/{id}
Deletar plano base (draft).
```
Response: { sucesso: bool }
```

---

## SERVICES (Lógica de Negócio)

### engine_pedagogica.py
Motor pedagógico que:
- Calcula FSRS (taxas de retenção)
- Determina fase do aluno
- Gera metas semanais
- Prioriza tarefas

**Funções principais:**
```python
def verificar_encerramento_meta(aluno_id, db) -> bool
def gerar_meta(aluno_id, db) -> Meta
def obter_proximas_tarefas_aluno(aluno_id, limite=10, db=None) -> list[StudyTask]
```

### gerador_cronograma.py
Gera cronograma adaptativo.

**Fórmula:**
```
tasks_semanais = int(horas_por_dia × dias_por_semana)
```

- Round-robin entre matérias
- Distribuição por semana
- Assignação de `week_number` e `order_in_week`

### desempenho_diagnostico.py
Calcula desempenho e percentual de acerto.

**Funções:**
```python
def calcular_e_salvar_desempenho_diagnostico(aluno_id, db)
def taxa_acerto_por_subtopico(aluno_id, subtopico_id, db) -> float
def erros_criticos(aluno_id, db) -> list[ErroCrítico]
```

### plano_pos_diagnostico.py
Gera tasks de reforço baseadas em weak areas.

### task_conteudo_service.py
Geração de conteúdo com IA.

**Funções:**
```python
def gerar_objetivo_instrucoes(conteudo: TaskConteudo, db)
def gerar_pdf(task_code: str, db: Session) -> str
def buscar_videos(task_code: str, db: Session)
```

**Prompt para IA:**
```
"Você é um professor de cursinho preparatório.
Escreva material sobre [subtópico] (máx 600 palavras).
Estruture com: ## Conceito | ### Como cobrado | ### Pontos-chave"
```

### questao_ia.py
Geração de questões com IA.

### explicacao_subtopico.py
Explicações curriculares com IA.

### priorizacao.py
Algoritmo de priorização de tarefas.

**Critérios:**
- Urgência (data prevista)
- FSRS (when to review again)
- Proficiência (áreas fracas)
- Progresso da meta

### decay.py
Decay de retenção (FSRS).

---

## MÓDULOS ESPECIALIZADOS

### modules/conteudo/
Geração inteligente de conteúdo.

**Routers:**
- POST /conteudo/resumo
- POST /conteudo/flashcards
- POST /conteudo/exemplo

**Service** integra com `core/ai_provider.py`.

### modules/onboarding/
Fluxo de primeiro acesso do aluno.

**Passo 1:** Selecionar área (Fiscal, Jurídica, etc)  
**Passo 2:** Selecionar fase (Pré-edital / Pos-edital)  
**Passo 3:** Selecionar experiência (Iniciante / Tempo de estudo)  
**Passo 4:** Configurar disponibilidade (horas/dia, dias/semana)  
**Passo 5:** Selecionar funcionalidades (geração conteúdo, análise desempenho, etc)

---

## FUNCIONALIDADES PRINCIPAIS

### 1. Autenticação & Autorização
- Registro de novo usuário
- Login com JWT
- Roles: administrador, mentor, estudante
- Proteção de endpoints por role

### 2. Onboarding
- Coleta de preferências (área, fase, disponibilidade)
- Criação automática de meta inicial
- Sugestão de funcionalidades

### 3. Cronograma Adaptativo
- Gera tasks baseadas em:  
  - Horas/dia e dias/semana do aluno
  - Matérias da área escolhida
  - Distribuição round-robin
- Atualiza conforme progresso

### 4. Banco de Questões
- Questões por matéria/subtópico
- Níveis (fácil, médio, difícil)
- Importação em lote (JSON/CSV)
- Admin pode editar/deletar

### 5. Análise de Desempenho
- Taxa de acerto geral
- Desempenho por matéria/subtópico
- Erros críticos (weak areas)
- Gráficos de evolução mensal

### 6. Geração de Conteúdo com IA
- Explicações (PDFs)
- Resumos
- Flashcards
- Exemplos práticos
- Busca automática de videos (YouTube)

### 7. Painel Administrativo
- Gestão de questões (CRUD)
- Importação em lote
- Gestão de tópicos/subtópicos
- Gestão de usuários
- Aprovação de PlanoBase

### 8. PlanoBase (Pedagógico)
- Base estructurada por area/perfil
- Aprovação admin
- Versionamento

---

## FLUXOS DE USUÁRIO

### Fluxo 1: Primeiro Acesso (Aluno)

```
1. Register (email + password)
2. Redirect /onboarding
3. Selecionar área (Fiscal)
4. Selecionar fase (Pré-edital / Pos-edital)
5. Selecionar experiência
6. Configurar disponibilidade
7. Selecionar funcionalidades
8. POST /onboarding → cria PerfilEstudo + Meta01 + tasks geradas
9. Redirect /dashboard
```

### Fluxo 2: Estudo Diário

```
1. GET /agenda (tarefas priorizadas para hoje)
2. Selecionar tarefa
3. GET /study-tasks/{id} (detalhes)
4. GET /task-conteudo/{task_code} (ler material)
5. GET /task-conteudo/{task_code}/videos (assistir videos)
6. GET /questoes?subtopico_id=X (resolver questões)
7. POST /questoes/{id}/responder (registrar resposta)
8. PATCH /study-tasks/{id} (atualizar progresso)
9. GET /desempenho (ver resultado)
```

### Fluxo 3: Administração

```
1. Login como administrador
2. GET /admin/topicos/hierarquia (ver estrutura)
3. POST /admin/questoes/importar (importar em lote)
4. GET /admin/usuarios (listar alunos)
5. PATCH /admin/usuarios/{id} (atribuir mentor)
6. GET /admin/plano-base (revisar planos)
7. POST /admin/plano-base/{id}/aprovar (aprovar)
```

---

## PADRÕES E REGRAS

### Padrões de Código

1. **Tipagem clara**
   - Usar type hints em funções
   - Usar Pydantic para schemas

2. **Separação de responsabilidades**
   - Routers: apenas validação + delegação
   - Services: toda a lógica
   - Models: apenas representação de dados

3. **Éviter complexidade desnecessária**
   - No beta, simplicidade primeiro
   - Refatorações futuras conforme necessário

4. **Nomeação consistente**
   - Models: CamelCase (Aluno, StudyTask)
   - Functions: snake_case (gerar_meta, calcular_desempenho)
   - Routers: kebab-case em URLs (/study-tasks, /task-conteudo)

### Regras do Projeto

1. Seguir arquitetura modular (app/core, app/models, app/routers, app/services)
2. Não adicionar bibliotecas externas sem justificativa
3. Não refatorar sem necessidade
4. Nunca implementar funcionalidades fora da tarefa atual
5. IA apenas para gerar conteúdo (explicações, exemplos, flashcards)
6. Banco dados: SQLite (dev), PostgreSQL (prod)

---

## STATUS DO PROJETO

### Fases

| Fase | Descrição | Status | Progresso |
|------|-----------|--------|-----------|
| FASE-0 | Banco de questões | ✅ Concluída | 2/2 |
| FASE-1 | Fluxo do aluno | ✅ Concluída | 5/5 |
| FASE-2 | Desempenho | ✅ Concluída | 3/3 |
| FASE-3 | Painel admin | ⬜ Pendente | 0/4 |
| FASE-3.5 | PlanoBase + pedagogia | ⬜ Pendente | 0/4 |
| FASE-4 | Painel mentor | ⬜ Pendente | 0/1 |
| FASE-5 | Limpeza + deploy | ⬜ Pendente | 0/2 |

### Implementadas

✅ Autenticação JWT  
✅ Modelos de dados completos  
✅ Onboarding com IA  
✅ Cronograma adaptativo  
✅ Geração de conteúdo com IA  
✅ Análise de desempenho  
✅ Banco de questões  
✅ Dashboard do aluno  
✅ Frontend com React + Tailwind  

### Em Desenvolvimento

⬜ Painel administrativo completo  
⬜ PlanoBase pedagógico  
⬜ Painel do mentor  
⬜ Importação de questões  
⬜ Gestão de tópicos/subtópicos  

---

## COMO RODAR

### Pré-requisitos

- Python 3.8+
- Node.js 16+
- SQLite (incluso) ou PostgreSQL

### Backend

```bash
# Ativar virtual env
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar migrations
alembic upgrade head

# Seed de dados (tópicos, ciclos, admin)
# Automático ao iniciar (veja app/main.py lifespan)

# Iniciar servidor
uvicorn app.main:app --reload
# API em: http://localhost:8000
# Docs (Swagger): http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev
# App em: http://localhost:5173

# Build para produção
npm run build
```

### Variáveis de Ambiente

Criar `.env` na raiz:

```env
# Banco de dados
DATABASE_URL=sqlite:///./test.db
# Para produção: postgresql://user:pass@localhost/skolai

# JWT
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# IA
GEMINI_API_KEY=sua-chave-gemini
ANTHROPIC_API_KEY=sua-chave-anthropic

# CORS
FRONTEND_URL=http://localhost:5173

# Admin padrão
ADMIN_EMAIL=admin@skolai.com
ADMIN_PASSWORD=admin123
```

---

## DEPENDÊNCIAS

### Python (Backend)

```
FastAPI 0.115.0 - Web framework
SQLAlchemy 2.0.35 - ORM
Alembic 1.13.3 - Migrations
Pydantic 2.9.2 - Validação
python-jose 3.3.0 - JWT
passlib 1.7.4 - Hash de senhas
bcrypt 4.0.1 - Criptografia
python-dotenv 1.0.1 - Variáveis de env
uvicorn 0.30.6 - ASGI server
google-generativeai 0.8.3 - Gemini Flash API
anthropic 0.37.1 - Claude API
reportlab 4.2.2 - Geração de PDFs
pdfplumber 0.11.4 - Leitura de PDFs
openpyxl 3.1.5 - Leitura de Excel
pandas 2.2.3 - Data analysis
httpx 0.27.2 - HTTP client
```

### Node.js (Frontend)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.0.0",
    "axios": "^1.0.0",
    "tailwindcss": "^3.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

---

## CONTATO & DOCUMENTAÇÃO ADICIONAL

- **Documentação Técnica**: Veja pasta `/docs/`
- **Guia de Implementação**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Regras do Projeto**: [PROJECT_RULES.md](PROJECT_RULES.md)
- **Status Atual**: [AGORA.md](AGORA.md)

---

**Última atualização**: 18 de março de 2026

**Versão do Projeto**: Beta 0.1.0

---


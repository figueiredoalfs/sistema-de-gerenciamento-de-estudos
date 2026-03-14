# ConcursoAI — Implementation Guide

Este arquivo controla a implementação do sistema.

Instruções para o agente:

1) Leia este documento inteiro antes de iniciar.
2) Identifique a primeira tarefa marcada como ⬜ PENDING.
3) Marque como 🟡 IN_PROGRESS.
4) Implemente completamente.
5) Marque como ✅ DONE.
6) Não pule tarefas.
7) Não implemente funcionalidades fora da tarefa atual.

Regra importante:

Siga estritamente a arquitetura descrita neste documento.

Não adicione complexidade desnecessária.

Objetivo do projeto:

Criar uma plataforma de estudo para concursos com:

- cronograma adaptativo
- análise de desempenho
- geração de conteúdo com IA
- baterias de questões

Este é um **beta inicial**, então a arquitetura deve ser simples.

Funcionalidades avançadas serão implementadas depois.

---

# Arquitetura do sistema

Stack principal:

- FastAPI
- SQLAlchemy
- SQLite (dev)
- PostgreSQL (produção)
- Gemini Flash (IA)

Estrutura de diretórios:

app/

core/
database.py
security.py
ai_provider.py

models/
user.py
exam.py
subject.py
topic.py
topic_progress.py
question_attempt.py
study_session.py

modules/

onboarding/
router.py
service.py

baterias/
router.py
service.py

desempenho/
router.py
service.py

cronograma/
router.py
service.py

conteudo/
router.py
service.py

---

# Modelos do sistema

## User

id
email
password_hash
role
created_at

roles:

admin
student

---

## Exam

id
nome
data_prova

---

## Subject

id
exam_id
nome
peso_edital

---

## Topic

id
subject_id
nome
peso_edital

---

## TopicProgress

user_id
topic_id

accuracy_rate
questions_answered

last_studied
last_review
next_review

priority_score

---

## QuestionAttempt

id
user_id
topic_id

acertos
erros
fonte

data

---

## StudySession

id
user_id
topic_id

tipo

study_theory
review
practice

data_agendada
status

---

# Scheduler simplificado

Prioridade:

priority_score =
peso_edital × 2
+
(1 - accuracy_rate) × 3
+
days_since_last_review

---

# Spaced repetition (beta)

Intervalos:

0
1
3
7
14
30
60

Regra:

se acerto >= 80% → próximo intervalo

se acerto < 50% → voltar intervalo

---

# IA

IA só deve gerar:

- explicação curta
- exemplo
- flashcards

Evitar textos longos.

---

# TASK LIST

## Infraestrutura

### TASK 1
✅ DONE

Criar estrutura de diretórios do projeto conforme arquitetura.

---

### TASK 2
✅ DONE

Criar core/database.py

Requisitos:

- suporte SQLite
- suporte PostgreSQL
- detectar DATABASE_URL

Fix Railway:

DATABASE_URL = DATABASE_URL.replace("postgres://","postgresql://")

Criar SessionLocal e Base.

---

### TASK 3
✅ DONE

Criar core/security.py

Implementar autenticação JWT.

Funções:

create_access_token
verify_password
hash_password

Endpoints:

POST /auth/register
POST /auth/login
GET /auth/me

---

## Models

### TASK 4
✅ DONE

Criar model User usando SQLAlchemy.

---

### TASK 5
✅ DONE

Criar model Exam.

---

### TASK 6
✅ DONE

Criar model Subject.

Relacionamento:

Exam → Subjects

---

### TASK 7
✅ DONE

Criar model Topic.

Relacionamento:

Subject → Topics

---

### TASK 8
✅ DONE

Criar model TopicProgress.

Relacionamento:

User + Topic

---

### TASK 9
✅ DONE

Criar model QuestionAttempt.

---

### TASK 10
✅ DONE

Criar model StudySession.

---

## Onboarding

### TASK 11
✅ DONE

Criar módulo onboarding.

Endpoint:

POST /onboarding

Campos:

exam
horas_dia
dias_semana

Salvar dados iniciais do aluno.

---

## Baterias de questões

### TASK 12
✅ DONE

Criar módulo baterias.

Endpoint:

POST /baterias

Campos:

topic_id
acertos
erros
fonte

Salvar em QuestionAttempt.

Atualizar TopicProgress.

---

### TASK 13
✅ DONE

Endpoint:

GET /baterias

Retornar histórico do usuário.

---

## Desempenho

### TASK 14
✅ DONE

Criar endpoint:

GET /desempenho/resumo

Retornar:

accuracy_rate por matéria
accuracy_rate por tópico
total questões

---

## Cronograma

### TASK 15
✅ DONE

Criar serviço de cálculo de prioridade.

Usar fórmula definida.

---

### TASK 16
✅ DONE

Criar endpoint:

GET /cronograma/semana

Gerar sessões:

study_theory
review
practice

Máximo:

2 sessões mesma matéria por dia.

---

## IA

### TASK 17
✅ DONE

Criar core/ai_provider.py

Classes:

AIProvider
GeminiProvider

---

### TASK 18
✅ DONE

Endpoint:

POST /conteudo/resumo

Gerar explicação curta usando IA.

---

### TASK 19
✅ DONE

Endpoint:

POST /conteudo/flashcards

Gerar 3–5 flashcards.

---

### TASK 20
✅ DONE

Endpoint:

POST /conteudo/exemplo

Gerar exemplo prático.

---

## Dashboard

### TASK 21
✅ DONE (parcial — via /agenda + /desempenho)

GET /agenda já retorna sessões priorizadas do dia.
GET /desempenho já retorna taxa de acerto por matéria.
Dashboard (pg_plano.py) consome ambos e exibe KPIs + tabela.
Endpoint dedicado /dashboard não é necessário por ora.

---

# Deploy

### TASK 22
⬜ PENDING

Preparar deploy Railway.

Variáveis:

DATABASE_URL
SECRET_KEY
GEMINI_API_KEY

---

# Regras importantes

Não implementar ainda:

- FSRS avançado
- diagnóstico cognitivo
- previsão de desempenho
- análise coletiva

Essas features serão adicionadas após o beta.

---

# Fim do documento

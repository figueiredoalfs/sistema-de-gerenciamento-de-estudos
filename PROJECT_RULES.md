# Project Rules — ConcursoAI

Estas regras devem ser seguidas por qualquer agente de IA que trabalhe neste repositório.

O objetivo é evitar complexidade desnecessária e manter consistência na arquitetura.

---

# Regras Gerais

1) Sempre seguir a arquitetura definida em IMPLEMENTATION_GUIDE.md.

2) Nunca implementar funcionalidades que não estejam explicitamente definidas em uma task.

3) Não refatorar código existente sem necessidade.

4) Não adicionar bibliotecas externas sem justificativa.

5) Manter código simples e legível.

6) Priorizar soluções simples em vez de soluções complexas.

---

# Arquitetura

O projeto segue arquitetura modular.

Estrutura obrigatória:

app/

core/
models/
modules/

Cada módulo deve conter:

router.py
service.py

---

# Models

Todos os models devem usar:

SQLAlchemy declarative base.

Evitar lógica complexa dentro dos models.

Lógica deve ficar em services.

---

# Routers

Routers devem apenas:

- receber request
- validar dados
- chamar service

Nunca implementar lógica complexa em routers.

---

# Services

Toda lógica de negócio deve ficar em services.

Services devem ser reutilizáveis.

---

# IA

A IA deve ser usada apenas para:

- gerar explicações
- gerar exemplos
- gerar flashcards

A IA não deve controlar a lógica do sistema.

---

# Scheduler

O scheduler deve seguir a fórmula definida no guia.

Não implementar algoritmos complexos no beta.

---

# Banco de dados

Durante desenvolvimento usar SQLite.

Em produção usar PostgreSQL.

Sempre usar SQLAlchemy.

---

# Código

Preferências:

- funções curtas
- tipagem clara
- evitar duplicação
- comentários apenas quando necessário

---

# Limitações do Beta

NÃO implementar ainda:

- FSRS avançado
- previsão de desempenho
- análise cognitiva complexa
- sistema coletivo de aprendizado

Essas funcionalidades serão adicionadas após o beta.

---

# Objetivo do projeto

Criar um beta funcional com:

- cronograma
- análise de desempenho
- baterias de questões
- geração de conteúdo com IA

O sistema deve ser simples, estável e fácil de evoluir.

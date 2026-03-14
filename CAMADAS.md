# ConcursoAI — Camadas do Sistema

Toda solicitação deve ser classificada em 1 ou mais camadas antes de implementar.
Alterar SOMENTE os arquivos da camada identificada.

---

## Camada BD — Banco de Dados
**Arquivos:** `database.py`, `app/core/database.py`, `app/models/*.py`, `alembic/`

Exemplos: "adicionar campo X à tabela Y", "criar nova tabela", "mudar tipo de coluna"

---

## Camada API — Backend / Regras de Negócio
**Arquivos:** `app/routers/*.py`, `app/services/*.py`, `app/schemas/*.py`, `app/scripts/*.py`, `app/core/security.py`, `app/core/config.py`, `app/modules/`

Exemplos: "criar endpoint", "mudar lógica de priorização", "corrigir cálculo de score"

---

## Camada UI — Telas / Frontend
**Arquivos:** `telas/*.py`, `telas/components.py`, `app.py`

Exemplos: "mudar layout da tela X", "adicionar botão", "ajustar cor/estilo"

---

## Camada CONFIG — Configuração e Documentação
**Arquivos:** `.env`, `config_*.py`, `SESSAO.md`, `IMPLEMENTATION_GUIDE.md`, `CAMADAS.md`, `*.md`

Exemplos: "adicionar matéria ao catálogo", "mudar peso de fonte", "atualizar documentação"

---

## Camada INT — Integração Streamlit ↔ FastAPI
**Arquivos:** `api_client.py`

Exemplos: "adicionar chamada de novo endpoint", "mudar timeout", "corrigir payload enviado"

---

## Regra de Classificação

Ao receber uma solicitação:
1. Identificar a camada → **BD / API / UI / CONFIG / INT**
2. Listar os arquivos que serão alterados
3. Se tocar **mais de 2 camadas** simultaneamente → avisar o usuário e pedir confirmação

---

## Tabela Rápida de Referência

| Camada  | Arquivos principais                                         |
|---------|-------------------------------------------------------------|
| BD      | `database.py`, `app/models/`, `alembic/`                    |
| API     | `app/routers/`, `app/services/`, `app/schemas/`             |
| UI      | `telas/`, `app.py`                                          |
| CONFIG  | `config_*.py`, `.env`, `*.md`                               |
| INT     | `api_client.py`                                             |

# AprovAI — Sistema de Acompanhamento de Desempenho

Aplicacao web local para registro e analise de baterias de questoes de concursos.
Construida com Streamlit + SQLite. Roda 100% offline, sem necessidade de internet.

## Funcionalidades

- **Dashboard** — KPIs gerais e ranking de erros por materia
- **Lancar Bateria** — registro de questoes por materia e assunto (salvo de forma atomica ao finalizar)
- **Registrar Erros** — anotacao de topicos com erros apos finalizar uma bateria
- **Historico** — listagem paginada de baterias com filtro por mes/ano
- **Erros Criticos** — tabela de erros ordenada por quantidade (ranking)
- **Evolucao Mensal** — grafico interativo de % de acertos por materia ao longo dos meses
- **Cadastro** — gerenciamento de materias e assuntos usados nos dropdowns

## Instalacao

```bash
pip install -r requirements.txt
```

## Migracao de dados (opcional)

Se voce possui dados no arquivo `controle_desempenho.xlsx`, execute uma unica vez:

```bash
python migrar_dados.py
```

O banco `sisfig.db` e criado automaticamente na primeira execucao do app, mesmo sem migracao.

## Como rodar

```bash
streamlit run app.py
```

O app abrira no navegador em `http://localhost:8501`.

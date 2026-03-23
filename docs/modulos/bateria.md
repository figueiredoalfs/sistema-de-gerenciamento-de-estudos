# Módulo: Bateria

## Propósito
Permite ao aluno montar e registrar baterias de questões multi-disciplinares a partir do banco de questões (`QuestaoBanco`), com filtros por banca, disciplina e tópico. Diferente das tasks (currículo guiado), a bateria é livre e iniciada pelo aluno.

## Arquivos principais
- `app/routers/bateria.py` — endpoints de bateria
- `app/models/questao_banco.py` — model `QuestaoBanco` (banco externo)
- `app/models/bateria.py` (se existir) — model de registro de bateria
- `frontend/src/pages/LancarBateria.jsx` — interface de montagem
- `frontend/src/api/bateria.js` — chamadas de API

## Endpoints
```
GET  /topicos/hierarquia     → árvore: matéria → bloco → subtópico
GET  /bancas                 → lista de bancas disponíveis
POST /bateria                → registra bateria realizada
GET  /baterias               → histórico paginado de baterias do aluno
```

## Fluxo de dados
```
Frontend:
  1. GET /topicos/hierarquia → monta filtros de disciplina/tópico
  2. GET /bancas → monta filtro de banca
  3. Aluno seleciona questões e responde
  4. POST /bateria {questoes: [{questao_banco_id, correta, tempo_s}], filtros}
     → persiste resultado
     → retorna {acertos, total, taxa}
```

## Model QuestaoBanco
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `question_code` | String(50) | Código único da questão |
| `statement` | Text | Enunciado |
| `alternatives_json` | Text | JSON {"A":…,"B":…,"C":…,"D":…,"E":…} |
| `correct_answer` | String(1) | Letra correta |
| `banca` | String | Nome da banca |
| `year` | Integer | Ano |
| `subject` | String | Disciplina |
| `materia` | String | Matéria (mais granular) |
| `materia_pendente` | Boolean | Aguardando classificação |

## Dependências externas
- `Topico` — hierarquia de filtros
- `Aluno` — dono da bateria
- `admin_importar_questoes.py` — popula `QuestaoBanco` via importação admin

## Regras de negócio críticas
- `question_code` é chave única — upsert na importação (ON CONFLICT DO UPDATE)
- Questões com `materia_pendente=True` aguardam revisão admin antes de aparecer em filtros
- Bateria é **independente** do sistema de metas/tasks — não afeta proficiência FSRS

## Pontos de atenção
- `alternatives_json` é string JSON — sempre parse antes de usar
- Busca por disciplina usa `.ilike()` — case-insensitive, funciona em SQLite e PostgreSQL
- A hierarquia `/topicos/hierarquia` é compartilhada com outros módulos — não alterar estrutura de retorno

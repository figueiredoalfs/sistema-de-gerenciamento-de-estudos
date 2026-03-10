# Decisões tomadas — não questionar

## Técnicas
- Docker incompatível com o Windows do usuário → SQLite local (dev)
- Flashcard por texto digitado, não áudio (self-explanation preservado)
- Celery em modo eager local: CELERY_TASK_ALWAYS_EAGER=True no .env
- Fix Railway obrigatório: DATABASE_URL.replace('postgres://', 'postgresql://')

## Produto
- Déficit de meta invisível para o aluno — só admin/mentor vê
- Calibração não se repete: uma_vez=True na Sessao
- Sem ranking entre usuários reais
- Interleaving: máximo 2 sessões da mesma matéria por dia
- Metas nunca crescem por atraso
- Deploy: Railway (gratuito no beta)
- IA própria: inviável agora — reavaliar após 6-18 meses com dados suficientes

## Pesos por fonte (não alterar sem dados do D-IC)
mesma_banca=1.5 | outra_banca=1.2 | calibracao=1.2
plataforma=1.0  | quiz_ia=0.8     | curso=0.6

## Admin
- W1+W2+W3+W4 deve sempre = 1.0 (validar no endpoint)
- Troca de IA via painel sem redeploy
- Déficit privado: GET /admin/meta/{id}/historico

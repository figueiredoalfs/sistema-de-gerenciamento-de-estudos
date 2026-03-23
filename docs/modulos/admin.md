# Módulo: Admin

## Propósito
Painel administrativo com acesso restrito a `role = administrador`. Cobre gestão de usuários, tópicos, questões, planos base, pendências de classificação, ciclos de estudo, notificações, configurações do sistema e importação em lote.

## Arquivos principais
- `app/routers/admin_config.py` — configurações e modelos de IA
- `app/routers/admin_topicos.py` — CRUD de tópicos/matérias
- `app/routers/admin_questoes.py` (se existir) — gestão de questões
- `app/routers/admin_importar_questoes.py` — importação em lote (JSON/CSV)
- `app/routers/admin_importar_tec.py` — importação via TEC Concursos
- `app/routers/admin_bancas.py` — gestão de bancas
- `app/routers/admin_pendencias.py` — questões com materia_pendente
- `app/routers/admin_plano_base.py` — CRUD de planos base
- `app/routers/admin_ciclos.py` — gestão de ciclos de matérias
- `app/routers/admin_notificacoes.py` — notificações para alunos
- `app/routers/admin_stats.py` — estatísticas gerais
- `frontend/src/pages/Admin*.jsx` — páginas do painel
- `frontend/src/api/admin*.js` — chamadas de API admin

## Endpoints por sub-módulo
```
GET/PUT /admin/config            → configurações do sistema (chave/valor)
GET     /admin/config/modelos-ia → modelos de IA disponíveis
GET/POST/PUT/DELETE /admin/topicos    → CRUD de matérias/tópicos
POST    /admin/importar/questoes      → importação em lote
POST    /admin/importar/tec           → importação TEC Concursos
GET/PUT /admin/pendencias             → questões sem classificação
GET/POST/PUT/DELETE /admin/planos-base → templates de estudo
GET/POST/PUT/DELETE /admin/ciclos     → ciclos de matérias
GET/POST /admin/notificacoes          → mensagens para alunos
GET     /admin/stats                  → métricas globais do sistema
GET/PUT/DELETE /admin/usuarios        → gestão de alunos (ativar/desativar/role)
```

## Guard de acesso
```python
# Todos os endpoints admin usam:
current_user: Aluno = Depends(require_admin)
# Retorna 403 para qualquer role != 'administrador'
```

## Dependências externas
- `Topico`, `QuestaoBanco`, `Questao`, `PlanoBase`, `CicloMateria` — models gerenciados
- `AIProvider` — modelos de IA configuráveis via `admin/config`
- `Aluno` — gestão de usuários

## Regras de negócio críticas
- **Importação em lote**: timeout 600s no cliente (`admin_importar_questoes.py`) — não reduzir
- Importação usa UPSERT (`question_code` como chave) — idempotente, pode re-importar
- Questões importadas com `materia_pendente=True` ficam invisíveis para alunos até classificação
- Plano base define estrutura de geração de metas — alterar com cuidado (afeta todos os alunos da área)
- Admin pode mudar role de usuário, mas o aluno precisa de novo login para o JWT refletir o novo role

## Pontos de atenção
- `admin/config` armazena configurações como chave/valor em banco — inclui modelo de IA ativo
- Alteração do modelo de IA em `admin/config` tem efeito imediato (lido dinamicamente por `ai_provider.py`)
- Importação TEC: scraping externo — pode quebrar se o site mudar layout

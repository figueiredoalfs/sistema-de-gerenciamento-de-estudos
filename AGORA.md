# AGORA.md — Correções imediatas + próximos passos

> Leia este arquivo junto com o SESSAO.md.
> SESSAO.md = rotina de sessão.
> AGORA.md = o que fazer agora e por quê.
> Quando todas as tarefas aqui estiverem concluídas, arquive este arquivo.

---

## Estado atual do sistema (diagnóstico confirmado)

### O que está vivo e funcionando
- React (Login, Onboarding, Dashboard) — código limpo
- FastAPI: 4 routers usados pelo React: `auth`, `onboarding`, `study_tasks`, `metas`
- Model `StudyTask` com status ENUM correto: `pending`, `in_progress`, `completed`
- 221 tasks no banco: 204 `study` + 17 `diagnostico`

### O que está morto (não deletar ainda — fazer depois das correções)
```
app.py, api_client.py, database.py, style.py
config_app.py, config_fontes.py, config_materias.py
migrar_dados.py, telas/
app/routers/: bateria, erro_critico, desempenho, agenda, usuarios,
              admin_topicos, admin_ciclos, admin_stats, conhecimento,
              questoes, respostas, explicacoes, admin_importar_questoes,
              task_conteudo, cronograma_semanal
```

### Causa raiz dos problemas de front
O ENUM de `tipo` tem 9 valores de duas eras diferentes:
- Era antiga (dados reais no banco): `study`, `diagnostico`
- Era nova (só no código, nunca gerados): `teoria`, `revisao`, `questionario`, `simulado`, `reforco`

O frontend espera os tipos novos para renderizar comportamentos diferentes.
O banco só tem tipos antigos. Os dois mundos nunca se encontraram.

---

## Correções de segurança — fazer ANTES de tudo

### SEGURANÇA 1 — Verificar se .env foi commitado
```bash
git log --all --full-history -- .env
```
Se retornar qualquer commit: revogar a chave Gemini imediatamente em
https://console.cloud.google.com → APIs & Services → Credentials
Depois limpar o histórico:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```
Confirmar que `.env` está no `.gitignore`:
```bash
grep ".env" .gitignore
```

### SEGURANÇA 2 — SECRET_KEY não pode ser hardcoded
```bash
grep -n "SECRET_KEY" app/core/config.py
```
Se retornar uma string fixa em vez de `os.getenv("SECRET_KEY")`:
qualquer pessoa com acesso ao código pode forjar tokens JWT.
Corrigir para ler obrigatoriamente do ambiente:
```python
SECRET_KEY = os.environ["SECRET_KEY"]  # levanta erro se não definido
```

### SEGURANÇA 3 — Restringir CORS antes do deploy
Em `app/main.py`, o `allow_origins=["*"]` está ok em dev local.
Antes do deploy no Railway, restringir para:
```python
allow_origins=[
    "http://localhost:5173",       # dev local Vite
    "https://seu-dominio.railway.app",  # produção
],
```
Não fazer agora — fazer junto com o deploy.

---

## Correções — execute nesta ordem exata

### CORREÇÃO 1 — Migrar dados: `study` → `teoria`
**Por que:** 204 tasks com tipo `study` são o equivalente direto de `teoria` no novo sistema.
Fazer isso antes de mexer no ENUM evita erro de constraint no banco.

```python
# Rodar uma vez — pode ser no shell do Python
from app.core.database import SessionLocal
db = SessionLocal()
db.execute("UPDATE study_tasks SET tipo = 'teoria' WHERE tipo = 'study'")
db.commit()
db.close()
print("Migração concluída")
```

Verificar:
```python
from app.core.database import SessionLocal
from app.models.study_task import StudyTask
from sqlalchemy import func
db = SessionLocal()
rows = db.query(StudyTask.tipo, func.count()).group_by(StudyTask.tipo).all()
for tipo, qtd in rows: print(f'{tipo}: {qtd}')
db.close()
# Esperado: teoria: 204 | diagnostico: 17
```

---

### CORREÇÃO 2 — Limpar o ENUM no model
**Por que:** ENUM com 9 valores de duas eras causa confusão e bugs silenciosos.
Manter só os 6 válidos.

Em `app/models/study_task.py`, substituir o campo `tipo` por:

```python
tipo = Column(
    Enum(
        "diagnostico",
        "teoria",
        "revisao",
        "questionario",
        "simulado",
        "reforco",
        name="study_task_tipo_enum",
    ),
    nullable=False,
)
```

---

### CORREÇÃO 3 — Migration Alembic
**Por que:** o banco precisa refletir o ENUM limpo.

```bash
alembic revision --autogenerate -m "limpar_enum_tipo_task"
alembic upgrade head
```

Se o Alembic não detectar a mudança do ENUM automaticamente
(SQLite não suporta ALTER TYPE), adicionar manualmente na migration:

```python
# Em migrations/versions/xxxx_limpar_enum_tipo_task.py
def upgrade():
    # SQLite: recriar a tabela com o ENUM correto
    # PostgreSQL: usar op.execute("ALTER TYPE ... RENAME VALUE ...")
    pass  # Claude Code vai gerar o conteúdo correto para seu banco
```

---

### CORREÇÃO 4 — Confirmar schema de GET /tasks/today
**Por que:** o frontend faz `data.tasks ?? data` — fallback defensivo que indica
incerteza sobre o formato. Precisa confirmar e padronizar.

Subir o servidor e testar:
```bash
# Terminal 1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — pegar token
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teste@aprovai.com&password=senha123"

# Terminal 2 — testar endpoint (substituir TOKEN)
curl -s http://localhost:8000/tasks/today \
  -H "Authorization: Bearer TOKEN" | python3 -m json.tool
```

**Formato esperado pelo frontend (tasks.js):**
```json
{
  "daily_limit": 3,
  "tasks": [
    {
      "id": "...",
      "tipo": "teoria",
      "status": "pending",
      "subject_nome": "Direito Administrativo",
      "subtopic_nome": "Atos Administrativos",
      "numero_cronograma": 1,
      "task_code": "DA-ATOS-001"
    }
  ]
}
```

Se o formato real for diferente, ajustar o router `study_tasks.py`
para retornar exatamente esse schema — não mexer no frontend.

---

### CORREÇÃO 5 — Remover dailyLimit duplicado do frontend
**Por que:** backend já limita por `horas_por_dia`. Frontend faz `tasks.slice(0, dailyLimit)`
em cima — duplicação que causa bugs silenciosos se os dois calcularem diferente.

Em `frontend/src/hooks/useTasks.js`:
- Remover o cálculo de `dailyLimit` no cliente
- Remover o `tasks.slice(0, dailyLimit)`
- Confiar no array que o backend retorna

---

### CORREÇÃO 6 — Refetch após concluir task de diagnóstico
**Por que:** quando aluno conclui task `diagnostico`, o backend gera novas tasks
automaticamente. Mas o frontend não faz refetch — as tasks novas ficam no banco
sem aparecer no dashboard até o aluno recarregar.

Em `frontend/src/hooks/useTasks.js`, na função `concluirTask`:
```javascript
// Depois do PATCH, sempre fazer refetch
await updateTaskStatus(taskId, 'completed')
await refetch() // garantir que tasks novas aparecem imediatamente
```

---

## Próximos passos — após as 6 correções acima

### PRÓXIMO 1 — Expansão do TaskCard por tipo
Esta é a feature central do produto. Após as correções, o card precisa expandir
e mostrar ações diferentes por tipo:

```
teoria / revisao:
  [ Vídeo Aula ]  [ Gerar PDF ]  [ Concluir → abre questionário de 5 questões ]

questionario / simulado:
  [ Iniciar Questões ]  → conclui automaticamente ao terminar

reforco:
  igual a teoria, mas questionário com 10-15 questões
```

**Campos que o backend já tem e o frontend ainda não usa:**
- `task_code` — código único compartilhado entre alunos (cache de IA)
- `questoes_json` — questões já geradas
- `numero_cronograma` — posição na sequência semanal

---

### PRÓXIMO 2 — Limpar código morto
Só fazer depois que o fluxo básico estiver funcionando.
Deletar os arquivos listados em "O que está morto" acima.
Remover os 15 routers inativos do `main.py`.

---

### PRÓXIMO 3 — Features de conteúdo (vídeos + PDF)
Após o card expansível funcionar:
- Vídeos: busca YouTube via IA, salva no banco, reutiliza para outros alunos
- PDF: geração via IA com cache por `task_code`
- Questionário de validação: 5 questões obrigatórias para finalizar teoria/revisao

---

## Referência rápida — contratos confirmados

| Endpoint | Método | Usado por | Status |
|---|---|---|---|
| /auth/login | POST | Login.jsx | ✅ funcionando |
| /auth/me | GET | AuthContext.jsx | ✅ mas confirmar campo `area` |
| /onboarding | POST | Onboarding.jsx | ✅ mas confirmar salva `area` |
| /tasks/today | GET | useTasks.js | ⚠️ formato não confirmado |
| /tasks/{id}/status | PATCH | useTasks.js | ✅ ENUM correto |
| /metas | GET | metas.js | ⚠️ confirmar status `aberta` |
| /metas/gerar | POST | useTasks.js | ✅ |

**Atenção:** após o onboarding, `GET /auth/me` precisa retornar o campo `area`.
O guard `OnboardingGuard` em `App.jsx` verifica `user.area` para decidir se
redireciona para `/onboarding` ou deixa entrar no dashboard.
Se `area` não vier no response, loop infinito de onboarding.


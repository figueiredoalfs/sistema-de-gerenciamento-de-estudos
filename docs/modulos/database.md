# Módulo: Database

## Propósito
Configura a conexão com o banco de dados (SQLite em dev, PostgreSQL em prod), gerencia o ciclo de vida das sessões e executa migrações via Alembic na startup.

## Arquivos principais
- `app/core/config.py` — `Settings` (lê env vars), `database_url_compat`
- `app/core/database.py` — engine, `SessionLocal`, `get_db`
- `alembic/env.py` — integração Alembic com SQLAlchemy
- `alembic/versions/` — arquivos de migração
- `alembic.ini` — configuração base do Alembic
- `app/main.py` (lifespan) — executa `alembic upgrade head` na startup

## Fluxo de dados

### Startup
```
lifespan():
  subprocess: alembic upgrade head   ← aplica migrações pendentes
  seed_topicos()
  seed_ciclos()
  seed_areas()
  seed_admin()
  reclassificar()                    ← envolvido em try/except
```

### Sessão por request
```
get_db() → SessionLocal() → yield db → db.close()
# Usado via Depends(get_db) em todos os routers
```

### Configuração condicional por dialeto
```python
# config.py — database_url_compat:
"postgres://"   → "postgresql://"           # Railway legacy
"postgresql://" sem sslmode + sem .railway.internal → + "?sslmode=require"

# database.py — connect_args:
SQLite     → {"check_same_thread": False}
PostgreSQL externo → {"sslmode": "require"}
PostgreSQL interno (.railway.internal) → {}
```

### Alembic batch mode
```python
# alembic/env.py:
render_as_batch=(connection.dialect.name == "sqlite")
# SQLite não suporta ALTER TABLE → batch mode
# PostgreSQL → batch mode desligado (ALTER TABLE nativo)
```

## Dependências externas
- `sqlalchemy==2.0.35`
- `alembic==1.13.3`
- `psycopg2-binary==2.9.9` (prod)
- Env vars: `DATABASE_URL`, `SECRET_KEY`

## Regras de negócio críticas
- **Nunca usar `Base.metadata.create_all()`** — tudo passa por Alembic
- Toda nova model deve ser importada em `alembic/env.py` (ou em `app/models/__init__.py` importado lá) para ser detectada
- Novas migrações: `alembic revision --autogenerate -m "descrição"`
- **PostgreSQL de produção**: `DATABASE_URL = ${{Postgres.DATABASE_URL}}` no Railway

## Pontos de atenção
- `sqlite:///./dev.db` como `DATABASE_URL` em produção = banco efêmero que zera a cada redeploy
- Campos `Boolean` no PostgreSQL são tipo nativo BOOLEAN — `func.sum()` exige `cast(campo, Integer)` para agregar (ver `desempenho.md`)
- JSON é armazenado como `Text` em todos os models — parse manual em runtime (`json.loads/dumps`)
- Enums PostgreSQL são criados como tipos no banco — renomear valores de Enum exige migration explícita

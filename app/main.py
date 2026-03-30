from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base  # noqa: F401 — importado para Alembic detectar os models
from app.routers import auth, onboarding, bateria, desempenho, usuarios, admin_topicos, admin_ciclos, admin_stats, questoes, admin_importar_questoes, admin_importar_tec, admin_pendencias, admin_bancas, admin_notificacoes, admin_config, admin_convites, dev, sessoes_estudo  # noqa: E501

# Importar todos os models para o Alembic detectar
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Aplica todas as migrations pendentes (alembic upgrade head)
    import os
    from alembic.config import Config as AlembicConfig
    from alembic import command as alembic_command
    _ini_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "alembic.ini")
    alembic_cfg = AlembicConfig(_ini_path)
    alembic_command.upgrade(alembic_cfg, "head")

    # Seed canônico da hierarquia fiscal (normaliza nomes, remove duplicatas)
    from app.scripts.seed_fiscal import seed as seed_fiscal
    seed_fiscal()

    # Seed de ciclos de matérias por área (depende dos tópicos já existirem)
    from app.scripts.seed_ciclos import seed_ciclos
    seed_ciclos()

    # Seed de áreas padrão (fiscal, militar, etc.)
    from app.scripts.seed_areas import seed_areas
    seed_areas()

    # Garante que existe pelo menos 1 usuário admin no banco FastAPI
    from app.scripts.seed_admin import seed_admin
    seed_admin()

    # Seed de bancas examinadoras padrão (idempotente)
    from app.scripts.seed_bancas import seed_bancas
    seed_bancas()

    # Reclassifica questões com matéria/banca não reconhecida
    try:
        from app.scripts.reclassificar_pendencias import reclassificar
        from app.core.database import SessionLocal
        _db = SessionLocal()
        try:
            reclassificar(_db)
        finally:
            _db.close()
    except Exception:
        pass  # não bloqueia o startup

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Skolai API",
    description="Plataforma de gestão de estudos para concursos públicos com IA",
    version="1.0.0-beta",
)

_allowed_origins = (
    [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
    if settings.ALLOWED_ORIGINS != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Filtered", "X-Total-Bank"],
)

# Routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(bateria.router)
app.include_router(desempenho.router)
app.include_router(usuarios.router)
app.include_router(admin_topicos.router)
app.include_router(admin_ciclos.router)
app.include_router(admin_stats.router)
app.include_router(questoes.router)
app.include_router(admin_importar_questoes.router)
app.include_router(admin_importar_tec.router)
app.include_router(admin_pendencias.router)
app.include_router(admin_bancas.router)
app.include_router(admin_notificacoes.router)
app.include_router(admin_config.router)
app.include_router(admin_convites.router)
app.include_router(sessoes_estudo.router)
app.include_router(dev.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "Skolai"}

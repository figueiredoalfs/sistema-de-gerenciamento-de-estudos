from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base  # noqa: F401 — importado para Alembic detectar os models
from app.routers import auth, onboarding, bateria, erro_critico, desempenho, agenda, usuarios, admin_topicos, admin_ciclos, admin_stats, conhecimento, questoes, respostas, study_tasks, explicacoes, admin_importar_questoes, task_conteudo, admin_plano_base, admin_importar_tec, admin_pendencias, admin_bancas, admin_notificacoes, admin_config, plano_base_aluno, dev  # noqa: E501
from app.routers import cronograma_semanal
from app.routers import metas
from app.modules.conteudo.router import router as conteudo_router

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

    # Seed de tópicos padrão (idempotente — pula se já existirem)
    from app.scripts.seed_topicos import seed
    seed()

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
app.include_router(erro_critico.router)
app.include_router(desempenho.router)
app.include_router(agenda.router)
app.include_router(conteudo_router)
app.include_router(usuarios.router)
app.include_router(admin_topicos.router)
app.include_router(admin_ciclos.router)
app.include_router(admin_stats.router)
app.include_router(conhecimento.router)
app.include_router(questoes.router)
app.include_router(respostas.router)
app.include_router(study_tasks.router)
app.include_router(explicacoes.router)
app.include_router(admin_importar_questoes.router)
app.include_router(task_conteudo.router)
app.include_router(cronograma_semanal.router)
app.include_router(metas.router)
app.include_router(admin_plano_base.router)
app.include_router(admin_importar_tec.router)
app.include_router(admin_pendencias.router)
app.include_router(admin_bancas.router)
app.include_router(admin_notificacoes.router)
app.include_router(admin_config.router)
app.include_router(plano_base_aluno.router)
app.include_router(dev.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "Skolai"}

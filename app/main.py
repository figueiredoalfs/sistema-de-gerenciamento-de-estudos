from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, onboarding, bateria, erro_critico, desempenho, agenda, usuarios, admin_topicos, admin_ciclos, admin_stats, conhecimento, questoes, respostas, study_tasks, explicacoes
from app.modules.conteudo.router import router as conteudo_router

# Importar todos os models para o Alembic detectar
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante que todas as tabelas existem (fallback quando Alembic não foi rodado)
    Base.metadata.create_all(bind=engine)

    # Seed de tópicos padrão (idempotente — pula se já existirem)
    from app.scripts.seed_topicos import seed
    seed()

    # Seed de ciclos de matérias por área (depende dos tópicos já existirem)
    from app.scripts.seed_ciclos import seed_ciclos
    seed_ciclos()

    # Garante que existe pelo menos 1 usuário admin no banco FastAPI
    from app.scripts.seed_admin import seed_admin
    seed_admin()

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Skolai API",
    description="Plataforma de gestão de estudos para concursos públicos com IA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "Skolai"}

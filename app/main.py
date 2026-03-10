from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, onboarding, bateria, erro_critico, desempenho, agenda

# Importar todos os models para o Alembic detectar
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed de tópicos padrão (idempotente — pula se já existirem)
    from app.scripts.seed_topicos import seed
    seed()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="ConcursoAI API",
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


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "ConcursoAI"}

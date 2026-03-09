from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, onboarding, bateria, erro_critico, desempenho

# Importar todos os models para o Alembic detectar
import app.models  # noqa: F401

app = FastAPI(
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


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "ConcursoAI"}

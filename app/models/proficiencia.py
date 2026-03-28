import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

# Pesos por fonte (CONTEXTO.md)
PESO_POR_FONTE = {
    "prova_anterior_mesma_banca": 1.5,
    "prova_anterior_outra_banca": 1.2,
    "calibracao": 1.2,
    "qconcursos": 1.0,
    "tec": 1.0,
    "simulado": 1.0,
    "quiz_ia": 0.8,
    "manual": 0.8,
    "curso": 0.6,
}


class Proficiencia(Base):
    __tablename__ = "proficiencias"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topico_id = Column(String(36), ForeignKey("topicos.id"), nullable=True, index=True)

    # Identificação da bateria original (para rastreabilidade do SISFIG)
    id_bateria = Column(String(100))
    materia = Column(String(200))
    subtopico = Column(String(300))

    acertos = Column(Integer, default=0)
    total = Column(Integer, default=0)
    percentual = Column(Float, default=0.0)  # 0–100

    fonte = Column(
        Enum(
            "qconcursos",
            "tec",
            "prova_anterior_mesma_banca",
            "prova_anterior_outra_banca",
            "simulado",
            "quiz_ia",
            "manual",
            "calibracao",
            "curso",
            name="fonte_enum",
        ),
        nullable=False,
        default="manual",
    )
    peso_fonte = Column(Float, default=1.0)
    banca = Column(String(100), nullable=True)
    duracao_min = Column(Integer, nullable=True)

    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="proficiencias")
    topico = relationship("Topico", back_populates="proficiencias")

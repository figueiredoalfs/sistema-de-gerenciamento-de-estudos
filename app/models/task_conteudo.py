import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base

TIPO_PREFIXES: dict[str, str] = {
    "teoria":       "TEO",
    "revisao":      "REV",
    "questionario": "QUE",
    "simulado":     "SIM",
    "reforco":      "REF",
    "study":        "STU",
    "questions":    "QST",
    "review":       "RVW",
    "diagnostico":  "DIA",
}


def gerar_task_code(tipo: str) -> str:
    prefix = TIPO_PREFIXES.get(tipo, "TSK")
    return f"{prefix}-{secrets.token_hex(3)}"


class TaskConteudo(Base):
    __tablename__ = "task_conteudo"
    __table_args__ = (
        UniqueConstraint("subtopico_id", "tipo", name="uq_task_conteudo_subtopico_tipo"),
    )

    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_code    = Column(String(20), unique=True, nullable=False, index=True)
    subtopico_id = Column(String(36), ForeignKey("topicos.id"), nullable=True, index=True)
    tipo         = Column(String(30), nullable=False)
    objetivo     = Column(Text, nullable=True)
    instrucoes   = Column(Text, nullable=True)
    conteudo_pdf = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subtopico = relationship("Topico", foreign_keys=[subtopico_id])
    videos    = relationship("TaskVideo", back_populates="conteudo", cascade="all, delete-orphan")

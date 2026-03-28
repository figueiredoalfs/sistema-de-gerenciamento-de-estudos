import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class SessaoEstudo(Base):
    __tablename__ = "sessoes_estudo"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    subtopico_id = Column(String(36), ForeignKey("topicos.id"), nullable=True, index=True)

    tipo = Column(String(20), nullable=False, default="teoria")  # "teoria" | "questoes"
    data = Column(Date, nullable=False, default=date.today)
    duracao_min = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", backref="sessoes_estudo")
    subtopico = relationship("Topico", foreign_keys=[subtopico_id])

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Cronograma(Base):
    __tablename__ = "cronogramas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    # Modo pré-prova: cronograma normal
    # Modo revisão final: ativado automaticamente 14 dias antes da prova
    modo = Column(
        Enum("pre_prova", "revisao_final", name="modo_cronograma_enum"),
        nullable=False,
        default="pre_prova",
    )

    modo_revisao_final = Column(Boolean, default=False)
    data_ativacao_revisao = Column(DateTime, nullable=True)

    edital_json = Column(Text)     # JSON com tópicos e pesos extraídos do edital
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="cronogramas")
    sessoes = relationship("Sessao", back_populates="cronograma")

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class PadraoCognitivo(Base):
    """
    Detectado após >= 50 questões erradas.
    tipo: excecao / dupla_negativa / aplicacao / conceito / comparacao
    """

    __tablename__ = "padroes_cognitivos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    tipo = Column(
        Enum(
            "excecao",
            "dupla_negativa",
            "aplicacao",
            "conceito",
            "comparacao",
            name="padrao_tipo_enum",
        ),
        nullable=False,
    )

    confianca = Column(Float, default=0.0)          # taxa desse tipo / taxa geral (>1.5 = padrão detectado)
    total_erros_analisados = Column(Integer, default=0)
    descricao = Column(Text)

    ativo = Column(Boolean, default=True)
    detectado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="padroes_cognitivos")

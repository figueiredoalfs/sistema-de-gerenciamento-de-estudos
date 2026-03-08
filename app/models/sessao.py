import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sessao(Base):
    """
    Representa uma sessão de estudo agendada ou concluída.
    Campos FSRS (stability, difficulty) coletados desde F-01 para habilitar
    o algoritmo completo na F-06 (3-4 meses de dados, 10+ alunos).
    """

    __tablename__ = "sessoes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topico_id = Column(String(36), ForeignKey("topicos.id"), nullable=True, index=True)
    cronograma_id = Column(String(36), ForeignKey("cronogramas.id"), nullable=True)

    tipo = Column(
        Enum(
            "teoria_pdf",
            "exercicios",
            "video",
            "flashcard_texto",
            "calibracao",
            name="tipo_sessao_enum",
        ),
        nullable=False,
    )

    duracao_planejada_min = Column(Integer)   # duração planejada
    duracao_real_min = Column(Integer)        # feedback de tempo real (beta)

    confianca = Column(
        Enum("baixa", "media", "alta", name="confianca_enum"),
        nullable=False,
        default="baixa",
    )

    # Campos FSRS — coletados desde o início (F-01), algoritmo ativado na F-06
    stability = Column(Float, nullable=True)
    difficulty = Column(Float, nullable=True)

    # Calibração nunca se repete por matéria
    uma_vez = Column(Boolean, default=False)

    concluida = Column(Boolean, default=False)
    data_agendada = Column(DateTime)
    data_concluida = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="sessoes")
    topico = relationship("Topico", back_populates="sessoes")
    cronograma = relationship("Cronograma", back_populates="sessoes")

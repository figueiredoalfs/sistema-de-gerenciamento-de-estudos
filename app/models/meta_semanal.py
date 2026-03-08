import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class MetaSemanal(Base):
    """
    Janela móvel de 7 dias (sem dia fixo de reset).
    deficit_min é PRIVADO — visível só admin/mentor.
    """

    __tablename__ = "metas_semanais"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    janela_inicio = Column(DateTime, nullable=False)
    janela_fim = Column(DateTime, nullable=False)

    nivel = Column(
        Enum("conservador", "moderado", "agressivo", name="nivel_meta_enum"),
        nullable=False,
        default="moderado",
    )

    carga_meta_min = Column(Integer, default=0)       # minutos planejados
    carga_realizada_min = Column(Integer, default=0)  # minutos concluídos

    # Campo PRIVADO — nunca expor na API pública do aluno
    deficit_min = Column(Integer, default=0)

    encerrada = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="metas_semanais")

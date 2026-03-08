import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ErroCritico(Base):
    __tablename__ = "erros_criticos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topico_id = Column(String(36), ForeignKey("topicos.id"), nullable=True, index=True)

    id_bateria = Column(String(100))
    materia = Column(String(200))
    topico_texto = Column(String(500))  # texto livre do tópico errado
    qtd_erros = Column(Integer, default=1)
    observacao = Column(Text)

    status = Column(
        Enum("pendente", "em_revisao", "resolvido", name="erro_status_enum"),
        nullable=False,
        default="pendente",
    )

    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="erros_criticos")
    topico = relationship("Topico", back_populates="erros_criticos")

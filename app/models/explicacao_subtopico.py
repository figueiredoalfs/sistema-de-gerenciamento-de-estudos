import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint

from app.core.database import Base


class ExplicacaoSubtopico(Base):
    """Explicação de um subtópico gerada pela IA — compartilhada por todos os alunos."""

    __tablename__ = "explicacoes_subtopico"
    __table_args__ = (UniqueConstraint("topico_id", name="uq_explicacao_topico"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topico_id = Column(String(36), ForeignKey("topicos.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class RespostaQuestao(Base):
    __tablename__ = "respostas_questoes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    questao_id = Column(String(36), ForeignKey("questoes.id"), nullable=False, index=True)
    # Denormalizado de questao.subtopic_id para queries de desempenho rápidas
    subtopico_id = Column(String(36), ForeignKey("topicos.id"), nullable=False, index=True)

    resposta_dada = Column(String(1), nullable=False)  # A, B, C, D ou E
    correta = Column(Boolean, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", foreign_keys=[aluno_id])
    questao = relationship("Questao", foreign_keys=[questao_id])
    subtopico = relationship("Topico", foreign_keys=[subtopico_id])

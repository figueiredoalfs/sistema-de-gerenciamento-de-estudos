import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

FONTE_ENUM = Enum(
    "ia",
    "admin",
    "qconcursos",
    "tec",
    "prova_real",
    "simulado",
    name="fonte_questao_enum",
)


class Questao(Base):
    __tablename__ = "questoes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Referências à hierarquia de tópicos
    subject_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    subtopic_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)

    # Conteúdo da questão
    enunciado = Column(Text, nullable=False)
    alternativas_json = Column(Text, nullable=False)  # JSON: {"A": "...", "B": "...", ...}
    resposta_correta = Column(String(1), nullable=False)  # A, B, C, D ou E

    # Metadados de origem
    fonte = Column(FONTE_ENUM, nullable=False, default="admin")
    banca = Column(String(100), nullable=True)
    ano = Column(Integer, nullable=True)

    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos (somente leitura — questões são entidades globais)
    subject = relationship("Topico", foreign_keys=[subject_id])
    topic = relationship("Topico", foreign_keys=[topic_id])
    subtopic = relationship("Topico", foreign_keys=[subtopic_id])

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Topico(Base):
    __tablename__ = "topicos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Hierarquia: nivel 0=matéria / 1=bloco / 2=tópico
    parent_id = Column(String(36), ForeignKey("topicos.id"), nullable=True)
    nivel = Column(Integer, default=2)  # 0, 1, 2

    nome = Column(String(300), nullable=False)
    descricao = Column(Text)
    area = Column(String(100))
    banca = Column(String(100))

    peso_edital = Column(Float, default=1.0)   # peso normalizado do edital
    decay_rate = Column(Float, default=0.05)   # λ por categoria (Legislação=0.03, RL=0.08, demais=0.05)

    # Dependências (IDs de tópicos pré-requisito), armazenados como JSON string
    dependencias_json = Column(Text, default="[]")

    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Auto-relacionamento para hierarquia
    filhos = relationship("Topico", backref="parent", remote_side=None, foreign_keys=[parent_id])

    # Outros relacionamentos
    proficiencias = relationship("Proficiencia", back_populates="topico")
    erros_criticos = relationship("ErroCritico", back_populates="topico")
    sessoes = relationship("Sessao", back_populates="topico")

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class PerfilEstudo(Base):
    __tablename__ = "perfil_estudo"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, unique=True)

    # Passo 1 — área do concurso
    area = Column(String(100), nullable=False, default="fiscal")

    # Passo 2 — fase de estudo
    fase_estudo = Column(
        Enum("pre_edital", "pos_edital", name="fase_estudo_enum"),
        nullable=False,
    )

    # Passo 3 — experiência
    experiencia = Column(
        Enum("iniciante", "tempo_de_estudo", name="experiencia_enum"),
        nullable=False,
    )
    # Preenchido apenas quando experiencia == 'tempo_de_estudo'
    # Valores: "<1m", "1-3m", "3-6m", ">6m"
    tempo_estudo = Column(String(20), nullable=True)

    # Passo 4 — funcionalidades selecionadas (JSON array)
    # Ex: '["geracao_conteudo", "analise_desempenho", "cronograma_estudo", "geracao_questoes"]'
    funcionalidades_json = Column(Text, nullable=False, default="[]")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    aluno = relationship("Aluno", back_populates="perfil_estudo")

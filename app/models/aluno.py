import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)

    role = Column(Enum("admin", "aluno", name="role_enum"), nullable=False, default="aluno")
    nivel_desafio = Column(
        Enum("conservador", "moderado", "agressivo", name="nivel_desafio_enum"),
        nullable=False,
        default="moderado",
    )

    horas_por_dia = Column(Float, default=3.0)
    dias_por_semana = Column(Float, default=5.0)

    area = Column(String(100))           # Fiscal / Jurídica / Policial / TI / Saúde / Outro
    banca = Column(String(100))
    cargo = Column(String(200))
    data_prova = Column(DateTime)

    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    proficiencias = relationship("Proficiencia", back_populates="aluno", cascade="all, delete-orphan")
    erros_criticos = relationship("ErroCritico", back_populates="aluno", cascade="all, delete-orphan")
    sessoes = relationship("Sessao", back_populates="aluno", cascade="all, delete-orphan")
    cronogramas = relationship("Cronograma", back_populates="aluno", cascade="all, delete-orphan")
    metas_semanais = relationship("MetaSemanal", back_populates="aluno", cascade="all, delete-orphan")
    padroes_cognitivos = relationship("PadraoCognitivo", back_populates="aluno", cascade="all, delete-orphan")
    simulados = relationship("Simulado", back_populates="aluno", cascade="all, delete-orphan")

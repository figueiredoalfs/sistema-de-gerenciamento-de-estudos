import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class PlanoBase(Base):
    __tablename__ = "planos_base"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    area = Column(String(100), nullable=False)           # fiscal, juridica, etc.
    perfil = Column(String(50), nullable=False)          # iniciante, intermediario, avancado
    versao = Column(Integer, default=1, nullable=False)

    gerado_por_ia = Column(Boolean, default=False, nullable=False)
    revisado_admin = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # JSON com lista de fases:
    # [{ "numero": 1, "nome": "...", "criterio_avanco": "...", "materias": ["..."] }]
    fases_json = Column(Text, nullable=False, default="[]")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

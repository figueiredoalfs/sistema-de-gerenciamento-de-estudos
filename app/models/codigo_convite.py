import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


class CodigoConvite(Base):
    __tablename__ = "codigos_convite"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(200), nullable=True)
    usos_maximos = Column(Integer, nullable=True)   # null = ilimitado
    usos_atuais = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)    # null = sem expiração

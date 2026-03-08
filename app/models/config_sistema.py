import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text

from app.core.database import Base


class ConfigSistema(Base):
    """
    Configurações globais ajustáveis pelo admin sem redeploy.
    Exemplos de chaves:
      ia_provider     = 'gemini' | 'anthropic'
      w1, w2, w3, w4  = pesos do algoritmo de priorização (soma deve = 1.0)
    """

    __tablename__ = "config_sistema"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=False)
    descricao = Column(Text)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

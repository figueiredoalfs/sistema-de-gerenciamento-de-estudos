from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String

from app.core.database import Base


class Banca(Base):
    __tablename__ = "bancas"

    id = Column(String(36), primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

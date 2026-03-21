import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String, UniqueConstraint

from app.core.database import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False, unique=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

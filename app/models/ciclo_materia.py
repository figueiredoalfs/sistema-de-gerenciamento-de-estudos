import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class CicloMateria(Base):
    __tablename__ = "ciclo_materias"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    area = Column(String(100), nullable=False, index=True)  # "fiscal", "juridica", ...
    subject_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)  # nivel=0
    ordem = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    subject = relationship("Topico", foreign_keys=[subject_id])

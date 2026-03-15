import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class TaskVideo(Base):
    __tablename__ = "task_videos"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_code        = Column(String(20), ForeignKey("task_conteudo.task_code"), nullable=False, index=True)
    titulo           = Column(String(300), nullable=False)
    url              = Column(String(500), nullable=False)
    descricao        = Column(Text, nullable=True)
    avaliacao_media  = Column(Float, default=0.0)
    total_avaliacoes = Column(Integer, default=0)
    created_at       = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conteudo   = relationship("TaskConteudo", back_populates="videos", foreign_keys=[task_code])
    avaliacoes = relationship("TaskVideoAvaliacao", back_populates="video", cascade="all, delete-orphan")

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class TaskVideoAvaliacao(Base):
    __tablename__ = "task_video_avaliacoes"
    __table_args__ = (
        UniqueConstraint("video_id", "aluno_id", name="uq_avaliacao_video_aluno"),
    )

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id   = Column(String(36), ForeignKey("task_videos.id"), nullable=False, index=True)
    aluno_id   = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    nota       = Column(Integer, nullable=False)  # 1–5
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    video = relationship("TaskVideo", back_populates="avaliacoes", foreign_keys=[video_id])
    aluno = relationship("Aluno", foreign_keys=[aluno_id])

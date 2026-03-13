import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False, index=True)

    tipo = Column(
        Enum("study_theory", "review", "practice", name="study_session_tipo_enum"),
        nullable=False,
        default="study_theory",
    )

    data_agendada = Column(DateTime, nullable=True)
    status = Column(
        Enum("pending", "done", "skipped", name="study_session_status_enum"),
        nullable=False,
        default="pending",
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    topic = relationship("Topic", back_populates="study_sessions")

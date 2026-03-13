import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class TopicProgress(Base):
    __tablename__ = "topic_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False, index=True)

    accuracy_rate = Column(Float, default=0.0)       # 0.0 – 1.0
    questions_answered = Column(Integer, default=0)

    last_studied = Column(DateTime, nullable=True)
    last_review = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)

    priority_score = Column(Float, default=0.0)

    topic = relationship("Topic", back_populates="progress")

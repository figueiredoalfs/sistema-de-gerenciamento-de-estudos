import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False, index=True)

    acertos = Column(Integer, default=0)
    erros = Column(Integer, default=0)
    fonte = Column(String(100), nullable=False, default="manual")

    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    topic = relationship("Topic", back_populates="attempts")

import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    nome = Column(String(300), nullable=False)
    peso_edital = Column(Float, default=1.0)

    subject = relationship("Subject", back_populates="topics")
    progress = relationship("TopicProgress", back_populates="topic", cascade="all, delete-orphan")
    attempts = relationship("QuestionAttempt", back_populates="topic", cascade="all, delete-orphan")

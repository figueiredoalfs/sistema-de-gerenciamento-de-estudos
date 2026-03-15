import uuid

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint

from app.core.database import Base


class QuestionSubtopic(Base):
    __tablename__ = "question_subtopics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(
        String(36),
        ForeignKey("questoes_banco.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subtopic_id = Column(
        String(36),
        ForeignKey("topicos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fonte = Column(String(10), nullable=False, server_default="manual")

    __table_args__ = (
        UniqueConstraint("question_id", "subtopic_id", name="uq_question_subtopic"),
    )

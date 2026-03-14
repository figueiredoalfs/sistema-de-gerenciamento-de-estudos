import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    # Hierarquia de tópicos (nivel 0=subject, 1=topic, 2=subtopic) → tabela topicos
    subject_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    subtopic_id = Column(String(36), ForeignKey("topicos.id"), nullable=False, index=True)

    tipo = Column(
        Enum("study", "questions", "review", name="study_task_tipo_enum"),
        nullable=False,
    )

    status = Column(
        Enum("pending", "in_progress", "completed", name="study_task_status_enum"),
        nullable=False,
        default="pending",
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", foreign_keys=[aluno_id])
    subject = relationship("Topico", foreign_keys=[subject_id])
    topic = relationship("Topico", foreign_keys=[topic_id])
    subtopic = relationship("Topico", foreign_keys=[subtopic_id])

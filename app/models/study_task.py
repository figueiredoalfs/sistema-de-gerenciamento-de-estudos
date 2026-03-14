import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    # Hierarquia de tópicos (nivel 0=subject, 1=topic, 2=subtopic) → tabela topicos
    # topic_id e subtopic_id são nullable: tasks diagnósticas operam no nível da matéria
    subject_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topicos.id"), nullable=True)
    subtopic_id = Column(String(36), ForeignKey("topicos.id"), nullable=True)

    tipo = Column(
        Enum("study", "questions", "review", "diagnostico", name="study_task_tipo_enum"),
        nullable=False,
    )

    status = Column(
        Enum("pending", "in_progress", "completed", name="study_task_status_enum"),
        nullable=False,
        default="pending",
    )

    # JSON array de IDs de questões — preenchido nas baterias diagnósticas
    questoes_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", foreign_keys=[aluno_id])
    subject = relationship("Topico", foreign_keys=[subject_id])
    topic = relationship("Topico", foreign_keys=[topic_id])
    subtopic = relationship("Topico", foreign_keys=[subtopic_id])

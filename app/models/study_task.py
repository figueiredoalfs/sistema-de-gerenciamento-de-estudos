import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
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
        Enum(
            "study", "questions", "review", "diagnostico",
            "teoria", "revisao", "questionario", "simulado", "reforco",
            name="study_task_tipo_enum",
        ),
        nullable=False,
    )

    status = Column(
        Enum("pending", "in_progress", "completed", name="study_task_status_enum"),
        nullable=False,
        default="pending",
    )

    # JSON array de IDs de questões — preenchido nas baterias diagnósticas
    questoes_json = Column(Text, nullable=True)

    # Conteúdo compartilhado entre alunos (mesmo subtopico+tipo)
    task_code         = Column(String(20), ForeignKey("task_conteudo.task_code"), nullable=True, index=True)
    numero_cronograma = Column(Integer, nullable=True)

    # Cronograma semanal
    week_number   = Column(Integer, nullable=True)  # número da semana (1, 2, 3, ...)
    order_in_week = Column(Integer, nullable=True)  # posição dentro da semana (1..N)

    # Meta pedagógica à qual esta task pertence (nullable: tasks antigas não têm meta)
    goal_id = Column(String(36), ForeignKey("metas.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno    = relationship("Aluno", foreign_keys=[aluno_id])
    subject  = relationship("Topico", foreign_keys=[subject_id])
    topic    = relationship("Topico", foreign_keys=[topic_id])
    subtopic = relationship("Topico", foreign_keys=[subtopic_id])
    conteudo = relationship("TaskConteudo", foreign_keys=[task_code])
    meta     = relationship("Meta", back_populates="tasks", foreign_keys=[goal_id])

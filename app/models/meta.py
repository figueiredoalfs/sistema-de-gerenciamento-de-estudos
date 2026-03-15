import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Meta(Base):
    """
    Contêiner pedagógico de tasks semanais.

    Uma Meta agrupa as StudyTasks geradas pela engine pedagógica para uma semana
    de estudo. É distinta de MetaSemanal (que rastreia tempo/minutos); a Meta
    rastreia o ciclo de aprendizado por subtópico.

    status: aberta → meta ativa; encerrada → arquivada (nunca deletada).
    """

    __tablename__ = "metas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    # Contador sequencial por aluno (1, 2, 3, ...) — não baseado em calendário
    numero_semana = Column(Integer, nullable=False)

    # Total de tasks que a meta deve conter (= int(horas_por_dia × dias_por_semana))
    tasks_meta = Column(Integer, nullable=False)

    # Atualizado incrementalmente conforme tasks são concluídas
    tasks_concluidas = Column(Integer, nullable=False, default=0)

    # aberta → meta ativa; encerrada → arquivada
    status = Column(String(20), nullable=False, default="aberta")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", foreign_keys=[aluno_id])
    tasks = relationship("StudyTask", back_populates="meta", cascade="all, delete-orphan")

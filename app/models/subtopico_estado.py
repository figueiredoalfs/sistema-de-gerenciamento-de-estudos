import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubtopicoEstado(Base):
    """
    Rastreia o estado pedagógico de um aluno em relação a um subtópico.

    Máquina de estados:
        novo → em_estudo → em_revisao → dominado

    Transições controladas pela engine_pedagogica com base em:
        - exposure_count: quantos ciclos completos (teoria+questionario) o aluno fez
        - accuracy_rate: taxa de acerto calculada de RespostaQuestao (0.0–1.0)

    Limiares progressivos:
        exposure 1 → 60%  |  exposure 2 → 70%  |  exposure 3+ → 80%  |  domínio → 85%
    """

    __tablename__ = "subtopico_estados"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)
    subtopico_id = Column(String(36), ForeignKey("topicos.id"), nullable=False, index=True)

    # Estado atual do subtópico para este aluno
    estado = Column(String(20), nullable=False, default="novo")

    # Número de ciclos pedagógicos completos para este subtópico
    exposure_count = Column(Integer, nullable=False, default=0)

    # Taxa de acerto consolidada (0.0–1.0), calculada de RespostaQuestao
    accuracy_rate = Column(Float, nullable=False, default=0.0)

    # Quando foi gerada a última task para este subtópico
    ultima_exposicao = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("aluno_id", "subtopico_id", name="uq_subtopico_estado_aluno"),
    )

    aluno = relationship("Aluno", foreign_keys=[aluno_id])
    subtopico = relationship("Topico", foreign_keys=[subtopico_id])

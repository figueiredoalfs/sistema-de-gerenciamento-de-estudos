import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Simulado(Base):
    __tablename__ = "simulados"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    aluno_id = Column(String(36), ForeignKey("alunos.id"), nullable=False, index=True)

    # ID do edital/cronograma de referência (opcional)
    edital_id = Column(String(36), nullable=True)
    cronograma_id = Column(String(36), ForeignKey("cronogramas.id"), nullable=True)

    # Questões geradas: [{topico_id, enunciado, alternativas[], gabarito, tipo}]
    questoes_json = Column(Text, default="[]")

    # Respostas e resultado: {acertos, total, percentual, por_materia: {}, ip_impacto}
    resultado_json = Column(Text, default="{}")

    total_questoes = Column(Integer, default=0)
    acertos = Column(Integer, default=0)
    percentual = Column(Float, default=0.0)

    concluido = Column(Boolean, default=False)
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("Aluno", back_populates="simulados")

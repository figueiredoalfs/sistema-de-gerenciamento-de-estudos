import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class QuestaoBanco(Base):
    __tablename__ = "questoes_banco"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_code = Column(String(50), unique=True, nullable=False, index=True)
    subject = Column(String(200), nullable=False)
    statement = Column(Text, nullable=False)
    alternatives_json = Column(Text, nullable=False)  # JSON: {"A": "...", "B": "...", ...}
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D ou E
    board = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    materia_pendente = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

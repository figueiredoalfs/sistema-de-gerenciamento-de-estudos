import uuid

from sqlalchemy import Column, Float, ForeignKey, String, UniqueConstraint

from app.core.database import Base


class SubtopicoArea(Base):
    """Configura peso e complexidade de um subtópico para uma área específica.

    complexidade define:
    - baixa  → limiar de domínio 70%
    - media  → limiar de domínio 75%
    - alta   → limiar de domínio 80%
    """

    __tablename__ = "subtopico_areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subtopico_id = Column(String(36), ForeignKey("topicos.id"), nullable=False)
    area = Column(String(100), nullable=False)
    peso = Column(Float, default=1.0)
    complexidade = Column(String(10), default="media")  # baixa / media / alta

    __table_args__ = (UniqueConstraint("subtopico_id", "area", name="uq_subtopico_area"),)

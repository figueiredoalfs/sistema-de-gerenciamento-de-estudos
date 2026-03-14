from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TopicoCreate(BaseModel):
    nome: str
    nivel: int = 2  # 0=matéria, 1=bloco, 2=tópico
    parent_id: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None
    banca: Optional[str] = None
    peso_edital: float = 1.0
    decay_rate: float = 0.05
    dependencias_json: str = "[]"


class TopicoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None
    banca: Optional[str] = None
    peso_edital: Optional[float] = None
    decay_rate: Optional[float] = None
    dependencias_json: Optional[str] = None
    ativo: Optional[bool] = None


class TopicoResponse(BaseModel):
    id: str
    nome: str
    nivel: int
    parent_id: Optional[str]
    descricao: Optional[str]
    area: Optional[str]
    banca: Optional[str]
    peso_edital: float
    decay_rate: float
    dependencias_json: str
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}

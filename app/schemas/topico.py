from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


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
    prerequisitos_json: str = "[]"


class TopicoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None
    banca: Optional[str] = None
    peso_edital: Optional[float] = None
    decay_rate: Optional[float] = None
    dependencias_json: Optional[str] = None
    prerequisitos_json: Optional[str] = None
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
    prerequisitos_json: str
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── SubtopicoArea ────────────────────────────────────────────────────────────

AREAS_ATIVAS = {"fiscal", "eaof_com", "eaof_svm", "cfoe_com"}
COMPLEXIDADES = {"baixa", "media", "alta"}


class SubtopicoAreaUpsert(BaseModel):
    area: str
    peso: float = 1.0
    complexidade: str = "media"

    @field_validator("complexidade")
    @classmethod
    def validar_complexidade(cls, v: str) -> str:
        if v not in COMPLEXIDADES:
            raise ValueError(f"complexidade deve ser: {', '.join(COMPLEXIDADES)}")
        return v


class SubtopicoAreaResponse(BaseModel):
    id: str
    subtopico_id: str
    area: str
    peso: float
    complexidade: str

    model_config = {"from_attributes": True}


# ─── Hierarquia ───────────────────────────────────────────────────────────────

class SubtopicoHierarquia(BaseModel):
    id: str
    nome: str
    nivel: int
    ativo: bool
    peso_edital: float
    prerequisitos_json: str
    num_questoes: int
    areas: List[SubtopicoAreaResponse]


class BlocoHierarquia(BaseModel):
    id: str
    nome: str
    nivel: int
    ativo: bool
    subtopicos: List[SubtopicoHierarquia]


class MateriaHierarquia(BaseModel):
    id: str
    nome: str
    nivel: int
    ativo: bool
    blocos: List[BlocoHierarquia]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class ResponderQuestaoRequest(BaseModel):
    resposta_dada: str

    @field_validator("resposta_dada")
    @classmethod
    def validar_alternativa(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in {"A", "B", "C", "D", "E"}:
            raise ValueError("resposta_dada deve ser A, B, C, D ou E")
        return v


class RespostaQuestaoResponse(BaseModel):
    id: str
    questao_id: str
    subtopico_id: str
    resposta_dada: str
    correta: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DesempenhoSubtopicoItem(BaseModel):
    subtopico_id: str
    subtopico_nome: str
    respondidas: int
    acertos: int
    taxa_acerto: float  # 0.0–100.0


class DesempenhoSubtopicosResponse(BaseModel):
    total_respondidas: int
    total_acertos: int
    taxa_acerto_geral: float
    subtopicos: List[DesempenhoSubtopicoItem]

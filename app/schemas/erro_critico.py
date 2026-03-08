from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ErroCriticoRequest(BaseModel):
    materia: str
    topico_texto: Optional[str] = None
    topico_id: Optional[str] = None
    id_bateria: Optional[str] = None
    qtd_erros: int = 1
    observacao: Optional[str] = None


class ErroCriticoStatusUpdate(BaseModel):
    status: str  # pendente | em_revisao | resolvido


class ErroCriticoOut(BaseModel):
    id: str
    materia: str
    topico_texto: Optional[str] = None
    qtd_erros: int
    observacao: Optional[str] = None
    status: str
    data: datetime
    id_bateria: Optional[str] = None

    class Config:
        from_attributes = True


class ErroCriticoListResponse(BaseModel):
    total: int
    itens: List[ErroCriticoOut]

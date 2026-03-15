from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskVideoCreate(BaseModel):
    titulo:   str
    url:      str
    descricao: Optional[str] = None


class TaskVideoResponse(BaseModel):
    id:               str
    task_code:        str
    titulo:           str
    url:              str
    descricao:        Optional[str] = None
    avaliacao_media:  float = 0.0
    total_avaliacoes: int = 0
    created_at:       datetime

    model_config = {"from_attributes": True}


class TaskVideoAvaliacaoCreate(BaseModel):
    nota: int = Field(..., ge=1, le=5)


class AvaliarVideoResponse(BaseModel):
    video_id:         str
    avaliacao_media:  float
    total_avaliacoes: int

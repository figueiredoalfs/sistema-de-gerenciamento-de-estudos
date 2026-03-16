from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.study_task import StudyTaskResponse


class MetaGerarRequest(BaseModel):
    pass  # engine auto-incrementa o numero_semana; nenhum campo obrigatório


class MetaResponse(BaseModel):
    id: str
    aluno_id: str
    numero_semana: int
    tasks_meta: int
    tasks_concluidas: int
    status: str
    created_at: datetime
    tasks: List[StudyTaskResponse] = []

    model_config = {"from_attributes": True}


class MetaListResponse(BaseModel):
    total: int
    abertas: int      # metas com status="aberta"
    encerradas: int   # metas com status="encerrada" (histórico)
    metas: List[MetaResponse]


class GoalActiveResponse(BaseModel):
    goal_id: str
    tasks_total: int
    tasks_completed: int
    progress_percentage: int

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

from app.schemas.resposta_questao import DesempenhoSubtopicoItem

TipoTask = Literal[
    "study", "questions", "review", "diagnostico",
    "teoria", "revisao", "questionario", "simulado", "reforco",
]
StatusTask = Literal["pending", "in_progress", "completed"]


class StudyTaskCreate(BaseModel):
    subject_id: str
    # Opcionais: tasks diagnósticas operam no nível da matéria (sem topic/subtopic)
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    tipo: TipoTask


class StudyTaskStatusUpdate(BaseModel):
    status: StatusTask


class TaskGeradaItem(BaseModel):
    id: str
    subject_id: str
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    subject_nome: Optional[str] = None
    topic_nome: Optional[str] = None
    subtopic_nome: Optional[str] = None
    tipo: str
    status: str


class StudyTaskResponse(BaseModel):
    id: str
    aluno_id: str
    subject_id: str
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    subject_nome: Optional[str] = None
    topic_nome: Optional[str] = None
    subtopic_nome: Optional[str] = None
    tipo: str
    status: str
    questoes_json:        Optional[str] = None
    task_code:            Optional[str] = None
    numero_cronograma:    Optional[int] = None
    week_number:          Optional[int] = None
    order_in_week:        Optional[int] = None
    created_at:           datetime
    desempenho_subtopicos: Optional[List[DesempenhoSubtopicoItem]] = None
    tarefas_geradas:      Optional[List[TaskGeradaItem]] = None

    model_config = {"from_attributes": True}


class StudyTaskListResponse(BaseModel):
    total: int
    itens: List[StudyTaskResponse]

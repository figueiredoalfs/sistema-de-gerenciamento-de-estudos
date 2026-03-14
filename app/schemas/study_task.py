from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

TipoTask = Literal["study", "questions", "review"]
StatusTask = Literal["pending", "in_progress", "completed"]


class StudyTaskCreate(BaseModel):
    subject_id: str
    topic_id: str
    subtopic_id: str
    tipo: TipoTask


class StudyTaskStatusUpdate(BaseModel):
    status: StatusTask


class StudyTaskResponse(BaseModel):
    id: str
    aluno_id: str
    subject_id: str
    topic_id: str
    subtopic_id: str
    subject_nome: Optional[str] = None
    topic_nome: Optional[str] = None
    subtopic_nome: Optional[str] = None
    tipo: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyTaskListResponse(BaseModel):
    total: int
    itens: List[StudyTaskResponse]
